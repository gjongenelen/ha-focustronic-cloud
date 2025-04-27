import logging
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    for api in hass.data[DOMAIN][entry.entry_id]["apis"]:
        entities = api.factories["sensor"]
        async_add_entities(entities)
        api.api.add_entities(entities)

class GenericSensor(SensorEntity):
    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self.device_info = device
        self._state = None
        self._available = False

    @property
    def state(self):
        return self._state

    @property
    def available(self):
        return self._available

    @property
    def unit_of_measurement(self):
        return getattr(self, "_unit", None)

class MastertronicStatusSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_status', "Status")
        self._state = None

    def handle_api_data(self, data):
        self._state = data["mcu_status"]
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertronicStatusTextSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_status_text', "Status text")
        self._state = None

    def handle_api_data(self, data):
        self._state = {
            "I": "Idle",
            "T-5": "Testing OLI",
        }.get(data["mcu_status"], data["mcu_status"])
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertroniTestCountSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_lifetime_test_count', "Test count")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["lifetime_test_count"]
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertroniParamValueSensor(GenericSensor):
    def __init__(self, device, param, unit):
        super().__init__(device, f'{device["serial_number"]}_{param}_value', f'Value of {param}')
        self.param = param
        self._unit = unit
        self._state = None

    def handle_api_data(self, data):
        for param in data["parameter-information"]["parameters"]:
            if param["parameter"] == f'{self.param.upper()}_VAL':
                if param["value"] < 0:
                    self._state = 0
                else:
                    self._state = param["value"] / param["multiply_factor"]
                break
        self._available = data["is_active"]
        self.async_write_ha_state()
