"""Base class for all Arduino Dashboard Apps."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.components import mqtt
from homeassistant.helpers.device_registry import DeviceInfo

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DashboardApp:
    """Base class for an Arduino Dashboard App."""

    def __init__(self, hass: HomeAssistant, app_id: str, name: str):
        self.hass = hass
        self.app_id = app_id
        self.name = name

    @property
    def device_info(self) -> DeviceInfo:
        """Links entities/topics to a specific unique device in Home Assistant."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.app_id)},
            name=self.name,
            manufacturer="Arduino Dashboard",
            model=f"App: {self.name}",
        )

    async def async_setup(self):
        """Called when the app is set up to initialize listeners or MQTT subscriptions."""
        pass

    async def publish_data(self, subtopic: str, payload: str, retain: bool = False):
        """Helper function to easily publish data to a specific MQTT topic."""
        topic = f"{self.app_id}/{subtopic}"
        await mqtt.async_publish(self.hass, topic, payload, retain=retain)