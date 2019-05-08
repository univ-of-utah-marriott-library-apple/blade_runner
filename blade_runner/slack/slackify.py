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

import re
import os
import sys
import socket
import plistlib
import subprocess

blade_runner_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(blade_runner_dir, "dependencies"))
sys.path.insert(0, os.path.join(blade_runner_dir, "slack"))

from blade_runner.dependencies.management_tools.slack import IncomingWebhooksSender as IWS


def main():
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set the default message.
    default_message = slack_data['default_message']
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    try:# Get channel arg.
        channel = sys.argv[1]
    except IndexError as e:
        raise IndexError("{}. No channel specified. Please specify a channel".format(e))
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    try:# Get message arg.
        message = sys.argv[2]
    except IndexError as e:
        message = default_message
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get Slack url.
    slack_url = slack_data['slack_url']
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get current IP.
    current_ip = socket.gethostbyname(socket.gethostname())
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set up bot.
    bot = IWS(slack_url, bot_name=current_ip, channel=channel)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the hostname
    cmd = ['hostname']
    hostname_output = subprocess.check_output(cmd)
    hostname = re.split("\.", hostname_output)[0]
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Send the message.
    bot.send_message("Notification for {0}: {1}".format(hostname, message))
    print("Slackify message sent.")


if __name__ == "__main__":
    print("Starting Slackify.py")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the directory of this file.
    blade_runner_dir = os.path.abspath(__file__)
    for i in range(3):
        blade_runner_dir = os.path.dirname(blade_runner_dir)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get path to Slack config plist.
    slack_plist = os.path.join(blade_runner_dir, "private/slack_configs/slack.plist")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Convert plist into dictionary.
    slack_data = plistlib.readPlist(slack_plist)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    main()
