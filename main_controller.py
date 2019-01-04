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

# TODO Interface with a Trello board and dynamically create lists for the DEP

class MainController(object):
    def __init__(self, root, server, slack_data):

        self.model = Model(server)
        self.jss_server = server
        self.tuggyboat = TuggyBoat(server)
        self.computer = Computer()
        self.dt = DecisionTree()
        self.inventory_status = None
        self.root = root

        self.main_view = None
        self.entry_controller = None
        self.entry_view = None
        self.refocus()

        self.barcode_searched = False
        self.asset_searched = False
        self.serial_searched = False
        self.print_enabled = False
        self.slack_enabled = True

        self.offboard_config = None
        self.slack_data = slack_data
        self.private_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private")

    def run(self):
        self.main_view = MainView(self.root, self)
        self.populate_config_combobox()
        self.refocus()
        self.main_view.mainloop()

    def populate_config_combobox(self):
        private_files = os.listdir(self.private_dir)
        offboard_configs = []
        for file in private_files:
            if file.endswith(".xml"):
                offboard_configs.append(file)
        self.main_view.combobox.config(values=offboard_configs)
        self.main_view.combobox.current(0)

    def options_scene(self, config):
        self.offboard_config = config
        self.forget_buttons()
        self.main_view.selection_lbl.grid(row=1)

        self.main_view.selection_lbl.config(text="Current configuration file: " + config)

        # if sender is self.main_view.salvage_btn:
        #     self.main_view.selection_lbl.config(text="Inventory Status: SALVAGE")
        #     self.inventory_status = "Salvage"
        # elif sender is self.main_view.storage_btn:
        #     self.main_view.selection_lbl.config(text="Inventory Status: STORAGE")
        #     self.inventory_status = "Storage"

        self.main_view.choose_lbl.config(text="Choose one of the following options:")

        self.main_view.serial_btn.grid(row=2, column=0, sticky='EW')

        self.main_view.barcode_btn.grid(row=3, column=0, sticky='EW')

        self.main_view.asset_btn.grid(row=4, column=0, sticky='EW')

    def forget_buttons(self):
        self.main_view.next_btn.grid_forget()

        # self.main_view.salvage_btn.grid_forget()
        # self.main_view.storage_btn.grid_forget()

    def serial_input(self):
        self.computer.serial_number = self.computer.get_serial()
        logger.debug("Serial number: {0!r}".format(self.computer.serial_number))
        self.jss_server.search_param = self.computer.serial_number
        self.dt.proceed = True
        self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
        self.serial_searched = True
        self.next_input()
        
    def barcode_input(self):
        self.entry_controller = EntryController(self.main_view, self.computer, self.dt)
        self.entry_controller.barcode_only()
        # Wait
        self.main_view.wait_window(window=self.entry_controller.entry_view)
        print(self.computer.barcode_1)
        self.jss_server.search_param = self.computer.barcode_1
        self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
        self.barcode_searched = True
        self.dt.proceed = True
        self.next_input()

    def asset_input(self):
        self.entry_controller = EntryController(self.main_view, self.computer, self.dt)
        self.entry_controller.asset_only()
        # Wait
        self.main_view.wait_window(window=self.entry_controller.entry_view)
        self.jss_server.search_param = self.computer.asset_tag
        self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)
        self.asset_searched = True
        self.dt.proceed = True
        self.next_input()

    def next_input(self):
        if self.barcode_searched and self.computer.jss_id is None:
            if not self.asset_searched:
                self.asset_input()
                return
        if self.asset_searched and self.computer.jss_id is None:
            if not self.barcode_searched:
                self.barcode_input()
                return
        if self.barcode_searched and self.asset_searched and self.computer.jss_id is None:
            if not self.serial_searched:
                self.serial_input()
                return
        self.process_logic()

    def process_logic(self):
        self.dt.proceed = False

        # If JSS ID doesn't exist
        if self.computer.jss_id is None:
            self.entry_controller = EntryController(self.main_view, self.computer, self.dt)
            self.entry_controller.populate_entry_fields()
            self.entry_controller.entry_view.text_lbl.config(text="No JSS record exists for this computer.\n"
                                                                       "Create the new record by filling in the\n"
                                                                       "following fields:")
            # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
            # the barcode, asset, and name fields of the computer object will be updated.
            self.main_view.wait_window(window=self.entry_controller.entry_view)

            # Make sure the serial field for the computer object was updated/set.
            if self.computer.serial_number is None:
                self.computer.serial_number = self.computer.get_serial()

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.dt.proceed is False:
                return

            # If user clicked submit in the entry view window, the computer will be enrolled in the JSS to create
            # a JSS ID for it in JAMF.
            logger.debug("Enrolling because JSS ID is None.")
            self.jss_server.enroll_computer()
            logger.debug("Enrolling finished.")

            # Since JSS ID has now been created, retrieve it using the search parameter inputted by the user.
            self.computer.jss_id = self.jss_server.match(self.jss_server.search_param)

            # Update the JAMF record with the barcode, asset, and name of the computer
            self.jss_server.push_enroll_fields(self.computer)

            # Store the recently pushed fields
            pushed_fields = self.tuggyboat.get_tugboat_fields(self.computer.jss_id)
            logger.debug("Pushed enroll fields: {}".format(pformat(pushed_fields)))

        # If JSS ID exists
        elif self.computer.jss_id is not None:
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # CHANGED

            # # Get tugboat fields before altering them.
            # tugboat_fields = self.tuggyboat.get_tugboat_fields(self.computer.jss_id)
            # logger.debug("Original fields before alteration: {}".format(pformat(tugboat_fields)))

            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # CHANGED
            prev_barcode_1 = self.jss_server.get_barcode_1(self.computer.jss_id)
            prev_barcode_2 = self.jss_server.get_barcode_2(self.computer.jss_id)
            prev_asset = self.jss_server.get_asset_tag(self.computer.jss_id)
            prev_name = self.jss_server.get_computer_name(self.computer.jss_id)

            # Store the unaltered barcode, asset, and name fields.
            # prev_barcode_1 = tugboat_fields['general']['barcode_1']
            # prev_asset = tugboat_fields['general']['asset_tag']
            # prev_name = self.jss_server.get_prev_name(self.computer.jss_id)

            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

            # If neither the barcode or asset have been entered, set the fields to the returned JSS fields
            if not self.barcode_searched and not self.asset_searched:
                self.computer.barcode_1 = prev_barcode_1
                self.computer.barcode_2 = prev_barcode_2
                self.computer.asset_tag = prev_asset
                self.computer.name = prev_name

            if self.computer.serial_number is None:
                self.computer.serial_number = self.computer.get_serial()

            logger.debug("Previous barcode: {}".format(prev_barcode_1))
            logger.debug("Previous asset: {}".format(prev_asset))
            logger.debug("Previous name: {}".format(prev_name))

            # Open the entry window
            self.entry_controller = EntryController(self.main_view, self.computer, self.dt)
            self.entry_controller.entry_view.text_lbl.config(text="JSS record exists. Please verify/correct the "
                                                                  "following fields.")
            self.entry_controller.populate_entry_fields()
            # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
            # the barcode, asset, and name fields of the computer object will be updated.
            self.main_view.wait_window(window=self.entry_controller.entry_view)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.dt.proceed is False:
                return

            # Check to see what fields changed after the user updated the fields through the entry view window.
            if self.computer.barcode_1 == prev_barcode_1:
                logger.debug("Barcode {} is correct.".format(self.computer.barcode_1))
                self.computer.barcode_1 = None
            else:
                self.computer.incorrect_barcode = prev_barcode_1
                logger.debug("Barcode {} is incorrect.".format(self.computer.incorrect_barcode))

            if self.computer.asset_tag == prev_asset:
                logger.debug("Asset {} is correct.".format(self.computer.asset_tag))
                self.computer.asset_tag = None
            else:
                self.computer.incorrect_asset = prev_asset
                logger.debug("Asset {} is incorrect.".format(self.computer.incorrect_asset))

            if self.jss_server.get_serial(self.computer.jss_id) == self.computer.get_serial():
                logger.debug("Serial {} is correct.".format(self.computer.serial_number))
                self.computer.serial_number = None
            else:
                self.computer.serial_number = self.computer.get_serial()
                self.computer.incorrect_serial = self.jss_server.get_serial(self.computer.jss_id)
                logger.debug("JSS serial {} is incorrect.".format(self.computer.incorrect_serial))

            if self.computer.name == prev_name:
                self.computer.name = None

            # Check if Managed
            managed = self.jss_server.get_managed_status(self.computer.jss_id)
            logger.debug("Management status is {}".format(managed))

            # If managed status is false, re-enroll computer to set managed status to true.
            if managed == 'false' or managed == 'False':
                logger.info("Enrolling to change managed status to true to enable modification of JSS record.")
                self.jss_server.enroll_computer()

            # Push enroll fields to JSS server
            self.jss_server.push_enroll_fields(self.computer)

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # CHANGED
        # Get xml fields before altering them.
        # pre_offboard_fields = self.jss_server.get_xml_fields(self.computer.jss_id, offboard_xml)
        # logger.debug("Fields before offboarding: {}".format(pformat(pre_offboard_fields)))

        # Stores offboarded values for later comparison
        # fields_to_offboard = self.tuggyboat.get_offboard_fields(self.computer.jss_id)
        # logger.debug("Fields to be offboarded: {}".format(pformat(fields_to_offboard)))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # CHANGED


        # offboarded_values = self.tuggyboat.set_offboard_fields(fields_to_offboard, inventory_status=self.inventory_status)
        # logger.debug("Offboarded fields to be sent: {}".format(pformat(offboarded_values)))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # CHANGED
        self.jss_server.push_xml_fields(os.path.join(self.private_dir, self.offboard_config), self.computer.jss_id)

        # Push offboard fields to the JSS
        # self.tuggyboat.push_offboard_fields(self.computer.jss_id, offboarded_values)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # CHANGED
        # post_offboard_fields = self.jss_server.get_xml_fields(self.computer.jss_id, offboard_xml)
        # logger.debug("Fields after offboarding: {}".format(pformat(post_offboard_fields)))

        # Retrieves new computer data after sending the offboard fields for later comparison
        # new_jss_data = self.tuggyboat1.get_offboard_fields(self.computer.jss_id)
        # logger.debug("New retrieved fields: {}".format(pformat(new_jss_data)))

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Compare new JSS data against the sent offboarded fields. They should be the same.
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # CHANGED
        # Get the new managed status and make sure it's false
        post_managed_status = self.jss_server.get_managed_status(self.computer.jss_id)
        logger.debug("post_managed_status: {}".format(post_managed_status))

        if post_managed_status != 'false':
            raise SystemExit("ERROR: Managed status is not false after offboarding.")

        # # Get the new computer name and make sure it's the same as the offboarded name
        # new_computer_name = new_jss_data['general']['computer_name']
        # logger.debug("new_computer_name: {}".format(new_computer_name))
        #
        # intended_computer_name = offboarded_values['general']['computer_name']
        # logger.debug("intented_computer_name: {}".format(intended_computer_name))
        #
        # if new_computer_name != intended_computer_name:
        #     raise SystemExit(
        #         "ERROR: Computer name is " + new_computer_name + " but should be " + intended_computer_name)

        # # Remove managed status from new_JSS_data and offboarded_values to compare the rest of the data.
        # new_jss_data['general']['remote_management'].pop('managed', None)
        # offboarded_values['general']['remote_management'].pop('managed', None)
        #
        # # Check new data against offboarded fields
        # if new_jss_data != offboarded_values:
        #     raise SystemExit("ERROR: Some of the new fields do not match offboard values")
        # logger.debug("All offboarded values were successfully received by the JSS.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Notify slack channel that offboard tool has finished.
        if self.slack_data['slack_enabled'] == "True":
            self.send_slack_message("Offboarding complete.")

        # Prepare document for printing
        doc = JssDoc(self.jss_server, self.computer.jss_id, self.computer)
        doc.create_html()
        doc.html2pdf()
        if self.print_enabled:
            doc.applescript_print()

        # final_tugboat_fields = self.jss_server.get_tugboat_fields(self.computer.jss_id)
        # logger.debug("Final Tugboat fields: \n{}".format(pformat(final_tugboat_fields)))

        if self.slack_data['slackify_daemon_enabled'] == 'True':
            self.start_slackify_reminder_dameon()

        logger.info("Blade Runner successfully finished.")
        self.terminate()

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

    # Run the application
    app = MainController(root, jss_server, slack_data)
    app.run()


