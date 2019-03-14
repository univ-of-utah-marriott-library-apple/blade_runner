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

import Tkinter as tk
import ttk


class MainView(tk.Toplevel):
    """The main Blade-Runner view that is displayed at startup and serves as the home view.

    Attributes
        header (Label): Header label.
        selection_lbl (Label): Selection label.
        choose_lbl (Label): Instructional label.
        combobox (Combobox): Shows available offboard configurations.
    """
    def __init__(self, master, controller):
        """Initializes the main view.

        Sets title, closing protocol, controller, GUI widgets, and binds keys and actions
        to functions.

        Args:
            master (Tk): the main view's master or root window
            controller (MainController): the main view's controller
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        tk.Toplevel.__init__(self, master)
        self.title("Blade Runner")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the action for when the window is closed using the close button
        self.protocol('WM_DELETE_WINDOW', self._exit_btn_clicked)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # The main views controller
        self._controller = controller
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Creating components
        self.header = tk.Label(self, text="Blade-Runner", font=("Copperplate", 40))
        self.header.grid(row=0)

        self.selection_lbl = tk.Label(self)

        self.choose_lbl = tk.Label(self, text="Select an offboard configuration file below.")
        self.choose_lbl.grid(row=2)

        self.combobox = ttk.Combobox(self)
        self.combobox.grid(row=3, column=0, stick='EW')

        self._next_btn = tk.Button(self, text="Next", fg='blue', command=lambda: self._next_btn_clicked())
        self._next_btn.grid(row=4, column=0, sticky='EW')

        self._serial_btn = tk.Button(self, text="Get Serial Number", fg='blue', command=lambda: self._input_btn_clicked('serial_number'))

        self._barcode_1_btn = tk.Button(self, text="Enter Barcode 1", command=lambda: self._input_btn_clicked('barcode_1'))

        self._barcode_2_btn = tk.Button(self, text="Enter Barcode 2", command=lambda: self._input_btn_clicked('barcode_2'))

        self._asset_btn = tk.Button(self, text="Enter Asset Number", command=lambda: self._input_btn_clicked('asset_tag'))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind the return key to the serial button
        self.bind('<Return>', lambda event: self._next_btn_clicked())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # After the window loads, the function is fired. This is the Map event, or when the window has finished being
        # constructed.
        self.bind('<Map>', lambda event: self.populate_combobox())

    def _input_btn_clicked(self, identifier):
        """
        Takes the identifier of the button pressed and passes it to the controller. The controller then acts
        according to the identifier received.

        Args:
            identifier (str): identifier corresponding to the button pressed

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self._controller.search_sequence(identifier)

    def _next_btn_clicked(self):
        """
        When the next button is clicked, the selected offboard configuration is saved in the controller and the main
        view changes to the 'options scene'. This scene gives the available ways to search the JSS.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Switch to the options scene.
        self.main_scene()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Bind the Return key to the input function.
        self.bind('<Return>', lambda event: self._input_btn_clicked('serial_number'))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Save the selected offboard configuration into the controller.
        self._controller.save_offboard_config(self.combobox.get())

    def _exit_btn_clicked(self):
        """
        This is bound to the WM_DELETE_WINDOW in __init__() and is called when the red x button is pressed.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroys the main view and master/root Tk window.
        self._controller.terminate()

    def populate_combobox(self):
        """
        Populates the combobox with the available offboard configurations (xml files).

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Calls the populate function in the controller. That function does the actual populating.
        self._controller.populate_config_combobox()

    def main_scene(self):
        """
        Sets the main scene. This scene contains the available JSS search options in the form of buttons. Which
        buttons are shown is determined by the SearchParams object. The SearchParams object is created from the search
        params configuration file in the MainController.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove the next button from the view.
        self._next_btn.grid_forget()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Add and configure the selection label.
        self.selection_lbl.grid(row=1)
        self.selection_lbl.config(text="Current configuration file: " + self.combobox.get())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Reconfigure the choose label.
        self.choose_lbl.config(text="Choose one of the following options:")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Determine which buttons to show according to the enabled search params. These search params are
        # read from the search params config file and stored in a SearchParams object.
        if 'serial_number' in self._controller.search_params.enabled:
            self._serial_btn.grid(row=2, column=0, sticky='EW')

        if 'barcode_1' in self._controller.search_params.enabled:
            self._barcode_1_btn.grid(row=3, column=0, sticky='EW')

        if 'barcode_2' in self._controller.search_params.enabled:
            self._barcode_2_btn.grid(row=4, column=0, sticky='EW')

        if 'asset_tag' in self._controller.search_params.enabled:
            self._asset_btn.grid(row=5, column=0, sticky='EW')



