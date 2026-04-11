# Frontend Integration Guide - Arisha

**For:** Connecting Streamlit app to Backend API  
**Date:** April 11, 2026  
**Status:** 🟢 Ready for Implementation

---

## Quick Start

### The Backend API is Ready! ✅

All 6 endpoints are now working and returning data. Your frontend can start calling them instead of using hardcoded mock data.

**API URL:** `http://localhost:8000`

---

## Step 1: Update Your Imports

In your Streamlit app files, add these imports:

```python
import requests
import streamlit as st
from datetime import datetime

# API endpoint
API_URL = "http://localhost:8000"

# Cache the requests to avoid too many API calls
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_ambulances():
    response = requests.get(f"{API_URL}/ambulances/active")
    return response.json()

@st.cache_data(ttl=60)
def get_incidents():
    response = requests.get(f"{API_URL}/incidents/active")
    return response.json()

@st.cache_data(ttl=60)
def get_hospitals():
    response = requests.get(f"{API_URL}/hospitals")
    return response.json()

def predict_eta(distance, hour, is_monsoon, ambulance_type, violations_zone):
    response = requests.post(
        f"{API_URL}/predict-eta",
        json={
            "distance": distance,
            "hour": hour,
            "is_monsoon": is_monsoon,
            "ambulance_type": ambulance_type,
            "violations_zone": violations_zone
        }
    )
    return response.json()

def dispatch_ambulance(lat, lon, incident_type, severity, distance):
    response = requests.post(
        f"{API_URL}/dispatch",
        json={
            "patient_lat": lat,
            "patient_lon": lon,
            "incident_type": incident_type,
            "severity": severity,
            "distance": distance,
            "hour": datetime.now().hour,
            "is_monsoon": False  # Get from weather API or parameter
        }
    )
    return response.json()
```

---

## Step 2: Update `citizen_tracker.py`

**Before (Hardcoded):**

```python
# Old way - mock data
eta_minutes = 8
hospitals = [
    {"name": "Apollo", "beds": 5, "lat": 19.08, "lon": 72.88},
    {"name": "Fortis", "beds": 10, "lat": 19.07, "lon": 72.87}
]
```

**After (API Calls):**

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("🏥 Citizen Tracker")

# Get current location from user
patient_lat = st.number_input("Patient Latitude", value=19.076)
patient_lon = st.number_input("Patient Longitude", value=72.877)
distance = st.slider("Distance to Hospital (km)", 0.1, 50.0, 5.0)

# Predict ETA
eta_response = requests.post(
    f"{API_URL}/predict-eta",
    json={
        "distance": distance,
        "hour": datetime.now().hour,
        "is_monsoon": False,
        "ambulance_type": 2,
        "violations_zone": 0
    }
)

if eta_response.status_code == 200:
    eta_data = eta_response.json()
    st.metric("📍 Estimated Time to Arrival", f"{eta_data['eta_minutes']:.1f} min")
else:
    st.error("Could not get ETA prediction")

# Get hospitals
hospitals_response = requests.get(f"{API_URL}/hospitals")
if hospitals_response.status_code == 200:
    hospitals_data = hospitals_response.json()
    st.subheader("🏥 Nearby Hospitals")

    for hospital in hospitals_data["hospitals"]:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**{hospital['name']}**")
        with col2:
            st.write(f"Beds: {hospital['beds_available']}")
        with col3:
            st.write(f"ETA: {hospital['eta_minutes']} min")
else:
    st.error("Could not get hospital list")
```

---

## Step 3: Update `dispatcher_dashboard.py`

**Before:**

```python
# Mock ambulances
ambulances = [
    {"id": "AMB001", "location": "Sector 5", "status": "Available"},
    {"id": "AMB002", "location": "Sector 7", "status": "En Route"}
]

incidents = [
    {"id": "INC001", "type": "Cardiac", "location": "Sector 5", "severity": "Critical"},
    {"id": "INC002", "type": "Trauma", "location": "Sector 7", "severity": "High"}
]
```

**After:**

```python
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("🚑 Dispatcher Dashboard")

# Get active ambulances
ambulance_response = requests.get(f"{API_URL}/ambulances/active")
if ambulance_response.status_code == 200:
    ambulance_data = ambulance_response.json()
    st.subheader(f"🚑 Active Ambulances ({ambulance_data['total']})")

    for ambulance in ambulance_data["ambulances"]:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{ambulance['id']}**")
        with col2:
            st.write(f"{ambulance['type']}")
        with col3:
            st.write(f"Status: {ambulance['status']}")
        with col4:
            st.write(f"Driver: {ambulance['driver']}")
else:
    st.error("Could not get ambulance list")

# Get active incidents
incident_response = requests.get(f"{API_URL}/incidents/active")
if incident_response.status_code == 200:
    incident_data = incident_response.json()
    st.subheader(f"🚨 Active Incidents ({incident_data['total']})")

    for incident in incident_data["incidents"]:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**{incident['id']}**")
        with col2:
            st.write(f"{incident['type']}")
        with col3:
            st.write(f"Severity: {incident['severity']}")
        with col4:
            st.write(f"Status: {incident['status']}")

    # Dispatch button
    if st.button("🚑 Dispatch New Ambulance"):
        dispatch_response = requests.post(
            f"{API_URL}/dispatch",
            json={
                "patient_lat": 19.076,
                "patient_lon": 72.877,
                "incident_type": "Cardiac",
                "severity": "Critical",
                "distance": 5.0,
                "hour": datetime.now().hour,
                "is_monsoon": False
            }
        )

        if dispatch_response.status_code == 200:
            dispatch_data = dispatch_response.json()
            st.success(f"✅ Dispatched {dispatch_data['ambulance_type']} ambulance")
            st.write(f"ETA: {dispatch_data['eta_minutes']} minutes")
        else:
            st.error("Dispatch failed")
else:
    st.error("Could not get incident list")
```

---

## Step 4: Update `simulation.py`

Add calls to backend for realistic data:

```python
import requests
import streamlit as st
from datetime import datetime

API_URL = "http://localhost:8000"

st.title("🎮 Simulation Engine")

# Get real ambulances for simulation
ambulances_response = requests.get(f"{API_URL}/ambulances/active")
if ambulances_response.status_code == 200:
    ambulances = ambulances_response.json()["ambulances"]
    st.write(f"Simulating with {len(ambulances)} real ambulances")

    # Simulate movement
    for ambulance in ambulances:
        st.write(f"{ambulance['id']}: {ambulance['status']}")

# Simulate new incident
if st.button("📍 Simulate New Incident"):
    # Dispatch to backend
    dispatch_response = requests.post(
        f"{API_URL}/dispatch",
        json={
            "patient_lat": 19.076,
            "patient_lon": 72.877,
            "incident_type": "Cardiac",
            "severity": "Critical",
            "distance": 5.0,
            "hour": datetime.now().hour,
            "is_monsoon": False
        }
    )

    if dispatch_response.status_code == 200:
        result = dispatch_response.json()
        st.json(result)
```

---

## Step 5: Error Handling

Always wrap API calls in try-except:

```python
import requests
import streamlit as st

API_URL = "http://localhost:8000"

try:
    response = requests.get(f"{API_URL}/ambulances/active", timeout=5)
    response.raise_for_status()  # Raise exception for bad status codes

    if response.status_code == 200:
        data = response.json()
        # Use data
    else:
        st.error(f"API returned status {response.status_code}")

except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to backend API. Is it running on localhost:8000?")
except requests.exceptions.Timeout:
    st.error("❌ API request timed out")
except requests.exceptions.JSONDecodeError:
    st.error("❌ Invalid JSON response from API")
except Exception as e:
    st.error(f"❌ Error: {e}")
```

---

## Step 6: Performance Tips

### 1. Cache Frequently Called Endpoints

```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_ambulances():
    return requests.get(f"{API_URL}/ambulances/active").json()
```

### 2. Use Conditional Rendering

```python
# Only update when needed
if st.checkbox("Refresh Hospital List"):
    hospitals = requests.get(f"{API_URL}/hospitals").json()
    st.json(hospitals)
```

### 3. Add Loading States

```python
with st.spinner("Fetching ambulances..."):
    ambulances = requests.get(f"{API_URL}/ambulances/active").json()
st.success("✅ Loaded")
```

---

## API Endpoint Reference

### Health Check

```bash
GET http://localhost:8000/health
```

Returns: `{"status": "healthy", "model_loaded": true, "scaler_loaded": true}`

### Get Ambulances

```bash
GET http://localhost:8000/ambulances/active
```

Returns: List of 5 ambulances with status, location, type

### Get Incidents

```bash
GET http://localhost:8000/incidents/active
```

Returns: List of 3 incidents with type, severity, status

### Get Hospitals

```bash
GET http://localhost:8000/hospitals
```

Returns: List of 4 hospitals with beds, location, ETA

### Predict ETA

```bash
POST http://localhost:8000/predict-eta
Body: {
    "distance": 5.0,
    "hour": 14,
    "is_monsoon": false,
    "ambulance_type": 2,
    "violations_zone": 0
}
```

Returns: `{"eta_minutes": 8.21, "confidence": 0.99, "status": "success"}`

### Dispatch Ambulance

```bash
POST http://localhost:8000/dispatch
Body: {
    "patient_lat": 19.075,
    "patient_lon": 72.87,
    "incident_type": "Cardiac",
    "severity": "Critical",
    "distance": 5.0,
    "hour": 14,
    "is_monsoon": false
}
```

Returns: Full dispatch result with ambulance ID, hospital, ETA

---

## Testing Checklist

- [ ] API is running on `http://localhost:8000`
- [ ] `/health` returns `status: "healthy"`
- [ ] `/ambulances/active` returns 5 ambulances
- [ ] `/incidents/active` returns 3 incidents
- [ ] `/hospitals` returns 4 hospitals
- [ ] `/predict-eta` returns ETA in 3-20 minute range
- [ ] `/dispatch` returns complete dispatch result
- [ ] Streamlit app loads without errors
- [ ] Ambulance list displays correctly
- [ ] Incident list displays correctly
- [ ] Hospital list displays correctly
- [ ] ETA predictions show reasonable values
- [ ] Error messages display gracefully

---

## Support

**Backend Owner:** Sriya  
**Questions?** Check:

1. `docs/API_CONTRACT.md` - Complete API specification
2. `modules/backend/README.md` - Backend documentation
3. `BACKEND_STATUS_APR11.md` - Current status

---

## Implementation Timeline

- **Apr 14:** First time connecting to API
- **Apr 15-17:** Full frontend integration
- **Apr 18:** Testing and debugging
- **Apr 19:** Submit final version
- **Apr 20:** Demo day!

---

Good luck with the integration! 🚀
