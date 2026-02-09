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

# --- NOUVEAU : DÉFINITION OFFICIELLE DES SORTIES (Source PHP) ---
# Format : Index: ("Nom", "Type")
# Type : "pump", "heater", "light", "binary" (On/Off simple)
KLEREO_OUT_MAP = {
    0:  ("Eclairage", "light"),
    1:  ("Filtration", "pump"),
    2:  ("Correcteur pH", "binary"),
    3:  ("Désinfectant", "binary"),
    4:  ("Chauffage", "heater"),
    5:  ("Auxiliaire 1", "binary"),
    6:  ("Auxiliaire 2", "binary"),
    7:  ("Auxiliaire 3", "binary"),
    8:  ("Floculant", "binary"),
    9:  ("Auxiliaire 4", "binary"),
    10: ("Auxiliaire 5", "binary"),
    11: ("Auxiliaire 6", "binary"),
    12: ("Auxiliaire 7", "binary"),
    13: ("Auxiliaire 8", "binary"),
    14: ("Auxiliaire 9", "binary"),
    15: ("Désinfectant Hybride", "binary"),
}

# Mapping des types de capteurs pour les alarmes (Source PHP getSensorIndex)
SENSOR_TYPES = {
    0: ("Température coffret Care/premium", "°C"),
    1: ("Température air", "°C"),
    2: ("Température eau", "°C"),
    3: ("pH seul", "pH"),
    4: ("Redox seul", "mV"),
    5: ("Pression filtre", "mbar"),
    6: ("Niveau bidon pH", "%"),
    7: ("Niveau bidon traitement", "%"),
    8: ("Position volet / couverture", "%"),
    9: ("pH Gen2", "pH"),
    10: ("Redox Gen2", "mV"),
    11: ("Chlore Gen2", "mg/L"),
    12: ("Température eau Gen2", "°C"),
    13: ("Pression Gen2-A", "mbar"),
    14: ("Pression Gen2-B", "mbar"),
    15: ("Débit1 Kompact / Gen3-1", "m³/h"),
    16: ("Température eau Kompact / Gen3-1", "°C"),
    17: ("pH Kompact / Gen3-1", "pH"),
    18: ("Redox Kompact / Gen3-1", "mV"),
    19: ("Température air2", "°C"),
    20: ("Température air3", "°C"),
    21: ("Pression Gen3-1", "mbar"),
    22: ("Chlore Gen3-1", "mg/L"),
    23: ("Niveau bidon floculant", "%"),
    24: ("Débit2 Gen3-1", "m³/h"),
    25: ("Température air4 / Débit1 Gen3-2", "°C"),
    26: ("Température air5 / Débit2 Gen3-2", "°C"),
    27: ("Température air6 / Température Gen3-2", "°C"),
    28: ("Température air7 / pH Gen3-2", "°C"),
    29: ("Température air8 / Redox Gen3-2", "°C"),
    30: ("Température air9 / Pression Gen3-2", "°C"),
    31: ("Température air10 / Chlore Gen3-2", "°C"),
}

# Index des Sondes (Probes) - Inchangé car c'est une autre liste
PROBE_INDEXES = {
    "air": 1,
    "pressure": 3,
    "flow": 9,
    "ph_tank": 6,
    "cl_tank": 7,
    "cover": 8,
}

# Codes Alarmes
ALARM_CODES = {
    0: "Pas d'alerte",
    1: "Capteur HS",
    2: "Problème de configuration relais",
    3: "Inversion sondes pH/Redox",
    5: "Piles faibles",
    6: "Calibration",
    7: "Minimum",
    8: "Maximum",
    10: "Non reçu",
    11: "Hors-gel",
    12: "Alerte #12 inconnue",
    13: "Surconsommation d'eau",
    14: "Fuite d'eau",
    21: "Défaut mémoire interne",
    22: "Problème de circulation",
    23: "Plages de filtration insuffisantes",
    25: "pH élevé, désinfectant inefficace",
    26: "Filtration sous-dimensionée",
    28: "Régulation arrêtée",
    29: "Filtration en mode MANUEL-ARRET",
    30: "Mode INSTALLATION",
    31: "Traitement choc",
    34: "Régulation suspendue ou désactivée",
    35: "Maintenance",
    36: "Limitation journalière de l'injection",
    37: "Muticapteur défaillant",
    38: "Liaison électrolyseur défaillante",
    39: "Limite jounalière du brominateur",
    40: "Electrolyseur:",
    41: "Liaison pompe à chaleur défaillante",
    42: "Configuration des capteurs incohérente",
    43: "Electrolyseur sécurisé",
    44: "Entretien des pompes doseuses",
    45: "Apprentissage non fait",
    46: "Flux d'eau analyse absent",
    47: "Configuration de la couverture incohérente",
    48: "Filtration non contrôlée",
    49: "Vérifiez l'horloge",
    50: "Pompe à chaleur",
    51: "Pompe à chaleur",
    52: "Pompe à chaleur",
    53: "Liaison filtration défaillante",
    54: "Pompe de filtration",
    55: "Mulcapteur Gen3 ou Gen5 absent",
    56: "Etat de la filtration inconnu, risque de traitement sans filtration",
    57: "Multicapteur Gen3 ou Gen4 absent",
    58: "Mauvaise configuration de la pompe",
    59: "Problème de communication avec le module de mesure de consommation",
    60: "Écran de la pompe à vitesse variable verrouillé",
    61: "Défaut pompe à chaleur"
}