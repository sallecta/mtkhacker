#!/usr/bin/env python3
# MTK Flash Client (c) B.Kerler 2018-2021.
# Licensed under GPLv3 License
import os
import logging
from struct import unpack
from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
from mtkclient.config.usb_ids import default_ids
from mtkhacker_modules.path_module import MTKH_path
from mtkclient.Library.pltools import PLTools
from mtkclient.Library.mtk_preloader import Preloader
from mtkclient.Library.mtk_daloader import DAloader
from mtkhacker_modules.connect_module import MTKHhacker_connect
from mtkclient.Library.error import ErrorHandler


def split_by_n(seq, unit_count):
	"""A generator to divide a sequence into chunks of n units."""
	while seq:
		yield seq[:unit_count]
		seq = seq[unit_count:]


class Mtk:
	def __init__(self, config, serialportname: str = None, arg_setup=True):
		self.config = config
		self.loader = config.loader
		self.vid = config.vid
		self.pid = config.pid
		self.interface = config.interface
		self.path = MTKH_path()
		self.eh = ErrorHandler()
		if arg_setup:
			self.setup(self.vid, self.pid, self.interface, serialportname)
	
	def setup(self, vid=None, pid=None, interface=None, serialportname: str = None):
		if vid is None:
			vid = self.vid
		if pid is None:
			pid = self.pid
		if interface is None:
			interface = self.interface
		if vid != -1 and pid != -1:
			if interface == -1:
				for dev in default_ids:
					if dev[0] == vid and dev[1] == pid:
						interface = dev[2]
						break
			portconfig = [[vid, pid, interface]]
		else:
			portconfig = default_ids
		self.connect = MTKHhacker_connect(self, portconfig, serialportname)
		self.preloader = Preloader(self)
		self.daloader = DAloader(self)
		
	def patch_preloader_security(self, data):
		patched = False
		data = bytearray(data)
		patches = [
			("A3687BB12846", "0123A3602846", "oppo security"),
			("B3F5807F01D1", "B3F5807F01D14FF000004FF000007047", "mt6739 c30"),
			("B3F5807F04BF4FF4807305F011B84FF0FF307047", "B3F5807F04BF4FF480734FF000004FF000007047", "regular"),
			("10B50C680268", "10B5012010BD", "ram blacklist"),
			("08B5104B7B441B681B68", "00207047000000000000", "seclib_sec_usbdl_enabled"),
			("5072656C6F61646572205374617274","50617463686564204C205374617274", "Patched loader msg"),
			("F0B58BB002AE20250C460746","002070470000000000205374617274", "sec_img_auth"),
			("FFC0F3400008BD","FF4FF0000008BD","get_vfy_policy")
		]
		i = 0
		for patchval in patches:
			pattern = bytes.fromhex(patchval[0])
			idx = data.find(pattern)
			if idx != -1:
				patch = bytes.fromhex(patchval[1])
				data[idx:idx + len(patch)] = patch
				self.info(f"Patched \"{patchval[2]}\" in preloader")
				patched = True
				# break
			i += 1
		if not patched:
			self.warning(f"Failed to patch preloader security")
		else:
			# with open("preloader.patched", "wb") as wf:
			#    wf.write(data)
			#    print("Patched !")
			# self.info(f"Patched preloader security: {hex(i)}")
			data = data
		return data

	def parse_preloader(self, preloader):
		if isinstance(preloader, str):
			if os.path.exists(preloader):
				with open(preloader, "rb") as rf:
					data = rf.read()
		else:
			data = preloader
		data = bytearray(data)
		magic = unpack("<I", data[:4])[0]
		if magic == 0x014D4D4D:
			self.info(f"Valid preloader detected.")
			daaddr = unpack("<I", data[0x1C:0x20])[0]
			# dasize = unpack("<I", data[0x20:0x24])[0]
			# maxsize = unpack("<I", data[0x24:0x28])[0]
			# content_offset = unpack("<I", data[0x28:0x2C])[0]
			# sig_length = unpack("<I", data[0x2C:0x30])[0]
			jump_offset = unpack("<I", data[0x30:0x34])[0]
			daaddr = jump_offset + daaddr
			dadata = data[jump_offset:]
		else:
			self.warning("Preloader detected as shellcode, might fail to run.")
			daaddr = self.config.chipconfig.da_payload_addr
			dadata = data
		return daaddr, dadata
	
	def crasher(self, display=True, mode=None):
		rmtk = self
		plt = PLTools(self)
		if self.config.enforcecrash or self.config.meid is None or not self.config.is_brom:
			self.info("We're not in bootrom, trying to crash da...")
			if mode is None:
				for crashmode in range(0, 3):
					try:
						plt.crash(crashmode)
					except:
						pass
					rmtk = Mtk(self.config, rmtk.connect.serialportname)
					rmtk.preloader.display = display
					if rmtk.preloader.init(maxtries=20):
						if rmtk.config.is_brom:
							break
			else:
				try:
					plt.crash(mode)
				except Exception as err:
					logger.error(str(err))
					pass
				rmtk = Mtk(config=self.config, serialportname=rmtk.connect.serialportname)
				rmtk.preloader.display = display
				if rmtk.preloader.init(maxtries=20):
					return rmtk
		return rmtk

	def bypass_security(self):
		mtk = self.crasher()
		plt = PLTools(mtk)
		if self.config.payloadfile is None:
			if self.config.chipconfig.loader is None:
				self.config.payloadfile = os.path.join(self.path.payloads,
													   "generic_patcher_payload.bin")
			else:
				self.config.payloadfile = os.path.join(self.path.payloads,
													   self.config.chipconfig.loader)
		if plt.runpayload(filename=self.config.payloadfile):
			mtk.connect.run_handshake()
			return mtk
		else:
			self.error("Error on running kamakiri payload")
		return self
