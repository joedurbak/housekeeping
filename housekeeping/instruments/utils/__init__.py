from housekeeping.instruments.temperature.model_325 import Model325
from housekeeping.instruments.temperature.model_331 import Model331
from housekeeping.instruments.temperature.model_218 import Model218
from housekeeping.instruments.temperature.cryotel_avc import CryotelAVC
from housekeeping.instruments.pressure.lesker392 import Lesker392
from housekeeping.instruments.pressure.pfeiffer import PfeifferDualGauge

temperature_controller = {
    "Model325": Model325,
    "Model331": Model331,
    "CryotelAVC": CryotelAVC
}

temperature_monitor = {
    "Model218": Model218
}

pressure = {
    "Lesker392": Lesker392,
    "PfeifferDualGauge": PfeifferDualGauge
}
