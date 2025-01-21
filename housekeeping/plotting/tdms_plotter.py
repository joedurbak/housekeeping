from matplotlib import pyplot as plt
from nptdms import TdmsFile
import numpy as np
import pandas as pd

# tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_182_01_Camera Control.tdms'
# tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_196_01_Camera Control.tdms'
tdms_filename = r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_175_01_Camera Control.tdms'
tdms_filenames = [
    r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_175_01_Camera Control.tdms',
    r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_176_01_Camera Control.tdms',
    r'C:\Users\gsfcprime\Documents\LabVIEW Data\TDMS\2024_177_01_Camera Control.tdms'
]

# tdms = TdmsFile.read(tdms_filename)
# ls336_data = tdms['Lakeshore 336'].as_dataframe()
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
