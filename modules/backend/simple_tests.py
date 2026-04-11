"""
Simple API Testing Suite for NaviRaksha Backend
Tests all endpoints without special unicode characters
"""

import requests
import json
import time
from datetime import datetime
import statistics

BASE_URL = "http://127.0.0.1:8000"

results = {'passed': 0, 'failed': 0, 'errors': [], 'timings': []}

def test(name, condition):
    """Simple test assertion"""
    if condition:
        print(f"[PASS] {name}")
        results['passed'] += 1
    else:
        print(f"[FAIL] {name}")
        results['failed'] += 1
        results['errors'].append(name)

print("\n" + "="*70)
print("NaviRaksha Backend - Simple Test Suite")
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("="*70 + "\n")

# ========== Test 1: Health Endpoint ==========
print("TEST 1: Health Endpoint")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    test("Health returns status 200", response.status_code == 200)
    data = response.json()
    test("Has status field", 'status' in data)
    test("Has model_loaded field", 'model_loaded' in data)
    test("Has scaler_loaded field", 'scaler_loaded' in data)
    test("Status is healthy", data.get('status') == 'healthy')
    print(f"Response: {json.dumps(data, indent=2)}\n")
except Exception as e:
    test("Health endpoint", False)
    print(f"Error: {e}\n")

# ========== Test 2: ETA Prediction ==========
print("TEST 2: ETA Prediction")
print("-" * 70)
try:
    payload = {
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False,
        "ambulance_type": 2,
        "violations_zone": 0
    }
    response = requests.post(f"{BASE_URL}/predict-eta", json=payload, timeout=5)
    test("ETA returns status 200", response.status_code == 200)
    data = response.json()
    test("Has eta_minutes field", 'eta_minutes' in data)
    test("ETA value is reasonable", 3 <= data.get('eta_minutes', 0) <= 20)
    print(f"ETA Prediction: {data.get('eta_minutes'):.1f} minutes")
    print(f"Confidence: {data.get('confidence')}\n")
except Exception as e:
    test("ETA prediction", False)
    print(f"Error: {e}\n")

# ========== Test 3: Ambulances ==========
print("TEST 3: Active Ambulances")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/ambulances/active", timeout=5)
    test("Ambulances returns 200", response.status_code == 200)
    data = response.json()
    test("Has ambulances array", 'ambulances' in data)
    ambulances = data.get('ambulances', [])
    test("Has ambulance data", len(ambulances) > 0)
    print(f"Total ambulances: {len(ambulances)}")
    if ambulances:
        print(f"Sample: {json.dumps(ambulances[0], indent=2)}\n")
except Exception as e:
    test("Ambulances endpoint", False)
    print(f"Error: {e}\n")

# ========== Test 4: Incidents ==========
print("TEST 4: Active Incidents")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/incidents/active", timeout=5)
    test("Incidents returns 200", response.status_code == 200)
    data = response.json()
    test("Has incidents array", 'incidents' in data)
    incidents = data.get('incidents', [])
    test("Has incident data", len(incidents) > 0)
    print(f"Total incidents: {len(incidents)}\n")
except Exception as e:
    test("Incidents endpoint", False)
    print(f"Error: {e}\n")

# ========== Test 5: Hospitals ==========
print("TEST 5: Hospitals")
print("-" * 70)
try:
    response = requests.get(f"{BASE_URL}/hospitals", timeout=5)
    test("Hospitals returns 200", response.status_code == 200)
    data = response.json()
    test("Has hospitals array", 'hospitals' in data)
    hospitals = data.get('hospitals', [])
    test("Has hospital data", len(hospitals) > 0)
    print(f"Total hospitals: {len(hospitals)}\n")
except Exception as e:
    test("Hospitals endpoint", False)
    print(f"Error: {e}\n")

# ========== Test 6: Dispatch ==========
print("TEST 6: Emergency Dispatch")
print("-" * 70)
try:
    payload = {
        "patient_lat": 19.076,
        "patient_lon": 72.877,
        "incident_type": "Cardiac",
        "severity": "Critical",
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False
    }
    response = requests.post(f"{BASE_URL}/dispatch", json=payload, timeout=5)
    test("Dispatch returns 200", response.status_code == 200)
    data = response.json()
    test("Has ambulance_type", 'ambulance_type' in data)
    test("Has eta_minutes", 'eta_minutes' in data)
    print(f"Ambulance Type: {data.get('ambulance_type')}")
    print(f"ETA: {data.get('eta_minutes')} minutes\n")
except Exception as e:
    test("Dispatch endpoint", False)
    print(f"Error: {e}\n")

# ========== Test 7: Error Handling ==========
print("TEST 7: Invalid Input Handling")
print("-" * 70)
try:
    # Missing required fields
    payload = {"distance": 5.0}  # Missing other fields
    response = requests.post(f"{BASE_URL}/predict-eta", json=payload, timeout=5)
    test("Handles missing fields", response.status_code in [200, 400])
    
    # Empty body
    response = requests.post(f"{BASE_URL}/predict-eta", json={}, timeout=5)
    test("Handles empty body", response.status_code in [200, 400])
    print()
except Exception as e:
    test("Error handling", False)
    print(f"Error: {e}\n")

# ========== Summary ==========
print("="*70)
print("TEST SUMMARY")
print("="*70)
total = results['passed'] + results['failed']
pass_rate = (results['passed'] / total * 100) if total > 0 else 0

print(f"Total Tests: {total}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
print(f"Pass Rate: {pass_rate:.1f}%")

if results['errors']:
    print(f"\nFailed tests:")
    for error in results['errors']:
        print(f"  - {error}")

if pass_rate == 100:
    print("\nSUCCESS: All tests passed! API is ready for production.\n")
elif pass_rate >= 80:
    print("\nGOOD: Most tests passed. Minor issues to fix.\n")
else:
    print("\nWARNING: Several tests failed. API needs work.\n")
