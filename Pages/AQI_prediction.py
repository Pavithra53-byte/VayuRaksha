import streamlit as st
import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime, timedelta

# -----------------------------------------
# PAGE SETUP
# -----------------------------------------
st.set_page_config(page_title="AQI Prediction", layout="wide")
st.title("AI-Based AQI / PM2.5 Prediction Dashboard")

DATA_FILE = "Data/history.csv"   # use simulator data (LIVE)
MODEL_FILE = "Models/aqi_model.pkl"

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
if not os.path.exists(DATA_FILE):
    st.error("⚠ No history.csv found. Run IoT simulator first.")
    st.stop()

df = pd.read_csv(DATA_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# -----------------------------------------
# FIX LOCATION LIST (ADD MISSING TWO PLACES)
# -----------------------------------------
HOTSPOTS = [
    "AIIMS Delhi", "Anand Vihar", "Chandni Chowk", "Connaught Place", "Dwarka",
    "Gurugram", "Noida Sector 62", "Greater Noida", "Faridabad", "Ghaziabad",
    "Lodhi Road", "Vasant Kunj",
    "Aravalli Biodiversity Park", "Sanjay Van"
]

# filter only valid ones
locations = [loc for loc in HOTSPOTS if loc in df["location"].unique()]

loc = st.selectbox("Select Location", locations)
df_loc = df[df["location"] == loc].sort_values("timestamp")

# -----------------------------------------
# TIME RANGE TREND
# -----------------------------------------
st.subheader(f"Recent PM2.5 Trend — {loc}")

window_hours = st.slider("Select time range (hours)", 1, 48, 12)

start_time = datetime.now() - timedelta(hours=window_hours)
df_recent = df_loc[df_loc["timestamp"] >= start_time]

# if empty → show flat line instead of warning
if df_recent.empty:
    st.line_chart(pd.DataFrame({"timestamp": [], "pm2_5": []}).set_index("timestamp"))
else:
    st.line_chart(df_recent.set_index("timestamp")["pm2_5"])

# -----------------------------------------
# LOAD MODEL
# -----------------------------------------
st.subheader(" AI Predictions")

if not os.path.exists(MODEL_FILE):
    st.error("⚠ Model not found. Run train_model.py.")
    st.stop()

model = pickle.load(open(MODEL_FILE, "rb"))

# -----------------------------------------
# PREPARE FEATURES
# -----------------------------------------
df_loc["tidx"] = (df_loc["timestamp"] - df_loc["timestamp"].min()).dt.total_seconds() / 3600
last_row = df_loc.iloc[-1]

base_features = [
    last_row["pm10"],
    last_row["no2"],
    last_row["so2"],
    last_row["co"]
]

# -----------------------------------------
# Prediction intervals
# -----------------------------------------
intervals = {
    "30 minutes": 0.5,
    "1 hour": 1.0,
    "2 hours": 2.0,
    "4 hours": 4.0
}

choices = st.multiselect("Prediction intervals", list(intervals.keys()), default=["30 minutes"])

cols = st.columns(len(choices))

pred_list = []

for i, label in enumerate(choices):
    add_hours = intervals[label]
    future_tidx = df_loc["tidx"].iloc[-1] + add_hours

    features = base_features + [future_tidx]
    prediction = model.predict([features])[0]

    pred_list.append(prediction)

    cols[i].metric(label, f"{prediction:.2f} µg/m³", delta=f"from {last_row['pm2_5']:.2f}")

# -----------------------------------------
# FORECAST CURVE
# -----------------------------------------
st.subheader("Forecast Curve")

future_times = []
future_values = []

for h in np.linspace(0.1, 4, 20):
    ft = df_loc["tidx"].iloc[-1] + h
    fv = model.predict([base_features + [ft]])[0]
    future_times.append(last_row["timestamp"] + timedelta(hours=h))
    future_values.append(fv)

curve_df = pd.DataFrame({"timestamp": future_times, "pm2_5": future_values})
st.line_chart(curve_df.set_index("timestamp"))

# -----------------------------------------
# LAST 10 ROWS
# -----------------------------------------
st.subheader("Last 10 Recorded Values")
st.dataframe(df_loc.tail(10))
