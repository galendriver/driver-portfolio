# Financial Planning Action Tracker
**Household:** Galen & Jaclyn
**Last Updated:** 2026-02-19
**Next Review:** March 2026 (post-property sale & tender settlement)

---

## Status Legend
- `✅ DONE` — Completed
- `🔴 URGENT` — Time-sensitive, do immediately
- `🟡 PENDING` — Awaiting trigger event
- `🔁 ONGOING` — Recurring action

---

## WEEK 1 — Feb 17–23, 2026

| Status | Action | Details | Deadline |
|--------|--------|---------|----------|
| ✅ DONE | Databricks 401(k) reallocated | New tactical allocation in place (2/19/26) | — |
| ✅ DONE | Future contributions updated | Databricks 401(k) contribution allocation updated | — |
| ✅ DONE | $30k HELOC payment | Balance now $150,000 | — |
| 🔴 URGENT | **Accept Databricks tender offer** | Sell $200k (33.7% of vested @ ~$190/unit). Net proceeds ~$180,335 after ~$19,665 tax. | **Before deadline closes** |
| 🔴 URGENT | **Crypto tax-loss harvesting** | Sell NEAR ($161), AIOZ ($61), Algorand ($5), Compound ($0.35), Kishu Inu ($4) — total ~$1,900 losses. Do BEFORE tender settles to offset gains. | **Before tender settles** |
| 🔴 URGENT | **Harvest KSCP loss** | Sell Knightscope: ~$6 current, $505 loss (-95.39%) | **Before tender settles** |

### Crypto Loss Harvesting Detail
| Token | Current Value | Est. Loss | Action |
|-------|--------------|-----------|--------|
| NEAR Protocol | $161 | ~$648 | Sell all |
| AIOZ Network | $61 | ~$695 | Sell all |
| Algorand | $5 | ~$10 | Sell all |
| Compound | $0.35 | ~$9 | Sell all |
| Kishu Inu | $4 | ~high | Sell all |
| KSCP (brokerage) | $6 | ~$505 | Sell all |
| **Total** | | **~$1,900** | |

---

## WEEKS 2–3 — Feb 24 – Mar 9, 2026

| Status | Action | Details | Trigger |
|--------|--------|---------|---------|
| 🟡 PENDING | Recreational property closes escrow | Sale price ~$150k gross, ~$142.5k net after $7.5k tax | Escrow closes |
| 🟡 PENDING | Pay off HELOC in full | Use property net proceeds + $7,500 from cash reserves. Balance: $150k → $0. Opens $250k credit line. | Day of proceeds receipt |
| 🟡 PENDING | Receive tender proceeds | $200k gross → ~$180,335 net (after ~$19,665 federal LTCG tax) | ~2–3 weeks after acceptance |

---

## WEEKS 3–4 — Mar 10–23, 2026 (Deploy $332,735)

### Sources
| Source | Gross | Net |
|--------|-------|-----|
| Databricks tender | $200,000 | ~$180,335 |
| Property sale | ~$150,000 | ~$142,500 |
| Cash from reserves | $9,900 | $9,900 |
| **Total** | | **~$332,735** |

### Deployment Plan
| Status | Priority | Action | Amount | Target |
|--------|----------|--------|--------|--------|
| 🟡 PENDING | 1 | ~~Pay off HELOC~~ *(handled in Wks 2–3)* | $150,000 | Saves $10,500/yr |
| 🟡 PENDING | 2a | Buy Healthcare ETF/stocks | $50,000 | XLV or VHT (0% → target 3–5%) |
| 🟡 PENDING | 2b | Buy Financials ETF/stocks | $40,000 | XLF or VFH (0% → target 3–5%) |
| 🟡 PENDING | 2c | Buy Industrials ETF/stocks | $25,000 | XLI or select (GE, RTX, CAT) |
| 🟡 PENDING | 2d | Buy Japan ETF | $10,000 | EWJ or DXJ |
| 🟡 PENDING | 2e | Buy EM ETF | $10,000 | VWO or IEMG |
| 🟡 PENDING | 3 | Primary mortgage paydown | $30,000 | Balance: $1.33M → $1.30M |
| 🟡 PENDING | 4 | Rebuild cash reserve | $17,735 | HYSA → total cash ~$57,735 |

---

## ONGOING — March 2026+

### Monthly
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | Monitor RSU vesting (Galen) | Amazon RSUs, ~$40–50k/yr vesting |
| 🔁 ONGOING | Sell 75% of each Amazon RSU vest | Immediately upon vesting; deploy to underweight sectors |
| 🔁 ONGOING | Monitor RSU vesting (Jaclyn) | Post-IPO: sell 50–75% upon lockup expiration |
| 🔁 ONGOING | Update account balances | Log to `data/balances-YYYY-MM.csv` |

### Quarterly (Mar / Jun / Sep / Dec)
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | Review 401(k) allocations for drift | Rebalance if >10% off target |
| 🔁 ONGOING | Check taxable portfolio sector weights | Run `check_allocations.py` |
| 🔁 ONGOING | Trim if any single position >25% liquid | Target: trim to 20% |
| 🔁 ONGOING | Databricks concentration check | Flag if >45% household or >70% Jaclyn's NW |

### Annual (January)
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | Comprehensive portfolio review | Update retirement projections |
| 🔁 ONGOING | Assess mortgage refi opportunity | Target: 4.0–4.5% fixed (from 5.85% ARM) |
| 🔁 ONGOING | Tax-loss harvesting sweep | Check all positions for unrealized losses |
| 🔁 ONGOING | Max 401(k) contributions | $23k each = $46k/yr household |
| 🔁 ONGOING | Evaluate backdoor Roth / mega backdoor Roth | $7k/person Roth + up to $50k+ mega backdoor |
| 🔁 ONGOING | Plan capital gains strategy for year | Coordinate RSU sales, tender, loss offsets |

---

## Guardrails — Auto-Check These

| Metric | Current | Target / Limit | Alert If |
|--------|---------|----------------|----------|
| Databricks % of household | 46% | Keep <40% post-tender | >45% |
| Databricks % of Jaclyn's NW | 86% | Keep <60% post-tender | >70% |
| Any single liquid position | NVDA ~24% | Keep <25% | >25% |
| Amazon % of household | ~13% | Keep <20% | >20% |
| Healthcare allocation | 0% | Target 3–5% | <2% after deployment |
| Financials allocation | 0% | Target 3–5% | <2% after deployment |
| International (total) | ~5% | Target 8–10% | <5% |
| HELOC balance | $150,000 | $0 post-sale | >$0 after property close |
| Cash + HELOC liquidity | ~$307k post-plan | Keep >$200k | <$150k |

---

## 2026 Tax Snapshot

| Event | Capital Gain | Tax Rate | Est. Tax |
|-------|-------------|----------|----------|
| Databricks tender | ~$133,000 | 15% federal LTCG | ~$19,950 |
| Property sale | ~$50,000 | 15% federal LTCG | ~$7,500 |
| Crypto loss offset | ~($1,900) | — | ~($285) |
| **Net 2026 capital gains tax** | | | **~$27,165** |

*Washington state: 7% capital gains applies above $250k threshold — not triggered by these transactions.*

---

## Key Milestones

| Date | Milestone | Target Net Worth |
|------|-----------|-----------------|
| Feb 2026 | Baseline | $1,780,780 |
| Mar 2026 | Post-sale + HELOC eliminated | ~$1,930,780 |
| Aug 2026 | 6-month check | ~$2,050,000 |
| Feb 2027 | 1-year target | ~$2,100,000–$2,300,000 |
| 2035–2036 | Retirement (age 47–48) | $6,000,000–$7,000,000 |
