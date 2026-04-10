import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import random
from datetime import datetime


def run():
    # Page configuration handled by the top-level router

    st.title("🚑 NaviRaksha Simulation Engine")
    st.markdown("Generate realistic test data for dashboards")

    # Sidebar controls
    st.sidebar.markdown("### ⚙️ Simulation Settings")
    num_ambulances = st.sidebar.slider("🚗 Number of Ambulances", 1, 15, 5)
    num_incidents = st.sidebar.slider("🚨 Number of Incidents", 1, 10, 4)

    zones = ["Vashi", "Belapur", "Nerul", "Kharghar", "Panvel", "Turbhe", "Sanpada", "Ulwe"]
    ambulance_types = ["ALS", "BLS", "Mini", "Bike"]
    incident_types = ["Cardiac", "Trauma", "Respiratory", "Burn", "Poison"]

    # Generate data
    def generate_ambulances(n):
        ambulances = []
        for i in range(n):
            ambulances.append({
                'id': f"{ambulance_types[i % 4]}-{i+1:03d}",
                'lat': 19.0760 + random.uniform(-0.03, 0.03),
                'lon': 72.8777 + random.uniform(-0.03, 0.03),
                'status': random.choice(['Available', 'En Route', 'On Scene']),
                'eta': random.randint(0, 25) if random.choice([True, False]) else 0,
                'type': ambulance_types[i % 4],
                'zone': zones[i % len(zones)]
            })
        return ambulances

    def generate_incidents(n):
        incidents = []
        for i in range(n):
            incidents.append({
                'id': f"INC-{i+1:04d}",
                'lat': 19.0760 + random.uniform(-0.03, 0.03),
                'lon': 72.8777 + random.uniform(-0.03, 0.03),
                'severity': random.choice(['Critical', 'High', 'Medium', 'Low']),
                'type': incident_types[i % len(incident_types)],
                'zone': zones[i % len(zones)],
                'status': random.choice(['Waiting', 'Assigned', 'En Route'])
            })
        return incidents

    # Generate data
    ambulances = generate_ambulances(num_ambulances)
    incidents = generate_incidents(num_incidents)

    # Display data
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🚗 Ambulances")
        amb_df = pd.DataFrame(ambulances)[['id', 'type', 'status', 'zone']]
        st.dataframe(amb_df, width='stretch', hide_index=True)

    with col2:
        st.markdown("### 🚨 Incidents")
        inc_df = pd.DataFrame(incidents)[['id', 'type', 'severity', 'zone']]
        st.dataframe(inc_df, width='stretch', hide_index=True)

    st.markdown("---")

    # Map
    st.markdown("### 🗺️ Simulation Map")
    m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)

    # Add ambulances
    amb_colors = {'ALS': 'red', 'BLS': 'blue', 'Mini': 'orange', 'Bike': 'darkred'}
    for amb in ambulances:
        color = amb_colors.get(amb['type'], 'gray')
        folium.Marker(
            [amb['lat'], amb['lon']],
            popup=f"{amb['id']} - {amb['status']}",
            icon=folium.Icon(color=color, icon='ambulance', prefix='fa')
        ).add_to(m)

    # Add incidents
    for inc in incidents:
        severity_color = {'Critical': 'darkred', 'High': 'red', 'Medium': 'orange', 'Low': 'yellow'}
        color = severity_color.get(inc['severity'], 'gray')
        folium.Marker(
            [inc['lat'], inc['lon']],
            popup=f"{inc['id']} - {inc['severity']}",
            icon=folium.Icon(color=color, icon='info-sign', prefix='glyphicon')
        ).add_to(m)

    st_folium(m, width=None, height=500)

    # Bottom controls
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Generate New Data"):
            st.rerun()

    with col2:
        if st.button("💾 Export to CSV"):
            pd.DataFrame(ambulances).to_csv('simulation_ambulances.csv', index=False)
            pd.DataFrame(incidents).to_csv('simulation_incidents.csv', index=False)
            st.success("✓ Exported to CSV!")

    with col3:
        if st.button("📊 Refresh Stats"):
            st.info("Data refreshed!")

    st.caption(f"Generated at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    run()