"""
NaviRaksha Load Testing Script
Test concurrent users, response times, and API stability under load
Uses Locust framework for distributed load testing
"""

from locust import HttpUser, task, between
from random import randint, choice, uniform
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
AMBULANCE_TYPES = [1, 2, 3]  # ALS, BLS, Mini
SEVERITIES = ["Critical", "High", "Medium", "Low"]
INCIDENT_TYPES = ["Cardiac", "Trauma", "Respiratory", "Burn", "Allergic"]
HOURS = list(range(24))

# Navi Mumbai coordinates range
LAT_MIN, LAT_MAX = 19.0, 19.1
LON_MIN, LON_MAX = 72.8, 72.9


class NaviRakshaUser(HttpUser):
    """
    Simulates a real user interacting with NaviRaksha API
    Includes health checks, predictions, and dispatch operations
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    @task(5)
    def health_check(self):
        """Health check - lightweight, should always succeed"""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            if response.status_code == 200:
                response.success()
                logger.debug(f"✓ Health check passed")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def get_active_ambulances(self):
        """Fetch active ambulances"""
        with self.client.get(
            "/ambulances/active",
            catch_response=True,
            name="/ambulances/active"
        ) as response:
            if response.status_code == 200 and response.json().get('status') == 'success':
                response.success()
                logger.debug(f"✓ Got {len(response.json()['ambulances'])} ambulances")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def get_active_incidents(self):
        """Fetch active incidents"""
        with self.client.get(
            "/incidents/active",
            catch_response=True,
            name="/incidents/active"
        ) as response:
            if response.status_code == 200 and response.json().get('status') == 'success':
                response.success()
                logger.debug(f"✓ Got {len(response.json()['incidents'])} incidents")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(3)
    def get_hospitals(self):
        """Fetch hospital list"""
        with self.client.get(
            "/hospitals",
            catch_response=True,
            name="/hospitals"
        ) as response:
            if response.status_code == 200 and response.json().get('status') == 'success':
                response.success()
                logger.debug(f"✓ Got {len(response.json()['hospitals'])} hospitals")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(10)
    def predict_eta(self):
        """Predict ETA using default RF model"""
        payload = {
            "distance": uniform(1, 15),
            "hour": choice(HOURS),
            "is_monsoon": randint(0, 1),
            "ambulance_type": choice(AMBULANCE_TYPES),
            "violations_zone": randint(0, 3)
        }
        
        with self.client.post(
            "/predict-eta",
            json=payload,
            catch_response=True,
            name="/predict-eta"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'eta_minutes' in data:
                    response.success()
                    logger.debug(f"✓ ETA prediction: {data['eta_minutes']} min")
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(8)
    def predict_eta_by_model(self):
        """Predict ETA with model selection"""
        model = choice(["RF", "LSTM", "GNN"])
        payload = {
            "model": model,
            "distance": uniform(1, 15),
            "hour": choice(HOURS),
            "is_monsoon": randint(0, 1),
            "ambulance_type": choice(AMBULANCE_TYPES),
            "violations_zone": randint(0, 3)
        }
        
        with self.client.post(
            "/predict-eta/by-model",
            json=payload,
            catch_response=True,
            name="/predict-eta/by-model [" + model + "]"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and data.get('model') == model:
                    response.success()
                    logger.debug(f"✓ {model} prediction: {data['eta_minutes']} min (RF: {data['reference_eta_rf']})")
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(15)
    def dispatch_emergency(self):
        """Dispatch emergency - main operation"""
        payload = {
            "incident_latitude": uniform(LAT_MIN, LAT_MAX),
            "incident_longitude": uniform(LON_MIN, LON_MAX),
            "severity": choice(SEVERITIES),
            "incident_type": choice(INCIDENT_TYPES),
            "patient_name": f"Patient_{randint(1000, 9999)}",
            "patient_phone": f"+91-{randint(6000000000, 9999999999)}",
            "distance_km": uniform(0.5, 5)
        }
        
        with self.client.post(
            "/dispatch",
            json=payload,
            catch_response=True,
            name="/dispatch"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    response.success()
                    ambulance_id = data.get('ambulance', {}).get('id')
                    eta = data.get('eta_minutes')
                    logger.debug(f"✓ Dispatch: {ambulance_id} to {data.get('incident', {}).get('severity')} (ETA: {eta}min)")
                else:
                    response.failure("Dispatch failed")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_model_comparison(self):
        """Get model performance comparison"""
        with self.client.get(
            "/models/comparison",
            catch_response=True,
            name="/models/comparison"
        ) as response:
            if response.status_code == 200:
                response.success()
                logger.debug(f"✓ Got model comparison metrics")
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def database_status(self):
        """Check database status (admin endpoint)"""
        with self.client.get(
            "/admin/db/status",
            catch_response=True,
            name="/admin/db/status"
        ) as response:
            if response.status_code == 200:
                response.success()
                data = response.json()
                logger.debug(f"✓ DB Status: {data.get('ambulances_count')} ambulances, "
                           f"{data.get('incidents_count')} incidents, "
                           f"{data.get('hospitals_count')} hospitals")
            else:
                response.failure(f"Status: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulates an administrator performing CRUD operations
    """
    
    wait_time = between(5, 10)  # Admin operations are slower
    
    @task(1)
    def create_ambulance(self):
        """Create new ambulance"""
        ambulance_id = f"LOAD-{randint(1000, 9999)}"
        payload = {
            "id": ambulance_id,
            "type": choice(["ALS", "BLS", "Mini"]),
            "driver_name": f"Driver_{randint(1, 1000)}",
            "phone": f"+91-{randint(6000000000, 9999999999)}",
            "latitude": uniform(LAT_MIN, LAT_MAX),
            "longitude": uniform(LON_MIN, LON_MAX),
            "status": "Available"
        }
        
        with self.client.post(
            "/admin/ambulances",
            json=payload,
            catch_response=True,
            name="/admin/ambulances [POST]"
        ) as response:
            if response.status_code == 201:
                response.success()
                logger.debug(f"✓ Created ambulance: {ambulance_id}")
            elif response.status_code == 409:
                # Already exists - acceptable
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(1)
    def create_incident(self):
        """Create new incident"""
        incident_id = f"INC-LOAD-{randint(100000, 999999)}"
        payload = {
            "id": incident_id,
            "severity": choice(SEVERITIES),
            "type": choice(INCIDENT_TYPES),
            "location": f"Location_{randint(1, 100)}",
            "latitude": uniform(LAT_MIN, LAT_MAX),
            "longitude": uniform(LON_MIN, LON_MAX),
            "patient_name": f"Patient_{randint(1000, 9999)}",
            "patient_phone": f"+91-{randint(6000000000, 9999999999)}"
        }
        
        with self.client.post(
            "/admin/incidents",
            json=payload,
            catch_response=True,
            name="/admin/incidents [POST]"
        ) as response:
            if response.status_code == 201:
                response.success()
                logger.debug(f"✓ Created incident: {incident_id}")
            elif response.status_code == 409:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_ambulance(self):
        """Read ambulance details"""
        ambulance_id = choice(["ALS-001", "BLS-001", "MINI-001"])
        
        with self.client.get(
            f"/admin/ambulances/{ambulance_id}",
            catch_response=True,
            name="/admin/ambulances/{id} [GET]"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")
    
    @task(2)
    def get_incident(self):
        """Read incident details"""
        incident_id = choice(["INC-001", "INC-002", "INC-003"])
        
        with self.client.get(
            f"/admin/incidents/{incident_id}",
            catch_response=True,
            name="/admin/incidents/{id} [GET]"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")


# ============================================================================
# Usage Instructions
# ============================================================================
"""
Run Load Test:

1. SIMPLE (100 users, 10 spawn rate):
   locust -f tests/load_test.py --host=http://localhost:8000 -u 100 -r 10

2. MODERATE (500 users, 50 spawn rate, 10 min duration):
   locust -f tests/load_test.py --host=http://localhost:8000 -u 500 -r 50 --run-time 10m

3. HIGH STRESS (1000 users, 100 spawn rate, 5 min duration):
   locust -f tests/load_test.py --host=http://localhost:8000 -u 1000 -r 100 --run-time 5m

4. WITH WEB UI (interactive):
   locust -f tests/load_test.py --host=http://localhost:8000

5. HEADLESS (automated, output to CSV):
   locust -f tests/load_test.py --host=http://localhost:8000 -u 500 -r 50 --run-time 10m --headless --csv=results

CSV Results will include:
- Response times (avg, min, max, 95th percentile, 99th percentile)
- Failure rates per endpoint
- Request counts
- Throughput (requests/second)

Key Metrics to Monitor:
- Response time < 500ms for health check & predict-eta
- Response time < 1000ms for dispatch operations
- Zero failures on successful loads
- Throughput > 50 req/s under 500 concurrent users
"""
