#!/usr/bin/env python
"""Test ambulance CRUD endpoints"""

import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"

def test_create_ambulance():
    """Test: Create a new ambulance"""
    print("\n" + "="*70)
    print("TEST 1: CREATE Ambulance (POST /admin/ambulances)")
    print("="*70)
    
    payload = {
        "id": "AMB-TEST-001",
        "name": "Test Ambulance 1",
        "type": "ALS",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "driver_name": "John Test",
        "crew_size": 2,
        "status": "available"
    }
    
    response = requests.post(f"{BASE_URL}/admin/ambulances", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 201

def test_get_ambulance():
    """Test: Get a specific ambulance"""
    print("\n" + "="*70)
    print("TEST 2: GET Ambulance (GET /admin/ambulances/<id>)")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/admin/ambulances/AMB-TEST-001")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def test_update_ambulance():
    """Test: Update an ambulance"""
    print("\n" + "="*70)
    print("TEST 3: UPDATE Ambulance (PUT /admin/ambulances/<id>)")
    print("="*70)
    
    payload = {
        "name": "Updated Test Ambulance 1",
        "driver_name": "Jane Doe",
        "crew_size": 3,
        "status": "responding"
    }
    
    response = requests.put(f"{BASE_URL}/admin/ambulances/AMB-TEST-001", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def test_delete_ambulance():
    """Test: Delete an ambulance"""
    print("\n" + "="*70)
    print("TEST 4: DELETE Ambulance (DELETE /admin/ambulances/<id>)")
    print("="*70)
    
    response = requests.delete(f"{BASE_URL}/admin/ambulances/AMB-TEST-001")
    print(f"Status: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def test_error_cases():
    """Test: Error cases"""
    print("\n" + "="*70)
    print("TEST 5: Error Cases")
    print("="*70)
    
    # 5a: Try to get non-existent ambulance
    print("\n5a. GET non-existent ambulance:")
    response = requests.get(f"{BASE_URL}/admin/ambulances/NONEXISTENT-99")
    print(f"Status: {response.status_code} (Expected: 404)")
    
    # 5b: Try to create duplicate
    print("\n5b. CREATE duplicate (after deletion, should succeed):")
    payload = {
        "id": "AMB-TEST-002",
        "name": "Test Ambulance 2",
        "type": "BLS",
        "latitude": 19.0800,
        "longitude": 72.8800,
        "driver_name": "Mary Smith",
        "crew_size": 1
    }
    response = requests.post(f"{BASE_URL}/admin/ambulances", json=payload)
    print(f"Status: {response.status_code} (Expected: 201)")
    
    # Try again (should fail with 409 Conflict)
    print("\n5c. CREATE duplicate again (should fail):")
    response = requests.post(f"{BASE_URL}/admin/ambulances", json=payload)
    print(f"Status: {response.status_code} (Expected: 409)")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 5d: Missing required field
    print("\n5d. CREATE missing required field:")
    bad_payload = {
        "name": "Incomplete Ambulance",
        "type": "ALS"
        # Missing: id, latitude, longitude
    }
    response = requests.post(f"{BASE_URL}/admin/ambulances", json=bad_payload)
    print(f"Status: {response.status_code} (Expected: 400)")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Clean up: Delete test ambulance 2
    requests.delete(f"{BASE_URL}/admin/ambulances/AMB-TEST-002")

def main():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║               AMBULANCE CRUD ENDPOINTS - TEST SUITE                         ║
║                                                                              ║
║  Testing: POST, GET, PUT, DELETE operations on /admin/ambulances          ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "CREATE": False,
        "GET": False,
        "UPDATE": False,
        "DELETE": False,
        "ERROR_HANDLING": False
    }
    
    try:
        # Wait for server to be ready
        max_retries = 5
        for attempt in range(max_retries):
            try:
                requests.get(f"{BASE_URL}/health")
                break
            except:
                if attempt < max_retries - 1:
                    print(f"Waiting for server... ({attempt+1}/{max_retries-1})")
                    time.sleep(1)
                else:
                    print("❌ Server not responding!")
                    return
        
        results["CREATE"] = test_create_ambulance()
        results["GET"] = test_get_ambulance()
        results["UPDATE"] = test_update_ambulance()
        results["DELETE"] = test_delete_ambulance()
        results["ERROR_HANDLING"] = test_error_cases()
        
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "⚠️  PARTIAL"
        print(f"{test:20} | {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed_tests}/{total_tests} tests successful\n")

if __name__ == "__main__":
    main()
