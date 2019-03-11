import Tkinter as tk


class VerifyView(tk.Toplevel):
    def __init__(self, master, controller):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self._close_button_clicked)

        # These two lines make it so only the entry_view window can be interacted with
        self.transient(master)
        self.grab_set()

        self.controller = controller
        self.title("Create New JSS Record")
        header_frame = tk.Frame(self)
        content_frame = tk.Frame(self)

        self.bind('<Return>', lambda event: self._user_submit_btn_clicked())

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Creating and adding components to subframes
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Text header component
        self.text_lbl = tk.Label(header_frame, text="No JSS record exists for this computer.\n"
                                                    "Create the new record by filling in the\n"
                                                    "following fields:\n")
        self.text_lbl.grid(row=0)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # User header
        self.user_lbl = tk.Label(content_frame, text="Entered by user:")
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
        # Serial components
        self.serial_lbl = tk.Label(content_frame, text='Serial #')
        self.serial_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

        # Submit button
        self._user_submit_btn = tk.Button(content_frame, text='Submit from User', command=self._user_submit_btn_clicked)
        self._user_submit_btn.grid(row=6, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        header_frame.grid(row=0)
        content_frame.grid(row=1)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>^

    def _close_button_clicked(self):
        self.controller.cancel_operation()

    def user_submit_btn_clicked(self):
        self.controller.proceed_operation("user")

    def jss_submit_btn_clicked(self):
        self.controller.proceed_operation("jss")

    def set_to_middle(self):
        self.controller.set_to_middle(self)
