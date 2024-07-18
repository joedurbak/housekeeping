import json

from serial.tools.list_ports import comports

with open('devices.json') as f:
    devices = json.load(f)

comports = comports()

devices_flattened = {}

for device_type, device_type_dict in devices.items():
    for device_name, device_list in device_type_dict.items():
        for device_number, device_dict in enumerate(device_list):
            devices_flattened[f'{device_type}_{device_name}_{device_number}'] = device_dict

# print(devices_flattened)

comport_dict = {}
for port in comports:
    print(port.serial_number, port.device)
    comport_dict[port.serial_number] = port.device

for device_name, device_dict in devices_flattened.items():
    port = comport_dict.get(device_dict.get('serial_number', ''), 'no port')
    print(device_name, port)
