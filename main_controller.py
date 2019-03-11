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
from stall_window import StallWindow

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
        self._computer.serial_number = self._computer.get_serial()
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
        self._main(input_type)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For every search parameter enabled
        for param in self.search_params:
            # If search parameter hasn't been searched yet.
            if not self.search_params.was_searched(param):
                # If user hasn't canceled operation and no match was found
                if self._proceed is True and self._computer.jss_id is None:
                    # Process the input type and handle the JSS search.
                    self._main(param)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # All search params have been searched and Blade-Runner has finished processing the computer.
        # Restart Blade-Runner.
        self.restart()

    def _main(self, input_type):
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
        # If the search resulted in a match...
        if self._computer.jss_id:
            # Set match
            self.search_params.set_match(input_type)
            # Open view  so user can verify inputted data against JSS data.
            self.open_dual_verify_view()
            # If user didn't cancel operation...
            if self._proceed:
                # Get managed status of computer
                managed = self._jss_server.get_managed_status(self._computer.jss_id)
                logger.debug("Management status: {}".format(managed))
                # If managed status is false, re-enroll computer to set managed status to true. This enables the
                # JSS record to be modified
                if managed == 'false':
                    msg = "Enrolling to change managed status to true to enable modification of JSS record."
                    logger.debug(msg)
                    # Open a stall window, enroll the computer, and close the stall window.
                    StallWindow(self._main_view, self._jss_server.enroll_computer, msg)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Otherwise, if all input types have been searched...
        elif self.search_params.all_searched():
            # Open view  so user can verify inputted data.
            self.open_verify_view()
            # If user didn't cancel operation...
            if self._proceed:
                msg = "Enrolling because no JSS ID exists for this computer."
                logger.debug(msg)
                # Open a stall window, enroll the computer, and close the stall window.
                StallWindow(self._main_view, self._jss_server.enroll_computer, msg)

                # Since JSS ID has now been created, retrieve it.
                self._computer.jss_id = self._jss_server.match(self._computer.serial_number)
                logger.debug("JSS id after enrolling: {}".format(self._computer.jss_id))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Otherwise, return.
        elif self._computer.jss_id is None:
            return
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Push computer's identity fields to the JSS.
        self._jss_server.push_identity_fields(self._computer)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Offboard computer
        self._offboard()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Send slack message and start slackify daemon according to slack data config.
        self._slack_handler(self._slack_data)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create and print JssDoc according to settings.
        self._jss_doc_handler(self._computer, self._jss_server, print_doc=self._print_enabled)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info("Blade Runner successfully finished.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Display success message box.
        tkMessageBox.showinfo("Finished", "Blade-Runner successfully finished.")

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

    def open_verify_view(self):
        """Opens a VerifyView window.

        Returns:
            void
        """
        message = "JSS doesn't record exist. Please verify\nthe following fields before submitting\nthem to the JSS.\n"
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
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

    def open_dual_verify_view(self):
        """Opens a DualVerifyView window.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open DualVerifyWindow/Controller
        message = "JSS record exists. Please verify/correct\n the following fields."
        self._verify_controller = DualVerifyController(self._main_view, self._computer, self.verify_params,
                                                       self._jss_server)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Configure message to be displayed.
        self._verify_controller.entry_view.text_lbl.config(text=message)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Wait for entry view window to close.
        self._main_view.wait_window(window=self._verify_controller.entry_view)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Store exit status of the view.
        self._proceed = self._verify_controller.proceed

    def _user_defined_updates(self):
        """User defines implementation. Meant to update the computer's JSS record with extra information before
        offboarding.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # TODO Remove this for open source version. MacGroup only.
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Append the computer name with the serial number.
        self._offboard_config = user.append_name(self._computer.get_serial(), self._offboard_config)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Add a timestamp to the additional notes attribute.
        self._offboard_config = user.timestamp_note(self._offboard_config)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the previous computer name extension attribute.
        self._offboard_config = user.set_previous_computer_name(self._computer.name, self._offboard_config)

    def _offboard(self):
        """Offboard computer object with the offboard config.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Update the JSS record according to the implementation of the user.
        self._user_defined_updates()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Push the offboard config to the JSS to offboard the computer.
        self._jss_server.push_xml_str(self._offboard_config, self._computer.jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the new managed status and make sure it's false
        post_managed_status = self._jss_server.get_managed_status(self._computer.jss_id)
        logger.debug("post_managed_status: {}".format(post_managed_status))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Make sure managed status is false. If not, exit.
        if post_managed_status != 'false':
            raise SystemExit("ERROR: Managed status is not false after offboarding.")

    def _slack_handler(self, slack_data):
        """Handles all Slack related items: sends Slack message and starts Slackify daemon.

        Args:
            slack_data (dict): Slack configuration.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Notify slack channel that offboard tool has finished.
        if slack_data['slack_enabled'] == "True":
            # TODO add this to a config (slack message).
            self.send_slack_message("Offboarding complete. Serial {}".format(self._computer.serial_number))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Start Slackify daemon
        if slack_data['slackify_daemon_enabled'] == 'True':
            self.start_slackify_reminder_dameon()

    def _jss_doc_handler(self, computer, jss_server, print_doc=False):
        """Creates a document from the predefined setup in JssDoc and prints the document
        to the default printer if print_doc is True.

        Args:
            computer (Computer): Stores information about the computer. Only used for JSS ID and "incorrect fields".
            jss_server (JssServer): JSS server to query.
            print_doc (bool): Prints document to default printer if True.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Prepare document for printing
        doc = JssDoc(jss_server, computer)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create html document from settings in JssDoc.
        doc.create_html()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Convert HTML document into a PDF document.
        doc.html_to_pdf()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If document printing is enabled, print to the default printer.
        # TODO: Make print_doc part of some config.
        if print_doc:
            doc.print_to_default()

    def send_slack_message(self, message):
        """Sends a Slack message to a specified channel and Slack url.

        Args:
            message (str): Message to be sent to the Slack channel.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the current IP
        current_ip = socket.gethostbyname(socket.gethostname())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set up the Slack bot
        slack_bot = IWS(self._slack_data['slack_url'], bot_name=current_ip, channel=self._slack_data['slack_channel'])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Send the Slack message
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


