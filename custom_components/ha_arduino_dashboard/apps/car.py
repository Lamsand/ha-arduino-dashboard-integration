"""Car App for HA Arduino Dashboard."""
import logging
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
            "sensor.garage_id_7_accuniveau": "battery",
            "sensor.evcc_laadpaal_charge_power": "chargingPower",
            "sensor.garage_id_7_elektrisch_bereik": "cruisingRange",
            "number.evcc_laadpaal_vehicle_limit_soc": "targetCharge",
        }

        # Luister naar wijzigingen van de opgegeven Home Assistant entiteiten
        self.hass.states.async_track_state_change_event(
            list(self.entity_topic_map.keys()),
            self._async_on_ha_state_change,
        )

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT when tracked entity changes."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        
        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        # Haal het specifieke topic-pad op uit de mapping
        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            # Pushed het bericht naar: arduino/car/<subtopic>
            await self.publish_data(subtopic, str(new_state.state))
            _LOGGER.debug("Pushed %s state (%s) to MQTT topic car/%s", entity_id, new_state.state, subtopic)