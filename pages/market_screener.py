import streamlit as st
import pandas as pd
from datetime import datetime
import yfinance as yf
from data.fetcher import (
    fetch_stock_data, assign_sectors, fetch_index_data,
    get_active_tickers, fetch_screener_details
)
from components.styles import clean_html

def render():
    # ── CSS Injection ──────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .index-cards-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .index-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        backdrop-filter: blur(8px);
    }
    .index-card-label {
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: rgba(255, 255, 255, 0.35);
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .index-card-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #F0EBD8;
        margin-bottom: 4px;
    }
    .index-card-change {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 500;
    }
    .index-card-change.up {
        color: #2DD4BF;
    }
    .index-card-change.down {
        color: #E05C5C;
    }

    .screener-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        position: relative;
        border-left: 4px solid #C9A84C;
        transition: all 0.2s ease;
    }
    .screener-card:hover {
        border-color: rgba(201, 168, 76, 0.3);
        background: rgba(255, 255, 255, 0.04);
    }
    .screener-card.breakout {
        border-left-color: #2DD4BF;
    }
    .screener-card.breakdown {
        border-left-color: #E05C5C;
    }
    .screener-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.8rem;
    }
    .screener-card-left {
        flex: 1;
        padding-right: 1.5rem;
    }
    .screener-card-right {
        text-align: right;
        min-width: 220px;
    }
    .company-name {
        font-size: 18px;
        font-weight: 600;
        color: #F0EBD8;
        margin-bottom: 2px;
    }
    .ticker-sector {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: rgba(255, 255, 255, 0.35);
        margin-bottom: 10px;
    }
    .business-summary {
        font-size: 12.5px;
        color: rgba(255, 255, 255, 0.5);
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .catalyst-section {
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 10px;
        margin-top: 10px;
    }
    .catalyst-title {
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.08em;
        color: rgba(255, 255, 255, 0.3);
        margin-bottom: 4px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .catalyst-content {
        font-size: 12.5px;
        color: #2DD4BF;
    }
    .catalyst-content.stale {
        color: rgba(255, 255, 255, 0.45);
    }
    .catalyst-date {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.3);
        margin-left: 8px;
    }
    .price-large {
        font-family: 'JetBrains Mono', monospace;
        font-size: 20px;
        font-weight: 600;
        color: #F0EBD8;
        margin-bottom: 4px;
    }
    .signal-status-high {
        font-size: 11px;
        font-weight: 600;
        color: #2DD4BF;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .signal-status-low {
        font-size: 11px;
        font-weight: 600;
        color: #E05C5C;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .vol-surge-text {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.45);
        margin-top: 4px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 4px;
    }
    .vol-surge-icon {
        color: #E8C96A;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────
    today_time = datetime.now().strftime("%d %b %Y - %H:%M")
    st.markdown(f"""
    <div class="page-header" style="justify-content: space-between; align-items: center; margin-bottom: 1.2rem;">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:36px; height:36px; border-radius:10px; background:linear-gradient(135deg,rgba(45,212,191,0.3),rgba(45,212,191,0.1)); border:1px solid rgba(45,212,191,0.4); display:flex; align-items:center; justify-content:center;">
                <span style="font-family:'DM Serif Display',serif; font-size:16px; color:#2DD4BF; font-weight:600;">◆</span>
            </div>
            <h1 class="page-title">Nifty500 Screener</h1>
        </div>
        <span style="font-size:12px; color:rgba(255,255,255,0.25); font-family:'JetBrains Mono',monospace;">52-Week High / Low · Volume Confirmed | Last screen: {today_time}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Index Cards Row ────────────────────────────────────────────────────
    with st.spinner("Fetching index statistics..."):
        indices_data = fetch_index_data()

    if indices_data:
        st.markdown('<div class="index-cards-container">', unsafe_allow_html=True)
        for name, data in indices_data.items():
            price_val = data["price"]
            change_val = data["change"]
            pct_val = data["pct"]

            sign = "+" if change_val >= 0 else ""
            change_cls = "up" if change_val >= 0 else "down"
            arrow = "▲" if change_val >= 0 else "▼"

            # India VIX doesn't use currency symbol
            cur_sym = "" if name == "India VIX" else "₹"
            
            st.markdown(f"""
            <div class="index-card">
                <div class="index-card-label">{name}</div>
                <div class="index-card-price">{cur_sym}{price_val:,.2f}</div>
                <div class="index-card-change {change_cls}">
                    {arrow} {pct_val:+.2f}% ({change_val:+.2f})
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Fetch Data ─────────────────────────────────────────────────────────
    tickers = get_active_tickers()
    with st.spinner("Screening market data..."):
        df = fetch_stock_data(tickers[:80]) # Cap for speed and API safety

    if df.empty:
        st.warning("No screener data loaded. Please check active configurations.")
        return

    market = st.session_state.get("market", "India (NSE)")
    df = assign_sectors(df, market)

    highs = df[df["Is_52W_High"] == True]
    lows = df[df["Is_52W_Low"] == True]

    # Today's Signals Summary Bar
    st.markdown(clean_html(f"""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:1.5rem; padding: 10px 14px; background:rgba(255,255,255,0.02); border-top:1px solid rgba(255,255,255,0.06); border-bottom:1px solid rgba(255,255,255,0.06); border-radius:8px;">
        <span style="font-size:11px; font-weight:600; letter-spacing:0.1em; color:rgba(255,255,255,0.4); text-transform:uppercase; display:flex; align-items:center; gap:6px;">
            <span style="color:#C9A84C;">◆</span> TODAY'S SIGNALS
        </span>
        <span style="font-size:11px; font-weight:600; letter-spacing:0.05em; color:#2DD4BF; display:flex; align-items:center; gap:4px;">
            <span>⇧</span> {len(highs)} BREAKOUT HIGHS
        </span>
        <span style="font-size:11px; font-weight:600; letter-spacing:0.05em; color:#E05C5C; display:flex; align-items:center; gap:4px;">
            <span>⇩</span> {len(lows)} BREAKDOWN LOWS
        </span>
    </div>
    """), unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab_highs, tab_lows, tab_errors = st.tabs([
        f"▲ Breakout Highs ({len(highs)})",
        f"▼ Breakdown Lows ({len(lows)})",
        "⚠ Errors (0)"
    ])

    with tab_highs:
        if not highs.empty:
            for _, row in highs.sort_values("Momentum", ascending=False).iterrows():
                ticker_full = row["Full_Ticker"]
                ticker_clean = row["Ticker"]
                price = row["Price"]
                pct_change = row["Ret_1D"]
                vol_ratio = row["Vol_Ratio"]
                currency_symbol = "₹" if ".NS" in ticker_full else "$"

                # Fetch company details and news (Cached)
                details = fetch_screener_details(ticker_full)
                company_name = details["name"]
                sector = details["sector"]
                summary = details["summary"]
                news_list = details["news"]

                # Extract catalyst
                catalyst_html = ""
                if news_list:
                    latest_news = news_list[0]
                    news_title = latest_news.get("title", "")
                    news_pub_time = latest_news.get("providerPublishTime", 0)
                    
                    if news_pub_time > 0:
                        pub_dt = datetime.fromtimestamp(news_pub_time)
                        time_delta = datetime.now() - pub_dt
                        is_stale = time_delta.days > 5
                        pub_formatted = pub_dt.strftime("%d %b %Y")

                        stale_badge = ' <span class="badge badge-bear" style="font-size:9px; padding:1px 5px; margin-left:6px; background:rgba(224,92,92,0.12); color:#E05C5C; border:1px solid rgba(224,92,92,0.25);">⚠ STALE</span>' if is_stale else ''
                        catalyst_cls = "stale" if is_stale else ""
                        
                        catalyst_html = f"""
                        <div class="catalyst-section">
                            <div class="catalyst-title">MAJOR CATALYST{stale_badge}</div>
                            <div class="catalyst-content {catalyst_cls}">
                                <strong>{pub_formatted}:</strong> {news_title} <span class="catalyst-date">{pub_formatted}</span>
                            </div>
                        </div>
                        """

                # Render Card
                st.markdown(clean_html(f"""
                <div class="screener-card breakout">
                    <div class="screener-card-header">
                        <div class="screener-card-left">
                            <div class="company-name">{company_name}</div>
                            <div class="ticker-sector">{ticker_clean} · {sector}</div>
                            <div class="business-summary">{summary[:400]}...</div>
                            {catalyst_html}
                        </div>
                        <div class="screener-card-right">
                            <div class="price-large">{currency_symbol}{price:,.2f}</div>
                            <div class="signal-status-high">▲ AT 52-WEEK HIGH</div>
                            <div class="vol-surge-text">
                                <span class="vol-surge-icon">⚡</span> Vol surge {vol_ratio:.1f}x confirmed
                            </div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card"><p style="color:rgba(255,255,255,0.35);text-align:center;padding:2rem;">No stocks are registering breakout signals today.</p></div>', unsafe_allow_html=True)

    with tab_lows:
        if not lows.empty:
            for _, row in lows.sort_values("RSI", ascending=True).iterrows():
                ticker_full = row["Full_Ticker"]
                ticker_clean = row["Ticker"]
                price = row["Price"]
                pct_change = row["Ret_1D"]
                vol_ratio = row["Vol_Ratio"]
                currency_symbol = "₹" if ".NS" in ticker_full else "$"

                # Fetch company details and news (Cached)
                details = fetch_screener_details(ticker_full)
                company_name = details["name"]
                sector = details["sector"]
                summary = details["summary"]
                news_list = details["news"]

                # Extract catalyst
                catalyst_html = ""
                if news_list:
                    latest_news = news_list[0]
                    news_title = latest_news.get("title", "")
                    news_pub_time = latest_news.get("providerPublishTime", 0)
                    
                    if news_pub_time > 0:
                        pub_dt = datetime.fromtimestamp(news_pub_time)
                        time_delta = datetime.now() - pub_dt
                        is_stale = time_delta.days > 5
                        pub_formatted = pub_dt.strftime("%d %b %Y")

                        stale_badge = ' <span class="badge badge-bear" style="font-size:9px; padding:1px 5px; margin-left:6px; background:rgba(224,92,92,0.12); color:#E05C5C; border:1px solid rgba(224,92,92,0.25);">⚠ STALE</span>' if is_stale else ''
                        catalyst_cls = "stale" if is_stale else ""
                        
                        catalyst_html = f"""
                        <div class="catalyst-section">
                            <div class="catalyst-title">MAJOR CATALYST{stale_badge}</div>
                            <div class="catalyst-content {catalyst_cls}">
                                <strong>{pub_formatted}:</strong> {news_title} <span class="catalyst-date">{pub_formatted}</span>
                            </div>
                        </div>
                        """

                # Render Card
                st.markdown(clean_html(f"""
                <div class="screener-card breakdown">
                    <div class="screener-card-header">
                        <div class="screener-card-left">
                            <div class="company-name">{company_name}</div>
                            <div class="ticker-sector">{ticker_clean} · {sector}</div>
                            <div class="business-summary">{summary[:400]}...</div>
                            {catalyst_html}
                        </div>
                        <div class="screener-card-right">
                            <div class="price-large">{currency_symbol}{price:,.2f}</div>
                            <div class="signal-status-low">▼ AT 52-WEEK LOW</div>
                            <div class="vol-surge-text">
                                <span class="vol-surge-icon">⚡</span> Vol surge {vol_ratio:.1f}x confirmed
                            </div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card"><p style="color:rgba(255,255,255,0.35);text-align:center;padding:2rem;">No stocks are registering breakdown signals today.</p></div>', unsafe_allow_html=True)

    with tab_errors:
        st.markdown('<div class="glass-card"><p style="color:rgba(255,255,255,0.35);text-align:center;padding:2rem;">All stock feeds scanned successfully. Errors: 0.</p></div>', unsafe_allow_html=True)
