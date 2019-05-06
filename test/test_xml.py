
import xml.etree.cElementTree as ET
import os
import re
from jss_server import JssServer
import plistlib
from computer import Computer
from pprint import pformat, pprint
import json
import xml.dom.minidom


# Set up the server
blade_runner_dir = os.path.dirname(os.path.abspath(__file__))
jss_server_plist = os.path.join(blade_runner_dir, "private/test_jss_server_config.plist")
jss_server_data = plistlib.readPlist(jss_server_plist)
jss_server = JssServer(**jss_server_data)

# Create the computer
computer = Computer()
# jss_server.enroll_computer()

# Get the ID
jss_id = jss_server.match(computer.get_serial())

# pprint(jss_server.get_offboard_fields(jss_id))
# jss_server.push_xml(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_xml.xml"), jss_id)

offboard_fields = jss_server.get_subsets_data(jss_id, "private/offboard_config.xml")
print(jss_server.get_general_data(jss_id)['asset_tag'])

print(jss_server.get_general_data(jss_id))

xml_file = xml.dom.minidom.parse("private/offboard_config.xml") # or xml.dom.minidom.parseString(xml_string)
pretty_xml_as_string = xml_file.toprettyxml()
# print(pretty_xml_as_string)
# ofxml = xml.dom.minidom.parseString(offboard_fields)
# pretty_jamf = ofxml.toprettyxml()
# print(pretty_jamf)
#
# for line in pretty_xml_as_string.splitlines():
#     if line not in pretty_jamf:
#         print(line)


def strip_xml(xml_filea, xml_model_file):
    root1 = ET.fromstring(xml_model_file)
    # tree1 = ET.ElementTree(root1)
    # tree2 = ET.parse(xml_filea)
    # root2 = tree2.getroot()
    #
    # # subsets = []
    # # print(root1.findall("./"))
    # # for subset in root1.findall("./"):
    # #     for val in root1.findall("./" + subset.tag + "/"):
    # #         print(val.tail)
    # #
    # # headers1 = root1.findall("./")
    # # headers2 = root2.findall("./")
    #
    # # for item in root1.iter("general"):
    # #
    # #     print(dir(item))
    # tree2a = ET.parse(xml_filea)
    #
    # print(ET.tostring(root1))
    # for item in tree1.iter():
    #     match = False
    #     for i in tree2.iter():
    #         if item.tag == i.tag:
    #             match = True
    #     if match is False:
    #         list(tree2)
    #
    # print(ET.tostring(root1))


strip_xml("private/offboard_config.xml", offboard_fields)



def get_subsets_data(self, jss_id, xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    subsets = []
    for subset in root.findall("./"):
        subsets.append(subset.tag)
    print(subsets)


