Blade-Runner
===========

Blade-Runner is a Python application that manages Mac computer systems through
API calls to a JAMF server. It has the ability to manage, off-board, update, and delete
JAMF records for a given computer, auto-generate documents populated
with data from the JAMF server, secure erase all internal disks, and notify Slack
channels of Blade-Runner's progress.

# Contents

* [Features](#features) - What can Blade-Runner do?
* [System Requirements](#system-requirements)

# Features

### JAMF Integration
* Manage/unmanage computer.
* Off-board computer.
* Update computer record.
* Delete computer record.

### Secure Erase
* Secure erase all internal disks.

### Auto-Generate Documents
* Create a document populated with JAMF data for a given computer.

### Auto-Print Documents
* Print auto-generated documents to the default printer.

### Slack Integration
* Send Slack notifications on Blade-Runner's progress. Channel, URL, and
message are configurable.
* "Reminder of completion" daemon that sends Slack notifications on a given 
time interval after Blade-Runner has finished.

### Plist/XML Configuration
* JAMF config.
* Slack config.

# System Requirements

Blade-Runner requires Python 2.7.9 or higher, and is compatible on macOS 10.9 
(Mavericks) - 10.12 (Sierra). It has not been tested on OSes outside that 
range.

# Configuration
Blade-Runner is configured through plists and XML files. These configuration
files are used for JAMF, Slack, and Blade-Runner. The configuration files
are located in `blade-runner/private`. All of them must be configured before
running Blade-runner.

### JAMF Configuration
The JAMF configuration plist (`jss_server_config.plist`) contains the following
keys:

* username
  * JAMF login username that will be used to make API calls to the JAMF server. 
* password
  * JAMF login password that will be used to make API calls to the JAMF server.
* jss_url
  * URL of the JAMF server to be queried.
* invite
  * Invitation code used to enroll a computer into the JAMF server. 
* jamf_binary_1
  * Location of `jamf` binary on computer. This is the primary `jamf` binary
  that will be used to enroll computers.
* jamf_binary_2
  * Secondary `jamf` binary location. Intended to be a location on an external
  hard drive in the case that the computer being enrolled doesn't have a `jamf` 
  binary.









