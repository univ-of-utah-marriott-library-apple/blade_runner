Blade Runner
===========


*Blade Runner* is a JAMF Pro based Python application that manages deprecated Mac computer systems. It does so through offboarding, enrolling, and updating JAMF records, as well as secure erasing the computer's internal disks, generating and printing documents with data retreived from JAMF Pro, displaying inconsistencies in JAMF records against user entered data, and sending progress updates through Slack.

![](rsrc/images/selection_scene_wbg.png)

It is configured through plists and XML files, allowing for multiple offboarding configurations, a dynamically updating GUI, Slack integration, and specification of which search terms can be used to locate/update a JAMF Pro record.

For a list of features, see [Features & How They Work](#features-and-how-they-work).

# Contents

* [Download](#download)
* [System Requirements](#system-requirements)
* [Configuration](#configuration)
    * [JAMF Pro Configuration](#jamf-pro-configuration)
    * [Offboard Configuration](#offboard-configuration)
    * [Search Parameters Configuration](#search-parameters-configuration)
    * [Verification Parameters Configuration](#verification-parameters-configuration)
    * [User Defined Actions](#user-defined-actions)
* [Features & How They Work](#features-and-how-they-work)
    * [Offboard](#offboard)
    * [Enroll](#enroll)
    * [Secure Erase](#secure-erase)
        * [Firmware Password Detection](#firmware-password-detection)
        * [Internal Disks Detection & Erasure](#internal-disks-detection-and-erasure)
        * [Secure Erase Verification Tests](#secure-erase-verification-tests)
        * [Internal CoreStorage Detection & Dismantling](#internal-corestorage-detection-and-dismantling)
        * [Secure Erase Error Recovery](#secure-erase-error-recovery)
    * [Slack Notifications](#slack-notifications)
        * [Slack Reminder Daemon](#slack-notifications)   
    * [Auto Document Generation and Printing](#auto-document-generation-and-printing)
        * [Displays Inconsistencies in JAMF Record](#jamf-record-inconsistencies) 
* [Uninstallation](#uninstallation)
* [Contact](#contact)
* [Update History](#update-history)

# Download

The latest release is available for download [here](../../releases). 
Uninstallation instructions are provided [below](#uninstallation). 

# System Requirements

*Blade Runner* requires Python 2.X.X >= Python 2.7.9, and is compatible on macOS 10.9 
(Mavericks) through 10.12 (Sierra). It has not been tested on OSes outside that 
range.

# Configuration

*Blade Runner* is configured through plists and XML files. These configuration
files are used for JAMF Pro access, Slack notifications, and *Blade Runner*. The configuration files
are located in `private` and all must be configured before running *Blade Runner*.

* [JAMF Configuration](#jamf-pro-configuration)
* [Offboard Configuration](#offboard-configuration)
* [Search Parameters Configuration](#search-parameters-configuration)
* [Verification Parameters Configuration](#verification-parameters-configuration)
* [User Defined Actions](#user-defined-actions)

## JAMF Pro Configuration

`jamf_pro.plist` contains the information
needed for *Blade Runner* to run JAMF Pro related tasks. The config contains the 
following keys:

* **username**
  * JAMF Pro login username that will be used to make API requests to JAMF Pro. 
* **password**
  * JAMF Pro login password that will be used to make API requests to the JAMF Pro.
* **jss_url**
  * JAMF Pro url.
* **invite**
  * Invitation code used to enroll a computer into JAMF Pro. 
* **jamf_binary_1**
  * Location of `jamf` binary on computer. This is the primary `jamf` binary
  that will be used to enroll computers.
* **jamf_binary_2**
  * Secondary `jamf` binary location. Intended to be a location on an external
  hard drive, e.g., `/Volumes/my_external_drive/jamf` in the case that the 
  computer being enrolled doesn't have a `jamf` binary.

### Example Config

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>username</key>
	<string>user1234</string>
	<key>password</key>
	<string>secret_pass123</string>
	<key>jss_url</key>
	<string>https://my.jamf.server.domain:portnumber</string>
	<key>invite</key>
	<string>1234567891234567891234567891234567890</string>
	<key>jamf_binary_1</key>
	<string>/usr/local/bin/jamf</string>
	<key>jamf_binary_2</key>
	<string>/Volumes/my_external_drive/jamf</string>
</dict>
</plist>
```

## Offboard Configuration

Offboard configurations can have any name but must be XML files. These configs
contain the information to be sent to JAMF Pro when offboarding. When 
offboarding with *Blade Runner*, an offboard configuration selection will be 
shown to the user. All XML files in `private` will be available for selection.

![](rsrc/images/offboard_scene_drop_down_wbg.png)


**The XML file must represent a valid string for JAMF's XML API calls.** The best
way to check this is to go to `https://my.jamf.server.domain:portnumber/api`,
click on `computers>computers/id>Try it out!`, and look at the available 
data in `XML Response Body`. Your configuration file's tags and structure should
only contain tags that exist in `XML Response Body`.

### Example Configs

* Offboard configuration that only sets management status to false:
```
<computer>
  <general>
    <remote_management>
      <managed>false</managed>
    </remote_management>
  </general>
</computer>
```

* Offboard configuration that sets management status to false and clears all location fields:
```
<computer>
  <general>
    <remote_management>
      <managed>false</managed>
    </remote_management>
  </general>
  <location>
    <username></username>
    <realname></realname>
    <real_name></real_name>
    <email_address></email_address>
    <position></position>
    <phone></phone>
    <phone_number></phone_number>
    <department></department>
    <building></building>
    <room></room>
  </location>
</computer>
```

* Offboard configuration that sets management status to false and updates an extension attribute (extension attributes differ between JAMF servers):
```
<computer>
  <general>
    <remote_management>
      <managed>false</managed>
    </remote_management>
  </general>
  <extension_attributes>
    <extension_attribute>
      <id>12</id>
      <name>Inventory Status</name>
      <type>String</type>
      <value>Storage</value>
    </extension_attribute>
  </extension_attributes>
</computer>
```

## Search Parameters Configuration

`search_params.plist` determines the search parameters that can be used to find a computer record in JAMF Pro. The 
*Blade Runner* GUI will dynamically update according to these search parameters 
by only showing buttons that correspond to the enabled search parameters.

The available search parameters are `serial number`, `barcode 1`, `barcode 2`, and `asset tag`.

![](rsrc/images/offboard_scene_all_wbg.png)

### Example Config

* Config that updates *Blade Runner* GUI to show `barcode 1`, `asset_tag`, and 
  `serial number` buttons and allows the user to search JAMF Pro using those search parameters:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>barcode_1</key>
	<string>True</string>
	<key>barcode_2</key>
	<string>False</string>
	<key>asset_tag</key>
	<string>True</string>
	<key>serial_number</key>
	<string>True</string>
</dict>
</plist>
```

![](rsrc/images/offboard_scene_wbg.png)


## Verification Parameters Configuration

`verify_params.plist` determines which search parameters need to be verified when a match in JAMF Pro is found. Here's a short example scenario:

* User searches for a computer using `barcode 1`:
  * No match found.
    * User then searches for a computer using `asset tag`:
      * Match found.
        * If `barcode 1` and `asset_tag` are enabled in `verify_params.plist`, *Blade Runner* will ask the user to verify/correct the information entered for `barcode 1` and `asset_tag` against JAMF Pro's record.

<img src="rsrc/images/verify_all_wbg.png"  width="800" height="480">

It is generally the case that any keys enabled in [search_params.plist](#search-parameters-configuration)
should also be enabled in `verify_config.plist`.

*Blade Runner*'s GUI will dynamically update according to which verification 
parameters are enabled.

## User Defined Actions

There are areas in *Blade Runner*'s codebase where a custom implementation of a
process may be needed. In such circumstances, a configuration file isn't sufficient
and the code needs to be supplemented.

To facilitate "knowing" where to put this code, `user_actions.py` is provided. It
contains three unimplemented functions that are always called.

### modify_items

`user_actions.py` contains an unimplemented function named `modify_items()`. This functions is called in [jss_doc.py](#auto-document-generation-and-printing).
It appears right before the body of the document is generated. Its purpose is to allow the user to 
modify the data that appears in the document. `modify_items()` takes the 
`JssDoc`'s `self` as the first parameter and a list of tuples as the second 
parameter. `self` provides access to JAMF Pro. Each tuple in the list contains 
the name and value of the data to be added to the document.

The first parameters of the standard data tuples are the following:

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
    
and produce a document like this:

<img src="rsrc/images/jssdoc.png"  width="400" height="517">

#### Remove Example  
An implementation to **remove** the Name tuple would look like this:

```
# user_actions.py

def modify_items(self, items):
    # Remove Name tuple from the list
    items.pop(0)
```

and would result in a document like this:

<img src="rsrc/images/jssdoc_name_removed.png"  width="400" height="517">

#### Add Example:
An implementation to **add** some custom data tuples might look like this:

```
# user_actions.py

def modify_items(self, items):
    # Getting an extension attribute by its name from the server.
    estimated_age = self.jss_server.get_extension_attribute(self.computer.jss_id, name="Estimated Age")
    
    # Getting an extension attribute by its ID from the server.
    prev_name = self.jss_server.get_extension_attribute(self.computer.jss_id, id="46")
    
    items.insert(1, ("Estimated Age", estimated_age))
    items.insert(2, ("Previous Name", prev_name))
```

and would result in a document similar to this:

<img src="rsrc/images/jssdoc_add_data.png"  width="400" height="517">

### update_offboard_config

`user_actions.py` contains an uimplemented function `update_offboard_config()` that is called before *Blade Runner* sends the offboard config to JAMF Pro. Its purpose is to make custom changes to the offboard data before it is sent.

#### Example

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

```
# user_actions.py
import xml.etree.cElementTree as ET

def update_offboard_config(self):
    # Parse the XML string into an XML tree and get the root.
    xml_root = ET.fromstring(self._offboard_config)

    # Find the "name" tag in "general" and replace its value with the serial number.
    for general_element in xml_root.findall("./general"):
        name_element = general_element.find('name')
        name_element.text = self._computer.serial_number

    # Save the new XML string.
    self._offboard_config = ET.tostring(xml_root)
```

### update_slack_message

`user_actions.py` contains an unimplemented function named `update_slack_message().` This function is called right before the Slack message is sent.

An implementation that appends the serial number to the Slack message would look like this:

```
def update_slack_message(self, message):
    message += " Serial: {}".format(self._computer.serial_number)
    return message
```

# Features and How They Work

*Blade Runner* essentially performs 5 tasks:

    1. Offboard
    2. Enroll
    3. Secure Erase
        i. Firmware Password Detection
       ii. Internal Disks Detection & Erasure
      iii. Secure Erase Verification Tests
       iv. Internal CoreStorage Detection & Dismantling
        v. Secure Erase Error Recovery
    4. Auto Document Generation & Printing
    5. Slack Notifications
        i. Slack Reminder Daemon
    
## Offboard

Offboarding is done through API calls made by *Blade Runner* to JAMF Pro.
The user selects an offboarding configuration file and that file is sent to
JAMF Pro as an XML string.

## Enroll

The purpose of enrolling before offboarding is to:

1. create a record for a computer if it doesn't already exist in JAMF Pro.
2. change the managed status of an existing computer from false to true.
This enables modification of the computer record.

Enrolling is done through the `jamf` binary with an invitation code: 

    jamf enroll -invitation 1234567891234567891234567891234567890 -noPolicy -noManage -verbose

The invitation code is set in the [JAMF Pro configuration](#jamf-pro-configuration).

## Secure Erase

The secure erase functionality contains the following features:

    1. Firmware Password Detection.
    2. Internal Disk Detection/Erase
    3. Secure Erase Verification Tests
    4. Internal CoreStorage Detection/Dismantling
    5. Secure Erase Error Recovery
    6. Slack Notifications
    7. Auto Document Generation/Printing.

### Firmware Password Detection

*Blade Runner* uses the `firmwarepasswd` command to check for the existence 
of a firmware password before secure erasing. This is done to ensure that
the firmware password has been removed in the scenario that the computer
will be put in storage or sold to another user.

**NOTE:** `firmwarepasswd` command only exists on macOS 10.10 and above. If 
*Blade Runner* is unable to find `firmwarepasswd`, a pop up will display
asking the user to disable the firmware password before continuing. The user
can then proceed with the secure erase at their own discretion.

### Internal Disks Detection and Erasure

Internal disk detection is done through `diskutil info -plist disk#`.
A plist is returned containing information about the disk. One of the keys
in the plist is `Internal`, denoting the internal status of the disk. The
disks are then erased with a single-pass zero-fill erase using 
`diskutil secureErase 0 disk#`.

### Secure Erase Verification Tests

A series of four tests is performed on every disk that is erased. These tests
use `diskutil` output to determine if a disk was erased successfully.

* `disktutil verifyDisk disk#`
  * Test 1: If output contains "Nonexistent", "unknown", or "damaged", test passes.
* `diskutil info -plist disk#`
  * Test 2: If the value of `Content` key is `''`, test passes.
  * Test 3: If the length of `AllDisks` key value is `1`, test passes.
  * Test 4: If the length of `VolumesFromDisks` key value is `0`, test passes.

If all four tests pass, the disk has been secure erased.

### Internal CoreStorage Detection and Dismantling

Internal CoreStorage detection is done through `diskutil coreStorage info -plist disk#`
and testing for the existence of the `MemberOfCoreStorageLogicalVolumeGroup`
key. If the disk contains this key, its lvgUUID is obtained, and is deleted
with `diskutil cs delete lvgUUID#`.

### Secure Erase Error Recovery

If an error occurs while attempting a secure erase, a series of steps is taken
to recover from and fix the error before attempting another secure erase. The
two commons problems that prevent a secure erase are:

1. Inability to unmount disk
2. Inability to work with a disk that needs to be repaired

In these situations, *Blade Runner* first performs a force unmount with
`diskutil unmountDisk force disk#` before attempting another secure erase. If 
this fails, an attempt is made to repair the disk with `diskutil repairVolume disk#` 
before trying to secure erase a final time.

## Slack Notifications

Slack notifications can be used to indicate the start and end of the process
along with any errors that occur in the process. Currently,
Slack notifications are reliant on `management_tools`, which is an included
dependency.

There is also a Slack reminder daemon that is launched when *Blade Runner* 
finishes offboarding a computer. Only one of these daemons can be launched on a 
computer at a time, and it will send a notification on a daily basis until the 
offboarded computer is turned off or the daemon is killed manually.

## Auto Document Generation and Printing

Auto document generation is done in `jss_doc.py` by the `JssDoc` class. This 
class generates a document by querying JAMF Pro for the following data:

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

and will create a document like this:

<img src="rsrc/images/jssdoc.png"  width="400" height="517">

On the code side of things, these fields are represented by tuples, in which the 
first parameter is the data name and the second parameter is the data value. 
This is important to know if you plan on [adding to](#add-example) or 
[removing from](#remove-example) the data above to customize the document.

### Jamf Record Inconsistencies

In the case that JAMF Pro record inconsistencies exist between user entered data and the 
pre-offboard computer record, those inconsistencies will be added to the document
for the user to review later if they so wish.

The reported inconsistencies are as follows:

    * Previous barcode 1
    * Previous barcode 2
    * Previous asset tag
    * Previous serial

For example, if the entered `barcode 1` differs from JAMF Pro's record, the previous `barcode 1` will be displayed:

<img src="rsrc/images/jssdoc_review.png"  width="400" height="517">

The intent of this is to help track down and correct other mangled/incorrect 
computer records.

# Uninstallation

`raise NotImplementedError`

# Contact

Issues/bugs can be reported [here](../../issues). If you have any questions or 
comments, feel free to [email us](mailto:mlib-its-mac-github@lists.utah.edu).

Thanks!

# Update History

| Date       | Version | Description
|------------|:-------:|------------------------------------------------------|
| TBA        | 1.0.0   | Initial Release                                      





