#!/usr/bin/env python3
"""
Flask web server for Driver Portfolio viewer.
Imports price fetching logic from ../scripts/fetch_prices.py — no duplicate logic.

Run locally:  python3 -m flask --app web/server run
Production:   gunicorn web.server:app --bind 0.0.0.0:$PORT
"""

import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, date

from flask import Flask, jsonify, render_template

_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from fetch_prices import load_rows, fetch_all_prices, get_row_value  # noqa: E402

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

# ---------------------------------------------------------------------------
# YTD price fetching (cached — Jan 1 prices don't change after the fact)
# ---------------------------------------------------------------------------

_YTD_CACHE = Path(__file__).parent.parent / "data" / "ytd-prices-cache.json"
_THIS_YEAR  = date.today().year


def _load_ytd_cache():
    if _YTD_CACHE.exists():
        try:
            data = json.loads(_YTD_CACHE.read_text())
            if data.get("year") == _THIS_YEAR:
                return data.get("prices", {})
        except Exception:
            pass
    return None


def _save_ytd_cache(prices: dict):
    _YTD_CACHE.write_text(json.dumps({"year": _THIS_YEAR, "prices": prices}, indent=2))


def _fetch_ytd_yf(symbols: list) -> dict:
    """First available trading day of the year via Yahoo Finance."""
    if not symbols:
        return {}
    import yfinance as yf
    prices = {}
    start = f"{_THIS_YEAR}-01-01"
    end   = f"{_THIS_YEAR}-01-10"
    for sym in symbols:
        try:
            hist = yf.Ticker(sym).history(start=start, end=end)
            if not hist.empty:
                prices[sym] = float(hist["Close"].iloc[0])
        except Exception as e:
            print(f"  [ytd yf] {sym}: {e}")
    return prices


def _fetch_ytd_cg(cg_ids: list) -> dict:
    """Jan 1 price via CoinGecko historical API."""
    if not cg_ids:
        return {}
    prices = {}
    date_str = f"01-01-{_THIS_YEAR}"  # CoinGecko: DD-MM-YYYY
    for cg_id in cg_ids:
        try:
            url  = f"https://api.coingecko.com/api/v3/coins/{cg_id}/history?date={date_str}"
            resp = requests.get(url, timeout=15, headers={"User-Agent": "financial-planner/1.0"})
            data = resp.json()
            prices[cg_id] = float(data["market_data"]["current_price"]["usd"])
        except Exception as e:
            print(f"  [ytd cg] {cg_id}: {e}")
        time.sleep(1.2)  # CoinGecko free-tier rate limit
    return prices


def get_ytd_prices(rows: list) -> dict:
    cached = _load_ytd_cache()
    if cached is not None:
        return cached

    yf_syms, cg_ids = [], []
    for row in rows:
        if not (row.get("shares") or "").strip():
            continue
        yf  = (row.get("yf_symbol") or "").strip()
        cg  = (row.get("cg_id") or "").strip()
        if yf:
            yf_syms.append(yf)
        elif cg:
            cg_ids.append(cg)

    print(f"  Fetching YTD start prices ({_THIS_YEAR}-01-01)...")
    prices = {}
    prices.update(_fetch_ytd_yf(list(set(yf_syms))))
    prices.update(_fetch_ytd_cg(list(set(cg_ids))))
    _save_ytd_cache(prices)
    return prices


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/portfolio")
def portfolio():
    try:
        rows       = load_rows()
        prices     = fetch_all_prices(rows)
        ytd_prices = get_ytd_prices(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Enrich rows
    for row in rows:
        val, source = get_row_value(row, prices)
        row["_value"]        = val
        row["_price_source"] = source

    # Build positions + accumulate summary gain buckets
    positions = []

    def _gains_bucket():
        return {"ytd_start": 0.0, "ytd_cur": 0.0, "at_cost": 0.0, "at_cur": 0.0}

    g_total  = _gains_bucket()
    g_galen  = _gains_bucket()
    g_jaclyn = _gains_bucket()

    for row in rows:
        shares_str = (row.get("shares") or "").strip()
        shares     = float(shares_str) if shares_str else None
        yf_sym     = (row.get("yf_symbol") or "").strip()
        cg_id      = (row.get("cg_id") or "").strip()
        price_key  = yf_sym or cg_id
        owner      = row.get("owner", "")

        price = None
        if price_key and row["_price_source"] == "live":
            price = prices.get(price_key)

        # YTD
        ytd_gain = ytd_pct = ytd_start_value = None
        ytd_price = ytd_prices.get(price_key) if price_key else None
        if ytd_price and shares and price is not None:
            ytd_start_value = round(shares * ytd_price, 2)
            ytd_gain        = round(row["_value"] - ytd_start_value, 2)
            ytd_pct         = round(ytd_gain / ytd_start_value * 100, 2) if ytd_start_value else None
            for bucket in [g_total, (g_galen if owner == "galen" else g_jaclyn if owner == "jaclyn" else None)]:
                if bucket:
                    bucket["ytd_start"] += ytd_start_value
                    bucket["ytd_cur"]   += row["_value"]

        # All-time
        alltime_gain = alltime_pct = cost_basis = None
        cb_str = (row.get("cost_basis") or "").strip()
        if cb_str:
            try:
                cost_basis   = float(cb_str)
                alltime_gain = round(row["_value"] - cost_basis, 2)
                alltime_pct  = round(alltime_gain / cost_basis * 100, 2) if cost_basis else None
                for bucket in [g_total, (g_galen if owner == "galen" else g_jaclyn if owner == "jaclyn" else None)]:
                    if bucket:
                        bucket["at_cost"] += cost_basis
                        bucket["at_cur"]  += row["_value"]
            except ValueError:
                pass

        positions.append({
            "ticker":          row.get("ticker", ""),
            "description":     row.get("description", ""),
            "owner":           owner,
            "account":         row.get("account", ""),
            "asset_class":     row.get("asset_class", ""),
            "sector":          row.get("sector", ""),
            "shares":          shares,
            "price":           round(price, 4) if price is not None else None,
            "value":           round(row["_value"], 2),
            "price_source":    row["_price_source"],
            "ytd_start_value": ytd_start_value,
            "ytd_gain":        ytd_gain,
            "ytd_pct":         ytd_pct,
            "cost_basis":      cost_basis,
            "alltime_gain":    alltime_gain,
            "alltime_pct":     alltime_pct,
        })

    positions.sort(key=lambda x: x["value"], reverse=True)

    def _gain_summary(bucket):
        ytd_gain = at_gain = ytd_pct = at_pct = None
        if bucket["ytd_start"]:
            ytd_gain = round(bucket["ytd_cur"] - bucket["ytd_start"], 2)
            ytd_pct  = round(ytd_gain / bucket["ytd_start"] * 100, 2)
        if bucket["at_cost"]:
            at_gain = round(bucket["at_cur"] - bucket["at_cost"], 2)
            at_pct  = round(at_gain / bucket["at_cost"] * 100, 2)
        return {"ytd_gain": ytd_gain, "ytd_pct": ytd_pct, "alltime_gain": at_gain, "alltime_pct": at_pct}

    liquid_total = sum(
        r["_value"] for r in rows
        if r.get("asset_class") != "private_equity"
        and r.get("ticker") != "DBRX_UNVESTED"
    )

    last_updated = prices.get("fetched_at_human") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "last_updated": last_updated,
        "summary": {
            "total_portfolio": round(sum(r["_value"] for r in rows)),
            "galen_total":     round(sum(r["_value"] for r in rows if r.get("owner") == "galen")),
            "jaclyn_total":    round(sum(r["_value"] for r in rows if r.get("owner") == "jaclyn")),
            "liquid_total":    round(liquid_total),
            **{f"portfolio_{k}": v for k, v in _gain_summary(g_total).items()},
            **{f"galen_{k}": v for k, v in _gain_summary(g_galen).items()},
            **{f"jaclyn_{k}": v for k, v in _gain_summary(g_jaclyn).items()},
        },
        "positions": positions,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
