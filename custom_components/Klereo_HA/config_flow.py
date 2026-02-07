"""Config flow for Klereo."""
import voluptuous as vol
import hashlib  # <--- Import pour le hachage
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_LOGIN, CONF_PASSWORD, CONF_POOL_ID
from .api import KlereoApiClient

class KlereoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            # 1. On récupère le mot de passe clair saisi
            clear_password = user_input[CONF_PASSWORD]
            
            # 2. On le convertit en SHA1 (hex digest)
            # C'est ce hash qui sera envoyé à l'API et stocké dans Home Assistant
            hashed_password = hashlib.sha1(clear_password.encode("utf-8")).hexdigest()
            
            # 3. On met à jour user_input avec le hash pour le stockage
            user_input[CONF_PASSWORD] = hashed_password

            # 4. On teste la connexion avec le hash
            session = async_get_clientsession(self.hass)
            client = KlereoApiClient(
                user_input[CONF_LOGIN], 
                user_input[CONF_PASSWORD], # C'est maintenant le hash
                user_input[CONF_POOL_ID], 
                session
            )
            
            # On tente de récupérer le token pour valider que le login/pass(sha1) fonctionnent
            token = await client.async_get_token()
            
            if token:
                # Si on a le token, on crée l'entrée avec le mot de passe hashé
                return self.async_create_entry(title="Ma Piscine Klereo", data=user_input)
            else:
                errors["base"] = "auth_error"

        # Le formulaire reste standard (l'utilisateur ne voit pas que ça va être hashé)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_LOGIN): str,
                vol.Required(CONF_PASSWORD): str, # Saisie en clair ici
                vol.Required(CONF_POOL_ID): str,
            }),
            errors=errors,
        )