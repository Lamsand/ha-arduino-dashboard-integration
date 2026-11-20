"""Text entities for the HA Arduino Dashboard integration."""
from homeassistant.components.text import TextEntity
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
    """Set up the Lights app lamp-name text entities."""
    if entry.options.get("lights_enabled", False) is not True:
        return

    async_add_entities([LampNameText(entry, lamp) for lamp in range(1, 7)])


class LampNameText(TextEntity):
    """Allow a configured lamp name to be changed without editing options."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, lamp: int) -> None:
        self._entry = entry
        self._option_key = f"lights_lamp_{lamp}_name"
        self._attr_unique_id = f"lights_lamp_{lamp}_name"
        self._attr_name = f"Lamp {lamp} name"

    @property
    def native_value(self) -> str:
        """Return the lamp name stored in the integration options."""
        value = self._entry.options.get(self._option_key, "")
        return value if isinstance(value, str) else ""

    @property
    def device_info(self) -> DeviceInfo:
        """Associate this entity with the Lights app device."""
        return {
            "identifiers": {(DOMAIN, "lights")},
            "name": "Arduino Lights Dashboard",
            "manufacturer": "HA Arduino Dashboard",
            "model": "App: Arduino Lights Dashboard",
        }

    async def async_set_value(self, value: str) -> None:
        """Save the new lamp name in the integration options."""
        options = dict(self._entry.options)
        options[self._option_key] = value
        self.hass.config_entries.async_update_entry(self._entry, options=options)
        self.async_write_ha_state()
