from entry_view import EntryView
import Tkinter as tk
import subprocess
import inspect
from management_tools import loggers
import os

cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)


class EntryViewController(object):
    def __init__(self, master, model):
        self.model = model
        self.entry_view = EntryView(master)
        self.set_to_middle(self.entry_view)

        # These two lines make it so only the entry_view window can be interacted with
        self.entry_view.transient(master)
        self.entry_view.grab_set()
        self.entry_view.submit_btn.config(command=self.submit_btn)

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

    def submit_btn(self):
        self.store_entry_view_fields()
        self.model.proceed = True
        self.entry_view.destroy()

    def store_entry_view_fields(self):
        self.model.barcode = self.entry_view.barcode_entry.get()
        self.model.asset = self.entry_view.asset_entry.get()
        self.model.name = self.entry_view.name_entry.get()