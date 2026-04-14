"""
Test script for NaviRaksha Backend API
Run this to verify the API is working correctly
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "Health check failed"
    print("✅ Health check passed!")

def test_predict_eta():
    """Test ETA prediction"""
    print("\n⏱️  Testing /predict-eta...")
    payload = {
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False,
        "ambulance_type": 2,  # BLS
        "violations_zone": 0
    }
    response = requests.post(f"{BASE_URL}/predict-eta", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "ETA prediction failed"
    assert "eta_minutes" in response.json(), "No ETA in response"
    print(f"✅ Predicted ETA: {response.json()['eta_minutes']} minutes")

def test_get_ambulances():
    """Test get active ambulances"""
    print("\n🚑 Testing /ambulances/active...")
    response = requests.get(f"{BASE_URL}/ambulances/active")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total ambulances: {data['total']}")
    print(f"Ambulances: {json.dumps(data['ambulances'][:2], indent=2)}")  # Show first 2
    assert response.status_code == 200, "Get ambulances failed"
    assert len(data['ambulances']) > 0, "No ambulances found"
    print(f"✅ Found {data['total']} active ambulances")

def test_get_incidents():
    """Test get active incidents"""
    print("\n🚨 Testing /incidents/active...")
    response = requests.get(f"{BASE_URL}/incidents/active")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total incidents: {data['total']}")
    print(f"Incidents: {json.dumps(data['incidents'][:2], indent=2)}")  # Show first 2
    assert response.status_code == 200, "Get incidents failed"
    print(f"✅ Found {data['total']} active incidents")

def test_get_hospitals():
    """Test get hospitals"""
    print("\n🏥 Testing /hospitals...")
    response = requests.get(f"{BASE_URL}/hospitals")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total hospitals: {data['total']}")
    print(f"Hospitals: {json.dumps(data['hospitals'][:2], indent=2)}")  # Show first 2
    assert response.status_code == 200, "Get hospitals failed"
    print(f"✅ Found {data['total']} hospitals")

def test_dispatch():
    """Test emergency dispatch"""
    print("\n📍 Testing /dispatch...")
    payload = {
        "patient_lat": 19.076,
        "patient_lon": 72.877,
        "incident_type": "Cardiac",
        "severity": "Critical",
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False
    }
    response = requests.post(f"{BASE_URL}/dispatch", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200, "Dispatch failed"
    assert "ambulance_type" in response.json(), "No ambulance type in response"
    print(f"✅ Dispatch successful - Sending {response.json()['ambulance_type']}")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("NaviRaksha Backend API - Test Suite")
    print("=" * 60)
    
    try:
        test_health()
        test_predict_eta()
        test_get_ambulances()
        test_get_incidents()
        test_get_hospitals()
        test_dispatch()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🎉 Backend API is working correctly!")
        print("\nNext steps:")
        print("1. Connect Arisha's frontend to these endpoints")
        print("2. Update ambulance/incident data sources")
        print("3. Integrate with Turya's routing module")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("Make sure the API is running: python modules/backend/app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == '__main__':
    run_all_tests()
