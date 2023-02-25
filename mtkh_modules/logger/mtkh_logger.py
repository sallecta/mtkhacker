from mtkhacker_modules.meta_module import MTKHhacker_meta as mtkhacker_meta
from inspect import getframeinfo, stack
import os
import sys

# Usage
# from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
# logger.info('logger message')
# logger.debug('logger message')
# logger.warning('logger message')
# logger.error('logger message')
# logger.critical('logger message')


class MTKH_logger:
	red = '\033[31m'
	redbold = '\033[1;31;40m'
	green = '\033[32m'
	yellow = '\033[33m'
	yellowbold = '\033[1;33;40m'
	cyan = '\033[36m'
	end = '\033[m'
	level = 'DEBUG'
	DEBUG = 'DEBUG'
	INFO = 'INFO'
	WARNING = 'WARNING'
	ERROR = 'ERROR'
	CRITICAL='CRITICAL'
	def info(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		if arg_opt == 'sameline':
			print(f"{n}:info:{f}[{l}]: {arg_msg}", end='\r')
		else:
			print(f"{n}:info:{f}[{l}]: {arg_msg}")
		sys.stdout.flush()
	
	def debug(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"{this.cyan}{n}:debug{this.end}:{f}[{l}]: {arg_msg}")
		sys.stdout.flush()
	
	def warning(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"{this.yellow}{n}:warning{this.end}:{f}[{l}]: {arg_msg}")
		sys.stdout.flush()
	
	def error(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"{this.red}{n}:error{this.end}:{f}[{l}]: {arg_msg}")
		sys.stdout.flush()
	
	def critical(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"{this.redbold}{n}:critical{this.end}:{f}[{l}]: {arg_msg}")
		sys.stdout.flush()
	
	def exit(arg_msg=None, arg_opt=None):
		msg = "Exit by developer"
		if arg_msg != None:
			msg = msg + ". " + arg_msg
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"{this.yellowbold}{n}{this.end}:{f}[{l}]: {msg}")
		sys.stdout.flush()
		sys.exit(0)
	
