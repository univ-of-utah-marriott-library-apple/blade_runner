import xml.etree.cElementTree as ET
import datetime


def xml_file_append_name(string, xml_file):
    xml_tree = ET.parse(xml_file)
    xml_root = xml_tree.getroot()

    for general_element in xml_root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = name_element.text + string

    return ET.tostring(xml_root)


def append_name(string, xml_str):
    xml_root = ET.fromstring(xml_str)

    for general_element in xml_root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = name_element.text + string

    return ET.tostring(xml_root)


def timestamp_note(xml_str, append=True):
    d = datetime.datetime.now().strftime("%Y.%m.%d_%H:%M:%S")

    if append:
        return append_additional_note(d, xml_str)

    return set_additional_note(d, xml_str)


def append_additional_note(string, xml_str):
    xml_root = ET.fromstring(xml_str)

    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:

            if ext_attr.find('name').text == "Additional Item Notes" or ext_attr.find('id').text == "45":
                value_element = ext_attr.find('value')
                value_element.text = value_element.text + string

    return ET.tostring(xml_root)


def set_additional_note(string, xml_str):
    xml_root = ET.fromstring(xml_str)

    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:
            if ext_attr.find('id').text == "45":
                value_element = ext_attr.find('value')
                value_element.text = string

    return ET.tostring(xml_root)


def set_previous_computer_name(string, xml_str):
    xml_root = ET.fromstring(xml_str)

    for ext_attrs in xml_root.findall("./extension_attributes"):
        for ext_attr in ext_attrs:
            if ext_attr.find('id').text == "46":
                value_element = ext_attr.find('value')
                value_element.text = string

    return ET.tostring(xml_root)


def xml_to_string(xml_file):
    xml_tree = ET.parse(xml_file)
    xml_root = xml_tree.getroot()
    return ET.tostring(xml_root)


def update_managed_status(status, xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for remote_management_element in root.findall("./general/remote_management"):
        managed_element = remote_management_element.find("managed")
        managed_element.text = status

    tree.write(xml_file)


def update_inventory_status(status, xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for ext_attr_element in root.findall("./extension_attributes/extension_attribute"):
        element = ext_attr_element.find("name")
        if element.text == "Inventory Status":
            inventory_status_element = ext_attr_element.find("value")
            inventory_status_element.text = status

    tree.write(xml_file)


if __name__ == "__main__":
    xml_file = "scratch.xml"
    xml_file_append_name("johnny", xml_file)
    update_managed_status("false", xml_file)
    update_inventory_status("Salvage", xml_file)