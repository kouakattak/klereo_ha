# 🏊 Klereo Connect pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-0.0.1-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()
[![Maintener](https://img.shields.io/badge/maintainer-Communauté-blue)]()

**Klereo Connect** est une intégration personnalisée (**Custom Component**) pour Home Assistant qui permet de connecter les systèmes d'automatisation de piscine **Klereo (K-Link)** via l'API Cloud V3.

Cette intégration remplace les anciennes implémentations manuelles (YAML, `rest_command`, templates) par une solution **native en Python**, plus rapide, plus robuste et configurable entièrement via l'interface utilisateur.

## ✨ Fonctionnalités

### 📡 Capteurs (Lecture toutes les 10s)
* **Températures** : Eau (`EauCapteur`) et Air Extérieur (`Index 1`).
* **Chimie** :
    * Valeurs **pH** et **Redox** en temps réel.
    * Récupération des **valeurs cibles (consignes)** sous forme d'attributs.
* **Équipements** :
    * Vitesse réelle de la pompe.
    * Position du volet (Ouvert / Fermé).
* **Consommables** :
    * État des bidons de **pH-** et **Chlore Liquide** (Retourne `OK` ou `Vide`).

### 🎮 Contrôles (Actions)
* **Éclairage** : Interrupteur On/Off pour le projecteur (`switch`).
* **Pompe de Filtration** : Sélecteur de mode complet (`select`) :
    * `Arrêt`
    * `Vitesse 1` / `Vitesse 2` / `Vitesse 3` (Modes Manuels)
    * `Régulé (Auto)`
    * `Plages Horaires`

### ⚙️ Backend
* **Gestion de Token** : Authentification JWT automatique avec renouvellement transparent à l'expiration.
* **Zéro YAML** : Configuration 100% via l'interface graphique (Config Flow).

---

## 🚀 Installation

### Méthode 1 : Via HACS (Recommandé)

1.  Ouvrez HACS dans Home Assistant.
2.  Allez dans le menu (3 points en haut à droite) > **Dépôts personnalisés**.
3.  Ajoutez l'URL de ce dépôt dans la catégorie **Intégration**.
4.  Recherchez **"Klereo Connect"** et cliquez sur **Télécharger**.
5.  Redémarrez Home Assistant.

### Méthode 2 : Manuelle

1.  Téléchargez la dernière release du dépôt.
2.  Copiez le dossier `klereo` dans le répertoire `custom_components` de votre installation Home Assistant.
    * Chemin final attendu : `/config/custom_components/klereo/`
3.  Redémarrez Home Assistant.

---

## 🔧 Configuration

Une fois l'intégration installée et Home Assistant redémarré :

1.  Allez dans **Paramètres** > **Appareils et services**.
2.  Cliquez sur **Ajouter une intégration** (en bas à droite).
3.  Recherchez **Klereo Connect**.
4.  Remplissez le formulaire avec vos identifiants K-Link :
    * **Identifiant** : Email ou Login.
    * **Mot de passe** : Votre mot de passe.
    * **Pool ID** : L'ID unique de votre piscine (ex: `89140`, visible dans l'URL de l'interface web Klereo).

---

## 📊 Exemple de Dashboard

Voici une carte Lovelace complète utilisant uniquement des composants natifs (Grid, Glance, Entities, Gauge). Aucune carte tierce n'est requise.

Créez une carte **Manuel** et collez le code suivant :

```yaml
type: vertical-stack
cards:
  # --- 1. EN-TÊTE ---
  - type: entity
    entity: sensor.piscine_temperature
    name: Ma Piscine
    icon: mdi:pool
    attribute: date_communication

  # --- 2. TEMPÉRATURES ---
  - type: grid
    columns: 2
    square: true
    cards:
      - type: gauge
        entity: sensor.piscine_temperature
        name: Eau
        unit: °C
        min: 0
        max: 40
        needle: true
        severity:
          green: 26
          yellow: 15
          red: 0
      - type: gauge
        entity: sensor.piscine_temperature_air
        name: Air Ext.
        unit: °C
        min: -10
        max: 50
        needle: true

  # --- 3. ÉTAT & LUMIÈRE ---
  - type: glance
    show_name: true
    show_state: true
    show_icon: true
    columns: 4
    entities:
      - entity: sensor.piscine_pompe_vitesse
        name: Vitesse
        icon: mdi:pump
      - entity: sensor.piscine_mode_filtration
        name: Mode
        icon: mdi:cog-sync
      - entity: switch.piscine_lumiere
        name: Spot
        icon: mdi:lightbulb-spot
        tap_action:
          action: toggle
      - entity: sensor.piscine_volet
        name: Volet
        icon: mdi:shield-check

  # --- 4. CHIMIE ---
  - type: grid
    columns: 2
    square: true
    cards:
      - type: gauge
        entity: sensor.piscine_ph
        name: pH
        min: 6
        max: 8.5
        needle: true
        severity:
          green: 7
          yellow: 7.6
          red: 7.8
      - type: gauge
        entity: sensor.piscine_redox
        name: Redox
        min: 0
        max: 1000
        needle: true
        severity:
          green: 550
          yellow: 800
          red: 900

  # --- 5. PILOTAGE & MAINTENANCE ---
  - type: entities
    title: Pilotage & Consommables
    entities:
      - entity: select.piscine_controle_pompe
        name: Mode Filtration
        icon: mdi:pump-cog
      - type: divider
      - type: attribute
        entity: sensor.piscine_ph
        attribute: cible
        name: Consigne pH Cible
        icon: mdi:target
      - type: attribute
        entity: sensor.piscine_redox
        attribute: cible
        name: Consigne Redox Cible
        icon: mdi:target
      - type: divider
      - entity: sensor.piscine_bidon_ph
        name: Bidon pH-
      - entity: sensor.piscine_bidon_chlore
        name: Bidon Chlore