import serial
import os
from time import sleep
from datetime import date, datetime

from housekeeping.instruments.base.modified_generic_instrument import ModifiedGenericInstrument


class SeeedSTH01(ModifiedGenericInstrument):
    def __init__(self,
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
                 connection=None,
                 serial_cmd_termination='\r\n'):
        super(SeeedSTH01, self).__init__(
            serial_number=serial_number,
            com_port=com_port,
            baud_rate=baud_rate,
            data_bits=data_bits,
            stop_bits=stop_bits,
            parity=parity,
            flow_control=flow_control,
            handshaking=handshaking,
            timeout=timeout,
            ip_address=ip_address,
            tcp_port=tcp_port,
            connection=connection,
            serial_cmd_termination=serial_cmd_termination
        )

    def get_pressure(self):
        response = self.query('#01RDS')
        return float(response.split()[-1])

    def get_pressure_ig(self):
        response = self.query('#01RD')
        return float(response.split()[-1])

    def get_pressure_cg1(self):
        response = self.query('#01RDCG1')
        return float(response.split()[-1])

    def get_pressure_cg2(self):
        response = self.query('#01RDCG2')
        return float(response.split()[-1])

    def set_ion_gauge_on(self):
        response = self.query('#01IG1')
        return response

    def set_ion_gauge_off(self):
        self.query("#01IG0")

    def log_dict(self):
        _dict = {}
        prefix = self.__class__.__name__
        _dict["{}_pressure_mBar".format(prefix)] = self.get_pressure()


# if __name__ == '__main__':
#     # test program:
#     import minimalmodbus
#
#     PORT = 'COM43'
#     TEMP_REGISTER = 0x0000
#     HUM_REGISTER = 0x0001
#     DEWPOINT_REGISTER = 0x0002
#
#     # Set up instrument
#     instrument = minimalmodbus.Instrument(port=PORT, slaveaddress=1, mode=minimalmodbus.MODE_RTU)
#
#     # Make the settings explicit
#     instrument.serial.baudrate = 9600  # Baud
#     instrument.serial.bytesize = 8
#     instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
#     instrument.serial.stopbits = 1
#     instrument.serial.timeout = 1  # seconds
#
#     # Good practice
#     instrument.close_port_after_each_call = True
#
#     instrument.clear_buffers_before_each_transaction = True
#
#     # Read temperatureas a float
#     # if you need to read a 16 bit register use instrument.read_register()
#     temperature = instrument.read_register(TEMP_REGISTER, signed=True)
#     temperature = temperature/100
#
#     # Read the humidity
#     humidity = instrument.read_register(HUM_REGISTER)
#     humidity = humidity/100
#
#     # Read the dew point
#     dew_point = instrument.read_register(DEWPOINT_REGISTER)
#     dew_point = dew_point/100
#
#     # Pront the values
#     print('The temperature is: %.1f deg C\r' % temperature)
#     print('The humidity is: %.1f percent\r' % humidity)
#     print('The dew point is: %.1f deg C\r' % dew_point)


if __name__ == '__main__':
    # test program:
    import minimalmodbus

    PORT = 'COM5'
    TEMP_REGISTER = 0x0000
    HUM_REGISTER = 0x0001
    DEWPOINT_REGISTER = 0x0002

    # Set up instrument
    instrument = minimalmodbus.Instrument(port=PORT, slaveaddress=1, mode=minimalmodbus.MODE_RTU)

    # Make the settings explicit
    instrument.serial.baudrate = 9600  # Baud
    instrument.serial.bytesize = 8
    instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 1  # seconds

    # Good practice
    instrument.close_port_after_each_call = True

    instrument.clear_buffers_before_each_transaction = True

    # Read temperatureas a float
    # if you need to read a 16 bit register use instrument.read_register()
    temperature = instrument.read_register(TEMP_REGISTER, signed=True)
    temperature = temperature/100

    # Read the humidity
    humidity = instrument.read_register(HUM_REGISTER)
    humidity = humidity/100

    # Read the dew point
    dew_point = instrument.read_register(DEWPOINT_REGISTER)
    dew_point = dew_point/100

    # Pront the values
    print('The temperature is: %.1f deg C\r' % temperature)
    print('The humidity is: %.1f percent\r' % humidity)
    print('The dew point is: %.1f deg C\r' % dew_point)
