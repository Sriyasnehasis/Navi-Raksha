import streamlit as st

# Page configuration — must be first Streamlit call
st.set_page_config(
    page_title="NaviRaksha — Emergency Medical Services",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global premium CSS applied to ALL pages
st.markdown("""
<style>
    /* ===== DARK PREMIUM THEME ===== */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    [data-testid="stSidebar"] .stMarkdown { color: #e0e0e0; }
    
    /* Hide default header */
    header[data-testid="stHeader"] { background: transparent; }
    
    /* Global text */
    .stApp, .stMarkdown, p, span, label { color: #e0e0e0 !important; }
    h1, h2, h3, h4 { color: #ffffff !important; }
    
    /* Metric cards */
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.9em; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 12px;
        font-weight: 600; padding: 0.5rem 1.2rem;
        transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.5);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%) !important;
        box-shadow: 0 4px 15px rgba(231,76,60,0.4);
    }
    
    /* Containers / Cards */
    [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px; backdrop-filter: blur(10px);
    }
    
    /* DataFrames */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05); border-radius: 10px;
        color: #aaa; padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Select boxes & inputs */
    .stSelectbox > div > div, .stNumberInput > div > div > input,
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e0e0e0 !important; border-radius: 10px;
    }
    
    /* Custom classes */
    .brand-header {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 50%, #e74c3c 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.8em; font-weight: 800; letter-spacing: -1px;
        margin-bottom: 0;
    }
    .brand-sub { color: #888 !important; font-size: 1.05em; margin-top: -10px; }
    
    .glass-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 20px; margin: 8px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .glass-card:hover { 
        background: rgba(255,255,255,0.07);
        border-color: rgba(102,126,234,0.3);
        transform: translateY(-2px);
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px; padding: 20px 24px; text-align: center;
        box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    }
    .kpi-card h4 { color: rgba(255,255,255,0.7) !important; font-size: 0.85em; margin: 0; font-weight: 500; }
    .kpi-card h2 { color: #fff !important; font-size: 2em; margin: 5px 0 0 0; font-weight: 700; }
    
    .kpi-red {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 8px 25px rgba(231,76,60,0.3);
    }
    .kpi-green {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        box-shadow: 0 8px 25px rgba(39,174,96,0.3);
    }
    .kpi-orange {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        box-shadow: 0 8px 25px rgba(243,156,18,0.3);
    }
    
    .severity-critical { color: #e74c3c !important; font-weight: 700; }
    .severity-severe { color: #f39c12 !important; font-weight: 700; }
    .severity-moderate { color: #f1c40f !important; font-weight: 600; }
    .severity-minor { color: #2ecc71 !important; font-weight: 600; }
    
    .status-pill {
        display: inline-block; padding: 4px 14px;
        border-radius: 20px; font-size: 0.8em; font-weight: 600;
    }
    .pill-available { background: rgba(39,174,96,0.15); color: #2ecc71; }
    .pill-enroute { background: rgba(243,156,18,0.15); color: #f39c12; }
    .pill-onscene { background: rgba(52,152,219,0.15); color: #3498db; }
    
    .live-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.75em; font-weight: 700; letter-spacing: 1px;
        animation: pulse 2s infinite;
    }
    .live-green { background: rgba(39,174,96,0.2); color: #2ecc71; }
    .live-yellow { background: rgba(243,156,18,0.2); color: #f39c12; }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Progress bar */
    .eta-bar-container {
        background: rgba(255,255,255,0.05);
        border-radius: 10px; height: 8px; overflow: hidden; margin-top: 6px;
    }
    .eta-bar-fill {
        height: 100%; border-radius: 10px;
        background: linear-gradient(90deg, #2ecc71, #f39c12, #e74c3c);
        transition: width 1s ease;
    }
    
    /* Metric highlights for Dispatcher Dashboard */
    .metric-highlight {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 15px; text-align: center;
        transition: all 0.3s ease;
    }
    .metric-highlight:hover {
        background: rgba(255,255,255,0.08);
        border-color: rgba(102,126,234,0.4);
        transform: translateY(-2px);
    }
    .metric-highlight h3 { color: #888 !important; font-size: 0.85em; margin: 0; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
    .metric-highlight h2 { color: #00d4ff !important; font-size: 1.8em; margin: 5px 0 0 0; font-weight: 700; }
    
    /* Footer */
    .footer-text { color: #555 !important; font-size: 0.8em; text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("""
<div style="text-align:center; padding: 10px 0 20px 0;">
    <span style="font-size: 2.5em;">🚑</span>
    <h2 style="margin: 5px 0 0 0; font-weight: 700;">NaviRaksha</h2>
    <p style="color: #666; font-size: 0.85em; margin-top: -5px;">Emergency Medical Services</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

page = st.sidebar.selectbox("📋 Dashboard", [
    "🗺️ Citizen Tracker",
    "🎯 Dispatcher Control",
    "🧪 Simulation"
], label_visibility="collapsed")

st.sidebar.markdown("---")

if page == "🗺️ Citizen Tracker":
    import citizen_tracker as citizen_tracker
    citizen_tracker.run()
elif page == "🎯 Dispatcher Control":
    import dispatcher_dashboard as dispatcher_dashboard
    dispatcher_dashboard.run()
elif page == "🧪 Simulation":
    import simulation as simulation
    simulation.run()


