#!/usr/bin/python
# -*- coding: utf-8 -*-

'''pytests for secure_erase_internals.py. Run "python -m unittest test_secure_erase_internals" or
"python test_secure_erase_internals.py"
'''

import re
import os
import sys
import unittest
import subprocess as sp

from blade_runner.secure_erase import secure_erase_internals as sei

global test_disk

home = os.path.expanduser("~")


class TestSecureEraseInternalDisks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """This will only run once, regardless of how many tests there are."""

        cls.vol_name = 'test_disk'
        create_dmg = [
            'hdiutil',
            'create',
            '-size',
            '1g',
            '-fs',
            'HFS+J',
            '-volname',
            cls.vol_name,
            home + '/' + cls.vol_name
        ]
        try:
            sp.check_output(create_dmg)
        except:
            print('The file ' + cls.vol_name + '.dmg' + 'already exists. Please delete it and try again.')
            sys.exit()


        mount_dmg = ['hdiutil', 'mount', home + '/' + cls.vol_name + '.dmg']
        sp.check_output(mount_dmg)

        cmd = ['diskutil', 'list', cls.vol_name]
        # outputs a byte string
        disk_output = sp.check_output(cmd)
        # using grouping to later extract first group
        byte_str_pattern = re.compile(b'(/dev/disk\d+)(\s)')
        main_disk = re.findall(byte_str_pattern, disk_output)
        # extracting first group of match
        cls.main_disk = main_disk[0]

        create_file_in_dmg = ['touch', '/Volumes/' + cls.vol_name + '/test.txt']
        sp.check_output(create_file_in_dmg)

    @classmethod
    def tearDownClass(cls):
        """This will only run once, regardless of how many tests there are."""

        detach_dmg = ['hdiutil', 'detach', cls.main_disk[0]]
        sp.check_output(detach_dmg)

        delete_dmg = ['rm','-f',home + '/' + cls.vol_name + '.dmg']
        sp.check_output(delete_dmg)


    def setUp(self):
        '''This will be run before each test case.'''
        self.vol_name = self.__class__.vol_name
        self.main_disk = self.__class__.main_disk

    def test_erase_valid_disk(self):
        is_erased = sei.secure_erase_internal_disks(self.main_disk)
        self.assertTrue(is_erased)


if __name__ == '__main__':
    if os.geteuid() != 0:
        raise SystemExit("Must be run as root.")
    unittest.main(verbosity=1)