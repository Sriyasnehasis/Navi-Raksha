#!/usr/bin/env python
"""Comprehensive CRUD tests for all admin endpoints"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def wait_for_server(max_retries=10):
    """Wait for server to be ready"""
    for i in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            print("✓ Server is ready\n")
            return True
        except:
            if i < max_retries - 1:
                print(f"Waiting for server... ({i+1}/{max_retries})")
                time.sleep(1)
    return False

def test_section(title):
    """Print test section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_crud(resource, resource_name, create_payload, update_payload):
    """Test CRUD operations for a resource"""
    test_section(f"Testing {resource_name} CRUD Operations")
    
    resource_id = create_payload['id']
    endpoint = f"/admin/{resource}"
    
    # CREATE
    print(f"\n1. CREATE {resource_name}...")
    response = requests.post(f"{BASE_URL}{endpoint}", json=create_payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    created = response.json()
    print(f"   ✅ Created: {resource_id}")
    
    # GET
    print(f"\n2. GET {resource_name}...")
    response = requests.get(f"{BASE_URL}{endpoint}/{resource_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    fetched = response.json()
    print(f"   ✅ Retrieved: {resource_id}")
    
    # UPDATE
    print(f"\n3. UPDATE {resource_name}...")
    response = requests.put(f"{BASE_URL}{endpoint}/{resource_id}", json=update_payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    updated = response.json()
    print(f"   ✅ Updated: {resource_id}")
    
    # DELETE
    print(f"\n4. DELETE {resource_name}...")
    response = requests.delete(f"{BASE_URL}{endpoint}/{resource_id}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print(f"   ✅ Deleted: {resource_id}")
    
    # Verify deleted
    print(f"\n5. Verify {resource_name} is deleted...")
    response = requests.get(f"{BASE_URL}{endpoint}/{resource_id}")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print(f"   ✅ Confirmed deleted: {resource_id}")
    
    return True

def main():
    """Run all tests"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║           COMPREHENSIVE CRUD TESTS - ALL RESOURCES                         ║
║                                                                              ║
║  Testing: Ambulances, Incidents, Hospitals                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    if not wait_for_server():
        print("❌ Server not responding!")
        return False
    
    try:
        # 1. AMBULANCE CRUD
        ambulance_create = {
            "id": "TEST-AMB-CRUD",
            "name": "Test Ambulance",
            "type": "ALS",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "driver_name": "Driver Name",
            "crew_size": 2,
            "status": "available"
        }
        
        ambulance_update = {
            "name": "Updated Ambulance",
            "driver_name": "New Driver",
            "status": "responding"
        }
        
        test_crud("ambulances", "Ambulance", ambulance_create, ambulance_update)
        
        # 2. HOSPITAL CRUD
        hospital_create = {
            "id": "TEST-HOSP-CRUD",
            "name": "Test Hospital",
            "address": "123 Hospital St",
            "phone": "123-456-7890",
            "latitude": 19.0800,
            "longitude": 72.8800,
            "total_beds": 100,
            "available_beds": 30,
            "is_active": True,
            "has_trauma_center": True,
            "has_cardiac_care": True
        }
        
        hospital_update = {
            "name": "Updated Hospital",
            "available_beds": 25,
            "has_trauma_center": False
        }
        
        test_crud("hospitals", "Hospital", hospital_create, hospital_update)
        
        # 3. INCIDENT CRUD
        # First create hospital for assignment
        hospital_resp = requests.post(
            f"{BASE_URL}/admin/hospitals",
            json={
                "id": "TEMP-HOSP",
                "name": "Temp Hospital",
                "latitude": 19.08,
                "longitude": 72.88,
                "total_beds": 50,
                "available_beds": 10
            }
        )
        
        ambulance_resp = requests.post(
            f"{BASE_URL}/admin/ambulances",
            json={
                "id": "TEMP-AMB",
                "name": "Temp Ambulance",
                "type": "BLS",
                "latitude": 19.076,
                "longitude": 72.877,
                "driver_name": "Test",
                "crew_size": 1
            }
        )
        
        incident_create = {
            "id": "TEST-INC-CRUD",
            "incident_type": "Cardiac",
            "severity": "critical",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "patient_name": "Test Patient",
            "patient_age": 45,
            "contact_number": "9876543210",
            "status": "waiting"
        }
        
        incident_update = {
            "severity": "severe",
            "status": "assigned",
            "patient_age": 46,
            "assigned_ambulance_id": "TEMP-AMB",
            "assigned_hospital_id": "TEMP-HOSP"
        }
        
        test_crud("incidents", "Incident", incident_create, incident_update)
        
        # Clean up temp resources
        requests.delete(f"{BASE_URL}/admin/hospitals/TEMP-HOSP")
        requests.delete(f"{BASE_URL}/admin/ambulances/TEMP-AMB")
        
        # Success!
        print("\n" + "="*70)
        print("  ✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nSummary:")
        print("  ✓ Ambulance CRUD: CREATE, READ, UPDATE, DELETE")
        print("  ✓ Hospital CRUD: CREATE, READ, UPDATE, DELETE")
        print("  ✓ Incident CRUD: CREATE, READ, UPDATE, DELETE")
        print("\nAll 12 operations successful!\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
