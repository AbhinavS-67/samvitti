import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

# ── Index Constituents ──────────────────────────────────────────────────────

NIFTY50 = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","BHARTIARTL.NS","ICICIBANK.NS",
    "INFOSYS.NS","SBIN.NS","HINDUNILVR.NS","ITC.NS","WIPRO.NS",
    "AXISBANK.NS","KOTAKBANK.NS","LT.NS","BAJFINANCE.NS","ONGC.NS",
    "ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","NESTLEIND.NS",
    "HCLTECH.NS","POWERGRID.NS","NTPC.NS","TECHM.NS","ULTRACEMCO.NS",
    "JSWSTEEL.NS","GRASIM.NS","BAJAJFINSV.NS","COALINDIA.NS","ADANIENT.NS",
    "ADANIPORTS.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS","EICHERMOT.NS",
    "HEROMOTOCO.NS","TATAMOTORS.NS","TATACONSUM.NS","M&M.NS","SBILIFE.NS",
    "HDFCLIFE.NS","INDUSINDBK.NS","APOLLOHOSP.NS","BRITANNIA.NS","BPCL.NS",
    "TATASTEEL.NS","HINDALCO.NS","UPL.NS","SHRIRAMFIN.NS","BEL.NS",
]

SP500_SAMPLE = [
    "AAPL","MSFT","NVDA","GOOGL","AMZN","META","TSLA","AVGO","JPM","LLY",
    "V","UNH","XOM","MA","JNJ","HD","PG","COST","ABBV","MRK",
    "AMD","CVX","NFLX","CRM","BAC","PEP","TMO","ADBE","ACN","CSCO",
    "ABT","WFC","DHR","TXN","LIN","PM","MCD","NEE","HON","AMGN",
    "ORCL","INTC","CAT","IBM","GE","BA","MMM","GS","MS","BLK",
]

NIFTY_NEXT_50 = [
    "HAL.NS", "TATAPOWER.NS", "IOC.NS", "PFC.NS", "REC.NS", "DLF.NS", 
    "CHOLAFIN.NS", "SIEMENS.NS", "GAIL.NS", "VEDL.NS", "SHREECEM.NS", 
    "HAVELLS.NS", "TRENT.NS", "AMBUJACEM.NS", "PNB.NS", "ABB.NS", 
    "ICICIPRULI.NS", "LICI.NS", "DMART.NS", "TATACOMM.NS", "COLPAL.NS", 
    "MCDOWELL-N.NS", "SRF.NS", "MARICO.NS", "CANBK.NS", "BANKBARODA.NS", 
    "BERGEPAINT.NS", "GODREJCP.NS", "PIDILITIND.NS", "ICICIGI.NS", "INDIGO.NS", 
    "IRCTC.NS", "MOTHERSON.NS", "PAGEIND.NS", "ZOMATO.NS", "JIOFIN.NS", 
    "BOSCHLTD.NS", "ADANIENSOL.NS", "ADANIGREEN.NS", "MUTHOOTFIN.NS"
]

NIFTY_MIDCAP_100 = [
    "POLYCAB.NS", "KEI.NS", "SUZLON.NS", "AUBANK.NS", "FEDERALBNK.NS", 
    "MRF.NS", "IPCALAB.NS", "BATAINDIA.NS", "COFORGE.NS", "PERSISTENT.NS", 
    "DIXON.NS", "MAXHEALTH.NS", "VOLTAS.NS", "BHEL.NS", "GMRINFRA.NS", 
    "TATAELXSI.NS", "ASHOKLEY.NS", "IRFC.NS", "RVNL.NS", "YESBANK.NS", 
    "OBEROIRLTY.NS", "LUPIN.NS", "CONCOR.NS", "DALBHARAT.NS", "ESCORTS.NS", 
    "HINDPETRO.NS", "IDFCFIRSTB.NS", "NMDC.NS", "OIL.NS", 
    "PETRONET.NS", "SJVN.NS", "TATACOMM.NS", "TVSMOTOR.NS", "UNIONBANK.NS"
]

NIFTY_SMALLCAP_100 = [
    "RITES.NS", "IRCON.NS", "HUDCO.NS", "CENTURYTEX.NS", "RADICO.NS", 
    "MCX.NS", "CDSL.NS", "BSE.NS", "ANGELONE.NS", "SUVENPHAR.NS", 
    "MAHABANK.NS", "KARURVYSYA.NS", "CESC.NS", "NLCINDIA.NS", "CYIENT.NS", 
    "SONATSOFTW.NS", "PPLPHARMA.NS", "CAMS.NS", "KEC.NS", "MANAPPURAM.NS", 
    "GLENMARK.NS", "HFCL.NS", "IOB.NS", "ITI.NS", "J&KBANK.NS", "PNBHOUSING.NS", 
    "Centralbank.NS", "POONAWALLA.NS", "RAMCOCEM.NS", "TATAINVEST.NS"
]

NIFTY_BANK = [
    "HDFCBANK.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "SBIN.NS", 
    "INDUSINDBK.NS", "PNB.NS", "BANKBARODA.NS", "FEDERALBNK.NS", 
    "IDFCFIRSTB.NS", "AUBANK.NS", "BANDHANBNK.NS"
]

NIFTY_IT = [
    "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", 
    "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "KPITTECH.NS"
]

NIFTY_AUTO = [
    "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", 
    "BAJAJ-AUTO.NS", "TVSMOTOR.NS", "TIINDIA.NS", "ASHOKLEY.NS", "BHARATFORG.NS", 
    "BALKRISIND.NS", "BOSCHLTD.NS", "SAMVARDHNA.NS", "SONACOMS.NS"
]

NIFTY_METAL = [
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "VEDL.NS", 
    "NMDC.NS", "SAIL.NS", "HINDZINC.NS", "JSL.NS", "NATIONALUM.NS", 
    "HINDCOPPER.NS", "WELCORP.NS", "APLAPOLLO.NS", "RATNAMANI.NS"
]

NIFTY_PHARMA = [
    "SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", 
    "LUPIN.NS", "AUROPHARMA.NS", "ALKEM.NS", "GLAND.NS", "LAURUSLABS.NS", 
    "ZYDUSLIFE.NS", "BIOCON.NS", "IPCALAB.NS", "SYNGENE.NS", "GLENMARK.NS", 
    "TORNTPHARM.NS", "GRANULES.NS", "ABBOTINDIA.NS", "JBCHEPHARM.NS"
]

INDICES_MAP = {
    "Nifty 50": NIFTY50,
    "Nifty Next 50": NIFTY_NEXT_50,
    "Nifty Midcap 100": NIFTY_MIDCAP_100,
    "Nifty Smallcap 100": NIFTY_SMALLCAP_100,
    "Nifty Bank": NIFTY_BANK,
    "Nifty IT": NIFTY_IT,
    "Nifty Auto": NIFTY_AUTO,
    "Nifty Metal": NIFTY_METAL,
    "Nifty Pharma": NIFTY_PHARMA,
    "US (S&P 500)": SP500_SAMPLE,
}

SECTOR_MAP_IN = {
    "RELIANCE.NS":"Energy","ONGC.NS":"Energy","BPCL.NS":"Energy","COALINDIA.NS":"Energy",
    "POWERGRID.NS":"Utilities","NTPC.NS":"Utilities",
    "TCS.NS":"IT","INFOSYS.NS":"IT","WIPRO.NS":"IT","HCLTECH.NS":"IT","TECHM.NS":"IT",
    "HDFCBANK.NS":"Financials","ICICIBANK.NS":"Financials","SBIN.NS":"Financials",
    "AXISBANK.NS":"Financials","KOTAKBANK.NS":"Financials","BAJFINANCE.NS":"Financials",
    "BAJAJFINSV.NS":"Financials","INDUSINDBK.NS":"Financials","SBILIFE.NS":"Financials",
    "HDFCLIFE.NS":"Financials","SHRIRAMFIN.NS":"Financials",
    "SUNPHARMA.NS":"Healthcare","DRREDDY.NS":"Healthcare","CIPLA.NS":"Healthcare",
    "DIVISLAB.NS":"Healthcare","APOLLOHOSP.NS":"Healthcare",
    "HINDUNILVR.NS":"FMCG","ITC.NS":"FMCG","NESTLEIND.NS":"FMCG",
    "BRITANNIA.NS":"FMCG","TATACONSUM.NS":"FMCG",
    "MARUTI.NS":"Auto","TATAMOTORS.NS":"Auto","M&M.NS":"Auto",
    "EICHERMOT.NS":"Auto","HEROMOTOCO.NS":"Auto",
    "LT.NS":"Infra","ADANIPORTS.NS":"Infra","BEL.NS":"Infra","ADANIENT.NS":"Infra",
    "JSWSTEEL.NS":"Metals","TATASTEEL.NS":"Metals","HINDALCO.NS":"Metals",
    "GRASIM.NS":"Cement","ULTRACEMCO.NS":"Cement",
    "ASIANPAINT.NS":"Consumer","TITAN.NS":"Consumer",
}


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_stock_data(tickers: list, period: str = "1y") -> pd.DataFrame:
    """Download OHLCV + compute 52W hi/lo, RSI, momentum score."""
    if not tickers:
        return pd.DataFrame()
    try:
        raw = yf.download(
            tickers, period=period, auto_adjust=True,
            group_by="ticker", threads=True, progress=False
        )
    except Exception:
        return pd.DataFrame()

    records = []
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                df = raw.copy()
            else:
                df = raw[ticker].copy()

            df = df.dropna(subset=["Close"])
            if len(df) < 50:
                continue

            close = df["Close"]
            high  = df["High"]
            low   = df["Low"]
            vol   = df["Volume"]

            w52_high = high.rolling(252, min_periods=200).max().iloc[-1]
            w52_low  = low.rolling(252, min_periods=200).min().iloc[-1]
            curr     = close.iloc[-1]
            avg_vol  = vol.rolling(20).mean().iloc[-1]
            curr_vol = vol.iloc[-1]

            # RSI-14
            delta   = close.diff()
            gain    = delta.clip(lower=0).rolling(14).mean()
            loss    = (-delta.clip(upper=0)).rolling(14).mean()
            rs      = gain / loss.replace(0, np.nan)
            rsi     = (100 - (100 / (1 + rs))).iloc[-1]

            # Momentum: % from 52W low relative to range
            rng = w52_high - w52_low
            momentum = ((curr - w52_low) / rng * 100) if rng > 0 else 50.0

            # Distance from 52W high/low
            pct_from_high = (curr - w52_high) / w52_high * 100
            pct_from_low  = (curr - w52_low)  / w52_low  * 100

            # Volume signal
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0

            # 1-month return
            ret_1m = (curr / close.iloc[-21] - 1) * 100 if len(close) > 21 else 0.0
            ret_5d = (curr / close.iloc[-6]  - 1) * 100 if len(close) > 6  else 0.0
            ret_1d = (curr / close.iloc[-2]  - 1) * 100 if len(close) > 1  else 0.0

            # 50 DMA
            ma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else curr
            is_above_ma50 = bool(curr > ma50)

            is_52w_high = pct_from_high >= -1.5   # within 1.5% of 52W high
            is_52w_low  = pct_from_low  <= 5.0    # within 5% of 52W low

            records.append({
                "Ticker":        ticker.replace(".NS",""),
                "Full_Ticker":   ticker,
                "Price":         round(curr, 2),
                "52W_High":      round(w52_high, 2),
                "52W_Low":       round(w52_low, 2),
                "Pct_From_High": round(pct_from_high, 2),
                "Pct_From_Low":  round(pct_from_low, 2),
                "RSI":           round(rsi, 1),
                "Momentum":      round(momentum, 1),
                "Vol_Ratio":     round(vol_ratio, 2),
                "Ret_1M":        round(ret_1m, 2),
                "Ret_5D":        round(ret_5d, 2),
                "Ret_1D":        round(ret_1d, 2),
                "Is_52W_High":   is_52w_high,
                "Is_52W_Low":    is_52w_low,
                "Vol_Confirmed": vol_ratio >= 1.5,
                "MA50":          round(ma50, 2),
                "Above_MA50":    is_above_ma50,
            })
        except Exception:
            continue

    return pd.DataFrame(records)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fundamentals(ticker: str) -> dict:
    """Pull P/E, P/B, D/E from yfinance info."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "pe_ratio":   info.get("trailingPE",    None),
            "pb_ratio":   info.get("priceToBook",   None),
            "de_ratio":   info.get("debtToEquity",  None),
            "market_cap": info.get("marketCap",     None),
            "sector":     info.get("sector",        "—"),
            "name":       info.get("longName",       ticker),
        }
    except Exception:
        return {}


def get_active_tickers() -> list:
    """Return the list of tickers to fetch based on current session state scope."""
    scope = st.session_state.get("data_scope", "Market Indices")
    if scope == "Custom Search":
        return st.session_state.get("custom_tickers", ["RELIANCE.NS", "AAPL", "MSFT", "TCS.NS"])
    else:
        active_index = st.session_state.get("active_index", "Nifty 50")
        if active_index == "Both (NSE + S&P 500)":
            return NIFTY50 + SP500_SAMPLE
        return INDICES_MAP.get(active_index, NIFTY50)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_index_data() -> dict:
    """Fetch live price and daily changes for key indices: Nifty 50, Sensex, Nifty Bank, India VIX."""
    indices = {
        "Nifty 50": "^NSEI",
        "SENSEX": "^BSESN",
        "Nifty Bank": "^NSEBANK",
        "India VIX": "^INDIAVIX"
    }
    results = {}
    for label, ticker in indices.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if len(hist) >= 2:
                curr = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2]
                change = curr - prev
                pct = (change / prev) * 100
                results[label] = {
                    "price": curr,
                    "change": change,
                    "pct": pct
                }
            else:
                results[label] = {"price": 0.0, "change": 0.0, "pct": 0.0}
        except Exception:
            results[label] = {"price": 0.0, "change": 0.0, "pct": 0.0}
    return results


def get_sector(ticker: str, market: str) -> str:
    if market == "India (NSE)":
        return SECTOR_MAP_IN.get(ticker, "Other")
    return "—"


def assign_sectors(df: pd.DataFrame, market: str) -> pd.DataFrame:
    scope = st.session_state.get("data_scope", "Market Indices")
    if scope == "Custom Search":
        df["Sector"] = df["Full_Ticker"].apply(
            lambda t: SECTOR_MAP_IN.get(t, "Other/Custom") if t.endswith(".NS") else "US/Custom"
        )
    else:
        if market == "India (NSE)":
            df["Sector"] = df["Full_Ticker"].map(SECTOR_MAP_IN).fillna("Other")
        else:
            df["Sector"] = "—"
    return df


def compute_sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Returns sector-level counts of highs vs lows."""
    if df.empty or "Sector" not in df.columns:
        return pd.DataFrame()
    return df.groupby("Sector").agg(
        Total=("Ticker","count"),
        Highs=("Is_52W_High","sum"),
        Lows=("Is_52W_Low","sum"),
        Avg_Momentum=("Momentum","mean"),
        Avg_RSI=("RSI","mean"),
    ).reset_index().sort_values("Total", ascending=False)


def score_label(score: float) -> str:
    if score >= 80: return "Strong"
    if score >= 60: return "Moderate"
    if score >= 40: return "Neutral"
    return "Weak"


def fmt_cap(cap):
    if cap is None: return "—"
    if cap >= 1e12: return f"₹{cap/1e12:.1f}T"
    if cap >= 1e9:  return f"₹{cap/1e9:.1f}B"
    if cap >= 1e6:  return f"₹{cap/1e6:.1f}M"
    return str(cap)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_screener_details(ticker: str) -> dict:
    """Fetch cached business details and news for the screener card view."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        news = t.news
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "Other"),
            "summary": info.get("longBusinessSummary", "No business summary available."),
            "news": news
        }
    except Exception:
        return {
            "name": ticker,
            "sector": "Other",
            "summary": "Business description not available.",
            "news": []
        }
