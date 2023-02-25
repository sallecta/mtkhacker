import sys
import io
import usb.core
import usb.util

from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
from mtkh_modules.mtkh_vars import MTKH_vars as vars
from mtkh_modules.usb.mtkh_usb_vars import MTKH_USB_vars as usb_vars

# https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst
class MTKH_USB():#default_ids=default_ids,devclass=10
	
	device = None
	
	def __init__(self):
		static=MTKH_USB
		self.connected = False
		self.devclass = -1
		self.device = None
		self.configuration = None
		self.interface = -1
		self.endpoint_in = -1
		self.endpoint_out = -1
		self.backend = None
		self.__set_backend()
	
	def __set_backend(self):
		if sys.platform.startswith('freebsd') or sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
			self.backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.so")
		elif sys.platform.startswith('win32'):
			if calcsize("P") * 8 == 64:
				self.backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb-1.0.dll")
			else:
				self.backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb32-1.0.dll")
		if self.backend is not None:
			try:
				self.backend.lib.libusb_set_option.argtypes = [c_void_p, c_int]
				self.backend.lib.libusb_set_option(self.backend.ctx, 1)
			except:
				self.backend = None

	def handshake(self):
		return True
	
	def find(self):
		if self.connected:
			logger.debug("Allready connected, closing old connection...")
			# self.close()
			# self.connected = False
			# logger.debug("   done.")
		devices = usb.core.find(find_all=True, bDeviceClass=0x2, backend=self.backend)
		for dev in devices:
			logger.debug(f"v:p:: {hex(dev.idVendor)}:{hex(dev.idProduct)}")
			for key in usb_vars.usb_ids:
				stored = usb_vars.usb_ids[key]
				if dev.idVendor == stored['vendor'] and dev.idProduct == stored['product']:
					self.device = dev
					self.interface = stored['interface']
					logger.debug(f"Found device {hex(dev.idVendor)}:{hex(dev.idProduct)} of type {type(self.device)}")
					break
			if self.device is not None:
				break
		if self.device is None:
			return False 
		logger.debug(f"Found device {hex(self.device.idVendor)}:{hex(self.device.idProduct)} of type {type(self.device)}")
		try:
			self.configuration = self.device.get_active_configuration()
		except usb.core.USBError as e:
			logger.debug(f"Failed to get active usb configuration: {e}")
			if e.strerror == "Configuration not set":
				self.device.set_configuration()
				self.configuration = self.device.get_active_configuration()
			if e.errno == 13:
				logger.debug(f"USB backend fail: {e}")
				self.backend = usb.backend.libusb0.get_backend()
				self.device = usb.core.find(idVendor=self.vid, idProduct=self.pid, backend=self.backend)
		if self.configuration is None:
			logger.error("Couldn't get device configuration.")
			return False
		logger.debug("Got device configuration.")
		logger.debug(self.configuration)
		if self.interface == -1:
			logger.debug(f"Selecting interface from {self.configuration.bNumInterfaces} available")
			for interfacenum in range(0, self.configuration.bNumInterfaces):
				itf = usb.util.find_descriptor(self.configuration, bInterfaceNumber=interfacenum)
				if self.devclass != -1:
					if itf.bInterfaceClass == self.devclass:
						self.interface = interfacenum
						break
				else:
					self.interface = interfacenum
					break
		if self.interface > self.configuration.bNumInterfaces:
			logger.error(f"Invalid interface, max number is {self.configuration.bNumInterfaces}.")
			return False
		if self.interface != -1:
			logger.debug(f"Found interface {hex(self.interface)}")
			itf = usb.util.find_descriptor(self.configuration, bInterfaceNumber=self.interface)
			try:
				if self.device.is_kernel_driver_active(0):
					logger.debug("Kernel driver is active, detaching...")
					self.device.detach_kernel_driver(0)
			except Exception as err:
				logger.error("No kernel driver supported: " + str(err))
			try:
				usb.util.claim_interface(self.device, 0)
			except Exception as err:
				logger.error("claim_interface failed: " + str(err))
				return False
			
			try:
				if self.device.is_kernel_driver_active(self.interface):
					logger.debug("Detaching kernel driver")
					self.device.detach_kernel_driver(self.interface)
			except Exception as err:
				logger.error("  ...failed: " + str(err))
			try:
				if self.interface != 0:
					usb.util.claim_interface(self.device, self.interface)
			except Exception as err:
				logger.error("claim_interface failed: " + str(err))
			
			if self.endpoint_out == -1:
				self.endpoint_out = usb.util.find_descriptor(itf,
													   # match the first OUT endpoint
													   custom_match=lambda e: \
														   usb.util.endpoint_direction(e.bEndpointAddress) ==
														   usb.util.ENDPOINT_OUT)
			if self.endpoint_in == -1:
				self.endpoint_in = usb.util.find_descriptor(itf,
													  # match the first OUT endpoint
													  custom_match=lambda e: \
														  usb.util.endpoint_direction(e.bEndpointAddress) ==
														  usb.util.ENDPOINT_IN)
			self.connected = True
			return True
		logger.error("Couldn't find CDC interface. Aborting.")
		self.connected = False
		return False
