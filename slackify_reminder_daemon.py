from daemon import daemon
import time
import subprocess
import os
import sys
import plistlib
from management_tools import filelock


# TODO Create config plist that specifies frequency and whether or not the daemon is enabled.

def slackify_reminder():
    python_bin = '/usr/bin/python'
    script_path = os.path.join(script_dir, 'slackify.py')
    channel = slack_data['slack_channel']
    message = 'Reminder: Blade-Runner finished.'
    while True:
        hour = time.localtime().tm_hour
        if 9 <= hour < 18:
            cmd = [python_bin, script_path, channel, message]
            subprocess.Popen(cmd, stderr=subprocess.STDOUT)
        time.sleep(24*3600)


def run_daemon():
    print("Running Slackify daemon.")
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stdout, pidfile=filelock.FileLock('/tmp/spam.pid', timeout=0)):
        slackify_reminder()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    slack_plist = os.path.join(script_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)
    run_daemon()
