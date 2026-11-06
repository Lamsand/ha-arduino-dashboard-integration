import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

DOMAIN = "ha_arduino_dashboard"


class ArduinoDashboardConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Initial configuration when adding the integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="HA Arduino Dashboard",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CustomOptionsFlowHandler()


class CustomOptionsFlowHandler(config_entries.OptionsFlow):
    """Dashboard settings."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            options = {
                key: value
                for key, value in self.config_entry.options.items()
                if value is not None
            }
            for app_options in user_input.values():
                if isinstance(app_options, dict):
                    options.update(
                        {
                            key: value
                            for key, value in app_options.items()
                            if value is not None
                        }
                    )
            return self.async_create_entry(title="", data=options)

        opts = self.config_entry.options

        lights_schema = {
            vol.Optional(
                "lights_enabled",
                default=opts.get("lights_enabled", False),
            ): selector.BooleanSelector(),
        }
        for lamp in range(1, 7):
            entity_key = f"lights_lamp_{lamp}_entity"
            name_key = f"lights_lamp_{lamp}_name"
            lights_schema.update(
                {
                    vol.Optional(
                        entity_key,
                        **(
                            {"default": opts[entity_key]}
                            if opts.get(entity_key)
                            else {}
                        ),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["light"],
                            multiple=False,
                        )
                    ),
                    vol.Optional(
                        f"lights_lamp_{lamp}_on_off",
                        default=opts.get(f"lights_lamp_{lamp}_on_off", False),
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        name_key,
                        **(
                            {"default": opts[name_key]}
                            if isinstance(opts.get(name_key), str)
                            else {}
                        ),
                    ): selector.TextSelector(),
                }
            )

        schema = vol.Schema(
            {
                vol.Optional("car"): section(
                    vol.Schema(
                        {
                            vol.Optional(
                                "car_enabled",
                                default=opts.get("car_enabled", False),
                            ): selector.BooleanSelector(),
                            vol.Optional(
                                "car_battery_entity",
                                **(
                                    {"default": opts["car_battery_entity"]}
                                    if opts.get("car_battery_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor", "number"],
                                    multiple=False,
                                )
                            ),
                            vol.Optional(
                                "car_range_entity",
                                **(
                                    {"default": opts["car_range_entity"]}
                                    if opts.get("car_range_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor"],
                                    multiple=False,
                                )
                            ),
                            vol.Optional(
                                "car_charging_power_entity",
                                **(
                                    {"default": opts["car_charging_power_entity"]}
                                    if opts.get("car_charging_power_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor"],
                                    multiple=False,
                                )
                            ),
                            vol.Optional(
                                "car_target_charge_entity",
                                **(
                                    {"default": opts["car_target_charge_entity"]}
                                    if opts.get("car_target_charge_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor", "number"],
                                    multiple=False,
                                )
                            ),
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Optional("energy"): section(
                    vol.Schema(
                        {
                            vol.Optional(
                                "energy_enabled",
                                default=opts.get("energy_enabled", False),
                            ): selector.BooleanSelector(),
                            vol.Optional(
                                "energy_pv_entity",
                                **(
                                    {"default": opts["energy_pv_entity"]}
                                    if opts.get("energy_pv_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor"],
                                    multiple=False,
                                )
                            ),
                            vol.Optional(
                                "energy_smart_meter_entity",
                                **(
                                    {"default": opts["energy_smart_meter_entity"]}
                                    if opts.get("energy_smart_meter_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor"],
                                    multiple=False,
                                )
                            ),
                            vol.Optional(
                                "energy_total_consumption_entity",
                                **(
                                    {
                                        "default": opts[
                                            "energy_total_consumption_entity"
                                        ]
                                    }
                                    if opts.get("energy_total_consumption_entity")
                                    else {}
                                ),
                            ): selector.EntitySelector(
                                selector.EntitySelectorConfig(
                                    domain=["sensor"],
                                    multiple=False,
                                )
                            ),
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Optional("lights"): section(
                    vol.Schema(lights_schema),
                    {"collapsed": True},
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )