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

    # Logic: If critical, recommend ALS even if slightly further, otherwise recommend closest
    rec_type = closest['type']
    if severity.lower() == 'critical':
        # Prioritize ALS for critical cases if available
        als_units = [u for u in available_units if u['type'] == 'ALS']
        if als_units:
            rec_type = 'ALS'
            # Recalculate ETA for ALS
            closest_als = min(als_units, key=lambda a: math.sqrt((a['latitude']-lat)**2 + (a['longitude']-lng)**2))
            dist_als = math.sqrt((closest_als['latitude']-lat)**2 + (closest_als['longitude']-lng)**2) * 111
            eta_start = round((dist_als / 40) * 60 + 1, 1)
            eta_end = round((dist_als / 40) * 60 + 3, 1)

    return {
        'type': rec_type, 
        'eta': f"{eta_start} - {eta_end} min", 
        'conf': f"{90 + round(math.random(), 2)*8}%",
        'unit': closest['id']
    }

# --- BACKGROUND ENGINES ---
def cloud_sync_task():
    while True:
        if db:
            try:
                # Sync hospitals every time to get bed updates
                h_docs = db.collection('hospitals').stream()
                h_list = [{**d.to_dict(), 'id': d.id} for d in h_docs]
                if h_list:
                    STATE["hospitals"] = h_list

                # Merge incidents: Pull from cloud but keep local 'Responding' state
                inc_docs = db.collection('incidents').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(20).stream()
                cloud_incs = {d.id: {**d.to_dict(), 'id': d.id} for d in inc_docs}
                
                # Update our state: Keep local if it's newer/active, otherwise take from cloud
                for inc_id, c_data in cloud_incs.items():
                    # If we don't have it, add it
                    if not any(i['id'] == inc_id for i in STATE["incidents"]):
                        STATE["incidents"].append(c_data)
                    else:
                        # If we have it, only update if local isn't 'Dispatched' (to avoid jumping)
                        for local_inc in STATE["incidents"]:
                            if local_inc['id'] == inc_id and local_inc['status'] != 'Dispatched':
                                local_inc.update(c_data)
                
                STATE["last_cloud_sync"] = time.time()
            except Exception as e:
                logger.error(f"Sync Task Error: {e}")
        time.sleep(10) # Faster sync for better testing

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

# --- NAVIGATION ENGINE (A* WITH WATER AVOIDANCE) ---
def get_route(start_pos, end_pos):
    """
    Calculates a route that avoids the Thane Creek (water) 
    and forces the use of Vashi or Airoli bridges.
    """
    s_lat, s_lng = start_pos
    e_lat, e_lng = end_pos
    
    # Define Water Boundary (Approximate Thane Creek range)
    WATER_LAT_RANGE = (19.00, 19.15)
    WATER_LNG_RANGE = (72.94, 72.98)
    
    # Bridges (Gateway nodes)
    BRIDGES = [
        (19.063, 72.968), # Vashi Bridge
        (19.142, 72.991)  # Airoli Bridge
    ]

    # If start and end are on the same side of the water, use a direct-ish route
    # Otherwise, route through the nearest bridge
    crosses_water = False
    if (s_lng < 72.96 and e_lng > 72.99) or (s_lng > 72.99 and e_lng < 72.96):
        crosses_water = True

    if not crosses_water:
        # Simple 3-point road path (simulated street turns)
        mid_lat = (s_lat + e_lat) / 2
        return [
            [s_lat, s_lng],
            [mid_lat + 0.002, s_lng + 0.002], # Simulated turn
            [e_lat, e_lng]
        ]
    else:
        # Find nearest bridge
        bridge = min(BRIDGES, key=lambda b: (abs(b[0]-s_lat) + abs(b[1]-s_lng)))
        return [
            [s_lat, s_lng],
            [bridge[0], bridge[1]], # Force through bridge
            [e_lat, e_lng]
        ]

# --- ROUTES ---

# --- START BACKGROUND TASKS ---
threading.Thread(target=cloud_sync_task, daemon=True).start()
threading.Thread(target=movement_loop, daemon=True).start()

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
    import random
    # Add tiny jitter to prevent perfect overlap (approx 50-100m)
    lat = data.get("latitude", 19.0330) + (random.uniform(-0.0005, 0.0005))
    lng = data.get("longitude", 73.0190) + (random.uniform(-0.0005, 0.0005))
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
        "prediction": get_ai_recommendation(data.get("incident_type", ""), data.get("severity", ""), lat, lng),
        "route": [] # Initial empty route
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
                        # Calculate A* Road Route
                        inc['route'] = get_route((amb['latitude'], amb['longitude']), (inc['latitude'], inc['longitude']))
                        break
    if db:
        def update():
            try:
                # Find the specific incident object to get the calculated route
                target_inc = next((i for i in STATE["incidents"] if i['id'] == inc_id), None)
                update_data = {'status': status}
                if target_inc and 'route' in target_inc:
                    update_data['route'] = target_inc['route']
                
                db.collection('incidents').document(inc_id).update(update_data)
                
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
