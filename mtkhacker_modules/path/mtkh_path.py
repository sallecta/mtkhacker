#!/usr/bin/env python3

import os

class MTKH_path:
	def __init__(self, arg_path_file=None):
		if arg_path_file: #class static variables
			if not hasattr(MTKH_path, 'main'):
				MTKH_path.main = os.path.dirname(os.path.realpath(arg_path_file))
			if not hasattr(MTKH_path, 'images'): 
				MTKH_path.images = os.path.join(MTKH_path.main, "media", "images", "gui")
			if not hasattr(MTKH_path, 'preloaders'): 
				MTKH_path.preloaders = os.path.join(MTKH_path.main, "media", "mtk", "preloaders")
			if not hasattr(MTKH_path, 'loaders'): 
				MTKH_path.loaders = os.path.join(MTKH_path.main, "media", "mtk", "loaders")
			if not hasattr(MTKH_path, 'payloads'): 
				MTKH_path.payloads = os.path.join(MTKH_path.main, "media", "mtk", "payloads")
			if not hasattr(MTKH_path, 'logs'): 
				MTKH_path.logs = os.path.join(MTKH_path.main, "logs")
			#files
			if not hasattr(MTKH_path, 'devicefile'): 
				MTKH_path.devicefile = os.path.join(MTKH_path.logs, "device.txt")
			if not hasattr(MTKH_path, 'hwparamfile'): 
				MTKH_path.hwparamfile = os.path.join(MTKH_path.logs, "hwparam.json")
			#
		if not hasattr(MTKH_path, 'main'):
			  raise Exception("MTKH_path class first instantiation must be with current application path in main app file, like somevar = MTKH_path(__file__)") 
	
	def __static_variables_check(arg_static_var):
		print('emm')
	
	def bname(arg_path):
		return os.basename(arg_path)
