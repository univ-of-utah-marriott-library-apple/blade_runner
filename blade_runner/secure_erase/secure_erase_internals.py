#!/usr/bin/python
# -*- coding: utf-8 -*-

"""This script is meant to be run off an external HD. Make sure that the management_tools module is in the correct
folder on the external HD.
"""

import subprocess as sp
import re
from management_tools import loggers
import os
import sys
import inspect
import socket
import urllib2
from management_tools.slack import IncomingWebhooksSender as IWS
import plistlib
import document as doc
import tkMessageBox
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
from msg_box import MsgBox


def firmware_pass_exists():
    cmd = ['firmwarepasswd', '-check']
    try:
        firm_status = sp.check_output(cmd, stderr=sp.STDOUT)
        if firm_status.find("Yes") != -1:
            logger.info("Firmware password is enabled")
            return True
        else:
            return False
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("There was an error checking the firmware password status.")
        raise e
    except OSError as e:
        if e.errno is 2:
            logger.error('Command "{}" not found.'.format(cmd[0]))
            raise OSError('Command "{}" not found.'.format(cmd[0]))

    logger.info("Firmware password is disabled")
    return False


def list_main_disks_deprecated():
    """Lists main disks, e.g. disk0, disk1, disk2, etc.
    """
    cmd = ['diskutil', 'info', '-all']
    # outputs a byte string
    disk_output = sp.check_output(cmd)
    byte_str_pattern = re.compile(b'/dev/disk\d+\n')
    main_disks = re.findall(byte_str_pattern, disk_output)
    # Removes \n from each item in the list.
    main_disks = map(str.strip, main_disks)
    logger.debug("Main disks: " + str(main_disks))

    return main_disks


def list_main_disks():
    cmd = ['diskutil', 'list', '-plist']
    disk_output = sp.check_output(cmd)
    disks_info = plistlib.readPlistFromString(disk_output)
    return disks_info['WholeDisks']


def find_internal_disks_deprecated(main_disks):
    """Finds internal disks from a list of the main disks.
    """
    internal_disks = []
    for disk in main_disks:
        cmd = ['diskutil', 'list', 'internal', disk]
        internal_status = sp.check_output(cmd)
        if internal_status.find(disk) != -1:
            internal_disks.append(disk)

    logger.debug("Internal Disks: " + str(internal_disks))
    return internal_disks


def find_internal_disks(main_disks):
    internal_disks = []
    for disk in main_disks:
        cmd = ['diskutil', 'info', '-plist', disk]
        disk_output = sp.check_output(cmd)
        disk_info = plistlib.readPlistFromString(disk_output)
        if disk_info['Internal']:
            internal_disks.append(disk)
    logger.debug("Internal Disks: " + str(internal_disks))
    return internal_disks


def interactive(question, default=None):
    if not sys.stdout.isatty():
        logger.debug("Not a tty.")
        return True

    response = None
    while response not in ['y', 'n', 'yes', 'no']:
        r = raw_input("{0} [y/n]: ".format(question))
        response = r.lower() if r else default

    logger.debug("Response : " + response)
    return True if response in ['yes', 'y'] else False


class VerifyErase(object):

    @staticmethod
    def by_verify_disk(disk):
        cmd = ['diskutil', 'verifyDisk', disk]
        try:
            output = sp.check_output(cmd, stderr=sp.STDOUT)
        except sp.CalledProcessError as e:
            output = "{0}".format(e.output)
        if ("Nonexistent" or "unknown" or "damaged") in output:
            logger.info("Secure erase successful as per by_verify_disk()")
            return True
        else:
            logger.warn("Secure erase failed as per by_verify_disk()")
            return False

    @staticmethod
    def by_type_name(disk):
        cmd = ['diskutil', 'info', '-plist', disk]
        output = sp.check_output(cmd)
        type_name = plistlib.readPlistFromString(output)['Content']
        if type_name == '':
            logger.info("Secure erase successful as per by_type_name()")
            return True
        else:
            logger.info("Secure erase failed as per by_type_name()")
            return False

    @staticmethod
    def by_all_disks(disk):
        cmd = ['diskutil', 'list', '-plist', disk]
        output = sp.check_output(cmd)
        all_disks = plistlib.readPlistFromString(output)['AllDisks']
        if len(all_disks) == 1:
            logger.info("Secure erase successful as per by_all_disks()")
            return True
        logger.info("Secure erase failed as per by_all_disks()")
        return False

    @staticmethod
    def by_volumes_from_disks(disk):
        cmd = ['diskutil', 'list', '-plist', disk]
        output = sp.check_output(cmd)
        vols_from_disks = plistlib.readPlistFromString(output)['VolumesFromDisks']
        if len(vols_from_disks) == 0:
            logger.info("Secure erase successful as per byAllVolumesFromDisks()")
            return True
        logger.info("Secure erase failed as per byAllVolumesFromDisks()")
        return False


def is_virtual_deprecated(disk):
    cmd = ['diskutil', 'info', '-plist', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("Failed to determine state of {0}".format(disk))
        raise SystemExit(e.output)
    state = plistlib.readPlistFromString(output)['VirtualOrPhysical']
    if state == "Virtual":
        logger.debug("{0} is a virtual disk".format(disk))
        return True
    elif state == "Physical":
        logger.debug("{0} is a physical disk".format(disk))
        return False
    logger.debug("Could not determine the state of {0}.".format(disk))


def is_coreStorage_deprecated(disk):
    cmd = ['diskutil', 'info', '-plist', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        plistlib.readPlistFromString(output)['CoreStorageLVGUUID']
        logger.debug("{0} is a CoreStorage".format(disk))
        return True
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage".format(disk))
        return False
    except sp.CalledProcessError as e:
        logger.debug(e.output)
        if str(e.output).find("Could not find disk") != -1:
            logger.debug("{0} is not a CoreStorage".format(disk))
            return False
        raise


def get_lvgUUID_deprecated(disk):
    cmd = ['diskutil', 'info', '-plist', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        lvgUUID = plistlib.readPlistFromString(output)['CoreStorageLVGUUID']
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage. Couldn’t retrieve lvgUUID".format(disk))
        return False
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("Couldn’t retrieve lvgUUID for {0}".format(disk))
        raise
    return lvgUUID


def is_coreStorage(disk):
    cmd = ["diskutil", "coreStorage", "info", "-plist", disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        plistlib.readPlistFromString(output)['MemberOfCoreStorageLogicalVolumeGroup']
        logger.debug("{0} is a CoreStorage".format(disk))
        return True
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage".format(disk))
        return False
    except sp.CalledProcessError as e:
        if str(e.output).find("is not a CoreStorage disk") != -1:
            logger.debug("{0} is not a CoreStorage".format(disk))
            return False
        logger.debug(e.output)
        raise


def get_lvgUUID(disk):
    cmd = ['diskutil', 'coreStorage', 'info', '-plist', disk]
    try:
        output = sp.check_output(cmd)
        lvgUUID = plistlib.readPlistFromString(output)['MemberOfCoreStorageLogicalVolumeGroup']
        logger.debug("{} lvgUUID is {}".format(disk, lvgUUID))
    except KeyError as e:
        logger.debug("{0}".format(e))
        logger.debug("{0} is not a CoreStorage. Couldn't retrieve lvgUUID".format(disk))
        return False
    except sp.CalledProcessError as e:
        logger.error(e.output)
        logger.error("Couldn't retrieve lvgUUID for {0}".format(disk))
        raise
    return lvgUUID


def force_unmount(disk):
    cmd = ['diskutil', 'unmount', 'force', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        logger.info("{0} successfully force umounted.".format(disk))
        return True
    except sp.CalledProcessError as e:
        logger.debug(e.output)
        logger.info("{0} failed force umount.".format(disk))
        return False


def delete_corestorage(lvgUUID):
    cmd = ['diskutil', 'cs', 'delete', lvgUUID]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        return True
    except sp.CalledProcessError as e:
        logger.debug(e.output)
        logger.info("Couldn't erase CoreStorage")
        return False


def repair_volume(disk):
    cmd = ['diskutil', 'repairVolume', disk]
    try:
        output = sp.check_output(cmd, stderr=sp.STDOUT)
        logger.debug(output)
        logger.info("{0} was successfully repaired.".format(disk))
        return True
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("{0} couldn't be repaired.".format(disk))


def secure_erase(disk):
    logger.warn("SECURE ERASING " + disk)
    cmd = ['diskutil', 'secureErase', '0', disk]

    try:
        sp.check_output(cmd, stderr=sp.STDOUT)
        logger.warn('{0} successfully erased.'.format(disk))
        return True
    except sp.CalledProcessError as e:
        logger.info(e.output)
        logger.info("Secure erase on {0} failed".format(disk))
        return False


def diskutil_list():
    cmd = ['diskutil', 'list']
    disk_output = sp.check_output(cmd)
    logger.info(disk_output)
    return disk_output


def secure_erase_internal_disks(internal_disks):
    """Uses secureErase to 0 erase the internal disks. This is to prevent accidental erasing of the external
    host disk.
    """
    disk_output = diskutil_list()
    logger.warn("***************************************************************")
    logger.warn("You are about to secure erase the following internal disk(s):")
    for disk in internal_disks:
        logger.warn("" + disk)
    logger.warn("***************************************************************")
    proceed = True
    erased_status = []
    if proceed:
        logger.warn("Proceeding with secure erase.")
        for disk in internal_disks:
            if not disk.isspace():
                cmd = ['diskutil', 'secureErase', '0', disk]

                try:
                    logger.warn("SECURE ERASING " + disk)
                    sp.Popen(cmd, stderr=sp.STDOUT).wait()
                    logger.warn('{0} successfully erased.'.format(disk))
                    erased_status.append(True)
                except sp.CalledProcessError as exc:
                    logger.warn("{1}: Failure in erasing {0}.".format(disk, exc.output))
                    try:
                        logger.info("Attemping to force unmount " + disk)
                        cmd = ['diskutil', 'unmountDisk', 'force', disk]
                        unmount_output = sp.check_output(cmd, stderr=sp.STDOUT)
                        logger.info(unmount_output)

                        logger.warn("SECOND ATTEMPT AT SECURE ERASING " + disk)
                        logger.warn("SECURE ERASING " + disk)

                        cmd = ['diskutil', 'secureErase', '0', disk]
                        sp.Popen(cmd, stderr=sp.STDOUT).wait()

                        logger.warn('{0} successfully erased.'.format(disk))
                        erased_status.append(True)
                    except sp.CalledProcessError as e:
                        logger.info(e)
                        try:
                            logger.debug("Attempting to repair {0}".format(disk))
                            output = repair_volume(disk)
                            logger.debug(output)
                            logger.debug("Repair of {0} was successful.".format(disk))
                            logger.debug("Last attempt to secure erase {0}.".format(disk))
                            was_erased = secure_erase(disk)
                            erased_status.append(was_erased)
                        except sp.CalledProcessError as e:
                            logger.info(e.output)
                            erased_status.append(False)

    else:
        logger.info('Operation aborted. Secure erase not performed.')
        erased_status.append(False)

    if all(erased_status) is True:
        return True
    else:
        return False


def main():
    logger.info("SECURE ERASE INTERNALS")
    if os.geteuid() != 0:
        raise SystemExit("Must be run as root.")

    try:
        if firmware_pass_exists():
            msg = "Firmware password is still enabled. Disable to continue."
            logger.warn(msg)
            raise SystemExit(msg)
    except OSError as e:
        msg = ("The current OS is < 10.10. This means the existence of a firmware password \n"
               "can only be verified by booting to the recovery drive. If you know the firmware \n"
               "password has been disabled, continue. Otherwise, cancel.")
        msgbox = MsgBox(msg)
        if not msgbox.proceed:
            raise SystemExit("User canceled.")

    logger.info("Firmware password is not enabled. Continuing with procedure.")
    diskutil_list()
    main_disks = list_main_disks()
    internal_disks = find_internal_disks(main_disks)
    logger.info("Checking for CoreStorage.")
    for disk in internal_disks:
        try:
            if is_coreStorage(disk):
                output = force_unmount(disk)
                lvgUUID = get_lvgUUID(disk)
                logger.info("Deleting CoreStorage on {0}".format(disk))
                delete_corestorage(lvgUUID)
        except SystemExit as e:
            logger.info(e)

        main_disks = list_main_disks()
        internal_disks = find_internal_disks(main_disks)

        erased = secure_erase_internal_disks(internal_disks)

        if erased is True:
            erase_verified = []
            for disk in internal_disks:
                erase_verified.append(VerifyErase.by_verify_disk(disk))
                erase_verified.append(VerifyErase.by_type_name(disk))
                erase_verified.append(VerifyErase.by_all_disks(disk))
                erase_verified.append(VerifyErase.by_volumes_from_disks(disk))
            if all(erase_verified):
                logger.warn("SECURE ERASE SUCCESSFUL")
                try:
                    bot.send_message("SECURE ERASE SUCCESSFUL")
                except urllib2.URLError:
                    err = "Make sure you have ethernet/internet connection"
                    logger.error(err)
                    raise SystemExit(err)

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
                html = os.path.join(docs_dir, "secure_erased.html")
                doc.create_html(html_content, html)
                pdf = doc.html_to_pdf(html)
                try:
                    doc.print_pdf_to_default(pdf)
                except Exception as e:
                    logger.warn("Wasn't able to print secure erase document. Exception: {}".format(e))
            else:
                logger.warn("SECURE ERASE FAILED")
                bot.send_message("SECURE ERASE FAILED")
                raise SystemExit("SECURE ERASE FAILED")
        else:
            logger.warn("SECURE ERASE FAILED")
            bot.send_message("SECURE ERASE FAILED")
            raise SystemExit("SECURE ERASE FAILED")


cf = inspect.currentframe()
abs_file_path = inspect.getframeinfo(cf).filename
basename = os.path.basename(abs_file_path)
lbase = os.path.splitext(basename)[0]
logger = loggers.FileLogger(name=lbase, level=loggers.DEBUG)

if __name__ == "__main__":
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get path to Python script.
    blade_runner_dir = os.path.dirname(abs_file_path)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set path to docs generated by JssDoc.
    docs_dir = os.path.join(blade_runner_dir, "generated_docs")
    slack_plist = os.path.join(blade_runner_dir, "private/slack_config.plist")
    slack_data = plistlib.readPlist(slack_plist)

    current_ip = socket.gethostbyname(socket.gethostname())
    bot = IWS(slack_data["slack_url"], bot_name=current_ip, channel=slack_data["slack_channel"])
    main()

