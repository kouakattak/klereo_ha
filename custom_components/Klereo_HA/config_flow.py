"""Config flow for Klereo."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_LOGIN, CONF_PASSWORD, CONF_POOL_ID
from .api import KlereoApiClient

class KlereoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = KlereoApiClient(
                user_input[CONF_LOGIN], 
                user_input[CONF_PASSWORD], 
                user_input[CONF_POOL_ID], 
                session
            )
            token = await client.async_get_token()
            
            if token:
                return self.async_create_entry(title="Ma Piscine Klereo", data=user_input)
            else:
                errors["base"] = "auth_error"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LOGIN): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_POOL_ID): str,
            }),
            errors=errors,
        )