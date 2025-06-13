import os

from matplotlib import pyplot as plt
from nptdms import TdmsFile
import numpy as np
import pandas as pd

tdms_dir = r'G:\RIMAS TDMS archive'
all_files = os.listdir(tdms_dir)
tdms_prefixes = ['2024_{:03d}'.format(i) for i in range(257, 266)]
tdms_filenames = []
for prefix in tdms_prefixes:
    for f in all_files:
        if f.startswith(prefix) and f.endswith('.tdms'):
            tdms_filenames.append(os.path.join(tdms_dir, f))
print('\n'.join(tdms_filenames))
# tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_182_01_Camera Control.tdms'
# tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_196_01_Camera Control.tdms'
# tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_175_01_Camera Control.tdms'
# tdms_filenames = [
#     r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_175_01_Camera Control.tdms',
#     r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_176_01_Camera Control.tdms',
#     r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_177_01_Camera Control.tdms'
# ]
# tdms_dir = r'F:\PRIME_housekeeping-logs\TDMS\TDMS-cryo2-incident'
# tdms_filenames = [os.path.join(tdms_dir, f) for f in os.listdir(tdms_dir) if f.endswith('.tdms')]
# tdms = TdmsFile.read(tdms_filename)
# ls336_data = tdms['Lakeshore 336'].as_dataframe()
# runaway test is ~2024_262

plt_ls336 = False
plt_cryocooler = False
plt_pressure = True

if plt_ls336:
    ls336_data = pd.concat(
        [TdmsFile.read(tdms_filename)['Lakeshore 336'].as_dataframe() for tdms_filename in tdms_filenames],
        ignore_index=True
    )

    channels = [
        # 'Timestamp',
        'LS336 Input A',
        'LS336 Input B',
        'LS336 Input C',
        'LS336 Input D',
        'LS336 Input D2',
        'LS336 Input D3',
        'LS336 Input D4'
    ]

    timestamp = ls336_data['Timestamp']
    temperatures = ls336_data[channels]
    fig = plt.figure()
    # major_yticks = np.arange(90, 110, 1.0)
    # minor_yticks = np.arange(90, 110, 0.2)

    # major_yticks = np.arange(94.997, 95.003, 0.001)
    # minor_yticks = np.arange(94.997, 95.003, 0.0005)

    major_yticks = np.arange(80, 300, 20)
    minor_yticks = np.arange(80, 300, 5)

    ax = fig.add_subplot(1, 1, 1)
    ax.set_yticks(major_yticks)
    ax.set_yticks(minor_yticks, minor=True)
    ax.plot(timestamp, temperatures)
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.set_xlim((np.min(timestamp), np.max(timestamp)))
    ax.set_ylim((80, 300))
    plt.xlabel('Timestamp (month-day hour)')
    plt.ylabel('Temperature (K)')
    # plt.title('Internal Dewar Temperatures')
    plt.title('Cooldown Dewar Temperatures')
    plt.tight_layout()
    plt.show()

if plt_cryocooler:
    cryocooler_data = []
    for tdms_filename in tdms_filenames:
        try:
            cryocooler_data.append(TdmsFile.read(tdms_filename)['CryoCooler'].as_dataframe())
        except (ValueError, KeyError):
            print('Cryocooler Value/Key Error: ', tdms_filename)
    cryocooler_data = pd.concat(cryocooler_data, ignore_index=True)
    cc_channels = [
        'Cryo1Power Measured',
        'Cryo1Coldhead Temp',
        'Cryo1Reject Temp',
        'Cryo2Power Measured',
        'Cryo2Coldhead Temp',
        'Cryo2Reject Temp',
        'Cryo3Power Measured',
        'Cryo3Coldhead Temp',
        'Cryo3Reject Temp',
    ]
    print(cryocooler_data)
    cc_timestamp = cryocooler_data['Timestamp']

    fig = plt.figure()
    # major_yticks = np.arange(90, 110, 1.0)
    # minor_yticks = np.arange(90, 110, 0.2)

    # major_yticks = np.arange(94.997, 95.003, 0.001)
    # minor_yticks = np.arange(94.997, 95.003, 0.0005)

    major_yticks = np.arange(0, 300, 20)
    minor_yticks = np.arange(0, 300, 5)

    ax = fig.add_subplot(1, 1, 1)
    ax.set_yticks(major_yticks)
    ax.set_yticks(minor_yticks, minor=True)
    ax.plot(cc_timestamp, cryocooler_data[cc_channels])
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    ax.legend(cc_channels)
    ax.set_xlim((np.min(cc_timestamp), np.max(cc_timestamp)))
    # ax.set_ylim((80, 300))
    plt.xlabel('Timestamp (month-day hour)')
    # plt.ylabel('Temperature (K)')
    # plt.title('Internal Dewar Temperatures')
    plt.title('Cooldown Dewar Temperatures')
    plt.tight_layout()
    plt.show()

if plt_pressure:
    pressure_data = []
    for tdms_filename in tdms_filenames:
        try:
            pressure_data.append(TdmsFile.read(tdms_filename)['Pressure Monitor'].as_dataframe())
        except (ValueError, KeyError):
            print('Pressure Monitor Value/Key Error: ', tdms_filename)

    pressure_data = pd.concat(pressure_data, ignore_index=True)
    channels = [
        'Pressure Instrument',
    ]
    print(pressure_data)

    timestamp = pressure_data['Timestamp']

    fig = plt.figure()
    # major_yticks = np.arange(90, 110, 1.0)
    # minor_yticks = np.arange(90, 110, 0.2)

    # major_yticks = np.arange(94.997, 95.003, 0.001)
    # minor_yticks = np.arange(94.997, 95.003, 0.0005)

    # major_yticks = np.arange(0, 300, 20)
    # minor_yticks = np.arange(0, 300, 5)

    ax = fig.add_subplot(1, 1, 1)
    # ax.set_yticks(major_yticks)
    # ax.set_yticks(minor_yticks, minor=True)
    ax.plot(timestamp, pressure_data[channels])
    ax.grid(which='both')
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    # ax.legend(cc_channels)
    ax.set_xlim((np.min(timestamp), np.max(timestamp)))
    # ax.set_ylim((80, 300))
    plt.xlabel('Timestamp (month-day hour)')
    plt.ylabel('Pressure (mbar)')
    # plt.title('Internal Dewar Temperatures')
    plt.title('Cooldown Dewar Temperatures')
    plt.tight_layout()
    plt.show()
