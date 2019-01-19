class Controller(object):
    def set_to_middle(self, window):
        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Updates window info to current window state
        window.update_idletasks()

        # Sets window position
        window.geometry('+%d+%d' % (screen_width / 2 - window.winfo_width() / 2, screen_height / 4))