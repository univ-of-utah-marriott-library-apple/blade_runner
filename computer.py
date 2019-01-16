import os
import subprocess
from management_tools import loggers
import re
import inspect

class Computer(object):
    def __init__(self):
        self.serial_number = None
        self.jss_id = None
        self.barcode_1 = None
        self.barcode_2 = None
        self.asset_tag = None
        self.name = None
        self.prev_computer_name = None
        self.needs_enroll = None
        self.incorrect_barcode_1 = None
        self.incorrect_barcode_2 = None
        self.incorrect_asset = None
        self.incorrect_serial = None
        self.prev_barcode_1 = None
        self.prev_barcode_2 = None
        self.prev_asset_tag = None
        self.prev_name = None

    def get_serial(self):
        """Gets and returns serial number from the computer"""
        logger.info("get_serial" + ": activated")

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets raw data that contains the serial number
        serial_request_raw = subprocess.check_output(["system_profiler", "SPHardwareDataType"])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets serial number from the raw data
        serial_number_local = re.findall('Serial Number .system.: (.*)', serial_request_raw)[0]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info("get_serial" + ": succeeded")
        return serial_number_local


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)
