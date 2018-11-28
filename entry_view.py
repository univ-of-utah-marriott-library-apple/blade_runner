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
        # Barcode components
        barcode_lbl = tk.Label(content_frame, text='Barcode:')
        barcode_lbl.grid(row=1, column=0, sticky="E")
        self.barcode_entry = tk.Entry(content_frame)
        self.barcode_entry.grid(row=1, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Asset components
        asset_lbl = tk.Label(content_frame, text='Asset:')
        asset_lbl.grid(row=2, column=0, sticky="E")
        asset_entry = self.asset_entry = tk.Entry(content_frame)
        asset_entry.grid(row=2, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Name components
        name_lbl = tk.Label(content_frame, text='Name:')
        name_lbl.grid(row=3, column=0, sticky="E")
        self.name_entry = tk.Entry(content_frame)
        self.name_entry.grid(row=3, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Submit button
        self.submit_btn = tk.Button(content_frame, text='Submit')
        self.submit_btn.grid(row=4, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

        header_frame.grid(row=0)
        content_frame.grid(row=1)