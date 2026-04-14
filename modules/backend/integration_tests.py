#!/usr/bin/env python3
"""Comprehensive test of database-integrated API"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from app import app

print("\n" + "="*70)
print("Database-Integrated API Test Suite")
print("="*70 + "\n")

test_suite = [
    {
        "name": "Health Check",
        "method": "GET",
        "endpoint": "/health",
        "data": None,
        "checks": ["status", "model_loaded", "scaler_loaded"]
    },
    {
        "name": "ETA Prediction",
        "method": "POST",
        "endpoint": "/predict-eta",
        "data": {"distance": 5, "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0},
        "checks": ["eta_minutes", "confidence", "status"]
    },
    {
        "name": "Active Ambulances (from DB)",
        "method": "GET",
        "endpoint": "/ambulances/active",
        "data": None,
        "checks": ["ambulances", "total"]
    },
    {
        "name": "Active Incidents (from DB)",
        "method": "GET",
        "endpoint": "/incidents/active",
        "data": None,
        "checks": ["incidents", "total"]
    },
    {
        "name": "Hospitals (from DB)",
        "method": "GET",
        "endpoint": "/hospitals",
        "data": None,
        "checks": ["hospitals", "total"]
    },
    {
        "name": "Emergency Dispatch",
        "method": "POST",
        "endpoint": "/dispatch",
        "data": {"latitude": 19.076, "longitude": 72.877, "incident_type": "Cardiac", "severity": "CRITICAL", "hour": 14, "is_monsoon": False, "distance": 5},
        "checks": ["ambulance_type", "ambulance_id", "eta_minutes", "hospital"]
    },
    {
        "name": "DB Status",
        "method": "GET",
        "endpoint": "/admin/db/status",
        "data": None,
        "checks": ["database_path", "tables", "total_records"]
    }
]

passed = 0
failed = 0

with app.test_client() as client:
    for test in test_suite:
        print(f"Test: {test['name']}")
        print(f"  Endpoint: {test['method']} {test['endpoint']}")
        
        try:
            if test['method'] == 'GET':
                response = client.get(test['endpoint'])
            else:
                response = client.post(test['endpoint'], json=test['data'])
            
            print(f"  Status: {response.status_code}", end="")
            
            if response.status_code not in [200, 201]:
                print(" - ERROR")
                print(f"    Response: {response.get_data(as_text=True)}")
                failed += 1
                print()
                continue
            
            data = response.get_json()
            
            # Check required fields
            missing = [f for f in test['checks'] if f not in data]
            if missing:
                print(f" - FAILED (missing: {', '.join(missing)})")
                print(f"    Response keys: {list(data.keys())}")
                failed += 1
            else:
                print(" - PASSED")
                # Show interesting data
                if test['endpoint'] == '/ambulances/active':
                    amb_count = len(data.get('ambulances', []))
                    print(f"    Found {amb_count} ambulances")
                    if amb_count > 0:
                        print(f"    First: {data['ambulances'][0].get('id')} ({data['ambulances'][0].get('type')})")
                elif test['endpoint'] == '/incidents/active':
                    inc_count = len(data.get('incidents', []))
                    print(f"    Found {inc_count} incidents")
                    if inc_count > 0:
                        print(f"    First: {data['incidents'][0].get('id')} - {data['incidents'][0].get('incident_type')}")
                elif test['endpoint'] == '/hospitals':
                    hosp_count = len(data.get('hospitals', []))
                    print(f"    Found {hosp_count} hospitals")
                    if hosp_count > 0:
                        print(f"    First: {data['hospitals'][0].get('name')} ({data['hospitals'][0].get('available_beds')} beds)")
                elif test['endpoint'] == '/dispatch':
                    print(f"    Ambulance: {data.get('ambulance_id')} ({data.get('ambulance_type')})")
                    print(f"    ETA: {data.get('eta_minutes')} minutes")
                    print(f"    Hospital: {data.get('hospital', {}).get('name')}")
                elif test['endpoint'] == '/predict-eta':
                    print(f"    ETA: {data.get('eta_minutes')} minutes")
                elif test['endpoint'] == '/admin/db/status':
                    print(f"    Total records: {data.get('total_records')}")
                    print(f"    Tables: {data.get('tables')}")
                passed += 1
        
        except Exception as e:
            print(f" - EXCEPTION: {str(e)}")
            failed += 1
        
        print()

print("="*70)
print(f"Results: {passed} PASSED, {failed} FAILED")
print("="*70 + "\n")
