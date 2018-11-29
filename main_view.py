import Tkinter as tk


class View(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title("Blade Runner")
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Creating components
        self.header = tk.Label(self, text="Blade-Runner", font=("Copperplate", 40))
        self.header.grid(row=0)

        self.choose_lbl = tk.Label(self, text="Choose one of the following options:", )
        self.choose_lbl.grid(row=1)

        self.serial_btn = tk.Button(self, text="Get Serial Number", fg='blue')
        self.serial_btn.grid(row=2, column=0, sticky='EW')

        self.barcode_btn = tk.Button(self, text="Enter Barcode Number")
        self.barcode_btn.grid(row=3, column=0, sticky='EW')

        self.asset_btn = tk.Button(self, text="Enter Asset Number")
        self.asset_btn.grid(row=4, column=0, sticky='EW')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>