"""
Load Testing Script for Navi-Raksha Backend
Tests API performance with concurrent users
"""

from locust import HttpUser, task, between
import random
import json
from datetime import datetime

# Backend URL - Change to your deployed URL
BACKEND_URL = "https://navi-raksha-backend.onrender.com"


class AmbulanceDispatchUser(HttpUser):
    """Simulates a user making dispatch requests"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Initialize user session"""
        # Test health check first
        self.health_check()
    
    def health_check(self):
        """Verify backend is up"""
        self.client.get("/health", name="Health Check")
    
    @task(3)  # Weight: 3x more frequent
    def dispatch_ambulance(self):
        """Simulate emergency dispatch request"""
        payload = {
            "latitude": 19.076 + random.uniform(-0.05, 0.05),
            "longitude": 72.877 + random.uniform(-0.05, 0.05),
            "incident_type": random.choice(["Cardiac", "Trauma", "Respiratory", "Burn"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "patient_name": f"Patient_{random.randint(1000, 9999)}"
        }
        self.client.post(
            "/dispatch",
            json=payload,
            name="Dispatch Ambulance"
        )
    
    @task(2)  # Weight: 2x
    def predict_eta(self):
        """Get ETA prediction for a route"""
        payload = {
            "distance_km": random.uniform(1, 10),
            "traffic_level": random.choice(["low", "moderate", "high"]),
            "ambulance_type": random.choice(["ALS", "BLS", "Mini"])
        }
        self.client.post(
            "/predict-eta",
            json=payload,
            name="Predict ETA"
        )
    
    @task(2)  # Weight: 2x
    def get_active_ambulances(self):
        """Get list of active ambulances"""
        self.client.get("/ambulances/active", name="Get Active Ambulances")
    
    @task(2)  # Weight: 2x
    def get_active_incidents(self):
        """Get list of active incidents"""
        self.client.get("/incidents/active", name="Get Active Incidents")
    
    @task(1)  # Weight: 1x
    def get_hospitals(self):
        """Get hospitals list and availability"""
        self.client.get("/hospitals", name="Get Hospitals")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║  Navi-Raksha Load Testing                             ║
    ╚═══════════════════════════════════════════════════════╝
    
    Usage:
    
    1. RUN WITH GUI:
       locust -f load_test.py --host=https://navi-raksha-backend.onrender.com
       
    2. RUN HEADLESS (100 users, 10 spawn rate, 5 min duration):
       locust -f load_test.py --host=https://navi-raksha-backend.onrender.com \\
         --users 100 --spawn-rate 10 --run-time 5m --headless
    
    3. RUN BIG TEST (500 users, 50 spawn rate, 10 min):
       locust -f load_test.py --host=https://navi-raksha-backend.onrender.com \\
         --users 500 --spawn-rate 50 --run-time 10m --headless
    
    4. SAVE CSV RESULTS:
       locust -f load_test.py --host=https://navi-raksha-backend.onrender.com \\
         --users 100 --spawn-rate 10 --run-time 5m --headless \\
         --csv=load_test_results
    
    After running, view results:
    - Terminal output (default)
    - CSV files: load_test_results_*.csv
    - Check http://localhost:8089 (if using GUI)
    """)
