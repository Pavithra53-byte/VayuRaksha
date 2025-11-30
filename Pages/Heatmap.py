import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import json
import os

st.set_page_config(page_title="AQI Heat Map", layout="wide")
st.title("AQI Heat Map — Delhi NCR")

# ---------------------------
# CPCB AQI Calculation
# ---------------------------
def compute_individual_index(Cp, Clow, Chigh, Ilow, Ihigh):
    return ((Ihigh - Ilow) / (Chigh - Clow)) * (Cp - Clow) + Ilow

def aqi_from_components(pm25, pm10, no2, so2, co):

    sub = []

    # PM2.5
    if pm25 <= 30: sub.append(compute_individual_index(pm25,0,30,0,50))
    elif pm25 <= 60: sub.append(compute_individual_index(pm25,31,60,51,100))
    elif pm25 <= 90: sub.append(compute_individual_index(pm25,61,90,101,200))
    elif pm25 <= 120: sub.append(compute_individual_index(pm25,91,120,201,300))
    elif pm25 <= 250: sub.append(compute_individual_index(pm25,121,250,301,400))
    else: sub.append(compute_individual_index(pm25,251,350,401,500))

    # PM10
    if pm10 <= 50: sub.append( compute_individual_index(pm10,0,50,0,50))
    elif pm10 <= 100: sub.append( compute_individual_index(pm10,51,100,51,100))
    elif pm10 <= 250: sub.append( compute_individual_index(pm10,101,250,101,200))
    elif pm10 <= 350: sub.append( compute_individual_index(pm10,251,350,201,300))
    elif pm10 <= 430: sub.append( compute_individual_index(pm10,351,430,301,400))
    else: sub.append( compute_individual_index(pm10,431,600,401,500))

    # NO2
    if no2 <= 40: sub.append(compute_individual_index(no2,0,40,0,50))
    elif no2 <= 80: sub.append(compute_individual_index(no2,41,80,51,100))
    elif no2 <= 180: sub.append(compute_individual_index(no2,81,180,101,200))
    elif no2 <= 280: sub.append(compute_individual_index(no2,181,280,201,300))
    elif no2 <= 400: sub.append(compute_individual_index(no2,281,400,301,400))
    else: sub.append(compute_individual_index(no2,401,500,401,500))

    # SO2
    if so2 <= 40: sub.append(compute_individual_index(so2,0,40,0,50))
    elif so2 <= 80: sub.append(compute_individual_index(so2,41,80,51,100))
    elif so2 <= 380: sub.append(compute_individual_index(so2,81,380,101,200))
    elif so2 <= 800: sub.append(compute_individual_index(so2,381,800,201,300))
    elif so2 <= 1600: sub.append(compute_individual_index(so2,801,1600,301,400))
    else: sub.append(compute_individual_index(so2,1601,2000,401,500))

    # CO (mg/m3)
    if co <= 1: sub.append(compute_individual_index(co,0,1,0,50))
    elif co <= 2: sub.append(compute_individual_index(co,1,2,51,100))
    elif co <= 10: sub.append(compute_individual_index(co,2,10,101,200))
    elif co <= 17: sub.append(compute_individual_index(co,10,17,201,300))
    elif co <= 34: sub.append(compute_individual_index(co,17,34,301,400))
    else: sub.append(compute_individual_index(co,34,50,401,500))

    return max(sub)

# ---------------------------
# LOAD LIVE IOT DATA
# ---------------------------
if not os.path.exists("Data/iot_data.json"):
    st.error("IoT Data file missing.")
    st.stop()

with open("Data/iot_data.json") as f:
    data = json.load(f)

heat_points = []
markers = []

for d in data:
    # CO is already in mg/m3 now → no scaling needed
    aqi = aqi_from_components(
        d["pm2_5"], d["pm10"], d["no2"], d["so2"], d["co"]
    )

    intensity = min(1.0, max(0.01, aqi / 500))

    heat_points.append([d["lat"], d["lon"], intensity])
    markers.append((d["lat"], d["lon"], aqi, d["location_name"]))

# ---------------------------
# MAP
# ---------------------------
m = folium.Map(location=[28.6139, 77.2090], zoom_start=10, tiles="cartodbpositron")

HeatMap(heat_points, radius=35, blur=25).add_to(m)

for lat, lon, aqi, name in markers:
    folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        color="black",
        fill=True,
        fill_color="red" if aqi > 300 else "orange" if aqi > 150 else "green",
        tooltip=f"{name} — AQI: {int(aqi)}"
    ).add_to(m)

st_folium(m, width=1200, height=700)
