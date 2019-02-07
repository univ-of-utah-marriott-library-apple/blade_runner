from controller import Controller


class EntryController(Controller):
    def __init__(self, master, computer, view):
        self.computer = computer
        self.entry_view = view

    def store_entry_field(self, input_type):
        if input_type == "barcode_1":
            if self.entry_view.barcode_1_entry.get() != "":
                self.computer.barcode_1 = self.entry_view.barcode_1_entry.get()
                return True

        elif input_type == "barcode_2":
            if self.entry_view.barcode_2_entry.get() != "":
                self.computer.barcode_2 = self.entry_view.barcode_2_entry.get()
                return True

        elif input_type == "asset_tag":
            if self.entry_view.asset_entry.get() != "":
                self.computer.asset_tag = self.entry_view.asset_entry.get()
                return True

        elif input_type == "computer_name":
            if self.entry_view.name_entry.get() != "":
                self.computer.name = self.entry_view.name_entry.get()
                return True

        elif input_type == "serial_number":
            if self.entry_view.serial_entry.get() != "":
                self.computer.serial_number = self.entry_view.serial_entry.get()
                return True

        return False

    def populate_user_entry(self, input_type):
        none_filter = lambda x: "" if x is None else x

        if input_type == 'barcode_1':
            self.entry_view.barcode_1_entry.insert(0, "{}".format(none_filter(self.computer.barcode_1)))

        elif input_type == 'barcode_2':
            self.entry_view.barcode_2_entry.insert(0, "{}".format(none_filter(self.computer.barcode_2)))

        elif input_type == 'asset_tag':
            self.entry_view.asset_entry.insert(0, "{}".format(none_filter(self.computer.asset_tag)))

        elif input_type == 'computer_name':
            self.entry_view.name_entry.insert(0, "{}".format(none_filter(self.computer.name)))

        elif input_type == 'serial_number':
            self.entry_view.serial_entry.insert(0, "{}".format(none_filter(self.computer.serial_number)))

    def determine_user_widget(self, input_type):
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

        elif input_type == "serial_number":
            self.entry_view.serial_lbl.grid(row=5, column=0, sticky="E")
            self.entry_view.serial_entry.grid(row=5, column=1, sticky='E')

    def focus_entry(self, input_type):
        if input_type == "barcode_1":
            self.entry_view.barcode_1_entry.focus()

        elif input_type == "barcode_2":
            self.entry_view.barcode_2_entry.focus()

        elif input_type == "asset_tag":
            self.entry_view.asset_entry.focus()

        elif input_type == "computer_name":
            self.entry_view.name_entry.focus()

        elif input_type == "serial_number":
            self.entry_view.serial_entry.focus()

    # def populate_entry(self, input_type, source):
    #     none_filter = lambda x: "" if x is None else x
    #
    #     if source == "user":
    #         barcode_1 = self.computer.barcode_1
    #         barcode_2 = self.computer.barcode_2
    #         asset_tag = self.computer.asset_tag
    #         name = self.computer.name
    #         serial_number = self.computer.serial_number
    #
    #     elif source == "jss":
    #         barcode_1 = self.computer.prev_barcode_1
    #         barcode_2 = self.computer.prev_barcode_2
    #         asset_tag = self.computer.prev_asset_tag
    #         name = self.computer.prev_name
    #         serial_number = self.computer.prev_serial_number
    #
    #     if input_type == 'barcode_1':
    #         self.entry_view.barcode_1_entry.insert(0, "{}".format(none_filter(barcode_1)))
    #
    #     elif input_type == 'barcode_2':
    #         self.entry_view.barcode_2_entry.insert(0, "{}".format(none_filter(barcode_2)))
    #
    #     elif input_type == 'asset_tag':
    #         self.entry_view.asset_entry.insert(0, "{}".format(none_filter(asset_tag)))
    #
    #     elif input_type == 'computer_name':
    #         self.entry_view.name_entry.insert(0, "{}".format(none_filter(name)))
    #
    #     elif input_type == 'serial_number':
    #         self.entry_view.serial_entry.insert(0, "{}".format(none_filter(serial_number)))





