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

def get_ai_recommendation(incident_type, severity, lat, lng):
    """
    Calculates dynamic ETA and unit recommendation based on 
    actual fleet proximity and vehicle type performance.
    """
    available_units = [a for a in STATE["ambulances"] if a['status'] == 'available']
    
    if not available_units:
        return {'type': 'ALS', 'eta': '12-15 min (Delay)', 'conf': '85%', 'note': 'High Demand'}

    # Find closest unit of any type
    closest = min(available_units, key=lambda a: math.sqrt((a['latitude']-lat)**2 + (a['longitude']-lng)**2))
    
    # Simple travel time calculation (Distance * 111km per deg / speed * 60 min)
    dx = closest['latitude'] - lat
    dy = closest['longitude'] - lng
    dist_km = math.sqrt(dx**2 + dy**2) * 111
    
    # Speed assumptions: Bike 55km/h, ALS/BLS 40km/h
    speed = 55 if closest['type'] == 'BIKE' else 40
    eta_min = (dist_km / speed) * 60
    
    # Add 2 min buffer for dispatch/traffic
    eta_start = round(eta_min + 1, 1)
    eta_end = round(eta_min + 3, 1)

    return {
        'type': closest['type'], 
        'eta': f"{eta_start} - {eta_end} min", 
        'conf': f"{92 + round(random.random(), 2)*6}%",
        'unit': closest['id']
    }

# --- BACKGROUND ENGINES ---
def cloud_sync_task():
    while True:
        if db:
            try:
                # Sync hospitals
                h_docs = db.collection('hospitals').stream()
                h_list = [{**d.to_dict(), 'id': d.id} for d in h_docs]
                if h_list: STATE["hospitals"] = h_list

                # Sync incidents
                inc_docs = db.collection('incidents').limit(20).stream()
                new_incs = [{**d.to_dict(), 'id': d.id} for d in inc_docs]
                if new_incs: STATE["incidents"] = new_incs
                STATE["last_cloud_sync"] = time.time()
            except: pass
        time.sleep(10)

def movement_loop():
    print("🚑 MOVEMENT LOOP STARTED - NAVIRAKSHA ENGINE ACTIVE")
    while True:
        for amb in STATE["ambulances"]:
            if amb['status'] == 'responding' and amb.get('assigned_incident'):
                target = next((i for i in STATE["incidents"] if i['id'] == amb['assigned_incident']), None)
                if target and target.get('status') == 'Dispatched':
                    dx = target['latitude'] - amb['latitude']
                    dy = target['longitude'] - amb['longitude']
                    dist = math.sqrt(dx**2 + dy**2)
                    
                    if dist < 0.0008: # Arrival threshold (approx 80m)
                        # ARRIVAL LOGIC
                        amb['status'] = 'available'
                        amb['assigned_incident'] = None
                        target['status'] = 'Resolved'
                        
                        logger.info(f"✅ Incident {target['id']} Resolved - Ambulance arrived.")
                        
                        if db:
                            def sync_resolve(t_id):
                                try: db.collection('incidents').document(t_id).update({'status': 'Resolved'})
                                except: pass
                            threading.Thread(target=sync_resolve, args=(target['id'],)).start()
                    else:
                        # Move toward target (5% per tick)
                        amb['latitude'] += dx * 0.06
                        amb['longitude'] += dy * 0.06
                        
                        if db:
                            try:
                                def sync_pos(a_id, lat, lng):
                                    try: db.collection('ambulances').document(a_id).update({'latitude': lat, 'longitude': lng})
                                    except: pass
                                threading.Thread(target=sync_pos, args=(amb['id'], amb['latitude'], amb['longitude'])).start()
                            except: pass
        time.sleep(2)

threading.Thread(target=cloud_sync_task, daemon=True).start()
threading.Thread(target=movement_loop, daemon=True).start()

# --- GEOGRAPHIC INTELLIGENCE ---
BRIDGES = [
    (19.0433, 72.9833), # Vashi Bridge
    (19.1411, 72.9855)  # Airoli Bridge
]

def get_route(s_lat, s_lng, e_lat, e_lng):
    """
    Returns a road-aware path that avoids water crossing by 
    routing through the nearest bridge if needed.
    """
    # Simple check: if both points are on the same side, direct route
    # If s_lng < 72.98 and e_lng > 72.98 (or vice versa), they are crossing water
    if (s_lng < 72.985 and e_lng < 72.985) or (s_lng > 72.985 and e_lng > 72.985):
        return [[s_lat, s_lng], [e_lat, e_lng]]
    
    # Find nearest bridge
    bridge = min(BRIDGES, key=lambda b: (abs(b[0]-s_lat) + abs(b[1]-s_lng)))
    return [
        [s_lat, s_lng],
        [bridge[0], bridge[1]], 
        [e_lat, e_lng]
    ]

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
        "prediction": get_ai_recommendation(data.get("incident_type", ""), data.get("severity", ""), lat, lng)
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
                        # Generate Intelligence Path (Bridge-aware)
                        route_path = get_route(amb['latitude'], amb['longitude'], inc['latitude'], inc['longitude'])
                        inc['path'] = route_path
                        break
    if db:
        def update():
            try:
                update_data = {'status': status}
                if route_path: update_data['path'] = route_path
                
                db.collection('incidents').document(inc_id).update(update_data)
                if assigned_amb_id:
                    db.collection('ambulances').document(assigned_amb_id).update({'status': 'responding', 'assigned_incident': inc_id})
            except: pass
        threading.Thread(target=update).start()
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
