import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

DOMAIN = "ha_arduino_dashboard"


class ArduinoDashboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """De primaire ConfigFlow voor de integratie."""

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
    """Beheerpaneel voor het toevoegen, bewerken en verwijderen van apps."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.apps = dict(config_entry.options.get("apps", {}))
        self.selected_app_id = None

    async def async_step_init(self, user_input=None):
        """Hoofdmenu bij het openen van de instellingen."""
        menu = ["add_app"]
        if self.apps:
            menu.extend(["edit_app", "delete_app"])

        return self.async_show_menu(step_id="init", menu_options=menu)

    # --- APP TOEVOEGEN ---
    async def async_step_add_app(self, user_input=None):
        """Stap voor het toevoegen van een nieuwe auto app."""
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

    # --- APP BEWERKEN ---
    async def async_step_edit_app(self, user_input=None):
        """Kies welke app je wilt bewerken."""
        if user_input is not None:
            self.selected_app_id = user_input["select_app"]
            return await self.async_step_edit_app_details()

        app_options = {app_id: data["name"] for app_id, data in self.apps.items()}
        schema = vol.Schema({vol.Required("select_app"): vol.In(app_options)})
        return self.async_show_form(step_id="edit_app", data_schema=schema)

    async def async_step_edit_app_details(self, user_input=None):
        """Pas de instellingen van de gekozen app aan."""
        current_data = self.apps[self.selected_app_id]

        if user_input is not None:
            self.apps[self.selected_app_id] = {
                "name": current_data["name"],
                "battery_entity": user_input.get("battery_entity"),
                "range_entity": user_input.get("range_entity"),
                "odometer_entity": user_input.get("odometer_entity"),
            }
            return self.async_create_entry(title="", data={"apps": self.apps})

        schema = vol.Schema(
            {
                vol.Required(
                    "battery_entity", default=current_data.get("battery_entity")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "number"], multiple=False
                    )
                ),
                vol.Optional(
                    "range_entity", default=current_data.get("range_entity")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"], multiple=False)
                ),
                vol.Optional(
                    "odometer_entity", default=current_data.get("odometer_entity")
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor"], multiple=False)
                ),
            }
        )

        return self.async_show_form(step_id="edit_app_details", data_schema=schema)

    # --- APP VERWIJDEREN ---
    async def async_step_delete_app(self, user_input=None):
        """Verwijder een gekozen app."""
        if user_input is not None:
            app_id = user_input["select_app"]
            if app_id in self.apps:
                del self.apps[app_id]
            return self.async_create_entry(title="", data={"apps": self.apps})

        app_options = {app_id: data["name"] for app_id, data in self.apps.items()}
        schema = vol.Schema({vol.Required("select_app"): vol.In(app_options)})
        return self.async_show_form(step_id="delete_app", data_schema=schema)