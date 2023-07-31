from enum import IntEnum

import serial

from lakeshore.generic_instrument import InstrumentException
from lakeshore.temperature_controllers import HeaterError, StandardEventRegister, RegisterBase, InterfaceMode

from housekeeping.instruments.base.modified_generic_instrument import ModifiedGenericInstrument


class AlarmParameters:
    """Class used to disable or configure an alarm in conjunction with the set/get_alarm_parameters() method"""

    def __init__(self, source, high_value, low_value, deadband, latch_enable, audible=None, visible=None):
        """Constructor for AlarmParameters class

            Args:
                source: (int):
                    Specifies input data to check. 1 = Kelvin, 2 = Celsius,
                    3 = sensor units, 4 = linear data.
                high_value (float):
                    Sets the value the source is checked against to activate the
                    high alarm
                low_value (float):
                    Sets the value the source is checked against to activate low alarm.
                deadband (float):
                    Sets the value that the source must change outside of an alarm
                    condition to deactivate an unlatched alarm.
                latch_enable (bool):
                    Specifies a latched alarm (False = off, True = on)
                audible (bool):
                    Specifies if the internal speaker will beep when an alarm condition
                    occurs (False = off, True = on)
                    Optional parameter.
                visible (bool):
                    Specifies if the Alarm LED on the instrument front panel will blink
                    when an alarm condition occurs (False = off, True = on)
                    Optional parameter.
        """
        self.source = source
        self.high_value = high_value
        self.low_value = low_value
        self.deadband = deadband
        self.latch_enable = latch_enable
        self.audible = audible
        self.visible = visible


class ServiceRequestRegister(RegisterBase):
    """Class object representing the Service Request Enable register."""
    bit_names = [
        "new_reading",
        "",
        "",
        "alarm",
        "error",
        "",
        "service_request",
        ""
    ]

    def __init__(self,
                 new_reading,
                 alarm,
                 error,
                 service_request):
        self.new_reading = new_reading
        self.alarm = alarm
        self.error = error
        self.service_request = service_request


class StatusByteRegister(RegisterBase):
    """Class object representing the status byte register."""
    bit_names = [
        "new_reading",
        "unused",
        "overload",
        "alarm",
        "error",
        "event_status_bit",
        "service_request"
        "datalog_done"
    ]

    def __init__(self,
                 new_reading,
                 unused,
                 overload,
                 alarm,
                 error,
                 event_status_bit,
                 service_request,
                 datalog_done):
        self.new_reading = new_reading
        self.unused = unused
        self.overload = overload
        self.alarm = alarm
        self.error = error
        self.event_status_bit = event_status_bit
        self.service_request = service_request
        self.datalog_done = datalog_done


class HeaterRange(IntEnum):
    """Control loop heater range enumeration"""
    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class InputSensorUnits(IntEnum):
    """Enumeration for the preferred units of an input sensor."""
    KELVIN = 1
    CELSIUS = 2
    SENSOR = 3
    LINEAR_EQUATION = 4


class SensorTypes(IntEnum):
    DIODE_2_5V = 0
    DIODE_7_5V = 1
    PLATINUM_250_OHM = 2
    PLATINUM_500_OHM = 3
    PLATINUM_5000_OHM = 4
    CERNOX = 5


class Model325Model331SensorTypes(IntEnum):
    SILICON_DIODE = 0
    GaAlAs_DIODE = 1
    PLATINUM_100_OHM_250 = 2
    PLATINUM_100_OHM_500 = 3
    PLATINUM_1000_OHM = 4
    NTC_RTD = 5
    THERMOCOUPLE_25_MV = 6
    THERMOCOUPLE_50_MV = 7
    _2_5V_1_MA = 8
    _7_5V_1_MA = 9


class AnalogMode(IntEnum):
    OFF = 0
    INPUT = 1
    MANUAL = 2


class Baud(IntEnum):
    _300 = 0
    _1200 = 1
    _9600 = 2


class CurveHeader:
    """A class that configures the user curve header and corresponding parameters"""

    def __init__(self, curve_name, serial_number, curve_data_format, temperature_limit, coefficient):
        """Constructor for Model224CurveHeader class

            Args:
                curve_name (str):
                    Specifies curve name (limit of 15 characters)

                serial_number (str):
                    Specifies curve serial number (limit of 10 characters)

                curve_data_format (Model224CurveFormat):
                    Specifies the curve data format

                temperature_limit (float):
                    * Specifies the curve temperature limit in Kelvin

                coefficient (Model224CurveTemperatureCoefficients):
                    * Specifies the curve temperature coefficient

        """

        self.curve_name = curve_name
        self.serial_number = serial_number
        self.curve_data_format = curve_data_format
        self.temperature_limit = temperature_limit
        self.coefficient = coefficient


class CurveFormat(IntEnum):
    """Enumerations specify formats for temperature sensor curves"""
    MILLIVOLT_PER_KELVIN = 1
    VOLTS_PER_KELVIN = 2
    OHMS_PER_KELVIN = 3
    LOG_OHMS_PER_KELVIN = 4


class CurveTemperatureCoefficients(IntEnum):
    """Enumerations specify positive/negative temperature sensor curve coefficients"""
    NEGATIVE = 1
    POSITIVE = 2


class DisplayFieldUnits(IntEnum):
    """Enumerated type defining how units are enumerated for settings and using Display Fields."""
    KELVIN = 1
    CELSIUS = 2
    SENSOR = 3
    LINEAR_DATA = 4
    MINIMUM_DATA = 5
    MAXIMUM_DATA = 6


class Terminator(IntEnum):
    CRLF = 0
    LFCR = 1
    LF = 2
    NONE = 3


class BaseLakeshoreMonitor(ModifiedGenericInstrument):
    """
    BaseLakeshoreMonitor is based on LS218S monitor
    """
    # vid_pid = (1659, 8963)

    def __init__(self,
                 serial_number=None,
                 com_port=None,
                 baud_rate=9600,
                 data_bits=serial.SEVENBITS,
                 stop_bits=serial.STOPBITS_ONE,
                 parity=serial.PARITY_ODD,
                 flow_control=False,
                 handshaking=False,
                 timeout=2.0,
                 ip_address=None,
                 tcp_port=7777,
                 connection=None,
                 serial_cmd_termination='\r\n'
                 ):

        super(BaseLakeshoreMonitor, self).__init__(
            serial_number, com_port, baud_rate, data_bits, stop_bits, parity, flow_control, handshaking, timeout,
            ip_address, tcp_port, connection, serial_cmd_termination
        )

    EventRegister = StandardEventRegister
    ServiceRegister = ServiceRequestRegister
    StatusByteRegister = StatusByteRegister
    InputSensorUnits = InputSensorUnits
    AnalogMode = AnalogMode
    Baud = Baud
    CurveHeader = CurveHeader
    CurveFormat = CurveFormat
    CurveTemperatureCoefficients = CurveTemperatureCoefficients
    DisplayFieldUnits = DisplayFieldUnits
    Terminator = Terminator
    SensorTypes = SensorTypes
    InterfaceMode = InterfaceMode

    def _get_identity(self):
        return self.query('*IDN?').split(',')

    def _error_check(self, error_code):
        event_register = self.EventRegister.from_integer(error_code)
        if event_register.query_error:
            raise InstrumentException('Query Error')
        if event_register.command_error:
            raise InstrumentException('Command Error: Invalid Command or Query')
        if event_register.execution_error:
            raise InstrumentException('Execution Error: Instrument not able to execute command or query.')

    def clear_interface_command(self):
        """Clears the bits in the Status Byte Register, Standard Event Status Register, and Operation Event Register,
        and terminates all pending operations. Clears the interface, but not the controller."""

        self.command("*CLS")

    def get_standard_event_enable_mask(self):
        """Returns the names of the standard event enable register bits and their values.
        These values determine which bits propagate to the standard event register"""

        response = self.query("*ESE?")
        status_register = self.EventRegister.from_integer(response)
        return status_register

    def check_operation_complete_command(self):
        response = self.query("*OPC?")
        return response

    def reset_instrument(self):
        """Sets controller parameters to power-up settings"""

        self.command("*RST")

    def set_standard_event_enable_mask(self, register_mask):
        """Configures values of the standard event enable register bits.
        These values determine which bits propagate to the standard event register

            Args:
                register_mask (StandardEventRegister):
                    An StandardEventRegister class object with all bits set to a value

        """

        integer_representation = register_mask.to_integer()
        self.command("*ESE " + str(integer_representation))

    def get_standard_event_status_register(self):
        """Returns the names of the standard event enable register bits and their values.
        These values determine which bits propagate to the standard event register"""

        response = self.query("*ESR?")
        status_register = self.EventRegister.from_integer(response)
        return status_register

    def _get_identity(self):
        return self.query('*IDN?').split(',')

    def set_service_request(self, register_mask):
        """Manually enable/disable the mask of the corresponding status flag bit in the status
        byte register

            Args:
                register_mask (ServiceRequestRegister):
                    A ServiceRequestRegister class object with all bits configured
        """

        integer_representation = register_mask.to_integer()
        self.command("*SRE " + str(integer_representation))

    def get_service_request(self):
        """Returns the status byte register bits and their values as a class instance"""

        response = self.query("*SRE?")
        status_register = self.ServiceRegister.from_integer(response)
        return status_register

    def get_status_byte(self):
        """Returns the status flag bits as a class instance without resetting the register"""

        response = self.query("*STB?")
        status_flag = StatusByteRegister.from_integer(response)
        return status_flag

    def get_self_test(self):
        """Instrument self test result completed at power up

            Return:
                test_errors (bool):
                    * True = errors found
                    * False = no errors found
        """

        test_errors = bool(int(self.query("*TST?")))
        return test_errors

    def set_wait_to_continue(self):
        """Causes the IEEE-488 interface to hold off until all pending operations have been completed.
        This has the same function as the set_operation_complete() method, except that it does not set the
        Operation Complete event bit in the Event Status Register"""

        self.command("*WAI")

    def get_celsius_reading(self, input_channel):
        """Returns the temperature value in celsius of either channel

            Args:
                input_channel:
                    * Selects the channel to retrieve measurement.

            Returns:
                (float):
                    The reading of the sensor in celsius
        """

        return float(self.query("CRDG? {}".format(input_channel)))

    def get_celsius_reading_all(self):
        """Returns the temperature value in celsius of either channel

                    Returns:
                        (list):
                            The reading of the sensor in celsius
                """
        return [float(i) for i in (self.query("CRDG? {}".format(0))).split(',')]

    def delete_curve(self, curve):
        """Deletes the user curve

            Args:
                curve (int):
                    * Specifies a user curve to delete

        """
        self.command("CRVDEL {}".format(curve))

    def set_curve_header(self, curve_number, curve_header):
        """Configures the user curve header

            Args:
                curve_number (int):
                    * Specifies which curve to configure.
                    * Options are:
                        * 21 - 59

                curve_header (self.CurveHeader):
                    * A Model224CurveHeader class object containing the desired curve information

        """
        command_string = "CRVHDR {},{},{},{},{},{}".format(curve_number,
                                                           curve_header.curve_name,
                                                           curve_header.serial_number,
                                                           curve_header.curve_data_format,
                                                           curve_header.temperature_limit,
                                                           curve_header.coefficient)
        self.command(command_string)

    def get_curve_header(self, curve):
        """Returns parameters set on a particular user curve header

            Args:
                curve (int):
                    * Specifies a curve to retrieve
                    * Options are:
                        * 21 - 59

            Returns:
                header (CurveHeader):
                    * A CurveHeader class object containing the desired curve information

        """
        response = self.query("CRVHDR? {}".format(curve))
        curve_header = response.split(",")
        header = self.CurveHeader(str(curve_header[0]),
                                  str(curve_header[1]),
                                  self.CurveFormat(int(curve_header[2])),
                                  float(curve_header[3]),
                                  self.CurveTemperatureCoefficients(int(curve_header[4])))
        return header

    def set_curve_data_point(self, curve, index, sensor_units, temperature):
        """Configures a user curve point

            Args:
                curve (int or str):
                    * Specifies which curve to configure

                index (int):
                    * Specifies the points index in the curve

                sensor_units (float):
                    * Specifies sensor units for this point to 6 digits

                temperature (float):
                    * Specifies the corresponding temperature in Kelvin for this point to 6 digits

        """
        self.command("CRVPT {},{},{},{}".format(curve, index, sensor_units, temperature))

    def get_curve_data_point(self, curve, index):
        """Returns a standard or user curve data point

            Args:
                curve (int):
                    * Specifies which curve to query

                index (int):
                    * Specifies the points index in the curve

            Return:
                curve_point (tuple)
                    * (sensor_units: float, temp_value: float))

        """
        curve_point = self.query("CRVPT? {},{}".format(curve, index)).split(",")
        return float(curve_point[0]), float(curve_point[1])

    def set_display_field_settings(self, field, input_channel, display_units):
        """Configures a display field in custom display mode.

            Args:
                field (int):
                    * Specifies which display field to configure.
                    * Options are:
                        * 1 - 8

                input_channel (int)
                    * Defines which input to display.

                display_units (self.DisplayFieldUnits)
                    * Defines which units to display reading in.

        """
        self.command("DISPFLD {},{},{}".format(field, input_channel, display_units))

    def get_display_field_settings(self, field):
        """Returns the settings of a single display field in custom display mode.

            Args:
                field (int):
                    * Specifies the display field to query.
                    * Options are:
                        * 1 - 8

            Returns:
                (dict):
                    {input_channel: InputChannel, display_units: DisplayFieldUnits}

        """
        display_field_settings = self.query("DISPFLD? " + str(field))
        separated_settings = display_field_settings.split(",")
        return {'input_channel': int(separated_settings[0]),
                'display_units': self.DisplayFieldUnits(int(separated_settings[1]))}

    def set_filter(self, input_channel, filter_enabled, number_of_points=8, filter_reset_threshold=10):
        """Enables or disables a filter for the readings of the specified input channel. Filter is a running
        average that smooths input readings exponentially.

            Args:
                input_channel (str):
                    * The input to set or disable a filter for.

                filter_enabled (bool):
                    * Enables or disables a filter for the input channel.
                    * True for enabled, False for disabled.

                number_of_points (int):
                    * Specifies the number of points used for the filter.
                    * Inputting a larger number of points will slow down the instrument's response to changes in
                        temperature.
                    * Options are:
                        * 2 - 64
                    * Optional if disabling the filter function.

                filter_reset_threshold (int):
                    * Specifies the limit for restarting the filter, represented by a percent of the full scale reading.
                        If raw reading differs from filtered value by more than this threshold, filter averaging resets.
                    * Options are:
                        * 1% - 10%
                    * Optional if disabling the filter function.

        """
        self.command("FILTER " + str(input_channel) + "," + str(int(filter_enabled)) + "," + str(number_of_points) +
                     "," + str(filter_reset_threshold))

    def get_filter(self, input_channel):
        """Retrieves information about the filter set on the specified input channel.

            Args:
                input_channel (str):
                    * The input to query for filter information.

            Returns:
                (dict):
                    {filter_enabled: bool, number_of_points: int, filter_reset_threshold: int}

        """
        filter_information = self.query("FILTER? " + str(input_channel))
        separated_information = filter_information.split(",")
        return {'filter_enabled': bool(int(separated_information[0])),
                'number_of_points': int(separated_information[1]),
                'filter_reset_threshold': int(separated_information[2])}

    def set_ieee_488(self, address, eoi_disable=False, terminator=None):
        """Specifies the IEEE address

            Args:
                address (int):
                    * 1-30 (0 and 31 reserved)
                eoi_disable (bool):
                    * Disables/enables the EOI mode. False = Enabled, True = Disabled
                terminator (int, Terminator):
                    * ieee termination
        """
        if terminator is None:
            terminator = Terminator.CRLF
        self.command("IEEE {},{},{}".format(terminator, int(eoi_disable), address))

    def get_ieee_488(self):
        """Returns the IEEE address set

            Return:
                address (int):
                    * 1-30 (0 and 31 reserved)

        """
        return int(self.query("IEEE?"))

    def set_input_curve(self, input_channel, curve_number):
        """Specifies the curve an input uses for temperature conversion

            Args:
                input_channel (str):
                    Specifies which input to configure

                curve_number (int):
                    * 0 = none, 1-20 = standard curves, 21-59 = user curves

        """
        self.command("INCRV " + str(input_channel) + "," + str(curve_number))
        # Check that the user mapped an input to a curve (not just set the input to no curve)
        if curve_number != 0:
            # Query the curve mapped to input_channel, if the query returns zero,
            # an invalid curve was selected for the specified input
            set_curve = self.get_input_curve(input_channel)
            if set_curve == 0:
                raise InstrumentException("The specified curve type does not match the configured input type")

    def get_input_curve(self, input_channel):
        """Returns the curve number being used for a given input

            Args:
                input_channel (str):
                    Specifies which input to query

            Return:
                curve_number (int):
                    * 0-59

        """
        return int(self.query("INCRV? " + str(input_channel)))

    def set_input_type(self, input_group, sensor_type, compensation=None):
        """

        Parameters
        ----------
        input_group: A (1-4) or B (5-8)
        sensor_type
        compensation: bool or None

        Returns
        -------

        """
        if compensation is not None:
            compensation_term = ',{}'.format(int(compensation))
        else:
            compensation_term = ''
        self.command('INTYPE {},{}'.format(input_group, sensor_type) + compensation_term)

    def get_input_type(self, input_group):
        response = self.query("INPUT? {}".format(input_group))
        split_response = response.split(',')
        if len(split_response) > 2:
            compensation = bool(int(split_response[1]))
        else:
            compensation = None
        return self.SensorTypes(int(split_response[0])), compensation

    def get_kelvin_reading(self, input_channel):
        """Returns the temperature value in kelvin of either channel

            Args:
                input_channel:
                    * Selects the channel to retrieve measurement.

            Returns:
                (float):
                    The reading of the sensor in kelvin
        """

        return float(self.query("KRDG? {}".format(input_channel)))

    def get_kelvin_reading_all(self):
        """Returns the temperature value in kelvin of either channel

                    Returns:
                        (list):
                            The reading of the sensor in kelvin
                """
        return [float(i) for i in (self.query("KRDG? {}".format(0))).split(',')]

    def set_keypad_lock(self, state, code):
        """Locks or unlocks front panel keypad (except for alarms and disabling heaters).

            Args:
                state (bool)
                    * Sets the keypad to locked or unlocked. Options are:
                    * False for unlocked or True for locked

                code (int)
                    * Specifies 3 digit lock-out code. Options are:
                    * 000 - 999

        """
        self.command("LOCK " + str(int(state)) + "," + str(code))

    def get_keypad_lock(self):
        """Returns the state of the keypad lock and the lock-out code.

            Return:
                (dict):
                    * [state: bool, code: int]

        """
        output_string = self.query("LOCK?")
        separated_response = output_string.split(",")
        return {'state': bool(int(separated_response[0])),
                'code': int(separated_response[1])}

    def select_interface_mode(self, interface_mode):
        """Selects the mode for the remote interface being used.

            Args:
                interface_mode (InterfaceMode):
                    Object of enum type InterfaceMode representing the desired communication mode.

        """
        self.command("MODE {}".format(interface_mode))

    def get_interface_mode(self):
        """Returns the mode of the remote interface.
            0 = local, 1 = remote, 2 = remote with local lockout.

            Returns:
                (InterfaceMode):
                    Object of enum type InterfaceMode representing the communication mode.

        """
        mode_number = int(self.query("MODE?"))
        return self.InterfaceMode(mode_number)


class Model218Model331Overlap(BaseLakeshoreMonitor):
    SensorTypes = Model325Model331SensorTypes

    def set_alarm_parameters(self, input_channel, alarm_enable, alarm_settings=None):
        """Configures the alarm parameters for an input

            Args:
                input_channel (str):
                    Specifies which input to configure
                alarm_enable (bool):
                    Specifies whether to turn on the alarm for the input, or turn the alarm off.
                alarm_settings (AlarmParameters):
                    See AlarmParameters class. Optional if alarm_enable is set to False

        """

        if alarm_enable:
            if alarm_settings.audible is None:
                audible = 0
            else:
                audible = int(alarm_settings.audible)
            if alarm_settings.visible is None:
                visible = 0
            else:
                visible = int(alarm_settings.visible)
            self.command("ALARM {},{},{},{},{},{},{},{},{}".format(
                input_channel.upper(), int(alarm_enable), alarm_settings.source, alarm_settings.high_value,
                alarm_settings.low_value, alarm_settings.deadband, int(alarm_settings.latch_enable), audible, visible)
            )
        else:
            self.command("ALARM " + str(input_channel.upper()) + "," + str(int(alarm_enable)) + ",0,0,0,0,0,0,0")

    def get_alarm_parameters(self, input_channel):
        """Returns the present state of all alarm parameters

            Args:
                input_channel (str):
                    Specifies which input to configure

            Return:
                (dict):
                    {alarm_enable: bool, alarm_settings: Model224AlarmParameters}

        """
        parameters = self.query("ALARM? " + str(input_channel)).split(",")
        alarm_enable = bool(int(parameters[0]))
        alarm_settings = AlarmParameters(
            float(parameters[1]), float(parameters[2]), float(parameters[3]), bool(int((parameters[4]))),
            bool(int(parameters[5]))
        )
        return {'alarm_enable': alarm_enable,
                'alarm_settings': alarm_settings}

    def get_alarm_status(self, input_channel):
        """Returns the high state and low state of the alarm for the specified channel

            Args:
                input_channel (str)
                    * Specifies which input channel to read from.

            Returns:
                (dict):
                    {high_state: bool, low_state: bool}
                        * high_state (bool)
                            * True if high state is on, False if high state is off

                        * low_state (bool)
                            * True if low state is on, False if low state is off

        """
        response = self.query("ALARMST? " + str(input_channel))
        separated_response = response.split(",")
        return {"input": input_channel,
                "high_state": bool(int(separated_response[0])),
                "low_state": bool(int(separated_response[1]))}

    def set_audible_alarm(self, on=False):
        on_str = str(int(on))
        self.command('ALMB '+on_str)

    def get_audible_alarm(self):
        return bool(int(self.query('ALMB?')))

    def reset_alarm_status(self):
        self.command('ALMRST')

    def set_analog_output_parameters(
            self, output, bipolar_enable, mode, temperature_input, source, high_value, low_value, manual_value
    ):
        """

        Parameters
        ----------
        output: int, Specifies which analog output to configure (1 or 2)
        bipolar_enable: bool, Specifies analog output: 0 = positive only, or 1 = bipolar
        mode: self.AnalogMode or int, Specifies data the analog output monitors: 0 = off, 1 = input, 2 = manual
        temperature_input: Specifies which input to monitor
        source: self.InputSensorUnits or int, Specifies input data. 1 = Kelvin, 2 = Celsius, 3 = sensor units,
            4 = linear equation
        high_value: float, If <mode> = 1, this parameter represents the data at which the analog
            output reaches +100% output
        low_value: float, If <mode> = 1, this parameter represents the data at which the analog
            output reaches -100% output if bipolar, or 0% output if positive only.
        manual_value: float, If <mode> = 2, this parameter is the output of the analog output

        Returns
        -------

        """
        self.command(
            'ANALOG {},{},{},{},{},{},{},{}'.format(
                output, int(bipolar_enable), int(mode), temperature_input, int(source), high_value, low_value,
                manual_value
            )
        )

    def get_analog_output_parameters(self, output):
        response = self.query('ANALOG? {}'.format(output))
        output, bipolar_enable, mode, temperature_input, source, high_value, low_value, manual_value = \
            response.split(',')
        return {
            'output': int(output),
            'bipolar_enable': bool(int(bipolar_enable)),
            'mode': self.AnalogMode(int(mode)),
            'temperature_input': int(temperature_input),
            'source': self.InputSensorUnits(int(source)),
            'high_value': float(high_value),
            'low_value': float(low_value),
            'manual_value': float(manual_value)
        }

    def _get_analog_output_percentage(self, output):
        """Returns the output percentage of the analog voltage output

            Args:
                output (int):
                    * Specifies which analog voltage output to query

            Return:
                (float):
                    * Analog voltage heater output percentage

        """
        return float(self.query("AOUT? {}".format(output)))

    def set_baud_rate(self, rate):
        """

        Parameters
        ----------
        rate : self.Baud or int

        Returns
        -------

        """
        self.command('BAUD {}'.format(rate))

    def get_baud_rate(self):
        return self.Baud(int(self.query('BAUD?')))


'''
    def set_to_factory_defaults(self):
        """Sets all the settings and configurations to their factory default values."""
        self.command("DFLT 99")

    def get_reading_status(self, input_channel):
        """Returns the reading status of any input status flags that may be set.

            Args:
                input_channel (str):
                    * The input to check for reading status flags.
                    * Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

            Returns:
                (dict):
                    {invalid_reading: bool, temperature_under_range: bool, temperature_over_range: bool,
                    sensor_units_zero: bool, sensor_units_over_range: bool}
        """
        flag_code = int(self.query("RDGST? {}".format(input_channel)))
        reading_status = Model224ReadingStatusRegister.from_integer(flag_code)
        return reading_status

    
    def get_sensor_reading(self, input_channel):
        """Returns the sensor reading in the sensor's units.

            Args:
                input_channel:
                    * Selects the channel to retrieve measurement.
                    * Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

            Returns:
                reading (float):
                    * The raw sensor reading in the units of the connected sensor

        """

        return float(self.query("SRDG? {}".format(input_channel)))

   
    def get_all_inputs_celsius_reading(self):
        """Returns the temperature reading in degrees Celsius of all the inputs.

            Returns:
                (dict):
                    {input_a_reading: float, input_b_reading: float, input_c1_reading: float, input_c2_reading: float,
                    input_c3_reading: float, input_c4_reading: float, input_c5_reading: float, input_d1_reading: float,
                    input_d2_reading: float, input_d3_reading: float, input_d4_reading: float, input_d5_reading: float}
        """
        reading = self.query("CRDG? 0")
        separated_readings = reading.split(",")
        return {'input_a_reading': float(separated_readings[0]),
                'input_b_reading': float(separated_readings[1]),
                'input_c1_reading': float(separated_readings[2]),
                'input_c2_reading': float(separated_readings[3]),
                'input_c3_reading': float(separated_readings[4]),
                'input_c4_reading': float(separated_readings[5]),
                'input_c5_reading': float(separated_readings[6]),
                'input_d1_reading': float(separated_readings[7]),
                'input_d2_reading': float(separated_readings[8]),
                'input_d3_reading': float(separated_readings[9]),
                'input_d4_reading': float(separated_readings[10]),
                'input_d5_reading': float(separated_readings[11])}

    def set_input_diode_excitation_current(self, input_channel, diode_current):
        """Sets the excitation current of a diode sensor. Input must be configured for a diode sensor for command
        to work. Current defaults to 10uA.

            Args:
                input_channel (str):
                    * The input to configure the diode excitation current for.

                diode_current (Model224DiodeExcitationCurrent):
                    * The excitation current for the diode sensor.

        """
        self.command("DIOCUR {},{}".format(input_channel, diode_current))

    def get_input_diode_excitation_current(self, input_channel):
        """Returns the diode excitation current for the given diode sensor.

            Args:
                input_channel (str):
                    The diode sensor input to query the current of.

            Returns:
                diode_current (Model224DiodeExcitationCurrent):
                    A member of the Model224DiodeExcitationCurrent enum class.

        """
        diode_current_int = int(self.query("DIOCUR? " + input_channel))
        return Model224DiodeExcitationCurrent(diode_current_int)

    def set_sensor_name(self, channel, sensor_name):
        """Sets a given name to a sensor on the specified channel

            Args:
                channel (str):
                    * Specifies which the sensor to name is on.
                    * Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

                sensor_name(str):
                    * Name user wants to give to the sensor on the specified channel

        """

        self.command("INNAME {},\"{}\"".format(channel, sensor_name))

    def get_sensor_name(self, channel):
        """Returns the name of the sensor on the specified channel

            Args:
                channel (str):
                    * Specifies which input sensor to retrieve name of.
                    * Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

            Returns:
                name (str)
                    * Name associated with the sensor

        """

        return self.query("INNAME? {}".format(channel))

    def set_display_contrast(self, contrast_level):
        """Sets the contrast level for the front panel display

            Args:
                contrast_level (int):
                    * Display contrast for the front panel LCD screen
                    * Options are:
                        * 1 - 32

        """

        self.command("BRIGT {}".format(contrast_level))

    def get_display_contrast(self):
        """Returns the contrast level of front panel display

            Return:
                (int):
                    * Contrast level of the front panel LCD screen

        """

        return int(self.query("BRIGT?"))

    def set_led_state(self, state):
        """Sets the front panel LEDs to on or off.

            Args:
                state (bool)
                    * Sets the LEDs to functional or nonfunctional. Options are:
                    * False for off or True for on

        """
        self.command("LEDS " + str(int(state)))

    def get_led_state(self):
        """Returns whether or not front panel LEDs are enabled.

            Returns:
                state (bool)
                    * Specifies whether front panel LEDs are functional. Returns:
                    * False if disabled, True enabled.

        """
        return bool(int(self.query("LEDS?")))



    def get_min_max_data(self, input_channel):
        """Returns the minimum and maximum data from an input

            Args:
                input_channel (str):
                    Specifies which input to query
            Return:
                min_max_data (dict):
                    * [minimum: float, maximum: float]

        """
        min_max_data = self.query("MDAT? " + str(input_channel)).split(",")
        min_max_dictionary = {"minimum": float(min_max_data[0]),
                              "maximum": float(min_max_data[1])}
        return min_max_dictionary

    def reset_min_max_data(self):
        """Resets the minimum and maximum input data"""
        self.command("MNMXRST")

    

    def set_website_login(self, username, password):
        """Sets the username and password to connect instrument to website.

            Args:
                username (str)
                    * Username to set for login.
                    * Must be less than or equal to 15 characters.
                    * Method automatically puts quotation marks around string, so they are not needed in the
                      string literal passed into the method.

                password (str)
                    * password to set for login.
                    * Must be less than or equal to 15 characters.
                    * Method automatically puts quotation marks around string, so they are not needed in the
                      string literal passed into the method.

        """
        self.command("WEBLOG \"" + username + "\",\"" + password + "\"")

    def get_website_login(self):
        """Returns the set username and password for web login for the instrument.

            Returns:
                (dict):
                    {username: str, password: str}
        """
        username_password = self.query("WEBLOG?")
        separated_string = username_password.split(",")
        # Remove padded whitespace and quotations in the returned username and password
        username = separated_string[0].strip(' "')
        password = separated_string[1].strip(' "')
        return {"username": username,
                "password": password}

    def reset_alarm_status(self):
        """Clears the high and low status of all alarms."""
        self.command("ALMRST")


    def generate_and_apply_soft_cal_curve(self, source_curve, curve_number, serial_number, calibration_point_1,
                                          calibration_point_2=(0, 0), calibration_point_3=(0, 0)):
        """Creates a SoftCal curve from 1-3 temperature/sensor points and a standard curve. Inputs generated curve
        into the given curve number.

            Args:
                source_curve (Model224SoftCalSensorTypes):
                    * The standard curve to use to generate the SoftCal curve from along with calibration points.

                curve_number (int):
                    * The curve number to save the generated curve to.
                    * Options are:
                        * 21 - 59

                serial_number (str):
                    * Serial number of the user curve.
                    * Maximum of 10 characters

                calibration_point_1 (tuple):
                    * Tuple of two floats in the form (temperature_value, sensor_value)

                calibration_point_2 (tuple):
                    * Tuple of two floats in the form (temperature_value, sensor_value)
                    * Optional parameter

                calibration_point_3 (tuple):
                    * Tuple of two floats in the form (temperature_value, sensor_value)
                    * Optional parameter

        """
        self.command("SCAL {},{},{},{},{},{},{},{},{}".format(source_curve, curve_number, serial_number,
                                                              calibration_point_1[0], calibration_point_1[1],
                                                              calibration_point_2[0], calibration_point_2[1],
                                                              calibration_point_3[0], calibration_point_3[1]))

    def get_curve(self, curve):
        """Returns a list of all the data points in a particular curve

            Args:
                curve (int):
                    * Specifies which curve to set

            Return:
                data_points (list):
                    * A list containing every point in the curve represented as a tuple
                        * (sensor_units: float, temp_value: float)

        """

        data_points = []
        true_point_index = 0
        for i in range(0, 200):
            point = self.get_curve_data_point(curve, i + 1)
            data_points.append(point)
            if point[0] != 0 or point[1] != 0:
                true_point_index = i

        # Remove all extraneous points
        data_points = data_points[:true_point_index + 1]

        return data_points

    def set_curve(self, curve, data_points):
        """Method to define a user curve using a list of data points

            Args:
                curve (int):
                    * Specifies which curve to set

                data_points (list):
                    * A list containing every point in the curve represented as a tuple
                        * (sensor_units: float, temp_value: float)

        """

        self.delete_curve(curve)

        for index, point in data_points:
            self.set_curve_data_point(curve, index + 1, point[0], point[1])

    def get_relay_status(self, relay_channel):
        """Returns whether the specified relay is On or Off.

            Args:
                relay_channel (int)
                    * The relay channel to query.
                    * Options are:
                        * 1 or 2

            Returns:
                (bool):
                    * True if relay is on, False if relay is off.
        """
        return bool(int(self.query("RELAYST? " + str(relay_channel))))

    
    def configure_input(self, input_channel, settings):
        """Configures a sensor for measurement input readings.

            Args:
                input_channel (str):
                    The input to configure the input for. Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

                settings (Model224InputSensorSettings):
                    Object of the Model224InputSensorSettings containing information for sensor setup.

        """
        self.command("INTYPE {},{},{},{},{},{}".format(input_channel, settings.sensor_type,
                                                       int(settings.autorange_enabled),
                                                       settings.sensor_range, int(settings.compensation),
                                                       settings.preferred_units))

    def disable_input(self, input_channel):
        """Disables the selected input channel.

            Args:
                input_channel (str):
                    The input to disable. Options are:
                        * A
                        * B
                        * C (1 - 5)
                        * D (1 - 5)

        """
        # Fill all parameters with 0 to disable
        self.command("INTYPE " + str(input_channel) + ",0,0,0,0,0")

    def get_input_configuration(self, input_channel):
        """Returns the configuration settings of the sensor at the specified input channel.

            Args:
                input_channel (str)
                    The input to query. Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

            Returns:
                (Model224InputSensorSettings):
                    Object of type Model224InputSensorSettings containing information about the sensor at the given
                    input_channel

        """
        settings_string = self.query("INTYPE? " + str(input_channel))
        separated_settings = settings_string.split(",")
        # Convert sensor_range depending on sensor type
        sensor_type = int(separated_settings[0])
        if sensor_type == 1:
            sensor_range = Model224DiodeSensorRange(int(separated_settings[2]))
        elif sensor_type == 2:
            sensor_range = Model224PlatinumRTDSensorResistanceRange(int(separated_settings[2]))
        elif sensor_type == 3:
            sensor_range = Model224NTCRTDSensorResistanceRange(int(separated_settings[2]))
        else:
            # Sensor is disabled
            sensor_range = None
        # Create object
        return Model224InputSensorSettings(Model224InputSensorType(sensor_type),
                                           Model224InputSensorUnits(int(separated_settings[4])),
                                           sensor_range,
                                           bool(int(separated_settings[1])),
                                           bool(int(separated_settings[3])))

    def select_remote_interface(self, remote_interface):
        """Selects the remote interface to use for communications.

            Args:
                remote_interface (Model224RemoteInterface):
                    Object of enum type Model224RemoteInterface, representing the type of interface used for
                    communications

        """
        self.command("INTSEL {}".format(remote_interface))

    def get_remote_interface(self):
        """Returns the remote interface being used for communications.

            Returns:
                (Model224RemoteInterface):
                    Object of enum type Model224RemoteInterface representing the interface being used for
                    communications

        """
        interface_number = int(self.query("INTSEL?"))
        return Model224RemoteInterface(interface_number)





    def configure_display(self, display_mode, number_of_fields=0):
        """Configures the display of the instrument.

            Args:
                display_mode (Model224DisplayMode):
                    * Defines what mode to set the display in.
                    * Mode either defines which input to display, or sets up a custom display using display fields.

                number_of_fields (Model224NumberOfFields):
                    * Defines the number of display locations to display.
                    * Only valid if mode is set to CUSTOM

        """
        self.command("DISPLAY {},{}".format(display_mode, number_of_fields))

    def get_display_configuration(self):
        """Returns the mode of the display. If display mode is Custom, this method also returns the number of
        display fields in the custom display.

            Returns:
                (dict):
                    {display_mode: Model224DisplayMode, number_of_fields: Model224NumberOfFields}

        """
        display_settings_string = self.query("DISPLAY?")
        separated_settings = display_settings_string.split(",")
        display_mode = int(separated_settings[0])
        if display_mode != 4:
            return_dictionary = {'display_mode': Model224DisplayMode(display_mode),
                                 'number_of_fields': None}
        else:
            number_of_fields = int(separated_settings[1])
            return_dictionary = {'display_mode': Model224DisplayMode(display_mode),
                                 'number_of_fields': Model224NumberOfFields(number_of_fields)}
        return return_dictionary

    def turn_relay_on(self, relay_number):
        """Turns the specified relay on.

            Args:
                relay_number (int):
                    * The relay to turn on.
                    * Options are:
                        * 1 or 2

        """
        self.command("RELAY {},1,0,0".format(relay_number))

    def turn_relay_off(self, relay_number):
        """Turns the specified relay off.

            Args:
                relay_number (int):
                    * The relay to turn off.
                    * Options are:
                        * 1 or 2

        """
        self.command("RELAY {},0,0,0".format(relay_number))

    def set_relay_alarms(self, relay_number, activating_input_channel, alarm_relay_trigger_type):
        """Sets a relay to turn on and off automatically based on the state of the alarm of the specified input channel.

            Args:
                relay_number (int):
                    * The relay to configure.
                    * Options are:
                        * 1 or 2

                activating_input_channel (str):
                    * Specifies which input alarm activates the relay when the relay is in alarm mode
                    * Only applies if ALARM mode is chosen.
                    * Options are:
                        * A
                        * B
                        * C(1 - 5)
                        * D(1 - 5)

                alarm_relay_trigger_type (Model224RelayControlAlarm):
                    * Specifies the type of alarm that triggers the relay
                    * Only applies if ALARM mode is chosen.

        """
        self.command("RELAY {},2,{},{}".format(relay_number, activating_input_channel, alarm_relay_trigger_type))

    def get_relay_alarm_control_parameters(self, relay_number):
        """Returns the relay alarm configuration for either of the two configurable relays. Relay must be
        configured for alarm mode to retrieve parameters.

            Args:
                relay_number (int)
                    * Specifies which relay to query
                    * Options are:
                        * 1 or 2

            Return:
                (dict):
                    {activating_input_channel: str, alarm_relay_trigger_type: Model224RelayControlAlarm}

        """

        relay_config = self.query("RELAY? {}".format(relay_number)).split(",")
        activating_input_channel = relay_config[1]
        alarm_relay_trigger_type = Model224RelayControlAlarm(int(relay_config[2]))
        return {'activating_input_channel': activating_input_channel,
                'alarm_relay_trigger_type': alarm_relay_trigger_type}

    def get_relay_control_mode(self, relay_number):
        """Returns the configured mode of the specified relay.

            Args:
                relay_number (int):
                    * Specifies which relay to query
                    * Options are:
                        * 1 or 2

            Returns:
                (Model224RelayControlMode):
                    * The configured mode of the relay, represented as an object of the enum type
                        Model224RelayControlMode

        """
        relay_settings = self.query("RELAY? " + str(relay_number))
        split_relay_settings = relay_settings.split(",")
        return Model224RelayControlMode(int(split_relay_settings[0]))
'''


class BaseLakeshoreController(BaseLakeshoreMonitor):
    _heater_error_enum = HeaterError

    def get_heater_output(self, output):
        """Sample heater output in percent, scale is dependent upon the instrument used and heater configuration

            Args:
                output (int):
                    * Heater output to query

            Return:
                (float):
                    * percent of full scale current/voltage/power

        """
        return float(self.query("HTR? {}".format(output)))

    def get_heater_status(self, output):
        """Returns the heater error code state, error is cleared upon querying the heater status

            Args:
                output (int):
                    * Specifies which heater output to query (1 or 2)

            Return:
                (IntEnum):
                     * Object of instrument's HeaterError type

        """
        status_code = int(self.query("HTRST? {}".format(output)))
        return self._heater_error_enum(status_code)

    def set_heater_range(self, output, heater_range):
        """Sets the heater range for a particular output. The range setting has no effect if an output is in
        the off mode, and does not apply to an output in Monitor Out mode. An output in Monitor Out mode is always on.

            Args:
                output (int):
                    * Specifies which output to configure (1 or 2)

                heater_range (IntEnum):
                    * For Outputs 1 and 2 in Current mode:
                        * HeaterRange IntEnum member

        """
        self.command("RANGE {},{}".format(output, heater_range))

    def get_heater_range(self, output):
        """Returns the heater range for a particular output.

            Args:
                output (int):
                    * Specifies which output to configure (1 or 2)

            Return:
                heater_range (IntEnum):
                    * For Outputs 1 and 2 in Current mode:
                        * HeaterRange IntEnum member
        """
        heater_range = int(self.query("RANGE? {}".format(output)))
        heater_range = HeaterRange(heater_range)
        return heater_range

    def set_heater_pid(self, output, gain, integral, derivative):
        """Configure the closed loop control parameters of the heater output.

            Args:
                output (int):
                     * Specifies which output's control loop to configure

                gain (float):
                    * Proportional term in PID control.
                    * This controls how strongly the control output reacts to the present error.

                integral (float):
                    * Integral term in PID control.
                    * This controls how strongly the control output reacts to the past error history

                derivative (float):
                    * Derivative term in PID control
                    * This value controls how quickly the present field setpoint will transition to a new setpoint.
                    * The ramp rate is configured in field units per second.

        """
        self.command("PID {},{},{},{}".format(output, gain, integral, derivative))

    def get_heater_pid(self, output):
        """Returns the closed loop control parameters of the heater output

            Args:
                output (int):
                    * Specifies which output's control loop to query

            Return:
                (dict):
                    * Keys:
                    * "gain": float
                        * Proportional term in PID control.

                    * "integral": float
                        * Integral term in PID control.

                    * "ramp_rate": float
                        * Derivative term in PID control

        """
        pid_values = self.query("PID? {}".format(output))
        pid_values = pid_values.split(",")
        return {"gain": float(pid_values[0]),
                "integral": float(pid_values[1]),
                "ramp_rate": float(pid_values[2])}

    def set_setpoint_ramp_parameter(self, output, ramp_enable, rate_value):
        """Sets the control loop of a particular output

            Args:
                output (int):
                    * Specifies which output's control loop to configure

                ramp_enable (bool):
                    * Specifies whether ramping is off or on (False = Off or True = On)

                rate_value (float):
                    * 0.1 to 100
                    * Specifies setpoint ramp rate in kelvin per minute.
                    * The rate is always positive but will respond to ramps up or down.
                    * A rate of 0 is interpreted as infinite, and will respond as if setpoint ramping were off

        """
        self.command("RAMP {},{},{}".format(output, int(ramp_enable), rate_value))

    def get_setpoint_ramp_parameter(self, output):
        """Returns the control loop parameters of a particular output

            Args:
                output (int):
                    * Specifies which output's control loop to return

            Return:
                (dict):
                    * Keys:
                    * "ramp_enable": bool
                    * "rate_value": float

        """
        parameters = self.query("RAMP? {}".format(output)).split(",")
        return {"ramp_enable": bool(int(parameters[0])),
                "rate_value": float(parameters[1])}

    def get_setpoint_ramp_status(self, output):
        """Returns whether or not the setpoint is ramping

            Args:
                output (int):
                    * Specifies which output's control loop to query

            Return:
                (bool):
                    * Ramp status
                    * False = Not ramping, True = Ramping

        """
        return bool(int(self.query("RAMPST? {}".format(output))))

    def set_setpoint(self, output, setpoint_value):
        """Sets the control setpoint

            Args:
                    output (int):
                        * Specifies which output's control loop to query
                    setpoint_value (float):
                        * Specifies setpoint temperature

        """
        self.command("SETP {},{}".format(output, setpoint_value))

    def get_setpoint(self, output):
        """Returns whether or not the setpoint is ramping

            Args:
                output (int):
                    * Specifies which output's control loop to query

            Return:
                (float):
                    * Control setpoint value
        """
        return float(self.query("SETP? {}".format(output)))
