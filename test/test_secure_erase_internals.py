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

'''pytests for secure_erase_internals.py. Run "python -m unittest test_secure_erase_internals" or
"python test_secure_erase_internals.py"
'''

import os
import sys
import logging
import unittest
import subprocess as sp

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from blade_runner.secure_erase import secure_erase_internals as sei

logging.getLogger(__name__).addHandler(logging.NullHandler())


class TestSecureEraseInternalDisks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """This will only run once, regardless of how many tests there are."""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Setup command to create a test disk.
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
            os.path.join("/tmp", cls.vol_name)
        ]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        cls.test_disk_path = os.path.join("/tmp", cls.vol_name + ".dmg")

        # Create the test disk.
        try:
            sp.check_output(create_dmg)
        except:
            print('The file {}.dmg already exists. Please delete it and try again.'.format(cls.vol_name))
            delete_dmg = ['rm', '-f', cls.test_disk_path]
            sp.check_output(delete_dmg)
            raise SystemExit("The file {}.dmg already existed. It has now been deleted. Try again.".format(cls.vol_name))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Mount the test disk.
        mount_dmg = ['hdiutil', 'mount', cls.test_disk_path]
        sp.check_output(mount_dmg)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Path to disk.
        cls.test_disk = os.path.join('/dev/', sei.whole_disks(cls.vol_name)[0])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a file inside the test disk volume.
        create_file_in_dmg = ['touch', os.path.join('/Volumes/', cls.vol_name, 'test.txt')]
        sp.check_output(create_file_in_dmg)

    @classmethod
    def tearDownClass(cls):
        """This will only run once, regardless of how many tests there are."""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Detach the test disk.
        detach_dmg = ['hdiutil', 'detach', cls.test_disk]
        sp.check_output(detach_dmg)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Delete the test disk dmg.
        delete_dmg = ['rm','-f',  cls.test_disk_path]
        sp.check_output(delete_dmg)


    def setUp(self):
        '''This will be run before each test case.'''
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Save vol_name and test_disk to self.
        self.vol_name = self.__class__.vol_name
        self.test_disk = self.__class__.test_disk

    def test_erase_valid_disk(self):
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Erase the test disk.
        is_erased = sei.secure_erase_disks([self.test_disk])
        self.assertTrue(is_erased)


if __name__ == '__main__':
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Ensure run as root.
    if os.geteuid() != 0:
        raise SystemExit("Must be run as root.")
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

    # Set up logger.
    logging.basicConfig(level=logging.DEBUG, format=fmt, filemode='a', filename=filepath)
    logger = logging.getLogger(script_name)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Start unit tests.
    unittest.main(verbosity=1)