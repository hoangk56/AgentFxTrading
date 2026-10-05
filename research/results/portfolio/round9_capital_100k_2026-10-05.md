# Round 9: what a $100,000 account changes (2026-10-05)

The user asked (Vietnamese) "reseach cho tôi chiến thuật và thuật toán mới với mức vốn $100000": new strategies for a
$100k account. Asked where the money would run, the user chose three directions and relaxed the limits of
`research/PROMPT.md` (hold weeks to months, many positions, lots may depend on capital):

| stream | direction | venue |
|---|---|---|
| I | the current IC Markets cTrader account at $100k: what the size and the relaxed limits unlock, and C3 at that size | IC cTrader, the 26 symbols (IC's share CFDs are MT5-only, not on cTrader) |
| O | S&P 500 index options: harvesting the volatility risk premium | a listed-options broker (IBKR: SPX / XSP), not cTrader |
| P | a $100k prop-firm account on cTrader running C3 | prop firms that offer cTrader |

The $100k is a research premise, not a funded account. The user confirmed afterwards that this round is strategy
research only. So the sizing, prop-firm and "what it takes to run" parts below show what the numbers imply. They are
not a deployment plan, and nothing was changed on the bots.

Three parallel subagents worked from one brief; the briefs, hypotheses (written before their numbers) and the prop
simulator are in [round9_capital_100k/](round9_capital_100k/). HOLD (2025-01..2026-09) was not opened for any new
series. The process section lists the exceptions and disclosures.

## Answer

**No new algorithm.** The extra capital does not create a new edge on any of the three venues. What it changes is
how C3, the one proven edge, can be sized and where it can run.

| direction | verdict | key numbers |
|---|---|---|
| I-A: C3 on IC at $100k | **scales cleanly**; the practical result | 1 % risk per leg = 1.4-2.5 lots; spreads at the 18:00 / 00:55 / 02:55 UTC minutes are ordinary; floating losses add ~10 % to the closed-trade DD. Risk per leg for a 10 / 20 / 30 % DD tolerance (rule fixed before computing): **0.375 / 0.75 / 1.5 %** |
| I-B: six new IC families (macro fair value ×3, COT, crash buying, net-swap carry) | none passes | best: S&P 500 after VIX > 30, net > 0 in every era but NW t 1.35-1.91, max DD 47 %; ~237 cells, max \|t\| 2.84 at chance level |
| O: index option selling (VRP) | real premium, **no alpha** over SPX at the same beta | VIX exceeds next-30-day realised vol by 4.1 points (t 15). PUT alpha +1.5 %/yr (t 1.3) over 1996-2024, but **-3.3 %/yr in 2016-21**. Every short-vol index lost alpha after 2015 (WPUT -7.2 %/yr, t -3.1). No timing overlay survives the checks; costs matter only for condors and weeklies |
| P: C3 at a prop firm | **positive EV on paper**, with firm credit risk | FTMO 2-Step (Swing), 1 % per leg with an account guard: P(pass both phases) 0.97, median 238 days to funded, expected payouts $16.4k in the first funded year for a €540 fee. No-edge baseline: $1.1k. Half edge: P(pass) 0.72, EV $7.0k |

What the numbers imply for a hypothetical $100k account, in order of the evidence behind them:
1. **Own capital on IC:** run C3 unchanged at **$750 per leg (0.75 %)** for a 20 % DD tolerance. Backtest ~+17 %/yr
   of the starting capital, ~+15 % after the assumed size slippage, ~+8 % if the edge is half. Mark-to-market max DD
   5.3 %. 3-year 95th-percentile DD: 12 % (full edge) to 19 % (half edge). This is an ops change (`PUT
   /api/bots/{name}`) plus `MaxLotsPerTrade` 5 → 10-15.
2. **A prop account:** the same C3 can run there with an account-level daily-loss guard, which needs cBot changes
   (P-C below). It is the same bet as item 1: both lose on the same gotobi days, so the risks add up.
3. **Options:** selling puts on XSP is equity beta with a fatter left tail, not a strategy. One cash-secured XSP
   ATM put a month is about 35 % SPX + 65 % T-bills, with a worse worst month.

## I. IC Markets cTrader at $100k

### I-A. C3 at size

Inputs:
- C3's cTrader trade CSV (`gotobi_cbot_trades.csv`, 2016-26) used in full. C3 already passed its holdout; this is
  sizing, not discovery.
- Intrabar paths rebuilt from IC M1 for 2016-24 (cut at 2025). For 2025-26 legs, only the CSV close is used.
- JP-holiday gotobi days dropped.
- The stop is rebuilt from M1 (3 × ATR20 H1) and matches the CSV lots within 0.01 lot on 96 % of legs.

Non-holiday mean R per leg is +0.058 (2016-21 +0.062, 2022-24 +0.045, 2025-26 +0.066). That splits as gross +0.063,
commission -0.014 and swap +0.007; the swap uses 2026 rates applied to every year.

Full tables are in [round9_capital_100k/I_c3_at_size.txt](round9_capital_100k/I_c3_at_size.txt).

**Lots per leg at $100k:**

| risk / leg | lots, median (max): USDJPY / EURJPY / GBPJPY | 3-leg event notional, median (max) | margin at 1:30, median (max) | legs > 5 lots |
|---|---|---|---|---|
| 0.25 % | 0.64 (2.6) / 0.51 (1.5) / 0.36 (0.9) | $168k ($515k) | $5.6k ($17k) | 0 % |
| 0.5 % | 1.27 (5.2) / 1.02 / 0.72 | $335k ($1.03M) | $11k ($34k) | 0.1 % |
| 1 % | 2.54 (10.4) / 2.03 (6.1) / 1.43 (3.6) | $671k ($2.06M) | $22k ($69k) | 1.5 % |
| 1.5 % | 3.81 (15.6) / 3.05 / 2.15 | $1.01M ($3.09M) | $34k ($103k) | 10 % |
| 2 % | 5.08 (20.7) / 4.06 (12.2) / 2.86 | $1.34M ($4.12M) | $45k ($137k) | 26 % |

- **Notional per $1 of risk** is 254 / 228 / 186 (median), so today's $50 leg is $9-13k of notional.
- **Sizes are largest on the quietest days**, when the stop is tightest.
- **The binding cap is the bot's own `MaxLotsPerTrade` of 5.** IC's per-order maximum could not be verified (IC's
  site was unreachable), but no leg comes near 50 lots.
- **Leverage:** at 1:30, 1.5 % per leg or more can need more margin than the equity. At the live 1:1000 this does
  not bind.

**Spreads at C3's minutes** (2016-24, median pips):

| minute | USDJPY / EURJPY / GBPJPY | ticks per minute (UTC day's median) |
|---|---|---|
| 18:00 long entry | 0.1 / 0.3 / 0.7 | 59-103 (53-85) |
| 00:55 fix | 0.1 / 0.4 / 1.0 | 124-145, about 2× the day |
| 02:55 exit | 0.1 / 0.4 / 0.9 | 43-64 |
| Sunday 22:0x reopen (13 % of longs) | 0.8 / 1.5 / 2.5 (90th percentile 3.4-5.9) | 36-58 |

**Slippage:**
- Each extra pip per side costs 2 × slip / stop per leg. At 0.1 / 0.2 / 0.5 / 1.0 pip per side, the edge keeps
  94 / 87 / 69 / 37 %.
- The assumed impact at size keeps 89 % of the edge at 1 % risk and 77 % at 2 %. The assumption is 0.1 / 0.2 /
  0.3 pip per side up to ~3 lots, doubled for 3-10 lots. It comes from a square-root impact model; it is not
  measured, since there is no depth-of-market data.

**Post-hoc flag, not a rule:** the Sunday-reopen long legs pay 0.04 R of spread and earned R +0.035 (t 1.2),
against +0.083 for the 18:00 longs.

**Drawdown at fixed $ risk** (a fraction of the starting $100k; mark-to-market at each minute's worst point, 2016-24):

| risk / leg | closed DD | MTM DD | worst day | avg return %/yr of start (2016-26) | compounding: MTM DD / CAGR |
|---|---|---|---|---|---|
| 0.25 % | 2.0 % | 2.2 % | -1.2 % | 5.8 | 2.9 % / 5.9 % |
| 0.5 % | 3.5 | 3.9 | -2.3 | 11.6 | 5.8 / 12.1 |
| 0.75 % | 4.8 | 5.3 | -3.4 | 17.5 | 8.6 / 18.5 |
| 1 % | 5.8 | 6.5 | -4.5 | 23.3 | 11.3 / 25.2 |
| 1.5 % | 8.1 | 8.7 | -6.5 | 34.9 | 16.6 / 39.2 |
| 2 % | 10.5 | 11.3 | -8.3 | 46.5 | 21.8 / 54.2 |

- **In R:** max DD 10.5 R closed against 11.7 R marked to market; worst day -5.35 R.
- **Monthly:** annual Sharpe 2.1, worst month -5.2 R, 71 % of months positive, 11/11 years positive. These are
  backtest figures before size slippage.
- **Legs beyond -1.05 R:** 17 of 3,627, the worst -2.0 R. They came from the 2022-02-27 Sunday reopen, the UK exit
  poll on 2017-06-08, and stops hit by spread spikes at the 21-22 UTC rollover.

**Block bootstrap.** 5,000 paths, blocks of 10 gotobi days, fixed $ sizing. The table gives P(MTM DD ≥ 10 / 20 / 30 %)
within 3 years:

| risk / leg | full edge | edge halved |
|---|---|---|
| 0.375 % | 0 / 0 / 0 % | 4 / 0 / 0 % |
| 0.5 % | 1 / 0 / 0 | 15 / 0 / 0 |
| 0.75 % | 12 / 0 / 0 | 46 / 3 / 0 |
| 1 % | 32 / 1 / 0 | 73 / 11 / 1 |
| 1.5 % | 70 / 7 / 1 | 95 / 35 / 8 |
| 2 % | 87 / 18 / 2 | 99 / 59 / 22 |

- **Compounding is worse:** at 1 % per leg the probabilities are 64 / 1 / 0 with the full edge and 91 / 14 / 1
  halved.
- **The sizing rule was fixed before computing:** the largest risk with P(DD ≥ tolerance in 3 y) ≤ 10 % under the
  halved edge, fixed $. It gives **0.375 % for a 10 % tolerance, 0.75 % for 20 % (1.0 % on the 2016-26 pool), and
  1.5 % for 30 %**.

**Expected $ at 0.75 %** (an estimate, not a measured figure): ~403 legs a year × +0.050 R after size slippage ×
$750 ≈ **$15k a year**. With the edge halved, ~$8.5k.

**IC volume rebates:** not verified (site unreachable). C3 at 1 % trades ~70 lots a month. A $1/lot rebate would be
worth +0.002 R per leg, 3.7 % of the edge, which changes nothing.

### I-B. New mechanisms on IC's 26 symbols (design 2004-15, checks to 2024, HOLD cut at load)

| family (mechanism, source) | data / era | gross | net | t / Sharpe | verdict |
|---|---|---|---|---|---|
| H1 gold vs 10y TIPS + dollar, residual reversion (Erb & Harvey 2013) | Dukascopy + IC 2004-24, weekly | Sharpe -0.46 | -2.8 %/yr | NW t -2.0. The residual trends (momentum sign, t 2.6 at 8 weeks in 2004-15) | fail |
| H2 USDJPY vs US-JP 2y/10y spread | 2004-24 | Sharpe -0.44 | Sharpe -0.59 | t -2.5; momentum sign in all eras | fail |
| H3 AUD/NZD/CAD vs gold, WTI and rate gap (Chen & Rogoff 2003) | 2004-24 | Sharpe -0.30..+0.01 | book Sharpe -0.26 | t -1.25; reverts only in 2022-24 | fail |
| H4 COT speculator z, contrarian, 4/8/12-week cohorts, 14 markets | CFTC 2000-24 | Sharpe -0.12..0.00 | -0.29..-0.33 | 152 cells, max \|t\| 2.19 (3 with \|t\| ≥ 2 vs 7 by chance) | fail |
| H5a S&P 500 after a ≥ 10 % drawdown, hold 21/42/63 days | SPX 1990-2024 | +2-3 %/yr | ~0 after long financing (r + 5.2 %) | negative in 1990-2015 | fail |
| H5b S&P 500 after VIX > 30, hold 21/42/63 days (Nagel 2012) | 1990-2024 | +4.1-4.9 %/yr | +2.0-2.9 %/yr | NW t 1.35-1.91; > 0 in every era; beats buy-and-hold by +5.4 bp per invested day (t 2.2, 63 days); max DD 47 %; 13/22 active years | fail (t, DD) |
| H6 carry book on positive net IC swap only, ≤ 10 legs, equal vol | 2004-24 | price -2.4, swap +3.3 %/yr | +0.7 %/yr at 12.6 % vol | Sharpe 0.05; 2008 -38 % | fail |
| H7 multi-strategy book with C3 | | | | every book's \|ρ\| with C3 ≤ 0.06 | nothing to add |

About 237 cells in all; chance gives ~11 with |t| ≥ 2 and a maximum near 3. The observed maximum is 2.84 (H3
AUDUSD 2022-24). FRED, Yahoo and IC's site were unreachable for this stream, so the series were substituted, each
as an amendment written into HYPOTHESES_I.md before its numbers:
- US Treasury yield curves in place of DFII10/DGS;
- BIS policy rates;
- EIA WTI spot;
- CBOE SPX/VIX;
- an FX-panel dollar index.

Missing: copper, and indices other than SPX before 2016.

## O. S&P 500 index options, the volatility risk premium

Data:
- **CBOE strategy indices** (42 series) cut at 2024-12-31, plus Yahoo ^SP500TR and ^IRX.
- **Eras:** PRE 1988/1996-2015 for design, CHECK1 2016-21, CHECK2 2022-24.
- **Costs:** IBKR plus Cboe fees, and half-spreads from a 2026-10-05 CBOE delayed-quote snapshot. The snapshot was
  deleted after the ratios were extracted.
- **Notes:** index rules and fees are in
  [round9_capital_100k/O_cboe_methodology_and_fees.txt](round9_capital_100k/O_cboe_methodology_and_fees.txt).

**O-A. The premium is real; the alpha is not.**

| hypothesis | data / era | result | verdict |
|---|---|---|---|
| A1 VIX vs next-30-day realised vol (Carr & Wu; Bollerslev, Tauchen & Zhou) | 1990-2024 | +4.1 vol points (t 15.3), PRE / CHECK1 / CHECK2 4.3 / 3.9 / 3.2, positive at 83-86 % of month-ends. VIX9D +3.7; **VIX1D -2.4** (2022-05..2024) | premium real in every era |
| A2 PUT, ATM monthly put-write (Ungar & Moran; Israelov & Nielsen) | 1996-2024 | excess 6.5 %/yr, Sharpe 0.61 (SPX 0.56), beta 0.59, alpha +1.5 %/yr (t 1.27); by era +2.7 (t 2.1) / **-3.3** / +0.9 | fail |
| PUTY, 2 % OTM | 1988-2024 | Sharpe 0.56, beta 0.41, alpha +0.9 % (t 0.86) | fail |
| WPUT, weekly | 2006-2024 | Sharpe 0.31, alpha -2.1 % (t -1.6); by era +1.2 / -6.0 / -6.1 | fail |
| BXMD, 30-delta covered call | 1988-2024 | Sharpe 0.65, beta 0.81, alpha +1.0 % (t 1.67); by era +1.9 (t 3.0) / -2.4 / -0.3 | fail |
| CNDR, iron condor | 1988-2024 | Sharpe 0.42, alpha +1.8 % (t 1.6); Sharpe by era 0.62 / **-0.40** / -0.01 | fail |
| BXM, BFLY, CMBO, PUTD, PUTVM, CLL(Z), PPUT, VXTH, RXM | | best full-sample alpha t 1.44 | fail |

- **Alpha after 2015 minus before:** PUT -3.9 %/yr, WPUT -7.2 (t -3.1), BXMD -3.3 (t -2.0), CNDR -5.4, BFLY -7.0.
  Across 16 indices the best full-sample alpha t is 1.67, below the ~2.0 that chance gives.
- **Tails of PUT:** worst month -17.7 %, max DD -37 %, skew -1.6. In Sep-Nov 2008 it lost -27.6 % (SPX TR -29.6 %);
  from 19 Feb to 23 Mar 2020 it lost -28.9 % (SPX TR -33.8 %).

**O-B. Retail costs** (per contract: SPX ~$1.45, XSP ~$0.80; half-spread as % of mid: SPX ATM monthly 0.23 %, 3-8
delta 1.4 %; XSP 1.5-2× SPX):

| index, net on XSP | cost %/yr | net Sharpe | net alpha (t) |
|---|---|---|---|
| PUT | 0.13 | 0.60 | +1.4 % (1.17) |
| BXMD | 0.13 | 0.64 | +0.9 % (1.48) |
| WPUT | 0.41 | 0.29 | -2.4 % (-1.8) |
| CNDR | 1.06 | 0.27 | +0.8 % (0.69) |
| BFLY | 1.34 | 0.01 | -0.5 % |

**O-C. Timing overlays.**
- **Setup:** 8 rules × PUT/CNDR/WPUT, chosen on PRE. Each was compared with 1,000 random on/off sequences of the
  same in-market share.
- **The best PRE cells reversed in the checks.** PUT "sell only if VIX - RV20 > 0" gained +0.22 Sharpe in PRE
  (p 0.015), then -0.24 / -0.06 in CHECK1 / CHECK2. WPUT "VIX - RV20 > 4" gained +0.53 in PRE, then -0.06 / +0.24.
  Chance alone gives a smallest p of ~0.04 over 24 tests.
- **VIX/VIX3M < 1 hurt** all three indices in PRE.
- **The 200-day trend filter** halved PUT's DD in PRE and 2022-24. It did nothing in 2020 and cost 0.27 of Sharpe
  in 2016-21.

**O-D. Defined risk does not help.** The bought wings (deep OTM puts) are the most overpriced options.
- **Real-price spread:** a 2 %/5 % OTM put spread built from real index prices (PUTY plus PPUT's long put) had net
  alpha -2.8 %/yr (t -2.2) and a max DD of -44 %.
- **Model spread, not usable:** a Black-Scholes-from-VIX model with a SKEW-scaled skew prices short ATM puts well,
  but is too optimistic for long wings (+0.40 %/month error on the real-price spread in PRE). Its put-spread
  results are not usable.
- **Return per unit of tail** (annual excess / |worst 21 days|), full sample / 2016-24:

  | | full sample | 2016-24 |
  |---|---|---|
  | SPX TR | 0.27 | 0.41 |
  | BXMD | 0.25 | 0.28 |
  | PUT | 0.23 | 0.22 |
  | CNDR | 0.13 | -0.21 |

**O-E. Equity beta.**
- **PUT vs SPX at the same beta:** full sample, excess 6.4 vs 5.1 %, Sharpe 0.60 vs 0.56, worst month -17.7 vs
  -9.8 %. In 2016-24: 6.0 vs 7.3 %, Sharpe 0.60 vs 0.83.
- **Correlation with C3** (2016-24): daily -0.001, monthly +0.10.

**If the exposure is wanted anyway:**
- **Trade:** 1 XSP ATM put a month, sold at the 3rd-Friday roll with a limit at mid, cash-secured in T-bills.
  That is leverage ~0.6 at SPX 5,000-6,000.
- **Expect:** ~6 %/yr compound, max DD -18 to -23 %, worst cycle ~-17 %.
- **Leverage caps:** keep leverage ≤ 0.85 for a 2008-like cycle to cost ≤ 20 % (≤ 0.72 for 2020).
- **Running it:** about 12 orders a year, so manual is fine. IBKR API code would be new; nothing in this repo
  applies.

## P. A $100k prop-firm account running C3

**Rule survey, accessed 2026-10-05:**
- ftmo.com, the5ers.com and fxify.com resolve to 127.0.0.1 on this Mac, and the block was not bypassed. FTMO's
  rules come from academy.ftmo.com / promo.ftmo.com and search summaries of the official pages.
- Some of The5ers' fees are third-party.
- The page dumps behind each cell stay in the session scratchpad, not in the repo.

| plan | fee | targets | daily loss (basis, reset UTC) | max loss | payouts | what bites C3 |
|---|---|---|---|---|---|---|
| FTMO 2-Step | €540, refunded with the 1st payout | 10 % / 5 %, 4 days per phase, no time limit | 5 % of initial from the balance at midnight Prague (22/23 UTC), floating counts | 10 % static | 80 % (90 % with scaling), bi-weekly | standard funded accounts ban opening ±2 min around FOMC 14:00 ET = C3's 18:00 UTC entry in summer, so use **Swing** (1:30); $400k cap per strategy; $2.50/lot/side |
| FTMO 1-Step | €499, no refund | 10 % | 3 % | 10 % trailing on end-of-day balance | 90 % | best day ≤ 50 % of positive days |
| The5ers High Stakes | $491-545 (+$10 for cTrader), 70 % refunded | 10/5 or 8/5 | 5 % of max(balance, equity) at server midnight | 10 % static | 80 %, **$4k cap per payout** | own-code EAs only; visible stop; ±2 min news ban |
| E8 One / E8 Pro | $488 | 9 % / 8 % | 4 % / 2.5 % | 6 % trailing (never resets) / 8 % | 80 % / only 50 % withdrawable | news ban; "whole daily drawdown on one idea" banned |
| Goat Instant | ~$767 | none | 3 % of max(balance, equity) | 6 % trailing | 80 % | closed for good at -2 % floating loss |

**Excluded:**
- FundedNext: no $100k on cTrader, and no bots on cTrader.
- FXIFY and Blue Guardian: no cTrader.
- Alpha Capital: cBots banned.
- Funding Pips: VPS banned, and funded accounts are force-closed overnight.
- Maven: EAs banned.
- Goat 1-/2-Step: VPS banned.
- Seacrest: closed in Feb 2026.

Blue Guardian, Funding Pips and Alpha restrict Vietnam. **Whether FTMO and The5ers accept Vietnamese residents was
not checked** (no web budget was left).

**Credit risk:**
- MyForexFunds was frozen by the CFTC case for more than 2 years; the case was dismissed in 2025.
- True Forex Funds became insolvent in 2024.
- FPFX data: 14 % of buyers pass and ~7 % are ever paid.
- FTMO, Alpha and Blue Guardian say funded accounts are simulated.

**The model:**
- **Sample:** 605 non-holiday gotobi events, 2016-24, 3,607 legs.
- **R and costs:** R against the rebuilt stop, firm commission applied, swaps excluded. Leg R +0.055 (t 8.2); per
  event +0.33 R (sd 1.57).
- **Intraday basket paths** from IC M1: worst -5.6 R, 1 % quantile -4.3 R.
- **Simulation:** 20k block-bootstrap paths of 10 events plus every historical start; evaluation up to 3 years,
  then 12 funded months.
- **EV** = E[payouts + refund] - fee.
- **The guard:**
  - risk per leg ≤ daily limit / 3.75;
  - skip the short legs when the day's room is < 3.75 × risk;
  - size down near the max-loss floor;
  - "kill" closes everything 0.5 % before either limit.

Code: [P_sim.py.txt](round9_capital_100k/P_sim.py.txt), [P_plans.py.txt](round9_capital_100k/P_plans.py.txt);
all cells: [P_summary.txt](round9_capital_100k/P_summary.txt).

**Results at each plan's EV-best policy (bootstrap):**

| plan | policy, risk / leg | P(phase 1) / P(all) | median / p90 days | E payouts, year 1 | EV (× fee) | half edge: P(all), EV | no edge: P(all), EV |
|---|---|---|---|---|---|---|---|
| The5ers HS 10/5 | guard + kill, ~1.33 % | 0.98 / 0.96 | 207 / 531 | $17.9k | $17.7k (35×) | 0.68, $7.1k | 0.25, $0.9k |
| FTMO 2-Step | guard, ~1.33 % | 0.98 / 0.96 | 211 / 566 | $17.9k | $17.9k (28×) | 0.66, $6.9k | 0.25, $0.9k |
| **FTMO 2-Step (recommended)** | **guard, 1.0 %** | **0.99 / 0.97** | **238 / 556** | **$16.4k** | **$16.3k (26×)** | **0.72, $7.0k** | **0.23, $0.6k** |
| FTMO 1-Step | kill, ~1.33 % | 0.95 | 156 / 481 | $16.3k | $15.7k (27×) | 0.73, $6.8k | 0.35, $1.3k |
| E8 One | guard, 1.25 % | 0.94 | 200 / 623 | $5.8k | $5.4k (11×) | 0.59, $1.2k | 0.18, -$0.3k |
| Goat Instant | none, 0.5 % | – | – | $5.1k | $4.3k (6×) | $2.0k | $0.3k |

- **The guard matters more than the size.** On FTMO 2-Step without it:

  | risk / leg | P(all) | of which daily-loss breaches |
  |---|---|---|
  | 0.75 % | 0.96 | 0 % |
  | 1 % | 0.74 | 20 % |
  | 1.5 % | 0.48 | 48 % |
  | 2 % | 0.34 | 66 % |

  At ≥ 1.5 % per leg, daily-loss breaches are 92-98 % of all breaches.
- **Sensitivity** (FTMO, ~1.33 %): +0.3 / +0.5 pip spread per side gives EV $13.8k / $11.0k; commission at $8
  round trip gives $15.5k.
- **The no-edge EV > 0 ($0.6-1.4k)** is the option-like payoff: unlimited time, a refund, the loss capped at the
  fee. It depends on the firm paying.
- **FTMO 2-Step at 1 % is recommended over the EV-best The5ers because of credit risk.** FTMO publishes financials
  and owns OANDA. 1 % per leg (3 % per event) also stays clear of the "one-sided bet" clauses.

**P-C. GotobiBot at a firm (the cBot was not edited; changes needed):**
1. **Risk and lot cap:** `RiskPerTradeMoney` $1,000, and `MaxLotsPerTrade` 5 → ~15.
2. **A new account-level guard**, shared by the three instances, reading balance and equity. It needs:
   - the firm-day boundary in UTC with DST;
   - the start-of-day reference on the firm's basis;
   - skipping the shorts when room < 3.75 × risk;
   - sizing down near the floor;
   - a kill switch 0.5 % before either limit.
3. **News windows:** move the long entry off FOMC / Minutes days in US summer, or rely on the Swing account.
4. **Camouflage:** decoys off, since the firm sees everything. Keep a visible broker stop (The5ers requires it).
5. **Housekeeping:**
   - SkipDates gains 25 Dec. The cTrader CSV's 25-Dec legs (2018-20) have absurd spreads and were dropped.
   - Run one copy per firm. FTMO caps $400k per strategy, and copies at one firm are perfectly correlated.

## What this says

- **Capital is not the constraint, so $100k does not change round 8's conclusion.** IC's cost structure still binds
  every new idea on IC. The one premium the venue change opened, short index volatility, has paid no alpha over
  beta since 2015.
- **What $100k does change** is how C3 is sized and where it runs. C3 scales without capacity trouble up to ~1-1.5 %
  per leg. The choice left is the DD tolerance: the risk-per-leg table above. At a prop firm, C3's edge shows up
  mostly as a high pass probability, and that is worth much more than the fee if the firm pays.
- **Own capital and a prop account are the same bet.** Running C3 on both doubles the exposure to the same gotobi
  days.

## Process and disclosures

- **HOLD.** Every new series was cut at < 2025-01-01 on load. That covers CBOE, Yahoo, CFTC, BIS, the US Treasury,
  EIA and IC M1; the saved files end on 2024-12-31 (checked).
  - C3's own trade CSV was used in full (2016-26) by streams I and P, as the brief allowed: C3 passed its holdout,
    and this is sizing / rule modelling.
- **HOLD-era levels seen** (prices, no returns):
  1. When the lead probed the CBOE download URLs, the last row of PUT and VIX printed (2026-10-02 levels).
  2. Stream O's 2026-10-05 option-chain snapshot showed current index levels. It was deleted after the
     half-spread ratios were extracted.
- **Unreachable sources.**
  - In stream I: FRED, Yahoo and IC's site (substituted as above).
  - In stream O: FRED and www.cboe.com. The T-bill rate is Yahoo ^IRX, and IBKR commissions are from memory.
  - ftmo.com, the5ers.com and fxify.com resolve to 127.0.0.1 on this Mac.
  - The session's 200 web searches were used up, so FTMO/The5ers eligibility for Vietnam is unchecked.
- **Cost model.** The cTrader CSV applies 2026 swaps to every year (+0.007 R per leg). Lot rounding at $50
  understates |R| by ~4 %. The brief's "$36k notional per $50 leg" was wrong; per leg it is $9-13k.
- **Code.** The screens are scratch scripts in the session scratchpad, as in rounds 3-8. Kept here: the briefs, the
  three hypothesis files, the prop simulator (`P_*.py.txt`), its summary, and C3's at-size tables. Nothing in
  `research/` code was edited.
- **Cells.** About 237 cells in I-B. In O: ~52 strategy cells, plus 99 calibration and 72 cost cells. In P: 1,568
  grid cells, 110 sensitivity cells and ~300 exploratory runs; no edge was searched in P.
