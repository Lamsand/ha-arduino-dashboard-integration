"""The HA Arduino Dashboard component."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration via the user interface (ConfigEntry)."""
    hass.data.setdefault(DOMAIN, {})
    
    # Here we will store the active app instances
    hass.data[DOMAIN][entry.entry_id] = {}
    
    _LOGGER.info("HA Arduino Dashboard integration successfully loaded")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Delete the integration when it is disabled."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True