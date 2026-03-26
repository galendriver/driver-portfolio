#!/usr/bin/env python3
"""
Flask web server for Driver Portfolio viewer.
Imports price fetching logic from ../scripts/fetch_prices.py — no duplicate logic.

Run locally:  python3 -m flask --app web/server run
Production:   gunicorn web.server:app --bind 0.0.0.0:$PORT
"""

import csv
import sys
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime, date

from flask import Flask, jsonify, render_template, make_response

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
# Baseline (frozen pre-March-2026 snapshot)
# ---------------------------------------------------------------------------

_BASELINE_CSV = Path(__file__).parent.parent / "data" / "balances-baseline.csv"


def load_baseline_rows():
    with open(_BASELINE_CSV, newline="") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _merge_vested_positions(positions):
    """Server-side merge of vested positions sharing the same yf_symbol."""
    by_symbol = {}
    no_symbol = []

    for p in positions:
        sym = p.get("symbol")
        if not sym:
            no_symbol.append(p)
            continue
        if sym not in by_symbol:
            by_symbol[sym] = dict(p)
        else:
            m = by_symbol[sym]
            m["value"] = round(m["value"] + p["value"], 2)
            if p["shares"] is not None:
                m["shares"] = round((m["shares"] or 0) + p["shares"], 6)

            # Merge absolute gains; recompute pct from summed value
            for gain_k, pct_k in [("day_gain", "day_pct"), ("week_gain", "week_pct")]:
                if p[gain_k] is not None:
                    if m[gain_k] is not None:
                        m[gain_k] = round(m[gain_k] + p[gain_k], 2)
                        start = m["value"] - m[gain_k]
                        m[pct_k] = round(m[gain_k] / start * 100, 2) if start else None
                    else:
                        m[gain_k] = p[gain_k]
                        m[pct_k] = p[pct_k]

            if p["ytd_gain"] is not None:
                if m["ytd_gain"] is not None:
                    m["ytd_gain"] = round(m["ytd_gain"] + p["ytd_gain"], 2)
                    if p["ytd_start_value"] is not None and m["ytd_start_value"] is not None:
                        m["ytd_start_value"] = round(m["ytd_start_value"] + p["ytd_start_value"], 2)
                        m["ytd_pct"] = round(m["ytd_gain"] / m["ytd_start_value"] * 100, 2) if m["ytd_start_value"] else None
                else:
                    m["ytd_gain"] = p["ytd_gain"]
                    m["ytd_pct"] = p["ytd_pct"]
                    m["ytd_start_value"] = p["ytd_start_value"]

    return list(by_symbol.values()) + no_symbol


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

    positions          = []
    unvested_positions = []

    # Accumulators for portfolio-level gain summaries (vested only)
    day_start_total = day_cur_total = 0.0
    week_start_total = week_cur_total = 0.0
    ytd_start_total = ytd_cur_total = 0.0
    at_cost_total = at_cur_total = 0.0

    for row in rows:
        is_unvested = row.get("asset_class") == "unvested_rsu"

        shares_str = (row.get("shares") or "").strip()
        shares     = float(shares_str) if shares_str else None
        yf_sym     = (row.get("yf_symbol") or "").strip()
        cg_id      = (row.get("cg_id") or "").strip()
        price_key  = yf_sym or cg_id

        price = None
        if price_key and row["_price_source"] == "live":
            price = prices.get(price_key)

        # ── Day (prev close) ────────────────────────────────────
        day_gain = day_pct = None
        prev_price = prices.get(f"prev:{price_key}") if price_key else None
        if prev_price and shares and price is not None:
            day_start = round(shares * prev_price, 2)
            day_gain  = round(row["_value"] - day_start, 2)
            day_pct   = round(day_gain / day_start * 100, 2) if day_start else None
            if not is_unvested:
                day_start_total += day_start
                day_cur_total   += row["_value"]

        # ── Week (7 calendar days ago) ──────────────────────────
        week_gain = week_pct = None
        week_price = prices.get(f"week:{price_key}") if price_key else None
        if week_price and shares and price is not None:
            week_start = round(shares * week_price, 2)
            week_gain  = round(row["_value"] - week_start, 2)
            week_pct   = round(week_gain / week_start * 100, 2) if week_start else None
            if not is_unvested:
                week_start_total += week_start
                week_cur_total   += row["_value"]

        # ── YTD ────────────────────────────────────────────────
        ytd_gain = ytd_pct = ytd_start_value = None
        ytd_price = ytd_prices.get(price_key) if price_key else None
        if ytd_price and shares and price is not None:
            ytd_start_value = round(shares * ytd_price, 2)
            ytd_gain        = round(row["_value"] - ytd_start_value, 2)
            ytd_pct         = round(ytd_gain / ytd_start_value * 100, 2) if ytd_start_value else None
            if not is_unvested:
                ytd_start_total += ytd_start_value
                ytd_cur_total   += row["_value"]

        # ── All-time ────────────────────────────────────────────
        # cost_basis in CSV is per-share; multiply by shares for total.
        # For manual_value rows (no shares), skip — no meaningful basis.
        alltime_gain = alltime_pct = cost_basis = None
        cb_str = (row.get("cost_basis") or "").strip()
        if cb_str and shares is not None:
            try:
                cost_basis   = round(shares * float(cb_str), 2)
                alltime_gain = round(row["_value"] - cost_basis, 2)
                alltime_pct  = round(alltime_gain / cost_basis * 100, 2) if cost_basis else None
                if not is_unvested:
                    at_cost_total += cost_basis
                    at_cur_total  += row["_value"]
            except ValueError:
                pass

        pos = {
            "ticker":          row.get("ticker", ""),
            "description":     row.get("description", ""),
            "owner":           row.get("owner", ""),
            "account":         row.get("account", ""),
            "asset_class":     row.get("asset_class", ""),
            "sector":          row.get("sector", ""),
            "shares":          shares,
            "price":           round(price, 4) if price is not None else None,
            "value":           round(row["_value"], 2),
            "price_source":    row["_price_source"],
            "symbol":          price_key or None,
            "day_gain":        day_gain,
            "day_pct":         day_pct,
            "week_gain":       week_gain,
            "week_pct":        week_pct,
            "ytd_start_value": ytd_start_value,
            "ytd_gain":        ytd_gain,
            "ytd_pct":         ytd_pct,
            "cost_basis":      cost_basis,
            "alltime_gain":    alltime_gain,
            "alltime_pct":     alltime_pct,
        }

        if is_unvested:
            unvested_positions.append(pos)
        else:
            positions.append(pos)

    # Server-side merge of vested positions sharing the same yf_symbol
    positions = _merge_vested_positions(positions)
    positions.sort(key=lambda x: x["value"], reverse=True)

    # Portfolio-level gain summaries
    def _pct(cur, start):
        return round((cur - start) / start * 100, 2) if start else None

    liquid_total = sum(
        r["_value"] for r in rows
        if r.get("asset_class") not in ("private_equity", "unvested_rsu")
        and r.get("ticker") != "DBRX_UNVESTED"
    )

    total_portfolio = sum(
        r["_value"] for r in rows
        if r.get("asset_class") != "unvested_rsu"
    )

    last_updated = prices.get("fetched_at_human") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    resp = make_response(jsonify({
        "last_updated": last_updated,
        "summary": {
            "total_portfolio": round(total_portfolio),
            "liquid_total":    round(liquid_total),
            "day_gain":        round(day_cur_total - day_start_total, 2) if day_start_total else None,
            "day_pct":         _pct(day_cur_total, day_start_total),
            "week_gain":       round(week_cur_total - week_start_total, 2) if week_start_total else None,
            "week_pct":        _pct(week_cur_total, week_start_total),
            "ytd_gain":        round(ytd_cur_total - ytd_start_total, 2) if ytd_start_total else None,
            "ytd_pct":         _pct(ytd_cur_total, ytd_start_total),
            "alltime_gain":    round(at_cur_total - at_cost_total, 2) if at_cost_total else None,
            "alltime_pct":     _pct(at_cur_total, at_cost_total),
        },
        "positions":          positions,
        "unvested_positions": unvested_positions,
    }))
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/baseline")
def baseline():
    try:
        rows       = load_baseline_rows()
        prices     = fetch_all_prices(rows)
        ytd_prices = get_ytd_prices(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    total     = 0.0
    ytd_total = 0.0

    for r in rows:
        val, _ = get_row_value(r, prices)
        total += val

        shares_str = (r.get("shares") or "").strip()
        shares     = float(shares_str) if shares_str else None
        yf_sym     = (r.get("yf_symbol") or "").strip()
        cg_id      = (r.get("cg_id") or "").strip()
        price_key  = yf_sym or cg_id

        ytd_price = ytd_prices.get(price_key) if price_key else None
        if ytd_price and shares:
            ytd_total += shares * ytd_price

    ytd_gain = round(total - ytd_total) if ytd_total else None
    ytd_pct  = round((total - ytd_total) / ytd_total * 100, 2) if ytd_total else None

    resp = make_response(jsonify({
        "snapshot_date": "2026-03-11",
        "label":         "Pre-reallocation baseline",
        "total":         round(total),
        "ytd_total":     round(ytd_total),
        "ytd_gain":      ytd_gain,
        "ytd_pct":       ytd_pct,
    }))
    resp.headers["Cache-Control"] = "no-store"
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
