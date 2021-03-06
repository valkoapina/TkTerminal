import Tkinter as tk
import ttk as ttk
import serial.tools.list_ports
import serial.serialutil


class _PortSettingsFrame(tk.LabelFrame):
    _XPADDING = 5
    _YPADDING = 5

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self.port_list_label = ttk.Label(self, text='Port')
        self.port_list_label.grid(row=0, column=0, sticky=tk.W, padx=(self._XPADDING, 0))
        self.port_list = ttk.Combobox(self, values=self.get_port_list())
        self.port_list.grid(row=0, column=1, padx=(self._XPADDING, self._XPADDING), pady=(self._YPADDING, 0))
        self.port_list.current(0)
        self.port_list.state(statespec=('readonly',))

        self.baudrate_list_label = ttk.Label(self, text='Baud rate')
        self.baudrate_list_label.grid(row=1, column=0, sticky=tk.W, padx=(self._XPADDING, 0))
        self.baudrate_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.BAUDRATES)
        self.baudrate_list.grid(row=1, column=1, padx=(self._XPADDING, self._XPADDING))
        self.baudrate_list.current(0)
        self.baudrate_list.state(statespec=('readonly',))

        self.bytesize_list_label = ttk.Label(self, text='Data bits')
        self.bytesize_list_label.grid(row=2, column=0, sticky=tk.W, padx=(self._XPADDING, 0))
        self.bytesize_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.BYTESIZES)
        self.bytesize_list.grid(row=2, column=1, padx=(self._XPADDING, self._XPADDING))
        self.bytesize_list.current(len(self.bytesize_list['values']) - 1)
        self.bytesize_list.state(statespec=('readonly',))

        self.stopbits_list_label = ttk.Label(self, text='Stop bits')
        self.stopbits_list_label.grid(row=3, column=0, sticky=tk.W, padx=(self._XPADDING, 0))
        self.stopbits_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.STOPBITS)
        self.stopbits_list.grid(row=3, column=1, padx=(self._XPADDING, self._XPADDING))
        self.stopbits_list.current(0)
        self.stopbits_list.state(statespec=('readonly',))

        self.parity_list_label = ttk.Label(self, text='Parity')
        self.parity_list_label.grid(row=4, column=0, sticky=tk.W, padx=(self._XPADDING, 0))
        self.parity_list = ttk.Combobox(self, values=self._get_parity_names())
        self.parity_list.grid(row=4, column=1, padx=(self._XPADDING, self._XPADDING), pady=(0, self._YPADDING))
        self.parity_list.current(0)
        self.parity_list.state(statespec=('readonly',))

    @staticmethod
    def get_port_list():
        port_list = list()
        for port in serial.tools.list_ports.comports():
            port_list.append(port.device)
            port_list.append('loop://')
        return port_list

    @staticmethod
    def _get_parity_names():
        parity_list = list()
        for key, value in serial.serialutil.PARITY_NAMES.iteritems():
            parity_list.append(value)
        return list(reversed(parity_list))


class _TransmitSettingsFrame(tk.LabelFrame):
    _XPADDING = 5
    _YPADDING = 5

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self._selection = tk.IntVar(0)
        self._port_list = ttk.Radiobutton(self, text='Append nothing', variable=self._selection, value=0)
        self._port_list.grid(row=0, column=0, padx=(self._XPADDING, self._XPADDING), pady=(self._YPADDING, 0),
                             sticky=tk.W)
        self._port_list = ttk.Radiobutton(self, text='Append CR', variable=self._selection, value=1)
        self._port_list.grid(row=1, column=0, padx=(self._XPADDING, self._XPADDING), pady=(0, 0), sticky=tk.W)
        self._port_list = ttk.Radiobutton(self, text='Append LF', variable=self._selection, value=2)
        self._port_list.grid(row=2, column=0, padx=(self._XPADDING, self._XPADDING), pady=(0, 0), sticky=tk.W)
        self._port_list = ttk.Radiobutton(self, text='Append CR-LF', variable=self._selection, value=3)
        self._port_list.grid(row=3, column=0, padx=(self._XPADDING, self._XPADDING), pady=(0, 0), sticky=tk.W)
        self._port_list = ttk.Radiobutton(self, text='Append LF-CR', variable=self._selection, value=4)
        self._port_list.grid(row=4, column=0, padx=(self._XPADDING, self._XPADDING), pady=(0, self._YPADDING),
                             sticky=tk.W)

    def get_selection(self):
        retvals = ['', '\r', '\n', '\r\n', '\n\r']
        return retvals[self._selection.get()]


class _ConclusionFrame(tk.Frame):
    _XPADDING = 5
    _YPADDING = 5

    def __init__(self, parent, settings_saved_callback, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._settings_saved_callback = settings_saved_callback

        self._cancel_button = ttk.Button(self, text='Cancel', command=self._cancel_button_pressed)
        self._cancel_button.grid(row=0, column=0, padx=self._XPADDING, pady=(self._YPADDING, 0))
        self._save_button = ttk.Button(self, text='Save', command=self._save_button_pressed)
        self._save_button.grid(row=0, column=1, padx=self._XPADDING, pady=(self._YPADDING, 0))

    def _cancel_button_pressed(self):
        self._close()

    def _save_button_pressed(self):
        self._close()
        self._settings_saved_callback()

    def _close(self):
        self._parent.state('withdrawn')
        self._parent.grab_release()


class Settings(tk.Toplevel):
    def __init__(self, parent, settings_changed_callback, *args, **kwargs):
        tk.Toplevel.__init__(self, parent)
        self._parent = parent
        self._settings_changed_callback = settings_changed_callback
        self.settings = dict(port_settings={}, transmit_settings={})

        self.state('withdrawn')
        self.wm_title('Settings')
        self.resizable(width=False, height=False)
        self.protocol('WM_DELETE_WINDOW', self._on_exit)

        self._port_settings_frame = _PortSettingsFrame(self, text='Port settings', relief=tk.SOLID, borderwidth=1)
        self._port_settings_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self._transmit_settings_frame = _TransmitSettingsFrame(self, text='Transmitted data', relief=tk.SOLID,
                                                               borderwidth=1)
        self._transmit_settings_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self._conclusion_frame = _ConclusionFrame(self, self._settings_saved)
        self._conclusion_frame.grid(row=1, column=1, sticky=tk.E)
        self._update_settings()

    def _update_settings(self):
        self.settings['port_settings']['port'] = self._port_settings_frame.port_list.get()
        self.settings['port_settings']['baudrate'] = self._port_settings_frame.baudrate_list.get()
        self.settings['port_settings']['parity'] = self._get_parity_value(
            self._port_settings_frame.parity_list.get())
        self.settings['port_settings']['bytesize'] = self._port_settings_frame.bytesize_list.get()
        self.settings['port_settings']['stopbits'] = self._port_settings_frame.stopbits_list.get()

        self.settings['transmit_settings']['append'] = self._transmit_settings_frame.get_selection()

    def open(self):
        self._port_settings_frame.port_list['values'] = self._port_settings_frame.get_port_list()
        self.transient(self._parent)
        self.grab_set()
        self.lift()
        self.state('normal')

        # Center window to parent window
        xposition = self._parent.winfo_rootx() + self._parent.winfo_width() / 2 - self.winfo_width() / 2
        yposition = self._parent.winfo_rooty() + self._parent.winfo_height() / 2 - self.winfo_height() / 2
        self.geometry("+%d+%d" % (xposition, yposition))

    def close(self):
        pass

    def _check_settings(self, settings, setting):
        retval = None
        for key, value in settings.iteritems():
            if isinstance(value, dict):
                retval = self._check_settings(value, setting)
                if retval is not None:
                    break
            else:
                if key == setting:
                    retval = value
                    break
        return retval

    def get(self, setting):
        return self._check_settings(self.settings, setting)

    def _settings_saved(self):
        self._update_settings()
        self._settings_changed_callback(self.settings)

    @staticmethod
    def _get_parity_value(parity_name):
        for key, value in serial.serialutil.PARITY_NAMES.iteritems():
            if value == parity_name:
                return key
        return None

    def _on_exit(self):
        self.state('withdrawn')
        self.grab_release()
