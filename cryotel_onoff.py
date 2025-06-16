"""
Single file version of housekeeping.instruments.temperature.cryotel_avc with added on/off interface

installation:

pip install argparse lakeshore
"""
import argparse

import serial
from time import sleep

from argparse import ArgumentParser
from lakeshore.generic_instrument import InstrumentException, GenericInstrument, comports

cryocoolers = [
    "FT86J1KYA",
    "FT86J1KYB",
    "FT86J1KYC"
]

cryocooler_on_mode = ('temperature', 'temperature', 'power')


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

    def _get_identity(self):
        serial_number = 'xxxx'
        model_number = 'xxxx'
        serial_string = 'xxxx/xxxx'
        firmware_version = 'xxxx'
        return serial_number, model_number, serial_string, firmware_version

    def _usb_command(self, command):
        """Send a command over the serial USB connection"""
        self.device_serial.write(command.encode('ascii') + self.serial_cmd_termination)

    def _usb_query(self, query):
        """Query over the serial USB connection"""

        self._usb_command(query)
        # sleep(1)
        # response = self.device_serial.read(5)
        response = self.device_serial.read_until(self.serial_cmd_termination).decode('ascii')

        # If nothing is returned, raise a timeout error.
        if not response:
            raise InstrumentException("Communication timed out")

        return response.rstrip()

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

    def log_dict(self):
        return {}


class CryotelAVC(ModifiedGenericInstrument):
    def __init__(
            self,
            serial_number=None,
            com_port=None,
            baud_rate=9600,
            data_bits=serial.EIGHTBITS,
            stop_bits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            flow_control=False,
            handshaking=False,
            timeout=2.0,
            connection=None,
            serial_cmd_termination='\r'
    ):
        super(CryotelAVC, self).__init__(
            serial_number, com_port, baud_rate, data_bits, stop_bits, parity, flow_control, handshaking, timeout,
            connection, serial_cmd_termination
        )
        self.command_return_lines = {
            'COOLER': 2,
            'E': 4,
            'ERROR': 2,
            'KD': 2,
            'KI': 2,
            'KP': 2,
            'LOGIN': 2,
            'LOGOUT': 2,
            'MODE': 2,
            'P': 2,
            'PASSWD': 2,
            'PWOUT': 2,
            'SENSOR': 2,
            'STATUS': 8,
            'TC': 2,
            'TEMP RJ': 2,
            'TTARGET': 2,
            'VERSION': 2
        }

        self.error_codes = {
            '00000001': 'High Reject Temperature Error',
            '00000010': 'Low Reject Temperature Error',
            '10000000': 'Over Current Error',
            '11111111': 'Invalid Configuration Error',
            '10000001': 'High Reject Temperature and Over Current Error',
            '10000010': 'Low Reject Temperature and Over Current Error',
        }

    def _usb_query(self, query):
        """Query over the serial USB connection"""
        query = query.upper()
        self._usb_command(query)
        # sleep(1)
        # response = self.device_serial.read(5)
        _cmd = query.split('=')[0].strip()
        response = ''
        for l in range(self.command_return_lines[_cmd]):
            response += self.device_serial.read_until(self.serial_cmd_termination).decode('ascii') + '\n'

        # If nothing is returned, raise a timeout error.
        if not response:
            raise InstrumentException("Communication timed out")
        return response.rstrip()

    @staticmethod
    def warn_no_arguments(command, argument):
        if argument is not None:
            UserWarning(
                '{} command does not accept arguments. Continuing query without applying argument, {}.'.format(
                    command, argument))

    def cryotel_command(self, command, argument=None):
        if argument is None:
            q = command
        else:
            q = '='.join([command, argument])
        return self.query(q)

    def no_arg_command(self, command, argument=None):
        self.warn_no_arguments(command, argument)
        return self.cryotel_command(command)

    def cooler(self, argument=None):
        return self.cryotel_command('COOLER', argument)

    def e(self, argument=None):
        return self.no_arg_command('E', argument)

    def error(self, argument=None):
        e = self.no_arg_command('ERROR', argument)
        try:
            raise InstrumentException(self.error_codes[e])
        except KeyError:
            pass

    def kd(self, argument=None):
        return self.cryotel_command('KD', argument)

    def ki(self, argument=None):
        return self.cryotel_command('KI', argument)

    def kp(self, argument=None):
        return self.cryotel_command('KP', argument)

    def login(self, argument=None):
        return self.cryotel_command('LOGIN', argument)

    def logout(self, argument=None):
        return self.cryotel_command('LOGOUT', argument)

    def mode(self, argument=None):
        return self.no_arg_command('MODE', argument)

    def p(self, argument=None):
        return self.no_arg_command('P', argument)

    def pwout(self, argument=None):
        return self.no_arg_command('PWOUT', argument)

    def power_setpoint(self, argument=None):
        """
        Copy of pwout
        """
        return self.pwout(argument)

    def passwd(self, argument=None):
        return self.cryotel_command('PASSWD', argument)

    def password(self, argument=None):
        """
        Copy of passwd
        """
        return self.passwd(argument)

    def sensor(self, argument=None):
        return self.no_arg_command('SENSOR', argument)

    def status(self, argument=None):
        return self.no_arg_command('STATUS', argument)

    def tc(self, argument=None):
        return self.no_arg_command('TC', argument)

    def temperature_coldhead(self, argument=None):
        """
        Copy of tc
        """
        return self.tc(argument)

    def temp_rj(self, argument=None):
        return self.no_arg_command('TEMP RJ', argument)

    def temperature_reject(self, argument=None):
        """
        Copy of temp_rj
        """
        return self.temp_rj(argument)

    def ttarget(self, argument=None):
        return self.cryotel_command('TTARGET', argument)

    def temperature_setpoint(self, argument=None):
        """
        Copy of ttarget
        """
        return self.ttarget(argument)

    def version(self, argument=None):
        return self.no_arg_command('VERSION', argument)

    def start_cryocooler(self, mode, setpoint=None):
        """
        Convenience method to start cryocooler

        Parameters
        ----------
        mode : str
            cryocooler operation mode, either (p)ower or (t)emperature.
            Any string that starts with 'p' or 't' will activate power or temperature mode respectively.
            Not case-sensitive.
        setpoint : float
            Cryocooler setpoint in Watts for power mode, and in Kelvin for temperature mode.
            Default is to keep whatever current setpoint is in use.
        """
        commands = {
            'P': ('POWER', self.pwout),
            'T': ('ON', self.ttarget),
        }
        command, setpoint_fn = commands[mode.upper()[0]]
        if setpoint is not None:
            setpoint_fn(setpoint)
        return self.command(command)

    def stop_cryocooler(self):
        """
        Convenience method to stop cryocooler
        """
        return self.cooler('OFF')


def start_coolers(modes=cryocooler_on_mode):
    for cooler, mode in zip(cryocoolers, modes):
        if mode.upper().startswith('P') or mode.upper().startswith('T'):
            with CryotelAVC(serial_number=cooler) as cryotel:
                print(cryotel.start_cryocooler(mode))


def stop_coolers():
    for cooler in cryocoolers:
        with CryotelAVC(serial_number=cooler) as cryotel:
            print(cryotel.stop_cryocooler())


def main():
    parser = argparse.ArgumentParser(description='cryotel-on-off')
    parser.add_argument(
        'command',
        help='command can be "start" or "stop". This will either start the configured cryocoolers or stop all of the cryocoolers'
    )
    parser.add_argument(
        '-c','--cooler-on-mode', default=cryocooler_on_mode,
        help='mode to start cryocoolers in joined with a comma (,). Can be "power", "temperature" or "off". Not case-sensitive. Only the first letter for each mode matters. Default is {}'.format(','.join(cryocooler_on_mode)))
    args = parser.parse_args()
    if args.command == 'start':
        modes = args.cooler_on_mode.split(',')
        start_coolers(modes)
    if args.command == 'stop':
        stop_coolers()
    else:
        print('unknown command')
        parser.print_help()

if __name__ == '__main__':
    main()
