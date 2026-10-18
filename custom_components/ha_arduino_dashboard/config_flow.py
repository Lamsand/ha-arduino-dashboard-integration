import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

class CustomOptionsFlowHandler(config_entries.OptionsFlow):
    # ... (init en overige methodes blijven hetzelfde)

    async def async_step_add_app(self, user_input=None):
        """Stap voor het toevoegen van een nieuwe auto app met specifieke auto-entiteiten."""
        errors = {}

        if user_input is not None:
            app_id = user_input["app_name"].lower().strip().replace(" ", "_")

            if app_id in self.apps:
                errors["base"] = "app_exists"
            else:
                # Sla alle ingegeven car-entiteiten op onder deze app
                self.apps[app_id] = {
                    "name": user_input["app_name"],
                    "battery_entity": user_input.get("battery_entity"),
                    "range_entity": user_input.get("range_entity"),
                    "odometer_entity": user_input.get("odometer_entity"),
                }
                return self.async_create_entry(title="", data={"apps": self.apps})

        # Formulier met velden voor specifieke auto-sensoren
        schema = vol.Schema(
            {
                vol.Required("app_name", default="Mijn Auto"): str,
                # Batterij / Brandstof niveau sensor
                vol.Required("battery_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "number"],
                        multiple=False,
                    )
                ),
                # Actieradius / Range sensor (optioneel)
                vol.Optional("range_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=False,
                    )
                ),
                # Kilometerstand sensor (optioneel)
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