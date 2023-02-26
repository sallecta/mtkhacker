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
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		if arg_opt == 'sameline':
			print(f"{n}:info:{f}:{m}[{l}]: {arg_msg}", end='\r')
		else:
			print(f"\n{n}:info:{f}:{m}[{l}]: \n  {arg_msg}\n")
		sys.stdout.flush()
	
	def debug(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"\n{this.cyan}{n}:debug{this.end}:{f}:{m}[{l}]: \n  {arg_msg}\n")
		sys.stdout.flush()
	
	def warning(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"\n{this.yellow}{n}:warning{this.end}:{f}:{m}[{l}]: \n  {arg_msg}\n")
		sys.stdout.flush()
	
	def error(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"\n{this.red}{n}:error{this.end}:{f}:{m}[{l}]: \n  {arg_msg}\n")
		sys.stdout.flush()
	
	def critical(arg_msg, arg_opt=None):
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"\n{this.redbold}{n}:critical{this.end}:{f}:{m}[{l}]: \n  {arg_msg}\n")
		sys.stdout.flush()
	
	def exit(arg_msg=None, arg_opt=None):
		msg = "Exit by developer"
		if arg_msg != None:
			msg = msg + ". " + arg_msg
		frameinfo = getframeinfo(stack()[1][0])
		n = mtkhacker_meta.name
		f = os.path.basename(os.path.splitext(frameinfo.filename)[0])
		m = frameinfo.function
		l = frameinfo.lineno
		this=MTKH_logger
		print(f"\n{this.yellowbold}{n}{this.end}:{f}:{m}[{l}]: \n  {msg}\n")
		sys.stdout.flush()
		sys.exit(0)
	
