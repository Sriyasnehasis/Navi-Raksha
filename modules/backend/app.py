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

# --- GEOGRAPHIC INTELLIGENCE ---
BRIDGES = [
    (19.0433, 72.9833), # Vashi Bridge
    (19.1411, 72.9855)  # Airoli Bridge
]

def get_neighborhood(lat, lng):
    if lat > 19.12: return "Airoli, Sector 5"
    if lat > 19.10: return "Ghansoli, Sector 3"
    if lat > 19.08: return "Kopar Khairane, Sector 12"
    if lat > 19.06: return "Vashi, Sector 17"
    if lat > 19.04: return "Nerul, Palm Beach Road"
    if lat > 19.02: return "Belapur, CBD Sector 11"
    return "Sanpada, Sector 5"

def get_ai_recommendation(lat, lng):
    available_units = [a for a in STATE["ambulances"] if a['status'] == 'available']
    if not available_units:
        return {'type': 'ALS', 'eta': '10-12 min', 'conf': '85%'}

    closest = min(available_units, key=lambda a: math.sqrt((a['latitude']-lat)**2 + (a['longitude']-lng)**2))
    dist_km = math.sqrt((closest['latitude']-lat)**2 + (closest['longitude']-lng)**2) * 111
    
    eta_min = round((dist_km / 40) * 60 + 1, 1)
    return {
        'type': closest['type'], 
        'eta': f"{eta_min} - {eta_min + 2} min", 
        'conf': f"{90 + round(math.sin(lat)*5, 1)}%"
    }

def get_route(s_lat, s_lng, e_lat, e_lng):
    # If same side of creek, direct line. If crossing creek, use bridge.
    if (s_lng < 72.985 and e_lng < 72.985) or (s_lng > 72.985 and e_lng > 72.985):
        return [[s_lat, s_lng], [e_lat, e_lng]]
    bridge = min(BRIDGES, key=lambda b: (abs(b[0]-s_lat) + abs(b[1]-s_lng)))
    return [[s_lat, s_lng], [bridge[0], bridge[1]], [e_lat, e_lng]]

# --- BACKGROUND ENGINES ---
def cloud_sync_task():
    while True:
        # CONSERVATIVE SYNC: Only fetch new incidents, never overwrite local memory
        if db:
            try:
                inc_docs = db.collection('incidents').limit(20).stream()
                cloud_ids = {i['id'] for i in STATE["incidents"]}
                for d in inc_docs:
                    if d.id not in cloud_ids:
                        STATE["incidents"].append({**d.to_dict(), 'id': d.id})
                STATE["last_cloud_sync"] = time.time()
            except: pass
        time.sleep(30)

def movement_loop():
    print("🚑 MOVEMENT LOOP ACTIVE")
    while True:
        for amb in STATE["ambulances"]:
            if amb['status'] == 'responding' and amb.get('assigned_incident'):
                target = next((i for i in STATE["incidents"] if i['id'] == amb['assigned_incident']), None)
                if target and target.get('status') == 'Dispatched':
                    dx = target['latitude'] - amb['latitude']
                    dy = target['longitude'] - amb['longitude']
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.0008:
                        amb['status'] = 'available'
                        amb['assigned_incident'] = None
                        target['status'] = 'Resolved'
                        if db: 
                            try: db.collection('incidents').document(target['id']).update({'status': 'Resolved'})
                            except: pass
                    else:
                        amb['latitude'] += dx * 0.07
                        amb['longitude'] += dy * 0.07
                        if db:
                            try: db.collection('ambulances').document(amb['id']).update({'latitude': amb['latitude'], 'longitude': amb['longitude']})
                            except: pass
        time.sleep(2)

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
        "prediction": get_ai_recommendation(lat, lng)
    }
    STATE["incidents"].insert(0, new_inc)
    if db:
        try: db.collection('incidents').document(new_inc['id']).set(new_inc)
        except: pass
    return jsonify(new_inc)

@app.route('/incidents/<inc_id>/status', methods=['PUT'])
def update_status(inc_id):
    status = request.json.get('status', 'Dispatched')
    assigned_amb_id = None
    route_path = None
    
    for inc in STATE["incidents"]:
        if inc['id'] == inc_id:
            inc['status'] = status
            if status == 'Dispatched':
                for amb in STATE["ambulances"]:
                    if amb['status'] == 'available':
                        amb['status'] = 'responding'
                        amb['assigned_incident'] = inc_id
                        assigned_amb_id = amb['id']
                        route_path = get_route(amb['latitude'], amb['longitude'], inc['latitude'], inc['longitude'])
                        inc['path'] = route_path
                        break
    if db:
        try:
            db.collection('incidents').document(inc_id).update({'status': status, 'path': route_path})
            if assigned_amb_id:
                db.collection('ambulances').document(assigned_amb_id).update({'status': 'responding', 'assigned_incident': inc_id})
        except: pass
    return jsonify({"status": "updated", "path": route_path})

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
