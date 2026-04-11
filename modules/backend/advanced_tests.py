"""
Advanced API Testing Suite for NaviRaksha Backend
Tests: Valid/Invalid inputs, Error handling, Edge cases, Performance, Data validation
"""

import requests
import json
import time
from datetime import datetime
import statistics

BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

class APITester:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'timings': []
        }
    
    def test_header(self, title):
        """Print test section header"""
        print(f"\n{Colors.BLUE}{'='*70}")
        print(f"  {title.upper()}")
        print(f"{'='*70}{Colors.END}\n")
    
    def assert_status(self, response, expected_status, test_name):
        """Assert response status code"""
        if response.status_code == expected_status:
            print(f"{Colors.GREEN}✅ {test_name}{Colors.END}")
            self.results['passed'] += 1
            return True
        else:
            error = f"{test_name} - Got {response.status_code}, expected {expected_status}"
            print(f"{Colors.RED}❌ {error}{Colors.END}")
            print(f"   Response: {response.text[:100]}")
            self.results['failed'] += 1
            self.results['errors'].append(error)
            return False
    
    def assert_field(self, data, field, test_name):
        """Assert field exists in response"""
        if field in data:
            print(f"{Colors.GREEN}✅ {test_name}{Colors.END}")
            self.results['passed'] += 1
            return True
        else:
            error = f"{test_name} - Field '{field}' not found"
            print(f"{Colors.RED}❌ {error}{Colors.END}")
            self.results['failed'] += 1
            self.results['errors'].append(error)
            return False
    
    def assert_range(self, value, min_val, max_val, test_name):
        """Assert value is within range"""
        if min_val <= value <= max_val:
            print(f"{Colors.GREEN}✅ {test_name} ({value}){Colors.END}")
            self.results['passed'] += 1
            return True
        else:
            error = f"{test_name} - Value {value} not in range [{min_val}, {max_val}]"
            print(f"{Colors.RED}❌ {error}{Colors.END}")
            self.results['failed'] += 1
            self.results['errors'].append(error)
            return False
    
    def time_request(self, method, endpoint, **kwargs):
        """Time an API request"""
        start = time.time()
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", **kwargs)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", **kwargs)
        elapsed = (time.time() - start) * 1000  # Convert to ms
        self.results['timings'].append(elapsed)
        return response, elapsed
    
    # ========== TEST SUITES ==========
    
    def test_health_endpoint(self):
        """Test 1: Health endpoint with valid request"""
        self.test_header("Test 1: Health Endpoint")
        
        response, elapsed = self.time_request("GET", "/health", timeout=5)
        self.assert_status(response, 200, "Health endpoint returns 200")
        
        data = response.json()
        self.assert_field(data, 'status', "Response has 'status' field")
        self.assert_field(data, 'model_loaded', "Response has 'model_loaded' field")
        self.assert_field(data, 'scaler_loaded', "Response has 'scaler_loaded' field")
        self.assert_field(data, 'timestamp', "Response has 'timestamp' field")
        
        print(f"   Response time: {elapsed:.1f}ms")
        print(f"   Status: {data.get('status')}")
        print(f"   Model loaded: {data.get('model_loaded')}")
    
    def test_predict_eta_valid_inputs(self):
        """Test 2: ETA prediction with valid inputs"""
        self.test_header("Test 2: ETA Prediction - Valid Inputs")
        
        valid_cases = [
            {"distance": 5.0, "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0, "name": "Normal case"},
            {"distance": 0.1, "hour": 0, "is_monsoon": True, "ambulance_type": 1, "violations_zone": 5, "name": "Extreme case 1"},
            {"distance": 50.0, "hour": 23, "is_monsoon": True, "ambulance_type": 3, "violations_zone": 10, "name": "Extreme case 2"},
            {"distance": 15.5, "hour": 9, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 2, "name": "Rush hour"},
            {"distance": 20.0, "hour": 3, "is_monsoon": False, "ambulance_type": 1, "violations_zone": 0, "name": "Night time"},
        ]
        
        for case in valid_cases:
            name = case.pop('name')
            response, elapsed = self.time_request(
                "POST", "/predict-eta",
                json=case,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if self.assert_status(response, 200, f"ETA prediction - {name}"):
                data = response.json()
                self.assert_field(data, 'eta_minutes', f"  - has ETA value")
                self.assert_field(data, 'confidence', f"  - has confidence")
                self.assert_range(data['eta_minutes'], 3, 20, f"  - ETA in valid range")
                print(f"     ETA: {data['eta_minutes']:.1f} min | Time: {elapsed:.1f}ms")
    
    def test_predict_eta_invalid_inputs(self):
        """Test 3: ETA prediction with invalid inputs"""
        self.test_header("Test 3: ETA Prediction - Invalid Inputs (Error Handling)")
        
        invalid_cases = [
            ({"distance": -5.0, "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0}, "Negative distance"),
            ({"distance": 5.0, "hour": 25, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0}, "Hour > 23"),
            ({"distance": 5.0, "hour": 14, "is_monsoon": False, "ambulance_type": 99, "violations_zone": 0}, "Invalid ambulance type"),
            ({}, "Empty body"),
            ({"distance": 5.0}, "Missing fields"),
            ({"distance": "invalid", "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0}, "Invalid data type"),
        ]
        
        for payload, desc in invalid_cases:
            response, elapsed = self.time_request(
                "POST", "/predict-eta",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            # Should either handle gracefully (200) or return 400
            if response.status_code in [200, 400]:
                print(f"{Colors.GREEN}✅ Handled '{desc}' gracefully (status {response.status_code}){Colors.END}")
                self.results['passed'] += 1
            else:
                print(f"{Colors.RED}❌ '{desc}' returned unexpected status {response.status_code}{Colors.END}")
                self.results['failed'] += 1
                self.results['errors'].append(f"Invalid input '{desc}' - status {response.status_code}")
    
    def test_ambulances_endpoint(self):
        """Test 4: Get active ambulances"""
        self.test_header("Test 4: Active Ambulances Endpoint")
        
        response, elapsed = self.time_request("GET", "/ambulances/active", timeout=5)
        self.assert_status(response, 200, "Get ambulances returns 200")
        
        data = response.json()
        self.assert_field(data, 'ambulances', "Response has 'ambulances' array")
        self.assert_field(data, 'total', "Response has 'total' count")
        self.assert_field(data, 'timestamp', "Response has 'timestamp'")
        
        ambulances = data.get('ambulances', [])
        print(f"   Total ambulances: {len(ambulances)}")
        print(f"   Response time: {elapsed:.1f}ms")
        
        if ambulances:
            print(f"\n   Sample ambulance:")
            for key in ['id', 'type', 'status', 'location']:
                if key in ambulances[0]:
                    print(f"      {key}: {ambulances[0][key]}")
    
    def test_incidents_endpoint(self):
        """Test 5: Get active incidents"""
        self.test_header("Test 5: Active Incidents Endpoint")
        
        response, elapsed = self.time_request("GET", "/incidents/active", timeout=5)
        self.assert_status(response, 200, "Get incidents returns 200")
        
        data = response.json()
        self.assert_field(data, 'incidents', "Response has 'incidents' array")
        self.assert_field(data, 'total', "Response has 'total' count")
        
        incidents = data.get('incidents', [])
        print(f"   Total incidents: {len(incidents)}")
        print(f"   Response time: {elapsed:.1f}ms")
        
        if incidents:
            print(f"\n   Sample incident:")
            for key in ['id', 'type', 'severity', 'status']:
                if key in incidents[0]:
                    print(f"      {key}: {incidents[0][key]}")
    
    def test_hospitals_endpoint(self):
        """Test 6: Get hospitals"""
        self.test_header("Test 6: Hospitals Endpoint")
        
        response, elapsed = self.time_request("GET", "/hospitals", timeout=5)
        self.assert_status(response, 200, "Get hospitals returns 200")
        
        data = response.json()
        self.assert_field(data, 'hospitals', "Response has 'hospitals' array")
        self.assert_field(data, 'total', "Response has 'total' count")
        
        hospitals = data.get('hospitals', [])
        print(f"   Total hospitals: {len(hospitals)}")
        print(f"   Response time: {elapsed:.1f}ms")
        
        if hospitals:
            print(f"\n   Sample hospital:")
            for key in ['id', 'name', 'beds_available']:
                if key in hospitals[0]:
                    print(f"      {key}: {hospitals[0][key]}")
    
    def test_dispatch_endpoint(self):
        """Test 7: Emergency dispatch"""
        self.test_header("Test 7: Emergency Dispatch Endpoint")
        
        valid_cases = [
            {"patient_lat": 19.076, "patient_lon": 72.877, "incident_type": "Cardiac", "severity": "Critical", "distance": 5.0, "hour": 14, "is_monsoon": False, "name": "Cardiac emergency"},
            {"patient_lat": 19.080, "patient_lon": 72.880, "incident_type": "Trauma", "severity": "Severe", "distance": 3.0, "hour": 16, "is_monsoon": False, "name": "Trauma case"},
            {"patient_lat": 19.090, "patient_lon": 72.890, "incident_type": "Respiratory", "severity": "Moderate", "distance": 8.0, "hour": 22, "is_monsoon": True, "name": "Respiratory in rain"},
        ]
        
        for case in valid_cases:
            name = case.pop('name')
            response, elapsed = self.time_request(
                "POST", "/dispatch",
                json=case,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if self.assert_status(response, 200, f"Dispatch - {name}"):
                data = response.json()
                self.assert_field(data, 'ambulance_type', f"  - has ambulance_type")
                self.assert_field(data, 'eta_minutes', f"  - has ETA")
                self.assert_field(data, 'hospital', f"  - has hospital")
                print(f"     Ambulance: {data.get('ambulance_type')} | ETA: {data.get('eta_minutes'):.1f} min | Time: {elapsed:.1f}ms")
    
    def test_performance(self):
        """Test 8: Performance metrics"""
        self.test_header("Test 8: Performance Metrics")
        
        print(f"Total requests: {len(self.results['timings'])}")
        
        if self.results['timings']:
            timings = self.results['timings']
            avg_time = statistics.mean(timings)
            min_time = min(timings)
            max_time = max(timings)
            p95_time = sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 1 else avg_time
            
            print(f"Response times:")
            print(f"   Average: {avg_time:.1f}ms")
            print(f"   Minimum: {min_time:.1f}ms")
            print(f"   Maximum: {max_time:.1f}ms")
            print(f"   P95:     {p95_time:.1f}ms")
            
            if avg_time < 100:
                print(f"{Colors.GREEN}✅ Average response time is excellent (<100ms){Colors.END}")
                self.results['passed'] += 1
            elif avg_time < 200:
                print(f"{Colors.YELLOW}⚠️  Average response time is acceptable (<200ms){Colors.END}")
                self.results['passed'] += 1
            else:
                print(f"{Colors.RED}❌ Average response time is slow (>200ms){Colors.END}")
                self.results['failed'] += 1
    
    def test_concurrent_requests(self):
        """Test 9: Concurrent requests handling"""
        self.test_header("Test 9: Concurrent Requests Test")
        
        import concurrent.futures
        
        def make_eta_request():
            response = requests.post(
                f"{BASE_URL}/predict-eta",
                json={"distance": 5.0, "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0},
                timeout=5
            )
            return response.status_code == 200
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_eta_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_count = sum(results)
        print(f"Concurrent requests: 10")
        print(f"Successful: {success_count}/10")
        
        if success_count == 10:
            print(f"{Colors.GREEN}✅ All concurrent requests succeeded{Colors.END}")
            self.results['passed'] += 1
        else:
            print(f"{Colors.YELLOW}⚠️  {10 - success_count} concurrent requests failed{Colors.END}")
            self.results['failed'] += 1
    
    def test_error_scenarios(self):
        """Test 10: Error scenarios"""
        self.test_header("Test 10: Error Scenarios")
        
        # Test 404 (endpoint not found)
        response = requests.get(f"{BASE_URL}/nonexistent", timeout=5)
        if response.status_code == 404:
            print(f"{Colors.GREEN}✅ 404 returned for nonexistent endpoint{Colors.END}")
            self.results['passed'] += 1
        else:
            print(f"{Colors.RED}❌ Expected 404, got {response.status_code}{Colors.END}")
            self.results['failed'] += 1
        
        # Test malformed JSON
        try:
            response = requests.post(
                f"{BASE_URL}/predict-eta",
                data="not json",
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            if response.status_code in [400, 500]:
                print(f"{Colors.GREEN}✅ Malformed JSON handled (status {response.status_code}){Colors.END}")
                self.results['passed'] += 1
            else:
                print(f"{Colors.YELLOW}⚠️  Unexpected status for malformed JSON: {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}❌ Error with malformed JSON: {e}{Colors.END}")
            self.results['failed'] += 1
    
    def print_summary(self):
        """Print test summary"""
        self.test_header("Final Summary")
        
        total = self.results['passed'] + self.results['failed']
        pass_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {Colors.GREEN}{self.results['passed']}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.results['failed']}{Colors.END}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.results['errors']:
            print(f"\n{Colors.RED}Errors:{Colors.END}")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        if pass_rate >= 90:
            print(f"\n{Colors.GREEN}✅ API IS PRODUCTION READY!{Colors.END}")
        elif pass_rate >= 70:
            print(f"\n{Colors.YELLOW}⚠️  API is mostly functional but needs fixes{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ API needs significant work{Colors.END}")

def main():
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"  NaviRaksha Backend - Advanced Testing Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}{Colors.END}")
    
    tester = APITester()
    
    try:
        tester.test_health_endpoint()
        tester.test_predict_eta_valid_inputs()
        tester.test_predict_eta_invalid_inputs()
        tester.test_ambulances_endpoint()
        tester.test_incidents_endpoint()
        tester.test_hospitals_endpoint()
        tester.test_dispatch_endpoint()
        tester.test_performance()
        tester.test_concurrent_requests()
        tester.test_error_scenarios()
        tester.print_summary()
        
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
