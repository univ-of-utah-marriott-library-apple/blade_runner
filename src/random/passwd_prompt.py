from Tkinter import *
import pexpect
import tkSimpleDialog


def sudo_process(cmd):
    root = Tk()
    root.withdraw()

    try:
        child = pexpect.spawn('bash', cmd)

        exit_condition = False
        while not exit_condition:
            result = child.expect(['Password:', 'attempts', pexpect.EOF, pexpect.TIMEOUT, 'SECURE ERASE INTERNALS'])
            if result == 0:
                password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=root)
                child.sendline(password)
            elif result == 1:
                msg = "Could not execute command. Password was incorrect."
                return Results(False, msg)
            elif result == 2:
                msg = "Reached end of output. Process may not have been executed."
                return Results(False, msg)
            elif result == 3:
                msg = "Password prompt timed out."
                return Results(False, msg)
            elif result == 4:
                for line in child:
                    print(line.strip())
                if "0" not in line:
                    return Results(False, "secure_erase_internals.py returned a non-zero exit code")
                msg = "Process was successful."
                return Results(True, msg)
            else:
                msg = "Unknown error occurred."
                return Results(False, msg)
    except Exception as e:
        msg = "Unknown error.".format(e)
        return Results(False, msg)


class Results(object):

    def __init__(self, success, msg):
        self.success = success

        self.msg = msg


if __name__ == "__main__":
    cmd = ['-c', '/usr/bin/sudo touch /tmp/hello']
    sudo_process(cmd)