import serial
import os
from time import sleep
from datetime import date, datetime

from lakeshore.generic_instrument import GenericInstrument, InstrumentException, comports


class Model218(GenericInstrument):
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
                 **kwargs):

        # Call the parent init, then fill in values specific to the 224
        GenericInstrument.__init__(self, serial_number, com_port, baud_rate, data_bits, stop_bits, parity, flow_control,
                                   handshaking, timeout, ip_address, tcp_port, **kwargs)

    def clear_interface_command(self):
        """Clears the bits in the Status Byte Register, Standard Event Status Register, and Operation Event Register,
        and terminates all pending operations. Clears the interface, but not the controller."""

        self.command("*CLS")

    def get_standard_event_enable_mask(self):
        """Returns the names of the standard event enable register bits and their values.
        These values determine which bits propagate to the standard event register"""

        response = self.query("*ESE?")
        # status_register = Model218StandardEventRegister.from_integer(response)
        return response  # TODO: parse register

    def set_standard_event_enable_mask(self, register_mask):
        """Configures values of the standard event enable register bits.
        These values determine which bits propagate to the standard event register

            Args:
                register_mask (Model224StandardEventRegister):
                    An StandardEventRegister class object with all bits set to a value

        """

        integer_representation = register_mask.to_integer()
        self.command("*ESE " + str(integer_representation))

    def get_standard_event_status_register(self):
        """Returns the names of the standard event enable register bits and their values.
        These values determine which bits propagate to the standard event register"""

        response = self.query("*ESR?")
        # status_register = Model218StandardEventRegister.from_integer(response)
        return response  # TODO: parse register

    def _get_identity(self):
        return self.query('*IDN?').split(',')

    def get_kelvin_reading(self, input_channel):
        """Returns the temperature value in kelvin of either channel

            Args:
                input_channel:
                    * Selects the channel to retrieve measurement.
                    * Options are:
                        * 1-8

            Returns:
                (float):
                    The reading of the sensor in kelvin
        """

        return float(self.query("KRDG? {}".format(input_channel)))

    def get_kelvin_reading_all(self):
        """Returns the temperature value in kelvin of either channel

                    Returns:
                        (list):
                            The reading of the sensor in kelvin
                """
        return [float(i) for i in (self.query("KRDG? {}".format(0))).split(',')]

    def _usb_command(self, command):
        """Send a command over the serial USB connection"""

        self.device_serial.write(command.encode('ascii') + b'\r\n')

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
                        self.device_serial.write(b'\r\n')
                        sleep(0.1)
                        self.device_serial.reset_input_buffer()

                        break
        else:
            if com_port is None and serial_number is None:
                raise InstrumentException("No serial connections found")

            raise InstrumentException(
                "No serial connections found with a matching COM port and/or matching serial number")


if __name__ == '__main__':
    monitor = Model218(com_port='COM10')
    print(monitor.model_number)
    save_file = date.isoformat(date.today()) + '.tsv'
    header = 'timestamp\t' + '\t'.join(['temp{}'.format(i) for i in range(1, 9)]) + '\n'
    if not os.path.isfile(save_file):
        with open(save_file, 'w') as f:
            f.write(header)
    while True:
        timestamp = datetime.now()
        temps = monitor.get_kelvin_reading_all()
        templine = datetime.isoformat(timestamp) + '\t' + '\t'.join([str(i) for i in temps]) + '\n'
        print(templine)
        with open(save_file, 'a') as f:
            f.write(templine)
        sleep(5)
