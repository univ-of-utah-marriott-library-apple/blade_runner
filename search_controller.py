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

from entry_controller import EntryController
import inspect
from management_tools import loggers
import os
from entry_view import EntryView


class SearchController(EntryController):
    """Controller for searching the JSS.
    """
    def __init__(self, master, computer, input_type):
        """Set up the search controller.

        Args:
            master: Parent Tk window.
            computer (Computer): Stores information about the computer.
            input_type (str): Data identifier.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set up the view and pass it to EntryController.
        view = EntryView(master, self)
        super(SearchController, self).__init__(computer, view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the view to the middle.
        self._set_to_middle(view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set proceed flag.
        self.proceed = False
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.input_type = input_type
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid the user widgets according to the input type.
        self._grid_user_widget(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Fill the user entries with computer information matching the input type.
        self._fill_user_entry(computer, input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Focus on the entry.
        self._focus_entry(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the view to the middle.
        self._set_to_middle(view)

    def proceed_operation(self):
        """Stores user entered data, sets proceed flag to True, and destroys the entry view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If anything was stored, set proceed flag to True and kill the view.
        if self._store_user_entry(self.computer, self.input_type):
            self.proceed = True
            self.entry_view.destroy()

    def cancel_operation(self):
        """If user cancels operation, set proceed flag to False and destroy the view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set proceed flag to False and destroy the view.
        self.proceed = False
        self.entry_view.destroy()


cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)
