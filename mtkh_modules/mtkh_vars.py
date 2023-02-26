from PySide6.QtCore import (QObject)

from mtkh_modules.errors.mtkh_errors import MTKH_errors
from mtkh_modules.path.mtkh_path import MTKH_path

import sys
class MTKH_vars:
	args = None
	usb_retry_delay = 2 # seconds
	usb = None
	partition = None
	gui = None
	guiprogress = None
	update_status_text = None
	tr = QObject().tr
	if sys.platform.startswith('darwin'):
		bootrom_exploit = "kamakiri"
	else:
		bootrom_exploit = "kamakiri2"
	errors = MTKH_errors()
	path = MTKH_path()
	
