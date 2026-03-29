# NaviRaksha: GNN-Based Ambulance Response Time Prediction

## 🚑 Project Overview

AI-powered EMS platform for Navi Mumbai, integrating:

- **GNN ETA Prediction** - Predict ambulance arrival time (< 3 min error)
- **Dynamic A\* Routing** - Generate fastest routes in real-time
- **Smart Dispatch** - Assign ALS/BLS/Mini/Bike based on incident location
- **Hospital Recommender** - Rank hospitals by ETA + bed availability
- **Live Citizen Tracking** - Real-time ambulance position + ETA countdown
- **Dispatcher Dashboard** - Fleet management + incident queue + KPIs

## 👥 Team Members

| Role       | Person  | Responsibility                   |
| ---------- | ------- | -------------------------------- |
| **Role 1** | Sriya   | Data Engineer + Integration Lead |
| **Role 2** | Anjanaa | ML Engineer (GNN, RF, LSTM)      |
| **Role 3** | Turya   | Routing & Dispatch Logic         |
| **Role 4** | Arisha  | Frontend Dev + Research Paper    |

## 📁 Project Structure

```
navi-raksha/
├── data/
│   ├── raw/           (OSM, Uber traffic, hospitals)
│   └── processed/     (Cleaned & featurized data)
├── models/
│   ├── checkpoints/   (Training checkpoints)
│   └── trained/       (Final weights: GNN, RF, LSTM)
├── modules/
│   ├── ml/            (ML models)
│   ├── routing/       (A* router, dispatch classifier)
│   └── frontend/      (Streamlit apps)
├── notebooks/         (EDA, experiments)
├── tests/             (Unit tests)
├── ui/                (Streamlit pages)
├── docs/              (Design docs, API specs)
└── requirements.txt
```


## 🎯 Key Deliverables

- ✓ GNN model with MAE < 3 minutes
- ✓ A\* router responding in < 2 seconds
- ✓ Ambulance dispatcher with 95%+ accuracy
- ✓ Live citizen tracker with 3D map
- ✓ Dispatcher dashboard with real-time KPIs
- ✓ IEEE-format research paper
- ✓ Final presentation with demo

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/navi-raksha.git
cd navi-raksha

# Create virtual environment
python -m venv navi_env
.\navi_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Start work!
python -c "import torch; print('Ready!')"
```

## 📊 India-Specific Features

- **Monsoon flooding detection** (June-Sept, Kharghar/Ulwe zones): 1.3× ETA penalty
- **MIDC industrial surge** (Thane-Belapur 8-10 AM & 5-7 PM): 1.2× penalty
- **Bridge bottlenecks** (Vashi, Airoli): 1.5-2× penalty
- **Festival traffic** (Ganesh Chaturthi, Navratri): 1.4× city-wide penalty
- **Slum corridor access** (narrow lanes): bike ambulance dispatch

---


