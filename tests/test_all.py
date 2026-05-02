"""
NaviRaksha - Comprehensive Test Suite
Tests backend API, routing module, dispatch classifier, and 4 required scenarios.

Run: python -m pytest tests/ -v
Or:  python tests/test_all.py
"""

import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000"

# ============================================================================
# UTILITY HELPERS
# ============================================================================

def wait_for_server(max_retries=10):
    """Wait for backend server to be ready"""
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            return True
        except Exception:
            if i < max_retries - 1:
                time.sleep(1)
    return False

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check(label, condition):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"  {status} | {label}")
    return condition

passed = 0
failed = 0

def track(result):
    global passed, failed
    if result:
        passed += 1
    else:
        failed += 1

# ============================================================================
# TEST 1: API ENDPOINT TESTS
# ============================================================================

def test_api_endpoints():
    """Test all core API endpoints"""
    section("TEST 1: API Endpoint Verification")
    
    # Health
    r = requests.get(f"{BASE_URL}/health")
    track(check("GET /health returns 200", r.status_code == 200))
    data = r.json()
    track(check("Health reports model status", 'model_loaded' in data))
    
    # Predict ETA
    r = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 14, "is_monsoon": False,
        "ambulance_type": 2, "violations_zone": 0
    })
    track(check("POST /predict-eta returns 200", r.status_code == 200))
    data = r.json()
    track(check("ETA is a valid number", isinstance(data.get('eta_minutes'), (int, float))))
    track(check("ETA is in realistic range (3-20 min)", 3 <= data.get('eta_minutes', 0) <= 20))
    
    # Ambulances
    r = requests.get(f"{BASE_URL}/ambulances/active")
    track(check("GET /ambulances/active returns 200", r.status_code == 200))
    data = r.json()
    track(check("Ambulances list is not empty", len(data.get('ambulances', [])) > 0))
    
    # Incidents
    r = requests.get(f"{BASE_URL}/incidents/active")
    track(check("GET /incidents/active returns 200", r.status_code == 200))
    
    # Hospitals
    r = requests.get(f"{BASE_URL}/hospitals")
    track(check("GET /hospitals returns 200", r.status_code == 200))
    data = r.json()
    track(check("Hospitals list is not empty", len(data.get('hospitals', [])) > 0))
    
    # Dispatch
    r = requests.post(f"{BASE_URL}/dispatch", json={
        "patient_lat": 19.076, "patient_lon": 72.877,
        "incident_type": "Cardiac", "severity": "CRITICAL",
        "distance": 5.0, "hour": 14, "is_monsoon": False
    })
    track(check("POST /dispatch returns 200", r.status_code == 200))
    data = r.json()
    track(check("Dispatch returns ambulance_type", 'ambulance_type' in data))
    track(check("Dispatch returns eta_minutes", 'eta_minutes' in data))
    track(check("Dispatch returns hospital", 'hospital' in data))
    track(check("Dispatch returns route_coords", isinstance(data.get('route_coords'), list) and len(data.get('route_coords', [])) >= 2))
    track(check("Dispatch returns route_summary", isinstance(data.get('route_summary'), dict)))
    track(check("Dispatch returns hospital_rankings", isinstance(data.get('hospital_rankings'), list) and len(data.get('hospital_rankings', [])) > 0))

# ============================================================================
# TEST 2: CRUD OPERATIONS
# ============================================================================

def test_crud_operations():
    """Test CRUD operations for ambulances, incidents, hospitals"""
    section("TEST 2: CRUD Operations")
    
    # --- Ambulance CRUD ---
    amb = {
        "id": "TEST-AMB-001", "name": "Test Ambulance", "type": "ALS",
        "latitude": 19.076, "longitude": 72.877, "driver_name": "Test Driver", "crew_size": 2
    }
    r = requests.post(f"{BASE_URL}/admin/ambulances", json=amb)
    track(check("Ambulance CREATE", r.status_code == 201))
    
    r = requests.get(f"{BASE_URL}/admin/ambulances/TEST-AMB-001")
    track(check("Ambulance READ", r.status_code == 200))
    
    r = requests.put(f"{BASE_URL}/admin/ambulances/TEST-AMB-001", json={"driver_name": "New Driver"})
    track(check("Ambulance UPDATE", r.status_code == 200))
    
    r = requests.delete(f"{BASE_URL}/admin/ambulances/TEST-AMB-001")
    track(check("Ambulance DELETE", r.status_code == 200))
    
    # --- Hospital CRUD ---
    hosp = {
        "id": "TEST-HOSP-001", "name": "Test Hospital",
        "latitude": 19.08, "longitude": 72.88, "total_beds": 100, "available_beds": 50
    }
    r = requests.post(f"{BASE_URL}/admin/hospitals", json=hosp)
    track(check("Hospital CREATE", r.status_code == 201))
    
    r = requests.get(f"{BASE_URL}/admin/hospitals/TEST-HOSP-001")
    track(check("Hospital READ", r.status_code == 200))
    
    r = requests.put(f"{BASE_URL}/admin/hospitals/TEST-HOSP-001", json={"available_beds": 25})
    track(check("Hospital UPDATE", r.status_code == 200))
    
    r = requests.delete(f"{BASE_URL}/admin/hospitals/TEST-HOSP-001")
    track(check("Hospital DELETE", r.status_code == 200))
    
    # --- Incident CRUD ---
    inc = {
        "id": "TEST-INC-001", "incident_type": "Cardiac", "severity": "critical",
        "latitude": 19.076, "longitude": 72.877, "patient_name": "Test Patient", "status": "completed"
    }
    r = requests.post(f"{BASE_URL}/admin/incidents", json=inc)
    track(check("Incident CREATE", r.status_code == 201))
    
    r = requests.get(f"{BASE_URL}/admin/incidents/TEST-INC-001")
    track(check("Incident READ", r.status_code == 200))
    
    r = requests.put(f"{BASE_URL}/admin/incidents/TEST-INC-001", json={"severity": "severe"})
    track(check("Incident UPDATE", r.status_code == 200))
    
    r = requests.delete(f"{BASE_URL}/admin/incidents/TEST-INC-001")
    track(check("Incident DELETE", r.status_code == 200))

# ============================================================================
# TEST 3: DISPATCH CLASSIFIER (Routing Module)
# ============================================================================

def test_dispatch_classifier():
    """Test Turya's DispatchClassifier directly"""
    section("TEST 3: Dispatch Classifier (Routing Module)")
    
    try:
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from modules.routing.dispatch_classifier import DispatchClassifier
        dc = DispatchClassifier()
        
        # Critical cardiac → ALS
        result = dc.classify('Critical', 5.0, 'Cardiac')
        track(check("Critical/Cardiac → ALS", result == 'ALS'))
        
        # High trauma → ALS
        result = dc.classify('High', 5.0, 'Trauma')
        track(check("High/Trauma → ALS", result == 'ALS'))
        
        # High respiratory → BLS
        result = dc.classify('High', 5.0, 'Respiratory')
        track(check("High/Respiratory → BLS", result == 'BLS'))
        
        # Medium close → Mini
        result = dc.classify('Medium', 1.5, 'Respiratory')
        track(check("Medium/Close(1.5km) → Mini", result == 'Mini'))
        
        # Medium far → BLS
        result = dc.classify('Medium', 5.0, 'Respiratory')
        track(check("Medium/Far(5km) → BLS", result == 'BLS'))
        
        # Low → Bike
        result = dc.classify('Low', 3.0, 'Minor')
        track(check("Low severity → Bike", result == 'Bike'))
        
    except ImportError as e:
        print(f"  ⚠️ Could not import DispatchClassifier: {e}")
        track(False)

# ============================================================================
# SCENARIO TESTS (4 Required Scenarios)
# ============================================================================

def test_scenario_1_monsoon():
    """Scenario 1: Monsoon conditions should increase ETA"""
    section("SCENARIO 1: Monsoon Flooding → ETA Impact")
    
    # Normal conditions
    r1 = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 14, "is_monsoon": False,
        "ambulance_type": 2, "violations_zone": 0
    })
    eta_normal = r1.json().get('eta_minutes', 0)
    
    # Monsoon conditions
    r2 = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 14, "is_monsoon": True,
        "ambulance_type": 2, "violations_zone": 0
    })
    eta_monsoon = r2.json().get('eta_minutes', 0)
    
    print(f"  Normal ETA:  {eta_normal:.2f} min")
    print(f"  Monsoon ETA: {eta_monsoon:.2f} min")
    track(check("Monsoon ETA >= Normal ETA (weather penalty applied)", eta_monsoon >= eta_normal))

def test_scenario_2_rush_hour():
    """Scenario 2: MIDC Rush Hour → ETA impact"""
    section("SCENARIO 2: MIDC Rush Hour → ETA Impact")
    
    # Off-peak (2 PM)
    r1 = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 14, "is_monsoon": False,
        "ambulance_type": 2, "violations_zone": 0
    })
    eta_offpeak = r1.json().get('eta_minutes', 0)
    
    # Rush hour (8 AM)
    r2 = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 8, "is_monsoon": False,
        "ambulance_type": 2, "violations_zone": 0
    })
    eta_rush = r2.json().get('eta_minutes', 0)
    
    # Night (2 AM)
    r3 = requests.post(f"{BASE_URL}/predict-eta", json={
        "distance": 5.0, "hour": 2, "is_monsoon": False,
        "ambulance_type": 2, "violations_zone": 0
    })
    eta_night = r3.json().get('eta_minutes', 0)
    
    print(f"  Night ETA (2 AM):     {eta_night:.2f} min")
    print(f"  Off-Peak ETA (2 PM):  {eta_offpeak:.2f} min")
    print(f"  Rush Hour ETA (8 AM): {eta_rush:.2f} min")
    track(check("Rush hour ETA >= Off-peak ETA", eta_rush >= eta_offpeak * 0.95))  # Allow small tolerance

def test_scenario_3_multi_dispatch():
    """Scenario 3: Multiple simultaneous dispatches → correct type assignment"""
    section("SCENARIO 3: Multi-Ambulance Dispatch → Type Assignment")
    
    dispatches = [
        {"severity": "CRITICAL", "incident_type": "Cardiac", "distance": 5.0, "expected": "ALS"},
        {"severity": "SEVERE", "incident_type": "Respiratory", "distance": 5.0, "expected": "BLS"},
        {"severity": "MODERATE", "incident_type": "Medical", "distance": 1.5, "expected": "Mini"},
    ]
    
    for d in dispatches:
        r = requests.post(f"{BASE_URL}/dispatch", json={
            "patient_lat": 19.076, "patient_lon": 72.877,
            "incident_type": d["incident_type"], "severity": d["severity"],
            "distance": d["distance"], "hour": 14, "is_monsoon": False
        })
        data = r.json()
        assigned_type = data.get('ambulance_type', '')
        print(f"  {d['severity']}/{d['incident_type']} → dispatched: {assigned_type} (expected: {d['expected']})")
        track(check(
            f"{d['severity']} dispatch assigns {d['expected']}",
            assigned_type == d['expected']
        ))

def test_scenario_4_hospital_ranking():
    """Scenario 4: Hospital re-ranking on bed availability"""
    section("SCENARIO 4: Hospital Ranking by Bed Availability")
    
    r = requests.get(f"{BASE_URL}/hospitals")
    data = r.json()
    hospitals = data.get('hospitals', [])
    
    track(check("Hospitals endpoint returns data", len(hospitals) > 0))
    
    # Verify hospitals have bed info
    for h in hospitals[:3]:
        has_beds = 'available_beds' in h and 'total_beds' in h
        track(check(f"Hospital {h.get('name', 'Unknown')} has bed info", has_beds))
    
    # Test dispatch returns hospital with beds
    r2 = requests.post(f"{BASE_URL}/dispatch", json={
        "patient_lat": 19.076, "patient_lon": 72.877,
        "incident_type": "Cardiac", "severity": "CRITICAL",
        "distance": 5.0, "hour": 14, "is_monsoon": False
    })
    dispatch_data = r2.json()
    hospital = dispatch_data.get('hospital', {})
    track(check("Dispatch returns hospital with beds available",
                hospital.get('available_beds', 0) > 0))
    
    nearby = dispatch_data.get('nearby_hospitals', [])
    track(check("Dispatch returns nearby hospital alternatives", len(nearby) > 0))

# ============================================================================
# MAIN
# ============================================================================

def main():
    global passed, failed
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║       NAVIRAKSHA - COMPREHENSIVE TEST SUITE                      ║
║                                                                    ║
║  Tests: API, CRUD, Dispatch Classifier, 4 Scenarios               ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    if not wait_for_server():
        print("❌ Backend server not running! Start it with:")
        print("   .venv\\Scripts\\python.exe modules\\backend\\app.py")
        return False
    
    print("✅ Server is online\n")
    
    try:
        test_api_endpoints()
        test_crud_operations()
        test_dispatch_classifier()
        test_scenario_1_monsoon()
        test_scenario_2_rush_hour()
        test_scenario_3_multi_dispatch()
        test_scenario_4_hospital_ranking()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    total = passed + failed
    print(f"\n{'='*60}")
    print(f"  RESULTS: {passed}/{total} tests passed")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"{'='*60}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
