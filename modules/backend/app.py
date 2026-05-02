import logging
from datetime import datetime
import threading
import time
import math
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import firestore
from firebase_config import get_firestore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = get_firestore()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})
logger.info("✅ Cloud-Sync enabled for Firestore")

# --- INITIAL SEEDING LOGIC ---
def seed_initial_data():
    if not db:
        return
    
    # Seed Ambulances if empty
    amb_ref = db.collection('ambulances')
    if len(amb_ref.get()) == 0:
        logger.info("💾 Seeding initial ambulance fleet to Firestore...")
        fleet = [
            {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.076, 'longitude': 72.877},
            {'id': 'BLS-001', 'driver_name': 'Amit Patel', 'status': 'available', 'type': 'BLS', 'latitude': 19.086, 'longitude': 72.887},
            {'id': 'BIKE-001', 'driver_name': 'Suresh Nair', 'status': 'available', 'type': 'Bike', 'latitude': 19.096, 'longitude': 72.897}
        ]
        for a in fleet:
            amb_ref.document(a['id']).set(a)

    # Seed Hospitals if empty
    hosp_ref = db.collection('hospitals')
    if len(hosp_ref.get()) == 0:
        logger.info("💾 Seeding hospital network to Firestore...")
        hospitals = [
            {'id': 'H001', 'name': 'Fortis Hospital Navi Mumbai', 'available_beds': 45, 'total_beds': 150, 'latitude': 19.071, 'longitude': 72.997},
            {'id': 'H002', 'name': 'Apollo Clinic Vashi', 'available_beds': 78, 'total_beds': 100, 'latitude': 19.061, 'longitude': 72.987}
        ]
        for h in hospitals:
            hosp_ref.document(h['id']).set(h)

seed_initial_data()



def get_precise_location(lat, lon):
    """Live Geocoder: Fetches exact building/street addresses from OpenStreetMap"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'NaviRaksha-Emergency-System/1.0'}
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            # Return exact building/road or suburb
            addr = data.get('address', {})
            parts = [addr.get(k) for k in ['building', 'road', 'suburb', 'city'] if addr.get(k)]
            return ", ".join(parts) if parts else data.get('display_name', 'Mumbai')
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
    
    # Simple Fallback if API is slow/down
    return "Palm Beach Rd, Navi Mumbai"

# --- MOCK DB ---
ACTIVE_INCIDENTS = [
    {
        'id': 'INC-001', 'patient_name': 'Ramesh Sharma', 'incident_type': 'Cardiac', 'severity': 'Critical', 
        'status': 'Waiting', 'latitude': 19.0760, 'longitude': 72.8777, 'time': '0:01',
        'location_address': get_precise_location(19.0760, 72.8777),
        'prediction': {"type": "ALS — Advanced Life Support", "eta": "3.5 - 4.2", "conf": "98%"}
    },
    {
        'id': 'INC-002', 'patient_name': 'Priya Verma', 'incident_type': 'Trauma', 'severity': 'High', 
        'status': 'Waiting', 'latitude': 19.0860, 'longitude': 72.8877, 'time': '0:01',
        'location_address': get_precise_location(19.0860, 72.8877),
        'prediction': {"type": "BLS — Basic Life Support", "eta": "4.8 - 5.5", "conf": "92%"}
    }
]

AMBULANCES = [
    {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.076, 'longitude': 72.877},
    {'id': 'BLS-001', 'driver_name': 'Amit Patel', 'status': 'available', 'type': 'available', 'latitude': 19.086, 'longitude': 72.887},
    {'id': 'BIKE-001', 'driver_name': 'Suresh Nair', 'status': 'available', 'type': 'Bike', 'latitude': 19.096, 'longitude': 72.897},
    {'id': 'ALS-002', 'driver_name': 'Priya Singh', 'status': 'on-scene', 'type': 'ALS', 'latitude': 19.056, 'longitude': 72.857},
    {'id': 'BLS-002', 'driver_name': 'Deepa Gupta', 'status': 'responding', 'type': 'BLS', 'latitude': 19.046, 'longitude': 72.847},
    {'id': 'MINI-001', 'driver_name': 'Vikram Rao', 'status': 'available', 'type': 'Mini', 'latitude': 19.036, 'longitude': 72.837}
]

HOSPITALS = [
    {'id': 'H001', 'name': 'Fortis Hospital Navi Mumbai', 'available_beds': 45, 'total_beds': 150},
    {'id': 'H002', 'name': 'Apollo Clinic Vashi', 'available_beds': 78, 'total_beds': 100}
]

def get_ai_recommendation(inc_type, severity):
    sev = severity.upper()
    if sev == 'CRITICAL' or inc_type.lower() in ['cardiac', 'stroke']:
        return {"type": "ALS — Advanced Life Support", "eta": "3.5 - 4.2", "conf": "98%"}
    return {"type": "BLS — Basic Life Support", "eta": "5.0 - 6.0", "conf": "91%"}

@app.route('/health')
def health(): return jsonify({"status": "ok"})

@app.route('/ambulances/active')
def get_ambulances(): 
    if not db:
        return jsonify({"ambulances": []})
    docs = db.collection('ambulances').stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        res.append(d)
    return jsonify({"ambulances": res})

@app.route('/incidents/active')
def get_incidents(): 
    if not db:
        return jsonify({"incidents": []})
    # Get last 10 incidents ordered by time
    docs = db.collection('incidents').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10).stream()
    res = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        res.append(d)
    return jsonify({"incidents": res})

@app.route('/hospitals')
def get_hospitals(): 
    if not db:
        return jsonify({"hospitals": []})
    docs = db.collection('hospitals').stream()
    return jsonify({"hospitals": [doc.to_dict() for doc in docs]})

@app.route('/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    patient_name = data.get('patient_name', 'Unknown')
    phone = data.get('phone', 'N/A')
    incident_type = data.get('incident_type', 'Medical')
    severity = data.get('severity', 'Moderate')
    patient_lat = data.get('latitude', 19.076)
    patient_lon = data.get('longitude', 72.877)
    
    mock_inc = {
        'id': f"INC-{datetime.now().strftime('%M%S')}",
        'patient_name': patient_name,
        'phone': phone,
        'incident_type': incident_type,
        'severity': severity,
        'status': 'Waiting',
        'latitude': patient_lat,
        'longitude': patient_lon,
        'location_address': get_precise_location(patient_lat, patient_lon),
        'time': datetime.now().strftime("%H:%M"),
        'timestamp': datetime.now(), # For sorting
        'prediction': get_ai_recommendation(incident_type, severity)
    }
    
    if db:
        db.collection('incidents').document(mock_inc['id']).set(mock_inc)
        logger.info(f"🚨 CLOUD SOS SAVED: {patient_name}")
    
    return jsonify(mock_inc)



def move_ambulances_task():
    """Background task to simulate live movement of dispatched ambulances."""
    while True:
        try:
            if not db: 
                time.sleep(5)
                continue
                
            # Find ambulances that are 'responding'
            ambs = db.collection('ambulances').where('status', '==', 'responding').stream()
            for amb in ambs:
                a_data = amb.to_dict()
                inc_id = a_data.get('assigned_incident')
                if not inc_id:
                    continue
                
                # Get the incident they are going to
                inc_ref = db.collection('incidents').document(inc_id)
                inc_doc = inc_ref.get()
                if not inc_doc.exists:
                    continue
                i_data = inc_doc.to_dict()
                
                # Calculate movement (simple step toward target)
                curr_lat, curr_lon = a_data['latitude'], a_data['longitude']
                dest_lat, dest_lon = i_data['latitude'], i_data['longitude']
                
                dist = math.sqrt((dest_lat - curr_lat)**2 + (dest_lon - curr_lon)**2)
                
                if dist < 0.001: # Arrived
                    db.collection('ambulances').document(amb.id).update({
                        'status': 'on-site',
                        'latitude': dest_lat,
                        'longitude': dest_lon
                    })
                    logger.info(f"🏁 Ambulance {amb.id} arrived at {inc_id}")
                else:
                    # Move 10% closer each tick
                    step = 0.1
                    new_lat = curr_lat + (dest_lat - curr_lat) * step
                    new_lon = curr_lon + (dest_lon - curr_lon) * step
                    db.collection('ambulances').document(amb.id).update({
                        'latitude': new_lat,
                        'longitude': new_lon
                    })
            
            time.sleep(3) # Move every 3 seconds
        except Exception as e:
            logger.error(f"Movement Engine Error: {e}")
            time.sleep(5)

# Start movement thread
threading.Thread(target=move_ambulances_task, daemon=True).start()

@app.route('/incidents/<inc_id>/status', methods=['PUT'])
def update_incident_status(inc_id):
    if not db:
        return jsonify({"error": "No DB"}), 500
    data = request.json
    status = data.get('status', 'Dispatched')
    
    doc_ref = db.collection('incidents').document(inc_id)
    if doc_ref.get().exists:
        # If dispatching, find an available ambulance
        if status == 'Dispatched':
            amb_query = db.collection('ambulances').where('status', '==', 'available').limit(1).stream()
            assigned_amb = None
            for a in amb_query:
                assigned_amb = a
            
            if assigned_amb:
                # Update Ambulance
                db.collection('ambulances').document(assigned_amb.id).update({
                    'status': 'responding',
                    'assigned_incident': inc_id
                })
                # Update Incident
                doc_ref.update({
                    'status': status,
                    'assigned_ambulance': assigned_amb.id
                })
                logger.info(f"✅ Dispatched {assigned_amb.id} to {inc_id}")
                return jsonify({"status": "dispatched", "amb_id": assigned_amb.id})
            else:
                return jsonify({"error": "No available ambulances"}), 400
        
        doc_ref.update({'status': status})
        return jsonify({"status": "updated"})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(port=8000, debug=True)
