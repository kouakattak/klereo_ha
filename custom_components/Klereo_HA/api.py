"""API Client for Klereo."""
import aiohttp
import logging
import json

# L'import relatif (.) est OBLIGATOIRE dans Home Assistant
from .const import API_URL_JWT, API_URL_DETAILS, API_URL_SET

_LOGGER = logging.getLogger(__name__)

class KlereoApiClient:
    def __init__(self, login, password, pool_id, session):
        self._login = login
        self._password = password
        self._pool_id = str(pool_id)
        self._session = session
        self._token = None

    async def _request(self, method, url, data_str, is_auth=False):
        """Exécute une requête propre (stateless)."""
        
        # 1. Nettoyage des cookies pour éviter les conflits Session vs Token
        self._session.cookie_jar.clear()

        # 2. Headers
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Home Assistant/2026"
        }
        
        # Ajout du Token (JWT)
        if not is_auth and self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.request(method, url, data=data_str, headers=headers) as resp:
                text = await resp.text()
                
                if resp.status != 200:
                    _LOGGER.error("Erreur HTTP Klereo %s : %s", resp.status, text[:200])
                    return None

                return json.loads(text)
        except json.JSONDecodeError:
            _LOGGER.error("Erreur décodage JSON Klereo: %s", text[:200])
            return None
        except Exception as err:
            _LOGGER.error("Erreur connexion Klereo: %s", err)
            return None

    async def async_get_token(self):
        """Récupère le JWT."""
        payload = f"login={self._login}&password={self._password}&version=391-H&app=Api"
        
        data = await self._request("POST", API_URL_JWT, payload, is_auth=True)
        
        if data:
            # On privilégie le champ 'jwt' (celui qui marche !)
            self._token = data.get("jwt")
            
            if not self._token:
                # Fallback au cas où
                self._token = data.get("token")
                
            return self._token
        return None

    async def async_get_data(self):
        """Récupère les données."""
        if not self._token:
            await self.async_get_token()

        payload = f"poolID={self._pool_id}&lang=fr"
        
        data = await self._request("POST", API_URL_DETAILS, payload)

        # Gestion expiration / session invalide
        if data and "status" in data and data["status"] == "error":
            _LOGGER.warning("Token Klereo expiré (%s), renouvellement...", data.get("detail"))
            await self.async_get_token()
            # Retry
            return await self._request("POST", API_URL_DETAILS, payload)
            
        return data

    async def async_set_out(self, out_idx, new_mode, new_state):
        """Envoie une commande."""
        if not self._token:
            await self.async_get_token()
            
        payload = f"poolID={self._pool_id}&outIdx={out_idx}&newMode={new_mode}&newState={new_state}&comMode=1&lang=fr"
        
        data = await self._request("POST", API_URL_SET, payload)
        
        # On renvoie True si on a reçu une réponse valide
        return data is not None