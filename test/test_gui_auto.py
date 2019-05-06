#!/usr/bin/python

import unittest
import os
import plistlib
from jss_server import JssServer
import inspect
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
from main_controller import MainController


class TestGUI(unittest.TestCase):

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


class TestCombobox(TestGUI):
    def setUp(self):
        super(TestCombobox, self).setUp()

    def test_config_selection(self):
        self.br.test_run(self.callback_config_selection)
        self.assertTrue(self.br._offboard_config)

    def callback_config_selection(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(200, self.terminate_main_view)

    def terminate_main_view(self):
        self.br.terminate()


class TestSearchParams(TestGUI):
    def setUp(self):
        super(TestSearchParams, self).setUp()
        self.br.restart = self.dummy_restart
        self.br._jss_server.match = self.dummy_match

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_barcode_1_saved(self):
        self.br.test_run(self.callback_barcode_1_saved)
        self.assertTrue(self.br._computer.barcode_1)

    def callback_barcode_1_saved(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_1"))
        self.br._main_view._barcode_1_btn.invoke()

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_barcode_2_saved(self):
        self.br.test_run(self.callback_barcode_2_saved)
        self.assertTrue(self.br._computer.barcode_2)

    def callback_barcode_2_saved(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_2"))
        self.br._main_view._barcode_2_btn.invoke()

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_asset_tag_saved(self):
        self.br.test_run(self.callback_asset_tag_saved)
        self.assertTrue(self.br._computer.asset_tag)

    def callback_asset_tag_saved(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("asset_tag"))
        self.br._main_view._asset_btn.invoke()

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_serial_saved(self):
        self.br.test_run(self.callback_serial_saved)
        self.assertTrue(self.br._computer.serial_number)

    def callback_serial_saved(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("serial_number"))
        self.br._main_view._serial_btn.invoke()

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def proceed_and_terminate(self, data_id):
        self.br._open_search_view = self.dummy_open_search_view
        if data_id == "barcode_1":
            self.br._search_controller.entry_view.barcode_1_entry.insert(0, "barcode_1_num")
        if data_id == "barcode_2":
            self.br._search_controller.entry_view.barcode_2_entry.insert(0, "barcode_2_num")
        if data_id == "asset_tag":
            self.br._search_controller.entry_view.asset_entry.insert(0, "asset_tag")
        if data_id == "serial_number":
            pass
        self.br._search_controller.proceed_operation()
        self.br.terminate()

    def dummy_match(self, dummy):
        return None

    def dummy_restart(self):
        pass

    def dummy_open_search_view(self, dummy):
        self.br._proceed = False


class TestVerifyView(TestGUI):

    def setUp(self):
        super(TestVerifyView, self).setUp()
        self.br._jss_server.match = self.dummy_match
        self.br.restart = self.dummy_restart

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_barcode_1_first(self):
        self.br.test_run(lambda: self.start_with_barcode_1())
        self.assertEqual("barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("barcode_2_num", self.br._computer.barcode_2)
        self.assertTrue("asset_tag_num", self.br._computer.asset_tag)
        self.assertTrue(self.br._computer.serial_number)
        self.assertTrue(self.br.search_params.all_searched())
        self.assertFalse(self.br.search_params.exists_match())
        self.assertFalse(self.br._computer.jss_id)

    def test_barcode_2_first(self):
        self.br.test_run(lambda: self.start_with_barcode_2())
        self.assertTrue(self.br._computer.barcode_1)
        self.assertTrue(self.br._computer.barcode_2)
        self.assertTrue(self.br._computer.asset_tag)
        self.assertTrue(self.br._computer.serial_number)
        self.assertFalse(self.br.search_params.exists_match())
        self.assertFalse(self.br._computer.jss_id)

    def test_asset_tag_first(self):
        self.br.test_run(lambda: self.start_with_asset_tag())
        self.assertTrue(self.br._computer.barcode_1)
        self.assertTrue(self.br._computer.barcode_2)
        self.assertTrue(self.br._computer.asset_tag)
        self.assertTrue(self.br._computer.serial_number)
        self.assertFalse(self.br.search_params.exists_match())
        self.assertFalse(self.br._computer.jss_id)

    def test_serial_number_first(self):
        self.br.test_run(lambda: self.start_with_serial_number())
        self.assertTrue(self.br._computer.barcode_1)
        self.assertTrue(self.br._computer.barcode_2)
        self.assertTrue(self.br._computer.asset_tag)
        self.assertTrue(self.br._computer.serial_number)
        self.assertFalse(self.br.search_params.exists_match())
        self.assertFalse(self.br._computer.jss_id)

    def start_with_barcode_1(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_1"))
        self.br._main_view._barcode_1_btn.invoke()

    def start_with_barcode_2(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_2"))
        self.br._main_view._barcode_2_btn.invoke()

    def start_with_asset_tag(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("asset_tag"))
        self.br._main_view._asset_btn.invoke()

    def start_with_serial_number(self):
        self.br._main_view._next_btn.invoke()
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("serial_number"))
        self.br._main_view._serial_btn.invoke()

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_barcode_1_saved(self):
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_1"))

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_barcode_2_saved(self):
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("barcode_2"))

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_asset_tag_saved(self):
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("asset_tag"))

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def callback_serial_saved(self):
        self.br._main_view.after(500, lambda: self.proceed_and_terminate("serial_number"))

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def proceed_and_terminate(self, data_id):
        if not self.br.search_params.all_searched():
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
            self.br.terminate()

    def dummy_match(self, dummy):
        return None

    def dummy_restart(self):
        pass

class TestDualVerifyView(TestGUI):

    def setUp(self):
        super(TestDualVerifyView, self).setUp()
        self.br._jss_server.match = self.dummy_match
        self.br.restart = self.dummy_restart
        self.br._jss_server.get_barcode_1 = lambda x: "jss_barcode_1_num"
        self.br._jss_server.get_barcode_2 = lambda x: "jss_barcode_2_num"
        self.br._jss_server.get_asset_tag = lambda x: "jss_asset_tag_num"
        self.br._jss_server.get_serial = lambda x: "jss_serial_num"
        self.br._jss_server.get_name = lambda x: "jss_name_string"
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_keep_jss_data_on_first_match(self):
        self.match = "barcode_1"
        self.br.test_run(lambda: self.start_with_barcode_1())
        self.assertEqual("jss_barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("jss_barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("jss_asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("jss_name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        self.assertTrue(self.br._computer.jss_id)

    def test_keep_jss_data_on_non_first_match(self):
        self.match = "asset_tag"
        self.br.test_run(lambda: self.start_with_barcode_1())
        self.assertEqual("jss_barcode_1_num", self.br._computer.barcode_1)
        self.assertEqual("jss_barcode_2_num", self.br._computer.barcode_2)
        self.assertEqual("jss_asset_tag_num", self.br._computer.asset_tag)
        self.assertEqual("jss_name_string", self.br._computer.name)
        self.assertTrue(self.br.search_params.exists_match())
        self.assertTrue(self.br._computer.jss_id)

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
            self.br._verify_controller.set_proceed = lambda x: False
            self.br._verify_controller.proceed_operation("jss")
            self.br.terminate()

    def dummy_match(self, dummy):
        if self.curr_search_param == self.match:
            return "1234"
        return None

    def dummy_restart(self):
        pass

    def dummy_get_managed_status(self):
        self.br._proceed = False
        return "true"

if __name__ == "__main__":
    unittest.main(verbosity=2)