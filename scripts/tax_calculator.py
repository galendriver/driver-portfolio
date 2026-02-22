#!/usr/bin/env python3
"""
2026 Tax Calculator — Galen & Jaclyn
Calculates federal and WA state tax liability for capital gains events,
RSU income, and loss harvesting. Includes scenario modeling.

Usage:
    python scripts/tax_calculator.py                        # base plan
    python scripts/tax_calculator.py --scenario ipo         # post-IPO sale scenario
    python scripts/tax_calculator.py --events data/tax-events-2026.csv
"""

import csv
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# 2026 Tax Constants (MFJ — Married Filing Jointly)
# ---------------------------------------------------------------------------

# Federal income tax brackets (MFJ, 2026 estimated — close to 2025)
ORDINARY_BRACKETS = [
    (23_200,   0.10),
    (94_300,   0.12),
    (201_050,  0.22),
    (383_900,  0.24),
    (487_450,  0.32),
    (731_200,  0.35),
    (float("inf"), 0.37),
]

# Long-term capital gains brackets (MFJ, 2026)
LTCG_BRACKETS = [
    (94_050,   0.00),
    (583_750,  0.15),
    (float("inf"), 0.20),
]

# Net Investment Income Tax — 3.8% on investment income above MAGI threshold
NIIT_THRESHOLD_MFJ = 250_000
NIIT_RATE = 0.038

# Washington State capital gains tax — 7% on LTCG above $250k/year
WA_CGT_EXEMPTION = 250_000
WA_CGT_RATE = 0.07

# Standard deduction 2026 (MFJ estimated)
STANDARD_DEDUCTION_MFJ = 30_000

# 401(k) max contribution both spouses
RETIREMENT_CONTRIBUTIONS = 46_000   # $23k x 2

# ---------------------------------------------------------------------------
# Household Base Income (from context doc)
# ---------------------------------------------------------------------------

HOUSEHOLD_BASE = {
    "galen_salary":        155_000,
    "jaclyn_salary":       210_000,
    "jaclyn_bonus":         37_800,
    "rental_net_income":    26_400,
}

# Deductions/adjustments
ITEMIZED_DEDUCTIONS = {
    "mortgage_interest_primary":  77_805,  # 5.85% ARM on $1.33M
    "mortgage_interest_rental":    9_600,  # 3.2% fixed; fully deductible as rental expense
    "rental_depreciation":        20_000,  # ~$550k basis / 27.5 yrs
    "retirement_401k":            46_000,  # both maxed
}

# ---------------------------------------------------------------------------
# Data Model
# ---------------------------------------------------------------------------

@dataclass
class TaxEvent:
    name: str
    owner: str
    event_type: Literal["ltcg", "stcg", "loss", "ordinary"]
    proceeds: float
    cost_basis: float
    holding: str
    settled: bool
    notes: str
    gain: float = field(init=False)

    def __post_init__(self):
        self.gain = self.proceeds - self.cost_basis


def load_events(filepath: str) -> list[TaxEvent]:
    events = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(TaxEvent(
                name=row["event_name"],
                owner=row["owner"],
                event_type=row["event_type"],
                proceeds=float(row["proceeds"]),
                cost_basis=float(row["cost_basis"]),
                holding=row["holding"],
                settled=row["settled"].lower() == "true",
                notes=row["notes"],
            ))
    return events


# ---------------------------------------------------------------------------
# Tax Calculation Engine
# ---------------------------------------------------------------------------

def apply_brackets(income: float, brackets: list) -> float:
    tax = 0.0
    prev = 0.0
    for limit, rate in brackets:
        if income <= prev:
            break
        taxable = min(income, limit) - prev
        tax += taxable * rate
        prev = limit
    return tax


def calculate_ordinary_income_tax(taxable_ordinary: float) -> float:
    return apply_brackets(taxable_ordinary, ORDINARY_BRACKETS)


def calculate_ltcg_tax(ltcg: float, ordinary_income: float) -> float:
    """LTCG is taxed on top of ordinary income (stacking)."""
    tax_with = apply_brackets(ordinary_income + ltcg, LTCG_BRACKETS)
    tax_without = apply_brackets(ordinary_income, LTCG_BRACKETS)
    return tax_with - tax_without


def calculate_niit(net_investment_income: float, magi: float) -> float:
    """3.8% on lesser of NII or (MAGI - threshold)."""
    excess_magi = max(0, magi - NIIT_THRESHOLD_MFJ)
    subject_to_niit = min(net_investment_income, excess_magi)
    return subject_to_niit * NIIT_RATE


def calculate_wa_cgt(total_ltcg: float) -> float:
    """WA 7% capital gains tax on LTCG above $250k."""
    return max(0, total_ltcg - WA_CGT_EXEMPTION) * WA_CGT_RATE


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def color(text, code): return f"{code}{text}{RESET}"
def fmt(v): return f"${v:>14,.0f}"
def fmt_pct(v): return f"{v:.1f}%"
def hr(): print(color("─" * 65, DIM))


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def run_report(events: list[TaxEvent], scenario_name: str = "Base Plan"):

    # ── Aggregate events ──────────────────────────────────────────────────
    ltcg_gains   = [(e.name, e.gain) for e in events if e.event_type == "ltcg"]
    stcg_gains   = [(e.name, e.gain) for e in events if e.event_type == "stcg"]
    losses       = [(e.name, e.gain) for e in events if e.event_type == "loss"]
    ordinary_add = [(e.name, e.proceeds) for e in events if e.event_type == "ordinary"]

    total_ltcg      = sum(g for _, g in ltcg_gains)
    total_stcg      = sum(g for _, g in stcg_gains)
    total_losses    = sum(g for _, g in losses)          # negative numbers
    total_ordinary  = sum(v for _, v in ordinary_add)

    # Net capital gains (losses offset gains; up to $3k can offset ordinary income)
    net_cg = total_ltcg + total_stcg + total_losses      # losses are negative
    net_ltcg = max(0, total_ltcg + total_losses)         # losses reduce LTCG first
    excess_losses = min(0, net_cg)                        # any losses beyond gains

    # Ordinary income construction
    base_ordinary = sum(HOUSEHOLD_BASE.values())
    gross_ordinary = base_ordinary + total_ordinary

    # Deductions
    total_itemized = sum(ITEMIZED_DEDUCTIONS.values())
    deduction = max(total_itemized, STANDARD_DEDUCTION_MFJ)
    using_itemized = total_itemized > STANDARD_DEDUCTION_MFJ

    # Ordinary income loss offset (max $3k/yr against ordinary income)
    ordinary_loss_offset = max(-3_000, excess_losses)
    taxable_ordinary = max(0, gross_ordinary - deduction + ordinary_loss_offset)

    # MAGI (before deductions, used for NIIT/bracket phase-ins)
    magi = gross_ordinary + net_ltcg

    # Federal taxes
    fed_ordinary_tax  = calculate_ordinary_income_tax(taxable_ordinary)
    fed_ltcg_tax      = calculate_ltcg_tax(net_ltcg, taxable_ordinary)
    net_invest_income = net_ltcg    # simplified (excludes dividends/interest for now)
    niit              = calculate_niit(net_invest_income, magi)
    total_federal     = fed_ordinary_tax + fed_ltcg_tax + niit

    # WA State
    wa_cgt = calculate_wa_cgt(net_ltcg)

    # Total
    total_tax = total_federal + wa_cgt
    effective_rate = total_tax / magi * 100 if magi else 0

    # ── Print ─────────────────────────────────────────────────────────────
    print()
    print(color("=" * 65, BOLD))
    print(color(f"  2026 TAX CALCULATOR — {scenario_name.upper()}", BOLD))
    print(color("=" * 65, BOLD))

    # Income summary
    print()
    print(color("── GROSS INCOME ────────────────────────────────────────────", BOLD))
    print(f"  Galen salary:                   {fmt(HOUSEHOLD_BASE['galen_salary'])}")
    print(f"  Jaclyn salary:                  {fmt(HOUSEHOLD_BASE['jaclyn_salary'])}")
    print(f"  Jaclyn bonus (18% target):      {fmt(HOUSEHOLD_BASE['jaclyn_bonus'])}")
    print(f"  Rental net income:              {fmt(HOUSEHOLD_BASE['rental_net_income'])}")
    print(f"  RSU vests (ordinary income):    {fmt(total_ordinary)}")
    print(f"  {color('Gross ordinary income:', BOLD)}         {color(fmt(gross_ordinary), BOLD)}")
    print()
    print(f"  Long-term capital gains (gross):{fmt(total_ltcg)}")
    if total_losses < 0:
        print(f"  Capital losses harvested:       {fmt(total_losses)}")
    print(f"  Net LTCG:                       {fmt(net_ltcg)}")
    if total_stcg > 0:
        print(f"  Short-term capital gains:       {fmt(total_stcg)}")
    print(f"  {color('MAGI:', BOLD)}                          {color(fmt(magi), BOLD)}")

    # Capital gains events detail
    print()
    print(color("── CAPITAL GAINS EVENTS ────────────────────────────────────", BOLD))
    print(f"  {'Event':<35} {'Proceeds':>10} {'Basis':>10} {'Gain/Loss':>12} {'Type'}")
    print(f"  {'─'*35} {'─'*10} {'─'*10} {'─'*12} {'─'*8}")
    for e in events:
        if e.event_type in ("ltcg", "stcg", "loss"):
            g_str = f"${e.gain:>+11,.0f}"
            g_col = GREEN if e.gain >= 0 else RED
            print(f"  {e.name:<35} {fmt(e.proceeds)[1:]:>10} {fmt(e.cost_basis)[1:]:>10} {color(g_str, g_col)} {e.event_type.upper()}")
    hr()
    print(f"  {'Net capital gains':<35} {'':>10} {'':>10} {color(fmt(net_ltcg), BOLD):>12}")
    if excess_losses < 0:
        print(f"  {color(f'Unused losses (carry forward): ${abs(excess_losses):,.0f}', YELLOW)}")
    print()

    # Deductions
    print(color("── DEDUCTIONS ──────────────────────────────────────────────", BOLD))
    if using_itemized:
        print(f"  Using: itemized (${total_itemized:,.0f} > standard ${STANDARD_DEDUCTION_MFJ:,.0f})")
    else:
        print(f"  Using: standard deduction (${STANDARD_DEDUCTION_MFJ:,.0f})")
    for k, v in ITEMIZED_DEDUCTIONS.items():
        print(f"    {k.replace('_',' ').title():<40} {fmt(v)}")
    print(f"  {'─'*45}")
    print(f"  Total deductions applied:       {fmt(deduction)}")
    print(f"  Taxable ordinary income:        {fmt(taxable_ordinary)}")
    print()

    # Federal tax
    print(color("── FEDERAL TAX ─────────────────────────────────────────────", BOLD))
    print(f"  Ordinary income tax (35% marginal): {fmt(fed_ordinary_tax)}")
    print(f"  Long-term capital gains tax (15%):  {fmt(fed_ltcg_tax)}")

    if niit > 0:
        print(f"  {color('Net Investment Income Tax (3.8%):', YELLOW)}   {color(fmt(niit), YELLOW)}")
        niit_note = f"NIIT applies: MAGI ${magi:,.0f} > ${NIIT_THRESHOLD_MFJ:,} threshold"
        print(f"    {color('⚠ ' + niit_note, YELLOW)}")
        print(f"    {color('Effective LTCG rate = 15% + 3.8% = 18.8% — verify with CPA', YELLOW)}")
    else:
        print(f"  Net Investment Income Tax (3.8%):  {fmt(niit)}  (below threshold)")

    print(f"  {'─'*50}")
    print(f"  {color('Total federal tax:', BOLD)}                 {color(fmt(total_federal), BOLD)}")
    print()

    # WA State
    print(color("── WASHINGTON STATE ────────────────────────────────────────", BOLD))
    print(f"  WA income tax:                      {fmt(0)}  (no state income tax)")
    if wa_cgt > 0:
        print(f"  {color('WA capital gains tax (7%):', RED)}         {color(fmt(wa_cgt), RED)}")
        print(f"    {color(f'⚠ Net LTCG ${net_ltcg:,.0f} exceeds ${WA_CGT_EXEMPTION:,} exemption', RED)}")
    else:
        print(f"  WA capital gains tax (7%):          {fmt(0)}  (LTCG ${net_ltcg:,.0f} < ${WA_CGT_EXEMPTION:,} exempt)")
    print()

    # Summary
    print(color("── TAX SUMMARY ─────────────────────────────────────────────", BOLD))
    print(f"  Federal ordinary income tax:    {fmt(fed_ordinary_tax)}")
    print(f"  Federal LTCG tax (15%):         {fmt(fed_ltcg_tax)}")
    print(f"  Net Investment Income Tax:      {fmt(niit)}")
    print(f"  WA state capital gains tax:     {fmt(wa_cgt)}")
    print(f"  {'─'*45}")
    print(f"  {color('TOTAL 2026 TAX LIABILITY:', BOLD)}      {color(fmt(total_tax), BOLD)}")
    print(f"  Effective rate (on MAGI):       {fmt_pct(effective_rate)}")
    print()
    after_tax = magi - total_tax
    print(f"  MAGI:                           {fmt(magi)}")
    print(f"  Total taxes:                    {fmt(total_tax)}")
    print(f"  {color('After-tax income:', BOLD)}              {color(fmt(after_tax), BOLD)}")
    print()

    # Capital-gains-only tax breakdown (useful for planning)
    cg_only_tax = fed_ltcg_tax + niit + wa_cgt
    print(color("── CAPITAL GAINS TAX ONLY (for planning) ───────────────────", BOLD))
    print(f"  Gross LTCG events:              {fmt(total_ltcg)}")
    print(f"  Loss offsets:                   {fmt(total_losses)}")
    print(f"  Net LTCG:                       {fmt(net_ltcg)}")
    print(f"  Federal LTCG tax:               {fmt(fed_ltcg_tax)}")
    print(f"  NIIT (3.8%):                    {fmt(niit)}")
    print(f"  WA state CGT:                   {fmt(wa_cgt)}")
    print(f"  {'─'*45}")
    print(f"  {color('Total capital gains taxes:', BOLD)}      {color(fmt(cg_only_tax), BOLD)}")
    print(f"  Net proceeds (after CG taxes):")
    for e in events:
        if e.event_type == "ltcg" and e.gain > 0:
            # Approximate per-event tax rate
            approx_rate = (fed_ltcg_tax + niit) / net_ltcg if net_ltcg else 0
            est_tax = e.gain * approx_rate
            net = e.proceeds - est_tax
            print(f"    {e.name:<35} {color(fmt(net), GREEN)}")
    print()

    return total_tax, net_ltcg


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_ipo_sale(events: list[TaxEvent], additional_dbrx_gain: float):
    """Model selling additional Databricks shares post-IPO."""
    scenario_events = [e for e in events]
    scenario_events.append(TaxEvent(
        name="Databricks post-IPO sale",
        owner="jaclyn",
        event_type="ltcg",
        proceeds=additional_dbrx_gain * 1.5,   # assume 1.5x basis appreciation
        cost_basis=additional_dbrx_gain,
        holding="long",
        settled=False,
        notes="Scenario: post-IPO lockup expiry sale",
    ))
    return scenario_events


def scenario_amazon_rsu_full_sell(events: list[TaxEvent]):
    """Model selling 100% of Amazon RSUs instead of 75%."""
    # Find existing RSU entries and add the extra 25%
    extra_rsu = sum(
        e.proceeds * 0.25
        for e in events
        if "Amazon RSU" in e.name and e.event_type == "ordinary"
    )
    scenario_events = list(events)
    scenario_events.append(TaxEvent(
        name="Amazon RSU extra 25% sold (scenario)",
        owner="galen",
        event_type="ltcg",  # if held >1yr after vest
        proceeds=extra_rsu * 1.1,  # assume 10% appreciation post-vest
        cost_basis=extra_rsu,
        holding="long",
        settled=False,
        notes="Scenario: sell 100% of RSU vests vs 75%",
    ))
    return scenario_events


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="2026 Tax Calculator")
    parser.add_argument("--events", default="data/tax-events-2026.csv")
    parser.add_argument(
        "--scenario",
        choices=["base", "ipo", "rsu_full"],
        default="base",
        help=(
            "base: 2026 plan as-is | "
            "ipo: add post-IPO Databricks sale | "
            "rsu_full: sell 100%% of Amazon RSU vests"
        ),
    )
    parser.add_argument(
        "--ipo-gain",
        type=float,
        default=200_000,
        help="Additional Databricks gain for IPO scenario (default: $200,000)",
    )
    args = parser.parse_args()

    filepath = Path(args.events)
    if not filepath.exists():
        filepath = Path(__file__).parent.parent / args.events
    if not filepath.exists():
        print(f"Error: events file not found: {args.events}")
        return

    events = load_events(str(filepath))

    if args.scenario == "base":
        run_report(events, "Base Plan — 2026")

    elif args.scenario == "ipo":
        print(color(f"\n  ℹ  IPO scenario: adding ${args.ipo_gain:,.0f} additional Databricks LTCG", CYAN))
        scenario_events = scenario_ipo_sale(events, args.ipo_gain)
        tax_base, _ = run_report(events, "Base Plan — 2026")
        tax_ipo, _  = run_report(scenario_events, f"IPO Scenario (+${args.ipo_gain:,.0f} DBRX gain)")
        print(color("── SCENARIO COMPARISON ─────────────────────────────────────", BOLD))
        print(f"  Base plan total tax:            {fmt(tax_base)}")
        print(f"  IPO scenario total tax:         {fmt(tax_ipo)}")
        print(f"  Incremental tax on IPO sale:    {fmt(tax_ipo - tax_base)}")
        marginal = (tax_ipo - tax_base) / args.ipo_gain * 100 if args.ipo_gain else 0
        print(f"  Marginal rate on IPO proceeds:  {fmt_pct(marginal)}")
        print()
        if tax_ipo - tax_base > 0:
            wa = calculate_wa_cgt(args.ipo_gain)
            if wa > 0:
                print(color(f"  ⚠  WA state CGT triggered on IPO sale: {fmt(wa)}", YELLOW))
                print(f"     Consider spreading sales across tax years to stay under $250k/yr")
        print()

    elif args.scenario == "rsu_full":
        scenario_events = scenario_amazon_rsu_full_sell(events)
        tax_base, _ = run_report(events, "Base Plan (sell 75% RSUs)")
        tax_full, _ = run_report(scenario_events, "Scenario: Sell 100% Amazon RSUs")
        print(color("── SCENARIO COMPARISON ─────────────────────────────────────", BOLD))
        print(f"  Base plan total tax:            {fmt(tax_base)}")
        print(f"  Full RSU sell total tax:        {fmt(tax_full)}")
        print(f"  Additional tax:                 {fmt(tax_full - tax_base)}")
        print()


if __name__ == "__main__":
    main()
