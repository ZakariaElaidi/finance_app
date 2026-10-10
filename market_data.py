"""Price data layer for the deal room.

No Streamlit imports here, so the pages AND scripts/update_prices.py can both use it.

How it works
    * scripts/update_prices.py (run daily by GitHub Actions) fetches prices and stores them in
      price_history.csv + btp_market_data.csv.
    * The Streamlit pages read the stored data first (fast, no network). Only if the stored data
      is missing or old do they try a live fetch.

Live sources, in order
    1. casased  -> Casablanca Stock Exchange daily data (Medias24 API), pip install casased
    2. Yahoo Finance (yfinance)
    3. Google Finance page (latest price only)
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
FRESH_DAYS = 4  # stored data older than this is considered stale (covers weekends)

# Company name (as used in the app and in btp_market_data.csv) -> identifiers per provider.
#   ids   = names/tickers to try in casased, in order (first one that returns data wins)
#   gf    = Google Finance ticker (exchange code CMA)
#   yahoo = Yahoo Finance symbol (may not exist for Casablanca)
# If the daily job log shows NO DATA for a company, fix the identifiers here: the log prints the
# errors and the names casased knows.
TICKERS = {
    "LafargeHolcim": {"ids": ["LHM", "LafargeHolcim", "Holcim Maroc", "LafargeHolcim Maroc"], "gf": "LHM", "yahoo": "LHM.CS"},
    "Addoha": {"ids": ["ADH", "Addoha"], "gf": "ADH", "yahoo": "ADH.CS"},
    "Alliances": {"ids": ["ADI", "Alliances"], "gf": "ADI", "yahoo": "ADI.CS"},
    "Ciments du Maroc": {"ids": ["CMA", "Ciments du Maroc"], "gf": "CMA", "yahoo": "CMA.CS"},
    "TGCC": {"ids": ["TGCC", "TGC"], "gf": "TGC", "yahoo": "TGC.CS"},
    "Sonasid": {"ids": ["SND", "Sonasid"], "gf": "SND", "yahoo": "SND.CS"},
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Accept-Language": "en-US,en;q=0.9",
}

ERRORS: list[str] = []  # provider failures, printed by scripts/update_prices.py


def _err(msg: str) -> None:
    ERRORS.append(msg[:300])


# ---------------------------------------------------------------- normalisation
def _normalize(df: pd.DataFrame | None) -> pd.DataFrame | None:
    """Any provider's table -> columns Date, Open, High, Low, Close (floats, sorted, one row per day)."""
    if df is None or len(df) == 0:
        return None
    d = df.copy()
    lowered = [str(c).lower() for c in d.columns]
    if "date" in lowered:
        d.columns = lowered
    else:  # date is the index
        d = d.reset_index()
        d.columns = ["date"] + [str(c).lower() for c in d.columns[1:]]

    def pick(*names):
        for n in names:
            if n in d.columns:
                return pd.to_numeric(d[n], errors="coerce")
        return None

    close = pick("close", "value", "adj close")
    if close is None:
        return None
    high, low, opn = pick("high", "max"), pick("low", "min"), pick("open")

    dates = pd.to_datetime(d["date"], errors="coerce")
    if dates.isna().mean() > 0.5:
        dates = pd.to_datetime(d["date"], errors="coerce", dayfirst=True)
    if getattr(dates.dt, "tz", None) is not None:
        dates = dates.dt.tz_localize(None)

    out = pd.DataFrame({"Date": dates.dt.normalize(), "Close": close})
    out["Open"] = opn if opn is not None else close.shift(1)  # no open from source -> previous close
    out["Open"] = out["Open"].fillna(out["Close"])
    out["High"] = high if high is not None else out[["Open", "Close"]].max(axis=1)
    out["Low"] = low if low is not None else out[["Open", "Close"]].min(axis=1)
    out["High"] = np.maximum(out["High"].fillna(out["Close"]), out[["Open", "Close"]].max(axis=1))
    out["Low"] = np.minimum(out["Low"].fillna(out["Close"]), out[["Open", "Close"]].min(axis=1))
    out = out.dropna(subset=["Date", "Close"])
    out = out[out["Close"] > 0].drop_duplicates("Date", keep="last").sort_values("Date")
    out = out[["Date", "Open", "High", "Low", "Close"]].reset_index(drop=True)
    return out if not out.empty else None


# ---------------------------------------------------------------- providers
def fetch_casased_history(identifier: str, days: int = 200) -> pd.DataFrame | None:
    """Daily data for one Casablanca stock via the casased package (Medias24 API)."""
    try:
        import casased as cas

        start = (date.today() - timedelta(days=days)).isoformat()
        raw = cas.get_history(identifier, start=start, end=date.today().isoformat())
        return _normalize(raw)
    except Exception as e:
        _err(f"casased/{identifier}: {type(e).__name__}: {e}")
        return None


def casased_names() -> list[str]:
    try:
        import casased as cas

        return [str(n) for n in cas.notation()]
    except Exception:
        return []


def fetch_yahoo_history(symbol: str, days: int = 200) -> pd.DataFrame | None:
    try:
        import yfinance as yf

        raw = yf.Ticker(symbol).history(
            start=date.today() - timedelta(days=days),
            end=date.today() + timedelta(days=1),
            auto_adjust=False,
        )
        if raw is None or raw.empty:
            _err(f"yahoo/{symbol}: empty result (symbol probably not covered)")
            return None
        return _normalize(raw.reset_index())
    except Exception as e:
        _err(f"yahoo/{symbol}: {type(e).__name__}: {e}")
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
        else:
            _err(f"google/{gf_ticker}: HTTP {r.status_code}")
    except Exception as e:
        _err(f"google/{gf_ticker}: {type(e).__name__}: {e}")
    try:
        proxy = f"https://api.allorigins.win/get?url={urllib.parse.quote(url)}"
        r = requests.get(proxy, timeout=8)
        if r.status_code == 200:
            val = _parse_google_price(r.json().get("contents", ""))
            if val:
                return val
    except Exception as e:
        _err(f"google-proxy/{gf_ticker}: {type(e).__name__}: {e}")
    return None


def fetch_live_history(company: str, days: int) -> tuple[pd.DataFrame | None, str | None]:
    """Try each live provider for real daily OHLC. Returns (df, provider_name)."""
    cfg = TICKERS.get(company)
    if not cfg:
        return None, None
    for ident in cfg["ids"]:
        df = fetch_casased_history(ident, days)
        if df is not None:
            return df, "casased"
    df = fetch_yahoo_history(cfg["yahoo"], days)
    if df is not None:
        return df, "yahoo"
    return None, None


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


def _is_fresh(df: pd.DataFrame) -> bool:
    return not df.empty and df["Date"].iloc[-1] >= pd.Timestamp(date.today() - timedelta(days=FRESH_DAYS))


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
    """(price_in_MAD, source). source: stored (fresh) | live | stale | snapshot | none."""
    h = stored_history(company, 3650)
    if _is_fresh(h):
        return float(h["Close"].iloc[-1]), "stored"
    live, _ = fetch_live_history(company, 10)
    if live is not None:
        return float(live["Close"].iloc[-1]), "live"
    cfg = TICKERS.get(company)
    if cfg:
        p = fetch_google_price(cfg["gf"])
        if p:
            return p, "live"
    if not h.empty:
        return float(h["Close"].iloc[-1]), "stale"
    p = snapshot_price(company)
    if p:
        return p, "snapshot"
    return None, "none"


def get_history(company: str, days: int) -> tuple[pd.DataFrame | None, str]:
    """Real daily OHLC in MAD, or (None, 'none'). source: stored | live | stale."""
    h = stored_history(company, days)
    covers_range = not h.empty and h["Date"].iloc[0] <= pd.Timestamp(date.today() - timedelta(days=days - 7))
    if len(h) >= 2 and _is_fresh(h) and covers_range:
        return h, "stored"
    live, _ = fetch_live_history(company, days + 5)
    if live is not None:
        cutoff = pd.Timestamp(date.today() - timedelta(days=days))
        live = live[live["Date"] >= cutoff].reset_index(drop=True)
        if len(live) >= 2:
            return live, "live"
    if len(h) >= 2:
        return h, "stored" if _is_fresh(h) else "stale"
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
def update_all(incremental_days: int = 10, backfill_days: int = 200) -> list[dict]:
    """Fetch every company, upsert rows into price_history.csv, refresh Price_MAD in btp_market_data.csv.

    A company with little stored history gets a long backfill; otherwise only the last few days.
    """
    ERRORS.clear()
    hist = load_history()
    report, new_rows, last_close = [], [], {}

    for name, cfg in TICKERS.items():
        have = int((hist["Company"] == name).sum())
        days = backfill_days if have < 60 else incremental_days
        rows, source = fetch_live_history(name, days)
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

    if len(last_close) < len(TICKERS):
        names = casased_names()
        if names:
            _err("casased knows these names (use them in TICKERS ids): " + ", ".join(names[:150]))

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
