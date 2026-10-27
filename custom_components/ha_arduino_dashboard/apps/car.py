"""Car App for HA Arduino Dashboard."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event

from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


class CarApp(DashboardApp):
    """Car App pushing Home Assistant states to Arduino via MQTT."""

    def __init__(self, hass, entry: ConfigEntry, options: dict[str, object]):
        super().__init__(
            hass,
            entry_id=entry.entry_id,
            app_id="car",
            name="Arduino Car Dashboard",
        )
        self.entry = entry
        self.entity_topic_map = {
            entity_id: topic
            for option, topic in (
                ("car_battery_entity", "battery"),
                ("car_range_entity", "cruisingRange"),
                ("car_charging_power_entity", "chargingPower"),
                ("car_target_charge_entity", "targetCharge"),
            )
            if isinstance((entity_id := options.get(option)), str) and entity_id
        }

    async def async_setup(self):
        """Set up device registration and HA state tracking for the Car app."""
        await super().async_setup()  # Registreert het apparaat in HA
        _LOGGER.info("Setting up Car App...")

        if self.entity_topic_map:
            unsubscribe = async_track_state_change_event(
                self.hass, list(self.entity_topic_map), self._async_on_ha_state_change
            )
            self.entry.async_on_unload(unsubscribe)

        for entity_id, topic in self.entity_topic_map.items():
            state = self.hass.states.get(entity_id)
            if state is not None and state.state not in ("unknown", "unavailable"):
                await self.publish_data(topic, state.state, retain=True)

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT (retained)."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            # retain=True keeps the message on the MQTT broker.
            await self.publish_data(subtopic, str(new_state.state), retain=True)
            _LOGGER.debug(
                "Pushed %s state (%s) to MQTT topic car/%s (retained)",
                entity_id,
                new_state.state,
                subtopic,
            )