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


class StallWindow(tk.Toplevel):
    """StallWindow displays a message informing the user of the callback being run, runs the callback function,
    prevents the parent window from being interacted with, and closes itself after the callback has finished.
    """

    def __init__(self, master, callback, msg):
        """Initializes a stall window.

        Args:
            master: Master Tk window.
            callback (func): The function to be called.
            msg (str): Message to be displayed in window.

        Notes:
            callback is the name of the function without ().

        Examples:

            def awesome_func():
                print('I am awesome.')

            # Set the function as the callback for the StallWindow.
            StallWindow(master_window, awesome_func, "Running my awesome function!")

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        tk.Toplevel.__init__(self, master)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the action for when the window is closed using the close button
        self.protocol('WM_DELETE_WINDOW', self._dummy_btn)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make it so only the view window can be interacted with.
        self.transient(master)
        self.grab_set()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the window's title.
        self.title("Waiting for process to complete.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a content frame.
        content_frame = tk.Frame(self, height=master.winfo_width())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Text header widget
        self.text_lbl = tk.Label(content_frame, text=msg, wraplength=self.master.winfo_width())
        self.text_lbl.grid(row=0, padx=(20, 20), pady=(20, 20))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grid the content frame.
        content_frame.grid(row=0)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # After 2 seconds, run run_callback(callback).
        master.after(2000, lambda: self._run_callback(callback))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the window to the middle of the screen
        self._set_to_middle(self)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Wait for the window to be closed.
        self.wait_window()

    def _run_callback(self, callback):
        """Runs the callback function and destroys the StallWindow after the callback has finished.

        Args:
            callback (func): The callback function.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run the callback function
        callback()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroy the StallWindow.
        self._destroy()

    def _dummy_btn(self):
        """Dummy button. Does nothting. Prevents the StallWindow from being closed.

        Returns:
            void
        """
        pass

    def _destroy(self):
        """Destroys the StallWindow.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroy the StallWindow
        self.destroy()

    def _set_to_middle(self, window):
        """Sets a Tkinter window to the center of the screen.

        Args:
            window: Tkinter window.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Updates window info to current window state
        window.update_idletasks()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Sets window position
        window.geometry('+{}+{}'.format(screen_width / 2 - window.winfo_width()/2, screen_height / 4))


# Start logging.
cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))
