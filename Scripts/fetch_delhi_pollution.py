import requests
import csv
from datetime import datetime

API_KEY = "a060ed3cd3caf3c02e807227b1d5383a"

hotspots = {
    "AIIMS Delhi": (28.5672, 77.2100),
    "Anand Vihar": (28.6460, 77.3150),
    "Chandni Chowk": (28.6562, 77.2300),
    "Connaught Place": (28.6304, 77.2177),
    "Dwarka": (28.5921, 77.0460),

    # New NCR Locations
    "Gurugram": (28.4595, 77.0266),
    "Noida Sector 62": (28.6289, 77.3649),
    "Greater Noida": (28.4744, 77.5080),
    "Faridabad": (28.4089, 77.3178),
    "Ghaziabad": (28.6692, 77.4538),

    # Low-pollution areas for variation
    "Lodhi Road": (28.5918, 77.2197),
    "Vasant Kunj": (28.5204, 77.1580)
}

def get_pollution(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    r = requests.get(url)
    return r.json()

csv_path = "Data/pollution_data.csv"

for name, (lat, lon) in hotspots.items():
    data = get_pollution(lat, lon)
    comp = data["list"][0]["components"]

    row = [
        datetime.now(),
        name,
        lat,
        lon,
        comp["pm2_5"],
        comp["pm10"],
        comp["no2"],
        comp["co"],
        comp["so2"]
    ]

    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

print("✔ Data saved to pollution_data.csv")
