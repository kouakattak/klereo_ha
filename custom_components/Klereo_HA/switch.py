from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([KlereoLightSwitch(coordinator, client)])

class KlereoLightSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, client):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Piscine Lumière"
        self._attr_unique_id = "klereo_light_switch"
        self._attr_icon = "mdi:lightbulb-spot"

    @property
    def is_on(self):
        outs = self.coordinator.data.get("outs", [])
        light = next((o for o in outs if o["index"] == 0), None)
        return light["realStatus"] == 1 if light else False

    async def async_turn_on(self, **kwargs):
        await self._client.async_set_out(0, 0, 1) # outIdx=0, mode=0, state=1
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self._client.async_set_out(0, 0, 0) # outIdx=0, mode=0, state=0
        await self.coordinator.async_request_refresh()