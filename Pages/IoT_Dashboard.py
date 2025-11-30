import streamlit as st
import json
import requests
from datetime import datetime

st.set_page_config(page_title="IoT Dashboard — VayuRaksha", layout="wide")

# ----------------- CSS -----------------
st.markdown("""
<style>
.device-card {
    background: #ffffff;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}
.device-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 6px;
}
.status-tag {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    color: white;
}
.small-text {
    font-size: 12px;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# ------------------ AQI COLOR FUNCTION ------------------
def get_aqi_category(aqi):
    if aqi is None:
        return "Offline", "#7f8c8d"
    try:
        a = float(aqi)
    except:
        return "Unknown", "#7f8c8d"
    if a <= 50: return "Good", "#00B050"
    if a <= 100: return "Satisfactory", "#92D050"
    if a <= 200: return "Moderate", "#FFFF00"
    if a <= 300: return "Poor", "#FF9900"
    if a <= 400: return "Very Poor", "#FF0000"
    return "Severe", "#C00000"

# ------------------ LOAD IoT DATA ------------------
def load_iot_data():
    try:
        with open("Data/iot_data.json", "r") as f:
            return json.load(f)
    except:
        return []

iot_data = load_iot_data()

# -----------------------------------------------------
# MANUALLY ADD 2 NEW LOCATIONS IF THEY ARE MISSING
# -----------------------------------------------------
extra_locations = {
    "Aravalli Biodiversity Park": {
        "location_name": "Aravalli Biodiversity Park",
        "pm2_5": 15,
        "pm10": 40,
        "no2": 12,
        "so2": 5,
        "co": 0.2,
        "battery": 95,
        "status": "ACTIVE",
        "timestamp": str(datetime.now())
    },
    "Sanjay Van": {
        "location_name": "Sanjay Van",
        "pm2_5": 45,
        "pm10": 70,
        "no2": 25,
        "so2": 10,
        "co": 0.3,
        "battery": 92,
        "status": "ACTIVE",
        "timestamp": str(datetime.now())
    }
}

# Add them ONLY if not present in iot_data.json
present_names = {d.get("location_name") for d in iot_data}

for name, data in extra_locations.items():
    if name not in present_names:
        iot_data.append(data)

# ------------------ PAGE TITLE ------------------
st.title("IoT Dashboard — Live Device Status")
st.write("Shows real-time IoT sensor data across city hotspots.")

if not iot_data:
    st.warning("No IoT data found. Start the IoT simulator.")
    st.stop()

# ------------------ SHOW DEVICES ------------------
cols = st.columns(3)
i = 0

for device in iot_data:
    name = device.get("location_name")
    pm25 = device.get("pm2_5")
    pm10 = device.get("pm10")
    no2 = device.get("no2")
    so2 = device.get("so2")
    co = device.get("co")
    battery = device.get("battery")
    status = device.get("status")
    timestamp = device.get("timestamp")

    # AQI approx (PM2.5 based)
    aqi_value = pm25 if pm25 else 0
    aqi_cat, aqi_color = get_aqi_category(aqi_value)

    with cols[i % 3]:
        st.markdown("<div class='device-card'>", unsafe_allow_html=True)

        # Title
        st.markdown(f"<div class='device-title'>{name}</div>", unsafe_allow_html=True)

        # Status Tag
        status_color = "#27ae60" if status == "ACTIVE" else "#c0392b"
        st.markdown(
            f"<div class='status-tag' style='background:{status_color}'>{status}</div>",
            unsafe_allow_html=True
        )
        st.write("")

        # AQI BOX
        aqi_box = f"""
        <div style="
            background:{aqi_color};
            color:white;
            padding:6px 12px;
            width:fit-content;
            border-radius:8px;
            margin-top:10px;
            margin-bottom:12px;
            font-weight:600;
        ">
            AQI: {aqi_cat} ({round(aqi_value,2)})
        </div>
        """
        st.markdown(aqi_box, unsafe_allow_html=True)

        # Pollutants
        poll_html = f"""
        <p><b>PM2.5:</b> {pm25} µg/m³</p>
        <p><b>PM10:</b> {pm10} µg/m³</p>
        <p><b>NO₂:</b> {no2} µg/m³</p>
        <p><b>SO₂:</b> {so2} µg/m³</p>
        <p><b>CO:</b> {co} µg/m³</p>
        <p><b>Battery:</b> {battery}%</p>
        <p class='small-text'>
        <b>Last Updated:</b><br>{timestamp}
        </p>
        """
        st.markdown(poll_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    i += 1
