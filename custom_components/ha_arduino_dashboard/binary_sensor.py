"""Binary sensors for the HA Arduino Dashboard integration."""
from datetime import datetime
from typing import Callable

from homeassistant.components import mqtt
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN

CONNECTION_TOPIC = "home/connection"
CONNECTION_PAYLOAD = "Yoohoo!"
CONNECTION_TIMEOUT = 15


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Basics connection binary sensor."""
    async_add_entities([BasicsConnectionBinarySensor()])


class BasicsConnectionBinarySensor(BinarySensorEntity):
    """Indicate whether the Arduino recently sent its connection message."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_has_entity_name = True
    _attr_is_on = False
    _attr_name = "Connection"
    _attr_unique_id = "basics_connection"

    def __init__(self) -> None:
        self._cancel_timeout: Callable[[], None] | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Associate this entity with the Basics app device."""
        return {
            "identifiers": {(DOMAIN, "basics")},
            "name": "Arduino Basics Dashboard",
            "manufacturer": "HA Arduino Dashboard",
            "model": "App: Arduino Basics Dashboard",
        }

    async def async_added_to_hass(self) -> None:
        """Subscribe to the Arduino connection message."""
        await super().async_added_to_hass()
        unsubscribe = await mqtt.async_subscribe(
            self.hass, CONNECTION_TOPIC, self._async_message_received
        )
        self.async_on_remove(unsubscribe)
        self.async_on_remove(self._cancel_pending_timeout)

    async def _async_message_received(self, message: ReceiveMessage) -> None:
        """Mark the device online when its expected message is received."""
        if message.payload != CONNECTION_PAYLOAD:
            return

        self._attr_is_on = True
        self._cancel_pending_timeout()
        self._cancel_timeout = async_call_later(
            self.hass, CONNECTION_TIMEOUT, self._async_mark_offline
        )
        self.async_write_ha_state()

    def _cancel_pending_timeout(self) -> None:
        """Cancel the pending offline transition when the entity is removed."""
        if self._cancel_timeout is not None:
            self._cancel_timeout()
            self._cancel_timeout = None

    def _async_mark_offline(self, _now: datetime) -> None:
        """Mark the device offline when no recent connection message exists."""
        self._cancel_timeout = None
        self._attr_is_on = False
        self.async_write_ha_state()
