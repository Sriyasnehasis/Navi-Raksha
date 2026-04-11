import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("Waiting for server...")
for i in range(5):
    try:
        requests.get(f"{BASE_URL}/health", timeout=1)
        print("✓ Server is ready\n")
        break
    except:
        if i < 4:
            time.sleep(1)

# Test 1: CREATE
print("=" * 60)
print("TEST 1: CREATE Ambulance (POST /admin/ambulances)")
print("=" * 60)
payload = {
    "id": "TEST-AMB-001",
    "name": "Test Ambulance",
    "type": "ALS",
    "latitude": 19.076,
    "longitude": 72.877,
    "driver_name": "Test Driver",
    "crew_size": 2,
    "status": "available"
}

response = requests.post(
    f"{BASE_URL}/admin/ambulances",
    json=payload,
    timeout=5
)
print(f"Status: {response.status_code} (Expected: 201)")
print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
assert response.status_code == 201, f"Expected 201, got {response.status_code}"

# Test 2: GET
print("=" * 60)
print("TEST 2: GET Ambulance (GET /admin/ambulances/<id>)")
print("=" * 60)
response = requests.get(
    f"{BASE_URL}/admin/ambulances/TEST-AMB-001",
    timeout=5
)
print(f"Status: {response.status_code} (Expected: 200)")
print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Test 3: UPDATE
print("=" * 60)
print("TEST 3: UPDATE Ambulance (PUT /admin/ambulances/<id>)")
print("=" * 60)
update_payload = {
    "name": "Updated Test Ambulance",
    "driver_name": "New Driver",
    "status": "responding"
}
response = requests.put(
    f"{BASE_URL}/admin/ambulances/TEST-AMB-001",
    json=update_payload,
    timeout=5
)
print(f"Status: {response.status_code} (Expected: 200)")
print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# Test 4: DELETE
print("=" * 60)
print("TEST 4: DELETE Ambulance (DELETE /admin/ambulances/<id>)")
print("=" * 60)
response = requests.delete(
    f"{BASE_URL}/admin/ambulances/TEST-AMB-001",
    timeout=5
)
print(f"Status: {response.status_code} (Expected: 200)")
print(f"Response:\n{json.dumps(response.json(), indent=2)}\n")
assert response.status_code == 200, f"Expected 200, got {response.status_code}"

print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
