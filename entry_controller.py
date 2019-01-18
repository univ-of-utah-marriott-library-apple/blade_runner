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
    def __init__(self, master, computer, params, input_type):

        self.entry_view = EntryView(master)
        self.entry_view.protocol('WM_DELETE_WINDOW', self.close_button_clicked)
        self.computer = computer
        self.proceed = None
        # self.verify_data = verify_data
        self.params = params
        self.input_type = input_type

        self.set_to_middle(self.entry_view)

        # These two lines make it so only the entry_view window can be interacted with
        self.entry_view.transient(master)
        self.entry_view.grab_set()

        self.entry_view.submit_btn.config(command=self.submit_btn_clicked)
        self.entry_view.bind('<Return>', lambda event: self.submit_btn_clicked())

        self.determine_widgets(input_type)

    def set_to_middle(self, window):
        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Updates window info to current window state
        window.update_idletasks()

        # Sets window position
        window.geometry('+%d+%d' % (screen_width / 2 - window.winfo_width() / 2, screen_height / 4))

    def submit_btn_clicked(self):
        self.store_entry_fields()
        self.proceed = True
        self.entry_view.destroy()

    def store_entry_field(self):
        if self.input_type == "barcode_1":
            if self.entry_view.barcode_1_entry.get() != "":
                self.computer.barcode_1 = self.entry_view.barcode_1_entry.get()

        elif self.input_type == "barcode_2":
            if self.entry_view.barcode_2_entry.get() != "":
                self.computer.barcode_2 = self.entry_view.barcode_2_entry.get()

        elif self.input_type == "asset_tag":
            if self.entry_view.asset_entry.get() != "":
                self.computer.asset_tag = self.entry_view.asset_entry.get()

        elif self.input_type == "computer_name":
            if self.entry_view.name_entry.get() != "":
                self.computer.name = self.entry_view.name_entry.get()
        elif self.input_type == "config":
            self.store_entry_fields()

    def store_entry_fields(self):
        if 'barcode_1' in self.params.enabled:
            if self.entry_view.barcode_1_entry.get() != "":
                self.computer.barcode_1 = self.entry_view.barcode_1_entry.get()

        if 'barcode_2' in self.params.enabled:
            if self.entry_view.barcode_2_entry.get() != "":
                self.computer.barcode_2 = self.entry_view.barcode_2_entry.get()

        if 'asset_tag' in self.params.enabled:
            if self.entry_view.asset_entry.get() != "":
                self.computer.asset_tag = self.entry_view.asset_entry.get()

        if 'computer_name' in self.params.enabled:
            if self.entry_view.name_entry.get() != "":
                self.computer.name = self.entry_view.name_entry.get()

    def populate_entry_fields(self):
        none_filter = lambda x: "" if x is None else x

        if 'barcode_1' in self.params.enabled:
            self.entry_view.barcode_1_entry.insert(0, "{}".format(none_filter(self.computer.barcode_1)))

        if 'barcode_2' in self.params.enabled:
            self.entry_view.barcode_2_entry.insert(0, "{}".format(none_filter(self.computer.barcode_2)))

        if 'asset_tag' in self.params.enabled:
            self.entry_view.asset_entry.insert(0, "{}".format(none_filter(self.computer.asset_tag)))

        if 'computer_name' in self.params.enabled:
            self.entry_view.name_entry.insert(0, "{}".format(none_filter(self.computer.name)))

    def close_button_clicked(self):
        self.proceed = False
        self.entry_view.destroy()

    def determine_widgets(self, input_type):
        if input_type == "barcode_1":
            self.entry_view.barcode_1_lbl.grid(row=1, column=0, sticky="E")
            self.entry_view.barcode_1_entry.grid(row=1, column=1)

        elif input_type == "barcode_2":
            self.entry_view.barcode_2_lbl.grid(row=2, column=0, sticky="E")
            self.entry_view.barcode_2_entry.grid(row=2, column=1)

        elif input_type == "asset_tag":
            self.entry_view.asset_lbl.grid(row=3, column=0, sticky="E")
            self.entry_view.asset_entry.grid(row=3, column=1)

        elif input_type == "computer_name":
            self.entry_view.name_lbl.grid(row=4, column=0, sticky="E")
            self.entry_view.name_entry.grid(row=4, column=1)

        elif input_type == "config":
            self.determine_widgets_from_config()

    def determine_widgets_from_config(self):
        if 'barcode_1' in self.params.enabled:
            self.entry_view.barcode_1_lbl.grid(row=1, column=0, sticky="E")
            self.entry_view.barcode_1_entry.grid(row=1, column=1)

        if 'barcode_2' in self.params.enabled:
            self.entry_view.barcode_2_lbl.grid(row=2, column=0, sticky="E")
            self.entry_view.barcode_2_entry.grid(row=2, column=1)

        if 'asset_tag' in self.params.enabled:
            self.entry_view.asset_lbl.grid(row=3, column=0, sticky="E")
            self.entry_view.asset_entry.grid(row=3, column=1)

        if 'computer_name' in self.params.enabled:
            self.entry_view.name_lbl.grid(row=4, column=0)
            self.entry_view.name_entry.grid(row=4, column=1)
