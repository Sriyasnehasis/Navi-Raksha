# API Load Testing & Documentation Guide

## Overview

This directory contains complete API documentation and load testing tools for NaviRaksha Backend API.

### Contents

1. **Swagger API Documentation** (`../docs/swagger.yaml`)
   - Complete OpenAPI 3.0.0 specification
   - 24 endpoints fully documented
   - Request/response schemas
   - HTML preview available

2. **Load Testing Tools**
   - `load_test.py` - Advanced load testing with Locust framework
   - `quick_load_test.py` - Simple Python-based load testing (no dependencies)

---

## API Documentation

### View Swagger Documentation

#### Option 1: Online Swagger Editor

1. Go to https://editor.swagger.io/
2. Paste the contents of `../docs/swagger.yaml`
3. View interactive API documentation

#### Option 2: Local Swagger UI (with Docker)

```bash
docker run -p 80:8080 -e SWAGGER_JSON=/app/swagger.yaml -v $(pwd)/docs/swagger.yaml:/app/swagger.yaml swaggerapi/swagger-ui
```

Then visit: http://localhost/

#### Option 3: Read YAML Directly

```bash
cat ../docs/swagger.yaml
```

### API Endpoints Summary

| Category           | Count  | Key Endpoints                                                             |
| ------------------ | ------ | ------------------------------------------------------------------------- |
| Health & Info      | 1      | `/health`                                                                 |
| ETA Prediction     | 3      | `/predict-eta`, `/predict-eta/by-model`, `/models/comparison`             |
| Operations         | 3      | `/ambulances/active`, `/incidents/active`, `/hospitals`                   |
| Dispatch           | 1      | `/dispatch`                                                               |
| Admin - DB         | 4      | `/admin/db/init`, `/admin/db/seed`, `/admin/db/reset`, `/admin/db/status` |
| Admin - Ambulances | 4      | `POST`, `GET`, `PUT`, `DELETE`                                            |
| Admin - Incidents  | 4      | `POST`, `GET`, `PUT`, `DELETE`                                            |
| Admin - Hospitals  | 4      | `POST`, `GET`, `PUT`, `DELETE`                                            |
| **TOTAL**          | **24** | -                                                                         |

---

## Load Testing Guide

### Prerequisites

Before running any load tests:

1. **Start Backend API**

```bash
cd modules/backend
python app.py
# API should be running on http://localhost:8000
```

2. **Database should be initialized**

```bash
# If not auto-initialized, seed manually:
curl -X POST http://localhost:8000/admin/db/seed
```

### Option 1: Quick Load Test (Recommended for Quick Checks)

Simple Python-based testing - **no additional dependencies needed**

#### Install Dependencies (Optional - uses only requests)

```bash
pip install requests
```

#### Run Tests

**Light Load (50 concurrent requests):**

```bash
python tests/quick_load_test.py 10 5
# 10 workers × 5 requests = 50 total
```

**Medium Load (500 concurrent requests):**

```bash
python tests/quick_load_test.py 50 10
# 50 workers × 10 requests = 500 total
```

**Heavy Load (1000+ concurrent requests):**

```bash
python tests/quick_load_test.py 100 50
# 100 workers × 50 requests = 5000 total
```

#### Results Output

- Console summary with response times (min, max, mean, median, stdev)
- Error tracking and reporting
- JSON results saved to `load_test_results.json`
- Throughput calculation (requests/second)

**Example Output:**

```
GET /predict-eta
  Requests: 500
  Response Time (ms):
    Min:     145.23
    Max:     892.15
    Mean:    342.56
    Median:  315.42
    Stdev:   178.92

SUMMARY
Total Requests:     1000
Total Errors:       0
Error Rate:         0.00%
Total Time:         25.43s
Throughput:         39.32 req/s
```

---

### Option 2: Advanced Load Test with Locust

Professional-grade distributed load testing framework

#### Install Locust

```bash
pip install locust
```

#### Run Locust Tests

**Interactive Web UI (Recommended for first-time):**

```bash
locust -f tests/load_test.py --host=http://localhost:8000
# Opens web UI at http://localhost:8089
# Configure users, spawn rate, and watch real-time charts
```

**Headless - Light (100 users):**

```bash
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 100 -r 10 --run-time 2m --headless
```

**Headless - Medium (500 users, 10 minutes):**

```bash
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 500 -r 50 --run-time 10m --headless
```

**Headless - Heavy (1000 users, 5 minutes):**

```bash
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 1000 -r 100 --run-time 5m --headless
```

**Export Results to CSV:**

```bash
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 500 -r 50 --run-time 5m --headless --csv=results
# Creates: results_stats.csv, results_stats_history.csv, results_failures.csv
```

#### Locust Features

- **Multiple User Types:**
  - `NaviRakshaUser` - Simulates regular users with realistic task distribution
  - `AdminUser` - Simulates admin operations (CRUD)

- **Task Distribution:**
  - 5× Health checks (lightweight)
  - 3× Ambulance/Incident/Hospital fetches
  - 10× ETA predictions
  - 8× Model-specific ETA predictions
  - 15× Emergency dispatch (main workload)
  - 2× Model comparison
  - 1× Database status checks

- **Real-time Monitoring:**
  - Response time charts
  - Throughput graphs
  - Failure rate tracking
  - Worker and request count visualization

---

## Performance Benchmarking

### Expected Response Times

| Endpoint                | Expected (ms) | Tolerance |
| ----------------------- | ------------- | --------- |
| `/health`               | 10-50         | <100      |
| `/predict-eta`          | 100-300       | <500      |
| `/predict-eta/by-model` | 150-400       | <600      |
| `/dispatch`             | 200-800       | <1200     |
| `/ambulances/active`    | 50-200        | <300      |
| `/hospitals`            | 50-200        | <300      |

### Success Criteria

✅ **PASS if:**

- All endpoints respond within tolerance
- Error rate < 1%
- Throughput > 30 req/s (for 500 users)
- No connection timeouts
- Database remains responsive

❌ **FAIL if:**

- Response time consistently > tolerance
- Error rate > 5%
- Throughput < 10 req/s
- More than 5% timeout errors
- Memory usage grows unbounded

---

## Load Test Scenarios

### Scenario 1: Rush Hour (Morning)

```bash
# Spike in ambulance requests (7-9 AM)
# 500-1000 concurrent users
python tests/quick_load_test.py 100 20
```

### Scenario 2: Peak Load (All Day)

```bash
# Sustained load throughout day
# 1000 concurrent users for extended period
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 1000 -r 100 --run-time 30m --headless
```

### Scenario 3: Dispatch Burst

```bash
# High dispatch requests only
# Custom test - modify quick_load_test.py to only run test_dispatch()
python tests/quick_load_test.py 200 10
```

### Scenario 4: Sustained Stress

```bash
# Long-running stability test (1 hour)
locust -f tests/load_test.py --host=http://localhost:8000 \
  -u 500 -r 50 --run-time 1h --headless --csv=stress_results
```

---

## Troubleshooting

### Issue: Connection Refused

```
Error: Failed to connect to http://localhost:8000
```

**Solution:** Start the backend API first

```bash
cd modules/backend
python app.py
```

### Issue: Timeout Errors

```
Error: Request timeout exceeded
```

**Solutions:**

1. Reduce concurrent users: `python tests/quick_load_test.py 10 5`
2. Increase timeout in script (modify `TIMEOUT = 30`)
3. Check CPU usage: `top` or Task Manager
4. Restart backend: `pkill -f "python app.py"`

### Issue: Database Locked

```
Error: database is locked
```

**Solution:**

1. Increase SQLite pool size in app.py
2. Consider migrating to PostgreSQL for production
3. Reduce concurrent connections

### Issue: Out of Memory

```
Error: MemoryError
```

**Solutions:**

1. Reduce workers: `python tests/quick_load_test.py 20 5`
2. Monitor memory: Add `import psutil` and track in script
3. Increase system RAM or VM memory allocation

---

## Performance Optimization Tips

### Backend Optimizations

1. **Enable Response Caching**
   - Already configured with `@cache.cached(timeout=10)`
   - Add caching to frequently used endpoints

2. **Database Indexing**
   - Indexes already in place on:
     - `ambulance.id`, `ambulance.status`
     - `incident.id`, `incident.status`
     - `hospital.id`, `hospital.is_active`
     - `dispatch.incident_id`, `dispatch.ambulance_id`

3. **Connection Pooling**
   - SQLite uses StaticPool (good for dev)
   - For production, switch to PostgreSQL with full pooling

4. **Model Loading**
   - Models loaded at startup (not per-request)
   - Graph pre-loaded for A\* routing

### Load Testing Optimizations

1. **Use Quick Load Test for Iteration**
   - Faster feedback loop
   - No UI overhead

2. **Use Locust for Final Validation**
   - Better statistics
   - Real distributed load simulation

3. **Run During Off-Peak Hours**
   - Avoid impacting production
   - Get consistent baseline measurements

---

## Continuous Performance Monitoring

### Automated Testing

Add to CI/CD pipeline:

```bash
#!/bin/bash
# ci_load_test.sh

# Run load test
python tests/quick_load_test.py 50 10

# Check results
if grep -q '"total_errors": 0' load_test_results.json; then
  echo "✅ Load test PASSED"
  exit 0
else
  echo "❌ Load test FAILED"
  exit 1
fi
```

### Baseline Measurements

Record baseline performance:

```bash
# Capture baseline
python tests/quick_load_test.py 50 10 > baseline.txt

# Compare future runs
python tests/quick_load_test.py 50 10 > current.txt
diff baseline.txt current.txt
```

---

## API Usage Examples

### Basic Health Check

```bash
curl -X GET http://localhost:8000/health
```

### Predict ETA

```bash
curl -X POST http://localhost:8000/predict-eta \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 5.0,
    "hour": 14,
    "is_monsoon": 0,
    "ambulance_type": 2,
    "violations_zone": 0
  }'
```

### Emergency Dispatch

```bash
curl -X POST http://localhost:8000/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "incident_latitude": 19.076,
    "incident_longitude": 72.877,
    "severity": "High",
    "incident_type": "Trauma",
    "patient_name": "John Doe",
    "patient_phone": "+91-9876543210",
    "distance_km": 2.5
  }'
```

---

## Documentation Files

- `swagger.yaml` - Full OpenAPI 3.0 specification
- `load_test.py` - Locust-based advanced load testing
- `quick_load_test.py` - Simple Python load testing
- `README.md` - This file

---

## Support & Questions

For API issues: Check OpenAPI spec in Swagger Editor
For load testing issues: Review troubleshooting section above
For performance concerns: Contact DevOps team

**Last Updated:** April 12, 2026
**API Version:** 1.0.0
