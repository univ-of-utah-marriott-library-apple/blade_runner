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
import subprocess
import webbrowser
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


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
    base_no_ext = os.path.splitext(os.path.basename(pdf))[0]
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Build AppleScript to print PDF to default printer from Preview.
    script = r'''
    set theFile to POSIX path of "{}"
    do shell script("open " & quoted form of theFile) 
    tell application "Preview"
        delay 2
        set theOpenDocs to get name of every window
        repeat with theDoc in theOpenDocs
            if theDoc contains "{}" then
                set theWindow to the first item of (get the windows whose name is theDoc)
                print theWindow
            end if
        end repeat
    end tell
    '''.format(pdf, base_no_ext)
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

