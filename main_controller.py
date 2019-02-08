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
from dual_verify_controller import DualVerificationController
from controller import Controller

# TODO Interface with a Trello board and dynamically create lists for the DEP
# TODO BUG: If spaces are entered in the asset or barcode inputs the program quits. Formatting issue. Need to format spaces.


class MainController(Controller):
    def __init__(self, root, server, slack_data, verify_params, search_params):

        self.jss_server = server
        self.computer = Computer()
        self.proceed = True
        self.root = root

        self.main_view = None
        self.search_controller = None
        self.verify_controller = None
        self.entry_view = None
        self.print_enabled = False

        self.offboard_config = None
        self.slack_data = slack_data
        self.private_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private")

        self.verify_params = VerifyParams(verify_params)
        self.search_params = SearchParams(search_params)

        self.refocus()

    def run(self):
        self.main_view = MainView(self.root, self)
        self.refocus()
        self.main_view.mainloop()

    def terminate(self):
        # Destroy the main view and the root mainloop.
        self.main_view.destroy()
        self.root.destroy()

    def restart(self):
        self.computer = Computer()
        self.verify_params = VerifyParams(self.verify_params.originals)
        self.search_params = SearchParams(self.search_params.originals)
        logger.info("Blade-Runner reset.")

    def populate_config_combobox(self):
        private_files = os.listdir(self.private_dir)
        offboard_configs = []
        for file in private_files:
            if file.endswith(".xml"):
                offboard_configs.append(file)
        self.main_view.combobox.config(values=offboard_configs)
        self.main_view.combobox.current(0)

    def save_offboard_config(self, offboard_config):
        self.offboard_config = user.xml_to_string(os.path.join(self.private_dir, offboard_config))

    def determine_input_type(self, input_type):
        if input_type == "serial_number":
            self.computer.serial_number = self.computer.get_serial()

        self.search_controller = SearchController(self.main_view, self.computer, input_type)

        self.main_view.wait_window(window=self.search_controller.entry_view)

        self.proceed = self.search_controller.proceed

        if self.proceed is False:
            self.restart()
            return

        if input_type == "barcode_1":
            search_param = self.computer.barcode_1
        elif input_type == "barcode_2":
            search_param = self.computer.barcode_2
        elif input_type == "asset_tag":
            search_param = self.computer.asset_tag
        elif input_type == "serial_number":
            search_param = self.computer.serial_number

        try:
            self.computer.jss_id = self.jss_server.match(search_param)
            self.search_params.set_searched(input_type)
        except NameError as e:
            raise SystemExit("{}. The input type supplied from the button is not supported.".format(e))

        if self.computer.jss_id is not None:
            self.search_params.set_match(input_type)
            self.process_logic()
        elif self.search_params.all_searched():
            self.process_logic()

    # def next_input_old(self):
    #     for param in self.search_params:
    #         if not self.search_params.was_searched(param):
    #             if self.computer.jss_id is None:
    #                 if self.proceed is True:
    #                     self.determine_input_type(param)
    #                 else:
    #                     return
    #     self.restart()

    def act(self, input_type):
        self.determine_input_type(input_type)

        for param in self.search_params:
            if not self.search_params.was_searched(param):
                if self.proceed is True and self.computer.jss_id is None:
                    self.determine_input_type(param)

        self.restart()

    def open_verification_view(self, message):
        if self.search_params.exists_match():
            if self.search_params.search_count >= 1:

                self.computer.prev_barcode_1 = self.jss_server.get_barcode_1(self.computer.jss_id)
                self.computer.prev_barcode_2 = self.jss_server.get_barcode_2(self.computer.jss_id)
                self.computer.prev_asset_tag = self.jss_server.get_asset_tag(self.computer.jss_id)
                self.computer.prev_serial_number = self.jss_server.get_serial(self.computer.jss_id)
                self.computer.prev_name = self.jss_server.get_computer_name(self.computer.jss_id)

                logger.debug("Previous barcode_1: {}".format(self.computer.prev_barcode_1))
                logger.debug("Previous barcode_2: {}".format(self.computer.prev_barcode_2))
                logger.debug("Previous asset_tag: {}".format(self.computer.prev_asset_tag))
                logger.debug("Previous serial_number: {}".format(self.computer.prev_serial_number))
                logger.debug("Previous name: {}".format(self.computer.prev_name))

                self.verify_controller = DualVerificationController(self.main_view, self.computer, self.verify_params,
                                                                self.search_params)
        else:
            self.verify_controller = VerificationController(self.main_view, self.computer, self.verify_params, self.search_params)

        self.verify_controller.entry_view.text_lbl.config(text=message)

        # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
        # the barcode, asset, and name fields of the computer object will be updated.
        self.main_view.wait_window(window=self.verify_controller.entry_view)
        if self.verify_controller.proceed is True:
            self.proceed = True

    def process_logic(self):
        self.proceed = False

        # If JSS ID doesn't exist
        if self.computer.jss_id is None:
            message = "JSS doesn't record exist. Please verify\nthe following fields before submitting\nthem to the JSS.\n"
            self.open_verification_view(message)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.proceed is False:
                self.restart()
                return

            # Make sure the serial field for the computer object was updated/set.
            if self.computer.serial_number is None:
                self.computer.serial_number = self.computer.get_serial()

            # If user clicked submit in the entry view window, the computer will be enrolled in the JSS to create
            # a JSS ID for it in JAMF.
            logger.debug("Enrolling because no JSS ID exists for this computer.")
            self.jss_server.enroll_computer()
            logger.debug("Enrolling finished.")

            # Since JSS ID has now been created, retrieve it using the search parameter inputted by the user.
            self.computer.jss_id = self.jss_server.match(self.computer.serial_number)
            logger.debug("JSS id after enrolling: {}".format(self.computer.jss_id))

            # Update the JAMF record with the barcode, asset, and name of the computer
            self.jss_server.push_enroll_fields(self.computer)

        # If JSS ID exists
        elif self.computer.jss_id is not None:
            message = "JSS record exists. Please verify/correct\n " \
                      "the following fields."
            self.open_verification_view(message)

            if self.computer.serial_number is None:
                self.computer.serial_number = self.computer.get_serial()

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.proceed is False:
                self.restart()
                return

            self.set_correct_entries_to_none(self.computer)
            self.store_incorrect_records(self.computer)

            # Check if Managed
            managed = self.jss_server.get_managed_status(self.computer.jss_id)
            logger.debug("Management status is {}".format(managed))

            # If managed status is false, re-enroll computer to set managed status to true.
            if managed == 'false' or managed == 'False':
                logger.info("Enrolling to change managed status to true to enable modification of JSS record.")
                self.jss_server.enroll_computer()

            # Push enroll fields to JSS server
            self.jss_server.push_enroll_fields(self.computer)

        # TODO Remove this for open source version. MacGroup only.
        # At this point, all computer fields that were the same are now none.
        self.offboard_config = user.append_xml_str_name(self.computer.get_serial(), self.offboard_config)
        self.offboard_config = user.timestamp_note(self.offboard_config)

        self.jss_server.push_xml_str_fields(self.offboard_config, self.computer.jss_id)
        # self.jss_server.push_xml_fields(os.path.join(self.private_dir, self.offboard_config), self.computer.jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the new managed status and make sure it's false
        post_managed_status = self.jss_server.get_managed_status(self.computer.jss_id)
        logger.debug("post_managed_status: {}".format(post_managed_status))

        if post_managed_status != 'false':
            raise SystemExit("ERROR: Managed status is not false after offboarding.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Notify slack channel that offboard tool has finished.
        if self.slack_data['slack_enabled'] == "True":
            self.send_slack_message("Offboarding complete.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Prepare document for printing
        doc = JssDoc(self.jss_server, self.computer.jss_id, self.computer)
        doc.create_html()
        doc.html2pdf()
        if self.print_enabled:
            doc.applescript_print()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Start Slackify daemon
        if self.slack_data['slackify_daemon_enabled'] == 'True':
            self.start_slackify_reminder_dameon()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        #  Terminate
        logger.info("Blade Runner successfully finished.")
        self.terminate()

    def store_incorrect_records(self, computer):
        # Check to see what fields changed after the user updated the fields through the entry view window.
        if computer.barcode_1 != computer.prev_barcode_1:
            computer.incorrect_barcode_1 = computer.prev_barcode_1
            logger.debug("barcode_1 {} is incorrect.".format(computer.incorrect_barcode_1))

        if computer.barcode_2 != computer.prev_barcode_2:
            computer.incorrect_barcode_2 = computer.prev_barcode_2
            logger.debug("barcode_2 {} is incorrect.".format(computer.incorrect_barcode_2))

        if computer.asset_tag != computer.prev_asset_tag:
            computer.incorrect_asset = computer.prev_asset_tag
            logger.debug("asset_tag {} is incorrect.".format(computer.incorrect_asset))

        if computer.prev_serial_number != computer.get_serial():
            computer.serial_number = computer.get_serial()
            computer.incorrect_serial = self.jss_server.get_serial(computer.jss_id)
            logger.debug("JSS serial {} is incorrect.".format(computer.incorrect_serial))

    def set_correct_entries_to_none(self, computer):
        # Check to see what fields changed after the user updated the fields through the entry view window.

        if computer.barcode_1 == computer.prev_barcode_1:
            logger.debug("barcode_1 {} is correct.".format(computer.barcode_1))
            computer.barcode_1 = None

        if computer.barcode_2 == computer.prev_barcode_2:
            logger.debug("barcode_2 {} is correct.".format(computer.barcode_2))
            computer.barcode_2 = None

        if computer.asset_tag == computer.prev_asset_tag:
            logger.debug("asset_tag {} is correct.".format(computer.asset_tag))
            computer.asset_tag = None

        if computer.serial_number == computer.prev_serial_number:
            logger.debug("Serial {} is correct.".format(computer.serial_number))
            computer.serial_number = None

        if computer.name == computer.prev_name:
            computer.name = None

    # def keep_unique_entries(self):
    #     # Check to see what fields changed after the user updated the fields through the entry view window.
    #     if self.computer.barcode_1 == self.computer.prev_barcode_1:
    #         logger.debug("barcode_1 {} is correct.".format(self.computer.barcode_1))
    #         self.computer.barcode_1 = None
    #     else:
    #         self.computer.incorrect_barcode_1 = self.computer.prev_barcode_1
    #         logger.debug("barcode_1 {} is incorrect.".format(self.computer.incorrect_barcode_1))
    #
    #     if self.computer.barcode_2 == self.computer.prev_barcode_2:
    #         logger.debug("barcode_2 {} is correct.".format(self.computer.barcode_2))
    #         self.computer.barcode_2 = None
    #     else:
    #         self.computer.incorrect_barcode_2 = self.computer.prev_barcode_2
    #         logger.debug("barcode_2 {} is incorrect.".format(self.computer.incorrect_barcode_2))
    #
    #     if self.computer.asset_tag == self.computer.prev_asset_tag:
    #         logger.debug("asset_tag {} is correct.".format(self.computer.asset_tag))
    #         self.computer.asset_tag = None
    #     else:
    #         self.computer.incorrect_asset = self.computer.prev_asset_tag
    #         logger.debug("asset_tag {} is incorrect.".format(self.computer.incorrect_asset))
    #
    #     if self.jss_server.get_serial(self.computer.jss_id) == self.computer.get_serial():
    #         logger.debug("Serial {} is correct.".format(self.computer.serial_number))
    #         self.computer.serial_number = None
    #     else:
    #         self.computer.serial_number = self.computer.get_serial()
    #         self.computer.incorrect_serial = self.jss_server.get_serial(self.computer.jss_id)
    #         logger.debug("JSS serial {} is incorrect.".format(self.computer.incorrect_serial))
    #
    #     if self.computer.name == self.computer.prev_name:
    #         self.computer.name = None

    def send_slack_message(self, message):
        current_ip = socket.gethostbyname(socket.gethostname())
        slack_bot = IWS(self.slack_data['slack_url'], bot_name=current_ip, channel=self.slack_data['slack_channel'])
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


def main():
    # if os.geteuid() != 0:
    #     raise SystemExit("Must be run as root.")
    root = tk.Tk()
    root.withdraw()

    # Read from jss config plist and set up the JSS server
    blade_runner_dir = os.path.dirname(abs_file_path)
    jss_server_plist = os.path.join(blade_runner_dir, "private/jss_server_config.plist")
    jss_server_data = plistlib.readPlist(jss_server_plist)
    jss_server = JssServer(**jss_server_data)
    logger.debug(jss_server.jss_url)

    # Read from Slack config plist to set up Slack notifications
    slack_plist = os.path.join(blade_runner_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)
    current_ip = socket.gethostbyname(socket.gethostname())
    bot = IWS(slack_data['slack_url'], bot_name=current_ip, channel=slack_data['slack_channel'])

    # Read from the offboard config plist to set up which fields will be offboarded
    offboard_xml = "private/offboard_config.xml"

    verify_config = os.path.join(blade_runner_dir, "private/verify_config.plist")
    verify_data = plistlib.readPlist(verify_config)

    search_params_config = os.path.join(blade_runner_dir, "private/search_params_config.plist")
    search_params = plistlib.readPlist(search_params_config)

    # Run the application
    app = MainController(root, jss_server, slack_data, verify_data, search_params)
    app.run()


if __name__ == "__main__":
    main()


