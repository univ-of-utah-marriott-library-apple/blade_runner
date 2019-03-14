from Tkinter import *
import pexpect
import tkSimpleDialog


def passw():
    root = Tk()
    root.withdraw()
    password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=root)
    # root.mainloop()
    if not password:
        print("User canceled operation.")
        return

    try:
        child = pexpect.spawn('bash', ['-c', '/usr/bin/sudo touch /tmp/hello'])

        exit_condition = False
        while not exit_condition:
            result = child.expect(['Password:', 'attempts', pexpect.EOF, pexpect.TIMEOUT])
            if result == 0:
                password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=root)
                child.sendline(password)
            elif result == 1:
                exit_condition = True
                print("Could not execute command. Password was incorrect.")
            elif result == 2:
                exit_condition = True
            elif result == 3:
                exit_condition = True
                print("Password prompt timed out.")
            else:
                exit_condition = True
                print("Unknown error occurred.")
    except Exception as e:
        print("Unknown error.".format(e))


if __name__ == "__main__":
    passw()