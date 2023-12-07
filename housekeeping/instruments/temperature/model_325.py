import os
from time import sleep
from datetime import date, datetime

from housekeeping.instruments.temperature.base_lakeshore import BaseLakeshoreController, HeaterRange


class Model325(BaseLakeshoreController):
    def query(self, query_string):
        return super(BaseLakeshoreController, self).query(query_string).strip(';')

    def command(self, command_string):
        super(BaseLakeshoreController, self).command(command_string)


if __name__ == '__main__':
    monitor = Model325(com_port='COM5')
    print(monitor.model_number)
    heater_input = 0
    monitor.set_setpoint(heater_input, 95)
    monitor.set_heater_pid(heater_input, 60, 17, 0)
    monitor.set_heater_range(heater_input, HeaterRange.LOW)
    print(monitor.get_setpoint(heater_input))
    print(monitor.get_heater_pid(heater_input))
    print(monitor.get_heater_range(heater_input))
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
        with open(save_file, 'a') as f:
            f.write(templine)
        sleep(5)
