# 📥 Data Setup Guide for Team

## Quick Start

After cloning the repo, you need the **road graph file** (21 MB) to run the feature engineering notebooks.

---

## Option 1: Download from Google Colab (EASIEST) ✅

**Anjanaa, Turya, Arisha:**

1. **Clone the repo:**
   ```bash
   git clone https://github.com/Sriyasnehasis/Navi-Raksha.git
   cd Navi-Raksha
   ```

2. **Get the road graph file:**
   - Ask Sriya for access to: **Google Drive → NaviRaksha_Output → raw**
   - Download: `navi_mumbai_road_graph.pkl` (21 MB)
   - Save to: `data/raw/navi_mumbai_road_graph.pkl`

3. **Check if file exists:**
   ```bash
   ls data/raw/navi_mumbai_road_graph.pkl  # Should exist
   ```

4. **Done!** You can now run any notebook that loads the road graph.

---

## Option 2: Run Feature Engineering on Colab (RECOMMENDED)

**For Anjanaa + others who need training data:**

1. **Access shared Colab notebook:**
   - Sriya has shared: `03_feature_engineering_COLAB.ipynb`
   - Open in Google Colab from Drive

2. **Run all cells** (takes ~2-3 minutes)

3. **Outputs saved to:**
   - `NaviRaksha_Output/processed/train.csv` (350 samples)
   - `NaviRaksha_Output/processed/val.csv` (75 samples)
   - `NaviRaksha_Output/processed/test.csv` (75 samples)

4. **Download CSVs:**
   - Download the 3 files
   - Save to your local: `data/processed/`
   - (Or pull from GitHub repo directly - already committed)

---

## File Locations

### In Repository (Committed to GitHub) ✅
```
data/processed/
├── train.csv     (350 samples, 70%)  ✅ READY
├── val.csv       (75 samples, 15%)   ✅ READY
└── test.csv      (75 samples, 15%)   ✅ READY
```

### Shared on Google Drive (Not in GitHub)
```
NaviRaksha_Output/
├── raw/
│   ├── navi_mumbai_road_graph.pkl      (21 MB - need this)
│   ├── navi_mumbai_edges.geojson       (18 MB)
│   ├── navi_mumbai_road_graph.graphml  (46 MB)
│   └── key_locations.csv
└── processed/
    ├── train.csv   (auto-generated)
    ├── val.csv     (auto-generated)
    └── test.csv    (auto-generated)
```

---

## Team Task Assignment

### **Anjanaa (ML Engineer)**
- **Needs:** train.csv, val.csv, test.csv
- **Status:** ✅ Files ready in `data/processed/` (GitHub)
- **Next:** Train RF/LSTM baselines
- **Timeline:** Mar 30 - Apr 4

### **Turya (Routing Engineer)**
- **Needs:** `data/raw/navi_mumbai_road_graph.pkl`
- **Next:** Implement A* routing
- **Timeline:** Mar 30 - Apr 10

### **Arisha (Frontend Engineer)**
- **Needs:** `data/raw/navi_mumbai_edges.geojson` (for map visualization)
- **Next:** Build Streamlit UI components
- **Timeline:** Mar 30 - Apr 10

### **Sriya (Lead, ML Core)**
- **Status:** ✅ Feature engineering complete
- **Next:** Train GNN on Colab GPU (Apr 7-16)
- **Milestone:** GNN MAE < 3.0 minutes

---

## Troubleshooting

**Q: I don't have Google Drive access?**
- A: Ask Sriya to share the `NaviRaksha_Output` folder link
- Share permissions: Editor access required

**Q: Where do I save the pkl file?**
- A: `data/raw/navi_mumbai_road_graph.pkl`
- Create folder if missing: `mkdir -p data/raw`

**Q: Can I get files without Google Drive?**
- A: Not yet - raw files are too large for GitHub (use Git LFS if needed later)
- For now: Google Drive sharing is simplest

**Q: Do I need to run feature engineering?**
- A: NO! CSVs already committed to GitHub
- You only need the pkl file if you want to run the notebook yourself

---

## Verification

After setup, verify everything is in place:

```bash
# Check repo structure
ls -la data/

# Check if processed files exist (should)
ls -la data/processed/

# Check if raw files exist (manually copied)
ls -la data/raw/
```

Expected output:
```
data/
├── processed/
│   ├── train.csv  ✅
│   ├── val.csv    ✅
│   ├── test.csv   ✅
└── raw/
    ├── navi_mumbai_road_graph.pkl  ✅ (manually copied from Drive)
    └── ... other files
```

---

## Contact

- **Data issues:** Ask Sriya
- **Google Drive access:** Ask Sriya
- **File locations:** See this guide

---

**Last updated:** March 30, 2026  
**Status:** Ready for Phase 2 (Apr 1+)
