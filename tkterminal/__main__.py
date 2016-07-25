import Tkinter as tk
import ttk as ttk
from serialconnection import *
from Queue import *
from settings import *


class _Control(tk.Frame):
    def __init__(self, window, settings, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, window, *args, **kwargs)
        self.settings = settings
        self._serial_connection = serial_connection

        self.connection_button = ttk.Button(self, text='Open', command=self._connection_button_open_)
        self.connection_button.grid(row=0, column=1, padx=25, pady=(25, 0))
        self.settings_button = ttk.Button(self, text='Settings', command=self._open_settings_window_)
        self.settings_button.grid(row=0, column=2, padx=25, pady=(25, 0))

    def _connection_button_open_(self):
        self._serial_connection.open(port=self.settings.get('port'), baudrate=self.settings.get('baudrate'),
                                    parity=self.settings.get('parity'), timeout=10)

    def _connection_button_close_(self):
        self._serial_connection.close()

    def _open_settings_window_(self):
        self.settings.open()

    def update(self, connection_state):
        if connection_state is True:
            self.connection_button.config(text='Close', command=self._connection_button_close_)
        else:
            self.connection_button.config(text='Open', command=self._connection_button_open_)


class _Terminal(tk.Frame):
    def __init__(self, window, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, window, *args, **kwargs)
        self._serial_connection = serial_connection

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.terminal_text = tk.Text(self, relief=tk.SUNKEN, borderwidth=3)
        self.terminal_text.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W, padx=25, pady=25)

        self.terminal_entry = ttk.Entry(self)
        self.terminal_entry.grid(row=1, column=0, sticky=tk.E + tk.W, padx=25, pady=(0, 25))
        self.send_button = ttk.Button(self, text='Send', command=self._send_button_clicked_)
        self.send_button.grid(row=1, column=1, sticky=tk.E, padx=25, pady=(0, 25))

    def _send_button_clicked_(self):
        self._serial_connection.write(self.terminal_entry.get())

    def insert(self, data):
        self.terminal_text.insert(tk.END, data)


class GUI:
    def __init__(self, window, serial_connection):
        self._window = window
        self.serial_connection = serial_connection
        self.connection_state = False
        self.queue = Queue()
        self.serial_connection.subscribe(self._received_data_, self._connection_state_)

        settings_window = tk.Toplevel(window)
        settings_window.state('withdrawn')
        self.settings = Settings(settings_window, self._settings_changed)

        self.control_frame = _Control(window, self.settings, serial_connection)
        self.control_frame.pack(fill=tk.X)

        self.terminal_frame = _Terminal(window, serial_connection)
        self.terminal_frame.pack(fill=tk.BOTH, expand=True)

        self._periodic_call_()

    def _periodic_call_(self):
        if self.queue.empty() is False:
            self._update_text_terminal_(self.queue.get(0))
        self.control_frame.update(self.connection_state)
        self._window.after(10, self._periodic_call_)

    def _received_data_(self, data):
        self.queue.put_nowait(data)

    def _update_text_terminal_(self, data):
        self.terminal_frame.insert(data)

    def _connection_state_(self, state):
        self.connection_state = state

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

    root = tk.Tk()
    gui = GUI(root, serial_connection)

    root.mainloop()


if __name__ == "__main__":
    main()
