import Tkinter as tk
import ttk as ttk
from serialconnection import *
from Queue import *
from settings import *


class _Control(tk.Frame):
    def __init__(self, parent, settings, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._settings = settings
        self._serial_connection = serial_connection
        self._connection_button_open_text = ', '.join(
            (' '.join((settings.get('port'), settings.get('baudrate'), 'bps')),
             settings.get('bytesize') + settings.get('parity') + settings.get(
                 'stopbits')))

        self._connection_button_closed_text = 'Disconnected - click to connect'

        self.grid_columnconfigure(0, weight=1)

        self._connection_button_text = tk.StringVar(value=self._connection_button_closed_text)
        self.connection_button = ttk.Button(self, textvar=self._connection_button_text,
                                            command=self._connection_button_open_)
        self.connection_button.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky=tk.W + tk.E)
        self.settings_button = ttk.Button(self, text='Settings', command=self._open_settings_window_)
        self.settings_button.grid(row=0, column=1, padx=(5, 5), pady=(5, 0))
        self.settings_button = ttk.Button(self, text='Exit', command=self._exit)
        self.settings_button.grid(row=0, column=2, padx=(5, 5), pady=(5, 0))

    def _connection_button_open_(self):
        self._serial_connection.open(port=self._settings.get('port'), baudrate=self._settings.get('baudrate'),
                                     parity=self._settings.get('parity'), bytesize=self._settings.get('bytesize'),
                                     stopbits=self._settings.get('stopbits'), timeout=10)

    def _connection_button_close_(self):
        self._serial_connection.close()

    def _open_settings_window_(self):
        self._settings.open(self._parent)

    def _exit(self):
        try:
            self._serial_connection.close()
        except Exception as e:
            pass
        self._parent.destroy()

    def update(self, connection_state):
        if connection_state is True:
            self._connection_button_text.set(self._connection_button_open_text)
            self.connection_button.config(command=self._connection_button_close_)
        else:
            self._connection_button_text.set(self._connection_button_closed_text)
            self.connection_button.config(command=self._connection_button_open_)


class _TerminalReceive(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._terminal_text = tk.Text(self, relief=tk.SUNKEN, borderwidth=3)
        self._terminal_text.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W, padx=(5, 5), pady=(5, 5))

    def insert(self, data):
        self._terminal_text.insert(tk.END, data)


class _TerminalSend(tk.Frame):
    def __init__(self, parent, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._serial_connection = serial_connection

        self.grid_columnconfigure(0, weight=1)
        self._terminal_entry = ttk.Entry(self)
        self._terminal_entry.grid(row=1, column=0, sticky=tk.E + tk.W, padx=(5, 5), pady=(0, 5))
        self._send_button = ttk.Button(self, text='Send', command=self._send_button_clicked_)
        self._send_button.grid(row=1, column=1, sticky=tk.E, padx=(0, 5), pady=(0, 5))

    def _send_button_clicked_(self):
        self._serial_connection.write(self._terminal_entry.get())


class MainGui:
    def __init__(self, parent, serial_connection):
        self._parent = parent
        self.serial_connection = serial_connection
        self.connection_state = False
        self.queue = Queue()
        self.serial_connection.subscribe(self._received_data_, self._connection_state_)

        self._parent.wm_title('TkTerminal')

        settings_window = tk.Toplevel(self._parent)
        settings_window.state('withdrawn')
        self.settings = Settings(settings_window, self._settings_changed)

        self.control_frame = _Control(self._parent, self.settings, serial_connection)
        self.control_frame.pack(fill=tk.X, expand=False)

        self.terminal_receive_frame = _TerminalReceive(self._parent)
        self.terminal_receive_frame.pack(fill=tk.BOTH, expand=True)

        self.terminal_send_frame = _TerminalSend(self._parent, serial_connection)
        self.terminal_send_frame.pack(fill=tk.X, expand=False)

        self._periodic_call_()

    def _periodic_call_(self):
        if self.queue.empty() is False:
            self._update_text_terminal_(self.queue.get(0))
        self.control_frame.update(self.connection_state)
        self._parent.after(100, self._periodic_call_)

    def _received_data_(self, data):
        self.queue.put_nowait(data)

    def _update_text_terminal_(self, data):
        self.terminal_receive_frame.insert(data)

    def _connection_state_(self, state):
        self.connection_state = state

    def _settings_changed(self, settings):
        if self.connection_state is True:
            self.serial_connection.close()
        self.serial_connection.open(port=self.settings.get('port'), baudrate=self.settings.get('baudrate'),
                                    parity=self.settings.get('parity'), bytesize=self.settings.get('bytesize'),
                                    stopbits=self.settings.get('stopbits'), timeout=10)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    serial_connection = SerialConnection()

    root = tk.Tk()
    gui = MainGui(root, serial_connection)

    root.mainloop()


if __name__ == "__main__":
    main()
