import xml.etree.cElementTree as ET


def append_xml_name(string, xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for general_element in root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = name_element.text + string

    tree.write(xml_file)


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
    append_xml_name("johnny", xml_file)
    update_managed_status("false", xml_file)
    update_inventory_status("Salvage", xml_file)