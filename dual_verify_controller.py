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

from entry_controller import EntryController
import inspect
from management_tools import loggers
import os
from dual_verify_view import DualVerifyView


class DualVerifyController(EntryController):
    """Controls DualVerifyView.

    Inherits from EntryController.
    This is class receives input from the user and from the JSS and displays it in the DualVerifyView for
    comparision.

    Attributes
        proceed (bool): Status on how the view was closed. If the view is closed by the x button, proceed is False,
                        otherwise, it's True.

    """
    def __init__(self, master, computer, verify_params, jss_server):
        """Stores view and shows and populates widgets according to search params."""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create view and store it in the super class.
        view = DualVerifyView(master, self)
        super(DualVerifyController, self).__init__(computer, view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.proceed = False
        self._verify_params = verify_params
        self._jss_server = jss_server
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Determine which widgets to show based off the verify params
        self._grid_user_widgets(verify_params)
        self._grid_jss_widgets(verify_params)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Fill the JSS attributes in the computer object.
        self.get_jss_data(self.computer, jss_server)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Populate the widgets based off the verify params
        self._fill_user_entries(computer, verify_params)
        self._fill_jss_entries(computer, verify_params)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Disable editing of the JSS widgets
        self._disable_jss_entries()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Center the view
        self._set_to_middle(view)

    def proceed_operation(self, sender):
        """Stores verification fields in Computer object, sets proceed to True, and destroys the dual verify view.

        Args:
            sender (str): Identifier of button that called proceed_operation.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If the sender buttons ID is 'user', store the user fields
        if sender == "user":
            self._store_user_entries(self.computer, self._verify_params)
            self._store_conflicts(self.computer)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If the sender buttons ID is 'jss', store the jss fields
        if sender == "jss":
            self._store_jss_entries(self.computer, self._verify_params)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.set_proceed(True)
        self.entry_view.destroy()

    def cancel_operation(self):
        """Signals that operation has been canceled by setting proceed to False. Destroys entry view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.proceed = False
        self.entry_view.destroy()

    def set_proceed(self, proceed):
        self.proceed = proceed

    def get_jss_data(self, computer, jss_server):
        """Get the JSS data for a computer object and store it in the computer object.

        Args:
            computer (Computer): Stores information about the computer.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the JSS data for the computer.
        computer.jss_barcode_1 = jss_server.get_barcode_1(computer.jss_id)
        computer.jss_barcode_2 = jss_server.get_barcode_2(computer.jss_id)
        computer.jss_asset_tag = jss_server.get_asset_tag(computer.jss_id)
        computer.jss_serial_number = jss_server.get_serial(computer.jss_id)
        computer.prev_name = jss_server.get_name(computer.jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.debug("Previous barcode_1: {}".format(computer.jss_barcode_1))
        logger.debug("Previous barcode_2: {}".format(computer.jss_barcode_2))
        logger.debug("Previous asset_tag: {}".format(computer.jss_asset_tag))
        logger.debug("Previous serial_number: {}".format(computer.jss_serial_number))
        logger.debug("Previous name: {}".format(computer.prev_name))

    def _store_conflicts(self, computer):
        # Check to see what fields changed after the user updated the fields through the entry view window.
        if computer.barcode_1 and computer.barcode_1 != computer.jss_barcode_1:
            computer.incorrect_barcode_1 = computer.jss_barcode_1
            logger.debug("barcode_1 {} is incorrect.".format(computer.incorrect_barcode_1))

        if computer.barcode_2 and computer.barcode_2 != computer.jss_barcode_2:
            computer.incorrect_barcode_2 = computer.jss_barcode_2
            logger.debug("barcode_2 {} is incorrect.".format(computer.incorrect_barcode_2))

        if computer.asset_tag and computer.asset_tag != computer.jss_asset_tag:
            computer.incorrect_asset = computer.jss_asset_tag
            logger.debug("asset_tag {} is incorrect.".format(computer.incorrect_asset))

        if computer.serial_number and computer.jss_serial_number != computer.get_serial():
            computer.serial_number = computer.get_serial()
            computer.incorrect_serial = self._jss_server.get_serial(computer.jss_id)
            logger.debug("JSS serial {} is incorrect.".format(computer.incorrect_serial))

    def _store_user_entries(self, computer, verify_params):
        """Store the user fields in the Computer object.

        Args:
            computer (Computer): Stores information about the computer.
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter that is enabled, store its value in the Computer object.
        for param in verify_params.enabled:
            self._store_user_entry(computer, param)

    def _store_jss_entry(self, computer, input_type):
        """Store data from JSS entry in Computer.

        Args:
            computer (Computer): Stores information about the computer.
            input_type (str): Data ID.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store data from the JSS entry for barcode 1
        if input_type == "barcode_1":
            if self.entry_view.jss_barcode_1_entry.get() != "":
                computer.barcode_1 = self.entry_view.jss_barcode_1_entry.get()

        # Store data from the JSS entry for barcode 2
        elif input_type == "barcode_2":
            if self.entry_view.jss_barcode_2_entry.get() != "":
                computer.barcode_2 = self.entry_view.jss_barcode_2_entry.get()

        # Store data from the JSS entry for asset tag
        elif input_type == "asset_tag":
            if self.entry_view.jss_asset_entry.get() != "":
                computer.asset_tag = self.entry_view.jss_asset_entry.get()

        # Store data from the JSS entry for computer name
        elif input_type == "computer_name":
            if self.entry_view.jss_name_entry.get() != "":
                computer.name = self.entry_view.jss_name_entry.get()

        # Store data from the JSS entry for serial number
        elif input_type == "serial_number":
            if self.entry_view.jss_serial_entry.get() != "":
                computer.serial_number = self.entry_view.jss_serial_entry.get()

    def _store_jss_entries(self, computer, verify_params):
        """Store the JSS fields in the Computer object.

        Args:
            computer (Computer): Stores information about the computer.
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter that is enabled, store its value in the Computer object.
        for param in verify_params.enabled:
            self._store_jss_entry(computer, param)

    def _fill_user_entries(self, computer, verify_params):
        """Populates the user entries with user entered data contained in the Computer object. It knows which fields to
        populated from the verification parameters.

        Args:
            computer (Computer): Stores information about the computer.
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter that is enabled, populate its entry with JSS data from the Computer object.
        for param in verify_params.enabled:
            self._fill_user_entry(computer, param)

    def _fill_jss_entries(self, computer, verify_params):
        """Populates the user entries with JSS data contained in the Computer object. It knows which fields to
        populated from the verification parameters.

        Args:
            computer (Computer): Stores information about the computer.
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter enabled, populate its entry with user entered data from the Computer object.
        for param in verify_params.enabled:
            self._fill_jss_entry(computer, param)

    def _fill_jss_entry(self, computer, data_id):
        """Fills the JSS entry with JSS data stored in the Computer object that corresponds to the input.

        Args:
            computer (Computer): Store information about the computer.
            data_id (str): Data ID.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Lambda expression explanation:
        # If input is None, return "" instead of None. Otherwise return the value of the input. This is used below
        # to filter out None when filling the entries:
        #
        #    If the requested data from Computer is None, fill the entry with empty sting "" instead of None. Otherwise
        #    fill the entry with the data value.

        none_filter = lambda x: "" if x is None else x
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Fill barcode 1 entry
        if data_id == 'barcode_1':
            self.entry_view.jss_barcode_1_entry.insert(0, "{}".format(none_filter(computer.jss_barcode_1)))

        # Fill barcode 2 entry
        elif data_id == 'barcode_2':
            self.entry_view.jss_barcode_2_entry.insert(0, "{}".format(none_filter(computer.jss_barcode_2)))

        # Fill asset tag entry
        elif data_id == 'asset_tag':
            self.entry_view.jss_asset_entry.insert(0, "{}".format(none_filter(computer.jss_asset_tag)))

        # Fill computer name entry
        elif data_id == 'computer_name':
            self.entry_view.jss_name_entry.insert(0, "{}".format(none_filter(computer.prev_name)))

        # Fill serial number entry
        elif data_id == 'serial_number':
            self.entry_view.jss_serial_entry.insert(0, "{}".format(none_filter(computer.jss_serial_number)))

    def _grid_user_widgets(self, verify_params):
        """Grids user entry widgets in the view according to the verification params.

        Args:
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Show the user label.
        self.entry_view.user_lbl.grid(row=0, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter enabled, build its corresponding widget.
        for param in verify_params.enabled:
            self._grid_user_widget(param)

    def _grid_jss_widget(self, input_type):
        """Grids JSS widgets that corresponds to the input.

        Args:
            input_type (str): Data ID.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid barcode 1 widgets
        if input_type == "barcode_1":
            self.entry_view.jss_barcode_1_lbl.grid(row=1, column=2, sticky="E")
            self.entry_view.jss_barcode_1_entry.grid(row=1, column=3)

        # Grid barcode 2 widgets
        elif input_type == "barcode_2":
            self.entry_view.jss_barcode_2_lbl.grid(row=2, column=2, sticky="E")
            self.entry_view.jss_barcode_2_entry.grid(row=2, column=3)

        # Grid asset tag widgets
        elif input_type == "asset_tag":
            self.entry_view.jss_asset_lbl.grid(row=3, column=2, sticky="E")
            self.entry_view.jss_asset_entry.grid(row=3, column=3)

        # Grid computer name widgets
        elif input_type == "computer_name":
            self.entry_view.jss_name_lbl.grid(row=4, column=2, sticky="E")
            self.entry_view.jss_name_entry.grid(row=4, column=3)

        # Grid serial number widgets
        elif input_type == "serial_number":
            self.entry_view.jss_serial_lbl.grid(row=5, column=2, sticky="E")
            self.entry_view.jss_serial_entry.grid(row=5, column=3, sticky='E')

    def _grid_jss_widgets(self, verify_params):
        """Grids jss entry widgets in the view according to the verification params.

        Args:
            verify_params (VerifyParams): Specifies which verification fields are enabled.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Show the JSS label.
        self.entry_view.jss_lbl.grid(row=0, column=3)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every verification parameter enabled, build its corresponding widget.
        for param in verify_params.enabled:
            self._grid_jss_widget(param)

    def _disable_jss_entries(self):
        """Disables interaction with JSS widgets.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Disable interaction with entries.
        state = "disabled"
        self.entry_view.jss_barcode_1_entry.config(state=state)
        self.entry_view.jss_barcode_2_entry.config(state=state)
        self.entry_view.jss_asset_entry.config(state=state)
        self.entry_view.jss_name_entry.config(state=state)
        self.entry_view.jss_serial_entry.config(state=state)


# Start logging.
cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))
