
import xml.etree.cElementTree as ET
import os
import re
from jss_server import JssServer
import plistlib
from computer import Computer
from pprint import pformat, pprint



blade_runner_dir = os.path.dirname(os.path.abspath(__file__))
jss_server_plist = os.path.join(blade_runner_dir, "private/test_jss_server_config.plist")
jss_server_data = plistlib.readPlist(jss_server_plist)
jss_server = JssServer(**jss_server_data)
computer = Computer()
# jss_server.enroll_computer()
jss_id = jss_server.match(computer.get_serial())
pprint(jss_server.get_offboard_fields(jss_id))
jss_server.push_xml_fields(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_xml.xml"), jss_id)
