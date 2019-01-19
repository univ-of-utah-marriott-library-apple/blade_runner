from entry_controller_base import EntryController
import inspect
from management_tools import loggers
import os


class VerificationController(EntryController):
    def __init__(self, master, computer, verify_params):
        super(VerificationController, self).__init__(master, computer)
        self.proceed = None
        self.verify_params = verify_params
        self.determine_widgets_from_config()

    def proceed_operation(self):
        self.store_verification_fields()
        self.proceed = True
        self.entry_view.destroy()

    def store_verification_fields(self):
        for param in self.verify_params.enabled:
            self.store_entry_field(param)

    def populate_verification_fields(self):
        none_filter = lambda x: "" if x is None else x

        if 'barcode_1' in self.verify_params.enabled:
            self.entry_view.barcode_1_entry.insert(0, "{}".format(none_filter(self.computer.barcode_1)))

        if 'barcode_2' in self.verify_params.enabled:
            self.entry_view.barcode_2_entry.insert(0, "{}".format(none_filter(self.computer.barcode_2)))

        if 'asset_tag' in self.verify_params.enabled:
            self.entry_view.asset_entry.insert(0, "{}".format(none_filter(self.computer.asset_tag)))

        if 'computer_name' in self.verify_params.enabled:
            self.entry_view.name_entry.insert(0, "{}".format(none_filter(self.computer.name)))

    def determine_widgets_from_config(self):
        for param in self.verify_params.enabled:
            self.determine_widget(param)

    def cancel_operation(self):
        self.proceed = False
        self.entry_view.destroy()


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)