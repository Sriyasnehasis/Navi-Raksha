#!/usr/bin/env python3
"""Performance benchmarking for NaviRaksha API

Measures response times, caching effectiveness, and overall throughput
"""

import time
import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))

from app import app

print("\n" + "="*70)
print("NaviRaksha API Performance Benchmark")
print("="*70 + "\n")

# Define tests
tests = [
    {"name": "Health Check", "method": "GET", "endpoint": "/health", "data": None},
    {"name": "Ambulances (Cached)", "method": "GET", "endpoint": "/ambulances/active", "data": None},
    {"name": "Incidents (Cached)", "method": "GET", "endpoint": "/incidents/active", "data": None},
    {"name": "Hospitals (Cached)", "method": "GET", "endpoint": "/hospitals", "data": None},
    {"name": "ETA Prediction", "method": "POST", "endpoint": "/predict-eta", 
     "data": {"distance": 5, "hour": 14, "is_monsoon": False, "ambulance_type": 2, "violations_zone": 0}},
    {"name": "Dispatch", "method": "POST", "endpoint": "/dispatch",
     "data": {"latitude": 19.076, "longitude": 72.877, "incident_type": "Cardiac", "severity": "CRITICAL", 
              "hour": 14, "is_monsoon": False, "distance": 5}},
]

print("Test 1: Single Request Response Times")
print("-" * 70)

results = {}
with app.test_client() as client:
    for test in tests:
        times = []
        
        # First request (cold cache)
        start = time.time()
        if test['method'] == 'GET':
            response = client.get(test['endpoint'])
        else:
            response = client.post(test['endpoint'], json=test['data'])
        cold_time = (time.time() - start) * 1000
        times.append(cold_time)
        
        # 4 more warm cache requests (if caching is enabled)
        for _ in range(4):
            start = time.time()
            if test['method'] == 'GET':
                response = client.get(test['endpoint'])
            else:
                response = client.post(test['endpoint'], json=test['data'])
            warm_time = (time.time() - start) * 1000
            times.append(warm_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        cache_benefit = ((cold_time - min_time) / cold_time * 100) if cold_time > 0 else 0
        
        results[test['name']] = {
            'cold': cold_time,
            'warm': min_time,
            'avg': avg_time,
            'max': max_time,
            'cache_benefit': cache_benefit,
            'status': response.status_code
        }
        
        print(f"{test['name']:<30} | Cold: {cold_time:7.2f}ms | Warm: {min_time:7.2f}ms | "
              f"Avg: {avg_time:7.2f}ms | Cache: {cache_benefit:5.1f}%")

print("\n" + "="*70)
print("Test 2: Cache Effectiveness Over Time")
print("-" * 70)
print("-" * 70)

cached_endpoints = [
    {"name": "Health Check", "endpoint": "/health", "timeout": 10},
    {"name": "Ambulances", "endpoint": "/ambulances/active", "timeout": 30},
    {"name": "Incidents", "endpoint": "/incidents/active", "timeout": 20},
    {"name": "Hospitals", "endpoint": "/hospitals", "timeout": 60},
]

print(f"{'Endpoint':<20} | {'Cache Timeout':<15} | {'Cold Time':<10} | {'Warm Time':<10} | "
      f"{'Speedup':<10}")
print("-" * 70)

with app.test_client() as client:
    for test in cached_endpoints:
        # Cold request
        start = time.time()
        response = client.get(test['endpoint'])
        cold_time = (time.time() - start) * 1000
        
        # Warm request (cached)
        start = time.time()
        response = client.get(test['endpoint'])
        warm_time = (time.time() - start) * 1000
        
        speedup = cold_time / warm_time if warm_time > 0 else 0
        
        print(f"{test['name']:<20} | {test['timeout']}s           | "
              f"{cold_time:8.2f}ms | {warm_time:8.2f}ms | {speedup:8.1f}x")

print("\n" + "="*70)
print("Summary Statistics")
print("="*70)

print("\nOverall Performance:")
total_cold_time = sum(r['cold'] for r in results.values())
total_avg_time = sum(r['avg'] for r in results.values())
avg_cache_benefit = sum(r['cache_benefit'] for r in results.values()) / len(results)

print(f"Total queries tested: {len(results)}")
print(f"Total cold time: {total_cold_time:.2f}ms")
print(f"Total average time: {total_avg_time:.2f}ms")
print(f"Average cache benefit: {avg_cache_benefit:.1f}%")
print(f"Concurrent throughput: {throughput:.1f} req/s")

print("\nOptimizations Applied:")
print("  ✓ Database indexing on frequently queried columns")
print("  ✓ SQLAlchemy connection pooling (StaticPool)")
print("  ✓ Response caching (30s ambulances, 20s incidents, 60s hospitals)")
print("  ✓ Query optimization in service layer")

print("\n" + "="*70 + "\n")
