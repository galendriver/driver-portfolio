#!/usr/bin/env python3
"""
Flask web server for Driver Portfolio viewer.
Imports price fetching logic from ../scripts/fetch_prices.py — no duplicate logic.

Run locally:  flask --app web/server run
Production:   gunicorn web.server:app --bind 0.0.0.0:$PORT
"""

import sys
import os
from pathlib import Path
from datetime import datetime

from flask import Flask, jsonify, render_template

# Add scripts directory to path so we can import fetch_prices
_SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

from fetch_prices import load_rows, fetch_all_prices, get_row_value  # noqa: E402

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/portfolio")
def portfolio():
    try:
        rows = load_rows()
        prices = fetch_all_prices(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Enrich each row with computed value and price source
    for row in rows:
        val, source = get_row_value(row, prices)
        row["_value"] = val
        row["_price_source"] = source

    # Summary totals
    total_portfolio = sum(r["_value"] for r in rows)
    galen_total = sum(r["_value"] for r in rows if r.get("owner") == "galen")
    jaclyn_total = sum(r["_value"] for r in rows if r.get("owner") == "jaclyn")
    liquid_total = sum(
        r["_value"] for r in rows
        if r.get("asset_class") != "private_equity"
        and r.get("ticker") != "DBRX_UNVESTED"
    )

    # Build positions list
    positions = []
    for row in rows:
        shares_str = (row.get("shares") or "").strip()
        shares = float(shares_str) if shares_str else None

        yf_sym = (row.get("yf_symbol") or "").strip()
        cg_id = (row.get("cg_id") or "").strip()
        price_key = yf_sym or cg_id
        price = None
        if price_key and row["_price_source"] == "live":
            price = prices.get(price_key)

        positions.append({
            "ticker": row.get("ticker", ""),
            "description": row.get("description", ""),
            "owner": row.get("owner", ""),
            "account": row.get("account", ""),
            "shares": shares,
            "price": round(price, 4) if price is not None else None,
            "value": round(row["_value"], 2),
            "sector": row.get("sector", ""),
            "price_source": row["_price_source"],
        })

    # Sort by value descending
    positions.sort(key=lambda x: x["value"], reverse=True)

    last_updated = prices.get("fetched_at_human") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "last_updated": last_updated,
        "summary": {
            "total_portfolio": round(total_portfolio),
            "galen_total": round(galen_total),
            "jaclyn_total": round(jaclyn_total),
            "liquid_total": round(liquid_total),
        },
        "positions": positions,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
