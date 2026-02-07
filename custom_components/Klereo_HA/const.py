"""Constants for the Klereo integration."""
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
)

DOMAIN = "klereo"
CONF_POOL_ID = "pool_id"
CONF_LOGIN = "login"
CONF_PASSWORD = "password"

# URL de l'API
API_URL_JWT = "https://connect.klereo.fr/php/GetJWT.php"
API_URL_DETAILS = "https://connect.klereo.fr/php/GetPoolDetails.php"
API_URL_SET = "https://connect.klereo.fr/php/SetOut.php"

# --- MAPPINGS ---

FILTRATION_MODES = {
    0: "Arrêt",
    1: "Manuel (24h/24)",
    2: "Programmé (Horloge)",
    3: "Automatique (Température)"
}

PUMP_SPEEDS = {
    0: "Arrêt",
    1: "Vitesse 1 (Eco)",
    2: "Vitesse 2 (Normal)",
    3: "Vitesse 3 (Max)",
}

OUT_INDEXES = {
    "light": 0,
    "pump": 1,
    "aux": 2,
    "heating": 3,
}

PROBE_INDEXES = {
    "air": 1,
    "pressure": 3,
    "salt": 4,
    "ph_tank": 6,
    "cl_tank": 7,
    "cover": 8,
    "flow": 9,
}

# --- NOUVEAU : CODES ALARMES (Source : Plugin Jeedom) ---
ALARM_CODES = {
    1: "Lavage filtre nécessaire",
    2: "Bidon pH vide",
    3: "Bidon Chlore/Redox vide",
    4: "Température Eau basse (<3°C)",
    5: "Mise hors gel (Air < -2°C)",
    6: "Défaut débit",
    7: "Défaut débit (Cellule)",
    8: "Sécurité surdosage pH",
    9: "Sécurité surdosage Chlore/Redox",
    10: "Batterie faible",
    11: "Défaut communication Box",
    12: "Défaut communication Capteurs",
    13: "Erreur système",
    14: "Défaut analyse pH",
    15: "Défaut analyse Redox",
    16: "Appoint d'eau (Niveau bas)",
    17: "Défaut pompe",
    18: "Défaut chauffage",
}