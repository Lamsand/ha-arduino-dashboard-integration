"""Select entities for the HA Arduino Dashboard integration."""
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_LAMP_IMAGE, DOMAIN, LAMP_IMAGE_OPTIONS


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lights app lamp-image selectors."""
    if entry.options.get("lights_enabled", False) is not True:
        return

    async_add_entities([LampImageSelect(entry, lamp) for lamp in range(1, 7)])


class LampImageSelect(SelectEntity):
    """Select the image displayed for a configured lamp."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_options = list(LAMP_IMAGE_OPTIONS)

    def __init__(self, entry: ConfigEntry, lamp: int) -> None:
        self._entry = entry
        self._option_key = f"lights_lamp_{lamp}_image"
        self._attr_unique_id = self._option_key
        self._attr_name = f"Lamp {lamp} image"

    @property
    def current_option(self) -> str:
        """Return the selected image or the default."""
        value = self._entry.options.get(self._option_key)
        return (
            value
            if isinstance(value, str) and value in LAMP_IMAGE_OPTIONS
            else DEFAULT_LAMP_IMAGE
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Associate this entity with the Lights app device."""
        return {
            "identifiers": {(DOMAIN, "lights")},
            "name": "Arduino Lights Dashboard",
            "manufacturer": "HA Arduino Dashboard",
            "model": "App: Arduino Lights Dashboard",
        }

    async def async_select_option(self, option: str) -> None:
        """Save the selected image in the integration options."""
        if option not in LAMP_IMAGE_OPTIONS:
            raise ValueError(f"Unsupported lamp image: {option}")

        options = dict(self._entry.options)
        options[self._option_key] = option
        self.hass.config_entries.async_update_entry(self._entry, options=options)
        self.async_write_ha_state()
