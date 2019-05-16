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

""" Runs Blade Runner.

Runs Blade Runner as a package. Must be in Blade Runner's python root directory to run.

Example:

    # Current working directory is "/path/to/Blade Runner.app/Contents/Resources/Blade Runner/"
    python -m blade_runner.runner

"""

import subprocess
import os
import sys
import inspect
import re

blade_runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(blade_runner_dir, "dependencies"))

from blade_runner.dependencies.tempapp import TempApp
from blade_runner.dependencies.management_tools import loggers


def main():
    # Ensure being run as root.
    if os.geteuid() != 0:
        raise SystemExit("Blade Runner must be run as root.")

    # Set the icon path
    icon = os.path.join(blade_runner_dir, "rsrc/images/BladeRunner.icns")
    # Set the plist overrides
    infoPlist_overrides = {'CFBundleName': 'Blade Runner'}
    # Set the bundle name
    bundle_name = 'Blade Runner'

    # Set the list of binaries to check.
    python_binaries = [sys.executable, "/usr/bin/python2.7", "python2", "/usr/bin/python", "/anaconda2/bin/python2"]
    # Find which binaries are greater than or equal to 2.7.9.
    valid_bins = compatible_python_bins(python_binaries)

    # For every valid binary, try to run it with the Python icon replaced with Blade Runner's icon.
    for python_bin in valid_bins:
        try:
            myApp = TempApp(infoPlist_overrides, bundle_name=bundle_name, app_icon=icon, python_bin=python_bin)
            logger.info("Attempting to run with Python version: {}".format(get_python_version(python_bin)))
            subprocess.check_output([myApp.python_path, '-m', 'blade_runner.controllers.main_controller'], cwd=blade_runner_dir)
            return
        except IOError as e:
            logger.error(e)

    # For every valid binary, try to run Blade Runner normally (no icon change).
    for python_bin in valid_bins:
        logger.info("Running application without icon update.")
        logger.info("Attempting to run with Python binary {}, version {}".format(python_bin, get_python_version(python_bin)))
        try:
            subprocess.check_output([python_bin, '-m', 'blade_runner.controllers.main_controller'])
            return
        except ImportError as e:
            logger.error(e)


def compatible_python_bins(python_bins):
    logger.info("Checking Python versions...")
    versions = []
    for binary in python_bins:
        versions.append(get_python_version(binary))

    compat_bins = []
    for i, version in enumerate(versions):
        if version:
            if version[0] == 2:
                if version[1] == 7:
                    if version[2] >= 9:
                        compat_bins.append(python_bins[i])
    logger.debug("Compatible binaries: {}".format(compat_bins))
    return compat_bins


def get_python_version(python_bin):
    try:
        cmd = [python_bin, '--version']
        version = subprocess.check_output([python_bin, '--version'], stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, OSError) as e:
        logger.debug(e)
        return None

    match = re.match('Python (\d+).(\d+).(\d+)', version)
    if match:
        major = int(match.group(1))
        minor = int(match.group(2))
        micro = int(match.group(3))
        version = (major, minor, micro)
    else:
        version = None
    return version


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))

if __name__ == "__main__":
    main()
