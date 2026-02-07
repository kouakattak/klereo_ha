"""Capteurs Klereo."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # On définit les capteurs ici
    sensors = [
        KlereoSensor(coordinator, "Température Eau", "temp_eau", "°C", SensorDeviceClass.TEMPERATURE),
        KlereoSensor(coordinator, "Température Air", "temp_air", "°C", SensorDeviceClass.TEMPERATURE),
        KlereoSensor(coordinator, "pH", "ph", "pH", None),
        KlereoSensor(coordinator, "Redox", "redox", "mV", SensorDeviceClass.VOLTAGE),
        KlereoSensor(coordinator, "Volet", "volet", None, None), # Texte: Ouvert/Fermé
        KlereoSensor(coordinator, "Bidon pH", "bidon_ph", None, None),
        KlereoSensor(coordinator, "Bidon Chlore", "bidon_chlore", None, None),
        KlereoSensor(coordinator, "Pompe Vitesse", "pompe_vitesse", None, None),
        KlereoSensor(coordinator, "Mode Filtration", "mode_filtration", None, None),
    ]
    async_add_entities(sensors)

class KlereoSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, sensor_type, unit, device_class):
        super().__init__(coordinator)
        self._name = name
        self._type = sensor_type
        self._unit = unit
        self._device_class = device_class
        self._attr_unique_id = f"klereo_{sensor_type}"
        self._attr_name = f"Piscine {name}"

    @property
    def native_value(self):
        data = self.coordinator.data
        probes = data.get("probes", [])
        outs = data.get("outs", [])

        # Logique de récupération selon le type
        if self._type == "temp_eau":
            idx = data.get("EauCapteur", 0)
            return self._get_probe_val(probes, idx)
            
        if self._type == "temp_air":
            return self._get_probe_val(probes, 1)

        if self._type == "ph":
            idx = data.get("pHCapteur", 0)
            return round(self._get_probe_val(probes, idx), 2)

        if self._type == "redox":
            idx = data.get("TraitCapteur", 0)
            return round(self._get_probe_val(probes, idx))

        if self._type == "volet":
            val = self._get_probe_val(probes, 8)
            return "Fermé" if val >= 100 else "Ouvert"

        if self._type == "bidon_ph":
            val = self._get_probe_val(probes, 6)
            return "OK" if val == 100 else "Vide"

        if self._type == "bidon_chlore":
            val = self._get_probe_val(probes, 7)
            return "OK" if val == 100 else "Vide"
            
        if self._type == "pompe_vitesse":
            # Pompe = Outs index 1
            pump = next((o for o in outs if o["index"] == 1), None)
            if not pump: return "Inconnu"
            val = pump["realStatus"]
            if val == 0: return "Arrêt"
            if val == 1: return "Vitesse 1"
            if val == 2: return "Vitesse 2"
            if val == 3: return "Vitesse 3"
            return str(val)

        if self._type == "mode_filtration":
            pump = next((o for o in outs if o["index"] == 1), None)
            if not pump: return "Inconnu"
            m = pump["mode"]
            if m == 0: return "Manuel"
            if m == 1: return "Plages Horaires"
            if m == 3: return "Régulé (Auto)"
            return f"Mode {m}"

        return None

    def _get_probe_val(self, probes, idx):
        for p in probes:
            if p["index"] == idx:
                return p["filteredValue"]
        return 0

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def device_class(self):
        return self._device_class