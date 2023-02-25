import os
from struct import unpack, pack

from mtkhacker_modules.hwparam_module import MTKHhacker_hwparam
from mtkhacker_modules.path_module import MTKH_path
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.hwcrypto import crypto_setup, hwcrypto
from mtkclient.Library.utils import progress, find_binary
from mtkclient.Library.seccfg import seccfg
from binascii import hexlify
from mtkclient.Library.utils import mtktee
from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
import hashlib
import json

class LCmd:
    CUSTOM_READ = b"\x29"
    CUSTOM_WRITE = b"\x2A"
    ACK = b"\x5A"
    NACK = b"\xA5"

class legacyext:
    def __init__(self, arg_mtk, arg_legacy):
        self.path = MTKH_path()
        self.arg_mtk = arg_mtk
        self.eh = ErrorHandler()
        self.config = self.arg_mtk.config
        self.usbwrite = self.arg_mtk.connect.usbwrite
        self.usbread = self.arg_mtk.connect.usbread
        self.echo = self.arg_mtk.connect.echo
        self.rbyte = self.arg_mtk.connect.rbyte
        self.rdword = self.arg_mtk.connect.rdword
        self.rword = self.arg_mtk.connect.rword
        self.arg_legacy = arg_legacy
        self.Cmd=LCmd()
        self.da2 = None
        self.da2address = None


    def patch_da2(self, da2):
        da2patched = bytearray(da2)
        # Patch security READ_REG16_CMD
        check_addr = find_binary(da2, b"\x08\xB5\x4F\xF4\x50\x42")
        if check_addr is not None:
            da2patched[check_addr:check_addr + 6] = b"\x08\xB5\x00\x20\x08\xBD"
            logger.info("Legacy DA2 is patched.")
        else:
            logger.warning("Legacy address check not patched.")
        check_addr2 = find_binary(da2, b"\x30\xB5\x85\xB0\x03\xAB")
        if check_addr2 is not None:
            """
            PUSH            {R4-R6,LR}
            MOV             R4, #0x8004A6C8
            LDR             R3, [R4,#0x24]
            BLX             R3
            LDR             R3, [R4,#0x24]
            MOV             R5, R0
            BLX             R3
            MOV             R6, R0
            LDR             R0, [R5]
            ADD.W           R5, R5, #4
            LDR             R3, [R4,#0x28]
            BLX             R3
            SUB.W           R6, R6, #1
            CMP             R6, #0
            BNE             0x8000C1B6
            MOVS            R0, #0x5A
            LDR             R3, [R4,#0x10]
            POP.W           {R4-R6,LR}
            BX              R3
            """
            cmdF0 = bytes.fromhex("70 B5 4A F2 C8 64 C8 F2 04 04 63 6A 98 47 63 6A 05 46 98 47 06 46 4F F0 00 01 28 68 05 F1 04 05 A3 6A 98 47 A6 F1 01 06 00 2E F6 D1 5A 20 23 69 BD E8 70 40 18 47")
            da2patched[check_addr2:check_addr2+len(cmdF0)]=cmdF0
            logger.info("Legacy DA2 CMD F0 is patched.")
        else:
            logger.warning("Legacy DA2 CMD F0 not patched.")
        return da2patched

    def fix_hash(self, da1, da2, da2sig_len, hashpos, hashmode):
        da1 = bytearray(da1)
        dahash = None
        if hashmode == 1:
            dahash = hashlib.sha1(da2[:-da2sig_len]).digest()
        elif hashmode == 2:
            dahash = hashlib.sha256(da2[:-da2sig_len]).digest()
        da1[hashpos:hashpos + len(dahash)] = dahash
        return da1

    def readmem(self, addr, dwords=1):
        res = []
        for pos in range(dwords):
            data = self.legacy.read_reg32(addr + pos * 4)
            if data is None:
                return False
            if dwords == 1:
                return data
            res.append(data)
        return res

    def custom_read(self, addr, length):
        dwords=length//4
        if length%4!=0:
            dwords+=1
        #data = bytearray(b"".join(int.to_bytes(val,4,'little') for val in [self.legacy.read_reg32(addr + pos * 4) for pos in range(dwords)]))
        res = self.legacy.custom_F0(addr, dwords)
        data = bytearray(b"".join([int.to_bytes(val,4,'little') for val in res]))
        return data[:length]

    def writeregister(self, addr, dwords):
        if isinstance(dwords, int):
            dwords = [dwords]
        pos = 0
        if len(dwords) < 0x20:
            for val in dwords:
                if not self.legacy.write_reg32(addr + pos, val):
                    return False
                pos += 4
        else:
            dat = b"".join([pack("<I", val) for val in dwords])
            self.custom_write(addr, dat)
        return True

    def writemem(self, addr, data):
        for i in range(0, len(data), 4):
            value = data[i:i + 4]
            while len(value) < 4:
                value += b"\x00"
            self.writeregister(addr + i, unpack("<I", value))
        return True

    def custom_write(self, addr, data):
        return self.writemem(addr, data)

    def setotp(self, hwc):
        otp = None
        if self.mtk.config.preloader is not None:
            idx = self.mtk.config.preloader.find(b"\x4D\x4D\x4D\x01\x30")
            if idx != -1:
                otp = self.mtk.config.preloader[idx + 0xC:idx + 0xC + 32]
        if otp is None:
            otp = 32 * b"\x00"
        hwc.sej.sej_set_otp(otp)

    def cryptosetup(self):
        setup = crypto_setup()
        setup.blacklist = self.config.chipconfig.blacklist
        setup.gcpu_base = self.config.chipconfig.gcpu_base
        setup.dxcc_base = self.config.chipconfig.dxcc_base
        setup.hwcode = self.config.hwcode
        setup.da_payload_addr = self.config.chipconfig.da_payload_addr
        setup.sej_base = self.config.chipconfig.sej_base
        setup.read32 = self.readmem
        setup.write32 = self.writeregister
        setup.writemem = self.writemem
        return hwcrypto(setup, self.config.gui)

    def seccfg(self, lockflag):
        if lockflag not in ["unlock", "lock"]:
            return False, "Valid flags are: unlock, lock"
        hwc = self.cryptosetup()
        sc_org = seccfg(hwc)
        data, guid_gpt = self.legacy.partition.get_gpt(self.mtk.config.gpt_settings, "user")
        seccfg_data = None
        partition = None
        for rpartition in guid_gpt.partentries:
            if rpartition.name == "seccfg":
                partition = rpartition
                seccfg_data = self.legacy.readflash(
                    addr=partition.sector * self.mtk.daloader.daconfig.pagesize,
                    length=partition.sectors * self.mtk.daloader.daconfig.pagesize,
                    filename="", parttype="user", display=False)
                break
        if seccfg_data is None:
            return False, "Couldn't detect existing seccfg partition. Aborting unlock."
        if seccfg_data[:4] != pack("<I", 0x4D4D4D4D):
            return False, "Unknown seccfg partition header. Aborting unlock."

        if not sc_org.parse(seccfg_data):
            return False, "Error on parsing seccfg."
        sc_new = seccfg(hwc)
        self.setotp(hwc)
        hwtype = "hw"
        V3 = True
        sc_new.create(sc_org=sc_org, hwtype=hwtype, V3=V3)
        if sc_org.hash != sc_new.hash:
            V3=False
            sc_new.create(sc_org=sc_org, hwtype=hwtype, V3=V3)
        if sc_org.hash != sc_new.hash:
            hwtype = "sw"
            sc_new.create(sc_org=sc_org, hwtype=hwtype)
            if sc_org.hash != sc_new.hash:
                return False, "Device has is either already unlocked or algo is unknown. Aborting."
        writedata = sc_new.create(sc_org=None, hwtype=hwtype, lockflag=lockflag, V3=V3)
        if self.legacy.writeflash(addr=partition.sector * self.mtk.daloader.daconfig.pagesize,
                                  length=len(writedata),
                                  filename=None, wdata=writedata, parttype="user", display=True):
            return True, "Successfully wrote seccfg."
        return False, "Error on writing seccfg config to flash."

    def decrypt_tee(self, filename="tee1.bin", aeskey1:bytes=None, aeskey2:bytes=None):
        hwc = self.cryptosetup()
        with open(filename, "rb") as rf:
            data=rf.read()
            idx=0
            while idx!=-1:
                idx=data.find(b"EET KTM ",idx+1)
                if idx!=-1:
                    mt = mtktee()
                    mt.parse(data[idx:])
                    rdata=hwc.mtee(data=mt.data, keyseed=mt.keyseed, ivseed=mt.ivseed,
                                   aeskey1=aeskey1, aeskey2=aeskey2)
                    open("tee_"+hex(idx)+".dec","wb").write(rdata)

    def generate_keys(self):
        hwc = self.cryptosetup()
        retval = {}
        retval["hwcode"] = hex(self.config.hwcode)
        meid = self.config.get_meid()
        socid = self.config.get_socid()
        hwcode = self.config.get_hwcode()
        if meid is not None:
            logger.info("MEID        : " + hexlify(meid).decode('utf-8'))
            retval["meid"] = hexlify(meid).decode('utf-8')
            if self.config.hwparam is None:
                self.config.hwparam = MTKHhacker_hwparam(meid, self.config.hwparam_path)
            self.config.hwparam.writesetting("meid", hexlify(meid).decode('utf-8'))
        if socid is not None:
            logger.info("SOCID       : " + hexlify(socid).decode('utf-8'))
            retval["socid"] = hexlify(socid).decode('utf-8')
            self.config.hwparam.writesetting("socid", hexlify(socid).decode('utf-8'))
        if hwcode is not None:
            logger.info("HWCODE      : " + hex(hwcode))
            retval["hwcode"] = hex(hwcode)
            self.config.hwparam.writesetting("hwcode", hex(hwcode))
        if self.config.chipconfig.dxcc_base is not None:
            logger.info("Generating dxcc rpmbkey...")
            rpmbkey = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb")
            logger.info("Generating dxcc fdekey...")
            fdekey = hwc.aes_hwcrypt(btype="dxcc", mode="fde")
            logger.info("Generating dxcc rpmbkey2...")
            rpmb2key = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb2")
            logger.info("Generating dxcc km key...")
            ikey = hwc.aes_hwcrypt(btype="dxcc", mode="itrustee")
            #logger.info("Generating dxcc platkey + provkey key...")
            #platkey, provkey = hwc.aes_hwcrypt(btype="dxcc", mode="prov")
            #logger.info("Provkey     : " + hexlify(provkey).decode('utf-8'))
            #logger.info("Platkey     : " + hexlify(platkey).decode('utf-8'))
            if rpmbkey is not None:
                logger.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                self.config.hwparam.writesetting("rpmbkey",hexlify(rpmbkey).decode('utf-8'))
                retval["rpmbkey"] = hexlify(rpmbkey).decode('utf-8')
            if rpmb2key is not None:
                logger.info("RPMB2       : " + hexlify(rpmb2key).decode('utf-8'))
                self.config.hwparam.writesetting("rpmb2key",hexlify(rpmb2key).decode('utf-8'))
                retval["rpmb2key"] = hexlify(rpmb2key).decode('utf-8')
            if fdekey is not None:
                logger.info("FDE         : " + hexlify(fdekey).decode('utf-8'))
                self.config.hwparam.writesetting("fdekey",hexlify(fdekey).decode('utf-8'))
                retval["fdekey"] = hexlify(fdekey).decode('utf-8')
            if ikey is not None:
                logger.info("iTrustee    : " + hexlify(ikey).decode('utf-8'))
                self.config.hwparam.writesetting("kmkey", hexlify(ikey).decode('utf-8'))
                retval["kmkey"] = hexlify(ikey).decode('utf-8')
            if self.config.chipconfig.prov_addr:
                provkey = self.custom_read(self.config.chipconfig.prov_addr, 16)
                logger.info("PROV        : " + hexlify(provkey).decode('utf-8'))
                self.config.hwparam.writesetting("provkey", hexlify(provkey).decode('utf-8'))
                retval["provkey"] = hexlify(provkey).decode('utf-8')
            """
            hrid = self.xflash.get_hrid()
            if hrid is not None:
                logger.info("HRID        : " + hexlify(hrid).decode('utf-8'))
                open(os.path.join("logs", "hrid.txt"), "wb").write(hexlify(hrid))
            """
            if hwcode == 0x699 and self.config.chipconfig.sej_base:
                mtee3 = hwc.aes_hwcrypt(mode="mtee3", btype="sej")
                if mtee3:
                    logger.info("MTEE3       : " + hexlify(mtee3).decode('utf-8'))
                    self.config.hwparam.writesetting("mtee3", hexlify(mtee3).decode('utf-8'))
                    retval["mtee3"] = hexlify(mtee3).decode('utf-8')
            return retval
        elif self.config.chipconfig.sej_base is not None:
            if os.path.exists("tee.json"):
                val=json.loads(open("tee.json","r").read())
                self.decrypt_tee(val["filename"],bytes.fromhex(val["data"]),bytes.fromhex(val["data2"]))
            if meid == b"":
                if self.config.chipconfig.meid_addr is None:
                    meid_addr = 0x1008ec
                else:
                    meid_addr = self.config.chipconfig.meid_addr
                meid = b"".join([pack("<I", val) for val in self.readmem(meid_addr, 4)])
            if meid != b"":
                logger.info("Generating sej rpmbkey...")
                self.setotp(hwc)
                rpmbkey = hwc.aes_hwcrypt(mode="rpmb", data=meid, btype="sej")
                if rpmbkey:
                    logger.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                    self.config.hwparam.writesetting("rpmbkey", hexlify(rpmbkey).decode('utf-8'))
                    retval["rpmbkey"] = hexlify(rpmbkey).decode('utf-8')
                logger.info("Generating sej mtee...")
                mtee = hwc.aes_hwcrypt(mode="mtee", btype="sej")
                if mtee:
                    logger.info("MTEE        : " + hexlify(mtee).decode('utf-8'))
                    self.config.hwparam.writesetting("mtee", hexlify(mtee).decode('utf-8'))
                    retval["mtee"] = hexlify(mtee).decode('utf-8')
                logger.info("Generating sej mtee3...")
                mtee3 = hwc.aes_hwcrypt(mode="mtee3", btype="sej")
                if mtee3:
                    logger.info("MTEE3       : " + hexlify(mtee3).decode('utf-8'))
                    self.config.hwparam.writesetting("mtee3", hexlify(mtee3).decode('utf-8'))
                    retval["mtee3"] = hexlify(mtee3).decode('utf-8')
            else:
                logger.info("SEJ Mode: No meid found. Are you in brom mode ?")
        if self.config.chipconfig.gcpu_base is not None:
            if self.config.hwcode in [0x335,0x8167,0x8163]:
                logger.info("Generating gcpu mtee2 key...")
                mtee2 = hwc.aes_hwcrypt(btype="gcpu", mode="mtee")
                if mtee2 is not None:
                    logger.info("MTEE2       : " + hexlify(mtee2).decode('utf-8'))
                    self.config.hwparam.writesetting("mtee2", hexlify(mtee2).decode('utf-8'))
                    retval["mtee2"] = hexlify(mtee2).decode('utf-8')
        self.config.hwparam.writesetting("hwcode", retval["hwcode"])
        return retval
