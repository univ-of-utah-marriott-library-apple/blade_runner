from model import Model
from main_view import View
from entry_view_controller import EntryViewController
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

class MainViewController(object):
    def __init__(self, root, server):

        self.model = Model(server)
        self.jss_server = server
        self.computer = Computer()
        self.dt = DecisionTree()

        self.main_view = View(root)
        self.entry_view_controller = None
        self.entry_view = None
        self.set_to_middle(self.main_view)
        self.refocus()

        self.main_view.serial_btn.config(command=self.get_serial_btn)
        self.main_view.bind('<Return>', self.get_serial_btn)


    def run(self):
        self.main_view.mainloop()
        self.refocus()

    def get_serial_btn(self):
        self.computer.serial = self.computer.get_serial()
        logger.debug("Serial number: {0!r}".format(self.computer.serial))

        #self.dt.search_param = self.computer.serial
        self.jss_server.search_param = self.computer.serial
        self.dt.proceed = True
        self.computer.jss_id = self.jss_server.return_jss_match(self.computer.serial)
        self.process_logic()

    def process_logic(self):
        self.dt.proceed = False

        # If JSS ID doesn't exist
        if self.computer.jss_id is None:
            self.entry_view_controller = EntryViewController(self.main_view, self.computer, self.dt)
            self.entry_view_controller.entry_view.text_lbl.config(text="No JSS record exists for this computer.\n"
                                                                       "Create the new record by filling in the\n"
                                                                       "following fields:")
            # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
            # the barcode, asset, and name fields of the computer object will be updated.
            self.main_view.wait_window(window=self.entry_view_controller.entry_view)

            # Make sure the serial field for the computer object was updated/set.
            if self.computer.serial is None:
                self.computer.serial = self.computer.get_serial()

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.dt.proceed is False:
                return

            # If user clicked submit in the entry view window, the computer will be enrolled in the JSS to create
            # a JSS ID for it in JAMF.
            logger.debug("Enrolling because JSS ID is None.")
            self.jss_server.enroll_computer()
            logger.debug("Enrolling finished.")

            # Since JSS ID has now been created, retrieve it using the search parameter inputted by the user.
            self.computer.jss_id = self.jss_server.return_jss_match(jss_server.search_param)

            # Update the JAMF record with the barcode, asset, and name of the computer
            self.jss_server.push_enroll_fields(self.computer)

            # Store the recently pushed fields
            pushed_fields = self.jss_server.get_tugboat_fields(self.computer.jss_id)
            logger.debug("Pushed enroll fields: {}".format(pformat(pushed_fields)))

        # If JSS ID exists
        elif self.computer.jss_id is not None:
            # Get tugboat fields before altering them.
            tugboat_fields = self.jss_server.get_tugboat_fields(self.computer.jss_id)
            logger.debug("Original fields before alteration: {}".format(pformat(tugboat_fields)))

            # Store the unaltered barcode, asset, and name fields.
            prev_barcode = tugboat_fields['general']['barcode_1']
            prev_asset = tugboat_fields['general']['asset_tag']
            prev_name = self.jss_server.get_prev_name(self.computer.jss_id)

            self.computer.barcode = prev_barcode
            self.computer.asset = prev_asset
            self.computer.name = prev_name
            # SHOULD THIS BE PREV NAME OR SMOETHING ELSE

            if self.computer.serial is None:
                self.computer.serial = self.computer.get_serial()

            logger.debug("Previous barcode: {}".format(prev_barcode))
            logger.debug("Previous asset: {}".format(prev_asset))
            logger.debug("Previous name: {}".format(prev_name))

            # Open the entry window
            self.entry_view_controller = EntryViewController(self.main_view, self.computer, self.dt)
            self.entry_view_controller.entry_view.text_lbl.config(text="JSS record exists. Please verify the following"
                                                                       "fields.")
            # Wait for entry view window to close. After entry view window has been closed through the "submit" button,
            # the barcode, asset, and name fields of the computer object will be updated.
            self.main_view.wait_window(window=self.entry_view_controller.entry_view)

            # If user closes out of entry view window using the x button, proceed = False, and the function exits.
            if self.dt.proceed is False:
                return

            # Check to see what fields changed after the user updated the fields through the entry view window.
            if self.computer.barcode == prev_barcode:
                logger.debug("Barcode {} is correct.".format(self.computer.barcode))
                self.computer.barcode = None
            else:
                self.computer.incorrect_barcode = prev_barcode
                logger.debug("Barcode {} is incorrect.".format(self.computer.incorrect_barcode))

            if self.computer.asset == prev_asset:
                logger.debug("Asset {} is correct.".format(self.computer.asset))
                self.computer.asset = None
            else:
                self.computer.incorrect_asset = prev_asset
                logger.debug("Asset {} is incorrect.".format(self.computer.incorrect_asset))

            if self.jss_server.get_serial(self.computer.jss_id) == self.computer.get_serial():
                logger.debug("Serial {} is correct.".format(self.computer.serial))
                self.computer.serial = None
            else:
                self.computer.serial = self.computer.get_serial()
                self.computer.incorrect_serial = tugboat_fields['general']['serial_number']
                logger.debug("JSS serial {} is incorrect.".format(self.computer.incorrect_serial))

            if self.computer.name_label == prev_name:
                self.computer.name_label = None

            # Check if Managed
            managed = self.jss_server.get_managed_status(self.computer.jss_id)
            logger.debug("Management status is {}".format(managed))

            # If managed status is false, re-enroll computer to set managed status to true.
            if managed == 'false' or managed == 'False':
                logger.info("Enrolling to change managed status to true to enable modification of JSS record.")
                self.jss_server.enroll_computer()

            # Push enroll fields to JSS server
            self.jss_server.push_enroll_fields(self.computer)

        # Stores offboarded values for later comparison
        fields_to_offboard = self.jss_server.get_offboard_fields(self.computer.jss_id)
        logger.debug("Fields to be offboarded: {}".format(pformat(fields_to_offboard)))

        offboarded_values = self.jss_server.set_offboard_fields(fields_to_offboard, inventory_status='Salvage')
        logger.debug("Offboarded fields to be sent: {}".format(pformat(offboarded_values)))

        # Push offboard fields to the JSS
        self.jss_server.push_offboard_fields(self.computer.jss_id, offboarded_values)

        # Retrieves new computer data after sending the offboard fields for later comparison
        new_jss_data = self.jss_server.get_offboard_fields(self.computer.jss_id)
        logger.debug("New retrieved fields: {}".format(pformat(new_jss_data)))

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Compare new JSS data against the sent offboarded fields. They should be the same.
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the new managed status and make sure it's false
        new_managed_status = new_jss_data['general']['remote_management']['managed'].lower()
        logger.debug("new_managed_status: {}".format(new_managed_status))

        if new_managed_status != 'false':
            raise SystemExit("ERROR: Managed status is not false after offboarding.")

        # Get the new computer name and make sure it's the same as the offboarded name
        new_computer_name = new_jss_data['general']['computer_name']
        logger.debug("new_computer_name: {}".format(new_computer_name))

        intended_computer_name = offboarded_values['general']['computer_name']
        logger.debug("intented_computer_name: {}".format(intended_computer_name))

        if new_computer_name != intended_computer_name:
            raise SystemExit(
                "ERROR: Computer name is " + new_computer_name + " but should be " + intended_computer_name)

        # Remove managed status from new_JSS_data and offboarded_values to compare the rest of the data.
        new_jss_data['general']['remote_management'].pop('managed', None)
        offboarded_values['general']['remote_management'].pop('managed', None)

        # Check new data against offboarded fields
        if new_jss_data != offboarded_values:
            raise SystemExit("ERROR: Some of the new fields do not match offboard values")
        logger.debug("All offboarded values were successfully received by the JSS.")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Notify slack channel that offboard tool has finished.
        # bot.send_message("offboard_tool.py finished.")

        logger.info("Building HTML Page")
        doc = JssDoc(self.jss_server, self.computer.jss_id)
        doc.create_html()
        doc.html2pdf()
        doc.applescript_print()
        logger.info("Building HTML Page Finished")

        final_tugboat_fields = self.jss_server.get_tugboat_fields(self.computer.jss_id)
        logger.debug("Final Tugboat fields: \n{}".format(pformat(final_tugboat_fields)))
        self.main_view.destroy()
        logger.info("Blade Runner successfully finished.")
        # raise SystemExit()


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

    blade_runner_dir = os.path.dirname(abs_file_path)
    jss_server_plist = os.path.join(blade_runner_dir, "private/jss_server_config.plist")
    jss_server_data = plistlib.readPlist(jss_server_plist)
    jss_server = JssServer(**jss_server_data)
    logger.debug(jss_server.jss_url)

    slack_plist = os.path.join(blade_runner_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)
    current_ip = socket.gethostbyname(socket.gethostname())
    bot = IWS(slack_data['slack_url'], bot_name=current_ip, channel=slack_data['slack_channel'])

    app = MainViewController(root, jss_server)
    app.run()


