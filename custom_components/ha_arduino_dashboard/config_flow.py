import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

DOMAIN = "ha_arduino_dashboard"


class ArduinoDashboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Eerste configuratie bij het toevoegen van de integratie."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="HA Arduino Dashboard", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CustomOptionsFlowHandler(config_entry)


class CustomOptionsFlowHandler(config_entries.OptionsFlow):
    """Eén enkele pagina voor alle instellingen."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Sla alle ingevoerde opties direct op
            return self.async_create_entry(title="", data=user_input)

        # Haal huidige/opgeslagen instellingen op als standaardwaarden
        opts = self.config_entry.options

        schema = vol.Schema(
            {
                # 1. Schakelaar voor Car (Aan / Uit)
                vol.Optional("car_enabled", default=opts.get("car_enabled", False)): bool,
                # 2. Entiteit invoervelden voor de auto
                vol.Optional("car_battery_entity", default=opts.get("car_battery_entity")): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "number"], multiple=False)
                ),
                vol.Optional("car_range_entity", default=opts.get("car_range_entity")): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"], multiple=False)
                ),
                vol.Optional("car_odometer_entity", default=opts.get("car_odometer_entity")): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"], multiple=False)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)