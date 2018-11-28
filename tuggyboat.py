from jss_server import JssServer


class TuggyBoat(object):
    def __init__(self, jss_server):
        pass

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

