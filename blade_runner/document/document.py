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

import os
import inspect
import subprocess
import webbrowser

from blade_runner.dependencies.management_tools import loggers


def create_html(content, filepath):
    if not filepath.endswith(".html"):
        filepath = "{}.html".format(filepath)

    with open(filepath, "w+") as f:
        f.write(content)


def open_html(filepath):
    """Open the html file in Safari.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    try:# open HTML file in Safari.
        webbrowser.get('macosx').open("file://" + filepath)
    except Exception as e:
        logger.error("Couldn't open webrowser. {}".format(e))


def html_to_pdf(html):
    """Convert HTML file to PDF. Prints only the first page, which is the "-P 1" option.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    pre_ext = os.path.splitext(html)[0]
    pdf = "{}.pdf".format(pre_ext)

    try:# convert HTML to PDF.
        with open(pdf, 'w+') as pdfout:
            subprocess.call(['/usr/sbin/cupsfilter', "-P", "1", html], stdout=pdfout,
                            stderr=subprocess.STDOUT)
        return pdf
    except subprocess.CalledProcessError as e:
        logger.error(e.output)


def print_pdf_to_default(pdf):
    """Print PDF file to default printer.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Build AppleScript to print PDF to default printer from Preview.
    script = r'''
    set theFile to POSIX path of "{}"
    do shell script("open " & theFile) 
    tell application "Preview"
        delay 2
        print the front document
    end tell
            '''.format(pdf)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Write AppleScript text to a bash file.
    with open("/tmp/print.sh", "w+") as f:
        f.write(script)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    try:# run the AppleScript with osascript.
        cmd = ['/usr/bin/osascript', '/tmp/print.sh']
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        logger.info("Print successful.")
        # Append file name with "printed".
        pre_ext, ext = os.path.splitext(pdf)
        os.rename(pdf, "{}_printed.pdf".format(pre_ext))
    except subprocess.CalledProcessError as e:
        logger.error(str(e.output))
        logger.error("Document didn't print. Make sure a default printer has been configured.")


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbase = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbase, level=loggers.DEBUG)
