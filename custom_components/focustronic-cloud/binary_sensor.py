import logging

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    for api in hass.data[DOMAIN][entry.entry_id]["apis"]:
        entities = api.factories["binary_sensor"]
        async_add_entities(entities)
        api.api.add_entities(entities)


class GenericBinarySensor(BinarySensorEntity):
    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self.device_info = device
        self._attr_is_on = False
        self._available = False

    @property
    def available(self):
        return self._available


class MastertronicActiveSensor(GenericBinarySensor):
    def __init__(self, device):
        super().__init__(device, f'{device["serial_number"]}_active', "Active")
        self._attr_is_on = False

    def handle_api_data(self, data):
        self._attr_is_on = data["is_active"]
        self._available = True
        self.async_write_ha_state()
