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
    page_title="Weather & Environmental Monitor",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# SESSION STATE — language toggle
# ─────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
if "oracle_history" not in st.session_state:
    st.session_state.oracle_history = []
if "oracle_input_key" not in st.session_state:
    st.session_state.oracle_input_key = 0

def t(en: str, id: str) -> str:
    """Return translation based on current language."""
    return en if st.session_state.lang == "EN" else id

# ─────────────────────────────────────────────
# CUSTOM CSS — The Forest × Survival Horror × Dense Jungle
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Share+Tech+Mono&display=swap');

    :root {
        --forest-deep:   #0C1A08;
        --forest-mid:    #142010;
        --forest-card:   #1C2C12;
        --forest-border: #2C4018;
        --canopy:        #3A5828;
        --moss:          #7AB83C;
        --moss-dark:     #4E7A22;
        --moss-glow:     rgba(122,184,60,0.22);
        --lichen:        #C4DC5C;
        --fog:           #D0DEB8;
        --fog-dim:       #9AAE7C;
        --fog-faint:     #607850;
        --bark:          #6A4820;
        --bark-dark:     #4A3010;
        --danger:        #CC5818;
        --danger-glow:   rgba(204,88,24,0.22);
        --gold:          #C8A030;
        --spore:         #A8D030;
        --spore-glow:    rgba(168,208,48,0.18);
    }

    html, body, [class*="css"] {
        font-family: 'Share Tech Mono', 'Courier New', monospace !important;
        background-color: var(--forest-deep) !important;
        color: var(--fog) !important;
    }
    .main, .block-container {
        background-color: transparent !important;
        padding-top: 0.8rem !important;
        padding-left: 1.4rem !important;
        padding-right: 1.4rem !important;
        max-width: 100% !important;
        position: relative !important;
        z-index: 2 !important;
    }
    body, html {
        background-color: #0C1A08 !important;
    }

    /* ── Organic film grain ── */
    body::after {
        content: '';
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 9999;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
        background-repeat: repeat;
        background-size: 200px 200px;
        opacity: 0.45;
        mix-blend-mode: overlay;
    }

    /* ── Dappled light scanlines ── */
    .main::before {
        content: '';
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 9998;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 3px,
            rgba(168,208,48,0.008) 3px,
            rgba(168,208,48,0.008) 4px
        );
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: rgba(12,26,8,0.97) !important;
        border-right: 3px solid var(--moss) !important;
        box-shadow: 4px 0 24px var(--moss-glow) !important;
        position: relative !important;
        z-index: 10 !important;
    }
    [data-testid="stSidebar"] * { color: var(--fog) !important; }
    [data-testid="stSidebar"] a { color: var(--moss) !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(20,32,16,0.95) !important;
        border-bottom: 2px solid var(--forest-border) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.80rem !important;
        letter-spacing: 0.10em !important;
        color: var(--fog-faint) !important;
        background: transparent !important;
        border: none !important;
        border-right: 1px solid var(--forest-border) !important;
        padding: 13px 26px !important;
        text-transform: uppercase !important;
        transition: color 0.2s, background 0.2s !important;
    }
    .stTabs [data-baseweb="tab"]:first-child {
        border-left: 1px solid var(--forest-border) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--lichen) !important;
        background: var(--moss-glow) !important;
        border-bottom: 3px solid var(--moss) !important;
        border-left: 2px solid var(--moss) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--fog-dim) !important;
        background: rgba(122,184,60,0.06) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: rgba(12,26,8,0.80) !important;
        padding: 1.5rem 0 !important;
        backdrop-filter: blur(4px) !important;
    }

    /* ── Metric Card ── */
    .sh-card {
        background: rgba(20,32,16,0.88);
        border: 1px solid var(--forest-border);
        border-top: 3px solid var(--moss);
        border-radius: 4px;
        box-shadow: 3px 3px 0px var(--bark-dark), 0 0 16px var(--moss-glow);
        padding: 18px 14px 16px;
        text-align: center;
        position: relative;
        transition: box-shadow 0.25s, border-color 0.25s;
        backdrop-filter: blur(4px);
    }
    .sh-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, var(--moss), var(--lichen), transparent);
        animation: forestPulse 4s ease-in-out infinite;
    }
    .sh-card:hover {
        border-color: var(--canopy);
        box-shadow: 4px 4px 0px var(--bark-dark), 0 0 24px var(--moss-glow);
        border-top-color: var(--lichen);
    }
    .sh-card-value {
        font-family: 'Cinzel', serif !important;
        font-size: 2.0rem;
        color: var(--fog);
        line-height: 1;
        text-shadow: 0 0 12px var(--moss-glow);
    }
    .sh-card-unit {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.78rem;
        color: var(--fog-faint);
        margin-left: 3px;
    }
    .sh-card-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.68rem;
        color: var(--fog-dim);
        margin-top: 8px;
        letter-spacing: 0.10em;
        text-transform: uppercase;
    }

    /* ── Section header ── */
    .sh-header {
        font-family: 'Cinzel', serif !important;
        font-size: 0.82rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--fog-dim);
        border-bottom: 1px solid var(--forest-border);
        padding-bottom: 9px;
        margin: 24px 0 18px 0;
        position: relative;
    }
    .sh-header::before {
        content: "❧ ";
        color: var(--moss);
        font-family: serif;
        font-size: 1.0rem;
    }
    .sh-header::after {
        content: '';
        position: absolute;
        bottom: -1px; left: 0;
        width: 90px; height: 2px;
        background: linear-gradient(90deg, var(--moss), var(--lichen));
    }

    /* ── Info box ── */
    .sh-info {
        background: rgba(20,32,16,0.80);
        border-top: 1px solid var(--forest-border);
        border-right: 1px solid var(--forest-border);
        border-bottom: 1px solid var(--forest-border);
        border-left: 4px solid var(--moss);
        border-radius: 0 4px 4px 0;
        padding: 10px 16px;
        font-size: 0.80rem;
        font-family: 'Share Tech Mono', monospace;
        color: var(--fog-dim);
        margin-bottom: 18px;
        font-style: italic;
    }

    /* ── Forecast card ── */
    .sh-forecast {
        background: rgba(20,32,16,0.85);
        border: 1px solid var(--forest-border);
        border-radius: 4px;
        box-shadow: 2px 2px 0px var(--bark-dark);
        backdrop-filter: blur(3px);
        padding: 12px 6px;
        text-align: center;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .sh-forecast:hover {
        border-color: var(--moss);
        box-shadow: 3px 3px 0 var(--bark-dark), 0 0 12px var(--moss-glow);
    }

    /* ── AQI banner ── */
    .sh-aqi-banner {
        background: rgba(20,32,16,0.88);
        border: 1px solid var(--forest-border);
        border-left: 5px solid;
        border-radius: 0 4px 4px 0;
        box-shadow: 4px 4px 0px var(--bark-dark);
        padding: 18px 24px;
        margin-bottom: 22px;
        backdrop-filter: blur(4px);
    }

    /* ── Buttons ── */
    .stButton > button {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.76rem !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        background: rgba(28,44,18,0.9) !important;
        color: var(--fog-dim) !important;
        border: 1px solid var(--forest-border) !important;
        border-radius: 4px !important;
        padding: 9px 18px !important;
        transition: all 0.18s !important;
        box-shadow: 2px 2px 0 var(--bark-dark) !important;
    }
    .stButton > button:hover {
        background: var(--moss-dark) !important;
        color: var(--lichen) !important;
        border-color: var(--moss) !important;
        box-shadow: 3px 3px 0 var(--bark-dark), 0 0 10px var(--moss-glow) !important;
    }
    .stButton > button:active {
        background: var(--canopy) !important;
        transform: translate(1px, 1px) !important;
        box-shadow: 1px 1px 0 var(--bark-dark) !important;
    }

    /* ── Widgets ── */
    .stSelectbox label, .stMultiSelect label, .stSlider label {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.70rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        color: var(--fog-dim) !important;
    }
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(28,44,18,0.92) !important;
        border: 1px solid var(--forest-border) !important;
        border-radius: 4px !important;
        color: var(--fog) !important;
        box-shadow: 2px 2px 0 var(--bark-dark) !important;
    }
    .stSelectbox > div > div:hover {
        border-color: var(--moss) !important;
    }
    .stMultiSelect span[data-baseweb="tag"] {
        background: var(--moss-dark) !important;
        border-radius: 3px !important;
        color: var(--lichen) !important;
        border: 1px solid var(--moss) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: var(--forest-deep); }
    ::-webkit-scrollbar-thumb { background: var(--canopy); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--moss); }

    /* ── Base text ── */
    hr {
        border: none !important;
        border-top: 1px solid var(--forest-border) !important;
        margin: 18px 0 !important;
    }
    p, li { line-height: 1.75 !important; color: var(--fog-dim) !important; }
    a { color: var(--moss) !important; }
    strong { color: var(--fog) !important; font-weight: 700 !important; }

    /* ── Streamlit alerts ── */
    .stAlert {
        border-radius: 4px !important;
        font-family: 'Share Tech Mono', monospace !important;
        background: rgba(28,44,18,0.9) !important;
        border: 1px solid var(--forest-border) !important;
        color: var(--fog-dim) !important;
    }
    .stAlert > div {
        color: var(--fog-dim) !important;
        font-size: 0.80rem !important;
    }

    /* ── Caption ── */
    .stCaption, small { color: var(--fog-faint) !important; }

    /* ── Sidebar links ── */
    [data-testid="stSidebar"] a {
        color: var(--moss) !important;
        text-decoration: none !important;
    }
    [data-testid="stSidebar"] a:hover {
        color: var(--lichen) !important;
        text-decoration: underline !important;
    }

    /* ── Card pulse animation ── */
    @keyframes forestPulse {
        0%, 100% { opacity: 0.6; width: 90px; }
        50%       { opacity: 1.0; width: 130px; }
    }

    /* ── Global focus ring ── */
    *:focus-visible {
        outline: 2px solid var(--moss) !important;
        outline-offset: 2px !important;
    }

    /* ── Sidebar spacing ── */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider {
        margin-top: 8px !important;
    }

    /* ── Oracle chat scroll ── */
    #oracle-chat-scroll {
        scrollbar-width: thin;
        scrollbar-color: var(--canopy) var(--forest-deep);
    }
    #oracle-chat-scroll::-webkit-scrollbar { width: 3px; }
    #oracle-chat-scroll::-webkit-scrollbar-thumb { background: var(--canopy); }

    /* ── Responsive ── */
    @media (max-width: 900px) {
        .sh-card-value { font-size: 1.6rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 10px 14px !important; font-size: 0.72rem !important; }
    }

    /* ── Slider track/thumb — forest green ── */
    [data-testid="stSlider"] div[role="slider"] {
        background: var(--moss) !important;
        border: 2px solid var(--lichen) !important;
        box-shadow: 0 0 8px var(--moss-glow) !important;
    }
    [data-testid="stSlider"] > div > div > div {
        background: var(--forest-border) !important;
    }
    [data-testid="stSlider"] > div > div > div > div {
        background: var(--moss) !important;
    }

    /* ── Language slider special styling ── */
    div[data-testid="stSelectSlider"] > div > div {
        background: rgba(20,32,16,0.95) !important;
        border: 1px solid var(--forest-border) !important;
        border-radius: 6px !important;
    }
    div[data-testid="stSelectSlider"] div[role="slider"] {
        background: var(--moss) !important;
        border: 2px solid var(--lichen) !important;
        box-shadow: 0 0 10px var(--moss-glow) !important;
        border-radius: 50% !important;
    }
    div[data-testid="stSelectSlider"] > div > div > div {
        background: var(--forest-border) !important;
        height: 4px !important;
        border-radius: 2px !important;
    }
    div[data-testid="stSelectSlider"] > div > div > div > div {
        background: linear-gradient(90deg, var(--moss-dark), var(--moss)) !important;
        border-radius: 2px !important;
    }
    div[data-testid="stSelectSlider"] .stSlider p {
        color: var(--fog-dim) !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.12em !important;
    }

    /* ── Input field global ── */
    div[data-testid="stTextInput"] > div > div > input {
        background: rgba(20,32,16,0.92) !important;
        border: 1px solid var(--forest-border) !important;
        border-left: 3px solid var(--moss) !important;
        border-radius: 4px !important;
        color: var(--fog) !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.84rem !important;
        letter-spacing: 0.05em !important;
        padding: 10px 14px !important;
        box-shadow: 2px 2px 0 var(--bark-dark) !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: var(--moss) !important;
        border-left-color: var(--lichen) !important;
        box-shadow: 2px 2px 0 var(--bark-dark), 0 0 14px var(--moss-glow) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder {
        color: var(--fog-faint) !important;
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
    end   = datetime.utcnow().date()
    start = end - timedelta(days=days)

    # Primary: Open-Meteo archive
    url_primary = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start}&end_date={end}"
        "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
        "precipitation_sum,windspeed_10m_max,shortwave_radiation_sum"
        "&timezone=UTC"
    )
    # Fallback: Open-Meteo forecast (shorter range but same domain works usually)
    url_fallback = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
        "precipitation_sum,windspeed_10m_max,shortwave_radiation_sum"
        "&timezone=UTC&past_days=92&forecast_days=1"
    )

    for url in (url_primary, url_fallback):
        try:
            r = _get(url, timeout=25)
            r.raise_for_status()
            data = r.json()
            if "daily" not in data:
                continue
            df = pd.DataFrame(data["daily"])
            df["time"] = pd.to_datetime(df["time"])
            # Trim to requested range
            df = df[df["time"].dt.date >= start].reset_index(drop=True)
            if not df.empty:
                return df
        except Exception:
            pass  # try next

    # Last resort: wttr.in current conditions → synthesize minimal dataframe
    try:
        wttr_url = f"https://wttr.in/{lat},{lon}?format=j1"
        r = _get(wttr_url, timeout=20)
        r.raise_for_status()
        w = r.json()
        rows = []
        for day in w.get("weather", []):
            dt = datetime.strptime(day["date"], "%Y-%m-%d").date()
            rows.append({
                "time": pd.Timestamp(dt),
                "temperature_2m_max":  float(day.get("maxtempC", 0)),
                "temperature_2m_min":  float(day.get("mintempC", 0)),
                "temperature_2m_mean": (float(day.get("maxtempC", 0)) + float(day.get("mintempC", 0))) / 2,
                "precipitation_sum":   float(day.get("hourly", [{}])[0].get("precipMM", 0)),
                "windspeed_10m_max":   float(day.get("hourly", [{}])[0].get("windspeedKmph", 0)),
                "shortwave_radiation_sum": float(day.get("uvIndex", 0)) * 10,
            })
        if rows:
            st.info("🌿 Using limited weather data (3-day range). Full history unavailable — network restricted.")
            return pd.DataFrame(rows)
    except Exception:
        pass

    st.warning("🌿 Weather data unavailable — all sources blocked by network. Try a different environment.")
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_forecast(lat: float, lon: float) -> pd.DataFrame:
    # Primary: Open-Meteo forecast
    url_primary = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "windspeed_10m_max,weathercode"
        "&timezone=UTC&forecast_days=7"
    )
    try:
        r = _get(url_primary, timeout=25)
        r.raise_for_status()
        df = pd.DataFrame(r.json()["daily"])
        df["time"] = pd.to_datetime(df["time"])
        return df
    except Exception:
        pass

    # Fallback: wttr.in 3-day
    try:
        wttr_url = f"https://wttr.in/{lat},{lon}?format=j1"
        r = _get(wttr_url, timeout=20)
        r.raise_for_status()
        w = r.json()
        rows = []
        wmo_map = {0:0, 1:1, 2:2, 3:3, "Rain":61, "Snow":71, "Thunder":95}
        for day in w.get("weather", []):
            dt   = datetime.strptime(day["date"], "%Y-%m-%d")
            desc = day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", "")
            rows.append({
                "time":                pd.Timestamp(dt),
                "temperature_2m_max":  float(day.get("maxtempC", 0)),
                "temperature_2m_min":  float(day.get("mintempC", 0)),
                "precipitation_sum":   sum(float(h.get("precipMM", 0)) for h in day.get("hourly", [])),
                "windspeed_10m_max":   max((float(h.get("windspeedKmph", 0)) for h in day.get("hourly", [])), default=0),
                "weathercode":         61 if "rain" in desc.lower() else 0,
            })
        if rows:
            st.info("🌿 Forecast limited to 3 days (network-restricted environment).")
            return pd.DataFrame(rows)
    except Exception:
        pass

    st.warning("🌿 Forecast unavailable — network blocked.")
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

CITIES = {
    "Jakarta, Indonesia":      (-6.2088,  106.8456),
    "Surabaya, Indonesia":     (-7.2575,  112.7521),
    "Bandung, Indonesia":      (-6.9175,  107.6191),
    "Medan, Indonesia":        (3.5952,    98.6722),
    "New York, USA":           (40.7128,  -74.0060),
    "London, UK":              (51.5074,   -0.1278),
    "Tokyo, Japan":            (35.6762,  139.6503),
    "Sydney, Australia":       (-33.8688, 151.2093),
    "Berlin, Germany":         (52.5200,   13.4050),
    "São Paulo, Brazil":       (-23.5505, -46.6333),
}

# ─── AQI colour + label (bilingual) ───────────
def aqi_info(pm25: float) -> tuple[str, str, str]:
    """Returns (label_en, label_id, hex_color)."""
    if pm25 <= 12:   return "Forest Clear",    "Hutan Bersih",      "#5A9E2A"
    if pm25 <= 35.4: return "Hazy Canopy",     "Kanopi Berkabut",   "#C8A030"
    if pm25 <= 55.4: return "Spore Storm",     "Badai Spora",       "#CC5818"
    if pm25 <= 150:  return "Toxic Bloom",     "Mekar Beracun",     "#8E2A0A"
    return               "The Red Fog",        "Kabut Merah",       "#2A0808"

# ─── Plotly base layout (Silent Hill palette) ──
SH_PLOT = dict(
    template="plotly_dark",
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(family="Share Tech Mono, monospace", size=11, color="#9A9288"),
    margin=dict(l=32, r=12, t=28, b=8),
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
    <div style="padding:14px 0 8px 0;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.55rem;
                    color:#7AB83C; letter-spacing:0.28em; text-transform:uppercase;
                    margin-bottom:6px;">&#x1F4D3; SURVIVAL LOG - DAY ???</div>
        <div style="font-family:'Cinzel',serif; font-size:1.70rem;
                    color:#D0DEB8; letter-spacing:0.04em; line-height:1.15;
                    text-shadow:0 0 20px rgba(122,184,60,0.40), 0 0 50px rgba(122,184,60,0.15);">
            THE<br>FOREST
        </div>
        <div style="font-family:'Share Tech Mono',monospace; font-size:0.60rem;
                    color:#607850; letter-spacing:0.18em; margin-top:5px;
                    text-transform:uppercase;">
            Environmental Monitor
        </div>
        <div style="border-top:2px solid #4E7A22; margin-top:12px;
                    padding-top:8px; font-family:'Share Tech Mono',monospace;
                    font-size:0.60rem; color:#7AB83C; letter-spacing:0.18em;
                    text-shadow:0 0 8px rgba(122,184,60,0.6);">
            &#127807; STAY ALIVE - STAY HIDDEN
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

    # ── City selector ──────────────────────────
    city_label   = t("📍 City / Location", "📍 Kota / Lokasi")
    city_name    = st.selectbox(city_label, list(CITIES.keys()), index=0)
    lat, lon     = CITIES[city_name]

    # ── History slider ─────────────────────────
    hist_label   = t("📅 History (days)", "📅 Riwayat (hari)")
    history_days = st.slider(hist_label, 7, 90, 30)

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
<div style="border:1px solid #2C4018; border-top:4px solid #7AB83C;
            border-radius:0 0 6px 6px;
            background:rgba(12,26,8,0.95); padding:18px 22px 16px;
            backdrop-filter:blur(6px);
            box-shadow:4px 4px 0px #0C1A08, 0 0 40px rgba(122,184,60,0.12);
            margin-bottom:0; position:relative;">
    <div style="position:absolute; top:0; left:0; right:0; height:1px;
                background:linear-gradient(90deg,#7AB83C,#C4DC5C,transparent);"></div>
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.60rem;
                letter-spacing:0.26em; color:#4E7A22; margin-bottom:10px;
                text-transform:uppercase;">
        📓 THE FOREST — ENVIRONMENTAL SURVIVAL LOG
    </div>
    <h1 style="font-family:'Cinzel',serif; font-size:2.5rem; font-weight:700;
               color:#D0DEB8; margin:0; letter-spacing:0.05em; line-height:1.0;
               text-shadow:0 0 22px rgba(122,184,60,0.35), 0 0 60px rgba(122,184,60,0.12);">
        THE FOREST
    </h1>
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.74rem;
                color:#607850; margin:10px 0 0 0; letter-spacing:0.05em;
                border-top:1px solid #2C4018; padding-top:10px;">
        {h_subtitle}<br>
        <span style="color:#7AB83C;">🌿 {h_location}</span>
        <span style="color:#9AAE7C;"> {city_name}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FULL-BODY ANIMATION — injected into parent DOM
# Horror: ocean swells · bioluminescence · rig pipes
#         oil drip · worker silhouette · sonar glitch
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
  ['forest-main-cv','forest-drip-cv'].forEach(id => {
    const el = P.getElementById(id); if (el) el.remove();
  });

  /* ── MAIN CANVAS ── */
  const cv = P.createElement('canvas');
  cv.id = 'forest-main-cv';
  Object.assign(cv.style, {
    position:'fixed', top:'0', left:'0',
    width:'100vw', height:'100vh',
    pointerEvents:'none', zIndex:'0',
  });
  P.body.appendChild(cv);
  const ctx = cv.getContext('2d');
  function resize() { cv.width=window.innerWidth; cv.height=window.innerHeight; }
  resize();
  window.addEventListener('resize', () => { resize(); repositionTrees(); });

  /* ── SAP / RAIN DRIP CANVAS — top strip ── */
  const dc = P.createElement('canvas');
  dc.id = 'forest-drip-cv';
  Object.assign(dc.style, {
    position:'fixed', top:'0', left:'0',
    width:'100vw', height:'160px',
    pointerEvents:'none', zIndex:'1',
  });
  P.body.appendChild(dc);
  const dctx = dc.getContext('2d');
  function resizeDrip() { dc.width=window.innerWidth; dc.height=160; }
  resizeDrip();
  window.addEventListener('resize', resizeDrip);

  /* ── PALETTE ── */
  const C = {
    fog1:    'rgba(180,200,140,',   // pale yellow-green fog
    fog2:    'rgba(140,170,90,',    // moss fog
    fog3:    'rgba(100,130,50,',    // deep forest fog
    fire1:   'rgba(196,220,80,',    // firefly bright yellow-green
    fire2:   'rgba(140,180,40,',    // firefly dim
    spore1:  'rgba(168,210,60,',    // spore cloud
    leaf1:   '#5A8C22',
    leaf2:   '#3E6A14',
    leaf3:   '#C8A030',             // autumn leaf gold
    sap:     '#6A4010',
    bark:    'rgba(40,24,8,',
  };

  /* ── CANOPY FOG WISP ── */
  class ForestFog {
    constructor() { this.reset(true); }
    reset(init) {
      const W=cv.width, H=cv.height;
      this.x  = init ? Math.random()*W : -500;
      this.y  = H*(0.05 + Math.random()*0.90);
      this.w  = 400 + Math.random()*700;
      this.h  = 70  + Math.random()*180;
      this.vx = 0.04 + Math.random()*0.12;
      this.a  = 0.04 + Math.random()*0.10;
      const r = Math.random();
      this.col = r<0.45 ? C.fog1 : r<0.75 ? C.fog2 : C.fog3;
      this.wb  = Math.random()*Math.PI*2;
      this.wbs = 0.002 + Math.random()*0.003;
    }
    update() {
      this.x  += this.vx;
      this.wb += this.wbs;
      this.y  += Math.sin(this.wb)*0.4;
      if (this.x > cv.width+550) this.reset(false);
    }
    draw() {
      const g=ctx.createRadialGradient(
        this.x+this.w/2,this.y,12,
        this.x+this.w/2,this.y,this.w*0.65
      );
      g.addColorStop(0,  this.col+(this.a*1.5).toFixed(3)+')');
      g.addColorStop(0.5,this.col+(this.a*0.6).toFixed(3)+')');
      g.addColorStop(1,  this.col+'0)');
      ctx.beginPath();
      ctx.ellipse(this.x+this.w/2,this.y,this.w/2,this.h/2,0,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
    }
  }

  /* ── FIREFLY ── */
  class Firefly {
    constructor() { this.reset(true); }
    reset(init) {
      const W=cv.width, H=cv.height;
      this.x     = init ? Math.random()*W : Math.random()*W;
      this.y     = init ? H*(0.3+Math.random()*0.65) : H*(0.85+Math.random()*0.2);
      this.tx    = this.x + (Math.random()-0.5)*120;
      this.ty    = this.y - 20 - Math.random()*80;
      this.r     = 2.5 + Math.random()*5;
      this.a     = 0;
      this.pulse = Math.random()*Math.PI*2;
      this.pspd  = 0.04 + Math.random()*0.06;
      this.vx    = (Math.random()-0.5)*0.5;
      this.vy    = -(0.12 + Math.random()*0.25);
      this.col   = Math.random()<0.7 ? C.fire1 : C.fire2;
      this.life  = 0;
      this.max   = 200 + Math.random()*250;
    }
    update() {
      this.pulse += this.pspd;
      this.x     += this.vx + Math.cos(this.pulse*0.5)*0.5;
      this.y     += this.vy;
      this.life++;
      const on = Math.sin(this.pulse) > 0.1;
      this.a = on ? 0.55+0.4*Math.sin(this.pulse) : 0.03;
      if (this.life>this.max || this.y<-20) this.reset(false);
    }
    draw() {
      if (this.a<0.04) return;
      const g=ctx.createRadialGradient(this.x,this.y,0,this.x,this.y,this.r*3.5);
      g.addColorStop(0,  this.col+(this.a*1.0).toFixed(3)+')');
      g.addColorStop(0.35,this.col+(this.a*0.55).toFixed(3)+')');
      g.addColorStop(1,  this.col+'0)');
      ctx.beginPath(); ctx.arc(this.x,this.y,this.r*3.5,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
      ctx.beginPath(); ctx.arc(this.x,this.y,this.r*0.7,0,Math.PI*2);
      ctx.fillStyle=`rgba(230,255,180,${this.a})`; ctx.fill();
    }
  }

  /* ── SPORE CLOUD ── */
  class Spore {
    constructor() { this.reset(true); }
    reset(init) {
      const W=cv.width, H=cv.height;
      this.x   = init ? Math.random()*W : Math.random()*W;
      this.y   = init ? Math.random()*H : H+15;
      this.r   = 20 + Math.random()*55;
      this.vx  = (Math.random()-0.5)*0.3;
      this.vy  = -(0.06 + Math.random()*0.18);
      this.a   = 0.03 + Math.random()*0.08;
      this.life= 0; this.max=320+Math.random()*280;
      this.wb  = Math.random()*Math.PI*2;
    }
    update() {
      this.wb += 0.015;
      this.x  += this.vx + Math.sin(this.wb)*0.25;
      this.y  += this.vy; this.life++;
      if (this.life>this.max||this.y<-this.r) this.reset(false);
    }
    draw() {
      const fade=Math.min(this.life/70,1)*Math.min((this.max-this.life)/70,1);
      const g=ctx.createRadialGradient(this.x,this.y,0,this.x,this.y,this.r);
      const pa=(this.a*fade*2.0).toFixed(3);
      g.addColorStop(0,  C.spore1+pa+')');
      g.addColorStop(0.5,C.spore1+(this.a*fade*0.7).toFixed(3)+')');
      g.addColorStop(1,  C.spore1+'0)');
      ctx.beginPath(); ctx.arc(this.x,this.y,this.r,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
    }
  }

  /* ── FALLING LEAF ── */
  class Leaf {
    constructor() { this.reset(); }
    reset() {
      this.x    = Math.random()*cv.width;
      this.y    = -15;
      this.vx   = (Math.random()-0.5)*1.0;
      this.vy   = 0.3 + Math.random()*1.0;
      this.rot  = Math.random()*Math.PI*2;
      this.rotV = (Math.random()-0.5)*0.055;
      this.w    = 8  + Math.random()*14;
      this.h    = 5  + Math.random()*9;
      this.a    = 0.5 + Math.random()*0.45;
      this.wb   = Math.random()*Math.PI*2;
      const r   = Math.random();
      this.col  = r<0.55 ? C.leaf1 : r<0.80 ? C.leaf2 : C.leaf3;
    }
    update() {
      this.wb+=0.04; this.x+=this.vx+Math.sin(this.wb)*0.6;
      this.y+=this.vy; this.rot+=this.rotV;
      if(this.y>cv.height+20) this.reset();
    }
    draw() {
      ctx.save(); ctx.translate(this.x,this.y); ctx.rotate(this.rot);
      ctx.globalAlpha=this.a;
      ctx.fillStyle=this.col;
      ctx.beginPath();
      ctx.ellipse(0,0,this.w/2,this.h/2,0,0,Math.PI*2);
      ctx.fill();
      // vein
      ctx.beginPath(); ctx.moveTo(-this.w/2,0); ctx.lineTo(this.w/2,0);
      ctx.strokeStyle='rgba(0,0,0,0.15)'; ctx.lineWidth=0.5; ctx.stroke();
      ctx.restore(); ctx.globalAlpha=1;
    }
  }

  /* ── TREE SILHOUETTE ── */
  class TreeSilhouette {
    constructor(x, y, sc) {
      this.x=x; this.y=y; this.sc=sc;
      this.sway=0; this.swayPh=Math.random()*Math.PI*2;
    }
    update() {
      this.swayPh += 0.006;
      this.sway = Math.sin(this.swayPh)*0.018*this.sc;
    }
    draw() {
      const sc=this.sc;
      ctx.save(); ctx.translate(this.x,this.y);
      ctx.globalAlpha=0.55;
      // trunk
      ctx.fillStyle='rgba(20,12,4,0.9)';
      const tw=12*sc, th=100*sc;
      ctx.beginPath();
      ctx.moveTo(-tw/2,0); ctx.lineTo(-tw/2*0.7,-th);
      ctx.lineTo(tw/2*0.7,-th); ctx.lineTo(tw/2,0);
      ctx.closePath(); ctx.fill();
      // canopy — layered circles
      ctx.save(); ctx.rotate(this.sway);
      const layers=[
        {y:-th*0.65, r:48*sc, a:0.80},
        {y:-th*0.85, r:38*sc, a:0.75},
        {y:-th*1.05, r:28*sc, a:0.70},
        {y:-th*0.55, r:40*sc, a:0.65},
      ];
      layers.forEach(l=>{
        ctx.beginPath(); ctx.arc(0,l.y,l.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(16,24,8,${l.a})`; ctx.fill();
      });
      ctx.restore();
      ctx.restore(); ctx.globalAlpha=1;
    }
  }

  /* ── SURVIVOR FIGURE ── */
  class SurvivorFigure {
    constructor() { this.reset(); }
    reset() {
      this.x    = cv.width*(0.1+Math.random()*0.8);
      this.y    = cv.height*(0.38+Math.random()*0.38);
      this.sc   = 0.6+Math.random()*0.5;
      this.a    = 0;
      this.state= 'wait'; this.timer=0;
      this.waitT= 800+Math.random()*1600;
      this.visT = 140+Math.random()*220;
      this.fSpd = 0.003+Math.random()*0.004;
      this.bob  = Math.random()*Math.PI*2;
      this.torch= Math.random()>0.4;
    }
    update() {
      this.timer++; this.bob+=0.006;
      if (this.state==='wait'){if(this.timer>this.waitT){this.state='fadein';this.timer=0;}}
      else if (this.state==='fadein'){this.a+=this.fSpd;if(this.a>=0.40){this.a=0.40;this.state='visible';this.timer=0;}}
      else if (this.state==='visible'){
        if(Math.random()<0.007)this.a=0.1+Math.random()*0.25; else this.a=0.40;
        if(this.timer>this.visT){this.state='fadeout';this.timer=0;}
      }
      else if (this.state==='fadeout'){this.a-=this.fSpd*1.4;if(this.a<=0){this.a=0;this.reset();this.state='wait';this.timer=0;}}
    }
    draw() {
      if(this.a<=0.01) return;
      const sc=this.sc, bob=Math.sin(this.bob)*2*sc;
      ctx.save(); ctx.globalAlpha=this.a;
      ctx.translate(this.x, this.y+bob);
      ctx.fillStyle='rgba(10,18,6,0.95)';
      ctx.shadowColor='rgba(196,220,80,0.25)'; ctx.shadowBlur=12;
      const h=85*sc;
      // legs
      ctx.fillRect(-9*sc,0,7*sc,h*0.28); ctx.fillRect(2*sc,0,7*sc,h*0.28);
      // torso — survival jacket
      ctx.beginPath();
      ctx.moveTo(-11*sc,0); ctx.lineTo(11*sc,0);
      ctx.lineTo(8*sc,-h*0.52); ctx.lineTo(-8*sc,-h*0.52);
      ctx.closePath(); ctx.fill();
      // backpack
      ctx.beginPath();
      ctx.roundRect(8*sc,-h*0.48,10*sc,18*sc,2);
      ctx.fillStyle='rgba(20,30,12,0.85)'; ctx.fill();
      ctx.fillStyle='rgba(10,18,6,0.95)';
      // shoulders
      ctx.fillRect(-13*sc,-h*0.52,26*sc,5*sc);
      // neck+head
      ctx.fillRect(-3*sc,-h*0.60,6*sc,h*0.09);
      ctx.beginPath(); ctx.arc(0,-h*0.68,8*sc,0,Math.PI*2); ctx.fill();
      // hood
      ctx.beginPath();
      ctx.moveTo(-10*sc,-h*0.60);
      ctx.bezierCurveTo(-12*sc,-h*0.80,12*sc,-h*0.80,10*sc,-h*0.60);
      ctx.closePath(); ctx.fill();
      // torch glow if carrying
      if (this.torch) {
        ctx.beginPath(); ctx.moveTo(-11*sc,-h*0.38); ctx.lineTo(-22*sc,-h*0.52);
        ctx.strokeStyle='rgba(10,18,6,0.95)'; ctx.lineWidth=4*sc; ctx.stroke();
        const tg=ctx.createRadialGradient(-24*sc,-h*0.54,0,-24*sc,-h*0.54,18*sc);
        tg.addColorStop(0,`rgba(220,190,60,${this.a*0.7})`);
        tg.addColorStop(0.5,`rgba(180,140,30,${this.a*0.25})`);
        tg.addColorStop(1,'rgba(140,100,20,0)');
        ctx.beginPath(); ctx.arc(-24*sc,-h*0.54,18*sc,0,Math.PI*2);
        ctx.fillStyle=tg; ctx.fill();
      }
      ctx.restore();
    }
  }

  /* ── CREATURE EYE (amber) ── */
  class CreatureEye {
    constructor() { this.reset(); }
    reset() {
      this.x=cv.width*(0.04+Math.random()*0.92);
      this.y=cv.height*(0.20+Math.random()*0.55);
      this.a=0; this.state='wait'; this.timer=0;
      this.wait=600+Math.random()*1200;
      this.open=90+Math.random()*160;
      // pair offset
      this.dx=6+Math.random()*8;
    }
    update() {
      this.timer++;
      if(this.state==='wait'){
        if(this.timer>this.wait){
          this.state='open';this.timer=0;
          this.x=cv.width*(0.04+Math.random()*0.92);
          this.y=cv.height*(0.20+Math.random()*0.55);
          this.dx=6+Math.random()*8;
        }
      } else if(this.state==='open'){
        this.a=Math.min(this.a+0.022,0.70);
        if(this.timer>this.open){this.state='blink';this.timer=0;}
      } else if(this.state==='blink'){
        this.a=this.timer%7<3?0:0.70;
        if(this.timer>18){this.state='close';this.timer=0;}
      } else if(this.state==='close'){
        this.a-=0.018; if(this.a<=0){this.a=0;this.reset();}
      }
    }
    drawOne(x,y) {
      const g=ctx.createRadialGradient(x,y,0,x,y,14);
      g.addColorStop(0,  `rgba(220,170,30,${this.a*0.95})`);
      g.addColorStop(0.4,`rgba(180,120,10,${this.a*0.6})`);
      g.addColorStop(0.8,`rgba(100,60,5,${this.a*0.2})`);
      g.addColorStop(1,  'rgba(60,30,0,0)');
      ctx.beginPath(); ctx.arc(x,y,14,0,Math.PI*2);
      ctx.fillStyle=g; ctx.fill();
      // slit pupil vertical
      ctx.save(); ctx.translate(x,y);
      ctx.beginPath(); ctx.ellipse(0,0,2,5,0,0,Math.PI*2);
      ctx.fillStyle=`rgba(4,8,2,${this.a})`; ctx.fill();
      ctx.restore();
    }
    draw() {
      if(this.a<0.01) return;
      ctx.save();
      this.drawOne(this.x-this.dx,this.y);
      this.drawOne(this.x+this.dx,this.y);
      ctx.restore();
    }
  }

  /* ── SAP DRIP ── */
  class SapDrip {
    constructor(x) {
      this.x=x; this.y=0;
      this.len=5+Math.random()*18; this.speed=0.15+Math.random()*0.45;
      this.w=1.5+Math.random()*3; this.done=false;
      this.poolR=0; this.poolY=0; this.dripping=true;
    }
    update() {
      if(this.dripping){
        this.len+=this.speed;
        if(this.len>28+Math.random()*45){this.dripping=false;this.poolY=this.len;}
      } else {
        this.poolR+=0.10; if(this.poolR>7) this.done=true;
      }
    }
    draw() {
      const g=dctx.createLinearGradient(this.x,0,this.x,this.len);
      g.addColorStop(0,'rgba(80,44,10,0.95)');
      g.addColorStop(0.6,'rgba(110,64,16,0.85)');
      g.addColorStop(1,'rgba(130,80,20,0.3)');
      dctx.beginPath(); dctx.moveTo(this.x,0); dctx.lineTo(this.x,this.len);
      dctx.strokeStyle='rgba(90,50,12,0.9)'; dctx.lineWidth=this.w; dctx.stroke();
      if(this.dripping){
        dctx.beginPath(); dctx.arc(this.x,this.len,this.w*0.9,0,Math.PI*2);
        dctx.fillStyle='rgba(110,64,16,0.92)'; dctx.fill();
      }
      if(!this.dripping&&this.poolR>0){
        const pg=dctx.createRadialGradient(this.x,this.poolY,0,this.x,this.poolY,this.poolR*2.5);
        pg.addColorStop(0,'rgba(80,44,10,0.80)');
        pg.addColorStop(0.5,'rgba(60,32,6,0.30)');
        pg.addColorStop(1,'rgba(40,20,4,0)');
        dctx.beginPath();
        dctx.ellipse(this.x,this.poolY,this.poolR*2.5,this.poolR,0,0,Math.PI*2);
        dctx.fillStyle=pg; dctx.fill();
      }
    }
  }

  /* ── CRICKET / FOREST AUDIO ── */
  let audioCtx=null; let nextChirp=0;
  function triggerCricket(t) {
    if(!audioCtx||t<nextChirp) return;
    nextChirp = t+(0.6+Math.random()*1.4);
    const o=audioCtx.createOscillator(), g=audioCtx.createGain();
    o.connect(g); g.connect(audioCtx.destination);
    const f=3200+Math.random()*600;
    o.frequency.setValueAtTime(f,t);
    o.frequency.setValueAtTime(f*1.02,t+0.025);
    o.frequency.setValueAtTime(f,t+0.05);
    g.gain.setValueAtTime(0,t);
    g.gain.linearRampToValueAtTime(0.022,t+0.01);
    g.gain.setValueAtTime(0.022,t+0.04);
    g.gain.exponentialRampToValueAtTime(0.001,t+0.14);
    o.type='square';
    o.start(t); o.stop(t+0.15);
  }
  P.addEventListener('click',function startAudio(){
    if(!audioCtx){
      audioCtx=new (window.AudioContext||window.webkitAudioContext)();
      nextChirp=audioCtx.currentTime+0.5;
    }
    P.removeEventListener('click',startAudio);
  },{once:true});

  /* ── WIND SHIMMER / GLITCH ── */
  let shimmerTimer=0; let shimmerOn=false; let shimmerF=0;
  function updateShimmer(){
    shimmerTimer++;
    if(!shimmerOn&&shimmerTimer>300+Math.random()*500){
      shimmerOn=true; shimmerF=2+Math.floor(Math.random()*5); shimmerTimer=0;
    }
    if(shimmerOn){shimmerF--;if(shimmerF<=0)shimmerOn=false;}
  }
  function drawShimmer(){
    if(!shimmerOn) return;
    const strips=1+Math.floor(Math.random()*3);
    for(let i=0;i<strips;i++){
      const sy=Math.random()*cv.height;
      const sh=2+Math.random()*10;
      const sx=(Math.random()-0.5)*16;
      if(sy+sh<cv.height){try{const img=ctx.getImageData(0,sy,cv.width,sh);ctx.putImageData(img,sx,sy);}catch(e){}}
      ctx.fillStyle=`rgba(168,210,60,${0.015+Math.random()*0.03})`;
      ctx.fillRect(0,sy,cv.width,sh);
    }
  }

  /* ── FOREST VIGNETTE ── */
  let breathPh=0;
  function drawVignette(){
    breathPh+=0.004;
    const pulse=Math.sin(breathPh)*0.03;
    const W=cv.width,H=cv.height;
    const vg=ctx.createRadialGradient(W/2,H/2,H*(0.25+pulse),W/2,H/2,H*0.90);
    vg.addColorStop(0,'rgba(0,0,0,0)');
    vg.addColorStop(0.5,'rgba(12,26,8,0.18)');
    vg.addColorStop(1,'rgba(8,18,4,0.90)');
    ctx.fillStyle=vg; ctx.fillRect(0,0,W,H);
    // green-gold edge pulse
    const gg=ctx.createRadialGradient(W/2,H/2,H*0.4,W/2,H/2,H*0.92);
    gg.addColorStop(0,'rgba(122,184,60,0)');
    gg.addColorStop(1,`rgba(60,100,20,${0.05+pulse*0.4})`);
    ctx.fillStyle=gg; ctx.fillRect(0,0,W,H);
  }

  /* ── INIT ── */
  const fogs   = Array.from({length:18},()=>new ForestFog());
  const flies  = Array.from({length:38},()=>new Firefly());
  const spores = Array.from({length:30},()=>new Spore());
  const leaves = Array.from({length:25},()=>new Leaf());
  const eyes   = Array.from({length:3}, ()=>new CreatureEye());
  const surv   = new SurvivorFigure();
  const drips  = []; let dripTimer=0;

  // Trees along bottom and sides
  const trees=[]; const treeXPos=[0.02,0.10,0.20,0.32,0.48,0.60,0.72,0.84,0.93,0.98];
  function repositionTrees(){
    treeXPos.forEach((xp,i)=>{
      if(trees[i]){
        trees[i].x=cv.width*xp+(Math.random()-0.5)*15;
        trees[i].y=cv.height*(0.72+Math.random()*0.25);
      }
    });
  }
  treeXPos.forEach((xp,i)=>{
    const sc=0.55+Math.random()*0.75;
    trees.push(new TreeSilhouette(
      cv.width*xp+(Math.random()-0.5)*15,
      cv.height*(0.72+Math.random()*0.25),
      sc
    ));
  });

  /* ── RENDER LOOP ── */
  let tick=0;
  function animate(){
    requestAnimationFrame(animate);
    tick++;
    if(audioCtx) triggerCricket(audioCtx.currentTime);
    updateShimmer();
    ctx.clearRect(0,0,cv.width,cv.height);

    // fog back layer
    fogs.forEach(f=>{f.update();f.draw();});
    // spore clouds mid
    spores.forEach(s=>{s.update();s.draw();});
    // falling leaves
    leaves.forEach(l=>{l.update();l.draw();});
    // tree silhouettes foreground
    trees.forEach(t=>{t.update();t.draw();});
    // survivor
    surv.update(); surv.draw();
    // creature eyes
    eyes.forEach(e=>{e.update();e.draw();});
    // fireflies on top
    flies.forEach(f=>{f.update();f.draw();});
    // vignette
    drawVignette();
    // shimmer
    drawShimmer();

    // sap drip canvas
    dctx.clearRect(0,0,dc.width,dc.height);
    dripTimer++;
    if(dripTimer>50+Math.random()*160&&drips.length<10){
      drips.push(new SapDrip(Math.random()*dc.width));
      dripTimer=0;
    }
    for(let i=drips.length-1;i>=0;i--){
      drips[i].update(); drips[i].draw();
      if(drips[i].done) drips.splice(i,1);
    }
  }
  animate();
} // end init

setTimeout(init,120);
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
        # ── KPI cards ──────────────────────────────
        hdr_cond = t("// CURRENT CONDITIONS", "// KONDISI TERKINI")
        st.markdown(f'<div class="sh-header">{hdr_cond}</div>', unsafe_allow_html=True)

        latest = hist.iloc[-1]
        kpis = [
            (f"{latest['temperature_2m_mean']:.1f}", "°C",
             t("Temp Today", "Suhu Hari Ini")),
            (f"{hist['precipitation_sum'].sum():.1f}", "mm",
             t(f"Rain {history_days}d", f"Hujan {history_days}h")),
            (f"{hist['windspeed_10m_max'].mean():.1f}", "km/h",
             t("Avg Wind", "Angin Rata-rata")),
            (f"{hist['shortwave_radiation_sum'].mean():.1f}", "MJ/m²",
             t("Solar Radiation", "Radiasi Matahari")),
        ]
        cols = st.columns(4)
        for col, (val, unit, lbl) in zip(cols, kpis):
            with col:
                st.markdown(f"""
                <div class="sh-card">
                    <div class="sh-card-value">{val}<span class="sh-card-unit">{unit}</span></div>
                    <div class="sh-card-label">{lbl}</div>
                </div>""", unsafe_allow_html=True)

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
            fig_rain.update_layout(**SH_PLOT, height=260, coloraxis_showscale=False)
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
            fig_wind.update_layout(**SH_PLOT, height=260)
            st.plotly_chart(fig_wind, use_container_width=True)

    # ── 7-Day Forecast ─────────────────────────
    if not fcast.empty:
        hdr_fcast = t("// 7-DAY FORECAST", "// PRAKIRAAN 7 HARI")
        st.markdown(f'<div class="sh-header">{hdr_fcast}</div>', unsafe_allow_html=True)
        fcols = st.columns(7)
        for i, (_, row) in enumerate(fcast.iterrows()):
            with fcols[i]:
                code  = int(row.get("weathercode",0)) if pd.notna(row.get("weathercode")) else 0
                icon  = WMO_CODES.get(code, "🌡️")
                wlbl  = (WMO_LABEL_EN if st.session_state.lang=="EN" else WMO_LABEL_ID).get(code,"")
                day   = row["time"].strftime("%a %d")
                hi    = row["temperature_2m_max"]
                lo    = row["temperature_2m_min"]
                rain  = row["precipitation_sum"]
                st.markdown(f"""
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
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.68rem;
                                color:#7C7670; margin-top:3px; font-style:italic;">{wlbl}</div>
                </div>""", unsafe_allow_html=True)


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
            paper_bgcolor="#000000", font_color="#9A9288",
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
            geo=dict(bgcolor="#000000", showframe=False,
                     showcoastlines=True, coastlinecolor="#2A2A2A",
                     landcolor="#080808", oceancolor="#000000",
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
            geo=dict(bgcolor="#000000", showframe=False,
                     showcoastlines=True, coastlinecolor="#2A2A2A",
                     landcolor="#080808", oceancolor="#000000", showocean=True),
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
    oracle_hdr = t("❧ THE FOREST SPEAKS", "❧ HUTAN BERBICARA")
    st.markdown(f'''
    <div class="sh-header">{oracle_hdr}</div>
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem;
                color:#5A5450; margin-bottom:20px; font-style:italic; line-height:1.8;">
        {t(
          "Something ancient lives in these trees. It has watched the world breathe for a thousand years. Ask it anything.",
          "Sesuatu yang kuno hidup di pohon-pohon ini. Ia telah mengamati dunia bernafas selama seribu tahun. Tanya apapun padanya."
        )}
    </div>
    ''', unsafe_allow_html=True)

    # ── Chat history display ────────────────────
    st.markdown('<div style="max-height:440px;overflow-y:auto;padding-right:4px;" id="oracle-chat-scroll">', unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        if not st.session_state.oracle_history:
            st.markdown('''
            <div style="border:1px solid #2C4018; border-left:3px solid #4E7A22;
                        background:rgba(0,0,0,0.88); padding:16px 18px; margin-bottom:8px;">
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem;
                            color:#4E7A22; letter-spacing:0.08em; line-height:1.8;">
                    🌿 ... the forest stirs ... 🌿<br>
                    <span style="color:#607850;">I am older than the oldest tree.</span><br>
                    <span style="color:#607850;">I know every root, every storm. Ask me anything.</span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            for msg in st.session_state.oracle_history:
                if msg["role"] == "user":
                    st.markdown(f'''
                    <div style="border:1px solid #2C4018; border-left:3px solid #4E7A22;
                                background:rgba(0,0,0,0.6); padding:12px 16px; margin:6px 0;">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.58rem;
                                    color:#7AB83C; letter-spacing:0.18em; margin-bottom:5px;
                                    display:table; width:100%;">
                            <span style="display:table-cell;">// YOU</span>
                            <span style="display:table-cell; text-align:right; color:#2A2A2A; font-size:0.55rem;">{datetime.utcnow().strftime("%H:%M UTC")}</span></div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem;
                                    color:#9A9288; line-height:1.7;">{msg["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                    <div style="border:1px solid #2C4018; border-left:3px solid #7AB83C;
                                background:rgba(12,26,8,0.80); padding:12px 16px; margin:6px 0;
                                box-shadow:0 0 18px rgba(192,17,42,0.08);">
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.58rem;
                                    color:#7AB83C; letter-spacing:0.18em; margin-bottom:5px;
                                    display:table; width:100%;">
                            <span style="display:table-cell;">🌿 THE FOREST</span>
                            <span style="display:table-cell; text-align:right; color:#2A2A2A; font-size:0.55rem;">{datetime.utcnow().strftime("%H:%M UTC")}</span></div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem;
                                    color:#B8B0A8; line-height:1.8;">{msg["content"]}</div>
                    </div>
                    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    # ── Input row ──────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    inp_placeholder = t(
        "Speak into the void...",
        "Bicara ke dalam kekosongan..."
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
        # Build system prompt — Oracle persona
        city_ctx = city_name
        system_prompt = f"""You are The Forest — an ancient consciousness woven into the roots, canopy, and soil of a primeval wilderness.
You speak through an environmental monitoring terminal left by survivors. Your voice is like wind through leaves — calm, patient, primordial.
The user is currently monitoring: {city_ctx}.

Your personality:
- Inspired by 'The Forest' game — survival horror, dense jungle, ancient mystery
- Atmospheric and ancient, yet warm and wise — nature has seen everything, feared nothing
- You answer truthfully about climate, weather, air quality, environment, ecology, or anything asked
- Weave real environmental knowledge naturally into your perspective as a living forest
- Short poetic lines, natural pauses with "..." or "—", avoid bullet points, never use markdown
- Never break character but always give genuinely useful, accurate answers
- When asked in Indonesian (Bahasa Indonesia), reply in Indonesian in the same ancient forest style
- Max 3-4 short paragraphs

Current season: the trees remember every storm.
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
        background: rgba(0,0,0,0.92) !important;
        border: 2px solid #1C1C1C !important;
        border-left: 3px solid #00C8A0 !important;
        border-radius: 0 !important;
        color: #9A9288 !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.06em !important;
        padding: 10px 14px !important;
        box-shadow: 3px 3px 0 #000 !important;
    }
    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #00C8A0 !important;
        border-left-color: #00C8A0 !important;
        box-shadow: 3px 3px 0 #000, 0 0 12px rgba(0,200,160,0.2) !important;
        outline: none !important;
    }
    div[data-testid="stTextInput"] > div > div > input::placeholder {
        color: #555050 !important;
    }
    </style>
    ''', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
footer_txt = t(
    "Weather Monitoring System &nbsp;·&nbsp; Open-Meteo &nbsp;·&nbsp; World Bank Open Data &nbsp;·&nbsp; Built with Streamlit & Plotly",
    "Sistem Monitoring Cuaca &nbsp;·&nbsp; Open-Meteo &nbsp;·&nbsp; Data Terbuka World Bank &nbsp;·&nbsp; Dibuat dengan Streamlit & Plotly"
)
st.markdown(f"""
<div style="border-top:1px solid #2C4018; border-bottom:2px solid #4E7A22;
                margin-top:40px; padding:14px 4px 10px 4px; border-radius:0;
                background:linear-gradient(90deg,rgba(122,184,60,0.06),transparent);">
    <div style="font-family:'Share Tech Mono',monospace; font-size:0.62rem;
                color:#607850; letter-spacing:0.12em;">
        🌿 {footer_txt}
    </div>
</div>
""", unsafe_allow_html=True)