from simple_pid import PID


class BaseController:
    def __init__(self, p, i, d, setpoint, monitor, power_supply):
        self.p = p
        self.i = i
        self.d = d
        self.setpoint = setpoint
        self.monitor = monitor
        self.power_supply = power_supply
