class Controller(object):
    def set_to_middle(self, window):
        # Updates window info to current window state
        window.update_idletasks()

        # Gets computer screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Sets window position
        # window.geometry('+%d+%d' % (screen_width / 2 - window.winfo_width(), screen_height / 4))
        window.geometry('+{}+{}'.format(screen_width / 2 - window.winfo_width()/2, screen_height / 4))
