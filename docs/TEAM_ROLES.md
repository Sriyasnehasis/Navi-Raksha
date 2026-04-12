# Team Role Assignments & Responsibilities

---

## **ROLE 1: DATA ENGINEER + TEAM LEAD** 👨‍💼

**Assigned To:** Sriya Snehasis (YOU)  
**Enrollment:** A70405223183

### **Primary Responsibility**

Build the core data infrastructure, develop the GNN model, coordinate all team activities, ensure system integration.

### **Modules Owned**

- **Module 1 (Part):** GNN ETA Prediction Engine
- **System Integration:** Coordinate API contracts between all 6 modules
- **Project Leadership:** Timeline tracking, GitHub management, team communication

### **Weekly Deliverables by Phase**

#### **Weeks 1–2 (Setup)**

- [ ] GitHub repo initialization
- [ ] Project folder structure
- [ ] requirements.txt (all dependencies)
- [ ] Feature engineering design document
- [ ] Data sources specification
- [ ] Team role assignments & task allocation

#### **Weeks 3–4 (Data Preparation)**

- [ ] Extract Navi Mumbai road network using OSMnx (~5,000–10,000 nodes)
- [ ] Validate 50+ key city nodes (Vashi, Nerul, Belapur, Kharghar, Panvel, Turbhe, Airoli, Sanpada, Ulwe, Dronagiri)
- [ ] Create EDA notebook: node degree distribution, edge length statistics, connectivity analysis
- [ ] Export road graph in 4 formats: .pkl (NetworkX), .geojson (edges), .geojson (nodes), .graphml
- [ ] Test shortest-path queries on 10 manual routes (all must be found ✓)

#### **Weeks 5–7 (GNN Development)** ⭐

- [ ] Design GNN architecture (PyTorch Geometric, 2–3 GCN layers, 64→32 neurons)
- [ ] Prepare training data: Convert NetworkX graph to PyG Data object
- [ ] Train GNN on 500 samples, 100 epochs, Adam optimizer, MAE loss
- [ ] Hyperparameter tuning: test layer depths, learning rates (0.001–0.01)
- [ ] **TARGET: GNN MAE < 3 minutes on validation set** (beat RF 4.2 min, LSTM 3.9 min)
- [ ] Save best model: `models/trained/gnn_best.pt`
- [ ] Create model comparison report: RF vs LSTM vs GNN (table with MAE/RMSE metrics)

#### **Weeks 8–12 (Integration & Backend)**

- [ ] Design API contracts between modules (sketch endpoints: /predict_eta, /get_route, /hospital_ranking, /dispatch_assign)
- [ ] Build FastAPI/Flask wrapper for GNN inference (loads .pt file, returns ETA <500 ms)
- [ ] Test model serving latency across 100 queries
- [ ] Create Docker Dockerfile + docker-compose.yml for full stack
- [ ] Coordinate with Arisha: ensure dashboard APIs are correctly called

#### **Weeks 13–15 (Testing & Paper)**

- [ ] Execute 4 scenario tests:
  - Monsoon detour: Kharghar flooding → routes avoid, ETA +15%
  - MIDC rush hour: Thane-Belapur penalized, alternative routes generated
  - Multi-ambulance: 3 simultaneously → 3 unique optimal routes
  - Hospital re-ranking: bed update → recommender re-scores
- [ ] Setup GitHub Actions CI/CD (auto-run unit tests on push)
- [ ] Write research paper **Sections 3–4:** Methodology (GNN architecture, training procedure, dataset details), Results (3-model comparison table, SHAP plots)
- [ ] Create DEPLOYMENT.md: Docker commands, environment setup, quick-start guide

### **Key Attributes**

- **Python Skills:** Advanced (PyTorch, OSMnx, NetworkX, Pandas)
- **Leadership:** Coordinates across 4 team members, unblocks dependencies
- **Timeline:** Must deliver road graph by Week 4 (blocks Turya & Anjanaa)
- **Hardware:** Ryzen 5 CPU (use Google Colab GPU for GNN training)

### **GitHub Responsibilities**

- Manage main README
- Create & assign issues
- Review PRs from team
- Manage Project tab (milestones, progress tracking)
- Maintain clean commit history

---

## **ROLE 2: ML ENGINEER** 🤖

**Assigned To:** Anjanaa Lunia  
**Enrollment:** A70405223130

### **Primary Responsibility**

Develop baseline ML models, create hospital recommender, perform explainability analysis, support Sriya with GNN.

### **Modules Owned**

- **Module 1 (Part):** Random Forest Baseline + LSTM Temporal Model
- **Module 4:** Hospital Recommendation Engine
- **Support:** SHAP explainability analysis for all models

### **Weekly Deliverables by Phase**

#### **Weeks 1–2 (Setup)**

- [ ] Participate in team setup
- [ ] Understand feature engineering design from Sriya
- [ ] Review timeline and dependencies

#### **Weeks 3–4 (Data Preparation)**

- [ ] Download Uber Movement historical traffic data for Mumbai
- [ ] Extract average speeds per road segment
- [ ] Create baseline speed lookup table: {road_segment_id → speed_kmh}
- [ ] Engineer temporal features: hour_of_day, day_of_week, is_monsoon, is_festival, is_peak_hour, is_midc_zone
- [ ] Handle missing data: fallback to road-type average speeds
- [ ] Prepare dataset splits: 70% train, 15% val, 15% test (5,000 samples target)
- [ ] Save: `data/processed/train.csv`, `val.csv`, `test.csv`

#### **Weeks 5–6 (Baseline Models)**

- [ ] **Random Forest:**
  - Features: segment_length, road_type, hour_of_day, day_of_week, monsoon, festival, is_bridge, is_midc
  - Target: ETA (minutes)
  - Hyperparams: max_depth=10, n_estimators=50, cv=5
  - Evaluate: MAE, RMSE on validation set
  - Save: `models/trained/rf_baseline.pkl`
  - **TARGET: MAE ≈ 4.2 minutes (baseline)**
- [ ] **LSTM Temporal:**
  - Input: 10-step temporal sequences of historical speeds
  - Architecture: LSTM(64) → Dense(32) → Dense(1)
  - Epochs: 50 with early stopping on val_loss
  - Save: `models/trained/lstm_baseline.h5`
  - **TARGET: MAE ≈ 3.9 minutes**

- [ ] Document metrics: training time, convergence behavior

#### **Weeks 7–9 (Hospital Recommender & SHAP)**

- [ ] **SHAP Feature Importance:**
  - Run SHAP on all 3 models (RF, LSTM, GNN from Sriya)
  - Identify top 5 features driving ETA predictions
  - Generate summary plots: beeswarm, force plots
  - **Example output:** "Bridge bottlenecks = 28%, MIDC surge = 22%, monsoon = 18%"
  - Save: `data/processed/shap_analysis.png`

- [ ] **Hospital Recommender Module:**
  - Load 10 NMMC hospitals: name, lat/lon, bed_capacity, available_beds, specializations
  - Implement scoring: Score = -ETA + (available_beds/capacity × 10) + (underserved_zone_weight × 5)
  - Apply 2× weight boost for underserved zones: Ulwe, Dronagiri
  - Function: `recommend_hospitals(incident_lat, incident_lon, eta_estimates) → top_3_ranked`
  - **TARGET: Return top 3 hospitals within 30 seconds**
  - Auto-generate pre-alert template: "ALS ambulance ETA 8 min, trauma case, send to bed #7"
  - Save: `modules/ml/hospital_recommender.py`

#### **Weeks 10–12 (Validation & Documentation)**

- [ ] Unit test hospital recommender: 20 test cases
- [ ] Document all baseline model hyperparameters in `docs/model_specifications.md`
- [ ] Create model comparison table (RF vs LSTM vs GNN) with:
  - MAE (minutes)
  - RMSE (minutes)
  - Training time (minutes)
  - Inference latency (ms)
  - Code complexity (lines)

#### **Weeks 13–15 (Paper & Evaluation)**

- [ ] Scenario testing: Hospital re-ranking on bed availability update (Scenario 4)
- [ ] Write research paper **Sections 2 & 5:**
  - Section 2: Literature Survey (existing EMS prediction systems, their gaps)
  - Section 5: Results (3-model comparison table, SHAP explainability plots, hospital recommender validation)
- [ ] Validate final model metrics on held-out test set

### **Key Attributes**

- **Python Skills:** Advanced (Scikit-learn, Keras/TensorFlow, SHAP, Pandas)
- **Dependencies:** Receives dataset from Sriya (Weeks 3–4), must complete baselines before integrated testing
- **Deadline:** All models trained by end of Week 7 (before integration phase)
- **Critical:** SHAP analysis is crucial for research paper credibility

---

## **ROLE 3: ROUTING & DISPATCH ENGINEER** 🗺️

**Assigned To:** Turya Kalburgi  
**Enrollment:** A70405223142

### **Primary Responsibility**

Develop pathfinding algorithm, implement multi-type ambulance dispatch logic, optimize routes in real-time.

### **Modules Owned**

- **Module 2:** Dynamic A\* Route Optimizer
- **Module 3:** Multi-Type Ambulance Dispatch Classifier

### **Weekly Deliverables by Phase**

#### **Weeks 1–4 (Setup & Validation)**

- [ ] Participate in team setup (Weeks 1–2)
- [ ] Receive road_graph.pkl from Sriya (Weeks 3–4)
- [ ] Load graph & validate connectivity on 10 manual test routes
- [ ] Verify shortest-path queries return correct paths
- [ ] Study A\* algorithm, haversine distance formula

#### **Weeks 5–7 (A\* Pathfinding Development)**

- [ ] **Implement A\* Algorithm:**
  - Heuristic: straight-line distance (lat/lon → km using haversine)
  - Edge weights: Initially baseline speeds, later GNN predictions from Sriya
  - Output: List of (path, total_time_min, turn_sequence)
  - Generate **top 3 fastest routes** in ranked order

- [ ] **Performance Optimization:**
  - **TARGET: Route generation < 2 seconds for any source-destination pair**
  - Load test: 5 simultaneous route requests, all <1 sec each
  - Save: `modules/routing/route_optimizer.py`

- [ ] **Unit Tests (10+ test cases):**
  - Empty path (source = destination)
  - Unreachable destination (graceful error handling)
  - Monsoon scenario: Kharghar flooded → verify route avoids flooded segment
  - MIDC rush hour: Thane-Belapur penalized → alternative routes generated
  - Bridge bottleneck: Vashi bridge busy → non-Vashi route preferred
  - Multi-start: same destination, different sources → different optimal routes

#### **Weeks 8–9 (Dispatch Classifier & Integration)**

- [ ] **Integrate GNN Predictions:**
  - Receive GNN model from Sriya or API endpoint
  - Update edge weights dynamically with GNN ETA estimates
  - Test: routes change when traffic conditions change

- [ ] **Dynamic Re-routing:**
  - Trigger condition: predicted ETA delta > 2 minutes from original
  - Notification to ambulance: new route + updated ETA
  - **TARGET: Re-routing latency < 1 second**

- [ ] **Ambulance Type Dispatcher:**
  - Manually label 50 incident locations: road_width, zone_density, accessibility
  - Train classifier: Random Forest or Scikit-learn pipeline
  - Features: road_width, population_density, building_height_avg, lane_count
  - **Dispatch Rules:**
    - Wide arterial road + standard case → **ALS** (Advanced Life Support van)
    - Narrow residential lane + standard case → **Mini-ambulance** (Tata Ace)
    - Slum interior (no vehicle access) → **Bike ambulance** (first responder)
    - **Critical cardiac case:** Override all rules → **ALS** (priority)
  - **TARGET: 95%+ accuracy on validation set (50-case test)**
  - Save: `modules/routing/dispatch_classifier.py`

- [ ] Unit tests: 20 test cases covering road type, zone, case severity combinations

#### **Weeks 10–12 (Testing & Documentation)**

- [ ] Scenario testing:
  - Scenario 1: Monsoon detour test
  - Scenario 2: MIDC rush hour test
  - Scenario 3: Multi-ambulance dispatch (3 simultaneous calls → 3 unique routes)
- [ ] Create algorithm documentation: A\* complexity analysis, why <2 sec is achievable for Navi Mumbai graph size
- [ ] Integration test with Sriya's APIs (GNN + your routing)

#### **Weeks 13–15 (Integration & Presentation)**

- [ ] Full integration: Dashboard (Arisha) → your routing APIs → ambulances get correct routes
- [ ] Performance benchmarking report
- [ ] Prepare presentation section: Live demo of A\* re-routing, dispatch classifier in action
- [ ] Final validation: All 4 scenarios pass ✓

### **Key Attributes**

- **Python Skills:** Intermediate+ (NetworkX, Scikit-learn, algorithm optimization)
- **Math Knowledge:** Graph algorithms, heuristic search, optimization
- **Dependencies:** Needs road_graph.pkl from Sriya (Week 4), GNN predictions available by Week 7
- **Performance Critical:** Sub-2-sec routing is essential for Real-time dispatch

---

## **ROLE 4: FRONTEND DEVELOPER + PAPER LEAD** 🎨

**Assigned To:** Arisha Khan  
**Enrollment:** A70405223103

### **Primary Responsibility**

Build user-facing dashboards, create live tracking interface, compile research paper, prepare final presentation.

### **Modules Owned**

- **Module 5:** Citizen Live Tracking Interface
- **Module 6:** Dispatcher Dashboard
- **Research:** Lead paper compilation + presentation slides

### **Weekly Deliverables by Phase**

#### **Weeks 1–2 (Design & Setup)**

- [ ] Create UI/UX wireframes (pen & paper or Figma):
  - Citizen view: Interactive Folium map, ambulance marker, ETA timer, delay message
  - Dispatcher view: Fleet status table, live map, incident queue, 4 KPI cards
  - Mobile responsiveness mockups
- [ ] Define color scheme:
  - ALS van: 🔴 Red
  - BLS van: 🟠 Orange
  - Mini-ambulance: 🟡 Yellow
  - Bike ambulance: 🔵 Blue
- [ ] Setup Streamlit project structure: `ui/citizen_tracker.py`, `ui/dispatcher_dashboard.py`

#### **Weeks 3–7 (Component Development)**

- [ ] Create reusable Streamlit components library:
  - `render_folium_map(center_lat, center_lon, ambulances, hospitals)`
  - `render_eta_countdown(initial_eta_seconds, update_interval_sec)`
  - `render_fleet_status_table(ambulance_list)`
  - `render_incident_queue(incidents)`
  - `render_kpi_cards(avg_response_time, active_incidents, completed_cases, eta_accuracy)`
  - Save: `ui/components.py`

#### **Weeks 8–10 (Citizen Tracker)**

- [ ] **Citizen Live Tracker Page (`ui/citizen_tracker.py`):**
  - Folium map: Navi Mumbai basemap, 10 hospital markers (clickable for details)
  - Live ambulance marker: moves along A\* route in real-time (updates every 5 sec)
  - ETA countdown: live timer (minutes:seconds format), updates dynamically
  - Delay reason display: toast notification + text below map
    - Example: "Delayed due to waterlogging on Kharghar Sector 7 Road"
    - Example: "Rerouting due to traffic on Sion-Panvel Highway"
  - Input form (for testing): ambulance_id, incident_lat, incident_lon
  - Auto-refresh: every 5 seconds, preserves map center
  - Visual: color-coded ambulance markers (ALS=red, BLS=orange, etc.)
  - **TARGET: <5 second update latency, no map lag on 5 ambulances**

#### **Weeks 10–12 (Dispatcher Dashboard)**

- [ ] **Dispatcher Dashboard Page (`ui/dispatcher_dashboard.py`) - Multi-tab Interface:**
  - **Tab 1: Fleet Status**
    - Table: ambulance_id, type, location, status, availability
    - Real-time update, sortable by type/status
  - **Tab 2: Map View**
    - Interactive Folium map: all ambulances + incidents live
    - Zoom/pan smooth, <200ms response time
    - Info popups: ambulance details on click
  - **Tab 3: Incident Queue**
    - Table: incident_id, priority, caller_lat, caller_lon, assigned_ambulance, status
    - Incoming calls appear in real-time
  - **Tab 4: KPIs**
    - 4 metric cards (large, readable):
      - "Avg Response Time Today: 12.5 min"
      - "Active Incidents: 7"
      - "Completed Cases (24h): 43"
      - "ETA Accuracy: 94.2%"
  - **TARGET: No lag on 5+ ambulances + incidents, responsive on tablet**

- [ ] **Simulation Backend Support:**
  - Create ambulance trajectory simulator: moves along route, updates coordinates every iteration
  - Simulates monsoon delay at 60% mark: ETA increases by 15%
  - Simulates hospital bed update: recommender re-ranks, pre-alert generated
  - Save: `modules/simulation.py`

#### **Weeks 12–13 (Polish & Testing)**

- [ ] UI/UX polish:
  - Responsive design (works on desktop, tablet, mobile)
  - Dark mode toggle (for dispatcher night shifts)
  - Accessibility: alt text, heading hierarchy, keyboard navigation
  - Error handling: graceful fallbacks if ambulance location unavailable

- [ ] Manual QA checklist:
  - [ ] Ambulance spawns at random initial location
  - [ ] Citizens see live tracking with <5 sec latency
  - [ ] Route recalculates on simulated traffic change
  - [ ] Hospital recommendations update in real-time
  - [ ] Folium map zoom/pan smooth on full road graph
  - [ ] Dispatcher sees all 5 ambulances without lag
  - [ ] Incident queue updates as new calls come in

- [ ] Load testing: 5 simultaneous user sessions on citizen tracker (no crashes)
- [ ] Record live demo video: "Citizen places call → ambulance assigned → live tracking → hospital arrival" (2-3 min)

#### **Weeks 13–15 (Research Paper & Presentation)**

- [ ] **Compile Full IEEE Research Paper (6–8 pages):**
  - **Section 1: Abstract** (300 words max)
    - Problem, proposed solution, results, impact
  - **Sections 2–3:** From team (Anjanaa: literature review, Sriya: methodology)
  - **Section 4: System Architecture** (YOU)
    - 5-layer architecture diagram
    - Module interactions, API contracts
  - **Sections 5–6:** From team (Anjanaa: results/SHAP, Sriya: conclusions)
  - **References:** Consolidate all 50+ citations
  - Format: IEEE style via Overleaf (LaTeX template)
  - Target: Acceptable-quality draft, ready for final review

- [ ] **Create Presentation Slides (20 min delivery):**
  - Title slide: Project, team, institution
  - Problem statement: Maharashtra EMS crisis (1 slide)
  - Solution overview: 6 modules (1 slide)
  - Architecture diagram: Data flow (1 slide)
  - Demo walkthrough: GNN → Routing → Dispatcher → Citizen tracker (3 slides + live demo 5 min)
  - Results: Model comparison, scenario tests (2 slides)
  - Key findings: India-specific insights (1 slide)
  - Conclusions & future work (1 slide)
  - Q&A (10 min)

- [ ] **Record Demo Video:**
  - Scenario: Full journey from emergency call to hospital arrival
  - Show: GNN ETA, route selection, dispatch decision, live tracking, hospital pre-alert
  - Include: Monsoon detour example, multi-ambulance coordination example
  - Duration: 3-5 minutes, high quality (1080p+)

### **Key Attributes**

- **Design Skills:** UI/UX thinking, responsive design, user empathy
- **Streamlit Expertise:** Component design, state management, performance optimization
- **Writing Skills:** Research paper compilation, clear technical communication
- **Dependencies:** Receives APIs from Sriya (routing), Turya (dispatch), Anjanaa (hospital) by Week 12
- **Timeline:** Can work independently until Week 10 (wireframes, components), then integrates all APIs

---

## **Team Interdependencies**

```
Weeks 1–4: PARALLEL (minimal dependencies)
  ├─ Sriya: Road graph extraction + EDA
  ├─ Anjanaa: Data preprocessing, awaiting Sriya's dataset
  ├─ Turya: A* algorithm design, awaiting Sriya's road graph
  └─ Arisha: UI/UX design (fully independent)

Weeks 5–7: SEQUENTIAL (Sriya → Anjanaa, Turya)
  ├─ Sriya: GNN training (BLOCKS approval of baseline models)
  ├─ Anjanaa: RF/LSTM training (can start, but timing matters)
  ├─ Turya: A* refinement (awaiting GNN for edge weights)
  └─ Arisha: Streamlit components (fully independent)

Weeks 8–9: INTEGRATION phase
  ├─ Sriya: GNN API wrapper (needed by Turya for routing)
  ├─ Turya: Re-routing + dispatch (uses Sriya's GNN)
  ├─ Anjanaa: Hospital recommender (uses Sriya's GNN for ETA)
  └─ Arisha: Mockups dashboard structure

Weeks 10–12: ASSEMBLY phase
  ├─ All: Integrate APIs into Arisha's dashboards
  ├─ Arisha: Connect all 4 APIs to frontend
  └─ Sriya: Docker containerization

Weeks 13–15: VALIDATION & PUBLICATION
  ├─ All: Scenario testing + bug fixes
  ├─ Anjanaa + Arisha: Research paper writing
  ├─ Arisha: Final presentation slides + demo video
  └─ Sriya: Code cleanup + GitHub submission prep
```

---

## **Communication Protocol**

**Daily:** 10 AM async update on Slack/Teams

- 1 sentence: What did you complete?
- 1 sentence: What are you working on?
- 1 sentence: Any blockers?

**Weekly:** Friday 6 PM (30 min video sync)

- Review progress against timeline
- Discuss dependencies and blockers
- Plan next week

**GitHub:**

- Create issues for each task
- Assign to responsible person with due date
- Use milestones for phases
- PR reviews: 1 approval before merge

---

**Last Updated:** March 29, 2026  
**Next Review:** April 5, 2026 (End of Phase 1)  
**Document Owner:** Sriya (Team Lead)
