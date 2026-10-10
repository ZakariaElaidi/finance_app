"""Price data layer for the deal room.

No Streamlit imports here, so the pages AND scripts/update_prices.py can both use it.

Price sources, in order:
    1. Yahoo Finance (yfinance)         -> full OHLC history
    2. Google Finance page (scraped)    -> latest price only
    3. price_history.csv                -> last stored daily rows (written by update_prices.py)
    4. btp_market_data.csv              -> last manually stored price (final fallback)
"""
from __future__ import annotations

import re
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent
HISTORY_CSV = ROOT / "price_history.csv"
SNAPSHOT_CSV = ROOT / "btp_market_data.csv"
HISTORY_COLS = ["Date", "Company", "Open", "High", "Low", "Close"]

# Company name (as used in the app and in btp_market_data.csv) -> symbols per provider.
# "gf"    = Google Finance ticker on the Casablanca exchange (GF code CMA), already used by page 1.
# "yahoo" = Yahoo Finance symbol. These are best guesses: run scripts/update_prices.py once and
#           check the output. If a symbol returns nothing, fix it here (one line per company).
TICKERS = {
    "LafargeHolcim": {"gf": "LHM", "yahoo": "LHM.CS"},
    "Addoha": {"gf": "ADH", "yahoo": "ADH.CS"},
    "Alliances": {"gf": "ADI", "yahoo": "ADI.CS"},
    "Ciments du Maroc": {"gf": "CMA", "yahoo": "CMA.CS"},
    "TGCC": {"gf": "TGC", "yahoo": "TGC.CS"},
    "Sonasid": {"gf": "SND", "yahoo": "SND.CS"},
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------- providers
def fetch_yahoo_history(symbol: str, days: int = 200) -> pd.DataFrame | None:
    """Daily OHLC from Yahoo. Returns columns Date, Open, High, Low, Close, or None."""
    try:
        import yfinance as yf

        raw = yf.Ticker(symbol).history(
            start=date.today() - timedelta(days=days),
            end=date.today() + timedelta(days=1),
            auto_adjust=False,
        )
        if raw is None or raw.empty:
            return None
        df = raw.reset_index()
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None).dt.normalize()
        df = df[["Date", "Open", "High", "Low", "Close"]].dropna()
        return df if not df.empty else None
    except Exception:
        return None


def _parse_google_price(html: str) -> float | None:
    from bs4 import BeautifulSoup

    node = BeautifulSoup(html, "html.parser").find("div", class_="YMlKec fxKbKc")
    if not node:
        return None
    cleaned = re.sub(r"[^\d.]", "", node.text.replace(",", ""))
    try:
        val = float(cleaned)
    except ValueError:
        return None
    return val if val > 0 else None


def fetch_google_price(gf_ticker: str) -> float | None:
    """Latest price from the Google Finance quote page (direct, then via public proxy)."""
    url = f"https://www.google.com/finance/quote/{gf_ticker}:CMA"
    try:
        r = requests.get(url, headers=_HEADERS, timeout=8)
        if r.status_code == 200:
            val = _parse_google_price(r.text)
            if val:
                return val
    except Exception:
        pass
    try:
        proxy = f"https://api.allorigins.win/get?url={urllib.parse.quote(url)}"
        r = requests.get(proxy, timeout=8)
        if r.status_code == 200:
            return _parse_google_price(r.json().get("contents", ""))
    except Exception:
        pass
    return None


# ---------------------------------------------------------------- stored data
def load_history() -> pd.DataFrame:
    if not HISTORY_CSV.exists():
        return pd.DataFrame(columns=HISTORY_COLS)
    try:
        df = pd.read_csv(HISTORY_CSV, parse_dates=["Date"])
        return df[HISTORY_COLS]
    except Exception:
        return pd.DataFrame(columns=HISTORY_COLS)


def stored_history(company: str, days: int) -> pd.DataFrame:
    df = load_history()
    cutoff = pd.Timestamp(date.today() - timedelta(days=days))
    df = df[(df["Company"] == company) & (df["Date"] >= cutoff)]
    return df.sort_values("Date")[["Date", "Open", "High", "Low", "Close"]].reset_index(drop=True)


def snapshot_price(company: str) -> float | None:
    try:
        df = pd.read_csv(SNAPSHOT_CSV)
        row = df[df["Company"] == company]
        val = float(row["Price_MAD"].iloc[0]) if not row.empty else None
        return val if val and val > 0 else None
    except Exception:
        return None


# ---------------------------------------------------------------- public API for pages
def get_last_price(company: str) -> tuple[float | None, str]:
    """Returns (price_in_MAD, source) with source in live | stored | snapshot | none."""
    cfg = TICKERS.get(company)
    if cfg:
        y = fetch_yahoo_history(cfg["yahoo"], 10)
        if y is not None:
            return float(y["Close"].iloc[-1]), "live"
        p = fetch_google_price(cfg["gf"])
        if p:
            return p, "live"
    h = stored_history(company, 3650)
    if not h.empty:
        return float(h["Close"].iloc[-1]), "stored"
    p = snapshot_price(company)
    if p:
        return p, "snapshot"
    return None, "none"


def get_history(company: str, days: int) -> tuple[pd.DataFrame | None, str]:
    """Real daily OHLC in MAD, or (None, 'none'). Source is live | stored."""
    cfg = TICKERS.get(company)
    if cfg:
        y = fetch_yahoo_history(cfg["yahoo"], days + 5)
        if y is not None and len(y) >= 2:
            cutoff = pd.Timestamp(date.today() - timedelta(days=days))
            y = y[y["Date"] >= cutoff].reset_index(drop=True)
            if len(y) >= 2:
                return y, "live"
    h = stored_history(company, days)
    if len(h) >= 2:
        return h, "stored"
    return None, "none"


def simulate_history(anchor_price: float, days: int, seed_key: str) -> pd.DataFrame:
    """Random walk ending at anchor_price. ONLY a visual placeholder, never real data."""
    rng = np.random.default_rng(42 + len(seed_key) + days)
    vol = anchor_price * 0.02
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days)
    steps = rng.normal(0, vol, size=days)
    closes = anchor_price - np.cumsum(steps[::-1])[::-1]
    opens = closes - rng.normal(0, vol, size=days)
    highs = np.maximum(opens, closes) + np.abs(rng.normal(0, vol * 0.6, size=days))
    lows = np.minimum(opens, closes) - np.abs(rng.normal(0, vol * 0.6, size=days))
    return pd.DataFrame({"Date": dates, "Open": opens, "High": highs, "Low": lows, "Close": closes})


# ---------------------------------------------------------------- daily updater
def update_all(history_days: int = 10) -> list[dict]:
    """Fetch every company, upsert rows into price_history.csv, refresh Price_MAD in btp_market_data.csv."""
    hist = load_history()
    report, new_rows, last_close = [], [], {}

    for name, cfg in TICKERS.items():
        rows, source = fetch_yahoo_history(cfg["yahoo"], history_days), "yahoo"
        if rows is None:
            p = fetch_google_price(cfg["gf"])
            if p:
                rows = pd.DataFrame(
                    [{"Date": pd.Timestamp(date.today()), "Open": p, "High": p, "Low": p, "Close": p}]
                )
                source = "google"
        if rows is None:
            report.append({"company": name, "source": None, "rows": 0, "last_close": None})
            continue
        rows = rows.copy()
        rows.insert(1, "Company", name)
        new_rows.append(rows[HISTORY_COLS])
        last_close[name] = float(rows["Close"].iloc[-1])
        report.append({"company": name, "source": source, "rows": len(rows), "last_close": last_close[name]})

    if new_rows:
        merged = pd.concat([hist] + new_rows, ignore_index=True)
        merged["Date"] = pd.to_datetime(merged["Date"])
        merged = merged.drop_duplicates(["Date", "Company"], keep="last").sort_values(["Company", "Date"])
        merged["Date"] = merged["Date"].dt.strftime("%Y-%m-%d")
        merged.round(2).to_csv(HISTORY_CSV, index=False)

        snap = pd.read_csv(SNAPSHOT_CSV, dtype=str)
        for name, close in last_close.items():
            snap.loc[snap["Company"] == name, "Price_MAD"] = f"{close:.2f}"
        snap.to_csv(SNAPSHOT_CSV, index=False)

    return report
