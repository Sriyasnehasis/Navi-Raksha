# 🚀 TEAM ACTION PLAN - Apr 9 Decision

## Strategic Decision: RF First, GNN Parallel

**Context:** RF achieved 0.0662 min MAE (excellent). GNN at 0.285 min due to architecture not leveraging graph structure.

**Decision:**

- ✅ Deploy RF immediately (Week 2)
- 🔄 Redesign GNN in parallel (Anjanaa, Apr 10-14)
- Don't delay Turya's routing work waiting for GNN

---

## WHO DOES WHAT (Apr 10 onwards)

### 👩‍💻 **Anjanaa** (ML Lead)

**Task:** Rebuild GNN with proper graph architecture  
**Timeline:** Apr 10 (Thu) → Apr 14 (Mon)  
**Deliverables:**

- [ ] `notebooks/05_gnn_graph_aware.ipynb` (training notebook)
- [ ] `data/processed/graph_trips_*.pkl` (new dataset)
- [ ] `models/trained/gnn_graph_aware.pt` (trained model)
- [ ] `docs/gnn_analysis_graph_aware.md` (comparison report)

**Resources Provided:**

- Read: `GNN_REBUILD_QUICK_SUMMARY.md` (overview)
- Follow: `GNN_REBUILD_GUIDE_FOR_ANJANAA.md` (detailed code, 5 phases)
- Use: `navi_mumbai_road_graph.pkl` (already in data/raw/)
- Ask: Sriya (me) if blocked

**Success Criteria:**

- New GNN MAE < 0.15 min (at least 2x better than old)
- Code documented in notebook
- Comparison to RF included

---

### 🗺️ **Turya** (Routing Lead)

**Task:** Build A\* router + dispatch + hospital ranker  
**Timeline:** Apr 10 (Thu) → Apr 20 (Sun)  
**Deliverable:** `routing_module.py`

**Key Points:**

- ✅ Use **RF model** (`models/trained/rf_model.pkl`) - IT'S READY NOW
- ✅ Don't wait for Anjanaa's GNN
- Use `navi_mumbai_road_graph.pkl` for routing
- Build A\* with traffic-weighted edges

**Module Breakdown:**

1. **A\* Router**
   - Input: Source zone, destination hospital, hour, weather
   - Output: Route + ETA
   - ✅ Use RF model for ETA prediction

2. **Dispatch Classifier**
   - Predict ambulance type (ALS/BLS/Mini/Bike)
   - Input: Incident severity, location, distance
   - Target: 95%+ accuracy

3. **Hospital Ranker**
   - Input: Patient location, top 5 nearby hospitals
   - Output: Ranked by ETA + bed availability
   - Use: A\* router for ETA calculation

---

### 🎨 **Arisha** (Frontend Lead)

**Task:** Build UI + analytics dashboard  
**Timeline:** Apr 10 (Thu) → Apr 27 (Sun)  
**Deliverables:**

1. Dispatcher Dashboard
2. Citizen Tracker
3. Analytics Dashboard
4. IEEE Paper (due Apr 30)

**Key Points:**

- ✅ Proceed with current specs (RF model available now)
- Assume Turya's routing API ready by Apr 21
- Start UI mockups this week

---

### 📌 **Sriya** (You - Integration Lead)

**Task:** Backend API + System Integration  
**Timeline:** Apr 21 (Mon) → Apr 30 (Wed)  
**Deliverables:**

```
curl http://localhost:8000/predict-eta?source=Vashi&dest=Hospital&hour=14
curl http://localhost:8000/dispatch?incident_severity=critical
curl http://localhost:8000/route?source=lat,lon&dest=lat,lon
```

**Week 1-2 (Apr 10-20):**

- [ ] Coordinate team
- [ ] Setup backend template (Flask/FastAPI)
- [ ] Review Anjanaa's GNN results
- [ ] Review Turya's routing module

**Week 3 (Apr 21-27):**

- [ ] Connect RF → Routing → Frontend
- [ ] API endpoint development
- [ ] End-to-end testing

**Week 4 (Apr 28-May 1):**

- [ ] System testing & optimization
- [ ] Handle Arisha's paper queries
- [ ] Deploy to production

---

## 📅 TIMELINE (Detailed)

### **Week 1: Apr 10-13 (This Week)**

**Monday (Apr 10):**

- [ ] Anjanaa: Phase 1-2 of GNN rebuild (OSM + routes)
- [ ] Turya: Start A\* routing skeleton with RF model
- [ ] Arisha: Finalize UI mockups
- [ ] Sriya: Setup backend template

**Tue-Wed (Apr 11-12):**

- [ ] Anjanaa: Phase 3-4 (features + training)
- [ ] Turya: A\* implementation
- [ ] Arisha: First UI components
- [ ] Sriya: API structure

**Thu-Fri (Apr 13-14):**

- [ ] Anjanaa: Finish Phase 5, push to test branch
- [ ] Turya: 50% of routing complete
- [ ] Arisha: 50% of dashboard
- [ ] Sriya: Review & document

### **Week 2: Apr 14-20**

**Mon (Apr 14):**

- [ ] Anjanaa: Code review + optimization
- [ ] Turya: **DEADLINE: Routing module 90% done**
- [ ] Arisha: Frontend 80% done
- [ ] Sriya: Review: dispatch, hospital ranker

**Tue-Fri (Apr 15-18):**

- [ ] Anjanaa: GNN optimization if time
- [ ] Turya: Final tests, optimizations
- [ ] Arisha: Final UI refinements
- [ ] Sriya: Prepare integration docs

**Sun (Apr 20):**

- [ ] **GATE: All modules pushed to test branch ready for integration**

### **Week 3: Apr 21-27**

**Daily:**

- Integration work (Sriya leads)
- End-to-end testing
- Bug fixes

**By Apr 27:**

- Full system working locally

### **Week 4: Apr 28-May 1**

**Apr 28-29:** Final tests  
**Apr 30:** Arisha paper submission deadline  
**May 1:** Production deployment + demo ✅

---

## 📊 DECISION MATRIX

| Decision       | RF First                     | GNN First                  |
| -------------- | ---------------------------- | -------------------------- |
| Deploy on time | ✅ Yes                       | ❌ 1-2 week delay          |
| Model quality  | ✅ 0.0662 MAE proven         | ❌ 0.285 MAE current issue |
| GNN learning   | 🔄 Parallel research         | ✅ Main focus              |
| Risk           | ✅ Low (RF tested)           | ❌ High (GNN untested)     |
| Paper impact   | ✅ Working system + analysis | ❌ Better model theory     |

**Selected:** RF First + GNN Parallel = Best of both ✅

---

## 🎯 SUCCESS METRICS

**Week 1 (Apr 10-13):**

- ✅ Anjanaa: New GNN code on test branch
- ✅ Turya: A\* skeleton working with RF
- ✅ Arisha: UI framework chosen
- ✅ Sriya: Backend template + docs

**Week 2 (Apr 14-20):**

- ✅ Complete modules ready for integration
- ✅ All tests passing
- ✅ Code documented

**Week 3+ (Apr 21-27):**

- ✅ Full system integrated
- ✅ End-to-end flow working
- ✅ Ready for paper + demo

**Week 4 (Apr 28-May 1):**

- ✅ Paper published
- ✅ Production deployment
- ✅ Live demo

---

## 📝 COMMUNICATION

**Today (Apr 9):**
Send this document + GNN guides to Anjanaa

**Tomorrow (Apr 10):**
Send routing specs to Turya (attach RF model file)

**This Week:**
Daily standup (10 AM): 15 min status update

---

## ⚠️ BLOCKERS / RISKS

| Risk                           | Mitigation                                          |
| ------------------------------ | --------------------------------------------------- |
| GNN not better than RF         | Continue GNN research, use RF in production         |
| Routing too slow               | Use simpler algorithm (Dijkstra vs A\*)             |
| Frontend needs backend changes | Daily API syncs between Sriya ↔ Arisha              |
| Paper quality issues           | Arisha starts writing today, not Apr 29             |
| Integration delays             | Start integration in Week 2 (don't wait for Week 3) |

---

## ✅ FINAL CHECKLIST

- [ ] Send Anjanaa: GNN guides + schedule
- [ ] Send Turya: RF model location + routing specs
- [ ] Send Arisha: Timeline + paper deadline reminder
- [ ] Push this document to test branch
- [ ] Schedule standup for tomorrow (Apr 10, 10 AM)

**Ready? Let's ship! 🚀**
