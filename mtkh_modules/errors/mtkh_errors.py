from mtkh_modules.errors.mtkh_errors_default import MTKH_errors_default
from mtkh_modules.errors.mtkh_errors_xflash import MTKH_errors_XFlash

class MTKH_errors:
	def __init__(self):
		this = MTKH_errors
		this.ec = MTKH_errors_default
		this.xec = MTKH_errors_XFlash
	
	def get(self, arg_error):
		if arg_error in this.ec:
			return this.ec[arg_error] + " (" + hex(arg_error) + ")"
		if arg_error in self.xec:
			return this.xec[arg_error] + " (" + hex(arg_error) + ")"
		return "Unknown error: " + hex(arg_error)
