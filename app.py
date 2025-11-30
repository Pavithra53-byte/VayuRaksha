import streamlit as st
from pathlib import Path
import base64

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="VayuRaksha Dashboard",
    page_icon="🌬️",
    layout="wide"
)

# ---------------------------------------------------
# BACKGROUND IMAGE WITH 45% DARK OVERLAY
# ---------------------------------------------------
def set_bg(image_path):
    img = Path(image_path)
    if img.exists():
        encoded = base64.b64encode(img.read_bytes()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background: 
                linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        .main-card {{
            background: rgba(255,255,255,0.90);
            padding: 28px;
            border-radius: 18px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }}
        </style>
        """, unsafe_allow_html=True)

# Load background
set_bg("assets/bg.jpg")

# ---------------------------------------------------
# MAIN HEADER CARD
# ---------------------------------------------------
st.markdown(
    """
    <div class='main-card'>
        <h1 style='font-size:44px; font-weight:800; color:#001122;'>
            VayuRaksha — Smart Urban Air Protection System
        </h1>
        <p style='font-size:20px; margin-top:-10px; color:#003344;'>
            AI + IoT Powered Pollution Control for Sustainable Urban Transport
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")  # spacing

# ---------------------------------------------------
# MISSION SECTION
# ---------------------------------------------------
st.markdown(
    """
    <div class='main-card'>
    <h3 style='font-size:30px; color:#001122;'>Mission</h3>

VayuRaksha is an **AI + IoT powered urban air safety network** designed to protect commuters and residents from harmful pollution using:

- IoT sensor units placed on street poles  
- Solar-powered pollutant absorption modules  
- AI-powered AQI / PM2.5 prediction engine  
- Smart route recommendations for safer travel  
- Real-time city-wide air quality dashboards  

    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# ---------------------------------------------------
# NAVIGATION SECTION
# ---------------------------------------------------
st.markdown(
    """
    <div class='main-card'>
        <h3 style='font-size:30px; color:#001122;'>Navigation Menu</h3>

        Use the sidebar to explore:

- Route Pollution Analyzer  
- AI AQI / PM2.5 Prediction  
- IoT Device Dashboard  
- Pollution Heatmap  
- City Dashboard  

    </div>
    """,
    unsafe_allow_html=True
)
