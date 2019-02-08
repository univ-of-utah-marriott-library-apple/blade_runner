from entry_controller import EntryController
import inspect
from management_tools import loggers
import os
from dual_verify_view import DualVerifyView


class DualVerificationController(EntryController):
    def __init__(self, master, computer, verify_params, search_params):
        view = DualVerifyView(master, self)
        super(DualVerificationController, self).__init__(master, computer, view)
        self.proceed = None
        self.verify_params = verify_params
        self.search_params = search_params

        self.determine_user_entries()
        self.populate_user_entries()
        self.determine_jss_entries()
        self.populate_jss_entries()
        self.disable_interaction_jss_widgets()

        self.set_to_middle(view)

    def proceed_operation(self, sender):
        if sender == "user":
            self.store_user_verification_fields()
        if sender == "jss":
            self.store_jss_verification_fields()
        self.proceed = True
        self.entry_view.destroy()

    def store_user_verification_fields(self):
        for param in self.verify_params.enabled:
            self.store_entry_field(param)

    def store_jss_verification_fields(self):
        for param in self.verify_params.enabled:
            self.store_jss_entry_field(param)

    def populate_user_entries(self):
        for param in self.verify_params.enabled:
            self.populate_user_entry(param)

    def populate_jss_entries(self):
        for param in self.verify_params.enabled:
            self.populate_jss_entry(param)

    def determine_user_entries(self):
        self.entry_view.user_lbl.grid(row=0, column=1)
        for param in self.verify_params.enabled:
            self.determine_user_widget(param)

    def determine_jss_entries(self):
        self.entry_view.jss_lbl.grid(row=0, column=3)
        for param in self.verify_params.enabled:
            self.determine_jss_widget(param)

    def cancel_operation(self):
        self.proceed = False
        self.entry_view.destroy()

    def disable_interaction_jss_widgets(self):
        self.entry_view.jss_barcode_1_entry.config(state="disabled")
        self.entry_view.jss_barcode_2_entry.config(state="disabled")
        self.entry_view.jss_asset_entry.config(state="disabled")
        self.entry_view.jss_name_entry.config(state="disabled")
        self.entry_view.jss_serial_entry.config(state="disabled")

    def determine_jss_widget(self, input_type):
        if input_type == "barcode_1":
            self.entry_view.jss_barcode_1_lbl.grid(row=1, column=2, sticky="E")
            self.entry_view.jss_barcode_1_entry.grid(row=1, column=3)

        elif input_type == "barcode_2":
            self.entry_view.jss_barcode_2_lbl.grid(row=2, column=2, sticky="E")
            self.entry_view.jss_barcode_2_entry.grid(row=2, column=3)

        elif input_type == "asset_tag":
            self.entry_view.jss_asset_lbl.grid(row=3, column=2, sticky="E")
            self.entry_view.jss_asset_entry.grid(row=3, column=3)

        elif input_type == "computer_name":
            self.entry_view.jss_name_lbl.grid(row=4, column=2, sticky="E")
            self.entry_view.jss_name_entry.grid(row=4, column=3)

        elif input_type == "serial_number":
            self.entry_view.jss_serial_lbl.grid(row=5, column=2, sticky="E")
            self.entry_view.jss_serial_entry.grid(row=5, column=3, sticky='E')

    def populate_jss_entry(self, input_type):
        none_filter = lambda x: "" if x is None else x

        if input_type == 'barcode_1':
            self.entry_view.jss_barcode_1_entry.insert(0, "{}".format(none_filter(self.computer.prev_barcode_1)))

        elif input_type == 'barcode_2':
            self.entry_view.jss_barcode_2_entry.insert(0, "{}".format(none_filter(self.computer.prev_barcode_2)))

        elif input_type == 'asset_tag':
            self.entry_view.jss_asset_entry.insert(0, "{}".format(none_filter(self.computer.prev_asset_tag)))

        elif input_type == 'computer_name':
            self.entry_view.jss_name_entry.insert(0, "{}".format(none_filter(self.computer.prev_name)))

        elif input_type == 'serial_number':
            self.entry_view.jss_serial_entry.insert(0, "{}".format(none_filter(self.computer.prev_serial_number)))

    def store_jss_entry_field(self, input_type):
        if input_type == "barcode_1":
            if self.entry_view.jss_barcode_1_entry.get() != "":
                self.computer.barcode_1 = self.entry_view.jss_barcode_1_entry.get()

        elif input_type == "barcode_2":
            if self.entry_view.jss_barcode_2_entry.get() != "":
                self.computer.barcode_2 = self.entry_view.jss_barcode_2_entry.get()

        elif input_type == "asset_tag":
            if self.entry_view.jss_asset_entry.get() != "":
                self.computer.asset_tag = self.entry_view.jss_asset_entry.get()

        elif input_type == "computer_name":
            if self.entry_view.jss_name_entry.get() != "":
                self.computer._name = self.entry_view.jss_name_entry.get()

        elif input_type == "serial_number":
            if self.entry_view.jss_serial_entry.get() != "":
                self.computer.serial_number = self.entry_view.jss_serial_entry.get()


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)