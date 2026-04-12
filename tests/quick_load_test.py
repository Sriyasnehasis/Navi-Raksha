"""
NaviRaksha Quick Load Test - Simple requests-based load testing
Alternative to Locust for quick performance benchmarking
No additional dependencies - uses built-in libraries only
"""

import requests
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, stdev
from random import randint, choice, uniform
from datetime import datetime
import sys

# Configuration
API_BASE_URL = "http://localhost:8000"
NUM_WORKERS = 10  # concurrent threads
NUM_REQUESTS_PER_WORKER = 50
TIMEOUT = 10  # seconds

# Test data
AMBULANCE_TYPES = [1, 2, 3]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
INCIDENT_TYPES = ["Cardiac", "Trauma", "Respiratory", "Burn"]
LAT_MIN, LAT_MAX = 19.0, 19.1
LON_MIN, LON_MAX = 72.8, 72.9

# Results tracking
results = {
    'health': [],
    'ambulances': [],
    'predict_eta': [],
    'dispatch': [],
    'errors': [],
    'total_time': 0
}


def test_health_check():
    """Test /health endpoint"""
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        elapsed = (time.time() - start) * 1000  # convert to ms
        
        if response.status_code == 200:
            results['health'].append(elapsed)
            return True, elapsed
        else:
            results['errors'].append(f"Health check failed: {response.status_code}")
            return False, elapsed
    except Exception as e:
        results['errors'].append(f"Health check error: {str(e)}")
        return False, 0


def test_get_ambulances():
    """Test /ambulances/active endpoint"""
    try:
        start = time.time()
        response = requests.get(f"{API_BASE_URL}/ambulances/active", timeout=TIMEOUT)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            results['ambulances'].append(elapsed)
            return True, elapsed
        else:
            results['errors'].append(f"Get ambulances failed: {response.status_code}")
            return False, elapsed
    except Exception as e:
        results['errors'].append(f"Get ambulances error: {str(e)}")
        return False, 0


def test_predict_eta():
    """Test /predict-eta endpoint"""
    try:
        payload = {
            "distance": uniform(1, 15),
            "hour": randint(0, 23),
            "is_monsoon": randint(0, 1),
            "ambulance_type": choice(AMBULANCE_TYPES),
            "violations_zone": 0
        }
        
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/predict-eta",
            json=payload,
            timeout=TIMEOUT
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200 and response.json().get('status') == 'success':
            results['predict_eta'].append(elapsed)
            return True, elapsed
        else:
            results['errors'].append(f"Predict ETA failed: {response.status_code}")
            return False, elapsed
    except Exception as e:
        results['errors'].append(f"Predict ETA error: {str(e)}")
        return False, 0


def test_dispatch():
    """Test /dispatch endpoint"""
    try:
        payload = {
            "incident_latitude": uniform(LAT_MIN, LAT_MAX),
            "incident_longitude": uniform(LON_MIN, LON_MAX),
            "severity": choice(SEVERITIES),
            "incident_type": choice(INCIDENT_TYPES),
            "patient_name": f"Patient_{randint(1000, 9999)}",
            "patient_phone": f"+91-{randint(6000000000, 9999999999)}",
            "distance_km": uniform(0.5, 5)
        }
        
        start = time.time()
        response = requests.post(
            f"{API_BASE_URL}/dispatch",
            json=payload,
            timeout=TIMEOUT
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200 and response.json().get('status') == 'success':
            results['dispatch'].append(elapsed)
            return True, elapsed
        else:
            results['errors'].append(f"Dispatch failed: {response.status_code}")
            return False, elapsed
    except Exception as e:
        results['errors'].append(f"Dispatch error: {str(e)}")
        return False, 0


def worker_thread(worker_id, total_requests):
    """Worker thread that runs load tests"""
    tests = [test_health_check, test_get_ambulances, test_predict_eta, test_dispatch]
    
    for i in range(total_requests):
        test = choice(tests)
        success, elapsed = test()
        
        # Print progress every 10 requests
        if (i + 1) % 10 == 0:
            print(f"  Worker {worker_id}: {i + 1}/{total_requests} requests completed")


def print_results():
    """Print formatted test results"""
    print("\n" + "="*70)
    print("                   LOAD TEST RESULTS")
    print("="*70)
    
    def stats_for(endpoint_name, times_list):
        if not times_list:
            return None
        
        return {
            'count': len(times_list),
            'min': min(times_list),
            'max': max(times_list),
            'mean': mean(times_list),
            'median': median(times_list),
            'stdev': stdev(times_list) if len(times_list) > 1 else 0
        }
    
    endpoints = {
        'GET /health': results['health'],
        'GET /ambulances/active': results['ambulances'],
        'POST /predict-eta': results['predict_eta'],
        'POST /dispatch': results['dispatch']
    }
    
    total_requests = sum(len(v) for v in results.values() if isinstance(v, list))
    
    for endpoint_name, times_list in endpoints.items():
        stats = stats_for(endpoint_name, times_list)
        if stats:
            print(f"\n{endpoint_name}")
            print(f"  Requests: {stats['count']}")
            print(f"  Response Time (ms):")
            print(f"    Min:     {stats['min']:.2f}")
            print(f"    Max:     {stats['max']:.2f}")
            print(f"    Mean:    {stats['mean']:.2f}")
            print(f"    Median:  {stats['median']:.2f}")
            print(f"    Stdev:   {stats['stdev']:.2f}")
    
    print(f"\n{'SUMMARY':-^70}")
    print(f"Total Requests:     {total_requests}")
    print(f"Total Errors:       {len(results['errors'])}")
    print(f"Error Rate:         {len(results['errors'])/max(total_requests, 1)*100:.2f}%")
    print(f"Total Time:         {results['total_time']:.2f}s")
    print(f"Throughput:         {total_requests/max(results['total_time'], 1):.2f} req/s")
    
    if results['errors']:
        print(f"\nERRORS (first 10):")
        for error in results['errors'][:10]:
            print(f"  - {error}")
    
    print("="*70)


def run_load_test(num_workers=NUM_WORKERS, requests_per_worker=NUM_REQUESTS_PER_WORKER):
    """Run the load test with specified parameters"""
    print(f"\n🚀 Starting NaviRaksha Load Test")
    print(f"   URL:      {API_BASE_URL}")
    print(f"   Workers:  {num_workers}")
    print(f"   Req/Worker: {requests_per_worker}")
    print(f"   Total:    {num_workers * requests_per_worker} requests")
    print(f"\n⏳ Running...\n")
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for parallel requests
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for worker_id in range(num_workers):
            future = executor.submit(worker_thread, worker_id, requests_per_worker)
            futures.append(future)
        
        # Wait for all threads to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                results['errors'].append(f"Worker error: {str(e)}")
    
    results['total_time'] = time.time() - start_time
    
    # Print results
    print_results()
    
    # Save results to JSON
    with open('load_test_results.json', 'w') as f:
        export_results = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'url': API_BASE_URL,
                'workers': num_workers,
                'requests_per_worker': requests_per_worker
            },
            'results': {
                'health_check': {
                    'count': len(results['health']),
                    'avg_ms': mean(results['health']) if results['health'] else 0
                },
                'ambulances': {
                    'count': len(results['ambulances']),
                    'avg_ms': mean(results['ambulances']) if results['ambulances'] else 0
                },
                'predict_eta': {
                    'count': len(results['predict_eta']),
                    'avg_ms': mean(results['predict_eta']) if results['predict_eta'] else 0
                },
                'dispatch': {
                    'count': len(results['dispatch']),
                    'avg_ms': mean(results['dispatch']) if results['dispatch'] else 0
                },
                'total_requests': sum(len(v) for v in results.values() if isinstance(v, list)),
                'total_errors': len(results['errors']),
                'total_time_seconds': results['total_time'],
                'throughput_rps': sum(len(v) for v in results.values() if isinstance(v, list)) / max(results['total_time'], 1)
            }
        }
        json.dump(export_results, f, indent=2)
    
    print(f"\n✅ Results saved to load_test_results.json")


if __name__ == "__main__":
    # Parse command line arguments
    workers = NUM_WORKERS
    requests_per = NUM_REQUESTS_PER_WORKER
    
    if len(sys.argv) > 1:
        try:
            workers = int(sys.argv[1])
        except ValueError:
            print(f"Usage: python quick_load_test.py [workers] [requests_per_worker]")
            print(f"  workers: number of concurrent threads (default: {NUM_WORKERS})")
            print(f"  requests_per_worker: requests per thread (default: {NUM_REQUESTS_PER_WORKER})")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            requests_per = int(sys.argv[2])
        except ValueError:
            pass
    
    try:
        run_load_test(num_workers=workers, requests_per_worker=requests_per)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print_results()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)
