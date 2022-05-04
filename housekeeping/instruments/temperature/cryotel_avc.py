import serial

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
            connection, serial_cmd_termination
        )
        self.command_return_lines = {
            'COOLER': 2,
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
