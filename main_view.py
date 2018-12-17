import Tkinter as tk


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

        self.choose_lbl = tk.Label(self, text="What is the inventory status of this computer?")
        self.choose_lbl.grid(row=2)

        self.salvage_btn = tk.Button(self, text="Salvage", fg='blue', command=lambda: self.salvage_btn_clicked())
        self.salvage_btn.grid(row=3, column=0, sticky='EW')

        self.storage_btn = tk.Button(self, text="Storage", command=lambda: self.storage_btn_clicked())
        self.storage_btn.grid(row=4, column=0, sticky='EW')

        self.serial_btn = tk.Button(self, text="Get Serial Number", fg='blue', command=lambda: self.serial_btn_clicked())
        self.barcode_btn = tk.Button(self, text="Enter Barcode Number", command=lambda: self.barcode_btn_clicked())
        self.asset_btn = tk.Button(self, text="Enter Asset Number", command=lambda: self.asset_btn_clicked())

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind the return key to the serial button
        self.bind('<Return>', self.serial_btn_clicked)

        # Set the window to the middle of the screen
        self.controller.set_to_middle(self)

    def serial_btn_clicked(self):
        self.controller.serial_input()

    def barcode_btn_clicked(self):
        self.controller.barcode_input()

    def asset_btn_clicked(self):
        self.controller.asset_input()

    def salvage_btn_clicked(self):
        self.controller.options_scene(self.salvage_btn)

    def storage_btn_clicked(self):
        self.controller.options_scene(self.storage_btn)

    def exit_btn_clicked(self):
        self.master.destroy()


