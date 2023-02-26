from mtkh_modules.mtkh_vars import MTKH_vars as vars

#from mtkh_modules.chip.mtkh_chip import MTKH_chip

from mtkh_modules.chip.mtkh_chip_defs import MTKH_chip_defs
from mtkh_modules.chip.mtkh_chip_efuses import MTKH_chip_efuses

class MTKH_chip:
	defs = MTKH_chip_defs()
	efuses =  MTKH_chip_efuses()
	#
	var1 = None
	watchdog = None
	uart = None
	brom_payload_addr = None
	da_payload_addr = None
	pl_payload_addr = None
	cqdma_base = None
	sej_base = None
	dxcc_base = None
	gcpu_base = None
	ap_dma_mem = None
	name = ""
	description = ""
	da_code = None
	meid_addr = None
	socid_addr = None
	blacklist = None
	blacklist_count = None
	send_ptr = None
	ctrl_buffer = ()
	cmd_handler = None
	brom_register_access = None
	da_mode = defs.da_modes.default
	loader = None
	prov_addr = None
	misc_lock = None
	efuse_addr = None
	#from Mtk_Config
	peek = None
	pid = -1
	cid = None
	vid = -1
	var1 = 0xA
	is_brom = False
	skipwdt = False
	interface = -1
	readsocid = False
	enforcecrash = False
	debugmode = False
	preloader = None
	preloader_filename = None
	payloadfile = None
	loader = None
	gpt_file = None
	generatekeys = None
	daconfig = None
	bmtflag = None
	bmtblockcount = None
	bmtpartsize = None
	packetsizeread = 0x400
	flashinfo = None
	readsize = 0
	sparesize = 16
	plcap = None
	blver = -2
	gcpu = None
	pagesize = 512
	SECTOR_SIZE_IN_BYTES = 4096  # fixme
	baudrate = 115200
	cpu = ""
	hwcode = None
	meid = None
	socid = None
	target_config = None
	gpt_settings = None
	hwparam = None
	sram = None
	dram = None
