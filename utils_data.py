# utils_data.py
import json
import os
import requests
import math
from datetime import datetime
import pandas as pd

# --------------------------------------------------------
# HOTSPOTS
# --------------------------------------------------------
HOTSPOTS = {
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

    # Clean-air zones
    "Aravalli Biodiversity Park": (28.5246, 77.1777),
    "Sanjay Van": (28.5330, 77.2000)
}

# --------------------------------------------------------
# API KEY
# --------------------------------------------------------
API_KEY = "a060ed3cd3caf3c02e807227b1d5383a"

def fetch_api(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        r = requests.get(url, timeout=6)
        data = r.json()["list"][0]["components"]
        return {
            "pm2_5": data.get("pm2_5"),
            "pm10": data.get("pm10"),
            "no2": data.get("no2"),
            "so2": data.get("so2"),
            "co": data.get("co")
        }
    except:
        return None

# --------------------------------------------------------
# AQI CALCULATION (CPCB)
# --------------------------------------------------------
BREAKPOINTS = {
    "pm2_5": [(0,30,0,50),(31,60,51,100),(61,90,101,200),
              (91,120,201,300),(121,250,301,400),(251,500,401,500)],
    "pm10":  [(0,50,0,50),(51,100,51,100),(101,250,101,200),
              (251,350,201,300),(351,430,301,400),(431,600,401,500)],
    "no2":   [(0,40,0,50),(41,80,51,100),(81,180,101,200),
              (181,280,201,300),(281,400,301,400),(401,1000,401,500)],
    "so2":   [(0,40,0,50),(41,80,51,100),(81,380,101,200),
              (381,800,201,300),(801,1600,301,400),(1601,3000,401,500)],
    "co":    [(0,1,0,50),(1.1,2,51,100),(2.1,10,101,200),
              (10.1,17,201,300),(17.1,34,301,400),(34.1,50,401,500)],
}

def compute_subindex(Cp, bps):
    if Cp is None:
        return None
    for Cl, Ch, Il, Ih in bps:
        if Cl <= Cp <= Ch:
            return ((Ih - Il) / (Ch - Cl)) * (Cp - Cl) + Il
    return None

def compute_aqi(comps):
    subs = []
    for pol, bps in BREAKPOINTS.items():
        v = comps.get(pol)
        if v is None:
            continue
        si = compute_subindex(v, bps)
        if si is not None:
            subs.append(si)

    return max(subs) if subs else None

# --------------------------------------------------------
# LOAD IoT FILE
# --------------------------------------------------------
def load_iot():
    try:
        with open("Data/iot_data.json", "r") as f:
            return json.load(f)
    except:
        return None

# --------------------------------------------------------
# MAIN FUNCTION: LOAD STATES
# --------------------------------------------------------
def load_states():
    iot = load_iot()
    lookup = {d.get("location_name"): d for d in iot} if iot else {}

    states = {}

    for name, (lat, lon) in HOTSPOTS.items():
        if name in lookup:
            rec = lookup[name]
            comps = {
                "pm2_5": rec.get("pm2_5"),
                "pm10": rec.get("pm10"),
                "no2": rec.get("no2"),
                "so2": rec.get("so2"),
                "co": rec.get("co"),
            }
        else:
            comps = fetch_api(lat, lon)

        if comps is None:
            states[name] = {"lat": lat, "lon": lon, "aqi": None}
            continue

        aqi = compute_aqi(comps)

        states[name] = {
            "lat": lat,
            "lon": lon,
            "aqi": aqi,
            **comps
        }

        # CLEAN AIR OVERRIDES
        if name == "Aravalli Biodiversity Park":
            states[name]["aqi"] = 40
            states[name]["pm2_5"] = 15

        if name == "Sanjay Van":
            states[name]["aqi"] = 80
            states[name]["pm2_5"] = 45

    return states

# --------------------------------------------------------
# HAVERSINE FOR ROUTE
# --------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi/2)**2 +
         math.cos(p1)*math.cos(p2)*math.sin(dlambda/2)**2)

    return 2 * R * math.asin(math.sqrt(a))
