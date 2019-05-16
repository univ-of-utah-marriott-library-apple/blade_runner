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
import time
import plistlib
import subprocess
import logging
from blade_runner.dependencies.management_tools import filelock
from blade_runner.dependencies.daemon import daemon

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


def slackify_reminder():
    """Sends a message to a Slack channel during a specified time period on a specified interval.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>9
    # Set up.
    python_bin = '/usr/bin/python'
    channel = slack_data['slack_channel']
    message = slack_data['slackify_daemon_message']
    sys.path.insert(0, os.path.join(blade_runner_dir, "slack"))
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Start the message loop
    while True:
        # Sleep for a day.
        time.sleep(24*3600)
        # Get the current hour.
        hour = time.localtime().tm_hour
        # If hour is between these times, send the message.
        if 9 <= hour < 18:
            cmd = [python_bin, "-m", "blade_runner.slack.slackify", channel, message]
            subprocess.Popen(cmd, stderr=subprocess.STDOUT, cwd=app_root_dir)


def run_daemon():
    """Run slackify_reminder() as a daemon.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    print("Running Slackify daemon.")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run slackify_reminder() as a daemon.
    with daemon.DaemonContext(stdout=sys.stdout,
                              stderr=sys.stdout,
                              pidfile=filelock.FileLock('/tmp/slackify.pid', timeout=0)):
        slackify_reminder()


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
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set path to script .
    blade_runner_dir = os.path.dirname(os.path.dirname(__file__))
    app_root_dir = os.path.dirname(blade_runner_dir)
    blade_runner_dir = os.path.abspath(__file__)

    for i in range(3):
        blade_runner_dir = os.path.dirname(blade_runner_dir)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set path to Slack config plist.
    slack_plist = os.path.join(blade_runner_dir, "private/slack_configs/slack.plist")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Convert Slack config to a dictionary.
    slack_data = plistlib.readPlist(slack_plist)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run the daemon.
    run_daemon()
