#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import os
import sys
import logging
import time
from binascii import hexlify
from struct import pack
from mtkhacker_modules.path_module import MTKH_path as mtkhacker_path
from mtkclient.Library.Connection.usblib import usb_class
from mtkclient.Library.Connection.seriallib import serial_class
from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger

class MTKHhacker_connect:
	class deviceclass:
		vid = 0
		pid = 0

		def __init__(self, vid, pid):
			self.vid = vid
			self.pid = pid

	def __init__(self, mtk, portconfig, serialportname:str=None):
		self.config = mtk.config
		self.mtk = mtk
		self.serialportname = None
		if serialportname is not None:
			print("!? serialportname is not None="+serialportname)
			self.cdc = serial_class(portconfig=portconfig, devclass=10)
			self.cdc.setportname(serialportname)
		else:
			self.cdc = usb_class(portconfig=portconfig, devclass=10)
		self.usbread = self.cdc.usbread
		self.usbwrite = self.cdc.usbwrite
		self.close = self.cdc.close
		self.rdword = self.cdc.rdword
		self.rword = self.cdc.rword
		self.rbyte = self.cdc.rbyte
		self.detectusbdevices = self.cdc.detectdevices
		self.usbreadwrite = self.cdc.usbreadwrite

	def run_handshake(self):
		EP_OUT = self.cdc.EP_OUT.write
		EP_IN = self.cdc.EP_IN.read
		maxinsize = self.cdc.EP_IN.wMaxPacketSize

		i = 0
		startcmd = b"\xa0\x0a\x50\x05"
		length = len(startcmd)
		try:
			while i < length:
				if EP_OUT(int.to_bytes(startcmd[i], 1, 'little')):
					v = EP_IN(maxinsize)
					if len(v) == 1 and v[0] == ~(startcmd[i]) & 0xFF:
						i += 1
					else:
						i = 0
			logger.info("Device detected :)")
			return True
		except Exception as serr:
			logger.error(f"Defice detection error: {str(serr)}")
			time.sleep(0.005)
		return False

	def handshake(self, maxtries=None, loop=0):
		counter = 0
		logger.info("\n\n  "+\
				"Hint:\n\n" + \
				"    Power off the phone before connecting.\n\n" + \
				"    For BROM mode, press and hold vol up, vol dwn, \n" + \
				"      or all hw buttons and connect usb.\n\n" +
				"    For Preloader mode, don't press any hw button \n" + \
				"      and connect usb.\n"
				"    If it is already connected and on, \n" + \
				"      hold power for 10 seconds to reset.\n"
				)
		while not self.cdc.connected:
			if maxtries is not None and counter == maxtries:
				break
			counter += 1
			logger.info(f"Connection attempt No {counter}", 'sameline')
			self.cdc.connected = self.cdc.connect()
			if self.cdc.connected and self.run_handshake():
				logger.info(f"Connected at attempt No {counter}")
				return True
			time.sleep(1)
		
		logger.info(f"Failed to connect at attempt No {counter}")
		return False

	def mtk_cmd(self, value, bytestoread=0, nocmd=False):
		response = b""
		dlen = len(value)
		success = self.usbwrite(value)
		time.sleep(0.05)
		if success:
			if nocmd:
				cmdrsp = self.usbread(bytestoread)
				return cmdrsp
			else:
				cmdrsp = self.usbread(dlen)
				if cmdrsp[0] is not value[0]:
					logger.error("Cmd error :" + hexlify(cmdrsp).decode('utf-8'))
					return -1
				if bytestoread > 0:
					response = self.usbread(bytestoread)
				return response
		else:
			logger.warning("Couldn't send :" + hexlify(value).decode('utf-8'))
			return response

	def echo(self, data):
		if isinstance(data, int):
			data = pack(">I", data)
		if isinstance(data, bytes):
			data = [data]
		for val in data:
			self.usbwrite(val)
			tmp = self.usbread(len(val), maxtimeout=0)
			# print(hexlify(tmp))
			if val != tmp:
				return False
		return True
