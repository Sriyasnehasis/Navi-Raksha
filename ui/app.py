import streamlit as st

# Simple router for dashboards in this repo. Each dashboard exposes a `run()`.
st.set_page_config(page_title="NaviRaksha Unified App", layout="wide")

st.sidebar.title("NaviRaksha — Dashboards")
page = st.sidebar.selectbox("Select Dashboard", [
    "Citizen Tracker",
    "Dispatcher Control",
    "Simulation"
])

if page == "Citizen Tracker":
    import citizen_tracker as citizen_tracker
    citizen_tracker.run()
elif page == "Dispatcher Control":
    import dispatcher_dashboard as dispatcher_dashboard
    dispatcher_dashboard.run()
elif page == "Simulation":
    import simulation as simulation
    simulation.run()
