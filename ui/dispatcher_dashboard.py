import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime
import random
import requests

# Get backend URL from secrets (production) or use localhost (development)
BACKEND_URL = st.secrets.get("backend", {}).get("API_URL", "http://localhost:8000")


def run():
    # ------------------------------------------------------------------ #
    # Fetch live data from backend
    # ------------------------------------------------------------------ #
    @st.cache_data(ttl=8)
    def fetch_fleet():
        try:
            resp = requests.get(f"{BACKEND_URL}/ambulances/active", timeout=3).json()
            ambulances = resp.get('ambulances', []) if isinstance(resp, dict) else resp
            if ambulances:
                rows = []
                for a in ambulances:
                    rows.append({
                        'ID': a.get('id', ''),
                        'Type': a.get('type', 'BLS'),
                        'Status': a.get('status', 'unknown').replace('_', ' ').title(),
                        'Driver': a.get('driver_name', 'N/A'),
                        'lat': a.get('latitude', 19.076),
                        'lon': a.get('longitude', 72.877),
                        'Response Time': '--',
                    })
                return pd.DataFrame(rows), True
        except Exception:
            pass
        df = pd.DataFrame({
            'ID': ['ALS-001', 'ALS-002', 'BLS-001', 'BLS-002', 'MINI-001'],
            'Type': ['ALS', 'ALS', 'BLS', 'BLS', 'Mini'],
            'Status': ['Available', 'En Route', 'Available', 'On Scene', 'Available'],
            'Driver': ['Raj Kumar', 'Priya Singh', 'Amit Patel', 'Suresh Nair', 'Deepa Gupta'],
            'Response Time': ['--', '12 min', '--', 'On Scene', '--'],
        })
        base_lat, base_lon = 19.0760, 72.8777
        df['lat'] = [base_lat + random.uniform(-0.02, 0.02) for _ in range(len(df))]
        df['lon'] = [base_lon + random.uniform(-0.02, 0.02) for _ in range(len(df))]
        return df, False

    @st.cache_data(ttl=8)
    def fetch_incidents():
        try:
            resp = requests.get(f"{BACKEND_URL}/incidents/active", timeout=3).json()
            incidents = resp.get('incidents', []) if isinstance(resp, dict) else resp
            if incidents:
                rows = []
                for inc in incidents:
                    rows.append({
                        'ID': inc.get('id', ''),
                        'Type': inc.get('incident_type', 'Unknown'),
                        'Severity': inc.get('severity', 'moderate').replace('_', ' ').title(),
                        'Status': inc.get('status', 'waiting').replace('_', ' ').title(),
                        'Patient': inc.get('patient_name', 'N/A'),
                        'Time': inc.get('reported_at', datetime.now().strftime('%I:%M %p')),
                    })
                return pd.DataFrame(rows), True
        except Exception:
            pass
        return pd.DataFrame({
            'ID': ['INC-2401', 'INC-2402', 'INC-2403'],
            'Type': ['Cardiac', 'Trauma', 'Respiratory'],
            'Severity': ['Critical', 'High', 'Medium'],
            'Status': ['Assigned', 'Waiting', 'En Route'],
            'Patient': ['Ramesh S.', 'Priya V.', 'Ajay K.'],
            'Time': ['12:34 PM', '12:45 PM', '12:52 PM'],
        }), False

    @st.cache_data(ttl=30)
    def fetch_hospitals():
        try:
            resp = requests.get(f"{BACKEND_URL}/hospitals", timeout=3).json()
            return resp.get('hospitals', []) if isinstance(resp, dict) else resp, True
        except Exception:
            return [], False

    fleet_df, fleet_live = fetch_fleet()
    incidents_df, incidents_live = fetch_incidents()
    hospitals, _ = fetch_hospitals()

    # ------------------------------------------------------------------ #
    # Header
    # ------------------------------------------------------------------ #
    live_badge = '<span class="live-badge live-green">● LIVE</span>' if (fleet_live and incidents_live) else '<span class="live-badge live-yellow">● DEMO</span>'

    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="display:flex; align-items:center; gap:15px;">
            <h1 class="brand-header" style="font-size:2.2em;">🎯 Dispatcher Control</h1>
            {live_badge}
        </div>
        <p class="brand-sub">Fleet Management & Incident Coordination Center</p>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # KPI Row
    # ------------------------------------------------------------------ #
    total = len(fleet_df)
    avail = len(fleet_df[fleet_df['Status'].str.lower().str.contains('available')])
    en_route = len(fleet_df[fleet_df['Status'].str.lower().str.contains('en route|responding')])
    active_inc = len(incidents_df)
    pending = len(incidents_df[incidents_df['Status'].str.lower().str.contains('waiting')]) if not incidents_df.empty else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f'<div class="kpi-card"><h4>TOTAL UNITS</h4><h2>{total}</h2></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi-card kpi-green"><h4>AVAILABLE</h4><h2>{avail}</h2></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi-card kpi-orange"><h4>EN ROUTE</h4><h2>{en_route}</h2></div>', unsafe_allow_html=True)
    with k4:
        st.markdown(f'<div class="kpi-card kpi-red"><h4>INCIDENTS</h4><h2>{active_inc}</h2></div>', unsafe_allow_html=True)
    with k5:
        st.markdown(f'<div class="kpi-card" style="background:linear-gradient(135deg,#8e44ad,#9b59b6);box-shadow:0 8px 25px rgba(142,68,173,0.3);"><h4>PENDING</h4><h2>{pending}</h2></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # Tabs
    # ------------------------------------------------------------------ #
    tab1, tab2, tab3, tab4 = st.tabs(["🚗 Fleet Status", "🚨 Incidents", "📊 Analytics", "⚙️ Settings"])

    # ---- TAB 1: Fleet ---- #
    with tab1:
        map_col, action_col = st.columns([2.5, 1], gap="large")

        with map_col:
            m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)

            colors = {'ALS': 'red', 'BLS': 'orange', 'Mini': 'green', 'BIKE': 'darkred'}
            for _, row in fleet_df.iterrows():
                color = colors.get(row['Type'], 'blue')
                folium.Marker(
                    [row['lat'], row['lon']],
                    popup=f"<b>{row['ID']}</b><br>{row['Type']}<br>👤 {row['Driver']}<br>Status: {row['Status']}",
                    icon=folium.Icon(color=color, icon='ambulance', prefix='fa', icon_color='white'),
                    tooltip=f"{row['Type']} - {row['ID']} ({row['Status']})"
                ).add_to(m)

            for hosp in hospitals:
                beds = hosp.get('available_beds', 0)
                hc = 'green' if beds > 10 else ('blue' if beds > 5 else 'red')
                folium.Marker(
                    [hosp.get('latitude', 0), hosp.get('longitude', 0)],
                    popup=f"🏥 {hosp.get('name', '')}<br>Beds: {beds}/{hosp.get('total_beds', 0)}",
                    icon=folium.Icon(color=hc, icon='plus-square', prefix='fa', icon_color='white'),
                    tooltip=f"🏥 {hosp.get('name', '')}"
                ).add_to(m)

            st_folium(m, width=None, height=450, use_container_width=True, returned_objects=[])

        with action_col:
            st.markdown("### ⚡ Quick Actions")

            if st.button("🔄 Refresh Data", use_container_width=True, key="dd_refresh"):
                st.cache_data.clear()
                st.rerun()
            if st.button("📞 New Dispatch", use_container_width=True, key="dd_dispatch"):
                st.info("Opening dispatch wizard...")
            if st.button("⚠️ Alert All Units", use_container_width=True, key="dd_alert"):
                st.warning("Alert broadcast to all units!")

            st.markdown("---")
            st.markdown("### 📋 Fleet Summary")
            for _, row in fleet_df.iterrows():
                status_raw = row['Status'].lower()
                if 'available' in status_raw:
                    pill = '<span class="status-pill pill-available">Available</span>'
                elif 'route' in status_raw or 'responding' in status_raw:
                    pill = '<span class="status-pill pill-enroute">En Route</span>'
                else:
                    pill = '<span class="status-pill pill-onscene">On Scene</span>'

                type_icon = {'ALS': '🔴', 'BLS': '🟠', 'Mini': '🟡', 'BIKE': '🟢'}.get(row['Type'], '⚪')
                st.markdown(f"""
                <div class="glass-card" style="padding:8px 12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600;">{type_icon} {row['ID']}</span>
                        {pill}
                    </div>
                    <span style="color:#888; font-size:0.8em;">👤 {row['Driver']}</span>
                </div>
                """, unsafe_allow_html=True)

    # ---- TAB 2: Incidents ---- #
    with tab2:
        if incidents_df.empty:
            st.markdown("""
            <div style="text-align:center; padding:40px;">
                <span style="font-size:3em;">✅</span>
                <h3>No Active Incidents</h3>
                <p style="color:#888;">All clear — no emergencies reported.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, row in incidents_df.iterrows():
                severity = row.get('Severity', 'Medium')
                sev_lower = severity.lower()
                sev_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(sev_lower, '🟡')
                border_color = {'critical': '#e74c3c', 'high': '#f39c12', 'medium': '#f1c40f', 'low': '#2ecc71'}.get(sev_lower, '#f1c40f')

                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid {border_color}; padding: 15px 20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:1.2em; font-weight:700;">{sev_icon} {row['ID']}</span>
                            <span style="color:#888;"> — {row['Type']}</span>
                        </div>
                        <span class="status-pill {'pill-available' if 'complet' in row['Status'].lower() else 'pill-enroute' if 'route' in row['Status'].lower() else 'pill-onscene'}">{row['Status']}</span>
                    </div>
                    <div style="margin-top:8px; color:#aaa; font-size:0.9em;">
                        👤 {row.get('Patient', 'N/A')} &nbsp;·&nbsp; ⏰ {row.get('Time', '')} &nbsp;·&nbsp; Severity: <span class="severity-{sev_lower}">{severity}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.button(f"📍 Assign", key=f"dd_assign_{idx}", use_container_width=True)
                with c2:
                    st.button(f"📞 Call", key=f"dd_call_{idx}", use_container_width=True)
                with c3:
                    st.button(f"✓ Close", key=f"dd_close_{idx}", use_container_width=True)

    # ---- TAB 3: Analytics ---- #
    with tab3:
        st.markdown("### 📈 Performance Dashboard")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Avg Response", "8.2 min", "-1.2 min")
        with m2:
            st.metric("Success Rate", "94.5%", "+2.1%")
        with m3:
            st.metric("Calls Today", f"{active_inc + 9}", "+3")
        with m4:
            st.metric("Hospitals Online", f"{len(hospitals)}", "0")

        st.markdown("---")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### Response Time Trend")
            chart_data = pd.DataFrame({
                'Time': pd.date_range('12:00', periods=8, freq='15min'),
                'Response (min)': [9.5, 9.2, 8.8, 8.5, 8.2, 8.0, 7.9, 7.8]
            })
            st.line_chart(chart_data.set_index('Time'))

        with chart_col2:
            st.markdown("#### Incidents by Type")
            type_data = pd.DataFrame({
                'Type': ['Cardiac', 'Trauma', 'Respiratory', 'Burn', 'Other'],
                'Count': [5, 3, 2, 1, 1]
            })
            st.bar_chart(type_data.set_index('Type'))

        # Fleet utilization
        st.markdown("#### Fleet Utilization")
        util_data = pd.DataFrame({
            'Unit': fleet_df['ID'].tolist(),
            'Utilization %': [random.randint(40, 95) for _ in range(len(fleet_df))]
        })
        st.bar_chart(util_data.set_index('Unit'))

    # ---- TAB 4: Settings ---- #
    with tab4:
        st.markdown("### ⚙️ System Configuration")

        set1, set2 = st.columns(2)
        with set1:
            st.markdown("#### Notifications")
            st.checkbox("🔊 Audio Alerts", value=True, key="dd_audio")
            st.checkbox("📧 Email Notifications", value=True, key="dd_email")
            st.checkbox("📱 SMS Alerts", value=False, key="dd_sms")
            st.select_slider("Alert Level", ["Low", "Medium", "High"], value="High", key="dd_lvl")

        with set2:
            st.markdown("#### Display")
            st.slider("Refresh Rate (sec)", 5, 60, 15, key="dd_rate")
            st.slider("Max Incidents Display", 5, 20, 10, key="dd_max")
            st.selectbox("Map Style", ["CartoDB Dark", "OpenStreetMap", "Stamen Terrain"], key="dd_map")

        st.markdown("---")
        st.markdown("#### Backend Health")
        try:
            health = requests.get(f"{BACKEND_URL}/health", timeout=2).json()
            status = health.get('status', 'unknown')
            model = health.get('model_loaded', False)
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; gap:30px;">
                    <div>🟢 <b>Status:</b> {status}</div>
                    <div>{'🟢' if model else '🔴'} <b>ML Model:</b> {'Loaded' if model else 'Not loaded'}</div>
                    <div>🟢 <b>URL:</b> {BACKEND_URL}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.markdown("""
            <div class="glass-card" style="border-left:3px solid #e74c3c;">
                <span style="color:#e74c3c;">🔴 Backend Offline</span> — Start with: <code>.venv\\Scripts\\python.exe modules\\backend\\app.py</code>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown(f'<p class="footer-text">Last updated: {datetime.now().strftime("%H:%M:%S")} IST</p>', unsafe_allow_html=True)


if __name__ == "__main__":
    run()