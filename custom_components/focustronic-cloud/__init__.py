import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import *
from .const import DOMAIN

PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data[DOMAIN][entry.entry_id] = {}

    apiI = FocustronicApi(entry.data["token"])

    tank = await apiI.getTank()

    apis = []
    for mastertronic in tank["data"]["mastertronics"]:
        apis.append(MastertronicApi(apiI, {
            "identifiers": {(DOMAIN, mastertronic["id"])},
            "name": mastertronic["friendly_name"],
            "sw_version": mastertronic["firmware_version"],
            "hw_version": mastertronic["mcu_version"],
            "serial_number": mastertronic["serial_number"]
        }, mastertronic["id"]))

    stop_event = asyncio.Event()

    async def poll_data():
        while not stop_event.is_set():
            for api in apis:
                try:
                    await api.update()
                except Exception as e:
                    _LOGGER.warning("Failed to fetch_data: %s", e)

            await asyncio.sleep(15)

    task = asyncio.create_task(poll_data())

    hass.data[DOMAIN][entry.entry_id]["stop_event"] = stop_event
    hass.data[DOMAIN][entry.entry_id]["task"] = task

    hass.data[DOMAIN][entry.entry_id]["apis"] = apis
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    data = hass.data[DOMAIN].pop(entry.entry_id)
    data["stop_event"].set()
    data["task"].cancel()
    try:
        await data["task"]
    except asyncio.CancelledError:
        pass
    return True
