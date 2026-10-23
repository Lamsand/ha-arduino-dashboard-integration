from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .apps.car import CarApp
from .apps.energy import EnergyApp
from .const import DOMAIN


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Arduino Dashboard integration."""
    options = entry.options
    apps = {}

    if options.get("car_enabled", False):
        car_app = CarApp(hass, entry, options)
        await car_app.async_setup()
        apps["car"] = car_app

    if options.get("energy_enabled", False):
        energy_app = EnergyApp(hass, entry, options)
        await energy_app.async_setup()
        apps["energy"] = energy_app

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = apps
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the integration when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True