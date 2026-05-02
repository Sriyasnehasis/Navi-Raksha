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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
db = get_firestore()

AMBULANCES = [
    {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.076, 'longitude': 72.877},
    {'id': 'ALS-002', 'driver_name': 'Priya Singh', 'status': 'available', 'type': 'ALS', 'latitude': 19.086, 'longitude': 72.887},
    {'id': 'BIKE-001', 'driver_name': 'Suresh Nair', 'status': 'available', 'type': 'BIKE', 'latitude': 19.066, 'longitude': 72.867}
]
ACTIVE_INCIDENTS = []
HOSPITALS = [
    {'id': 'H001', 'name': 'Fortis Hospital Navi Mumbai', 'available_beds': 45, 'total_beds': 150, 'latitude': 19.071, 'longitude': 72.997},
    {'id': 'H002', 'name': 'Apollo Clinic Vashi', 'available_beds': 78, 'total_beds': 100, 'latitude': 19.061, 'longitude': 72.987}
]

def get_ai_recommendation(incident_type, severity):
    if severity.lower() == 'critical': return {'type': 'ALS', 'eta': '3.5 - 4.2 min', 'conf': '98%'}
    return {'type': 'BLS', 'eta': '5.0 - 6.0 min', 'conf': '91%'}

@app.route('/ambulances/active')
def get_ambulances(): 
    try:
        if db:
            docs = db.collection('ambulances').stream()
            res = [ {**doc.to_dict(), 'id': doc.id} for doc in docs ]
            if res: return jsonify({"ambulances": res})
    except: pass
    return jsonify({"ambulances": AMBULANCES})

@app.route('/incidents/active')
def get_incidents(): 
    try:
        if db:
            docs = db.collection('incidents').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
            return jsonify({"incidents": [{**doc.to_dict(), 'id': doc.id} for doc in docs]})
    except: pass
    return jsonify({"incidents": ACTIVE_INCIDENTS})

@app.route('/hospitals')
def get_hospitals(): 
    try:
        if db:
            docs = db.collection('hospitals').stream()
            return jsonify({"hospitals": [doc.to_dict() for doc in docs]})
    except: pass
    return jsonify({"hospitals": HOSPITALS})

@app.route('/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    mock_inc = {
        "id": f"INC-{datetime.now().strftime('%M%S')}",
        "patient_name": data.get("patient_name", "Unknown"),
        "phone": data.get("phone", ""),
        "incident_type": data.get("incident_type", "Medical"),
        "severity": data.get("severity", "Moderate"),
        "latitude": data.get("latitude", 19.076),
        "longitude": data.get("longitude", 72.877),
        "status": "Waiting",
        "timestamp": datetime.now(),
        "prediction": get_ai_recommendation(data.get("incident_type", ""), data.get("severity", ""))
    }
    ACTIVE_INCIDENTS.insert(0, mock_inc)
    if db:
        try: db.collection('incidents').document(mock_inc['id']).set(mock_inc)
        except: pass
    return jsonify(mock_inc)

@app.route('/incidents/<inc_id>/status', methods=['PUT'])
def update_status(inc_id):
    status = request.json.get('status', 'Dispatched')
    # Local Update
    for inc in ACTIVE_INCIDENTS:
        if inc['id'] == inc_id:
            inc['status'] = status
            if status == 'Dispatched':
                for amb in AMBULANCES:
                    if amb['status'] == 'available':
                        amb['status'] = 'responding'
                        amb['assigned_incident'] = inc_id
                        break
    # Cloud Update (Async/Try)
    if db:
        try: db.collection('incidents').document(inc_id).update({'status': status})
        except: pass
    return jsonify({"status": "updated"})

@app.route('/admin/cleanup', methods=['POST'])
def cleanup():
    global ACTIVE_INCIDENTS
    ACTIVE_INCIDENTS = []
    for amb in AMBULANCES: amb['status'] = 'available'; amb['assigned_incident'] = None
    if db:
        try:
            for doc in db.collection('incidents').stream(): doc.reference.delete()
            for amb in db.collection('ambulances').stream(): amb.reference.update({'status': 'available', 'assigned_incident': None})
        except: pass
    return jsonify({"status": "success"})

def movement_loop():
    while True:
        # Local simulation
        for amb in AMBULANCES:
            if amb['status'] == 'responding' and amb.get('assigned_incident'):
                target = next((i for i in ACTIVE_INCIDENTS if i['id'] == amb['assigned_incident']), None)
                if target:
                    dx = target['latitude'] - amb['latitude']
                    dy = target['longitude'] - amb['longitude']
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < 0.001: amb['status'] = 'on-site'
                    else:
                        amb['latitude'] += dx * 0.2
                        amb['longitude'] += dy * 0.2
        # Cloud simulation (try-except isolated)
        if db:
            try:
                # Cloud movement logic could go here, but local is priority for this demo
                pass
            except: pass
        time.sleep(3)

threading.Thread(target=movement_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
