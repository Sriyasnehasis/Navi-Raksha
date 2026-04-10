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
            'Time': ['12:34 PM', '12:45 PM', '12:52 PM']
        })

    # Header
    st.markdown('<h1 class="main-header">🚑 NaviRaksha Dispatcher Control Room</h1>', unsafe_allow_html=True)
    st.markdown('Fleet Management & Incident Coordination', unsafe_allow_html=True)

    # KPIs at top
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("""
        <div class="metric-highlight">
            <h3>Active Units</h3>
            <h2>5</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown("""
        <div class="metric-highlight">
            <h3>Avg Response</h3>
            <h2>8.2 min</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown("""
        <div class="metric-highlight">
            <h3>Today's Incidents</h3>
            <h2>12</h2>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown("""
        <div class="metric-highlight">
            <h3>Pending Calls</h3>
            <h2>2</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚗 Fleet Status", "🚨 Incidents Queue", "📊 Analytics", "⚙️ Settings"])

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

    st.markdown("---")
    st.caption("Last updated: " + datetime.now().strftime("%H:%M:%S"))


if __name__ == "__main__":
    run()