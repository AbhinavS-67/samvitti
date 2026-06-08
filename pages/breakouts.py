import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data.fetcher import (
    fetch_stock_data, assign_sectors, fetch_fundamentals,
    NIFTY50, SP500_SAMPLE, score_label, get_active_tickers
)
from components.styles import clean_html


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Breakouts</h1>
        <span class="page-badge">52W Highs</span>
    </div>
    """, unsafe_allow_html=True)

    tickers = get_active_tickers()

    # ── Filters ────────────────────────────────────────────────────────────
    fcol1, fcol2, fcol3, fcol4 = st.columns([2,2,2,2])
    with fcol1:
        sort_by = st.selectbox("Sort by", ["Momentum","RSI","Vol Ratio","% from High"], key="bo_sort")
    with fcol2:
        vol_only = st.checkbox("Volume confirmed only", value=False, key="bo_vol")
    with fcol3:
        rsi_min = st.slider("Min RSI", 0, 100, 40, key="bo_rsi")
    with fcol4:
        show_fundamentals = st.checkbox("Show fundamentals", value=False, key="bo_fund")

    with st.spinner("Loading breakout data…"):
        df = fetch_stock_data(tickers[:80])

    if df.empty:
        st.warning("No data available.")
        return

    df = assign_sectors(df, market)
    highs = df[df["Is_52W_High"] == True].copy()
    highs = highs[highs["RSI"] >= rsi_min]
    if vol_only:
        highs = highs[highs["Vol_Confirmed"] == True]

    sort_map = {
        "Momentum": "Momentum", "RSI": "RSI",
        "Vol Ratio": "Vol_Ratio", "% from High": "Pct_From_High"
    }
    highs = highs.sort_values(sort_map[sort_by], ascending=(sort_by == "% from High"))

    # ── Summary pills ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;gap:10px;margin-bottom:1.2rem;flex-wrap:wrap;">
        <span class="badge badge-teal" style="background:rgba(45,212,191,0.1);color:#2DD4BF;border:1px solid rgba(45,212,191,0.25);padding:6px 14px;font-size:12px;">
            {len(highs)} breakouts
        </span>
        <span class="badge badge-gold" style="padding:6px 14px;font-size:12px;">
            {len(highs[highs['Vol_Confirmed']==True])} volume confirmed
        </span>
        <span class="badge badge-gray" style="padding:6px 14px;font-size:12px;">
            Avg momentum: {highs['Momentum'].mean():.0f}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if highs.empty:
        st.info("No breakouts match current filters.")
        return

    # ── Tabs: Table / Chart ───────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📋  Stock List", "📊  Scatter Analysis"])

    with tab1:
        currency = "₹" if market == "India (NSE)" else "$"
        table_html = """
        <div class="glass-card" style="padding:0.25rem 0; overflow-x:auto;">
        <table class="stock-table">
        <thead><tr>
            <th>#</th><th>Ticker</th><th>Sector</th><th>Price</th>
            <th>52W High</th><th>% from High</th><th>RSI</th>
            <th>Momentum</th><th>Vol Ratio</th><th>1M Ret</th><th>Signal</th>
        </tr></thead><tbody>
        """

        for i, (_, r) in enumerate(highs.iterrows(), 1):
            score_color = "#2DD4BF" if r["Momentum"] >= 70 else "#C9A84C" if r["Momentum"] >= 40 else "#E05C5C"
            vol_badge   = '<span class="badge badge-bull">↑ High Vol</span>' if r["Vol_Confirmed"] else '<span class="badge badge-gray">Avg</span>'
            signal      = score_label(r["Momentum"])
            sig_cls     = "badge-bull" if signal == "Strong" else "badge-gold" if signal == "Moderate" else "badge-gray"
            ret_color   = "#2DD4BF" if r["Ret_1M"] >= 0 else "#E05C5C"

            row_currency = "₹" if ".NS" in r.get("Full_Ticker", "") else "$"
            table_html += f"""
            <tr>
                <td style="color:rgba(255,255,255,0.25);font-size:11px;">{i}</td>
                <td><span class="ticker-cell">{r['Ticker']}</span></td>
                <td style="font-size:12px;color:rgba(255,255,255,0.4);">{r.get('Sector','—')}</td>
                <td><span class="mono">{row_currency}{r['Price']:,.2f}</span></td>
                <td><span class="mono" style="color:rgba(255,255,255,0.4);">{row_currency}{r['52W_High']:,.2f}</span></td>
                <td><span class="mono" style="color:#2DD4BF;">{r['Pct_From_High']:+.2f}%</span></td>
                <td><span class="mono">{r['RSI']:.0f}</span></td>
                <td>
                    <div class="score-bar-wrap">
                        <div class="score-bar-bg"><div class="score-bar-fill" style="width:{r['Momentum']}%;background:{score_color};"></div></div>
                        <span class="mono" style="font-size:11px;color:{score_color};min-width:28px;">{r['Momentum']:.0f}</span>
                    </div>
                </td>
                <td><span class="mono">{r['Vol_Ratio']:.2f}x</span></td>
                <td><span class="mono" style="color:{ret_color};">{r['Ret_1M']:+.1f}%</span></td>
                <td><span class="badge {sig_cls}">{signal}</span></td>
            </tr>
            """

        table_html += "</tbody></table></div>"
        st.markdown(clean_html(table_html), unsafe_allow_html=True)

        if show_fundamentals and len(highs) > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="section-title">Fundamental Overlay</p>', unsafe_allow_html=True)
            top5 = highs.head(5)
            fcols = st.columns(5)
            for col, (_, r) in zip(fcols, top5.iterrows()):
                fund = fetch_fundamentals(r["Full_Ticker"])
                with col:
                    pe = f"{fund.get('pe_ratio', '—'):.1f}x" if isinstance(fund.get('pe_ratio'), float) else "—"
                    pb = f"{fund.get('pb_ratio', '—'):.1f}x" if isinstance(fund.get('pb_ratio'), float) else "—"
                    de = f"{fund.get('de_ratio', '—'):.0f}%" if isinstance(fund.get('de_ratio'), float) else "—"
                    st.markdown(clean_html(f"""
                    <div class="glass-card" style="padding:1rem;">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:14px;font-weight:600;color:#F0EBD8;margin-bottom:10px;">{r['Ticker']}</div>
                        <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;">P/E</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;color:#C9A84C;">{pe}</div>
                        <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;margin-top:8px;">P/B</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;color:#C9A84C;">{pb}</div>
                        <div style="font-size:11px;color:rgba(255,255,255,0.35);margin-bottom:2px;margin-top:8px;">D/E</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:16px;color:#C9A84C;">{de}</div>
                    </div>
                    """), unsafe_allow_html=True)

    with tab2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=highs["RSI"], y=highs["Momentum"],
            mode="markers+text",
            text=highs["Ticker"],
            textposition="top center",
            textfont=dict(size=9, color="rgba(255,255,255,0.5)"),
            marker=dict(
                size=highs["Vol_Ratio"].clip(1, 5) * 8,
                color=highs["Momentum"],
                colorscale=[[0,"#E05C5C"],[0.5,"#C9A84C"],[1,"#2DD4BF"]],
                showscale=True,
                colorbar=dict(title="Score", thickness=12,
                              tickfont=dict(size=10, color="rgba(255,255,255,0.4)")),
                line=dict(color="rgba(255,255,255,0.15)", width=1),
            ),
            hovertemplate="<b>%{text}</b><br>RSI: %{x}<br>Momentum: %{y}<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(255,255,255,0.5)",
            height=420,
            margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(title="RSI", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)",
                       tickfont=dict(size=10)),
            yaxis=dict(title="Momentum Score", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)",
                       tickfont=dict(size=10)),
        )
        fig.add_vline(x=70, line_dash="dot", line_color="rgba(224,92,92,0.3)",
                      annotation_text="Overbought", annotation_font_size=10)
        fig.add_vline(x=50, line_dash="dot", line_color="rgba(255,255,255,0.1)")
        st.markdown('<div class="glass-card" style="padding:0.5rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("Bubble size = volume ratio. Color = momentum score.")
