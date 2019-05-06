#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: March 2019
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, and that the name of The University
# of Utah not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission. This software is supplied as is without expressed or
# implied warranties of any kind.
################################################################################

import re
import os
import inspect
import subprocess

from management_tools import loggers


class Computer(object):
    """Stores information about about a computer

    Attributes
        serial_number (str): Serial number of the computer
        jss_id (int): JSS ID of the computer
        barcode_1 (str): Barcode 1 of the computer
        barcode_2 (str): Barcode 2 of the computer
        asset_tag (str): Asset tag of the computer
        name (str): Name of the computer
        jss_name (str): JSS extension attribute
        incorrect_barcode_1 (str): Incorrect barcode 1
        incorrect_barcode_2 (str): Incorrect barcode 2
        incorrect_asset (str): Incorrect asset tag
        incorrect_serial (str): Incorrect serial number
        jss_barcode_1 (str): Barcode 1 record from JSS
        jss_barcode_2 (str): Barcode 2 record from JSS
        jss_asset_tag (str): Asset tag record from JSS
        jss_serial_number (str): Serial number record from JSS

    """
    def __init__(self):
        """ Initialize the Computer object. Stores information relative to the computer.

        Intended to be used as the model of the computer that Blade-Runner is running on.
        """
        self.serial_number = None
        self.jss_id = None
        self.barcode_1 = None
        self.barcode_2 = None
        self.asset_tag = None
        self.name = None
        self.incorrect_barcode_1 = None
        self.incorrect_barcode_2 = None
        self.incorrect_asset = None
        self.incorrect_serial = None
        self.jss_barcode_1 = None
        self.jss_barcode_2 = None
        self.jss_asset_tag = None
        self.jss_serial_number = None
        self.jss_name = None

    def get_serial(self):
        """Gets and returns serial number from the computer"""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info("get_serial" + ": activated")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets raw data that contains the serial number
        serial_request_raw = subprocess.check_output(["system_profiler", "SPHardwareDataType"])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets serial number from the raw data
        serial = re.findall('Serial Number .system.: (.*)', serial_request_raw)[0]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info("get_serial" + ": succeeded")
        return serial

# Start logging.
cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))
