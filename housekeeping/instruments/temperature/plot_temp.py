import os

from pandas import read_csv, to_datetime
from matplotlib import pyplot as plt
from matplotlib import dates as mdates

default_fields = (
    'system_mbar', 'ion_gauge_mbar', 'cg1_mbar', 'cg2_mbar', 'lesker_mbar'
)


def plot_pressure_log(log_file_name=None, fields=default_fields):
    if log_file_name is None:
        file_dir = os.path.dirname(__file__)
        log_files = [os.path.join(file_dir, f) for f in os.listdir(file_dir) if f.endswith('.tsv')]
        log_files.sort()
        log_file_name = log_files[-1]
    print(log_file_name)
    log_data = read_csv(log_file_name, delimiter='\t')
    log_data['time'] = to_datetime(log_data['timestamp'])
    log_data = log_data[log_data['ion_gauge_mbar'] < 1000]
    ax1 = plt.subplot(111)
    for field in fields:
        try:
            ax1.plot(log_data['time'], log_data[field])
        except KeyError:
            print('No field: {}'.format(field))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Pressure (mbar)')
    ax1.semilogy()
    plt.show()


if __name__ == '__main__':
    _fields = (
        # 'system_mbar',
        'ion_gauge_mbar',
    )
    plot_pressure_log(log_file_name=None, fields=_fields)
