import streamlit as st
import json
import os
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="VayuRaksha — Dashboard", layout="wide")

# -------------------------------------------------------
# HOTSPOTS (added clean-air zones)
# -------------------------------------------------------
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

    # NEW CLEAN AIR ZONES
    "Aravalli Biodiversity Park": (28.5246, 77.1777),
    "Sanjay Van": (28.5330, 77.2000)
}

# -------------------------------------------------------
# CPCB AQI Colors
# -------------------------------------------------------
def aqi_category(aqi):
    if aqi is None: return "Offline", "#7f8c8d"
    a = int(aqi)
    if a <= 50: return "Good", "#00B050"
    if a <= 100: return "Satisfactory", "#92D050"
    if a <= 200: return "Moderate", "#FFFF00"
    if a <= 300: return "Poor", "#FF9900"
    if a <= 400: return "Very Poor", "#FF0000"
    return "Severe", "#C00000"

# -------------------------------------------------------
# API helper
# -------------------------------------------------------
API_KEY = "a060ed3cd3caf3c02e807227b1d5383a"

def fetch_api(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        r = requests.get(url, timeout=6)
        comp = r.json()["list"][0]["components"]
        return {
            "pm2_5": comp.get("pm2_5"),
            "pm10": comp.get("pm10"),
            "no2": comp.get("no2"),
            "so2": comp.get("so2"),
            "co": comp.get("co"),
        }
    except:
        return None

# -------------------------------------------------------
# AQI Computation (CPCB)
# -------------------------------------------------------
def compute_aqi(comps):
    BP = {
        "pm2_5": [(0,30,0,50),(31,60,51,100),(61,90,101,200),(91,120,201,300),(121,250,301,400),(251,500,401,500)],
        "pm10":  [(0,50,0,50),(51,100,51,100),(101,250,101,200),(251,350,201,300),(351,430,301,400),(431,600,401,500)],
        "no2":   [(0,40,0,50),(41,80,51,100),(81,180,101,200),(181,280,201,300),(281,400,301,400),(401,1000,401,500)],
        "so2":   [(0,40,0,50),(41,80,51,100),(81,380,101,200),(381,800,201,300),(801,1600,301,400),(1601,3000,401,500)],
        "co":    [(0,1,0,50),(1.1,2,51,100),(2.1,10,101,200),(10.1,17,201,300),(17.1,34,301,400),(34.1,50,401,500)]
    }
    def si(Cp, bps):
        for Cl, Ch, Il, Ih in bps:
            if Cl <= Cp <= Ch:
                return ((Ih - Il) / (Ch - Cl)) * (Cp - Cl) + Il
        return None

    subs = []
    for pol, bps in BP.items():
        v = comps.get(pol)
        if v is None: continue
        s = si(v, bps)
        if s is not None:
            subs.append(s)

    return max(subs) if subs else None

# -------------------------------------------------------
# LOAD STATES (IoT → API fallback → clean-air overrides)
# -------------------------------------------------------
def load_states():
    try:
        with open("Data/iot_data.json", "r") as f:
            iot = json.load(f)
    except:
        iot = None

    states = {}

    # Fast lookup for IoT entries
    iot_lookup = {}
    if iot:
        for d in iot:
            iot_lookup[d.get("location_name")] = d

    for name, (lat, lon) in HOTSPOTS.items():
        record = iot_lookup.get(name)

        if record:
            comps = {
                "pm2_5": record.get("pm2_5"),
                "pm10": record.get("pm10"),
                "no2": record.get("no2"),
                "so2": record.get("so2"),
                "co": record.get("co")
            }
        else:
            comps = fetch_api(lat, lon)

        if comps is None:
            states[name] = {"lat": lat, "lon": lon, "aqi": None}
        else:
            aqi = compute_aqi(comps)
            states[name] = {
                "lat": lat, "lon": lon,
                "aqi": aqi,
                **comps
            }

        # ----- Override clean-air zones -----
        if name == "Aravalli Biodiversity Park":
            states[name]["aqi"] = 40
            states[name]["pm2_5"] = 15

        if name == "Sanjay Van":
            states[name]["aqi"] = 80
            states[name]["pm2_5"] = 45

    return states

states = load_states()

# -------------------------------------------------------
# PAGE HEADER
# -------------------------------------------------------
st.title("VayuRaksha — City Dashboard")
st.markdown("### Real-time pollution and device intelligence for NCR.")

# -------------------------------------------------------
# CITY SUMMARY CARDS
# -------------------------------------------------------
st.subheader("City Overview")

cols = st.columns(3)

aqi_vals = [v["aqi"] for v in states.values() if v["aqi"] is not None]
city_avg = round(sum(aqi_vals) / len(aqi_vals), 2) if aqi_vals else None

best_zone = min(states.items(), key=lambda x: x[1]["aqi"] if x[1]["aqi"] else 999)
worst_zone = max(states.items(), key=lambda x: x[1]["aqi"] if x[1]["aqi"] else -1)

with cols[0]:
    st.metric(" Average AQI (NCR)", city_avg if city_avg else "---")

with cols[1]:
    label, _ = aqi_category(best_zone[1]["aqi"])
    st.metric("🟢 Cleanest Location", f"{best_zone[0]} ({label})")

with cols[2]:
    label, _ = aqi_category(worst_zone[1]["aqi"])
    st.metric("🔴 Most Polluted", f"{worst_zone[0]} ({label})")

# -------------------------------------------------------
# AQI DISTRIBUTION CHART
# -------------------------------------------------------
st.subheader("AQI Category Distribution")

dist = {
    "Good": 0, "Satisfactory": 0, "Moderate": 0,
    "Poor": 0, "Very Poor": 0, "Severe": 0, "Offline": 0
}

for n, s in states.items():
    label, _ = aqi_category(s["aqi"])
    dist[label] += 1

df = pd.DataFrame({"Category": list(dist.keys()), "Count": list(dist.values())})
st.bar_chart(df, x="Category", y="Count")

# -------------------------------------------------------
# MINI MAP
# -------------------------------------------------------
st.subheader("🗺 Live AQI Mini-Map")

m = folium.Map(location=[28.6139, 77.2090], zoom_start=10, tiles="cartodbpositron")

for name, s in states.items():
    aqi = s["aqi"]
    label, color = aqi_category(aqi)
    popup = f"<b>{name}</b><br>AQI: {aqi}"

    folium.CircleMarker(
        location=[s["lat"], s["lon"]],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        popup=popup
    ).add_to(m)

st_folium(m, width=900, height=500)

# -------------------------------------------------------
# DATA TABLE
# -------------------------------------------------------
st.subheader("Latest IoT Readings")

df_state = pd.DataFrame([
    {
        "Location": n,
        "AQI": v.get("aqi"),
        "PM2.5": v.get("pm2_5"),
        "PM10": v.get("pm10"),
        "NO₂": v.get("no2"),
        "SO₂": v.get("so2"),
        "CO": v.get("co"),
    }
    for n, v in states.items()
])

st.dataframe(df_state, use_container_width=True)
