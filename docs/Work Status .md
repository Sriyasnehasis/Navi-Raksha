## 📊 PROJECT STATUS

### ✅ COMPLETED (Sriya)

- Dataset generation: **10,000 realistic EMS trips** ✓
- Train/Val/Test split: **8K / 1K / 1K** ✓
- RF baseline model: **4.2 min MAE** ✓
- 4 training notebooks: **Ready on GitHub** ✓
- Git workflow: **main + test branches set up** ✓

---

## 👥 ROLE ASSIGNMENTS

| Person      | Role                | Primary Task             | Timeline  |
| ----------- | ------------------- | ------------------------ | --------- |
| **Sriya**   | 🎯 Lead + Data      | Dataset ✅ + Integration | Apr 21-27 |
| **Anjanaa** | 🧠 ML Engineer      | Train models & compare   | Apr 8-13  |
| **Turya**   | 🛣️ Routing Dev      | A\* Router + Dispatch    | Apr 14-20 |
| **Arisha**  | 🎨 Frontend + Paper | Dashboard + IEEE Paper   | Apr 14-27 |

---

## 📈 PROJECT FLOW

### 🟢 Dataset to Models

```
SRIYA ✅ DONE
  └─> 10K Dataset
        ↓
ANJANAA (YOUR TURN!)
  ├─> Run Notebook 02: RF Baseline
  │     • Load train/val/test CSVs
  │     • Evaluate pre-trained RF model
  │     • Get baseline MAE (~4.2 min)
  │
  ├─> Run Notebook 03: LSTM Training (⏱️ 30 min)
  │     • Train LSTM on 8K samples
  │     • Target: MAE < 3.9 min
  │     • Save model: lstm_best_real.h5
  │
  ├─> Run Notebook 04: GNN Training (⏱️ 45 min)
  │     • Train GNN on OSM graph + data
  │     • Target: MAE < 3.0 min
  │     • Save model: gnn_best_real.pt
  │
  └─> Compare All 3 Models (📊 create report)
        • Which model wins?
        • Select best for production
        • Commit results to test branch
```

**ANJANAA'S DELIVERABLES **

- ✅ 02_random_forest_detailed.ipynb (executed)
- ✅ 03_lstm_training.ipynb (executed)
- ✅ 04_gnn_training.ipynb (executed)
- ✅ Model comparison report
- ✅ Performance metrics (MAE, RMSE, R²)
- ✅ Trained models saved
- ✅ Push results to test branch

---

### 🔨 Build Modules

```
TURYA
  ├─> A* Routing Algorithm
  │   Input: Source location + Destination (hospital)
  │   Output: Fastest route (< 2 sec response)
  │   Features:
  │     • Load OSM road graph
  │     • Weight edges: traffic, time, weather
  │     • Return optimized path
  │
  ├─> Ambulance Dispatch Classifier
  │   Input: Incident location + type
  │   Output: Ambulance type (ALS/BLS/Mini/Bike)
  │   • Use Anjanaa's trained model
  │   • 95%+ accuracy
  │
  └─> Hospital Ranker
      Input: Incident location
      Output: Ranked hospitals (ETA + beds)
      • Use A* to calculate ETAs
      • Rank by ETA + availability

Location: modules/routing/
```

**TURYA'S DELIVERABLES **

- ✅ astar_router.py (working A\* pathfinding)
- ✅ dispatch_classifier.py (ambulance type selection)
- ✅ hospital_ranker.py (hospital ranking)
- ✅ All modules tested independently
- ✅ API-ready (endpoints defined)

---

**ARISHA **
├─> Dispatcher Dashboard
│ • Live incident queue
│ • Ambulance location map (Folium)
│ • ETA predictions
│ • Hospital status
│ • KPIs (response time, success rate)
│
├─> Citizen Tracker
│ • Real-time ambulance location
│ • ETA countdown
│ • Hospital assignment
│
├─> Analytics Dashboard
│ • Historical performance
│ • Traffic patterns
│ • Zone-wise data
│

Location: ui/ or modules/frontend/

//ALL MEMBERS
└─> Start IEEE Paper
• Abstract + Intro + Methods
• Use results from Anjanaa

```

**ARISHA'S DELIVERABLES :**
- ✅ Dispatcher dashboard (complete)
- ✅ Citizen tracker page (complete)
- ✅ Analytics dashboard (complete)
- ✅ Responsive design + error handling
- ✅ Connected to backend APIs


---

###  🔗 Integration

```

SRIYA (TAKES OVER!)
├─> Create Backend API Layer
│ Endpoints:
│ • POST /predict-eta
│ • POST /find-route
│ • POST /dispatch
│ • POST /rank-hospitals
│
├─> Connect All Components
│ ML Module ──> API
│ Routing ──> API
│ Frontend ──> API
│
├─> System Testing
│ √ Test each endpoint
│ √ End-to-end flow testing
│ √ Load testing
│ √ Fix bugs
│
└─> Full Integration Testing

```

**SRIYA'S DELIVERABLES **
- ✅ Backend API server (Flask/FastAPI)
- ✅ All endpoints functional
- ✅ Database connected (if needed)
- ✅ System fully tested
- ✅ Deployment ready

---





## 🔗 DEPENDENCY CHAIN

```

┌─────────────────────────────────────────────┐
│ ANJANAA │
│ Train & Compare 3 Models │
│ Output: Trained models + selection │
└────────────────┬────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ TURYA │
│ Build Routing Module │
│ Output: A\*, Dispatch, Hospital Ranker │
└────────────────┬────────────────────────────┘
│
▼
┌─────────────────────────────────────────────┐
│ SRIYA │
│ Integrate Everything into Backend │
│ Output: Working API + full system │
└────────────────┬────────────────────────────┘

▼
┌─────────────────────────────────────────────┐
│ ARISHA (Parallel Week 2-3) │
│ Build Frontend Dashboard │
│ Output: UI connected to APIs │
└────────────────┬────────────────────────────┘
▼
🚀 LAUNCH

```


```
