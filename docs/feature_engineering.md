# Feature Engineering Design for NaviRaksha

## India-Specific Road Features

### 1. Monsoon Flooding Flag 🌧️

**Zones affected:** Kharghar, Ulwe, Dronagiri  
**Duration:** June 1 – September 30, 2026  
**Impact:** 1.3× travel time multiplier

**Code Implementation:**

```python
def apply_monsoon_penalty(edge, current_date):
    monsoon_start = datetime.date(2026, 6, 1)
    monsoon_end = datetime.date(2026, 9, 30)

    if monsoon_start <= current_date <= monsoon_end:
        if edge['zone'] in ['Kharghar', 'Ulwe', 'Dronagiri']:
            edge['travel_time_min'] *= 1.3
    return edge
```

---

### 2. MIDC Industrial Surge ⏰

**Zones affected:** Thane-Belapur Road, Turbhe, Rabale MIDC  
**Peak hours:**

- Morning shift: 8:00 AM – 10:00 AM
- Evening shift: 5:00 PM – 7:00 PM  
  **Impact:** 1.2× travel time multiplier

**Code Implementation:**

```python
def apply_midc_surge(edge, current_hour):
    if edge['is_midc'] == True:
        if current_hour in [8, 9, 17, 18]:
            edge['travel_time_min'] *= 1.2
    return edge
```

---

### 3. Bridge Bottleneck Score 🌉

**Critical bridges:** Vashi, Airoli  
**Impact:** 1.5–2.0× multiplier (congestion hotspot)

**Code Implementation:**

```python
def apply_bridge_penalty(edge):
    if edge['is_bridge'] == True:
        if edge['bridge_name'] in ['Vashi', 'Airoli']:
            edge['travel_time_min'] *= 1.75  # Average of 1.5-2.0
    return edge
```

---

### 4. Festival Traffic Multiplier 🎉

**High-traffic festivals:**

- **Ganesh Chaturthi:** August 28 – September 8, 2026
- **Navratri:** October 1 – October 10, 2026

**Impact:** 1.4× city-wide multiplier

**Code Implementation:**

```python
FESTIVAL_DATES = {
    'ganesh_chaturthi': [(8, 28), (9, 8)],
    'navratri': [(10, 1), (10, 10)]
}

def apply_festival_penalty(travel_time, current_date):
    month = current_date.month
    day = current_date.day

    for festival, (start_date, end_date) in FESTIVAL_DATES.items():
        start_m, start_d = start_date
        end_m, end_d = end_date

        if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
            travel_time *= 1.4

    return travel_time
```

---

### 5. Road Type Classification 🛣️

| Type              | Speed   | Width          | Zone                    |
| ----------------- | ------- | -------------- | ----------------------- |
| **Arterial**      | 40 km/h | Wide (>10m)    | Highways, main roads    |
| **Residential**   | 25 km/h | Medium (5-10m) | Residential colonies    |
| **Slum Interior** | N/A     | Narrow (<3m)   | Requires bike ambulance |

---

## Temporal Features

Each trip/ambulance call must have these features:

```python
temporal_features = {
    'hour_of_day': 0-23,              # 0=midnight, 12=noon
    'day_of_week': 0-6,               # 0=Monday, 6=Sunday
    'is_monsoon': bool,               # June-Sept?
    'is_festival': bool,              # Ganesh/Navratri?
    'is_peak_hour': bool,             # 8-10 AM or 5-7 PM?
    'is_midc_zone': bool,             # Industrial area?
}
```

---

## Edge Attributes in Road Graph

Each edge (road segment) will have:

```python
edge_attributes = {
    'u': 'node_id_1',
    'v': 'node_id_2',
    'key': 0,
    'osmid': 'osm_way_id',
    'name': 'Road Name',
    'length': 250,                    # meters
    'geometry': LineString(...),      # GeoJSON

    # Custom attributes for NaviRaksha
    'road_type': 'arterial',          # arterial|residential|slum
    'zone': 'Vashi',                  # Location zone
    'is_bridge': False,
    'bridge_name': None,              # Vashi|Airoli (if applicable)
    'is_midc': False,                 # Industrial area?
    'is_monsoon_prone': False,        # Kharghar|Ulwe|Dronagiri?

    'baseline_speed_kmh': 40,         # Will be updated by GNN
    'travel_time_min': 0.375,         # 250m at 40 km/h = 0.375 min
}
```

---

## Training Data Format

Each sample row for ML models:

```csv
source_lat,source_lon,dest_lat,dest_lon,hour,day_of_week,is_monsoon,is_festival,is_peak_hour,road_type,zone,is_bridge,is_midc,ground_truth_eta_minutes
19.0760,73.0567,19.0917,73.2500,8,1,0,0,1,arterial,Vashi,0,1,12.5
19.0485,73.0818,19.0130,73.1880,14,3,1,0,0,residential,Nerul,0,0,8.2
```

---

## Expected Model Performance

| Model         | Target MAE | Status            |
| ------------- | ---------- | ----------------- |
| Random Forest | 4.2 min    | Baseline (Week 5) |
| LSTM          | 3.9 min    | Temporal (Week 6) |
| GNN           | < 3.0 min  | **Goal** (Week 7) |

---

**Document Version:** 1.0  
**Created:** March 29, 2026  
**Author:** Sriya (Team Lead)
