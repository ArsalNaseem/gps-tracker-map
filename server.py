from flask import Flask, request, jsonify, render_template
import json
from datetime import datetime
import os

app = Flask(__name__)

# Path to store latest GPS data
DATA_FILE = 'latest.json'

# Ensure the JSON file exists initially
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({
            "lat": 0.0,
            "lon": 0.0,
            "timestamp": "N/A"
        }, f)

# Serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# POST endpoint to update location
@app.route('/update', methods=['POST'])
def update_location():
    try:
        data = request.get_json()

        if 'lat' not in data or 'lon' not in data:
            return jsonify({"status": "error", "message": "Missing 'lat' or 'lon'"}), 400

        data['timestamp'] = datetime.now().isoformat()

        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)

        return jsonify({"status": "OK", "data": data})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# GET endpoint to return latest location
@app.route('/latest', methods=['GET'])
def get_latest():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
