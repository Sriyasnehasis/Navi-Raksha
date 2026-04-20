# 🚑 NaviRaksha — RF-Based Emergency Medical Response System

> **Intelligent Ambulance Dispatch & ETA Prediction for Navi Mumbai**
> 
> Amity University Mumbai | Final Year Research Project | 2026

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25-red)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Overview

NaviRaksha is an AI-powered Emergency Medical Services (EMS) platform that optimizes ambulance dispatch and routing in **Navi Mumbai, India**. The system combines:

- **Machine Learning** — ETA prediction using Random Forest, LSTM, and GNN models
- **A\* Routing** — Traffic-aware pathfinding on real OSM road networks
- **Smart Dispatch** — Severity-based ambulance type classification (ALS/BLS/Mini/Bike)
- **Hospital Ranking** — Dynamic ranking by ETA + bed availability
- **Real-time Dashboard** — Live fleet tracking with interactive maps

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                         │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │ Citizen      │  │ Dispatcher    │  │ Simulation       │  │
│  │ Tracker      │  │ Control Room  │  │ Engine           │  │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────────┘  │
│         └──────────────────┼─────────────────┘              │
│                            │ REST API                        │
├────────────────────────────┼─────────────────────────────────┤
│                    FLASK BACKEND API                          │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ /predict  │  │ /dispatch│  │ /ambulances│  │ /hospitals│  │
│  │ -eta      │  │          │  │ /active    │  │           │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
│       │              │              │              │         │
│  ┌────┴─────┐  ┌────┴──────┐  ┌────┴──────┐               │
│  │ RF Model │  │ Dispatch  │  │ SQLAlchemy │               │
│  │ (ML)     │  │ Classifier│  │ Database   │               │
│  └──────────┘  └───────────┘  └───────────┘               │
└──────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### 1. Clone & Setup
```bash
git clone https://github.com/Sriyasnehasis/Navi-Raksha.git
cd navi-raksha
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Start Backend API
```bash
.venv\Scripts\python.exe modules\backend\app.py
# Server runs on http://localhost:8000
```

### 3. Start Frontend Dashboard
```bash
cd ui
.venv\Scripts\streamlit.exe run app.py
# Dashboard runs on http://localhost:8501
```

### 4. Run Tests
```bash
python tests/test_all.py
```

### 5. Docker (Optional)
```bash
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:8501
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check + model status |
| POST | `/predict-eta` | Predict ambulance ETA |
| POST | `/dispatch` | Full emergency dispatch |
| GET | `/ambulances/active` | List active ambulances |
| GET | `/incidents/active` | List active incidents |
| GET | `/hospitals` | List hospitals with beds |
| POST | `/admin/db/seed` | Seed sample data |
| POST | `/admin/db/reset` | Reset database |

**Full CRUD** available for ambulances, incidents, and hospitals via `/admin/` endpoints.

## 🧠 ML Models

| Model | MAE | RMSE | R² | Status |
|-------|-----|------|-----|--------|
| **Random Forest** | 0.066 min | 0.15 min | 0.998 | ✅ Production |
| LSTM | 0.101 min | 0.204 min | 0.998 | Backup |
| GNN | 0.110 min | 0.219 min | 0.997 | Research |

> RF was selected for production due to superior MAE. All 3 models were trained on 10,000 realistic EMS trip samples with 19 engineered features.

## 📁 Project Structure

```
navi-raksha/
├── modules/
│   ├── backend/          # Flask API (app.py, models.py, services.py)
│   ├── routing/          # A* router, dispatch classifier, hospital ranker
│   └── ml/               # Model loading utilities
├── ui/                   # Streamlit dashboard (3 pages)
├── models/trained/       # RF, LSTM, GNN model files
├── data/
│   ├── processed/        # Train/Val/Test CSVs (8K/1K/1K)
│   └── raw/              # OSM graph, hospitals CSV, key locations
├── notebooks/            # 9 training notebooks
├── tests/                # Comprehensive test suite (30+ tests)
├── docs/                 # Team guides, API contracts, plans
├── Dockerfile.backend    # Docker for API
├── Dockerfile.frontend   # Docker for Streamlit
└── docker-compose.yml    # Full stack deployment
```






