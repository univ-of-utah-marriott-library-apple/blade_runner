#!/usr/bin/python

from management_tools.slack import IncomingWebhooksSender as IWS
import socket
import subprocess
import sys
import re
import os
import plistlib

# TODO: Upload this version of Slackify to the slackify repo.

def main():
    default_message = slack_data['default_message']

    try:
        channel = sys.argv[1]
    except IndexError as e:
        raise IndexError("{}. No channel specified. Please specify a channel".format(e))

    try:
        message = sys.argv[2]
    except IndexError as e:
        message = default_message

    slack_url = slack_data['slack_url']
    current_ip = socket.gethostbyname(socket.gethostname())
    bot = IWS(slack_url, bot_name=current_ip, channel=channel)

    cmd = ['hostname']
    hostname_output = subprocess.check_output(cmd)
    hostname = re.split("\.", hostname_output)[0]
    bot.send_message("Notification for {0}: {1}".format(hostname, message))
    print("Slackify message sent.")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    slack_plist = os.path.join(script_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)
    main()