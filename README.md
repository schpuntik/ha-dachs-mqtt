Конечно, Jakob — вот **полный, единый, готовый README.md**, оформленный как один цельный файл, без разбивки на секции в отдельных сообщениях.  
Ты можешь просто скопировать его в `README.md` в корне репозитория.

---

# **README.md**

```markdown
# Dachs2MQTT – Home Assistant Add-on  
Reads values from SenerTec Dachs via HTTP and publishes them to MQTT with full Home Assistant Discovery support.

---

## ✨ Features

- 🔌 Reads all available Dachs parameters via the internal HTTP interface  
- 📡 Publishes values to MQTT in real time  
- 🧩 Automatic Home Assistant MQTT Discovery  
  - sensor  
  - binary_sensor  
  - switch (read-only)  
  - number (future support)  
- 🗂️ Sector-based grouping (Hydraulik, Brenner, Temperaturen, Wartung, etc.)  
- 🏭 SCADA-friendly entity grouping  
- 🧠 Automatic type detection  
  - Temperatures → °C  
  - Power → kW  
  - Energy → kWh  
  - Bitmasks → binary_sensor  
  - Aktoren → switch  
- 🧱 Modular architecture  
  - sectors.py – sector definitions  
  - zumdachs.py – full key list  
  - dachs.py – main logic  

---

## 📦 Installation

### 1. Add repository to Home Assistant

Open:

**Settings → Add-ons → Add-on Store → ⋮ → Repositories**

Add:

```
https://github.com/schpuntik/ha-dachs-mqtt
```

The repository will appear as:

**Dachs2MQTT Add-ons**

### 2. Install the add-on

Select:

**Dachs MQTT Bridge**

Click:

- Install  
- Start  
- (optional) Show in sidebar  

---

## ⚙️ Configuration

The add-on reads its configuration from `/data/options.json`.

Example:

```yaml
dachs_host: 192.168.178.77
dachs_user: glt
dachs_password: PASSWORT

mqtt_host: 192.168.178.141
mqtt_port: 1883
mqtt_user: ""
mqtt_password: ""

topic_prefix: dachs
interval: 15

sectors:
  basic: true
  bd3112: false
  brenner: true
  hydraulik: true
  temperaturen: true
  aktoren: true
  tageslauf: false
  mehrmodul: true
  wartung: true
```

### Sector explanation

| Sector        | Description |
|---------------|-------------|
| basic         | Basic system info |
| bd3112        | BD3112 module values |
| brenner       | Burner state & flags |
| hydraulik     | Pumps, valves, hydraulics |
| temperaturen  | All temperature sensors |
| aktoren       | Actuators (switches) |
| tageslauf     | Daily bitmask values |
| mehrmodul     | Multi-module systems |
| wartung       | Maintenance & warnings |

Disable sectors you don’t need to reduce load.

---

## 🧩 Home Assistant MQTT Discovery

The add-on automatically publishes discovery topics:

```
homeassistant/<entity_type>/<entity_id>/config
```

Each entity includes:

- name  
- unique_id  
- state_topic  
- device_class  
- state_class  
- unit_of_measurement  
- device block with sector grouping  

Entities appear automatically in Home Assistant under:

**Devices → Dachs – <Sector>**

---

## 🏗️ Architecture

```
ha-dachs-mqtt/
│
├── config.yaml          # Add-on definition
├── Dockerfile           # Supervisor-compatible image
├── run.sh               # Entry point
│
└── dachs_mqtt/
    ├── dachs.py         # Main logic
    ├── sectors.py       # Sector definitions
    ├── zumdachs.py      # Full key list
    ├── requirements.txt # Python dependencies
    └── __init__.py
```

---

## 🛠️ Development

### Build multi-arch images

This repository includes GitHub Actions workflow:

```
.github/workflows/build.yml
```

It builds and publishes:

```
ghcr.io/<user>/ha-dachs-mqtt/dachs_mqtt-{arch}:latest
ghcr.io/<user>/ha-dachs-mqtt/dachs_mqtt-{arch}:<version>
```

Trigger by tagging a release:

```bash
git tag v1.0.5
git push --tags
```

---

## 🧪 Testing locally

Run the add-on container manually:

```bash
docker build -t dachs_mqtt .
docker run --network host dachs_mqtt
```

---

## 📜 License

MIT License – see LICENSE file.

---

## ❤️ Credits

Created by **Jakob (schpuntik)**  
Optimized for reliability, clarity, and SCADA-style monitoring.
```

---
