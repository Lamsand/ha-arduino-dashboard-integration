from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .apps.car import CarApp
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Arduino Dashboard integration."""
    options = entry.options
    app = None
    if options.get("car_enabled", False):
        app = CarApp(hass, entry, options)
        await app.async_setup()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = app
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the integration when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True