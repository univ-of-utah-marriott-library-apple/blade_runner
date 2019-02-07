from entry_controller import EntryController
import inspect
from management_tools import loggers
import os
from entry_view import EntryView


class SearchController(EntryController):
    def __init__(self, master, computer, input_type):
        view = EntryView(master, self)
        super(SearchController, self).__init__(master, computer, view)
        self.set_to_middle(view)
        self.proceed = None
        self.input_type = input_type
        self.determine_user_widget(input_type)
        self.populate_user_entry(input_type)
        self.focus_entry(input_type)
        self.set_to_middle(view)

    def proceed_operation(self):
        if self.store_entry_field(self.input_type):
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
