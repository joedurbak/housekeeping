import os

from datetime import date, datetime
from time import sleep

from housekeeping.instruments.temperature.model_218 import Model218
from housekeeping.instruments.temperature.model_325 import Model325
from housekeeping.instruments.temperature.model_331 import Model331


if __name__ == '__main__':
    monitor = Model218(com_port='COM11')
    controller331 = Model331(com_port='COM19')
    controller325 = Model325(com_port='COM5')
    print(monitor.model_number)
    save_file = date.isoformat(date.today()) + '.tsv'
    header = 'timestamp\t' + '\t'.join(['temp{}'.format(i) for i in range(1, 9)]) + '\t' +\
             '\t'.join(('mod331chanA',)) + '\t' + '\t'.join(('mod325chanA',)) + '\n'
    if not os.path.isfile(save_file):
        with open(save_file, 'w') as f:
            f.write(header)
    while True:
        timestamp = datetime.now()
        temps = monitor.get_kelvin_reading_all()
        temps_331 = controller331.get_kelvin_reading_all()
        temps_325 = controller325.get_kelvin_reading_all()
        setpoint = min((temps[5]+1, 290.0))
        controller325.set_setpoint(1, setpoint)
        controller331.set_setpoint(1, setpoint)
        sleep(0.1)
        print(setpoint, controller325.get_heater_output(1))
        temps = temps + temps_331 + temps_325
        templine = datetime.isoformat(timestamp) + '\t' + '\t'.join([str(i) for i in temps]) + '\n'
        print(templine.strip())
        # print(monitor.query('IEEE?'))
        with open(save_file, 'a') as f:
            f.write(templine)
        sleep(5)
