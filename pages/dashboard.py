import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from data.fetcher import (
    fetch_stock_data, assign_sectors, compute_sector_summary,
    NIFTY50, SP500_SAMPLE, score_label, get_active_tickers
)
from components.styles import clean_html

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="rgba(255,255,255,0.6)",
    font_family="JetBrains Mono",
)


def kpi(label, value, delta="", delta_type="neutral", accent="gold"):
    delta_html = f'<div class="kpi-delta {delta_type}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card {accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""


def render():
    # ── Header ────────────────────────────────────────────────────────────
    today = datetime.now().strftime("%A, %d %b %Y")
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">Market Intelligence</h1>
        <span class="page-badge">Live Dashboard</span>
        <span style="margin-left:auto; font-size:12px; color:rgba(255,255,255,0.25);">{today}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Market & Filters ─────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([2, 2, 4])
    with col_a:
        market = st.selectbox("Market", ["India (NSE)", "US (S&P 500)", "Both"], label_visibility="visible")
    with col_b:
        view_mode = st.selectbox("View", ["Brief Mode", "Detailed Mode"])

    st.session_state["market"] = market
    st.session_state["view_mode"] = view_mode

    # ── Fetch data ─────────────────────────────────────────────────────────
    tickers = get_active_tickers()

    with st.spinner("Fetching market data…"):
        df = fetch_stock_data(tickers[:80])  # cap for speed

    if df.empty:
        st.warning("Unable to fetch data. Check your internet connection.")
        return

    df = assign_sectors(df, market)
    highs = df[df["Is_52W_High"] == True]
    lows  = df[df["Is_52W_Low"]  == True]
    vol_confirmed = df[df["Vol_Confirmed"] == True]

    # ── KPI Row ────────────────────────────────────────────────────────────
    st.markdown("""<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:1.5rem;">""", unsafe_allow_html=True)
    st.markdown(
        kpi("52W Breakouts", len(highs), f"↑ Volume confirmed: {len(highs[highs['Vol_Confirmed']==True])}", "up", "teal") +
        kpi("52W Breakdowns", len(lows), f"↓ Oversold (RSI<30): {len(lows[lows['RSI']<30])}", "down", "red") +
        kpi("Stocks Tracked", len(df), "Custom Search" if st.session_state.get("data_scope") == "Custom Search" else f"Indices: {market}", "neutral", "gold") +
        kpi("Avg Momentum", f"{df['Momentum'].mean():.0f}", "Score out of 100", "neutral", "blue"),
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Main content: two columns ──────────────────────────────────────────
    left, right = st.columns([3, 2], gap="medium")

    with left:
        # Top Breakouts
        st.markdown('<p class="section-title">Top Breakouts Today</p><p class="section-sub">Stocks at or near 52-week highs</p>', unsafe_allow_html=True)

        top_highs = highs.sort_values("Momentum", ascending=False).head(7)
        if not top_highs.empty:
            table_html = """
            <div class="glass-card" style="padding:0.5rem 0;">
            <table class="stock-table">
            <thead><tr>
                <th>Ticker</th><th>Price</th><th>% from 52W High</th>
                <th>RSI</th><th>Momentum</th><th>Vol</th>
            </tr></thead><tbody>
            """

            for _, r in top_highs.iterrows():
                vol_badge = '<span class="badge badge-bull">↑ High Vol</span>' if r["Vol_Confirmed"] else '<span class="badge badge-gray">Avg Vol</span>'
                score_color = "#2DD4BF" if r["Momentum"] >= 70 else "#C9A84C" if r["Momentum"] >= 40 else "#E05C5C"
                table_html += f"""
                <tr>
                    <td><span class="ticker-cell">{r['Ticker']}</span>
                        <div style="font-size:10px;color:rgba(255,255,255,0.25);">{r.get('Sector','')}</div></td>
                    <td><span class="mono">{'₹' if '.NS' in r.get('Full_Ticker','') else '$'}{r['Price']:,.2f}</span></td>
                    <td><span class="mono" style="color:#2DD4BF;">{r['Pct_From_High']:+.1f}%</span></td>
                    <td><span class="mono">{r['RSI']:.0f}</span></td>
                    <td>
                        <div class="score-bar-wrap">
                            <div class="score-bar-bg"><div class="score-bar-fill" style="width:{r['Momentum']}%;background:{score_color};"></div></div>
                            <span class="mono" style="font-size:11px;color:{score_color};min-width:28px;">{r['Momentum']:.0f}</span>
                        </div>
                    </td>
                    <td>{vol_badge}</td>
                </tr>
                """

            table_html += "</tbody></table></div>"
            st.markdown(clean_html(table_html), unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card"><p style="color:rgba(255,255,255,0.35);text-align:center;padding:2rem;">No 52W highs detected today</p></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Top Breakdowns
        st.markdown('<p class="section-title">Watch: Breakdown Stocks</p><p class="section-sub">Near 52-week lows — risk flags & reversal watch</p>', unsafe_allow_html=True)

        top_lows = lows.sort_values("RSI").head(6)
        if not top_lows.empty:
            table_html2 = """
            <div class="glass-card" style="padding:0.5rem 0;">
            <table class="stock-table">
            <thead><tr>
                <th>Ticker</th><th>Price</th><th>% from 52W Low</th>
                <th>RSI</th><th>Signal</th>
            </tr></thead><tbody>
            """

            for _, r in top_lows.iterrows():
                if r["RSI"] < 30:
                    sig = '<span class="badge badge-gold">Oversold — Watch</span>'
                elif r["RSI"] < 40:
                    sig = '<span class="badge badge-bear">Weak</span>'
                else:
                    sig = '<span class="badge badge-gray">Neutral</span>'

                table_html2 += f"""
                <tr>
                    <td><span class="ticker-cell">{r['Ticker']}</span>
                        <div style="font-size:10px;color:rgba(255,255,255,0.25);">{r.get('Sector','')}</div></td>
                    <td><span class="mono">{'₹' if '.NS' in r.get('Full_Ticker','') else '$'}{r['Price']:,.2f}</span></td>
                    <td><span class="mono" style="color:#E05C5C;">{r['Pct_From_Low']:+.1f}%</span></td>
                    <td><span class="mono" style="color:{'#E05C5C' if r['RSI']<30 else 'rgba(255,255,255,0.6)'};">{r['RSI']:.0f}</span></td>
                    <td>{sig}</td>
                </tr>
                """

            table_html2 += "</tbody></table></div>"
            st.markdown(clean_html(table_html2), unsafe_allow_html=True)
        else:
            st.markdown('<div class="glass-card"><p style="color:rgba(255,255,255,0.35);text-align:center;padding:2rem;">No 52W lows detected today</p></div>', unsafe_allow_html=True)

    with right:
        # Sector distribution chart
        st.markdown('<p class="section-title">Sector Heat</p><p class="section-sub">Breakouts vs Breakdowns by sector</p>', unsafe_allow_html=True)

        sector_df = compute_sector_summary(df)
        if not sector_df.empty:
            fig = go.Figure()
            fig.add_bar(
                x=sector_df["Highs"], y=sector_df["Sector"],
                orientation="h", name="Breakouts",
                marker_color="#2DD4BF",
                marker_line_width=0,
            )
            fig.add_bar(
                x=-sector_df["Lows"], y=sector_df["Sector"],
                orientation="h", name="Breakdowns",
                marker_color="#E05C5C",
                marker_line_width=0,
            )
            fig.update_layout(
                **PLOTLY_DARK,
                barmode="relative",
                height=280,
                margin=dict(l=0, r=10, t=10, b=10),
                xaxis=dict(showgrid=False, zeroline=True,
                           zerolinecolor="rgba(255,255,255,0.1)",
                           tickfont=dict(size=10)),
                yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                legend=dict(orientation="h", y=1.08, x=0,
                            font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
                bargap=0.25,
            )
            st.markdown('<div class="glass-card" style="padding:0.75rem;">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        # Momentum distribution
        st.markdown('<p class="section-title" style="margin-top:1rem;">Momentum Distribution</p><p class="section-sub">Spread across all tracked stocks</p>', unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=df["Momentum"], nbinsx=20,
            marker_color="#C9A84C", marker_line_width=0,
            opacity=0.8, name="Momentum",
        ))
        fig2.update_layout(
            **PLOTLY_DARK,
            height=180,
            margin=dict(l=0, r=0, t=5, b=5),
            xaxis=dict(title="Score", showgrid=False,
                       tickfont=dict(size=10), range=[0,100]),
            yaxis=dict(showgrid=False, tickfont=dict(size=10)),
            showlegend=False,
            bargap=0.05,
        )
        st.markdown('<div class="glass-card" style="padding:0.75rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        # AI Market Narrative
        st.markdown('<p class="section-title" style="margin-top:1rem;">Market Pulse</p>', unsafe_allow_html=True)
        n_high = len(highs)
        n_low  = len(lows)
        bias   = "bullish" if n_high > n_low else "bearish" if n_low > n_high else "mixed"
        bias_color = "#2DD4BF" if bias == "bullish" else "#E05C5C" if bias == "bearish" else "#C9A84C"

        top_sector = sector_df.iloc[0]["Sector"] if not sector_df.empty else "—"
        avg_rsi = df["RSI"].mean()

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
                <div style="width:8px;height:8px;border-radius:50%;background:{bias_color};"></div>
                <span style="font-size:12px;font-weight:600;color:{bias_color};text-transform:uppercase;letter-spacing:0.06em;">
                    Market Bias: {bias.title()}
                </span>
            </div>
            <p style="font-size:13px;color:rgba(255,255,255,0.55);line-height:1.6;margin:0;">
                {n_high} stocks are at or near 52-week highs vs {n_low} near 52-week lows.
                <strong style="color:#C9A84C;">{top_sector}</strong> leads the breakout count.
                Average RSI at <strong style="color:rgba(255,255,255,0.7);">{avg_rsi:.0f}</strong> —
                {'momentum remains intact.' if avg_rsi > 50 else 'broad weakness persists.'}
            </p>
            <div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.06);font-size:11px;color:rgba(255,255,255,0.25);">
                Based on EOD data · Updated every 30 mins
            </div>
        </div>
        """, unsafe_allow_html=True)
