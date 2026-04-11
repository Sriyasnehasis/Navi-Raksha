#!/usr/bin/env python3
"""Test Flask routes are properly registered"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app

print("\n=== Flask Routes Debug ===\n")

# List all registered routes
print("Registered routes:")
for rule in app.url_map.iter_rules():
    if 'static' not in rule.rule:
        print(f"  {rule.rule}")

print(f"\nTotal routes: {len([r for r in app.url_map.iter_rules()])}")

# Test the app with test client
print("\n=== Testing with Flask Test Client ===\n")

with app.test_client() as client:
    # Test health endpoint  
    print("Testing GET /health...")
    response = client.get('/health')
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.get_json()}")
    
    # Test ambulances endpoint
    print("\nTesting GET /ambulances/active...")
    response = client.get('/ambulances/active')
    print(f"  Status: {response.status_code}")
    print(f"  Response keys: {response.get_json().keys() if response.status_code == 200 else response.get_json()}")

print("\n=== Debug Complete ===\n")
