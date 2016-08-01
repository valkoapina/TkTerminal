import Tkinter as tk
import ttk as ttk
from serialconnection import *
from Queue import *
from settings import *
from Tkdnd import *


class _Control(tk.Frame):
    def __init__(self, parent, settings, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._settings = settings
        self._serial_connection = serial_connection

        self.grid_columnconfigure(0, weight=1)

        self._connection_button_text = tk.StringVar(
            value=self._create_connection_button_text(self._serial_connection.is_open()))
        self.connection_button = ttk.Button(self, textvar=self._connection_button_text,
                                            command=self._connection_button_open_)
        self.connection_button.grid(row=0, column=0, padx=(5, 5), pady=(5, 0), sticky=tk.W + tk.E)
        self.settings_button = ttk.Button(self, text='Settings', command=self._open_settings_window_)
        self.settings_button.grid(row=0, column=1, padx=(5, 5), pady=(5, 0))
        self.settings_button = ttk.Button(self, text='Close', command=self._close)
        self.settings_button.grid(row=0, column=2, padx=(5, 5), pady=(5, 0))

        self._update()

    def _connection_button_open_(self):
        self._serial_connection.open(port=self._settings.get('port'), baudrate=self._settings.get('baudrate'),
                                     parity=self._settings.get('parity'), bytesize=self._settings.get('bytesize'),
                                     stopbits=self._settings.get('stopbits'), timeout=1)

    def _connection_button_close_(self):
        self._serial_connection.close()

    def _open_settings_window_(self):
        self._settings.open()

    def _close(self):
        try:
            self._serial_connection.close()
        except Exception as e:
            pass
        self._parent.parent.remove()

    def _update(self):
        connection_state = self._serial_connection.is_open()
        if connection_state is True:
            self.connection_button.config(command=self._connection_button_close_)
        else:
            self.connection_button.config(command=self._connection_button_open_)
        self._connection_button_text.set(self._create_connection_button_text(connection_state))
        self._parent.after(100, self._update)

    def _create_connection_button_text(self, connection_state):
        text = ', '.join(
            (' '.join((self._settings.get('port'), self._settings.get('baudrate'), 'bps')),
             self._settings.get('bytesize') + self._settings.get('parity') + self._settings.get(
                 'stopbits')))
        if connection_state is True:
            text += ' - connected'
        else:
            text += ' - disconnected'
        return text


class _TerminalReceive(tk.Frame):
    def __init__(self, parent, serial_connection, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._serial_connection = serial_connection

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._scrollbar = ttk.Scrollbar(self)
        self._scrollbar.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E, padx=(0, 5), pady=(5, 5))
        self._terminal_text = tk.Text(self, relief=tk.SUNKEN, borderwidth=3)
        self._terminal_text.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=(5, 0), pady=(5, 5))
        self._terminal_text.config(yscrollcommand=self._scrollbar.set)
        self._scrollbar.config(command=self._terminal_text.yview)

        self._poll_received_data()

    def _poll_received_data(self):
        if self._serial_connection.is_open() is True:
            self._terminal_text.insert(tk.END, self._serial_connection.read())
        self._parent.after(100, self._poll_received_data)

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


class _ConnectionTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.serial_connection = create_serial_connection()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.settings = Settings(self, self._settings_changed)

        self.control_frame = _Control(self, self.settings, self.serial_connection)
        self.control_frame.grid(row=0, column=0, sticky=tk.W + tk.E)

        self.terminal_receive_frame = _TerminalReceive(self, self.serial_connection)
        self.terminal_receive_frame.grid(row=1, column=0, sticky=tk.N + tk.S + tk.W + tk.E)

        self.terminal_send_frame = _TerminalSend(self, self.serial_connection)
        self.terminal_send_frame.grid(row=2, column=0, sticky=tk.W + tk.E)

    def _settings_changed(self, settings):
        self.serial_connection.set_line_ending(self.settings.get('append'))
        if self.serial_connection.is_open() is True:
            self.serial_connection.close()
        self.serial_connection.open(port=self.settings.get('port'), baudrate=self.settings.get('baudrate'),
                                    parity=self.settings.get('parity'), bytesize=self.settings.get('bytesize'),
                                    stopbits=self.settings.get('stopbits'), timeout=1)


class _ConnectionNotebook(object, ttk.Notebook):
    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        self.bind_all("<<NotebookTabChanged>>", self._tab_changed_event)
        self.bind_all("<Double-Button-1>", self._mouse1_event)
        super(_ConnectionNotebook, self).add(ttk.Frame(self), text='+')
        self._new_tab_index = self.index('current')

    def add(self, event):
        tab = _ConnectionTab(self)
        super(_ConnectionNotebook, self).insert(event.widget.index('end') - 1, tab, text='New')
        self._new_tab_index = event.widget.index('current')
        self.select(self.index('end') - 2)

    def remove(self):
        current_index = self.index('current')
        self._new_tab_index -= 1
        if current_index > 0:
            self.forget(current_index)
            self.select(current_index - 1)
        else:
            self.select(current_index + 1)
            self.forget(current_index)

    def _tab_changed_event(self, event):
        if event.widget.index('current') == self._new_tab_index:
            self.add(event)

    def _mouse1_event(self, event):
        if isinstance(event.widget, _ConnectionNotebook):
            print(event.widget.index('current'))


class MainGui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.wm_title('TkTerminal')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.connections = _ConnectionNotebook(self)
        self.connections.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E)


def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    gui = MainGui()

    gui.mainloop()


if __name__ == "__main__":
    main()
