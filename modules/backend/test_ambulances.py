#!/usr/bin/env python3
"""DirectTest ambulances from database

"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import json

print("\n=== Testing Ambulances Endpoint ===\n")

with app.test_client() as client:
    print("GET / ambulances/active")
    response = client.get('/ambulances/active')
    print(f"Status: {response.status_code}")
    data = response.get_json()
    print(f"Response:\n{json.dumps(data, indent=2)}")
