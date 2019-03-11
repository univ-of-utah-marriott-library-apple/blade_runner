#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: Feb 2019
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

from daemon import daemon
import time
import subprocess
import os
import sys
import plistlib
from management_tools import filelock


# TODO Create config plist that specifies frequency and whether or not the daemon is enabled.

def slackify_reminder():
    """Sends a message to a Slack channel during a specified time period on a specified interval.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set up.
    python_bin = '/usr/bin/python'
    script_path = os.path.join(script_dir, 'slackify.py')
    channel = slack_data['slack_channel']
    message = 'Reminder: Blade-Runner finished.'
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Start the message loop
    while True:
        # Get the current hour.
        hour = time.localtime().tm_hour
        # If hour is between these times, send the message.
        if 9 <= hour < 18:
            cmd = [python_bin, script_path, channel, message]
            subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        # Sleep for a day.
        time.sleep(24*3600)


def run_daemon():
    print("Running Slackify daemon.")
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stdout, pidfile=filelock.FileLock('/tmp/slackify.pid', timeout=0)):
        slackify_reminder()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    slack_plist = os.path.join(script_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)
    run_daemon()
