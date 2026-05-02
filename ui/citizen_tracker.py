import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import numpy as np
from datetime import datetime

# Get backend URL from secrets (production) or use localhost (development)
BACKEND_URL = st.secrets.get("backend", {}).get("API_URL", "http://localhost:8000")


def run():
    # ------------------------------------------------------------------ #
    # Fetch live data from backend API
    # ------------------------------------------------------------------ #
    @st.cache_data(ttl=5)
    def fetch_backend_data():
        try:
            amb_resp = requests.get(
                f"{BACKEND_URL}/ambulances/active", timeout=2
            ).json()
            inc_resp = requests.get(f"{BACKEND_URL}/incidents/active", timeout=2).json()
            hosp_resp = requests.get(f"{BACKEND_URL}/hospitals", timeout=2).json()

            ambulances = (
                amb_resp.get("ambulances", [])
                if isinstance(amb_resp, dict)
                else amb_resp
            )
            incidents = (
                inc_resp.get("incidents", [])
                if isinstance(inc_resp, dict)
                else inc_resp
            )
            hospitals = (
                hosp_resp.get("hospitals", [])
                if isinstance(hosp_resp, dict)
                else hosp_resp
            )

            return ambulances, incidents, hospitals, True
        except Exception:
            return (
                [
                    {
                        "id": "ALS-001",
                        "latitude": 19.0760,
                        "longitude": 72.8777,
                        "status": "available",
                        "type": "ALS",
                        "driver_name": "Raj Kumar",
                    },
                    {
                        "id": "ALS-002",
                        "latitude": 19.0860,
                        "longitude": 72.8877,
                        "status": "responding",
                        "type": "ALS",
                        "driver_name": "Priya Singh",
                    },
                    {
                        "id": "BLS-001",
                        "latitude": 19.0920,
                        "longitude": 72.8900,
                        "status": "available",
                        "type": "BLS",
                        "driver_name": "Amit Patel",
                    },
                    {
                        "id": "BLS-002",
                        "latitude": 19.0820,
                        "longitude": 72.8650,
                        "status": "on_scene",
                        "type": "BLS",
                        "driver_name": "Suresh Nair",
                    },
                    {
                        "id": "MINI-001",
                        "latitude": 19.0950,
                        "longitude": 72.8750,
                        "status": "available",
                        "type": "BIKE",
                        "driver_name": "Deepa Gupta",
                    },
                ],
                [
                    {
                        "id": "INC-001",
                        "latitude": 19.0800,
                        "longitude": 72.8800,
                        "severity": "critical",
                        "incident_type": "Cardiac",
                        "patient_name": "Ramesh S.",
                    },
                    {
                        "id": "INC-002",
                        "latitude": 19.0900,
                        "longitude": 72.8900,
                        "severity": "severe",
                        "incident_type": "Trauma",
                        "patient_name": "Priya V.",
                    },
                ],
                [
                    {
                        "id": "HOSP-001",
                        "name": "Fortis Hospital",
                        "latitude": 19.0760,
                        "longitude": 72.8777,
                        "available_beds": 45,
                        "total_beds": 150,
                    },
                    {
                        "id": "HOSP-002",
                        "name": "Apollo Clinic",
                        "latitude": 19.0860,
                        "longitude": 72.8877,
                        "available_beds": 78,
                        "total_beds": 200,
                    },
                    {
                        "id": "HOSP-003",
                        "name": "Sai Nursing Home",
                        "latitude": 19.0900,
                        "longitude": 72.8950,
                        "available_beds": 22,
                        "total_beds": 80,
                    },
                ],
                False,
            )

    ambulances, incidents, hospitals, is_live = fetch_backend_data()

    # User location
    if "user_lat" not in st.session_state:
        st.session_state.user_lat = 19.0760
    if "user_lon" not in st.session_state:
        st.session_state.user_lon = 72.8777

    # ------------------------------------------------------------------ #
    # SIDEBAR
    # ------------------------------------------------------------------ #
    with st.sidebar:
        # Live badge
        if is_live:
            st.markdown(
                '<span class="live-badge live-green">● LIVE</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="live-badge live-yellow">● DEMO</span>',
                unsafe_allow_html=True,
            )

        st.markdown("### 📍 Your Location")
        st.session_state.user_lat = st.number_input(
            "Latitude",
            value=st.session_state.user_lat,
            step=0.001,
            format="%.4f",
            key="ct_lat",
        )
        st.session_state.user_lon = st.number_input(
            "Longitude",
            value=st.session_state.user_lon,
            step=0.001,
            format="%.4f",
            key="ct_lon",
        )

    user_lat = st.session_state.user_lat
    user_lon = st.session_state.user_lon

    # Calculate distances
    def calc_dist(lat1, lon1, lat2, lon2):
        return np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111

    # Filter out non-dict ambulances and calculate distances
    valid_ambulances = [a for a in ambulances if isinstance(a, dict)]
    for amb in valid_ambulances:
        amb["distance_km"] = calc_dist(
            user_lat,
            user_lon,
            amb.get("latitude", user_lat),
            amb.get("longitude", user_lon),
        )

    valid_hospitals = [h for h in hospitals if isinstance(h, dict)]
    for hosp in valid_hospitals:
        hosp["distance_km"] = calc_dist(
            user_lat,
            user_lon,
            hosp.get("latitude", user_lat),
            hosp.get("longitude", user_lon),
        )

    ambulances_sorted = sorted(
        valid_ambulances, key=lambda x: x.get("distance_km", 999)
    )
    hospitals_sorted = sorted(valid_hospitals, key=lambda x: x.get("distance_km", 999))
    nearest_amb = ambulances_sorted[0] if ambulances_sorted else None
    nearest_hosp = hospitals_sorted[0] if hospitals_sorted else None

    # ------------------------------------------------------------------ #
    # Sidebar: Nearest Resources
    # ------------------------------------------------------------------ #
    with st.sidebar:
        st.markdown("---")

        # Nearest Ambulance
        if nearest_amb:
            amb_dist = nearest_amb["distance_km"]
            amb_type = nearest_amb.get("type", "BLS")
            eta_min = max(1, int(amb_dist * 3))
            eta_pct = min(100, max(5, int((1 - amb_dist / 5) * 100)))

            type_colors = {
                "ALS": "#e74c3c",
                "BLS": "#f39c12",
                "BIKE": "#2ecc71",
                "MINI": "#2ecc71",
            }
            tc = type_colors.get(amb_type, "#3498db")

            st.markdown(
                f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size: 1.5em;">🚑</span>
                    <span style="background:{tc}22; color:{tc}; padding:3px 10px; border-radius:12px; font-size:0.8em; font-weight:600;">{amb_type}</span>
                </div>
                <h4 style="margin: 8px 0 4px 0;">Nearest Ambulance</h4>
                <p style="font-size:1.4em; font-weight:700; margin:0; color:#00d4ff !important;">{nearest_amb["id"]}</p>
                <p style="color:#888 !important; margin: 2px 0;">👤 {nearest_amb.get("driver_name", "N/A")}</p>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <div><span style="color:#888;">Distance</span><br><b>{amb_dist:.2f} km</b></div>
                    <div><span style="color:#888;">ETA</span><br><b style="color:#00d4ff !important;">~{eta_min} min</b></div>
                </div>
                <div class="eta-bar-container">
                    <div class="eta-bar-fill" style="width: {eta_pct}%;"></div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📞 Call", key="call_amb_s", use_container_width=True):
                    st.success(f"Calling {nearest_amb['id']}!")
            with col2:
                if st.button("📍 Track", key="track_amb_s", use_container_width=True):
                    st.info(f"Tracking {nearest_amb['id']}...")

        # Nearest Hospital
        if nearest_hosp:
            hosp_dist = nearest_hosp["distance_km"]
            beds = nearest_hosp.get("available_beds", 0)
            total = nearest_hosp.get("total_beds", 1)
            bed_pct = int((beds / max(total, 1)) * 100)
            bed_color = (
                "#2ecc71" if beds > 10 else ("#f39c12" if beds > 5 else "#e74c3c")
            )

            st.markdown(
                f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size: 1.5em;">🏥</span>
                    <span style="background:{bed_color}22; color:{bed_color}; padding:3px 10px; border-radius:12px; font-size:0.8em; font-weight:600;">{beds} beds</span>
                </div>
                <h4 style="margin: 8px 0 4px 0;">Nearest Hospital</h4>
                <p style="font-size:1.1em; font-weight:700; margin:0;">{nearest_hosp.get("name", "Hospital")}</p>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <div><span style="color:#888;">Distance</span><br><b>{hosp_dist:.2f} km</b></div>
                    <div><span style="color:#888;">Beds</span><br><b style="color:{bed_color} !important;">{beds}/{total}</b></div>
                </div>
                <div class="eta-bar-container">
                    <div style="height:100%; border-radius:10px; background:{bed_color}; width:{bed_pct}%;"></div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Emergency Request
        st.markdown("### 🚨 Report Emergency")
        incident_type = st.selectbox(
            "Type",
            ["Cardiac", "Trauma", "Respiratory", "Burn", "Other"],
            key="ct_inc_type",
        )
        severity = st.select_slider(
            "Severity",
            ["Minor", "Moderate", "Severe", "Critical"],
            value="Severe",
            key="ct_sev",
        )

        if st.button(
            "🚑 REQUEST AMBULANCE",
            use_container_width=True,
            type="primary",
            key="ct_req",
        ):
            try:
                payload = {
                    "patient_lat": user_lat,
                    "patient_lon": user_lon,
                    "incident_type": incident_type,
                    "severity": severity.upper(),
                    "distance": nearest_amb["distance_km"] if nearest_amb else 5.0,
                    "hour": datetime.now().hour,
                    "is_monsoon": False,
                }
                resp = requests.post(f"{BACKEND_URL}/dispatch", json=payload, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.active_dispatch = data
                    st.balloons()
                    st.success("✅ Emergency request processed!")
                    st.info(
                        f"🚑 {data.get('ambulance_id', 'N/A')} dispatched! ({data.get('ambulance_type', 'BLS')})"
                    )
                    st.info(f"⏱️ ETA: {data.get('eta_minutes', '?')} min")
                else:
                    st.error("Backend error processing dispatch.")
            except Exception as e:
                st.error(f"Cannot connect to backend: {e}")

            # Keep fallback if needed
            if "active_dispatch" not in st.session_state:
                st.balloons()
                st.success("✅ Emergency request sent (Mock mode)!")
                st.info(f"🚑 {nearest_amb['id'] if nearest_amb else 'N/A'} dispatched!")
                st.info(
                    f"⏱️ ETA: ~{max(1, int(nearest_amb['distance_km'] * 3)) if nearest_amb else '?'} min"
                )

        # Legend
        st.markdown("---")
        st.markdown(
            """
        <div style="font-size:0.8em; color:#666 !important;">
        <b>Map Legend</b><br>
        🔴 ALS &nbsp; 🟠 BLS &nbsp; 🟡 Mini/Bike<br>
        🟢 Hospital (>10 beds) &nbsp; 🔵 (5-10) &nbsp; 🔴 (<5)<br>
        🔵 Your Location
        </div>
        """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------ #
    # MAIN CONTENT
    # ------------------------------------------------------------------ #

    # Header
    st.markdown(
        """
    <div style="margin-bottom: 20px;">
        <h1 class="brand-header">🚑 NaviRaksha</h1>
        <p class="brand-sub">Real-time Emergency Response Tracking — Navi Mumbai</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # KPI Row
    k1, k2, k3, k4 = st.columns(4)
    avail_count = sum(
        1
        for a in valid_ambulances
        if isinstance(a, dict) and "available" in a.get("status", "").lower()
    )
    with k1:
        st.markdown(
            f'<div class="kpi-card"><h4>AMBULANCES</h4><h2>{len(valid_ambulances)}</h2></div>',
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f'<div class="kpi-card kpi-green"><h4>AVAILABLE</h4><h2>{avail_count}</h2></div>',
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            f'<div class="kpi-card kpi-red"><h4>INCIDENTS</h4><h2>{len(incidents)}</h2></div>',
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            f'<div class="kpi-card kpi-orange"><h4>HOSPITALS</h4><h2>{len(valid_hospitals)}</h2></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Map + Sidebar columns
    map_col, info_col = st.columns([2.5, 1], gap="large")

    with map_col:
        st.markdown("### 🗺️ Live Tracking Map")

        # Dark-themed map
        m = folium.Map(location=[user_lat, user_lon], zoom_start=13, prefer_canvas=True)

        # User location — pulsing blue circle
        folium.CircleMarker(
            [user_lat, user_lon],
            radius=10,
            color="#3498db",
            fill=True,
            fillColor="#3498db",
            fillOpacity=0.8,
            weight=3,
            tooltip="📍 Your Location",
        ).add_to(m)
        # Outer pulse ring
        folium.CircleMarker(
            [user_lat, user_lon],
            radius=25,
            color="#3498db",
            fill=True,
            fillColor="#3498db",
            fillOpacity=0.15,
            weight=1,
        ).add_to(m)

        # Ambulances
        amb_colors = {"ALS": "red", "BLS": "orange", "BIKE": "green", "MINI": "green"}
        for amb in valid_ambulances:
            color = amb_colors.get(amb.get("type", "BLS"), "blue")
            status = amb.get("status", "unknown").replace("_", " ").title()
            folium.Marker(
                [amb.get("latitude", user_lat), amb.get("longitude", user_lon)],
                popup=f"<b>🚑 {amb.get('id', '?')}</b><br>Type: {amb.get('type', '?')}<br>Status: {status}<br>Driver: {amb.get('driver_name', 'N/A')}",
                icon=folium.Icon(
                    color=color, icon="ambulance", prefix="fa", icon_color="white"
                ),
                tooltip=f"{amb.get('type', '?')} — {amb.get('id', '?')}",
            ).add_to(m)

        # Incidents
        sev_colors = {
            "critical": "red",
            "severe": "orange",
            "moderate": "yellow",
            "minor": "green",
        }
        sev_radius = {"critical": 14, "severe": 11, "moderate": 8, "minor": 6}
        for inc in incidents:
            if not isinstance(inc, dict):
                continue

            # Safe coordinate retrieval to avoid KeyError
            lat = inc.get("latitude")
            lon = inc.get("longitude")

            if lat is None or lon is None:
                continue

            sev = inc.get("severity", "moderate").lower()
            folium.CircleMarker(
                [lat, lon],
                radius=sev_radius.get(sev, 8),
                color=sev_colors.get(sev, "yellow"),
                fill=True,
                fillColor=sev_colors.get(sev, "yellow"),
                fillOpacity=0.7,
                weight=2,
                tooltip=f"⚠️ {sev.upper()} — {inc.get('incident_type', '?')}",
                popup=f"<b>{inc.get('id', '?')}</b><br>{inc.get('incident_type', '?')}<br>Patient: {inc.get('patient_name', 'N/A')}",
            ).add_to(m)

        # Hospitals
        for hosp in valid_hospitals:
            beds = hosp.get("available_beds", 0)
            h_color = "green" if beds > 10 else ("blue" if beds > 5 else "red")
            folium.Marker(
                [hosp.get("latitude", user_lat), hosp.get("longitude", user_lon)],
                popup=f"<b>🏥 {hosp.get('name', 'Hospital')}</b><br>Beds: {beds}/{hosp.get('total_beds', 0)}",
                icon=folium.Icon(
                    color=h_color, icon="plus-square", prefix="fa", icon_color="white"
                ),
                tooltip=f"🏥 {hosp.get('name', 'Hospital')} ({beds} beds)",
            ).add_to(m)

        # Draw route from active dispatch if available
        if (
            "active_dispatch" in st.session_state
            and "route_coords" in st.session_state.active_dispatch
        ):
            route_pts = st.session_state.active_dispatch["route_coords"]
            if len(route_pts) > 1:
                folium.PolyLine(
                    route_pts,
                    color="#00ff00",
                    weight=4,
                    opacity=0.8,
                    tooltip="A* Optimized Route",
                ).add_to(m)
        elif nearest_amb:
            # Fallback direct line
            folium.PolyLine(
                [
                    [user_lat, user_lon],
                    [nearest_amb["latitude"], nearest_amb["longitude"]],
                ],
                color="#00d4ff",
                weight=2,
                opacity=0.6,
                dash_array="10",
                tooltip="Direct Distance",
            ).add_to(m)

        st_folium(
            m, width=None, height=550, use_container_width=True, returned_objects=[]
        )

    with info_col:
        st.markdown("### 🚑 Fleet Status")

        if "active_dispatch" in st.session_state:
            active_dispatch = st.session_state.active_dispatch
            route_summary = active_dispatch.get("route_summary", {})
            st.markdown("### 🧭 Active Dispatch Route")
            st.markdown(
                f"""
            <div class="glass-card" style="padding:10px 14px; border-left: 3px solid #00d4ff;">
                <b>Mode:</b> {route_summary.get("routing_mode", "fallback").upper()}<br>
                <b>Ambulance → Patient Nodes:</b> {route_summary.get("ambulance_to_patient_nodes", 0)}<br>
                <b>Patient → Hospital Nodes:</b> {route_summary.get("patient_to_hospital_nodes", 0)}
            </div>
            """,
                unsafe_allow_html=True,
            )

            rankings = active_dispatch.get("hospital_rankings", [])
            if rankings:
                st.markdown("### 🏥 Ranked Hospitals")
                for rank, item in enumerate(rankings, 1):
                    hosp = item.get("hospital", {})
                    st.markdown(
                        f"""
                    <div class="glass-card" style="padding:8px 12px;">
                        <b>#{rank} {hosp.get("name", "Hospital")}</b><br>
                        <span style="color:#888; font-size:0.85em;">ETA: {item.get("eta_to_hospital_min", "N/A")} min · Score: {item.get("score", "N/A")}</span>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        for idx, amb in enumerate(ambulances_sorted[:5]):
            amb_type = amb.get("type", "BLS")
            status_raw = amb.get("status", "unknown").lower()
            dist = amb["distance_km"]
            eta = max(1, int(dist * 3))

            type_icon = {"ALS": "🔴", "BLS": "🟠", "BIKE": "🟢", "MINI": "🟡"}.get(
                amb_type, "⚪"
            )

            if "available" in status_raw:
                pill = '<span class="status-pill pill-available">Available</span>'
            elif "route" in status_raw or "responding" in status_raw:
                pill = '<span class="status-pill pill-enroute">En Route</span>'
            else:
                pill = '<span class="status-pill pill-onscene">On Scene</span>'

            st.markdown(
                f"""
            <div class="glass-card" style="padding:12px 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-size:1.1em; font-weight:700;">{type_icon} {amb["id"]}</span>
                        <br><span style="color:#888; font-size:0.85em;">👤 {amb.get("driver_name", "N/A")}</span>
                    </div>
                    <div style="text-align:right;">
                        {pill}<br>
                        <span style="color:#00d4ff !important; font-weight:700; font-size:0.9em;">{dist:.1f}km · ~{eta}m</span>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Active incidents
        if incidents:
            st.markdown("### ⚠️ Active Incidents")
            for inc in incidents:
                if not isinstance(inc, dict):
                    continue
                sev = inc.get("severity", "moderate").lower()
                sev_class = f"severity-{sev}"
                sev_icon = {
                    "critical": "🔴",
                    "severe": "🟠",
                    "moderate": "🟡",
                    "minor": "🟢",
                }.get(sev, "⚪")

                st.markdown(
                    f"""
                <div class="glass-card" style="padding:10px 14px; border-left: 3px solid {"#e74c3c" if sev == "critical" else "#f39c12" if sev == "severe" else "#f1c40f"};">
                    <span class="{sev_class}">{sev_icon} {sev.upper()}</span> — {inc.get("incident_type", "?")}
                    <br><span style="color:#888; font-size:0.85em;">{inc.get("id", "?")} · 👤 {inc.get("patient_name", "N/A")}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------------ #
    # Bottom: Hospitals
    # ------------------------------------------------------------------ #
    st.markdown("---")
    st.markdown("### 🏥 Nearby Hospitals")

    if valid_hospitals:
        cols = st.columns(min(4, len(valid_hospitals)))
        for idx, hosp in enumerate(valid_hospitals[:4]):
            with cols[idx % 4]:
                beds = hosp.get("available_beds", 0)
                total = hosp.get("total_beds", 1)
                dist = hosp.get("distance_km", 0)
                bed_color = (
                    "#2ecc71" if beds > 10 else ("#f39c12" if beds > 5 else "#e74c3c")
                )

                st.markdown(
                    f"""
                <div class="glass-card" style="text-align:center;">
                    <span style="font-size:1.5em;">🏥</span>
                    <h4 style="margin:8px 0 4px 0; font-size:0.95em;">{hosp.get("name", "Hospital")}</h4>
                    <p style="color:#00d4ff !important; font-size:1.3em; font-weight:700; margin:4px 0;">{dist:.1f} km</p>
                    <p style="color:{bed_color} !important; font-weight:600; margin:2px 0;">🛏️ {beds}/{total} beds</p>
                    <p style="color:#888 !important; font-size:0.8em;">⏱️ ~{max(1, int(dist * 3))} min</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Timestamp
    st.markdown(
        f'<p class="footer-text">Last updated: {datetime.now().strftime("%H:%M:%S")} IST</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    run()
