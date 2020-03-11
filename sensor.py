import voluptuous as vol
import logging
from homeassistant.components.sensor import PLATFORM_SCHEMA
from huawei_solar import HuaweiSolar
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_HOST
from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
)


_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Huawei Inverter"

ATTR_MODEL_ID = "model_id"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_NB_PV_STRINGS = "nb_pv_strings"
ATTR_RATED_POWER = "rated_power"
ATTR_GRID_STANDARD = "grid_standard"
ATTR_GRID_COUNTRY = "grid_country"
ATTR_DAILY_YIELD = "daily_yield"
ATTR_TOTAL_YIELD = "total_yield"
ATTR_DAY_POWER_PEAK = "day_active_power_peak"
ATTR_REACTIVE_POWER = "reactive_power"
ATTR_POWER_FACTOR = "power_factor"
ATTR_EFFICIENCY = "efficiency"
ATTR_GRID_FREQUENCY = "grid_frequency"
ATTR_GRID_VOLTAGE = "grid_voltage"
ATTR_GRID_CURRENT = "grid_current"
ATTR_STARTUP_TIME = "startup_time"
ATTR_SHUTDOWN_TIME = "shutdown_time"
ATTR_INTERNAL_TEMPERATURE = "internal_temperature"
ATTR_DEVICE_STATUS = "device_status"
ATTR_NB_OPTIMIZERS = "nb_optimizers"
ATTR_NB_ONLINE_OPTIMIZERS = "nb_online_optimizers"
ATTR_SYSTEM_TIME = "system_time"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({vol.Required(CONF_HOST): cv.string})


def setup_platform(hass, config, add_entities, discovery_info=None):
    _LOGGER.debug("Setup Huawei Inverter")

    host = config[CONF_HOST]
    try:
        inverter = HuaweiSolar(host)
    except Exception as ex:
        _LOGGER.error("could not connect to Huawei inverter: %s", ex)
        return False
    _LOGGER.debug("created inverter")
    entities = []

    entities.append(HuaweiSolarSensor(inverter))

    add_entities(entities, True)
    _LOGGER.debug("added entities")


class HuaweiSolarSensor(Entity):
    def __init__(self, inverter):
        self._inverter = inverter
        self._hidden = False
        self._unit = POWER_WATT
        self._icon = "mdi:solar-power"
        self._name = self._inverter.get("model_name").value
        self._model_id = self._inverter.get("model_id").value
        self._serial_number = self._inverter.get("serial_number").value
        self._nb_pv_strings = self._inverter.get("nb_pv_strings").value
        self._pv_strings_voltage = [None] * self._nb_pv_strings
        self._pv_strings_current = [None] * self._nb_pv_strings
        self._rated_power = self._inverter.get("rated_power").value
        self._nb_optimizers = self._inverter.get("nb_optimizers").value
        tmp = self._inverter.get("grid_code").value
        self._grid_standard = tmp.standard
        self._grid_country = tmp.country

        self._last_update = None

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        attributes = {
            ATTR_MODEL_ID: self._model_id,
            ATTR_SERIAL_NUMBER: self._serial_number,
            ATTR_NB_PV_STRINGS: self._nb_pv_strings,
            ATTR_RATED_POWER: self._rated_power,
            ATTR_GRID_STANDARD: self._grid_standard,
            ATTR_GRID_COUNTRY: self._grid_country,
            ATTR_DAILY_YIELD: self._daily_yield,
            ATTR_TOTAL_YIELD: self._total_yield,
            ATTR_DAY_POWER_PEAK: self._day_active_power_peak,
            ATTR_REACTIVE_POWER: self._reactive_power,
            ATTR_POWER_FACTOR: self._power_factor,
            ATTR_EFFICIENCY: self._efficiency,
            ATTR_GRID_FREQUENCY: self._grid_frequency,
            ATTR_GRID_VOLTAGE: self._grid_voltage,
            ATTR_GRID_CURRENT: self._grid_current,
            ATTR_STARTUP_TIME: self._startup_time.isoformat(),
            ATTR_SHUTDOWN_TIME: self._shutdown_time.isoformat(),
            ATTR_INTERNAL_TEMPERATURE: self._internal_temperature,
            ATTR_DEVICE_STATUS: self._device_status,
            ATTR_NB_OPTIMIZERS: self._nb_optimizers,
            ATTR_NB_ONLINE_OPTIMIZERS: self._nb_online_optimizers,
            ATTR_SYSTEM_TIME: self._system_time,
        }
        # for i in range(int(self._nb_pv_strings)):
        #    attributes[f"pv_string_{i+1:02}_voltage"] = self._pv_strings_voltage[i]
        #    attributes[f"pv_string_{i+1:02}_current"] = self._pv_strings_current[i]
        return attributes

    @property
    def unit_of_measurement(self):
        return self._unit

    def update(self):
        self._state = self._inverter.get("active_power").value
        self._daily_yield = self._inverter.get("daily_yield_energy").value
        self._total_yield = self._inverter.get("accumulated_yield_energy").value
        self._reactive_power = self._inverter.get("reactive_power").value
        self._power_factor = self._inverter.get("power_factor").value
        self._efficiency = self._inverter.get("efficiency").value
        self._grid_voltage = self._inverter.get("grid_voltage").value
        self._grid_current = self._inverter.get("grid_current").value
        self._grid_frequency = self._inverter.get("grid_frequency").value
        self._startup_time = self._inverter.get("startup_time").value.time()
        self._shutdown_time = self._inverter.get("shutdown_time").value.time()
        self._system_time = self._inverter.get("system_time").value
        self._internal_temperature = self._inverter.get("internal_temperature").value
        self._device_status = self._inverter.get("device_status").value
        self._nb_online_optimizers = self._inverter.get("nb_online_optimizers").value
        self._day_active_power_peak = self._inverter.get("day_active_power_peak").value
        for i in range(int(self._nb_pv_strings)):
            self._pv_strings_voltage[i] = self._inverter.get(
                f"pv_{i+1:02}_voltage"
            ).value
            self._pv_strings_current[i] = self._inverter.get(
                f"pv_{i+1:02}_current"
            ).value