"""Switch entities for the HA Arduino Dashboard integration."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lights app on-off configuration switches."""
    if entry.options.get("lights_enabled", False) is not True:
        return

    async_add_entities([LampOnOffSwitch(entry, lamp) for lamp in range(1, 7)])


class LampOnOffSwitch(SwitchEntity):
    """Configure whether a lamp should only use on/off commands."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, lamp: int) -> None:
        self._entry = entry
        self._option_key = f"lights_lamp_{lamp}_on_off"
        self._attr_unique_id = self._option_key
        self._attr_name = f"Lamp {lamp} on-off"

    @property
    def is_on(self) -> bool:
        """Return whether on/off-only mode is enabled."""
        return self._entry.options.get(self._option_key, False) is True

    @property
    def device_info(self) -> DeviceInfo:
        """Associate this entity with the Lights app device."""
        return {
            "identifiers": {(DOMAIN, "lights")},
            "name": "Arduino Lights Dashboard",
            "manufacturer": "HA Arduino Dashboard",
            "model": "App: Arduino Lights Dashboard",
        }

    async def async_turn_on(self, **kwargs: object) -> None:
        """Enable on/off-only mode for this lamp."""
        await self._async_set_value(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Disable on/off-only mode for this lamp."""
        await self._async_set_value(False)

    async def _async_set_value(self, value: bool) -> None:
        """Save the setting in the integration options."""
        options = dict(self._entry.options)
        options[self._option_key] = value
        self.hass.config_entries.async_update_entry(self._entry, options=options)
        self.async_write_ha_state()
