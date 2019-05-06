#!/usr/bin/python

'''pytests for offboard_tool.py. Must be run as root. Run unittest by cd into working directory and running:

    python -m unittest test_offboard_tool

'''

import os
import inspect
import unittest
import plistlib
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from blade_runner.controllers.main_controller import MainController
from blade_runner.jamf_pro.params import SearchParams, VerifyParams
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


class TestRestart(TestBladeRunner):

    def setUp(self):
        super(TestRestart, self).setUp()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set up Computer before resetting it.
        self.br._computer.barcode_1 = "barcode_1_num"
        self.br._computer.barcode_2 = "barcode_2_num"
        self.br._computer.asset_tag = "asset_tag_num"
        self.br._computer.serial_number = "serial_num"
        self.br._computer.name = "test_name"
        self.br._computer.incorrect_barcode_1 = "incorrect_barcode_1_num"
        self.br._computer.incorrect_barcode_2 = "incorrect_barcode_2_num"
        self.br._computer.incorrect_asset = "incorrect_asset_num"
        self.br._computer.incorrect_serial = "incorrect_serial_num"
        self.br._computer.jss_id = "jss_id_num"
        self.br._computer.jss_barcode_1 = "jss_barcode_1_num"
        self.br._computer.jss_barcode_2 = "jss_barcode_2_num"
        self.br._computer.jss_asset_tag = "jss_asset_tag_num"
        self.br._computer.jss_serial_number = "jss_serial_num"
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set them to None so we can verify that restart reloads them.
        self.br.verify_params.disabled = None
        self.br.verify_params.enabled = None
        self.br.verify_params.originals = None
        self.br.verify_params.search_status = None

        self.br.search_params.disabled = None
        self.br.search_params.enabled = None
        self.br.search_params.search_status = None
        self.br.search_params.originals = None
        self.br.search_params.match_status = None
        self.br.search_params.search_count = 1
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def test_restart(self):
        """Test restarting Computer, VerifyParams, and SearchParams to their initial state after having been modified.
        """
        # Restart Blade-Runner
        self.br.restart()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Assert that Computer attributes have been set to None.
        self.assertIsNone(self.br._computer.barcode_1)
        self.assertIsNone(self.br._computer.barcode_2)
        self.assertIsNone(self.br._computer.asset_tag)
        self.assertIsNone(self.br._computer.serial_number)
        self.assertIsNone(self.br._computer.name)
        self.assertIsNone(self.br._computer.incorrect_barcode_1)
        self.assertIsNone(self.br._computer.incorrect_barcode_2)
        self.assertIsNone(self.br._computer.incorrect_asset)
        self.assertIsNone(self.br._computer.incorrect_serial)
        self.assertIsNone(self.br._computer.jss_id)
        self.assertIsNone(self.br._computer.jss_barcode_1)
        self.assertIsNone(self.br._computer.jss_barcode_2)
        self.assertIsNone(self.br._computer.jss_asset_tag)
        self.assertIsNone(self.br._computer.jss_serial_number)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Load verify/search params from config.
        verify_params_data = plistlib.readPlist(self.verify_config)
        search_params_data = plistlib.readPlist(self.search_params_config)

        verify_params = VerifyParams(verify_params_data)
        search_params = SearchParams(search_params_data)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Assert that verify/search params have been reloaded.
        self.assertEqual(self.br.verify_params.originals, verify_params.originals)
        self.assertEqual(self.br.verify_params.disabled, verify_params.disabled)
        self.assertEqual(self.br.verify_params.enabled, verify_params.enabled)
        self.assertEqual(self.br.verify_params.search_status, verify_params.search_status)

        self.assertEqual(self.br.search_params.disabled, search_params.disabled)
        self.assertEqual(self.br.search_params.enabled, search_params.enabled)
        self.assertEqual(self.br.search_params.search_status, search_params.search_status)
        self.assertEqual(self.br.search_params.originals, search_params.originals)
        self.assertEqual(self.br.search_params.match_status, search_params.match_status)
        self.assertEqual(self.br.search_params.search_count, search_params.search_count)


class TestSearchSequence(TestBladeRunner):

    def setUp(self):
        super(TestSearchSequence, self).setUp()
        search_params_all = os.path.join(self.blade_runner_dir, "private/test/search_params_config_all_enabled.plist")
        search_params_data = plistlib.readPlist(search_params_all)
        self.br.search_params = SearchParams(search_params_data)
        self.br.restart = self.restart

    def restart(self):
        pass

    def test_all_search_params_enabled(self):
        """Ensure that the search sequence covers all the search parameters."""
        def main(param):
            self.br.search_params.set_searched(param)

        self.br._main = main
        self.br.search_sequence("barcode_1")

        for param in self.br.search_params:
            self.assertTrue(self.br.search_params.was_searched(param), msg=param)

        self.assertFalse(self.br.search_params.exists_match())
        self.assertTrue(self.br.search_params.all_searched())
        self.assertEqual(4, self.br.search_params.search_count)

    def test_match_first(self):
        """Ensure that the search sequence only processes the first search parameter."""
        def main(param):
            self.br.search_params.set_searched(param)
            self.br.search_params.set_match(param)
            self.br._computer.jss_id = "123"

        self.br._main = main
        first_param = "barcode_1"
        self.br.search_sequence(first_param)

        for param in self.br.search_params:
            if param == first_param:
                self.assertTrue(self.br.search_params.was_searched(param), msg=param)
                self.assertTrue(self.br.search_params.match_status[param])
            else:
                self.assertFalse(self.br.search_params.was_searched(param), msg=param)
                self.assertFalse(self.br.search_params.match_status[param])

        self.assertTrue(self.br.search_params.exists_match())
        self.assertFalse(self.br.search_params.all_searched())
        self.assertEqual(1, self.br.search_params.search_count)

    def test_match_last(self):
        """Ensure the search sequence processes all the parameters when the last one results in a match."""
        def main(param):
            self.br.search_params.set_searched(param)
            if self.br.search_params.all_searched():
                self.br.search_params.set_match(param)
                self.br._computer.jss_id = "123"
                self.matched_param = param

        self.br._main = main
        self.first_param = "barcode_1"
        self.br.search_sequence(self.first_param)

        for param in self.br.search_params:
            if param == self.matched_param:
                self.assertTrue(self.br.search_params.was_searched(param), msg=param)
                self.assertTrue(self.br.search_params.match_status[param])
            else:
                self.assertTrue(self.br.search_params.was_searched(param), msg=param)
                self.assertFalse(self.br.search_params.match_status[param])

        self.assertTrue(self.br.search_params.exists_match())
        self.assertTrue(self.br.search_params.all_searched())
        self.assertEqual(4, self.br.search_params.search_count)


class TestDynamicSearch(TestBladeRunner):

    def setUp(self):
        super(TestDynamicSearch, self).setUp()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set up Computer
        self.br._computer.barcode_1 = "barcode_1_num"
        self.br._computer.barcode_2 = "barcode_2_num"
        self.br._computer.asset_tag = "asset_tag_num"
        self.br._computer.serial_number = "serial_num"

    def match(self, param):
        return "123"

    def no_match(self, param):
        return None

    def test_barcode_1_match(self):
        self.br._jss_server.match = self.match
        data_id = "barcode_1"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertEqual("123", self.br._computer.jss_id)
        self.assertEqual("barcode_1_num", self.br._computer.barcode_1)

    def test_barcode_2_match(self):
        self.br._jss_server.match = self.match
        data_id = "barcode_2"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertEqual("123", self.br._computer.jss_id)
        self.assertEqual("barcode_2_num", self.br._computer.barcode_2)

    def test_asset_tag_match(self):
        self.br._jss_server.match = self.match
        data_id = "asset_tag"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertEqual("123", self.br._computer.jss_id)
        self.assertEqual("asset_tag_num", self.br._computer.asset_tag)

    def test_serial_match(self):
        self.br._jss_server.match = self.match
        data_id = "serial_number"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertEqual("123", self.br._computer.jss_id)
        self.assertEqual("serial_num", self.br._computer.serial_number)

    def test_barcode_1_no_match(self):
        self.br._jss_server.match = self.no_match
        data_id = "barcode_1"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertIsNone(self.br._computer.jss_id)
        self.assertEqual("barcode_1_num", self.br._computer.barcode_1)

    def test_barcode_2_no_match(self):
        self.br._jss_server.match = self.no_match
        data_id = "barcode_2"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertIsNone(self.br._computer.jss_id)
        self.assertEqual("barcode_2_num", self.br._computer.barcode_2)

    def test_asset_tag_no_match(self):
        self.br._jss_server.match = self.no_match
        data_id = "asset_tag"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertIsNone(self.br._computer.jss_id)
        self.assertEqual("asset_tag_num", self.br._computer.asset_tag)

    def test_serial_no_match(self):
        self.br._jss_server.match = self.no_match
        data_id = "serial_number"
        self.br._dynamic_search(self.br._computer, data_id)
        self.assertIsNone(self.br._computer.jss_id)
        self.assertEqual("serial_num", self.br._computer.serial_number)


class TestGetOffboardConfigs(TestBladeRunner):

    def setUp(self):
        super(TestGetOffboardConfigs, self).setUp()
        self.test_dir = os.path.join(self.blade_runner_dir, "private/test/get_offboard_configs")
        self.configs = ["test_config_1.xml", "test_config_2.xml"]

    def test_get_offboard_configs(self):
        offboard_configs = self.br._get_offboard_configs(self.test_dir)

        for config in offboard_configs:
            self.assertTrue(config in offboard_configs)


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


if __name__ == '__main__':
    test_classes_to_run = [
                           TestRestart,
                           TestSearchSequence,
                           TestDynamicSearch,
                           TestGUIServerDualVerifyViewInitiallyManaged,
                          ]

    loader = unittest.TestLoader()

    suites_list = []
    for test_class in test_classes_to_run:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    big_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(big_suite)