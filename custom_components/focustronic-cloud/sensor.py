import logging
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
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
            "C": "Calibrating",
            "I": "Idle",
            "U": "U?",
            "T-1": "Testing CA",
            "T-2": "Testing MG",
            "T-3": "Testing PO4",
            "T-5": "Testing OLI",
            "T-6": "Testing KH",
            "T-100": "Testing NO3",
            "T-911": "Stirring",
            "T-912": "912?",
            "T-913": "913?",
            "T-918": "918?",
            "T-920": "Calibrating OLI",
            "T-991": "991?",
            "T-992": "992?",
            "T-993": "993?",
        }.get(data["mcu_status"], data["mcu_status"])
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertronicTestCountSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_lifetime_test_count', "Test count")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["lifetime_test_count"]
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertronicHoseCountSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_current_hose_count', "Hose count")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["settings"]["current_hose_count"]
        self._available = data["is_active"]
        self.async_write_ha_state()


class MastertronicNeedleCountSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_current_needle_count', "Needle count")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["settings"]["current_needle_count"]
        self._available = data["is_active"]
        self.async_write_ha_state()


class MastertronicNeedleCountLimitSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_needle_count_limit', "Needle count limit")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["settings"]["needle_count_limit"]
        self._available = data["is_active"]
        self.async_write_ha_state()


class MastertronicHoseCountLimitSensor(GenericSensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_hose_count_limit', "Hose count limit")
        self._state = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    def handle_api_data(self, data):
        self._state = data["settings"]["hose_count_limit"]
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertroniParamValueSensor(GenericSensor):
    def __init__(self, device, param, unit):
        super().__init__(device, f'{device["serial_number"]}_{param}_value', f'Value of {param}')
        self.param = param
        self._unit = unit
        self._state = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

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

class MastertroniVialReagentSensor(GenericSensor):
    def __init__(self, device, id):
        super().__init__(device, f'{device["serial_number"]}_vial{id}_reagent', f'Vial{id} reagent')
        self.id = id
        self._state = None

    def handle_api_data(self, data):
        for vial in data["parameter-information"]["vials"]:
            if vial["vial_id"] == self.id:
                self._state = vial["reagent_key"]
                break
        self._available = data["is_active"]
        self.async_write_ha_state()

class MastertroniVialVolumeSensor(GenericSensor):
    def __init__(self, device, id):
        super().__init__(device, f'{device["serial_number"]}_vial{id}_remaining_volume', f'Vial{id} remaining volume')
        self.id = id
        self._unit = "ml"
        self._state = None

    def handle_api_data(self, data):
        for vial in data["parameter-information"]["vials"]:
            if vial["vial_id"] == self.id:
                self._state = vial["remaining_volume"] / 100
                break
        self._available = data["is_active"]
        self.async_write_ha_state()
