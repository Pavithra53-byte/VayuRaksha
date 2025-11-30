# predict_aqi.py

import pandas as pd
import pickle
import os
from datetime import datetime, timedelta

MODEL_PATH = "Models/pm25_model.pkl"
CSV_PATH = "Data/pollution_data.csv"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ Model not found. Train using train_model.py")

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("❌ Data file not found: Data/pollution_data.csv")

# Load model
model = pickle.load(open(MODEL_PATH, "rb"))

# Load dataset
df = pd.read_csv(CSV_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# Create time index (same as training)
df["tidx"] = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds() / 3600

# Get last row
last_row = df.iloc[-1]
last_tidx = last_row["tidx"]

print("\n📌 Base reference time:", last_row["timestamp"])
print("Last PM2.5 reading:", last_row["pm2_5"])

# Prediction intervals (in hours)
intervals = {
    "30 minutes": 0.5,
    "1 hour": 1.0,
    "2 hours": 2.0,
    "4 hours": 4.0
}

print("\n🔮 Predicted PM2.5 values:\n")

for label, step in intervals.items():
    t_future = last_tidx + step

    # MODEL REQUIRES ALL FEATURES
    sample = [
        [
            last_row["pm10"],
            last_row["no2"],
            last_row["so2"],
            last_row["co"],
            t_future
        ]
    ]

    pred = model.predict(sample)[0]
    pred = max(pred, 0)

    print(f"{label}: {pred:.2f} µg/m³")
