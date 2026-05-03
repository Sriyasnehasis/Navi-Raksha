from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
import time
import math
from firebase_admin import firestore
from firebase_config import get_firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
db = get_firestore()

# --- GLOBAL IN-MEMORY STATE ---
STATE = {
    "ambulances": [
        {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.0212, 'longitude': 73.0180},
        {'id': 'ALS-002', 'driver_name': 'Priya Singh', 'status': 'available', 'type': 'ALS', 'latitude': 19.0330, 'longitude': 73.0290},
        {'id': 'BIKE-001', 'driver_name': 'Suresh Nair', 'status': 'available', 'type': 'BIKE', 'latitude': 19.0150, 'longitude': 73.0330}
    ],
    "incidents": [],
    "hospitals": [
        {'id': 'H001', 'name': 'Fortis Hospital Vashi', 'available_beds': 45, 'total_beds': 150, 'latitude': 19.071, 'longitude': 72.997},
        {'id': 'H002', 'name': 'Apollo Clinic Vashi', 'available_beds': 78, 'total_beds': 100, 'latitude': 19.061, 'longitude': 72.987},
        {'id': 'H003', 'name': 'MGM Hospital Vashi', 'available_beds': 56, 'total_beds': 200, 'latitude': 19.074, 'longitude': 73.003},
        {'id': 'H004', 'name': 'Reliance Hospital KK', 'available_beds': 112, 'total_beds': 250, 'latitude': 19.098, 'longitude': 73.012},
        {'id': 'H005', 'name': 'Terna Hospital Nerul', 'available_beds': 34, 'total_beds': 120, 'latitude': 19.034, 'longitude': 73.021}
    ],
    "last_cloud_sync": 0
}

SYNC_INTERVAL = 60 

def get_neighborhood(lat, lng):
    if lat > 19.10: return "Airoli, Sector 5"
    if lat > 19.08: return "Kopar Khairane, Sector 2"
    if lat > 19.06: return "Vashi, Sector 17"
    if lat > 19.04: return "Nerul, Palm Beach Road"
    return "Belapur, CBD Sector 11"

def get_ai_recommendation(incident_type, severity):
    if severity.lower() == 'critical': return {'type': 'ALS', 'eta': '3.5 - 4.2 min', 'conf': '98%'}
    return {'type': 'BLS', 'eta': '5.0 - 6.0 min', 'conf': '91%'}

# --- BACKGROUND ENGINES ---
def cloud_sync_task():
    while True:
        if db:
            try:
                # Only sync incidents/hospitals to avoid overwriting live local movement
                inc_docs = db.collection('incidents').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
                new_incs = [{**d.to_dict(), 'id': d.id} for d in inc_docs]
                STATE["incidents"] = new_incs
                STATE["last_cloud_sync"] = time.time()
            except: pass
        time.sleep(SYNC_INTERVAL)

def movement_loop():
    print("🚑 MOVEMENT LOOP STARTED - NAVIRAKSHA ENGINE ACTIVE")
    while True:
        for amb in STATE["ambulances"]:
            if amb['status'] == 'responding' and amb.get('assigned_incident'):
                target = next((i for i in STATE["incidents"] if i['id'] == amb['assigned_incident']), None)
                # STRICT CHECK: Only move if the target incident is actually DISPATCHED
                if target and target.get('status') == 'Dispatched':
                    dx = target['latitude'] - amb['latitude']
                    dy = target['longitude'] - amb['longitude']
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.0005: 
                        # ARRIVAL LOGIC
                        amb['status'] = 'available' # Make it ready for next call
                        amb['assigned_incident'] = None
                        
                        target['status'] = 'Resolved'
                        logger.info(f"Incident {target['id']} Resolved - Ambulance arrived at scene.")
                        
                        # Background cloud sync for resolution
                        if db:
                            def sync_resolve(t_id):
                                try: db.collection('incidents').document(t_id).update({'status': 'Resolved'})
                                except: pass
                            threading.Thread(target=sync_resolve, args=(target['id'],)).start()
                    else:
                        # Visual Glide: Move 5% per second for better responsiveness
                        amb['latitude'] += dx * 0.05
                        amb['longitude'] += dy * 0.05
                        
                        # SYNC TO CLOUD: Push new position so frontend map moves
                        if db:
                            try:
                                # We use a background thread for firestore update to keep movement loop fast
                                def sync_pos(a_id, lat, lng):
                                    try: db.collection('ambulances').document(a_id).update({'latitude': lat, 'longitude': lng})
                                    except: pass
                                threading.Thread(target=sync_pos, args=(amb['id'], amb['latitude'], amb['longitude'])).start()
                            except: pass
        time.sleep(2) # Balanced interval for Render performance

threading.Thread(target=cloud_sync_task, daemon=True).start()
threading.Thread(target=movement_loop, daemon=True).start()

# --- ROUTES ---

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/ambulances/active')
def get_ambulances(): 
    return jsonify({"ambulances": STATE["ambulances"]})

@app.route('/incidents/active')
def get_incidents(): 
    return jsonify({"incidents": STATE["incidents"]})

@app.route('/hospitals')
def get_hospitals(): 
    return jsonify({"hospitals": STATE["hospitals"]})

@app.route('/dispatch', methods=['POST'])
def dispatch():
    data = request.json
    lat = data.get("latitude", 19.0330)
    lng = data.get("longitude", 73.0190)
    new_inc = {
        "id": f"INC-{datetime.now().strftime('%M%S')}",
        "patient_name": data.get("patient_name", "Unknown"),
        "phone": data.get("phone", ""),
        "incident_type": data.get("incident_type", "Medical"),
        "severity": data.get("severity", "Moderate"),
        "latitude": lat,
        "longitude": lng,
        "location_address": get_neighborhood(lat, lng),
        "status": "Waiting",
        "timestamp": datetime.now(),
        "prediction": get_ai_recommendation(data.get("incident_type", ""), data.get("severity", ""))
    }
    STATE["incidents"].insert(0, new_inc)
    if db:
        def save():
            try: db.collection('incidents').document(new_inc['id']).set(new_inc)
            except: pass
        threading.Thread(target=save).start()
    return jsonify(new_inc)

@app.route('/incidents/<inc_id>/status', methods=['PUT'])
def update_status(inc_id):
    status = request.json.get('status', 'Dispatched')
    assigned_amb_id = None
    for inc in STATE["incidents"]:
        if inc['id'] == inc_id:
            inc['status'] = status
            if status == 'Dispatched':
                for amb in STATE["ambulances"]:
                    if amb['status'] == 'available':
                        amb['status'] = 'responding'
                        amb['assigned_incident'] = inc_id
                        assigned_amb_id = amb['id']
                        break
    if db:
        def update():
            try:
                db.collection('incidents').document(inc_id).update({'status': status})
                if assigned_amb_id:
                    db.collection('ambulances').document(assigned_amb_id).update({'status': 'responding', 'assigned_incident': inc_id})
            except: pass
        threading.Thread(target=update).start()
    return jsonify({"status": "updated"})

@app.route('/admin/cleanup', methods=['POST'])
def cleanup():
    STATE["incidents"] = []
    for amb in STATE["ambulances"]: 
        amb['status'] = 'available'
        amb['assigned_incident'] = None
    if db:
        def purge():
            try:
                for doc in db.collection('incidents').stream(): doc.reference.delete()
            except: pass
        threading.Thread(target=purge).start()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
