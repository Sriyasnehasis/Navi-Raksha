# 🧠 GNN Model Rebuild Guide: From Flat Features to Real Graph

**For:** Anjanaa  
**Timeline:** Apr 10-16 (5 working days)  
**Goal:** Build a proper graph-based GNN that uses road network topology

---

## 📊 Current Problem

Your GNN treats trips as **flat tabular data** (like RF/LSTM):

```
Input: [distance, hour, zone, violations] → Output: ETA
```

This wastes GNN's strength! GNNs excel at **learning from graph structure**:

```
Input: Road graph + Trip route + Segment features → Output: ETA
```

---

## ✅ Solution: Rebuild Dataset + Model

Your new dataset will have:

- **Real road graph** (OSM: nodes = intersections, edges = roads)
- **Trip routes** (which segments were actually used)
- **Segment features** (traffic, weather, length per road segment)
- **ETA label** (what we predict)

---

## 📋 STEP-BY-STEP PROCEDURE

### **PHASE 1: Extract & Prepare OSM Graph** (Days 1-2)

#### **Step 1.1: Load Existing OSM Graph**

```python
import pickle
import networkx as nx
import pandas as pd

# Load the OSM graph you already have
with open('../data/raw/navi_mumbai_road_graph.pkl', 'rb') as f:
    G = pickle.load(f)

print(f"Graph stats:")
print(f"  Nodes: {G.number_of_nodes()}")
print(f"  Edges: {G.number_of_edges()}")
print(f"  Node example: {list(G.nodes(data=True))[0]}")
print(f"  Edge example: {list(G.edges(data=True))[0]}")
```

**What to look for:**

- Node attributes: lat, lon, street name?
- Edge attributes: length, speed_limit, road_type?
- If missing: we'll add them in Step 1.2

---

#### **Step 1.2: Enrich OSM Edges with Speed/Traffic Data**

```python
# For each edge, add:
# 1. Length (usually in meters in OSM)
# 2. Speed factor by time-of-day
# 3. Monsoon impact zone

# First, create a speed profile for Navi Mumbai
PEAK_HOURS = list(range(8, 10)) + list(range(17, 19))  # 8-10 AM, 5-7 PM
MONSOON_ZONES = ['Kharghar', 'Ulwe']  # Most prone to flooding

speed_profile = {
    'peak_hour': 20,        # km/h during peak
    'normal_hour': 35,      # km/h normal
    'night_hour': 40,       # km/h late night
    'monsoon_factor': 0.75, # 25% slower
}

# Add attributes to each edge
for u, v, data in G.edges(data=True):
    if 'length' not in data:
        # If length missing, estimate from lat/lon
        node_u = G.nodes[u]
        node_v = G.nodes[v]
        if 'y' in node_u and 'x' in node_u:
            from math import radians, cos, sin, asin, sqrt
            # Haversine formula for distance
            lon1, lat1, lon2, lat2 = node_u['x'], node_u['y'], node_v['x'], node_v['y']
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Earth radius in km
            length_km = c * r
            data['length_km'] = length_km
        else:
            data['length_km'] = 1.0  # Default

    # Add speed profile
    data['speed_kmh_normal'] = speed_profile['normal_hour']
    data['speed_kmh_peak'] = speed_profile['peak_hour']
    data['speed_kmh_night'] = speed_profile['night_hour']

print("✅ OSM edges enriched with speed data")
```

---

#### **Step 1.3: Create Node Features DataFrame**

```python
# Extract node features for embedding
node_features = []
for node_id, attrs in G.nodes(data=True):
    node_features.append({
        'node_id': node_id,
        'lat': attrs.get('y', 0),
        'lon': attrs.get('x', 0),
        'degree': G.degree(node_id),  # How many roads connect here
        'is_hospital': False,  # We'll mark hospitals later
        'is_incident_zone': False,
    })

node_df = pd.DataFrame(node_features)
print(f"✅ Node features: {len(node_df)} nodes")
print(node_df.head())
```

---

### **PHASE 2: Rebuild Trip Dataset with Routes** (Days 2-3)

#### **Step 2.1: Load Existing Trip Data**

```python
# Load your existing dataset
train_df = pd.read_csv('../data/processed/train_real.csv')
val_df = pd.read_csv('../data/processed/val_real.csv')
test_df = pd.read_csv('../data/processed/test_real.csv')

print(f"Existing data shape:")
print(f"  Train: {train_df.shape}")
print(f"  Val: {val_df.shape}")
print(f"  Test: {test_df.shape}")
print(f"  Columns: {train_df.columns.tolist()}")
```

---

#### **Step 2.2: Map Trips to Graph Routes**

```python
# For each trip, find the route in the graph
# Trip has: source_location → destination_location

# First, map our 5 zones to OSM nodes (use key_locations.csv)
key_locations_df = pd.read_csv('../data/raw/key_locations.csv')
print(key_locations_df)

# Create mapping: location_name → closest_graph_node
location_to_node = {}
for idx, row in key_locations_df.iterrows():
    location_name = row['Unnamed: 0']  # Or appropriate column
    node_id = row['nearest_node']  # Already have from previous dataset!
    location_to_node[location_name] = int(node_id)

print("Location to Node mapping:")
print(location_to_node)
```

---

#### **Step 2.3: Add Route Information to Trips**

```python
from collections import deque

def find_shortest_path(G, source_node, dest_node):
    """Find shortest path in graph"""
    try:
        path = nx.shortest_path(G, source=source_node, target=dest_node, weight='length_km')
        return path
    except:
        return None

# Add route info to each trip
def enrich_trip_with_route(row, G, location_to_node):
    """Add route and segment features to a trip"""

    # Determine source and destination nodes
    # From dataset, you have zones like 'zone_Vashi', 'zone_Nerul'
    source_zone = None
    dest_zone = 0  # Assume all trips go to hospitals (0 = first hospital, etc)

    # Find which zone column is 1
    zone_cols = [c for c in row.index if c.startswith('zone_')]
    for zcol in zone_cols:
        if row[zcol] == 1:
            zone_name = zcol.replace('zone_', '')
            source_zone = zone_name
            break

    if source_zone is None:
        return {
            'source_node': None,
            'dest_node': None,
            'route': None,
            'num_segments': 0,
            'total_route_length_km': 0,
        }

    source_node = location_to_node.get(source_zone)
    # For destination, pick a hospital (let's use first one)
    dest_node = location_to_node.get('Vashi_CBD_Main')  # Pick a hospital

    if source_node is None or dest_node is None:
        return {
            'source_node': None,
            'dest_node': None,
            'route': None,
            'num_segments': 0,
            'total_route_length_km': 0,
        }

    # Find shortest path
    route = find_shortest_path(G, source_node, dest_node)

    if route is None:
        return {
            'source_node': source_node,
            'dest_node': dest_node,
            'route': None,
            'num_segments': 0,
            'total_route_length_km': 0,
        }

    # Calculate route length
    total_length = 0
    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        if G.has_edge(u, v):
            total_length += G[u][v].get('length_km', 1.0)

    return {
        'source_node': source_node,
        'dest_node': dest_node,
        'route': route,  # List of node IDs
        'num_segments': len(route) - 1,
        'total_route_length_km': total_length,
    }

# Apply to training data
print("Building routes for training data...")
route_info_list = []
for idx, row in train_df.iterrows():
    info = enrich_trip_with_route(row, G, location_to_node)
    route_info_list.append(info)
    if (idx + 1) % 1000 == 0:
        print(f"  Processed {idx + 1} trips...")

route_info_df = pd.DataFrame(route_info_list)
train_df_enriched = pd.concat([train_df, route_info_df], axis=1)

print(f"✅ Training data enriched with routes")
print(train_df_enriched.head())
```

---

#### **Step 2.4: Create Segment Feature Vectors**

```python
# For each trip, create feature vector for each segment
# Segments = edges along the route

def get_segment_features(G, route, hour, is_monsoon, zone_violations):
    """Get features for each segment in the route"""

    segment_features_list = []

    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]

        if not G.has_edge(u, v):
            continue

        edge_data = G[u][v]

        # Determine speed for this time
        if hour in PEAK_HOURS:
            speed_kmh = edge_data.get('speed_kmh_peak', 20)
        elif hour >= 22 or hour <= 6:
            speed_kmh = edge_data.get('speed_kmh_night', 40)
        else:
            speed_kmh = edge_data.get('speed_kmh_normal', 35)

        # Apply monsoon factor if needed
        if is_monsoon:
            speed_kmh *= 0.75

        # Calculate travel time for this segment
        length_km = edge_data.get('length_km', 1.0)
        travel_time_min = (length_km / speed_kmh) * 60 if speed_kmh > 0 else 5

        segment_features = {
            'segment_idx': i,
            'edge_u': u,
            'edge_v': v,
            'length_km': length_km,
            'speed_kmh': speed_kmh,
            'travel_time_min': travel_time_min,
            'is_bridge': edge_data.get('is_bridge', False),
            'is_oneway': edge_data.get('oneway', False),
            'road_type': edge_data.get('highway', 'residential'),
            'zone_violation_proximity': zone_violations,  # Passed in
        }

        segment_features_list.append(segment_features)

    return segment_features_list

# Create full trip with segment features
def create_graph_trip(row, G, location_to_node):
    """Create complete trip record with segment info"""

    route_info = enrich_trip_with_route(row, G, location_to_node)

    if route_info['route'] is None:
        return None

    # Get segment features
    is_monsoon = row.get('is_monsoon', 0)
    hour = row.get('hour', 12)
    zone_violations = row.get('violations_zone', 0)

    segment_features = get_segment_features(
        G,
        route_info['route'],
        int(hour),
        bool(is_monsoon),
        zone_violations
    )

    if len(segment_features) == 0:
        return None

    return {
        'trip_id': row.get('trip_id'),
        'source_node': route_info['source_node'],
        'dest_node': route_info['dest_node'],
        'route': route_info['route'],
        'num_segments': route_info['num_segments'],
        'total_route_length_km': route_info['total_route_length_km'],
        'segment_features': segment_features,
        'eta_minutes': row.get('eta_minutes'),
        'hour': hour,
        'is_monsoon': is_monsoon,
        'ambulance_type': row.get('ambulance_type', 0),
    }

# Process all training data
print("Creating graph-based trips...")
graph_trips = []
for idx, row in train_df.iterrows():
    trip = create_graph_trip(row, G, location_to_node)
    if trip is not None:
        graph_trips.append(trip)
    if (idx + 1) % 500 == 0:
        print(f"  Processed {idx + 1} trips, {len(graph_trips)} valid...")

print(f"✅ Created {len(graph_trips)} graph-based trips")

# Save to pickle for later
import pickle
with open('../data/processed/graph_trips_train.pkl', 'wb') as f:
    pickle.dump(graph_trips, f)

print("Graph trips saved to data/processed/graph_trips_train.pkl")
```

---

### **PHASE 3: Feature Engineering** (Days 3-4)

#### **Step 3.1: Add Context Features per Segment**

```python
# Enhance segment features with traffic/weather context

def enhance_segment_features_with_context(segment_features, hour, is_monsoon, violation_count):
    """Add traffic/weather context to each segment"""

    enhanced = segment_features.copy()

    # Traffic factor
    if hour in PEAK_HOURS:
        enhanced['traffic_factor'] = 0.6  # 40% slower in peak hours
        enhanced['congestion_level'] = 'high'
    else:
        enhanced['traffic_factor'] = 1.0
        enhanced['congestion_level'] = 'normal'

    # Monsoon factor
    if is_monsoon:
        enhanced['monsoon_factor'] = 0.75  # 25% slower
        enhanced['weather_condition'] = 'monsoon'
    else:
        enhanced['monsoon_factor'] = 1.0
        enhanced['weather_condition'] = 'clear'

    # Violation proximity (congestion proxy)
    if violation_count > 30000:
        enhanced['violation_severity'] = 'high'
        enhanced['violation_impact'] = 0.85  # 15% slower
    elif violation_count > 15000:
        enhanced['violation_severity'] = 'medium'
        enhanced['violation_impact'] = 0.92
    else:
        enhanced['violation_severity'] = 'low'
        enhanced['violation_impact'] = 1.0

    # Ambulance-specific factors
    # Ambulances can use one-ways, shortcuts, etc.
    enhanced['ambulance_boost'] = 1.05 if enhanced.get('is_oneway') else 1.0

    # Bridge factor (often bottlenecks)
    if enhanced.get('is_bridge'):
        enhanced['bridge_factor'] = 0.8  # Slower on bridges
    else:
        enhanced['bridge_factor'] = 1.0

    # Final speed adjustment
    enhanced['final_speed_kmh'] = (
        enhanced['speed_kmh']
        * enhanced['traffic_factor']
        * enhanced['monsoon_factor']
        * enhanced['violation_impact']
        * enhanced['ambulance_boost']
        * enhanced['bridge_factor']
    )

    # Recalculate travel time
    length = enhanced['length_km']
    final_speed = enhanced['final_speed_kmh']
    enhanced['final_travel_time_min'] = (length / final_speed * 60) if final_speed > 0 else 10

    return enhanced

# Apply to all trips
print("Enhancing segment features...")
for trip in graph_trips:
    enhanced_segments = []
    for seg in trip['segment_features']:
        enhanced = enhance_segment_features_with_context(
            seg,
            trip['hour'],
            trip['is_monsoon'],
            trip.get('zone_violations', 0)
        )
        enhanced_segments.append(enhanced)
    trip['segment_features'] = enhanced_segments

print("✅ Segment features enriched with context")
```

---

### **PHASE 4: Build New GNN Model** (Days 4-5)

#### **Step 4.1: Create Graph Data Structure for PyTorch**

```python
import torch
import torch.nn as nn
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, GraphSAGE

# Convert OSM graph to PyTorch Geometric format
edge_index_list = []
edge_attr_list = []
node_features_list = []

# Create node ID mapping
node_id_to_idx = {node: idx for idx, node in enumerate(G.nodes())}

# Create node features (position + degree)
for node_id in G.nodes():
    idx = node_id_to_idx[node_id]
    node_data = G.nodes[node_id]
    lat = node_data.get('y', 0)
    lon = node_data.get('x', 0)
    degree = G.degree(node_id)

    node_features_list.append([lat, lon, degree])

node_features = torch.tensor(node_features_list, dtype=torch.float32)

# Create edges with attributes
for u, v, data in G.edges(data=True):
    u_idx = node_id_to_idx[u]
    v_idx = node_id_to_idx[v]
    edge_index_list.append([u_idx, v_idx])
    edge_index_list.append([v_idx, u_idx])  # Bidirectional

    length_km = data.get('length_km', 1.0)
    speed_kmh = data.get('speed_kmh_normal', 35)

    edge_attr_list.append([length_km, speed_kmh])
    edge_attr_list.append([length_km, speed_kmh])

edge_index = torch.tensor(edge_index_list, dtype=torch.long).t().contiguous()
edge_attr = torch.tensor(edge_attr_list, dtype=torch.float32)

# Create PyG data object
graph_pyg = Data(
    x=node_features,
    edge_index=edge_index,
    edge_attr=edge_attr,
    num_nodes=len(node_id_to_idx)
)

print(f"PyTorch Geometric Graph:")
print(f"  Nodes: {graph_pyg.num_nodes}")
print(f"  Edges: {graph_pyg.num_edges}")
print(f"  Node features: {graph_pyg.x.shape}")
print(f"  Edge features: {graph_pyg.edge_attr.shape}")
```

---

#### **Step 4.2: Create Route Encoding Function**

```python
def encode_route_to_graph_input(trip, graph_pyg, node_id_to_idx):
    """Convert a trip's route into graph-aware features"""

    route = trip['route']
    segment_features = trip['segment_features']

    # Route node indices
    route_node_indices = [node_id_to_idx[node_id] for node_id in route]

    # Segment features (each edge in route)
    segment_features_tensor = torch.tensor(
        np.array([[
            seg['length_km'],
            seg['final_speed_kmh'],
            seg['traffic_factor'],
            seg['monsoon_factor'],
            seg['violation_impact'],
            1.0 if seg.get('is_bridge') else 0.0,
        ] for seg in segment_features]),
        dtype=torch.float32
    )

    # Trip-level features
    trip_features = torch.tensor([
        trip['hour'] / 24,  # Normalize hour
        1.0 if trip['is_monsoon'] else 0.0,
        trip['ambulance_type'],
    ], dtype=torch.float32)

    return {
        'route_nodes': torch.tensor(route_node_indices),
        'segment_features': segment_features_tensor,
        'trip_features': trip_features,
        'eta': torch.tensor([trip['eta_minutes']], dtype=torch.float32),
    }

# Test on one trip
sample_input = encode_route_to_graph_input(graph_trips[0], graph_pyg, node_id_to_idx)
print(f"Sample encoded trip:")
print(f"  Route nodes: {sample_input['route_nodes'].shape}")
print(f"  Segment features: {sample_input['segment_features'].shape}")
print(f"  Trip features: {sample_input['trip_features'].shape}")
print(f"  ETA: {sample_input['eta']}")
```

---

#### **Step 4.3: Build Graph-Aware GNN Model**

```python
class GraphAwareGNN(nn.Module):
    """
    GNN that understands:
    - Road network topology
    - Trip route structure
    - Segment-level features
    - Trip-level context
    """

    def __init__(self, node_feat_dim=3, edge_feat_dim=2, gcn_hidden=64):
        super().__init__()

        # Graph-level processing
        self.node_encoder = nn.Linear(node_feat_dim, gcn_hidden)
        self.edge_encoder = nn.Linear(edge_feat_dim, gcn_hidden)

        # Graph convolution layers
        self.gcn1 = GCNConv(gcn_hidden, gcn_hidden)
        self.gcn2 = GCNConv(gcn_hidden, gcn_hidden)

        # Segment processing
        self.segment_encoder = nn.Sequential(
            nn.Linear(6, 32),  # 6 segment features
            nn.ReLU(),
            nn.Linear(32, gcn_hidden),
        )

        # Route aggregation (learn importance of each segment)
        self.attention = nn.Sequential(
            nn.Linear(gcn_hidden, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

        # Trip features
        self.trip_encoder = nn.Sequential(
            nn.Linear(3, 16),  # hour, monsoon, ambulance_type
            nn.ReLU(),
            nn.Linear(16, gcn_hidden),
        )

        # Final predictor
        self.predictor = nn.Sequential(
            nn.Linear(gcn_hidden * 3, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, graph_pyg, route_nodes, segment_features, trip_features):
        """
        Args:
            graph_pyg: Full graph structure
            route_nodes: Node indices in this trip's route
            segment_features: Features for each edge in route
            trip_features: Hour, monsoon, ambulance type

        Returns:
            ETA prediction (in minutes)
        """

        # 1. Encode nodes from graph structure
        node_embed = self.node_encoder(graph_pyg.x)

        # 2. Apply graph convolution (learn from topology)
        node_embed = self.gcn1(node_embed, graph_pyg.edge_index)
        node_embed = torch.relu(node_embed)
        node_embed = self.gcn2(node_embed, graph_pyg.edge_index)

        # 3. Extract embeddings for this route
        route_node_embeds = node_embed[route_nodes]  # [num_segments+1, gcn_hidden]

        # 4. Encode segment features
        segment_embed = self.segment_encoder(segment_features)  # [num_segments, gcn_hidden]

        # 5. Combine route nodes + segments
        # Average route node embeddings
        route_context = route_node_embeds[:-1] + segment_embed  # [num_segments, gcn_hidden]

        # 6. Attention pooling: weight each segment by importance
        attention_weights = self.attention(route_context)  # [num_segments, 1]
        attention_weights = torch.softmax(attention_weights, dim=0)  # Normalize

        # Weighted sum of segments
        aggregated_route = torch.sum(
            route_context * attention_weights,
            dim=0,
            keepdim=True
        )  # [1, gcn_hidden]

        # 7. Encode trip features
        trip_embed = self.trip_encoder(trip_features)  # [gcn_hidden]

        # 8. Concatenate all contexts
        final_context = torch.cat([
            aggregated_route[0],
            trip_embed,
            torch.mean(route_context, dim=0),  # Average over all segments
        ])  # [gcn_hidden * 3]

        # 9. Predict ETA
        eta = self.predictor(final_context)  # [1]

        return eta

# Test model
model = GraphAwareGNN(node_feat_dim=3, edge_feat_dim=2, gcn_hidden=64)
sample_trip = graph_trips[0]
inputs = encode_route_to_graph_input(sample_trip, graph_pyg, node_id_to_idx)

with torch.no_grad():
    eta_pred = model(
        graph_pyg,
        inputs['route_nodes'],
        inputs['segment_features'],
        inputs['trip_features']
    )

print(f"✅ Model test passed")
print(f"  Predicted ETA: {eta_pred.item():.2f} min")
print(f"  Actual ETA: {sample_trip['eta_minutes']:.2f} min")
```

---

#### **Step 4.4: Training Loop**

```python
import torch.optim as optim

# Prepare data
print("Preparing training data...")
train_inputs = []
for trip in graph_trips[:8000]:  # 8K train
    try:
        inp = encode_route_to_graph_input(trip, graph_pyg, node_id_to_idx)
        train_inputs.append(inp)
    except:
        continue

print(f"✅ Prepared {len(train_inputs)} training samples")

# Setup training
model = GraphAwareGNN(gcn_hidden=128)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.L1Loss()  # MAE loss
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model.to(device)
graph_pyg.to(device)

# Training
print("🚀 Training Graph-Aware GNN...")
best_loss = float('inf')

for epoch in range(50):
    epoch_loss = 0
    for inp in train_inputs:
        optimizer.zero_grad()

        # Move to device
        route_nodes = inp['route_nodes'].to(device)
        segment_features = inp['segment_features'].to(device)
        trip_features = inp['trip_features'].to(device)
        eta_true = inp['eta'].to(device)

        # Forward
        eta_pred = model(graph_pyg, route_nodes, segment_features, trip_features)

        # Loss
        loss = criterion(eta_pred, eta_true)

        # Backward
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    avg_loss = epoch_loss / len(train_inputs)

    if (epoch + 1) % 5 == 0:
        print(f"Epoch {epoch+1:2d}/50 | Loss: {avg_loss:.6f}")

    if avg_loss < best_loss:
        best_loss = avg_loss
        torch.save(model.state_dict(), '../models/trained/gnn_graph_aware.pt')

print("✅ Training complete!")
print(f"Best loss: {best_loss:.6f}")
```

---

### **PHASE 5: Evaluation** (Day 5)

#### **Step 5.1: Test on Validation Set**

```python
# Prepare val data
val_inputs = []
for trip in graph_trips[8000:9000]:  # 1K val
    try:
        inp = encode_route_to_graph_input(trip, graph_pyg, node_id_to_idx)
        val_inputs.append(inp)
    except:
        continue

# Evaluate
y_true = []
y_pred = []

model.eval()
with torch.no_grad():
    for inp in val_inputs:
        route_nodes = inp['route_nodes'].to(device)
        segment_features = inp['segment_features'].to(device)
        trip_features = inp['trip_features'].to(device)
        eta_true = inp['eta'].item()

        eta_p = model(graph_pyg, route_nodes, segment_features, trip_features)

        y_true.append(eta_true)
        y_pred.append(eta_p.item())

# Metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_true = np.array(y_true)
y_pred = np.clip(np.array(y_pred), 3, 15)  # Clip to valid range

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)

print(f"\n🎯 Graph-Aware GNN Performance:")
print(f"  Val MAE:  {mae:.4f} min")
print(f"  Val RMSE: {rmse:.4f} min")
print(f"  Val R²:   {r2:.6f}")
```

---

## 📊 What to Expect

### **Before (Old GNN - Flat Features)**

```
Test MAE: 0.285 min (17.1 seconds)
Reason: Doesn't understand graph structure
```

### **After (Graph-Aware GNN)**

```
Expected Test MAE: 0.08-0.12 min (4.8-7.2 seconds)
Reason: Uses road network topology + segment features
Improvement: 65-75% better!
```

---

## 📋 Deliverables

By Apr 16, commit to test branch:

- [ ] `06_gnn_graph_aware.ipynb` (complete notebook)
- [ ] `data/processed/graph_trips_train.pkl` (new dataset)
- [ ] `data/processed/graph_trips_val.pkl` (validation)
- [ ] `data/processed/graph_trips_test.pkl` (test)
- [ ] `models/trained/gnn_graph_aware.pt` (trained model)
- [ ] `docs/gnn_analysis_graph_aware.md` (results report)

---

## 🔗 Report Format

Write a brief report with:

1. **Data Changes**
   - Old: Flat features (19 columns)
   - New: Graph routes + segment features
   - Why better: Uses topology

2. **Model Architecture**
   - GCN layers for graph learning
   - Attention pooling for route aggregation
   - Segment-aware encoding

3. **Results**
   - Validation MAE (target: < 0.12 min)
   - Comparison to old GNN
   - Comparison to RF/LSTM

4. **Conclusion**
   - Is this better than RF?
   - Should we use this for production?

---

## 🚨 If You Get Stuck

- **No OSM attributes?** Use estimated lengths from lat/lon (Haversine formula)
- **Route finding fails?** Check if source/dest nodes exist in graph
- **Out of memory?** Use smaller batch sizes, sample 2K trips instead of 8K
- **Model not converging?** Increase learning rate, fewer GCN layers

**Ask Sriya immediately if blocked!**

---

## ✅ Timeline

- Day 1-2: Prepare OSM graph
- Day 2-3: Rebuild trip dataset with routes
- Day 3-4: Add context features
- Day 4-5: Build + train new GNN
- Day 5: Evaluate + report

**Target:** 50% better MAE than old GNN (< 0.15 min)

Let's make GNN actually work! 🚀
