import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
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

    market = st.session_state.get("market", "India (NSE)")
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

    # ── Summary pills & CSV export ────────────────────────────────────────
    col_pills, col_dl = st.columns([3, 1])
    with col_pills:
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
    with col_dl:
        csv_data = highs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name="breakouts.csv",
            mime="text/csv",
            key="dl_breakouts"
        )

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

    # ── Detailed Chart Section ───────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-title">Interactive Chart Analysis</p><p class="section-sub">1-Year closing price & RSI detail</p>', unsafe_allow_html=True)

    breakout_tickers = highs["Full_Ticker"].tolist()
    if breakout_tickers:
        selected_full_ticker = st.selectbox(
            "Select Ticker for Detailed Chart",
            options=breakout_tickers,
            format_func=lambda x: x.replace(".NS", ""),
            key="bo_chart_ticker"
        )

        with st.spinner(f"Loading chart for {selected_full_ticker.replace('.NS', '')}..."):
            try:
                hist_df = yf.download(selected_full_ticker, period="1y", auto_adjust=True, progress=False)
            except Exception:
                hist_df = pd.DataFrame()

        if not hist_df.empty:
            if isinstance(hist_df.columns, pd.MultiIndex):
                hist_df.columns = hist_df.columns.get_level_values(0)
            
            if "Close" in hist_df.columns:
                hist_df = hist_df.dropna(subset=["Close"])
            if len(hist_df) > 14:
                # RSI calculation
                close_series = hist_df["Close"]
                delta = close_series.diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = (-delta.clip(upper=0)).rolling(14).mean()
                rs = gain / loss.replace(0, np.nan)
                hist_df["RSI"] = 100 - (100 / (1 + rs))

                # 52W levels
                w52_high = hist_df["Close"].max()
                w52_low  = hist_df["Close"].min()

                from plotly.subplots import make_subplots
                fig_detail = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.08,
                    row_heights=[0.7, 0.3]
                )

                # Price line
                fig_detail.add_trace(
                    go.Scatter(
                        x=hist_df.index, y=hist_df["Close"],
                        name="Close Price", line=dict(color="#C9A84C", width=2)
                    ),
                    row=1, col=1
                )
                # 52W Bounds
                fig_detail.add_hline(
                    y=w52_high, line_dash="dash", line_color="#2DD4BF",
                    annotation_text=f"52W High: {w52_high:.2f}", annotation_position="top left",
                    row=1, col=1
                )
                fig_detail.add_hline(
                    y=w52_low, line_dash="dash", line_color="#E05C5C",
                    annotation_text=f"52W Low: {w52_low:.2f}", annotation_position="bottom left",
                    row=1, col=1
                )

                # RSI line
                fig_detail.add_trace(
                    go.Scatter(
                        x=hist_df.index, y=hist_df["RSI"],
                        name="RSI (14)", line=dict(color="#60A5FA", width=1.5)
                    ),
                    row=2, col=1
                )
                fig_detail.add_hline(y=70, line_dash="dot", line_color="rgba(224,92,92,0.4)", row=2, col=1)
                fig_detail.add_hline(y=30, line_dash="dot", line_color="rgba(45,212,191,0.4)", row=2, col=1)

                fig_detail.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="rgba(255,255,255,0.6)",
                    font_family="JetBrains Mono",
                    height=450,
                    margin=dict(l=10, r=10, t=10, b=10),
                    showlegend=False,
                    xaxis2=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Price"),
                    yaxis2=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="RSI", range=[0, 100])
                )

                st.markdown('<div class="glass-card" style="padding:0.75rem;">', unsafe_allow_html=True)
                st.plotly_chart(fig_detail, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Insufficient historical data to plot detailed chart.")
        else:
            st.warning("Detailed historical price chart is not available for this ticker.")
