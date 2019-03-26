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

from controller import Controller


class EntryController(Controller):
    """Entry controller. Stores values from entries. Fills entries. Grids widgets to view."""

    def __init__(self, computer, view):
        """Initializes entry controller.

        Args:
            computer (Computer): Used to store and fill entries.
            view: Controller's view.
        """
        self.computer = computer
        self.entry_view = view

    def _store_user_entry(self, computer, data_id):
        """Stores the data from the entry that matches the data ID. The data gets stored in the Computer object.

        Args:
            computer (Computer): Stores data in entry.
            data_id (str): data ID for the data requested.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store barcode 1 in Computer's barcode 1 attribute.
        if data_id == "barcode_1":
            if self.entry_view.barcode_1_entry.get() != "":
                computer.barcode_1 = self.entry_view.barcode_1_entry.get()
                return True

        # Store barcode 2 in Computer's barcode 2 attribute.
        elif data_id == "barcode_2":
            if self.entry_view.barcode_2_entry.get() != "":
                computer.barcode_2 = self.entry_view.barcode_2_entry.get()
                return True

        # Store asset tag in Computer's asset tag attribute.
        elif data_id == "asset_tag":
            if self.entry_view.asset_entry.get() != "":
                computer.asset_tag = self.entry_view.asset_entry.get()
                return True

        # Store computer name in Computer's name attribute.
        elif data_id == "computer_name":
            if self.entry_view.name_entry.get() != "":
                computer.name = self.entry_view.name_entry.get()
                return True

        # Store serial number in Computer's serial number attribute.
        elif data_id == "serial_number":
            if self.entry_view.serial_entry.get() != "":
                computer.serial_number = self.entry_view.serial_entry.get()
                return True

        return False

    def _fill_user_entry(self, computer, data_id):
        """Fill the entry with JSS data from Computer attribute that corresponds to the data ID.

        Args:
            computer (Computer): Supplies entry with data.
            data_id (str): Specifies data requested.

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
            self.entry_view.barcode_1_entry.insert(0, "{}".format(none_filter(computer.barcode_1)))

        # Fill barcode 2 entry
        elif data_id == 'barcode_2':
            self.entry_view.barcode_2_entry.insert(0, "{}".format(none_filter(computer.barcode_2)))

        # Fill asset tag entry
        elif data_id == 'asset_tag':
            self.entry_view.asset_entry.insert(0, "{}".format(none_filter(computer.asset_tag)))

        # Fill name entry
        elif data_id == 'computer_name':
            self.entry_view.name_entry.insert(0, "{}".format(none_filter(computer.name)))

        # Fill serial entry
        elif data_id == 'serial_number':
            self.entry_view.serial_entry.insert(0, "{}".format(none_filter(computer.serial_number)))

    def _grid_user_widget(self, data_id):
        """Grids user widgets.

        Args:
            data_id (str): Specifies widgets to grid.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid barcode 1 entry
        if data_id == "barcode_1":
            self.entry_view.barcode_1_lbl.grid(row=1, column=0, sticky="E")
            self.entry_view.barcode_1_entry.grid(row=1, column=1)

        # Grid barcode 2 entry
        elif  data_id == "barcode_2":
            self.entry_view.barcode_2_lbl.grid(row=2, column=0, sticky="E")
            self.entry_view.barcode_2_entry.grid(row=2, column=1)

        # Grid asset entry
        elif data_id == "asset_tag":
            self.entry_view.asset_lbl.grid(row=3, column=0, sticky="E")
            self.entry_view.asset_entry.grid(row=3, column=1)

        # Grid name entry
        elif data_id == "computer_name":
            self.entry_view.name_lbl.grid(row=4, column=0, sticky="E")
            self.entry_view.name_entry.grid(row=4, column=1)

        # Grid serial entry
        elif data_id == "serial_number":
            self.entry_view.serial_lbl.grid(row=5, column=0, sticky="E")
            self.entry_view.serial_entry.grid(row=5, column=1, sticky='E')

    def _focus_entry(self, data_id):
        """Move focus to entry corresponding to the data ID.

        Args:
            data_id (str): Specifies entry to focus on.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Focus on barcode 1 entry
        if data_id == "barcode_1":
            self.entry_view.barcode_1_entry.focus()

        # Focus on barcode 2 entry
        elif data_id == "barcode_2":
            self.entry_view.barcode_2_entry.focus()

        # Focus on asset entry
        elif data_id == "asset_tag":
            self.entry_view.asset_entry.focus()

        # Focus on name entry
        elif data_id == "computer_name":
            self.entry_view.name_entry.focus()

        # Focus on serial entry
        elif data_id == "serial_number":
            self.entry_view.serial_entry.focus()



