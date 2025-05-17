from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import json
from math import radians, sin, cos, sqrt, atan2
import os

app = Flask(__name__)

GEOFENCE_FILE = "geofence.json"
LATEST_FILE = "latest.json"

# --- GEOFENCE UTILITIES ---
def load_geofence():
    if os.path.exists(GEOFENCE_FILE):
        with open(GEOFENCE_FILE, 'r') as f:
            return json.load(f)
    try:
        with open(LATEST_FILE, "r") as f:
            data = json.load(f)
            return {"lat": data["latitude"], "lon": data["longitude"], "radius": 50}
    except Exception:
        return {"lat": 33.744078, "lon": 72.786381, "radius": 50}

def save_geofence(data):
    with open(GEOFENCE_FILE, 'w') as f:
        json.dump(data, f)

def is_outside_geofence(lat, lon, center_lat, center_lon, radius_meters):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat - center_lat)
    dlon = radians(lon - center_lon)
    a = sin(dlat / 2)**2 + cos(radians(center_lat)) * cos(radians(lat)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance > radius_meters

# --- MAIN ENDPOINT TO RECEIVE COORDINATES ---
@app.route('/Mapapi/server.py', methods=['GET'])
def receive_coordinates():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        msg = request.args.get('msg', '')

        geofence = load_geofence()
        center_lat, center_lon, radius = geofence["lat"], geofence["lon"], geofence["radius"]

        status_msg = "OUTSIDE GEOFENCE RANGE" if is_outside_geofence(lat, lon, center_lat, center_lon, radius) else "INSIDE SAFE ZONE"

        data = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "geofence_status": status_msg,
            "message": msg
        }

        with open(LATEST_FILE, "w") as f:
            json.dump(data, f)

        print(f"[RECEIVED] Lat: {lat}, Lon: {lon}, Status: {status_msg}")
        return jsonify({"status": "OK", "message": "Coordinates received"}), 200

    except Exception as e:
        return jsonify({"status": "FAIL", "error": str(e)}), 400

# --- SET GEOFENCE FROM CLIENT ---
@app.route('/Mapapi/set_geofence', methods=['POST'])
def set_geofence():
    try:
        content = request.get_json()
        save_geofence({
            "lat": float(content['lat']),
            "lon": float(content['lon']),
            "radius": float(content.get('radius', 50))
        })
        return jsonify({"status": "OK", "message": "Geofence updated"})
    except Exception as e:
        return jsonify({"status": "FAIL", "error": str(e)}), 400

# --- RETURN LATEST COORDINATES TO FRONTEND ---
@app.route('/Mapapi/latest')
def get_latest():
    try:
        with open(LATEST_FILE, "r") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": "Failed to load latest.json", "details": str(e)}), 500

# --- SERVE FRONTEND (OPTIONAL) ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# --- RUN SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
