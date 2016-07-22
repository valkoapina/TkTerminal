from Tkinter import *
from ttk import *
from serialconnection import *
from Queue import *
from settings import *


class GUI:
    def __init__(self, master, serial_connection):
        self.master = master
        self.serial_connection = serial_connection
        self.connection_state = False
        self.queue = Queue()
        self.serial_connection.subscribe(self._received_data_, self._connection_state_)

        settings_window_widget = Toplevel(master)
        settings_window_widget.state('withdrawn')
        self.settings = Settings(settings_window_widget, self._settings_changed)

        settings_frame = Frame(master)
        settings_frame.pack(fill=X)
        self.connection_button = Button(settings_frame, text='Open', command=self._connection_button_open_)
        self.connection_button.grid(row=0, column=1, padx=25, pady=(25, 0))
        self.settings_button = Button(settings_frame, text='Settings', command=self._open_settings_window_)
        self.settings_button.grid(row=0, column=2, padx=25, pady=(25, 0))

        terminal_frame = Frame(master)
        terminal_frame.pack(fill=BOTH, expand=True)
        terminal_frame.grid_columnconfigure(0, weight=1)
        terminal_frame.grid_rowconfigure(0, weight=1)
        self.terminal_text = Text(terminal_frame, relief=SUNKEN, borderwidth=3)
        self.terminal_text.grid(row=0, column=0, sticky=N + S + E + W, padx=25, pady=25)

        terminal_entry_frame = Frame(master)
        terminal_entry_frame.pack(fill=X)
        terminal_entry_frame.grid_columnconfigure(0, weight=1)
        self.terminal_entry = Entry(terminal_entry_frame)
        self.terminal_entry.grid(row=0, column=0, sticky=E + W, padx=25, pady=(0, 25))
        self.send_button = Button(terminal_entry_frame, text='Send', command=self._send_button_clicked_)
        self.send_button.grid(row=0, column=1, sticky=E, padx=25, pady=(0, 25))

        self._periodic_call_()

    def _periodic_call_(self):
        if self.queue.empty() is False:
            self._update_text_terminal_(self.queue.get(0))
        if self.connection_state is True:
            self.connection_button.config(text='Close', command=self._connection_button_close_)
        else:
            self.connection_button.config(text='Open', command=self._connection_button_open_)
        self.master.after(10, self._periodic_call_)

    def _send_button_clicked_(self):
        self.serial_connection.write(self.terminal_entry.get())

    def _connection_button_open_(self):
        self.serial_connection.open(port=self.settings.get('port'), baudrate=self.settings.get('baudrate'),
                                    parity=self.settings.get('parity'), timeout=10)

    def _connection_button_close_(self):
        self.serial_connection.close()

    def _received_data_(self, data):
        self.queue.put_nowait(data)

    def _update_text_terminal_(self, data):
        self.terminal_text.insert(END, data)

    def _connection_state_(self, state):
        self.connection_state = state

    def _open_settings_window_(self):
        self.settings.open()

    def _settings_changed(self, settings):
        if self.connection_state is True:
            self.serial_connection.close()
        self.serial_connection.open(port=self.settings.get('port'), baudrate=self.settings.get('baudrate'),
                                    parity=self.settings.get('parity'), timeout=10)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    serial_connection = SerialConnection()

    root = Tk()
    gui = GUI(root, serial_connection)

    root.mainloop()


if __name__ == "__main__":
    main()
