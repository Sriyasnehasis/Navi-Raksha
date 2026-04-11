# 🗺️ TURYA - QUICK START (Apr 14-20)

**Hello Turya!** You're on the routing module. Start Monday, push by Friday. Here's what to do:

---

## 📋 YOUR 3 TASKS (1 week, 4 days coding)

### **Task 1: A\* Router** (Days 1-2 Mon-Tue)

- Load OSM graph from `data/raw/navi_mumbai_road_graph.pkl`
- Find fastest routes using A\* algorithm
- Use RF model for ETA predictions
- **File:** `modules/routing/a_star_router.py`

### **Task 2: Dispatch Classifier** (Days 2-3 Wed)

- Classify incident severity → ambulance type
- Logic: Critical=ALS, High=BLS/ALS, Medium=Mini/BLS, Low=Bike
- **File:** `modules/routing/dispatch_classifier.py`

### **Task 3: Hospital Ranker** (Days 3-4 Thu)

- Rank 3 best hospitals by ETA + bed availability
- Use A\* router to calculate routes
- **File:** `modules/routing/hospital_ranker.py`

### **Task 4: Integration** (Day 5 Fri)

- Connect all 3 parts into `NaviRakshaRouter` class
- Create unified emergency handler
- **File:** `modules/routing/__init__.py`

---

## 🎯 DELIVERABLES (Push to test branch by Friday)

```
modules/routing/
├── __init__.py                 ← NaviRakshaRouter unified class
├── a_star_router.py            ← A* pathfinding
├── dispatch_classifier.py       ← Ambulance type selection
└── hospital_ranker.py          ← Hospital ranking

notebooks/
└── 05_routing_module_testing.ipynb ← Test your code
```

---

## 🚀 YOU HAVE EVERYTHING YOU NEED

✅ **Data Files:**

- `data/raw/navi_mumbai_road_graph.pkl` (OSM graph)
- `data/raw/key_locations.csv` (zone mapping)
- `data/raw/hospitals_navi_mumbai.csv` (hospitals)

✅ **Model:**

- `models/trained/rf_model.pkl` (RF for ETA)
- `models/trained/rf_features.pkl` (scaler)

✅ **Detailed Guide:**

- See `TURYA_ROUTING_MODULE_GUIDE.md` for step-by-step code

---

## 📅 TIMELINE

| Day          | What                  | Status       |
| ------------ | --------------------- | ------------ |
| Mon (Apr 14) | A\* Router            | Start coding |
| Tue (Apr 15) | A\* finish + test     | Day 2        |
| Wed (Apr 16) | Dispatch Classifier   | Day 3        |
| Thu (Apr 17) | Hospital Ranker       | Day 4        |
| Fri (Apr 18) | Integration + testing | Day 5        |
| Fri (Apr 19) | **PUSH TO GITHUB** ✅ | Done         |

---

## 💡 KEY FUNCTIONS YOU'LL BUILD

### **AStarRouter.find_route()**

```python
route, eta = router.find_route(
    source_node=zone_to_node['Vashi'],
    dest_node=zone_to_node['CBD_Main'],
    hour=14,
    is_monsoon=False
)
# Returns: list of node IDs + travel time
```

### **DispatchClassifier.classify()**

```python
amb_type = dispatcher.classify(
    incident_severity='Critical',
    distance_km=5,
    incident_type='Cardiac'
)
# Returns: 'ALS' or 'BLS' or 'Mini' or 'Bike'
```

### **HospitalRanker.rank_hospitals()**

```python
hospitals = ranker.rank_hospitals(
    patient_lat=19.076,
    patient_lon=72.877,
    ambulance_type='ALS',
    hour=14,
    is_monsoon=False,
    max_results=3
)
# Returns: Top 3 hospitals sorted by ETA
```

---

## ✅ QUICK CHECKLIST

Before pushing Friday, verify:

- [ ] A\* router finds routes between zones
- [ ] ETA predictions work (using RF model)
- [ ] Dispatch classifier returns correct ambulance types
- [ ] Hospital ranker returns top 3 hospitals
- [ ] Full flow: incident → ambulance type → route → hospital
- [ ] No errors when loading data files
- [ ] Code is commented and clean

---

## 🆘 IF YOU GET STUCK

**Common Issues:**

1. **Graph won't load?**
   - Check file path: `data/raw/navi_mumbai_road_graph.pkl`
   - Use: `import pickle; print(pickle.load(...))`

2. **Route returns None?**
   - Check zone_to_node mapping is correct
   - Verify nodes exist in graph: `node in G.nodes()`

3. **ETA predictions wrong?**
   - Load scaler: `rf_features.pkl`
   - Check feature order matches RF training

4. **Hospital data missing?**
   - Load CSV: `data/raw/hospitals_navi_mumbai.csv`
   - Has columns: id, name, lat, lon, beds, available_beds

**Ask Sriya (me) if blocked** 👈

---

## 📚 RESOURCES

**Full detailed guide:** `TURYA_ROUTING_MODULE_GUIDE.md`

- Complete code for each part
- Testing examples
- Troubleshooting tips

**Model files ready:**

- RF model: `models/trained/rf_model.pkl` ✅
- Scaler: `models/trained/rf_features.pkl` ✅

**Data files ready:**

- OSM graph: `data/raw/navi_mumbai_road_graph.pkl` ✅
- Zones: `data/raw/key_locations.csv` ✅
- Hospitals: `data/raw/hospitals_navi_mumbai.csv` ✅

---

## 🎯 SUCCESS CRITERIA

By Friday EOD:

✅ Routing module can handle emergency call  
✅ Returns ambulance type + route + ETA  
✅ Returns top 3 best hospitals  
✅ All tested locally  
✅ Code pushed to GitHub

---

**You got this! Start Monday! 🚀**

**Questions? → Ask Sriya**  
**Stuck? → Read full guide: `TURYA_ROUTING_MODULE_GUIDE.md`**
