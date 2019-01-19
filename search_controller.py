from entry_controller_base import EntryController
import inspect
from management_tools import loggers
import os


class SearchController(EntryController):
    def __init__(self, master, computer, input_type):
        super(SearchController, self).__init__(master, computer)
        self.proceed = None
        self.input_type = input_type
        self.determine_widget(input_type)

    def proceed_operation(self):
        self.store_entry_field(self.input_type)
        self.proceed = True
        self.entry_view.destroy()

    def cancel_operation(self):
        self.proceed = False
        self.entry_view.destroy()


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)
