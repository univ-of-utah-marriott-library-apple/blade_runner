import Tkinter as tk
import ttk

class MainView(tk.Toplevel):
    def __init__(self, master, controller):
        tk.Toplevel.__init__(self, master)
        # self.master = master
        self.title("Blade Runner")
        self.protocol('WM_DELETE_WINDOW', self.exit_btn_clicked)

        # Set the controller
        self.controller = controller

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Creating components
        self.header = tk.Label(self, text="Blade-Runner", font=("Copperplate", 40))
        self.header.grid(row=0)

        self.selection_lbl = tk.Label(self)

        self.choose_lbl = tk.Label(self, text="Select an offboard configuration file below.")
        self.choose_lbl.grid(row=2)

        self.combobox = ttk.Combobox(self)
        self.combobox.grid(row=3, column=0, stick='EW')

        self.next_btn = tk.Button(self, text="Next", fg='blue', command=lambda: self.next_btn_clicked())
        self.next_btn.grid(row=4, column=0, sticky='EW')

        self.serial_btn = tk.Button(self, text="Get Serial Number", fg='blue', command=lambda: self.input_btn_clicked('serial_number'))
        # self.barcode_btn = tk.Button(self, text="Enter Barcode Number", command=lambda: self.barcode_btn_clicked())
        # self.asset_btn = tk.Button(self, text="Enter Asset Number", command=lambda: self.asset_btn_clicked())

        self.barcode_1_btn = tk.Button(self, text="Enter Barcode 1", command=lambda: self.input_btn_clicked('barcode_1'))
        self.barcode_2_btn = tk.Button(self, text="Enter Barcode 2", command=lambda: self.input_btn_clicked('barcode_2'))
        self.asset_btn = tk.Button(self, text="Enter Asset Number", command=lambda: self.input_btn_clicked('asset_tag'))

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind the return key to the serial button
        self.bind('<Return>', lambda event: self.next_btn_clicked())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # After the window loads, the function is fired. This is the Map event, or when the window has mapped.
        self.bind('<Map>', lambda event: self.populate_combobox())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the window to the middle of the screen
        self.controller.set_to_middle(self)

    def input_btn_clicked(self, input_type):
        if input_type == 'barcode_1':
            self.controller.determine_input_type(input_type)
        if input_type == 'barcode_2':
            self.controller.determine_input_type(input_type)
        if input_type == 'asset_tag':
            self.controller.determine_input_type(input_type)
        if input_type == 'serial_number':
            self.controller.determine_input_type(input_type)

    def next_btn_clicked(self):
        self.options_scene()
        self.bind('<Return>', lambda event: self.serial_btn_clicked())
        self.controller.save_offboard_config(self.combobox.get())

    def serial_btn_clicked(self):
        self.controller.serial_input()

    def barcode_btn_clicked(self):
        self.controller.barcode_1_input()

    def asset_btn_clicked(self):
        self.controller.asset_input()

    def exit_btn_clicked(self):
        self.master.destroy()

    def populate_combobox(self):
        self.controller.populate_config_combobox()

    def options_scene(self):
        self.next_btn.grid_forget()

        self.selection_lbl.grid(row=1)
        self.selection_lbl.config(text="Current configuration file: " + self.combobox.get())

        self.choose_lbl.config(text="Choose one of the following options:")

        self.serial_btn.grid(row=2, column=0, sticky='EW')

        if self.controller.verify_data['barcode_1'] is True:
            self.barcode_1_btn.grid(row=3, column=0, sticky='EW')

        if self.controller.verify_data['barcode_2'] is True:
            self.barcode_2_btn.grid(row=4, column=0, sticky='EW')

        if self.controller.verify_data['asset_tag'] is True:
            self.asset_btn.grid(row=5, column=0, sticky='EW')



