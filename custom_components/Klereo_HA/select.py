from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

OPTIONS = ["Arrêt", "Vitesse 1", "Vitesse 2", "Vitesse 3", "Régulé (Auto)", "Plages Horaires"]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([KlereoPumpSelect(coordinator, client)])

class KlereoPumpSelect(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Piscine Contrôle Pompe"
        self._attr_unique_id = "klereo_pump_control"
        self._attr_icon = "mdi:pump-cog"
        self._attr_options = OPTIONS

    @property
    def current_option(self):
        outs = self.coordinator.data.get("outs", [])
        pump = next((o for o in outs if o["index"] == 1), None)
        if not pump: return "Arrêt"
        
        m = pump["mode"]
        s = pump["status"] # On utilise la consigne, pas realStatus

        if m == 3: return "Régulé (Auto)"
        if m == 1: return "Plages Horaires"
        if m == 0:
            if s == 0: return "Arrêt"
            if s == 1: return "Vitesse 1"
            if s == 2: return "Vitesse 2"
            if s == 3: return "Vitesse 3"
        return "Arrêt"

    async def async_select_option(self, option: str) -> None:
        new_mode = 0
        new_state = 0

        if option == "Régulé (Auto)":
            new_mode = 3
            new_state = 2
        elif option == "Plages Horaires":
            new_mode = 1
            new_state = 2
        elif option == "Arrêt":
            new_mode = 0
            new_state = 0
        elif option == "Vitesse 1":
            new_mode = 0
            new_state = 1
        elif option == "Vitesse 2":
            new_mode = 0
            new_state = 2
        elif option == "Vitesse 3":
            new_mode = 0
            new_state = 3

        # Envoi commande pompe (index 1)
        await self._client.async_set_out(1, new_mode, new_state)
        await self.coordinator.async_request_refresh()