import logging
from homeassistant.components.number import NumberEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    for api in hass.data[DOMAIN][entry.entry_id]["apis"]:
        entities = api.factories["number"]
        async_add_entities(entities)
        api.api.add_entities(entities)

class RedSeaNumberEntity(NumberEntity):

    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self.device_info = device
        self._attr_native_value = 0
        self._available = False

    @property
    def available(self):
        return self._available
