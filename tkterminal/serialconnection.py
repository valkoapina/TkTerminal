from serial import *
from serial.threaded import *
import serial.tools.list_ports
import traceback


class _Protocol(LineReader):
    def __init__(self, data_received_callback, connection_state_changed_callback):
        self._data_received_callback = data_received_callback
        self._connection_state_changed_callback = connection_state_changed_callback

    def connection_made(self, transport):
        super(_Protocol, self).connection_made(transport)
        sys.stdout.write('port opened\n')
        self._connection_state_changed_callback(True)

    def handle_line(self, data):
        sys.stdout.write('line received: {}\n'.format(repr(data)))

    def data_received(self, data):
        sys.stdout.write('data received: {}\n'.format(repr(data)))
        self._data_received_callback(data)

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        sys.stdout.write('port closed\n')
        self._connection_state_changed_callback(False)


class SerialConnection:
    def __init__(self):
        self._serial_connection = None
        self._data_subscriber = None
        self._connection_state_subscriber = None
        self._reader_thread = None

    @staticmethod
    def get_ports():
        port_list = list()
        for port in serial.tools.list_ports.comports():
            port_list.append(port.device)
            port_list.append('loop://')
        return port_list

    def subscribe(self, data_subscriber, connection_state_subscriber):
        self._data_subscriber = data_subscriber
        self._connection_state_subscriber = connection_state_subscriber

    def open(self, port='loop://', baudrate=9600, parity=PARITY_NONE, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE,
             timeout=10):
        try:
            self._serial_connection = serial.serial_for_url(port, baudrate=baudrate, parity=parity,
                                                            bytesize=int(bytesize), stopbits=int(stopbits),
                                                            timeout=timeout)
            self._reader_thread = ReaderThread(self._serial_connection,
                                               lambda: _Protocol(self._data_subscriber, self._connection_state_subscriber))
            self._reader_thread.start()
            print(self._serial_connection.BAUDRATES)
        except Exception as e:
            self.close()
            return False
        else:
            return True

    def close(self):
        self._reader_thread.stop()
        self._serial_connection.close()

    def write(self, data):
        self._reader_thread.write(data)

    def write_line(self, data):
        self._reader_thread.write_line(data)
