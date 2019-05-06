slackify
Slackify is a script designed to notify a user specified channel with a user specified message. It is intended to be used from the command line to enable notification of a finished process.

How to use:
slackify.py "#general" "This is my custom message."

Example:
echo hello; slackify.py "#general" "The echo command finished."
Slackify requires the management_tools module, so it has been included for convenience.