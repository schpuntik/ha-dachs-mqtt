import json
import time
import logging
import requests
import paho.mqtt.client as mqtt
from pathlib import Path

from .sectors import SECTORS

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("dachs_mqtt")

OPTIONS_PATH = Path("/data/options.json")

# Default addon configuration
DEFAULT_OPTIONS = {
    "mqtt_host": "localhost",
    "mqtt_port": 1883,
    "mqtt_user": "",
    "mqtt_password": "",
    "interval": 10,

    "dachs_host": "localhost",
    "dachs_port": 8080,   # default API port
    "dachs_user": "",
    "dachs_password": "",
    "base_topic": "dachs",
    "sectors": {}
}


# Load addon options
def load_options():
    if not OPTIONS_PATH.exists():
        OPTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OPTIONS_PATH.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_OPTIONS, f, indent=2)
        return DEFAULT_OPTIONS

    with OPTIONS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


# Sanitize MQTT topic
def sanitize_topic(s: str) -> str:
    return s.replace("#", "_").replace("+", "_")


# Sanitize HA-friendly name
def sanitize_name(s: str) -> str:
    return s.replace("#", "").replace("+", "")


# Build list of active sector entries
def build_entries(options):
    sectors_cfg = options.get("sectors", {})
    entries = []

    for sector_name, enabled in sectors_cfg.items():
        if enabled:
            for entry in SECTORS.get(sector_name, []):
                entries.append((entry, sector_name))

    return entries


# Normalize entity_id for HA
def normalize_entity_id(name: str) -> str:
    s = name.lower()
    for ch in [" ", "%", ",", ".", "ä", "ö", "ü", "ß", ":", "/", "(", ")", "-", "[", "]"]:
        s = s.replace(ch, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


# Classify entity for HA Discovery
def classify_entity(entry, sector_name):
    dtype = entry[0]
    key = entry[1]
    name = entry[1]

    entity_kind = "sensor"
    device_class = None
    state_class = None
    unit = None

    # Basic type classification
    if "Temp" in key or "temp" in key:
        entity_kind = "sensor"
        device_class = "temperature"
        unit = "°C"
        state_class = "measurement"

    elif "Wirkleistung" in key or "Leistung" in key:
        entity_kind = "sensor"
        device_class = "power"
        unit = "kW"
        state_class = "measurement"

    elif "Arbeit" in key:
        entity_kind = "sensor"
        device_class = "energy"
        unit = "kWh"
        state_class = "total_increasing"

    elif "Betriebssekunden" in key:
        entity_kind = "sensor"
        device_class = "duration"
        unit = "s"
        state_class = "total_increasing"

    # Binary/switch classification
    if dtype in (3, 4):
        if ".Aktor." in key or "ProgAus" in key:
            entity_kind = "switch"
        else:
            entity_kind = "binary_sensor"

    # Fault/warning classification
    if key.endswith(".fStoerung") or key.endswith(".bStoerung") or "Warnung" in key:
        entity_kind = "binary_sensor"
        device_class = "problem"

    if "Wartung_Cache.fStehtAn" in key:
        entity_kind = "binary_sensor"
        device_class = "problem"

    device_name = f"Dachs – {sector_name}"

    return {
        "entity_kind": entity_kind,
        "device_class": device_class,
        "state_class": state_class,
        "unit": unit,
        "device_name": device_name,
        "name": name,
    }


# Publish HA MQTT Discovery config
def publish_discovery(client, base_topic, entry, sector_name):
    dtype, key, name2, uuid = entry

    c = classify_entity(entry, sector_name)
    entity_kind = c["entity_kind"]
    device_class = c["device_class"]
    state_class = c["state_class"]
    unit = c["unit"]
    device_name = c["device_name"]

    name = sanitize_name(c["name"])
    entity_id = normalize_entity_id(f"{sector_name}_{name}")

    safe_key = sanitize_topic(key)
    state_topic = f"{base_topic}/{safe_key}"

    unique_id = uuid if uuid else f"dachs_{normalize_entity_id(key)}"

    payload = {
        "name": name,
        "unique_id": unique_id,
        "state_topic": state_topic,
        "device": {
            "identifiers": ["dachs_mqtt"],
            "name": device_name,
            "manufacturer": "SenerTec",
            "model": "Dachs",
        },
    }

    # Optional HA fields
    if device_class:
        payload["device_class"] = device_class
    if state_class:
        payload["state_class"] = state_class
    if unit:
        payload["unit_of_measurement"] = unit

    # Select HA component
    if entity_kind == "sensor":
        topic = f"homeassistant/sensor/{entity_id}/config"
    elif entity_kind == "binary_sensor":
        topic = f"homeassistant/binary_sensor/{entity_id}/config"
    elif entity_kind == "switch":
        topic = f"homeassistant/switch/{entity_id}/config"
    else:
        topic = f"homeassistant/sensor/{entity_id}/config"

    client.publish(topic, json.dumps(payload), retain=True)


# Check Dachs API availability
def check_dachs_connection(session, host, port, user, password):
    test_key = "Hka_Mw1.Temp.sbZS_Vorlauf2"
    url = f"http://{host}:{port}/getKey"

    try:
        resp = session.get(
            url,
            params={"k": test_key},
            auth=(user, password) if user else None,
            timeout=5
        )

        if resp.status_code == 401:
            _LOGGER.error("Dachs API rejected authentication (401).")
            return False

        resp.raise_for_status()
        _LOGGER.info("Authorization successful — Dachs reachable.")
        return True

    except Exception as e:
        _LOGGER.error("Unable to reach Dachs (%s:%s): %s", host, port, e)
        return False


# Main loop
def main():
    options = load_options()

    host = options["dachs_host"]
    port = options.get("dachs_port", 8080)
    user = options["dachs_user"]
    password = options.get("dachs_password", "")
    base_topic = options.get("base_topic", "dachs")

    mqtt_host = options["mqtt_host"]
    mqtt_port = options["mqtt_port"]
    mqtt_user = options.get("mqtt_user") or None
    mqtt_password = options.get("mqtt_password") or None

    entries = build_entries(options)
    _LOGGER.info("Active keys: %d", len(entries))

    # MQTT client setup
    client = mqtt.Client()
    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    session = requests.Session()

    # Pre-start API check
    check_dachs_connection(session, host, port, user, password)

    # Publish HA Discovery
    for entry, sector_name in entries:
        publish_discovery(client, base_topic, entry, sector_name)

    _LOGGER.info("MQTT Discovery published for %d entities", len(entries))

    # Main update loop
    while True:
        for entry, sector_name in entries:
            dtype, key, name2, uuid = entry
            safe_key = sanitize_topic(key)

            try:
                url = f"http://{host}:{port}/getKey"
                resp = session.get(
                    url,
                    params={"k": key},
                    auth=(user, password) if user else None,
                    timeout=5
                )
                resp.raise_for_status()
                value_raw = resp.text.strip()

                # Extract clean value from "key=value"
                if "=" in value_raw:
                    _, value_raw = value_raw.split("=", 1)
                    value_raw = value_raw.strip()

            except Exception as e:
                _LOGGER.error("HTTP error for %s: %s", key, e)
                continue

            # Convert numeric values
            value = value_raw
            try:
                if dtype == 1 and value_raw != "":
                    value = float(value_raw.replace(",", "."))
            except Exception:
                value = value_raw

            # Publish state
            topic = f"{base_topic}/{safe_key}"
            client.publish(topic, payload=value, retain=False)

        time.sleep(10)


if __name__ == "__main__":
    main()
