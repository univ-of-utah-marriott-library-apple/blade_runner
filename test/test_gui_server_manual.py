#!/usr/bin/python

import os
import sys
import inspect
import unittest
import plistlib
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "blade_runner/dependencies"))
from blade_runner.jamf_pro.jss_server import JssServer
from blade_runner.controllers.main_controller import MainController


class TestGUIServerManual(unittest.TestCase):

    def setUp(self):
        cf = inspect.currentframe()

        root = tk.Tk()
        root.withdraw()

        abs_file_path = inspect.getframeinfo(cf).filename
        self.blade_runner_dir = os.path.dirname(abs_file_path)
        jss_server_plist = os.path.join(self.blade_runner_dir, "private/jamf_pro_configs/jamf_pro.plist")
        jss_server_data = plistlib.readPlist(jss_server_plist)
        jss_server = JssServer(**jss_server_data)

        self.slack_plist = os.path.join(self.blade_runner_dir, "private/slack_configs/slack.plist")
        self.slack_data = plistlib.readPlist(self.slack_plist)

        self.verify_config = os.path.join(self.blade_runner_dir, "private/verify_params_configs/verify_params.plist")
        self.verify_data = plistlib.readPlist(self.verify_config)

        self.search_params_config = os.path.join(self.blade_runner_dir, "private/search_params_configs/search_params.plist")
        self.search_params = plistlib.readPlist(self.search_params_config)

        self.br = MainController(root, jss_server, self.slack_data, self.verify_data, self.search_params)

    def test_manual(self):
        self.br.run()


if __name__ == "__main__":
    unittest.main(verbosity=2)
