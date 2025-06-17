import serial

from lakeshore.generic_instrument import InstrumentException

from housekeeping.instruments.base.modified_generic_instrument import ModifiedGenericInstrument


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
            connection=connection, serial_cmd_termination=serial_cmd_termination
        )
        # self.serial_cmd_termination = serial_cmd_termination.encode()
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
        self.delim_order = ('Power Measured', 'Power Commanded', 'Target Temp', 'Reject Temp', 'Coldhead Temp')

    # def _usb_command(self, command):
    #     """Send a command over the serial USB connection"""
    #     _cmd = command.encode('ascii') + self.serial_cmd_termination
    #     print(_cmd)
    #     self.device_serial.write(_cmd)

    def _usb_query(self, query):
        """Query over the serial USB connection"""
        query = query.upper()
        self._usb_command(query)
        # sleep(1)
        # response = self.device_serial.read(5)
        _cmd = query.split('=')[0].strip()
        # response = ''
        # for l in range(self.command_return_lines[_cmd]):
        #     response += self.device_serial.read_until(self.serial_cmd_termination).decode('ascii') + '\n'
        sleep(0.5)
        response = self.device_serial.read_all().decode('ascii')
        # print(response)
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
        return self.cooler(command)

    def stop_cryocooler(self):
        """
        Convenience method to stop cryocooler
        """
        return self.cooler('OFF')

    def get_status_dict(self):
        status = self.status()
        status_lines = status.splitlines()[2:]
        status_parsed = [line.split('=') for line in status_lines]
        status_dict = {k.strip(): v.strip() for k, v in status_parsed}
        return status_dict

    def get_status_delim(self, delim='\t'):
        status = self.get_status_dict()
        status_list = [status[key] for key in self.delim_order]
        return delim.join(status_list)
