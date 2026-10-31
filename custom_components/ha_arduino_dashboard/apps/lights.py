"""Lights App for HA Arduino Dashboard."""
import logging
from functools import partial

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event

from .base import DashboardApp

_LOGGER = logging.getLogger(__name__)


class LightsApp(DashboardApp):
    """Control configured Home Assistant lights through MQTT."""

    def __init__(self, hass, entry: ConfigEntry, options: dict[str, object]):
        super().__init__(
            hass,
            entry_id=entry.entry_id,
            app_id="lights",
            name="Arduino Lights Dashboard",
        )
        self.entry = entry
        self.lamp_configs = [
            (
                lamp,
                options.get(f"lights_lamp_{lamp}_entity"),
                options.get(f"lights_lamp_{lamp}_on_off") is True,
                options.get(f"lights_lamp_{lamp}_name", ""),
            )
            for lamp in range(1, 7)
        ]
        self.lights = [
            (lamp, entity_id, on_off_only)
            for lamp, entity_id, on_off_only, _name in self.lamp_configs
            if isinstance(entity_id, str) and entity_id
        ]

    async def async_setup(self, enabled: bool = True):
        """Publish lamp configuration and subscribe when the app is enabled."""
        for lamp, entity_id, on_off_only, name in self.lamp_configs:
            await self.publish_data(
                f"lamp{lamp}/enabled",
                "on"
                if enabled and isinstance(entity_id, str) and entity_id
                else "off",
            )
            await self.publish_data(
                f"lamp{lamp}/on-off",
                "on" if on_off_only else "off",
            )
            await self.publish_data(
                f"lamp{lamp}/name",
                name if isinstance(name, str) else "",
            )

        if not enabled:
            return

        await super().async_setup()
        _LOGGER.info("Setting up Lights App...")

        for lamp, entity_id, on_off_only in self.lights:
            topic = f"lights/lamp{lamp}"
            callback = partial(
                self._async_on_mqtt_message,
                entity_id=entity_id,
            )
            unsubscribe = await mqtt.async_subscribe(self.hass, topic, callback)
            self.entry.async_on_unload(unsubscribe)

            if not on_off_only:
                unsubscribe = await mqtt.async_subscribe(
                    self.hass,
                    f"{topic}/br",
                    partial(
                        self._async_on_brightness_message,
                        entity_id=entity_id,
                    ),
                )
                self.entry.async_on_unload(unsubscribe)

        if self.lights:
            unsubscribe = async_track_state_change_event(
                self.hass,
                list({entity_id for _, entity_id, _ in self.lights}),
                self._async_on_light_state_change,
            )
            self.entry.async_on_unload(unsubscribe)

    async def _async_on_mqtt_message(
        self,
        message: ReceiveMessage,
        entity_id: str,
    ) -> None:
        """Toggle a light when its MQTT switch command is received."""
        if message.payload != "Switch":
            return

        await self.hass.services.async_call(
            "light", "toggle", {"entity_id": entity_id}
        )

    async def _async_on_brightness_message(
        self, message: ReceiveMessage, entity_id: str
    ) -> None:
        """Set a light's brightness from its MQTT percentage command."""
        try:
            brightness_pct = int(message.payload)
        except (TypeError, ValueError):
            _LOGGER.warning("Ignoring invalid brightness payload: %s", message.payload)
            return

        if not 0 <= brightness_pct <= 100:
            _LOGGER.warning(
                "Ignoring out-of-range brightness payload: %s", message.payload
            )
            return

        await self.hass.services.async_call(
            "light",
            "turn_on",
            {"entity_id": entity_id, "brightness_pct": brightness_pct},
        )

    async def _async_on_light_state_change(self, event) -> None:
        """Publish changed light state or brightness to its retained MQTT topic."""
        entity_id = event.data.get("entity_id")
        old_state = event.data.get("old_state")
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        for lamp, configured_entity, on_off_only in self.lights:
            if configured_entity != entity_id:
                continue

            if on_off_only:
                if old_state is not None and old_state.state == new_state.state:
                    continue
                payload = new_state.state
            else:
                old_brightness = (
                    old_state.attributes.get("brightness")
                    if old_state is not None
                    else None
                )
                brightness = new_state.attributes.get("brightness")
                if old_brightness == brightness:
                    continue
                payload = (
                    "off" if brightness is None or brightness == 0 else str(brightness)
                )

            await self.publish_data(f"lamp{lamp}", payload, retain=True)
