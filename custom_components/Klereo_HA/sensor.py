"""Capteurs Klereo avec Découverte Automatique."""
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
from .const import DOMAIN, FILTRATION_MODES, PUMP_SPEEDS, PROBE_INDEXES, OUT_INDEXES, ALARM_CODES

async def async_setup_entry(hass, entry, async_add_entities):
    """Configuration des capteurs avec découverte automatique."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    # On s'assure d'avoir des données avant de commencer
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    data = coordinator.data
    probes_data = data.get("probes", [])
    outs_data = data.get("outs", [])

    # 1. On crée une liste des Index présents physiquement
    # Ex: existing_probe_indexes = [0, 1, 6, 7]
    existing_probe_indexes = [p.get("index") for p in probes_data]
    existing_out_indexes = [o.get("index") for o in outs_data]

    sensors = []

    # --- 0. ALARMES (Toujours présent) ---
    sensors.append(KlereoAlarmSensor(coordinator))

    # --- 1. CAPTEURS DYNAMIQUES (Définis par la config Klereo) ---
    # Klereo définit quel index sert à quoi dans la racine du JSON
    
    # Température Eau
    idx_eau = data.get("EauCapteur", 0)
    if idx_eau in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Température Eau", "temp_eau", idx_eau, UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE))

    # pH
    idx_ph = data.get("pHCapteur", 0)
    if idx_ph in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "pH", "ph", idx_ph, "pH", None))

    # Redox
    idx_redox = data.get("TraitCapteur", 0)
    if idx_redox in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Redox", "redox", idx_redox, "mV", SensorDeviceClass.VOLTAGE))

    # Sel / Conductivité
    idx_sel = data.get("SelCapteur", 4)
    if idx_sel in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Taux de Sel", "salt", idx_sel, "g/L", None))


    # --- 2. CAPTEURS FIXES (Définis dans const.py) ---
    # On vérifie si l'index théorique existe vraiment chez vous

    # Température Air
    if PROBE_INDEXES["air"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Température Air", "temp_air", PROBE_INDEXES["air"], UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE))

    # Pression
    if PROBE_INDEXES["pressure"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Pression Filtre", "pressure", PROBE_INDEXES["pressure"], UnitOfPressure.BAR, SensorDeviceClass.PRESSURE))

    # Débit (Flow)
    if PROBE_INDEXES["flow"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Débit", "flow", PROBE_INDEXES["flow"], "m³/h", None))

    # Bidons & Volet
    if PROBE_INDEXES["ph_tank"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Bidon pH", "bidon_ph", PROBE_INDEXES["ph_tank"], None, None))
    
    if PROBE_INDEXES["cl_tank"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Bidon Chlore", "bidon_chlore", PROBE_INDEXES["cl_tank"], None, None))
        
    if PROBE_INDEXES["cover"] in existing_probe_indexes:
        sensors.append(KlereoSensor(coordinator, "Volet", "volet", PROBE_INDEXES["cover"], None, None))


    # --- 3. SORTIES / ACTIONNEURS (OUTS) ---
    
    # Pompe (Vitesse & Mode)
    if OUT_INDEXES["pump"] in existing_out_indexes:
        sensors.append(KlereoSensor(coordinator, "Pompe Vitesse", "pompe_vitesse", OUT_INDEXES["pump"], None, None))
        sensors.append(KlereoSensor(coordinator, "Mode Filtration", "mode_filtration", OUT_INDEXES["pump"], None, None))

    # Chauffage
    if OUT_INDEXES["heating"] in existing_out_indexes:
        sensors.append(KlereoSensor(coordinator, "Chauffage", "heating_status", OUT_INDEXES["heating"], None, None))

    # Auxiliaire
    if OUT_INDEXES["aux"] in existing_out_indexes:
        sensors.append(KlereoSensor(coordinator, "Auxiliaire", "aux_status", OUT_INDEXES["aux"], None, None))

    async_add_entities(sensors)


# --- CLASSES IDENTIQUES À AVANT, MAIS SIMPLIFIÉES GRÂCE À L'INDEX PASSÉ EN PARAMÈTRE ---

class KlereoSensor(CoordinatorEntity, SensorEntity):
    """Représentation d'un capteur Klereo."""

    def __init__(self, coordinator, name, sensor_type, index, unit, device_class):
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._index = index # On stocke l'index précis découvert
        self._attr_name = f"Piscine {name}"
        self._attr_unique_id = f"klereo_{sensor_type}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        # On active l'historique (Measurement) pour tout ce qui a une unité
        if unit:
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

    @property
    def native_value(self):
        """Retourne la valeur du capteur."""
        if not self.coordinator.data: return None

        data = self.coordinator.data
        
        # Cas spécial : Capteurs basés sur les OUTS (Pompe, Chauffage)
        if self._sensor_type in ["pompe_vitesse", "mode_filtration", "heating_status", "aux_status"]:
            return self._get_out_value(data.get("outs", []))
        
        # Cas général : Capteurs basés sur les PROBES (Sondes)
        return self._get_probe_value(data.get("probes", []))

    def _get_probe_value(self, probes):
        # On cherche la sonde qui a le bon index
        probe = next((p for p in probes if p["index"] == self._index), None)
        if not probe: return None

        val = probe.get("filteredValue")
        if val is None: return None

        # Traitement spécifique selon le type
        if self._sensor_type == "ph": return round(val, 2)
        if self._sensor_type == "redox": return round(val)
        if self._sensor_type in ["temp_eau", "temp_air"]: return round(val, 1)
        if self._sensor_type == "pressure": return round(val, 2)
        if self._sensor_type == "flow": return round(val, 1)
        if self._sensor_type == "salt": return round(val, 1)

        # Logiques Binaires
        if self._sensor_type == "volet":
            return "Fermé" if val >= 50 else "Ouvert"
        if "bidon" in self._sensor_type:
            return "Vide" if val == 0 else "OK"

        return val

    def _get_out_value(self, outs):
        # On cherche l'équipement qui a le bon index
        out = next((o for o in outs if o["index"] == self._index), None)
        if not out: return None

        if self._sensor_type == "pompe_vitesse":
            return PUMP_SPEEDS.get(int(out.get("realStatus", 0)), "Inconnu")
            
        if self._sensor_type == "mode_filtration":
            return FILTRATION_MODES.get(int(out.get("mode", 0)), "Inconnu")
            
        if self._sensor_type == "heating_status":
            return "En chauffe" if out.get("realStatus") == 1 else "Arrêt"
            
        if self._sensor_type == "aux_status":
            return "Marche" if out.get("realStatus") == 1 else "Arrêt"
            
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
    """Capteur qui liste les alarmes actives (inchangé)."""

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
        return {
            "liste_alarmes": self._get_active_alarms(),
            "codes_bruts": self._get_raw_codes()
        }

    def _get_active_alarms(self):
        if not self.coordinator.data: return []
        raw_alarms = self.coordinator.data.get("alarms", [])
        active_labels = []
        for alarm in raw_alarms:
            if str(alarm.get("isActive", "0")) == "1":
                code = int(alarm.get("code", 0))
                active_labels.append(ALARM_CODES.get(code, f"Alarme {code}"))
        return active_labels

    def _get_raw_codes(self):
        if not self.coordinator.data: return []
        return [int(a.get("code")) for a in self.coordinator.data.get("alarms", []) if str(a.get("isActive", "0")) == "1"]