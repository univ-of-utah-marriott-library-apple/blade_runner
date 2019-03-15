from Tkinter import *
import subprocess
import pexpect
import tkSimpleDialog


class ProcessWindow(Toplevel):

    def __init__(self, cmd, master):
        Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self._close_btn_clicked)
        self.title("Secure Erase Internals Output")
        self.frame = Frame(self, width=100, height=100)
        self.frame.pack(fill=None, expand=False)
        self.frame.grid_propagate(False)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.text = Text(self.frame)
        self.scrollbar = Scrollbar(self.frame, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollbar.set
        self.text.pack()
        self.text.insert(END, "Waiting for authentication...")
        self.after(1000, lambda: self.sudo_process(cmd, self.text))

    def sudo_process(self, cmd, text):
        root = Tk()
        root.withdraw()

        try:
            child = pexpect.spawn('bash', cmd)

            while True:
                result = child.expect(['SECURE ERASE INTERNALS', 'attempts', pexpect.EOF, pexpect.TIMEOUT, 'Password:', "Started"])
                print(result)
                if result == 4:
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
                elif result == 0:
                    self.normal_print(child, text)
                elif result == 5:
                    text.insert(END, "\n " + child.after + " " + child.readline())
                    self.in_place_print(child, text)
                    line = self.normal_print(child, text)
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

    def _close_btn_clicked(self):
        self.destroy()

    def normal_print(self, child, text):
        for line in child:
            if "SECURE ERASING" in line: break
            if line != "":
                line = line.strip()
                text.insert(END, line + "\n")
                text.update()
                text.see("end")
        return line

    def in_place_print(self, child, text):
        while True:
            result = child.expect(["\[", pexpect.EOF, "Finished", "Started"])
            if result == 0:
                if "Started" not in child.before and "K" not in child.before:
                    line = "[ {}".format(child.before)
                    pos = text.index("end-1c linestart")
                    text.delete(pos, END)
                    text.insert(END, "\n")
                    text.insert(END, line.strip())
                    text.update()
                    text.see("end")
            elif result == 1:
                break
            elif result == 2:
                print("\n " + child.after + " " + child.readline().strip())
                break
            elif result == 3:
                text.insert(END, child.after + " " + child.readline().strip())
            else:
                break




class Results(object):

    def __init__(self, success, msg):
        self.success = success
        self.msg = msg


if __name__ == "__main__":
    master = Tk()
    master.withdraw()
    cmd = ['-c', '/usr/bin/sudo python secure_erase_internals.py; echo "Return code: $?"']

    window = ProcessWindow(cmd, master)
    master.wait_window(window)