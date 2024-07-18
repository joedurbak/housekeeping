import serial

from housekeeping.instruments.base.modified_generic_instrument import ModifiedGenericInstrument, InstrumentException


class MKS392BRS485(ModifiedGenericInstrument):
    def __init__(self,
                 serial_number=None,
                 com_port=None,
                 baud_rate=9600,
                 data_bits=serial.EIGHTBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_NONE,
                 flow_control=False,
                 handshaking=False,
                 timeout=2.0,
                 ip_address=None,
                 tcp_port=7777,
                 connection=None,
                 serial_cmd_termination='\f',
                 address=253):
        super(MKS392BRS485, self).__init__(
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
        self.address = address

    def _usb_query(self, query):
        """Query over the serial USB connection."""

        self._usb_command(query)
        response = self.device_serial.read_until(b'\f').decode('ascii')

        # If nothing is returned, raise a timeout error.
        if not response:
            raise InstrumentException("Communication timed out")

        return response.rstrip()


