import inspect
from management_tools import loggers
import os
from computer import Computer


class Model(object):

    def __init__(self, server):
        self.jss_server = server
        self.computer = Computer()

        self.incorrect_barcode = None
        self.incorrect_asset = None
        self.incorrect_name = None
        self.incorrect_serial = None

        self.search_param = None
        self.jss_id = None

        self.proceed = False

        self.final_tugboat_fields = None

        self.barcode_var = None

        self.barcode = None
        self.asset = None
        self.asset_chkbtn = None
        self.asset_entry = None
        self.name = None
        self.serial = None


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)