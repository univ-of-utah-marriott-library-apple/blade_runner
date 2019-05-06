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
from verification_view import VerifyView


class VerificationController(EntryController):
    """Controller for VerificationView."""

    def __init__(self, master, computer, verify_params, search_params):
        """Set up the verification controller.

        Args:
            master: Parent Tk window.
            computer (Computer): Stores information about the computer.
            verify_params (VerifyParams): Verification parameters.
            search_params (SearchParams): Search parameters.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Save the view in the superclass (EntryController).
        view = VerifyView(master, self)
        super(VerificationController, self).__init__(computer, view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store inputs.
        self.proceed = False
        self.verify_params = verify_params
        self.search_params = search_params
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid user entries.
        self._grid_user_widgets()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Fil user entries.
        self._fill_user_entries()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set view to middle of screen.
        self._set_to_middle(view)

    def proceed_operation(self):
        """If user continues with operation, store entries, set proceed to True, and destroy the view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store user entries into computer object.
        self._store_user_entries()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set proceed flag
        self.proceed = True
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroy the view.
        self.entry_view.destroy()

    def _store_user_entries(self):
        """Store user entries.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every enabled verification parameter, store the value in its corresponding entry.
        for param in self.verify_params.enabled:
            self._store_user_entry(self.computer, param)

    def _fill_user_entries(self):
        """Fill user entries with information from the computer object.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every enabled verification parameter, set its value in its corresponding entry.
        for param in self.verify_params.enabled:
            self._fill_user_entry(self.computer, param)

    def _grid_user_widgets(self):
        """Grid user widgets into the view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid the user label.
        self.entry_view.user_lbl.grid(row=0, column=1)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every enabled verification parameter, grid its corresponding widget.
        for param in self.verify_params.enabled:
            self._grid_user_widget(param)

    def cancel_operation(self):
        """If user cancels operation, set proceed to False and destroy the view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.proceed = False
        self.entry_view.destroy()


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)