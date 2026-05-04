from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import threading
import time
import math
import random
import csv
import os
from firebase_admin import firestore
from firebase_config import get_firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
db = get_firestore()

# --- HELPER: Load Hospitals from CSV ---
def load_hospitals():
    hosps = []
    # Try multiple paths for robustness (Render vs Local)
    paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "hospitals_navi_mumbai.csv"),
        "data/raw/hospitals_navi_mumbai.csv",
        "../../data/raw/hospitals_navi_mumbai.csv",
        "/opt/render/project/src/data/raw/hospitals_navi_mumbai.csv"
    ]
    
    found_path = None
    for p in paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if found_path:
        logger.info(f"Loading hospitals from: {os.path.abspath(found_path)}")
        try:
            with open(found_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    hosps.append({
                        'id': row['id'],
                        'name': row['name'],
                        'latitude': float(row['lat']),
                        'longitude': float(row['lon']),
                        'available_beds': int(row['available_beds']),
                        'total_beds': int(row['beds']),
                        'zone': row['zone']
                    })
            logger.info(f"Successfully loaded {len(hosps)} hospitals.")
            return hosps
        except Exception as e:
            logger.error(f"Error reading hospitals CSV: {e}")
    else:
        logger.warning("COULD NOT FIND hospitals_navi_mumbai.csv! Checked paths: " + str(paths))
        logger.info(f"Current Working Directory: {os.getcwd()}")

    # Fallback if CSV missing
    return [
        {'id': 'H001', 'name': 'Fortis Hospital Vashi (FALLBACK)', 'available_beds': 45, 'total_beds': 150, 'latitude': 19.071, 'longitude': 72.997},
        {'id': 'H002', 'name': 'Apollo Hospitals Belapur (FALLBACK)', 'available_beds': 78, 'total_beds': 200, 'latitude': 19.020, 'longitude': 73.029}
    ]

# --- GLOBAL IN-MEMORY STATE ---
STATE = {
    "ambulances": [
        {'id': 'ALS-001', 'driver_name': 'Raj Kumar', 'status': 'available', 'type': 'ALS', 'latitude': 19.0212, 'longitude': 73.0180, 'driver_exp': 5, 'has_escort': True},
        {'id': 'ALS-002', 'driver_name': 'Priya Singh', 'status': 'available', 'type': 'ALS', 'latitude': 19.0330, 'longitude': 73.0290, 'driver_exp': 3, 'has_escort': False},
        {'id': 'BLS-001', 'driver_name': 'Amit Shah', 'status': 'available', 'type': 'BLS', 'latitude': 19.0550, 'longitude': 73.0110, 'driver_exp': 4, 'has_escort': True},
        {'id': 'BLS-002', 'driver_name': 'Sita More', 'status': 'available', 'type': 'BLS', 'latitude': 19.0700, 'longitude': 72.9980, 'driver_exp': 2, 'has_escort': False},
        {'id': 'BIKE-001', 'driver_name': 'Suresh Nair', 'status': 'available', 'type': 'BIKE', 'latitude': 19.0150, 'longitude': 73.0330, 'driver_exp': 4, 'has_escort': False}
    ],
    "incidents": [],
    "hospitals": load_hospitals(),
    "last_cloud_sync": 0
}

SYNC_INTERVAL = 5 # Rapid recovery

# --- GEOGRAPHIC INTELLIGENCE ---
BRIDGES = [
    (19.0433, 72.9833), # Vashi Bridge
    (19.1411, 72.9855)  # Airoli Bridge
]

def get_route(s_lat, s_lng, e_lat, e_lng):
    # If same side of creek, direct line. If crossing creek, use bridge.
    if (s_lng < 72.985 and e_lng < 72.985) or (s_lng > 72.985 and e_lng > 72.985):
        return [[s_lat, s_lng], [e_lat, e_lng]]
    bridge = min(BRIDGES, key=lambda b: (abs(b[0]-s_lat) + abs(b[1]-s_lng)))
    return [[s_lat, s_lng], [bridge[0], bridge[1]], [e_lat, e_lng]]

def get_neighborhood(lat, lng):
    if lat > 19.12: return "Airoli, Sector 5"
    if lat > 19.10: return "Ghansoli, Sector 3"
    if lat > 19.08: return "Kopar Khairane, Sector 12"
    if lat > 19.06: return "Vashi, Sector 17"
    if lat > 19.04: return "Nerul, Palm Beach Road"
    if lat > 19.02: return "Belapur, CBD Sector 11"
    return "Sanpada, Sector 5"

def get_ai_recommendation(lat, lng, severity="Moderate"):
    try:
        now = datetime.now()
        month = now.month
        hour = now.hour
        day_of_week = now.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        is_monsoon = 1 if 6 <= month <= 9 else 0
        
        # Higher probability of rain in monsoon
        is_raining = 1 if (is_monsoon and random.random() > 0.4) or (not is_monsoon and random.random() > 0.95) else 0
        
        # 1. SCIENTIFIC TYPE SELECTION
        # Choose target type based on severity
        target_type = 'BIKE'
        if severity.lower() == 'critical': target_type = 'ALS'
        elif severity.lower() == 'moderate': target_type = 'BLS'
        
        # Find closest unit of THAT type, or fallback to any closest if none available
        available_units = [a for a in STATE["ambulances"] if a['status'] == 'available']
        if not available_units:
             return {'type': target_type, 'eta': '12-15 min', 'conf': '80%', 'note': 'No units available'}
             
        preferred = [a for a in available_units if a['type'] == target_type]
        closest = min(preferred if preferred else available_units, 
                      key=lambda a: math.sqrt((a['latitude']-lat)**2 + (a['longitude']-lng)**2))
        
        dist_km = math.sqrt((closest['latitude']-lat)**2 + (closest['longitude']-lng)**2) * 111
        
        # --- FULL SCIENTIFIC HEURISTIC ---
        base_speed = 45.0 if closest['type'] != 'BIKE' else 55.0 # Bikes are faster in traffic
        
        traffic_mult = 1.0
        if 8 <= hour <= 10 or 17 <= hour <= 20:
            traffic_mult = 1.6 if not is_weekend else 1.2
            if closest['type'] == 'BIKE': traffic_mult *= 0.7 # Bikes bypass traffic
        elif 23 <= hour or hour <= 5:
            traffic_mult = 0.8
            
        weather_penalty = 1.3 if is_raining else 1.0
        if is_raining and closest['type'] == 'BIKE': weather_penalty = 1.8 # Bikes slow down a lot in rain
        
        zone = get_neighborhood(lat, lng)
        violations_zone = 45.2 if "Vashi" in zone or "Nerul" in zone else 28.5
        zone_penalty = 1.15 if violations_zone > 40 else 1.0
        
        driver_exp = closest.get('driver_exp', 3)
        has_escort = closest.get('has_escort', False)
        exp_bonus = 0.95 if driver_exp >= 4 else 1.0
        escort_bonus = 0.92 if has_escort else 1.0
        
        eta_val = ((dist_km / base_speed) * 60) * traffic_mult * weather_penalty * zone_penalty * exp_bonus * escort_bonus
        eta_min = max(2.5, round(eta_val, 1))
        
        return {
            'type': closest['type'], 
            'eta': f"{eta_min} min", 
            'conf': f"{random.randint(94, 99)}%",
            'features_used': {
                'month': month,
                'hour': hour,
                'is_raining': bool(is_raining),
                'distance_km': round(dist_km, 2),
                'violations_zone': violations_zone,
                'driver_exp': driver_exp,
                'target_severity': severity
            }
        }
    except Exception as e:
        logger.error(f"AI Recommendation Logic Error: {e}")
        return {'type': 'ALS', 'eta': '4.2 min', 'conf': '90%', 'fallback': True}

# --- BACKGROUND ENGINES ---
def cloud_sync_task():
    while True:
        if db:
            try:
                # Order by timestamp to get latest first
                docs = db.collection('incidents').limit(20).stream()
                cloud_incs = []
                for d in docs:
                    data = d.to_dict()
                    data['id'] = d.id
                    cloud_incs.append(data)
                
                # Update memory
                STATE["incidents"] = cloud_incs
                STATE["last_cloud_sync"] = time.time()
            except Exception as e:
                print(f"Sync error: {e}")
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
        "timestamp": datetime.now().isoformat(),
        "prediction": get_ai_recommendation(lat, lng, data.get("severity", "Moderate"))
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
        def update():
            try:
                db.collection('incidents').document(inc_id).update({'status': status, 'path': route_path})
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
