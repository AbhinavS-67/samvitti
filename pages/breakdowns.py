import streamlit as st
import plotly.graph_objects as go
from data.fetcher import fetch_stock_data, assign_sectors, NIFTY50, SP500_SAMPLE
from components.styles import clean_html


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Breakdowns</h1>
        <span class="page-badge" style="background:rgba(224,92,92,0.1);border-color:rgba(224,92,92,0.25);color:#E05C5C;">52W Lows</span>
    </div>
    """, unsafe_allow_html=True)

    market = st.session_state.get("market", "India (NSE)")
    tickers = []
    if market in ["India (NSE)", "Both"]:
        tickers += NIFTY50
    if market in ["US (S&P 500)", "Both"]:
        tickers += SP500_SAMPLE

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        sort_by = st.selectbox("Sort by", ["RSI (Asc)", "Momentum (Desc)", "% from Low"], key="bd_sort")
    with fcol2:
        reversal_only = st.checkbox("Reversal candidates only (RSI < 35)", key="bd_rev")
    with fcol3:
        vol_flag = st.checkbox("Volume spike only", key="bd_vol")

    with st.spinner("Loading breakdown data…"):
        df = fetch_stock_data(tickers[:80])

    if df.empty:
        st.warning("No data available.")
        return

    df = assign_sectors(df, market)
    lows = df[df["Is_52W_Low"] == True].copy()

    if reversal_only:
        lows = lows[lows["RSI"] < 35]
    if vol_flag:
        lows = lows[lows["Vol_Confirmed"] == True]

    sort_map = {
        "RSI (Asc)": ("RSI", True),
        "Momentum (Desc)": ("Momentum", False),
        "% from Low": ("Pct_From_Low", True),
    }
    col, asc = sort_map[sort_by]
    lows = lows.sort_values(col, ascending=asc)

    # summary
    oversold  = len(lows[lows["RSI"] < 30])
    near_rev  = len(lows[(lows["RSI"] < 35) & (lows["Vol_Confirmed"])])
    st.markdown(f"""
    <div style="display:flex;gap:10px;margin-bottom:1.2rem;flex-wrap:wrap;">
        <span class="badge badge-bear" style="padding:6px 14px;font-size:12px;">{len(lows)} breakdowns</span>
        <span class="badge badge-gold" style="padding:6px 14px;font-size:12px;">RSI &lt; 30: {oversold}</span>
        <span class="badge" style="background:rgba(45,212,191,0.1);color:#2DD4BF;border:1px solid rgba(45,212,191,0.2);padding:6px 14px;font-size:12px;">
            Reversal watch: {near_rev}
        </span>
    </div>
    """, unsafe_allow_html=True)

    if lows.empty:
        st.info("No breakdowns match current filters.")
        return

    currency = "₹" if market == "India (NSE)" else "$"

    tab1, tab2 = st.tabs(["📋  Stock List", "📊  RSI vs Price Position"])

    with tab1:
        table_html = """
        <div class="glass-card" style="padding:0.25rem 0; overflow-x:auto;">
        <table class="stock-table">
        <thead><tr>
            <th>#</th><th>Ticker</th><th>Sector</th><th>Price</th>
            <th>52W Low</th><th>% from Low</th><th>RSI</th><th>5D Ret</th><th>Signal</th>
        </tr></thead><tbody>
        """

        for i, (_, r) in enumerate(lows.iterrows(), 1):
            rsi_color = "#E05C5C" if r["RSI"] < 30 else "#C9A84C" if r["RSI"] < 40 else "rgba(255,255,255,0.6)"
            ret_color = "#2DD4BF" if r["Ret_5D"] >= 0 else "#E05C5C"

            if r["RSI"] < 30 and r["Vol_Confirmed"]:
                sig = '<span class="badge" style="background:rgba(45,212,191,0.12);color:#2DD4BF;border:1px solid rgba(45,212,191,0.25);">⚡ Reversal Watch</span>'
            elif r["RSI"] < 30:
                sig = '<span class="badge badge-gold">Oversold</span>'
            elif r["RSI"] < 40:
                sig = '<span class="badge badge-bear">Weak</span>'
            else:
                sig = '<span class="badge badge-gray">Neutral</span>'

            table_html += f"""
            <tr>
                <td style="color:rgba(255,255,255,0.25);font-size:11px;">{i}</td>
                <td><span class="ticker-cell">{r['Ticker']}</span></td>
                <td style="font-size:12px;color:rgba(255,255,255,0.4);">{r.get('Sector','—')}</td>
                <td><span class="mono">{currency}{r['Price']:,.2f}</span></td>
                <td><span class="mono" style="color:rgba(255,255,255,0.4);">{currency}{r['52W_Low']:,.2f}</span></td>
                <td><span class="mono" style="color:#E05C5C;">{r['Pct_From_Low']:+.1f}%</span></td>
                <td><span class="mono" style="color:{rsi_color};">{r['RSI']:.0f}</span></td>
                <td><span class="mono" style="color:{ret_color};">{r['Ret_5D']:+.1f}%</span></td>
                <td>{sig}</td>
            </tr>
            """

        table_html += "</tbody></table></div>"
        st.markdown(clean_html(table_html), unsafe_allow_html=True)

    with tab2:
        fig = go.Figure()

        # Color by reversal potential
        colors = []
        for _, r in lows.iterrows():
            if r["RSI"] < 30 and r["Vol_Confirmed"]:
                colors.append("#2DD4BF")
            elif r["RSI"] < 30:
                colors.append("#C9A84C")
            else:
                colors.append("#E05C5C")

        fig.add_trace(go.Scatter(
            x=lows["Pct_From_Low"], y=lows["RSI"],
            mode="markers+text",
            text=lows["Ticker"],
            textposition="top center",
            textfont=dict(size=9, color="rgba(255,255,255,0.4)"),
            marker=dict(
                size=10, color=colors,
                line=dict(color="rgba(255,255,255,0.1)", width=1),
            ),
            hovertemplate="<b>%{text}</b><br>% from Low: %{x:.1f}%<br>RSI: %{y:.0f}<extra></extra>",
        ))
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(224,92,92,0.05)",
                      layer="below", line_width=0)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(224,92,92,0.4)",
                      annotation_text="Oversold (30)", annotation_font_size=10)
        fig.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,0.1)")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(255,255,255,0.5)",
            height=400, margin=dict(l=10, r=10, t=20, b=10),
            xaxis=dict(title="% Above 52W Low", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
            yaxis=dict(title="RSI", showgrid=True,
                       gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=10)),
        )
        st.markdown('<div class="glass-card" style="padding:0.5rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;gap:16px;margin-top:8px;">
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:rgba(255,255,255,0.4);">
                <span style="width:8px;height:8px;border-radius:50%;background:#2DD4BF;display:inline-block;"></span>Reversal Watch
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:rgba(255,255,255,0.4);">
                <span style="width:8px;height:8px;border-radius:50%;background:#C9A84C;display:inline-block;"></span>Oversold
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:rgba(255,255,255,0.4);">
                <span style="width:8px;height:8px;border-radius:50%;background:#E05C5C;display:inline-block;"></span>Breakdown
            </span>
        </div>
        """, unsafe_allow_html=True)
