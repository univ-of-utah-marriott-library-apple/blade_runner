import os
import sys
import inspect
import tkSimpleDialog
import subprocess
from Tkinter import *

app_root_dir = os.path.dirname(os.path.dirname(__file__))
blade_runner_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(blade_runner_dir, "dependencies"))
sys.path.insert(0, blade_runner_dir)

from blade_runner.dependencies import pexpect
from blade_runner.dependencies.management_tools import loggers


def sudo_process(cmd, master, cwd=None):
    try:
        child = pexpect.spawn('bash', cmd, cwd=cwd)

        while True:
            match = child.expect(['Password:', pexpect.EOF, pexpect.TIMEOUT])
            if match == 0:
                logger.debug("Waiting for password.")
                password = tkSimpleDialog.askstring("Blade Runner", "Enter admin password:", show='*', parent=master)
                if not password:
                    logger.debug("No password entered. Exiting.")
                    return
                else:
                    sys.exit(password)
                    child.sendline(password)
                    return
            elif match == 1:
                logger.debug("Reached end of output. runner.py exiting")
                return
            elif match == 2:
                logger.debug("Password prompt timed out. Exiting.")
                return
            else:
                logger.debug("Unknown error occurred. Exiting.")
                return
    except pexpect.exceptions.EOF as e:
        msg = "runner.py finished.".format(e)
        logger.debug(msg)
    finally:
        logger.debug("Destroying runner.py root.")
        master.destroy()
        # master.update()
        # while child.isalive():
        #     match = child.expect(["\n", pexpect.EOF])
        #     if match == 0:
        #         print(child.before)


def set_to_middle(window):
    """Sets a Tkinter window to the center of the screen.

    Args:
        window: Tkinter window.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Updates window info to current window state
    window.update_idletasks()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Gets computer screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Sets window position
    window.geometry('+{}+{}'.format(screen_width / 2 - window.winfo_width()/2, screen_height / 4))


def refocus():
    """Set the focus to the Python application.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set up the command
    select_window = ['/usr/bin/osascript', '-e',
                     'tell application "Finder" to set frontmost of process "Python" to true']
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    try:  # set focus to the main view.
        subprocess.check_output(select_window)
    except subprocess.CalledProcessError:
        logger.debug("Setting frontmost of process Python to true failed.")


def main():
    root = Tk()
    set_to_middle(root)
    root.withdraw()
    cmd = ['-c', '/usr/bin/sudo python -m blade_runner.controllers.main_controller']
    root.after(1000, lambda: sudo_process(cmd, root, cwd=app_root_dir))
    root.after(2000, lambda: refocus())
    root.wait_window()


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))


if __name__ == "__main__":
    main()
