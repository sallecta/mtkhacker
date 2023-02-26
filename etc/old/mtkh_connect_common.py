# del this

import serial
import serial.tools.list_ports
import inspect
import traceback
from binascii import hexlify

from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
from mtkclient.Library.utils import *


class MTKH_connect_common:

	def __init__(self, portconfig=None, devclass=-1):
		self.connected = False
		self.timeout = 1000
		self.maxsize = 512
		self.vid = None
		self.pid = None
		self.stopbits = None
		self.databits = None
		self.parity = None
		self.baudrate = None
		self.configuration = None
		self.device = None
		self.devclass = devclass
		# self.xmlread = True
		self.portname = None
	
	def read(self, length=None, timeout=-1):
		if timeout == -1:
			timeout = self.timeout
		if length is None:
			length = self.maxsize
		return self.usbread(length, timeout)



