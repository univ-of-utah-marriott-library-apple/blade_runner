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

import xml.etree.cElementTree as ET
import datetime


def xml_file_append_name(string, xml_file):
    """Appends the name tag in the XML file with the given string.

    Args:
        string (str): String that is appended to the name.
        xml_file (str): File path to XML file.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Parse XML file into an XML tree.
    xml_tree = ET.parse(xml_file)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the root of the XML tree.
    xml_root = xml_tree.getroot()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Find the "name" tag in "general" and append its value with the string input.
    for general_element in xml_root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = name_element.text + string
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return an XML string.
    return ET.tostring(xml_root)


def append_name(string, xml_str):
    """Append the "name" tag in the XML string with the given string.

    Args:
        string (str): String that is appended to the name.
        xml_str (str): XML string.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Parse the XML string into an XML tree and get the root.
    xml_root = ET.fromstring(xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Find the "name" tag in "general" and append its value with the string input.
    for general_element in xml_root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = name_element.text + string
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return an XML string.
    return ET.tostring(xml_root)


def timestamp_note(xml_str, append=True):
    """Append or replace the value in "Additional Item Notes" with the current timestamp.

    Args:
        xml_str (str): XML string.
        append (bool): Whether not not value will be appended or replaced.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the current time.
    d = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Append the value with the timestamp and return the XML string.
    if append:
        return append_additional_note(d, xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Otherwise, replace the value with the timestamp and return the XML string.
    return set_additional_note(d, xml_str)


def append_additional_note(string, xml_str):
    """Append "Additional Item Notes" with the given string.

    Args:
        string (str): String to be appended to the value.
        xml_str (str): XML string.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Convert XML string into an XML tree and get the root of that tree.
    xml_root = ET.fromstring(xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the "Additional Item Notes" value under the "extenstion_attributes" tag and append the string to the value.
    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:
            if ext_attr.find('name').text == "Additional Item Notes" or ext_attr.find('id').text == "45":
                value_element = ext_attr.find('value')
                value_element.text = value_element.text + string
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return XML string.
    return ET.tostring(xml_root)


def set_additional_note(string, xml_str):
    """Replace "Additional Item Notes" with the given string.

    Args:
        string (str): String that replaces the value.
        xml_str (str): XML string.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Convert XML string into an XML tree and get the root of that tree.
    xml_root = ET.fromstring(xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the "Additional Item Notes" value under the "extenstion_attributes" tag and replace the value.
    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:
            if ext_attr.find('id').text == "45":
                value_element = ext_attr.find('value')
                value_element.text = string
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return XML string.
    return ET.tostring(xml_root)


def set_previous_computer_name(string, xml_str):
    """Set the previous computer name extension attribute.

    Args:
        string (str): String that replaces the value.
        xml_str (str): XML string.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Convert XML string into an XML tree and get the root of that tree.
    xml_root = ET.fromstring(xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the "Previous Name Field" value under the "extenstion_attributes" tag and replace the value.
    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:
            if ext_attr.find('id').text == "46":
                value_element = ext_attr.find('value')
                value_element.text = string
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return XML string.
    return ET.tostring(xml_root)


def xml_to_string(xml_file):
    """Get XML string representation of XML file.

    Args:
        xml_file (str): XML file path.

    Returns:
        XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Parse XML file into an XML tree.
    xml_tree = ET.parse(xml_file)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Get the root of the tree.
    xml_root = xml_tree.getroot()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return XML string.
    return ET.tostring(xml_root)


def set_inventory_status(status, xml_str):
    """Set the inventory status.

    Args:
        status (str): Inventory status.
        xml_str (str): XML string.

    Returns:
        Modified XML string.
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Create XML tree and get the root.
    root = ET.fromstring(xml_str)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set the "Inventory Status" value.
    for ext_attr_element in root.findall("./extension_attributes/extension_attribute"):
        element = ext_attr_element.find("name")
        if element.text == "Inventory Status":
            inventory_status_element = ext_attr_element.find("value")
            inventory_status_element.text = status
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Return XML string.
    return ET.tostring(root)

# TODO: Remove this.
if __name__ == "__main__":
    xml_file = "scratch.xml"
    xml_file_append_name("johnny", xml_file)
    set_inventory_status("Salvage", xml_file)