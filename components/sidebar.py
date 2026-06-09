import streamlit as st
from datetime import datetime

def render_sidebar():
    with st.sidebar:
        # Logo + brand
        st.markdown("""
        <div style="padding: 1.8rem 0.5rem 1.4rem 0.5rem; border-bottom: 1px solid rgba(201,168,76,0.15); margin-bottom: 1rem;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg,rgba(201,168,76,0.3),rgba(201,168,76,0.1)); border:1px solid rgba(201,168,76,0.4); display:flex; align-items:center; justify-content:center;">
                    <span style="font-family:'DM Serif Display',serif; font-size:16px; color:#C9A84C; font-weight:600;">S</span>
                </div>
                <div>
                    <div style="font-family:'DM Serif Display',serif; font-size:16px; color:#F0EBD8; line-height:1.1;">Samvitti</div>
                    <div style="font-size:9px; letter-spacing:0.18em; text-transform:uppercase; color:rgba(201,168,76,0.6);">Capital</div>
                </div>
            </div>
            <div style="font-size:10px; color:rgba(255,255,255,0.2); letter-spacing:0.05em; margin-top:10px; padding-left:2px;">
                Market Intelligence Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Market status pill
        now = datetime.now()
        hour = now.hour
        is_market_hours = 9 <= hour <= 16
        market_color = "#2DD4BF" if is_market_hours else "#E05C5C"
        market_text = "Market Open" if is_market_hours else "Market Closed"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:7px; padding:8px 12px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); border-radius:10px; margin-bottom:1.2rem;">
            <div style="width:6px; height:6px; border-radius:50%; background:{market_color}; box-shadow:0 0 6px {market_color}55;"></div>
            <span style="font-size:12px; color:rgba(255,255,255,0.5);">{market_text}</span>
            <span style="font-size:11px; color:rgba(255,255,255,0.25); margin-left:auto;">{now.strftime('%H:%M')}</span>
        </div>
        """, unsafe_allow_html=True)

        # Data Scope Selector
        st.markdown('<div style="margin-top:0.2rem; margin-bottom:0.4rem; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.2); padding-left:4px;">Data Scope</div>', unsafe_allow_html=True)
        scope = st.selectbox(
            "Data Scope",
            ["Market Indices", "Custom Search"],
            key="data_scope",
            label_visibility="collapsed"
        )

        if scope == "Market Indices":
            from data.fetcher import INDICES_MAP
            if "active_index" not in st.session_state:
                st.session_state.active_index = "Nifty 50"
            st.markdown('<div style="margin-top:0.2rem; margin-bottom:0.4rem; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.2); padding-left:4px;">Select Index</div>', unsafe_allow_html=True)
            active_index = st.selectbox(
                "Select Index",
                options=list(INDICES_MAP.keys()),
                key="active_index",
                label_visibility="collapsed"
            )
            if active_index == "US (S&P 500)":
                st.session_state["market"] = "US (S&P 500)"
            else:
                st.session_state["market"] = "India (NSE)"
        else:
            st.session_state["market"] = "Both"

        if scope == "Custom Search":
            default_options = [
                "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFOSYS.NS", "SBIN.NS",
                "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA"
            ]
            if "custom_tickers" not in st.session_state:
                st.session_state.custom_tickers = ["RELIANCE.NS", "AAPL", "MSFT", "TCS.NS"]

            with st.form("add_ticker_form", clear_on_submit=True, border=False):
                new_ticker = st.text_input("Add Ticker (e.g. INFY.NS, TSLA)", key="new_ticker_input")
                submitted = st.form_submit_button("Add Stock", use_container_width=True)
                if submitted and new_ticker:
                    clean_ticker = new_ticker.strip().upper()
                    if clean_ticker not in st.session_state.custom_tickers:
                        st.session_state.custom_tickers.append(clean_ticker)
                        st.toast(f"Added {clean_ticker} to custom list!")
                        st.rerun()

            selected_tickers = st.multiselect(
                "Active Stocks",
                options=list(set(st.session_state.custom_tickers + default_options)),
                default=st.session_state.custom_tickers,
                key="active_custom_tickers"
            )
            st.session_state.custom_tickers = selected_tickers
            st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        # Navigation
        pages = [
            ("Dashboard",       "🏠", "Overview & signals"),
            ("Market Screener", "🔍", "Signals & Catalysts"),
            ("Breakouts",       "📈", "52W Highs"),
            ("Breakdowns",      "📉", "52W Lows"),
            ("Sector Heatmap",  "🔥", "Sector clusters"),
            ("Report & Delivery","📄", "PDF & email"),
            ("Settings",        "⚙️", "Filters & config"),
        ]

        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"

        st.markdown('<div style="margin-bottom:0.4rem; font-size:10px; letter-spacing:0.1em; text-transform:uppercase; color:rgba(255,255,255,0.2); padding-left:4px;">Navigation</div>', unsafe_allow_html=True)

        for label, icon, hint in pages:
            is_active = st.session_state.current_page == label
            active_style = "background:rgba(201,168,76,0.1); border:1px solid rgba(201,168,76,0.22); color:#C9A84C;" if is_active else "border:1px solid transparent; color:rgba(255,255,255,0.45);"
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                use_container_width=True,
                help=hint
            ):
                st.session_state.current_page = label
                st.rerun()

        # Footer
        st.markdown("""
        <div style="position:absolute; bottom:1.5rem; left:0; right:0; padding:0 1rem; border-top:1px solid rgba(255,255,255,0.05); padding-top:1rem;">
            <div style="font-size:10px; color:rgba(255,255,255,0.18); text-align:center; line-height:1.6;">
                SEBI PMS: INP000004847<br>
                SEBI AIF: IN/AIF3/15-16/0182<br>
                <span style="color:rgba(201,168,76,0.35); margin-top:4px; display:block;">© 2025 Samvitti Capital Pvt Ltd</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.current_page
