"""Configuration flow for the roof weather station."""

from __future__ import annotations

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN, NAME


class RoofWeatherConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle setup from Home Assistant's UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create the single station entry; no credentials are needed."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=NAME, data={})
