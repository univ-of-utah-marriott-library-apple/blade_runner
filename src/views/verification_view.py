#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: March 2019
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies and
# that both that copyright notice and this permission notice appear
# in supporting documentation, and that the name of The University
# of Utah not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission. This software is supplied as is without expressed or
# implied warranties of any kind.
################################################################################

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


class VerifyView(tk.Toplevel):
    """View used for verifying previously entered data for a computer object."""

    def __init__(self, master, controller):
        """Build the view.

        Args:
            master: Parent Tk window.
            controller (Controller): Controller for the view.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Call __init__ for parent class.
        tk.Toplevel.__init__(self, master)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the function that is called when the "x" button is pressed.
        self.protocol('WM_DELETE_WINDOW', self._close_button_clicked)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # These two lines make it so only this window can be interacted with until it's dismissed.
        self.transient(master)
        self.grab_set()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the controller.
        self.controller = controller
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the view's title.
        self.title("Create New JSS Record")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create the frames.
        header_frame = tk.Frame(self)
        content_frame = tk.Frame(self)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind submit button to the Return key.
        self.bind('<Return>', lambda event: self._submit_btn_clicked())
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
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Barcode_2 components
        self.barcode_2_lbl = tk.Label(content_frame, text='Barcode 2:')
        self.barcode_2_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Asset components
        self.asset_lbl = tk.Label(content_frame, text='Asset Tag:')
        self.asset_entry = self.asset_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Name components
        self.name_lbl = tk.Label(content_frame, text='Name:')
        self.name_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Serial components
        self.serial_lbl = tk.Label(content_frame, text='Serial #')
        self.serial_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Submit button
        self._user_submit_btn = tk.Button(content_frame, text='Submit from User', command=self._submit_btn_clicked)
        self._user_submit_btn.grid(row=6, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        header_frame.grid(row=0)
        content_frame.grid(row=1)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>^
        self.resizable(False, False)

    def _close_button_clicked(self):
        """Cancels the operation when the close button is clicked.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Signal to the controller that the close button has been clicked.
        self.controller.cancel_operation()

    def _submit_btn_clicked(self):
        """Proceeds with operation when the user "submit" button is pressed.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Signal to the controller that the submit button has been clicked.
        self.controller.proceed_operation()

    def set_to_middle(self):
        """Sets window to middle of screen.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Signal the controller to set the view to the middle of the screen.
        self.controller.set_to_middle(self)
