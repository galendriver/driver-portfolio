# Financial Planning Action Tracker
**Household:** Galen & Jaclyn
**Last Updated:** 2026-09-05
**Next Review:** See [September 2026 Portfolio Reassessment](./reports/September_2026_Portfolio_Reassessment.md) — full account reconciliation + two-horizon strategy

---

## STATUS AS OF 2026-09-05 — Full Account Reconciliation

**Net worth: $2,165,905** (excl. $152,004 gross unvested AMZN RSUs). Liquid: $1,469,335.
Every account was pulled from source tonight. `balances.csv` is now the reconciled truth.

**Previously untracked assets found — ~$385k:**
- Nordstrom 401(k) (Fidelity 7883P) — **$53,698**, prior-employer plan, allocation never reviewed
- BECU — **$45,499** across 3 accounts (MMA $36,493 + two checking)
- AMZN in Fidelity TOD — 335.938 sh, **$86,843**, the CSV had only 251.6 sh
- GOOGL 14 sh in Jaclyn's -0552 — **$4,738**, in no record anywhere
- stETH + RNDR — **$30,097**, zeroed out by a price-fetch bug, not actually missing
- SOFI, QBTS, HSA, brokerage cash balances — smaller, all previously untracked

**Corrections:**
- **Account ownership was wrong.** The entire April Tranche 1 (~$97k) sits in **Jaclyn's** -0552 account, not Galen's — it was funded by her Databricks tender. The CSV had it under `galen_brokerage`.
- Databricks: **1,689 vested shares** ($321,510 @ $190) and **1,974 unvested units** ($375,060). Prior figures were unit counts from April and were stale.
- Galen 401(k): $140,661 → **$156,797**. Jaclyn's: F5 **$93,390** + Databricks **$90,308** (was recorded as a single "TRP 2055" line at $86,458).

**Open, unexecuted:**
- **May AND August 2026 RSU vests were never sold** — 84.319 AMZN sh (~$21,800) sitting undiversified against a standing 75%-sell rule. Cost basis ≈ market, so selling is tax-neutral.
- LUNR, NOK still held. Third flag.
- Tranche 2 ($26k) still never executed.
- $9,273 cash idle in -0552 since June.

**⚠️ App data source:** `web/server.py` reads the **Google Sheet**, not `balances.csv`. The Sheet is badly stale and has a trailing-tab typo in the stETH `yf_symbol` that zeroes that row (the code prefers `yf_symbol` and never falls back to `cg_id`). Until the Sheet is updated or the app is flipped to CSV-first, the deployed dashboard will keep understating net worth by roughly $385k.

---

## STATUS AS OF 2026-06-23 — Reconciliation

- **RSU sell rate is 75%, not 85%.** The 85% bump below (and throughout this file) was decided 4/15 but reconfirmed back to 75% on 6/23 — Galen is bullish on AMZN long-term. All "Sell 85%" references in this file and `balances.csv` are stale; treat 75% as current.
- **May RSU → GOOGL ($15,174 @ 85%, see "GOOGL Structural Build" below) was never executed.** Confirmed via brokerage screenshot 6/23 — both May lots (56.329 + 11.126 sh) still fully unsold. Superseded: 6/23 plan sells 75% (~$11,844) split AVUV $7,000 / VWO $4,844, not a GOOGL lump sum. GOOGL gets $5,000 from the separate ANET dry-powder pool instead.
- **ANET trigger is dead** — ANET at $169 (6/21), never corrected to the $120–125 entry. The $10k earmarked for it was redirected to GOOGL per 6/23 decision, not SPCX.
- **Tranche 2 ($26,000 top-off, table below) was never executed.** Share counts in the live brokerage account match Tranche 1 exactly, no top-off occurred. Status: unresolved, not folded into any current plan.
- **LUNR (30sh) and NOK (122sh)**: real positions, were in `balances.csv` (overlooked in two earlier searches this session) but never made it into the live Google Sheet. No thesis was ever documented for either. The 6/21 reassessment recommended cutting both — not yet acted on.
- Full detail: [reports/June_2026_Portfolio_Reassessment.md](./reports/June_2026_Portfolio_Reassessment.md)

---

---

## Status Legend
- `✅ DONE` — Completed
- `🔴 URGENT` — Time-sensitive, do immediately
- `🟡 PENDING` — Awaiting trigger event
- `🔁 ONGOING` — Recurring action
- `⏸ WATCH` — Monitor, act on trigger

---

## COMPLETED ✅

| Status | Action | Details |
|--------|--------|---------|
| ✅ DONE | Databricks 401(k) reallocated | Tactical allocation in place (2/19/26) |
| ✅ DONE | Future contributions updated | Databricks 401(k) contribution allocation updated |
| ✅ DONE | $30k HELOC payment | Balance reduced to $150,000 |
| ✅ DONE | Recreational property sold | $146,000 applied to HELOC → balance now ~$4,000 |
| ✅ DONE | HELOC zeroed out | Paid remaining ~$4,000 from cash. Full $250k credit line open. (3/12/26) |
| ✅ DONE | Harvest KSCP loss | Sold Knightscope — ~$505 loss captured. (3/12/26) |
| ✅ DONE | Crypto tax-loss harvesting | Sold NEAR, AIOZ, Algorand, Compound, Kishu Inu — ~$1,900 losses harvested. (3/12/26) |
| ✅ DONE | AMZN RSU reallocation | Sold 22 shares (Nov 2025 lot) → bought VHT 10.78 sh @ $278.43 + GOOGL 5.357 sh @ $303.89 in Fidelity account (3/12/26) |
| ✅ DONE | Portfolio + cost basis updated | balances.csv and Google Sheet updated with all current holdings and per-share cost basis. App deployed. |
| ✅ DONE | Databricks tender executed | ~$200k gross received |
| ✅ DONE | Tranche 1 deployed (4/16/26) | 8 positions executed: MSFT 29sh@$419.97, LLY 11sh@$905.90, VHT 36sh@$275.61, C 60sh@$131.50, TSLA 16sh@$394.06, RTX 25sh@$198.41, UNH 16sh@$315.05, RKLB 55sh@$76.92 |
| ✅ DONE | Google Sheet + CSV updated | All fills, DBRX post-tender value, Galen 401k ($140,661) updated |

---

## APRIL 2026 CAPITAL PLAN (Post-Tender, Updated 4/15)

### Actual Capital Math

| Source | Amount |
|--------|--------|
| Databricks tender (gross) | $200,000 |
| Less: 2025 federal tax owed | -$51,000 |
| Less: Electrical work | -$24,000 |
| Less: Repairs / painting | -$15,000 *(due May — not yet paid)* |
| **Net investable** | **$110,000** (~$100k deployed + ~$10k buffer) |
| Existing HYSA | $22,000 (untouched) |
| HELOC available (emergency) | $250,000 |

**Rationale for change from March $180k plan:** 2025 tax bill came in higher than forecast ($51k vs. ~$17k estimate). Two unforeseen home repairs required immediate action. Deploying $100k instead of $180k; concentration thesis still holds given 76% household AI/tech exposure.

---

## THIS WEEK — April 14–18 (Tranche 1 Deploy: $60,000)

### Pay First (Cash Out: $90k)
| Status | Action | Amount |
|--------|--------|--------|
| ✅ DONE | Pay 2025 federal taxes | $51,000 |
| ✅ DONE | Pay electrical contractor | $24,000 |
| 🟡 PENDING | Pay painting / repairs contractor — **due May** | $15,000 |

### Deploy in This Order (Priority = Conviction × Event Timing)

| # | Status | Ticker | Amount | Conviction | Thesis |
|---|--------|--------|--------|------------|--------|
| 1 | 🔴 URGENT | **MSFT** | $12,000 | MEDIUM (asymmetric) | −33% drawdown, 94% Buy, Q3 earnings 4/29. Full allocation — no adds planned. |
| 2 | 🔴 URGENT | **LLY** | $10,000 | **HIGH** | FDA-approved oral GLP-1 (Foundayo) 4/1, $1,209 target, 44% upside. Quality growth. |
| 3 | 🔴 URGENT | **VHT** | $10,000 | **HIGH** | Healthcare ETF. Closes largest sector gap (0% → ~2%). |
| 4 | 🔴 URGENT | **Citi (C)** | $8,000 | **HIGH** | Lowest-valuation large bank. Restructuring catalyst. |
| 5 | 🔴 URGENT | **TSLA** | $6,000 | MEDIUM | SpaceX IPO roadshow June. Energy/auto, not AI-pure. |
| 6 | 🔴 URGENT | **RTX** | $5,000 | MEDIUM | $268B backlog, Iran war premium. Already rallied — reduced sizing. |
| 7 | 🔴 URGENT | **UNH** | $5,000 | MEDIUM | Contrarian (−35% YTD). Sized small for ongoing fraud investigation risk. |
| 8 | 🔴 URGENT | **RKLB** | $4,000 | HIGH (speculative) | SpaceX IPO halo. |

**Tranche 1 total: $60,000**

### Also This Week
- [x] Log Tranche 1 fills → Google Sheet + balances.csv ✅ done 4/16
- [ ] Log April balances → `data/balances-2026-04.csv`
- [ ] Confirm $22k HYSA label ("2026 taxes" reserve — retain intact)

### ✅ Jaclyn Data — April 2026 Update Complete
- [x] Jaclyn DBRX vested: 1,422 units @ $190 = **$270,180** ✅
- [x] Jaclyn DBRX unvested: 2,334 units @ $190 = **$443,460** ✅
- [x] Jaclyn Fidelity 401k: **$86,458** ✅
- [x] Jaclyn Databricks 401k: **$84,204** ✅
- [ ] **Jaclyn's bonus** — 18% of base; expected to land end of April → **update balances in early June**

---

## LATE APRIL – EARLY MAY — Tranche 2 ($26,000)

Top-off sizing after Tranche 1 execution:

| Status | Ticker | Amount | Notes |
|--------|--------|--------|-------|
| 🟡 PENDING | LLY | $5,000 | Complete position |
| 🟡 PENDING | VHT | $5,000 | Complete position |
| 🟡 PENDING | Citi (C) | $4,000 | Complete position |
| 🟡 PENDING | TSLA | $4,000 | Complete position |
| 🟡 PENDING | RTX | $3,000 | Complete position |
| 🟡 PENDING | UNH | $3,000 | Complete position |
| 🟡 PENDING | RKLB | $2,000 | Complete position |
| | **TOTAL** | **$26,000** | |

---

## DRY POWDER — $14,000 (held in HYSA)

Trigger-based deployment only:

| Trigger | Action |
|---------|--------|
| ANET drops to $120–125 | Deploy $10k (per original plan) |
| MSFT drops >15% post-earnings 4/29 | Add $4k to MSFT |
| GOOGL drops 10%+ during 2026 | Front-load next RSU proceeds into GOOGL |
| Black-swan VIX >30 sustained | Hold dry |

---

## MSFT BOUNCE + BUILD STRATEGY (New — April 2026)

**Structure:** Buy MSFT at drawdown → hold to long-term cap gains → rotate proceeds to GOOGL (your high-conviction structural thesis: 3-lab AI exposure via Gemini + Anthropic + xAI/SpaceX).

### MSFT Exit Rules (All Require Post-4/15/2027 for Long-Term Treatment)

| Trigger | Action | Tax Impact |
|---------|--------|-----------|
| MSFT hits $500 (+40%) AND past 4/15/2027 | Trim 50% → rotate to GOOGL | 15% LTCG |
| MSFT hits $580 (+62%) AND past 4/15/2027 | Trim remaining 50% → rotate to GOOGL | 15% LTCG |
| MSFT $500+ BEFORE 4/15/2027 | **Wait.** Tax drag (38.8% ST vs 15% LT) = ~24% of gain | — |
| MSFT flat for 18 months | Hold. Reassess only if thesis breaks | — |

### GOOGL Structural Build (via AMZN RSU Proceeds)

**Rationale:** Instead of lump-sum GOOGL in April (adds to AI concentration), accumulate GOOGL over 2026 using Amazon RSU vest proceeds at new 85% sell rate. Tax-neutral (RSUs taxed at vest regardless).

| Vest Window | Gross | Sell 85% | GOOGL Deploy | Running GOOGL Build |
|-------------|-------|----------|--------------|---------------------|
| May 2026 | ~$20,790 | $17,672 | **$10,000** | $10k |
| Aug 2026 | ~$20,790 | $17,672 | **$8,000** | $18k |
| Nov 2026 | ~$20,575 | $17,489 | **$6,000** | $24k |
| **Total 2026 GOOGL build** | | | **$24,000** | |

**Year-end 2026 GOOGL position:** ~$43k (existing $19k + $24k build).
**2027+:** MSFT trim proceeds (if triggers hit) layer on top. Target: $55–70k GOOGL by mid-2027.

---

## MORTGAGE — No Action Required

| Item | Detail |
|------|--------|
| Rate | 5.85% ARM |
| ARM type | 7-year fixed → locked until **October 2032** |
| After-tax effective rate | **3.80%** (5.85% × 65% — mortgage interest deductible at 35% bracket) |
| Refi target | 4.0–4.5% 30-year fixed |
| Current 30-yr fixed market rate | ~6.0–6.3% — refinancing now would INCREASE your rate |
| Decision | **Do not pay down. Do not refi yet.** Revisit when 30-yr fixed hits ~5.0%. |
| Rate alert | Set notification at 5.0% → call mortgage broker |

---

## ONGOING — Monthly / Quarterly / Annual

### Monthly
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | **Sell 85% of each Amazon RSU vest** (updated from 75%) | Higher concentration reduction rate reflects 76% household AI/tech exposure. Do NOT sell existing AMZN core position. |
| 🔁 ONGOING | Monitor RSU vesting (Jaclyn) | Post-IPO: sell 50–75% upon lockup expiration |
| 🔁 ONGOING | Update account balances | Log to `data/balances-YYYY-MM.csv` |

### Amazon RSU Vest Deployment Plan — 2026 (UPDATED 4/15)

**Rule:** Sell 85% of each vest (was 75%). Keep 15% for residual AMZN exposure. Deploy 100% of proceeds to **non-AI diversifiers + GOOGL structural build**.

**Standing rule:** No RSU proceeds go to MSFT, META, NVDA, AMZN, or any pure AI-infrastructure name. Proceeds are the non-AI rebalancing tool.

#### May Vests — Deploy ~$22,674 (UPDATED 5/6 — AMZN at $275)

| Date | Units | Est. Total (at $275) | Deploy (85%) |
|------|-------|----------------------|--------------|
| May 15 | 16 | ~$4,400 | ~$3,740 |
| May 21 | 81 | ~$22,275 | ~$18,934 |

**Confirmed allocation (5/6):**
1. GOOGL ~$15,174 (structural build — $10k plan + ~$5,174 surplus from AMZN price increase)
2. VHT $3,000 (complete April position)
3. LLY $2,500 (complete April position)
4. Citi $2,000 (complete April position)

**Timing:** Wait until after May 21 vest clears, then execute full allocation in one pass.

#### August Vests — Deploy ~$17,672

**Allocation priority:**
1. ANET $10,000 **ONLY if corrected to ~$120–125** — else GOOGL $8,000
2. GOOGL $6,000 if ANET trigger hits (else $8,000)
3. Non-AI underweight (healthcare/financials/defense) ~$3,500

#### November Vests — Deploy ~$17,489

**Allocation priority:**
1. ANET $10,000 (if not yet deployed)
2. GOOGL $6,000
3. Most underweight sector at YE review ~$1,500

**2026 total RSU proceeds deploying: ~$52,833**

### Quarterly (Mar / Jun / Sep / Dec)
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | Review 401(k) allocations for drift | Rebalance if >10% off target. **Next check: June 2026.** Accounts to check manually (no auto-rebalance): (1) **Galen — Amazon/Fidelity (~$140k):** targets 60% VG 2045 / 30% Inst 500 Index / 10% Small-Mid Cap. (2) **Jaclyn — Databricks/Fidelity (~$84k):** targets 30% Intl / 15% EM / 25% TRP All-Cap / 15% Mid-Cap / 10% Value / 5% Bonds. Jaclyn's Fidelity TRP 2055 (~$86k) auto-rebalances — no action needed. |
| 🔁 ONGOING | Check taxable portfolio sector weights | Run `check_allocations.py` |
| 🔁 ONGOING | Trim if any single position >25% liquid | Target: trim to 20% |
| 🔁 ONGOING | Databricks concentration check | Flag if >45% household or >70% Jaclyn's NW |
| 🔁 ONGOING | Household AI/tech concentration check | Target: reduce 76% → <65% by YE 2026 |

### Annual (January)
| Status | Action | Details |
|--------|--------|---------|
| 🔁 ONGOING | Comprehensive portfolio review | Update retirement projections |
| 🔁 ONGOING | Assess mortgage refi opportunity | Target: 4.0–4.5% fixed. Don't refi above 5.0%. |
| 🔁 ONGOING | Tax-loss harvesting sweep | Check all positions for unrealized losses |
| 🔁 ONGOING | Max 401(k) contributions | $23k each = $46k/yr household |
| 🔁 ONGOING | Evaluate backdoor Roth / mega backdoor Roth | $7k/person Roth + up to $50k+ mega backdoor |

---

## DO NOT DO — Standing Decisions

| Decision | Rationale |
|----------|-----------|
| ❌ Do NOT sell NVDA | 38% analyst upside. Tax friction too high. AI capex intact. |
| ❌ Do NOT add to NVDA | Already 9% household at overweight. |
| ❌ Do NOT sell existing AMZN position | 36% consensus upside, 0 sell ratings. AWS growing 30%+. |
| ❌ Do NOT add META | Correlated with MSFT. Picking one hyperscaler only. |
| ❌ Do NOT lump-sum GOOGL | Use RSU proceeds for structural build instead (tax-efficient, dampens AI concentration per deployment cycle). |
| ❌ Do NOT add to AMZN from any source | RSU vests add enough; sell 85% of each. |
| ❌ Do NOT deploy RSU proceeds to AI names | Proceeds are the non-AI rebalancing tool. |
| ⚠️ ~~Do NOT buy XLE or broad energy ETFs~~ — **RETIRED 2026-09-05** | **This was never Galen's rule — Claude set it in March 2026 on purely technical grounds (XLE RSI 75.98 at an all-time high, war premium judged temporary), then it was restated in April as a "structural oversupply thesis" that was never actually underwritten.** A timing call got promoted to a standing constraint and steered allocation for six months. Retired. No sector is off-limits on principle; energy, power, and insurance are all evaluated on current conditions like anything else. See [September 2026 Reassessment](./reports/September_2026_Portfolio_Reassessment.md). |
| ⚠️ ~~Do NOT buy EWJ / VWO right now~~ — **SUPERSEDED 2026-06-24** | VWO was bought 6/24/26 (84.603 sh) as part of the RSU diversification decision. Rule is stale. |
| ❌ Do NOT pay down mortgage | 3.80% effective after-tax rate. ARM locked to Oct 2032. |
| ❌ Do NOT refinance yet | Current 30-yr fixed (6.0–6.3%) higher than ARM (5.85%). |

---

## Guardrails — Auto-Check These

| Metric | Current | Target / Limit | Alert If |
|--------|---------|----------------|----------|
| Databricks % of household | ~38% post-tender | Keep <40% | >45% |
| Databricks % of Jaclyn's NW | ~63% post-tender | Keep <60% | >70% |
| Household AI/tech concentration | ~76% | Target <65% YE 2026 | >80% |
| Any single liquid position | NVDA | Keep <25% | >25% |
| Amazon % of household | ~14% | Keep <20% | >20% |
| Healthcare allocation | ~0.2% | Target 5–7% post-April deploy | <4% |
| Financials allocation | 0% | Target 3–5% post-April deploy | <2% |
| International (total) | ~5% (in 401k) | Target 8–10% | <5% |
| HELOC balance | $0 | $0 | >$0 |
| Cash + HYSA liquidity | ~$22k + $14k dry powder | Keep >$30k | <$20k |
| 30-yr fixed mortgage rate | 6.0–6.3% | Alert at 5.0% to call broker | <5.0% |

---

## 2026 Tax Snapshot (Updated 4/15)

| Event | Capital Gain / Event | Tax Rate | Est. Tax |
|-------|---------------------|----------|----------|
| 2025 federal taxes (paid 4/15/26) | — | Prior year reconciliation | **$51,000 paid** |
| Databricks tender ST portion | ~$9,880 | 38.8% (ST + NIIT) | ~$3,834 |
| Databricks tender LT portion | ~$32,175 | 15% LTCG | ~$4,826 |
| Property sale (recreational) | ~$50,000 | 15% LTCG | ~$7,500 |
| Crypto + KSCP loss harvesting | ~($2,405) | Offset | ~($360) |
| **Net 2026 capital gains tax (est.)** | | | **~$15,800** |

*Washington state: 7% capital gains applies above $250k threshold — not triggered.*

---

## Key Milestones

| Date | Milestone | Target Net Worth |
|------|-----------|-----------------|
| Feb 2026 | Baseline | $1,780,780 |
| Mar 2026 | Post-tender + HELOC eliminated | ~$1,930,780 |
| Apr 2026 | Post-tax + house expenses + Tranche 1 deploy | ~$1,840,000 |
| Apr 29, 2026 | **MSFT Q3 earnings** (checkpoint) | — |
| May 2026 | First AMZN vest under new 85% rule → GOOGL build starts | — |
| Jun 2026 | SpaceX IPO — reassess TSLA/RKLB | — |
| Aug 2026 | 6-month portfolio check | ~$2,000,000 |
| Feb 2027 | 1-year target | ~$2,100,000–$2,300,000 |
| Apr 15, 2027 | MSFT long-term cap gains threshold — rotation window opens | — |
| Oct 2032 | ARM adjustment date — must refi before this | — |
| 2035–2036 | Retirement (age 47–48) | $6,000,000–$7,000,000 |

---

## Reference Documents

- [April 2026 Deployment Brief](./reports/April_2026_Deployment_Brief.md) — Full conviction framework + scenario modeling
- [Financial_Planning_Context_2026.md](./Financial_Planning_Context_2026.md) — Household baseline, asset inventory, 3-lab GOOGL thesis
- [data/balances.csv](./data/balances.csv) — Live position tracking
