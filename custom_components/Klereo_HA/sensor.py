"""Capteurs Klereo avec Mappings Officiels."""
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
from .const import (
    DOMAIN, 
    FILTRATION_MODES, 
    PUMP_SPEEDS, 
    PROBE_INDEXES, 
    ALARM_CODES, 
    KLEREO_OUT_MAP
)

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs avec découverte automatique."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    data = coordinator.data
    probes_data = data.get("probes", [])
    outs_data = data.get("outs", [])
    existing_probe_indexes = [p.get("index") for p in probes_data]
    
    sensors = []

    # --- 0. ALARMES ---
    sensors.append(KlereoAlarmSensor(coordinator))

    # --- 1. CAPTEURS SONDES (PROBES) ---
    # Dynamiques (définis par la config)
    idx_eau = data.get("EauCapteur", 0)
    if idx_eau in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Température Eau", "temp_eau", idx_eau, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE))
    
    idx_ph = data.get("pHCapteur", 0)
    if idx_ph in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "pH", "ph", idx_ph, "pH", None))
        
    idx_redox = data.get("TraitCapteur", 0)
    if idx_redox in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Redox", "redox", idx_redox, "mV", SensorDeviceClass.VOLTAGE))
        
    idx_sel = data.get("SelCapteur", 4)
    if idx_sel in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Taux de Sel", "salt", idx_sel, "g/L", None))

    # Fixes (définis par constantes)
    if PROBE_INDEXES["air"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Température Air", "temp_air", PROBE_INDEXES["air"], UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE))
    if PROBE_INDEXES["pressure"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Pression Filtre", "pressure", PROBE_INDEXES["pressure"], UnitOfPressure.BAR, SensorDeviceClass.PRESSURE))
    if PROBE_INDEXES["flow"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Débit", "flow", PROBE_INDEXES["flow"], "m³/h", None))
    if PROBE_INDEXES["ph_tank"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Bidon pH", "bidon_ph", PROBE_INDEXES["ph_tank"], None, None))
    if PROBE_INDEXES["cl_tank"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Bidon Chlore", "bidon_chlore", PROBE_INDEXES["cl_tank"], None, None))
    if PROBE_INDEXES["cover"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Volet", "volet", PROBE_INDEXES["cover"], None, None))

    # --- 2. SORTIES (OUTS) - DÉCOUVERTE BASÉE SUR LA LISTE PHP ---
    
    for out in outs_data:
        idx = int(out.get("index"))
        
        # On vérifie si cet index est connu dans notre Map officielle
        if idx in KLEREO_OUT_MAP:
            name, out_type = KLEREO_OUT_MAP[idx]
            
            # Type Pompe (Index 1) : Besoin de Vitesse + Mode
            if out_type == "pump":
                sensors.append(KlereoSensor(coordinator, f"{name} Vitesse", "pompe_vitesse", idx, None, None))
                sensors.append(KlereoSensor(coordinator, f"{name} Mode", "mode_filtration", idx, None, None))
            
            # Type Chauffage (Index 4)
            elif out_type == "heater":
                sensors.append(KlereoSensor(coordinator, name, "heating_status", idx, None, None))
                
            # Type Lumière (Index 0)
            elif out_type == "light":
                sensors.append(KlereoSensor(coordinator, name, "light_status", idx, None, None))
                
            # Type Binaire Générique (Auxiliaires, Floculant, Désinfectant...)
            elif out_type == "binary":
                sensors.append(KlereoSensor(coordinator, name, "binary_status", idx, None, None))

    async_add_entities(sensors)


# --- CLASSES ---

class KlereoSensor(CoordinatorEntity, SensorEntity):
    """Représentation d'un capteur Klereo."""

    def __init__(self, coordinator, name, sensor_type, index, unit, device_class):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._index = index 
        # Nommage propre : "Piscine Eclairage", "Piscine Auxiliaire 1", etc.
        self._attr_name = f"Piscine {name}"
        self._attr_unique_id = f"klereo_{sensor_type}_{index}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        if unit:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        data = self.coordinator.data
        
        # SI OUT (Sortie)
        if self._sensor_type in ["pompe_vitesse", "mode_filtration", "heating_status", "light_status", "binary_status"]:
            return self._get_out_value(data.get("outs", []))
        
        # SI PROBE (Sonde)
        return self._get_probe_value(data.get("probes", []))

    def _get_probe_value(self, probes):
        probe = next((p for p in probes if p["index"] == self._index), None)
        if not probe: return None
        val = probe.get("filteredValue")
        if val is None: return None

        if self._sensor_type == "ph": return round(val, 2)
        if self._sensor_type == "redox": return round(val)
        if self._sensor_type in ["temp_eau", "temp_air"]: return round(val, 1)
        if self._sensor_type == "pressure": return round(val, 2)
        if self._sensor_type == "flow": return round(val, 1)
        if self._sensor_type == "salt": return round(val, 1)
        if self._sensor_type == "volet": return "Fermé" if val >= 50 else "Ouvert"
        if "bidon" in self._sensor_type: return "Vide" if val == 0 else "OK"
        return val

    def _get_out_value(self, outs):
        out = next((o for o in outs if o["index"] == self._index), None)
        if not out: return None

        # Gestion Pompe
        if self._sensor_type == "pompe_vitesse":
            return PUMP_SPEEDS.get(int(out.get("realStatus", 0)), "Inconnu")
        if self._sensor_type == "mode_filtration":
            return FILTRATION_MODES.get(int(out.get("mode", 0)), "Inconnu")
            
        # Gestion ON/OFF générique (Pour tous les binary, heater, light)
        if self._sensor_type in ["heating_status", "light_status", "binary_status"]:
            status = out.get("realStatus")
            # Klereo : "1" ou 1 = ON, "0" ou 0 = OFF
            return "Marche" if str(status) == "1" else "Arrêt"
            
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data: return {}
        params = data.get("params", {})
        if self._sensor_type == "ph": return {"cible": params.get("ConsignePH")}
        if self._sensor_type == "redox": return {"cible": params.get("ConsigneRedox")}
        return {}


class KlereoAlarmSensor(CoordinatorEntity, SensorEntity):
    """Capteur Alarmes (Inchangé)."""
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "Piscine Alarmes"
        self._attr_unique_id = "klereo_alarms_global"
        self._attr_icon = "mdi:check-circle"
    @property
    def native_value(self):
        alarms = self._get_active_alarms()
        if not alarms: return "Aucune"
        if len(alarms) == 1: return alarms[0]
        return f"{len(alarms)} défauts"
    @property
    def icon(self):
        return "mdi:alert-circle" if self._get_active_alarms() else "mdi:check-circle"
    @property
    def extra_state_attributes(self):
        return {"liste_alarmes": self._get_active_alarms(), "codes_bruts": self._get_raw_codes()}
    def _get_active_alarms(self):
        if not self.coordinator.data: return []
        
        alarms_list = []
        raw_alarms = self.coordinator.data.get("alarms", [])
        
        for alarm in raw_alarms:
            if str(alarm.get("isActive", "0")) != "1":
                continue
                
            code = int(alarm.get("code", 0))
            param = int(alarm.get("param", 0))
            
            msg = self._format_alarm_message(code, param)
            alarms_list.append(msg)
            
        return alarms_list

    def _get_raw_codes(self):
        if not self.coordinator.data: return []
        return [int(a.get("code")) for a in self.coordinator.data.get("alarms", []) if str(a.get("isActive", "0")) == "1"]

    def _format_alarm_message(self, code, param):
        """Formate le message d'alarme selon la logique PHP (gestion du param)."""
        base_msg = ALARM_CODES.get(code, f"Code alerte inconnu : {code}")
        extra_msg = ""

        if code in [1, 7, 8, 10, 36]: # param = CapteurID
            # On affiche simplement l'ID du capteur faute de mapping complet "getSensorIndex"
            extra_msg = f" - Capteur {param}"
        elif code == 5:
            extra_msg = " - RFID"
        elif code == 6:
            if param == 0: extra_msg = " - pH"
            elif param == 1: extra_msg = " - Désinfectant"
        elif code in [13, 14]:
            extra_msg = f" - débit {param}"
        elif code == 35:
            extra_msg = f" - sortie {param}"
        elif code == 40:
            extra_msg = f" - BSVError {param}"
        elif code == 41:
            extra_msg = f" - Communication {param}"
        elif code in [50, 51, 52, 54, 61]:
            extra_msg = f" - code d'erreur {param}"
        elif code == 53:
            extra_msg = f" - pompe numéro {param}"
            
        return f"{base_msg}{extra_msg}"