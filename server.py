from flask import Flask, jsonify, send_from_directory
import json
import threading
import time
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Square path around the geofence center
coordinates = [
    # Bottom side (rightward)
    {"latitude": 33.744078, "longitude": 72.786381},
    {"latitude": 33.744078, "longitude": 72.786391},
    {"latitude": 33.744078, "longitude": 72.786401},
    {"latitude": 33.744078, "longitude": 72.786411},

    # Right side (upward)
    {"latitude": 33.744088, "longitude": 72.786411},
    {"latitude": 33.744098, "longitude": 72.786411},
    {"latitude": 33.744108, "longitude": 72.786411},

    # Top side (leftward)
    {"latitude": 33.744108, "longitude": 72.786401},
    {"latitude": 33.744108, "longitude": 72.786391},
    {"latitude": 33.744108, "longitude": 72.786381},

    # Left side (downward)
    {"latitude": 33.744098, "longitude": 72.786381},
    {"latitude": 33.744088, "longitude": 72.786381},
    {"latitude": 33.744078, "longitude": 72.786381},
]

index = 0

def is_outside_geofence(lat, lon, center_lat, center_lon, radius_meters):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat - center_lat)
    dlon = radians(lon - center_lon)
    a = sin(dlat / 2)**2 + cos(radians(center_lat)) * cos(radians(lat)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance > radius_meters

def update_coordinates():
    global index
    geofence_center = (33.744078, 72.786381)
    geofence_radius = 10  # meters

    while True:
        data = coordinates[index]
        lat = data["latitude"]
        lon = data["longitude"]

        outside = is_outside_geofence(lat, lon, *geofence_center, geofence_radius)
        status_msg = "OUTSIDE GEOFENCE RANGE" if outside else "INSIDE SAFE ZONE"

        data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["geofence_status"] = status_msg

        with open("latest.json", "w") as f:
            json.dump(data, f)

        index = (index + 1) % len(coordinates)
        time.sleep(2)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/latest')
def get_latest():
    try:
        with open("latest.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Failed to load JSON", "details": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=update_coordinates, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
