from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .api import API
from .const import PLATFORMS
from .coordinator import Coordinator

async def async_setup_entry(hass, entry):
    coordinator = Coordinator(hass, entry, API(async_get_clientsession(hass), entry.data["car_id"], entry.data["token"]))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def reload_entry(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
