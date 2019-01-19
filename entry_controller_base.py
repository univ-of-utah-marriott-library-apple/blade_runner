from controller import Controller
from entry_view_base import EntryView


class EntryController(Controller):
    def __init__(self, master, computer):
        self.computer = computer
        self.entry_view = EntryView(master, self)

    def store_entry_field(self, input_type):
        if input_type == "barcode_1":
            if self.entry_view.barcode_1_entry.get() != "":
                self.computer.barcode_1 = self.entry_view.barcode_1_entry.get()

        elif input_type == "barcode_2":
            if self.entry_view.barcode_2_entry.get() != "":
                self.computer.barcode_2 = self.entry_view.barcode_2_entry.get()

        elif input_type == "asset_tag":
            if self.entry_view.asset_entry.get() != "":
                self.computer.asset_tag = self.entry_view.asset_entry.get()

        elif input_type == "computer_name":
            if self.entry_view.name_entry.get() != "":
                self.computer.name = self.entry_view.name_entry.get()

    def determine_widget(self, input_type):
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