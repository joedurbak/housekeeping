import os
from time import sleep
from datetime import date, datetime

from housekeeping.instruments.temperature.base_lakeshore import BaseLakeshoreController, Model218Model331Overlap


class Model331(Model218Model331Overlap, BaseLakeshoreController):
    def get_heater_output(self, output):
        if output == 1:
            return float(self.query('HTR?'))
        elif output == 2:
            return float(self.query('AOUT?'))
        else:
            return -999


if __name__ == '__main__':
    monitor = Model331(com_port='COM27')
    print(monitor.model_number)
    save_file = date.isoformat(date.today()) + '.tsv'
    header = 'timestamp\t' + '\t'.join(['temp{}'.format(i) for i in range(1, 2)]) + '\n'
    if not os.path.isfile(save_file):
        with open(save_file, 'w') as f:
            f.write(header)
    while True:
        timestamp = datetime.now()
        temps = monitor.get_kelvin_reading_all()
        templine = datetime.isoformat(timestamp) + '\t' + '\t'.join([str(i) for i in temps]) + '\n'
        print(templine.strip())
        with open(save_file, 'a') as f:
            f.write(templine)
        sleep(10)
