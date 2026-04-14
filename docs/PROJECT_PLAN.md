# NaviRaksha: Project Plan & Scope

**Project Name:** GNN-Based Ambulance Response Time Prediction and Dynamic Route Optimization for Navi Mumbai  
**Institution:** Amity University Mumbai (ASET, Department of CSE)  
**Academic Year:** 2025–26  
**Duration:** 13 weeks (Jan Wk3 – May Wk1)  
**Submission Deadline:** May 1, 2026

---

## 📌 Problem Statement

Emergency Medical Services (EMS) in Maharashtra face a **critical response time crisis**:
- **National average:** 20-40 minutes (Maharashtra EMS 108 service)
- **Safe survival window:** 8 minutes (golden period for cardiac emergencies)
- **Maharashtra district-level average:** 134.5 minutes (unacceptable)
- **Base-to-scene travel time:** 23.15 minutes average

**Navi Mumbai specifics:**
- Complex geography: commercial zones (Vashi, Belapur), residential (Kharghar, Nerul), industrial (Turbhe MIDC), coastal (Ulwe, Dronagiri)
- Critical bottlenecks: Sion-Panvel Highway, Vashi/Airoli bridges
- Seasonal challenges: monsoon flooding, festival traffic surges
- Infrastructure gaps: narrow slum corridors, underserved remote zones

**No deployed AI system exists in India** that integrates ETA prediction, real-time routing, smart dispatch, and live tracking.

---

## 🎯 Project Objectives

1. **Develop GNN-based ETA model** for ambulance response time prediction (< 3 min MAE)
2. **Implement dynamic A* route optimizer** with real-time re-routing capability (< 2 sec response)
3. **Create multi-type ambulance dispatch system** (ALS/BLS/Mini/Bike classification, 95%+ accuracy)
4. **Build hospital recommendation engine** ranked by ETA + bed availability
5. **Deploy citizen live tracking interface** with 3D map visualization
6. **Create dispatcher dashboard** for NMMC control room operations
7. **Publish IEEE-quality research paper** documenting methodology and India-specific feature engineering
8. **Demonstrate end-to-end system** with final presentation + live demo

---

## 🚀 6 Core Modules

| # | Module | Owner | Input | Output | Success Target |
|---|--------|-------|-------|--------|-----------------|
| 1 | **GNN ETA Predictor** | Sriya (ML) | Source/dest coords, time, weather, zone | ETA (minutes) | MAE < 3 min |
| 2 | **A* Route Optimizer** | Turya (Routing) | Current location, destination, road graph | Top 3 routes, ETA | <2 sec latency |
| 3 | **Ambulance Dispatcher** | Turya (Routing) | Incident location, road type, case severity | ALS/BLS/Mini/Bike | 95%+ accuracy |
| 4 | **Hospital Recommender** | Anjanaa (ML) | Incident location, ETA estimates, bed data | Top 3 hospitals ranked | <30 sec response |
| 5 | **Citizen Tracker** | Arisha (Frontend) | Ambulance location, route, ETA | Live map + countdown | <5 sec latency |
| 6 | **Dispatcher Dashboard** | Arisha (Frontend) | Fleet status, incidents, KPIs | Control room UI | No lag on 5 units |

---

## 📊 India-Specific Features

### Monsoon Flooding Detection 🌧️
- **Zones:** Kharghar, Ulwe, Dronagiri
- **Duration:** June 1 – September 30
- **Impact:** 1.3× ETA multiplier for affected segments
- **Source:** IMD monsoon data

### MIDC Industrial Surge ⏰
- **Zones:** Thane-Belapur Road, Turbhe, Rabale industrial areas
- **Peak Hours:** 8-10 AM (shift start), 5-7 PM (shift end)
- **Impact:** 1.2× ETA multiplier during these hours
- **Source:** Known industrial shift timings

### Bridge Bottlenecks 🌉
- **Critical Bridges:** Vashi, Airoli
- **Impact:** 1.5-2.0× ETA multiplier (chokepoints)
- **Mitigation:** Route optimization to minimize bridge crossings

### Festival Traffic 🎉
- **High-Traffic Events:**
  - Ganesh Chaturthi: August 28 – September 8, 2026
  - Navratri: October 1 – October 10, 2026
- **Impact:** 1.4× city-wide ETA multiplier
- **Source:** Festival calendar

### Slum Corridor Access 🏘️
- **Challenge:** Narrow lanes in dense residential zones (Turbhe, Sanpada interiors)
- **Solution:** Multi-type ambulance dispatch (bike ambulances for first response)
- **Impact:** Critical for response time in underserved areas

---

## 📅 13-Week Timeline with Milestones

### **Phase 1: Requirements & Setup (Weeks 1–2)**
**Deliverables:**
- ✅ GitHub repo + team collaboration setup
- ✅ Project folder structure
- ✅ Python environment (venv + requirements.txt)
- ✅ Feature engineering design doc
- ✅ Data sources specification
- ✅ Team role assignments & task allocation

**Timeline:** January 3 – January 16, 2026  
**Status:** IN PROGRESS (March 29 catch-up)

---

### **Phase 2: Data & Network Preparation (Weeks 3–4)**
**Deliverables:**
- [ ] Navi Mumbai road network extraction (OSMnx)
- [ ] Validate 50+ key city nodes
- [ ] Feature engineering pipeline implementation
- [ ] EDA notebook with visualizations
- [ ] Training data preparation (500+ synthetic samples)

**Timeline:** January 17 – January 31  
**Key Tasks (Sriya):**
1. Extract road graph (~5,000–10,000 edges)
2. Apply feature engineering: monsoon flags, MIDC surge weights, bridge bottlenecks, festival multipliers
3. Create EDA with distribution plots, connectivity analysis
4. Validate all 10 key city locations (Vashi, Nerul, Belapur, Kharghar, Panvel, Turbhe, Airoli, Sanpada, Ulwe, Dronagiri)

---

### **Phase 3: ML Model Development (Weeks 5–7)**
**Deliverables:**
- [ ] Random Forest baseline model (4.2 min MAE target)
- [ ] LSTM temporal model (3.9 min MAE target)
- [ ] GNN model (< 3.0 min MAE target) ⭐
- [ ] SHAP explainability analysis
- [ ] Model comparison report

**Timeline:** February 7 – February 28  
**Key Tasks (Sriya + Anjanaa):**
- RF: Train on 500 samples, 50 trees, depth=10, evaluate on validation set
- LSTM: 64 hidden units, 50 epochs, temporal sequences, early stopping
- GNN: PyTorch Geometric, 2–3 GCN layers, graph convolution on road network
- SHAP: Feature importance plots, top 5 driving factors for predictions

**⚠️ CRITICAL:** GNN training on CPU takes ~4-6 hrs/epoch (total ~400+ hrs). **Use Google Colab free GPU tier** (12 hrs/week free access gives ~4 hrs per epoch on GPU).

---

### **Phase 4: Routing & Dispatch Logic (Weeks 8–9)**
**Deliverables:**
- [ ] A* pathfinding algorithm (top 3 routes, <2 sec generation)
- [ ] Dynamic re-routing on traffic/weather changes
- [ ] Ambulance type classifier (95%+ accuracy)
- [ ] Hospital recommender module
- [ ] Unit tests & validation

**Timeline:** March 7 – March 21  
**Key Tasks (Turya + Anjanaa):**
- Turya: A* pathfinding with haversine heuristic, integrate GNN edge weights
- Turya: Dispatch rule engine (wide road→ALS, narrow→Mini, slum→Bike, critical→override)
- Anjanaa: Hospital scoring & ranking logic, bed availability integration
- Both: Unit tests on 50+ test cases

---

### **Phase 5: Frontend & Integration (Weeks 10–12)**
**Deliverables:**
- [ ] Citizen live tracker (Folium map, ETA countdown, delay display)
- [ ] Dispatcher dashboard (fleet status, incidents, KPIs)
- [ ] Simulation backend (fake ambulance movement for testing)
- [ ] Full system integration test
- [ ] Docker deployment

**Timeline:** March 22 – April 11  
**Key Tasks (Arisha + Sriya):**
- Arisha: Streamlit apps, Folium visualization, responsive UI
- Sriya: API design, model serving (FastAPI), Docker containerization
- Joint: End-to-end integration testing, performance validation

---

### **Phase 6: Testing & Submission (Weeks 13–15)**
**Deliverables:**
- [ ] Unit tests (10+ per module)
- [ ] Integration tests (full pipeline)
- [ ] 4 scenario tests with documentation
- [ ] Research paper (IEEE format, 6–8 pages)
- [ ] Final presentation slides (20 min + demo)
- [ ] GitHub repo submission-ready

**Timeline:** April 12 – May 1  
**Key Tasks (ALL):**
- Scenario 1: Monsoon flooding → verify ETA +15%, routes avoid flooded segments
- Scenario 2: MIDC rush hour → verify Thane-Belapur penalty applied, alternative routes generated
- Scenario 3: Multi-ambulance simultaneous dispatch → unique routes, correct type assignment
- Scenario 4: Hospital re-ranking on bed availability update → recommender re-scores correctly
- Paper: Sections on literature, methodology (GNN architecture), results (model comparison, SHAP), conclusions
- Presentation: Live demo, architecture diagram, 3-4 key findings

---

## 🎯 Success Metrics & Acceptance Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **GNN Model MAE** | < 3 minutes | Test set evaluation (15% held-out) |
| **A* Router Latency** | < 2 seconds | Benchmark on 100 random queries |
| **Dispatch Classifier Accuracy** | ≥ 95% | Confusion matrix on 50-case test set |
| **Hospital Recommender Response** | < 30 seconds | API latency test with 1000 queries |
| **Citizen Tracker Update Latency** | < 5 seconds | Live browser test with 5-ambulance load |
| **Dispatcher Dashboard** | No lag | Folium rendering test (5+ ambulances + incidents) |
| **Road Network Coverage** | 50+ key nodes | GPS validation with map overlay |
| **Code Quality** | 100% test pass | GitHub Actions CI/CD pipeline |
| **Documentation** | Complete | README, API docs, deployment guide |
| **Paper Quality** | IEEE-acceptable draft | Peer review before submission |

---

## 💻 Technology Stack (Final)

```
Language:           Python 3.10+
ML/DL:              PyTorch, PyTorch Geometric, Scikit-learn, Keras/TensorFlow
Road Networks:      OSMnx, NetworkX, GeoPandas
Routing:            A* (NetworkX), OpenRouteService API
Visualization:      Folium, Matplotlib, Seaborn, Plotly
Web Framework:      Streamlit (frontend), FastAPI (backend)
Explainability:     SHAP
Data Processing:    Pandas, Numpy, Scipy
Development:        Jupyter Notebook, VS Code, Git/GitHub
Deployment:         Docker, GitHub Actions CI/CD
Version Control:    Git
```

---

## 📝 Deliverable Checklist

**By May 1, 2026, Submit:**
- [ ] GitHub repository (clean, documented, all commits)
- [ ] GNN trained model (.pt file, MAE < 3 min validated)
- [ ] A* router module (handles 5 concurrent requests)
- [ ] Dispatch classifier (95%+ accuracy on test set)
- [ ] Citizen tracker dashboa (live demo video, 2-3 min)
- [ ] Dispatcher dashboard (fleet management UI visible)
- [ ] Hospital recommender (top 3 ranked with ETA estimates)
- [ ] Research paper (6–8 pages, IEEE format, Overleaf draft)
- [ ] Final presentation slides (20 min delivery + 10 min Q&A)
- [ ] Testing report (4 scenarios documented with screenshots)
- [ ] Deployment guide (Docker commands, setup instructions)
- [ ] README with quick-start guide

---

## ⚠️ Critical Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **GNN training too slow (CPU bottleneck)** | Day 2+ of Wk 5-7 | Use Google Colab free GPU tier (12 hrs/week) |
| **OSM missing slum roads** | Route realism in dense areas | Manually add 10–15 critical slum corridors via local knowledge |
| **Real ETA ground truth unavailable** | Model accuracy validation | Use synthetic ground truth (baseline speed + feature multipliers) |
| **Team member unavailable mid-project** | Schedule slip | Pair critical modules, ensure 80% documentation |
| **Streamlit performance on large road graphs** | Dashboard unusable | Cache Folium map tiles, lazy-load hospital details, test by Week 10 |
| **13-week timeline aggressive** | Rush → quality loss | Prioritize 6 core modules, defer analytics/reporting features |

---

## 📞 Team Communication & Coordination

**Daily Standup:** 10 AM (async, 5-min update on Slack/Teams)  
- What did you complete yesterday?
- What are you working on today?
- Any blockers?

**Weekly Sync:** Friday evening (30 min video call)  
- Review phase progress
- Discuss interdependencies
- Plan next week

**Repository Workflow:**
- Feature branches: `feature/gnn-model`, `feature/routing`, etc.
- Main branch: Only tested, reviewed code
- PR rule: 1 approval before merge

---

## 🚀 Ready to Start?

**This document is your **north star**. Refer to it weekly to track progress.**

**Next Immediate Steps (This Weekend):**
1. Python environment setup (venv)
2. Install all 37 packages
3. Road graph extraction starts
4. Send team: Project plan + role assignments

---

**Document Version:** 1.0  
**Last Updated:** March 29, 2026  
**Next Review:** April 5, 2026 (End of Phase 1)  
**Lead:** Sriya Snehasis
