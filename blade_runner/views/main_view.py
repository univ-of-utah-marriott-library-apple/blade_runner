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

import logging
import Tkinter as tk
import ttk

logging.getLogger(__name__).addHandler(logging.NullHandler())


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
        self.logger = logging.getLogger(__name__)
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
        self.resizable(False, False)

        self._github_url = "<INSERT GITHUB REPO>"

        # Creating components
        self.text_font = ("Avenir Next","14")

        self.frame = tk.Frame(self)
        self.combobox_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self)

        self.selection_lbl = tk.Label(self.combobox_frame)

        self._version_lbl = tk.Label(self, text="v1.0.0", font=("Avenir Next", "8"))
        self._version_lbl.grid(row=1, padx=(8,0), sticky='w')

        self.choose_lbl = tk.Label(self.combobox_frame, text="Select an offboard configuration file below.", font=self.text_font)

        self.combobox = ttk.Combobox(self.combobox_frame, width=25)

        self._offboard_btn = tk.Button(self.frame, text="Offboard", fg="blue", command=lambda: self._offboard_btn_clicked(self.curr_scene),
                                       width=25, font=self.text_font)

        self._quit_btn = tk.Button(self.bottom_frame, text="Quit", command=lambda: self._exit_btn_clicked(),
                                   font=self.text_font)

        self._back_btn = tk.Button(self.bottom_frame, text="Back", command=lambda: self._back_btn_clicked(),
                                   font=self.text_font)

        self._help_btn = tk.Button(self.bottom_frame, text="Help", command=lambda: self._help_btn_clicked(self.curr_scene),
                                   font=self.text_font)

        self._about_btn = tk.Button(self.frame, text="About", command=lambda: self._about_btn_clicked(), font=self.text_font, width=25)
        self._how_to_text_box = tk.Text(self.frame, wrap="word", font=self.text_font)
        self._how_to_scroll_bar = tk.Scrollbar(self.frame, command=self._how_to_text_box.yview)

        self._how_to_btn = tk.Button(self.frame, text="How To", command=lambda: self._how_to_btn_clicked(), font=self.text_font, width=25)

        self._settings_btn = tk.Button(self.bottom_frame, text="Settings", font=self.text_font, command=lambda: self._settings_btn_clicked(self.curr_scene))
        self._slack_config_btn = tk.Button(self.frame, text="Slack Configuration", font=self.text_font, width=25, command=lambda: self._slack_config_btn_clicked())
        self._offboard_config_btn = tk.Button(self.frame, text="Offboard Configuration", font=self.text_font, width=25, command=lambda: self._offboard_config_btn_clicked())
        self._verify_config_btn = tk.Button(self.frame, text="Verification Configuration", font=self.text_font, width=25, command=lambda: self._verify_config_btn_clicked())
        self._search_config_btn = tk.Button(self.frame, text="Search Configuration", font=self.text_font, width=25, command=lambda: self._search_config_btn_clicked())
        self._directory_config_btn = tk.Button(self.frame, text="Configuration Directory", font=self.text_font, width=25, command=lambda: self._directory_config_btn_clicked())

        self._github_btn = tk.Button(self.frame, text="Github", command=lambda: self._github_btn_clicked(), font=self.text_font, width=25)
        self._github_lbl = tk.Label(self.frame, font=self.text_font)
        self._github_entry = tk.Entry(self.frame, width=len(self._github_url), justify='center', font=('Avenir Next','14','bold'))

        self._about_lbl = tk.Label(self.frame, justify='left', font=self.text_font)
        self._how_to_lbl = tk.Label(self.frame, justify='left', font=self.text_font)

        self._serial_btn = tk.Button(self.frame, text="Serial Number", fg='blue',
                                     command=lambda: self._input_btn_clicked('serial_number'), width=25, font=self.text_font)

        self._barcode_1_btn = tk.Button(self.frame, text="Barcode 1",
                                        command=lambda: self._input_btn_clicked('barcode_1'), width=25, font=self.text_font)

        self._barcode_2_btn = tk.Button(self.frame, text="Barcode 2",
                                        command=lambda: self._input_btn_clicked('barcode_2'), width=25, font=self.text_font)

        self._asset_btn = tk.Button(self.frame, text="Asset Tag",
                                    command=lambda: self._input_btn_clicked('asset_tag'), width=25, font=self.text_font)

        self._secure_erase_btn = tk.Button(self.frame, text="Secure Erase Internal Disks",
                                           command=lambda: self._secure_erase_btn_clicked(), width=25, font=self.text_font)

        self._separator = ttk.Separator(self, orient='horizontal')
        self._separator_2 = ttk.Separator(self, orient='horizontal')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # After the window loads, the function is fired. This is the Map event, or when the window has finished being
        # constructed.
        self.bind('<Map>', lambda event: self.populate_combobox())

        self.return_id = self.bind('<Return>', lambda event: self._offboard_btn_clicked())

        # define the image

        encoded_logo = '''\
        R0lGODlhWAJRAPcAAAAAACYmJkJCQlhYWGtra319fZMAAJwAAZ8ACqAABqMADKUBFKYBG6kBHKUK
        HagFGLQBHboAHLMAFKoEIKcPIqwKJa4OKrMGI7sEIrEJJrEOKrwKKKgUJq4RLKsYK6cQJLASLq8U
        MK0dM7ATMbIeN7IeOLsTMK4jNa8hObEkPLAqPsMBIswKKsILKsQSMMcfO8chPMgjPrUmQLYtRbI1
        RLY1Srg2TLY6TrgwR7s9Uqs8TsotRsknQs46U7pBVb1EWblNWbdAVr1OYL5SZLpaa75ha7dldK5x
        fcBGW89CWcFJXs9AV9FGXsFNYdJMY8JSZcFWacNabNRSZ9RVadVYbcReccVjdcdnecpsfcZoedlm
        ettsfthhdcRze8pwf7h3g8xugNtugMxzhMx3iM57itxzhNB6id99jc9/kI2NjZycnLeVm7eGj7+e
        pKqqqr+jqL+tsbi4uMmEidKAjsiIlNGDlNeJltSMm9qJl8+Tl8+QnNOQneKKmeGFlOSQnseaotqV
        otiYp9mbqtaVpOaXpOaYpOefrcelq9Whpd2lstqust+tuNavt8S0uNOzueijr+egreCuuuqst+Gy
        veyyvOC7vuO1wOS7xOW+yO68xMXFxdXHytHR0d3d3ebGyufJyuvIzufAx/DCyuvM0+nH0PPN0+vT
        1e3T2u/Y3uLe3/DS1/Ha3vPV2+/f4PHe4unp6efh4vHh5fPm6vXq6/bu8Pvv8fT09Pr09fv2+P//
        //f4+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAAAAAAALAAAAABYAlEA
        AAj+AHMJHEiwoMGDCBMqXMiwocOHECNKnEixosWLGDNq3Mixo8ePIEOKHEmypMmTKFOqXMmypcuX
        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
        EHRWgQcmuOBSJVM14RKTcGyNFThSIItVQKGYFFIoxvhiUDTGuOKOO+Y4Y4oXqUCBKO4YtleVPzog
        CpKwOGCjDECgRaZABxgAX036lAlnlwj+CLhQ8dwM07yqJKSwEwL8SnbBSZ9uKz8z02VvXVvyS8rb
        QQWQq0KutYYJALHFjiquqtAagC8HjW76UYsCaM9gueemu27CTlU478tUdEwXEl7diCAGBmdgAcIH
        N/xwxRNXvPHGOWKA2JUnt2CBJrAYY4woHNhohS4F6yTcUkMfdLDQ6W3sFU7ARP0w1cEW8XTCSA9T
        MPnsxj133Q3GW2+9WYWsERZmBsGCCo5HPnnll2e+eeWfPH5y6TcSoQMFEsCeASU3MMHP3b8Hn0My
        wye/fPMV6913VYHf8AgWeF1SSyY/knx6+yeXn6MQMmABjvP/ByBJOLEz0QXQgAfM3Rn+1KcqKpCE
        FoYghCF0wRgjrMBF9+tV/e7HgelgsCMXWMEaEDhC8KmBAJ8iYQpVODAFLvBEDSRJH7iwhS0UojF/
        iEBoPLjDDOqKhxmIgAY2sUIiFtGIR0RiLlrows3A0CKUKIQonJCJPkiiMZuYgQQgYAEQ5I+HXwRj
        BiSQgS94L4lnRGMa1Ui3JbqgBQp7o2Xi6AInWgQSmVBFDygBCRs6xhFEmEFrSDBIQhKyBCUgwSER
        echENhKRg8zNIB/JGkMq8pGSTCQjDdlIEuRmkZO0JCZxQAdYrNGUp0RlKjukwBe00pWvhGUrYRDL
        Wc5Sli+go0xKUQZRUMIPZWCFKoVPOUxiFtOYjalFjXRRI2Y205nPdGYyl1kLwUBiC7u04jG1uU1u
        dtOb3wRnOMU5TnKW05znRGc61blOdrbTne+EZzzlOU961tOe98RnPukWEAAh/wtYTVAgRGF0YVhN
        UDw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+Cjx4
        OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3Jl
        IDUuNi1jMTQwIDc5LjE2MDQ1MSwgMjAxNy8wNS8wNi0wMTowODoyMSAgICAgICAgIj4KIDxyZGY6
        UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5z
        IyI+CiAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIvPgogPC9yZGY6UkRGPgo8L3g6eG1w
        bWV0YT4KPD94cGFja2V0IGVuZD0iciI/PgH//v38+/r5+Pf29fTz8vHw7+7t7Ovq6ejn5uXk4+Lh
        4N/e3dzb2tnY19bV1NPS0dDPzs3My8rJyMfGxcTDwsHAv769vLu6ubi3trW0s7KxsK+urayrqqmo
        p6alpKOioaCfnp2cm5qZmJeWlZSTkpGQj46NjIuKiYiHhoWEg4KBgH9+fXx7enl4d3Z1dHNycXBv
        bm1sa2ppaGdmZWRjYmFgX15dXFtaWVhXVlVUU1JRUE9OTUxLSklIR0ZFRENCQUA/Pj08Ozo5ODc2
        NTQzMjEwLy4tLCsqKSgnJiUkIyIhIB8eHRwbGhkYFxYVFBMSERAPDg0MCwoJCAcGBQQDAgEAADs=
        '''

        self.asset_label = tk.Label(self)
        self.asset_photoimage = tk.PhotoImage(data=encoded_logo)
        self.asset_label['image'] = self.asset_photoimage
        self.asset_label.grid(row=0)

        self.frame.grid(row=3, padx=10, pady=(10, 15), sticky='ew')
        self._separator.grid(row=5, sticky='ew')
        self.bottom_frame.grid(row=6, padx=10, pady=(10, 10), sticky='ew')


        # Give any extra space to column 0. See this page for details:
        # https://stackoverflow.com/questions/45847313/what-does-weight-do-in-tkinter
        self.frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)

        self._selection_scene()

        self.prev_scene = None
        self.curr_scene = "selection_scene"

        self._quit_btn.grid(row=0, column=3, sticky='e')
        self._back_btn.grid(row=0, column=2, sticky='e')
        self._help_btn.grid(row=0, column=0, sticky='w')
        self._settings_btn.grid(row=0, column=1, stick='w')

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
        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

        # Save the selected offboard configuration into the controller.
        self._controller.save_offboard_config(self.combobox.get())
        # Start the search sequence.
        self._controller.search_sequence(identifier)

        self.return_id = self.bind('<Return>', lambda event: self._input_btn_clicked("serial_number"))

    def _secure_erase_btn_clicked(self):
        self._controller.secure_erase()

    def _exit_btn_clicked(self):
        """
        This is bound to the WM_DELETE_WINDOW in __init__() and is called when the red x button is pressed.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroys the main view and master/root Tk window.
        self._controller.terminate()

    def _back_btn_clicked(self):
        if self.curr_scene == "offboard_scene":
            self._grid_forget_offboard_scene()
            self._selection_scene()

        elif self.curr_scene == "help_scene":
            self._grid_forget_help_scene()
            if self.prev_scene == "selection_scene":
                self._selection_scene()
            elif self.prev_scene == "offboard_scene":
                self.offboard_scene()
            elif self.prev_scene == "settings_scene":
                self._selection_scene()

        elif self.curr_scene == "github_scene":
            self._grid_forget_github_scene()
            self._help_scene()

        elif self.curr_scene == "about_scene":
            self._grid_forget_about_scene()
            self._help_scene()

        elif self.curr_scene == "how_to_scene":
            self._grid_forget_how_to_scene()
            self._help_scene()

        elif self.curr_scene == "settings_scene":
            self._grid_forget_settings_scene()
            if self.prev_scene == "selection_scene":
                self._selection_scene()
            elif self.prev_scene == "offboard_scene":
                self.offboard_scene()
            elif self.prev_scene == "help_scene":
                self._selection_scene()

    def _help_btn_clicked(self, curr_scene):
        if curr_scene != "help_scene":
            self.prev_scene = curr_scene
        self._help_scene()

    def _offboard_btn_clicked(self, curr_scene):
        self.prev_scene = curr_scene
        self.offboard_scene()

    def _settings_btn_clicked(self, curr_scene):
        if curr_scene != "settings_scene":
            self.prev_scene = curr_scene
        self._settings_scene()

    def _slack_config_btn_clicked(self):
        self._controller.open_config("slack")

    def _offboard_config_btn_clicked(self):
        self._controller.open_config("offboard")

    def _verify_config_btn_clicked(self):
        self._controller.open_config("verify")

    def _search_config_btn_clicked(self):
        self._controller.open_config("search")

    def _directory_config_btn_clicked(self):
        self._controller.open_config("private")

    def _how_to_btn_clicked(self):
        self._how_to_scene()

    def _about_btn_clicked(self):
        self._about_scene()

    def _github_btn_clicked(self):
        self._github_scene()

    def populate_combobox(self):
        """
        Populates the combobox with the available offboard configurations (xml files).

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Calls the populate function in the controller. That function does the actual populating.
        self._controller.populate_config_combobox()

    def _settings_scene(self):
        self.curr_scene = "settings_scene"
        self._grid_forget_scenes()

        self._offboard_config_btn.grid(row=0)
        self._slack_config_btn.grid(row=1)
        self._verify_config_btn.grid(row=2)
        self._search_config_btn.grid(row=3)
        self._directory_config_btn.grid(row=4)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

    def _help_scene(self):
        self.curr_scene = "help_scene"
        self._grid_forget_scenes()

        self._about_btn.grid(row=0)
        self._how_to_btn.grid(row=1)
        self._github_btn.grid(row=2)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

    def _how_to_scene(self):
        self.curr_scene = "how_to_scene"
        self._grid_forget_help_scene()

        self._how_to_text_box.grid(row=0)
        self._how_to_scroll_bar.grid(row=0, column=1, sticky='nsew')
        self._how_to_text_box.config(yscroll=self._how_to_scroll_bar.set)

        self._how_to_text_box.insert('insert', self._controller.cat_readme())
        self._how_to_text_box.config(state='disabled')

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

    def _about_scene(self):
        self.curr_scene = "about_scene"
        self._grid_forget_help_scene()

        text = "Blade Runner is a JAMF Pro based Python application that manages deprecated Mac computer systems. " \
               "It does so through offboarding, enrolling, and updating JAMF records, as well as secure erasing the " \
               "computer's internal disks, generating and printing documents with data retreived from JAMF Pro, " \
               "displaying inconsistencies in JAMF records against user entered data, and sending progress updates " \
               "through Slack. \nIt is configured through plists and XML files, allowing for multiple offboarding " \
               "configurations, a dynamically updating GUI, Slack integration, and specification of which search terms " \
               "can be used to locate/update a JAMF Pro record."
        self._about_lbl.config(text=text, wraplength=self.frame.winfo_width())
        self._about_lbl.grid(row=0, padx=10)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

    def _github_scene(self):
        self.curr_scene = "github_scene"
        self._grid_forget_help_scene()

        self._github_lbl.grid(row=0)
        text = """To view the source code, submit bugs, or ask questions, visit Blade Runner's Github page at:"""
        self._github_lbl.config(text=text, wraplength=self.frame.winfo_width()*.90, justify="left")

        self._github_entry.grid(row=1)
        self._github_entry.insert("insert", self._github_url)
        self._github_entry.config(state='readonly', relief='flat', highlightthickness=0)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: None)

    def _selection_scene(self):
        self.curr_scene = "selection_scene"
        self._offboard_btn.grid(row=0)
        self._secure_erase_btn.grid(row=1)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: self._offboard_btn_clicked(self.curr_scene))

    def offboard_scene(self):
        self.curr_scene = "offboard_scene"
        self._grid_forget_selection_scene()

        self.combobox_frame.grid(row=2)
        # Add and configure the selection label.
        self.selection_lbl.grid(row=0, column=0)
        self.selection_lbl.config(text="Select an offboard configuration:", font=self.text_font)

        self.choose_lbl.grid(row=2, pady=(10, 0))
        self.choose_lbl.config(text="Search for computer's JAMF record by:")

        self.combobox.grid(row=1, column=0)

        if 'serial_number' in self._controller.search_params.enabled:
            self._serial_btn.grid(row=3, column=0)

        if 'barcode_1' in self._controller.search_params.enabled:
            self._barcode_1_btn.grid(row=4, column=0)

        if 'barcode_2' in self._controller.search_params.enabled:
            self._barcode_2_btn.grid(row=5, column=0)

        if 'asset_tag' in self._controller.search_params.enabled:
            self._asset_btn.grid(row=6, column=0)

        self.unbind('<Return>', self.return_id)
        self.return_id = self.bind('<Return>', lambda event: self._input_btn_clicked("serial_number"))

    def _grid_forget_settings_scene(self):
        self._offboard_config_btn.grid_forget()
        self._slack_config_btn.grid_forget()
        self._verify_config_btn.grid_forget()
        self._search_config_btn.grid_forget()
        self._directory_config_btn.grid_forget()

    def _grid_forget_scenes(self):
        self._grid_forget_help_scene()
        self._grid_forget_selection_scene()
        self._grid_forget_offboard_scene()
        self._grid_forget_settings_scene()

    def _grid_forget_github_scene(self):
        self._github_lbl.grid_forget()
        self._github_entry.grid_forget()

    def _grid_forget_about_scene(self):
        self._about_lbl.grid_forget()

    def _grid_forget_how_to_scene(self):
        self._how_to_lbl.grid_forget()
        self._how_to_scroll_bar.grid_forget()
        self._how_to_text_box.grid_forget()

    def _grid_forget_help_scene(self):
        self._about_btn.grid_forget()
        self._how_to_btn.grid_forget()
        self._github_btn.grid_forget()

    def _grid_forget_offboard_scene(self):
        self.selection_lbl.grid_forget()
        self.choose_lbl.grid_forget()
        self.combobox.grid_forget()
        self._serial_btn.grid_forget()
        self._asset_btn.grid_forget()
        self._barcode_1_btn.grid_forget()
        self._barcode_2_btn.grid_forget()
        self.combobox_frame.grid_forget()

    def _grid_forget_selection_scene(self):
        self._offboard_btn.grid_forget()
        self._secure_erase_btn.grid_forget()


