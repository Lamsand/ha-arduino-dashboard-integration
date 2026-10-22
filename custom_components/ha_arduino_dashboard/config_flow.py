import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

# Gebruik exact de domeinnaam uit je manifest.json
DOMAIN = "ha_arduino_dashboard"


class ArduinoDashboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """De primaire ConfigFlow die HA nodig heeft om de integratie te herkennen."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Voorkom dat de hoofdintegratie dubbel wordt toegevoegd."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="HA Arduino Dashboard", data={})

        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Koppel de OptionsFlow voor het beheren van de apps."""
        return CustomOptionsFlowHandler(config_entry)


class CustomOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.apps = dict(config_entry.options.get("apps", {}))

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(
            step_id="init", menu_options=["add_app"]
        )

    async def async_step_add_app(self, user_input=None):
        """Stap voor het toevoegen van een nieuwe auto app met specifieke auto-entiteiten."""
        errors = {}

        if user_input is not None:
            app_id = user_input["app_name"].lower().strip().replace(" ", "_")

            if app_id in self.apps:
                errors["base"] = "app_exists"
            else:
                self.apps[app_id] = {
                    "name": user_input["app_name"],
                    "battery_entity": user_input.get("battery_entity"),
                    "range_entity": user_input.get("range_entity"),
                    "odometer_entity": user_input.get("odometer_entity"),
                }
                return self.async_create_entry(title="", data={"apps": self.apps})

        schema = vol.Schema(
            {
                vol.Required("app_name", default="Mijn Auto"): str,
                vol.Required("battery_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "number"],
                        multiple=False,
                    )
                ),
                vol.Optional("range_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=False,
                    )
                ),
                vol.Optional("odometer_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=False,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="add_app", data_schema=schema, errors=errors
        )