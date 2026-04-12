# 📌 GNN Rebuild - Executive Summary (Send to Anjanaa)

## The Problem

Your current GNN treats trips as **flat features** (like RF/LSTM), but GNNs are meant for **graphs**!

- Current MAE: 0.285 min ❌
- Target MAE: < 0.12 min ✅

## The Solution: 3 Key Changes

### 1️⃣ **Use Real Road Network**

- Load `navi_mumbai_road_graph.pkl` (already exists!)
- Each trip = path through actual OSM roads
- Model learns from topology: intersections, bridges, one-ways

### 2️⃣ **Convert Trips to Routes**

- OLD: `[distance=15km, hour=9, zone=Vashi] → ETA`
- NEW: `Route=[Node1→Node2→Node3] with segment features → ETA`

For each segment:

- Length (from OSM)
- Speed (from road type)
- Traffic (peak hour factor)
- Monsoon (weather slowdown)
- Violations (congestion proxy)

### 3️⃣ **Redesign GNN Architecture**

1. **Graph Convolution** (GCN): Learn from road network structure
2. **Segment Encoding**: Process each road segment
3. **Attention Pooling**: Which segments matter most for ETA?
4. **Trip Context**: Hour + weather + ambulance type
5. **Final Prediction**: Combine all signals

## What Do You Need?

✅ **Already Have:**

- `navi_mumbai_road_graph.pkl` (OSM graph)
- `train_real.csv`, `val_real.csv`, `test_real.csv` (trip data)
- `key_locations.csv` (zone → node mapping)

❌ **Don't Have (Will Create):**

- `graph_trips_train.pkl` - Routes with segment features
- `gnn_graph_aware.pt` - New trained model

## NO Kaggle Needed! ✓

Everything is **already in your repo**:

- `data/raw/navi_mumbai_road_graph.pkl` ← OSM graph
- `data/processed/train_real.csv` ← Trip data
- `data/raw/key_locations.csv` ← Zone mapping

---

## The 5-Day Workflow

| Day | Phase               | What to Do                                                     |
| --- | ------------------- | -------------------------------------------------------------- |
| 1-2 | Extract OSM         | Load `navi_mumbai_road_graph.pkl`, add speed profiles per road |
| 2-3 | Rebuild Data        | Map each trip to actual route (sequence of roads)              |
| 3-4 | Feature Engineering | Add traffic/weather/monsoon factors per segment                |
| 4-5 | New GNN             | Build GCN-based model that understands routes                  |
| 5   | Validate            | Test on val set, compare to your old GNN                       |

---

## Expected Results

| Model           | Val MAE       | Why Better?                        |
| --------------- | ------------- | ---------------------------------- |
| Old GNN (Flat)  | 0.285 min     | ❌ Ignores graph                   |
| New GNN (Graph) | 0.08-0.12 min | ✅ Uses topology                   |
| RF (Baseline)   | 0.0662 min    | ✅ Still best, but GNN competitive |

**Your new GNN will be ~2.5x better than before!** 🚀

---

## Key Files

See: `GNN_REBUILD_GUIDE_FOR_ANJANAA.md` for:

- ✅ Line-by-line Python code
- ✅ All 5 phases explained
- ✅ How to handle edge cases
- ✅ What to commit to GitHub

---

## Bonus: No Extra Data Collection Needed

Your current dataset already has:

- ✅ Location zones → OSM nodes
- ✅ Travel times
- ✅ Hour of day
- ✅ Monsoon flag
- ✅ Violation counts

Just need to **reshape it to follow routes through graph** instead of using flat features.

---

## Questions?

1. **Q: What if the graph doesn't have all attributes?**  
   A: Estimate from lat/lon (use Haversine formula in Phase 1)

2. **Q: What if a route can't be found?**  
   A: Skip that trip (Phase 2.3 handles this)

3. **Q: How long to train?**  
   A: ~10-30 min per epoch on colab GPU

4. **Q: Will this definitely beat RF?**  
   A: Possibly not (RF might stay best), but will be competitive + show GNN strength

---

**Start with Phase 1 today!** 🎯

Full detailed guide: `GNN_REBUILD_GUIDE_FOR_ANJANAA.md`
