"""Energy App for HA Arduino Dashboard."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


class EnergyApp(DashboardApp):
    """Energy App pushing Home Assistant states to Arduino via MQTT."""

    def __init__(self, hass, entry: ConfigEntry, options: dict[str, object]):
        super().__init__(
            hass,
            entry_id=entry.entry_id,
            app_id="energy",
            name="Arduino Energy Dashboard",
        )
        self.entry = entry
        self.entity_topic_map = {
            entity_id: topic
            for option, topic in (
                ("energy_pv_entity", "currentProduction"),
                ("energy_smart_meter_entity", "currentImport"),
                ("energy_total_consumption_entity", "currentConsumption"),
            )
            if isinstance((entity_id := options.get(option)), str) and entity_id
        }

    async def async_setup(self):
        """Set up device registration and HA state tracking for the Energy app."""
        await super().async_setup()
        _LOGGER.info("Setting up Energy App...")

        if self.entity_topic_map:
            unsubscribe = async_track_state_change_event(
                self.hass, list(self.entity_topic_map), self._async_on_ha_state_change
            )
            self.entry.async_on_unload(unsubscribe)

        self.entry.async_on_unload(
            async_track_time_interval(
                self.hass,
                self._async_publish_short,
                timedelta(seconds=5),
            )
        )
        self.entry.async_on_unload(
            async_track_time_interval(
                self.hass,
                self._async_publish_long,
                timedelta(seconds=30),
            )
        )

        for entity_id, topic in self.entity_topic_map.items():
            state = self.hass.states.get(entity_id)
            if state is not None and state.state not in ("unknown", "unavailable"):
                await self.publish_data(topic, state.state, retain=True)

    async def _async_publish_short(self, now):
        """Publish the short energy value every five seconds."""
        await self.publish_data("newValue", "Short", retain=False)

    async def _async_publish_long(self, now):
        """Publish the long energy value every thirty seconds."""
        await self.publish_data("newValue", "Long", retain=False)

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT (retained)."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            await self.publish_data(subtopic, str(new_state.state), retain=True)
            _LOGGER.debug(
                "Pushed %s state (%s) to MQTT topic energy/%s (retained)",
                entity_id,
                new_state.state,
                subtopic,
            )
