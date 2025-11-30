import json
import os
import pandas as pd

print("Checking Data Folder...\n")

# 1. iot_data.json
if os.path.exists("Data/iot_data.json"):
    with open("Data/iot_data.json") as f:
        data = json.load(f)
        print("iot_data.json FOUND. First entry:")
        print(data[:1])
else:
    print("iot_data.json MISSING")

# 2. history.csv
if os.path.exists("Data/history.csv"):
    df = pd.read_csv("Data/history.csv")
    print("\nhistory.csv FOUND. Last rows:")
    print(df.tail())
else:
    print("history.csv MISSING")

# 3. pollution_data.csv
if os.path.exists("Data/pollution_data.csv"):
    df = pd.read_csv("Data/pollution_data.csv")
    print("\npollution_data.csv FOUND. Last rows:")
    print(df.tail())
else:
    print("pollution_data.csv MISSING")
