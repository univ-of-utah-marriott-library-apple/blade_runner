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


import os
import sys
import logging
import unittest
import subprocess
import Tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from blade_runner.jamf_pro.jss_server import JssServer
from blade_runner.controllers.verification_controller import VerificationController
from blade_runner.jamf_pro.computer import Computer
from blade_runner.jamf_pro.params import VerifyParams, SearchParams

logging.getLogger(__name__).addHandler(logging.NullHandler())


class TestVerificationController(unittest.TestCase):
    """Test the GUI and the server manually."""

    def setUp(self):
        self.jamf = JssServer()

        self.vc = None
        self.root = tk.Tk()
        self.comp = Computer()

        self.vp_dict = {'barcode_1': 'True','barcode_2': 'True','asset_tag': 'True','computer_name': 'True'}
        self.vp = VerifyParams(self.vp_dict)

        self.sp_dict = {'barcode_1': 'True','barcode_2': 'True','asset_tag': 'True','serial_number': 'True'}
        self.sp = SearchParams(self.sp_dict)

    def tearDown(self):
        self.root.destroy()

    def test_store_user_entries(self):
        # Populate Computer.
        self.comp.barcode_1 = "bc1"
        self.comp.barcode_2 = "bc2"
        self.comp.asset_tag = "asset"
        self.comp.serial_number = "serial"
        self.comp.name = "name"

        # Instantiate verification controller.
        self.vc = VerificationController(self.root, self.comp, self.vp, self.sp)

        # Remove entry values filled by Computer
        self.vc.entry_view.barcode_1_entry.delete(0, "end")
        self.vc.entry_view.barcode_2_entry.delete(0, "end")
        self.vc.entry_view.asset_entry.delete(0, "end")
        self.vc.entry_view.name_entry.delete(0, "end")


        new_bc1 = "new_bc1"
        new_bc2 = "new_bc2"
        new_asset = "new_asset"
        new_name = "new_name"

        # Fill entries with new data
        self.vc.entry_view.barcode_1_entry.insert(0, new_bc1)
        self.vc.entry_view.barcode_2_entry.insert(0, new_bc2)
        self.vc.entry_view.asset_entry.insert(0, new_asset)
        self.vc.entry_view.name_entry.insert(0, new_name)

        # Store the data
        self.vc._store_user_entries()

        # Assert that stored data is the same as the new data.
        self.assertEqual(new_bc1, self.comp.barcode_1)
        self.assertEqual(new_bc2, self.comp.barcode_2)
        self.assertEqual(new_asset, self.comp.asset_tag)
        self.assertEqual(new_name, self.comp.name)

    def test_fill_user_entries_when_computer_attrs_are_none(self):
        # Instantiate vc with a Computer whose attributes are None.
        self.vc = VerificationController(self.root, self.comp, self.vp, self.sp)

        # Assert that getting None results in empty string.
        self.assertEqual("", self.vc.entry_view.barcode_1_entry.get())
        self.assertEqual("", self.vc.entry_view.barcode_2_entry.get())
        self.assertEqual("", self.vc.entry_view.asset_entry.get())
        self.assertEqual("", self.vc.entry_view.name_entry.get())

    def test_fill_user_entries(self):
        # Setup Computer
        self.comp.barcode_1 = "bc1"
        self.comp.barcode_2 = "bc2"
        self.comp.asset_tag = "asset"
        self.comp.name = "name"

        # Instantiate vc
        self.vc = VerificationController(self.root, self.comp, self.vp, self.sp)

        # Assert that vc filled the entries with the data from Computer.
        self.assertEqual("bc1", self.vc.entry_view.barcode_1_entry.get())
        self.assertEqual("bc2", self.vc.entry_view.barcode_2_entry.get())
        self.assertEqual("asset", self.vc.entry_view.asset_entry.get())
        self.assertEqual("name", self.vc.entry_view.name_entry.get())


if __name__ == "__main__":
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set up logging vars.
    fmt = '%(asctime)s %(process)d: %(levelname)8s: %(name)s.%(funcName)s: %(message)s'
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_dir = os.path.join(os.path.expanduser("~"), "Library/Logs/Blade Runner")
    filepath = os.path.join(log_dir, script_name + ".log")

    # Create log path
    try:
        os.mkdir(log_dir)
    except OSError as e:
        if e.errno != 17:
            raise e

    # Ensure that the owner is the logged in user.
    subprocess.check_output(['chown', '-R', os.getlogin(), log_dir])

    # Set up logger.
    logging.basicConfig(level=logging.DEBUG, format=fmt, filemode='a', filename=filepath)
    logger = logging.getLogger(script_name)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Start unit tests.
    unittest.main(verbosity=2)
