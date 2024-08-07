import numpy as np
import serial
import os
from time import sleep
from datetime import date, datetime

from housekeeping.instruments.base.modified_generic_instrument import ModifiedGenericInstrument


class Lesker392(ModifiedGenericInstrument):
    def __init__(self,
                 serial_number=None,
                 com_port=None,
                 baud_rate=19200,
                 data_bits=serial.EIGHTBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE,
                 flow_control=False,
                 handshaking=False,
                 timeout=2.0,
                 ip_address=None,
                 tcp_port=7777,
                 connection=None,
                 serial_cmd_termination='\r'):
        super(Lesker392, self).__init__(
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
        _dict["{}_pressure_mBar".format(prefix)] = self.get_pressure()  # TODO: generalize for external gauge connection


if __name__ == '__main__':
    # lesker = Lesker392(serial_number='FT58MCQ8A')
    lesker = Lesker392(com_port='COM20')
    # sleep(2)
    print(lesker.get_pressure())
    save_file = date.isoformat(date.today()) + '.tsv'
    header = 'timestamp\t' + 'system_mbar\t' + 'ion_gauge_mbar\t' + 'cg1_mbar\t' + 'cg2_mbar' + '\n'
    if not os.path.isfile(save_file):
        with open(save_file, 'w') as f:
            f.write(header)
    lesker.set_ion_gauge_off()
    sleep(5)
    lesker.set_ion_gauge_on()
    sleep(5)
    while True:
        timestamp = datetime.now()
        pressure = lesker.get_pressure()
        ion_gauge_pressure = lesker.get_pressure_ig()
        # cg1_pressure = lesker.get_pressure_cg1()
        # cg2_pressure = lesker.get_pressure_cg2()
        cg1_pressure = np.nan
        cg2_pressure = np.nan
        writeline = datetime.isoformat(timestamp) + '\t' + str(pressure) + '\t' + str(ion_gauge_pressure) + '\t' + \
            str(cg1_pressure) + '\t' + str(cg2_pressure) + '\n'
        print(writeline.strip()),
        # print(monitor.query('IEEE?'))
        with open(save_file, 'a') as f:
            f.write(writeline)
        sleep(5)
