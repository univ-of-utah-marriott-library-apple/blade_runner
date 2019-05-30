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
from blade_runner.controllers.dual_verify_controller import DualVerifyController
from blade_runner.jamf_pro.computer import Computer
from blade_runner.jamf_pro.params import VerifyParams, SearchParams

logging.getLogger(__name__).addHandler(logging.NullHandler())


class TestDualVerificationController(unittest.TestCase):
    """Test the GUI and the server manually."""

    def setUp(self):
        self.jamf = JssServer()
        self.comp = Computer()

        self.test_bc1 = "test_bc1"
        self.test_bc2 = "test_bc2"
        self.test_asset = "test_asset"
        self.test_serial = "test_serial"
        self.test_name = "test_name"

        self.jss_bc1 = "jss_bc1"
        self.jss_bc2 = "jss_bc2"
        self.jss_asset = "jss_asset"
        self.jss_serial = "jss_serial"
        self.jss_name = "jss_name"

        self.jamf.get_barcode_1 = lambda comp: self.jss_bc1
        self.jamf.get_barcode_2 = lambda comp: self.jss_bc2
        self.jamf.get_asset_tag = lambda comp: self.jss_asset
        self.jamf.get_serial = lambda comp: self.jss_serial
        self.jamf.get_name = lambda comp: self.jss_name

        self.dvc = None
        self.root = tk.Tk()

        self.vp_dict = {'barcode_1': 'True','barcode_2': 'True','asset_tag': 'True','computer_name': 'True'}
        self.vp = VerifyParams(self.vp_dict)

        self.sp_dict = {'barcode_1': 'True','barcode_2': 'True','asset_tag': 'True','serial_number': 'True'}
        self.sp = SearchParams(self.sp_dict)

    def tearDown(self):
        self.root.destroy()

    def test_get_jss_data_fake_server(self):
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual(self.jss_bc1, self.comp.jss_barcode_1)
        self.assertEqual(self.jss_bc2, self.comp.jss_barcode_2)
        self.assertEqual(self.jss_asset, self.comp.jss_asset_tag)
        self.assertEqual(self.jss_serial, self.comp.jss_serial_number)
        self.assertEqual(self.jss_name, self.comp.jss_name)

    def test_store_conflicts_all_empty_string(self):
        self.comp.barcode_1 = ""
        self.comp.barcode_2 = ""
        self.comp.asset_tag = ""
        self.comp.serial_number = ""

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._store_conflicts(self.comp)

        self.assertIsNone(self.comp.incorrect_barcode_1)
        self.assertIsNone(self.comp.incorrect_barcode_2)
        self.assertIsNone(self.comp.incorrect_asset)
        self.assertIsNone(self.comp.incorrect_serial)

    def test_store_conflicts_all_none(self):
        self.comp.barcode_1 = None
        self.comp.barcode_2 = None
        self.comp.asset_tag = None
        self.comp.serial_number = None

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._store_conflicts(self.comp)

        self.assertIsNone(self.comp.incorrect_barcode_1)
        self.assertIsNone(self.comp.incorrect_barcode_2)
        self.assertIsNone(self.comp.incorrect_asset)
        self.assertIsNone(self.comp.incorrect_serial)

    def test_store_conflicts_all_conflicts(self):
        self.comp.barcode_1 = "diff_bc1"
        self.comp.barcode_2 = "diff_bc2"
        self.comp.asset_tag = "diff_asset"
        self.comp.serial_number = "diff_serial"

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._store_conflicts(self.comp)

        self.assertEqual(self.jss_bc1, self.comp.incorrect_barcode_1)
        self.assertEqual(self.jss_bc2, self.comp.incorrect_barcode_2)
        self.assertEqual(self.jss_asset, self.comp.incorrect_asset)
        self.assertEqual(self.jss_serial, self.comp.incorrect_serial)

    def test_store_conflicts_no_conflicts(self):
        self.comp.barcode_1 = self.jss_bc1
        self.comp.barcode_2 = self.jss_bc2
        self.comp.asset_tag = self.jss_asset
        self.comp.serial_number = self.comp.get_serial()

        self.jamf.get_serial = lambda comp: self.comp.get_serial()

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._store_conflicts(self.comp)

        self.assertIsNone(self.comp.incorrect_barcode_1)
        self.assertIsNone(self.comp.incorrect_barcode_2)
        self.assertIsNone(self.comp.incorrect_asset)
        self.assertIsNone(self.comp.incorrect_serial)

    def test_store_user_entries_all(self):
        self.comp.barcode_1 = "pre_b1"
        self.comp.barcode_2 = "pre_b2"
        self.comp.asset_tag = "pre_asset"
        self.comp.name = "pre_name"

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc.entry_view.barcode_1_entry.delete(0, "end")
        self.dvc.entry_view.barcode_2_entry.delete(0, "end")
        self.dvc.entry_view.asset_entry.delete(0, "end")
        self.dvc.entry_view.name_entry.delete(0, "end")

        self.dvc.entry_view.barcode_1_entry.insert(0, "post_b1")
        self.dvc.entry_view.barcode_2_entry.insert(0, "post_b2")
        self.dvc.entry_view.asset_entry.insert(0, "post_asset")
        self.dvc.entry_view.name_entry.insert(0, "post_name")

        self.dvc._store_user_entries(self.comp, self.vp)

        self.assertEqual("post_b1", self.comp.barcode_1)
        self.assertEqual("post_b2", self.comp.barcode_2)
        self.assertEqual("post_asset", self.comp.asset_tag)
        self.assertEqual("post_name", self.comp.name)

    def test_store_user_entries_all_none(self):
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertIsNone(self.comp.barcode_1)
        self.assertIsNone(self.comp.barcode_2)
        self.assertIsNone(self.comp.asset_tag)
        self.assertIsNone(self.comp.name)

    def test_store_user_entries_empty_string(self):
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._store_user_entries(self.comp, self.vp)

        self.dvc.entry_view.barcode_1_entry.insert(0, "")
        self.dvc.entry_view.barcode_2_entry.insert(0, "")
        self.dvc.entry_view.asset_entry.insert(0, "")
        self.dvc.entry_view.name_entry.insert(0, "")

        self.assertIsNone(self.comp.barcode_1)
        self.assertIsNone(self.comp.barcode_2)
        self.assertIsNone(self.comp.asset_tag)
        self.assertIsNone(self.comp.name)

    def test_fill_user_entries_all_none(self):
        # Instantiate vc with a Computer whose attributes are None.
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        # Assert that getting None results in empty string.
        self.assertEqual("", self.dvc.entry_view.barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.name_entry.get())

    def test_fill_user_entries_all_empty_string(self):
        self.comp.barcode_1 = ""
        self.comp.barcode_2 = ""
        self.comp.asset_tag = ""
        self.comp.serial_number = ""

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual("", self.dvc.entry_view.barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.name_entry.get())

    def test_fill_user_entries_all(self):
        self.comp.barcode_1 = self.test_bc1
        self.comp.barcode_2 = self.test_bc2
        self.comp.asset_tag = self.test_asset
        self.comp.name = self.test_name

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual(self.test_bc1, self.dvc.entry_view.barcode_1_entry.get())
        self.assertEqual(self.test_bc2, self.dvc.entry_view.barcode_2_entry.get())
        self.assertEqual(self.test_asset, self.dvc.entry_view.asset_entry.get())
        self.assertEqual(self.test_name, self.dvc.entry_view.name_entry.get())

    def test_fill_jss_entries_all(self):
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual(self.jss_bc1, self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual(self.jss_bc2, self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual(self.jss_asset, self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual(self.jss_name, self.dvc.entry_view.jss_name_entry.get())

    def test_fill_jss_entries_all_empty_string(self):
        self.jamf.get_barcode_1 = lambda comp: ""
        self.jamf.get_barcode_2 = lambda comp: ""
        self.jamf.get_asset_tag = lambda comp: ""
        self.jamf.get_serial = lambda comp: ""
        self.jamf.get_name = lambda comp: ""

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual("", self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_name_entry.get())

    def test_fill_jss_entries_all_none(self):
        self.jamf.get_barcode_1 = lambda comp: None
        self.jamf.get_barcode_2 = lambda comp: None
        self.jamf.get_asset_tag = lambda comp: None
        self.jamf.get_serial = lambda comp: None
        self.jamf.get_name = lambda comp: None

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.assertEqual("", self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_name_entry.get())

    def test_fill_jss_entry_all(self):
        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._fill_jss_entry(self.comp, "barcode_1")
        self.dvc._fill_jss_entry(self.comp, "barcode_2")
        self.dvc._fill_jss_entry(self.comp, "asset_tag")
        self.dvc._fill_jss_entry(self.comp, "name")

        self.assertEqual(self.jss_bc1, self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual(self.jss_bc2, self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual(self.jss_asset, self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual(self.jss_name, self.dvc.entry_view.jss_name_entry.get())

    def test_fill_jss_entry_all_none(self):
        self.jamf.get_barcode_1 = lambda comp: None
        self.jamf.get_barcode_2 = lambda comp: None
        self.jamf.get_asset_tag = lambda comp: None
        self.jamf.get_serial = lambda comp: None
        self.jamf.get_name = lambda comp: None

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._fill_jss_entry(self.comp, "barcode_1")
        self.dvc._fill_jss_entry(self.comp, "barcode_2")
        self.dvc._fill_jss_entry(self.comp, "asset_tag")
        self.dvc._fill_jss_entry(self.comp, "name")

        self.assertEqual("", self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_name_entry.get())

    def test_fill_jss_entry_all_empty_string(self):
        self.jamf.get_barcode_1 = lambda comp: ""
        self.jamf.get_barcode_2 = lambda comp: ""
        self.jamf.get_asset_tag = lambda comp: ""
        self.jamf.get_serial = lambda comp: ""
        self.jamf.get_name = lambda comp: ""

        self.dvc = DualVerifyController(self.root, self.comp, self.vp, self.jamf)

        self.dvc._fill_jss_entry(self.comp, "barcode_1")
        self.dvc._fill_jss_entry(self.comp, "barcode_2")
        self.dvc._fill_jss_entry(self.comp, "asset_tag")
        self.dvc._fill_jss_entry(self.comp, "name")

        self.assertEqual("", self.dvc.entry_view.jss_barcode_1_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_barcode_2_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_asset_entry.get())
        self.assertEqual("", self.dvc.entry_view.jss_name_entry.get())


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
