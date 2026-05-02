import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
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
            'Response Time (min)': [8, None, 12]  # Add response times for calculation
        }), False

    # Helper functions for KPI calculations
    def calculate_avg_response_time(incidents_df):
        if not isinstance(incidents_df, pd.DataFrame) or incidents_df.empty:
            return 0
        if 'Response Time (min)' not in incidents_df.columns:
            return 0
        response_times = incidents_df['Response Time (min)'].dropna()
        return response_times.mean() if not response_times.empty else 0

    def calculate_active_ambulances_ratio(fleet_df, incidents_df):
        active_ambulances = len(fleet_df[fleet_df['Status'].isin(['En Route', 'Incident Scene'])])
        total_incidents = len(incidents_df)
        return active_ambulances / total_incidents if total_incidents > 0 else 0

    def calculate_hospital_availability(hospitals_df):
        total_available = hospitals_df['Available Beds'].sum()
        total_beds = hospitals_df['Total Beds'].sum()
        return total_available / total_beds if total_beds > 0 else 0

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

    # Add fleet and incidents to session state
    if 'fleet' not in st.session_state:
        st.session_state.fleet = fleet_df.copy() if not fleet_df.empty else pd.DataFrame()
    if 'incidents' not in st.session_state:
        st.session_state.incidents = incidents_df.copy() if not incidents_df.empty else pd.DataFrame()
    
    # Add hospital data for availability
    if 'hospitals' not in st.session_state:
        st.session_state.hospitals = pd.DataFrame({
            'Name': ['Fortis Hospital', 'Apollo Clinic', 'Sai Nursing Home'],
            'Available Beds': [45, 78, 22],
            'Total Beds': [150, 200, 80]
        })

    # Initialize replay state with proper data
    if 'replay' not in st.session_state:
        st.session_state.replay = {
            'simulation_running': False,  # Tracks if simulation is running
            'current_step': 0,  # Current time step in simulation
            'max_steps': 10,
            'initial_fleet': fleet_df.copy(),
            'initial_incidents': incidents_df.copy(),
            'history': [],  # Store states for replay
            'timeline': [  # Mock timeline data with time-based status changes
                {'time': 1, 'ambulance_id': 'ALS-001', 'new_status': 'Dispatched', 'event': 'ALS-001 dispatched to incident'},
                {'time': 2, 'ambulance_id': 'ALS-001', 'new_status': 'En Route', 'event': 'ALS-001 en route'},
                {'time': 4, 'ambulance_id': 'ALS-001', 'new_status': 'On Scene', 'event': 'ALS-001 arrived on scene'},
                {'time': 6, 'ambulance_id': 'BLS-002', 'new_status': 'Dispatched', 'event': 'BLS-002 dispatched'},
                {'time': 7, 'ambulance_id': 'BLS-002', 'new_status': 'En Route', 'event': 'BLS-002 en route'},
                {'time': 9, 'ambulance_id': 'ALS-001', 'new_status': 'Completed', 'event': 'ALS-001 completed mission'},
                {'time': 10, 'ambulance_id': 'BLS-002', 'new_status': 'On Scene', 'event': 'BLS-002 arrived on scene'},
            ]
        }



    # ------------------------------------------------------------------ #
    # Header
    # ------------------------------------------------------------------ #
    live_badge = '<span class="live-badge live-green">● LIVE</span>' if (fleet_live and incidents_live) else '<span class="live-badge live-yellow">● DEMO</span>'

    # Calculate KPIs dynamically
    avg_response = calculate_avg_response_time(st.session_state.incidents)
    active_ratio = calculate_active_ambulances_ratio(st.session_state.fleet, st.session_state.incidents)
    hospital_avail = calculate_hospital_availability(st.session_state.hospitals)
    pending_calls = len(st.session_state.incidents[st.session_state.incidents['Status'] == 'Waiting'])

    # KPIs at top
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Active Units</h3>
            <h2>{len(st.session_state.fleet)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Avg Response</h3>
            <h2>{avg_response:.1f} min</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Today's Incidents</h3>
            <h2>{len(st.session_state.incidents)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Pending Calls</h3>
            <h2>{pending_calls}</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi5:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Active Ambulances Ratio</h3>
            <h2>{active_ratio:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi6:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>Hospital Availability</h3>
            <h2>{hospital_avail:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-bottom: 15px;">
        <div style="display:flex; align-items:center; gap:15px;">
            <h1 class="brand-header" style="font-size:2.2em;">🎯 Dispatcher Control</h1>
            {live_badge}
        </div>
        <p class="brand-sub">Fleet Management & Incident Coordination Center</p>
    </div>
    """, unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 Fleet Status", "🚨 Incidents Queue", "📊 Analytics", "⚙️ Settings", "🎬 Simulation Replay"])

    # ---- TAB 1: Fleet ---- #
    with tab1:
        map_col, action_col = st.columns([2.5, 1], gap="large")

        with map_col:
            m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)

            colors = {'ALS': 'red', 'BLS': 'orange', 'ADVANCED': 'blue', 'BIKE': 'green', 'MINI': 'green'}
            for _, row in st.session_state.fleet.iterrows():
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
            for _, row in st.session_state.fleet.iterrows():
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
        if st.session_state.incidents.empty:
            st.markdown("""
            <div style="text-align:center; padding:40px;">
                <span style="font-size:3em;">✅</span>
                <h3>No Active Incidents</h3>
                <p style="color:#888;">All clear — no emergencies reported.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for idx, row in st.session_state.incidents.iterrows():
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
            st.metric("Calls Today", f"{len(st.session_state.incidents) + 9}", "+3")
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
            'Unit': st.session_state.fleet['ID'].tolist(),
            'Utilization %': [random.randint(40, 95) for _ in range(len(st.session_state.fleet))]
        })
        st.bar_chart(util_data.set_index('Unit'))

        # Before vs After Comparison
        st.markdown("### Before vs After Comparison")
        if 'comparison' not in st.session_state:
            st.session_state.comparison = {
                'initial_avg_response': calculate_avg_response_time(st.session_state.replay['initial_incidents']),
                'final_avg_response': avg_response,
                'initial_active_ratio': calculate_active_ambulances_ratio(st.session_state.replay['initial_fleet'], st.session_state.replay['initial_incidents']),
                'final_active_ratio': active_ratio
            }
        
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.markdown("**Initial State**")
            st.metric("Avg Response Time", f"{st.session_state.comparison['initial_avg_response']:.1f} min")
            st.metric("Active Ambulances Ratio", f"{st.session_state.comparison['initial_active_ratio']:.2f}")
        with comp_col2:
            st.markdown("**Final State**")
            st.metric("Avg Response Time", f"{st.session_state.comparison['final_avg_response']:.1f} min")
            st.metric("Active Ambulances Ratio", f"{st.session_state.comparison['final_active_ratio']:.2f}")
        
        # Simple chart for comparison
        comparison_df = pd.DataFrame({
            'Metric': ['Avg Response Time', 'Active Ambulances Ratio'],
            'Initial': [st.session_state.comparison['initial_avg_response'], st.session_state.comparison['initial_active_ratio']],
            'Final': [st.session_state.comparison['final_avg_response'], st.session_state.comparison['final_active_ratio']]
        })
        st.bar_chart(comparison_df.set_index('Metric'))

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
                <span style="color:#e74c3c;">🔴 Backend Offline</span> — Start with: <code>python modules/backend/app.py</code>
            </div>
            """, unsafe_allow_html=True)
            st.error("Model engine connection failed. Using fallback heuristics.")
            st.info("Ensure the Flask backend is running on port 8000.")
            st.warning("Prediction confidence may be reduced in fallback mode.")

    with tab5:
        st.markdown("### Simulation Replay")
        
        # Controls
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("▶️ Play"):
                st.session_state.replay['simulation_running'] = True  # Start simulation loop
                # Capture before metrics only once
                if 'before_metrics' not in st.session_state.replay:
                    st.session_state.replay['before_metrics'] = {
                        'avg_response_time': calculate_avg_response_time(st.session_state.incidents),
                        'active_units_count': len(st.session_state.fleet),
                        'incident_count': len(st.session_state.incidents)
                    }
        with col2:
            if st.button("⏸️ Pause"):
                st.session_state.replay['simulation_running'] = False  # Pause without resetting step
        with col3:
            if st.button("🔄 Reset"):
                st.session_state.replay['simulation_running'] = False  # Stop simulation
                st.session_state.replay['current_step'] = 0  # Reset step to 0
                st.session_state.fleet = st.session_state.replay['initial_fleet'].copy()  # Reset fleet state
                st.session_state.incidents = st.session_state.replay['initial_incidents'].copy()  # Reset incidents state
                # Clear comparison metrics
                if 'before_metrics' in st.session_state.replay:
                    del st.session_state.replay['before_metrics']
                if 'after_metrics' in st.session_state.replay:
                    del st.session_state.replay['after_metrics']
                st.rerun()
        
        # Display current simulation time
        st.markdown(f"**Current Simulation Time:** {st.session_state.replay['current_step']} seconds")
        
        # Progress bar
        st.progress(st.session_state.replay['current_step'] / st.session_state.replay['max_steps'])
        
        # Display current events based on timeline
        current_events = [e for e in st.session_state.replay['timeline'] if e['time'] <= st.session_state.replay['current_step']]
        if current_events:
            st.markdown("#### Recent Events")
            for event in current_events[-3:]:  # Show last 3 events
                st.write(f"⏰ {event['time']}s: {event['event']}")
        
        # Replay engine: Time-based simulation loop
        if st.session_state.replay['simulation_running'] and st.session_state.replay['current_step'] < st.session_state.replay['max_steps']:
            import time
            time.sleep(1)  # Wait 1 second to simulate real-time progression
            st.session_state.replay['current_step'] += 1  # Increment current step
            
            # Update ambulance statuses based on timeline
            for event in st.session_state.replay['timeline']:
                if event['time'] == st.session_state.replay['current_step']:
                    # Find the ambulance and update its status
                    mask = st.session_state.fleet['ID'] == event['ambulance_id']
                    if mask.any():
                        st.session_state.fleet.loc[mask, 'Status'] = event['new_status']
                        st.success(f"Updated {event['ambulance_id']} to {event['new_status']}")
            
            st.rerun()  # Refresh UI to show updates
        
        # Capture after metrics when simulation completes
        if st.session_state.replay['current_step'] == st.session_state.replay['max_steps'] and 'after_metrics' not in st.session_state.replay:
            st.session_state.replay['after_metrics'] = {
                'avg_response_time': calculate_avg_response_time(st.session_state.incidents),
                'active_units_count': len(st.session_state.fleet),
                'incident_count': len(st.session_state.incidents)
            }
        
        # Display current ambulance status
        st.markdown("#### Current Ambulance Status")
        st.dataframe(st.session_state.fleet[['ID', 'Status', 'Type']], width='stretch', hide_index=True)
        
        # Update existing dashboard data dynamically (incidents can be updated similarly if needed)
        st.markdown("#### Current Incidents")
        st.dataframe(st.session_state.incidents[['ID', 'Status', 'Severity']], width='stretch', hide_index=True)
        
        # Comparison Results
        if 'after_metrics' in st.session_state.replay:
            st.markdown("### Comparison Results")
            before = st.session_state.replay['before_metrics']
            after = st.session_state.replay['after_metrics']
            
            # Display as metric cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Response Time", f"{after['avg_response_time']:.1f} min", f"{after['avg_response_time'] - before['avg_response_time']:.1f}")
            with col2:
                st.metric("Active Units", after['active_units_count'], after['active_units_count'] - before['active_units_count'])
            with col3:
                st.metric("Incident Count", after['incident_count'], after['incident_count'] - before['incident_count'])
            
            # Also show as table
            comparison_df = pd.DataFrame({
                'Metric': ['Avg Response Time (min)', 'Active Units', 'Incident Count'],
                'Before': [f"{before['avg_response_time']:.1f}", before['active_units_count'], before['incident_count']],
                'After': [f"{after['avg_response_time']:.1f}", after['active_units_count'], after['incident_count']],
                'Change': [f"{after['avg_response_time'] - before['avg_response_time']:.1f}", after['active_units_count'] - before['active_units_count'], after['incident_count'] - before['incident_count']]
            })
            st.table(comparison_df)

    st.markdown("---")
    st.caption("Last updated: " + datetime.now().strftime("%H:%M:%S"))


if __name__ == "__main__":
    run()