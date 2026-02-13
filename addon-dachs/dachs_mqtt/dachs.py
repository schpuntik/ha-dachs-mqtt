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

DEFAULT_OPTIONS = {
    "mqtt_host": "localhost",
    "mqtt_port": 1883,
    "mqtt_user": "",
    "mqtt_password": "",
    "interval": 10,

    "dachs_host": "localhost",
    "dachs_user": "",
    "dachs_password": "",
    "base_topic": "dachs",
    "sectors": {}
}


# ---------------------------------------------------------
# Загрузка конфигурации аддона
# ---------------------------------------------------------
def load_options():
    if not OPTIONS_PATH.exists():
        print("options.json not found — creating default config")
        OPTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OPTIONS_PATH.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_OPTIONS, f, indent=2)
        return DEFAULT_OPTIONS

    with OPTIONS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# Нормализация MQTT-топиков
# ---------------------------------------------------------
def sanitize_topic(s: str) -> str:
    return s.replace("#", "_").replace("+", "_")


# ---------------------------------------------------------
# Сбор активных записей
# ---------------------------------------------------------
def build_entries(options):
    sectors_cfg = options.get("sectors", {})
    entries = []

    for sector_name, enabled in sectors_cfg.items():
        if enabled:
            sector = SECTORS.get(sector_name, [])
            for entry in sector:
                entries.append((entry, sector_name))

    return entries


# ---------------------------------------------------------
# Нормализация имени → entity_id
# ---------------------------------------------------------
def normalize_entity_id(name: str) -> str:
    s = name.lower()
    for ch in [" ", "%", ",", ".", "ä", "ö", "ü", "ß", ":", "/", "(", ")", "-", "[", "]"]:
        s = s.replace(ch, "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


# ---------------------------------------------------------
# Классификация сущности
# ---------------------------------------------------------
def classify_entity(entry, sector_name):
    dtype = entry[0]
    key = entry[1]
    name = entry[2]

    entity_kind = "sensor"
    device_class = None
    state_class = None
    unit = None

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

    if dtype in (3, 4):
        if ".Aktor." in key or "ProgAus" in key:
            entity_kind = "switch"
        else:
            entity_kind = "binary_sensor"

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
    }


# ---------------------------------------------------------
# Публикация MQTT Discovery
# ---------------------------------------------------------
def publish_discovery(client, base_topic, entry, sector_name):
    dtype, key, name, uuid = entry

    classification = classify_entity(entry, sector_name)
    entity_kind = classification["entity_kind"]
    device_class = classification["device_class"]
    state_class = classification["state_class"]
    unit = classification["unit"]
    device_name = classification["device_name"]

    # ВОЗВРАЩАЕМ НАЗВАНИЕ СЕНСОРА ИЗ 3 ПОЛЯ
    entity_id = normalize_entity_id(f"{sector_name}_{name}")

    safe_key = sanitize_topic(key)
    state_topic = f"{base_topic}/{safe_key}"

    unique_id = uuid if uuid else f"dachs_{normalize_entity_id(key)}"

    payload = {
        "name": name,  # ← ВОТ ЗДЕСЬ ВОЗВРАЩЕНО ПОЛЕ 3
        "unique_id": unique_id,
        "state_topic": state_topic,
        "device": {
            "identifiers": ["dachs_mqtt"],
            "name": device_name,
            "manufacturer": "SenerTec",
            "model": "Dachs",
        },
    }

    if device_class:
        payload["device_class"] = device_class
    if state_class:
        payload["state_class"] = state_class
    if unit:
        payload["unit_of_measurement"] = unit

    if entity_kind == "sensor":
        topic = f"homeassistant/sensor/{entity_id}/config"
    elif entity_kind == "binary_sensor":
        topic = f"homeassistant/binary_sensor/{entity_id}/config"
    elif entity_kind == "switch":
        topic = f"homeassistant/switch/{entity_id}/config"
    else:
        topic = f"homeassistant/sensor/{entity_id}/config"

    client.publish(topic, json.dumps(payload), retain=True)


# ---------------------------------------------------------
# Основной цикл
# ---------------------------------------------------------
def main():
    options = load_options()

    host = options["dachs_host"]
    user = options["dachs_user"]
    password = options.get("dachs_password", "")
    base_topic = options.get("base_topic", "dachs")

    mqtt_host = options["mqtt_host"]
    mqtt_port = options["mqtt_port"]
    mqtt_user = options.get("mqtt_user") or None
    mqtt_password = options.get("mqtt_password") or None

    entries = build_entries(options)
    _LOGGER.info("Aktive Schlüssel: %d", len(entries))

    client = mqtt.Client()
    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    session = requests.Session()

    for entry, sector_name in entries:
        publish_discovery(client, base_topic, entry, sector_name)

    _LOGGER.info("MQTT Discovery published for %d entities", len(entries))

    while True:
        for entry, sector_name in entries:
            dtype, key, name, uuid = entry
            safe_key = sanitize_topic(key)

            try:
                url = f"http://{host}/getKey"
                resp = session.get(url, params={"k": key}, timeout=5)
                resp.raise_for_status()
                value_raw = resp.text.strip()
            except Exception as e:
                _LOGGER.error("HTTP Fehler für %s: %s", key, e)
                continue

            value = value_raw
            try:
                if dtype == 1 and value_raw != "":
                    value = float(value_raw.replace(",", "."))
            except Exception:
                value = value_raw

            topic = f"{base_topic}/{safe_key}"
            client.publish(topic, payload=value, retain=False)

        time.sleep(10)


if __name__ == "__main__":
    main()
