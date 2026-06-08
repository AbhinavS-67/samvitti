import streamlit as st

def clean_html(html_str: str) -> str:
    """Strip leading and trailing whitespace from each line to prevent Streamlit from interpreting HTML as Markdown code blocks."""
    return "\n".join(line.strip() for line in html_str.splitlines())

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');

    /* ─── Base ─── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        background: #080C14;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% 10%, rgba(201,168,76,0.06) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 80% 80%, rgba(45,212,191,0.04) 0%, transparent 50%);
    }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: rgba(12,17,28,0.92) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(201,168,76,0.15) !important;
    }
    [data-testid="stSidebar"] > div {
        padding-top: 0 !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none !important; }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    div[data-testid="stDecoration"] { display: none !important; }

    /* Force the sidebar collapse/expand toggle buttons to remain visible and interactive */
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] * {
        visibility: visible !important;
    }
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #C9A84C !important;
    }
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 1400px !important;
    }

    /* ─── Glass card ─── */
    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(201,168,76,0.25);
    }

    /* ─── KPI metric card ─── */
    .kpi-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        border-radius: 14px 14px 0 0;
    }
    .kpi-card.gold::before { background: linear-gradient(90deg, #C9A84C, #E8C96A); }
    .kpi-card.teal::before { background: linear-gradient(90deg, #2DD4BF, #5EEAD4); }
    .kpi-card.red::before  { background: linear-gradient(90deg, #E05C5C, #F08080); }
    .kpi-card.blue::before { background: linear-gradient(90deg, #60A5FA, #93C5FD); }

    .kpi-label {
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.4);
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        color: #F0EBD8;
        line-height: 1;
    }
    .kpi-delta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        margin-top: 6px;
    }
    .kpi-delta.up   { color: #2DD4BF; }
    .kpi-delta.down { color: #E05C5C; }
    .kpi-delta.neutral { color: rgba(255,255,255,0.35); }

    /* ─── Nav pill tabs ─── */
    .nav-pill-container {
        display: flex;
        gap: 6px;
        padding: 6px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 40px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        width: fit-content;
        margin-bottom: 1.5rem;
    }
    .nav-pill {
        padding: 8px 18px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 500;
        color: rgba(255,255,255,0.45);
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        text-decoration: none;
        white-space: nowrap;
    }
    .nav-pill:hover {
        color: rgba(255,255,255,0.75);
        background: rgba(255,255,255,0.05);
    }
    .nav-pill.active {
        background: rgba(201,168,76,0.15);
        border-color: rgba(201,168,76,0.35);
        color: #C9A84C;
    }

    /* ─── Section header ─── */
    .section-title {
        font-family: 'DM Serif Display', serif;
        font-size: 22px;
        color: #F0EBD8;
        margin: 0 0 4px 0;
    }
    .section-sub {
        font-size: 13px;
        color: rgba(255,255,255,0.35);
        margin: 0 0 1.2rem 0;
    }

    /* ─── Page header ─── */
    .page-header {
        display: flex;
        align-items: baseline;
        gap: 12px;
        margin-bottom: 1.8rem;
    }
    .page-title {
        font-family: 'DM Serif Display', serif;
        font-size: 30px;
        color: #F0EBD8;
        margin: 0;
    }
    .page-badge {
        font-size: 11px;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 20px;
        background: rgba(201,168,76,0.12);
        border: 1px solid rgba(201,168,76,0.25);
        color: #C9A84C;
    }

    /* ─── Signal badge ─── */
    .badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 500;
        padding: 3px 9px;
        border-radius: 20px;
        letter-spacing: 0.04em;
    }
    .badge-bull  { background: rgba(45,212,191,0.12); color: #2DD4BF; border: 1px solid rgba(45,212,191,0.25); }
    .badge-bear  { background: rgba(224,92,92,0.12);  color: #E05C5C; border: 1px solid rgba(224,92,92,0.25); }
    .badge-gold  { background: rgba(201,168,76,0.12); color: #C9A84C; border: 1px solid rgba(201,168,76,0.25); }
    .badge-gray  { background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.45); border: 1px solid rgba(255,255,255,0.1); }

    /* ─── Stock table ─── */
    .stock-table { width: 100%; border-collapse: collapse; }
    .stock-table thead tr {
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }
    .stock-table thead th {
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(255,255,255,0.3);
        padding: 8px 12px;
        text-align: left;
    }
    .stock-table tbody tr {
        border-bottom: 1px solid rgba(255,255,255,0.04);
        transition: background 0.15s ease;
    }
    .stock-table tbody tr:hover {
        background: rgba(201,168,76,0.04);
    }
    .stock-table tbody td {
        padding: 12px 12px;
        font-size: 13px;
        color: rgba(255,255,255,0.75);
        vertical-align: middle;
    }
    .ticker-cell {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 600;
        color: #F0EBD8;
    }
    .mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
    }

    /* ─── Score bar ─── */
    .score-bar-wrap {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .score-bar-bg {
        flex: 1;
        height: 5px;
        background: rgba(255,255,255,0.07);
        border-radius: 10px;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 10px;
    }

    /* ─── Sidebar nav items ─── */
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        margin: 2px 0;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 13.5px;
        font-weight: 450;
        color: rgba(255,255,255,0.45);
        border: 1px solid transparent;
        text-decoration: none;
        width: 100%;
    }
    .sidebar-nav-item:hover {
        background: rgba(255,255,255,0.04);
        color: rgba(255,255,255,0.75);
    }
    .sidebar-nav-item.active {
        background: rgba(201,168,76,0.1);
        border-color: rgba(201,168,76,0.2);
        color: #C9A84C;
    }

    /* ─── Streamlit overrides ─── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: rgba(255,255,255,0.75) !important;
    }
    .stButton > button {
        background: rgba(201,168,76,0.1) !important;
        border: 1px solid rgba(201,168,76,0.3) !important;
        border-radius: 10px !important;
        color: #C9A84C !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 6px 18px !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: rgba(201,168,76,0.2) !important;
        border-color: rgba(201,168,76,0.5) !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #F0EBD8 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.02);
        border-radius: 30px;
        padding: 4px;
        border: 1px solid rgba(255,255,255,0.06);
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 24px !important;
        color: rgba(255,255,255,0.4) !important;
        font-size: 13px !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(201,168,76,0.14) !important;
        border: 1px solid rgba(201,168,76,0.3) !important;
        color: #C9A84C !important;
    }
    [data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; }
    .stDataFrame { background: transparent !important; }
    .stExpander {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
    }
    p, li { color: rgba(255,255,255,0.65); font-size: 14px; }
    h1, h2, h3 { color: #F0EBD8 !important; }
    label { color: rgba(255,255,255,0.5) !important; font-size: 13px !important; }
    .stRadio > label { color: rgba(255,255,255,0.55) !important; }
    .stCheckbox > label { color: rgba(255,255,255,0.55) !important; }
    .stSlider .stSlider { color: #C9A84C !important; }
    [data-testid="stSidebarNav"] { display: none; }
    div[data-testid="column"] > div { height: 100%; }
    </style>
    """, unsafe_allow_html=True)
