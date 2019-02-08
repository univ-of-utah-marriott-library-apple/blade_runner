#!/usr/bin/python

'''pytests for offboard_tool.py. Must be run as root. Run unittest by cd into working directory and running:

    python -m unittest test_offboard_tool

'''

import unittest
import os
import socket
import subprocess
import sys
import re
from management_tools import loggers
import urllib2
import xml.etree.cElementTree as ET
import base64
import hashlib
import plistlib
import json
from Tkinter import *
import time
import webbrowser
from pprint import pprint
import re
from management_tools.slack import IncomingWebhooksSender as IWS
from jss_server import JssServer
import inspect
import Tkinter as tk
from main_controller import MainController

class TestBladeRunner(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cf = inspect.currentframe()

        root = tk.Tk()
        root.withdraw()

        abs_file_path = inspect.getframeinfo(cf).filename
        blade_runner_dir = os.path.dirname(abs_file_path)
        jss_server_plist = os.path.join(blade_runner_dir, "private/test_jss_server_config.plist")
        jss_server_data = plistlib.readPlist(jss_server_plist)
        cls.jss_server = JssServer(**jss_server_data)

        slack_plist = os.path.join(blade_runner_dir, "private/test_slack_config.plist")
        slack_data = plistlib.readPlist(slack_plist)
        current_ip = socket.gethostbyname(socket.gethostname())
        bot = IWS(slack_data['slack_url'], bot_name=current_ip, channel=slack_data['slack_channel'])

        offboard_config = "private/test_offboard_config.xml"

        verify_config = os.path.join(blade_runner_dir, "private/test_verify_config.plist")
        verify_data = plistlib.readPlist(verify_config)

        search_params_config = os.path.join(blade_runner_dir, "private/test_search_params_config.plist")
        search_params = plistlib.readPlist(search_params_config)

        cls.main_vc = MainController(root, cls.jss_server, slack_data, verify_data, search_params)
        cls.main_vc.computer.serial = cls.main_vc.computer.get_serial()
        # cls.main_vc.run()



    @unittest.skip("Takes a little time.")
    def test_enroll(self):
        '''Enrolls computer'''
        enrolled = self.jss_server.enroll_computer()
        self.assertTrue(enrolled)

    @unittest.skip("Takes a little time.")
    def test_return_jss_match(self):
        jss_ID = self.jss_server.match(self.serial)
        self.assertIsNotNone(jss_ID)

    @unittest.skip("Takes a little time.")
    def test_get_tugboat_fields(self):
        tugboat_fields = self.jss_server.get_tugboat_fields(self.jss_ID)

    @unittest.skip("Takes a little time.")
    def test_get_offboard_fields(self):
        pass
        #ot.get_offboard_fields(self.jss_ID)

    # @unittest.skip("Takes a little time.")
    def test_whole_process(self):
        self.main_vc.run()
        # self.main_vc.serial_input()




if __name__ == '__main__':
    unittest.main(verbosity=1)
