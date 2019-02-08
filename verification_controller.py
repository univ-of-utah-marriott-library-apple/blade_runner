from entry_controller import EntryController
import inspect
from management_tools import loggers
import os
from verification_view import VerifyView


class VerificationController(EntryController):
    def __init__(self, master, computer, verify_params, search_params):
        view = VerifyView(master, self)
        super(VerificationController, self).__init__(master, computer, view)
        self.proceed = None
        self.verify_params = verify_params
        self.search_params = search_params

        self.determine_user_entries()
        self.populate_user_entries()

        self.set_to_middle(view)

    def proceed_operation(self, sender):
        self.store_user_verification_fields()
        self.proceed = True
        self.entry_view.destroy()

    def store_user_verification_fields(self):
        for param in self.verify_params.enabled:
            self.store_entry_field(param)

    def populate_user_entries(self):
        for param in self.verify_params.enabled:
            self.populate_user_entry(param)

    def determine_user_entries(self):
        self.entry_view.user_lbl.grid(row=0, column=1)
        for param in self.verify_params.enabled:
            self.determine_user_widget(param)

    def cancel_operation(self):
        self.proceed = False
        self.entry_view.destroy()



cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)