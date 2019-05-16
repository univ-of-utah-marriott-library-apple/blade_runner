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

"""
How to run:

    sudo python test/test_gui_server_manual.py

Current working directory must be Blade Runner.

"""

import os
import sys
import inspect
import logging
import plistlib
import unittest
import Tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "blade_runner/dependencies"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "blade_runner/slack"))

from blade_runner.jamf_pro.jss_server import JssServer
from blade_runner.controllers.main_controller import MainController

logging.getLogger(__name__).addHandler(logging.NullHandler())


class TestGUIServerManual(unittest.TestCase):

    def setUp(self):
        if os.geteuid() != 0:
            raise SystemExit("Blade Runner must be run as root.")

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

        self.jamf_pro_doc_config = os.path.join(self.blade_runner_dir, "private/print_config/print.plist")
        self.doc_settings = plistlib.readPlist(self.jamf_pro_doc_config)

        self.br = MainController(root, jss_server, self.slack_data, self.verify_data, self.search_params, self.doc_settings)

    def test_manual(self):
        self.br.run()


if __name__ == "__main__":
    fmt = '%(asctime)s %(process)d: %(levelname)8s: %(name)s.%(funcName)s: %(message)s'
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_dir = os.path.join(os.path.expanduser("~"), "Library/Logs/Blade Runner")
    filepath = os.path.join(log_dir, script_name + ".log")
    try:
        os.mkdir(log_dir)
    except OSError as e:
        if e.errno != 17:
            raise e

    logging.basicConfig(level=logging.DEBUG, format=fmt, filemode='a', filename=filepath)
    logger = logging.getLogger(script_name)
    unittest.main(verbosity=2)
