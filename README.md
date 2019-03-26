Blade-Runner
===========

Blade-Runner is a Python application that manages Mac computer systems through
API calls to a JAMF server. It has the ability to manage, off-board, update, and delete
JAMF records for a given computer, auto-generate documents populated
with data from the JAMF server, secure erase all internal disks, and notify Slack
channels of Blade-Runner's progress.

# Capabilities

### JAMF
* Manage/unmanage computer.
* Off-board computer.
* Update computer record.
* Delete computer record.

### Erase
* Secure erase all internal disks.

### Auto-Generate Documents
* Create a document populated with JAMF data for a given computer.

### Auto-Print Documents
* Print auto-generated documents to the default printer.

### Slack
* Send Slack notifications on Blade-Runner's progress. Channel, URL, and
message are configurable.
* "Reminder of completion" daemon that sends Slack notifications on a given 
time interval after Blade-Runner has finished.

