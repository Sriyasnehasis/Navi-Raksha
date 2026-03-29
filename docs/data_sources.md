# Data Sources for NaviRaksha

## 1. Road Network: OpenStreetMap (via OSMnx)

- **Source:** https://www.openstreetmap.org
- **Library:** osmnx (Python)
- **What to extract:**
  - All roads in Navi Mumbai boundaries
  - Node coordinates (lat/lon)
  - Edge attributes (length, road type)
  - 50+ key locations (Vashi, Nerul, Belapur, etc.)
- **Expected:** 5,000–10,000 edges
- **Storage:** `data/raw/navi_mumbai_road_graph.pkl` (NetworkX format)
  `data/raw/navi_mumbai_roads.geojson` (for Folium visualization)

---

## 2. Traffic Data: Uber Movement

- **Source:** https://movement.uber.com (Mumbai region)
- **What to use:**
  - Historical speed data by hour/day
  - Aggregate to road segment level
  - Extract average speeds for baseline
- **Expected:** ~500 samples with temporal variation
- **Storage:** `data/raw/uber_movement_traffic.csv`

---

## 3. Hospital Data: NMMC + NITI Aayog

- **Top 10 NMMC hospitals:**

| Hospital            | Lat    | Lon    | Beds | Type            |
| ------------------- | ------ | ------ | ---- | --------------- |
| Vashi Hospital      | 19.074 | 73.056 | 200  | General         |
| Belapur Hospital    | 19.013 | 73.188 | 150  | General         |
| Panvel Hospital     | 18.983 | 73.307 | 180  | Trauma          |
| Kharghar Hospital   | 19.092 | 73.250 | 120  | General         |
| Seawoods Hospital   | 19.030 | 73.170 | 250  | Multi-specialty |
| Apollo Hospitals    | 19.012 | 73.190 | 400  | Specialty       |
| Fortis Hospital     | 19.075 | 73.058 | 350  | Specialty       |
| Millennium Hospital | 19.045 | 73.080 | 180  | General         |
| Ulwe Medical Center | 18.950 | 73.400 | 80   | Primary         |
| Dronagiri Clinic    | 18.908 | 73.375 | 60   | Primary         |

- **Storage:** `data/raw/hospitals_navi_mumbai.csv`

---

## 4. Weather Data: IMD (India Meteorological Department)

- **Source:** https://mausam.imd.gov.in
- **Cost:** FREE
- **For:** Monsoon dates, rainfall predictions

**Key dates we track:**

- **Monsoon onset:** June 1, 2026
- **Monsoon withdrawal:** September 30, 2026
- **Heavy rainfall alerts:** Real-time from IMD

**File:** `data/raw/weather_monsoon_dates.json`

---

## 5. Festival Calendar

- **Source:** Hindu calendar + local knowledge
- **Cost:** FREE

**High-traffic festivals (2026):**

- **Ganesh Chaturthi:** August 28 – September 8
- **Navratri:** October 1 – October 10

**File:** `data/raw/festival_calendar.json`

---

## How to Download Data (Week 3-4)

### A. Road Network (OSMnx) — AUTOMATIC

```python
import osmnx as ox
place = "Navi Mumbai, Maharashtra, India"
G = ox.graph_from_place(place, network_type='drive')
# Downloaded automatically (takes ~5-10 min)
```

### B. Uber Movement — MANUAL

1. Visit https://movement.uber.com
2. Create account (email)
3. Browse: Asia → India → Mumbai
4. Download CSV (Speed data, recent quarter)
5. Save to: `data/raw/uber_movement_traffic.csv`

### C. Hospital Data — MANUAL ENTRY

```python
import pandas as pd

hospitals = [
    {'name': 'Vashi Hospital', 'zone': 'Vashi', 'lat': 19.0760, 'lon': 73.0567, 'beds': 200, 'type': 'General'},
    {'name': 'Belapur Hospital', 'zone': 'Belapur', 'lat': 19.0130, 'lon': 73.1880, 'beds': 150, 'type': 'General'},
    # ... 8 more hospitals
]

df = pd.DataFrame(hospitals)
df.to_csv('data/raw/hospitals_navi_mumbai.csv', index=False)
```

### D. Festival Calendar — MANUAL ENTRY

```json
{
  "ganesh_chaturthi": {
    "name": "Ganesh Chaturthi",
    "start": "2026-08-28",
    "end": "2026-09-08",
    "traffic_multiplier": 1.4
  },
  "navratri": {
    "name": "Navratri",
    "start": "2026-10-01",
    "end": "2026-10-10",
    "traffic_multiplier": 1.4
  }
}
```

---

**Document Version:** 1.0  
**Created:** March 29, 2026  
**Author:** Sriya (Team Lead)
