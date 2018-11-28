from computer import Computer
import os
import re
import inspect
from management_tools import loggers
import subprocess
import webbrowser

class JssDoc(object):
    def __init__(self, jss_server, jss_id):
        self.jss_server = jss_server
        self.computer = Computer()
        self.home = os.path.expanduser("~")
        self.blade_runner_dir = "blade-runner-data/"
        self.abs_dir = self.home + '/Desktop/' + self.blade_runner_dir
        self.computer.jss_id = jss_id
        self.computer.prev_name = jss_server.get_prev_name(jss_id)
        self.computer.name = self.jss_server.get_tugboat_fields(jss_id)['general']['computer_name']
        self.computer.name = str(re.sub(u'(\u2019|\u2018)', '', self.computer.name))
        self.computer.barcode = self.jss_server.get_tugboat_fields(jss_id)['general']['barcode_1']
        self.computer.asset = self.jss_server.get_tugboat_fields(jss_id)['general']['asset_tag']


        self.lbase = self.computer.asset + "_yellow_asset_tag"
        self.abs_lbase = self.abs_dir + self.lbase
        self.abs_html = self.abs_lbase + ".html"
        self.abs_pdf = self.abs_lbase + ".pdf"

    def create_html(self):
        '''Creates an .html file'''
        hardware_list_main = self.jss_server.return_jss_hardware_inventory(self.computer.jss_id)
        hardware_list_storage = hardware_list_main['storage'][0]
        drive_capacity = str(hardware_list_storage['drive_capacity_mb'])

        # Grabs information on if the computer has an SSD or not.
        drive_model = hardware_list_storage['model']
        if "SSD" in drive_model:
            has_SSD = "Yes"
        elif "OWC" in drive_model:
            has_SSD = "Yes"
        else:
            has_SSD = "No"

        # Grabs the current total of RAM.
        ram_total = hardware_list_main["total_ram"]
        ram_total = str(ram_total) + " MB"

        # Grabs the Model of Computer
        computer_model = hardware_list_main["model"]

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General Tab requests
        # Builds overall list
        general_list_main = self.jss_server.return_jss_general_inventory(self.computer.jss_id)

        # Check if Managed
        remote_mangement_list = general_list_main['remote_management']
        managed = str(remote_mangement_list['managed'])

        # Grab the Serial Number
        serial_number = general_list_main["serial_number"]

        # Make directory for jss doc if it doesn't exist
        try:
            os.makedirs(self.abs_dir)
        except OSError as e:
            if e.errno != 17:
                raise

        if self.computer.incorrect_barcode is not None \
                or self.computer.incorrect_asset is not None \
                or self.computer.incorrect_serial is not None:
            review_content = """<b>These are the previous incorrect JSS fields. They should be reviewed to fix </b>
            <b>any JSS inconsistencies.</b>
            <p>
            <b>Previous barcode: </b> <font color="red">""" + self.computer.incorrect_barcode + """</font>
            <p>
            <b>Previous asset tag: </b> <font color="red">""" + self.computer.incorrect_asset + """</font>
            <p>
            <b>Previous serial number: </b> <font color="red">""" + self.computer.incorrect_serial + """</font>
            </font>"""
        else:
            review_content = ""

        file_content = """<!DOCTYPE HTML PUBLIC " -//W3C//DTD HTML 4.01 Transition//EN" 
        "http://www.w3.org/TR/htm14/loose.dtd">
        <html>
          <head>
            <title>Inventory</title>
            <link rel="stylesheet" href="myCs325Style.css" type="text/css"/>
          </head>
          <body>
            <font size="5">
            <b>New Name: </b> """ + self.computer.name + """
            <p>
            <b>Previous Name: </b> """ + self.computer.prev_name + """
            <p>
            <b>Barcode: </b> """ + self.computer.barcode + """
            <p>
            <b>Asset: </b> """ + self.computer.asset + """
            <p>
            <b>JSS ID: </b> """ + self.computer.jss_id + """    <b>Managed: </b> """ + managed + """
            <p>
            <b>Serial Number: </b> """ + serial_number + """
            <p>
            <b>Model: </b> """ + computer_model + """
            <p>
            <b>SSD: </b> """ + has_SSD + """    <b>RAM: </b> """ + ram_total + """
            <p>
            <b>Drive Capacity: </b> """ + drive_capacity + """ MB
            <p>
            """ + review_content + """
          </body>
        </html>"""

        with open(self.abs_html, "w+") as f:
            f.write(file_content)

    def open_html(self):
        logger.info("open_html" + ": activated")
        try:
            webbrowser.get('macosx').open("file://" + self.abs_html)
        except Exception as e:
            pass

    def html2pdf(self):
        '''Convert .html to .pdf so that file can be printed through command line. Prints only the first page, which
        is  the "-P 1" option.'''
        logger.info("Converting HTML to PDF")
        try:
            with open(self.abs_pdf, 'w+') as pdfout:
                subprocess.call(['/usr/sbin/cupsfilter', "-P", "1", self.abs_html], stdout=pdfout,
                                stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.debug(e.output)
        logger.info("Converting HTML to PDF finished.")

    def exist_printer(self, printer):
        logger.info("Checking for printers.")
        cmd = ['lpstat', '-a']
        try:
            printers = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if printers.find(printer) != -1:
                logger.info("Checking for printers finished.")
                return True
        except subprocess.CalledProcessError as e:
            logger.info("Checking for printers failed.")
            logger.debug(e.output)
            return False

        logger.info("Checking for printers finished.")
        return False

    def set_up_printer(self, printer, area, ip):
        logger.info("Setting up printer.")
        cmd = ['lpadmin', '-p', printer, '-L', area, '-E', '-v', ip]
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.info("Setting up printer failed.")
            logger.debug(e.output)

        logger.info("Setting up printer finished.")

    def print_pdf(self):
        '''Prints .pdf file to local printer. To find available printers, use:

                lpstat -a

        '''
        logger.info("print_pdf" + ": activated")

        printer_1 = 'Tech_Lvl5_HP_M3035'
        printer_2 = '_155_97_1_91'
        print_cmd = ['lp', '-d', printer_2, self.abs_pdf]
        try:
            subprocess.check_output(print_cmd)
            logger.info("Print successful.")
        except subprocess.CalledProcessError as e:
            logger.info(e)
        logger.info("Printing computer info finished.")

    def applescript_print(self):
        logger.info("applescript_print" + ": activated")

        script = r'''set theFile to POSIX path of "''' + self.abs_pdf + r'''"
        do shell script("open " & theFile) 
        tell application "Preview"
            delay 2
            print the front document
        end tell
                '''

        with open("/tmp/print.sh", "w+") as f:
            f.write(script)

        try:
            cmd = ['/usr/bin/osascript', '/tmp/print.sh']
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            logger.info("Print successful.")
            os.rename(self.abs_pdf, self.abs_lbase + '-printed' + ".pdf")
        except subprocess.CalledProcessError as e:
            logger.info("" + str(e.output))
            logger.info("Document didn't print. Make sure a default printer has been configured.")
            # logger.info("The selected printer " + printer + " can not be found. To set up a printer, or see a list of "
            #                                           "available printers, go to System "
            #                                           "Preferences>Printers & Scanners. The name of the printer is "
            #                                           "the argument for applescripot_print()")
            logger.info("applescript_print" + ": failed")


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)