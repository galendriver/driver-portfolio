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

CACHE_FILE = Path(__file__).parent.parent / "data" / "prices-cache.json"
CACHE_TTL_SECONDS = 300  # 5 minutes — refresh if older than this

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


def fetch_yfinance(symbols: list[str]) -> dict[str, float]:
    """Fetch prices for a list of Yahoo Finance symbols."""
    if not symbols:
        return {}
    prices = {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        for sym in symbols:
            try:
                info = tickers.tickers[sym].fast_info
                price = info.last_price
                if price and price > 0:
                    prices[sym] = round(price, 6)
            except Exception:
                pass
    except Exception as e:
        print(f"  [yfinance error] {e}")
    return prices


def fetch_coingecko(cg_ids: list[str]) -> dict[str, float]:
    """Fetch prices from CoinGecko free API (no key required)."""
    if not cg_ids:
        return {}
    ids_param = ",".join(cg_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_param}&vs_currencies=usd"
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "financial-planner/1.0"})
        resp.raise_for_status()
        data = resp.json()
        return {cg_id: data[cg_id]["usd"] for cg_id in cg_ids if cg_id in data}
    except Exception as e:
        print(f"  [CoinGecko error] {e}")
        return {}


def fetch_all_prices(rows: list[dict], force_refresh: bool = False) -> dict:
    """
    Given the balances CSV rows, fetch all needed prices.
    Returns dict keyed by row identifier: {yf_symbol or cg_id: price_usd}
    Uses cache unless force_refresh=True or cache is stale.
    """
    if not force_refresh:
        cache = load_cache()
        if cache:
            return cache

    yf_symbols = []
    cg_ids = []

    for row in rows:
        yf = row.get("yf_symbol", "").strip()
        cg = row.get("cg_id", "").strip()
        shares_str = row.get("shares", "").strip()
        manual = row.get("manual_value", "").strip()

        # Only fetch price if we have shares (otherwise uses manual_value)
        if not shares_str or not float(shares_str) if shares_str else True:
            if not shares_str:
                continue

        if yf:
            yf_symbols.append(yf)
        elif cg:
            cg_ids.append(cg)

    yf_symbols = list(set(yf_symbols))
    cg_ids = list(set(cg_ids))

    prices = {}

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

    print(f"\n  {'Symbol':<25} {'Price (USD)':>15}")
    print(f"  {'─'*25} {'─'*15}")
    for sym, price in sorted(prices.items()):
        if sym in ("fetched_at", "fetched_at_human"):
            continue
        print(f"  {sym:<25} ${price:>14,.4f}")

    cached_at = prices.get("fetched_at_human", "unknown")
    print(f"\n  Prices as of: {cached_at}")
    print(f"  Cache TTL: {CACHE_TTL_SECONDS}s — run with --refresh to force update\n")
