import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import random
import requests
from datetime import datetime

# Get backend URL from secrets (production) or use localhost (development)
BACKEND_URL = st.secrets.get("backend", {}).get("API_URL", "http://localhost:8000")


def run():
    # Header
    st.markdown("""
    <div style="margin-bottom: 15px;">
        <h1 class="brand-header" style="font-size:2.2em;">🧪 Simulation Engine</h1>
        <p class="brand-sub">Generate & test realistic emergency scenarios</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Simulation Config")
        num_ambulances = st.slider("🚗 Ambulances", 1, 15, 5, key="sim_amb_n")
        num_incidents = st.slider("🚨 Incidents", 1, 10, 4, key="sim_inc_n")
        
        st.markdown("---")
        st.markdown("### 🌦️ Conditions")
        is_monsoon = st.checkbox("🌧️ Monsoon Active", key="sim_monsoon")
        hour = st.slider("⏰ Hour of Day", 0, 23, datetime.now().hour, key="sim_hour")
        
        time_label = "🌙 Night" if hour < 6 or hour >= 23 else "🌅 Rush Hour" if (7 <= hour <= 9 or 16 <= hour <= 19) else "☀️ Off-Peak"
        st.markdown(f'<div class="glass-card" style="padding:10px;text-align:center;"><b>{time_label}</b><br><span style="color:#888;">Hour: {hour}:00</span></div>', unsafe_allow_html=True)

    zones = ["Vashi", "Belapur", "Nerul", "Kharghar", "Panvel", "Turbhe", "Sanpada", "Ulwe", "Airoli", "Dronagiri"]
    ambulance_types = ["ALS", "BLS", "Mini", "Bike"]
    incident_types = ["Cardiac", "Trauma", "Respiratory", "Burn", "Poison", "Drowning", "Fall"]
    severities = ["Critical", "High", "Medium", "Low"]

    # Generate data
    def generate_ambulances(n):
        ambulances = []
        for i in range(n):
            ambulances.append({
                'id': f"{ambulance_types[i % 4]}-{i+1:03d}",
                'lat': 19.0760 + random.uniform(-0.04, 0.04),
                'lon': 72.8777 + random.uniform(-0.04, 0.04),
                'status': random.choice(['Available', 'En Route', 'On Scene']),
                'eta': random.randint(3, 18) if random.choice([True, False]) else 0,
                'type': ambulance_types[i % 4],
                'zone': zones[i % len(zones)],
                'driver': f"Driver-{i+1}"
            })
        return ambulances

    def generate_incidents(n):
        incidents = []
        for i in range(n):
            sev = random.choice(severities)
            incidents.append({
                'id': f"INC-{random.randint(1000,9999)}",
                'lat': 19.0760 + random.uniform(-0.04, 0.04),
                'lon': 72.8777 + random.uniform(-0.04, 0.04),
                'severity': sev,
                'type': random.choice(incident_types),
                'zone': zones[i % len(zones)],
                'status': random.choice(['Waiting', 'Assigned', 'En Route']),
                'patient': f"Patient-{random.randint(100,999)}"
            })
        return incidents

    # Generate on change
    if ('sim_ambulances' not in st.session_state or
        st.session_state.get('sim_num_amb') != num_ambulances or
        st.session_state.get('sim_num_inc') != num_incidents):
        st.session_state.sim_ambulances = generate_ambulances(num_ambulances)
        st.session_state.sim_incidents = generate_incidents(num_incidents)
        st.session_state.sim_num_amb = num_ambulances
        st.session_state.sim_num_inc = num_incidents

    ambulances = st.session_state.sim_ambulances
    incidents = st.session_state.sim_incidents

    # ---- KPIs ---- #
    avail = sum(1 for a in ambulances if a['status'] == 'Available')
    critical = sum(1 for i in incidents if i['severity'] == 'Critical')
    waiting = sum(1 for i in incidents if i['status'] == 'Waiting')

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f'<div class="kpi-card"><h4>AMBULANCES</h4><h2>{num_ambulances}</h2></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card kpi-green"><h4>AVAILABLE</h4><h2>{avail}</h2></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card kpi-red"><h4>CRITICAL</h4><h2>{critical}</h2></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card kpi-orange"><h4>WAITING</h4><h2>{waiting}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ---- Two columns: Table + Map ---- #
    tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📋 Data Tables", "🧪 ETA Test"])

    with tab1:
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)

        amb_colors = {'ALS': 'red', 'BLS': 'orange', 'Mini': 'green', 'Bike': 'darkred'}
        for amb in ambulances:
            color = amb_colors.get(amb['type'], 'gray')
            folium.Marker(
                [amb['lat'], amb['lon']],
                popup=f"<b>🚑 {amb['id']}</b><br>Type: {amb['type']}<br>Status: {amb['status']}<br>Zone: {amb['zone']}",
                icon=folium.Icon(color=color, icon='ambulance', prefix='fa', icon_color='white'),
                tooltip=f"{amb['type']} — {amb['id']}"
            ).add_to(m)

        sev_colors = {'Critical': 'red', 'High': 'orange', 'Medium': 'beige', 'Low': 'green'}
        for inc in incidents:
            color = sev_colors.get(inc['severity'], 'gray')
            folium.CircleMarker(
                [inc['lat'], inc['lon']],
                radius=12 if inc['severity'] == 'Critical' else 8,
                color=color, fill=True, fillColor=color, fillOpacity=0.7,
                tooltip=f"⚠️ {inc['severity']} — {inc['type']}",
                popup=f"<b>{inc['id']}</b><br>{inc['type']}<br>Severity: {inc['severity']}<br>Patient: {inc['patient']}"
            ).add_to(m)

        st_folium(m, width=None, height=500, use_container_width=True, returned_objects=[])

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🚗 Fleet")
            amb_df = pd.DataFrame(ambulances)[['id', 'type', 'status', 'zone', 'driver']]
            st.dataframe(amb_df, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("### 🚨 Incidents")
            inc_df = pd.DataFrame(incidents)[['id', 'type', 'severity', 'zone', 'status', 'patient']]
            st.dataframe(inc_df, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### 🧪 Live ETA Prediction Test")
        st.markdown("Send a test dispatch request to the backend API and see the response.")

        eta_col1, eta_col2 = st.columns(2)
        with eta_col1:
            test_dist = st.number_input("Distance (km)", 1.0, 20.0, 5.0, key="sim_dist")
            test_type = st.selectbox("Incident Type", incident_types, key="sim_itype")
        with eta_col2:
            test_sev = st.selectbox("Severity", ["CRITICAL", "SEVERE", "MODERATE", "MINOR"], key="sim_sev")
            test_hour = st.number_input("Hour", 0, 23, hour, key="sim_test_hour")

        if st.button("🚀 Send Dispatch Request", use_container_width=True, type="primary", key="sim_dispatch_btn"):
            try:
                payload = {
                    "patient_lat": 19.076, "patient_lon": 72.877,
                    "incident_type": test_type, "severity": test_sev,
                    "distance": test_dist, "hour": test_hour,
                    "is_monsoon": is_monsoon
                }
                resp = requests.post(f"{BACKEND_URL}/dispatch", json=payload, timeout=5)
                data = resp.json()

                if resp.status_code == 200:
                    r1, r2 = st.columns(2)
                    with r1:
                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 3px solid #2ecc71;">
                            <h4 style="margin:0;">✅ Dispatch Response</h4>
                            <br>
                            <b>Ambulance:</b> {data.get('ambulance_id', 'N/A')}<br>
                            <b>Type:</b> {data.get('ambulance_type', 'N/A')}<br>
                            <b>ETA:</b> <span style="color:#00d4ff !important; font-size:1.3em; font-weight:700;">{data.get('eta_minutes', 'N/A')} min</span><br>
                            <b>Driver:</b> {data.get('ambulance_driver', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                    with r2:
                        hosp = data.get('hospital', {})
                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 3px solid #3498db;">
                            <h4 style="margin:0;">🏥 Assigned Hospital</h4>
                            <br>
                            <b>Name:</b> {hosp.get('name', 'N/A')}<br>
                            <b>Beds:</b> {hosp.get('available_beds', '?')}/{hosp.get('total_beds', '?')}<br>
                            <b>Severity:</b> {test_sev}<br>
                            <b>Weather:</b> {'🌧️ Monsoon' if is_monsoon else '☀️ Normal'}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {data.get('error', 'Unknown')}")

            except Exception as e:
                st.error(f"❌ Backend not responding: {e}")
                st.info("Start the backend: `.venv\\Scripts\\python.exe modules\\backend\\app.py`")

    # Bottom buttons
    st.markdown("---")
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("🔄 Regenerate Data", use_container_width=True, key="sim_regen"):
            st.session_state.pop('sim_ambulances', None)
            st.rerun()
    with b2:
        if st.button("💾 Export to CSV", use_container_width=True, key="sim_export"):
            pd.DataFrame(ambulances).to_csv('simulation_ambulances.csv', index=False)
            pd.DataFrame(incidents).to_csv('simulation_incidents.csv', index=False)
            st.success("✓ Exported to CSV!")
    with b3:
        if st.button("🔗 Check Backend", use_container_width=True, key="sim_health"):
            try:
                h = requests.get(f"{BACKEND_URL}/health", timeout=2).json()
                st.success(f"✅ Backend online — Model: {'✅' if h.get('model_loaded') else '❌'}")
            except Exception:
                st.error("❌ Backend offline")

    st.markdown(f'<p class="footer-text">Simulation generated at {datetime.now().strftime("%H:%M:%S")} IST</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    run()
