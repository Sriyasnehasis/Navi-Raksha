# NaviRaksha API Contract

**For:** Turya's Routing Module Integration  
**Last Updated:** April 11, 2026  
**API Version:** 1.0  
**Status:** ✅ Ready for Integration

---

## Quick Reference

```
Base URL: http://localhost:8000

Endpoints:
1. GET  /health                    → Health check
2. POST /predict-eta               → ETA prediction (5 features)
3. GET  /ambulances/active         → Active ambulance list
4. GET  /incidents/active          → Active incident list
5. GET  /hospitals                 → Hospital list with beds
6. POST /dispatch                  → Full dispatch workflow
```

---

## Routing Module Integration Points

### 1. ETA Prediction (Primary)

**Used by:** A\* Router (for path cost calculation)

```python
# Endpoint
POST http://localhost:8000/predict-eta

# Input Parameters:
{
    "distance": float,           # km (0.1-50.0)
    "hour": int,                 # 0-23
    "is_monsoon": bool,          # weather condition
    "ambulance_type": int,       # 1=ALS, 2=BLS, 3=Advanced
    "violations_zone": int       # traffic violations on route (0+)
}

# Output:
{
    "eta_minutes": int,          # Predicted ETA (3-20 min range)
    "eta_range": string,         # e.g., "5-10 minutes"
    "confidence": float,         # 0.0-1.0 confidence score
    "model": string,             # "Random Forest"
    "timestamp": ISO8601         # Response timestamp
}

# Python Example:
import requests

def predict_eta(distance, hour, is_monsoon, ambulance_type, violations_zone):
    response = requests.post(
        "http://localhost:8000/predict-eta",
        json={
            "distance": distance,
            "hour": hour,
            "is_monsoon": is_monsoon,
            "ambulance_type": ambulance_type,
            "violations_zone": violations_zone
        }
    )
    return response.json()["eta_minutes"]

# Usage:
eta = predict_eta(distance=5.0, hour=14, is_monsoon=False,
                   ambulance_type=2, violations_zone=0)
print(f"Predicted ETA: {eta} minutes")
```

---

### 2. Active Ambulances (For Dispatch Classifier)

**Used by:** Dispatch Classifier (to select closest ALS/BLS)

```python
# Endpoint
GET http://localhost:8000/ambulances/active

# Input: None (query parameters optional in future)

# Output:
{
    "total": int,
    "ambulances": [
        {
            "id": string,               # e.g., "AMB001"
            "type": string,             # "ALS" or "BLS"
            "status": string,           # "available", "responding", "transporting"
            "location": {
                "lat": float,
                "lon": float
            },
            "crew_size": int            # 1-2
        },
        ...
    ],
    "timestamp": ISO8601
}

# Python Example:
import requests

def get_available_ambulances(ambulance_type):
    response = requests.get("http://localhost:8000/ambulances/active")
    ambulances = response.json()["ambulances"]

    # Filter by type
    available = [a for a in ambulances
                 if a["type"] == ambulance_type and a["status"] == "available"]
    return available

# Usage:
als_ambulances = get_available_ambulances("ALS")
closest = min(als_ambulances, key=lambda a: distance_between(a["location"], patient_loc))
```

---

### 3. Hospital Data (For Hospital Ranker)

**Used by:** Hospital Ranker (to select best hospital)

```python
# Endpoint
GET http://localhost:8000/hospitals

# Input: None

# Output:
{
    "total": int,
    "hospitals": [
        {
            "id": string,               # e.g., "HOSP001"
            "name": string,             # Hospital name
            "location": {
                "lat": float,
                "lon": float
            },
            "beds_available": {
                "emergency": int,       # Emergency beds
                "icu": int,             # ICU beds
                "total": int            # Total available beds
            },
            "distance_from_patient": float,  # km
            "eta_minutes": int          # Calculated ETA to hospital
        },
        ...
    ],
    "timestamp": ISO8601
}

# Python Example:
import requests

def find_best_hospital(patient_lat, patient_lon, severity):
    response = requests.get("http://localhost:8000/hospitals")
    hospitals = response.json()["hospitals"]

    # Score hospitals based on ETA and availability
    scored = []
    for h in hospitals:
        score = h["eta_minutes"] + (1.0 / h["beds_available"]["total"])
        scored.append((score, h))

    best = min(scored, key=lambda x: x[0])
    return best[1]
```

---

### 4. Dispatch Workflow (Complete Emergency Handler)

**Used by:** Full integration (calls all above internally)

```python
# Endpoint
POST http://localhost:8000/dispatch

# Input:
{
    "patient_lat": float,          # Patient location latitude
    "patient_lon": float,          # Patient location longitude
    "incident_type": string,       # e.g., "Cardiac", "Trauma", "Respiratory"
    "severity": string,            # "Critical", "Severe", "Moderate", "Minor"
    "distance": float,             # Distance in km
    "hour": int,                   # Hour of day (0-23)
    "is_monsoon": bool             # Weather condition
}

# Output:
{
    "dispatch_id": string,         # Unique dispatch ID
    "ambulance_type": string,      # "ALS", "BLS", or "Advanced"
    "ambulance_id": string,        # Selected ambulance ID
    "eta_minutes": int,            # Predicted ETA to patient
    "hospital": {
        "id": string,
        "name": string,
        "eta_minutes": int,        # ETA from ambulance to hospital
        "beds_available": int
    },
    "status": string,              # "dispatched"
    "timestamp": ISO8601
}

# Python Example (Full Workflow):
import requests

def handle_emergency(patient_lat, patient_lon, incident_type, severity, distance):
    response = requests.post(
        "http://localhost:8000/dispatch",
        json={
            "patient_lat": patient_lat,
            "patient_lon": patient_lon,
            "incident_type": incident_type,
            "severity": severity,
            "distance": distance,
            "hour": 14,
            "is_monsoon": False
        }
    )

    result = response.json()
    print(f"Ambulance: {result['ambulance_id']} ({result['ambulance_type']})")
    print(f"ETA to patient: {result['eta_minutes']} minutes")
    print(f"Hospital: {result['hospital']['name']}")
    print(f"ETA to hospital: {result['hospital']['eta_minutes']} minutes")

    return result
```

---

## Feature Request Format

**For ETA Prediction, use exactly these 5 features in this order:**

| Feature             | Type  | Range      | Example | Notes                        |
| ------------------- | ----- | ---------- | ------- | ---------------------------- |
| **distance**        | float | 0.1-50.0   | 5.0     | km from ambulance to patient |
| **hour**            | int   | 0-23       | 14      | Hour of day (military time)  |
| **is_monsoon**      | bool  | True/False | False   | Monsoon season indicator     |
| **ambulance_type**  | int   | 1,2,3      | 2       | 1=ALS, 2=BLS, 3=Advanced     |
| **violations_zone** | int   | 0+         | 0       | Traffic violations count     |

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "Error type",
  "details": "Detailed explanation",
  "timestamp": "ISO8601 timestamp"
}
```

**Common HTTP Status Codes:**

- `200`: Success
- `400`: Bad request (missing/invalid parameters)
- `404`: Endpoint not found
- `500`: Server error (model loading failure, etc.)

---

## Direct Model Access (Alternative)

If API adds latency, use models directly:

```python
import pickle
import numpy as np

# Load models
with open("models/trained/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

with open("models/trained/rf_features.pkl", "rb") as f:
    scaler = pickle.load(f)

# Prepare features (must be in exact order)
features = np.array([[distance, hour, is_monsoon, ambulance_type, violations_zone]])

# Scale features
scaled = scaler.transform(features)

# Predict
eta_minutes = rf_model.predict(scaled)[0]
eta_minutes = max(3, min(20, eta_minutes))  # Clamp to 3-20 range
```

---

## Data Types & Formats

### Timestamps

- Format: ISO 8601 (e.g., `2026-04-11T14:30:45.123456`)
- Timezone: UTC
- Use `.isoformat()` in Python

### Coordinates

- Format: `{"lat": float, "lon": float}`
- Precision: 4 decimal places (≈100 meters)
- Bounds: Mumbai area (18.5-19.5, 72.5-73.5)

### IDs

- Ambulances: `AMB001`, `AMB002`, etc.
- Hospitals: `HOSP001`, `HOSP002`, etc.
- Incidents: `INC001`, `INC002`, etc.
- Dispatches: `DISP001`, `DISP002`, etc.

---

## Severity → Ambulance Type Mapping

```
Severity Level → Ambulance Type → Crew Size → Equipment
Critical       → ALS (1)        → 2         → Defibrillator, Cardiac monitoring
Severe         → BLS (2)        → 1-2       → Basic life support
Moderate       → BLS (2)        → 1         → Basic supplies
Minor          → Advanced (3)   → 1         → First aid supplies
```

---

## Performance Notes

- **Response Time:** <500ms per endpoint
- **Concurrent Requests:** Supports up to 100 concurrent
- **Rate Limiting:** None (add if needed)
- **Caching:** None (all data is live)

---

## Testing Endpoints Locally

```bash
# Start API
python modules/backend/app.py

# In another terminal, test each endpoint:

# 1. Health check
curl http://localhost:8000/health

# 2. ETA prediction
curl -X POST http://localhost:8000/predict-eta \
  -H "Content-Type: application/json" \
  -d '{"distance": 5.0, "hour": 14, "is_monsoon": false, "ambulance_type": 2, "violations_zone": 0}'

# 3. Active ambulances
curl http://localhost:8000/ambulances/active

# 4. Active incidents
curl http://localhost:8000/incidents/active

# 5. Hospitals
curl http://localhost:8000/hospitals

# 6. Dispatch
curl -X POST http://localhost:8000/dispatch \
  -H "Content-Type: application/json" \
  -d '{"patient_lat": 19.075, "patient_lon": 72.87, "incident_type": "Cardiac", "severity": "Critical", "distance": 5.0, "hour": 14, "is_monsoon": false}'

# Or run full test suite
python modules/backend/test_api.py
```

---

## Python Client Library (Recommended)

Create `modules/routing/api_client.py`:

```python
import requests
from typing import Dict, List, Tuple

class NaviRakshaAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def predict_eta(self, distance: float, hour: int, is_monsoon: bool,
                    ambulance_type: int, violations_zone: int) -> int:
        """Predict ETA in minutes"""
        response = requests.post(
            f"{self.base_url}/predict-eta",
            json={
                "distance": distance,
                "hour": hour,
                "is_monsoon": is_monsoon,
                "ambulance_type": ambulance_type,
                "violations_zone": violations_zone
            }
        )
        return response.json()["eta_minutes"]

    def get_ambulances(self) -> List[Dict]:
        """Get active ambulances"""
        response = requests.get(f"{self.base_url}/ambulances/active")
        return response.json()["ambulances"]

    def get_hospitals(self) -> List[Dict]:
        """Get hospitals with bed availability"""
        response = requests.get(f"{self.base_url}/hospitals")
        return response.json()["hospitals"]

    def dispatch(self, patient_lat: float, patient_lon: float,
                incident_type: str, severity: str, distance: float,
                hour: int, is_monsoon: bool) -> Dict:
        """Handle emergency dispatch"""
        response = requests.post(
            f"{self.base_url}/dispatch",
            json={
                "patient_lat": patient_lat,
                "patient_lon": patient_lon,
                "incident_type": incident_type,
                "severity": severity,
                "distance": distance,
                "hour": hour,
                "is_monsoon": is_monsoon
            }
        )
        return response.json()

# Usage in routing module:
api = NaviRakshaAPI()
eta = api.predict_eta(5.0, 14, False, 2, 0)
ambulances = api.get_ambulances()
hospitals = api.get_hospitals()
dispatch_result = api.dispatch(19.075, 72.87, "Cardiac", "Critical", 5.0, 14, False)
```

---

## Integration Checklist for Turya

- [ ] API is running on `http://localhost:8000`
- [ ] `/health` returns `status: "healthy"`
- [ ] `/predict-eta` works with your route feature values
- [ ] `/ambulances/active` returns list of available ambulances
- [ ] `/hospitals` returns hospital data
- [ ] `/dispatch` accepts your severity classification
- [ ] Response times are acceptable (<500ms)
- [ ] Error handling is implemented in routing module
- [ ] Feature values are within valid ranges
- [ ] Timestamps are correctly parsed

---

## Questions?

1. Check [Backend README](README.md) for full documentation
2. Run `modules/backend/test_api.py` to verify all endpoints
3. Review [Team Documentation](../../docs/) for context
4. Contact Sriya for integration issues

---

**API Status:** ✅ Production Ready  
**Last Verified:** April 11, 2026  
**Team:** NaviRaksha Project
