#!/usr/bin/python

# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2019 University of Utah Student Computing Labs.
# All Rights Reserved.
#
# Author: Thackery Archuletta
# Creation Date: Oct 2018
# Last Updated: Feb 2019
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

import Tkinter as tk
import inspect
import os
from management_tools import loggers


class EntryView(tk.Toplevel):
    """Entry view for entering data.

    Attributes
        text_lbl (Label): Contains text for header frame.

        user_lbl (Label): Label denoting user widgets.
        barcode_1_lbl (Label): Label denoting barcode 1 entry.
        barcode_2_lbl (Label): Label denoting barcode 2 entry.
        asset_lbl (Label): Label denoting asset entry.
        name_lbl (Label): Label denoting name entry.
        serial_lbl (Label): Label denoting serial number entry.

        barcode_1_entry (Entry): Barcode 1 entry.
        barcode_2_entry (Entry): Barcode 2 entry.
        asset_entry (Entry): Asset entry.
        name_entry (Entry): Name entry.
        serial_entry (Entry): Serial number entry.

    """
    def __init__(self, master, controller):
        """Initializes view.

        Args:
            master: Master Tk window.
            controller (DualVerifyController): Controller for this view.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        tk.Toplevel.__init__(self, master)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the action for when the window is closed using the close button
        self.protocol('WM_DELETE_WINDOW', self._close_button_clicked)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make it so only the view window can be interacted with.
        self.transient(master)
        self.grab_set()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store the controller
        self._controller = controller
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the window's title.
        self.title("Create New JSS Record")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create two frames inside the window.
        header_frame = tk.Frame(self)
        content_frame = tk.Frame(self)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind Return key to the user submit button
        self.bind('<Return>', lambda event: self._submit_btn_clicked())
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Creating and adding components to subframes
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>v
        # Text header widget
        self.text_lbl = tk.Label(header_frame, text='Please enter the following field:')
        self.text_lbl.grid(row=0)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # User header
        self.user_lbl = tk.Label(content_frame, text="Entered by user:")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Barcode_1 widget
        self.barcode_1_lbl = tk.Label(content_frame, text='Barcode 1:')
        self.barcode_1_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Barcode_2 widget
        self.barcode_2_lbl = tk.Label(content_frame, text='Barcode 2:')
        self.barcode_2_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Asset widget
        self.asset_lbl = tk.Label(content_frame, text='Asset Tag:')
        self.asset_entry = self.asset_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Name widget
        self.name_lbl = tk.Label(content_frame, text='Name:')
        self.name_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Serial widget
        self.serial_lbl = tk.Label(content_frame, text='Serial #')
        self.serial_entry = tk.Entry(content_frame)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Submit button
        self._user_submit_btn = tk.Button(content_frame, text='Submit', command=self._submit_btn_clicked)
        self._user_submit_btn.grid(row=6, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid the frames.
        header_frame.grid(row=0)
        content_frame.grid(row=1)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>^

    def _close_button_clicked(self):
        logger.debug("Close button clicked.")
        self._controller.cancel_operation()

    def _submit_btn_clicked(self):
        logger.debug("Submit button clicked.")
        self._controller.proceed_operation()


# Start logging.
cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))
