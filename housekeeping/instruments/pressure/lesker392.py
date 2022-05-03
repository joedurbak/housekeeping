import serial
import os


class Lesker392(serial.Serial):
    def __init__(self,
                 port=None,
                 baudrate=19200,
                 bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 timeout=None,
                 xonxoff=False,
                 rtscts=False,
                 write_timeout=None,
                 dsrdtr=False,
                 inter_byte_timeout=None,
                 exclusive=None,
                 **kwargs):
        super(Lesker392, self).__init__(
            port, baudrate, bytesize, parity, stopbits, timeout, xonxoff, rtscts, write_timeout, dsrdtr,
            inter_byte_timeout, exclusive, **kwargs
        )


if __name__ == '__main__':
    lesker = Lesker392(port='COM14')
    lesker.write(str.encode('#01RD', encoding='ascii') + b'\r\n')
    print(lesker.readline())
