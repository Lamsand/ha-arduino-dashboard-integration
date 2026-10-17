"""Base class for all Arduino Dashboard Apps."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components import mqtt
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DashboardApp:
    """Base class for an Arduino Dashboard App."""

    def __init__(self, hass: HomeAssistant, entry_id: str, app_id: str, name: str):
        self.hass = hass
        self.entry_id = entry_id
        self.app_id = app_id
        self.name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Link parameters to a specific unique Device in Home Assistant."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.app_id)},
            name=self.name,
            manufacturer="HA Arduino Dashboard",
            model=f"App: {self.name}",
        )

    async def register_device(self):
        """Register this app as an individual Device in Home Assistant."""
        device_registry = dr.async_get(self.hass)
        device_registry.async_get_or_create(
            config_entry_id=self.entry_id,
            identifiers={(DOMAIN, self.app_id)},
            name=self.name,
            manufacturer="HA Arduino Dashboard",
            model=f"App: {self.name}",
        )

    async def async_setup(self):
        """Called during setup to register the device and listeners."""
        await self.register_device()

    async def publish_data(self, subtopic: str, payload: str, retain: bool = True):
        """Publish payload to MQTT topic with retain enabled by default."""
        topic = f"{self.app_id}/{subtopic}"
        await mqtt.async_publish(self.hass, topic, payload, retain=retain)