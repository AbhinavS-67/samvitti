# Samvitti Capital — Market Intelligence Platform

A dark-themed, glassmorphism Streamlit dashboard for monitoring 52-week high/low breakouts across Indian (NSE) and US (S&P 500) markets.

## Setup

```bash
# 1. Clone / copy this folder
cd samvitti

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens at http://localhost:8501

## Pages

| Page | Description |
|------|-------------|
| Dashboard | KPI cards, top breakouts/breakdowns, sector heat chart, market pulse |
| Breakouts | Full 52W highs table with momentum score, RSI, volume flags, fundamentals |
| Breakdowns | 52W lows with reversal signals, scatter analysis |
| Sector Heatmap | Treemap + bar charts by sector |
| Report & Delivery | Generate PDF 1-pager, email configuration |
| Settings | Global filters, branding, cache control |

## Data
- Source: Yahoo Finance via `yfinance`
- India: Nifty 50 constituents (`.NS` suffix)
- US: S&P 500 sample (50 large caps)
- Cache: 30 minutes (configurable in Settings)
- 52W High: within 1.5% of 52-week high
- 52W Low: within 5% of 52-week low

## PDF Reports
Requires `reportlab`:
```bash
pip install reportlab
```

## Deployment (Streamlit Community Cloud)
1. Push to a GitHub repo
2. Go to share.streamlit.io
3. Connect repo, set main file to `app.py`
4. Add secrets in the Streamlit dashboard if using email delivery

---
SEBI PMS: INP000004847 | SEBI AIF: IN/AIF3/15-16/0182
© 2025 Samvitti Capital Pvt Ltd
