import json
import os.path
from binascii import hexlify
from mtkh_modules.path.mtkh_path import MTKH_path as mtkhacker_path

class MTKHhacker_hwparam:
	paramsetting = None
	hwcode = None
	
	def __init__(self, arg_meid:str):
		if isinstance(arg_meid,bytearray) or isinstance(arg_meid,bytes):
			arg_meid=hexlify(arg_meid).decode('utf-8')
		if arg_meid is None:
			self.paramsetting = {}
			if arg_meid is not None:
				self.paramsetting["arg_meid"] = arg_meid
				if not os.path.exists(mtkhacker_path.logs):
					os.mkdir(mtkhacker_path.logs)
			open(mtkhacker_path.hwparamfile, "w").write(json.dumps(self.paramsetting))
		else:
			self.paramsetting = {}
			if os.path.exists(mtkhacker_path.hwparamfile):
				try:
					self.paramsetting = json.loads(open(mtkhacker_path.hwparamfile, "r").read())
				except:
					#json file invalid, load nothing.
					pass
	
	
	def loadsetting(self,key:str):
		if self.paramsetting is not None:
			if key in self.paramsetting:
				return self.paramsetting[key]
		return None
	
	def writesetting(self, key:str,value:str):
		if self.paramsetting is not None:
			self.paramsetting[key]=value
			self.write_json()
	
	def write_json(self):
		if self.paramsetting is not None:
			if not os.path.exists(mtkhacker_path.logs):
				os.mkdir(mtkhacker_path.logs)
			open(mtkhacker_path.hwparamfile, "w").write(json.dumps(self.paramsetting))
