# 🚑 NaviRaksha: GNN-Based Emergency Medical Services Platform

## 📌 Project Status (Apr 7, 2026)

**Phase:** 🟢 Active Development | **Timeline:** Apr 7 - May 1, 2026 | **Target:** Production Ready

### ✅ Completed

- Dataset generation (10,000 realistic EMS OD pairs)
- RF baseline model (4.2 min MAE)
- 4 training notebooks (RF, LSTM, GNN analysis)
- Google Drive integration
- Git workflow setup (main + test branches)

### 🔄 In Progress

- LSTM training (target: MAE < 3.9 min)
- GNN training (target: MAE < 3.0 min)

### ⏳ Pending

- Routing module (Turya)
- Frontend development (Arisha)
- Paper writing & submission

---

## 🚑 Project Overview

AI-powered EMS platform for Navi Mumbai, integrating:

- **GNN ETA Prediction** 🟢 Notebooks Created | Predict ambulance arrival time (< 3 min error)
- **LSTM ETA Prediction** 🟢 Notebooks Created | Alternative deep learning approach
- **Dynamic A\* Routing** ⏳ In Development | Generate fastest routes in real-time
- **Smart Dispatch** ⏳ Planned | Assign ALS/BLS/Mini/Bike based on incident location
- **Hospital Recommender** ⏳ Planned | Rank hospitals by ETA + bed availability
- **Live Citizen Tracking** ⏳ Planned | Real-time ambulance position + ETA countdown
- **Dispatcher Dashboard** ⏳ Planned | Fleet management + incident queue + KPIs

---

## 👥 Team Members & Assignments

| Name        | Role                    | Assigned Task                   | Branch                |
| ----------- | ----------------------- | ------------------------------- | --------------------- |
| **Sriya**   | Data Engineer + Lead    | Dataset generation ✅ Complete  | main / test shared    |
| **Anjanaa** | ML Engineer             | GNN training + validation       | test (merged to main) |
| **Turya**   | Routing Developer       | A\* routing + dispatch logic    | test (merged to main) |
| **Arisha**  | Frontend + Paper Writer | Streamlit frontend + IEEE paper | test (merged to main) |

## 📁 Project Structure

````
navi-raksha/
├── notebooks/                        # 🟢 Training notebooks (READY FOR USE)
│   ├── 01_dataset_generation.ipynb   # Dataset creation (10K samples) ✅
│   ├── 02_random_forest_detailed.ipynb # RF baseline (4.2 min MAE) ✅
│   ├── 03_lstm_training.ipynb        # LSTM training pipeline 🟢
│   └── 04_gnn_training.ipynb         # GNN training pipeline 🟢
├── data/
│   ├── raw/                    (OpenCity violations, OSM graph, hospitals)
│   ├── processed/              (✅ train_real.csv, val_real.csv, test_real.csv)
│   └── trained/                (✅ rf_baseline_real.pkl)
├── models/
│   ├── checkpoints/            (Training checkpoints)
│   └── trained/                (Final weights: RF, LSTM, GNN)
├── modules/
│   ├── ml/                     (ML models)
│   ├── routing/                (A* router, dispatch classifier)
│   └── frontend/               (Streamlit apps)
├── tests/                      (Unit tests)
├── ui/                         (Streamlit pages)
├── docs/                       (Design docs, API specs)
├── .gitignore                  (Updated: notebooks enabled)
├── requirements.txt            (Dependencies)
└── README.md                   (This file)


## 🎯 Key Deliverables & Progress

| Deliverable | Target | Status | Notes |
|---|---|---|---|
| **Dataset** | 10K OD pairs | ✅ Complete | train/val/test CSVs ready |
| **RF Baseline** | 4.2 min MAE | ✅ Complete | Trained & evaluated |
| **LSTM Model** | < 3.9 min MAE | 🟢 Ready | Notebook created, awaiting execution |
| **GNN Model** | < 3.0 min MAE | 🟢 Ready | Notebook created, awaiting execution |
| **A\* Router** | < 2 sec response | ⏳ In Progress | Turya's module |
| **Dispatch Logic** | 95%+ accuracy | ⏳ In Progress | Turya's module |
| **Frontend UI** | Live dashboard | ⏳ In Progress | Arisha's responsibility |
| **Research Paper** | IEEE format | ⏳ In Progress | Arisha's responsibility |
| **Production Ready** | May 1, 2026 | 🎯 Target | Full integration & deployment |

## 🚀 Quick Start Guide

### For Teammates (All members)

```bash
# 1. Clone repository
git clone https://github.com/Sriyasnehasis/Navi-Raksha.git
cd navi-raksha

# 2. Checkout test branch (active development)
git checkout test
git pull origin test

# 3. Create & activate virtual environment
python -m venv navi_env
.\navi_env\Scripts\activate  # Windows
# or
source navi_env/bin/activate  # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run a notebook
jupyter notebook notebooks/02_random_forest_detailed.ipynb
```

### For Running Training Notebooks

```bash
# Dataset Generation (completed, for reference)
jupyter notebook notebooks/01_dataset_generation.ipynb

# RF Baseline Analysis (ready to run)
jupyter notebook notebooks/02_random_forest_detailed.ipynb

# LSTM Training (ready to run)
jupyter notebook notebooks/03_lstm_training.ipynb

# GNN Training (ready to run)
jupyter notebook notebooks/04_gnn_training.ipynb
```

### For Team Lead (Sriya)

```bash
# Check test branch progress
git checkout test
git pull origin test

# After testing, merge to main
git checkout main
git merge test
git push origin main
```

### Git Workflow

- **`main` branch**: Production code (merged only after testing)
- **`test` branch**: Development & testing (where everyone commits)

---

## 📊 Dataset Overview (Apr 7, 2026)

**Location:** Navi Mumbai (5 zones: Vashi, Nerul, Kharghar, Belapur, Airoli)

**Dataset Specs:**
- **Samples:** 10,000 realistic EMS trips
- **Train/Val/Test Split:** 8,000 / 1,000 / 1,000 (80/10/10)
- **Features:** 19 features (distance, time, zone, weather, violations, etc.)
- **Target:** ETA in minutes (min: 3, max: 15)

**Speed Model Factors:**
- ⏰ Time-based: Peak hours (20-25 km/h) vs off-peak (35-40 km/h)
- 🚨 Violations-based: -30% impact (congestion proxy)
- 📏 Distance: 1.0-1.15x multiplier
- 🌧️ Weather: Rain -25%, Monsoon -35%

**Files:**
- `data/processed/train_real.csv` (8,000 rows)
- `data/processed/val_real.csv` (1,000 rows)
- `data/processed/test_real.csv` (1,000 rows)
- `data/trained/rf_baseline_real.pkl` (trained model)

---

## 🎓 Model Performance Targets

| Model | Input | Target MAE | Status |
|---|---|---|---|
| **RF Baseline** | 19 features | 4.2 min | ✅ Achieved |
| **LSTM** | Sequences + 19 features | < 3.9 min | 🟢 Ready |
| **GNN** | OSM graph + 19 features | < 3.0 min | 🟢 Ready |`

## 🇮🇳 India-Specific Features

**Navi Mumbai Factors:**

- **Monsoon Flooding** (June-Sept, Kharghar/Ulwe zones): 1.3× ETA penalty
- **MIDC Industrial Traffic** (Thane-Belapur 8-10 AM & 5-7 PM): 1.2× penalty
- **Bridge Bottlenecks** (Vashi, Airoli bridges): 1.5-2× penalty
- **Festival Traffic** (Ganesh Chaturthi, Navratri): 1.4× city-wide penalty
- **Slum Corridor Access** (narrow lanes, no direct routes): Bike ambulance dispatch
- **Hospital Distribution** (5 major + 12 secondary): ETA-based recommender

**Violation Hotspots (Real Data):**
- Vashi: 48,637 violations/month (highest congestion indicator)
- Nerul: 38,622 violations/month
- Used as proxy for real-time traffic patterns

---

## 📅 Project Timeline (Apr 7 - May 1)

| Week | Phase | Deliverables | Owner |
|---|---|---|---|
| **Week 1 (Apr 7-13)** | Dataset & ML | ✅ Dataset complete, RF baseline, LSTM/GNN notebooks | Sriya + Anjanaa |
| **Week 2 (Apr 14-20)** | Training | Trained LSTM & GNN models, evaluate performance | Anjanaa |
| **Week 3 (Apr 21-27)** | Integration | Routing + dispatch + frontend ready, full system test | Turya + Arisha |
| **Week 4 (Apr 28-May 1)** | Polish | Paper ready, presentation, production deployment | All |

---

## 🔧 Technical Stack

| Component | Technology | Version |
|---|---|---|
| **Data Pipeline** | Python, Pandas, NumPy | 3.9+ |
| **ML Models** | TensorFlow, PyTorch, scikit-learn | Latest |
| **GNN Library** | PyTorch Geometric | 2.3.0 |
| **Routing** | NetworkX, OSM data | Latest |
| **Frontend** | Streamlit, Folium | Latest |
| **Database** | (TBD) | |
| **Version Control** | Git + GitHub | |

---

## 📞 Contact & Support

- **Sriya (Lead):** Project management, data engineering, integration
- **Anjanaa (ML):** Model training, evaluation, optimization
- **Turya (Routing):** A* algorithm, dispatch logic, optimization
- **Arisha (Frontend):** UI/UX, paper writing, presentation

---

## 📄 License

MIT License - See LICENSE file for details

---

**Last Updated:** April 7, 2026
**Project Status:** 🟢 Active Development | **Timeline:** 24 days to launch
````
