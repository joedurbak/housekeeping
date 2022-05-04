import serial
from time import sleep

from lakeshore.generic_instrument import GenericInstrument, comports, InstrumentException


class ModifiedGenericInstrument(GenericInstrument):
    # vid_pid = (1659, 8963)
    def __init__(self,
                 serial_number=None,
                 com_port=None,
                 baud_rate=9600,
                 data_bits=serial.SEVENBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_ODD,
                 flow_control=False,
                 handshaking=False,
                 timeout=2.0,
                 ip_address=None,
                 tcp_port=7777,
                 connection=None,
                 serial_cmd_termination='\n'
                 ):
        self.serial_cmd_termination = serial_cmd_termination.encode('ascii')
        super(ModifiedGenericInstrument, self).__init__(
            serial_number, com_port, baud_rate, data_bits, stop_bits, parity, flow_control, handshaking, timeout,
            ip_address, tcp_port, connection
        )

    def _usb_command(self, command):
        """Send a command over the serial USB connection"""

        self.device_serial.write(command.encode('ascii') + self.serial_cmd_termination)

    def connect_usb(self, serial_number=None, com_port=None, baud_rate=None, data_bits=None,
                    stop_bits=None, parity=None, timeout=None, handshaking=None, flow_control=None):
        """Establish a serial USB connection"""

        # Scan the ports for devices matching the VID and PID combos of the instrument
        for port in comports():
            if ((port.vid, port.pid) in self.vid_pid) or not self.vid_pid:
                # If the com port argument is passed, check for a match
                if port.device == com_port or com_port is None:
                    # If the serial number argument is passed, check for a match
                    if port.serial_number == serial_number or serial_number is None:
                        # Establish a connection with device using the instrument's serial communications parameters
                        self.device_serial = serial.Serial(port.device,
                                                           baudrate=baud_rate,
                                                           bytesize=data_bits,
                                                           stopbits=stop_bits,
                                                           xonxoff=handshaking,
                                                           timeout=timeout,
                                                           parity=parity,
                                                           rtscts=flow_control)

                        # Send the instrument a line break, wait 100ms, and clear the input buffer so that
                        # any leftover communications from a prior session don't gum up the works
                        self.device_serial.write(self.serial_cmd_termination)
                        sleep(0.1)
                        self.device_serial.reset_input_buffer()

                        break
        else:
            if com_port is None and serial_number is None:
                raise InstrumentException("No serial connections found")

            raise InstrumentException(
                "No serial connections found with a matching COM port and/or matching serial number")
