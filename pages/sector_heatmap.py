import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.fetcher import fetch_stock_data, assign_sectors, compute_sector_summary, NIFTY50, SP500_SAMPLE, get_active_tickers
from components.styles import clean_html


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Sector Heatmap</h1>
        <span class="page-badge">Macro Clusters</span>
    </div>
    """, unsafe_allow_html=True)

    tickers = get_active_tickers()

    metric = st.selectbox("Color by", ["Avg Momentum", "Avg RSI", "Breakout %", "Breakdown %"], key="hm_metric")

    with st.spinner("Loading sector data…"):
        df = fetch_stock_data(tickers[:80])

    if df.empty:
        st.warning("No data.")
        return

    df = assign_sectors(df, market)
    sector_df = compute_sector_summary(df)

    if sector_df.empty:
        st.info("No sector data available for this market selection.")
        return

    sector_df["Breakout_Pct"]  = (sector_df["Highs"] / sector_df["Total"] * 100).round(1)
    sector_df["Breakdown_Pct"] = (sector_df["Lows"]  / sector_df["Total"] * 100).round(1)

    metric_map = {
        "Avg Momentum": ("Avg_Momentum", "#C9A84C"),
        "Avg RSI":      ("Avg_RSI",      "#60A5FA"),
        "Breakout %":   ("Breakout_Pct", "#2DD4BF"),
        "Breakdown %":  ("Breakdown_Pct","#E05C5C"),
    }
    col_key, base_color = metric_map[metric]
    sector_df = sector_df.sort_values(col_key, ascending=False)

    # ── Treemap ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">Sector Overview</p><p class="section-sub">Size = number of stocks. Color = selected metric.</p>', unsafe_allow_html=True)

    color_scale = (
        [[0,"#E05C5C"],[0.5,"#C9A84C"],[1,"#2DD4BF"]] if "Breakout" in metric or "Momentum" in metric
        else [[0,"#E05C5C"],[0.5,"rgba(255,255,255,0.3)"],[1,"#2DD4BF"]]
    )

    fig_tree = go.Figure(go.Treemap(
        labels=sector_df["Sector"],
        values=sector_df["Total"],
        parents=[""] * len(sector_df),
        customdata=sector_df[[col_key, "Highs", "Lows", "Total"]].values,
        hovertemplate=(
            "<b>%{label}</b><br>"
            f"{metric}: %{{customdata[0]:.1f}}<br>"
            "Breakouts: %{customdata[1]}<br>"
            "Breakdowns: %{customdata[2]}<br>"
            "Total: %{customdata[3]}<extra></extra>"
        ),
        marker=dict(
            colors=sector_df[col_key],
            colorscale=color_scale,
            showscale=True,
            colorbar=dict(
                title=dict(text=metric, font=dict(size=11, color="rgba(255,255,255,0.4)")),
                thickness=12,
                tickfont=dict(size=10, color="rgba(255,255,255,0.4)"),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
            ),
            line=dict(color="rgba(8,12,20,0.8)", width=2),
        ),
        textfont=dict(family="JetBrains Mono", size=12, color="rgba(255,255,255,0.85)"),
    ))
    fig_tree.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=360,
    )
    st.markdown('<div class="glass-card" style="padding:0.5rem;">', unsafe_allow_html=True)
    st.plotly_chart(fig_tree, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Bar comparison ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="section-title">Momentum by Sector</p>', unsafe_allow_html=True)
        fig_mom = go.Figure(go.Bar(
            x=sector_df["Avg_Momentum"],
            y=sector_df["Sector"],
            orientation="h",
            marker_color=[
                "#2DD4BF" if v >= 60 else "#C9A84C" if v >= 40 else "#E05C5C"
                for v in sector_df["Avg_Momentum"]
            ],
            marker_line_width=0,
        ))
        fig_mom.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(255,255,255,0.5)",
            height=280, margin=dict(l=0, r=0, t=5, b=5),
            xaxis=dict(showgrid=False, range=[0,100], tickfont=dict(size=10)),
            yaxis=dict(showgrid=False, tickfont=dict(size=11)),
            showlegend=False, bargap=0.3,
        )
        st.markdown('<div class="glass-card" style="padding:0.5rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_mom, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-title">Highs vs Lows Count</p>', unsafe_allow_html=True)
        fig_hl = go.Figure()
        fig_hl.add_bar(
            x=sector_df["Sector"], y=sector_df["Highs"],
            name="Highs", marker_color="#2DD4BF", marker_line_width=0,
        )
        fig_hl.add_bar(
            x=sector_df["Sector"], y=sector_df["Lows"],
            name="Lows", marker_color="#E05C5C", marker_line_width=0,
        )
        fig_hl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(255,255,255,0.5)",
            barmode="group", height=280,
            margin=dict(l=0, r=0, t=5, b=5),
            xaxis=dict(showgrid=False, tickfont=dict(size=10), tickangle=-30),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                       tickfont=dict(size=10)),
            legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=11)),
            bargap=0.2, bargroupgap=0.1,
        )
        st.markdown('<div class="glass-card" style="padding:0.5rem;">', unsafe_allow_html=True)
        st.plotly_chart(fig_hl, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Sector detail table ────────────────────────────────────────────────
    st.markdown('<br><p class="section-title">Sector Detail</p>', unsafe_allow_html=True)
    table_html = """
    <div class="glass-card" style="padding:0.25rem 0;">
    <table class="stock-table">
    <thead><tr>
        <th>Sector</th><th>Stocks</th><th>Breakouts</th><th>Breakdowns</th>
        <th>Breakout %</th><th>Avg Momentum</th><th>Avg RSI</th><th>Bias</th>
    </tr></thead><tbody>
    """
    for _, r in sector_df.iterrows():
        bias = "Bullish" if r["Highs"] > r["Lows"] else "Bearish" if r["Lows"] > r["Highs"] else "Neutral"
        bias_cls = "badge-bull" if bias == "Bullish" else "badge-bear" if bias == "Bearish" else "badge-gray"
        mom_color = "#2DD4BF" if r["Avg_Momentum"] >= 60 else "#C9A84C" if r["Avg_Momentum"] >= 40 else "#E05C5C"
        table_html += f"""
        <tr>
            <td style="font-weight:500;color:#F0EBD8;">{r['Sector']}</td>
            <td class="mono">{int(r['Total'])}</td>
            <td class="mono" style="color:#2DD4BF;">{int(r['Highs'])}</td>
            <td class="mono" style="color:#E05C5C;">{int(r['Lows'])}</td>
            <td class="mono">{r['Breakout_Pct']:.1f}%</td>
            <td>
                <div class="score-bar-wrap">
                    <div class="score-bar-bg"><div class="score-bar-fill" style="width:{r['Avg_Momentum']}%;background:{mom_color};"></div></div>
                    <span class="mono" style="font-size:11px;color:{mom_color};min-width:28px;">{r['Avg_Momentum']:.0f}</span>
                </div>
            </td>
            <td class="mono">{r['Avg_RSI']:.0f}</td>
            <td><span class="badge {bias_cls}">{bias}</span></td>
        </tr>
        """
    table_html += "</tbody></table></div>"
    st.markdown(clean_html(table_html), unsafe_allow_html=True)
