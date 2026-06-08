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
                "Is_52W_High":   is_52w_high,
                "Is_52W_Low":    is_52w_low,
                "Vol_Confirmed": vol_ratio >= 1.5,
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


def get_sector(ticker: str, market: str) -> str:
    if market == "India (NSE)":
        return SECTOR_MAP_IN.get(ticker, "Other")
    return "—"


def assign_sectors(df: pd.DataFrame, market: str) -> pd.DataFrame:
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
