import streamlit as st


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Settings</h1>
        <span class="page-badge">Filters & Config</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-title">Data Filters</p><p class="section-sub">Applied globally across all pages</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        min_mktcap = st.select_slider(
            "Minimum Market Cap",
            options=["No limit", "₹500 Cr", "₹1,000 Cr", "₹5,000 Cr", "₹10,000 Cr", "₹50,000 Cr"],
            value="No limit", key="s_mktcap"
        )
        min_vol = st.select_slider(
            "Minimum Avg Daily Volume",
            options=["No limit", "50K", "1L", "5L", "10L", "50L"],
            value="No limit", key="s_vol"
        )
        exclude_sectors = st.multiselect(
            "Exclude sectors",
            ["Energy","IT","Financials","Healthcare","FMCG","Auto","Infra","Metals","Cement","Consumer","Utilities"],
            key="s_exc"
        )
        high_threshold = st.slider("52W High proximity (%)", 0.5, 5.0, 1.5, step=0.5, key="s_hi")
        low_threshold  = st.slider("52W Low proximity (%)", 1.0, 10.0, 5.0, step=0.5, key="s_lo")

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Save Filters", use_container_width=True):
            st.session_state["filters"] = {
                "min_mktcap": min_mktcap,
                "min_vol": min_vol,
                "exclude_sectors": exclude_sectors,
                "high_threshold": high_threshold,
                "low_threshold": low_threshold,
            }
            st.success("Filters saved!")

    with col2:
        st.markdown('<p class="section-title">Branding</p><p class="section-sub">Customise report headers</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fund_name = st.text_input("Fund Name", value="Samvitti Capital", key="s_name")
        tagline   = st.text_input("Tagline", value="Focussed on sustained wealth creation", key="s_tag")
        logo_file = st.file_uploader("Upload logo (PNG/SVG)", type=["png","svg","jpg"], key="s_logo")
        if logo_file:
            st.image(logo_file, width=120)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Cache & Refresh</p>', unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        refresh_interval = st.selectbox("Data refresh interval", ["30 minutes","1 hour","2 hours","Manual only"], key="s_ref")
        if st.button("Clear Cache & Refresh Now", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared. Data will re-fetch on next load.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">About</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="display:flex;flex-direction:column;gap:8px;">
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.35);">Version</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#C9A84C;">v1.0.0</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.35);">Data source</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.55);">Yahoo Finance (yfinance)</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.35);">Markets</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.55);">NSE · BSE · NYSE · NASDAQ</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.35);">Built for</span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.55);">Samvitti Capital Pvt Ltd</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
