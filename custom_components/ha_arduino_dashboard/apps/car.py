"""Car App for HA Arduino Dashboard."""
import logging
from homeassistant.helpers.event import async_track_state_change_event
from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


class CarApp(DashboardApp):
    """Car App pushing Home Assistant states to Arduino via MQTT."""

    def __init__(self, hass):
        super().__init__(hass, app_id="car", name="Arduino Car Dashboard")

    async def async_setup(self):
        """Set up HA state tracking for the Car app."""
        _LOGGER.info("Setting up Car App...")

        # Mapping van HA entiteiten naar de gewenste MQTT topics
        self.entity_topic_map = {
            "sensor.car_battery_level": "battery",
            "sensor.car_charging_power": "charginPower",
            "sensor.car_cruising_range": "cruisingRange",
            "number.car_target_charge": "targetCharge",
        }

        # Gebruik de geïmporteerde event helper in plaats van self.hass.states
        async_track_state_change_event(
            self.hass,
            list(self.entity_topic_map.keys()),
            self._async_on_ha_state_change,
        )

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT when tracked entity changes."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            await self.publish_data(subtopic, str(new_state.state))
            _LOGGER.debug(
                "Pushed %s state (%s) to MQTT topic car/%s",
                entity_id,
                new_state.state,
                subtopic,
            )