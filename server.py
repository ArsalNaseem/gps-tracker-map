from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import json
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Define geofence center and radius (real)
GEOFENCE_CENTER = (33.744078, 72.786381)  # Update if needed
GEOFENCE_RADIUS = 10  # in meters

def is_outside_geofence(lat, lon, center_lat, center_lon, radius_meters):
    R = 6371000  # Earth radius in meters
    dlat = radians(lat - center_lat)
    dlon = radians(lon - center_lon)
    a = sin(dlat / 2)**2 + cos(radians(center_lat)) * cos(radians(lat)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance > radius_meters

@app.route('/Mapapi/track.php', methods=['GET'])
def receive_coordinates():
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        status_msg = (
            "OUTSIDE GEOFENCE RANGE"
            if is_outside_geofence(lat, lon, *GEOFENCE_CENTER, GEOFENCE_RADIUS)
            else "INSIDE SAFE ZONE"
        )

        data = {
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "geofence_status": status_msg
        }

        with open("latest.json", "w") as f:
            json.dump(data, f)

        return jsonify({"status": "OK", "message": "Coordinates received"}), 200

    except Exception as e:
        return jsonify({"status": "FAIL", "error": str(e)}), 400

@app.route('/Mapapi/latest')
def get_latest():
    try:
        with open("latest.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Failed to load JSON", "details": str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
