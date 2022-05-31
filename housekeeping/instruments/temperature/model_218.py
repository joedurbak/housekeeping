import os
from time import sleep
from datetime import date, datetime

from housekeeping.instruments.temperature.base_lakeshore import Model218Model331Overlap


class Model218(Model218Model331Overlap):
    def set_date_time(self, date_time=None):
        if date_time is not None:
            assert isinstance(date_time, datetime)
        else:
            date_time = datetime.now()
        year = '{}'.format(date_time.year)[-2:]
        self.command(
            'DATETIME {},{},{},{},{},{}'.format(date_time.month, date_time.day, year, date_time.hour,
                                                date_time.minute, date_time.second)
        )

    def get_date_time(self):
        response = self.query('DATETIME?')
        month, day, year, hour, minute, second = [float(i) for i in response.split(',')]
        if year > float('{}'.format(datetime.now().year)[-2:]):
            year += 1900
        else:
            year += 2000
        return datetime(year, month, day, hour, minute, second)

    def set_input_control(self, temperature_input, enable=True):
        self.command('INPUT {},{}'.format(temperature_input, int(enable)))

    def get_input_control(self, temperature_input):
        response = self.query('INPUT? {}'.format(temperature_input))
        return bool(int(response))


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
        print(templine.strip())
        # print(monitor.query('IEEE?'))
        with open(save_file, 'a') as f:
            f.write(templine)
        sleep(5)
