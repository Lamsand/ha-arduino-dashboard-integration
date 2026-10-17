"""Config flow for HA Arduino Dashboard integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ArduinoDashboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manages the config flow for HA Arduino Dashboard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step when a user adds the integration via the UI."""
        # Makes sure that the integration can only be set up once
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Arduino Dashboard",
                data={},
            )

        # Show the confirmation screen in the UI
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )