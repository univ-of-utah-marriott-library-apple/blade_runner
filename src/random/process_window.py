from Tkinter import *
import subprocess


class ProcessWindow(Toplevel):

    def __init__(self, cmd, master):
        Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self._close_btn_clicked)

        self.txt_frm = Frame(self, width=600, height=600)
        self.txt_frm.pack(fill="both", expand=True)
        # ensure a consistent GUI size
        self.txt_frm.grid_propagate(False)
        # implement stretchability
        self.txt_frm.grid_rowconfigure(0, weight=1)
        self.txt_frm.grid_columnconfigure(0, weight=1)

        self.text = Text(self.txt_frm)
        self.scrollb = Scrollbar(self.txt_frm, command=self.text.yview)
        self.scrollb.grid(row=0, column=1, sticky='nsew')
        self.text['yscrollcommand'] = self.scrollb.set
        self.text.pack()

        self.after(1000, lambda: self.update_text_in_place(cmd, self.text))
        self.mainloop()

    def update_text_in_place(self, cmd, text):
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
        # While the process is running, output the process information onto a single line.
        while self.proc.poll() is None:
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Read a line from the process output.
            line = self.proc.stdout.readline()
            # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
            # Remove the newline character
            line = line.strip()
            text.delete(1.0, END)
            text.insert(END, line)
            text.update()
            text.see("end")

    def _close_btn_clicked(self):
        self.proc.terminate()
        self.destroy()


if __name__ == "__main__":
    master = Tk()
    master.withdraw()
    cmd = ["ping", "www.apple.com"]
    ProcessWindow(cmd, master)