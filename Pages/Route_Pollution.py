import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import math

# --------------------------------------------------------
# 1. Configuration and Styling
# --------------------------------------------------------

if "route_json" not in st.session_state:
    st.session_state.route_json = None

st.set_page_config(page_title="Route Pollution — VayuRaksha", layout="wide")

st.markdown("""
<style>
.panel {
    background: rgba(255,255,255,0.96);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(10,20,30,0.06);
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------
# 2. Data Definitions
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
    "Aravalli Biodiversity Park": (28.5246, 77.1777),
    "Sanjay Van": (28.5330, 77.2000),
}


def aqi_color(aqi):
    if aqi is None: return "#7f8c8d"
    a = int(aqi)
    if a <= 50: return "#00B050"
    if a <= 100: return "#92D050"
    if a <= 200: return "#FFFF00"
    if a <= 300: return "#FF9900"
    if a <= 400: return "#FF0000"
    return "#C00000"


def compute_aqi(pm25):
    if pm25 is None: return None
    pm = float(pm25)
    if pm <= 30: return 40
    if pm <= 60: return 80
    if pm <= 90: return 150
    if pm <= 120: return 250
    if pm <= 250: return 350
    return 450


# --------------------------------------------------------
# 3. Load IoT Data
# --------------------------------------------------------

def load_iot():
    try:
        with open("Data/iot_data.json") as f:
            return json.load(f)
    except:
        return None


def build_states():
    iot = load_iot()
    lookup = {d["location_name"]: d for d in iot} if iot else {}

    states = {}
    for name, (lat, lon) in HOTSPOTS.items():
        if name in lookup:
            pm25 = lookup[name].get("pm2_5")
        else:
            pm25 = None

        aqi = compute_aqi(pm25)
        states[name] = {"lat": lat, "lon": lon, "aqi": aqi}

        if name == "Aravalli Biodiversity Park":
            states[name]["aqi"] = 35
        if name == "Sanjay Van":
            states[name]["aqi"] = 60

    return states


device_states = build_states()


# --------------------------------------------------------
# 4. FIXED: Mock Route Generator (Always Works)
# --------------------------------------------------------

def get_route(slon, slat, elon, elat):
    """
    Returns a fake but smooth straight-line route.
    No internet needed. Always stable.
    """
    coords = []
    steps = 30

    for i in range(steps):
        t = i / (steps - 1)
        lat = slat * (1 - t) + elat * t
        lon = slon * (1 - t) + elon * t
        coords.append([lon, lat])

    return {
        "routes": [
            {"geometry": {"coordinates": coords}}
        ]
    }


# --------------------------------------------------------
# 5. Utility
# --------------------------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat/2)**2 +
         math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(d_lon/2)**2)
    return 2 * R * math.asin(math.sqrt(a))


def nearest_aqi(lat, lon, states):
    best, best_d = None, float("inf")
    for s in states.values():
        d = haversine(lat, lon, s["lat"], s["lon"])
        if d < best_d:
            best_d, best = d, s
    return best["aqi"] if best else None


# --------------------------------------------------------
# 6. UI
# --------------------------------------------------------

st.markdown("<div class='panel'>", unsafe_allow_html=True)
st.title("Route Pollution Analyzer — Segment Coloring")

col1, col2 = st.columns([1, 2])

with col1:
    start = st.selectbox("From", list(HOTSPOTS.keys()))
    end = st.selectbox("To", list(HOTSPOTS.keys()), index=3)

    if st.button("Analyze Route"):
        slat, slon = HOTSPOTS[start]
        elat, elon = HOTSPOTS[end]
        st.session_state.route_json = get_route(slon, slat, elon, elat)


with col2:
    st.markdown("### Legend (CPCB AQI Colors)")
    st.markdown("""
    <div style='display:flex;gap:10px'>
    <div style='background:#00B050;width:18px;height:18px'></div> Good
    <div style='background:#92D050;width:18px;height:18px'></div> Satisfactory
    <div style='background:#FFFF00;width:18px;height:18px'></div> Moderate
    <div style='background:#FF9900;width:18px;height:18px'></div> Poor
    <div style='background:#FF0000;width:18px;height:18px'></div> Very Poor
    <div style='background:#C00000;width:18px;height:18px'></div> Severe
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------------
# 7. Map Rendering
# --------------------------------------------------------

rjson = st.session_state.route_json

if not rjson:
    st.info("Select From / To and click Analyze Route.")
else:
    coords = rjson["routes"][0]["geometry"]["coordinates"]
    slat, slon = HOTSPOTS[start]
    elat, elon = HOTSPOTS[end]

    m = folium.Map(location=[(slat+elat)/2, (slon+elon)/2],
                   zoom_start=11, tiles="cartodbpositron")

    # Device markers
    for name, s in device_states.items():
        col = aqi_color(s["aqi"])
        folium.CircleMarker(
            location=[s["lat"], s["lon"]],
            radius=7, color=col, fill=True, fill_color=col,
            popup=f"{name}<br>AQI: {s['aqi']}"
        ).add_to(m)

    # Route segments
    for i in range(len(coords)-1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i+1]
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2

        seg_aqi = nearest_aqi(mid_lat, mid_lon, device_states)
        seg_col = aqi_color(seg_aqi)

        folium.PolyLine(
            locations=[[lat1, lon1], [lat2, lon2]],
            color=seg_col, weight=6, opacity=0.9
        ).add_to(m)

    st_folium(m, width=1100, height=650)

st.markdown("</div>", unsafe_allow_html=True)
