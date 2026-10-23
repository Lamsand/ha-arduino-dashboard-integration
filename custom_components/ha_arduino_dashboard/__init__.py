import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .apps.car import CarApp
from .apps.energy import EnergyApp
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Arduino Dashboard integration."""
    entries = hass.data.setdefault(DOMAIN, {})
    if entry.entry_id in entries:
        _LOGGER.warning(
            "Skipping duplicate setup for config entry %s", entry.entry_id
        )
        return True

    apps = {}
    entries[entry.entry_id] = apps
    options = entry.options
    setup_complete = False
    try:
        if options.get("car_enabled", False):
            car_app = CarApp(hass, entry, options)
            await car_app.async_setup()
            apps["car"] = car_app

        if options.get("energy_enabled", False):
            energy_app = EnergyApp(hass, entry, options)
            await energy_app.async_setup()
            apps["energy"] = energy_app

        entry.async_on_unload(entry.add_update_listener(update_listener))
        setup_complete = True
    finally:
        if not setup_complete:
            entries.pop(entry.entry_id, None)

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the integration when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True