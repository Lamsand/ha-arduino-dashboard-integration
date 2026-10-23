from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

DOMAIN = "ha_arduino_dashboard"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Instellen van de hoofd-entry."""
    apps = entry.options.get("apps", {})

    # 1. Sla de data op in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = apps

    # 2. Registreer elk sub-apparaat in de Device Registry
    device_reg = dr.async_get(hass)

    # Houd bij welke apparaten er in deze run actief zijn
    active_device_identifiers = set()

    for app_id, app_config in apps.items():
        identifier = (DOMAIN, f"{entry.entry_id}_{app_id}")
        active_device_identifiers.add(identifier)

        device_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={identifier},
            name=app_config["name"],
            manufacturer="Mijn Merk",
            model="Virtuele App",
        )

    # 3. Verwijder apparaten uit HA die door de gebruiker zijn gewist via 'delete_app'
    existing_devices = dr.async_entries_for_config_entry(
        device_reg, entry.entry_id
    )
    for dev in existing_devices:
        # Als het apparaat niet meer in de actieve lijst staat, verwijderen
        if not any(ident in active_device_identifiers for ident in dev.identifiers):
            device_reg.async_remove_device(dev.id)

    # 4. Luister naar wijzigingen vanuit de Options Flow
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Herlaad de integratie direct zodra er een app is toegevoegd, bewerkt of verwijderd."""
    await hass.config_entries.async_reload(entry.entry_id)
    
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Ruim de integratie op wanneer Home Assistant haar uitlaadt."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True