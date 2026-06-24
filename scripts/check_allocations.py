#!/usr/bin/env python3
"""
Portfolio Allocation Checker
Reads balance CSV, fetches live prices, calculates sector/asset weights, checks guardrails.
Usage: python scripts/check_allocations.py [--balances data/balances.csv] [--refresh]
"""

import csv
import sys
import argparse
from pathlib import Path
from datetime import date, datetime
from collections import defaultdict

# Live pricing — import from sibling script
sys.path.insert(0, str(Path(__file__).parent))
from fetch_prices import fetch_all_prices, get_row_value, load_rows, GSHEET_ID

# ---------------------------------------------------------------------------
# Guardrails & Targets
# ---------------------------------------------------------------------------

GUARDRAILS = [
    {
        "name": "Databricks % of household liquid portfolio",
        "scope": "household_liquid",
        "tickers": ["DBRX_VESTED"],
        "warn_pct": 40,
        "alert_pct": 45,
        "note": "Tender should bring this to ~37%",
    },
    {
        "name": "Databricks % of Jaclyn's net worth",
        "scope": "jaclyn_all",
        "tickers": ["DBRX_VESTED", "DBRX_UNVESTED"],
        "warn_pct": 60,
        "alert_pct": 70,
        "note": "Including unvested; post-tender target is <60%",
    },
    {
        "name": "Amazon % of household portfolio",
        "scope": "household_all",
        "tickers": ["AMZN", "AMZN_RSU"],
        "warn_pct": 18,
        "alert_pct": 20,
        "note": "Sell 75% of each RSU vest",
    },
    {
        "name": "NVDA % of household portfolio",
        "scope": "household_all",
        "tickers": ["NVDA"],
        "warn_pct": 20,
        "alert_pct": 25,
        "note": "Largest liquid single position",
    },
]

SECTOR_TARGETS = {
    "tech":             {"current": 90, "target_min": 60, "target_max": 75, "note": "Reduce via RSU sales + tender"},
    "healthcare":       {"current": 0,  "target_min": 3,  "target_max": 5,  "note": "Buy XLV/VHT post-tender"},
    "financials":       {"current": 0,  "target_min": 3,  "target_max": 5,  "note": "Buy XLF/VFH post-tender"},
    "industrials":      {"current": 0,  "target_min": 1,  "target_max": 2,  "note": "Buy XLI post-tender"},
    "international":    {"current": 2,  "target_min": 8,  "target_max": 10, "note": "Japan + EM ETFs"},
    "crypto":           {"current": 6,  "target_min": 3,  "target_max": 8,  "note": "After harvesting losers"},
    "bonds":            {"current": 0,  "target_min": 1,  "target_max": 3,  "note": "Via 401k bond index"},
    "cash":             {"current": 4,  "target_min": 2,  "target_max": 5,  "note": "HYSA; $57k post-plan"},
}

# ---------------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------------

def load_balances(filepath: str = None, force_refresh: bool = False) -> list[dict]:
    print()
    rows = load_rows(use_sheet=(filepath is None))
    print(f"  Fetching live prices...")
    prices = fetch_all_prices(rows, force_refresh=force_refresh)

    live_count = manual_count = missing_count = 0
    for row in rows:
        val, source = get_row_value(row, prices)
        row["value"] = val
        row["price_source"] = source
        if source == "live":
            live_count += 1
        elif source in ("manual", "manual-fallback"):
            manual_count += 1
        elif source == "missing":
            missing_count += 1

    cached_at = prices.get("fetched_at_human", "unknown")
    print(f"  Prices as of: {cached_at}")
    print(f"  Live: {live_count}  Manual: {manual_count}  Missing: {missing_count}")
    if missing_count > 0:
        missing = [r["ticker"] for r in rows if r.get("price_source") == "missing"]
        print(f"  [warn] No price for: {', '.join(missing)} — add shares or manual_value to CSV")
    print()
    return rows


def build_views(rows: list[dict]) -> dict:
    """Aggregate balances into useful slices."""
    views = defaultdict(float)
    by_ticker = defaultdict(float)
    by_sector = defaultdict(float)
    by_owner = defaultdict(float)
    by_asset_class = defaultdict(float)

    for r in rows:
        v = r["value"]
        owner = r["owner"]
        ticker = r["ticker"]
        sector = r["sector"]
        asset_class = r["asset_class"]

        views["total"] += v
        by_ticker[ticker] += v
        by_sector[sector] += v
        by_owner[owner] += v
        by_asset_class[asset_class] += v

        # Liquid = exclude private equity and unvested
        if asset_class not in ("private_equity",) and ticker != "DBRX_UNVESTED":
            views["total_liquid"] += v

        if owner == "galen":
            views["galen_all"] += v
            if asset_class not in ("private_equity",) and ticker != "DBRX_UNVESTED":
                views["galen_liquid"] += v

        if owner == "jaclyn":
            views["jaclyn_all"] += v
            if asset_class not in ("private_equity",) and ticker != "DBRX_UNVESTED":
                views["jaclyn_liquid"] += v

        # Household liquid = combined
        if asset_class not in ("private_equity",) and ticker != "DBRX_UNVESTED":
            views["household_liquid"] += v

    views["household_all"] = views["total"]

    return dict(views), dict(by_ticker), dict(by_sector), dict(by_owner), dict(by_asset_class)


# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def color(text, code):
    return f"{code}{text}{RESET}"

def pct(value, total):
    if total == 0:
        return 0.0
    return round(value / total * 100, 1)

def fmt_usd(value):
    return f"${value:>12,.0f}"

def bar(filled_pct, width=30):
    filled = int(filled_pct / 100 * width)
    filled = min(filled, width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


# ---------------------------------------------------------------------------
# Report Sections
# ---------------------------------------------------------------------------

def print_header(filepath: str):
    print()
    print(color("=" * 65, BOLD))
    print(color("  PORTFOLIO ALLOCATION REPORT", BOLD))
    print(f"  Source: {filepath}")
    print(f"  Run date: {date.today()}")
    print(color("=" * 65, BOLD))
    print()


def print_net_worth(views, by_owner):
    print(color("── NET WORTH SUMMARY ──────────────────────────────────────", BOLD))
    total = views["total"]
    liquid = views["household_liquid"]

    # Real estate equity (not in CSV — hardcoded from context)
    re_equity = 470_000 + 750_000  # primary + rental
    total_with_re = total + re_equity
    liabilities = 1_330_000 + 300_000  # primary + rental mortgage (recreational property sold, HELOC paid off 2026)
    net_worth = total_with_re - liabilities

    print(f"  Financial portfolio (incl. private equity): {fmt_usd(total)}")
    print(f"  Liquid portfolio (excl. unvested/private):  {fmt_usd(liquid)}")
    print(f"  Real estate equity (hardcoded):             {fmt_usd(re_equity)}")
    print(f"  Total assets:                               {fmt_usd(total_with_re)}")
    print(f"  Total liabilities:                          {fmt_usd(liabilities)}")
    print(f"  {color('Net worth:', BOLD)}                              {color(fmt_usd(net_worth), BOLD)}")
    print()
    print(f"  Galen's portfolio:   {fmt_usd(by_owner.get('galen', 0))}")
    print(f"  Jaclyn's portfolio:  {fmt_usd(by_owner.get('jaclyn', 0))}")
    print()


def print_guardrails(views, by_ticker):
    print(color("── GUARDRAILS ─────────────────────────────────────────────", BOLD))
    all_clear = True

    for g in GUARDRAILS:
        scope_total = views.get(g["scope"], 0)
        position_value = sum(by_ticker.get(t, 0) for t in g["tickers"])
        p = pct(position_value, scope_total)

        if p >= g["alert_pct"]:
            status = color(f"🔴 ALERT  {p:5.1f}%", RED)
            all_clear = False
        elif p >= g["warn_pct"]:
            status = color(f"🟡 WARN   {p:5.1f}%", YELLOW)
            all_clear = False
        else:
            status = color(f"✅ OK     {p:5.1f}%", GREEN)

        print(f"  {status}  {g['name']}")
        print(f"           {fmt_usd(position_value)} / {fmt_usd(scope_total)}  (limit: warn {g['warn_pct']}% / alert {g['alert_pct']}%)")
        if p >= g["warn_pct"]:
            print(f"           {color('Note: ' + g['note'], YELLOW)}")
        print()

    if all_clear:
        print(f"  {color('All guardrails clear.', GREEN)}")
    print()


def print_sector_breakdown(by_sector, views):
    print(color("── SECTOR ALLOCATION vs TARGETS ───────────────────────────", BOLD))
    total = views["household_all"]

    all_sectors = set(list(by_sector.keys()) + list(SECTOR_TARGETS.keys()))
    all_sectors.discard("diversified")  # target-date funds — mixed
    all_sectors.discard("private_equity")  # shown in guardrails
    all_sectors.discard("retirement")  # shown separately

    print(f"  {'Sector':<18} {'$Value':>12}  {'Actual':>7}  {'Target':>12}  {'Bar'}")
    print(f"  {'─'*18} {'─'*12}  {'─'*7}  {'─'*12}  {'─'*30}")

    for sector in sorted(all_sectors):
        val = by_sector.get(sector, 0)
        actual = pct(val, total)
        target_info = SECTOR_TARGETS.get(sector, {})
        t_min = target_info.get("target_min", 0)
        t_max = target_info.get("target_max", 100)

        target_str = f"{t_min}–{t_max}%"

        if t_min == 0 and t_max == 100:
            status_bar = bar(actual)
        elif actual < t_min:
            status_bar = color(bar(actual), YELLOW)
            target_str = color(target_str, YELLOW)
        elif actual > t_max:
            status_bar = color(bar(actual), RED)
            target_str = color(target_str, RED)
        else:
            status_bar = color(bar(actual), GREEN)
            target_str = color(target_str, GREEN)

        print(f"  {sector:<18} {fmt_usd(val)}  {actual:>6.1f}%  {target_str:>12}  {status_bar}")

    # Retirement/target-date funds — show as informational
    retirement_val = by_sector.get("diversified", 0) + by_sector.get("retirement", 0)
    if retirement_val:
        actual = pct(retirement_val, total)
        print(f"  {'401k/TDF (mixed)':<18} {fmt_usd(retirement_val)}  {actual:>6.1f}%  {'(varies)':>12}  {bar(actual)}")

    print()


def print_top_positions(by_ticker, views):
    print(color("── TOP POSITIONS (by value) ───────────────────────────────", BOLD))
    total = views["household_all"]
    liquid = views["household_liquid"]

    sorted_positions = sorted(by_ticker.items(), key=lambda x: x[1], reverse=True)
    print(f"  {'Ticker':<16} {'$Value':>12}  {'% Household':>12}  {'% Liquid':>10}")
    print(f"  {'─'*16} {'─'*12}  {'─'*12}  {'─'*10}")

    for ticker, val in sorted_positions[:15]:
        p_total = pct(val, total)
        p_liquid = pct(val, liquid)
        flag = ""
        if p_liquid >= 25:
            flag = color(" ⚠ EXCEEDS 25% LIQUID", RED)
        elif p_liquid >= 20:
            flag = color(" ⚠ APPROACHING LIMIT", YELLOW)
        print(f"  {ticker:<16} {fmt_usd(val)}  {p_total:>11.1f}%  {p_liquid:>9.1f}%{flag}")
    print()


def print_harvest_candidates(rows):
    print(color("── TAX-LOSS HARVEST CANDIDATES ────────────────────────────", BOLD))
    candidates = [r for r in rows if "HARVEST" in r.get("notes", "").upper()]
    if not candidates:
        print("  None flagged.\n")
        return

    total_loss = 0
    for r in candidates:
        print(f"  🔴 {r['ticker']:<10} current: {fmt_usd(r['value'])}   {r['notes']}")
    print()
    print(f"  Action: Sell all flagged positions BEFORE tender proceeds settle.")
    print(f"  Losses offset Databricks tender gains → saves ~$285 in federal tax.")
    print()


def print_action_summary(views, by_ticker):
    print(color("── IMMEDIATE ACTIONS ──────────────────────────────────────", BOLD))
    dbrx = by_ticker.get("DBRX_VESTED", 0)
    household = views["household_all"]
    dbrx_pct = pct(dbrx, household)

    if dbrx_pct > 45:
        print(f"  🔴 Databricks concentration at {dbrx_pct:.1f}% — TENDER OFFER IS CRITICAL")
    else:
        print(f"  🟡 Databricks at {dbrx_pct:.1f}% — accept tender to reduce below 40%")

    harvest_count = sum(1 for r in [] if "HARVEST" in r.get("notes", "").upper())
    print(f"  🔴 Crypto + KSCP tax-loss harvesting: execute before tender settles")
    print(f"  🟡 Post-tender deploy: $135k to healthcare/financials/industrials/international")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Portfolio allocation checker")
    parser.add_argument(
        "--balances",
        default=None,
        help="Path to local balances CSV (omit to use Google Sheet)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force live price refresh (ignore 5-min cache)",
    )
    args = parser.parse_args()

    rows = load_balances(filepath=args.balances, force_refresh=args.refresh)
    views, by_ticker, by_sector, by_owner, by_asset_class = build_views(rows)

    source_label = args.balances if args.balances else f"Google Sheet ({GSHEET_ID[:8]}...)"
    print_header(source_label)
    print_net_worth(views, by_owner)
    print_guardrails(views, by_ticker)
    print_sector_breakdown(by_sector, views)
    print_top_positions(by_ticker, views)
    print_harvest_candidates(rows)
    print_action_summary(views, by_ticker)


if __name__ == "__main__":
    main()
