#!/usr/bin/python

# -*- coding: utf-8 -*-
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

from computer import Computer
import os
import re
import inspect
from management_tools import loggers
import subprocess
import webbrowser
from tuggyboat import TuggyBoat


class JssDoc(object):

    def __init__(self, jss_server, computer):
        self.jss_server = jss_server
        self.computer = computer
        self.home = os.path.expanduser("~")
        self.blade_runner_dir = "blade-runner-data/"
        self.abs_dir = self.home + '/Desktop/' + self.blade_runner_dir

        self.lbase = self.jss_server.get_asset_tag(self.computer.jss_id) + "_yellow_asset_tag"
        self.abs_lbase = self.abs_dir + self.lbase
        self.abs_html = self.abs_lbase + ".html"
        self.abs_pdf = self.abs_lbase + ".pdf"

    def create_html(self):
        '''Creates an .html file'''

        # TODO Remove. This is MacGroup only.
        prev_name = self.jss_server.get_prev_name(self.computer.jss_id)

        name = self.jss_server.get_name(self.computer.jss_id)

        barcode_1 = self.jss_server.get_barcode_1(self.computer.jss_id)

        asset_tag = self.jss_server.get_asset_tag(self.computer.jss_id)
        drive_capacity = self.jss_server.get_drive_capacity(self.computer.jss_id)

        # Grabs the Model of Computer
        computer_model = self.jss_server.get_model(self.computer.jss_id)

        # Grabs information on if the computer has an SSD or not.
        if "SSD" in computer_model or "OWC" in computer_model:
            has_SSD = "Yes"
        else:
            has_SSD = "No"

        # Grabs the current total of RAM.
        ram_total = self.jss_server.get_ram(self.computer.jss_id)

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General Tab requests
        # Check if Managed
        managed = self.jss_server.get_managed_status(self.computer.jss_id)

        # Grab the Serial Number
        serial_number = self.jss_server.get_serial(self.computer.jss_id)

        # Make directory for jss doc if it doesn't exist
        try:
            os.makedirs(self.abs_dir)
        except OSError as e:
            if e.errno != 17:
                raise

        none_filter = lambda x : "" if x is None else x

        if self.computer.incorrect_barcode_1 is not None \
                or self.computer.incorrect_asset is not None \
                or self.computer.incorrect_serial is not None:
            review_content = """<b>These are the previous incorrect JSS fields. They should be reviewed to fix </b>
            <b>any JSS inconsistencies.</b>
            <p>
            <b>Previous barcode: </b> <font color="red">""" + "{}".format(none_filter(self.computer.incorrect_barcode_1)) + """</font>
            <p>
            <b>Previous asset tag: </b> <font color="red">""" + "{}".format(none_filter(self.computer.incorrect_asset)) + """</font>
            <p>
            <b>Previous serial number: </b> <font color="red">""" + "{}".format(none_filter(self.computer.incorrect_serial)) + """</font>
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
            <b>New Name: </b> """ + name + """
            <p>
            <b>Previous Name: </b> """ + prev_name + """
            <p>
            <b>Barcode: </b> """ + barcode_1 + """
            <p>
            <b>Asset: </b> """ + asset_tag + """
            <p>
            <b>JSS ID: </b> """ + self.computer.jss_id + """    <b>Managed: </b> """ + managed + """
            <p>
            <b>Serial Number: </b> """ + serial_number + """
            <p>
            <b>Model: </b> """ + computer_model + """
            <p>
            <b>SSD: </b> """ + has_SSD + """    <b>RAM: </b> """ + ram_total + """
            <p>
            <b>Drive Capacity: </b> """ + drive_capacity + """
            <p>
            """ + review_content + """
          </body>
        </html>"""

        with open(self.abs_html, "w+") as f:
            f.write(file_content)

    def open_html(self):
        logger.info("open_html: started")
        try:
            webbrowser.get('macosx').open("file://" + self.abs_html)
        except Exception as e:
            pass
        logger.info("open_html: finished")

    def html_to_pdf(self):
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

    def print_to_default(self):
        logger.info("print_to_default: started")

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
            logger.info("The selected printer can not be found. To set up a printer, or see a list of "
                                                      "available printers, go to System "
                                                      "Preferences>Printers & Scanners. The name of the printer is "
                                                      "the argument for print_to_default()")
        logger.info("print_to_default: finished")




cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbasename = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)