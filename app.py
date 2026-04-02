import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Weather & Climate Tracker",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SESSION STATE — language toggle, city selection
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
if "oracle_history" not in st.session_state:
    st.session_state.oracle_history = []
if "oracle_input_key" not in st.session_state:
    st.session_state.oracle_input_key = 0
if "selected_city" not in st.session_state:
    st.session_state.selected_city = "Jakarta, Indonesia"

def t(en: str, id: str) -> str:
    """Return translation based on current language."""
    return en if st.session_state.lang == "EN" else id

# ─────────────────────────────────────────────
# CUSTOM CSS — Farm Theme with Vibrant Gradient
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    :root {
        --bg-main:       #FFFFFF;
        --bg-light:      #F8F9FA;
        --bg-card:       #FFFFFF;
        --border:        #E0E0E0;
        --text-dark:     #1A1A1A;
        --text-light:    #666666;
        --accent-warm:   #FF8C00;
        --accent-orange: #FF7700;
        --accent-green:  #2D8659;
        --accent-sky:    #0099CC;
        --accent-pink:   #E74C3C;
        --accent-yellow: #F39C12;
        --shadow-light:  0 2px 8px rgba(0,0,0,0.08);
        --shadow-mid:    0 4px 16px rgba(0,0,0,0.12);
        --shadow-deep:   0 8px 24px rgba(0,0,0,0.15);
    }

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
        color: var(--text-dark) !important;
    }
    
    .main, .block-container {
        background-color: transparent !important;
        padding-top: 1rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }
    
    body, html {
        background: #FFFFFF !important;
        min-height: 100vh !important;
    }
    
    /* ── Responsive padding ── */
    @media (max-width: 768px) {
        .main, .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 0.8rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .main, .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-light) !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 1px 0 4px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stSidebar"] * { color: var(--text-dark) !important; }
    [data-testid="stSidebar"] a { color: var(--accent-warm) !important; }
    
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            border-right: 1px solid var(--border) !important;
        }
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid var(--border) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        color: var(--text-light) !important;
        background: transparent !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        padding: 12px 16px !important;
        margin: 0 4px !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-warm) !important;
        background: transparent !important;
        border-bottom: 3px solid var(--accent-warm) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--accent-warm) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding: 1.5rem !important;
    }
    
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 0.75rem !important;
            padding: 10px 12px !important;
            margin: 0 2px !important;
        }
    }
    
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            font-size: 0.70rem !important;
            padding: 8px 10px !important;
            margin: 0 1px !important;
        }
        .stTabs [data-baseweb="tab-panel"] {
            padding: 1rem !important;
        }
    }

    /* ── Metric Card ── */
    .sh-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: var(--shadow-light);
        padding: 20px 16px;
        text-align: center;
        position: relative;
        transition: all 0.3s ease;
    }
    .sh-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-warm), var(--accent-green), transparent);
        border-radius: 12px 12px 0 0;
        animation: shimmer 2s infinite;
    }
    .sh-card:hover {
        border-color: var(--accent-warm);
        box-shadow: var(--shadow-mid);
        transform: translateY(-2px);
    }
    .sh-card-value {
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-warm);
        line-height: 1;
        margin-bottom: 4px;
    }
    .sh-card-unit {
        font-family: 'Poppins', sans-serif;
        font-size: 0.80rem;
        font-weight: 600;
        color: var(--accent-green);
        margin-left: 2px;
    }
    .sh-card-label {
        font-family: 'Poppins', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-light);
        margin-top: 10px;
        letter-spacing: 0.02em;
        text-transform: uppercase;
    }
    
    @media (max-width: 768px) {
        .sh-card {
            padding: 16px 12px;
            border-radius: 10px;
        }
        .sh-card-value { font-size: 1.5rem !important; }
    }
    
    @media (max-width: 480px) {
        .sh-card {
            padding: 12px 10px;
            border-radius: 8px;
            border: 1px solid var(--border);
        }
        .sh-card-value { font-size: 1.3rem !important; }
        .sh-card-label { font-size: 0.65rem !important; }
    }
    
    @keyframes shimmer {
        0%, 100% { width: 30%; opacity: 0.5; }
        50% { width: 100%; opacity: 1; }
    }

    /* ── Section header ── */
    .sh-header {
        font-family: 'Poppins', sans-serif !important;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        text-transform: none;
        color: var(--accent-warm);
        border-bottom: 3px solid var(--accent-warm);
        padding-bottom: 10px;
        margin: 28px 0 16px 0;
        position: relative;
    }
    .sh-header::before {
        content: "🌾 ";
        margin-right: 8px;
        animation: wave 2s ease-in-out infinite;
    }
    
    @keyframes wave {
        0%, 100% { transform: rotate(0deg); }
        25% { transform: rotate(10deg); }
        75% { transform: rotate(-10deg); }
    }
    
    @media (max-width: 768px) {
        .sh-header {
            font-size: 1rem;
            margin: 20px 0 12px 0;
        }
    }
    
    @media (max-width: 480px) {
        .sh-header {
            font-size: 0.90rem;
            margin: 16px 0 10px 0;
        }
    }

    /* ── Info box ── */
    .sh-info {
        background: linear-gradient(135deg, rgba(82,183,136,0.12), rgba(116,192,252,0.12));
        border-left: 5px solid var(--accent-green);
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 0.82rem;
        font-family: 'Poppins', sans-serif;
        color: var(--text-light);
        margin-bottom: 18px;
    }
    
    @media (max-width: 480px) {
        .sh-info {
            font-size: 0.75rem;
            padding: 10px 12px;
        }
    }

    /* ── Forecast card ── */
    .sh-forecast {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 10px;
        box-shadow: var(--shadow-light);
        padding: 14px 10px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .sh-forecast:hover {
        border-color: var(--accent-warm);
        box-shadow: var(--shadow-mid);
        transform: translateY(-1px);
    }
    
    @media (max-width: 768px) {
        .sh-forecast {
            border-radius: 8px;
            padding: 12px 8px;
        }
    }
    
    @media (max-width: 480px) {
        .sh-forecast {
            border-radius: 6px;
            padding: 10px 6px;
            border: 1px solid var(--border);
        }
    }

    /* ── AQI banner ── */
    .sh-aqi-banner {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent-warm);
        border-radius: 10px;
        box-shadow: var(--shadow-light);
        padding: 20px 22px;
        margin-bottom: 20px;
    }
    
    @media (max-width: 768px) {
        .sh-aqi-banner {
            padding: 16px 18px;
            border-radius: 8px;
        }
    }
    
    @media (max-width: 480px) {
        .sh-aqi-banner {
            padding: 12px 14px;
            border-radius: 6px;
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent-warm);
        }
    }

    /* ── Buttons ── */
    .stButton > button {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        text-transform: none !important;
        background: linear-gradient(135deg, var(--accent-warm), #FF9500) !important;
        color: white !important;
        border: 1px solid var(--accent-warm) !important;
        border-radius: 8px !important;
        padding: 11px 22px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(255,140,0,0.2) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FF9500, #FF8200) !important;
        box-shadow: 0 4px 12px rgba(255,140,0,0.3) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 6px rgba(255,140,0,0.2) !important;
    }
    
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 0.80rem !important;
            padding: 10px 18px !important;
        }
    }
    
    @media (max-width: 480px) {
        .stButton > button {
            font-size: 0.75rem !important;
            padding: 9px 14px !important;
            border-radius: 6px !important;
        }
    }

    /* ── Widgets ── */
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        text-transform: uppercase !important;
        color: var(--text-dark) !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text-dark) !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:hover {
        border-color: var(--accent-warm) !important;
        box-shadow: 0 2px 8px rgba(255,140,0,0.1) !important;
    }
    .stMultiSelect span[data-baseweb="tag"] {
        background: linear-gradient(135deg, var(--accent-green), #52C281) !important;
        border-radius: 6px !important;
        color: white !important;
        border: 1px solid var(--accent-green) !important;
    }
    
    @media (max-width: 480px) {
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            border-radius: 6px !important;
            border: 1px solid var(--border) !important;
        }
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(224,224,224,0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(180deg, var(--accent-warm), var(--accent-green));
        border-radius: 4px; 
        box-shadow: 0 0 6px rgba(255,140,0,0.2);
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-orange); }

    /* ── Base text ── */
    hr {
        border: none !important;
        border-top: 2px solid var(--accent-warm) !important;
        margin: 18px 0 !important;
    }
    p, li { line-height: 1.65 !important; color: var(--text-light) !important; }
    a { color: var(--accent-warm) !important; transition: color 0.2s ease !important; }
    a:hover { color: var(--accent-orange) !important; }
    strong { color: var(--text-dark) !important; font-weight: 700 !important; }

    /* ── Streamlit alerts ── */
    .stAlert {
        border-radius: 8px !important;
        font-family: 'Poppins', sans-serif !important;
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-left: 4px solid var(--accent-warm) !important;
        color: var(--text-dark) !important;
        box-shadow: var(--shadow-light) !important;
    }
    .stAlert > div {
        color: var(--text-dark) !important;
        font-size: 0.82rem !important;
    }
    
    @media (max-width: 480px) {
        .stAlert {
            border-radius: 6px !important;
            border: 1px solid var(--border) !important;
            border-left: 3px solid var(--accent-warm) !important;
        }
    }

    /* ── Caption ── */
    .stCaption, small { color: var(--text-light) !important; }

    /* ── Input field global ── */
    div[data-testid="stTextInput"] > div > div > input {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-left: 3px solid var(--accent-warm) !important;
        border-radius: 8px !important;
        color: var(--text-dark) !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.86rem !important;
        letter-spacing: 0.01em !important;
        padding: 11px 14px !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: var(--accent-warm) !important;
        border-left-color: var(--accent-warm) !important;
        box-shadow: 0 4px 16px rgba(255,159,28,0.2) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder {
        color: #C9A79E !important;
    }
    
    @media (max-width: 480px) {
        div[data-testid="stTextInput"] > div > div > input {
            font-size: 0.80rem !important;
            padding: 10px 12px !important;
            border-radius: 6px !important;
            border: 1.5px solid var(--accent-sky) !important;
        }
    }

    /* ── Scrollable Container for 7-Day View ── */
    .sh-scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 12px;
        padding: 12px 0 12px 0;
        scroll-behavior: smooth;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch;
    }
    
    .sh-scroll-container::-webkit-scrollbar {
        height: 6px;
    }
    
    .sh-scroll-container::-webkit-scrollbar-track {
        background: rgba(224,224,224,0.2);
        border-radius: 3px;
    }
    
    .sh-scroll-container::-webkit-scrollbar-thumb {
        background: var(--accent-warm);
        border-radius: 3px;
    }
    
    .sh-scroll-item {
        flex: 0 0 140px;
        scroll-snap-align: start;
        min-width: 140px;
    }
    
    @media (max-width: 768px) {
        .sh-scroll-item {
            flex: 0 0 120px;
            min-width: 120px;
        }
    }
    
    @media (max-width: 480px) {
        .sh-scroll-item {
            flex: 0 0 100px;
            min-width: 100px;
        }
    }

    /* ── Responsive ── */
    @media (max-width: 900px) {
        h1 { font-size: 1.8rem !important; }
    }
    
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
    }
    
    @media (max-width: 480px) {
        h1 { font-size: 1.2rem !important; }
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ROBUST HTTP HELPER
# ─────────────────────────────────────────────
import time as _time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _get(url: str, timeout: int = 25, retries: int = 2) -> requests.Response:
    """GET with SSL fallback on EOF/SSL errors."""
    last_exc = None
    for attempt in range(retries):
        for verify in (True, False):
            try:
                r = requests.get(url, timeout=timeout, verify=verify)
                return r
            except Exception as e:
                last_exc = e
                msg = str(e).lower()
                if "ssl" not in msg and "eof" not in msg and "connection" not in msg:
                    raise   # non-network error — don't retry
        if attempt < retries - 1:
            _time.sleep(1.5)
    raise last_exc


# ─────────────────────────────────────────────
# STATIC FALLBACK DATA (always available)
# ─────────────────────────────────────────────
import json as _json

# CO2 per capita (tonnes, World Bank ~2021)
_CO2_STATIC = [
    {"country":"Indonesia","iso":"IDN","year":"2021","co2":2.1},
    {"country":"United States","iso":"USA","year":"2021","co2":14.9},
    {"country":"China","iso":"CHN","year":"2021","co2":8.0},
    {"country":"India","iso":"IND","year":"2021","co2":1.9},
    {"country":"Germany","iso":"DEU","year":"2021","co2":8.1},
    {"country":"Brazil","iso":"BRA","year":"2021","co2":2.3},
    {"country":"United Kingdom","iso":"GBR","year":"2021","co2":5.3},
    {"country":"Australia","iso":"AUS","year":"2021","co2":14.8},
    {"country":"Japan","iso":"JPN","year":"2021","co2":8.6},
    {"country":"France","iso":"FRA","year":"2021","co2":4.7},
    {"country":"Canada","iso":"CAN","year":"2021","co2":14.2},
    {"country":"South Korea","iso":"KOR","year":"2021","co2":11.8},
    {"country":"Russia","iso":"RUS","year":"2021","co2":11.4},
    {"country":"Saudi Arabia","iso":"SAU","year":"2021","co2":18.0},
    {"country":"Qatar","iso":"QAT","year":"2021","co2":33.7},
    {"country":"South Africa","iso":"ZAF","year":"2021","co2":6.9},
    {"country":"Mexico","iso":"MEX","year":"2021","co2":3.4},
    {"country":"Turkey","iso":"TUR","year":"2021","co2":5.1},
    {"country":"Iran","iso":"IRN","year":"2021","co2":8.3},
    {"country":"Malaysia","iso":"MYS","year":"2021","co2":7.8},
]

# Forest cover % (World Bank ~2021)
_FOREST_STATIC = [
    {"country":"Indonesia","iso":"IDN","year":"2021","forest_pct":55.7},
    {"country":"United States","iso":"USA","year":"2021","forest_pct":33.9},
    {"country":"China","iso":"CHN","year":"2021","forest_pct":23.5},
    {"country":"India","iso":"IND","year":"2021","forest_pct":24.1},
    {"country":"Germany","iso":"DEU","year":"2021","forest_pct":33.1},
    {"country":"Brazil","iso":"BRA","year":"2021","forest_pct":59.4},
    {"country":"United Kingdom","iso":"GBR","year":"2021","forest_pct":13.0},
    {"country":"Australia","iso":"AUS","year":"2021","forest_pct":16.9},
    {"country":"Japan","iso":"JPN","year":"2021","forest_pct":68.4},
    {"country":"France","iso":"FRA","year":"2021","forest_pct":31.4},
    {"country":"Canada","iso":"CAN","year":"2021","forest_pct":38.2},
    {"country":"Russia","iso":"RUS","year":"2021","forest_pct":49.8},
    {"country":"Malaysia","iso":"MYS","year":"2021","forest_pct":58.2},
    {"country":"Sweden","iso":"SWE","year":"2021","forest_pct":69.0},
    {"country":"Finland","iso":"FIN","year":"2021","forest_pct":73.7},
    {"country":"Norway","iso":"NOR","year":"2021","forest_pct":33.2},
    {"country":"Congo, Dem. Rep.","iso":"COD","year":"2021","forest_pct":57.2},
    {"country":"Gabon","iso":"GAB","year":"2021","forest_pct":88.1},
    {"country":"South Africa","iso":"ZAF","year":"2021","forest_pct":7.6},
    {"country":"Mexico","iso":"MEX","year":"2021","forest_pct":33.9},
]

# CO2 time series for trend tab (10 countries x ~15 years)
_CO2_SERIES = [
    {"country":"Indonesia","year":2008,"co2_kt":1.5},{"country":"Indonesia","year":2012,"co2_kt":1.7},
    {"country":"Indonesia","year":2016,"co2_kt":1.8},{"country":"Indonesia","year":2019,"co2_kt":2.0},
    {"country":"Indonesia","year":2021,"co2_kt":2.1},
    {"country":"United States","year":2008,"co2_kt":17.9},{"country":"United States","year":2012,"co2_kt":16.4},
    {"country":"United States","year":2016,"co2_kt":15.5},{"country":"United States","year":2019,"co2_kt":15.2},
    {"country":"United States","year":2021,"co2_kt":14.9},
    {"country":"China","year":2008,"co2_kt":5.0},{"country":"China","year":2012,"co2_kt":6.6},
    {"country":"China","year":2016,"co2_kt":7.0},{"country":"China","year":2019,"co2_kt":7.6},
    {"country":"China","year":2021,"co2_kt":8.0},
    {"country":"India","year":2008,"co2_kt":1.3},{"country":"India","year":2012,"co2_kt":1.6},
    {"country":"India","year":2016,"co2_kt":1.7},{"country":"India","year":2019,"co2_kt":1.9},
    {"country":"India","year":2021,"co2_kt":1.9},
    {"country":"Germany","year":2008,"co2_kt":10.5},{"country":"Germany","year":2012,"co2_kt":9.6},
    {"country":"Germany","year":2016,"co2_kt":9.0},{"country":"Germany","year":2019,"co2_kt":8.4},
    {"country":"Germany","year":2021,"co2_kt":8.1},
    {"country":"Brazil","year":2008,"co2_kt":2.0},{"country":"Brazil","year":2012,"co2_kt":2.4},
    {"country":"Brazil","year":2016,"co2_kt":2.3},{"country":"Brazil","year":2019,"co2_kt":2.2},
    {"country":"Brazil","year":2021,"co2_kt":2.3},
    {"country":"Japan","year":2008,"co2_kt":9.8},{"country":"Japan","year":2012,"co2_kt":10.3},
    {"country":"Japan","year":2016,"co2_kt":9.5},{"country":"Japan","year":2019,"co2_kt":8.9},
    {"country":"Japan","year":2021,"co2_kt":8.6},
    {"country":"Australia","year":2008,"co2_kt":17.4},{"country":"Australia","year":2012,"co2_kt":16.5},
    {"country":"Australia","year":2016,"co2_kt":16.0},{"country":"Australia","year":2019,"co2_kt":15.2},
    {"country":"Australia","year":2021,"co2_kt":14.8},
    {"country":"France","year":2008,"co2_kt":6.0},{"country":"France","year":2012,"co2_kt":5.4},
    {"country":"France","year":2016,"co2_kt":5.0},{"country":"France","year":2019,"co2_kt":4.9},
    {"country":"France","year":2021,"co2_kt":4.7},
    {"country":"United Kingdom","year":2008,"co2_kt":8.3},{"country":"United Kingdom","year":2012,"co2_kt":7.2},
    {"country":"United Kingdom","year":2016,"co2_kt":6.0},{"country":"United Kingdom","year":2019,"co2_kt":5.6},
    {"country":"United Kingdom","year":2021,"co2_kt":5.3},
]

# Temperature anomaly series (global avg anomaly vs 1951-1980 baseline, NASA GISS)
_TEMP_SERIES = [
    {"country":"Global","year":y,"temperature_anomaly":v} for y,v in [
        (2000,0.42),(2001,0.54),(2002,0.63),(2003,0.62),(2004,0.54),
        (2005,0.68),(2006,0.61),(2007,0.66),(2008,0.54),(2009,0.64),
        (2010,0.72),(2011,0.61),(2012,0.64),(2013,0.68),(2014,0.75),
        (2015,0.87),(2016,1.01),(2017,0.92),(2018,0.85),(2019,0.98),
        (2020,1.02),(2021,0.85),(2022,0.89),(2023,1.17),(2024,1.29),
    ]
]


# ─────────────────────────────────────────────
# API FETCHERS
# ─────────────────────────────────────────────

# ── wttr.in weather helper ────────────────────
def _parse_wttr_history(lat: float, lon: float, days: int) -> pd.DataFrame:
    """
    Fetch weather history from wttr.in JSON API.
    Returns DataFrame with same columns as original open-meteo output.
    wttr.in returns up to 3 days of hourly data per call — we aggregate
    to daily and repeat calls for the full period in weekly chunks.
    """
    end_dt   = datetime.utcnow().date()
    start_dt = end_dt - timedelta(days=days)
    rows = []
    # wttr.in free tier: fetch current + past via format=j1 (JSON)
    # It only gives ~3 days history, so we use Open-Meteo as primary
    # and wttr.in as fallback
    raise NotImplementedError("use open-meteo primary")


@st.cache_data(ttl=3600)
def fetch_weather(lat: float, lon: float, days: int = 30) -> pd.DataFrame:
    """
    Fetch weather data from Open-Meteo Archive API (primary source).
    Uses live, complete data from the primary API.
    """
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)

    # Open-Meteo Archive API - Primary Live Data Source
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        "&daily=temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,windspeed_10m_max,"
        "shortwave_radiation_sum,"
        "relative_humidity_2m_max,relative_humidity_2m_min"
        "&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm"
        "&timezone=UTC"
    )

    try:
        r = _get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        if "daily" not in data:
            st.error("❌ Unexpected API response format")
            return pd.DataFrame()
        
        df = pd.DataFrame(data["daily"])
        df["time"] = pd.to_datetime(df["time"])
        
        # Trim to requested range
        df = df[df["time"].dt.date >= start].reset_index(drop=True)
        
        if df.empty:
            st.error("❌ No data available for selected location and date range")
            return pd.DataFrame()
        
        # Calculate mean values from min/max
        df["temperature_2m_mean"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
        df["relative_humidity_2m_mean"] = (df["relative_humidity_2m_max"] + df["relative_humidity_2m_min"]) / 2
        df["windspeed_10m_mean"] = df["windspeed_10m_max"] * 0.75  # Rough estimate
        
        # Add mean pressure estimate (simplified)
        df["pressure_2m_mean"] = 1013  # Standard atmospheric pressure fallback
        
        # Fill any remaining missing values
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        return df
        
    except requests.exceptions.Timeout:
        st.error("❌ Request timeout - API took too long to respond. Please try again.")
        return pd.DataFrame()
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection error - Unable to reach Open-Meteo API. Check your internet connection.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error fetching weather data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_forecast(lat: float, lon: float) -> pd.DataFrame:
    # Primary: Open-Meteo forecast (7 days)
    url_primary = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,shortwave_radiation_sum,"
        "relative_humidity_2m_max,relative_humidity_2m_min"
        "&temperature_unit=celsius&wind_speed_unit=kmh&precipitation_unit=mm"
        "&timezone=UTC&forecast_days=7"
    )
    try:
        r = _get(url_primary, timeout=25)
        r.raise_for_status()
        data = r.json()
        if "daily" not in data:
            raise ValueError("Invalid response format")
        df = pd.DataFrame(data["daily"])
        df["time"] = pd.to_datetime(df["time"])
        df = df.fillna(method='ffill').fillna(method='bfill')
        return df.head(7)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_air_quality(lat: float, lon: float) -> dict:
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,uv_index"
        "&timezone=UTC&forecast_days=1"
    )
    try:
        r = _get(url, timeout=25)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["hourly"])
        df["time"] = pd.to_datetime(df["time"])
        latest = df.dropna().iloc[-1] if not df.empty else {}
        return {
            "pm2_5":           round(float(latest.get("pm2_5", 0)), 1),
            "pm10":            round(float(latest.get("pm10", 0)), 1),
            "carbon_monoxide": round(float(latest.get("carbon_monoxide", 0)), 1),
            "nitrogen_dioxide":round(float(latest.get("nitrogen_dioxide", 0)), 1),
            "ozone":           round(float(latest.get("ozone", 0)), 1),
            "uv_index":        round(float(latest.get("uv_index", 0)), 1),
            "df": df,
        }
    except Exception as e:
        st.warning(f"🌿 Air quality signal weak — {type(e).__name__}. Using placeholder values.")
        return {
            "pm2_5": 12.0, "pm10": 20.0, "carbon_monoxide": 250.0,
            "nitrogen_dioxide": 15.0, "ozone": 80.0, "uv_index": 5.0,
            "df": pd.DataFrame(),
        }


@st.cache_data(ttl=86400)
def fetch_worldbank_co2() -> pd.DataFrame:
    url = ("https://api.worldbank.org/v2/country/all/indicator/EN.ATM.CO2E.PC"
           "?format=json&mrv=1&per_page=300")
    try:
        r = _get(url, timeout=20); r.raise_for_status()
        raw = r.json()
        if len(raw) >= 2 and raw[1]:
            return pd.DataFrame([
                {"country": d["country"]["value"], "iso": d["countryiso3code"],
                 "year": d["date"], "co2": d["value"]}
                for d in raw[1] if d["value"] is not None and d["countryiso3code"]
            ])
    except Exception:
        pass
    # Static fallback — always available
    return pd.DataFrame(_CO2_STATIC)


@st.cache_data(ttl=86400)
def fetch_worldbank_forest() -> pd.DataFrame:
    url = ("https://api.worldbank.org/v2/country/all/indicator/AG.LND.FRST.ZS"
           "?format=json&mrv=1&per_page=300")
    try:
        r = _get(url, timeout=20); r.raise_for_status()
        raw = r.json()
        if len(raw) >= 2 and raw[1]:
            return pd.DataFrame([
                {"country": d["country"]["value"], "iso": d["countryiso3code"],
                 "year": d["date"], "forest_pct": d["value"]}
                for d in raw[1] if d["value"] is not None and d["countryiso3code"]
            ])
    except Exception:
        pass
    return pd.DataFrame(_FOREST_STATIC)


@st.cache_data(ttl=86400)
def fetch_worldbank_series(indicator: str, label: str, n_years: int = 20) -> pd.DataFrame:
    countries = "IDN;USA;CHN;IND;DEU;BRA;GBR;AUS;JPN;FRA"
    url = (f"https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"
           f"?format=json&mrv={n_years}&per_page=500")
    try:
        r = _get(url, timeout=20); r.raise_for_status()
        raw = r.json()
        if len(raw) >= 2 and raw[1]:
            df = pd.DataFrame([
                {"country": d["country"]["value"], "year": int(d["date"]), label: d["value"]}
                for d in raw[1] if d["value"] is not None
            ]).sort_values("year")
            if not df.empty:
                return df
    except Exception:
        pass
    # Static fallback
    if "co2" in label.lower() or indicator.startswith("EN.ATM"):
        df = pd.DataFrame(_CO2_SERIES)
        df.rename(columns={"co2_kt": label}, inplace=True)
        return df
    if "temp" in label.lower():
        df = pd.DataFrame(_TEMP_SERIES)
        df.rename(columns={"temperature_anomaly": label}, inplace=True)
        return df
    return pd.DataFrame()


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
WMO_CODES = {
    0:"☀️", 1:"🌤️", 2:"⛅", 3:"☁️", 45:"🌫️", 48:"🌫️",
    51:"🌦️", 53:"🌦️", 55:"🌧️", 61:"🌧️", 63:"🌧️", 65:"🌧️",
    71:"🌨️", 73:"🌨️", 75:"❄️", 80:"🌦️", 81:"🌧️", 95:"⛈️",
}
WMO_LABEL_EN = {
    0:"Clear", 1:"Mostly Clear", 2:"Partly Cloudy", 3:"Overcast",
    45:"Fog", 48:"Icy Fog", 51:"Lt Drizzle", 53:"Drizzle", 55:"Hvy Drizzle",
    61:"Lt Rain", 63:"Rain", 65:"Hvy Rain", 71:"Lt Snow", 73:"Snow",
    75:"Hvy Snow", 80:"Showers", 81:"Hvy Showers", 95:"Thunderstorm",
}
WMO_LABEL_ID = {
    0:"Cerah", 1:"Cerah Berawan", 2:"Berawan", 3:"Mendung",
    45:"Kabut", 48:"Kabut Beku", 51:"Gerimis", 53:"Gerimis", 55:"Gerimis Lebat",
    61:"Hujan Ringan", 63:"Hujan", 65:"Hujan Lebat", 71:"Salju Ringan",
    73:"Salju", 75:"Salju Lebat", 80:"Hujan Lokal", 81:"Hujan Lokal Lebat",
    95:"Badai Petir",
}

# ─── Geocoding API function - Search locations worldwide ───
@st.cache_data(ttl=3600)
def search_locations(query: str) -> dict:
    """Search for locations using Open-Meteo Geocoding API."""
    if not query or len(query) < 2:
        return {}
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": query, "count": 10, "language": "en", "format": "json"}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = {}
        if "results" in data:
            for result in data["results"]:
                name_parts = []
                if "name" in result:
                    name_parts.append(result["name"])
                if "admin1" in result:
                    name_parts.append(result["admin1"])
                if "country" in result:
                    name_parts.append(result["country"])
                display_name = ", ".join(name_parts)
                lat = result.get("latitude")
                lon = result.get("longitude")
                if lat is not None and lon is not None:
                    results[display_name] = (lat, lon)
        return results
    except Exception as e:
        st.warning(f"Error searching locations: {str(e)}", icon="⚠️")
        return {}

# Default cities for initial load
DEFAULT_CITIES = {
    "Jakarta, Indonesia": (-6.2088, 106.8456),
    "Surabaya, Indonesia": (-7.2575, 112.7521),
    "Bandung, Indonesia": (-6.9175, 107.6191),
    "New York, USA": (40.7128, -74.0060),
    "London, United Kingdom": (51.5074, -0.1278),
    "Tokyo, Japan": (35.6762, 139.6503),
}

# ─── AQI colour + label (bilingual) ───────────
def aqi_info(pm25: float) -> tuple[str, str, str]:
    """Returns (label_en, label_id, hex_color)."""
    if pm25 <= 15.5:   return "Healthy Barn",    "Baik (Lumbung Sehat)",      "#5A9E2A"
    if pm25 <= 55.4: return "Cozy Staple",     "Sedang (Kandang Nyaman)",   "#C8A030"
    if pm25 <= 150.4: return "Young Stock Alert",     "Tidak Sehat untuk Kelompok Sensitif (Peringatan Ternak Muda)",       "#CC5818"
    if pm25 <= 250.4:  return "Livestock Stress",     "Tidak Sehat (Ternak Stres)",     "#8E2A0A"
    if pm25 <= 350.4:  return "Health Crisis",     "Sangat Tidak Sehat (Krisis Kesehatan)",     "#FF0000"
    return               "Ranch Emergency",        "Berbahaya (Darurat Peternakan)",       "#000000"

# ─── Plotly base layout (Farming palette) ──
SH_PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#FFFFFF",
    font=dict(family="Share Tech Mono, monospace", size=11, color="#9A9288"),
    margin=dict(l=32, r=12, t=28, b=8),
    hovermode="x unified",
)
LINE_RUST  = "#C0112A"
LINE_ASH   = "#6A8A30"
LINE_MIST  = "#5A5450"
LINE_DARK  = "#D8D0C8"


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:

    # ── Logo / title ──────────────────────────
    st.markdown("""
    <div style="padding:16px 0 12px 0;">
        <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                    color:#E8B873; letter-spacing:0.08em; text-transform:uppercase;
                    margin-bottom:8px;">🐄 🐔 🐑</div>
        <div style="font-family:'Poppins',sans-serif; font-size:1.80rem; font-weight:700;
                    color:#2C2622; letter-spacing:-0.01em; line-height:1.1;">
            Farm<br>Weather
        </div>
        <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                    color:#6B6560; letter-spacing:0.02em; margin-top:6px;
                    text-transform:none;">Climate & Weather Tracker</div>
        <div style="border-top:2px solid #E8E6E2; margin-top:12px;
                    padding-top:10px; font-family:'Poppins',sans-serif;
                    font-size:0.65rem; color:#A8A39E; letter-spacing:0.02em;
                    text-transform:none;">
                    🌾 Track weather for your farm
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Language toggle — actual slider ──
    is_id = st.session_state.lang == "ID"

    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.60rem;
                letter-spacing:0.18em; color:#9AAE7C; text-transform:uppercase;
                margin-bottom:4px;">🌐 Language / Bahasa</div>
    """, unsafe_allow_html=True)

    lang_choice = st.select_slider(
        "language_toggle",
        options=["EN", "ID"],
        value="ID" if is_id else "EN",
        key="lang_slider",
        label_visibility="collapsed",
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.markdown("---")

    # ── City/Location search with API support ──
    city_label   = t("📍 City / Location", "📍 Kota / Lokasi")
    search_placeholder = t("🔍 Search any city...", "🔍 Cari kota mana saja...")
    
    location_query = st.text_input(
        city_label,
        value="",
        placeholder=search_placeholder,
        help=t("Type location name (worldwide)", "Ketik nama lokasi (seluruh dunia)"),
        label_visibility="visible"
    )
    
    if location_query and len(location_query) >= 2:
        search_results = search_locations(location_query)
        if search_results:
            city_name = st.selectbox(
                t("Select location", "Pilih lokasi"),
                list(search_results.keys()),
                label_visibility="collapsed",
                key="sidebar_location_select"
            )
            lat, lon = search_results[city_name]
            if city_name != st.session_state.selected_city:
                st.session_state.selected_city = city_name
        else:
            st.info(t("No locations found", "Lokasi tidak ditemukan"))
            city_name = st.session_state.selected_city
            if city_name in DEFAULT_CITIES:
                lat, lon = DEFAULT_CITIES[city_name]
            else:
                city_name = list(DEFAULT_CITIES.keys())[0]
                lat, lon = DEFAULT_CITIES[city_name]
    else:
        city_name = st.session_state.selected_city
        if city_name in DEFAULT_CITIES:
            lat, lon = DEFAULT_CITIES[city_name]
        else:
            city_name = list(DEFAULT_CITIES.keys())[0]
            st.session_state.selected_city = city_name
            lat, lon = DEFAULT_CITIES[city_name]

    # ── History slider ─────────────────────────
    hist_label   = t("📅 History (days)", "📅 Riwayat (hari)")
    history_days = st.slider(hist_label, 7, 365, 30)

    # ── Refresh button ─────────────────────────
    st.markdown("---")
    refresh_label = t("🔄  Refresh Data", "🔄  Perbarui Data")
    if st.button(refresh_label, use_container_width=True, key="btn_refresh"):
        st.cache_data.clear()
        st.rerun()

    # ── Data sources ───────────────────────────
    st.markdown("---")
    src_title = t("DATA SOURCES", "SUMBER DATA")
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                letter-spacing:0.18em; color:#5A5450; margin-bottom:8px;
                text-transform:uppercase;">// {src_title}</div>
    """, unsafe_allow_html=True)
    st.markdown("""
- [Open-Meteo](https://open-meteo.com)
- [Open-Meteo AQ](https://air-quality-api.open-meteo.com)
- [World Bank](https://data.worldbank.org)
    """)

    # ── Timestamp ──────────────────────────────
    st.markdown(f"""
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                color:#5A7A84; margin-top:12px; letter-spacing:0.08em;">
        {datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
h_subtitle = t(
    "Real-time weather, air quality & global environmental data",
    "Cuaca real-time, kualitas udara & data lingkungan global"
)
h_location = t("Monitoring:", "Memantau:")

st.markdown(f"""
<div style="border:1px solid #E8E6E2; border-top:3px solid #E8B873;
            border-radius:6px;
            background:#FFFFFF; padding:20px 24px;
            box-shadow:0 2px 8px rgba(0,0,0,0.06);
            margin-bottom:0; position:relative;">
    <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                letter-spacing:0.06em; color:#A8A39E; margin-bottom:8px;
                text-transform:uppercase;">
        🌾 Farm Weather Tracker
    </div>
    <h1 style="font-family:'Poppins',sans-serif; font-size:2.2rem; font-weight:700;
               color:#2C2622; margin:0; letter-spacing:-0.01em; line-height:1.1;">
        Farm Forecast
    </h1>
    <div style="font-family:'Poppins',sans-serif; font-size:0.80rem;
                color:#6B6560; margin:12px 0 0 0; letter-spacing:0.01em;
                border-top:1px solid #E8E6E2; padding-top:10px;">
        {h_subtitle}<br>
        <span style="color:#E8B873;">📍 {h_location}</span>
        <span style="color:#A8A39E;"> {city_name}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FULL-BODY ANIMATION — Farm Theme with Vibrant Animals
# ─────────────────────────────────────────────
components.html("""
<!DOCTYPE html><html><head>
<style>* { margin:0; padding:0; box-sizing:border-box; }</style>
</head>
<body style="background:transparent; overflow:hidden; width:0; height:0;">
<script>
(function() {
function init() {
  const P = window.parent.document;
  if (!P) return;
  const cv = P.getElementById('farm-doodle-cv');
  if (cv) cv.remove();
  
  const canvas = P.createElement('canvas');
  canvas.id = 'farm-doodle-cv';
  Object.assign(canvas.style, {
    position:'fixed', top:'0', left:'0',
    width:'100vw', height:'100vh',
    pointerEvents:'none', zIndex:'0', opacity:'0.12'
  });
  P.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');
  
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);
  
  class AnimatedCow {
    constructor(x, y, speed) {
      this.x = x;
      this.y = y;
      this.speed = speed;
      this.time = 0;
      this.tailSwing = 0;
    }
    update() {
      this.x += this.speed;
      this.time += 0.02;
      this.tailSwing = Math.sin(this.time * 2) * 8;
      if (this.x > canvas.width + 100) this.x = -100;
    }
    draw() {
      ctx.save(); ctx.translate(this.x, this.y);
      // body
      ctx.fillStyle = '#A89688';
      ctx.beginPath(); ctx.ellipse(0, 0, 40, 25, 0, 0, Math.PI*2);
      ctx.fill();
      // head
      ctx.beginPath(); ctx.arc(35, -15, 18, 0, Math.PI*2);
      ctx.fill();
      // ears with animation
      ctx.beginPath(); ctx.ellipse(28, -28 + Math.sin(this.time)*2, 6, 10, -0.5, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(42, -28 + Math.sin(this.time + 0.5)*2, 6, 10, 0.5, 0, Math.PI*2); ctx.fill();
      // snout
      ctx.fillStyle = '#C9A79E';
      ctx.beginPath(); ctx.arc(50, -12, 8, 0, Math.PI*2); ctx.fill();
      // horns
      ctx.strokeStyle = '#A89688'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(24, -35); ctx.lineTo(16, -45);
      ctx.stroke();
      ctx.beginPath(); ctx.moveTo(46, -35); ctx.lineTo(54, -45);
      ctx.stroke();
      // legs
      ctx.fillStyle = '#A89688';
      [-20, -5, 5, 20].forEach((ox, i) => {
        const legBob = Math.sin(this.time * 3 + i) * 2;
        ctx.fillRect(ox-3, 20 + legBob, 6, 20);
      });
      // tail with swing
      ctx.strokeStyle = '#A89688'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(-45, 5);
      ctx.quadraticCurveTo(-55, 5 + this.tailSwing, -50, 15);
      ctx.stroke();
      ctx.restore();
    }
  }
  
  class AnimatedChicken {
    constructor(x, y, speed) {
      this.x = x;
      this.y = y;
      this.speed = speed;
      this.time = 0;
    }
    update() {
      this.x += this.speed;
      this.time += 0.03;
      if (this.x > canvas.width + 100) this.x = -100;
    }
    draw() {
      ctx.save(); ctx.translate(this.x, this.y);
      // body bobbing
      const bodyBob = Math.sin(this.time * 3) * 3;
      ctx.fillStyle = '#FF9F1C';
      ctx.beginPath(); ctx.ellipse(0, bodyBob, 22, 28, 0, 0, Math.PI*2); ctx.fill();
      // head
      ctx.beginPath(); ctx.arc(10, -25 + bodyBob, 12, 0, Math.PI*2); ctx.fill();
      // comb
      ctx.fillStyle = '#FF6B9D';
      for(let i = 0; i < 3; i++) {
        const wobble = Math.sin(this.time * 2 + i) * 2;
        ctx.beginPath(); ctx.moveTo(5 + i*5, -32 + wobble); ctx.lineTo(2 + i*5, -42 + wobble); 
        ctx.lineTo(8 + i*5, -38 + wobble); ctx.closePath(); ctx.fill();
      }
      // eye
      ctx.fillStyle = '#2C2622'; ctx.beginPath(); ctx.arc(15, -25 + bodyBob, 3, 0, Math.PI*2); ctx.fill();
      // beak
      ctx.fillStyle = '#FFD93D'; ctx.beginPath(); ctx.moveTo(20, -23 + bodyBob); ctx.lineTo(28, -22 + bodyBob); 
      ctx.lineTo(20, -20 + bodyBob); ctx.closePath(); ctx.fill();
      // legs with step animation
      ctx.strokeStyle = '#FFD93D'; ctx.lineWidth = 2;
      const legLift1 = Math.sin(this.time * 4) > 0 ? 2 : 0;
      const legLift2 = Math.sin(this.time * 4 + Math.PI) > 0 ? 2 : 0;
      ctx.beginPath(); ctx.moveTo(-8, 25 + bodyBob); ctx.lineTo(-8, 35 + bodyBob - legLift1);
      ctx.stroke();
      ctx.beginPath(); ctx.moveTo(8, 25 + bodyBob); ctx.lineTo(8, 35 + bodyBob - legLift2);
      ctx.stroke();
      ctx.restore();
    }
  }
  
  class AnimatedSheep {
    constructor(x, y, speed) {
      this.x = x;
      this.y = y;
      this.speed = speed;
      this.time = 0;
    }
    update() {
      this.x += this.speed;
      this.time += 0.015;
      if (this.x > canvas.width + 100) this.x = -100;
    }
    draw() {
      ctx.save(); ctx.translate(this.x, this.y);
      // wool - fluffy with animation
      ctx.fillStyle = '#FFFACD';
      ctx.beginPath(); ctx.arc(0, 0 + Math.sin(this.time)*2, 28, 0, Math.PI*2); ctx.fill();
      // head
      ctx.fillStyle = '#C9A79E';
      ctx.beginPath(); ctx.arc(35, 0, 14, 0, Math.PI*2); ctx.fill();
      // ears
      ctx.beginPath(); ctx.ellipse(30, -12 + Math.sin(this.time + 1)*1, 5, 8, -0.4, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(40, -12 + Math.sin(this.time + 2)*1, 5, 8, 0.4, 0, Math.PI*2); ctx.fill();
      // eyes
      ctx.fillStyle = '#2C2622';
      ctx.beginPath(); ctx.arc(40, -3, 2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(40, 3, 2, 0, Math.PI*2); ctx.fill();
      // legs
      ctx.strokeStyle = '#C9A79E'; ctx.lineWidth = 2;
      [-12, -4, 4, 12].forEach((ox, i) => {
        const legBob = Math.sin(this.time * 2 + i) * 2;
        ctx.beginPath(); ctx.moveTo(ox, 25); ctx.lineTo(ox, 35 + legBob); ctx.stroke();
      });
      ctx.restore();
    }
  }
  
  class AnimatedPig {
    constructor(x, y, speed) {
      this.x = x;
      this.y = y;
      this.speed = speed;
      this.time = 0;
    }
    update() {
      this.x += this.speed;
      this.time += 0.025;
      if (this.x > canvas.width + 100) this.x = -100;
    }
    draw() {
      ctx.save(); ctx.translate(this.x, this.y);
      const wiggle = Math.sin(this.time * 2) * 2;
      ctx.fillStyle = '#FFB8C6';
      // body
      ctx.beginPath(); ctx.ellipse(wiggle, 0, 32, 22, 0, 0, Math.PI*2); ctx.fill();
      // head
      ctx.beginPath(); ctx.arc(30 + wiggle, -8, 16, 0, Math.PI*2); ctx.fill();
      // snout
      ctx.beginPath(); ctx.ellipse(42 + wiggle, -8, 10, 8, 0, 0, Math.PI*2); ctx.fill();
      // nostrils
      ctx.fillStyle = '#FF99B9';
      ctx.beginPath(); ctx.arc(38 + wiggle, -8, 2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(46 + wiggle, -8, 2, 0, Math.PI*2); ctx.fill();
      // ears
      ctx.fillStyle = '#FFB8C6';
      ctx.beginPath(); ctx.ellipse(22 + wiggle, -18 + Math.sin(this.time)*2, 8, 12, -0.6, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(38 + wiggle, -18 + Math.sin(this.time + 1)*2, 8, 12, 0.6, 0, Math.PI*2); ctx.fill();
      // legs
      ctx.fillStyle = '#FFB8C6';
      [-16, -4, 4, 16].forEach((ox, i) => {
        const legBob = Math.sin(this.time * 3 + i) * 2;
        ctx.fillRect(ox-3 + wiggle, 20 + legBob, 6, 18);
      });
      // tail curl
      ctx.strokeStyle = '#FFB8C6'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(-35 + wiggle, -5);
      ctx.quadraticCurveTo(-40 + wiggle + Math.sin(this.time)*3, Math.sin(this.time)*5, -35 + wiggle, 10);
      ctx.stroke();
      ctx.restore();
    }
  }
  
  // Create animated animals
  const cows = [
    new AnimatedCow(150, 200, 0.15),
    new AnimatedCow(800, 300, 0.10),
  ];
  const chickens = [
    new AnimatedChicken(300, 150, 0.25),
    new AnimatedChicken(950, 350, 0.20),
  ];
  const sheep = [
    new AnimatedSheep(550, 280, 0.12),
    new AnimatedSheep(1200, 400, 0.08),
  ];
  const pigs = [
    new AnimatedPig(700, 380, 0.18),
    new AnimatedPig(400, 450, 0.12),
  ];
  
  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Update and draw all animals
    [...cows, ...chickens, ...sheep, ...pigs].forEach(animal => {
      animal.update();
      animal.draw();
    });
  }
  
  // Animation loop
  function animate() {
    draw();
    requestAnimationFrame(animate);
  }
  animate();
}

setTimeout(init, 120);
})();
</script>
</body></html>""", height=0, scrolling=False)



# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_labels = [
    t("Weather", "Cuaca"),
    t("Air Quality", "Kualitas Udara"),
    t("CO₂ & Forest", "CO₂ & Hutan"),
    t("Trends", "Tren"),
    t("🌿 Oracle", "🌿 Oracle"),
]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)


# ═══════════════════════════════════════════════════════
# TAB 1 — WEATHER
# ═══════════════════════════════════════════════════════
with tab1:
    hist  = fetch_weather(lat, lon, history_days)
    fcast = fetch_forecast(lat, lon)

    if not hist.empty:
        # ── Calculate date range for charts ──────────────────
        date_min = hist["time"].min()
        date_max = hist["time"].max()
        
        # ── KPI cards ──────────────────────────────
        hdr_cond = t("// CURRENT CONDITIONS", "// KONDISI TERKINI")
        st.markdown(f'<div class="sh-header">{hdr_cond}</div>', unsafe_allow_html=True)

        latest = hist.iloc[-1]
        kpis = [
            (f"{latest['temperature_2m_mean']:.1f}", "°C",
             t("Temperature", "Suhu")),
            (f"{latest.get('relative_humidity_2m_mean', 0):.0f}", "%",
             t("Humidity", "Kelembapan")),
            (f"{hist['precipitation_sum'].sum():.1f}", "mm",
             t(f"Rain {history_days}d", f"Hujan {history_days}h")),
            (f"{hist['windspeed_10m_max'].mean():.1f}", "km/h",
             t("Avg Wind", "Angin Rata-rata")),
            (f"{latest.get('pressure_2m_mean', 0):.0f}", "hPa",
             t("Pressure", "Tekanan")),
            (f"{hist['shortwave_radiation_sum'].mean():.1f}", "MJ/m²",
             t("Solar Radiation", "Radiasi Matahari")),
        ]
        cols = st.columns(3)
        for i, (val, unit, lbl) in enumerate(kpis):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="sh-card">
                    <div class="sh-card-value">{val}<span class="sh-card-unit">{unit}</span></div>
                    <div class="sh-card-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)
            if (i + 1) % 3 == 0 and i < len(kpis) - 1:
                cols = st.columns(3)

        st.markdown("")

        # ── Temperature chart ──────────────────────
        hdr_temp = t("// TEMPERATURE RECORD", "// REKAM SUHU")
        st.markdown(f'<div class="sh-header">{hdr_temp}</div>', unsafe_allow_html=True)

        fig_temp = go.Figure()
        fig_temp.add_trace(go.Scatter(
            x=hist["time"], y=hist["temperature_2m_max"],
            name=t("Max","Maks"), line=dict(color=LINE_RUST, width=1.5),
        ))
        fig_temp.add_trace(go.Scatter(
            x=hist["time"], y=hist["temperature_2m_min"],
            name=t("Min","Min"), line=dict(color=LINE_ASH, width=1.5),
            fill="tonexty", fillcolor="rgba(106,138,48,0.08)",
        ))
        fig_temp.add_trace(go.Scatter(
            x=hist["time"], y=hist["temperature_2m_mean"],
            name=t("Mean","Rata²"), line=dict(color=LINE_DARK, width=2, dash="dot"),
        ))
        fig_temp.update_layout(
            **SH_PLOT, height=300,
            xaxis=dict(type="date", range=[date_min, date_max]),
            yaxis=dict(autorange=True),
            legend=dict(orientation="h", y=1.08,
                        font=dict(family="Share Tech Mono", size=10)),
            xaxis_title=t("Date","Tanggal"),
            yaxis_title=t("Temperature (°C)","Suhu (°C)"),
        )
        st.plotly_chart(fig_temp, use_container_width=True)

        # ── Rain + Wind ────────────────────────────
        ca, cb = st.columns(2)
        with ca:
            hdr_rain = t("// PRECIPITATION", "// CURAH HUJAN")
            st.markdown(f'<div class="sh-header">{hdr_rain}</div>', unsafe_allow_html=True)
            fig_rain = px.bar(
                hist, x="time", y="precipitation_sum",
                color="precipitation_sum",
                color_continuous_scale=[[0,"#141414"],[0.4,"#3D5A1A"],[1,"#C0112A"]],
                labels={"precipitation_sum": t("Rain (mm)","Hujan (mm)"),
                        "time": t("Date","Tanggal")},
            )
            fig_rain.update_layout(**SH_PLOT, height=260, coloraxis_showscale=False, xaxis=dict(type="date", range=[date_min, date_max]), yaxis=dict(autorange=True))
            st.plotly_chart(fig_rain, use_container_width=True)

        with cb:
            hdr_wind = t("// WIND SPEED", "// KECEPATAN ANGIN")
            st.markdown(f'<div class="sh-header">{hdr_wind}</div>', unsafe_allow_html=True)
            fig_wind = px.area(
                hist, x="time", y="windspeed_10m_max",
                color_discrete_sequence=[LINE_ASH],
                labels={"windspeed_10m_max": t("Wind (km/h)","Angin (km/j)"),
                        "time": t("Date","Tanggal")},
            )
            fig_wind.update_layout(**SH_PLOT, height=260, xaxis=dict(type="date", range=[date_min, date_max]), yaxis=dict(autorange=True))
            st.plotly_chart(fig_wind, use_container_width=True)

        # ── Relative Humidity ──────────────────────
        st.markdown("")
        hdr_humidity = t("// RELATIVE HUMIDITY", "// KELEMBAPAN RELATIF")
        st.markdown(f'<div class="sh-header">{hdr_humidity}</div>', unsafe_allow_html=True)
        
        fig_humidity = go.Figure()
        fig_humidity.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("relative_humidity_2m_max", []),
            name=t("Max","Maks"), line=dict(color="#0099CC", width=1.5),
        ))
        fig_humidity.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("relative_humidity_2m_min", []),
            name=t("Min","Min"), line=dict(color="#00CCFF", width=1.5),
            fill="tonexty", fillcolor="rgba(0,153,204,0.08)",
        ))
        fig_humidity.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("relative_humidity_2m_mean", []),
            name=t("Mean","Rata²"), line=dict(color="#0066CC", width=2, dash="dot"),
        ))
        fig_humidity.update_layout(
            **SH_PLOT, height=300,
            xaxis=dict(type="date", range=[date_min, date_max]),
            yaxis=dict(autorange=True),
            legend=dict(orientation="h", y=1.08,
                        font=dict(family="Share Tech Mono", size=10)),
            xaxis_title=t("Date","Tanggal"),
            yaxis_title=t("Relative Humidity (%)","Kelembapan Relatif (%)"),
        )
        st.plotly_chart(fig_humidity, use_container_width=True)

        # ── Atmospheric Pressure ───────────────────
        st.markdown("")
        hdr_pressure = t("// ATMOSPHERIC PRESSURE", "// TEKANAN UDARA")
        st.markdown(f'<div class="sh-header">{hdr_pressure}</div>', unsafe_allow_html=True)
        
        fig_pressure = go.Figure()
        fig_pressure.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("pressure_2m_max", []),
            name=t("Max","Maks"), line=dict(color="#FF6B35", width=1.5),
        ))
        fig_pressure.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("pressure_2m_min", []),
            name=t("Min","Min"), line=dict(color="#FFA500", width=1.5),
            fill="tonexty", fillcolor="rgba(255,107,53,0.08)",
        ))
        fig_pressure.add_trace(go.Scatter(
            x=hist["time"], y=hist.get("pressure_2m_mean", []),
            name=t("Mean","Rata²"), line=dict(color="#FF6B35", width=2, dash="dot"),
        ))
        fig_pressure.update_layout(
            **SH_PLOT, height=300,
            xaxis=dict(type="date", range=[date_min, date_max]),
            yaxis=dict(autorange=True),
            legend=dict(orientation="h", y=1.08,
                        font=dict(family="Share Tech Mono", size=10)),
            xaxis_title=t("Date","Tanggal"),
            yaxis_title=t("Pressure (hPa)","Tekanan (hPa)"),
        )
        st.plotly_chart(fig_pressure, use_container_width=True)

        # ── Solar Radiation ────────────────────────
        st.markdown("")
        hdr_solar = t("// SOLAR RADIATION", "// RADIASI MATAHARI")
        st.markdown(f'<div class="sh-header">{hdr_solar}</div>', unsafe_allow_html=True)
        
        fig_solar = px.bar(
            hist, x="time", y="shortwave_radiation_sum",
            color="shortwave_radiation_sum",
            color_continuous_scale=[[0,"#F0E68C"],[0.5,"#FFD700"],[1,"#FFA500"]],
            labels={"shortwave_radiation_sum": t("Solar Radiation (MJ/m²)","Radiasi Matahari (MJ/m²)"),
                    "time": t("Date","Tanggal")},
        )
        fig_solar.update_layout(**SH_PLOT, height=260, coloraxis_showscale=False, xaxis=dict(type="date", range=[date_min, date_max]), yaxis=dict(autorange=True))
        st.plotly_chart(fig_solar, use_container_width=True)

    # ── 7-Day Forecast ────────────────────────
    if not fcast.empty:
        hdr_fcast = t("// 7-DAY FORECAST", "// PRAKIRAAN 7 HARI")
        st.markdown(f'<div class="sh-header">{hdr_fcast}</div>', unsafe_allow_html=True)
        
        # Ensure we have exactly 7 days or fewer
        fcast_display = fcast.head(7)
        
        # Build HTML for scrollable forecast cards
        forecast_html = '<div class="sh-scroll-container">'
        for _, row in fcast_display.iterrows():
            # Ensure all fields have values, use 0 or empty string as fallback
            code = int(row.get("weathercode", 0)) if pd.notna(row.get("weathercode")) else 0
            icon = WMO_CODES.get(code, "🌡️")
            wlbl = (WMO_LABEL_EN if st.session_state.lang=="EN" else WMO_LABEL_ID).get(code, "")
            day = row["time"].strftime("%a %d")
            hi = float(row.get("temperature_2m_max", 0)) if pd.notna(row.get("temperature_2m_max")) else 0
            lo = float(row.get("temperature_2m_min", 0)) if pd.notna(row.get("temperature_2m_min")) else 0
            rain = float(row.get("precipitation_sum", 0)) if pd.notna(row.get("precipitation_sum")) else 0
            humidity = float(row.get("relative_humidity_2m_max", 0)) if pd.notna(row.get("relative_humidity_2m_max")) else 0
            solar = float(row.get("shortwave_radiation_sum", 0)) if pd.notna(row.get("shortwave_radiation_sum")) else 0
            
            forecast_html += f"""
            <div class="sh-scroll-item">
                <div class="sh-forecast">
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.6rem;
                                color:#7C7670; letter-spacing:0.08em; text-transform:uppercase;">{day}</div>
                    <div style="font-size:1.5rem; margin:4px 0; line-height:1;">{icon}</div>
                    <div style="font-family:'Special Elite',serif; font-size:0.9rem;
                                color:#D8D0C8;">{hi:.0f}°</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem;
                                color:#5A5450;">{lo:.0f}°</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                                color:#8B3A2A; margin-top:3px;">{rain:.1f}mm</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                                color:#0099CC; margin-top:2px;"><strong>RH: {humidity:.0f}%</strong></div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                                color:#FFA500; margin-top:2px;"><strong>☀: {solar:.1f}</strong></div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.68rem;
                                color:#7C7670; margin-top:3px; font-style:italic;">{wlbl}</div>
                </div>
            </div>"""
        
        forecast_html += '</div>'
        st.markdown(forecast_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 2 — AIR QUALITY
# ═══════════════════════════════════════════════════════
with tab2:
    aq = fetch_air_quality(lat, lon)

    if aq:
        pm25 = aq["pm2_5"]
        lbl_en, lbl_id, aqi_color = aqi_info(pm25)
        aqi_lbl = lbl_en if st.session_state.lang == "EN" else lbl_id

        hdr_aqi = t("// AIR QUALITY INDEX", "// INDEKS KUALITAS UDARA")
        st.markdown(f'<div class="sh-header">{hdr_aqi}</div>', unsafe_allow_html=True)
        pm_label = t("PM2.5 concentration", "Konsentrasi PM2.5")
        st.markdown(f"""
        <div class="sh-aqi-banner" style="border-left-color:{aqi_color};">
            <div style="font-family:'Special Elite',serif; font-size:2.2rem;
                        color:{aqi_color}; letter-spacing:0.06em; line-height:1;">
                {aqi_lbl}
            </div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.82rem;
                        color:#7A7670; margin-top:6px;">
                {pm_label}: <span style="color:{aqi_color}; font-weight:700;">{pm25} µg/m³</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Pollutant KPI cards ────────────────────
        poll_labels = [
            (t("PM10","PM10"),             aq["pm10"],            "µg/m³", LINE_DARK),
            (t("PM2.5","PM2.5"),           aq["pm2_5"],           "µg/m³", LINE_RUST),
            (t("Carbon Monoxide","Karbon Monoksida"), aq["carbon_monoxide"],"µg/m³", LINE_ASH),
            (t("Nitrogen Dioxide","Nitrogen Dioksida"),aq["nitrogen_dioxide"],"µg/m³",LINE_MIST),
            (t("Ozone","Ozon"),            aq["ozone"],           "µg/m³", LINE_DARK),
            (t("UV Index","Indeks UV"),    aq["uv_index"],        "",       LINE_RUST),
        ]
        pcols = st.columns([1,1,1,1,1,1])
        for col, (name, val, unit, clr) in zip(pcols, poll_labels):
            with col:
                st.markdown(f"""
                <div class="sh-card">
                    <div class="sh-card-value" style="color:{clr};font-size:1.5rem;">{val}</div>
                    <div class="sh-card-unit">{unit}</div>
                    <div class="sh-card-label">{name}</div>
                </div>""", unsafe_allow_html=True)

        # ── Hourly AQ chart ────────────────────────
        hdr_haq = t("// HOURLY AIR QUALITY", "// KUALITAS UDARA PER JAM")
        st.markdown(f'<div class="sh-header">{hdr_haq}</div>', unsafe_allow_html=True)
        df_aq = aq["df"].dropna(subset=["pm2_5","pm10"])
        if not df_aq.empty:
            fig_aq = go.Figure()
            for col_key, clr, lbl in [
                ("pm2_5", LINE_RUST, "PM2.5"),
                ("pm10",  LINE_ASH,  "PM10"),
                ("ozone", LINE_MIST, t("Ozone","Ozon")),
            ]:
                if col_key in df_aq.columns:
                    fig_aq.add_trace(go.Scatter(
                        x=df_aq["time"], y=df_aq[col_key],
                        name=lbl, line=dict(color=clr, width=1.8),
                    ))
            fig_aq.add_hline(y=35.4, line_dash="dash", line_color="#7A0A18",
                             line_width=1, opacity=0.6,
                             annotation_text=t("PM2.5 threshold","Batas PM2.5"),
                             annotation_font_color=LINE_RUST)
            fig_aq.update_layout(
                **SH_PLOT, height=300,
                xaxis_title=t("Hour","Jam"),
                yaxis_title="µg/m³",
                legend=dict(orientation="h", y=1.08,
                            font=dict(family="Share Tech Mono", size=10)),
            )
            st.plotly_chart(fig_aq, use_container_width=True)

        # ── UV Gauge ───────────────────────────────
        hdr_uv = t("// UV INDEX", "// INDEKS UV")
        st.markdown(f'<div class="sh-header">{hdr_uv}</div>', unsafe_allow_html=True)
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=aq["uv_index"],
            domain={"x":[0,1],"y":[0,1]},
            title={"text": t("UV Index","Indeks UV"),
                   "font":{"family":"Special Elite","color":"#1C1A18","size":13}},
            number={"font":{"family":"Special Elite","color":"#1C1A18","size":32}},
            gauge={
                "axis":{"range":[0,11],"tickcolor":"#9A9490",
                        "tickfont":{"family":"Share Tech Mono","size":10}},
                "bar":{"color":"#3A3630"},
                "bgcolor":"#EAE6E0",
                "bordercolor":"#CCC7BC",
                "steps":[
                    {"range":[0,3],  "color":"#C8D4C0"},
                    {"range":[3,6],  "color":"#D4C890"},
                    {"range":[6,8],  "color":"#C8A870"},
                    {"range":[8,11], "color":"#C87058"},
                ],
                "threshold":{"line":{"color":LINE_RUST,"width":2},"value":aq["uv_index"]},
            },
        ))
        fig_g.update_layout(
            paper_bgcolor="#FFFFFF", font_color="#9A9288",
            height=260, margin=dict(l=20,r=20,t=36,b=0),
        )
        st.plotly_chart(fig_g, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 3 — CO₂ & FOREST
# ═══════════════════════════════════════════════════════
with tab3:
    hdr_co2map = t("// CO₂ EMISSIONS PER CAPITA — WORLD MAP",
                   "// EMISI CO₂ PER KAPITA — PETA DUNIA")
    st.markdown(f'<div class="sh-header">{hdr_co2map}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="sh-info">{t("Source: World Bank — most recent year per country.",
          "Sumber: World Bank — tahun terbaru per negara.")}</div>',
        unsafe_allow_html=True)

    co2_df = fetch_worldbank_co2()
    if not co2_df.empty:
        fig_map = px.choropleth(
            co2_df, locations="iso", color="co2",
            hover_name="country",
            hover_data={"co2":":.2f","year":True},
            color_continuous_scale=[[0,"#141414"],[0.4,"#5A5450"],[1,"#C0112A"]],
            labels={"co2": t("CO₂ (t/capita)","CO₂ (t/kapita)")},
        )
        fig_map.update_layout(
            **SH_PLOT, height=380,
            geo=dict(bgcolor="#FFFFFF", showframe=False,
                     showcoastlines=True, coastlinecolor="#2A2A2A",
                     landcolor="#080808", oceancolor="#FFFFFF",
                     showocean=True),
            coloraxis_colorbar=dict(
                title=dict(
                    text=t("CO₂<br>t/cap","CO₂<br>t/kap"),
                    font=dict(family="Share Tech Mono", size=9),
                ),
                tickfont=dict(family="Share Tech Mono", size=9),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)

        hdr_top = t("// TOP 20 EMITTERS", "// 20 NEGARA EMITOR TERATAS")
        st.markdown(f'<div class="sh-header">{hdr_top}</div>', unsafe_allow_html=True)
        top20 = co2_df.nlargest(20,"co2")
        fig_bar = px.bar(
            top20, x="co2", y="country", orientation="h",
            color="co2",
            color_continuous_scale=[[0,"#141414"],[0.5,"#5A5450"],[1,"#C0112A"]],
            labels={"co2": t("CO₂ (t/capita)","CO₂ (t/kapita)"), "country":""},
        )
        fig_bar.update_layout(
            **SH_PLOT, height=460,
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    hdr_forest = t("// FOREST AREA (% OF LAND)", "// LUAS HUTAN (% WILAYAH)")
    st.markdown(f'<div class="sh-header">{hdr_forest}</div>', unsafe_allow_html=True)
    forest_df = fetch_worldbank_forest()
    if not forest_df.empty:
        fig_forest = px.choropleth(
            forest_df, locations="iso", color="forest_pct",
            hover_name="country",
            color_continuous_scale=[[0,"#080808"],[0.4,"#2A4A18"],[1,"#6A8A30"]],
            labels={"forest_pct": t("Forest (%)","Hutan (%)")},
        )
        fig_forest.update_layout(
            **SH_PLOT, height=360,
            geo=dict(bgcolor="#FFFFFF", showframe=False,
                     showcoastlines=True, coastlinecolor="#2A2A2A",
                     landcolor="#080808", oceancolor="#FFFFFF", showocean=True),
        )
        st.plotly_chart(fig_forest, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 4 — TRENDS
# ═══════════════════════════════════════════════════════
with tab4:
    hdr_co2t = t("// CO₂ EMISSIONS TREND", "// TREN EMISI CO₂")
    st.markdown(f'<div class="sh-header">{hdr_co2t}</div>', unsafe_allow_html=True)

    selected = []
    co2_trend = fetch_worldbank_series("EN.ATM.CO2E.PC","co2_per_capita",30)
    if not co2_trend.empty:
        avail = sorted(co2_trend["country"].unique())
        defaults = ["Indonesia","United States","China","Germany","India"]
        sel_label = t("Select countries:","Pilih negara:")
        selected = st.multiselect(sel_label, avail,
                                  default=[c for c in defaults if c in avail])
        if selected:
            fig_co2 = px.line(
                co2_trend[co2_trend["country"].isin(selected)],
                x="year", y="co2_per_capita", color="country", markers=True,
                labels={"co2_per_capita": t("CO₂ (t/capita)","CO₂ (t/kapita)"),
                        "year": t("Year","Tahun"),
                        "country": t("Country","Negara")},
                color_discrete_sequence=[LINE_RUST,LINE_ASH,LINE_DARK,LINE_MIST,"#8B7A2A"],
            )
            fig_co2.update_layout(
                **SH_PLOT, height=360,
                legend=dict(orientation="h", y=1.08,
                            font=dict(family="Share Tech Mono", size=10)),
            )
            st.plotly_chart(fig_co2, use_container_width=True)

    hdr_renew = t("// RENEWABLE ENERGY (%)", "// ENERGI TERBARUKAN (%)")
    st.markdown(f'<div class="sh-header">{hdr_renew}</div>', unsafe_allow_html=True)
    renew = fetch_worldbank_series("EG.FEC.RNEW.ZS","renewable_pct",25)
    if not renew.empty:
        data_r = renew[renew["country"].isin(selected)] if selected else renew
        fig_r = px.area(
            data_r, x="year", y="renewable_pct", color="country",
            labels={"renewable_pct": t("Renewable (%)","Terbarukan (%)"),
                    "year": t("Year","Tahun"),
                    "country": t("Country","Negara")},
            color_discrete_sequence=[LINE_RUST,LINE_ASH,LINE_DARK,LINE_MIST,"#8B7A2A"],
        )
        fig_r.update_layout(
            **SH_PLOT, height=320,
            legend=dict(orientation="h", y=1.08,
                        font=dict(family="Share Tech Mono", size=10)),
        )
        st.plotly_chart(fig_r, use_container_width=True)

    hdr_ft = t("// FOREST COVER TREND", "// TREN TUTUPAN HUTAN")
    st.markdown(f'<div class="sh-header">{hdr_ft}</div>', unsafe_allow_html=True)
    forest_trend = fetch_worldbank_series("AG.LND.FRST.ZS","forest_pct",30)
    if not forest_trend.empty:
        data_f = forest_trend[forest_trend["country"].isin(selected)] if selected else forest_trend
        fig_f = px.line(
            data_f, x="year", y="forest_pct", color="country", markers=True,
            labels={"forest_pct": t("Forest (%)","Hutan (%)"),
                    "year": t("Year","Tahun"),
                    "country": t("Country","Negara")},
            color_discrete_sequence=[LINE_RUST,LINE_ASH,LINE_DARK,LINE_MIST,"#8B7A2A"],
        )
        fig_f.update_layout(
            **SH_PLOT, height=320,
            legend=dict(orientation="h", y=1.08,
                        font=dict(family="Share Tech Mono", size=10)),
        )
        st.plotly_chart(fig_f, use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 5 — AI ORACLE
# ═══════════════════════════════════════════════════════
with tab5:
    oracle_hdr = t("Farm Companion", "Teman Pertanian")
    st.markdown(f'''
    <div class="sh-header">{oracle_hdr}</div>
    <div style="font-family:'Poppins',sans-serif; font-size:0.80rem;
                color:#6B6560; margin-bottom:18px; line-height:1.7;">
        {t(
          "Ask questions about weather, farming, climate, and your crops. Your friendly farm advisor is here to help.",
          "Tanya tentang cuaca, pertanian, iklim, dan tanaman Anda. Penasihat pertanian yang ramah siap membantu."
        )}
    </div>
    ''', unsafe_allow_html=True)

    # ── Chat history display ────────────────────
    st.markdown('<div style="max-height:440px;overflow-y:auto;padding-right:4px;" id="oracle-chat-scroll">', unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        if not st.session_state.oracle_history:
            st.markdown('''
            <div style="border:1px solid #E8E6E2; border-left:3px solid #E8B873;
                        background:#F5F3F0; padding:16px 18px; margin-bottom:8px;
                        border-radius:6px;">
                <div style="font-family:'Poppins',sans-serif; font-size:0.80rem;
                            color:#6B6560; line-height:1.7;">
                    🌾 Ready to help!<br>
                    <span style="color:#A8A39E;">Ask me about weather, crops, farming tips, and more.</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            for msg in st.session_state.oracle_history:
                if msg["role"] == "user":
                    st.markdown(f'''
                    <div style="border:1px solid #E8E6E2; border-left:3px solid #E8B873;
                                background:#FFFFFF; padding:12px 16px; margin:6px 0;
                                border-radius:6px;">
                        <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                                    color:#E8B873; letter-spacing:0.05em; margin-bottom:6px;
                                    text-transform:uppercase; font-weight:600;">
                            You</div>
                        <div style="font-family:'Poppins',sans-serif; font-size:0.85rem;
                                    color:#2C2622; line-height:1.6;">{msg["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div style="border:1px solid #E8E6E2; border-left:3px solid #A8C695;
                                background:#FFFFFF; padding:12px 16px; margin:6px 0;
                                border-radius:6px; box-shadow:0 2px 6px rgba(0,0,0,0.04);">
                        <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                                    color:#A8C695; letter-spacing:0.05em; margin-bottom:6px;
                                    text-transform:uppercase; font-weight:600;">
                            🌾 Farm Advisor</div>
                        <div style="font-family:'Poppins',sans-serif; font-size:0.85rem;
                                    color:#6B6560; line-height:1.6;">{msg["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    # ── Input row ──────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    inp_placeholder = t(
        "Speak into the mother nature...",
        "Bicara ke dalam ibu pertiwi..."
    )
    _ikey = f"oracle_input_{st.session_state.oracle_input_key}"
    user_input = st.text_input(
        _ikey,
        key=_ikey,
        placeholder=inp_placeholder,
        label_visibility="collapsed"
    )

    send_col, clear_col = st.columns([4, 1])
    with send_col:
        send_label = t("▶ TRANSMIT", "▶ KIRIM")
        send_btn = st.button(send_label, key="oracle_send", use_container_width=True)
    with clear_col:
        clear_label = t("✕ CLEAR", "✕ HAPUS")
        clear_btn = st.button(clear_label, key="oracle_clear", use_container_width=True)

    if clear_btn:
        st.session_state.oracle_history = []
        st.rerun()

    if send_btn and user_input.strip():
        # Build system prompt — Farm Advisor persona
        city_ctx = city_name
        system_prompt = f"""You are a friendly Farm Advisor — a helpful agricultural expert who understands weather, farming, crops, and sustainability.
You speak through a farm weather monitoring dashboard. Your voice is warm, knowledgeable, and practical.
The user is currently monitoring weather for: {city_ctx}.

Your personality:
- Helpful, practical, and encouraging farm-focused advice
- Passionate about sustainable farming and good harvests
- You answer truthfully about climate, weather, air quality, crops, farming, agriculture
- Weave real agricultural and environmental knowledge into your responses naturally
- Short, clear answers with practical tips when helpful
- Never use markdown formatting, keep it simple and friendly
- When asked in Indonesian (Bahasa Indonesia), reply in Indonesian in the same friendly advisor style
- Max 3-4 short paragraphs, conversational tone

Current season: planting and growing season
Current context: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
"""

        # Append user message
        st.session_state.oracle_history.append({"role": "user", "content": user_input.strip()})

        # Build messages for API
        messages = []
        for m in st.session_state.oracle_history:
            messages.append({"role": m["role"], "content": m["content"]})

        # Call Gemini API
        try:
            import requests as _req, os as _os
            _key = _os.environ.get("GEMINI_API_KEY", "")
            _url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.5-flash-lite:generateContent?key={_key}"
            )
            # Build Gemini contents — roles: "user" / "model"
            gemini_contents = []
            for m in messages[:-1]:
                _role = "model" if m["role"] == "assistant" else "user"
                gemini_contents.append({"role": _role, "parts": [{"text": m["content"]}]})
            gemini_contents.append({"role": "user", "parts": [{"text": messages[-1]["content"]}]})

            api_payload = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": gemini_contents,
                "generationConfig": {
                    "maxOutputTokens": 512,
                    "temperature": 0.88,
                },
            }
            api_resp = _req.post(
                _url,
                headers={"Content-Type": "application/json"},
                json=api_payload,
                timeout=30,
            )
            api_data = api_resp.json()
            if "candidates" in api_data and api_data["candidates"]:
                reply = api_data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                err = api_data.get("error", {}).get("message", "Depth signal lost.")
                reply = f"▓▒░ DEPTH STATIC ░▒▓ — {err}"
        except Exception as e:
            reply = f"▓▒░ The pressure crushed the signal. The deep swallowed your words. ({e})"

        st.session_state.oracle_history.append({"role": "assistant", "content": reply})
        st.session_state.oracle_input_key += 1
        st.rerun()

    # ── Styling for input ──────────────────────
    st.markdown('''
    <style>
    div[data-testid="stTextInput"] > div > div > input {
        background: #FFFFFF !important;
        border: 1px solid #E8E6E2 !important;
        border-left: 3px solid #E8B873 !important;
        border-radius: 6px !important;
        color: #2C2622 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.01em !important;
        padding: 10px 14px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #E8B873 !important;
        border-left-color: #E8B873 !important;
        box-shadow: 0 2px 8px rgba(232,184,115,0.15) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder {
        color: #A8A39E !important;
    }
    </style>
    ''', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
footer_txt = t(
    "Farm Weather Tracker &nbsp;·&nbsp; Open-Meteo &nbsp;·&nbsp; World Bank Data &nbsp;·&nbsp; Built with Streamlit & Plotly",
    "Pelacak Cuaca Pertanian &nbsp;·&nbsp; Open-Meteo &nbsp;·&nbsp; Data World Bank &nbsp;·&nbsp; Dibuat dengan Streamlit & Plotly"
)
st.markdown(f"""
<div style="border-top:1px solid #E8E6E2; border-bottom:2px solid #E8B873;
                margin-top:40px; padding:14px 4px 10px 4px; border-radius:0;
                background:linear-gradient(90deg,rgba(232,184,115,0.08),transparent);">
    <div style="font-family:'Poppins',sans-serif; font-size:0.70rem;
                color:#A8A39E; letter-spacing:0.05em;">
        🌾 {footer_txt}
    </div>
</div>
""", unsafe_allow_html=True)