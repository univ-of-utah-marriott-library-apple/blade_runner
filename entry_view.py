import Tkinter as tk


class EntryView(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title("Create New JSS Record")
        header_frame = tk.Frame(self)
        content_frame = tk.Frame(self)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Creating and adding components to subframes
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Text header component
        self.text_lbl = tk.Label(header_frame, text="No JSS record exists for this computer.\n"
                                            "Create the new record by filling in the\n"
                                            "following fields:")
        self.text_lbl.grid(row=0)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Barcode_1 components
        self.barcode_1_lbl = tk.Label(content_frame, text='Barcode 1:')
        self.barcode_1_entry = tk.Entry(content_frame)
        # self.barcode_1_entry.grid(row=1, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Barcode_2 components
        self.barcode_2_lbl = tk.Label(content_frame, text='Barcode 2:')
        self.barcode_2_entry = tk.Entry(content_frame)
        # self.barcode_2_entry.grid(row=2, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Asset components
        self.asset_lbl = tk.Label(content_frame, text='Asset Tag:')
        self.asset_entry = self.asset_entry = tk.Entry(content_frame)
        # self.asset_entry.grid(row=3, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Name components
        self.name_lbl = tk.Label(content_frame, text='Name:')
        self.name_entry = tk.Entry(content_frame)
        # self.name_entry.grid(row=4, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Submit button
        self.submit_btn = tk.Button(content_frame, text='Submit')
        self.submit_btn.grid(row=5, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        header_frame.grid(row=0)
        content_frame.grid(row=1)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>^
