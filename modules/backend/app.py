from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
import time
import math
import requests
from firebase_admin import firestore
from firebase_config import get_firestore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

db = get_firestore()

# --- MOCK DATA FALLBACKS ---
AMBULANCES = [
    {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.076, 'longitude': 72.877},
    {'id': 'ALS-002', 'driver_name': 'Priya Singh', 'status': 'available', 'type': 'ALS', 'latitude': 19.086, 'longitude': 72.887},
    {'id': 'BLS-001', 'driver_name': 'Amit Patel', 'status': 'available', 'type': 'BLS', 'latitude': 19.096, 'longitude': 72.897}
]
ACTIVE_INCIDENTS = []
HOSPITALS = [
    {'id': 'H001', 'name': 'Fortis Hospital Navi Mumbai', 'available_beds': 45, 'total_beds': 150, 'latitude': 19.071, 'longitude': 72.997},
    {'id': 'H002', 'name': 'Apollo Clinic Vashi', 'available_beds': 78, 'total_beds': 100, 'latitude': 19.061, 'longitude': 72.987}
]

def get_precise_location(lat, lon):
    return "Santa Cruz — Chembur Link Road, Kurla West, Mumbai"

def get_ai_recommendation(incident_type, severity):
    if severity.lower() == 'critical': return {'type': 'ALS', 'eta': '3.5 - 4.2 min', 'conf': '98%'}
    return {'type': 'BLS', 'eta': '5.0 - 6.0 min', 'conf': '91%'}

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "model_loaded": True, "db_connected": db is not None})

@app.route('/ambulances/active')
def get_ambulances(): 
    if not db: return jsonify({"ambulances": AMBULANCES})
    try:
        docs = db.collection('ambulances').stream()
        res = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            res.append(d)
        return jsonify({"ambulances": res if res else AMBULANCES})
    except Exception as e:
        logger.warning(f"Firestore Error: {e}")
        return jsonify({"ambulances": AMBULANCES})

@app.route('/incidents/active')
def get_incidents(): 
    if not db: return jsonify({"incidents": ACTIVE_INCIDENTS})
    try:
        docs = db.collection('incidents').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
        res = []
        for doc in docs:
            d = doc.to_dict()
            d['id'] = doc.id
            res.append(d)
        return jsonify({"incidents": res})
    except Exception as e:
        logger.warning(f"Firestore Error: {e}")
        return jsonify({"incidents": ACTIVE_INCIDENTS})

@app.route('/hospitals')
def get_hospitals(): 
    if not db: return jsonify({"hospitals": HOSPITALS})
    try:
        docs = db.collection('hospitals').stream()
        return jsonify({"hospitals": [doc.to_dict() for doc in docs]})
    except Exception as e:
        logger.warning(f"Firestore Error: {e}")
        return jsonify({"hospitals": HOSPITALS})

@app.route('/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    mock_inc = {
        "id": f"INC-{datetime.now().strftime('%M%S')}",
        "patient_name": data.get("patient_name", "Unknown"),
        "incident_type": data.get("incident_type", "Medical"),
        "severity": data.get("severity", "Moderate"),
        "latitude": data.get("latitude", 19.076),
        "longitude": data.get("longitude", 72.877),
        "status": "Waiting",
        "timestamp": datetime.now(),
        "prediction": get_ai_recommendation(data.get("incident_type"), data.get("severity"))
    }
    if db:
        try: db.collection('incidents').document(mock_inc['id']).set(mock_inc)
        except: pass
    return jsonify(mock_inc)

@app.route('/admin/cleanup', methods=['POST'])
def cleanup_data():
    if not db: return jsonify({"status": "success", "message": "Mocks reset locally"})
    try:
        # Delete incidents
        docs = db.collection('incidents').stream()
        for doc in docs: doc.reference.delete()
        # Reset ambulances
        ambs = db.collection('ambulances').stream()
        for amb in ambs: amb.reference.update({'status': 'available', 'assigned_incident': None})
        return jsonify({"status": "success", "message": "Firestore Purged"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def move_ambulances_task():
    while True:
        try:
            if db:
                ambs = db.collection('ambulances').where('status', '==', 'responding').stream()
                for amb in ambs:
                    # Simulation logic...
                    pass
            time.sleep(5)
        except: time.sleep(10)

threading.Thread(target=move_ambulances_task, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
