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

blade_runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(blade_runner_dir, "dependencies"))

from blade_runner.dependencies.tempapp import TempApp


def main():
    icon = os.path.join(blade_runner_dir,"rsrc/images/BladeRunner.icns")
    infoPlist_overrides = {'CFBundleName': 'Blade Runner'}
    bundle_name = 'Blade Runner'

    try: # Run application using the current python
        myApp = TempApp(infoPlist_overrides, bundle_name=bundle_name, app_icon=icon)

        subprocess.check_output([myApp.python_path, '-m', 'blade_runner.controllers.main_controller'], cwd=blade_runner_dir)
    except IOError:
        try: # Run application using the system's python
            myApp = TempApp(infoPlist_overrides, bundle_name=bundle_name, app_icon=icon, python_bin=os.path.realpath('/usr/bin/python2.7'))
            subprocess.check_output([myApp.python_path, '-m', 'blade_runner.controllers.main_controller'], cwd=blade_runner_dir)
        except:
            # If unable to run application with updated icon, run it normally.
            print("Running application without icon update.")
            subprocess.check_output(['/usr/bin/python', '-m', 'blade_runner.controllers.main_controller'])


if __name__ == "__main__":
    if os.geteuid() != 0:
        raise SystemExit("Blade Runner must be run as root.")
    main()
