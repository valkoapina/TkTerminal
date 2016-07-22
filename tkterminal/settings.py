import Tkinter as tk
import ttk as ttk
import serial.tools.list_ports
import serial.serialutil


class _PortSettingsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent

        self.port_list = ttk.Combobox(self, values=self.get_port_list())
        self.port_list.grid(row=0, column=0, padx=25, pady=(5, 0))
        self.port_list.current(0)
        self.port_list.state(statespec=('readonly',))

        self.baudrate_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.BAUDRATES)
        self.baudrate_list.grid(row=1, column=0, padx=25)
        self.baudrate_list.current(0)
        self.baudrate_list.state(statespec=('readonly',))

        self.parity_list = ttk.Combobox(self, values=self._get_parity_names())
        self.parity_list.grid(row=2, column=0, padx=25)
        self.parity_list.current(0)
        self.parity_list.state(statespec=('readonly',))

        self.bytesize_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.BYTESIZES)
        self.bytesize_list.grid(row=3, column=0, padx=25)
        self.bytesize_list.current(len(self.bytesize_list['values']) - 1)
        self.bytesize_list.state(statespec=('readonly',))

        self.stopbits_list = ttk.Combobox(self, values=serial.serialutil.SerialBase.STOPBITS)
        self.stopbits_list.grid(row=4, column=0, padx=25, pady=(0, 5))
        self.stopbits_list.current(0)
        self.stopbits_list.state(statespec=('readonly',))

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


class _ConclusionFrame(tk.Frame):
    def __init__(self, parent, settings_saved_callback, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._settings_saved_callback = settings_saved_callback

        self._cancel_button = ttk.Button(self, text='Cancel', command=self._cancel_button_pressed)
        self._cancel_button.grid(row=0, column=1, padx=25, pady=(25, 0))
        self._save_button = ttk.Button(self, text='Save', command=self._save_button_pressed)
        self._save_button.grid(row=0, column=2, padx=25, pady=(25, 0))

    def _cancel_button_pressed(self):
        self._parent.state('withdrawn')

    def _save_button_pressed(self):
        self._parent.state('withdrawn')
        self._settings_saved_callback()


class Settings:
    def __init__(self, parent, settings_changed_callback, *args, **kwargs):
        self._parent = parent
        self._settings_changed_callback = settings_changed_callback
        self.settings = dict(port_settings={})

        self._port_settings_frame = _PortSettingsFrame(parent, relief=tk.SOLID, borderwidth=1)
        self._port_settings_frame.pack(fill=tk.Y)
        self.conclusion_frame = _ConclusionFrame(parent, self._settings_saved)
        self.conclusion_frame.pack(fill=tk.BOTH)

        self._update_settings()

    def _update_settings(self):
        self.settings['port_settings']['port'] = self._port_settings_frame.port_list.get()
        self.settings['port_settings']['baudrate'] = self._port_settings_frame.baudrate_list.get()
        self.settings['port_settings']['parity'] = self._get_parity_value(
            self._port_settings_frame.parity_list.get())
        self.settings['port_settings']['bytesize'] = self._port_settings_frame.bytesize_list.get()
        self.settings['port_settings']['stopbits'] = self._port_settings_frame.stopbits_list.get()

    def open(self):
        self._port_settings_frame.port_list['values'] = self._port_settings_frame.get_port_list()
        self._parent.lift()
        self._parent.state('normal')

    def close(self):
        pass

    def _check_settings(self, settings, setting):
        retval = None
        for key, value in settings.iteritems():
            if isinstance(value, dict):
                retval = self._check_settings(value, setting)
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
