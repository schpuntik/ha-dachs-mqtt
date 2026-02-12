# Dachs2MQTT – Home Assistant Add-on  
Reads values from SenerTec Dachs via HTTP and publishes them to MQTT with full Home Assistant Discovery support.

---

## ✨ Features

- 🔌 **Reads all available Dachs parameters** via the internal HTTP interface  
- 📡 **Publishes values to MQTT** in real time  
- 🧩 **Automatic Home Assistant MQTT Discovery**  
  - `sensor`
  - `binary_sensor`
  - `switch` (read-only)
  - `number` (future support)
- 🗂️ **Sector-based grouping** (Hydraulik, Brenner, Temperaturen, Wartung, etc.)
- 🏭 **SCADA-friendly entity grouping**  
  Entities are grouped by sector for clean dashboards.
- 🧠 **Automatic type detection**  
  - Temperatures → °C  
  - Power → kW  
  - Energy → kWh  
  - Bitmasks → binary_sensor  
  - Aktoren → switch  
- 🧱 **Modular architecture**  
  - `sectors.py` – sector definitions  
  - `zumdachs.py` – full key list  
  - `dachs.py` – main logic  

---

## 📦 Installation

### 1. Add repository to Home Assistant

Go to:

**Settings → Add-ons → Add-on Store → ⋮ → Repositories**

Add:

