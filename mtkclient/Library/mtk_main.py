#!/usr/bin/env python3
# MTK Flash Client (c) B.Kerler 2018-2021.
# Licensed under GPLv3 License
import os
import sys
import logging
import time
from binascii import hexlify
from struct import unpack, pack
from mtkclient.Library.mtk_class import Mtk
from mtkhacker_modules.path_module import MTKH_path
from mtkclient.Library.pltools import PLTools
from mtkclient.Library.meta import META
from mtkclient.Library.utils import getint
from mtkclient.config.mtk_config import Mtk_Config
from mtkclient.Library.utils import print_progress
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.gpt import gpt_settings
import argparse
metamodes = "[FASTBOOT, FACTFACT, METAMETA, FACTORYM, ADVEMETA, AT+NBOOT]"

class ArgHandler:
    def __init__(self, args, config):
        try:
            config.gpt_file = None
            if args.gpt_file is not None:
                if os.path.exists(args.gpt_file):
                    config.gpt_file = args.gpt_file
        except AttributeError:
            pass
        try:
            if args.vid is not None:
                config.vid = getint(args.vid)
        except AttributeError:
            pass
        try:
            if args.pid is not None:
                config.pid = getint(args.pid)
        except AttributeError:
            pass
        try:
            if args.payload is not None:
                config.payloadfile = args.payload
        except:
            pass
        try:
            if args.loader is not None:
                config.loader = args.loader
        except AttributeError:
            pass
        try:
            if args.da_address is not None:
                config.chipconfig.da_payload_addr = getint(args.da_address)
                self.info("O:DA offset:\t\t\t" + args.da_address)
        except AttributeError:
            pass
        try:
            if args.brom_address is not None:
                config.chipconfig.brom_payload_addr = getint(args.brom_address)
                self.info("O:Payload offset:\t\t" + args.brom_address)
        except AttributeError:
            pass
        try:
            if args.watchdog_address is not None:
                config.chipconfig.watchdog = getint(args.wdt)
                self.info("O:Watchdog addr:\t\t" + args.wdt)
        except AttributeError:
            pass
        try:
            if args.skipwdt is not None:
                config.skipwdt = args.skipwdt
        except AttributeError:
            pass
        try:
            if args.uart_address is not None:
                config.chipconfig.uart = getint(args.uart_address)
                self.info("O:Uart addr:\t\t" + args.uart_address)
        except AttributeError:
            pass
        try:
            if args.preloader is not None:
                config.chipconfig.var1 = getint(args.var1)
                self.info("O:Var1:\t\t" + args.var1)
        except AttributeError:
            pass
        try:
            if args.preloader is not None:
                if os.path.exists(args.preloader):
                    config.preloader_filename = args.preloader
                    config.preloader = open(config.preloader_filename,"rb").read()
        except AttributeError:
            pass
        try:
            if args.generatekeys is not None:
                config.generatekeys = args.generatekeys
        except AttributeError:
            pass
        try:
            if args.ptype is not None:
                config.ptype = args.ptype
        except AttributeError:
            pass
        try:
            if args.socid is not None:
                config.readsocid = args.socid
        except AttributeError:
            pass
        try:
            if args.crash is not None:
                config.enforcecrash = args.crash
        except AttributeError:
            pass

        gpt_num_part_entries = 0
        try:
            if args.gpt_num_part_entries is not None:
                gpt_num_part_entries = args.gpt_num_part_entries
        except:
            pass

        gpt_part_entry_size = 0
        try:
            if args.gpt_part_entry_size is not None:
                gpt_part_entry_size = args.gpt_part_entry_size
        except:
            pass

        gpt_part_entry_start_lba = 0
        try:
            if args.gpt_part_entry_start_lba is not None:
                gpt_part_entry_start_lba = args.gpt_part_entry_start_lba
        except:
            pass

        config.gpt_settings = gpt_settings(gpt_num_part_entries,gpt_part_entry_size,
                                         gpt_part_entry_start_lba)

