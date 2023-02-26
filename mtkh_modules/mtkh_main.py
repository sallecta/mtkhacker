import os
from mtkclient.config.mtk_config import Mtk_Config
from mtkclient.Library.mtk_main import ArgHandler
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.mtk_class import Mtk
import sys
from mtkh_modules.da.mtkh_da import MTKH_DA

from mtkh_modules.path.mtkh_path import MTKH_path as mtkhacker_path
from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger

class MTKH_main:
	def __init__(self, args):
		self.args = args
		if not os.path.exists(mtkhacker_path.logs):
			os.mkdir(mtkhacker_path.logs)

	def close(self):
		sys.exit(0)

	def cmd_stage(self, arg_mtk, arg_filename, arg_stage2addr, arg_stage2file, arg_verifystage2):
		if arg_filename is None:
			stage1file = os.path.join(mtkhacker_path.payloads, "generic_stage1_payload.bin")
		else:
			stage1file = arg_filename
		if not os.path.exists(stage1file):
			self.error(f"Error: {stage1file} doesn't exist !")
			return False
		if arg_stage2file is not None:
			if not os.path.exists(arg_stage2file):
				self.error(f"Error: {arg_stage2file} doesn't exist !")
				return False
		else:
			arg_stage2file = os.path.join(arg_mtk.path.payloads, "stage2.bin")
		if arg_mtk.preloader.init():
			arg_mtk = arg_mtk.crasher()
			if arg_mtk.port.cdc.pid == 0x0003:
				plt = PLTools(arg_mtk)
				self.info("Uploading stage 1")
				arg_mtk.config.set_gui_status(arg_mtk.config.tr("Uploading stage 1"))
				if plt.runpayload(arg_filename=stage1file):
					self.info("Successfully uploaded stage 1, sending stage 2")
					arg_mtk.config.set_gui_status(arg_mtk.config.tr("Successfully uploaded stage 1, sending stage 2"))
					with open(arg_stage2file, "rb") as rr:
						stage2data = rr.read()
						while len(stage2data) % 0x200:
							stage2data += b"\x00"
					if arg_stage2addr is None:
						arg_stage2addr = arg_mtk.config.chipconfig.da_payload_addr
						if arg_stage2addr is None:
							arg_stage2addr = 0x201000
	
					# ###### Send stage2
					# magic
					arg_mtk.port.usbwrite(pack(">I", 0xf00dd00d))
					# cmd write
					arg_mtk.port.usbwrite(pack(">I", 0x4000))
					# address
					arg_mtk.port.usbwrite(pack(">I", arg_stage2addr))
					# length
					arg_mtk.port.usbwrite(pack(">I", len(stage2data)))
					bytestowrite = len(stage2data)
					pos = 0
					while bytestowrite > 0:
						size = min(bytestowrite, 1)
						if arg_mtk.port.usbwrite(stage2data[pos:pos + size]):
							bytestowrite -= size
							pos += size
					# arg_mtk.port.usbwrite(b"")
					time.sleep(0.1)
					flag = arg_mtk.port.rdword()
					if flag != 0xD0D0D0D0:
						self.error(f"Error on sending stage2, size {hex(len(stage2data))}.")
					self.info(f"Done sending stage2, size {hex(len(stage2data))}.")
					arg_mtk.config.set_gui_status(arg_mtk.config.tr("Done sending stage 2"))
					if arg_verifystage2:
						self.info("Verifying stage2 data")
						rdata = b""
						arg_mtk.port.usbwrite(pack(">I", 0xf00dd00d))
						arg_mtk.port.usbwrite(pack(">I", 0x4002))
						arg_mtk.port.usbwrite(pack(">I", arg_stage2addr))
						arg_mtk.port.usbwrite(pack(">I", len(stage2data)))
						bytestoread = len(stage2data)
						while bytestoread > 0:
							size = min(bytestoread, 1)
							rdata += arg_mtk.port.usbread(size)
							bytestoread -= size
						flag = arg_mtk.port.rdword()
						if flag != 0xD0D0D0D0:
							self.error("Error on reading stage2 data")
						if rdata != stage2data:
							self.error("Stage2 data doesn't match")
							with open("rdata", "wb") as wf:
								wf.write(rdata)
						else:
							self.info("Stage2 verification passed.")
							arg_mtk.config.set_gui_status(arg_mtk.config.tr("Stage2 verification passed."))
	
					# ####### Kick Watchdog
					# magic
					# arg_mtk.port.usbwrite(pack("<I", 0xf00dd00d))
					# cmd kick_watchdog
					# arg_mtk.port.usbwrite(pack("<I", 0x3001))
	
					# ######### Jump stage1
					# magic
					arg_mtk.port.usbwrite(pack(">I", 0xf00dd00d))
					# cmd jump
					arg_mtk.port.usbwrite(pack(">I", 0x4001))
					# address
					arg_mtk.port.usbwrite(pack(">I", arg_stage2addr))
					self.info("Done jumping stage2 at %08X" % arg_stage2addr)
					arg_mtk.config.set_gui_status(arg_mtk.config.tr("Done jumping stage2 at %08X" % arg_stage2addr))
					ack = unpack(">I", arg_mtk.port.usbread(4))[0]
					if ack == 0xB1B2B3B4:
						self.info("Successfully loaded stage2")

	def cmd_peek(self, arg_mtk, arg_addr, arg_length, arg_preloader, arg_filename):
		if arg_preloader is not None:
			if os.path.exists(arg_preloader):
				daaddr, dadata = arg_mtk.parse_preloader(arg_preloader)
		if arg_mtk.arg_preloader.init():
			if arg_mtk.config.target_config["daa"]:
				arg_mtk = arg_mtk.bypass_security()
		if arg_mtk is not None:
			if arg_preloader is not None:
				if os.path.exists(arg_preloader):
					daaddr, dadata = arg_mtk.parse_preloader(arg_preloader)
					if arg_mtk.arg_preloader.send_da(daaddr, len(dadata), 0x100, dadata):
						self.info(f"Sent arg_preloader to {hex(daaddr)}, arg_length {hex(len(dadata))}")
						if arg_mtk.arg_preloader.jump_da(daaddr):
							self.info(f"Jumped to pl {hex(daaddr)}.")
							time.sleep(2)
							config = Mtk_Config(arg_mtk.config.gui,arg_mtk.config.guiprogress)
							arg_mtk = Mtk(config=config, serialportname=arg_mtk.port.serialportname)
							res = arg_mtk.arg_preloader.init()
							if not res:
								self.error("Error on loading arg_preloader")
								return
							else:
								self.info("Successfully connected to pl.")
								# arg_mtk.arg_preloader.get_hw_sw_ver()
								# status=arg_mtk.arg_preloader.jump_to_partition(b"") # Do not remove !
				else:
					self.error("Error on jumping to pl")
					return
			self.info("Starting to read ...")
			dwords = arg_length // 4
			if arg_length % 4:
				dwords += 1
			if arg_filename is not None:
				wf = open(arg_filename, "wb")
			sdata = b""
			print_progress(0, 100, prefix='Progress:',
						   suffix='Starting, arg_addr 0x%08X' % arg_addr, bar_length=50)
			arg_length = dwords * 4
			old = 0
			pos = 0
			while dwords:
				size = min(512 // 4, dwords)
				if dwords == 1:
					data = pack("<I",arg_mtk.arg_preloader.read32(arg_addr + pos, size))
				else:
					data = b"".join(int.to_bytes(val, 4, 'little') for val in arg_mtk.arg_preloader.read32(arg_addr + pos, size))
				sdata += data
				if arg_filename is not None:
					wf.write(data)
				pos += len(data)
				prog = pos / arg_length * 100
				if round(prog, 1) > old:
					print_progress(prog, 100, prefix='Progress:',
								   suffix='Complete, arg_addr 0x%08X' % (arg_addr + pos), bar_length=50)
					old = round(prog, 1)
				dwords = (arg_length - pos) // 4
			print_progress(100, 100, prefix='Progress:',
						   suffix='Finished', bar_length=50)
			if arg_filename is None:
				print(hexlify(sdata).decode('utf-8'))
			else:
				wf.close()
				self.info(f"Data from {hex(arg_addr)} with size of {hex(arg_length)} was written to " + arg_filename)

	def cmd_log(self, mtk, filename):
		if mtk.preloader.init():
			self.info("Getting target logs...")
			try:
				logs = mtk.preloader.get_brom_log_new()
			except:
				logs = mtk.preloader.get_brom_log()
			if logs != b"":
				with open(filename, "wb") as wf:
					wf.write(logs)
					self.info(f"Successfully wrote logs to \"{filename}\"")
			else:
				self.info("No logs found.")

	def cmd_payload(self, arg_mtk, arg_payloadfile):
		if arg_mtk.preloader.init():
			arg_mtk = arg_mtk.crasher()
			plt = PLTools(arg_mtk)
			if arg_payloadfile is None:
				if arg_mtk.config.chipconfig.loader is None:
					arg_payloadfile = os.path.join(arg_mtk.path.payloads, "generic_patcher_payload.bin")
				else:
					arg_payloadfile = os.path.join(arg_mtk.path.payloads, arg_mtk.config.chipconfig.loader)
			plt.runpayload(filename=arg_payloadfile)
			if self.args.metamode:
				arg_mtk.port.run_handshake()
				arg_mtk.preloader.jump_bl()
				arg_mtk.port.close(reset=True)
				meta = META(arg_mtk)
				if meta.init(metamode=self.args.metamode, display=True):
					self.info(f"Successfully set meta mode : {self.args.metamode}")
		arg_mtk.port.close(reset=True)
	

	def run(self, arg_parser):
		config = Mtk_Config(gui=None, guiprogress=None)
		ArgHandler(self.args, config)
		self.eh = ErrorHandler()
		serialport = None
		try:
			serialport = self.args.serialport
		except:
			pass
		mtk = Mtk(config=config, serialportname=serialport)
		config.set_peek(mtk.daloader.peek) # ??
		
		command = self.args.cmd
		
		logger.debug(f"command: {command}")
		if command == "script":
			if not os.path.exists(self.args.script):
				self.error("Couldn't find script: "+self.args.script)
				self.close()
				return
			commands=open(self.args.script,"r").read().splitlines()
			# DA / FLash commands start here
			try:
				preloader = self.args.preloader
			except:
				preloader = None
			download_agent = MTKH_DA(mtk)
			mtk = download_agent.configure(mtk, preloader)
			if mtk is not None:
				for rcmd in commands:
					self.args = arg_parser.parse_args(rcmd.split(" "))
					ArgHandler(self.args, config)
					command = self.args.command
					download_agent.handle_da_cmds(mtk, command, self.args)
					sys.stdout.flush()
					sys.stderr.flush()
			else:
				self.close()
		elif command == "dumpbrom":
			if mtk.preloader.init():
				rmtk = mtk.crasher()
				if rmtk is None:
					sys.exit(0)
				if rmtk.port.cdc.vid != 0xE8D and rmtk.port.cdc.pid != 0x0003:
					self.warning("We couldn't enter preloader.")
				filename = self.args.filename
				if filename is None:
					cpu = ""
					if rmtk.config.cpu != "":
						cpu = "_" + rmtk.config.cpu
					filename = "brom" + cpu + "_" + hex(rmtk.config.hwcode)[2:] + ".bin"
				plt = PLTools(rmtk)
				plt.run_dump_brom(filename, self.args.ptype)
				rmtk.port.close()
			self.close()
		elif command == "dumppreloader":
			if mtk.preloader.init():
				rmtk = mtk.crasher()
				if rmtk is None:
					sys.exit(0)
				if rmtk.port.cdc.vid != 0xE8D or rmtk.port.cdc.pid != 0x0003:
					self.warning("We couldn't enter preloader.")
				plt = PLTools(rmtk)
				data, filename = plt.run_dump_preloader(self.args.ptype)
				if data is not None:
					if filename == "":
						if self.args.filename is not None:
							filename = self.args.filename
						else:
							filename = "preloader.bin"
					with open(filename, 'wb') as wf:
						print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
						wf.write(data)
						print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
						self.info("Preloader dumped as: " + filename)
				rmtk.port.close()
			self.close()
		elif command == "dumpsram":
			if mtk.preloader.init():
				rmtk = mtk.crasher()
				if rmtk is None:
					sys.exit(0)
				if rmtk.port.cdc.vid != 0xE8D and rmtk.port.cdc.pid != 0x0003:
					self.warning("We couldn't enter preloader.")
				filename = self.args.filename
				if filename is None:
					cpu = ""
					if rmtk.config.cpu != "":
						cpu = "_" + rmtk.config.cpu
					filename = "sram" + cpu + "_" + hex(rmtk.config.hwcode)[2:] + ".bin"
				plt = PLTools(rmtk)
				plt.run_dump_brom(filename, self.args.ptype, loader="generic_sram_payload.bin")
				rmtk.port.close()
			self.close()
		elif command == "brute":
			self.info("Kamakiri / DA Bruteforce run")
			rmtk = Mtk(config=mtk.config, serialportname=mtk.port.serialportname)
			plt = PLTools(rmtk)
			plt.runbrute(self.args)
			self.close()
		elif command == "crash":
			if mtk.preloader.init():
				mtk = mtk.crasher(mode=getint(self.args.mode))
			mtk.port.close()
			self.close()
		elif command == "plstage":
			if mtk.config.chipconfig.pl_payload_addr is not None:
				plstageaddr = mtk.config.chipconfig.pl_payload_addr
			else:
				plstageaddr = 0x40001000 #0x40200000  # 0x40001000
			if self.args.pl is None:
				plstage = os.path.join(mtk.path.payloads, "pl.bin")
			else:
				plstage = self.args.pl
			if os.path.exists(plstage):
				with open(plstage, "rb") as rf:
					rf.seek(0)
					if os.path.basename(plstage)!="pl.bin":
						pldata = mtk.patch_preloader_security(rf.read())
					else:
						pldata = rf.read()
			if mtk.preloader.init():
				if mtk.config.target_config["daa"]:
					mtk = mtk.bypass_security()
					if mtk is None:
						self.error("Error on bypassing security, aborting")
						return
				self.info("Connected to device, loading")
			else:
				self.error("Couldn't connect to device, aborting.")
	
			if mtk.config.is_brom and mtk.config.preloader is None and os.path.basename(plstage)=="pl.bin":
				self.warning("PL stage needs preloader, please use --preloader option. " +
							 "Trying to dump preloader from ram.")
				plt = PLTools(mtk=mtk)
				dadata, filename = plt.run_dump_preloader(self.args.ptype)
				mtk.config.preloader = mtk.patch_preloader_security(dadata)
	
			if mtk.config.preloader_filename is not None:
				self.info("Using custom preloader : " + mtk.config.preloader_filename)
				mtk.preloader.setreg_disablewatchdogtimer(mtk.config.hwcode)
				daaddr, dadata = mtk.parse_preloader(mtk.config.preloader_filename)
				dadata = mtk.config.preloader = mtk.patch_preloader_security(dadata)
				if mtk.preloader.send_da(daaddr, len(dadata), 0x100, dadata):
					self.info(f"Sent preloader to {hex(daaddr)}, length {hex(len(dadata))}")
					if mtk.preloader.jump_da(daaddr):
						self.info(f"PL Jumped to daaddr {hex(daaddr)}.")
						mtk = Mtk(config=mtk.config)
						if self.args.metamode is not None:
							time.sleep(1)
							meta = META(mtk)
							if meta.init(metamode=self.args.metamode, display=False):
								self.info(f"Successfully set meta mode : {self.args.metamode}")
							mtk.port.close()
							self.close()
							return
						if self.args.startpartition is not None or self.args.offset is not None or self.args.length is not None:
							time.sleep(1)
							res = mtk.preloader.init()
							if not res:
								self.error("Error on loading preloader")
								return
							else:
								self.info("Successfully connected to pl")
						else:
							mtk.port.close()
							time.sleep(3)
							self.info(f"Keep pressed power button to boot.")
							self.close()
							return
	
						if self.args.startpartition is not None:
							partition = self.args.startpartition
							self.info("Booting to : " + partition)
							#mtk.preloader.send_partition_data(partition, mtk.patch_preloader_security(pldata))
							status = mtk.preloader.jump_to_partition(partition)  # Do not remove !
	
						if self.args.offset is not None and self.args.length is not None:
							offset = getint(self.args.offset)
							length = getint(self.args.length)
							rlen = min(0x200, length)
							status=0
							mtk.preloader.get_hw_sw_ver()
							if self.args.filename is not None:
								with open(self.args.filename,"wb") as wf:
									for pos in range(offset, offset+length,rlen):
										print("Reading pos %08X" % pos)
										res = mtk.preloader.read32(pos, rlen//4)
										wf.write(b"".join([pack("<I",val) for val in res]))
							else:
								for pos in range(offset, offset+length,rlen):
									print("Reading pos %08X" % pos)
									res = mtk.preloader.read32(pos, rlen // 4)
									if res==[]:
										break
									print(hexlify(b"".join([pack("<I",val) for val in res])).decode('utf-8'))
	
							#for val in res:
							#    print(hex(val))
							if status != 0x0:
								self.error("Error on jumping to partition: " + self.eh.status(status))
							else:
								self.info("Jumping to partition ....")
							return
						mtk.port.close()
						sys.exit(0)
			if mtk.preloader.send_da(plstageaddr, len(pldata), 0x100, pldata):
				self.info(f"Sent stage2 to {hex(plstageaddr)}, length {hex(len(pldata))}")
				mtk.preloader.get_hw_sw_ver()
				if mtk.preloader.jump_da(plstageaddr):
					self.info(f"Jumped to stage2 at {hex(plstageaddr)}.")
					if os.path.basename(plstage) == "pl.bin":
						ack = unpack(">I", mtk.port.usbread(4))[0]
						if ack == 0xB1B2B3B4:
							self.info("Successfully loaded stage2")
							return
					else:
						self.info("Successfully loaded stage2, dis- and reconnect usb cable")
						time.sleep(2)
						ack = unpack(">I", mtk.port.usbread(4))[0]
						mtk.port.close()
						return
				else:
					self.error("Error on jumping to pl")
					return
			else:
				self.error("Error on sending pl")
				return
			self.close()
		elif command == "peek":
			addr = getint(self.args.address)
			length = getint(self.args.length)
			preloader = self.args.preloader
			filename = self.args.filename
			self.cmd_peek(mtk=mtk, addr=addr, length=length, preloader=preloader, filename=filename)
			self.close()
		elif command == "stage":
			filename = self.args.filename
			stage2addr = self.args.stage2addr
			if self.args.stage2addr is not None:
				stage2addr = getint(self.args.stage2addr)
			stage2file = self.args.stage2
			verifystage2 = self.args.verifystage2
	
			self.cmd_stage(mtk=mtk, filename=filename, stage2addr=stage2addr, stage2file=stage2file,
						   verifystage2=verifystage2)
			self.close()
		elif command == "payload":
			payloadfile = self.args.payload
			self.cmd_payload(mtk=mtk, payloadfile=payloadfile)
			self.close()
		elif command == "gettargetconfig":
			if mtk.preloader.init():
				self.info("Getting target info...")
				mtk.preloader.get_target_config()
			mtk.port.close()
			self.close()
		elif command == "logs":
			if self.args.filename is None:
				filename = "log.txt"
			else:
				filename = self.args.filename
			self.cmd_log(mtk=mtk, filename=filename)
			mtk.port.close()
			self.close()
		elif command == "meta":
			meta = META(mtk)
			if self.args.metamode is None:
				self.error("You need to give a metamode as argument ex: " + metamodes)
			else:
				if meta.init(metamode=self.args.metamode, display=True):
					self.info(f"Successfully set meta mode : {self.args.metamode}")
			mtk.port.close()
			self.close()
		elif command == "gpt_2":
			if self.args.action == 'print':
				logger.debug(f"{command} action is print")
				import mtkh_modules.actions.gpt.action_gpt_print
			else:
				logger.error(f"Wrong action for {command}: {self.args.action}")
			self.close()
		else:
			# DA / FLash commands start here
			logger.debug(f"Else command is {command}")
			try:
				preloader = self.args.preloader
				logger.debug(f"preloader is {preloader}")
			except:
				preloader = None
			download_agent = MTKH_DA(mtk)
			#
			mtk = download_agent.configure(mtk, preloader)
			# logger.exit()
			if mtk is not None:
				download_agent.handle_da_cmds(mtk, command, self.args)
			else:
				self.close()
	
