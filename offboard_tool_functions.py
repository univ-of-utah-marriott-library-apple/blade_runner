#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib
import os
import socket
import subprocess
import sys
import re
from management_tools import loggers
from management_tools.slack import IncomingWebhooksSender as IWS
import urllib2
import xml.etree.cElementTree as ET
import base64
import hashlib
import plistlib
import json
from Tkinter import *
import time
import webbrowser
from pprint import pprint
import re
from time import sleep
import sys
import inspect
# import autodepth

cf = inspect.currentframe()
filename = inspect.getframeinfo(cf).filename
filename = os.path.basename(filename)
filename = os.path.splitext(filename)[0]
logger = loggers.FileLogger(name=filename, level=loggers.DEBUG)
logger.debug("Name of logger: " + filename)

class JssServer(object):
    def __init__(self, username=None, password=None, jss_url=None):
        self.username = username
        self.password = password
        self.jss_url = jss_url


class OffboardTool(object):

    def __init__(self, jss_server, invite=None):
        self.username = jss_server.username
        self.password = jss_server.password
        self.jss_url = jss_server.jss_url
        # self.enroll_url = enroll_url
        self.invite = invite
        # self.jss_id = None

    def return_jss_match(self, search_param):

        # Using the JSS API go to the server and pull down the computer id.
        '''Potential fix. If the serial number contains a forward slash, the url request fails. Tried using %2F to fix
        the problem but that didn't work. This is a problem when enrolling VMs, unless you change the VM serial. ???
        Here's an example of what doesn't work:

            string = urllib.quote_plus('VM3Z3gnZu/1a')
            computer_url = '***REMOVED***/JSSResource/computers/match/' + string
        '''
        computer_url = self.jss_url + '/JSSResource/computers/match/' + search_param

        request = urllib2.Request(computer_url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))

        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as e:
            err = "{0}: JSS server could not be reached.".format(e)
            logger.error(err)
            raise SystemExit(err)
        except urllib2.URLError as e:
            err = "{0}: No network connection detected.".format(e)
            logger.error(err)
            raise SystemExit(err)

        logger.info("Status code from request: %s" % response.code)
        response_json = json.loads(response.read())

        # Splits the computer match from the xml to be read below.
        # The UDID matches to one computer. Store the computer information into a new xml.
        try:
            split_computer_match = response_json['computers'][0]
        except:
            if len(search_param) > 10:
                logger.info("Serial number was not found in the JSS.")
            else:
                logger.info("Barcode or asset not found in the JSS.")
            return None
        # Prints the computers ID.
        logger.info("JSS assigned ID: %r" % split_computer_match['id'])
        computer_id = split_computer_match['id']
        return str(computer_id)

    def return_jss_hardware_inventory(self, computer_id):

        # Using the JSS API go to the server and pull down the computer id.

        computer_url = self.jss_url + '/JSSResource/computers/id/' + computer_id + '/subset/Hardware'

        request = urllib2.Request(computer_url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))

        response = urllib2.urlopen(request)
        logger.info("Status code from request: %s" % response.code)
        response_json = json.loads(response.read())

        hardware_list_main = response_json['computer']['hardware']
        # print hardware_list_main
        return (hardware_list_main)

    def return_jss_general_inventory(self, computer_id):

        # Using the JSS API go to the server and pull down the computer id.

        computer_url = self.jss_url + '/JSSResource/computers/id/' + computer_id + '/subset/General'

        request = urllib2.Request(computer_url)
        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))

        response = urllib2.urlopen(request)
        logger.info("Status code from request: %s" % response.code)
        response_json = json.loads(response.read())

        general_list_main = response_json['computer']['general']

        return (general_list_main)

    def return_jss_extension_attributes(self, jss_id):
        logger.debug("jss_url: {}".format(self.jss_url))
        logger.debug("jss_id: {}".format(jss_id))
        # api request url
        computer_url = self.jss_url + '/JSSResource/computers/id/' + jss_id + '/subset/extension_attributes'

        # executing/sending request
        request = urllib2.Request(computer_url)
        request.add_header('Accept', 'application/json')

        # providing credentials
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))

        # receiving response of request
        response = urllib2.urlopen(request)

        logger.info("Status code from request: %s" % response.code)
        # putting response in JSON format
        response_json = json.loads(response.read())

        # remove unicode
        # response_json = ast.literal_eval(json.dumps(response_json))

        jss_extension_attributes = response_json.get('computer', {}).get('extension_attributes', {})

        return jss_extension_attributes

    def return_jss_location_fields(self, computer_id):

        computer_url = self.jss_url + '/JSSResource/computers/id/' + computer_id + '/subset/Location'

        request = urllib2.Request(computer_url)

        request.add_header('Accept', 'application/json')
        request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))

        # receiving response of request
        response = urllib2.urlopen(request)

        # putting response in JSON format
        response_json = json.loads(response.read())

        jss_location_fields = response_json.get('computer', {}).get('location', {})

        return jss_location_fields

    def prev_computer_name(self, jss_id):
        jss_extension_attributes = self.return_jss_extension_attributes(jss_id)

        # store tugboat extension attributes
        for attribute in jss_extension_attributes:

            if attribute['name'] == 'Previous Computer Names':
                prev_name = attribute['value']
                return prev_name

        return ""

    def get_tugboat_fields(self, computer_id):
        '''This method is not complete. I'd like to implement getting all Tugboat fields, but currently I'll just get
        the yellow asset tag and barcode. Later I'd like to have get_offboard_fields() call this function and just
        remove/pop entries that aren't used for offboarding.'''
        # get jss extenstion attributes
        jss_extension_attributes = self.return_jss_extension_attributes(computer_id)

        # store tugboat extension attributes
        for attribute in jss_extension_attributes:

            if attribute['name'] == 'Onboarding IP':

                onboarding_IP = attribute['value']

            elif attribute['name'] == 'Inventory Status':

                inventory_status = attribute['value']

            elif attribute['name'] == 'Inventory Category':

                inventory_category = attribute['value']

            elif attribute['name'] == 'Budget Source':

                budget_source = attribute['value']

        tugboat_ext_attr = {'extension_attributes'.decode('utf-8'): {}}
        tugboat_ext_attr['extension_attributes'].update({'Onboarding IP'.decode('utf-8'): onboarding_IP,
                                                         'Inventory Status'.decode('utf-8'): inventory_status,
                                                         'Inventory Category'.decode('utf-8'): inventory_category,
                                                         'Budget Source'.decode('utf-8'): budget_source})

        # get jss location fields such as building, department, email, phone, realname, etc.
        jss_location_fields = self.return_jss_location_fields(computer_id)
        tugboat_loc_fields = {'location'.decode('utf-8'): {}}

        # store tugboat location fields and reset user
        building = jss_location_fields['building']
        department = jss_location_fields['department']
        email_address = jss_location_fields['email_address']
        phone = jss_location_fields['phone']
        phone_number = jss_location_fields['phone_number']
        position = jss_location_fields['position']
        real_name = jss_location_fields['real_name']
        realname = jss_location_fields['realname']
        room = jss_location_fields['room']
        username = jss_location_fields['username']

        tugboat_loc_fields['location'].update({'building'.decode('utf-8'): building,
                                               'department'.decode('utf-8'): department,
                                               'email_address'.decode('utf-8'): email_address,
                                               'phone'.decode('utf-8'): phone,
                                               'phone_number'.decode('utf-8'): phone_number,
                                               'position'.decode('utf-8'): position,
                                               'real_name'.decode('utf-8'): real_name,
                                               'realname'.decode('utf-8'): realname,
                                               'room'.decode('utf-8'): room,
                                               'username'.decode('utf-8'): username})

        # Get general inventory to get managed status and serial number
        jss_general_inventory = self.return_jss_general_inventory(computer_id)
        computer_name = jss_general_inventory['name']
        serial_number = jss_general_inventory['serial_number']
        barcode_number_jss = jss_general_inventory['barcode_1']
        yellow_asset_tag_jss = jss_general_inventory['asset_tag']

        # Get managed status
        managed = str(jss_general_inventory['remote_management']['managed'])

        tugboat_gen_inventory = {'general'.decode('utf-8'): {}}
        # Update general inventory tugboat dictionary
        tugboat_gen_inventory['general'].update({'computer_name'.decode('utf-8'): computer_name,
                                                 'serial_number'.decode('utf-8'): serial_number,
                                                 'remote_management'.decode('utf-8'): {},
                                                 'barcode_1'.decode('utf-8'): barcode_number_jss,
                                                 'asset_tag'.decode('utf-8'): yellow_asset_tag_jss})

        tugboat_gen_inventory['general']['remote_management'].update(
            {'managed'.decode('utf-8'): managed.decode('utf-8')})

        # tugboat_fields = {'computer': None}
        tugboat_fields = {}
        tugboat_fields.update(tugboat_loc_fields)
        tugboat_fields.update(tugboat_gen_inventory)
        tugboat_fields.update(tugboat_ext_attr)

        return tugboat_fields

    def get_offboard_fields(self, computer_id):

        offboard_fields = self.get_tugboat_fields(computer_id)
        offboard_fields['extension_attributes'].pop('Budget Source', None)
        offboard_fields['general'].pop('barcode_1', None)
        offboard_fields['general'].pop('asset_tag', None)

        return offboard_fields

    def push_enroll_fields(self, jss_id=None, barcode=None, asset=None, name=None,
                           budget_source=None, serial=None):
        '''Pushes the following to the JSS:
            barcode number
            yellow asset tag number
            budget source
        '''
        logger.info("push_enroll_fields(): activated")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # v BEGIN: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Computer: Top XML tag
        top = ET.Element('computer')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Extension attributes tag
        ext_attrs = ET.SubElement(top, 'extension_attributes')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        if budget_source != None:
            budget_source.decode('utf-8')
            # Extension attribute tag
            budget_source_attr = ET.SubElement(ext_attrs, 'extension_attribute')

            # ID tag for budget source
            budget_source_id = ET.SubElement(budget_source_attr, 'id')
            budget_source_id.text = '22'

            # Name tag for budget source
            budget_source_name = ET.SubElement(budget_source_attr, 'name')
            budget_source_name.text = 'Budget Source'

            # Value tag for budget source
            budget_source_value = ET.SubElement(budget_source_attr, 'value')
            budget_source_value.text = budget_source
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        if name != None:
            # Extension attribute tag
            previous_computer_names__attr = ET.SubElement(ext_attrs, 'extension_attribute')

            # ID tag for previous computer name
            previous_computer_names_id = ET.SubElement(previous_computer_names__attr, 'id')
            previous_computer_names_id.text = '46'

            # Name tag for previous computer names
            previous_computer_names_name = ET.SubElement(previous_computer_names__attr, 'name')
            previous_computer_names_name.text = 'Previous Computer Names'

            # Value tag for budget source
            previous_computer_names_value = ET.SubElement(previous_computer_names__attr, 'value')
            previous_computer_names_value.text = name

        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General tag
        general = ET.SubElement(top, 'general')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # barcode_1 tag (white tag)
        if barcode != None:
            barcode_1_xml = ET.SubElement(general, 'barcode_1')
            barcode_1_xml.text = barcode.decode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # asset_tag tag (yellow tag)
        if asset != None:
            asset_tag_xml = ET.SubElement(general, 'asset_tag')
            asset_tag_xml.text = asset.decode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        if serial != None:
            serial_number_xml = ET.SubElement(general, 'serial_number')
            serial_number_xml.text = serial.decode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # ^ END: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

        try:

            logger.debug("  Submitting XML: %r" % ET.tostring(top))

            opener = urllib2.build_opener(urllib2.HTTPHandler)
            computer_url = self.jss_url + '/JSSResource/computers/id/' + jss_id
            request = urllib2.Request(computer_url, data=ET.tostring(top))
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))
            request.add_header('Content-Type', 'text/xml')
            request.get_method = lambda: 'PUT'
            response = opener.open(request)

            logger.info("   HTML PUT response code: %i" % response.code)

        #
        # handle HTTP errors and report
        except urllib2.HTTPError, error:
            contents = error.read()
            print("HTTP error contents: %r" % contents)
            if error.code == 400:
                print("HTTP code %i: %s " % (error.code, "Request error."))
                return
            elif error.code == 401:
                print("HTTP code %i: %s " % (error.code, "Authorization error."))
                return
            elif error.code == 403:
                print("HTTP code %i: %s " % (error.code, "Permissions error."))
                return
            elif error.code == 404:
                print("HTTP code %i: %s " % (error.code, "Resource not found."))
                return
            elif error.code == 409:
                error_message = re.findall("Error: (.*)<", contents)
                print("HTTP code %i: %s %s" % (error.code, "Resource conflict.", error_message[0]))
                return
            else:
                print("HTTP code %i: %s " % (error.code, "Misc HTTP error."))
                return
        except urllib2.URLError, error:
            print("URL error reason: %r" % error.reason)
            print("Error contacting JSS.")
            logger.info("push_enroll_fields(): finished")
            return
        except:
            print("Error submitting to JSS.")
            return
        finally:
            logger.info("push_enroll_fields(): finished")

    def push_label_fields(self, computer_id, barcode_number, yellow_asset_tag, name_label):
        '''Pushes the following to the JSS:
                barcode number
                yellow asset tag number
            '''
        logger.info("push_label_fields(): activated")
        # logger.debug("  ARGS (" + computer_id + ", " + barcode_number + ", " + yellow_asset_tag + ", " + name_label + ")")
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # v BEGIN: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Top XML tag
        top = ET.Element('computer')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General tag
        general = ET.SubElement(top, 'general')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # barcode_1 tag (white tag)
        if barcode_number != "":
            barcode_1_xml = ET.SubElement(general, 'barcode_1')
            barcode_1_xml.text = barcode_number.decode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # asset_tag tag (yellow tag)
        if yellow_asset_tag != "":
            yellow_asset_tag_xml = ET.SubElement(general, 'asset_tag')
            yellow_asset_tag_xml.text = yellow_asset_tag.decode('utf-8')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Extension attributes tag
        ext_attrs = ET.SubElement(top, 'extension_attributes')
        if name_label != "":
            # Extension attribute tag
            previous_computer_names__attr = ET.SubElement(ext_attrs, 'extension_attribute')

            # ID tag for previous computer name
            previous_computer_names_id = ET.SubElement(previous_computer_names__attr, 'id')
            previous_computer_names_id.text = '46'

            # Name tag for previous computer names
            previous_computer_names_name = ET.SubElement(previous_computer_names__attr, 'name')
            previous_computer_names_name.text = 'Previous Computer Names'

            # Value tag for budget source
            previous_computer_names_value = ET.SubElement(previous_computer_names__attr, 'value')
            previous_computer_names_value.text = name_label
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # ^ END: Create XML structure that will be sent through the api call
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

        try:
            logger.debug("  Submitting XML: %r" % ET.tostring(top))

            opener = urllib2.build_opener(urllib2.HTTPHandler)
            computer_url = self.jss_url + '/JSSResource/computers/id/' + computer_id
            request = urllib2.Request(computer_url, data=ET.tostring(top))
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))
            request.add_header('Content-Type', 'text/xml')
            request.get_method = lambda: 'PUT'
            response = opener.open(request)

            logger.info("   HTML PUT response code: %i" % response.code)

        #
        # handle HTTP errors and report
        except urllib2.HTTPError, error:
            contents = error.read()
            print("HTTP error contents: %r" % contents)
            if error.code == 400:
                print("HTTP code %i: %s " % (error.code, "Request error."))
                return
            elif error.code == 401:
                print("HTTP code %i: %s " % (error.code, "Authorization error."))
                return
            elif error.code == 403:
                print("HTTP code %i: %s " % (error.code, "Permissions error."))
                return
            elif error.code == 404:
                print("HTTP code %i: %s " % (error.code, "Resource not found."))
                return
            elif error.code == 409:
                error_message = re.findall("Error: (.*)<", contents)
                print("HTTP code %i: %s %s" % (error.code, "Resource conflict.", error_message[0]))
                return
            else:
                print("HTTP code %i: %s " % (error.code, "Misc HTTP error."))
                return
        except urllib2.URLError, error:
            print("URL error reason: %r" % error.reason)
            print("Error contacting JSS.")
            return
        except:
            print("Error submitting to JSS.")
            return
        finally:
            logger.info("push_label_fields(): finished")

    def push_offboard_fields(self, computer_id, offboard_fields):

        logger.debug("push_offboard_fields(): activated")

        # data entry: location
        building = offboard_fields['location']['building']
        department = offboard_fields['location']['department']
        email_address = offboard_fields['location']['email_address']
        phone = offboard_fields['location']['phone']
        phone_number = offboard_fields['location']['phone_number']
        position = offboard_fields['location']['position']
        real_name = offboard_fields['location']['real_name']
        realname = offboard_fields['location']['realname']
        room = offboard_fields['location']['room']
        username = offboard_fields['location']['username']

        # data entry: general
        name = offboard_fields['general']['computer_name']

        # data entry: remote management
        managed = offboard_fields['general']['remote_management']['managed']

        # data entry: extension attributes
        inventory_category = offboard_fields['extension_attributes']['Inventory Category']
        inventory_status = offboard_fields['extension_attributes']['Inventory Status']
        onboarding_ip = offboard_fields['extension_attributes']['Onboarding IP']

        # build XML object
        top = ET.Element('computer')

        # General xml fields
        general = ET.SubElement(top, 'general')

        computer_name_xml = ET.SubElement(general, 'name')
        computer_name_xml.text = name

        # general>remote management fields
        remote_management = ET.SubElement(general, 'remote_management')
        managed_xml = ET.SubElement(remote_management, 'managed')
        managed_xml.text = managed

        # Location xml fields
        location = ET.SubElement(top, 'location')

        username_xml = ET.SubElement(location, 'username')
        username_xml.text = username

        realname_xml = ET.SubElement(location, 'realname')
        realname_xml.text = realname

        real_name_xml = ET.SubElement(location, 'real_name')
        real_name_xml.text = real_name

        email_xml = ET.SubElement(location, 'email_address')
        email_xml.text = email_address

        position_xml = ET.SubElement(location, 'position')
        position_xml.text = position

        phone_xml = ET.SubElement(location, 'phone')
        phone_xml.text = phone

        phone_number_xml = ET.SubElement(location, 'phone_number')
        phone_number_xml.text = phone_number

        department_xml = ET.SubElement(location, 'department')
        department_xml.text = department

        building_xml = ET.SubElement(location, 'building')
        building_xml.text = building

        room_xml = ET.SubElement(location, 'room')
        room_xml.text = room

        # Extension attributes xml fields

        ext_attrs = ET.SubElement(top, 'extension_attributes')

        inventory_category_attr = ET.SubElement(ext_attrs, 'extension_attribute')

        inventory_category_id = ET.SubElement(inventory_category_attr, 'id')
        inventory_category_id.text = '19'

        inventory_category_name = ET.SubElement(inventory_category_attr, 'name')
        inventory_category_name.text = 'Inventory Category'

        inventory_category_value = ET.SubElement(inventory_category_attr, 'value')
        inventory_category_value.text = inventory_category

        inventory_status_attr = ET.SubElement(ext_attrs, 'extension_attribute')

        inventory_status_id = ET.SubElement(inventory_status_attr, 'id')
        inventory_status_id.text = '23'

        inventory_status_name = ET.SubElement(inventory_status_attr, 'name')
        inventory_status_name.text = 'Inventory Status'

        inventory_status_value = ET.SubElement(inventory_status_attr, 'value')
        inventory_status_value.text = inventory_status

        onboarding_ip_attr = ET.SubElement(ext_attrs, 'extension_attribute')

        onboarding_ip_id = ET.SubElement(onboarding_ip_attr, 'id')
        onboarding_ip_id.text = '24'

        onboarding_ip_name = ET.SubElement(onboarding_ip_attr, 'name')
        onboarding_ip_name.text = 'Onboarding IP'

        onboarding_ip_value = ET.SubElement(onboarding_ip_attr, 'value')
        onboarding_ip_value.text = onboarding_ip

        try:

            logger.debug("  Submitting XML: %r" % ET.tostring(top))
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            computer_url = self.jss_url + '/JSSResource/computers/id/' + computer_id
            request = urllib2.Request(computer_url, data=ET.tostring(top))
            request.add_header('Authorization', 'Basic ' + base64.b64encode(self.username + ':' + self.password))
            request.add_header('Content-Type', 'text/xml')
            request.get_method = lambda: 'PUT'
            response = opener.open(request)

            logger.debug("  HTML PUT response code: %i" % response.code)
            return True

        #
        # handle HTTP errors and report
        except urllib2.HTTPError, error:
            contents = error.read()
            print("HTTP error contents: %r" % contents)
            if error.code == 400:
                print("HTTP code %i: %s " % (error.code, "Request error."))
            elif error.code == 401:
                print("HTTP code %i: %s " % (error.code, "Authorization error."))
            elif error.code == 403:
                print("HTTP code %i: %s " % (error.code, "Permissions error."))
            elif error.code == 404:
                print("HTTP code %i: %s " % (error.code, "Resource not found."))
            elif error.code == 409:
                error_message = re.findall("Error: (.*)<", contents)
                print("HTTP code %i: %s %s" % (error.code, "Resource conflict.", error_message[0]))
            else:
                print("HTTP code %i: %s " % (error.code, "Misc HTTP error."))
        except urllib2.URLError, error:
            print("URL error reason: %r" % error.reason)
            print("Error contacting JSS.")
        except:
            print("Error submitting to JSS.")

        return False


    def set_offboard_fields(self, offboard_fields, inventory_status=None):

        logger.info("set_offboard_fields(): activated")

        if inventory_status == 'Salvage':

            new_prefix = '[SALV]-'.decode('utf-8')
            new_computer_name = new_prefix + offboard_fields['general']['serial_number']

        elif inventory_status == 'Storage':

            new_prefix = '[STOR]-'.decode('utf-8')
            new_computer_name = new_prefix + offboard_fields['general']['serial_number']

        else:

            raise SystemExit('Invalid inventory status. Please choose Salvage or Storage.')

        # offboard_fields['general'].pop('serial_number', None)

        offboard_fields['location'].update({'building': ''.decode('utf-8'),
                                            'department': ''.decode('utf-8'),
                                            'email_address': ''.decode('utf-8'),
                                            'phone': ''.decode('utf-8'),
                                            'phone_number': ''.decode('utf-8'),
                                            'position': ''.decode('utf-8'),
                                            'real_name': ''.decode('utf-8'),
                                            'realname': ''.decode('utf-8'),
                                            'room': ''.decode('utf-8'),
                                            'username': ''.decode('utf-8')})

        offboard_fields['general'].update({'computer_name': new_computer_name})

        offboard_fields['general']['remote_management'].update({'managed': 'False'.decode('utf-8')})

        offboard_fields['extension_attributes'].update({'Inventory Category': 'None'.decode('utf-8'),
                                                        'Inventory Status': inventory_status.decode('utf-8'),
                                                        'Onboarding IP': ''.decode('utf-8')})

        logger.debug("  offboard_fields: " + str(offboard_fields))
        logger.info("set_offboard_fields(): finished")

        return offboard_fields

    def is_jss_serial_correct(self, computer_id):
        ''' Verifies whether or not the local serial number matches the JSS serial number. Returns True if they match,
        and false if they differ.
        '''
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info(func_name() + ": activated")
        # Gets computer (local) serial number and serial number according to JSS
        local_serial = self.get_serial()
        tugboat_fields = self.get_tugboat_fields(computer_id)
        jss_serial = tugboat_fields['general']['serial_number']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Checks if local serial and JSS serial are different. If they are, the JSS serial is stored for review.
        if local_serial != jss_serial:
            logger.debug('Serial numbers are different. Local serial number = ' + local_serial + " != " +
                         jss_serial + " = JSS serial number.")
            logger.info(func_name() + ": succeeded")
            return False
        logger.info(func_name() + ": succeeded")
        return True
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    def get_managed_status(self, jss_id):
        general_list_main = self.return_jss_general_inventory(jss_id)
        remote_mangement_list = general_list_main['remote_management']
        return str(remote_mangement_list['managed'])

    def get_barcode(self, jss_id):
        barcode = self.get_tugboat_fields(jss_id)['general']['barcode_1']
        return barcode

    def get_asset(self, jss_id):
        asset = self.get_tugboat_fields(jss_id)['general']['asset_tag']
        return asset

    def get_name(self, jss_id):
        name = self.get_tugboat_fields(jss_id)['general']['computer_name']
        return name

    @staticmethod
    def get_serial():
        """Gets and returns serial number from the computer. event=None is needed beacuse get_serial is bound to the
        Return key when in the main window"""
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets raw data that contains the serial number
        output = subprocess.check_output(["system_profiler", "SPHardwareDataType"])
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Gets serial number from the raw data
        serial_number = re.findall('Serial Number .system.: (.*)', output)[0]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        return serial_number

    def enroll(self):
        # ***REMOVED***/
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        logger.info(func_name() + ": activated")
        logger.info('Enrolling computer.')
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        jamf = '/usr/local/bin/jamf'
        cmd = [jamf, 'enroll', '-invitation', self.invite, '-noPolicy',
               '-noManage', '-verbose']
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # Enroll computer
        try:
            enroll_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            logger.debug(enroll_output)
            logger.info('Enrolling finished.')
            return True
        # except subprocess.CalledProcessError as e:
        #     logger.error("  > " + str(e.output))
        #     logger.info(func_name() + ": failed")
        #     raise
        except (OSError, subprocess.CalledProcessError) as e:
            # if e.errno == 2:
            logger.error("Couldn't find " + jamf + ". Enrolling failed.")
            try:
                jamf = '/Volumes/Storage/jamf'
                logger.info("Enrolling again. Now using " + jamf)

                conf_cmd = [jamf, 'createConf', '-url', self.jss_url, '-verifySSLCert', 'never']
                conf_output = subprocess.check_output(conf_cmd, stderr=subprocess.STDOUT)
                logger.debug(conf_output)

    #             jss_url = enroll_url
    #             jamf_plist = '''<?xml version="1.0" encoding="UTF-8"?>
    # <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    # <plist version="1.0">
    # <dict>
    # 	<key>jss_url</key>
    # 	<string>''' + jss_url + '''</string>
    # 	<key>last_management_framework_change_id</key>
    # 	<string>33</string>
    # 	<key>max_clock_skew</key>
    # 	<string>-1</string>
    # 	<key>microsoftCAEnabled</key>
    # 	<false/>
    # 	<key>package_validation_level</key>
    # 	<string>1</string>
    # 	<key>self_service_app_path</key>
    # 	<string>/Applications/Utilities/Self Service.app</string>
    # 	<key>verifySSLCert</key>
    # 	<string>never</string>
    # </dict>
    # </plist>'''
    #
    #             with open("/Library/Preferences/com.jamfsoftware.jamf.plist", "w+") as f:
    #                 f.write(jamf_plist)

                enroll_cmd = [jamf, 'enroll', '-invitation', self.invite, '-noPolicy', '-noManage', '-verbose']
                enroll_output = subprocess.check_output(enroll_cmd, stderr=subprocess.STDOUT)
                logger.debug(enroll_output)
                logger.info('Enrolling finished.')
                return True
            except subprocess.CalledProcessError as e:
                logger.error(e.output)
                logger.info(func_name() + ": failed")
                raise
            except Exception as e:
                logger.error("  > Either the path to " + jamf + " is incorrect or JAMF has not "
                                                                "been installed on this computer. ")
                logger.error(e)
                logger.info(func_name() + ": failed")
                raise
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

class JSSDoc(OffboardTool):

    def __init__(self, jss_id, incorrect_barcode=None, incorrect_asset=None, incorrect_serial=None):
        super(JSSDoc, self).__init__()
        self.jss_id = jss_id
        self.home = os.path.expanduser("~")
        self.blade_runner_dir = "blade-runner-data/"
        self.abs_dir = self.home + '/Desktop/' + self.blade_runner_dir
        self.name_label = self.prev_computer_name(jss_id)
        old_computer_name = self.get_tugboat_fields(self.jss_id)['general']['computer_name']
        self.old_computer_name = str(re.sub(u'(\u2019|\u2018)', '', old_computer_name))
        self.barcode = self.get_tugboat_fields(jss_id)['general']['barcode_1']
        self.asset = self.get_tugboat_fields(jss_id)['general']['asset_tag']
        self.drive_capacity = str(self.return_jss_hardware_inventory(self.jss_id)['storage'][0]['drive_capacity_mb'])
        # self.lbase = self.old_computer_name
        self.lbase = self.asset + "_yellow_asset_tag"
        self.abs_lbase = self.abs_dir + self.lbase
        self.abs_html = self.abs_lbase + ".html"
        self.abs_pdf = self.abs_lbase + ".pdf"

        self.incorrect_barcode = incorrect_barcode
        self.incorrect_asset = incorrect_asset
        self.incorrect_serial = incorrect_serial

    def create_rtf(self):
        '''Creates an .rtf file'''
        self.ext = ".rtf"
        hardware_list_main = self.return_jss_hardware_inventory(self.jss_id)
        hardware_list_storage = hardware_list_main['storage'][0]
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
        general_list_main = self.return_jss_general_inventory(self.jss_id)
        # Check if Managed
        remote_mangement_list = general_list_main['remote_management']
        managed = str(remote_mangement_list['managed'])
        # Get the computer name
        old_computer_name = general_list_main['name']
        # Grab the Serial Number
        serial_number = general_list_main["serial_number"]

        file_text = r"""{\rtf1\ansi\ansicpg1252\cocoartf1504\cocoasubrtf830
{\fonttbl\f0\froman\fcharset0 Times-Roman;}
{\colortbl;\red255\green255\blue255;\red255\green0\blue0;\red255\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\margl1440\margr1440\vieww23200\viewh13720\viewkind0
\deftab720
\pard\pardeftab720\sl560\partightenfactor0

\f0\b\fs48 \cf2 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 Old Name:\'a0
\b0 """ + self.name_label + r"""\
\pard\pardeftab720\sl560\sa480\partightenfactor0

\b \cf2 JSS ID:\'a0
\b0 """ + self.jss_id + r"""\

\b Managed:\'a0
\b0 """ + managed + r"""\

\b Serial Number:\'a0
\b0 """ + serial_number + r"""\

\b Model:\'a0
\b0 """ + computer_model + r"""\

\b SSD:\'a0
\b0 """ + has_SSD + r"""\

\b RAM:\'a0
\b0 """ + ram_total + r"""\

\b The fields below are the previous JSS fields that were incorrect.
\b0 \'a0
\b They should be reviewed further to fix any inconsistencies in the JSS.
\b0 \

\b Previous barcode: \cf3 """ + self.incorrect_barcode + r"""\cf2 
\b0 \

\b Previous asset tag: \cf3 """ + self.incorrect_asset + r"""\cf2 
\b0 \
\pard\pardeftab720\sl560\sa240\partightenfactor0

\b \cf2 Previous serial number: \cf3 """ + self.incorrect_serial + r"""\cf2 
\b0\fs24 \
}"""

        try:
            os.makedirs(self.abs_dir)
        except OSError as e:
            if e.errno != 17:
                raise

        with open(self.file, "w+") as f:
            f.write(file_text)

    def create_html(self):
        '''Creates an .html file'''
        self.ext = '.html'
        hardware_list_main = self.return_jss_hardware_inventory(self.jss_id)
        hardware_list_storage = hardware_list_main['storage'][0]
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
        print("TOATL RAM: " + ram_total)
        # Grabs the Model of Computer
        computer_model = hardware_list_main["model"]
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # General Tab requests
        # Builds overall list
        general_list_main = self.return_jss_general_inventory(self.jss_id)
        # Check if Managed
        remote_mangement_list = general_list_main['remote_management']
        managed = str(remote_mangement_list['managed'])
        # Get the computer name
        old_computer_name = general_list_main['name']
        # Grab the Serial Number
        serial_number = general_list_main["serial_number"]

        try:
            os.makedirs(self.abs_dir)
        except OSError as e:
            if e.errno != 17:
                raise

        if self.incorrect_barcode is not None or self.incorrect_asset is not None or self.incorrect_serial is not None:
            review_content = """<b>These are the previous incorrect JSS fields. They should be reviewed to fix </b>
    <b>any JSS inconsistencies.</b>
    <p>
    <b>Previous barcode: </b> <font color="red">""" + self.incorrect_barcode + """</font>
    <p>
    <b>Previous asset tag: </b> <font color="red">""" + self.incorrect_asset + """</font>
    <p>
    <b>Previous serial number: </b> <font color="red">""" + self.incorrect_serial + """</font>
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
    <b>New Name: </b> """ + self.old_computer_name + """
    <p>
    <b>Previous Name: </b> """ + self.name_label + """
    <p>
    <b>Barcode: </b> """ + self.barcode + """
    <p>
    <b>Asset: </b> """ + self.asset + """
    <p>
    <b>JSS ID: </b> """ + self.jss_id + """    <b>Managed: </b> """ + managed + """
    <p>
    <b>Serial Number: </b> """ + serial_number + """
    <p>
    <b>Model: </b> """ + computer_model + """
    <p>
    <b>SSD: </b> """ + has_SSD + """    <b>RAM: </b> """ + ram_total + """
    <p>
    <b>Drive Capacity: </b> """ + self.drive_capacity + """ MB
    <p>
    """ + review_content + """
  </body>
</html>"""

        with open(self.abs_html, "w+") as f:
            f.write(file_content)

    def open_html(self):
        logger.info(func_name() + ": activated")
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
        logger.info(func_name() + ": activated")

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
        logger.info(func_name() + ": activated")

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
            logger.info(func_name() + ": failed")


def func_name():
    return str(sys._getframe().f_back.f_code.co_name) + "()"

# if __name__ == '__main__':
#     main()





