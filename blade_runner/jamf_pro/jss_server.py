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

import re
import sys
import json
import base64
import urllib2
import subprocess
import xml.etree.cElementTree as ET
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())


class JssServer(object):
    """Gets, posts, and deletes data from the JSS server.
    """

    def __init__(self, **kwargs):
        """Initializes JSS server.

        Args:
            **kwargs: See Keyword Args section.

        Keyword Args:
            _username (str): JSS username.
            _password (str): JSS password.
            _jss_url (str): JSS url.
            _invite (str): JSS invite for enrolling.
            _jamf_binary_1: Location of JAMF binary on computer.
            _jamf_binary_2: Location of JAMF binary on external drive.

        """
        self.logger = logging.getLogger(__name__)
        self._username = kwargs.get('username', None)
        self._password = kwargs.get('password', None)
        self._jss_url = kwargs.get('jss_url', None)
        self._invite = kwargs.get('invite', None)
        self._jamf_binary_1 = kwargs.get('jamf_binary_1', None)
        self._jamf_binary_2 = kwargs.get('jamf_binary_2', None)

        if self._username is None:
            raise SystemExit("Username for the JSS server was not specified.")
        if self._password is None:
            raise SystemExit("Password for the JSS server was not specified.")
        if self._jss_url is None:
            raise SystemExit("JSS url for the JSS server was not specified.")

    def match(self, search_param):
        """Returns the JSS ID of a computer matching the search parameter. Fulfills JAMF's match API.

        Examples:
            This is an example of the API call made when search_param = "123456"

                https://casper.indentifier.domain:1111/JSSResource/computers/match/123456

        Args:
            search_param (str): barcode 1, barcode 2, asset tag, or serial number of computer.

        Returns:
            JSS ID (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("match: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set API request URL
        request_url = "{0}/JSSResource/computers/match/{1}".format(self._jss_url, search_param)
        self.logger.debug("Request URL: {}".format(request_url))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        self.logger.info("Status code from request: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Read the JSON from the response.
        response_json = json.loads(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the computer data from the JSS
        try:
            computer_data = response_json['computers'][0]
        except IndexError as e:
            # If search param length is greater than 10, it is the serial number
            if len(search_param) > 10:
                self.logger.info("Serial number was not found in the JSS. {}".format(search_param))
            # Otherwise it's the barcode or asset tag
            else:
                self.logger.info("Barcode or asset not found in the JSS. {}".format(search_param))
            return None
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get JSS ID from computer data
        jss_id = str(computer_data['id'])
        self.logger.info("JSS ID: {}".format(jss_id))
        self.logger.debug("match: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return jss_id

    def get_hardware_data(self, jss_id):
        """Get hardware data for computer corresponding to the JSS ID from the JSS.

        Args:
            jss_id (str): JSS ID of the computer.

        Returns:
            hardware data
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_hardware_data: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set API request URL
        request_url = "{0}/JSSResource/computers/id/{1}/subset/Hardware".format(self._jss_url, jss_id)
        self.logger.debug("Request URL: {}".format(request_url))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        self.logger.info("Status code from request: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Read the JSON from the response.
        response_json = json.loads(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the hardware data from the JSON
        hardware_inventory = response_json['computer']['hardware']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_hardware_data: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return hardware_inventory

    def get_general_data(self, jss_id):
        """Gets general data for computer corresponding to JSS ID from the JSS.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            General data.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_general_data: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create API request URL
        request_url = "{0}/JSSResource/computers/id/{1}/subset/General".format(self._jss_url, jss_id)
        self.logger.debug("Request URL: {}".format(request_url))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        self.logger.info("Status code from request: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Read the JSON from the response.
        response_json = json.loads(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the general data from the JSON
        general_inv = response_json['computer']['general']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_general_data: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return general_inv

    def get_extension_attributes(self, jss_id):
        """Gets extension attributes for computer corresponding to JSS ID from the JSS.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Extension attributes.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_extension_attributes: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create API request URL
        request_url = "{0}/JSSResource/computers/id/{1}/subset/extension_attributes".format(self._jss_url, jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        self.logger.info("Status code from request: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Read the JSON from the response.
        response_json = json.loads(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the extension attributes from the JSON response.
        ext_attrs = response_json.get('computer', {}).get('extension_attributes', {})
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_extension_attributes: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return ext_attrs

    def get_extension_attribute(self, jss_id, name=None, id=None):
        """Gets an extensions attribute by extension attribute name or ID.

        Args:
            jss_id (str): JSS ID of computer.
            name (str): Extension attribute name.
            id (str): Extension attribute ID.

        Returns:
            Value of extension attribute.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_extension_attribute: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get extension attributes
        ext_attrs = self.get_extension_attributes(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Search for extension attribute's name or ID.
        for attribute in ext_attrs:
            if name:
                if attribute['name'] == name:
                    ext_attr_val = attribute['value']
                    return ext_attr_val
            elif id:
                if attribute['id'] == id:
                    ext_attr_val = attribute['value']
                    return ext_attr_val
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_extension_attribute: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return None

    def get_location_data(self, jss_id):
        """Gets location data for computer corresponding to JSS ID from the JSS.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Location data.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_location_data: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create API request URL
        request_url = "{0}/JSSResource/computers/id/{1}/subset/Location".format(self._jss_url, jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        self.logger.info("Status code from request: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Read the JSON from the response.
        response_json = json.loads(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the location data from the JSON response.
        jss_location_fields = response_json.get('computer', {}).get('location', {})
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_location_data: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return jss_location_fields

    def get_subsets_data(self, jss_id, xml_file):
        """Gets all the data in each subset of the xml file for the given JSS ID.

        Args:
            jss_id (str): JSS ID of computer.
            xml_file (str): File path to XML file.

        Returns:

        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_subsets_data: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Parse the xml file into an element tree
        tree = ET.parse(xml_file)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get the root element of the tree.
        root = tree.getroot()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For each subset in the xml file/element tree, add it to the subsets list.
        subsets = []
        for subset in root.findall("./"):
            subsets.append(subset.tag)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Initialize subset request that will be appended to the API request.
        subset_request = ""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # For each subset in the list, add it to the subset request.
        for subset in subsets:
            subset_request += subset + "&"
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove the last ampersand.
        subset_request = subset_request[:-1]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create request URL.
        request_url = "{0}/JSSResource/computers/id/{1}/subset/{2}".format(self._jss_url, jss_id, subset_request)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create GET request
        request = self.create_get_request_handler(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request
        response = self.open_request_handler(request)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Turn the xml response into an element tree.
        xml = ET.fromstring(response.read())
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Change the element tree into an xml string.
        xml_string = ET.tostring(xml, encoding='utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_subsets_data: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return xml_string

    def delete_record(self, jss_id):
        """Delete the JSS record corresponding to the JSS ID.

        Args:
            jss_id (str): JSS ID of computer.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("delete_record: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Delete the JSS record.
        self._delete_handler(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("delete_record: finished")

    def push_identity_fields(self, computer):
        """Pushes barcode, asset tag, serial number, and name fields to the JSS server.

        Args:
            computer (Computer): Provides data to send to the JSS.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_identity_fields: started")
        encoding = 'utf-8'
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # v BEGIN: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Computer: Top XML tag
        top = ET.Element('computer')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General tag
        general = ET.SubElement(top, 'general')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # barcode_1 tag
        if computer.barcode_1 is not None:
            barcode_1_xml = ET.SubElement(general, 'barcode_1')
            barcode_1_xml.text = computer.barcode_1.decode(encoding)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # barcode_2 tag
        if computer.barcode_2 is not None:
            barcode_2_xml = ET.SubElement(general, 'barcode_2')
            barcode_2_xml.text = computer.barcode_2.decode(encoding)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # asset_tag tag
        if computer.asset_tag is not None:
            asset_tag_xml = ET.SubElement(general, 'asset_tag')
            asset_tag_xml.text = computer.asset_tag.decode(encoding)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        if computer.serial_number is not None:
            serial_number_xml = ET.SubElement(general, 'serial_number')
            serial_number_xml.text = computer.serial_number.decode(encoding)

        if computer.name is not None:
            name_xml = ET.SubElement(general, 'name')
            name_xml.text = computer.name.decode(encoding)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # ^ END: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Convert xml tree to an xml string.
        xml = ET.tostring(top)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Push xml string and update the computer in the JSS.
        self._push_xml_str_handler(xml, computer.jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_identity_fields: finished")

    def push_xml(self, xml, jss_id):
        """Push data from XML file to update JSS record for the given JSS ID.

        Args:
            xml (str): File path of XML file.
            jss_id (str): JSS ID of computer.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_xml: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Parse XML file into an element tree.
        tree = ET.parse(xml)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Convert element tree into an XML string.
        xml = ET.tostring(tree.getroot(), encoding='utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove new lines from xml string.
        xml = re.sub("\n", "", xml)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove white space between tags.
        xml = re.sub("(>)\s+(<)", r"\1\2", xml)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Push XML string to udpate JSS record.
        self._push_xml_str_handler(xml, jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_xml: finished")

    def push_xml_str(self, xml_str, jss_id):
        """Push data from XML string to update JSS record for the given JSS ID.

        Args:
            xml (str): XML string
            jss_id (str): JSS ID of computer.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_xml_str: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove new lines from xml string.
        xml_str = re.sub("\n", "", xml_str)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Remove white space between tags.
        xml_str = re.sub("(>)\s+(<)", r"\1\2", xml_str)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Push XML string to udpate JSS record.
        self._push_xml_str_handler(xml_str, jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("push_xml_str: finished")

    def get_serial(self, jss_id):
        """Gets the serial number for the computer corresponding to JSS ID from the JSS.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Serial number of computer according to the JSS. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_serial: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get serial number.
        jss_serial = general_data['serial_number']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_serial: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return jss_serial

    def get_managed_status(self, jss_id):
        """Get managed status of computer corresponding to JSS ID.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Managed status of computer. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug('get_managed_status: started')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get remote management data.
        remote_mangement_data = general_data['remote_management']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get management status
        managed = str(remote_mangement_data['managed']).lower()
        self.logger.debug('Management status: {}'.format(managed))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug('get_managed_status: finished')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return managed

    def get_barcode_1(self, jss_id):
        """Get barcode 1 of computer corresponding to JSS ID.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Barcode 1 of computer. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_barcode_1: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get barcode 1.
        barcode = general_data['barcode_1']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_barcode_1: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return barcode

    def get_barcode_2(self, jss_id):
        """Get barcode 2 of computer corresponding to JSS ID.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Barcode 2 of computer. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_barcode_2: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get barcode 2.
        barcode = general_data['barcode_2']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_barcode_2: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return barcode

    def get_asset_tag(self, jss_id):
        """Get asset tag of computer corresponding to JSS ID.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Asset tag of computer. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_asset_tag: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get asset tag.
        asset = general_data['asset_tag']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_asset_tag: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return asset

    def get_name(self, jss_id):
        """Get name of computer corresponding to JSS ID.

        Args:
            jss_id (str): JSS ID of computer

        Returns:
            Name of computer. (str)
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_name: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get general data.
        general_data = self.get_general_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get name.
        name = general_data['name'].encode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_name: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return name

    def get_model(self, jss_id):
        """Get the model of the computer corresponding to the JSS ID.

        Args:
            jss_id (str): JSS ID of computer.

        Returns:
            Model of computer (str).
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_model: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get hardware data.
        hardware_data = self.get_hardware_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get computer model.
        computer_model = hardware_data["model"]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_model: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return computer_model

    def get_ram(self, jss_id):
        """Get the RAM of the computer corresponding to the JSS ID.

        Args:
            jss_id (str): JSS ID of computer.

        Returns:
            Amount of RAM (str).
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_ram: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get hardware data.
        hardware_data = self.get_hardware_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get RAM.
        ram = hardware_data["total_ram"]
        ram = "{} MB".format(ram)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_ram: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return ram

    def get_drive_capacity(self, jss_id):
        """Get the drive capacity (MB) of the computer corresponding to the JSS ID.

        Args:
            jss_id (str): JSS ID of computer.

        Returns:
            Drive capacity in MB (str).
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_drive_capacity: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get hardware data.
        hardware_data = self.get_hardware_data(jss_id)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Get drive capacity.
        storage = hardware_data["storage"][0]
        capacity = storage["drive_capacity_mb"]
        capacity = "{} MB".format(capacity)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("get_drive_capacity: finished")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return capacity

    def enroll_computer(self):
        """Enrolls the computer into the JSS. If the enroll fails, another attempt is made with the second JAMF binary.

        Notes:
            The sole purpose of this is to enable modification of the JSS record. It's not for long term enrollment.
            Hence '-noPolicy' and '-noManage' in the enroll command.

            If the process hangs when jamf is running softwareupdate, go to Settings>Computer Management>Inventory
            Collection>General and uncheck 'Include home directory sizes'. I also uncheck 'Collect available software
            updates' for the purpose of testing.

        Returns:
            The process created by Popen.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("enroll_computer: activated")
        self.logger.info('Enrolling computer.')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        try: # enrolling computer. If the process hangs, see Note section in docstring.
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Run enroll command
            return self._enroll(self._jamf_binary_1, self._invite)
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        except (OSError, subprocess.CalledProcessError) as e:
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            self.logger.error("First enroll attempt failed. Error: {}".format(e))
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            try: # enrolling using the second jamf binary
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                self.logger.info("Enrolling again. Now using {}".format(self._jamf_binary_2))
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Create jamf.conf configuration
                self._jamf_create_conf(self._jamf_binary_2, self._jss_url)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Enroll the computer
                return self._enroll(self._jamf_binary_2, self._invite)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                self.logger.info('Enrolling finished.')
                self.logger.debug('enroll_computer: finished')
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            except subprocess.CalledProcessError as e:
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                msg = "An error occurred while enrolling. {}".format(e)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Add another argument to the exception to store the message.
                e.args += (msg,)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                self.logger.error(msg)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                raise
            except Exception as e:
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                msg = "Enrolling failed. Either the path to {} is incorrect or JAMF has not been " \
                      "installed on this computer.".format(self._jamf_binary_2)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                # Add another argument to the exception to store the message.
                e.args += (msg,)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                self.logger.error(msg)
                # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
                raise
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            self.logger.info('Enrolling finished.')
            self.logger.debug('enroll_computer: finished')

    def _enroll(self, jamf_binary, invite):
        """Enroll the computer.

        Args:
            binary (str): Path to JAMF binary.
            invite (str): Invitation code to enroll in JAMF server.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Setup the command to enroll the computer.
        enroll_cmd = [jamf_binary, 'enroll', '-invitation', invite, '-noPolicy', '-noManage', '-verbose']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run command and print it in place
        proc = subprocess.Popen(enroll_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc

    def _jamf_create_conf(self, jamf_binary, jss_url):
        """Create jamf.conf configuration to bypass verifiying SSL cert when enrolling.

        Args:
            jamf_binary (str): Path to the JAMF binary.
            jss_url (str): URL of the JSS server.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set up the command to create the jamf.conf
        conf_cmd = [jamf_binary, 'createConf', '-url', jss_url, '-verifySSLCert', 'never']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Run the command.
        conf_output = subprocess.check_output(conf_cmd, stderr=subprocess.STDOUT)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug(conf_output)

    def _print_proc_in_place(self, cmd):
        """Run a process and print it in place. This means that all the output will be written to a single line,
        in which each new line from the process erases the previous line.

        Args:
            cmd (list): Command to be executed.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open the enroll process.
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # While the process is running, output the process information onto a single line.
        while proc.poll() is None:
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Read a line from the process output.
            line = proc.stdout.readline()
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Remove the newline character
            line = line.strip()
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # If the line is not empty string, insert the erase line character to erase the line and print
            # the new line. Then flush stdout. This makes the output print in place.
            if line != "":
                erase_line = '\x1b[2K'
                sys.stdout.write('{}Enrolling: {}\r'.format(erase_line, line))
                sys.stdout.flush()
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Print empty string to advance the line.
        print("")

    def _delete_handler(self, jss_id):
        """Handles delete requests.

        Args:
            jss_id (str):

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("_delete_handler: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create request url.
        request_url = "{}/JSSResource/computers/id/{}".format(self._jss_url, jss_id)
        self.logger.debug("Request URL: {}".format(request_url))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create the request.
        request = urllib2.Request(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Add the headers to the request
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self._username + ':' + self._password))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the method to DELETE
        request.get_method = lambda: 'DELETE'
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request.
        response = self.open_request_handler(request)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("HTML DELETE response code: {}".format(response.code))
        self.logger.debug("_delete_handler: finished")

    def open_request_handler(self, request):
        """Handles open requests for requests that are urllib2.Request.

        Args:
            request (urllib2.Request): Request to send.

        Returns:
            Response from request (str).
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open the request and handle it accordingly.
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as error:
            contents = error.read()
            self.logger.error("HTTP error contents: {}".format(contents))
            if error.code == 400:
                self.logger.error("HTTP code {}: {}".format(error.code, "Request error."))
            elif error.code == 401:
                self.logger.error("HTTP code {}: {}".format(error.code, "Authorization error."))
            elif error.code == 403:
                self.logger.error("HTTP code {}: {}".format(error.code, "Permissions error."))
            elif error.code == 404:
                self.logger.error("HTTP code {}: {}".format(error.code, "Resource not found."))
            elif error.code == 409:
                error_message = re.findall("Error: (.*)<", contents)
                self.logger.error("HTTP code {}: {} {}".format(error.code, "Resource conflict", error_message[0]))
            else:
                self.logger.error("HTTP code {}: {}".format(error.code, "Misc HTTP error."))
            raise error
        except urllib2.URLError as error:
            self.logger.error("URL error reason: {}".format(error.reason))
            self.logger.error("Error contacting JSS.")
            raise error
        except Exception as error:
            self.logger.debug("Error submitting to JSS: {}".format(error))
            raise error
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return response

    def create_get_request_handler(self, request_url):
        """Creates a GET request from a URL.

        Args:
            request_url (str): The request URL.

        Returns:
            The created request.
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create a request
        request = urllib2.Request(request_url)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Add headers to the request
        request.add_header('Accept', 'application/json')
        # Format credentials for header.
        creds = base64.b64encode("{}:{}".format(self._username, self._password))
        # Add credentials to header
        request.add_header('Authorization', 'Basic {}'.format(creds))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return request

    def _push_xml_str_handler(self, xml, jss_id):
        """Handles pushing XML string to the JSS.

        Args:
            xml (str): XML in string format.
            jss_id (str): JSS ID of computer.

        Returns:
            void
        """
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("_push_xml_str_handler: started")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create request url.
        request_url = "{}/JSSResource/computers/id/{}".format(self._jss_url, jss_id)
        self.logger.debug("Request URL: {}".format(request_url))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Create request from request url.
        request = urllib2.Request(request_url, data=xml)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Add headers to the request.
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self._username + ':' + self._password))
        request.add_header('Content-Type', 'text/xml')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Set the request method.
        request.get_method = lambda: 'PUT'
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Open/send the request.
        response = self.open_request_handler(request)
        self.logger.info("   HTML PUT response code: {}".format(response.code))
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        self.logger.debug("_push_xml_str_handler: finished")


# Setup logging
# cf = inspect.currentframe()
# abs_file_path = inspect.getframeinfo(cf).filename
# basename = os.path.basename(abs_file_path)
# lbasename = os.path.splitext(basename)[0]
# logger = loggers.FileLogger(name=lbasename, level=loggers.DEBUG)
# logger.debug("{} logger started.".format(lbasename))


