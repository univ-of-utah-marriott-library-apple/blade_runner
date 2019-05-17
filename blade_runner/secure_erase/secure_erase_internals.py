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

"""This script is meant to be run off an external HD. Make sure that the management_tools module is in the correct
folder on the external HD.
"""

import os
import sys
import socket
import logging
import urllib2
import plistlib
from time import sleep
import subprocess as sp

blade_runner_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(blade_runner_dir, "dependencies"))
sys.path.insert(0, os.path.join(blade_runner_dir, "slack"))
sys.path.insert(0, blade_runner_dir)

from blade_runner.windows.msg_box import MsgBox
from blade_runner.document import document as doc
from blade_runner.dependencies.management_tools.slack import IncomingWebhooksSender as IWS

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


def firmware_pass_exists():
    """Checks for the existence of a firmware password.

    Returns:
        True if firmware password exists.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set command
    cmd = ['firmwarepasswd', '-check']
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Check firmware password status.
    try:
        firm_status = sp.check_output(cmd, stderr=sp.STDOUT)
        if firm_status.find("Yes") != -1:
            logger.info("Firmware password is enabled")
            return True
        else:
            return False
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    #  Handle errors.
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("There was an error checking the firmware password status.")
        raise e
    except OSError as e:
        if e.errno is 2:
            logger.error('Command "{}" not found.'.format(cmd[0]))
            raise OSError('Command "{}" not found.'.format(cmd[0]))
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    logger.info("Firmware password is disabled")
    return False


def list_main_disks():
    """List main disks.

    Returns:
        List of main disks.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get main disks.
    cmd = ['diskutil', 'list', '-plist']
    disk_output = sp.check_output(cmd)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Parse the output into a dictionary.
    disks_info = plistlib.readPlistFromString(disk_output)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return the list of the disks.
    return disks_info['WholeDisks']


def find_internal_disks(main_disks):
    """Find the internal disks from a list of disks.

    Args:
        main_disks (list): List of disks.

    Returns:
        List of internal disks.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # For each disk, see if it's an internal disk.
    internal_disks = []
    for disk in main_disks:
        cmd = ['diskutil', 'info', '-plist', disk]
        disk_output = sp.check_output(cmd)
        disk_info = plistlib.readPlistFromString(disk_output)
        if disk_info['Internal']:
            internal_disks.append(disk)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return internal disks.
    logger.debug("Internal Disks: " + str(internal_disks))
    return internal_disks


def interactive(question, default=None):
    """Interactive question prompt for the command line.

    Args:
        question (str): Question that gets asked on the command line.
        default: Default response.

    Returns:
        True if yes.
        False if no.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If not being run from a tty, return True.
    if not sys.stdout.isatty():
        logger.debug("Not a tty.")
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Wait for a valid response and store it.
    response = None
    while response not in ['y', 'n', 'yes', 'no']:
        r = raw_input("{0} [y/n]: ".format(question))
        response = r.lower() if r else default
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return True or False depending on input.
    logger.debug("Response : " + response)
    return True if response in ['yes', 'y'] else False


class VerifyErase(object):
    """A series of tests to verify if a disk was secure erased. If all pass, the disk was secure erased.
    """

    @staticmethod
    def by_verify_disk(disk):
        """Uses diskutil's verifyDisk argument to determine if disk was secure erased.

        Args:
            disk (str): Disk

        Returns:
            True if output is "Nonexistant", "unknown", or "damaged".
            False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run command.
        cmd = ['diskutil', 'verifyDisk', disk]
        try:
            output = sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            output = "{0}".format(e.output)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Return True or False.
        if ("Nonexistent" or "unknown" or "damaged") in output:
            logger.info("Secure erase successful as per by_verify_disk()")
            return True
        else:
            logger.warn("Secure erase failed as per by_verify_disk()")
            return False

    @staticmethod
    def by_type_name(disk):
        """Checks the value of "Content" to determine if a disk was secure erased.

        Args:
            disk (str): Diskk

        Returns:
            True if value of "Content" is "".
            False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run command.
        cmd = ['diskutil', 'info', '-plist', disk]
        output = sp.check_output(cmd)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get value of "Content" and return True of False.
        type_name = plistlib.readPlistFromString(output)['Content']
        if type_name == '':
            logger.info("Secure erase successful as per by_type_name()")
            return True
        else:
            logger.info("Secure erase failed as per by_type_name()")
            return False

    @staticmethod
    def by_all_disks(disk):
        """Checks the value of "AllDisks" to determine if a disk was secure erased.

        Args:
            disk (str): Disk.

        Returns:
            True if length of "AllDisks" is 1.
            False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run command.
        cmd = ['diskutil', 'list', '-plist', disk]
        output = sp.check_output(cmd)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get value of "AllDisks"
        all_disks = plistlib.readPlistFromString(output)['AllDisks']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If length of "AllDisks" is 1, return True.
        if len(all_disks) == 1:
            logger.info("Secure erase successful as per by_all_disks()")
            return True
        logger.info("Secure erase failed as per by_all_disks()")
        return False

    @staticmethod
    def by_volumes_from_disks(disk):
        """Checks value of "VolumesFromDisks" to determine if a disk was secure erased.

        Args:
            disk (str): Disk.

        Returns:
            True if length of "VolumesFromDisks" is 0.
            False otherwise.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run command.
        cmd = ['diskutil', 'list', '-plist', disk]
        output = sp.check_output(cmd)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get value of "VolumesFromDisks".
        vols_from_disks = plistlib.readPlistFromString(output)['VolumesFromDisks']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If length of value is 0, return True.
        if len(vols_from_disks) == 0:
            logger.info("Secure erase successful as per byAllVolumesFromDisks()")
            return True
        logger.info("Secure erase failed as per byAllVolumesFromDisks()")
        return False


def is_coreStorage(disk):
    """Checks if a disk is CoreStorage.

    Args:
        disk (str): Disk.

    Returns:
        True if CoreStorage.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run command. If plist key exists, return True.
    try:
        cmd = ["diskutil", "coreStorage", "info", "-plist", disk]
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        plistlib.readPlistFromString(output)['MemberOfCoreStorageLogicalVolumeGroup']
        logger.debug("{0} is a CoreStorage".format(disk))
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If key doesn't exist, return False.
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage".format(disk))
        return False
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If output indicates its not a CoreStorage, return False. Raise otherwise.
    except sp.CalledProcessError as e:
        if str(e.output).find("is not a CoreStorage disk") != -1:
            logger.debug("{0} is not a CoreStorage".format(disk))
            return False
        logger.debug(e.output)
        raise


def get_lvgUUID(disk):
    """Get lvgUUID of the disk if it exists.

    Args:
        disk (str): Disk.

    Returns:
        lvgUUID (str) of disk if it exists.
        Returns False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run command and get lvgUUID.
    cmd = ['diskutil', 'coreStorage', 'info', '-plist', disk]
    try:
        output = sp.check_output(cmd)
        lvgUUID = plistlib.readPlistFromString(output)['MemberOfCoreStorageLogicalVolumeGroup']
        logger.debug("{} lvgUUID is {}".format(disk, lvgUUID))
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If key doesn't exist, return False.
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage. Couldn't retrieve lvgUUID".format(disk))
        return False
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If other failure, raise.
    except sp.CalledProcessError as e:
        logger.error(e.output)
        logger.error("Couldn't retrieve lvgUUID for {0}".format(disk))
        raise
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    return lvgUUID


def force_unmount(disk):
    """Force unmount disk.

    Args:
        disk (str): Disk.

    Returns:
        True if successful.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run command to force unmount disk. If successful, return True.
    cmd = ['diskutil', 'unmount', 'force', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        logger.info("{0} successfully force umounted.".format(disk))
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # On error, return False.
    except sp.CalledProcessError as e:
        logger.debug(e.output)
        logger.info("{0} failed force umount.".format(disk))
        return False


def delete_corestorage(lvgUUID):
    """Delete CoreStorage volume.

    Args:
        lvgUUID (str): lvgUUID of CoreStorage volume.

    Returns:
        True if successful.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run command to delete CoreStorage volume. If successful, return True.
    cmd = ['diskutil', 'cs', 'delete', lvgUUID]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # On error, return False.
    except sp.CalledProcessError as e:
        logger.debug(e.output)
        logger.info("Couldn't erase CoreStorage")
        return False


def repair_volume(disk):
    """Repair disk/volume.

    Args:
        disk (str): Disk to repair.

    Returns:
        True if successful.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run repair command. Return True if successful.
    cmd = ['diskutil', 'repairVolume', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        logger.info("{0} was successfully repaired.".format(disk))
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # On error, return False.
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("{0} couldn't be repaired.".format(disk))
        return False


def secure_erase(disk):
    """Secure erase the disk with a single-pass zero-fill erase.

    Args:
        disk (str): Disk.

    Returns:
        True if successful.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    logger.warn("SECURE ERASING " + disk)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run command to secure erase disk. Return True if successful.
    cmd = ['diskutil', 'secureErase', '0', disk]
    try:
        sp.check_output(cmd, stderr=sp.STDOUT)
        logger.warn('{0} successfully erased.'.format(disk))
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # On error, return False.
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("Secure erase on {0} failed".format(disk))
        return False


def diskutil_list():
    """List the disks using "diskutil list".

    Returns:
        Output from "diskutil list".
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # List the disks and return the output.
    cmd = ['diskutil', 'list']
    disk_output = sp.check_output(cmd)
    logger.info(disk_output)
    return disk_output


def secure_erase_internal_disks():
    """Secure erase internal disks with a single-pass zero-fill erase.

    Returns:
        True if successful.
        False otherwise.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get main disks.
    main_disks = list_main_disks()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get internal disks from main disks.
    internal_disks = find_internal_disks(main_disks)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the listed disks and print it to the screen
    disk_output = diskutil_list()
    logger.debug(disk_output)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Warn the user about the disks that will be erased. Give 10 seconds before proceeding.
    logger.warn("***************************************************************")
    logger.warn("You are about to secure erase the following internal disk(s). Proceeding in 10 seconds:")
    for disk in internal_disks:
        logger.warn("" + disk)
    logger.warn("***************************************************************")
    sleep(10)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Proceed with secure erase.
    erased_status = []
    logger.warn("Proceeding with secure erase.")
    for disk in internal_disks:
        # Sometimes a space is returned as a disk. Check for this.
        if not disk.isspace():
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # First attempt to secure erase disk.
            cmd = ['diskutil', 'secureErase', '0', disk]
            try:
                logger.warn("SECURE ERASING " + disk)
                sp.Popen(cmd, stderr=sp.STDOUT).wait()
                logger.warn('{0} successfully erased.'.format(disk))
                erased_status.append(True)
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Handle error. Try again.
            except sp.CalledProcessError as exc:
                logger.warn("{1}: Failure in erasing {0}.".format(disk, exc.output))
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Try to force unmount disk.
                try:
                    logger.info("Attemping to force unmount " + disk)
                    cmd = ['diskutil', 'unmountDisk', 'force', disk]
                    unmount_output = sp.check_output(cmd, stderr=sp.STDOUT)
                    logger.info(unmount_output)
                    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                    # Second attempt to secure erase.
                    logger.warn("SECOND ATTEMPT AT SECURE ERASING " + disk)
                    logger.warn("SECURE ERASING " + disk)

                    cmd = ['diskutil', 'secureErase', '0', disk]
                    sp.Popen(cmd, stderr=sp.STDOUT).wait()

                    logger.warn('{0} successfully erased.'.format(disk))
                    erased_status.append(True)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Handle error. Try again.
                except sp.CalledProcessError as e:
                    logger.info(e)
                    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                    # Try to repair disk.
                    try:
                        logger.debug("Attempting to repair {0}".format(disk))
                        output = repair_volume(disk)
                        logger.debug(output)
                        logger.debug("Repair of {0} was successful.".format(disk))
                        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                        # Third and last attempt to secure erase disk.
                        logger.debug("Last attempt to secure erase {0}.".format(disk))
                        was_erased = secure_erase(disk)
                        erased_status.append(was_erased)
                    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                    # Handle error. Append False to erased_status.
                    except sp.CalledProcessError as e:
                        logger.info(e.output)
                        erased_status.append(False)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If the erased status only contains True, then the disk was secure erased.
    if all(erased_status) is True:
        return True
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Otherwise, disk was not secure erased.
    return False


def main():
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # This logging statement must be here. It is used to signal to other files using pexpect that this script has
    # started.
    logger.info("SECURE ERASE INTERNALS")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Ensure being run as root.
    if os.geteuid() != 0:
        raise SystemExit("Must be run as root.")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Check if firmware password exists. If it does, abort.
    try:
        if firmware_pass_exists():
            msg = "Firmware password is still enabled. Disable to continue."
            logger.warn(msg)
            raise SystemExit(msg)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If unable to use firmwarepasswd command, give the option to proceed.
    except OSError as e:
        msg = ("The current OS is < 10.10. This means the existence of a firmware password \n"
               "can only be verified by booting to the recovery drive. If you know the firmware \n"
               "password has been disabled, continue. Otherwise, cancel.")
        msgbox = MsgBox(msg)
        if not msgbox.proceed:
            raise SystemExit("User canceled.")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    logger.info("Firmware password is not enabled. Continuing with procedure.")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # List main disks.
    diskutil_list()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the main disks.
    main_disks = list_main_disks()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Find internal disks.
    internal_disks = find_internal_disks(main_disks)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # See if any of them are CoreStorage volumes.
    logger.info("Checking for CoreStorage.")
    for disk in internal_disks:
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Force unmount disk and delete the CoreStorage volume.
        try:
            if is_coreStorage(disk):
                output = force_unmount(disk)
                lvgUUID = get_lvgUUID(disk)
                logger.info("Deleting CoreStorage on {0}".format(disk))
                delete_corestorage(lvgUUID)
        except SystemExit as e:
            logger.info(e)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Secure erase the internal disks.
        erased = secure_erase_internal_disks()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If erase successful, run verification tests.
        if erased is True:
            erase_verified = []
            for disk in internal_disks:
                erase_verified.append(VerifyErase.by_verify_disk(disk))
                erase_verified.append(VerifyErase.by_type_name(disk))
                erase_verified.append(VerifyErase.by_all_disks(disk))
                erase_verified.append(VerifyErase.by_volumes_from_disks(disk))
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # If all tests pass, secure erase was successful.
            if all(erase_verified):
                logger.warn("SECURE ERASE SUCCESSFUL")
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Send message
                try:
                    if slack_data["slack_enabled"].lower() == "true":
                        bot.send_message("SECURE ERASE SUCCESSFUL")
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Handle error and exit.
                except urllib2.URLError:
                    err = "Make sure you have ethernet/internet connection"
                    logger.error(err)
                    raise SystemExit(err)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Create document.
                html_content = """
                <!DOCTYPE HTML PUBLIC " -//W3C//DTD HTML 4.01 Transition//EN" 
                "http://www.w3.org/TR/htm14/loose.dtd">
                <html>
                <head>
                <title>Inventory</title>
                <link rel="stylesheet" href="myCs325Style.css" type="text/css"/>
                </head>
                <body>
                <font size="10">
                <br>
                <br>
                <br>
                <br>
                <b>SECURE ERASED</b>
                <br>
                <br>
                <br>	   
                <b><font color="red">READY FOR SURPLUS </font></b>
                <p>
                </font>
                </body>
                </html>"""
                html = os.path.join(secure_erase_docs_dir, "secure_erased.html")
                doc.create_html(html_content, html)
                pdf = doc.html_to_pdf(html)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Try to print document if printing enabled.
                try:
                    if print_settings["print"].lower() == "true":
                        doc.print_pdf_to_default(pdf)
                except Exception as e:
                    logger.warn("Wasn't able to print secure erase document. Exception: {}".format(e))
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # If not all tests passed, secure erase failed.
            else:
                logger.warn("SECURE ERASE FAILED")
                if slack_data["slack_enabled"].lower() == "true":
                    bot.send_message("SECURE ERASE FAILED")
                raise SystemExit("SECURE ERASE FAILED")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # If secure erase failed, exit.
        else:
            logger.warn("SECURE ERASE FAILED")
            if slack_data["slack_enabled"].lower() == "true":
                bot.send_message("SECURE ERASE FAILED")
            raise SystemExit("SECURE ERASE FAILED")


if __name__ == "__main__":
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set up logging vars.
    fmt = '%(asctime)s %(process)d: %(levelname)8s: %(name)s.%(funcName)s: %(message)s'
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    log_dir = os.path.join(os.path.expanduser("~"), "Library/Logs/Blade Runner")
    filepath = os.path.join(log_dir, script_name + ".log")

    # Make log directory.
    try:
        os.mkdir(log_dir)
    except OSError as e:
        if e.errno != 17:
            raise e

    # Set up logger.
    logging.basicConfig(level=logging.DEBUG, format=fmt, filemode='a', filename=filepath)
    logger = logging.getLogger(script_name)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get path to Python script.
    blade_runner_dir = os.path.abspath(__file__)
    for i in range(3):
        blade_runner_dir = os.path.dirname(blade_runner_dir)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set path to docs generated.
    home_dir = os.path.expanduser("~")
    documents_dir = os.path.join(home_dir, "Documents")
    br_docs_dir = os.path.join(documents_dir, "Blade Runner")
    secure_erase_docs_dir = os.path.join(br_docs_dir, "Secure Erase Docs")

    # Make directory for jss doc if it doesn't exist
    try:
        os.makedirs(secure_erase_docs_dir)
    except OSError as e:
        if e.errno != 17:
            raise
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get slack data from config.
    slack_plist = os.path.join(blade_runner_dir, "private/slack_configs/slack.plist")
    slack_data = plistlib.readPlist(slack_plist)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If slack enabled, setup bot.
    if slack_data["slack_enabled"].lower() == "true":
        current_ip = socket.gethostbyname(socket.gethostname())
        bot = IWS(slack_data["slack_url"], bot_name=current_ip, channel=slack_data["slack_channel"])
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Read from print config to enable or disable printing.
    print_config = os.path.join(blade_runner_dir, "private/print_config/print.plist")
    print_settings = plistlib.readPlist(print_config)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Run main.
    main()

