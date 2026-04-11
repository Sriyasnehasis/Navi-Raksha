# NaviRaksha Backend API

Complete Flask-based REST API for the NaviRaksha Emergency Medical Services platform. Serves ETA predictions powered by trained Random Forest model and manages dispatch, ambulance, and hospital data.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- All dependencies installed from `requirements.txt`
- Models trained and saved in `models/trained/`
  - `rf_model.pkl` (Random Forest model)
  - `rf_features.pkl` (Feature scaler)

### 2. Start the API

```bash
# Navigate to project root
cd c:\Users\sriya\Desktop\Learner\navi-raksha

# Start Flask server
python modules/backend/app.py
```

**Expected output:**

```
⚙️  Starting NaviRaksha Backend Server...
📊 Loading Random Forest model from: models/trained/rf_model.pkl
📊 Loading feature scaler from: models/trained/rf_features.pkl
✅ Models loaded successfully!
🚀 Starting Flask server on http://0.0.0.0:8000
   Visit http://localhost:8000/health to verify
```

The server will run on `http://localhost:8000`

### 3. Test the API

```bash
# In another terminal
python modules/backend/test_api.py
```

This will run all 6 endpoint tests and verify the API is working correctly.

---

## 📋 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

Check if the API and models are running correctly.

**Request:**

```bash
curl http://localhost:8000/health
```

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "scaler_loaded": true,
  "timestamp": "2026-04-11T14:30:45.123456",
  "version": "1.0.0"
}
```

---

### 2. ETA Prediction

**Endpoint:** `POST /predict-eta`

Predict emergency ambulance arrival time using the trained Random Forest model.

**Request:**

```bash
curl -X POST http://localhost:8000/predict-eta \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 5.0,
    "hour": 14,
    "is_monsoon": false,
    "ambulance_type": 2,
    "violations_zone": 0
  }'
```

**Parameters:**

- `distance` (float): Distance to patient in km (0.1 - 50.0)
- `hour` (int): Hour of day (0-23)
- `is_monsoon` (bool): Whether it's monsoon season
- `ambulance_type` (int): 1=ALS, 2=BLS, 3=Advanced
- `violations_zone` (int): Number of traffic violations in route

**Response:**

```json
{
  "eta_minutes": 8,
  "eta_range": "5-10 minutes",
  "confidence": 0.87,
  "model": "Random Forest",
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

**ETA Range:** Clamped between 3-20 minutes for safety

---

### 3. Active Ambulances

**Endpoint:** `GET /ambulances/active`

Get list of all active ambulances and their status.

**Request:**

```bash
curl http://localhost:8000/ambulances/active
```

**Response:**

```json
{
  "total": 5,
  "ambulances": [
    {
      "id": "AMB001",
      "type": "ALS",
      "status": "available",
      "location": {
        "lat": 19.076,
        "lon": 72.8777
      },
      "crew_size": 2
    },
    {
      "id": "AMB002",
      "type": "BLS",
      "status": "responding",
      "location": {
        "lat": 19.082,
        "lon": 72.89
      },
      "crew_size": 1
    }
  ],
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

---

### 4. Active Incidents

**Endpoint:** `GET /incidents/active`

Get list of all active emergency incidents.

**Request:**

```bash
curl http://localhost:8000/incidents/active
```

**Response:**

```json
{
  "total": 3,
  "incidents": [
    {
      "id": "INC001",
      "incident_type": "Cardiac",
      "severity": "Critical",
      "location": {
        "lat": 19.075,
        "lon": 72.87
      },
      "timestamp_reported": "2026-04-11T14:20:00",
      "status": "dispatched"
    },
    {
      "id": "INC002",
      "incident_type": "Trauma",
      "severity": "Severe",
      "location": {
        "lat": 19.09,
        "lon": 72.9
      },
      "timestamp_reported": "2026-04-11T14:15:00",
      "status": "en_route"
    }
  ],
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

---

### 5. Hospitals List

**Endpoint:** `GET /hospitals`

Get list of all hospitals with bed availability.

**Request:**

```bash
curl http://localhost:8000/hospitals
```

**Response:**

```json
{
  "total": 4,
  "hospitals": [
    {
      "id": "HOSP001",
      "name": "Apollo Hospital",
      "location": {
        "lat": 19.08,
        "lon": 72.88
      },
      "beds_available": {
        "emergency": 8,
        "icu": 3,
        "total": 11
      },
      "distance_from_patient": 2.5,
      "eta_minutes": 5
    }
  ],
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

---

### 6. Emergency Dispatch

**Endpoint:** `POST /dispatch`

Comprehensive dispatch endpoint that handles emergency workflow:

1. Classifies severity to determine ambulance type
2. Predicts ETA using RF model
3. Finds best hospital based on ETA + availability

**Request:**

```bash
curl -X POST http://localhost:8000/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "patient_lat": 19.0750,
    "patient_lon": 72.8700,
    "incident_type": "Cardiac",
    "severity": "Critical",
    "distance": 5.0,
    "hour": 14,
    "is_monsoon": false
  }'
```

**Parameters:**

- `patient_lat` (float): Patient latitude
- `patient_lon` (float): Patient longitude
- `incident_type` (string): Type of incident (e.g., "Cardiac", "Trauma", "Respiratory")
- `severity` (string): Severity level ("Critical", "Severe", "Moderate", "Minor")
- `distance` (float): Distance to patient in km
- `hour` (int): Hour of day (0-23)
- `is_monsoon` (bool): Whether it's monsoon season

**Response:**

```json
{
  "dispatch_id": "DISP001",
  "ambulance_type": "ALS",
  "ambulance_id": "AMB001",
  "eta_minutes": 8,
  "hospital": {
    "id": "HOSP001",
    "name": "Apollo Hospital",
    "eta_minutes": 13,
    "beds_available": 11
  },
  "status": "dispatched",
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

---

## 🔗 Frontend Integration

### Connecting Arisha's Frontend

The frontend (`ui/` folder) needs to be updated to call these endpoints instead of using hardcoded mock data.

#### Example: Updating `citizen_tracker.py`

**Before (hardcoded):**

```python
eta_minutes = 8  # hardcoded
hospitals = [
    {"name": "Apollo", "beds": 5},
    {"name": "Lilavati", "beds": 3}
]
```

**After (API calls):**

```python
import requests

API_URL = "http://localhost:8000"

# Get ETA prediction
response = requests.post(
    f"{API_URL}/predict-eta",
    json={
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False,
        "ambulance_type": 2,
        "violations_zone": 0
    }
)
eta_minutes = response.json()["eta_minutes"]

# Get hospitals
response = requests.get(f"{API_URL}/hospitals")
hospitals = response.json()["hospitals"]
```

#### Example: Updating `dispatcher_dashboard.py`

```python
# Get active ambulances
response = requests.get(f"{API_URL}/ambulances/active")
ambulances = response.json()["ambulances"]

# Get active incidents
response = requests.get(f"{API_URL}/incidents/active")
incidents = response.json()["incidents"]

# Dispatch new incident
response = requests.post(
    f"{API_URL}/dispatch",
    json={
        "patient_lat": 19.075,
        "patient_lon": 72.87,
        "incident_type": "Cardiac",
        "severity": "Critical",
        "distance": 5.0,
        "hour": 14,
        "is_monsoon": False
    }
)
dispatch_result = response.json()
```

---

## 🔧 Configuration

### Using Environment Variables

1. Copy `.env.example` to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Update values as needed in `.env`

3. The app will automatically load these settings

### Key Configurations

- **API_PORT**: Change server port (default: 8000)
- **FLASK_DEBUG**: Enable/disable debug mode
- **RF_MODEL_PATH**: Path to trained RF model
- **MIN_ETA_MINUTES**: Minimum ETA prediction (default: 3)
- **MAX_ETA_MINUTES**: Maximum ETA prediction (default: 20)

---

## 📊 Model Information

### Random Forest Model

- **File:** `models/trained/rf_model.pkl`
- **Features:** 5 (distance, hour, is_monsoon, ambulance_type, violations_zone)
- **Training MAE:** 0.0662 minutes (≈ 3.96 seconds error)
- **Target:** ETA in minutes (3-20 minute range)

### Feature Scaler

- **File:** `models/trained/rf_features.pkl`
- **Type:** StandardScaler
- **Used for:** Normalizing input features before prediction

---

## 🚨 Error Handling

The API returns appropriate HTTP status codes and error messages:

### Common Errors

**400 - Bad Request**

```json
{
  "error": "Invalid request data",
  "details": "Missing required field: distance",
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

**404 - Not Found**

```json
{
  "error": "Endpoint not found",
  "available_endpoints": ["/health", "/predict-eta", "/ambulances/active", ...]
}
```

**500 - Server Error**

```json
{
  "error": "Internal server error",
  "message": "Failed to load model",
  "timestamp": "2026-04-11T14:30:45.123456"
}
```

---

## 📈 Logging

All API requests and responses are logged to `navi_backend.log`:

```
2026-04-11 14:30:45,123 - navi_backend - INFO - Starting NaviRaksha Backend Server...
2026-04-11 14:30:45,234 - navi_backend - INFO - Models loaded successfully!
2026-04-11 14:30:52,145 - navi_backend - INFO - POST /predict-eta - predictions: [8]
2026-04-11 14:31:00,456 - navi_backend - INFO - GET /ambulances/active - returned 5 ambulances
```

View logs:

```bash
tail -f navi_backend.log
```

---

## 🔄 Integration with Routing Module (Turya)

The routing module can use the backend API in two ways:

### Option 1: Direct API Calls

```python
import requests

response = requests.post("http://localhost:8000/predict-eta", json={...})
eta = response.json()["eta_minutes"]
```

### Option 2: Direct Model Access (for lower latency)

```python
import pickle

with open("models/trained/rf_model.pkl", "rb") as f:
    model = pickle.load(f)

eta = model.predict([[distance, hour, is_monsoon, ambulance_type, violations_zone]])[0]
```

---

## ✅ Testing Checklist

- [ ] Backend server starts without errors
- [ ] `/health` endpoint returns `status: "healthy"`
- [ ] `/predict-eta` returns ETA between 3-20 minutes
- [ ] `/ambulances/active` returns list of ambulances
- [ ] `/incidents/active` returns list of incidents
- [ ] `/hospitals` returns list with bed availability
- [ ] `/dispatch` creates dispatch with correct ambulance type
- [ ] Frontend can call endpoints without CORS errors
- [ ] All responses include timestamps
- [ ] Error handling returns appropriate status codes

---

## 📚 Next Steps

1. **Week Apr 14-15:** Test API locally
2. **Week Apr 15-17:** Arisha connects frontend to API endpoints
3. **Week Apr 18:** Sriya creates API documentation for Turya's routing module
4. **Week Apr 19:** Full end-to-end testing
5. **Week Apr 20:** Integration with routing module

---

## 🆘 Troubleshooting

**API won't start:**

```
ModuleNotFoundError: No module named 'flask'
→ Solution: pip install -r requirements.txt
```

**Model loading fails:**

```
FileNotFoundError: rf_model.pkl not found
→ Solution: Verify models are in models/trained/ directory
```

**CORS errors in frontend:**

```
Access-Control-Allow-Origin header missing
→ Solution: Already enabled in app.py, verify frontend URL is allowed
```

**Frontend can't connect:**

```
Connection refused on localhost:8000
→ Solution: Verify API is running and port 8000 is not blocked
```

---

## 📞 Support

For questions or issues:

1. Check logs in `navi_backend.log`
2. Review this README
3. Test endpoints with `test_api.py`
4. Check team documentation in `docs/`

---

**Status:** ✅ Ready for production with mock data
**Last Updated:** April 11, 2026
**Team:** NaviRaksha Project
