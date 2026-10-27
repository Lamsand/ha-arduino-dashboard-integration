"""Basics App for HA Arduino Dashboard."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_change

from .base import DashboardApp


class BasicsApp(DashboardApp):
    """Basics App publishing the current time to the dashboard."""

    def __init__(self, hass, entry: ConfigEntry):
        super().__init__(
            hass,
            entry_id=entry.entry_id,
            app_id="basics",
            name="Arduino Basics Dashboard",
        )
        self.entry = entry

    async def async_setup(self):
        """Set up device registration and publish time on each minute boundary."""
        await super().async_setup()
        self.entry.async_on_unload(
            async_track_time_change(
                self.hass,
                self._async_publish_time,
                second=0,
            )
        )

    async def _async_publish_time(self, now):
        """Publish the local time at the start of each minute."""
        await self.publish_data("home/time", now.strftime("%H:%M"))
