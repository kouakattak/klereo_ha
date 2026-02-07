"""Capteurs Klereo."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # On définit les capteurs
    sensors = [
        # Températures (On utilise la constante officielle pour C°)
        KlereoSensor(
            coordinator, 
            "Température Eau", 
            "temp_eau", 
            UnitOfTemperature.CELSIUS, 
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT
        ),
        KlereoSensor(
            coordinator, 
            "Température Air", 
            "temp_air", 
            UnitOfTemperature.CELSIUS, 
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT
        ),
        
        # Chimie (On utilise des strings simples pour éviter les ImportErrors)
        KlereoSensor(
            coordinator, 
            "pH", 
            "ph", 
            "pH", 
            None, # Le pH n'a pas toujours de device_class selon les versions HA
            SensorStateClass.MEASUREMENT
        ),
        KlereoSensor(
            coordinator, 
            "Redox", 
            "redox", 
            "mV", 
            SensorDeviceClass.VOLTAGE, 
            SensorStateClass.MEASUREMENT
        ),
        
        # Etats (Texte ou sans unité)
        KlereoSensor(coordinator, "Volet", "volet", None, None, None),
        KlereoSensor(coordinator, "Bidon pH", "bidon_ph", None, None, None),
        KlereoSensor(coordinator, "Bidon Chlore", "bidon_chlore", None, None, None),
        KlereoSensor(coordinator, "Pompe Vitesse", "pompe_vitesse", None, None, None),
        KlereoSensor(coordinator, "Mode Filtration", "mode_filtration", None, None, None),
    ]
    async_add_entities(sensors)

class KlereoSensor(CoordinatorEntity, SensorEntity):
    """Représentation d'un capteur Klereo."""

    def __init__(self, coordinator, name, sensor_type, unit, device_class, state_class):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        
        # --- DEFINITION DES ATTRIBUTS NATIFS ---
        self._attr_name = f"Piscine {name}"
        self._attr_unique_id = f"klereo_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        probes = data.get("probes", [])
        outs = data.get("outs", [])

        try:
            # Logique de récupération selon le type
            if self._sensor_type == "temp_eau":
                idx = data.get("EauCapteur", 0)
                return self._get_probe_val(probes, idx)
                
            if self._sensor_type == "temp_air":
                # L'air est souvent sur l'index 1
                return self._get_probe_val(probes, 1)

            if self._sensor_type == "ph":
                idx = data.get("pHCapteur", 0)
                val = self._get_probe_val(probes, idx)
                return round(val, 2) if val is not None else None

            if self._sensor_type == "redox":
                idx = data.get("TraitCapteur", 0)
                val = self._get_probe_val(probes, idx)
                return round(val) if val is not None else None

            if self._sensor_type == "volet":
                val = self._get_probe_val(probes, 8)
                return "Fermé" if val and val >= 100 else "Ouvert"

            if self._sensor_type == "bidon_ph":
                val = self._get_probe_val(probes, 6)
                return "OK" if val == 100 else "Vide"

            if self._sensor_type == "bidon_chlore":
                val = self._get_probe_val(probes, 7)
                return "OK" if val == 100 else "Vide"
                
            if self._sensor_type == "pompe_vitesse":
                pump = next((o for o in outs if o["index"] == 1), None)
                if not pump: return "Inconnu"
                val = pump.get("realStatus")
                if val == 0: return "Arrêt"
                if val == 1: return "Vitesse 1"
                if val == 2: return "Vitesse 2"
                if val == 3: return "Vitesse 3"
                return str(val)

            if self._sensor_type == "mode_filtration":
                pump = next((o for o in outs if o["index"] == 1), None)
                if not pump: return "Inconnu"
                m = pump.get("mode")
                if m == 0: return "Manuel"
                if m == 1: return "Plages Horaires"
                if m == 3: return "Régulé (Auto)"
                return f"Mode {m}"

        except Exception as e:
            return None

        return None

    def _get_probe_val(self, probes, idx):
        """Helper pour chercher une sonde par index."""
        for p in probes:
            if p["index"] == idx:
                return p.get("filteredValue")
        return None

    @property
    def extra_state_attributes(self):
        """Attributs supplémentaires (Consignes)."""
        data = self.coordinator.data
        if not data:
            return {}
            
        params = data.get("params", {})
        
        if self._sensor_type == "ph":
            return {"cible": params.get("ConsignePH")}
            
        if self._sensor_type == "redox":
            return {"cible": params.get("ConsigneRedox")}
            
        return {}