import json
import random
import time
import csv
from pathlib import Path
from datetime import datetime

# --------------------------------------------------------------
# HOTSPOT LOCATIONS
# --------------------------------------------------------------
hotspots = {
    "AIIMS Delhi": (28.5672, 77.2100),
    "Anand Vihar": (28.6460, 77.3150),
    "Chandni Chowk": (28.6562, 77.2300),
    "Connaught Place": (28.6304, 77.2177),
    "Dwarka": (28.5921, 77.0460),
    "Gurugram": (28.4595, 77.0266),
    "Noida Sector 62": (28.6289, 77.3649),
    "Greater Noida": (28.4744, 77.5080),
    "Faridabad": (28.4089, 77.3178),
    "Ghaziabad": (28.6692, 77.4538),
    "Lodhi Road": (28.5918, 77.2197),
    "Vasant Kunj": (28.5204, 77.1580),

    # CLEAN-AIR LOCATIONS
    "Aravalli Biodiversity Park": (28.5246, 77.1777),
    "Sanjay Van": (28.5330, 77.2000)
}

IOT_OUTPUT = "Data/iot_data.json"
HISTORY_FILE = "Data/history.csv"

# Create CSV if missing
if not Path(HISTORY_FILE).exists():
    with open(HISTORY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "device_id", "location",
            "pm2_5", "pm10", "no2", "so2", "co",
            "battery", "status"
        ])

# --------------------------------------------------------------
# UTILITIES
# --------------------------------------------------------------
def realistic_pm25():
    return random.uniform(60, 180)

def realistic_pm10(pm25):
    return pm25 * random.uniform(1.4, 1.8)

def realistic_no2():
    return random.uniform(20, 80)

def realistic_so2():
    return random.uniform(10, 40)

def realistic_co():  
    # REALISTIC CO mg/m³ (converted from µg range)
    return random.uniform(0.5, 3.0)

def time_multiplier():
    h = datetime.now().hour
    if 6 <= h <= 10: return 1.3
    if 18 <= h <= 22: return 1.4
    if 0 <= h <= 5: return 0.75
    return 1.0

def battery_next(bat):
    h = datetime.now().hour
    if 10 <= h <= 16:
        return min(100, bat + random.uniform(2, 4))
    return max(0, bat - random.uniform(1, 3))

def determine_status(pm25, pm10, no2, co, battery):
    if battery < 20:
        return "CRITICAL"
    if pm25 > 150 or pm10 > 250:
        return "ACTIVE"
    if no2 > 60 or co > 2.5:
        return "ACTIVE"
    return "IDLE"

# Clean-air zones special values
def clean_air_readings():
    return {
        "pm2_5": random.uniform(8, 30),
        "pm10": random.uniform(15, 55),
        "no2": random.uniform(5, 20),
        "so2": random.uniform(3, 10),
        "co": random.uniform(0.2, 1.0)
    }

# --------------------------------------------------------------
# MAIN LOOP
# --------------------------------------------------------------
battery_levels = {name: random.uniform(40, 90) for name in hotspots}

while True:
    data_out = []
    mult = time_multiplier()

    for name, (lat, lon) in hotspots.items():

        if name in ["Aravalli Biodiversity Park", "Sanjay Van"]:
            r = clean_air_readings()
        else:
            pm25 = realistic_pm25() * mult
            r = {
                "pm2_5": pm25,
                "pm10": realistic_pm10(pm25),
                "no2": realistic_no2(),
                "so2": realistic_so2(),
                "co": realistic_co()
            }

        battery_levels[name] = battery_next(battery_levels[name])
        battery = round(battery_levels[name], 1)

        status = determine_status(
            r["pm2_5"], r["pm10"], r["no2"], r["co"], battery
        )

        row = {
            "device_id": name.replace(" ", "_"),
            "location_name": name,
            "lat": lat,
            "lon": lon,
            "pm2_5": round(r["pm2_5"], 2),
            "pm10": round(r["pm10"], 2),
            "no2": round(r["no2"], 2),
            "so2": round(r["so2"], 2),
            "co": round(r["co"], 2),  # mg/m³
            "battery": battery,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }

        data_out.append(row)

        with open(HISTORY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                row["timestamp"], row["device_id"], name,
                row["pm2_5"], row["pm10"], row["no2"], row["so2"], row["co"],
                battery, status
            ])

    with open(IOT_OUTPUT, "w") as f:
        json.dump(data_out, f, indent=4)

    print("IoT data updated...")
    time.sleep(5)
