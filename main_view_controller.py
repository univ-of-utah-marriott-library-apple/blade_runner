from model import Model
from main_view import View
from entry_view_controller import EntryViewController
import Tkinter as tk
import subprocess
import inspect
from management_tools import loggers
import os


class MainViewController(object):
    def __init__(self, root):
        self.model = Model()
        self.main_view = View(root)
        self.entry_view = None
        self.set_to_middle(self.main_view)
        self.refocus()

        self.main_view.serial_btn.config(command=self.get_serial_btn)
        self.main_view.bind('<Return>', self.get_serial_btn)


    def run(self):
        self.main_view.mainloop()

    def get_serial_btn(self):
        self.entry_view = EntryViewController(self.main_view, self.model)

    def refocus(self):
        # Python tkinter window gets selected automatically
        select_window = ['/usr/bin/osascript', '-e',
                         'tell application "Finder" to set frontmost of process "Python" to true']
        try:
            subprocess.check_output(select_window)
        except subprocess.CalledProcessError:
            logger.debug("Setting frontmost of process Python to true failed.")

    def set_to_middle(self, window):
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Updates window info to current window state
        window.update_idletasks()
        # Sets window position
        window.geometry('+%d+%d' % (screen_width / 2 - window.winfo_width() / 2, screen_height / 4))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def action_submit(self):
        print("submit button clicked")


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)


if __name__ == "__main__":
    # if os.geteuid() != 0:
    #     raise SystemExit("Must be run as root.")
    root = tk.Tk()
    root.withdraw()
    app = MainViewController(root)
    app.run()


