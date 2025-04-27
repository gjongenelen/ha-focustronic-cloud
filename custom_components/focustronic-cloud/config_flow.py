import voluptuous as vol
from homeassistant import config_entries

from .api import login
from .const import DOMAIN


class FocustronicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=vol.Schema({
                vol.Required("email"): str,
                vol.Required("password"): str,
            }), errors=errors)

        token, user_hash = await login(user_input["email"], user_input["password"])

        return self.async_create_entry(
            title=user_input["email"],
            data={
                "token": token,
                "hash": user_hash
            },
        )
