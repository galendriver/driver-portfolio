# Portfolio Reassessment — September 5, 2026
**Galen & Jaclyn | Full account reconciliation + two-horizon strategy**

*First pass where every account was pulled from source. `balances.csv` is now reconciled truth; prior versions were materially incomplete.*

---

## Executive Summary

**Net worth: $2,165,905.** Liquid $1,469,335. Plus $152,004 gross in unvested Amazon RSUs.

Three things matter out of this review:

1. **~$385k of assets were untracked or mispriced** — a whole Nordstrom 401(k), all of BECU, 84 shares of AMZN, and $30k of crypto zeroed by a code bug. The dashboard has been understating net worth all year.
2. **The macro regime flipped.** The Fed is now expected to *hike* (Sept 16, ~56–66% odds, Warsh hawkish). Every plan in this repo was written assuming easing or neutral. That assumption is dead.
3. **Databricks + Amazon = 52% of net worth and 100% of household income.** This is the actual risk to the retirement plan, and it dwarfs anything we do with the dry powder.

The 12-month aggressive mandate and the 2035 retirement plan are **not in conflict** — they're funded by different pools. Details in the two-horizon section.

---

## Reconciled Position

| Bucket | Value |
|---|---|
| US equities | $907,497 |
| Databricks private equity (vested $321,510 + unvested $375,060) | $696,570 |
| Retirement accounts | $394,194 |
| Crypto | $89,527 |
| Cash | $78,117 |
| **Total** | **$2,165,905** |
| *Unvested AMZN RSUs (gross, not yet yours)* | *$152,004* |

### What was found tonight

| Item | Amount | Note |
|---|---|---|
| Nordstrom 401(k) (Fidelity 7883P) | $53,698 | Prior-employer plan, just consolidated into Fidelity. Allocation never reviewed. |
| BECU (3 accounts) | $45,499 | Never tracked. $36,493 of it in a money market. |
| AMZN in Fidelity TOD | +$21,800 vs. record | CSV had 251.6 sh; actual 335.938 sh |
| stETH + RNDR | $30,097 | Not missing — zeroed by a price-fetch bug |
| GOOGL 14 sh (-0552) | $4,738 | In no record anywhere |
| SOFI, QBTS, HSA, brokerage cash | ~$9,700 | All previously untracked |

### Corrections

- **Account ownership was wrong.** The April Tranche 1 (~$97k) is in **Jaclyn's** -0552 account, not Galen's. It was funded by her Databricks tender. Every his/hers split in prior docs was miscomputed.
- **Databricks:** 1,689 vested shares ($321,510 @ $190) + 1,974 unvested units ($375,060). Prior numbers were April unit counts, stale by two vesting cycles.
- **401(k)s:** Galen's Amazon plan $140,661 → $156,797. Jaclyn's was recorded as one "TRP 2055" line at $86,458; it's actually two plans — F5 $93,390 + Databricks $90,308.

---

## Macro Regime — What Changed Since June

| | June 2026 assumption | September 2026 reality |
|---|---|---|
| Fed | Easing / on hold | **Hike expected Sept 16** (56–66%); Warsh hawkish at Jackson Hole |
| Inflation | Moderating | Sticky; energy-driven; stagflation is the live tail |
| Tariffs | Escalating | IEEPA tariffs struck down by SCOTUS (Feb), refunds flowing; Section 122 expired July 24 |
| Iran war | Ceasefire hopes | Ongoing. Hormuz shipping still below normal. Energy costs elevated. |
| Defense | War-premium tailwind | **Defense stocks have not rallied.** The RTX thesis underdelivered. |
| SpaceX | Pre-IPO | **Public (SPCX).** Absorbed xAI. ~$2.5T cap. Buying Cursor for $60B. $147.95, off a $225 high. |
| AI capex | Questioned | **Accelerating.** GOOGL raised to $195–205B, AMZN to $220B. NVDA guiding ~$100B FQ3. |

**Implication:** the portfolio is almost entirely long-duration growth, priced off discount rates that are now going the wrong way. The AI *fundamentals* remain strong; the *multiple* is what's exposed.

---

## The Real Risk

Rough concentration across the reconciled book:

| Exposure | Value | % of NW |
|---|---|---|
| Databricks (vested + unvested equity) | $696,570 | 32.2% |
| Amazon (Key + TOD, owned shares) | $435,056 | 20.1% |
| NVIDIA | $217,460 | 10.0% |
| Other AI/tech (AMD, PLTR, MSFT, GOOGL/GOOG, AAPL, OKLO, small caps) | $165,054 | 7.6% |
| Crypto | $89,527 | 4.1% |
| **AI/tech/correlated total** | **$1,603,668** | **74.0%** |
| Non-AI diversifiers (VHT, LLY, C, RTX, UNH, AVUV, VWO, WMT) | $89,927 | 4.2% |

*Amazon is 20.1% of net worth on owned shares alone; counting the $152,004 of unvested RSUs against an expanded base it's 25.3%.*

The <65% AI/tech target set in April was never reached — 74% today against a 77% starting point, and essentially all of that improvement came from market moves rather than deliberate action. The diversification actually executed (~$12.7k of AVUV + VWO) is a rounding error against the concentrated positions.

**But the sharper point is the correlation between assets and income:**

> **Databricks and Amazon together are 52% of net worth *and* 100% of household income.**

If Databricks stumbles, Jaclyn's equity (32% of NW) and the RSU stream funding future contributions break *simultaneously*. Same structure for Galen at Amazon. This is not market risk that diversification across tech names fixes — it is single-employer risk, twice over.

---

## Two-Horizon Framework

The mandate is "maximize 12-month returns with higher risk appetite" **and** "retirement is critical." These don't conflict, because they're funded by different pools and constrained by different things.

### Horizon A — 12-month aggressive sleeve (~$60k, 2.8% of NW)

This is the only capital that can actually be moved without triggering large tax bills. Because it's small relative to net worth, **it can afford to be genuinely aggressive.** Losing all of it changes the retirement math by roughly nothing; the concentrated book dominates.

The honest constraint: *adding more AI exposure is not risk-taking, it's leverage on a position already held.* Real risk-taking here means concentrated bets in things **uncorrelated to the existing $1.6M.**

**Deployment (aggressive tilt, per stated appetite):**

| Allocation | Amount | Thesis |
|---|---|---|
| **VST (Vistra)** | $15,000 | Best new idea. AI power demand is a physical bottleneck: data centers → 12% of US power by 2028 (DOE), grid 19GW short by 2035 (BNEF). VST is down 24% from highs, CEO bought $1.17M personally, and formed the Helix JV with **NVIDIA/KKR/Kuwait IA**. AI-linked upside, different factor, contracted cash flows. Preferred over CEG ($261, heavily re-rated). |
| **SPCX** | $15,000 | The Musk/xAI/Cursor/robotics bet. Only vehicle for xAI + Cursor + Starlink + launch. **Buy after Sept 9** — 319M shares unlock that day; never buy into a known supply event. Further tranche Dec 8; Musk locked until June 2027. |
| **Healthcare (VHT / LLY)** | $10,000 | Biggest sector gap, all three positions working (+18–26%), defensive against stagflation, zero AI correlation. |
| **AVUV + VWO** | $10,000 | Right call in June, funded at rounding-error size. Small-cap value and EM are the only things owned that aren't long-duration US tech. |
| **T-bills / Treasury MMF** | $10,000 | ~5% risk-free if the Fed hikes. In a hiking regime with a 74% AI book, cash is a position — it's the ammunition for a drawdown. |

**Not recommended for this horizon:**
- **More AI/semis** — fundamentals fine, but $1.6M of it is already owned.
- **TSLA for robotics** — Musk guided expectations *down*; Optimus is 2027+, Cybercab needs regulatory clearance, $25B capex, opex +37%. Nothing resolves inside 12 months. 29 shares already held across two accounts.
- **Insurance** — asked about, and the answer is no on data, not principle: commercial P&C premiums **declined in Q1 2026 for the first time in ~9 years**, ending a 33-quarter streak. Combined ratio deteriorating 95 → ~96.9. Loss costs 6–8% outpacing rate. A decelerating margin cycle.
- **OKLO adds** — thesis is right, clock is wrong. See below.

### Horizon B — Retirement (2035–2036, target $6–7M)

**The required return is lower than it looks.** Starting from $2.166M with ~$150k/yr of combined contributions (401k $46k + RSU streams + savings), an **8% CAGR** reaches ~$6.5M by 2036 — inside the target band. The plan does not require heroic returns.

What it requires is **not blowing up**, and the contribution stream continuing. Which makes the dominant risks:

1. **The next Databricks tender is the single highest-value financial event available.** 32% of net worth is illiquid, in one private company, valued off a stale $190 mark. Tenders are the only liquidity window. When one is announced, selling meaningfully into it matters more than every other decision in this document combined.
2. **Amazon RSU discipline needs to actually execute.** The 75% rule has now been missed for two consecutive vests. The mechanism isn't broken — it just isn't being run.
3. **Build the uncorrelated base.** AVUV + VWO are the right instruments at the wrong size. Every future RSU deployment should go here by default, not into another tech name.
4. **Housekeeping with real compounding value:** 401(k) drift check (overdue since June, now four accounts including the unreviewed Nordstrom plan), fund the HSA if eligible (currently $0.12, triple-tax-advantaged), confirm backdoor Roth is actually happening.

**The OKLO case is a good illustration of the two horizons.** The thesis — micro-nuclear levered to AI power demand — is validated: Meta prepay-for-power deal, NRC accelerated design approval, achieved self-sustaining fission. But first revenue is late 2027/early 2028, Ohio is 2030, full power 2034. It is a *retirement-horizon* holding that happens to sit in a taxable account. Hold at 0.6% of NW, don't add on a 12-month mandate, and stop treating it as an orphan position — the thesis is now written into `balances.csv`.

---

## Tax Mechanics

**Free to sell (basis ≈ market):**
The 84.319 AMZN shares from the unsold May + Aug 2026 vests. Basis $259.25–$263.78 vs. $258.51. Selling is **tax-neutral, slightly loss-generating.** Cleanest capital available.

**Harvest candidates:**

| Position | Loss |
|---|---|
| RKLB (72 sh) | −$1,520 |
| TSLA (25 sh, -0552) | −$1,429 |
| NOK (122 sh) | −$795 |
| LUNR (30 sh) | −$648 |
| **Total** | **~$4,392** |

**Locked until 4/16/2027 — do not touch:**
All Tranche 1 winners: LLY +$3,550, VHT +$2,663, MSFT +$2,312, UNH +$1,313, C +$766, RTX +$418. Short-term rate 38.8% vs. 15% long-term.

> ⚠️ **MSFT is at $499.70 and the tracker's $500 trim trigger is live right now. Do not take it.** The trigger was always conditioned on being past 4/15/2027. Selling today costs ~24% of the gain in tax drag.

**Expensive:** NVDA carries $179,657 of long-term gain. A 10% trim ≈ $3,300 in tax. WA's 7% capital gains tax needs >$250k of gains — only a large Databricks event triggers it.

---

## Action List

**Do now — raises ~$28k, banks ~$4.4k of losses, costs ~$0 in tax:**
1. Sell **100%** of the May + Aug 2026 AMZN RSU lots (84.319 sh, ~$21,800). Not 75% — the rule was set when AMZN was a smaller share of net worth, and these specific shares are tax-free to sell.
2. Cut **LUNR** and **NOK** (~$1,670). Third flag.
3. Cut **RKLB** (~$4,627). Thesis inverted — bought as a SpaceX halo play; SpaceX is now a public competitor.
4. Move the **BECU money market ($36,493)** to a Treasury MMF. ~$600–900/yr of free yield, zero risk, no tax consequence, independent of every other decision here.

**Deploy (~$60k):** per the Horizon A table. **SPCX only after Sept 9.**

**Fix the data pipeline:** `web/server.py` reads the **Google Sheet**, not `balances.csv`. The Sheet is stale and contains a trailing-tab typo in the stETH `yf_symbol` — and since the code does `if yf_symbol … elif cg_id`, it never falls back to CoinGecko. Either update the Sheet from the reconciled CSV or flip `load_rows(use_sheet=False)`. Until then the dashboard understates net worth by ~$385k.

**Schedule:**
- **Sept 9** — SPCX Day-90 unlock (319M shares). Entry point after, not before.
- **Sept 16** — FOMC. A hike repricing long-duration growth is the main near-term risk to the book.
- **Nov 15 / Nov 21** — next AMZN vests (96 units). Execute the sell rule on time this cycle.
- **Dec 8** — next SPCX unlock tranche.
- **April 16, 2027** — Tranche 1 LTCG date. Nothing sells before this.
- **Next Databricks tender** — the one that actually matters.

---

## Guardrails — Updated

| Metric | June record | Actual (Sept 5) | Target |
|---|---|---|---|
| Net worth | ~$1.90M (app) | **$2,165,905** | — |
| AI/tech concentration | ~77% | **74.0%** | <65% ❌ |
| Databricks % of household | ~38% | **32.2%** | <40% ✅ |
| Amazon % of household | ~14% | **20.1%** | <20% ❌ (25.3% incl. unvested RSUs) |
| Single largest liquid position (NVDA) | — | 10.0% | <25% ✅ |
| Cash + HYSA | ~$36k | **$78,117** | >$30k ✅ |
| Healthcare | ~0.2% | ~2.2% | 5–7% ❌ |
| International | ~5% | ~5.2% | 8–10% ❌ |
| HELOC balance | $0 | $0 | $0 ✅ |

**Amazon at 20.1% is the guardrail breach that matters** — just over the <20% limit on owned shares alone, and 25.3% once the unvested RSU pipeline is counted. Driven by the Key transfer plus two unsold vests.

---

## Corrections to Prior Guidance

- **The "no energy ETFs" rule was Claude's, not Galen's**, and has been retired. It was set in March 2026 on technical grounds (XLE RSI 75.98 at an all-time high, war premium judged temporary), then restated in April as a "structural oversupply thesis" that was never underwritten. A timing call became a standing constraint and steered allocation for six months. No sector is prohibited on principle.
- **OKLO was previously grouped with LUNR/NOK as "no thesis."** That was wrong — the thesis existed, it just wasn't written down. Now documented.
- **The `EWJ / VWO` prohibition** was superseded by the 6/24 VWO purchase and has been marked stale.

## Open Questions

1. Nordstrom 401(k) — what's it invested in? $53,698 with an unreviewed allocation.
2. Kishu Inu still shows a dust balance despite being reported sold in the 3/12/26 harvest. Confirm closed.
3. SOFI and QBTS — no documented thesis. Underwrite or cut.
4. Is the $15k painting/repairs bill (due May) actually paid?
5. HSA eligibility — is either of you on an HSA-qualified plan?
6. Databricks next tender — timing and expected price.
