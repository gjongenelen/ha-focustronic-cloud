import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    for api in hass.data[DOMAIN][entry.entry_id]["apis"]:
        entities = api.factories["switch"]
        async_add_entities(entities)
        api.api.add_entities(entities)


class MastertronicSwitchEntity(SwitchEntity):

    def __init__(self, device, id, name):
        self._attr_unique_id = id
        self.name = name
        self.device_info = device
        self._attr_is_on = False
        self._available = False

    @property
    def available(self):
        return self._available
