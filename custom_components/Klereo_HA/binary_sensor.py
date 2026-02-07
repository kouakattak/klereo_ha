from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([KlereoLightBinary(coordinator)])

class KlereoLightBinary(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Piscine Eclairage Etat"
        self._attr_unique_id = "klereo_light_binary"
        self._attr_device_class = BinarySensorDeviceClass.LIGHT

    @property
    def is_on(self):
        outs = self.coordinator.data.get("outs", [])
        light = next((o for o in outs if o["index"] == 0), None)
        return light["realStatus"] == 1 if light else False