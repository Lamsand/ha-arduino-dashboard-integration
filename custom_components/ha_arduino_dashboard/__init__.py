"""HA Arduino Dashboard component."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .apps.car import CarApp

_LOGGER = logging.getLogger(__name__)

# List of active dashboard apps
APPS = [
    CarApp,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Arduino Dashboard from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    loaded_apps = []

    # Instantiate and set up each registered app
    for app_cls in APPS:
        app_instance = app_cls(hass)
        await app_instance.async_setup()
        loaded_apps.append(app_instance)

    hass.data[DOMAIN][entry.entry_id] = loaded_apps
    _LOGGER.info("HA Arduino Dashboard loaded %d app(s)", len(loaded_apps))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload HA Arduino Dashboard config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True