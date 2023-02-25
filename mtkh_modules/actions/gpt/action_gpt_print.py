import time
import sys

from mtkh_modules.logger.mtkh_logger import MTKH_logger as logger
from mtkh_modules.mtkh_vars import MTKH_vars as vars
from mtkh_modules.usb.mtkh_usb import MTKH_USB
from mtkh_modules.partition.mtkh_partition import MTKH_Partition
logger.debug('hi')

vars.usb = MTKH_USB()

counter = 0
maxtries=None
loop=0
logger.info("\n\n  "+\
		"Finding MTK Device in connected USB devices.\n\n" +\
		"  Hint:\n\n" + \
		"    Power off the phone before connecting.\n\n" + \
		"    For BROM mode, press and hold vol up, vol dwn, \n" + \
		"      or all hw buttons and connect usb.\n\n" +
		"    For Preloader mode, don't press any hw button \n" + \
		"      and connect usb.\n"
		"    If it is already connected and on, \n" + \
		"      hold power for 10 seconds to reset.\n"
		)
while not vars.usb.connected:
	if maxtries is not None and counter == maxtries:
		break
	counter += 1
	logger.info(f"Connection attempt No {counter}", 'sameline')
	vars.usb.find()
	if vars.usb.connected and vars.usb.handshake():
		logger.info(f"Connected at attempt No {counter}")
		break
	time.sleep(vars.usb_retry_delay)

logger.info(f"Done.")
vars.partition = MTKH_Partition()
data, guid_gpt = vars.partition.gpt.get()

