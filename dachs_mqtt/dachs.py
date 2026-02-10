#!/usr/bin/env python3
import os
import time
import json
import requests
import paho.mqtt.client as mqtt

CONFIG_PATH = "/data/options.json"
with open(CONFIG_PATH, "r") as f:
    cfg = json.load(f)

DACHS_HOST = cfg["dachs_host"]
DACHS_USER = cfg["dachs_user"]
DACHS_PASS = cfg["dachs_password"]

MQTT_HOST = cfg["mqtt_host"]
MQTT_PORT = cfg["mqtt_port"]
TOPIC_PREFIX = cfg["topic_prefix"]
INTERVAL = cfg["interval"]

DACHS_URL = f"http://{DACHS_HOST}:8080/getKey?k="
DACHS_URL_END = "&_rnd=9619"

# -----------------------------
# ВСТАВЬ СЮДА ПОЛНЫЙ СПИСОК
# ИЗ ТВОЕГО ОРИГИНАЛЬНОГО СКРИПТА
# -----------------------------
ZumDachs = (
		[1,"Hka_Bd.Anforderung.ModulAnzahl",        "Anzahl der angeforderten Module",          ""],
		[4,"Hka_Bd.Anforderung.UStromF_Anf.bFlagSF","Anforderungen Stromfuehrung Bit Codiert",  ""],
		[4,"Hka_Bd.UStromF_Frei.bFreigabe",         "Freigabe Stromfuehrung Bit Codiert",       ""],
		[1,"Hka_Bd.bStoerung",			    "Aktuelle Stoerung Dachs = Wert + 100",     ""],
		[1,"Hka_Bd.bWarnung",			    "Aktueller Warncode Dachs = Wert + 600",    ""],
		[1,"Hka_Bd.UHka_Anf.Anforderung.fStrom",    "Anforderung Strom Flag",                   ""],
		[3,"Hka_Bd.UHka_Anf.usAnforderung",	    "Anforderung Dachs Bit Codiert",            ""],
		[3,"Hka_Bd.UHka_Frei.usFreigabe",	    "Freigabe Dachs Bit Codiert",               ""],
		[1,"Hka_Bd.ulArbeitElektr",		    "Erzeugte elektrische Arbeit kWh",          "b44a3af10-21ad-11e6-815a-cb474497d58e"],
		[1,"Hka_Bd.ulArbeitThermHka",		    "Erzeugte thermische Arbeit kWh",           "005837f0-21ae-11e6-8568-1b849bd56c27"],
		[1,"Hka_Bd.ulArbeitThermKon",		    "Erzeugte thermische Arbeit Kondenser kWh", "29f0ef60-21ae-11e6-a6fb-b10b93766e50"],
		[1,"Hka_Bd.ulBetriebssekunden",		    "Betriebsstunden Dachs Stunden",            "55749930-12ae-11e6-9aa9-2d1b06fad85e"],
		[1,"Hka_Bd.ulAnzahlStarts",		    "Anzahl Starts Dachs",                      ""],
		[1,"Hka_Bd_Stat.uchSeriennummer",	    "Seriennummer 10-stellig",                  ""],
		[1,"Hka_Bd_Stat.uchTeilenummer",	    "Teilenummer 10-stellig",                   ""],
		[1,"Hka_Bd_Stat.ulInbetriebnahmedatum",	    "Inbetriebnahme Sekunden seit 1.1.2000",    ""],
#
#Betriebsdaten 31.12.
		[1,"BD3112.Hka_Bd.ulBetriebssekunden",	"31.12:Betriebsstunden Dachs Stunden",            ""],
		[1,"BD3112.Hka_Bd.ulAnzahlStarts",	"31.12:Anzahl Starts Dachs",                      ""],
		[1,"BD3112.Hka_Bd.ulArbeitElektr",	"31.12:Erzeugte elektrische Arbeit kWh",          ""],
		[1,"BD3112.Hka_Bd.ulArbeitThermHka",	"31.12:Erzeugte thermische Arbeit kWh",           ""],
		[1,"BD3112.Hka_Bd.ulArbeitThermKon",	"31.12:Erzeugte thermische Arbeit Kondenser kWh", ""],
		[1,"BD3112.Ww_Bd.ulWwMengepA",		"31.12:Warmwassermenge pro Jahr m3",              ""],
#
#Daten 2. Warmeerzeuger
		[1,"Brenner_Bd.bIstStatus",		   "Status des SEplus Flag",                    ""],
		[1,"Brenner_Bd.bWarnung",		   "Warncode SEplus = Wert + 600",              ""],
		[4,"Brenner_Bd.UBrenner_Anf.usAnforderung","Anforderung Bit Codiert",                   ""],
		[4,"Brenner_Bd.UBrenner_Frei.bFreigabe",   "Freigabe Bit Codiert",                      ""],
		[1,"Brenner_Bd.ulAnzahlStarts",		   "Erzeugte thermische Arbeit kWh",            ""],
		[1,"Brenner_Bd.ulBetriebssekunden",	   "Erzeugte thermische Arbeit Kondenser kWh",  ""],
#
#Hydraulik Schema
		[1,"Hka_Ew.HydraulikNr.bSpeicherArt",	  "Speicherart",            ""],
		[1,"Hka_Ew.HydraulikNr.bWW_Art",	  "Brauchwasserbereitung",  ""],
		[1,"Hka_Ew.HydraulikNr.b2_Waermeerzeuger","2. Waermeerzeuger",      ""],
		[1,"Hka_Ew.HydraulikNr.bMehrmodul",	  "Mehrmodultechnik",       ""],
#
#Temperaturen
		[1,"Hka_Mw1.Temp.sAbgasHKA",		"Abgastemperatur Dachs C",        "4fb710c0-21aa-11e6-b664-d9a3367711f9"],
		[1,"Hka_Mw1.Temp.sAbgasMotor",		"Abgastemperatur Motor C",        "8639b840-21aa-11e6-a1f4-95a666850239"],
		[1,"Hka_Mw1.Temp.sKapsel",		"Kapseltemperatur C",             "a8e19160-21aa-11e6-861a-2d4575dff74c"],
		[1,"Hka_Mw1.Temp.sbAussen",		"Aussentemperatur C",             "f6945690-21a7-11e6-a657-afdacd3be8ba"],
		[1,"Hka_Mw1.Temp.sbFreigabeModul",	"Freigabe Modul C",               ""],
		[1,"Hka_Mw1.Temp.sbFuehler1",		"Temperatur Fuehler 1 (F1) C",    "dad0d4a0-21aa-11e6-75cb-bfb031667d12"],
		[1,"Hka_Mw1.Temp.sbFuehler2",		"Temperatur Fuehler 2 (F2) C",    "fcf04f20-21aa-11e6-af4a-e155fab6eb1b"],
		[1,"Hka_Mw1.Temp.sbGen",  		"Dachs Eintrittstemperatur C",    "5bb6cb20-21ab-11e6-86ed-77ef37378af7"],
		[1,"Hka_Mw1.Temp.sbMotor",		"Kuehlwassertemperatur Motor C",  "82e27440-21ab-11e6-8b73-2761738ed83a"],
		[1,"Hka_Mw1.Temp.sbRegler",		"Interne Reglertemperatur C",     "9e865c40-21ab-11e6-8cca-19daedb0826e"],
		[1,"Hka_Mw1.Temp.sbRuecklauf",		"Ruecklauftemperatur C",          "b965b1d0-21ab-11e6-b67b-cbfd5739138e"],
		[1,"Hka_Mw1.Temp.sbVorlauf",		"Vorlauftemperatur C",            "d6805bb0-21ab-11e6-95d6-55e2efeb7161"],
		[1,"Hka_Mw1.Temp.sbZS_Fuehler3",	"Temperatur Fuehler 3 (F3) C",    ""],
		[1,"Hka_Mw1.Temp.sbZS_Fuehler4",	"Temperatur Fuehler 4 (F4) C",    ""],
		[1,"Hka_Mw1.Temp.sbZS_Vorlauf1",	"Vorlauftemperatur Heizkreis 1 C","fad91320-21ab-11e6-bd6b-578fa070cc2e"],
		[1,"Hka_Mw1.Temp.sbZS_Vorlauf2",	"Vorlauftemperatur Heizkreis 2 C",""],
		[1,"Hka_Mw1.Temp.sbZS_Warmwasser",	"Temperatur Warmwasser C",        ""],
		[1,"Hka_Mw1.Solltemp.sbRuecklauf",	"Solltemperatur Ruecklauf C",     ""],
		[1,"Hka_Mw1.Solltemp.sbVorlauf",	"Solltemperatur Vorlauf C",       ""],
#
#Aktoren
		[1,"Hka_Mw1.Aktor.bWwPumpe",		"Brauchwasserladepumpe %",            ""],
		[1,"Hka_Mw1.Aktor.fFreiAltWaerm",	"Freigabe Waermeerzeuger Flag",       ""],
		[1,"Hka_Mw1.Aktor.fMischer1Auf",	"Mischer 1 Auf Flag",                 ""],
		[1,"Hka_Mw1.Aktor.fMischer1Zu",		"Mischer 1 Zu Flag",                  ""],
		[1,"Hka_Mw1.Aktor.fMischer2Auf",	"Mischer 2 Auf Flag",                 ""],
		[1,"Hka_Mw1.Aktor.fMischer2Zu",		"Mischer 2 Zu Flag",                  ""],
		[1,"Hka_Mw1.Aktor.fProgAus1",		"Programmierbarer Ausgang 1 Flag",    ""],
		[1,"Hka_Mw1.Aktor.fProgAus2",		"Programmierbarer Ausgang 2 Flag",    ""],
		[1,"Hka_Mw1.Aktor.fProgAus3",		"Programmierbarer Ausgang 2 Flag",    ""],
		[1,"Hka_Mw1.Aktor.fStoerung",		"Relais Stoerung Flag",               ""],
		[1,"Hka_Mw1.Aktor.fUPHeizkreis1",	"Pumpe Heizkreis 1 Flag",             "44e3e260-21dd-11e6-87c0-0fa390803568"],
		[1,"Hka_Mw1.Aktor.fUPHeizkreis2",	"Pumpe Heizkreis 2 Flag",             ""],
		[1,"Hka_Mw1.Aktor.fUPKuehlung",		"Interne Umwaelzpumpe Flag",          "753fba20-21dd-11e6-b3a8-6729e70303ef"],
		[1,"Hka_Mw1.Aktor.fUPVordruck",		"UP Vordruck Flag",                   ""],
		[1,"Hka_Mw1.Aktor.fUPZirkulation",	"Zirkulationspumpe Flag",             ""],
		[1,"Hka_Mw1.Aktor.fWartung",		"Relais Wartung Flag",                ""],
		[1,"Hka_Mw1.sWirkleistung",		"Aktuelle Wirkleistung _,_ _ kW",     "d73663e0-21ac-11e6-a0dc-23fd7dab6c31"],
		[1,"Hka_Mw1.ulMotorlaufsekunden",	"Motorlaufzeit seit Start Sekunden",  ""],
		[1,"Hka_Mw1.usDrehzahl",		"Motordrehzahl U/min",                ""],
#
#Tageslauf
		[2,"Laufraster15Min_aktTag.bDoppelstunde[0]", "15 Minuten Raster 2-4 Uhr Bit Codiert *",  ""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[1]", "15 Minuten Raster 4-6 Uhr Bit Codiert *",  ""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[2]", "15 Minuten Raster 6-8 Uhr Bit Codiert *",  ""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[3]", "15 Minuten Raster 8-10 Uhr Bit Codiert *", ""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[4]", "15 Minuten Raster 10-12 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[5]", "15 Minuten Raster 12-14 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[6]", "15 Minuten Raster 14-16 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[7]", "15 Minuten Raster 16-18 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[8]", "15 Minuten Raster 18-20 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[9]", "15 Minuten Raster 20-22 Uhr Bit Codiert *",""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[10]","15 Minuten Raster 22-0 Uhr Bit Codiert *", ""],
		[2,"Laufraster15Min_aktTag.bDoppelstunde[11]","15 Minuten Raster 0-2 Uhr Bit Codiert *",  ""],
#
#* Beispiel:
#		               02:00   03:00   04:00
#               bDoppelstunde[0] 1 1 0 0 | 0 1 1 0
#
#Mehrmodultechnik
		[1,"Mm[0].ModulSteuerung.fModulLaeuft",	   "Status Modul 1 Flag",         ""],
		[1,"Mm[0].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 1 Flag", ""],
		[1,"Mm[1].ModulSteuerung.fModulLaeuft",	   "Status Modul 2 Flag",         ""],
		[1,"Mm[1].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 2 Flag", ""],
		[1,"Mm[2].ModulSteuerung.fModulLaeuft",	   "Status Modul 3 Flag",         ""],
		[1,"Mm[2].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 3 Flag", ""],
		[1,"Mm[3].ModulSteuerung.fModulLaeuft",	   "Status Modul 4 Flag",         ""],
		[1,"Mm[3].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 4 Flag", ""],
		[1,"Mm[4].ModulSteuerung.fModulLaeuft",	   "Status Modul 5 Flag",         ""],
		[1,"Mm[4].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 5 Flag", ""],
		[1,"Mm[5].ModulSteuerung.fModulLaeuft",	   "Status Modul 6 Flag",         ""],
		[1,"Mm[5].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 6 Flag", ""],
		[1,"Mm[6].ModulSteuerung.fModulLaeuft",	   "Status Modul 7 Flag",         ""],
		[1,"Mm[6].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 7 Flag", ""],
		[1,"Mm[7].ModulSteuerung.fModulLaeuft",	   "Status Modul 8 Flag",         ""],
		[1,"Mm[7].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 8 Flag", ""],
		[1,"Mm[8].ModulSteuerung.fModulLaeuft",	   "Status Modul 9 Flag",         ""],
		[1,"Mm[8].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 9 Flag", ""],
		[1,"Mm[9].ModulSteuerung.fModulLaeuft",	   "Status Modul 10 Flag",        ""],
		[1,"Mm[9].ModulSteuerung.fModulVerfuegbar","Verfuegbarkeit Modul 10 Flag",""],
		[1,"Mm_MinMax.bModulBhMaxWart",		  "Modulnummer mit max h bis Wartung",""],
		[1,"Mm_MinMax.bModulBhMinWart",		  "Modulnummer mit min h bis Wartung",""],
		[1,"Mm_MinMax.sBhMaxWart",		  "Max h bis zur Wartung",            ""],
		[1,"Mm_MinMax.sBhMinWart",		  "Min h bis zur Wartung",            ""],
		[1,"Mm_MinMax.ModulBhMax.bModulNr",	  "Modulnummer mit max h",            ""],
		[1,"Mm_MinMax.ModulBhMax.ulWert",	  "Max h",                            ""],
		[1,"Mm_MinMax.ModulBhMin.bModulNr",	  "Modulnummer mit min h",            ""],
		[1,"Mm_MinMax.ModulBhMin.ulWert",	  "Min h",                            ""],
		[1,"Mm_MinMax.ModulStartMax.bModulNr",    "Modulnummer mit max Anzahl Starts",""],
		[1,"Mm_MinMax.ModulStartMax.ulWert",	  "Max Anzahl Starts",                ""],
		[1,"Mm_MinMax.ModulStartMin.bModulNr",    "Modulnummer mit min Anzahl Starts",""],
		[1,"Mm_MinMax.ModulStartMin.ulWert",	  "Min Anzahl Starts",                ""],
#
# Informationen ueber Wartung
		[1,"Wartung_Cache.fStehtAn",		 "Status Wartung Flag",                 ""],
		[1,"Wartung_Cache.ulBetriebssekundenBei","Betriebsstunden der letzten Wartung", ""],
		[1,"Wartung_Cache.ulZeitstempel",	 "letzte Wartung Sek seit 1.1.2000",    ""],
		[1,"Wartung_Cache.usIntervall",		 "Wartungsintervall Betriebsstunden",   ""]
)

# -----------------------------
# Функции
# -----------------------------
def read_dachs_value(key):
    url = DACHS_URL + key + DACHS_URL_END
    try:
        r = requests.get(url, auth=(DACHS_USER, DACHS_PASS), timeout=5)
        raw = r.content.decode("utf-8")
        if "=" not in raw:
            print(f"[WARN] Unexpected response for {key}: {raw}")
            return None
        return raw.split("=")[1].strip()
    except Exception as e:
        print(f"[ERROR] HTTP error for {key}: {e}")
        return None


def format_value(raw, fmt):
    if raw is None:
        return None

    if raw == "true":
        return "1"
    if raw == "false":
        return "0"

    try:
        val = int(raw)
    except:
        return raw

    if fmt == 1:
        return str(val)
    elif fmt == 2:
        return "{:08b}".format(val)
    elif fmt == 3:
        return "{:04x}".format(val)
    elif fmt == 4:
        return "{:02x}".format(val)

    return raw


def publish_discovery(client, key, desc):
    sensor_id = key.replace(".", "_")
    topic = f"homeassistant/sensor/dachs/{sensor_id}/config"

    payload = {
        "name": f"Dachs {key}",
        "state_topic": f"{TOPIC_PREFIX}/{key.replace('.', '/')}",
        "unique_id": f"dachs_{sensor_id}",
        "device": {
            "identifiers": ["dachs_system"],
            "name": "Dachs",
            "manufacturer": "Senertec"
        }
    }

    client.publish(topic, json.dumps(payload), retain=True)


def connect_mqtt():
    while True:
        try:
            client = mqtt.Client()
            client.connect(MQTT_HOST, MQTT_PORT, 60)
            client.loop_start()
            print("[INFO] Connected to MQTT")
            return client
        except Exception as e:
            print(f"[ERROR] MQTT connect failed: {e}, retry in 10s")
            time.sleep(10)


# -----------------------------
# Основной watchdog‑цикл
# -----------------------------
print("Starting Dachs → MQTT bridge with watchdog...")

mqtt_client = connect_mqtt()

# Discovery публикуем один раз при старте и при успешном реконнекте
def publish_all_discovery():
    for fmt, key, desc, uuid in ZumDachs:
        publish_discovery(mqtt_client, key, desc)
    print("[INFO] MQTT Discovery published for all registers.")

publish_all_discovery()

while True:
    try:
        loop_start = time.time()

        for fmt, key, desc, uuid in ZumDachs:
            raw = read_dachs_value(key)
            value = format_value(raw, fmt)

            if value is None:
                continue

            topic = f"{TOPIC_PREFIX}/{key.replace('.', '/')}"
            mqtt_client.publish(topic, value, retain=True)

        # выдерживаем интервал опроса
        elapsed = time.time() - loop_start
        sleep_time = max(1, INTERVAL - elapsed)
        time.sleep(sleep_time)

    except Exception as e:
        print(f"[FATAL] Unexpected error in main loop: {e}")
        # пробуем переподключить MQTT и продолжить
        try:
            mqtt_client.loop_stop()
        except Exception:
            pass
        mqtt_client = connect_mqtt()
        publish_all_discovery()
        print("[INFO] Watchdog: recovered from error, continuing...")
        time.sleep(5)
