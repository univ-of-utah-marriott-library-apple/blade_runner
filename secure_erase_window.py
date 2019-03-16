from Tkinter import *
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
        try:
            child = pexpect.spawn('bash', cmd, use_poll=True)

            while True:
                result = child.expect(['SECURE ERASE INTERNALS', 'attempts', pexpect.EOF, pexpect.TIMEOUT, 'Password:'])
                print(result)
                if result == 4:
                    self.focus_force()
                    password = tkSimpleDialog.askstring("Password", "Enter admin password:", show='*', parent=self)
                    child.sendline(password)
                elif result == 1:
                    msg = "Could not execute command. Password was incorrect."
                    return Results(False, msg)
                elif result == 2:
                    msg = "Reached end of output. Process may or may not have been executed."
                    return Results(False, msg)
                elif result == 3:
                    msg = "Password prompt timed out."
                    return Results(False, msg)
                elif result == 0:
                    last_line = self.dynamic_print(child, text)
                    if "0" not in last_line:
                        return Results(False, "There was an error.")
                    return Results(True, "Secure erase was successful!")
                else:
                    msg = "Unknown error occurred."
                    return Results(False, msg)
        except Exception as e:
            msg = "Unknown error.".format(e)
            return Results(False, msg)

    def _close_btn_clicked(self):
        self.destroy()

    def dynamic_print(self, child, text):
        prev_result = None
        while child.isalive():
            line = ""
            result = child.expect(["\[[^K][^\]]*\]", "\n", "\[K"])
            if result == 0:
                line = child.after
                print(line)
                pos = text.index("end-1c linestart")
                text.delete(pos, END)
                text.insert(END, "\n")
                text.insert(END, line.strip())
                text.update()
                text.see("end")
            elif result == 1:
                print(child.before)
                if prev_result == 0 or prev_result == 2:
                    text.insert(END, "\n")
                line = child.before
                line = line.strip()
                text.insert(END, line + "\n")
                text.update()
                text.see("end")

            prev_result = result
        return line

    # def in_place_print(self, child, text):
    #     while True:
    #         result = child.expect(["\[", pexpect.EOF, "Finished", "Started"])
    #         if result == 0:
    #             if "Started" not in child.before and "K" not in child.before:
    #                 line = "[ {}".format(child.before)
    #                 pos = text.index("end-1c linestart")
    #                 text.delete(pos, END)
    #                 text.insert(END, "\n")
    #                 text.insert(END, line.strip())
    #                 text.update()
    #                 text.see("end")
    #         elif result == 1:
    #             break
    #         elif result == 2:
    #             print("\n " + child.after + " " + child.readline().strip())
    #             break
    #         elif result == 3:
    #             text.insert(END, child.after + " " + child.readline().strip())
    #         else:
    #             break

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