from entry_view import EntryView
import inspect
from management_tools import loggers
import os

cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)


class EntryController(object):
    def __init__(self, master, computer, dt):
        self.entry_view = EntryView(master)
        self.entry_view.protocol('WM_DELETE_WINDOW', self.close_button_clicked)
        self.computer = computer
        self.dt = dt

        # self.populate_entry_fields()

        self.set_to_middle(self.entry_view)

        # These two lines make it so only the entry_view window can be interacted with
        self.entry_view.transient(master)
        self.entry_view.grab_set()

        self.entry_view.submit_btn.config(command=self.submit_btn_clicked)
        self.entry_view.bind('<Return>', lambda event: self.submit_btn_clicked())


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

    def submit_btn_clicked(self):
        self.store_entry_fields()
        self.dt.proceed = True
        self.entry_view.destroy()

    def store_entry_fields(self):
        if self.entry_view.barcode_entry.get() != "":
            self.computer.barcode_1 = self.entry_view.barcode_entry.get()
        if self.entry_view.asset_entry.get() != "":
            self.computer.asset_tag = self.entry_view.asset_entry.get()
        if self.entry_view.name_entry.get() != "":
            self.computer.name = self.entry_view.name_entry.get()

    def populate_entry_fields(self):
        noneFilter = lambda x : "" if x is None else x
        self.entry_view.barcode_entry.insert(0, "{}".format(noneFilter(self.computer.barcode_1)))
        self.entry_view.asset_entry.insert(0, "{}".format(noneFilter(self.computer.asset_tag)))
        self.entry_view.name_entry.insert(0, "{}".format(noneFilter(self.computer.name)))

    def close_button_clicked(self):
        self.dt.proceed = False
        self.entry_view.destroy()

    def barcode_only(self):
        self.entry_view.title("Search JSS")
        self.entry_view.text_lbl.config(text="Enter the barcode.")
        self.entry_view.name_entry.grid_forget()
        self.entry_view.name_lbl.grid_forget()
        self.entry_view.asset_entry.grid_forget()
        self.entry_view.asset_lbl.grid_forget()

    def asset_only(self):
        self.entry_view.title("Search JSS")
        self.entry_view.text_lbl.config(text="Enter the asset.")
        self.entry_view.name_entry.grid_forget()
        self.entry_view.name_lbl.grid_forget()
        self.entry_view.barcode_entry.grid_forget()
        self.entry_view.barcode_lbl.grid_forget()

    def serial_only(self):
        self.entry_view.title("Search JSS")
        self.entry_view.text_lbl.config(text="Enter the asset.")
        self.entry_view.name_entry.grid_forget()
        self.entry_view.name_lbl.grid_forget()
        self.entry_view.barcode_entry.grid_forget()
        self.entry_view.barcode_lbl.grid_forget()