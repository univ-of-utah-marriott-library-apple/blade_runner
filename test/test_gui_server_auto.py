#!/usr/bin/python

import os
import inspect
import unittest
import plistlib
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from blade_runner.controllers.main_controller import MainController
from blade_runner.user_actions import xml_updater as user
from blade_runner.jamf_pro.jss_server import JssServer


class TestBladeRunner(unittest.TestCase):

    def setUp(self):
        cf = inspect.currentframe()

        root = tk.Tk()
        root.withdraw()

        abs_file_path = inspect.getframeinfo(cf).filename
        self.blade_runner_dir = os.path.dirname(abs_file_path)
        jss_server_plist = os.path.join(self.blade_runner_dir, "private/test/jss_server_config.plist")
        jss_server_data = plistlib.readPlist(jss_server_plist)
        jss_server = JssServer(**jss_server_data)

        self.slack_plist = os.path.join(self.blade_runner_dir, "private/test/slack_config.plist")
        self.slack_data = plistlib.readPlist(self.slack_plist)

        self.verify_config = os.path.join(self.blade_runner_dir, "private/test/verify_params_config_all_enabled.plist")
        self.verify_data = plistlib.readPlist(self.verify_config)

        self.search_params_config = os.path.join(self.blade_runner_dir, "private/test/search_params_config_all_enabled.plist")
        self.search_params = plistlib.readPlist(self.search_params_config)

        self.br = MainController(root, jss_server, self.slack_data, self.verify_data, self.search_params)


class TestGUIServerDualVerifyViewInitiallyManaged(TestBladeRunner):
    def setUp(self):
        super(TestGUIServerDualVerifyViewInitiallyManaged, self).setUp()

        jss_id = self.br._jss_server.match(self.br._computer.get_serial())
        if not jss_id or self.br._jss_server.get_managed_status(jss_id) == "false":
            self.br._jss_server.enroll_computer()

        self.br._computer.jss_id = jss_id
        self.br._computer.barcode_1 = "jss_barcode_1_num"
        self.br._computer.barcode_2 = "jss_barcode_2_num"
        self.br._computer.asset_tag = "jss_asset_tag_num"
        self.br._computer.name = "jss_name_string"
        self.br._jss_server.push_identity_fields(self.br._computer)

        self.br.restart()
        self.br.restart = self.dummy_restart
        self.br._user_defined_actions = lambda: None
        self.br._root.report_callback_exception = lambda: None
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_keep_jss_data_immediate_match(self):
        self.match = "barcode_1"
        self.submit_btn_id = "jss"
        self.br.save_offboard_config = lambda x: self.dummy_save_offboard_config(keep_managed=True)
        self.br.test_run(self.start_with_barcode_1)

        self.assertEqual("jss_barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("jss_barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("jss_asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("jss_name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        jss_id = self.br._computer.jss_id
        self.assertTrue(jss_id)

        self.assertEqual("jss_barcode_1_num", self.br._jss_server.get_barcode_1(jss_id))
        self.assertEqual("jss_barcode_2_num", self.br._jss_server.get_barcode_2(jss_id))
        self.assertEqual("jss_asset_tag_num", self.br._jss_server.get_asset_tag(jss_id))
        self.assertEqual("jss_name_string", self.br._jss_server.get_name(jss_id))
        managed = self.br._jss_server.get_managed_status(jss_id)
        self.assertEqual("true", managed)

    def test_keep_jss_data_non_immediate_match(self):
        self.match = "asset_tag"
        self.submit_btn_id = "jss"
        self.br.save_offboard_config = lambda x: self.dummy_save_offboard_config(keep_managed=True)
        self.br.test_run(lambda: self.start_with_barcode_1())

        self.assertEqual("jss_barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("jss_barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("jss_asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("jss_name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        jss_id = self.br._computer.jss_id
        self.assertTrue(jss_id)

        self.assertEqual("jss_barcode_1_num", self.br._jss_server.get_barcode_1(jss_id))
        self.assertEqual("jss_barcode_2_num", self.br._jss_server.get_barcode_2(jss_id))
        self.assertEqual("jss_asset_tag_num", self.br._jss_server.get_asset_tag(jss_id))
        self.assertEqual("jss_name_string", self.br._jss_server.get_name(jss_id))
        managed = self.br._jss_server.get_managed_status(jss_id)
        self.assertEqual("true", managed)

    def test_keep_user_data_immediate_match(self):
        self.match = "barcode_1"
        self.submit_btn_id = "user"
        self.br.save_offboard_config = lambda x: self.dummy_save_offboard_config(keep_managed=True)
        self.br.test_run(self.start_with_barcode_1)

        self.assertEqual("barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        jss_id = self.br._computer.jss_id
        self.assertTrue(jss_id)

        self.assertEqual("barcode_1_num", self.br._jss_server.get_barcode_1(jss_id))
        self.assertEqual("barcode_2_num", self.br._jss_server.get_barcode_2(jss_id))
        self.assertEqual("asset_tag_num", self.br._jss_server.get_asset_tag(jss_id))
        self.assertEqual("name_string", self.br._jss_server.get_name(jss_id))
        managed = self.br._jss_server.get_managed_status(jss_id)
        self.assertEqual("true", managed)

    def test_keep_user_data_non_immediate_match(self):
        self.match = "asset_tag"
        self.submit_btn_id = "user"
        self.br.save_offboard_config = lambda x: self.dummy_save_offboard_config(keep_managed=True)
        self.br.test_run(self.start_with_barcode_1)

        self.assertEqual("barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        jss_id = self.br._computer.jss_id
        self.assertTrue(jss_id)

        self.assertEqual("barcode_1_num", self.br._jss_server.get_barcode_1(jss_id))
        self.assertEqual("barcode_2_num", self.br._jss_server.get_barcode_2(jss_id))
        self.assertEqual("asset_tag_num", self.br._jss_server.get_asset_tag(jss_id))
        self.assertEqual("name_string", self.br._jss_server.get_name(jss_id))
        managed = self.br._jss_server.get_managed_status(jss_id)
        self.assertEqual("true", managed)

    def start_with_barcode_1(self):
        self.br._main_view._next_btn.invoke()
        self.curr_search_param = "barcode_1"
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_1"))
        self.br._main_view._barcode_1_btn.invoke()

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_barcode_1_saved(self):
        self.curr_search_param = "serial_number"
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_1"))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_barcode_2_saved(self):
        self.curr_search_param = "barcode_1"
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_2"))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_asset_tag_saved(self):
        self.curr_search_param = "asset_tag"
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("asset_tag"))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_serial_saved(self):
        self.curr_search_param = "barcode_2"
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("serial_number"))

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def proceed_and_terminate(self, data_id):
        if not self.br._computer.jss_id:
            if data_id == "barcode_1":
                self.br._search_controller.entry_view.barcode_1_entry.insert(0, "barcode_1_num")
                self.callback_barcode_2_saved()
            if data_id == "barcode_2":
                self.br._search_controller.entry_view.barcode_2_entry.insert(0, "barcode_2_num")
                self.callback_asset_tag_saved()
            if data_id == "asset_tag":
                self.br._search_controller.entry_view.asset_entry.insert(0, "asset_tag_num")
                self.callback_serial_saved()
            if data_id == "serial_number":
                self.callback_barcode_1_saved()
            self.br._search_controller.proceed_operation()
        else:
            self.br._verify_controller.entry_view.name_entry.insert(0, "name_string")
            self.br._verify_controller.proceed_operation(self.submit_btn_id)
            self.br.terminate()

    def dummy_restart(self):
        pass

    def dummy_save_offboard_config(self, keep_managed=True):
        if keep_managed:
            config = os.path.join(self.blade_runner_dir, "private/test/offboard_config_managed_true.xml")
        else:
            config = os.path.join(self.blade_runner_dir, "private/test/offboard_config.xml")

        self.br._offboard_config = user.xml_to_string(config)

    def dummy_messagebox(self):
        pass


if __name__ == "__main__":
    unittest.main(verbosity=2)