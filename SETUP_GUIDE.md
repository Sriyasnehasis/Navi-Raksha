# Setup Guide for NaviRaksha Development Environment

This guide will help you clone the repository, setup your Python environment, and start contributing to the NaviRaksha project.

---

## 📋 Prerequisites

- **Python:** 3.10 or higher
- **Git:** Installed and configured
- **GitHub Account:** Access to the navi-raksha repository
- **Hardware:** At least 8 GB RAM (16 GB recommended for GNN training)
- **OS:** Windows 10+, macOS, or Ubuntu 20.04+

---

## 🚀 Quick Start (5 minutes)

### **Step 1: Clone Repository**

```bash
git clone https://github.com/YOUR-USERNAME/navi-raksha.git
cd navi-raksha
```

### **Step 2: Create Virtual Environment**

**Windows:**

```powershell
python -m venv navi_env
.\navi_env\Scripts\Activate.ps1
```

**Mac/Linux:**

```bash
python -m venv navi_env
source navi_env/bin/activate
```

### **Step 3: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

(Takes 15–30 minutes on first install)

### **Step 4: Verify Installation**

```bash
python -c "import torch; import osmnx; import streamlit; print('✓ All packages OK')"
```

---

## 📁 Folder Structure & What Goes Where

```
navi-raksha/
├── data/                          # All datasets
│   ├── raw/                       # Original files (don't modify)
│   │   ├── navi_mumbai_road_graph.pkl      (5.2 MB - OSM road network)
│   │   ├── uber_movement_traffic.csv       (traffic data)
│   │   └── hospitals_navi_mumbai.csv       (hospital locations & beds)
│   └── processed/                 # Cleaned & featurized datasets
│       ├── train.csv              (70% of data, for training)
│       ├── val.csv                (15% of data, for validation)
│       └── test.csv               (15% of data, for evaluation)
│
├── models/                        # Model files
│   ├── checkpoints/               # Save intermediate training states
│   │   └── gnn_epoch_50.pt        (GNN checkpoint)
│   └── trained/                   # Final trained models
│       ├── gnn_best.pt            (GNN - CRITICAL)
│       ├── rf_baseline.pkl        (Random Forest)
│       └── lstm_baseline.h5       (LSTM)
│
├── modules/                       # Python code packages
│   ├── ml/
│   │   ├── gnn.py                 (GNN model architecture)
│   │   ├── baselines.py           (RF & LSTM models)
│   │   └── hospital_recommender.py (Hospital ranking logic)
│   ├── routing/
│   │   ├── route_optimizer.py     (A* pathfinding)
│   │   ├── dispatch_classifier.py (Ambulance type assignment)
│   │   └── __init__.py
│   └── frontend/
│       └── __init__.py
│
├── notebooks/                     # Jupyter notebooks (analysis & EDA)
│   ├── 01_extract_road_graph.ipynb
│   ├── 02_road_graph_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_model_training.ipynb
│   └── 05_scenario_testing.ipynb
│
├── ui/                            # Streamlit apps
│   ├── citizen_tracker.py         (Live ambulance tracking for public)
│   ├── dispatcher_dashboard.py    (Fleet management for control room)
│   ├── components.py              (Reusable UI components)
│   └── simulation.py              (Test data generator)
│
├── tests/                         # Unit tests
│   ├── test_gnn_model.py
│   ├── test_routing.py
│   ├── test_dispatch_classifier.py
│   └── test_hospital_recommender.py
│
├── docs/                          # Documentation
│   ├── feature_engineering.md     (India-specific features: monsoon, MIDC, etc.)
│   ├── data_sources.md            (Where to download data)
│   ├── api_specification.md       (Module APIs & contracts)
│   └── deployment_guide.md        (Docker setup)
│
├── PROJECT_PLAN.md                (Main scope & timeline)
├── TEAM_ROLES.md                  (Who does what)
├── SETUP_GUIDE.md                 (This file)
├── README.md                      (Project overview)
├── requirements.txt               (Python dependencies)
├── .gitignore                     (Files to ignore in Git)
├── Dockerfile                     (Docker containerization)
└── docker-compose.yml             (Multi-container orchestration)
```

---

## 🛠️ Development Workflow

### **Before You Start**

1. Make sure you're in the `navi_env` virtual environment

   ```bash
   # Check: prompt should show (navi_env) at the start
   # If not, activate:
   .\navi_env\Scripts\Activate.ps1  # Windows
   source navi_env/bin/activate    # Mac/Linux
   ```

2. Update your local repo (in case others pushed changes)
   ```bash
   git pull origin main
   ```

### **Creating a Feature Branch**

Each person should work on their own branch:

```bash
# Create new branch (replace with your module)
git checkout -b feature/gnn-model
# OR
git checkout -b feature/routing-engine
# OR
git checkout -b feature/dashboard
```

### **Making Changes**

```bash
# Edit your files
nano modules/ml/gnn.py
# or use VS Code, PyCharm, etc.

# Test your changes
python -m pytest tests/test_gnn_model.py

# Check status
git status
```

### **Committing Changes**

```bash
# Add your changes
git add modules/ml/gnn.py
git add tests/test_gnn_model.py

# Commit with clear message
git commit -m "GNN: Implement 2-layer GCN architecture with early stopping"

# Push to GitHub
git push origin feature/gnn-model
```

### **Creating a Pull Request (PR)**

1. Go to GitHub: https://github.com/YOUR-USERNAME/navi-raksha
2. Click "Compare & pull request"
3. Fill in:
   - Title: "GNN: Implement 2-layer GCN architecture"
   - Description: What changed, why, any testing done
4. Assign a reviewer (another team member)
5. Once approved, merge to `main`

---

## 📝 Using Jupyter Notebooks

### **Start Jupyter**

```bash
jupyter notebook
# OR
jupyter lab
```

A browser window will open. Navigate to `notebooks/` folder.

### **Create a New Notebook**

1. Click "New" → "Python 3"
2. Save as: `notebooks/04_my_analysis.ipynb`
3. Add markdown title in first cell:
   ```markdown
   # GNN Model Training Analysis

   Author: Sriya
   Date: March 29, 2026
   ```

### **Best Practices**

- Keep notebooks for **exploration & visualization only**
- Move reusable code to **modules/** (e.g., `modules/ml/gnn.py`)
- Document each cell with markdown comments
- Don't commit large outputs (clear outputs before pushing)

---

## 🧪 Running Tests

### **Run All Tests**

```bash
python -m pytest tests/ -v
```

### **Run Specific Test**

```bash
python -m pytest tests/test_gnn_model.py::TestGNNArchitecture::test_forward_pass -v
```

### **Run with Coverage Report**

```bash
pip install pytest-cov
pytest tests/ --cov=modules --cov-report=html
# Open htmlcov/index.html to view
```

---

## 🚢 Running Streamlit Apps

### **Citizen Live Tracker**

```bash
streamlit run ui/citizen_tracker.py
# Opens at http://localhost:8501
```

### **Dispatcher Dashboard**

```bash
streamlit run ui/dispatcher_dashboard.py
# Opens at http://localhost:8501
```

### **Run Both (separate terminals)**

```bash
# Terminal 1:
streamlit run ui/citizen_tracker.py --logger.level=error

# Terminal 2:
streamlit run ui/dispatcher_dashboard.py --logger.level=error
```

---

## 🐳 Docker Setup (Week 12+)

### **Build Docker Image**

```bash
docker build -t navi-raksha:latest .
```

### **Run Container**

```bash
docker run -p 8501:8501 navi-raksha:latest
# Access at http://localhost:8501
```

### **Run with Docker Compose (Multiple Services)**

```bash
docker-compose up
# Starts Streamlit + backend API
```

---

## 📊 Using Google Colab for GNN Training (IMPORTANT)

**Why Colab?** Your Ryzen 5 CPU is slow for GNN (4-6 hrs/epoch). Colab free GPU: 30-60 min/epoch.

### **Setup Colab**

1. Go to https://colab.research.google.com
2. Upload your notebook: `notebooks/04_model_training.ipynb`
3. In first cell, install packages:
   ```python
   !pip install torch torch-geometric osmnx networkx pandas
   ```
4. Upload road graph pickle from `data/raw/`:
   ```python
   from google.colab import files
   uploaded = files.upload()
   # Select navi_mumbai_road_graph.pkl
   ```
5. Load and train:
   ```python
   import pickle
   G = pickle.load(open('navi_mumbai_road_graph.pkl', 'rb'))
   # Train GNN (will run on GPU automatically)
   ```
6. Download trained model:
   ```python
   files.download('gnn_best.pt')
   ```

---

## 🔧 Troubleshooting

### **"ModuleNotFoundError: No module named 'torch'"**

```bash
# Activate venv and reinstall
pip install -r requirements.txt
```

### **"OSError: /entities/road_graph.pkl: No such file or directory"**

```bash
# Check file exists
ls data/raw/
# If not, extract it:
python notebooks/01_extract_road_graph.ipynb  # Run in Jupyter
```

### **"Port 8501 is already in use"**

```bash
# Kill Streamlit process
pkill -f streamlit
# Or run on different port
streamlit run ui/citizen_tracker.py --server.port=8502
```

### **Virtual Environment Not Activating**

```powershell
# Windows - allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate again
.\navi_env\Scripts\Activate.ps1
```

---

## 📚 Learning Resources

- **PyTorch Geometric:** https://pytorch-geometric.readthedocs.io/
- **Streamlit Docs:** https://docs.streamlit.io/
- **OSMnx Guide:** https://osmnx.readthedocs.io/
- **A\* Algorithm:** https://en.wikipedia.org/wiki/A*_search_algorithm
- **Git Guide:** https://git-scm.com/book/en/v2

---

## ✅ Checklist: First-Time Setup

- [ ] Cloned repository
- [ ] Created virtual environment
- [ ] Installed all packages (no errors)
- [ ] Verified imports work
- [ ] Opened Jupyter notebook
- [ ] Created feature branch in Git
- [ ] Made first commit
- [ ] Pushed to GitHub
- [ ] Created Pull Request
- [ ] Got PR approved & merged ✓

---

## 📞 Help & Questions

- **Technical Questions:** Ask in Slack #naviraksha-dev with full error message
- **Project Questions:** Reference PROJECT_PLAN.md and TEAM_ROLES.md
- **Git Issues:** See Git section of this guide
- **Data Questions:** Check docs/data_sources.md

---

**Last Updated:** March 29, 2026  
**Owner:** Sriya (Team Lead)  
**Questions?** Ask in team Slack channel!
