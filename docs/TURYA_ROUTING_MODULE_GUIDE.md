# 🗺️ TURYA'S ROUTING MODULE - DETAILED GUIDE

**For:** Turya  
**Timeline:** Apr 14-20, 2026 (1 week)  
**Goal:** Build A\* Router + Dispatch Classifier + Hospital Ranker  
**Model to Use:** RF (`models/trained/rf_model.pkl`)

---

## 📋 QUICK OVERVIEW

You need to build 3 components:

| Component               | Purpose               | Input                           | Output              | Time   |
| ----------------------- | --------------------- | ------------------------------- | ------------------- | ------ |
| **A\* Router**          | Find fastest route    | Source, Destination, Hour       | Route + ETA         | 2 days |
| **Dispatch Classifier** | Select ambulance type | Incident severity, distance     | ALS/BLS/Mini/Bike   | 2 days |
| **Hospital Ranker**     | Rank best hospitals   | Patient location, incident type | Top 3 hospitals     | 2 days |
| **Integration**         | Connect all 3         | All above                       | Unified routing API | 1 day  |

---

## 🛣️ PART 1: A\* ROUTING MODULE (Days 1-2)

### **What You Have:**

- ✅ `data/raw/navi_mumbai_road_graph.pkl` (OSM graph with roads)
- ✅ `data/raw/navi_mumbai_road_graph.graphml.xml` (alternative format)
- ✅ `data/raw/key_locations.csv` (zone → coordinates mapping)

### **What You Need to Build:**

#### **Step 1.1: Load OSM Graph**

```python
import pickle
import networkx as nx
import pandas as pd
from datetime import datetime

# Load the graph
with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)

print(f"Graph loaded:")
print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")

# Load key locations (zone mapping)
locations_df = pd.read_csv('data/raw/key_locations.csv')
print(locations_df.head())
```

**Expected Output:**

```
Graph loaded:
  Nodes: ~5000-10000
  Edges: ~10000-20000
Location mapping: 10-15 zones to coordinates
```

---

#### **Step 1.2: Create Zone-to-Node Mapping**

```python
# Create mapping: zone name → nearest graph node
def create_zone_to_node_mapping(G, locations_df):
    """Map each zone to nearest OSM node"""
    zone_to_node = {}

    for idx, row in locations_df.iterrows():
        zone_name = row['zone_name']  # Adjust column name as needed
        lat = row['latitude']
        lon = row['longitude']

        # Find nearest node in graph
        min_dist = float('inf')
        nearest_node = None

        for node, attrs in G.nodes(data=True):
            node_lat = attrs.get('y', 0)
            node_lon = attrs.get('x', 0)

            # Euclidean distance (approximation for short distances)
            dist = ((node_lat - lat)**2 + (node_lon - lon)**2)**0.5

            if dist < min_dist:
                min_dist = dist
                nearest_node = node

        zone_to_node[zone_name] = nearest_node
        print(f"{zone_name} → Node {nearest_node}")

    return zone_to_node

zone_to_node = create_zone_to_node_mapping(G, locations_df)
print(f"\nZone mapping created: {len(zone_to_node)} zones")
```

---

#### **Step 1.3: Add Time-Dependent Edge Weights**

```python
def add_traffic_weights_to_graph(G, hour, is_monsoon=False):
    """Add edge weights based on time of day and weather"""

    # Define traffic factors
    PEAK_HOURS = list(range(8, 10)) + list(range(17, 19))  # 8-10 AM, 5-7 PM
    NIGHT_HOURS = list(range(22, 24)) + list(range(0, 6))

    for u, v, data in G.edges(data=True):
        # Base length in km
        length_km = data.get('length_km', 1.0)
        if length_km == 0:
            length_km = 1.0

        # Determine base speed based on road type
        road_type = data.get('highway', 'residential')
        if road_type in ['motorway', 'trunk']:
            base_speed = 50  # km/h
        elif road_type in ['primary', 'secondary']:
            base_speed = 40
        else:
            base_speed = 30

        # Apply time-of-day factor
        if hour in PEAK_HOURS:
            speed_factor = 0.6  # 40% slower in peak hours
        elif hour in NIGHT_HOURS:
            speed_factor = 1.2  # 20% faster at night
        else:
            speed_factor = 1.0

        # Apply monsoon factor (if needed)
        if is_monsoon:
            speed_factor *= 0.75  # 25% slower in monsoon

        # Calculate travel time in minutes
        effective_speed = base_speed * speed_factor
        travel_time_min = (length_km / effective_speed * 60) if effective_speed > 0 else 10

        # Ambulance advantage: can use one-ways, shortcuts
        if data.get('oneway'):
            travel_time_min *= 0.95  # 5% faster

        # Add as edge weight
        data['travel_time'] = travel_time_min
        data['weight'] = travel_time_min

    return G

# Add weights for current time
G_weighted = add_traffic_weights_to_graph(G, hour=14, is_monsoon=False)
print("Edge weights added (based on time + weather)")
```

---

#### **Step 1.4: Implement A\* Routing**

```python
from heapq import heappush, heappop
import math

class AStarRouter:
    """A* pathfinding with ETA prediction"""

    def __init__(self, G, rf_model, scaler):
        self.G = G
        self.rf_model = rf_model
        self.scaler = scaler

    def heuristic(self, node1, node2):
        """Euclidean distance heuristic"""
        lat1, lon1 = self.G.nodes[node1].get('y', 0), self.G.nodes[node1].get('x', 0)
        lat2, lon2 = self.G.nodes[node2].get('y', 0), self.G.nodes[node2].get('x', 0)

        # Approximate distance in km
        dlat = (lat2 - lat1) * 111  # 1 degree ≈ 111 km
        dlon = (lon2 - lon1) * 111 * math.cos(math.radians(lat1))

        return math.sqrt(dlat**2 + dlon**2)

    def find_route(self, source_node, dest_node, hour=12, is_monsoon=False):
        """Find fastest route using A*"""

        # Add current time weights to graph
        add_traffic_weights_to_graph(self.G, hour, is_monsoon)

        # A* search
        open_set = [(0, source_node)]  # (f_score, node)
        came_from = {}
        g_score = {node: float('inf') for node in self.G.nodes()}
        g_score[source_node] = 0

        closed_set = set()

        while open_set:
            _, current = heappop(open_set)

            if current in closed_set:
                continue

            if current == dest_node:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()

                return path, g_score[dest_node]

            closed_set.add(current)

            # Explore neighbors
            for neighbor in self.G.neighbors(current):
                if neighbor in closed_set:
                    continue

                edge_data = self.G[current][neighbor]
                travel_time = edge_data.get('travel_time', 1.0)

                tentative_g = g_score[current] + travel_time

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, dest_node)
                    heappush(open_set, (f_score, neighbor))

        return None, float('inf')  # No path found

    def predict_eta_for_route(self, route, hour, is_monsoon, ambulance_type):
        """Use RF model to refine ETA prediction"""

        # Calculate route length
        route_length_km = 0
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if self.G.has_edge(u, v):
                route_length_km += self.G[u][v].get('length_km', 1.0)

        # Prepare features for RF model
        features = {
            'distance': route_length_km,
            'hour': hour,
            'is_monsoon': 1 if is_monsoon else 0,
            'ambulance_type': self._encode_ambulance_type(ambulance_type),
            'violations_zone': 0,  # Default, will be enhanced later
        }

        # Scale features
        feature_array = self.scaler.transform([[
            features['distance'],
            features['hour'],
            features['is_monsoon'],
            features['ambulance_type'],
            features['violations_zone'],
        ]])

        # Predict ETA
        eta_min = self.rf_model.predict(feature_array)[0]

        return eta_min

    @staticmethod
    def _encode_ambulance_type(amb_type):
        """Encode ambulance type to number"""
        mapping = {'ALS': 3, 'BLS': 2, 'Mini': 1, 'Bike': 0}
        return mapping.get(amb_type, 0)

# Initialize router
import pickle
with open('models/trained/rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)

with open('models/trained/rf_features.pkl', 'rb') as f:
    scaler = pickle.load(f)

router = AStarRouter(G, rf_model, scaler)

# Test routing
route, travel_time = router.find_route(
    source_node=zone_to_node['Vashi'],
    dest_node=zone_to_node['CBD_Main'],
    hour=14,
    is_monsoon=False
)

if route:
    eta_min = router.predict_eta_for_route(route, 14, False, 'ALS')
    print(f"✅ Route found!")
    print(f"  Path: {len(route)} nodes")
    print(f"  ETA: {eta_min:.2f} min")
else:
    print("❌ No route found")
```

---

### **Deliverable 1: `modules/routing/a_star_router.py`**

Create file with full AStarRouter class (save code above)

---

## 🚑 PART 2: DISPATCH CLASSIFIER (Days 2-3)

### **What It Does:**

Predict which ambulance type to send: ALS / BLS / Mini / Bike

### **Logic (Simple Decision Tree):**

```python
class DispatchClassifier:
    """Classify incident severity → ambulance type"""

    @staticmethod
    def classify(incident_severity, distance_km, incident_type):
        """
        Args:
            incident_severity: 'Critical', 'High', 'Medium', 'Low'
            distance_km: Distance to incident
            incident_type: 'Cardiac', 'Trauma', 'Respiratory', 'Burn', etc.

        Returns:
            'ALS', 'BLS', 'Mini', 'Bike'
        """

        # Critical = Advance Life Support (ALS)
        if incident_severity == 'Critical':
            return 'ALS'

        # High = Basic Life Support
        if incident_severity == 'High':
            if incident_type in ['Cardiac', 'Trauma', 'Burn']:
                return 'ALS'
            return 'BLS'

        # Medium = Based on distance
        if incident_severity == 'Medium':
            if distance_km < 2:
                return 'Mini'  # Close, fast response
            return 'BLS'

        # Low = Motorcycle
        if incident_severity == 'Low':
            return 'Bike'  # Quick first assessment

        return 'BLS'  # Default

    @staticmethod
    def get_availability_of_type(ambulance_type, ambulances_db):
        """Check how many ambulances of this type are available"""
        count = 0
        for amb in ambulances_db:
            if amb['type'] == ambulance_type and amb['status'] == 'Available':
                count += 1
        return count

# Usage
dispatcher = DispatchClassifier()

dispatch_type = dispatcher.classify(
    incident_severity='Critical',
    distance_km=5.2,
    incident_type='Cardiac'
)
print(f"Dispatch: {dispatch_type}")  # Output: 'ALS'
```

---

### **Deliverable 2: `modules/routing/dispatch_classifier.py`**

Create file with DispatchClassifier class

---

## 🏥 PART 3: HOSPITAL RANKER (Days 3-4)

### **What It Does:**

Rank nearby hospitals by ETA + bed availability

```python
import pandas as pd
import numpy as np

class HospitalRanker:
    """Rank hospitals by ETA and availability"""

    def __init__(self, router, hospitals_df):
        """
        Args:
            router: AStarRouter instance
            hospitals_df: DataFrame with columns [id, name, lat, lon, beds, available_beds]
        """
        self.router = router
        self.hospitals_df = hospitals_df

    def rank_hospitals(self, patient_lat, patient_lon, ambulance_type='ALS', hour=12, is_monsoon=False, max_results=3):
        """
        Rank hospitals by ETA

        Returns:
            List of hospitals sorted by ETA (best first)
        """

        # Find nearest hospital node to patient location
        patient_node = self._find_nearest_node(patient_lat, patient_lon)

        hospital_rankings = []

        for idx, hospital in self.hospitals_df.iterrows():
            # Find route from patient to hospital
            hospital_node = self._get_hospital_node(hospital['id'])

            route, travel_time = self.router.find_route(
                source_node=patient_node,
                dest_node=hospital_node,
                hour=hour,
                is_monsoon=is_monsoon
            )

            if route is None:
                continue

            # Predict ETA using RF model
            eta_min = self.router.predict_eta_for_route(route, hour, is_monsoon, ambulance_type)

            # Score: balance ETA + bed availability
            bed_availability_ratio = hospital['available_beds'] / hospital['beds']

            # Weighted score: 70% ETA, 30% beds
            score = (0.7 * eta_min) + (0.3 * (1 - bed_availability_ratio) * 30)

            hospital_rankings.append({
                'rank': len(hospital_rankings) + 1,
                'hospital_id': hospital['id'],
                'hospital_name': hospital['name'],
                'eta_min': eta_min,
                'available_beds': hospital['available_beds'],
                'total_beds': hospital['beds'],
                'bed_availability': f"{bed_availability_ratio*100:.1f}%",
                'score': score,
                'route': route,
            })

        # Sort by score (lower is better)
        hospital_rankings.sort(key=lambda x: x['score'])

        return hospital_rankings[:max_results]

    def _find_nearest_node(self, lat, lon):
        """Find nearest graph node to given coordinates"""
        min_dist = float('inf')
        nearest_node = None

        for node, attrs in self.router.G.nodes(data=True):
            node_lat = attrs.get('y', 0)
            node_lon = attrs.get('x', 0)

            dist = ((node_lat - lat)**2 + (node_lon - lon)**2)**0.5

            if dist < min_dist:
                min_dist = dist
                nearest_node = node

        return nearest_node

    def _get_hospital_node(self, hospital_id):
        """Get OSM node ID for hospital"""
        # This should be in your hospitals_df or cached
        # For now, find nearest node to hospital coordinates
        hospital = self.hospitals_df[self.hospitals_df['id'] == hospital_id].iloc[0]
        return self._find_nearest_node(hospital['lat'], hospital['lon'])

# Load hospitals
hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')

ranker = HospitalRanker(router, hospitals_df)

# Get ranked hospitals
ranked = ranker.rank_hospitals(
    patient_lat=19.0760,
    patient_lon=72.8777,
    ambulance_type='ALS',
    hour=14,
    is_monsoon=False,
    max_results=3
)

print("Top 3 Hospitals:")
for h in ranked:
    print(f"  {h['rank']}. {h['hospital_name']} - ETA: {h['eta_min']:.1f} min, Beds: {h['available_beds']}/{h['total_beds']}")
```

---

### **Deliverable 3: `modules/routing/hospital_ranker.py`**

Create file with HospitalRanker class

---

## 🔗 PART 4: UNIFIED ROUTING API (Day 5)

### **Integration Module**

Create file: `modules/routing/__init__.py`

```python
from .a_star_router import AStarRouter
from .dispatch_classifier import DispatchClassifier
from .hospital_ranker import HospitalRanker

class NaviRakshaRouter:
    """Unified routing module"""

    def __init__(self):
        import pickle
        import pandas as pd
        import networkx as nx

        # Load graph
        with open('data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
            self.G = pickle.load(f)

        # Load models
        with open('models/trained/rf_model.pkl', 'rb') as f:
            self.rf_model = pickle.load(f)

        with open('models/trained/rf_features.pkl', 'rb') as f:
            self.scaler = pickle.load(f)

        # Load data
        self.hospitals_df = pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
        self.locations_df = pd.read_csv('data/raw/key_locations.csv')

        # Initialize components
        self.router = AStarRouter(self.G, self.rf_model, self.scaler)
        self.dispatcher = DispatchClassifier()
        self.ranker = HospitalRanker(self.router, self.hospitals_df)

    def handle_emergency(self, incident_data):
        """
        Main function to handle an emergency call

        Input:
        {
            'patient_lat': 19.076,
            'patient_lon': 72.877,
            'incident_type': 'Cardiac',
            'severity': 'Critical',
            'hour': 14,
            'is_monsoon': False
        }

        Output:
        {
            'ambulance_type': 'ALS',
            'route': [...nodes...],
            'eta': 8.5,
            'hospitals': [
                {'name': 'Hospital A', 'eta': 12.3, 'beds': 5},
                {'name': 'Hospital B', 'eta': 15.1, 'beds': 3},
                {'name': 'Hospital C', 'eta': 18.2, 'beds': 1},
            ]
        }
        """

        # Step 1: Classify ambulance type
        ambulance_type = self.dispatcher.classify(
            incident_data['severity'],
            0,  # distance (unknown yet)
            incident_data['incident_type']
        )

        # Step 2: Rank hospitals
        ranked_hospitals = self.ranker.rank_hospitals(
            patient_lat=incident_data['patient_lat'],
            patient_lon=incident_data['patient_lon'],
            ambulance_type=ambulance_type,
            hour=incident_data['hour'],
            is_monsoon=incident_data['is_monsoon'],
            max_results=3
        )

        # Step 3: Find route to best hospital
        best_hospital = ranked_hospitals[0]
        route = best_hospital['route']

        return {
            'ambulance_type': ambulance_type,
            'route': route,
            'eta_min': best_hospital['eta_min'],
            'best_hospital': {
                'id': best_hospital['hospital_id'],
                'name': best_hospital['hospital_name'],
                'available_beds': best_hospital['available_beds'],
            },
            'alternatives': [
                {
                    'name': h['hospital_name'],
                    'eta_min': h['eta_min'],
                    'beds': h['available_beds']
                }
                for h in ranked_hospitals[1:]
            ]
        }

# Usage
routing = NaviRakshaRouter()

response = routing.handle_emergency({
    'patient_lat': 19.076,
    'patient_lon': 72.877,
    'incident_type': 'Cardiac',
    'severity': 'Critical',
    'hour': 14,
    'is_monsoon': False
})

print(f"Dispatch: {response['ambulance_type']}")
print(f"ETA to hospital: {response['eta_min']:.1f} min")
print(f"Best hospital: {response['best_hospital']['name']}")
```

---

## 📦 DELIVERABLES (What to Push to GitHub)

By **Friday, Apr 19**, push these files to `test` branch:

```
modules/routing/
├── __init__.py           (NaviRakshaRouter class)
├── a_star_router.py      (A* routing)
├── dispatch_classifier.py (Ambulance type selection)
└── hospital_ranker.py    (Hospital ranking)

notebooks/
└── 05_routing_module_testing.ipynb (Test notebook)
```

---

## ✅ TESTING CHECKLIST

Before pushing, test locally:

- [ ] Load OSM graph ✓
- [ ] Create zone-to-node mapping ✓
- [ ] Find route between 2 zones ✓
- [ ] ETA prediction on route ✓
- [ ] Classify incident → ambulance type ✓
- [ ] Rank hospitals by ETA ✓
- [ ] Full emergency flow test ✓

---

## 📝 TEST CASES

```python
# Test 1: Vashi to CBD (rush hour)
route, eta = router.find_route(
    zone_to_node['Vashi'],
    zone_to_node['CBD_Main'],
    hour=17,  # Evening rush
    is_monsoon=False
)
assert route is not None, "Route should exist"
assert eta < 20, "ETA should be reasonable"

# Test 2: Dispatch Critical Cardiac
amb_type = dispatcher.classify('Critical', 5, 'Cardiac')
assert amb_type == 'ALS', "Critical cardiac should be ALS"

# Test 3: Rank hospitals
hospitals = ranker.rank_hospitals(19.076, 72.877)
assert len(hospitals) <= 3, "Should return max 3 hospitals"
assert hospitals[0]['eta_min'] <= hospitals[1]['eta_min'], "Should be sorted by ETA"
```

---

## 📞 SUPPORT

**If you get stuck:**

- Check data files exist: `data/raw/navi_mumbai_road_graph.pkl`, `key_locations.csv`
- Make sure RF model loaded: `models/trained/rf_model.pkl`
- Test with smaller zone pairs first
- Use print statements for debugging

**Ask Sriya (me) if:**

- Graph won't load
- Route finding returns None
- ETA values seem wrong
- Hospital data missing

---

## 🚀 TIMELINE

| Date             | What                      | Status |
| ---------------- | ------------------------- | ------ |
| **Apr 14 (Mon)** | A\* Router implementation | Day 1  |
| **Apr 15 (Tue)** | A\* testing + finish      | Day 2  |
| **Apr 16 (Wed)** | Dispatch Classifier       | Day 3  |
| **Apr 17 (Thu)** | Hospital Ranker           | Day 4  |
| **Apr 18 (Fri)** | Integration + testing     | Day 5  |
| **Apr 19 (Fri)** | **PUSH TO GITHUB** ✅     | Done   |

---

## 💡 BONUS: Integration with Sriya's API

Once Sriya builds the backend API, your routing module will connect like this:

```python
# Sriya's API will call your routing module
from modules.routing import NaviRakshaRouter

routing = NaviRakshaRouter()

@app.route('/dispatch', methods=['POST'])
def dispatch_ambulance():
    data = request.json
    response = routing.handle_emergency(data)
    return jsonify(response)
```

---

**Ready? Start with Step 1.1 on Monday!** 🚀

Good luck, Turya! You've got this! 💪
