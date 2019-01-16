from model import Model
from entry_controller import EntryController
from main_view import MainView
import Tkinter as tk
import subprocess
import inspect
from management_tools import loggers
import os
from jss_server import JssServer
import plistlib
from computer import Computer
from decision_tree import DecisionTree
from pprint import pformat
import socket
from management_tools.slack import IncomingWebhooksSender as IWS
from jss_doc import JssDoc
from tuggyboat import TuggyBoat
import user_xml_updater as user

# TODO Interface with a Trello board and dynamically create lists for the DEP
# TODO Dynamically change entry_view according to a plist. Plist will contain barcode_1, barcode_2, asset_tag, name.
# TODO If spaces are entered in the asset or barcode inputs the program quits. Formatting issue. Need to format spaces.

class MainController(object):
    def __init__(self, root, server, slack_data, verify_data):

        self.model = Model(server)
        self.jss_server = server
        self.tuggyboat = TuggyBoat(server)
        self.computer = Computer()
        self.proceed = False
        self.inventory_status = None
        self.root = root

        self.verify_data = self.config_values_to_bools(dict(verify_data))
        self.needs_search = self.config_values_to_bools(dict(verify_data))

        self.main_view = None
        self.entry_controller = None
        self.entry_view = None
        self.refocus()

        self.barcode_1_searched = False
        self.barcode_2_searched = False
        self.asset_searched = False
        self.serial_searched = False
        self.print_enabled = False
        self.slack_enabled = True

        self.offboard_config = None
        self.slack_data = slack_data
        self.private_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private")

    def run(self):
        self.main_view = MainView(self.root, self)
        self.refocus()
        self.main_view.mainloop()

    def config_values_to_bools(self, verify_data):
        for field in verify_data:
            if verify_data[field].lower() == "false":
                verify_data[field] = False
            elif verify_data[field].lower() == "true":
                verify_data[field] = True
        return verify_data

    def populate_config_combobox(self):
        private_files = os.listdir(self.private_dir)
        offboard_configs = []
        for file in private_files:
            if file.endswith(".xml"):
                offboard_configs.append(file)
        self.main_view.combobox.config(values=offboard_configs)
        self.main_view.combobox.current(0)

    def save_offboard_config(self, offboard_config):
        self.offboard_config = offboard_config

    def serial_input(self):
        self.computer.serial_number = self.computer.get_serial()
        self.jss_server.search_param = self.computer.serial_number
        self.proceed = True
        self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
        self.serial_searched = True
        self.next_input()

    def determine_input_type(self, input_type):
        self.needs_search[input_type] = False
        self.entry_controller = EntryController(self.main_view, self.computer, self.verify_data, input_type)
        # Wait
        self.main_view.wait_window(window=self.entry_controller.entry_view)

        self.proceed = self.entry_controller.proceed

        if self.proceed is False:
            return

        if input_type == "barcode_1":
            search_param = self.computer.barcode_1
            self.computer.jss_id = self.jss_server.match(search_param)
        elif input_type == "barcode_2":
            search_param = self.computer.barcode_2
            self.computer.jss_id = self.jss_server.match(search_param)
        elif input_type == "asset_tag":
            search_param = self.computer.asset_tag
            self.computer.jss_id = self.jss_server.match(search_param)

        self.next_input()

    def next_input(self):
        for verify_field in self.needs_search:
            if self.needs_search[verify_field] is True:
                self.needs_search[verify_field] = False
                if self.computer.jss_id is None:
                    self.determine_input_type(verify_field)
                    return
        if not any(list(self.needs_search.values())):
            if self.computer.jss_id is None:
                self.serial_input()
                return
            self.process_logic()

    def open_entry_view(self, message, wait=True):
        self.entry_controller = EntryController(self.main_view, self.computer, self.verify_data, "config")
        self.entry_controller.populate_entry_fields()
        self.entry_controller.entry_view.text_lbl.config(text=message)
        # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
        # the barcode, asset, and name fields of the computer object will be updated.
        if wait:
            self.main_view.wait_window(window=self.entry_controller.entry_view)
            if self.entry_controller.proceed is True:
                self.proceed = True

    def process_logic(self):
        self.proceed = False

        # If JSS ID doesn't exist
        if self.computer.jss_id is None:
            message = "No JSS record exists. Create the new record by filling in or verifying the following fields:"
            self.open_entry_view(message)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.proceed is False:
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

            # TODO Remove this for open source version. MacGroup only.
            user.append_xml_name(self.computer.serial_number, os.path.join(self.private_dir, self.offboard_config))

            # Update the JAMF record with the barcode, asset, and name of the computer
            self.jss_server.push_enroll_fields(self.computer)
        # If JSS ID exists
        elif self.computer.jss_id is not None:
            self.computer.prev_barcode_1 = self.jss_server.get_barcode_1(self.computer.jss_id)
            self.computer.prev_barcode_2 = self.jss_server.get_barcode_2(self.computer.jss_id)
            self.computer.prev_asset_tag = self.jss_server.get_asset_tag(self.computer.jss_id)
            self.computer.prev_name = self.jss_server.get_computer_name(self.computer.jss_id)

            logger.debug("Previous barcode_1: {}".format(self.computer.prev_barcode_1))
            logger.debug("Previous barcode_2: {}".format(self.computer.prev_barcode_2))
            logger.debug("Previous asset_tag: {}".format(self.computer.prev_asset_tag))
            logger.debug("Previous name: {}".format(self.computer.prev_name))

            for field in self.needs_search:
                if self.needs_search[field] is True:
                    if field == 'barcode_1':
                        self.computer.barcode_1 = self.computer.prev_barcode_1
                    if field == 'barcode_2':
                        self.computer.barcode_2 = self.computer.prev_barcode_2
                    if field == 'asset_tag':
                        self.computer.asset_tag = self.computer.prev_asset_tag

            # # If neither the barcode_1, barcode_2, or asset have been entered, set the fields to the returned JSS fields
            # if not self.barcode_1_searched and not self.barcode_2_searched and not self.asset_searched:
            #     self.computer.barcode_1 = self.computer.prev_barcode_1
            #     self.computer.barcode_2 = self.computer.prev_barcode_2
            #     self.computer.asset_tag = self.computer.prev_asset_tag
            #     self.computer.name = self.computer.prev_name

            if self.computer.serial_number is None:
                self.computer.serial_number = self.computer.get_serial()

            # Open the entry window
            message = "JSS record exists. Please verify/correct the following fields."
            self.open_entry_view(message)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.proceed is False:
                return

            self.review_changes()

            # Check if Managed
            managed = self.jss_server.get_managed_status(self.computer.jss_id)
            logger.debug("Management status is {}".format(managed))

            # If managed status is false, re-enroll computer to set managed status to true.
            if managed == 'false' or managed == 'False':
                logger.info("Enrolling to change managed status to true to enable modification of JSS record.")
                self.jss_server.enroll_computer()

            # Push enroll fields to JSS server
            self.jss_server.push_enroll_fields(self.computer)

        self.jss_server.push_xml_fields(os.path.join(self.private_dir, self.offboard_config), self.computer.jss_id)
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

    def review_changes(self):
        # Check to see what fields changed after the user updated the fields through the entry view window.
        if self.computer.barcode_1 == self.computer.prev_barcode_1:
            logger.debug("barcode_1 {} is correct.".format(self.computer.barcode_1))
            self.computer.barcode_1 = None
        else:
            self.computer.incorrect_barcode_1 = self.computer.prev_barcode_1
            logger.debug("barcode_1 {} is incorrect.".format(self.computer.incorrect_barcode_1))

        if self.computer.barcode_2 == self.computer.prev_barcode_2:
            logger.debug("barcode_2 {} is correct.".format(self.computer.barcode_2))
            self.computer.barcode_2 = None
        else:
            self.computer.incorrect_barcode_2 = self.computer.prev_barcode_2
            logger.debug("barcode_2 {} is incorrect.".format(self.computer.incorrect_barcode_2))

        if self.computer.asset_tag == self.computer.prev_asset_tag:
            logger.debug("asset_tag {} is correct.".format(self.computer.asset_tag))
            self.computer.asset_tag = None
        else:
            self.computer.incorrect_asset = self.computer.prev_asset_tag
            logger.debug("asset_tag {} is incorrect.".format(self.computer.incorrect_asset))

        if self.jss_server.get_serial(self.computer.jss_id) == self.computer.get_serial():
            logger.debug("Serial {} is correct.".format(self.computer.serial_number))
            self.computer.serial_number = None
        else:
            self.computer.serial_number = self.computer.get_serial()
            self.computer.incorrect_serial = self.jss_server.get_serial(self.computer.jss_id)
            logger.debug("JSS serial {} is incorrect.".format(self.computer.incorrect_serial))

        if self.computer.name == self.computer.prev_name:
            self.computer.name = None

    def send_slack_message(self, message):
        current_ip = socket.gethostbyname(socket.gethostname())
        slack_bot = IWS(self.slack_data['slack_url'], bot_name=current_ip, channel=self.slack_data['slack_channel'])
        slack_bot.send_message(message)

    def start_slackify_reminder_dameon(self):
        # Start Slackify reminder daemon
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cmd = ['/usr/bin/python', os.path.join(script_dir, 'slackify_reminder_daemon.py')]
            subprocess.Popen(cmd, stderr=subprocess.STDOUT)

    def terminate(self):
        # Destroy the main view and the root mainloop.
        self.main_view.destroy()
        self.root.destroy()

    def refocus(self):
        # Python tkinter window gets selected automatically
        select_window = ['/usr/bin/osascript', '-e',
                         'tell application "Finder" to set frontmost of process "Python" to true']
        try:
            subprocess.check_output(select_window)
        except subprocess.CalledProcessError:
            logger.debug("Setting frontmost of process Python to true failed.")

    def set_to_middle(self, window):
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Updates window info to current window state
        window.update_idletasks()
        # Sets window position
        window.geometry('+%d+%d' % (screen_width / 2 - window.winfo_width() / 2, screen_height / 4))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    # def barcode_2_input(self):
    #     self.needs_search['barcode_2'] = False
    #     self.entry_controller = EntryController(self.main_view, self.computer, self.proceed, self.verify_data)
    #     self.entry_controller.barcode_2_only()
    #     # Wait
    #     self.main_view.wait_window(window=self.entry_controller.entry_view)
    #     self.jss_server.search_param = self.computer.barcode_2
    #     self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
    #     self.barcode_2_searched = True
    #     self.proceed = True
    #     self.next_input()
    #
    # def asset_input(self):
    #     self.needs_search['asset_tag'] = False
    #     self.entry_controller = EntryController(self.main_view, self.computer, self.proceed, self.verify_data)
    #     self.entry_controller.asset_only()
    #     # Wait
    #     self.main_view.wait_window(window=self.entry_controller.entry_view)
    #     self.computer.jss_id = self.jss_server.match(self.computer.asset_tag)
    #     self.asset_searched = True
    #     self.proceed = True
    #     self.next_input()

    #
    # def barcode_1_input(self):
    #     self.needs_search['barcode_1'] = False
    #     self.entry_controller = EntryController(self.main_view, self.computer, self.proceed, self.verify_data)
    #     self.entry_controller.barcode_1_only()
    #     # Wait
    #     self.main_view.wait_window(window=self.entry_controller.entry_view)
    #     self.jss_server.search_param = self.computer.barcode_1
    #     self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
    #     self.barcode_1_searched = True
    #     self.proceed = True
    #     self.next_input()


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)


if __name__ == "__main__":
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

    # Run the application
    app = MainController(root, jss_server, slack_data, verify_data)
    app.run()


