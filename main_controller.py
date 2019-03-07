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

from main_view import MainView
import Tkinter as tk
import subprocess
import inspect
from management_tools import loggers
import os
from jss_server import JssServer
import plistlib
from computer import Computer
import socket
from management_tools.slack import IncomingWebhooksSender as IWS
from jss_doc import JssDoc
import user_xml_updater as user
from params import SearchParams, VerifyParams
from search_controller import SearchController
from verification_controller import VerificationController
from dual_verify_controller import DualVerifyController
from controller import Controller
import tkMessageBox

# TODO Interface with a Trello board and dynamically create lists for the DEP
# TODO BUG: If spaces are entered in the asset/barcode inputs the program quits. Need to format spaces.
# TODO Find a better way to enable/disable JSS Doc printing. I don't like it being an arg for MainController.


class MainController(Controller):
    """Blade-Runner's main controller."""

    def __init__(self, root, server, slack_data, verify_params, search_params, print_enabled=False):
        """Initialize the main controller.

        Args:
            root: The root Tk window.
            server (JssServer): The JSS server to connect to.
            slack_data (dict): Slack configuration data.
            verify_params (dict): Verification parameters configuration data.
            search_params (dict): Search parameters configuration data.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set report callback so that a Tk window will appear with the exception message when an exception occurs.
        self._root = root
        self._root.report_callback_exception = self._exception_messagebox
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # JSS server
        self._jss_server = server
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Stores information about the computer
        self._computer = Computer()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Used to exit out of a function if the user cancels.
        self._proceed = True
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set views
        self._main_view = None
        self._entry_view = None
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set controllers
        self._search_controller = None
        self._verify_controller = None
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set whether or not a JSSDoc will be printed to a printer.
        self._print_enabled = print_enabled
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set configuration data
        self._offboard_config = None
        self._slack_data = slack_data
        self.verify_params = VerifyParams(verify_params)
        self.search_params = SearchParams(search_params)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set path to private directory that contains the configuration files.
        self._private_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private")

    def _exception_messagebox(self, exc, value, traceback):
        """Displays a message box with the accompanying exception message whenver an exception occurs.

        Args:
            exc: Exception received.
            value: Value of exception.
            traceback: Traceback from exception.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Grab the last value in the value tuple. This is normally the message.
        message = "{}".format(value[-1])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Display a message box containing the exception's message.
        tkMessageBox.showerror('Exception', message)

    def run(self):
        """Start Blade-Runner.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create the main view.
        self._main_view = MainView(self._root, self)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set it to the middle of the screen.
        self._set_to_middle(self._main_view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Refocus on the window.
        self.refocus()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make this window the main loop.
        self._main_view.mainloop()

    def terminate(self):
        """Terminates Blade-Runner.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Destroy the main view and the root window.
        self._main_view.destroy()
        self._root.destroy()

    def restart(self):
        """Restart Blade-Runner without quiting the entire program.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a new Computer object.
        self._computer = Computer()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a new VerifyParams object.
        self.verify_params = VerifyParams(self.verify_params.originals)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a new SearchParams object.
        self.search_params = SearchParams(self.search_params.originals)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info("Blade-Runner reset.")

    def populate_config_combobox(self):
        """Populates the main view's combobox with available configuration files.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get a list of the files in the private directory.
        private_files = os.listdir(self._private_dir)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get all XML files .
        offboard_configs = []
        for file in private_files:
            if file.endswith(".xml"):
                offboard_configs.append(file)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Fill the main view's combobox with the XML files.
        self._main_view.combobox.config(values=offboard_configs)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the initial choice to the first XML file in the list.
        self._main_view.combobox.current(0)

    def save_offboard_config(self, offboard_config):
        """Save the offboard config as an XML string.

        Args:
            offboard_config (str): File name, not the file path.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Save the XML file as an XML string.
        self._offboard_config = user.xml_to_string(os.path.join(self._private_dir, offboard_config))

    def search_sequence(self, input_type):
        """Determines the search window sequence based on the input type and previous search params.

        Args:
            input_type (str): Data identifier.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Process the input type and handle the JSS search.
        self.search_handler(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every search parameter enabled
        for param in self.search_params:
            # If search parameter hasn't been searched yet.
            if not self.search_params.was_searched(param):
                # If user hasn't canceled operation and no match was found
                if self._proceed is True and self._computer.jss_id is None:
                    # Process the input type and handle the JSS search.
                    self.search_handler(param)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # All search params have been searched and Blade-Runner has finished processing the computer.
        # Restart Blade-Runner.
        self.restart()

    def search_handler(self, input_type):
        """Handles search events.

        Args:
            input_type (str): Data identifier.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open the search view for the input type.
        self.open_search_view(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If the user canceled the search view, proceed will be false, Blade-Runner will restart, and function returns.
        if self._proceed is False:
            self.restart()
            return
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Since the computer object has been filled with user input data for the input type, search the JSS.
        self.dynamic_search(self._computer, input_type)
        self.search_params.set_searched(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If the search resulted in a match, start the offboard process.
        if self._computer.jss_id is not None:
            self.search_params.set_match(input_type)
            self.process_logic()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Otherwise, if all input types have been searched, start the offboard process.
        elif self.search_params.all_searched():
            self.process_logic()

    def dynamic_search(self, computer, input_type):
        """Dynamically search the JSS with the Computer attribute that matches the input type.

        Args:
            computer (Computer): Stores information about the computer.
            input_type (str): Data identifier.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Use the computer object to set the search parameter.
        if input_type == "barcode_1":
            search_param = computer.barcode_1
        elif input_type == "barcode_2":
            search_param = computer.barcode_2
        elif input_type == "asset_tag":
            search_param = computer.asset_tag
        elif input_type == "serial_number":
            search_param = computer.serial_number
        else:
            raise SystemExit("The input type \"{}\" supplied from the button is not supported.".format(input_type))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Search the JSS.
        computer.jss_id = self._jss_server.match(search_param)

    def open_search_view(self, input_type):
        """Open the search view. Saves user input in computer object.

        Args:
            input_type (str): Data identifier.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If serial number, save serial number to computer object. This allows the serial to be displayed before
        # submitting it for a search.
        if input_type == "serial_number":
            self._computer.serial_number = self._computer.get_serial()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open the search controller/view. Inputs given to the view will be saved in the computer object.
        self._search_controller = SearchController(self._main_view, self._computer, input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Wait for search view to close.
        self._main_view.wait_window(window=self._search_controller.entry_view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If the user canceled the operation, proceed will be false.
        self._proceed = self._search_controller.proceed

    def open_verify_view(self, message):
        """Open the verification view. If there is a search match, a DualVerifyView will be opened, otherwise
        a VerifyView will be opened. Computer object will be updated.

        Args:
            message (str): Message to be displayed in view.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If a JSS match has been found, open a DualVerifyView.
        if self.search_params.exists_match():
            if self.search_params.search_count >= 1:
                self._verify_controller = DualVerifyController(self._main_view, self._computer, self.verify_params, self._jss_server)
        # Otherwise open a VerifyView.
        else:
            self._verify_controller = VerificationController(self._main_view, self._computer, self.verify_params, self.search_params)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Configure message to be displayed.
        self._verify_controller.entry_view.text_lbl.config(text=message)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Wait for entry view window to close.
        self._main_view.wait_window(window=self._verify_controller.entry_view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # After entry view window has been closed through the "submit" button, proceed will be True, and the barcode,
        # asset, and name fields of the computer object will be updated.
        self._proceed = self._verify_controller.proceed

    def process_logic(self):
        self._proceed = False

        # If JSS ID doesn't exist
        if self._computer.jss_id is None:
            message = "JSS doesn't record exist. Please verify\nthe following fields before submitting\nthem to the JSS.\n"
            self.open_verify_view(message)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self._proceed is False:
                self.restart()
                return

            # Make sure the serial field for the computer object was updated/set.
            if self._computer.serial_number is None:
                self._computer.serial_number = self._computer.get_serial()

            # If user clicked submit in the entry view window, the computer will be enrolled in the JSS to create
            # a JSS ID for it in JAMF.
            logger.debug("Enrolling because no JSS ID exists for this computer.")
            self._jss_server.enroll_computer()
            logger.debug("Enrolling finished.")

            # Since JSS ID has now been created, retrieve it using the search parameter inputted by the user.
            self._computer.jss_id = self._jss_server.match(self._computer.serial_number)
            logger.debug("JSS id after enrolling: {}".format(self._computer.jss_id))

            # Update the JAMF record with the barcode, asset, and name of the computer
            self._jss_server.push_identity_fields(self._computer)

        # If JSS ID exists
        elif self._computer.jss_id is not None:
            message = "JSS record exists. Please verify/correct\n " \
                      "the following fields."
            self.open_verify_view(message)

            if self._computer.serial_number is None:
                self._computer.serial_number = self._computer.get_serial()

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self._proceed is False:
                self.restart()
                return

            self.store_incorrect_records(self._computer)

            # Check if Managed
            managed = self._jss_server.get_managed_status(self._computer.jss_id)
            logger.debug("Management status is {}".format(managed))

            # If managed status is false, re-enroll computer to set managed status to true.
            if managed == 'false' or managed == 'False':
                logger.info("Enrolling to change managed status to true to enable modification of JSS record.")
                self._jss_server.enroll_computer()

            # Push enroll fields to JSS server
            self._jss_server.push_identity_fields(self._computer)

        # TODO Remove this for open source version. MacGroup only.
        # At this point, all computer fields that were the same are now none.
        self._offboard_config = user.append_name(self._computer.get_serial(), self._offboard_config)
        self._offboard_config = user.timestamp_note(self._offboard_config)
        self._offboard_config = user.set_previous_computer_name(self._computer.name, self._offboard_config)

        self._jss_server.push_xml_str(self._offboard_config, self._computer.jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the new managed status and make sure it's false
        post_managed_status = self._jss_server.get_managed_status(self._computer.jss_id)
        logger.debug("post_managed_status: {}".format(post_managed_status))

        if post_managed_status != 'false':
            raise SystemExit("ERROR: Managed status is not false after offboarding.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Notify slack channel that offboard tool has finished.
        if self._slack_data['slack_enabled'] == "True":
            # TODO add this to a config.
            self.send_slack_message("Offboarding complete. Serial {}".format(self._computer.serial_number))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Prepare document for printing
        doc = JssDoc(self._jss_server, self._computer)
        doc.create_html()
        doc.html_to_pdf()
        if self._print_enabled:
            doc.print_to_default()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Start Slackify daemon
        if self._slack_data['slackify_daemon_enabled'] == 'True':
            self.start_slackify_reminder_dameon()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        #  Terminate
        logger.info("Blade Runner successfully finished.")
        self.terminate()

    def store_incorrect_records(self, computer):
        # Check to see what fields changed after the user updated the fields through the entry view window.
        if computer.barcode_1 != computer.jss_barcode_1:
            computer.incorrect_barcode_1 = computer.jss_barcode_1
            logger.debug("barcode_1 {} is incorrect.".format(computer.incorrect_barcode_1))

        if computer.barcode_2 != computer.jss_barcode_2:
            computer.incorrect_barcode_2 = computer.jss_barcode_2
            logger.debug("barcode_2 {} is incorrect.".format(computer.incorrect_barcode_2))

        if computer.asset_tag != computer.jss_asset_tag:
            computer.incorrect_asset = computer.jss_asset_tag
            logger.debug("asset_tag {} is incorrect.".format(computer.incorrect_asset))

        if computer.jss_serial_number != computer.get_serial():
            computer.serial_number = computer.get_serial()
            computer.incorrect_serial = self._jss_server.get_serial(computer.jss_id)
            logger.debug("JSS serial {} is incorrect.".format(computer.incorrect_serial))

    def set_correct_entries_to_none(self, computer):
        # Check to see what fields changed after the user updated the fields through the entry view window.

        if computer.barcode_1 == computer.jss_barcode_1:
            logger.debug("barcode_1 {} is correct.".format(computer.barcode_1))
            computer.barcode_1 = None

        if computer.barcode_2 == computer.jss_barcode_2:
            logger.debug("barcode_2 {} is correct.".format(computer.barcode_2))
            computer.barcode_2 = None

        if computer.asset_tag == computer.jss_asset_tag:
            logger.debug("asset_tag {} is correct.".format(computer.asset_tag))
            computer.asset_tag = None

        if computer.serial_number == computer.jss_serial_number:
            logger.debug("Serial {} is correct.".format(computer.serial_number))
            computer.serial_number = None

        if computer.name == computer.prev_name:
            computer.name = None

    def send_slack_message(self, message):
        current_ip = socket.gethostbyname(socket.gethostname())
        slack_bot = IWS(self._slack_data['slack_url'], bot_name=current_ip, channel=self._slack_data['slack_channel'])
        slack_bot.send_message(message)

    def start_slackify_reminder_dameon(self):
        # Start Slackify reminder daemon
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ['/usr/bin/python', os.path.join(script_dir, 'slackify_reminder_daemon.py')]
            subprocess.Popen(cmd, stderr=subprocess.STDOUT)

    def refocus(self):
        # Python tkinter window gets selected automatically
        select_window = ['/usr/bin/osascript', '-e',
                         'tell application "Finder" to set frontmost of process "Python" to true']
        try:
            subprocess.check_output(select_window)
        except subprocess.CalledProcessError:
            logger.debug("Setting frontmost of process Python to true failed.")


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
logger.debug("{} logger started.".format(lbasename))


def main():
    # TODO uncomment sudo check for production
    # if os.geteuid() != 0:
    #     raise SystemExit("Must be run as root.")
    root = tk.Tk()
    root.withdraw()

    # Read from jss config plist and set up the JSS server
    blade_runner_dir = os.path.dirname(abs_file_path)
    jss_server_plist = os.path.join(blade_runner_dir, "private/jss_server_config.plist")
    jss_server_data = plistlib.readPlist(jss_server_plist)
    jss_server = JssServer(**jss_server_data)
    logger.debug(jss_server._jss_url)

    # Read from Slack config plist to set up Slack notifications
    slack_plist = os.path.join(blade_runner_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)

    verify_config = os.path.join(blade_runner_dir, "private/verify_config.plist")
    verify_data = plistlib.readPlist(verify_config)

    search_params_config = os.path.join(blade_runner_dir, "private/search_params_config.plist")
    search_params = plistlib.readPlist(search_params_config)

    # Run the application
    app = MainController(root, jss_server, slack_data, verify_data, search_params)
    app.run()


if __name__ == "__main__":
    main()


