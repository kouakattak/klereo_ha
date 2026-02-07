"""API Client for Klereo."""
import aiohttp
import logging
from .const import API_URL_JWT, API_URL_DETAILS, API_URL_SET

_LOGGER = logging.getLogger(__name__)

class KlereoApiClient:
    def __init__(self, login, password, pool_id, session):
        self._login = login
        self._password = password
        self._pool_id = pool_id
        self._session = session
        self._token = None

    async def async_get_token(self):
        """Récupère le token JWT."""
        payload = {
            "login": self._login,
            "password": self._password,
            "version": "391-H",
            "app": "Api"
        }
        async with self._session.post(API_URL_JWT, data=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                self._token = data.get("token")
                return self._token
            else:
                _LOGGER.error("Erreur Auth Klereo: %s", resp.status)
                return None

    async def async_get_data(self):
        """Récupère les données de la piscine."""
        if not self._token:
            await self.async_get_token()

        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {"poolID": self._pool_id, "lang": "fr"}

        async with self._session.post(API_URL_DETAILS, headers=headers, data=payload) as resp:
            # Si token expiré (401), on le renouvelle et on réessaie une fois
            if resp.status == 401 or resp.status == 403:
                _LOGGER.info("Token Klereo expiré, renouvellement...")
                await self.async_get_token()
                headers = {"Authorization": f"Bearer {self._token}"}
                async with self._session.post(API_URL_DETAILS, headers=headers, data=payload) as resp2:
                    return await resp2.json()
            
            return await resp.json()

    async def async_set_out(self, out_idx, new_mode, new_state):
        """Envoie une commande."""
        if not self._token:
            await self.async_get_token()
            
        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
            "poolID": self._pool_id,
            "outIdx": out_idx,
            "newMode": new_mode,
            "newState": new_state,
            "comMode": 1,
            "lang": "fr"
        }
        async with self._session.post(API_URL_SET, headers=headers, data=payload) as resp:
            return resp.status == 200