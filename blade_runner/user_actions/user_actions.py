import xml_updater


def modify_items(self, data):
    """User defined implementation for JssDoc in jss_doc.py. Meant to allow user to modify the data tuples that are
    used to autogenerate the document.

    The standard data tuples are the following:

        * Name
        * Barcode 1
        * Barcode 2
        * Asset Tag
        * JAMF ID
        * Serial Number
        * Model
        * SSD
        * RAM
        * Storage

    Examples:
        An implementation to add some custom data tuples might look like this:

            def modify_items(self, data):
                # Getting an extension attribute by its name from the server.
                estimated_age = self.jss_server.get_extension_attribute(self.computer.jss_id, name="Estimated Age")

                # Getting an extension attribute by its ID from the server.
                prev_name = self.jss_server.get_extension_attribute(self.computer.jss_id, id="46")

                items.insert(1, ("Estimated Age", estimated_age))
                items.insert(2, ("Previous Name", prev_name))

        An implementation to remove the Name tuple would look like this:

            def modify_items(self, data):
                # Remove the Name tuple from the list.
                items.pop(0)

    Args:
        self: JssDoc's self.
        data (tuple list): Data to be included in document.

    Returns:
        void
    """
    prev_name = self.jss_server.get_extension_attribute(self.computer.jss_id, name="Previous Computer Names")
    data.insert(1, ("Prev Name", prev_name))


def update_offboard_config(self):
    """User defines implementation. Meant to update the offboard config with extra information before sending it to
    JAMF Pro.

    At this point in Blade Runner's progress, the offboard config is stored as an XML string, so the implementation
    of this function will need to be able to update XML strings.

    Example:
        Given an offboard config like this:

            <computer>
                <general>
                    <name></name>
                    <remote_management>
                        <managed>false</managed>
                    </remote_management>
                </general>
            </computer>

        an implementation to always change the name to the serial number would look like this:

            def update_offboard_config(self):
                import xml.etree.cElementTree as ET

                # Get the serial number
                serial_number = self._computer.serial_number

                # Parse the XML string into an XML tree and get the root.
                xml_root = ET.fromstring(self._offboard_config)

                # Find the "name" tag in "general" and replace its value with the serial number.
                for general_element in xml_root.findall("./general"):
                    name_element = general_element.find('name')
                    name_element.text = serial_number

                # Save the new XML string.
                self._offboard_config = ET.tostring(xml_root)

    Args:
        self: MainController's self.

    Returns:
        void
    """
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Append the computer name with the serial number.
    self._offboard_config = xml_updater.append_name(self._computer.get_serial(), self._offboard_config)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Add a timestamp to the additional notes attribute.
    self._offboard_config = xml_updater.timestamp_note(self._offboard_config)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Set the previous computer name extension attribute.
    self._offboard_config = xml_updater.set_previous_computer_name(self._computer.jss_name, self._offboard_config)


def update_slack_message(self, message):
    """User defines implementation. Updates the Slack message before it is sent. Must return the message.

    Example:
        Appending the computer's serial number to the message:

            def update_slack_message(self, message):
                message += str(self._computer.serial_number)
                return message

    Args:
        self: MainController's self.
        message (str): Message to send to Slack.

    Returns:
        message
    """
    message += " Serial: {}".format(self._computer.serial_number)
    return message











