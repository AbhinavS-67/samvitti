import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
from data.fetcher import fetch_stock_data, assign_sectors, NIFTY50, SP500_SAMPLE, score_label, get_active_tickers


def generate_pdf_report(highs_df, lows_df, market, today):
    """Generate a simple text-based PDF report."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.colors import HexColor, white, black
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=20*mm, rightMargin=20*mm,
                                topMargin=20*mm, bottomMargin=20*mm)

        GOLD  = HexColor("#C9A84C")
        DARK  = HexColor("#0D1117")
        TEAL  = HexColor("#2DD4BF")
        RED   = HexColor("#E05C5C")
        GRAY  = HexColor("#6B7280")

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("title", fontSize=22, fontName="Helvetica-Bold",
                                     textColor=DARK, spaceAfter=4)
        sub_style   = ParagraphStyle("sub",   fontSize=10, fontName="Helvetica",
                                     textColor=GRAY, spaceAfter=16)
        h2_style    = ParagraphStyle("h2",    fontSize=13, fontName="Helvetica-Bold",
                                     textColor=DARK, spaceBefore=14, spaceAfter=6)
        body_style  = ParagraphStyle("body",  fontSize=9,  fontName="Helvetica",
                                     textColor=HexColor("#374151"), leading=14)

        elems = []
        elems.append(Paragraph("Samvitti Capital", title_style))
        elems.append(Paragraph(f"Market Intelligence Report — {today}  |  {market}", sub_style))
        elems.append(Spacer(1, 4*mm))

        # Top Breakouts
        elems.append(Paragraph("Top 5 Breakouts (52W Highs)", h2_style))
        data = [["Ticker","Price","% from High","RSI","Momentum","Signal"]]
        for _, r in highs_df.head(5).iterrows():
            data.append([
                r["Ticker"],
                f"{r['Price']:,.2f}",
                f"{r['Pct_From_High']:+.2f}%",
                f"{r['RSI']:.0f}",
                f"{r['Momentum']:.0f}",
                score_label(r["Momentum"]),
            ])
        t = Table(data, colWidths=[30*mm,28*mm,32*mm,22*mm,28*mm,28*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DARK),
            ("TEXTCOLOR",  (0,0), (-1,0), white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("GRID",       (0,0), (-1,-1), 0.3, HexColor("#E5E7EB")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#F9FAFB")]),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING",(0,0), (-1,-1), 6),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 6*mm))

        # Top Breakdowns
        elems.append(Paragraph("Top 5 Breakdowns (52W Lows)", h2_style))
        data2 = [["Ticker","Price","% from Low","RSI","5D Return","Flag"]]
        for _, r in lows_df.head(5).iterrows():
            flag = "⚡ Reversal Watch" if r["RSI"] < 30 and r["Vol_Confirmed"] else "Oversold" if r["RSI"] < 30 else "Breakdown"
            data2.append([
                r["Ticker"],
                f"{r['Price']:,.2f}",
                f"{r['Pct_From_Low']:+.1f}%",
                f"{r['RSI']:.0f}",
                f"{r['Ret_5D']:+.1f}%",
                flag,
            ])
        t2 = Table(data2, colWidths=[30*mm,28*mm,32*mm,22*mm,28*mm,28*mm])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), HexColor("#7F1D1D")),
            ("TEXTCOLOR",  (0,0), (-1,0), white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("GRID",       (0,0), (-1,-1), 0.3, HexColor("#E5E7EB")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, HexColor("#F9FAFB")]),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING",(0,0), (-1,-1), 6),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        elems.append(t2)
        elems.append(Spacer(1, 8*mm))

        elems.append(Paragraph("Disclaimer", ParagraphStyle("disc", fontSize=7, textColor=GRAY, leading=10)))
        elems.append(Paragraph(
            "This report is generated for internal use by Samvitti Capital Pvt Ltd. "
            "It does not constitute investment advice. Past performance is not indicative of future results. "
            "SEBI PMS: INP000004847 | SEBI AIF: IN/AIF3/15-16/0182",
            ParagraphStyle("disc2", fontSize=7, textColor=GRAY, leading=10)
        ))

        doc.build(elems)
        buf.seek(0)
        return buf
    except ImportError:
        return None


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Report & Delivery</h1>
        <span class="page-badge">PDF · Email</span>
    </div>
    """, unsafe_allow_html=True)

    tickers = get_active_tickers()

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown('<p class="section-title">Generate 1-Pager Report</p><p class="section-sub">Daily summary for fund managers and analysts</p>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        mode     = st.radio("Report mode", ["Brief (Exec Summary)", "Detailed (Full Analysis)"], horizontal=True)
        top_n    = st.slider("Top N stocks per section", 3, 10, 5)
        include_fund = st.checkbox("Include fundamentals overlay", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬇  Generate PDF Report", use_container_width=True):
            with st.spinner("Fetching data and building report…"):
                df = fetch_stock_data(tickers[:60])
                if df.empty:
                    st.error("No data. Check connection.")
                else:
                    df = assign_sectors(df, market)
                    highs = df[df["Is_52W_High"]].sort_values("Momentum", ascending=False)
                    lows  = df[df["Is_52W_Low"]].sort_values("RSI")
                    today = datetime.now().strftime("%d %b %Y")

                    pdf = generate_pdf_report(highs, lows, market, today)
                    if pdf:
                        st.download_button(
                            label="📄 Download Report PDF",
                            data=pdf,
                            file_name=f"samvitti_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                        )
                        st.success("Report generated successfully!")
                    else:
                        st.warning("reportlab not installed. Run: `pip install reportlab`")
                        st.markdown("""
                        <div class="glass-card" style="margin-top:1rem;">
                        <div style="font-size:13px;color:rgba(255,255,255,0.5);font-family:'JetBrains Mono',monospace;">
                        pip install reportlab
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="section-title">Email Delivery</p><p class="section-sub">Schedule daily report delivery</p>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        smtp_host = st.text_input("SMTP Host", value="smtp.gmail.com", key="smtp_h")
        smtp_port = st.number_input("Port", value=587, step=1, key="smtp_p")
        sender    = st.text_input("Sender Email", key="smtp_from")
        password  = st.text_input("Password / App Key", type="password", key="smtp_pwd")
        recipients = st.text_area("Recipients (one per line)", key="smtp_to",
                                   placeholder="analyst@samvitti.com\ncompliance@samvitti.com")
        send_time = st.time_input("Daily send time (IST)", value=None, key="smtp_time")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Send Test Email", use_container_width=True):
            if not sender or not recipients:
                st.error("Fill in sender and recipients.")
            else:
                st.info("Email delivery requires a running scheduler. Configure APScheduler in production deployment.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Delivery Log</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card">
            <div style="text-align:center;padding:2rem 1rem;">
                <div style="font-size:32px;margin-bottom:8px;">📭</div>
                <div style="font-size:13px;color:rgba(255,255,255,0.3);">No deliveries yet.<br>Configure and send your first report.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
