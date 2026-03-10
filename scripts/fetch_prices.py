#!/usr/bin/env python3
"""
Live price fetcher — Yahoo Finance (stocks) + CoinGecko (crypto).
Called automatically by check_allocations.py; can also run standalone.

Usage: python scripts/fetch_prices.py
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    print("Missing dependency: pip3 install yfinance")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Missing dependency: pip3 install requests")
    sys.exit(1)

CACHE_FILE      = Path(__file__).parent.parent / "data" / "prices-cache.json"
WEEK_CACHE_FILE = Path(__file__).parent.parent / "data" / "week-prices-cache.json"
CACHE_TTL_SECONDS      = 300       # 5 minutes
WEEK_CACHE_TTL_SECONDS = 6 * 3600  # 6 hours

# Google Sheet (set to "Anyone with link can view")
GSHEET_ID = "1CmjrabBz4eDvy5sSvX-2pi9NRcZFwzU74oe6w-88G-k"
GSHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/export?format=csv"
LOCAL_BALANCES = Path(__file__).parent.parent / "data" / "balances.csv"


def load_rows(use_sheet: bool = True) -> list[dict]:
    """
    Load balances rows from Google Sheet (default) or local CSV fallback.
    """
    import csv, io
    if use_sheet:
        try:
            resp = requests.get(GSHEET_CSV_URL, timeout=10)
            resp.raise_for_status()
            reader = csv.DictReader(io.StringIO(resp.text))
            rows = list(reader)
            print(f"  Loaded {len(rows)} rows from Google Sheet")
            return rows
        except Exception as e:
            print(f"  [warn] Google Sheet fetch failed ({e}), falling back to local CSV")
    with open(LOCAL_BALANCES, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"  Loaded {len(rows)} rows from local CSV")
    return rows


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
            age = time.time() - data.get("fetched_at", 0)
            if age < CACHE_TTL_SECONDS:
                return data
        except Exception:
            pass
    return {}


def save_cache(prices: dict):
    prices["fetched_at"] = time.time()
    prices["fetched_at_human"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    CACHE_FILE.write_text(json.dumps(prices, indent=2))


def load_week_cache() -> dict:
    if WEEK_CACHE_FILE.exists():
        try:
            data = json.loads(WEEK_CACHE_FILE.read_text())
            age = time.time() - data.get("fetched_at", 0)
            if age < WEEK_CACHE_TTL_SECONDS:
                return data
        except Exception:
            pass
    return {}


def save_week_cache(prices: dict):
    prices["fetched_at"] = time.time()
    WEEK_CACHE_FILE.write_text(json.dumps(prices, indent=2))


# ---------------------------------------------------------------------------
# Yahoo Finance
# ---------------------------------------------------------------------------

def fetch_yfinance(symbols: list[str]) -> dict[str, float]:
    """Fetch current prices + prev_close for a list of Yahoo Finance symbols."""
    if not symbols:
        return {}
    prices = {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        for sym in symbols:
            try:
                info = tickers.tickers[sym].fast_info
                price = info.last_price
                prev  = getattr(info, "previous_close", None)
                if price and price > 0:
                    prices[sym] = round(price, 6)
                if prev and prev > 0:
                    prices[f"prev:{sym}"] = round(prev, 6)
            except Exception:
                pass
    except Exception as e:
        print(f"  [yfinance error] {e}")
    return prices


def fetch_yfinance_week_ago(symbols: list[str]) -> dict[str, float]:
    """Fetch price from ~7 calendar days ago (≈5 trading days) via daily history."""
    if not symbols:
        return {}
    prices = {}
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(period="12d", interval="1d")
            if hist.empty:
                continue
            closes = hist["Close"].dropna()
            if len(closes) >= 6:
                prices[f"week:{sym}"] = round(float(closes.iloc[-6]), 6)
            elif len(closes) >= 1:
                prices[f"week:{sym}"] = round(float(closes.iloc[0]), 6)
        except Exception as e:
            print(f"  [week yf] {sym}: {e}")
    return prices


# ---------------------------------------------------------------------------
# CoinGecko
# ---------------------------------------------------------------------------

def fetch_coingecko(cg_ids: list[str]) -> dict[str, float]:
    """Fetch current prices + approx prev_close (24h ago) from CoinGecko."""
    if not cg_ids:
        return {}
    ids_param = ",".join(cg_ids)
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids_param}&vs_currencies=usd&include_24hr_change=true"
    )
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "financial-planner/1.0"})
        resp.raise_for_status()
        data = resp.json()
        prices = {}
        for cg_id in cg_ids:
            if cg_id not in data:
                continue
            current   = data[cg_id]["usd"]
            change_24 = data[cg_id].get("usd_24h_change")
            prices[cg_id] = current
            if change_24 is not None:
                # back-calculate price 24h ago
                denom = 1 + change_24 / 100
                if denom != 0:
                    prices[f"prev:{cg_id}"] = round(current / denom, 6)
        return prices
    except Exception as e:
        print(f"  [CoinGecko error] {e}")
        return {}


def fetch_coingecko_week_ago(cg_ids: list[str]) -> dict[str, float]:
    """Fetch price from ~7 days ago via CoinGecko market_chart endpoint."""
    if not cg_ids:
        return {}
    prices = {}
    for cg_id in cg_ids:
        try:
            url  = (
                f"https://api.coingecko.com/api/v3/coins/{cg_id}"
                f"/market_chart?vs_currency=usd&days=7&interval=daily"
            )
            resp = requests.get(url, timeout=15, headers={"User-Agent": "financial-planner/1.0"})
            data = resp.json()
            price_data = data.get("prices", [])
            if price_data:
                prices[f"week:{cg_id}"] = round(float(price_data[0][1]), 6)
        except Exception as e:
            print(f"  [week cg] {cg_id}: {e}")
        time.sleep(1.2)  # CoinGecko free-tier rate limit
    return prices


# ---------------------------------------------------------------------------
# Main fetch
# ---------------------------------------------------------------------------

def fetch_all_prices(rows: list[dict], force_refresh: bool = False) -> dict:
    """
    Given the balances CSV rows, fetch all needed prices.
    Returns flat dict keyed by symbol:
      {sym: current_price, "prev:{sym}": prev_close, "week:{sym}": week_ago_price, ...}
    Uses cache unless force_refresh=True or cache is stale.
    """
    if not force_refresh:
        cache = load_cache()
        if cache:
            # Merge in week cache if available
            week_cache = load_week_cache()
            if week_cache:
                cache.update({k: v for k, v in week_cache.items() if k != "fetched_at"})
            return cache

    yf_symbols = []
    cg_ids     = []

    for row in rows:
        yf  = row.get("yf_symbol", "").strip()
        cg  = row.get("cg_id", "").strip()
        shares_str = row.get("shares", "").strip()

        if not shares_str:
            continue

        if yf:
            yf_symbols.append(yf)
        elif cg:
            cg_ids.append(cg)

    yf_symbols = list(set(yf_symbols))
    cg_ids     = list(set(cg_ids))

    prices = {}

    # Current + prev_close prices
    if yf_symbols:
        print(f"  Fetching {len(yf_symbols)} stock prices from Yahoo Finance...")
        yf_prices = fetch_yfinance(yf_symbols)
        prices.update(yf_prices)
        for sym in yf_symbols:
            if sym not in yf_prices:
                print(f"  [warn] No price returned for {sym}")

    if cg_ids:
        print(f"  Fetching {len(cg_ids)} crypto prices from CoinGecko...")
        cg_prices = fetch_coingecko(cg_ids)
        prices.update(cg_prices)
        for cg_id in cg_ids:
            if cg_id not in cg_prices:
                print(f"  [warn] No price returned for {cg_id}")

    save_cache(prices)

    # Week-ago prices (separate longer-lived cache)
    week_cache = load_week_cache()
    if not week_cache:
        week_prices = {}
        if yf_symbols:
            print(f"  Fetching week-ago stock prices from Yahoo Finance...")
            week_prices.update(fetch_yfinance_week_ago(yf_symbols))
        if cg_ids:
            print(f"  Fetching week-ago crypto prices from CoinGecko...")
            week_prices.update(fetch_coingecko_week_ago(cg_ids))
        if week_prices:
            save_week_cache(week_prices)
        week_cache = week_prices

    prices.update({k: v for k, v in week_cache.items() if k != "fetched_at"})

    return prices


def get_row_value(row: dict, prices: dict) -> tuple[float, str]:
    """
    Compute dollar value for a single CSV row.
    Returns (value, source) where source is 'live', 'manual', or 'missing'.
    """
    shares_str = row.get("shares", "").strip()
    manual_str = row.get("manual_value", "").strip()
    yf_sym = row.get("yf_symbol", "").strip()
    cg_id = row.get("cg_id", "").strip()

    # Manual value (no shares) — private equity, 401k funds
    if manual_str and not shares_str:
        return float(manual_str), "manual"

    if not shares_str:
        return 0.0, "missing"

    shares = float(shares_str)
    if shares == 0:
        return 0.0, "zero"

    # Look up price
    price = None
    if yf_sym and yf_sym in prices:
        price = prices[yf_sym]
    elif cg_id and cg_id in prices:
        price = prices[cg_id]

    if price is not None:
        return round(shares * price, 2), "live"

    # Fallback to manual_value if live price unavailable
    if manual_str:
        return float(manual_str), "manual-fallback"

    return 0.0, "missing"


if __name__ == "__main__":
    import csv
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--balances", default="data/balances.csv")
    parser.add_argument("--refresh", action="store_true", help="Force refresh (ignore cache)")
    args = parser.parse_args()

    filepath = Path(args.balances)
    if not filepath.exists():
        filepath = Path(__file__).parent.parent / args.balances

    rows = []
    with open(filepath, newline="") as f:
        rows = list(csv.DictReader(f))

    prices = fetch_all_prices(rows, force_refresh=args.refresh)

    print(f"\n  {'Symbol':<30} {'Price (USD)':>15}")
    print(f"  {'─'*30} {'─'*15}")
    for sym, price in sorted(prices.items()):
        if sym in ("fetched_at", "fetched_at_human"):
            continue
        print(f"  {sym:<30} ${price:>14,.4f}")

    cached_at = prices.get("fetched_at_human", "unknown")
    print(f"\n  Prices as of: {cached_at}")
    print(f"  Cache TTL: {CACHE_TTL_SECONDS}s — run with --refresh to force update\n")
