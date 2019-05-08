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

from Tkinter import *
import tkSimpleDialog

from blade_runner.dependencies import pexpect


class SecureEraseWindow(Toplevel):

    def __init__(self, cmd, master, cwd=None):
        Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self._close_btn_clicked)
        self.title("Secure Erase Internals Output")
        self.result = None
        self.frame = Frame(self, width=100, height=100)
        self.frame.pack(fill=None, expand=False)
        self.frame.grid_propagate(False)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.text = Text(self.frame)
        self.scrollbar = Scrollbar(self.frame, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set
        self.text.pack()
        self.text.insert(END, "Waiting for authentication...")
        self._set_to_middle(self)
        self.after(1000, lambda: self.sudo_process(cmd, self.text, cwd))

    def sudo_process(self, cmd, text, cwd):
        try:
            child = pexpect.spawn('bash', cmd, cwd=cwd)

            while not self.result:
                match = child.expect(['SECURE ERASE INTERNALS', 'attempts', 'dummy', pexpect.TIMEOUT, 'Password:'])
                if match == 4:
                    self.focus_force()
                    password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=self)
                    if not password:
                        self.result = Results(False, "User cancelled.")
                        self.destroy()
                    else:
                        child.sendline(password)
                elif match == 1:
                    msg = "Could not execute command. Password was incorrect."
                    self.result = Results(False, msg)
                    self.destroy()
                elif match == 2:
                    msg = "Reached end of output early. Process may or may not have been executed."
                    return Results(False, msg)
                elif match == 3:
                    msg = "Password prompt timed out."
                    self.result = Results(False, msg)
                elif match == 0:
                    last_line = self.dynamic_print(child, text)
                    if "0" not in last_line:
                        self.result = Results(False, "There was an error.")
                    else:
                        self.result = Results(True, "Secure erase was successful!")
                else:
                    msg = "Unknown error occurred."
                    self.result = Results(False, msg)
        except Exception as e:
            msg = "Unknown error.".format(e)
            self.result = Results(False, msg)
            raise

    def _close_btn_clicked(self):
        self.destroy()

    def dynamic_print(self, child, text):
        prev_result = None
        while child.isalive():
            line = ""
            result = child.expect(["\[[^K][^\]]*\]", "\n", "\[K"])
            if result == 0:
                line = child.after
                pos = text.index("end-1c linestart")
                text.delete(pos, END)
                text.insert(END, "\n")
                text.insert(END, line.strip())
                text.update()
                text.see("end")
            elif result == 1:
                if prev_result == 0 or prev_result == 2:
                    text.insert(END, "\n")
                line = child.before
                line = line.strip()
                text.insert(END, line + "\n")
                text.update()
                text.see("end")

            prev_result = result
        return line

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


class Results(object):

    def __init__(self, success, msg):
        self.success = success
        self.msg = msg


if __name__ == "__main__":
    master = Tk()
    master.withdraw()
    cmd = ['-c', '/usr/bin/sudo python secure_erase_internals.py; echo "Return code: $?"']

    window = SecureEraseWindow(cmd, master)
    master.wait_window(window)
