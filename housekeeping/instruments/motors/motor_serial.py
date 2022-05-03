import serial
from datetime import datetime as dt
from time import sleep

import numpy as np
from lakeshore.generic_instrument import GenericInstrument, comports, InstrumentException


class BaseMotor(GenericInstrument):
    vid_pid = [(10755, 66), (9025, 16)]

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
            ip_address=None,
            tcp_port=7777,
            connection=None
            ):
        super(BaseMotor, self).__init__(
            serial_number, com_port, baud_rate, data_bits, stop_bits, parity, flow_control,
            handshaking, timeout, ip_address, tcp_port, connection
        )

    def connect_usb(self, serial_number=None, com_port=None, baud_rate=None, data_bits=None,
                    stop_bits=None, parity=None, timeout=None, handshaking=None, flow_control=None):
        super(BaseMotor, self).connect_usb(
            serial_number, com_port, baud_rate, data_bits, stop_bits, parity, timeout, handshaking, flow_control
        )
        sleep(5)

    def query(self, query_string, timeout_s=1, end_statements=('EOR', 'com_fail')):
        """Send a query to the instrument and return the response

            Args:
                query_string (str):
                    A serial query ending in a question mark
                timeout_s (float):
                    Timeout for specific query
                end_statements (tuple, list):
                    strings to stop reading the

            Returns:
               The instrument query response as a string.

        """

        # Query the instrument over serial. If serial is not configured, use TCP.
        with self.dut_lock:
            if self.device_serial is not None:
                response = self._usb_query(query_string, timeout_s, end_statements)
            elif self.device_tcp is not None:
                response = self._tcp_query(query_string)
            else:
                raise InstrumentException("No connections configured")

            self.logger.info('Sent query to %s: %s', self.serial_number, query_string)
            self.logger.info('Received response from %s: %s', self.serial_number, response)

        return response

    def _usb_query(self, query, timeout_s=1.0, end_statements=('EOR', 'com_fail')):
        print(query)
        print(timeout_s)
        self.device_serial.read_all()  # clear cache
        response = ''
        total_seconds = 0
        self._usb_command(query)
        sleep(1)
        start = dt.now()
        while total_seconds < timeout_s:
            # print(total_seconds)
            # sleep(0.1)
            line = self.device_serial.read_all()
            line = line.decode('ascii')
            response += line
            print(line.strip())
            end_line = False
            for end_statement in end_statements:
                if line.startswith(end_statement):
                    end_line = True
            if end_line:
                continue
            total_seconds = (dt.now() - start).total_seconds()
        return response

    def _get_identity(self):
        serial_number = 'xxxx'
        model_number = 'xxxx'
        serial_string = 'xxxx/xxxx'
        firmware_version = 'xxxx'
        return serial_number, model_number, serial_string, firmware_version

    def move(self, motor_number, steps, speed=100, acceleration=100, clockwise=True, switch_move=False, buffer_time=3):
        _dict = {
            'motor_number': motor_number,
            'steps': steps,
            'speed': speed,
            'acceleration': acceleration,
        }
        if clockwise:
            _dict['direction'] = '+'
        else:
            _dict['direction'] = '-'
        if switch_move:
            _dict['move_type'] = 'S'
        else:
            _dict['move_type'] = 'R'
        _cmd = 'M{motor_number}1{direction}{move_type}{steps}:{speed}:{acceleration}'
        _cmd_str = _cmd.format(**_dict)
        print(_cmd_str)
        a_time = speed / acceleration
        a_steps = 0.5 * acceleration * a_time ** 2
        if a_steps < steps:
            cont_speed_steps = steps - 2 * a_steps
            cont_speed_time = cont_speed_steps / speed
            total_move_time = 2 * a_time + cont_speed_time
        else:
            total_move_time = 2 * np.sqrt(steps / acceleration)
        timeout = total_move_time + buffer_time
        self.query(_cmd_str, timeout_s=timeout)


if __name__ == '__main__':
    m = BaseMotor(serial_number='7553335343735161A032')
    m.move(0, 10, clockwise=False)
