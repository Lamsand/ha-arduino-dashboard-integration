"""Car App for HA Arduino Dashboard."""
import logging
from homeassistant.helpers.event import async_track_state_change_event
from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


class CarApp(DashboardApp):
    """Car App pushing Home Assistant states to Arduino via MQTT."""

    def __init__(self, hass, entry_id: str):
        super().__init__(hass, entry_id=entry_id, app_id="car", name="Arduino Car Dashboard")

    async def async_setup(self):
        """Set up device registration and HA state tracking for the Car app."""
        await super().async_setup()  # Registreert het apparaat in HA
        _LOGGER.info("Setting up Car App...")

        self.entity_topic_map = {
            "sensor.garage_id_7_accuniveau": "battery",
            "sensor.evcc_laadpaal_charge_power": "chargingPower",
            "sensor.garage_id_7_elektrisch_bereik": "cruisingRange",
            "number.evcc_laadpaal_vehicle_limit_soc": "targetCharge",
        }

        async_track_state_change_event(
            self.hass,
            list(self.entity_topic_map.keys()),
            self._async_on_ha_state_change,
        )

    async def _async_on_ha_state_change(self, event):
        """Send updated state to Arduino over MQTT (retained)."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return

        subtopic = self.entity_topic_map.get(entity_id)
        if subtopic:
            # retain=True zorgt dat het bericht op de MQTT broker bewaard blijft
            await self.publish_data(subtopic, str(new_state.state), retain=True)
            _LOGGER.debug(
                "Pushed %s state (%s) to MQTT topic car/%s (retained)",
                entity_id,
                new_state.state,
                subtopic,
            )