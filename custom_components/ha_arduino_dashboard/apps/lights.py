"""Lights App for HA Arduino Dashboard."""
import logging
from functools import partial

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_state_change_event

from ..const import DEFAULT_LAMP_IMAGE, DEFAULT_LAMP_NAME, LAMP_IMAGE_OPTIONS
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
        self._options = dict(options)
        self.lamp_configs = [
            (
                lamp,
                options.get(f"lights_lamp_{lamp}_entity"),
                options.get(f"lights_lamp_{lamp}_enabled", True) is True,
                options.get(f"lights_lamp_{lamp}_on_off") is True,
                self._get_lamp_name(options, lamp),
            )
            for lamp in range(1, 7)
        ]
        self.lights = [
            (lamp, entity_id, on_off_only)
            for lamp, entity_id, lamp_enabled, on_off_only, _name in self.lamp_configs
            if lamp_enabled
            if isinstance(entity_id, str) and entity_id
        ]

    @staticmethod
    def _get_lamp_name(options: dict[str, object], lamp: int) -> str:
        """Return the configured lamp name or its default."""
        name = options.get(f"lights_lamp_{lamp}_name")
        return name if isinstance(name, str) and name else DEFAULT_LAMP_NAME

    @staticmethod
    def _get_lamp_image(options: dict[str, object], lamp: int) -> str:
        """Return the configured lamp image or its default."""
        image = options.get(f"lights_lamp_{lamp}_image")
        return (
            image
            if isinstance(image, str) and image in LAMP_IMAGE_OPTIONS
            else DEFAULT_LAMP_IMAGE
        )

    @classmethod
    def _get_lamp_image_payload(cls, options: dict[str, object], lamp: int) -> str:
        """Return the MQTT value for the selected lamp image."""
        image = cls._get_lamp_image(options, lamp)
        return "Custom" if image == "Custom (Arduino code defined)" else image

    async def async_setup(self, enabled: bool = True):
        """Publish lamp configuration and subscribe when the app is enabled."""
        for lamp, entity_id, lamp_enabled, on_off_only, name in self.lamp_configs:
            await self.publish_data(
                f"lamp{lamp}/enabled",
                "on"
                if enabled
                and lamp_enabled
                and isinstance(entity_id, str)
                and entity_id
                else "off",
            )
            await self.publish_data(
                f"lamp{lamp}/on-off",
                "on" if on_off_only else "off",
            )
            await self.publish_data(
                f"lamp{lamp}/name",
                name,
            )
            await self.publish_data(
                f"lamp{lamp}/image",
                self._get_lamp_image_payload(self._options, lamp),
            )

        if not enabled:
            return

        await super().async_setup()
        _LOGGER.info("Setting up Lights App...")

        for lamp, entity_id, _on_off_only in self.lights:
            topic = f"lights/lamp{lamp}"
            callback = partial(
                self._async_on_mqtt_message,
                entity_id=entity_id,
            )
            unsubscribe = await mqtt.async_subscribe(self.hass, topic, callback)
            self.entry.async_on_unload(unsubscribe)

            unsubscribe = await mqtt.async_subscribe(
                self.hass,
                f"{topic}/br",
                partial(
                    self._async_on_brightness_message,
                    lamp=lamp,
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

    async def async_apply_option_updates(self, options: dict[str, object]) -> bool:
        """Apply lamp setting changes without reloading the integration."""
        changed_keys = {
            key
            for key in self._options.keys() | options.keys()
            if self._options.get(key) != options.get(key)
        }
        if not changed_keys:
            return True

        supported_keys = {
            f"lights_lamp_{lamp}_{suffix}"
            for lamp in range(1, 7)
            for suffix in ("name", "on_off", "image")
        }
        if not changed_keys.issubset(supported_keys):
            return False

        self._options = dict(options)
        self.lamp_configs = [
            (
                lamp,
                entity_id,
                lamp_enabled,
                options.get(f"lights_lamp_{lamp}_on_off") is True,
                self._get_lamp_name(options, lamp),
            )
            for lamp, entity_id, lamp_enabled, _, _ in self.lamp_configs
        ]
        self.lights = [
            (lamp, entity_id, on_off_only)
            for lamp, entity_id, lamp_enabled, on_off_only, _name in self.lamp_configs
            if lamp_enabled
            if isinstance(entity_id, str) and entity_id
        ]

        for lamp in range(1, 7):
            if f"lights_lamp_{lamp}_name" in changed_keys:
                await self.publish_data(
                    f"lamp{lamp}/name",
                    self._get_lamp_name(options, lamp),
                )
            if f"lights_lamp_{lamp}_on_off" in changed_keys:
                await self.publish_data(
                    f"lamp{lamp}/on-off",
                    "on"
                    if options.get(f"lights_lamp_{lamp}_on_off") is True
                    else "off",
                )
            if f"lights_lamp_{lamp}_image" in changed_keys:
                await self.publish_data(
                    f"lamp{lamp}/image",
                    self._get_lamp_image_payload(options, lamp),
                )

        return True

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
        self, message: ReceiveMessage, lamp: int, entity_id: str
    ) -> None:
        """Set a light's brightness from its MQTT percentage command."""
        if self.lamp_configs[lamp - 1][3]:
            return

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
