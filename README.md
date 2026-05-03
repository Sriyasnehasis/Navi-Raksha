# 🚑 NaviRaksha — RF-Based Emergency Medical Response System

> **Intelligent Ambulance Dispatch & ETA Prediction for Navi Mumbai**

### 🌐 Live Production
| Service | Status | URL |
| :--- | :--- | :--- |
| **Dispatcher Intelligence Panel** | ![Firebase](https://img.shields.io/badge/Firebase-Hosting-FFCA28?style=flat&logo=firebase&logoColor=white) | [https://navi-raksha.web.app/dispatcher](https://navi-raksha.web.app/dispatcher) |
| **Citizen SOS Portal** | ![Firebase](https://img.shields.io/badge/Firebase-SOS_Portal-FFCA28?style=flat&logo=firebase&logoColor=white) | [https://navi-raksha.web.app/citizen](https://navi-raksha.web.app/citizen) |
| **Backend API Engine** | ![Render](https://img.shields.io/badge/Render-Backend-46E3B7?style=flat&logo=render&logoColor=white) | [https://navi-raksha-backend.onrender.com](https://navi-raksha-backend.onrender.com) |

---

## 📌 Overview

NaviRaksha is an AI-powered Emergency Medical Services (EMS) platform that optimizes ambulance dispatch and routing in **Navi Mumbai, India**. The system combines:

- **Machine Learning** — ETA prediction using Random Forest, LSTM, and GNN models
- **A\* Routing** — Traffic-aware pathfinding on real OSM road networks
- **Next.js Frontend** — Modern, responsive dashboard with real-time Firestore sync
- **Smart Dispatch** — Severity-based ambulance type classification (ALS/BLS/Mini/Bike)
- **Hospital Ranking** — Dynamic ranking by ETA + bed availability
- **Real-time Engine** — Live fleet tracking with automated movement simulation

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND (LIVE)                   │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────┐  │
│  │ Citizen SOS  │  │ Dispatcher    │  │ Simulation       │  │
│  │ Portal       │  │ Intel Panel   │  │ Control          │  │
│  └──────┬───────┘  └──────┬────────┘  └──────┬───────────┘  │
│         └──────────────────┼─────────────────┘              │
│                            │ REST API + Firestore Sync      │
├────────────────────────────┼─────────────────────────────────┤
│                    FLASK BACKEND ENGINE                       │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ /predict  │  │ /dispatch│  │ Movement  │  │ /hospitals│  │
│  │ -eta      │  │          │  │ Loop      │  │           │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  └─────┬─────┘  │
│       │              │              │              │         │
│  ┌────┴─────┐  ┌────┴──────┐  ┌────┴──────┐               │
│  │ RF Model │  │ Dispatch  │  │ Cloud Sync│               │
│  │ (ML)     │  │ Classifier│  │ Firestore │               │
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
│   ├── backend/          # Flask API Engine (Render)
│   ├── routing/          # A* router, dispatch classifier
│   └── ml/               # Model loading utilities
├── web/                  # Next.js Application (Firebase)
├── models/trained/       # RF, LSTM, GNN model files
├── data/
│   ├── processed/        # 10K realistic EMS trip samples
│   └── raw/              # OSM road graph, Navi Mumbai sectors
├── tests/                # Automated test suite (Pytest)
├── Dockerfile.backend    # Containerized API
└── render.yaml           # Infrastructure-as-Code for Render
```






