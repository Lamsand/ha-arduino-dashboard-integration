import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .apps.basics import BasicsApp
from .apps.car import CarApp
from .apps.energy import EnergyApp
from .apps.lights import LightsApp
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR]


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
    device_registry = dr.async_get(hass)
    setup_complete = False
    try:
        basics_app = BasicsApp(hass, entry)
        await basics_app.async_setup()
        apps["basics"] = basics_app

        if options.get("car_enabled", False):
            car_app = CarApp(hass, entry, options)
            await car_app.async_setup()
            apps["car"] = car_app
        else:
            _remove_app_device(device_registry, "car")

        if options.get("energy_enabled", False):
            energy_app = EnergyApp(hass, entry, options)
            await energy_app.async_setup()
            apps["energy"] = energy_app
        else:
            _remove_app_device(device_registry, "energy")

        lights_app = LightsApp(hass, entry, options)
        lights_enabled = options.get("lights_enabled", False) is True
        await lights_app.async_setup(enabled=lights_enabled)
        if lights_enabled:
            apps["lights"] = lights_app
        else:
            _remove_app_device(device_registry, "lights")

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        entry.async_on_unload(entry.add_update_listener(update_listener))
        setup_complete = True
    finally:
        if not setup_complete:
            entries.pop(entry.entry_id, None)

    return True


def _remove_app_device(device_registry: dr.DeviceRegistry, app_id: str) -> None:
    """Remove a disabled app's device from the Home Assistant device registry."""
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, app_id)}
    )
    if device is not None:
        device_registry.async_remove_device(device.id)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload the integration when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok
