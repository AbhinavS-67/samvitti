import streamlit as st
from components.styles import inject_styles
from components.sidebar import render_sidebar
from pages import dashboard, breakouts, breakdowns, sector_heatmap, report, settings

st.set_page_config(
    page_title="Samvitti Capital — Market Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_styles()

page = render_sidebar()

if page == "Dashboard":
    dashboard.render()
elif page == "Breakouts":
    breakouts.render()
elif page == "Breakdowns":
    breakdowns.render()
elif page == "Sector Heatmap":
    sector_heatmap.render()
elif page == "Report & Delivery":
    report.render()
elif page == "Settings":
    settings.render()
