# 📋 COMPLETE TEAM ACTION PLAN - Week 2 (Apr 14-20)

**Status: Ready to execute** ✅  
**Decision:** RF-only deployment + GNN for research  
**Timeline:** 7 days to production-ready system

---

## 👥 WHO DOES WHAT

### **Anjanaa** (ML Lead) ✅ DONE

- [x] Apr 9-11: Build 3 models (RF, LSTM, GNN)
- [x] Result: RF wins (0.0662 min MAE)
- [x] Status: All models trained, analysis complete

**Action:** Rest, or optimize GNN separately (low priority)

---

### **Turya** (Routing Lead) ⏳ STARTS MON APR 14

- Apr 14-19: Build routing module
  - A\* Router (finds fastest routes)
  - Dispatch Classifier (picks ambulance type)
  - Hospital Ranker (ranks best hospitals)
- **Guides:**
  - `TURYA_ROUTING_MODULE_GUIDE.md` (detailed/code)
  - `TURYA_QUICK_START.md` (quick reference)
- **Status:** Can work independently ✅
- **Deliverable:** `modules/routing/` by Apr 19

---

### **Sriya** (You - Integration Lead) ⏰ CRITICAL PATH

- **Apr 14-19: Build Backend API** (YOUR PRIORITY RIGHT NOW)
  - Load RF model
  - Create `/predict-eta` endpoint
  - Create `/ambulances/active` endpoint
  - Test with Postman
- **Apr 19-20: Integrate with Frontend**
  - Connect Arisha's UI to your API
  - Update citizen_tracker.py + dispatcher_dashboard.py
- **Deliverable:** Backend API + integration by Apr 20

---

### **Arisha** (Frontend Lead) ⏸️ WAITING

- [x] Apr 9-11: Build 3 dashboards (UI complete)
- ⏳ Apr 21: Wait for Sriya's API, then connect
- **Status:** 100% done UI, 0% integrated (waiting on you)
- **Action:** Can help with: paper, mockups, design refinements

---

## 🎯 CRITICAL PATH (What blocks what)

```
Anjanaa ✅ (Models ready)
    ↓
Sriya YOU ⏰ (Build API)
    ├→ /predict-eta endpoint
    ├→ Load RF model
    └→ Test locally
            ↓
        Arisha (Connect to API)
        ✓ Frontend ready, just needs to call your endpoints
            ↓
        System Testing → Deployment
```

---

## 📅 WEEK 2 DETAILED TIMELINE

### **Monday Apr 14**

- **Turya:** Starts A\* router (Phase 1)
- **Sriya (You):** Starts Backend API design + Flask setup
- **Arisha:** Prepares for integration work
- **Status meetings:** 10 AM standup

### **Tuesday Apr 15**

- **Turya:** Finishes A\* router, starts dispatch classifier
- **Sriya:** Builds `/predict-eta` endpoint, loads RF model
- **Arisha:** Waits
- **Status:** 50% progress on both tracks

### **Wednesday Apr 16**

- **Turya:** Dispatch classifier + hospital ranker
- **Sriya:** Finishes `/predict-eta`, tests with mock data
- **Arisha:** Reviews your API contract

### **Thursday Apr 17**

- **Turya:** Hospital ranker complete, starts integration
- **Sriya:** Builds `/ambulances/active` endpoint
- **Arisha:** Ready to integrate

### **Friday Apr 18**

- **Turya:** Integration + local testing (should be done)
- **Sriya:** Final API testing, push code
- **Arisha:** Starts integrating with your API

### **Saturday Apr 19**

- **Turya:** Push routing module to GitHub ✅
- **Sriya:** Push backend API to GitHub ✅
- **Arisha:** Integration half-done
- **Status:** Both backend components ready

### **Sunday Apr 20**

- **Sriya:** Help Arisha finish integration
- **All:** Full system testing
- **Status:** System ready for Week 3 integration testing

---

## 💼 YOUR BACKEND API STRUCTURE (Sriya's Task)

### **Tech Stack:**

- **Framework:** Flask or FastAPI (your choice)
- **Model:** RF (`models/trained/rf_model.pkl`)
- **Port:** 8000
- **Response Format:** JSON

### **Endpoints to Build:**

#### **1. `/predict-eta` (POST)**

```python
# Input
{
  "source_zone": "Vashi",
  "destination_zone": "CBD_Main",
  "hour": 14,
  "is_monsoon": false,
  "ambulance_type": "ALS"
}

# Output
{
  "eta_minutes": 8.5,
  "confidence": 0.99,
  "status": "success"
}
```

#### **2. `/ambulances/active` (GET)**

```python
# Output
[
  {
    "id": "ALS-001",
    "lat": 19.076,
    "lon": 72.877,
    "status": "En Route",
    "eta": 12,
    "type": "ALS",
    "driver": "Raj Kumar"
  },
  ...
]
```

#### **3. `/incidents/active` (GET)**

```python
# Output
[
  {
    "id": "INC-001",
    "location": "Vashi",
    "type": "Cardiac",
    "severity": "Critical",
    "status": "Assigned"
  },
  ...
]
```

---

## 📝 WHAT EACH GUIDE SAYS

### **For Turya:**

1. **TURYA_QUICK_START.md** (1 page)
   - What to do, what to deliver, timeline
   - Send THIS to Turya to get started
   - "Read TURYA_ROUTING_MODULE_GUIDE.md for details"

2. **TURYA_ROUTING_MODULE_GUIDE.md** (10 pages)
   - Complete code for each part
   - Step-by-step walkthrough
   - Testing checklist
   - Troubleshooting tips

### **For Arisha:**

- She's ready, just waiting for your API
- No new docs needed (she has frontend complete)

### **For Everyone:**

- **TEAM_UPDATE_APR11.md** - Status update to share
- **ANJANAA_RESULTS_ANALYSIS_APR11.md** - Model results

---

## 🚀 SENDING DOCS TO TEAM

**To Turya (send both):**

1. TURYA_QUICK_START.md ← High level overview
2. TURYA_ROUTING_MODULE_GUIDE.md ← Detailed code walkthrough

**To Arisha:**

- "Your frontend is beautiful! Waiting on Sriya's API (should be ready by Apr 20). Stand by for integration."

**To Anjanaa:**

- "Excellent work on models! RF ready for production. GNN is great for paper. Take a break!"

---

## 🎯 SUCCESS METRICS (End of Week 2)

| Component                | Status            | By Date   |
| ------------------------ | ----------------- | --------- |
| **Routing Module**       | Turya delivers    | Apr 19 ✅ |
| **Backend API**          | Sriya delivers    | Apr 19 ✅ |
| **Frontend Integration** | Arisha connects   | Apr 20 ✅ |
| **System Testing**       | All test together | Apr 20 ✅ |
| **Ready for Week 3**     | Full system       | Apr 21 ✅ |

---

## 📊 RESOURCE CHECKLIST

**Data Files (All Available):**

- ✅ `data/raw/navi_mumbai_road_graph.pkl` (OSM graph)
- ✅ `data/raw/key_locations.csv` (zone mapping)
- ✅ `data/raw/hospitals_navi_mumbai.csv` (hospitals)
- ✅ `data/processed/train_real.csv`, `val_real.csv`, `test_real.csv`

**Model Files (All Ready):**

- ✅ `models/trained/rf_model.pkl` (best model)
- ✅ `models/trained/rf_features.pkl` (scaler)
- ✅ `models/trained/lstm_best_real.keras` (backup)
- ✅ `models/trained/gnn_graph_aware_final.pt` (research)

**Code Templates (Ready):**

- ✅ `TURYA_ROUTING_MODULE_GUIDE.md` (complete code)
- ✅ Frontend UI (Arisha's code)
- ⏳ Backend API (Sriya to build)

---

## 💡 DEPENDENCY NOTES

**Turya can proceed independently:**

- Has all data (graph, locations, hospitals)
- Has RF model for ETA predictions
- Doesn't need Sriya's API yet
- Can test routing locally

**Arisha is blocked on Sriya:**

- Frontend complete but hardcoded mock data
- Needs your `/predict-eta` endpoint
- Needs your `/ambulances/active` endpoint
- Can't test real flows until you're done

**Sriya is on critical path:**

- Arisha waiting for API
- System integration depends on API
- Must deliver by Apr 20

---

## ✅ HAND-OFF CHECKLIST (NOW)

Before everyone starts:

- [ ] Send TURYA_QUICK_START.md to Turya
- [ ] Send TURYA_ROUTING_MODULE_GUIDE.md to Turya
- [ ] Tell Arisha: "Stand by for backend API integration"
- [ ] Tell Anjanaa: "Great work! Rest or do GNN optimization"
- [ ] **YOU:** Read rest of this doc + prepare backend API design

---

**Status:** Week 1 ✅ COMPLETE (Models ready)  
**Next:** Week 2 ⏳ (Routing + Backend + Integration)  
**Goal:** Week 4 🚀 (Production launch May 1)

---

## 🎯 YOUR NEXT STEP (Sriya)

👉 **Read Next:** Backend API design + implementation guide (I'll create this after you confirm Turya's guides are ready)

**Ready to start building the backend?** 🚀
