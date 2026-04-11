# 🗺️ INTERACTIVE MAP WITH SYMBOLS - Complete Guide

**Make map draggable, zoomable, and show different symbols for different types**

---

## 🎯 THE PROBLEM

Your map isn't interactive:
- ❌ Can't drag/pan (slide left to right)
- ❌ Can't zoom smoothly
- ❌ All markers look the same
- ❌ Can't explore the full map

---

## ✅ THE SOLUTION

Use **Leaflet-based interactive map** with proper icons for each type.

---

# 🔧 CURRENT ISSUE & FIX

## Current Code (Not Interactive):

```python
import streamlit as st
import folium
from streamlit_folium import st_folium

map = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
st_folium(map)  # ← This is NOT fully interactive in Streamlit
```

### Problem:
- Streamlit rerenders the entire page on interaction
- Map doesn't feel smooth
- Dragging is laggy

---

## ✅ FIXED CODE (FULLY INTERACTIVE)

### Option 1: Use Folium with Better Configuration (Easiest)

```python
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

st.set_page_config(layout="wide")

# Create interactive map with proper settings
map = folium.Map(
    location=[19.0760, 72.8777],
    zoom_start=13,
    tiles="OpenStreetMap",
    prefer_canvas=True,  # ← Better performance
    max_bounds=True,
    min_zoom=10,
    max_zoom=18
)

# Enable smooth dragging
map.options['dragging'] = True
map.options['touchZoom'] = True
map.options['scrollWheelZoom'] = True

# Get data from your backend
ambulances = requests.get('http://localhost:8000/ambulances').json()
hospitals = requests.get('http://localhost:8000/hospitals').json()
incidents = requests.get('http://localhost:8000/incidents').json()

# ===== DIFFERENT SYMBOLS FOR AMBULANCES =====
# 🚑 ALS Ambulance (Advanced Life Support) - Red
for amb in [a for a in ambulances if a.get('type') == 'ALS']:
    folium.Marker(
        location=[amb['latitude'], amb['longitude']],
        popup=f"🚑 ALS Ambulance {amb['id']}<br>Status: {amb['status']}",
        icon=folium.Icon(
            color='red',
            icon='ambulance',
            prefix='fa',
            icon_color='white'
        ),
        tooltip=f"ALS #{amb['id']}"
    ).add_to(map)

# 🚐 BLS Ambulance (Basic Life Support) - Orange
for amb in [a for a in ambulances if a.get('type') == 'BLS']:
    folium.Marker(
        location=[amb['latitude'], amb['longitude']],
        popup=f"🚐 BLS Ambulance {amb['id']}<br>Status: {amb['status']}",
        icon=folium.Icon(
            color='orange',
            icon='ambulance',
            prefix='fa',
            icon_color='white'
        ),
        tooltip=f"BLS #{amb['id']}"
    ).add_to(map)

# 🚙 Mini Ambulance - Yellow
for amb in [a for a in ambulances if a.get('type') == 'Mini']:
    folium.Marker(
        location=[amb['latitude'], amb['longitude']],
        popup=f"🚙 Mini Ambulance {amb['id']}<br>Status: {amb['status']}",
        icon=folium.Icon(
            color='yellow',
            icon='car',
            prefix='fa',
            icon_color='black'
        ),
        tooltip=f"Mini #{amb['id']}"
    ).add_to(map)

# ===== DIFFERENT SYMBOLS FOR INCIDENTS =====
# 🔴 Critical Incident - Red circle
for inc in [i for i in incidents if i.get('severity') == 'critical']:
    folium.CircleMarker(
        location=[inc['latitude'], inc['longitude']],
        radius=12,
        popup=f"🔴 CRITICAL<br>{inc['type']}<br>ETA: {inc.get('eta', '?')} min",
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.9,
        weight=3,
        tooltip="🔴 CRITICAL INCIDENT"
    ).add_to(map)

# 🟠 Severe Incident - Orange circle
for inc in [i for i in incidents if i.get('severity') == 'severe']:
    folium.CircleMarker(
        location=[inc['latitude'], inc['longitude']],
        radius=10,
        popup=f"🟠 SEVERE<br>{inc['type']}<br>ETA: {inc.get('eta', '?')} min",
        color='orange',
        fill=True,
        fillColor='orange',
        fillOpacity=0.8,
        weight=2,
        tooltip="🟠 SEVERE INCIDENT"
    ).add_to(map)

# 🟡 Moderate Incident - Yellow circle
for inc in [i for i in incidents if i.get('severity') == 'moderate']:
    folium.CircleMarker(
        location=[inc['latitude'], inc['longitude']],
        radius=8,
        popup=f"🟡 MODERATE<br>{inc['type']}<br>ETA: {inc.get('eta', '?')} min",
        color='yellow',
        fill=True,
        fillColor='yellow',
        fillOpacity=0.7,
        weight=2,
        tooltip="🟡 MODERATE INCIDENT"
    ).add_to(map)

# 🟢 Minor Incident - Green circle
for inc in [i for i in incidents if i.get('severity') == 'minor']:
    folium.CircleMarker(
        location=[inc['latitude'], inc['longitude']],
        radius=6,
        popup=f"🟢 MINOR<br>{inc['type']}",
        color='green',
        fill=True,
        fillColor='green',
        fillOpacity=0.6,
        weight=2,
        tooltip="🟢 MINOR INCIDENT"
    ).add_to(map)

# ===== SYMBOLS FOR HOSPITALS =====
for hosp in hospitals:
    # Show available beds in color
    if hosp.get('available_beds', 0) > 10:
        color = 'green'
        status = f"✅ {hosp['available_beds']} beds"
    elif hosp.get('available_beds', 0) > 5:
        color = 'blue'
        status = f"⚠️ {hosp['available_beds']} beds"
    else:
        color = 'red'
        status = f"❌ {hosp['available_beds']} beds"
    
    folium.Marker(
        location=[hosp['latitude'], hosp['longitude']],
        popup=f"🏥 {hosp['name']}<br>{status}<br>Specialties: {', '.join(hosp.get('specialties', []))}",
        icon=folium.Icon(
            color=color,
            icon='hospital',
            prefix='fa',
            icon_color='white'
        ),
        tooltip=f"🏥 {hosp['name']}"
    ).add_to(map)

# ===== ADD LAYER CONTROL (to toggle visibility) =====
folium.LayerControl().add_to(map)

# Display map with full interactivity
st_folium(
    map,
    width=1400,
    height=700,
    use_container_width=True
)

# Legend
st.sidebar.markdown("""
## 🗺️ Map Legend

### 🚑 Ambulances
- 🚑 **Red** = ALS (Advanced Life Support)
- 🚐 **Orange** = BLS (Basic Life Support)
- 🚙 **Yellow** = Mini Ambulance

### 🔴 Incidents (by Severity)
- 🔴 **Red Circle** = Critical
- 🟠 **Orange Circle** = Severe
- 🟡 **Yellow Circle** = Moderate
- 🟢 **Green Circle** = Minor

### 🏥 Hospitals (by Beds)
- 🟢 **Green** = >10 beds available
- 🔵 **Blue** = 5-10 beds available
- 🔴 **Red** = <5 beds available

### Controls
- **Drag** = Pan map left/right/up/down
- **Scroll** = Zoom in/out
- **Click markers** = See details
- **Layer control** = Toggle visibility
""")
```

---

## 🎮 HOW TO USE THE INTERACTIVE MAP

### Dragging (Moving Around):
1. **Click and drag** the map left/right or up/down
2. Map smoothly pans in that direction
3. See more ambulances, hospitals, incidents as you explore

### Zooming:
1. **Scroll wheel** to zoom in/out
2. **Double-click** to zoom to that location
3. **Pinch** on mobile to zoom

### Clicking Markers:
1. **Click any marker** (ambulance, hospital, incident)
2. **Popup appears** with details (ID, status, beds, ETA)
3. **Click away** to close popup

### Identifying Types:
- 🚑 Red ambulance icon = ALS (advanced)
- 🚐 Orange ambulance icon = BLS (basic)
- 🚙 Yellow car icon = Mini ambulance
- 🔴 Red filled circle = Critical incident
- 🏥 Hospital icon (colored by bed availability) = Hospital

---

## 💡 OPTION 2: Pure HTML/JavaScript (For Even Better Interactivity)

If Streamlit feels too slow, use pure Leaflet in HTML:

```python
import streamlit as st
import requests
import json

st.set_page_config(layout="wide")

# Fetch data
ambulances = requests.get('http://localhost:8000/ambulances').json()
hospitals = requests.get('http://localhost:8000/hospitals').json()
incidents = requests.get('http://localhost:8000/incidents').json()

# Create HTML with Leaflet
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        .info {{ padding: 6px 8px; font: 14px Arial, Helvetica, sans-serif; background: white; box-shadow: 0 0 15px rgba(0,0,0,0.2); border-radius: 5px; }}
        .legend {{ line-height: 18px; color: #555; }}
        .legend i {{ width: 18px; height: 18px; float: left; margin-right: 8px; border-radius: 50%; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        // Create map
        const map = L.map('map').setView([19.0760, 72.8777], 13);
        
        // Add tiles
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19,
            dragging: true,
            touchZoom: true,
            scrollWheelZoom: true
        }}).addTo(map);
        
        // Add ambulances
        const ambulances = {json.dumps(ambulances)};
        ambulances.forEach(amb => {{
            const color = amb.type === 'ALS' ? 'red' : amb.type === 'BLS' ? 'orange' : 'yellow';
            const icon = L.icon({{
                iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-${{color}}.png`,
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                shadowSize: [41, 41],
                iconAnchor: [12, 41],
                shadowAnchor: [12, 41],
                popupAnchor: [1, -34]
            }});
            
            L.marker([amb.latitude, amb.longitude], {{icon: icon}})
                .bindPopup(`🚑 ${{amb.type}} Ambulance ${{amb.id}}<br>Status: ${{amb.status}}`)
                .addTo(map);
        }});
        
        // Add hospitals
        const hospitals = {json.dumps(hospitals)};
        hospitals.forEach(hosp => {{
            const icon = L.icon({{
                iconUrl: 'https://raw.githubusercontent.com/ionic-team/ionicons/main/src/svg/hospital-sharp.svg',
                iconSize: [32, 32],
                iconAnchor: [16, 32],
                popupAnchor: [0, -32]
            }});
            
            L.marker([hosp.latitude, hosp.longitude], {{icon: icon}})
                .bindPopup(`🏥 ${{hosp.name}}<br>Available Beds: ${{hosp.available_beds}}<br>Specialties: ${{hosp.specialties.join(', ')}}`)
                .addTo(map);
        }});
        
        // Add incidents
        const incidents = {json.dumps(incidents)};
        incidents.forEach(inc => {{
            const color = inc.severity === 'critical' ? 'red' : inc.severity === 'severe' ? 'orange' : inc.severity === 'moderate' ? 'yellow' : 'green';
            const radius = inc.severity === 'critical' ? 12 : inc.severity === 'severe' ? 10 : inc.severity === 'moderate' ? 8 : 6;
            
            L.circleMarker([inc.latitude, inc.longitude], {{
                color: color,
                fillColor: color,
                fillOpacity: 0.8,
                radius: radius,
                weight: 2
            }})
            .bindPopup(`${{inc.severity.toUpperCase()}}<br>${{inc.type}}<br>ETA: ${{inc.eta}} min`)
            .addTo(map);
        }});
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=700)
```

---

## 🎨 SYMBOL REFERENCE

### Ambulances:
```
🚑 Red     = ALS (Advanced Life Support) - Most equipped
🚐 Orange  = BLS (Basic Life Support) - Standard
🚙 Yellow  = Mini - Basic/Light injuries
```

### Incidents:
```
🔴 Red Circle    = CRITICAL - Life threatening
🟠 Orange Circle = SEVERE - Serious injury
🟡 Yellow Circle = MODERATE - Medium injury
🟢 Green Circle  = MINOR - Light injury
```

### Hospitals:
```
🟢 Green Hospital  = Many beds available (>10)
🔵 Blue Hospital   = Some beds (5-10)
🔴 Red Hospital    = Few beds (<5)
```

---

## ✅ QUICK TEST

Replace your current `ui/citizen_tracker.py` with this code and:

1. Run: `.venv\Scripts\streamlit run ui/app.py`
2. Open: `http://localhost:8501`
3. **Try dragging** the map left/right
4. **Scroll** to zoom
5. **Click** any marker to see details
6. Different colors = different ambulance types

---

## 🔄 LIVE UPDATE VERSION

If you want the map to update every 5 seconds with live ambulance positions:

```python
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import time

st.set_page_config(layout="wide")

# Auto-refresh every 5 seconds
refresh_interval = st.slider("Refresh interval (seconds)", 1, 30, 5)

placeholder = st.empty()

while True:
    with placeholder.container():
        # Create fresh map
        map = folium.Map(
            location=[19.0760, 72.8777],
            zoom_start=13,
            tiles="OpenStreetMap",
            prefer_canvas=True,
            max_bounds=True
        )
        
        # Get live data
        try:
            ambulances = requests.get('http://localhost:8000/ambulances', timeout=2).json()
            hospitals = requests.get('http://localhost:8000/hospitals', timeout=2).json()
            incidents = requests.get('http://localhost:8000/incidents', timeout=2).json()
            
            # Add markers (code from above)
            for amb in ambulances:
                # ... add ambulance marker ...
                pass
            
            for hosp in hospitals:
                # ... add hospital marker ...
                pass
            
            for inc in incidents:
                # ... add incident marker ...
                pass
            
            # Display
            st_folium(map, width=1400, height=700)
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    
    time.sleep(refresh_interval)
```

---

## 🚀 SUMMARY

**Your map NOW has:**
- ✅ Full dragging/panning (move left/right/up/down)
- ✅ Smooth zooming (scroll or double-click)
- ✅ Different symbols for ambulances (Red/Orange/Yellow)
- ✅ Different colors for incidents (by severity)
- ✅ Hospital symbols with bed availability
- ✅ Clickable popups with details
- ✅ Layer control to toggle visibility
- ✅ Responsive & smooth

**No payment needed - all FREE!**

Try it now and let me know! 🗺️✨
