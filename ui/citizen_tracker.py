import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import random

# The UI scripts are refactored to expose a `run()` function so they can be integrated
# into a single Streamlit router. Imports remain at module-level; the page
# configuration and rendering are inside `run()` to avoid running on import.

def run():
    # Page configuration handled by the top-level router

    # Custom CSS for better styling
    st.markdown("""
    <style>
        .main-header { color: #e74c3c; font-size: 2.5em; font-weight: bold; margin-bottom: 1em; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .status-active { color: #27ae60; font-weight: bold; }
        .status-enroute { color: #f39c12; font-weight: bold; }
        .status-delayed { color: #e74c3c; font-weight: bold; }
        .info-box { background: #ecf0f1; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #3498db; }
        .hospital-info { background: #fff3cd; padding: 12px; border-radius: 5px; margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

    # Cache hospital data
    @st.cache_data
    def load_hospitals():
        try:
            return pd.read_csv('data/raw/hospitals_navi_mumbai.csv')
        except FileNotFoundError:
            return pd.DataFrame({
                'name': ['Fortis Hospital', 'Apollo Clinic', 'Sai Nursing Home', 'Nerul Hospital'],
                'lat': [19.0760, 19.0860, 19.0900, 19.0820],
                'lon': [72.8777, 72.8877, 72.8950, 72.8650],
                'beds': [150, 200, 80, 120],
                'available_beds': [45, 78, 22, 55]
            })

    # Cache ambulance data with session state
    if 'ambulances' not in st.session_state:
        st.session_state.ambulances = [
            {'id': 'ALS-001', 'lat': 19.0760, 'lon': 72.8777, 'status': 'En Route', 'eta': 12, 'type': 'ALS', 'driver': 'Raj Kumar'},
            {'id': 'BLS-002', 'lat': 19.0860, 'lon': 72.8877, 'status': 'Available', 'eta': 0, 'type': 'BLS', 'driver': 'Priya Singh'},
            {'id': 'MINI-003', 'lat': 19.0920, 'lon': 72.8900, 'status': 'En Route', 'eta': 8, 'type': 'Mini', 'driver': 'Amit Patel'},
        ]

    hospitals = load_hospitals()

    # Header
    st.markdown('<h1 class="main-header">🚑 NaviRaksha: Live Ambulance Tracker</h1>', unsafe_allow_html=True)
    st.markdown('Real-time emergency response tracking for Navi Mumbai', unsafe_allow_html=True)

    # Sidebar for user location
    with st.sidebar:
        st.markdown("### 📍 Your Location")
        user_lat = st.number_input("Latitude", value=19.0760, step=0.001)
        user_lon = st.number_input("Longitude", value=72.8777, step=0.001)
        
        st.markdown("### 🎯 Incident Details")
        incident_type = st.selectbox("Type", ["Medical", "Trauma", "Cardiac", "Respiratory"])
        severity = st.select_slider("Severity", ["Low", "Medium", "High", "Critical"], value="High")
        
        st.markdown("---")
        if st.button("📱 Call Ambulance"):
            st.success("✓ Ambulance dispatched! ETA: 8-12 minutes")

    # Main content
    col1, col2 = st.columns([2.5, 1], gap="large")

    with col1:
        st.markdown("### 🗺️ Live Tracking Map")
        
        # Create map
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=13, tiles="OpenStreetMap")
        
        # Add user location
        folium.CircleMarker([user_lat, user_lon], radius=8, popup="Your Location", 
                            color="blue", fill=True, fillColor="blue", fillOpacity=0.7).add_to(m)
        
        # Add hospitals
        for _, h in hospitals.iterrows():
            folium.Marker(
                [h['lat'], h['lon']], 
                popup=f"<b>{h['name']}</b><br>Beds: {h['available_beds']}/{h['beds']}<br>Available",
                icon=folium.Icon(color='green', icon='hospital-o')
            ).add_to(m)
        
        # Add ambulances with color coding
        for amb in st.session_state.ambulances:
            color_map = {'ALS': 'red', 'BLS': 'blue', 'Mini': 'orange'}
            folium.Marker(
                [amb['lat'], amb['lon']], 
                popup=f"<b>{amb['id']}</b><br>Type: {amb['type']}<br>Driver: {amb['driver']}<br>ETA: {amb['eta']} min",
                icon=folium.Icon(color=color_map.get(amb['type'], 'gray'), prefix='fa', icon='ambulance')
            ).add_to(m)
        
        st_folium(m, width=None, height=500)

    with col2:
        st.markdown("### ⏱️ ETA Updates")
        
        for amb in st.session_state.ambulances:
            if amb['status'] == 'En Route':
                status_class = 'status-enroute'
                status_icon = '🚗'
            elif amb['eta'] > 15:
                status_class = 'status-delayed'
                status_icon = '⚠️'
            else:
                status_class = 'status-active'
                status_icon = '✓'
            
            with st.container(border=True):
                st.markdown(f"{status_icon} **{amb['id']}** ({amb['type']})")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("ETA", f"{amb['eta']} min", delta=None)
                with col_b:
                    st.markdown(f"<p class='{status_class}'>{amb['status']}</p>", unsafe_allow_html=True)
                st.caption(f"Driver: {amb['driver']}")

    # Bottom section - Hospitals nearby
    st.markdown("---")
    st.markdown("### 🏥 Nearby Hospitals")

    hosp_cols = st.columns(len(hospitals))
    for idx, (_, h) in enumerate(hospitals.iterrows()):
        with hosp_cols[idx]:
            with st.container(border=True):
                st.markdown(f"**{h['name']}**")
                st.metric("Available Beds", f"{h['available_beds']}/{h['beds']}")
                distance = np.sqrt((h['lat']-user_lat)**2 + (h['lon']-user_lon)**2) * 111  # km
                st.caption(f"📍 {distance:.1f} km away")


if __name__ == "__main__":
    run()