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
from controller import Controller


class MsgBox(Controller):

    def __init__(self, msg):
        self.root = tk.Tk()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.root.title("WARNING")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the action for when the window is closed using the close button
        self.root.protocol('WM_DELETE_WINDOW', self._cancel_btn_clicked)
        self.root.attributes("-topmost", True)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Creating components
        
        self.text_lbl = tk.Label(self.root, text=msg)
        self.text_lbl.grid(row=0, column=0, sticky='EW')

        self._proceed_btn = tk.Button(self.root, text="Continue", command=lambda: self._proceed_btn_clicked())
        self._proceed_btn.grid(row=2, column=0, sticky='EW')

        self._cancel_btn = tk.Button(self.root, text="Cancel", command=lambda: self._cancel_btn_clicked())
        self._cancel_btn.grid(row=1, column=0, sticky='EW')
        
        self.proceed = False
        self._set_to_middle(self.root)
        self.root.bind('<Map>', lambda event: self.root.focus_force())
        self.root.mainloop()
    
    def _cancel_btn_clicked(self):
        self.proceed = False
        self.root.destroy()

    def _proceed_btn_clicked(self):
        self.proceed = True
        self.root.destroy()




