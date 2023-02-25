class MTKH_USB_vars:
	#idVendor, idProduct, interface
	default_ids = [
		[0x0E8D, 0x0003, -1],	# MTK BROM
		[0x0E8D, 0x6000, 2],	# MTK Preloader
		[0x0E8D, 0x2000, -1],	# MTK Preloader
		[0x0E8D, 0x2001, -1],	# MTK Preloader
		[0x0E8D, 0x20FF, -1],	# MTK Preloader
		[0x1004, 0x6000, 2],	# LG Preloader
		[0x22d9, 0x0006, -1],	# OPPO Preloader
		[0x0FCE, 0xF200, -1],	# Sony BROM
		[0x0FCE, 0xD1E9, -1],	# Sony BROM XA1
		[0x0FCE, 0xD1E2, -1],	# Sony BROM
		[0x0FCE, 0xD1EC, -1],	# Sony BROM L1
	]
	
	usb_ids = {
		1  : {'vendor': 0x0E8D, 'product': 0x0003, 'interface':  -1 },
		2  : {'vendor': 0x0E8D, 'product': 0x6000, 'interface':   2 },
		3  : {'vendor': 0x0E8D, 'product': 0x2000, 'interface':  -1 },
		4  : {'vendor': 0x0E8D, 'product': 0x2001, 'interface':  -1 },
		5  : {'vendor': 0x0E8D, 'product': 0x20FF, 'interface':  -1 },
		6  : {'vendor': 0x1004, 'product': 0x6000, 'interface':   2 },
		7  : {'vendor': 0x22d9, 'product': 0x0006, 'interface':  -1 },
		8  : {'vendor': 0x0FCE, 'product': 0xF200, 'interface':  -1 },
		9  : {'vendor': 0x0FCE, 'product': 0xD1E9, 'interface':  -1 },
		10 : {'vendor': 0x0FCE, 'product': 0xD1E2, 'interface':  -1 },
		11 : {'vendor': 0x0FCE, 'product': 0xD1EC, 'interface':  -1 }
	}
