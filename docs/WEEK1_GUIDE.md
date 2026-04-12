# 🚀 NaviRaksha: Week 1 Sprint Guide (Mar 29 - Apr 6)

## ✅ Completed (Today - Mar 29)

- [x] Python venv setup (`navi_env`)
- [x] requirements.txt fixed for Windows
- [x] Packages installing (setuptools, wheel, pandas, numpy, torch, osmnx, tensorflow, etc.)
- [x] Road graph extraction notebook created (`notebooks/01_extract_road_graph.ipynb`)
- [x] Code committed to GitHub

**Status:** ~20% of Week 1 complete ✅

---

## ⏳ Next: ROAD GRAPH EXTRACTION (Deadline: Apr 2, 11:59 PM)

### **Step 1: Wait for Package Installation (3-5 minutes)**

Once pip finishes, verify installation:

```powershell
.\navi_env\Scripts\Activate.ps1
python -c "import osmnx, torch, pandas; print('✓ All packages OK')"
```

### **Step 2: Run Road Graph Extraction Notebook**

- Open VS Code folder: `c:\Users\sriya\Desktop\Learner\navi-raksha`
- Open notebook: `notebooks/01_extract_road_graph.ipynb`
- Configure Python kernel: Select `navi_env` interpreter
- Run all cells (starts with `01_extract_road_graph.py` → Cell 1)
- **Expected output:**
  - Road network: ~5000-10000 nodes extracted from OSM
  - Key locations: 50+ validated city nodes
  - Files saved: `data/raw/navi_mumbai_road_graph.pkl` (main file)
  - **Duration:** ~10-15 minutes (OSM API query slower on first run)

### **Step 3: Verify Output Files**

After notebook completes, check:

```powershell
ls data/raw/
```

Should see:

- `navi_mumbai_road_graph.pkl` (~5-10 MB) ✅
- `key_locations.csv` (50+ rows) ✅
- `navi_mumbai_edges.geojson` ✅
- `navi_mumbai_road_graph.graphml` ✅

### **Step 4: Commit to GitHub**

```powershell
git add data/
git commit -m "Add Navi Mumbai road network extraction (5000+ nodes, 50+ key locations)"
git push origin main
```

---

## 📋 Parallel Tasks (For Team - Assign Now)

**While you extract road graph, direct team to start:**

### **Anjanaa (ML Engineer):**

- [ ] Download Uber movement traffic data: https://movement.uber.com/
- [ ] Create feature engineering pipeline notebook
- [ ] Prepare train/val/test dataset splits (target: 500 samples by Apr 5)
- **Deadline:** Apr 4

### **Turya (Routing Engineer):**

- [ ] Study A\* algorithm (Wikipedia + GeeksforGeeks)
- [ ] Prepare to receive road graph file on Apr 2
- [ ] Write skeleton of `modules/routing/route_optimizer.py`
- **Deadline:** Apr 5

### **Arisha (Frontend Lead):**

- [ ] Create Streamlit project structure:
  ```
  ui/
  ├── citizen_tracker.py
  ├── dispatcher_dashboard.py
  └── components.py
  ```
- [ ] Download Folium examples, test simple map
- **Deadline:** Apr 5

---

## 🎯 Week 1 Checkpoint (Apr 6)

**Team Sync - Friday 6 PM**

Mark as DONE ✅:

- [ ] Road graph extracted & validated (Sriya)
- [ ] Dataset pipeline ready (Anjanaa)
- [ ] A\* skeleton written & tested (Turya)
- [ ] UI components stubbed out (Arisha)
- [ ] All code pushed to GitHub

**If BLOCKED:**

- Road graph OSM errors? → Use cached copy from GitHub
- Data download slow? → Use mock data (500 synthetic samples)
- Package install fails? → Try `pip install <package>` individually

---

## 🔄 Daily Standup Template

**Time:** 10 AM daily (Slack/Teams)

Post this format:

```
✅ Yesterday: [1-2 things completed]
⏳ Today: [1-2 things you'll do]
🚫 Blockers: [Any issues? Ask here]
```

Example:

```
✅ Yesterday: Extracted road graph (5200 nodes), validated 50 city locations
⏳ Today: Run full EDA, create training data notebook
🚫 Blockers: None
```

---

## 📞 How to Get Help

**Technical Issues:**

- Package install errors → Try `pip list` to debug
- Notebook won't run → Check kernel selection (should be `navi_env`)
- OSM API timeout → Network issue, retry with `ox.config(timeout=30)`

**Project Questions:**

- Check `PROJECT_PLAN.md` for scope
- Check `TEAM_ROLES.md` for who owns what
- Ask in team Slack #naviraksha-dev channel

---

## 📊 Timeline Reminder

```
WEEK 1 (Mar 30-Apr 6):   ← YOU ARE HERE
  ├─ Road graph (Sriya) - Due Apr 2
  ├─ Data pipeline (Anjanaa) - Due Apr 4
  └─ Routing/UI setup (Turya/Arisha) - Due Apr 5

WEEK 2 (Apr 7-13):       Models start training
WEEK 3 (Apr 14-20):      Advanced features (SHAP, Hospital recommender)
WEEK 4 (Apr 21-27):      Integration & testing
WEEK 5 (Apr 28-May 1):   Paper & submission
```

**You have ~200 hours of team work total, 34 days deadline.**

**Status:** On track ✅

---

## 🚀 Ready?

1. Wait for pip to finish (5-10 min)
2. Test: `python -c "import osmnx; print('OK')"`
3. Run notebook: `notebooks/01_extract_road_graph.ipynb`
4. Push to GitHub
5. Move to data engineering phase

**Questions? Slack the team channel.**

Good luck! 💪
