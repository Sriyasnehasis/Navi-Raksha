# 🚀 NaviRaksha Team Briefing - March 30, 2026

**From:** Sriya Snehasis (Team Lead)  
**Date:** March 30, 2026  
**Deadline:** May 1, 2026 (33 days)  
**Status:** PHASE 1 Complete ✅ → **PHASE 2 Starts TODAY**

---

## ✅ PHASE 1 Complete (March 29)

**Deliverable:** Navi Mumbai Road Network Extracted & Validated

### What Was Done:

- ✅ Extracted OSM road network: **5000+ nodes, 8000+ edges**
- ✅ Defined & validated **66 key city locations** across all zones:
  - Vashi (9), Nerul (6), Belapur (6), Kharghar (8), Panvel (6)
  - Turbhe MIDC (6), Airoli (7), Sanpada (6), Ulwe (6), Dronagiri (6)
- ✅ Added India-specific features:
  - Monsoon-prone zones (Kharghar, Ulwe, Dronagiri)
  - MIDC industrial peak hours (Turbhe, Thane-Belapur)
  - Bridge bottlenecks (Vashi, Airoli)
- ✅ Saved in 4 formats (pkl, geojson, graphml, csv)
- ✅ Committed to GitHub

### Files Ready:

- `data/raw/navi_mumbai_road_graph.pkl` **(MAIN FILE - 21 MB)**
- `data/raw/key_locations.csv` (66 validated locations)
- `data/raw/navi_mumbai_edges.geojson` (visualization)
- `data/raw/navi_mumbai_road_graph.graphml.xml` (universal format)

**GitHub:** https://github.com/Sriyasnehasis/Navi-Raksha (main branch)

---

## 📋 PHASE 2: YOUR TASKS (Mar 30 - Apr 5)

### **ANJANAA (ML Engineer) - HIGHEST PRIORITY**

**Deadline:** April 4, 11:59 PM  
**Goal:** Prepare training dataset (500 samples) for ML models

#### Tasks:

1. **Download Uber Movement Traffic Data**
   - Website: https://movement.uber.com/
   - Region: Mumbai, Maharashtra
   - Focus: Historical speeds for Navi Mumbai area
   - Time range: 6 months minimum
   - Save to: `data/raw/uber_traffic_data.csv`

2. **Create Feature Engineering Notebook**
   - File: `notebooks/02_feature_engineering.ipynb`
   - Load: `data/raw/navi_mumbai_road_graph.pkl` (Sriya's output)
   - Extract features from road graph edges:
     ```
     ✅ segment_length_km (from graph)
     ✅ road_type (from OSM: primary, secondary, residential)
     ✅ is_monsoon_zone (from our feature flags)
     ✅ is_midc_zone (from our feature flags)
     ✅ is_bridge (from our feature flags)
     ✅ hour_of_day (0-23, temporal)
     ✅ day_of_week (0-6, temporal)
     ✅ is_peak_hour (8-10 AM or 5-7 PM)
     ✅ avg_speed_kmh (from Uber data)
     ✅ congestion_multiplier (computed from patterns)
     ```
   - Create synthetic labels: `ETA_minutes = segment_length_km / speed_kmh * 60`
   - Generate 500 samples (5,000 road segments × random temporal variations)

3. **Create Dataset Splits**
   - Train set: 70% (350 samples)
   - Validation set: 15% (75 samples)
   - Test set: 15% (75 samples)
   - Save as:
     - `data/processed/train.csv`
     - `data/processed/val.csv`
     - `data/processed/test.csv`

4. **Start Baseline Models**
   - File: `notebooks/03_baseline_models.ipynb`
   - Train Random Forest: 50 trees, max_depth=10
   - Train LSTM: 64 hidden units, 50 epochs
   - Target: MAE < 4.0 min each
   - Save: `models/trained/rf_baseline.pkl` , `lstm_baseline.h5`

#### Deliverables (by April 4):

- [ ] Uber traffic data downloaded
- [ ] Feature engineering notebook complete
- [ ] 3 dataset files (train/val/test CSV)
- [ ] RF + LSTM models trained
- [ ] Model comparison table (RF vs LSTM)

---

### **TURYA (Routing Engineer) - HIGH PRIORITY**

**Deadline:** April 10, 11:59 PM  
**Goal:** Implement A\* routing + dispatch classifier

#### Tasks:

1. **Study & Implement A\* Algorithm**
   - Resource: https://en.wikipedia.org/wiki/A*_search_algorithm
   - Create: `modules/routing/route_optimizer.py`
   - Features:
     - Load road graph from `data/raw/navi_mumbai_road_graph.pkl`
     - Implement A\* with haversine heuristic
     - Return **top 3 routes** ranked by time
     - Function: `optimize_route(source_lat, source_lon, dest_lat, dest_lon) → [route1, route2, route3]`
   - **TARGET:** Route generation < 2 seconds

2. **Implement Dispatch Classifier**
   - Create: `modules/routing/dispatch_classifier.py`
   - Classify ambulance type based on:
     - Road width (wide arterial → ALS, narrow → Mini/Bike)
     - Zone density (slum → Bike, standard → BLS, critical → ALS)
     - Case severity (critical cardiac → force ALS)
   - Algorithm: Random Forest or simple rule engine
   - **TARGET:** 95%+ accuracy on 50-case validation set
   - Assign types: **ALS** (van), **BLS** (van), **Mini** (compact), **Bike** (2-wheeler)

3. **Unit Tests**
   - Write 20+ test cases covering:
     - Empty paths, unreachable destinations
     - Monsoon detours (Kharghar flooding)
     - MIDC rush hour (Thane-Belapur penalized)
     - Bridge bottlenecks (Vashi/Airoli bridges)
   - File: `tests/test_routing.py`

4. **Integration with GNN** (once Sriya provides GNN API)
   - Update edge weights dynamically with GNN predictions
   - Re-route when predicted ETA changes by >2 minutes

#### Deliverables (by Apr 10):

- [ ] A\* algorithm implemented & tested
- [ ] Route generation latency < 2 sec
- [ ] Dispatch classifier with 95%+ accuracy
- [ ] 20+ unit tests written & passing
- [ ] Unit tests in GitHub Actions CI/CD

---

### **ARISHA (Frontend Lead) - MEDIUM PRIORITY**

**Deadline:** April 10, 11:59 PM  
**Goal:** Build Streamlit UI components & dashboards

#### Tasks:

1. **Create Streamlit Project Structure**

   ```
   ui/
   ├── citizen_tracker.py         (live tracking for public)
   ├── dispatcher_dashboard.py     (control room fleet management)
   └── components.py              (reusable components)
   ```

2. **Build Reusable Components** (`components.py`)
   - `render_folium_map(center_lat, center_lon, ambulances, hospitals)`
   - `render_eta_countdown(initial_eta_seconds)`
   - `render_fleet_status_table(ambulance_list)`
   - `render_incident_queue(incidents)`
   - `render_kpi_cards(avg_response_time, active_incidents, etc.)`

3. **Citizen Live Tracker** (`citizen_tracker.py`)
   - Folium map: Navi Mumbai + 10 hospitals
   - Live ambulance marker (updates every 5 sec)
   - ETA countdown (minutes:seconds)
   - Delay reason toast notification
   - **TARGET:** <5 sec latency, no lag on 5 ambulances

4. **Dispatcher Dashboard** (`dispatcher_dashboard.py`)
   - **Tab 1:** Fleet Status (ambulance table)
   - **Tab 2:** Map View (all ambulances + incidents live)
   - **Tab 3:** Incident Queue (incoming calls)
   - **Tab 4:** KPIs (response time, active cases, etc.)
   - **TARGET:** No lag on 5+ ambulances

5. **Simulation Backend** (`modules/simulation.py`)
   - Generate fake ambulance trajectories
   - Simulate monsoon delays (ETA +15% at 60% mark)
   - Simulate hospital bed updates (recommender re-ranks)

#### Deliverables (by Apr 10):

- [ ] Streamlit folder structure created
- [ ] Components library complete (5 functions)
- [ ] Citizen tracker app working (live map + ETA)
- [ ] Dispatcher dashboard complete (4 tabs)
- [ ] Simulation backend ready for testing

---

### **SRIYA (You - Continue) - CRITICAL PATH**

**Deadline:** April 16, 11:59 PM  
**Goal:** Feature engineering + GNN training on Colab GPU

#### Tasks:

1. **Feature Engineering** (Mar 30 - Apr 4)
   - Create `notebooks/02_feature_engineering.ipynb`
   - Convert road graph edges → training samples
   - Engineer 10 features: length, road_type, monsoon, MIDC, bridge, hour, day, peak, speed, congestion
   - Generate 500 samples with synthetic ETA labels
   - Create train/val/test splits (70/15/15)
   - **Deadline:** April 4

2. **GNN Model Training** (Apr 7 - Apr 16) ⭐
   - Create `notebooks/04_gnn_training.ipynb` for Colab
   - Use Google Colab GPU (free tier)
   - Load training data from `data/processed/train.csv`
   - Architecture: PyTorch Geometric, 2-3 GCN layers, 64→32→1 neurons
   - Loss: MAE (Mean Absolute Error)
   - **TARGET:** MAE < 3.0 minutes on validation set
   - Save: `models/trained/gnn_best.pt`
   - Log: Training curves, hyperparameter search results

3. **Model Comparison** (Apr 15 - Apr 16)
   - Create comparison table:
     ```
     Model    | MAE (min) | RMSE (min) | Training Time | Inference (ms)
     ---------|-----------|------------|---------------|---------------
     RF       | 4.2       | 5.1        | 2 min         | 0.5
     LSTM     | 3.9       | 4.8        | 15 min        | 1.2
     GNN ⭐  | < 3.0     | < 3.8      | 3 hours       | 2.0
     ```
   - Document in: `docs/model_comparison.md`

4. **API Wrapper** (Apr 16)
   - Create FastAPI endpoint: `POST /predict-eta`
   - Loads GNN model (.pt file)
   - Input: source_lat, dest_lat, source_lon, dest_lon, hour, day
   - Output: ETA (minutes)
   - Latency: < 500 ms

#### Deliverables (by Apr 16):

- [ ] Feature engineering notebook complete
- [ ] 500 training samples with 10 features
- [ ] Train/val/test splits created
- [ ] GNN trained on Colab (MAE < 3 min)
- [ ] Model comparison table published
- [ ] GNN API wrapper ready

---

## 📅 WEEK 2 TIMELINE (Mar 30 - Apr 6)

```
Mar 30 (Mon):  Team briefing, all start tasks
Mar 31 (Tue):  Data collection (Anjanaa), routing study (Turya), UI design (Arisha)
Apr 1  (Wed):  Feature engineering (Sriya), Uber data processing (Anjanaa)
Apr 2  (Thu):  Dataset ready (Anjanaa), A* skeleton (Turya), components (Arisha)
Apr 3  (Fri):  RF/LSTM training starts (Anjanaa), GNN on Colab (Sriya)
Apr 4  (Sat):  All datasets ready, baselines trained
Apr 5  (Sun):  Routing tests (Turya), UI testing (Arisha), GNN training continues
Apr 6  (Mon):  TEAM SYNC 6 PM - Review Phase 2 progress
```

**Friday 6 PM Sync (Apr 5):**

- Anjanaa: Show 500 samples, RF/LSTM curves
- Turya: Demo A\* with 5 test routes
- Arisha: Show Streamlit UI screenshots
- Sriya: GNN training progress on Colab

---

## 🎯 Success Criteria

| Deliverable          | Owner     | Deadline | Success Target             |
| -------------------- | --------- | -------- | -------------------------- |
| 500 training samples | Anjanaa   | Apr 4    | All 10 features, no NaN    |
| RF baseline MAE      | Anjanaa   | Apr 4    | < 4.2 minutes              |
| LSTM baseline MAE    | Anjanaa   | Apr 4    | < 3.9 minutes              |
| A\* routing <2 sec   | Turya     | Apr 10   | 100 queries all <1.5 sec   |
| Dispatch accuracy    | Turya     | Apr 10   | ≥ 95% on validation set    |
| Citizen tracker      | Arisha    | Apr 10   | <5 sec latency, no lag     |
| Dispatcher dashboard | Arisha    | Apr 10   | 4 tabs working, responsive |
| GNN trained (Colab)  | **Sriya** | Apr 16   | **MAE < 3.0 minutes** ⭐   |

---

## 📞 Communication

**Daily:** 10 AM async standup (Slack/Teams)

```
✅ Yesterday: [thing completed]
⏳ Today: [thing you'll do]
🚫 Blocker: [any issues]
```

**Weekly:** Friday 6 PM video sync (30 min)

- Progress review
- Blocker resolution
- Plan next week

**Emergency:** Slack ping in #naviraksha-dev

---

## 📚 Resources

- **Road graph:** `data/raw/navi_mumbai_road_graph.pkl`
- **Key locations:** `data/raw/key_locations.csv`
- **Project plan:** `PROJECT_PLAN.md`
- **Team roles:** `TEAM_ROLES.md`
- **GitHub:** https://github.com/Sriyasnehasis/Navi-Raksha
- **Colab template:** `notebooks/01_extract_road_graph_COLAB.ipynb` (for reference)

---

## ⚠️ Critical Path

```
Road Graph (✅ DONE)
    ↓
Feature Engineering (Anjanaa, Sriya) → Deadline: Apr 4
    ↓
ML Models (RF/LSTM/GNN) → Deadline: Apr 16
    ↓
API Wrapper (Sriya) → Deadline: Apr 16
    ↓
Integration (All) → Deadline: Apr 27
    ↓
Testing + Paper → Deadline: May 1
```

**If any task is delayed, escalate immediately!**

---

## 🚀 Summary

- ✅ **Phase 1 Complete:** Road network extracted (66 locations)
- ⏳ **Phase 2 Starts:** Feature engineering + ML models
- 📅 **33 days** until submission (May 1)
- 💪 **Team is ready** to execute
- 🎯 **MVP deadline:** April 27 (gives 4 days for final polish)

---

**Questions?** Slack or Friday sync.

**Ready to ship! Let's go! 🚀**

---

_Document by: Sriya Snehasis_  
_Date: March 30, 2026_  
_Status: Distribution Ready_
