"""Energy App for HA Arduino Dashboard."""
import logging
import math

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.event import async_track_state_change_event

from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


def _numeric_payload(state) -> str:
    """Return a finite numeric value or Home Assistant's unavailable state."""
    if state is None:
        return STATE_UNAVAILABLE

    try:
        value = float(str(state))
    except (TypeError, ValueError):
        return STATE_UNAVAILABLE

    if not math.isfinite(value):
        return STATE_UNAVAILABLE

    return str(state)


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

        for entity_id, topic in self.entity_topic_map.items():
            state = self.hass.states.get(entity_id)
            payload = _numeric_payload(state.state if state is not None else None)
            await self.publish_data(topic, payload, retain=True)

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT (retained)."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            payload = _numeric_payload(new_state.state if new_state is not None else None)
            await self.publish_data(subtopic, payload, retain=True)
            _LOGGER.debug(
                "Pushed %s state (%s) to MQTT topic energy/%s (retained)",
                entity_id,
                payload,
                subtopic,
            )
