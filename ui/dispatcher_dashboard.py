import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def run():
    # Page configuration handled by the top-level router

    # Custom CSS
    st.markdown("""
    <style>
        .main-header { color: #2c3e50; font-size: 2.5em; font-weight: bold; margin-bottom: 1em; }
        .status-badge { display: inline-block; padding: 8px 12px; border-radius: 20px; font-weight: bold; }
        .status-available { background: #d5f4e6; color: #27ae60; }
        .status-enroute { background: #fef5e7; color: #f39c12; }
        .status-assigned { background: #ebf5fb; color: #3498db; }
        .incident-card { background: #fff; border-left: 4px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .metric-highlight { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'fleet' not in st.session_state:
        st.session_state.fleet = pd.DataFrame({
            'ID': ['ALS-001', 'ALS-002', 'BLS-001', 'BLS-002', 'MINI-001'],
            'Location': ['Vashi', 'Belapur', 'Nerul', 'Kharghar', 'Panvel'],
            'Status': ['Available', 'En Route', 'Available', 'Incident Scene', 'Available'],
            'Type': ['ALS', 'ALS', 'BLS', 'BLS', 'Mini'],
            'Driver': ['Raj Kumar', 'Priya Singh', 'Amit Patel', 'Suresh Nair', 'Deepa Gupta'],
            'Response Time': ['--', '12 min', '--', 'On Scene', '--']
        })
        # assign stable lat/lon once so the map doesn't jitter on every rerun
        base_lat, base_lon = 19.0760, 72.8777
        lats = [base_lat + random.uniform(-0.02, 0.02) for _ in range(len(st.session_state.fleet))]
        lons = [base_lon + random.uniform(-0.02, 0.02) for _ in range(len(st.session_state.fleet))]
        st.session_state.fleet['lat'] = lats
        st.session_state.fleet['lon'] = lons

    if 'incidents' not in st.session_state:
        st.session_state.incidents = pd.DataFrame({
            'ID': ['INC-2401', 'INC-2402', 'INC-2403'],
            'Location': ['Belapur', 'Kharghar', 'Panvel'],
            'Type': ['Cardiac', 'Trauma', 'Respiratory'],
            'Severity': ['Critical', 'High', 'Medium'],
            'Status': ['Ambulance Assigned', 'Waiting', 'En Route'],
            'Time': ['12:34 PM', '12:45 PM', '12:52 PM'],
            'Response Time (min)': [8, None, 12]  # Add response times for calculation
        })

    # Add hospital data for availability
    if 'hospitals' not in st.session_state:
        st.session_state.hospitals = pd.DataFrame({
            'Name': ['Fortis Hospital', 'Apollo Clinic', 'Sai Nursing Home'],
            'Available Beds': [45, 78, 22],
            'Total Beds': [150, 200, 80]
        })

    # Initialize replay state
    if 'replay' not in st.session_state:
        st.session_state.replay = {
            'simulation_running': False,  # Tracks if simulation is running
            'current_step': 0,  # Current time step in simulation
            'max_steps': 10,
            'initial_fleet': st.session_state.fleet.copy(),
            'initial_incidents': st.session_state.incidents.copy(),
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

    # Helper functions for KPI calculations
    def calculate_avg_response_time(incidents_df):
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

    # Header
    st.markdown('<h1 class="main-header">🚑 NaviRaksha Dispatcher Control Room</h1>', unsafe_allow_html=True)
    st.markdown('Fleet Management & Incident Coordination', unsafe_allow_html=True)

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

    st.markdown("---")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚗 Fleet Status", "🚨 Incidents Queue", "📊 Analytics", "⚙️ Settings", "🎬 Simulation Replay"])

    with tab1:
        st.markdown("### Fleet Overview")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Map
            m = folium.Map(location=[19.0760, 72.8777], zoom_start=12)
            
            # Add ambulances to map
            colors = {'ALS': 'red', 'BLS': 'blue', 'Mini': 'orange'}
            for idx, row in st.session_state.fleet.iterrows():
                lat = row.get('lat', 19.0760)
                lon = row.get('lon', 72.8777)
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>{row['ID']}</b><br>{row['Type']}<br>Driver: {row['Driver']}",
                    icon=folium.Icon(color=colors.get(row['Type'], 'gray'), icon='ambulance', prefix='fa')
                ).add_to(m)
            
            st_folium(m, width=None, height=400)
        
        with col2:
            st.markdown("### Quick Actions")
            if st.button("🔄 Refresh Fleet"):
                st.rerun()
            if st.button("📞 Dispatch New"):
                st.info("Opening dispatch wizard...")
            if st.button("⚠️ Alert All Units"):
                st.warning("Alert broadcast enabled")
        
        st.markdown("### Fleet Details")
        st.dataframe(st.session_state.fleet, width='stretch', hide_index=True)

    with tab2:
        st.markdown("### Active Incidents")
        
        for idx, row in st.session_state.incidents.iterrows():
            severity_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}
            st.markdown(f"""
            <div class="incident-card">
                <b>{severity_color.get(row['Severity'])} {row['ID']}</b> - {row['Type']} | <span class="status-badge status-{row['Status'].lower().replace(' ', '-')}">{row['Status']}</span>
                <br>📍 {row['Location']} | ⏰ {row['Time']}
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button(f"📍 Assign - {row['ID']}", key=f"assign_{idx}"):
                    st.success(f"Assigned ambulance to {row['ID']}")
            with col_b:
                if st.button(f"📞 Call - {row['ID']}", key=f"call_{idx}"):
                    st.info(f"Calling incident commander for {row['ID']}")
            with col_c:
                if st.button(f"✓ Close - {row['ID']}", key=f"close_{idx}"):
                    st.success(f"Incident {row['ID']} closed")

    with tab3:
        st.markdown("### Performance Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Average Response Time", "8.2 min", "-1.2 min")
            st.metric("Call Success Rate", "94.5%", "+2.1%")
        
        with col2:
            st.metric("Total Calls Today", "12", "+3")
            st.metric("Critical Incidents", "2", "-1")
        
        st.markdown("### Response Time Trend")
        chart_data = pd.DataFrame({
            'Time': ['12:00', '12:15', '12:30', '12:45', '13:00'],
            'Avg Response (min)': [9.2, 8.8, 8.5, 8.2, 7.9]
        })
        st.line_chart(chart_data.set_index('Time'))

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

    with tab4:
        st.markdown("### System Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("🔊 Audio Alerts", value=True)
            st.checkbox("📧 Email Notifications", value=True)
            alert_level = st.select_slider("Alert Level", ["Low", "Medium", "High"], value="High")
        
        with col2:
            refresh_rate = st.slider("Refresh Rate (seconds)", 5, 60, 15)
            max_incidents = st.slider("Max Display Incidents", 5, 20, 10)
            st.info(f"Settings saved! Refresh rate: {refresh_rate}s")

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