import os
import subprocess
from management_tools import loggers
import re
import inspect

class Computer(object):
    def __init__(self):
        self.serial = None
        self.jss_id = None
        self.barcode = None
        self.asset = None
        self.name = None
        self.prev_name = None
        self.needs_enroll = None
        self.incorrect_barcode = None
        self.incorrect_asset = None
        self.incorrect_serial = None

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