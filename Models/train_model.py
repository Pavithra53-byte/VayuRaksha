# Models/train_model.py

import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# -------------------------------------------------------
# 1. LOAD DATA
# -------------------------------------------------------
CSV_PATH = "Data/pollution_data.csv"

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("❌ File Data/pollution_data.csv not found.")

print("Loading dataset:", CSV_PATH)
df = pd.read_csv(CSV_PATH)

# -------------------------------------------------------
# 2. FORMAT TIMESTAMP + SORT
# -------------------------------------------------------
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])
df = df.sort_values("timestamp")

# Create time index in *hours*
df["tidx"] = (df["timestamp"] - df["timestamp"].min()).dt.total_seconds() / 3600

# -------------------------------------------------------
# 3. FILL MISSING VALUES
# -------------------------------------------------------
df = df.ffill().bfill()

# -------------------------------------------------------
# 4. FEATURES + TARGET
# -------------------------------------------------------
features = ["pm10", "no2", "so2", "co", "tidx"]
target = "pm2_5"

X = df[features].values
y = df[target].values

# -------------------------------------------------------
# 5. TRAIN / TEST SPLIT
# -------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------------
# 6. TRAIN MODEL
# -------------------------------------------------------
print("Training RandomForestRegressor...")
model = RandomForestRegressor(
    n_estimators=250,
    max_depth=12,
    min_samples_split=5,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------------------------------
# 7. EVALUATE
# -------------------------------------------------------
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("\n📊 MODEL PERFORMANCE")
print("-----------------------------")
print("RMSE:", round(rmse, 3))
print("R2 Score:", round(r2, 3))
print("-----------------------------")

# -------------------------------------------------------
# 8. SAVE MODEL
# -------------------------------------------------------
MODEL_PATH = "Models/pm25_model.pkl"

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"✅ Model saved to {MODEL_PATH}")
