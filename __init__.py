"""Initialisation de l'intégration Klereo."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_LOGIN, CONF_PASSWORD, CONF_POOL_ID
from .api import KlereoApiClient

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor", "switch", "select"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup de l'intégration depuis la config UI."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    client = KlereoApiClient(
        entry.data[CONF_LOGIN],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_POOL_ID],
        session
    )

    async def async_update_data():
        """Récupération des données (Polling)."""
        try:
            data = await client.async_get_data()
            if not data or "response" not in data:
                raise UpdateFailed("Données Klereo invalides")
            return data["response"][0] # On retourne directement l'objet piscine
        except Exception as err:
            raise UpdateFailed(f"Erreur de communication: {err}")

    # Mise à jour toutes les 10 secondes (comme demandé)
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="klereo_pool",
        update_method=async_update_data,
        update_interval=timedelta(seconds=10),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok