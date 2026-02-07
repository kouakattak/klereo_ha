"""Capteurs Klereo."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
# N'oubliez pas d'importer ALARM_CODES ici
from .const import DOMAIN, FILTRATION_MODES, PUMP_SPEEDS, PROBE_INDEXES, OUT_INDEXES, ALARM_CODES

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    sensors = [
        # --- ALARMES (NOUVEAU) ---
        KlereoAlarmSensor(coordinator),

        # --- TEMPÉRATURES ---
        KlereoSensor(coordinator, "Température Eau", "temp_eau", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
        KlereoSensor(coordinator, "Température Air", "temp_air", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
        
        # --- CHIMIE ---
        KlereoSensor(coordinator, "pH", "ph", "pH", None, SensorStateClass.MEASUREMENT),
        KlereoSensor(coordinator, "Redox", "redox", "mV", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        
        # --- HYDRAULIQUE ---
        KlereoSensor(coordinator, "Pression Filtre", "pressure", UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
        KlereoSensor(coordinator, "Débit", "flow", "m³/h", None, SensorStateClass.MEASUREMENT),

        # --- ÉTATS & NIVEAUX ---
        KlereoSensor(coordinator, "Volet", "volet", None, None, None),
        KlereoSensor(coordinator, "Bidon pH", "bidon_ph", None, None, None),
        KlereoSensor(coordinator, "Bidon Chlore", "bidon_chlore", None, None, None),
        
        # --- FONCTIONNEMENT ---
        KlereoSensor(coordinator, "Pompe Vitesse", "pompe_vitesse", None, None, None),
        KlereoSensor(coordinator, "Mode Filtration", "mode_filtration", None, None, None),
        KlereoSensor(coordinator, "Chauffage", "heating_status", None, None, None),
        KlereoSensor(coordinator, "Auxiliaire", "aux_status", None, None, None),
    ]
    async_add_entities(sensors)

# --- CLASSE SPECIALE POUR LES ALARMES ---
class KlereoAlarmSensor(CoordinatorEntity, SensorEntity):
    """Capteur qui liste les alarmes actives."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Piscine Alarmes"
        self._attr_unique_id = "klereo_alarms_global"
        self._attr_icon = "mdi:check-circle"

    @property
    def native_value(self):
        """Retourne un résumé textuel."""
        alarms = self._get_active_alarms()
        
        if not alarms:
            return "Aucune"
        
        # S'il y a des alarmes, on retourne la première ou "X alarmes"
        if len(alarms) == 1:
            return alarms[0]
        return f"{len(alarms)} défauts"

    @property
    def icon(self):
        """Icône dynamique."""
        if self._get_active_alarms():
            return "mdi:alert-circle"
        return "mdi:check-circle"

    @property
    def extra_state_attributes(self):
        """Détail des alarmes dans les attributs."""
        return {
            "liste_alarmes": self._get_active_alarms(),
            "codes_bruts": self._get_raw_codes()
        }

    def _get_active_alarms(self):
        """Récupère les libellés des alarmes actives."""
        if not self.coordinator.data:
            return []
            
        raw_alarms = self.coordinator.data.get("alarms", [])
        active_labels = []

        for alarm in raw_alarms:
            # Klereo renvoie "isActive": 1 pour les alarmes en cours
            # On gère le cas où c'est un int ou un string
            is_active = str(alarm.get("isActive", "0")) == "1"
            
            if is_active:
                code = int(alarm.get("code", 0))
                # On traduit le code avec notre dictionnaire const.py
                label = ALARM_CODES.get(code, f"Alarme inconnue ({code})")
                active_labels.append(label)
        
        return active_labels

    def _get_raw_codes(self):
        """Récupère juste les numéros pour automatisation facile."""
        if not self.coordinator.data:
            return []
        
        raw_alarms = self.coordinator.data.get("alarms", [])
        return [
            int(a.get("code")) for a in raw_alarms 
            if str(a.get("isActive", "0")) == "1"
        ]

# --- CLASSE STANDARD POUR LES AUTRES CAPTEURS (Inchangée sauf imports) ---
class KlereoSensor(CoordinatorEntity, SensorEntity):
    """Représentation d'un capteur Klereo Standard."""

    def __init__(self, coordinator, name, sensor_type, unit, device_class, state_class):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"Piscine {name}"
        self._attr_unique_id = f"klereo_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None

        data = self.coordinator.data
        probes = data.get("probes", [])
        outs = data.get("outs", [])

        try:
            if self._sensor_type == "temp_eau":
                idx = data.get("EauCapteur", 0)
                return self._get_probe_val(probes, idx)
                
            if self._sensor_type == "temp_air":
                return self._get_probe_val(probes, PROBE_INDEXES["air"])

            if self._sensor_type == "ph":
                idx = data.get("pHCapteur", 0)
                val = self._get_probe_val(probes, idx)
                return round(val, 2) if val is not None else None

            if self._sensor_type == "redox":
                idx = data.get("TraitCapteur", 0)
                val = self._get_probe_val(probes, idx)
                return round(val) if val is not None else None
            
            # Pression
            if self._sensor_type == "pressure":
                val = self._get_probe_val(probes, PROBE_INDEXES["pressure"])
                return round(val, 2) if val is not None else None

            # Débit
            if self._sensor_type == "flow":
                val = self._get_probe_val(probes, PROBE_INDEXES["flow"])
                return round(val, 1) if val is not None else None

            if self._sensor_type == "volet":
                val = self._get_probe_val(probes, PROBE_INDEXES["cover"])
                if val is None: return "Inconnu"
                return "Fermé" if val >= 50 else "Ouvert"

            if self._sensor_type == "bidon_ph":
                val = self._get_probe_val(probes, PROBE_INDEXES["ph_tank"])
                if val is None: return "Inconnu"
                return "Vide" if val == 0 else "OK"

            if self._sensor_type == "bidon_chlore":
                val = self._get_probe_val(probes, PROBE_INDEXES["cl_tank"])
                if val is None: return "Inconnu"
                return "Vide" if val == 0 else "OK"
                
            if self._sensor_type == "pompe_vitesse":
                out = next((o for o in outs if o["index"] == OUT_INDEXES["pump"]), None)
                if not out: return "Inconnu"
                speed_idx = int(out.get("realStatus", 0))
                return PUMP_SPEEDS.get(speed_idx, f"Vitesse {speed_idx}")

            if self._sensor_type == "mode_filtration":
                out = next((o for o in outs if o["index"] == OUT_INDEXES["pump"]), None)
                if not out: return "Inconnu"
                mode_idx = int(out.get("mode", 0))
                return FILTRATION_MODES.get(mode_idx, f"Mode {mode_idx}")

            if self._sensor_type == "heating_status":
                out = next((o for o in outs if o["index"] == OUT_INDEXES["heating"]), None)
                if not out: return "Inconnu"
                return "En chauffe" if out.get("realStatus") == 1 else "Arrêt"

            if self._sensor_type == "aux_status":
                out = next((o for o in outs if o["index"] == OUT_INDEXES["aux"]), None)
                if not out: return "Inconnu"
                return "Marche" if out.get("realStatus") == 1 else "Arrêt"

        except Exception:
            return None
        return None

    def _get_probe_val(self, probes, idx):
        for p in probes:
            if p["index"] == idx:
                return p.get("filteredValue")
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data: return {}
        params = data.get("params", {})
        if self._sensor_type == "ph": return {"cible": params.get("ConsignePH")}
        if self._sensor_type == "redox": return {"cible": params.get("ConsigneRedox")}
        return {}