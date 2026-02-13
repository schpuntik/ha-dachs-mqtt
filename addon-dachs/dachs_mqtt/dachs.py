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

    # Добавлено:
    "host": "localhost",
    "port": 8080,
    "base_topic": "dachs",
    "sectors": {}
}


# ---------------------------------------------------------
# Загрузка конфигурации аддона
# ---------------------------------------------------------
def load_options():
    # Если файла нет — создаём дефолтный
    if not OPTIONS_PATH.exists():
        print("options.json not found — creating default config")
        OPTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with OPTIONS_PATH.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT_OPTIONS, f, indent=2)
        return DEFAULT_OPTIONS

    # Если файл есть — читаем
    with OPTIONS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------
# Сбор активных записей по секторам
# возвращаем список кортежей: (entry, sector_name)
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
# Определение типа сущности (sensor / binary_sensor / switch / number)
# и параметров для SCADA‑friendly группировки
# ---------------------------------------------------------
def classify_entity(entry, sector_name):
    dtype = entry[0]
    key = entry[1]
    name = entry[2]

    # По умолчанию – обычный sensor
    entity_kind = "sensor"
    device_class = None
    state_class = None
    unit = None

    # Простейшая типизация по ключу
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

    # Bitmask / Flags → binary_sensor или switch
    # dtype 3/4 – битовые/флаговые значения
    if dtype in (3, 4):
        # Aktoren → switch
        if ".Aktor." in key or "ProgAus" in key:
            entity_kind = "switch"
        else:
            entity_kind = "binary_sensor"

    # Некоторые явные флаги → binary_sensor
    if key.endswith(".fStoerung") or key.endswith(".bStoerung") or "Warnung" in key:
        entity_kind = "binary_sensor"
        device_class = "problem"

    if "Wartung_Cache.fStehtAn" in key:
        entity_kind = "binary_sensor"
        device_class = "problem"

    # SCADA‑friendly: группируем по сектору через device.name
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
    dtype = entry[0]
    key = entry[1]
    name = entry[2]
    uuid = entry[3]

    classification = classify_entity(entry, sector_name)
    entity_kind = classification["entity_kind"]
    device_class = classification["device_class"]
    state_class = classification["state_class"]
    unit = classification["unit"]
    device_name = classification["device_name"]

    # entity_id: включаем сектор для SCADA‑группировки
    entity_id = normalize_entity_id(f"{sector_name}_{name}")

    # unique_id
    if uuid:
        unique_id = uuid
    else:
        unique_id = f"dachs_{normalize_entity_id(key)}"

    state_topic = f"{base_topic}/{key}"

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

    if device_class:
        payload["device_class"] = device_class
    if state_class:
        payload["state_class"] = state_class
    if unit:
        payload["unit_of_measurement"] = unit

    # Выбор discovery‑топика по типу сущности
    if entity_kind == "sensor":
        topic = f"homeassistant/sensor/{entity_id}/config"
    elif entity_kind == "binary_sensor":
        topic = f"homeassistant/binary_sensor/{entity_id}/config"
    elif entity_kind == "switch":
        topic = f"homeassistant/switch/{entity_id}/config"
        # Для switch нужно добавить command_topic, но у нас пока только чтение
        # поэтому оставляем как read‑only sensor‑style switch
    elif entity_kind == "number":
        topic = f"homeassistant/number/{entity_id}/config"
    else:
        topic = f"homeassistant/sensor/{entity_id}/config"

    client.publish(topic, json.dumps(payload), retain=True)


# ---------------------------------------------------------
# Основной цикл аддона
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

    # Собираем активные записи (entry, sector_name)
    entries = build_entries(options)
    _LOGGER.info("Aktive Schlüssel: %d", len(entries))

    # MQTT клиент
    client = mqtt.Client()
    if mqtt_user:
        client.username_pw_set(mqtt_user, mqtt_password)
    client.connect(mqtt_host, mqtt_port, 60)
    client.loop_start()

    session = requests.Session()

    # MQTT Discovery – один раз при старте
    for entry, sector_name in entries:
        publish_discovery(client, base_topic, entry, sector_name)

    _LOGGER.info("MQTT Discovery published for %d entities", len(entries))

    # Основной цикл опроса
    while True:
        for entry, sector_name in entries:
            dtype = entry[0]
            key = entry[1]
            name = entry[2]  # ЧЕЛОВЕЧЕСКОЕ НАЗВАНИЕ

            try:
                url = f"http://{host}:{port}/getKey"
                resp = session.get(url, params={"k": key}, timeout=5)
                resp.raise_for_status()
                value_raw = resp.text.strip()
            except Exception as e:
                _LOGGER.error("HTTP Fehler für %s: %s", key, e)
                continue

            # Простая обработка типов
            value = value_raw
            try:
                if dtype == 1:
                    # числовые значения
                    if value_raw != "":
                        value = float(value_raw.replace(",", "."))
                elif dtype in (3, 4):
                    # битовые / флаговые – оставляем как есть (0/1 или маска)
                    pass
                elif dtype == 2:
                    # Tageslauf – битовая маска, можно позже декодировать
                    pass
            except Exception:
                # если не получилось преобразовать – отправляем как строку
                value = value_raw

            topic = f"{base_topic}/{key}"
            client.publish(topic, payload=value, retain=False)

        time.sleep(10)


if __name__ == "__main__":
    main()
