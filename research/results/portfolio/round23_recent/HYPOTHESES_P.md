# Round 23, stream P: practitioner / structural-flow hypotheses, declared before any number

Written 2026-10-15 11:06 UTC (`date -u`), before any round-23 return, mean or count from the panel was computed by
this stream. Brief: [BRIEF.md](BRIEF.md) row P and round13_structural/BRIEF.md (data, costs, bars, pitfalls).
HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31 and Dukascopy H1 is cut at 2016-01-01
at load for the PRE era.

## Step 1: source map (what circulated 2023-2026, and what it would take)

"Side rule" = how the side is computed from public data before the trade. "Power" = expected per-trade net Sharpe x
sqrt(1.73 x events/yr), a priori, from the source's size where one exists (otherwise my guess, marked "g").

| # | flow | source (cited) | side rule from public data | flow size / history | earliest date | events/yr | expected size vs IC cost | a-priori power | status |
|---|---|---|---|---|---|---|---|---|---|
| S1 | volatility-control / risk-control funds de-lever after a volatility jump, re-lever when vol falls | S&P DJI Risk Control index family (exposure = target vol / realized vol, EWMA decay 0.94 short / 0.97 long, max of the two, up to 150 % leverage, daily rebalance; S&P DJI methodology and the SEC FWP of the S&P 500 Risk Control 10 % index, sec.gov/Archives/edgar/data/19617/000095010314000961); Barclays 2018 ("$225bn of sales in the coming days", ~$500bn tied to vol targeting, Gulf News/Bloomberg 2018-02-07); Nomura (McElligott) vol-control sell-flow notes via SpotGamma (spotgamma.com/?p=1868) | sign of the day's change in the model exposure E = min(0.10/sigma, 1.5); trade the next day in that direction | $200-500bn AUM per bank estimates since ~2015 (structured notes, variable annuities, FIAs) | ~2012 (risk-control VA growth); fully in IS | ~50 gated days | g: 10-20 bp next day vs ~1 bp cost + ~2 bp swap; sd ~150 bp on gated days | ~1.0 | **declared P1** (relative: round 3 tested re-leveraging 20 days after a big day leaves a 21/63-day window; this is the immediate EWMA exposure change and both signs) |
| S2 | pension / balanced-fund threshold rebalancing (and quarter-end) | Harvey, Mazzoleni & Melone, "The Unintended Consequences of Rebalancing", NBER w33554 (2025): 60/40 threshold signal averaged over delta = 0-2.5 % predicts next-day S&P minus 10y returns, -16 bp (equity) per 1 sd, t > 4, 1997-2023; stronger near quarter-end and for large signals | side = -sign(weight deviation of a simulated 60/40 portfolio); trade the next day | US retirement assets $37.8tn (2022), >$20tn in public equity/debt (paper) | significant from early 2000s (paper) | 250 (all days) / ~83 (top tercile) | paper: ~16 bp per sd vs ~1 bp + 2 bp swap; sd ~110 bp | 1.2-1.9 (equity-only proxy, decay-adj. lower) | **declared P2** (relative: round 3/4 tested the paper's CALENDAR month-end part, not the threshold signal) |
| S3 | quarter-end pension rebalancing after a big equity-vs-bond divergence | same paper (quarter-end strengthening); sell-side quarter-end estimates in the press each quarter (JPMorgan / Goldman / Wells Fargo "pension rebalancing" notes) | -sign(QTD equity return) in the last days of a quarter, only when \|QTD\| is large | as S2 | as S2 | ~2-3 | g: 30-50 bp over 4 days vs sd ~250 | ~0.5 | **declared P6** (relative of round 3/4 month-end; differs: quarter-end only, magnitude gate) |
| S4 | CTA trend-signal flips executed over the following days | Goldman Sachs prime-brokerage CTA trigger notes (e.g. "$20bn of selling if the S&P falls below ..."), Nomura QIS CTA model (5 horizons) and BofA trigger levels as reported (Hedgeweek "CTAs sell up $42bn"; SpotGamma); Hurst, Ooi & Pedersen 1/3/12-month lookbacks | sign of the change of S = mean(sign of 21/63/252-day return); trade the next day in that direction | CTA AUM ~$300-400bn, flips estimated at $20-40bn per week per index | 1980s; fully in IS and PRE | ~20 per symbol | g: 5-10 bp vs ~1-3 bp cost; sd ~100 | ~1.4 pooled | **declared P3** (relative: TSMOM / Donchian as level strategies were tested in rounds 2/7/11 and C1; this trades only the day after a flip, side from the CHANGE of the signal) |
| S5 | buyback blackout windows around earnings seasons | Goldman Sachs buyback desk estimates as republished: blackout starts ~4-6 weeks before earnings, ends 1-2 days after; ~40 % of S&P 500 in blackout by mid-December 2024; 98 % on 2026-04-13, reopening ~2026-04-28 (Tickmill republications of GS notes; ETF Trends/ValueWalk "When does buyback blackout end"); GS "$1tn buybacks" (InvestmentNews) | calendar: open window vs peak blackout (fixed day-of-quarter calendar below); buybacks execute intraday under SEC Rule 10b-18 (not the opening trade, not the last 30 min) | ~$0.8-1tn/yr S&P 500 buybacks, ~$4bn/day average, concentrated in open windows | 1982 (Rule 10b-18); grew since 2010 | ~70 open-window days | g: 1-3 bp/day vs ~0.5-1 bp spread; sd ~70 bp | ~0.4 | **declared P4** (new; not in any earlier round) |
| S6 | post-monthly-OPEX "window of weakness" (dealer vanna/charm hedges roll off) | Cem Karsan "window of weakness" (week after monthly OPEX); McElligott (Nomura) "post-OpEx window for movement / down trade window after VIX expiry" (SpotGamma reposts 2020-21: spotgamma.com/1-20-20-nomura-update, spotgamma.com/explaining-opex-drift) | calendar: week after the third Friday short, OPEX week long | SPX options OI multi-trillion notional | ~2017-18 (dealer gamma era) | 12 + 12 | g: 20-40 bp per week vs ~2 bp + swaps; weekly sd ~220 | ~0.6 | **declared P5** (relative: round 10 pinning, round 20 expiry auctions tested the expiry day itself, not the following week) |
| S7 | MOC imbalance at the US close | NYSE/Nasdaq imbalance publications | follow the 15:50 imbalance | - | - | 250 | tested: round 11 (+0.29 bp US30), round 12 J (USTEC +1.5 bp mid, net < 0) | - | **not retested** (same construction) |
| S8 | index rebalance days (S&P quarterly, Russell reconstitution, MSCI) | index provider calendars | side needs constituent-level flows; index level has no known side | - | - | 1-4 | S&P quarterly = quad witching: round 3 ("noise"), round 20 G | - | **not retested**; Russell (US2000, 1/yr) has no power |
| S9 | leveraged / inverse ETF rebalancing, intraday momentum into the close, pinning, month-end WM/R hedge, expiry auctions | many | - | - | - | - | tested rounds 3, 6, 10, 12, 13, 17, 20 | - | **not retested** |
| S10 | spot bitcoin / ether ETF creation flows into the 16:00 ET NAV | issuer flow files (Farside etc.) | prior-day flow sign | ~$35bn net 2024 | **2024-01-11** (BTC), 2024-07-23 (ETH) | 250 | unknown | n/a in IS/VAL (VAL has 2024 only) | **needs the user** (flow exists only from 2024; needs ETF flow data + post-2026-09 data) |
| S11 | Japanese retail (new NISA) monthly accumulation buying foreign assets, yen sold early in the month | press 2024-25 (Nikkei, Bloomberg on toshin outflows) | short JPY around the first business days | ~JPY 1tn+/month from 2024 | **2024-01** (small tsumitate NISA since 2018) | 12 | unknown | n/a | **needs the user** (earliest testable 2024-01; HOLD era) |
| S12 | SPX 0DTE dealer hedging | CBOE daily expiries | - | - | **2022-05** (Tue/Thu expiries) | 250 | K3 found nothing | - | tested (round 12 K3) / needs the user for OI data |
| S13 | US Treasury buybacks | Treasury buyback schedule | - | - | **2024-05** | ~50 | unknown | n/a | **needs the user** (HOLD era; bonds not at IC) |
| S14 | Japanese life insurers' semiannual hedging plans, GPIF rebalancing | press each April/October (Reuters lifers' plans); GPIF policy portfolio 25 % +- bands | side comes from plan contents published after the fact / undisclosed rebalancing dates | large | n/a | 2 | - | - | **not testable** as a pre-computable side (untested ideas) |
| S15 | central-bank gold buying | WGC; PBoC monthly reserve release (7th) | side known only after the release | - | - | 12 | - | - | **not testable** (no ex-ante side) |
| S16 | risk-parity de-leveraging (stock-bond vol and correlation) | sell-side notes 2022-24 | needs bond returns | - | - | - | - | - | **needs the user** (10-year yield / bond futures data are price data); the equity-vol part is P1 |

## Step 2: common definitions (all cells)

- Data: shared panel `r23/shared/panel` (mid, spr, n; bar-START labels; HOLD absent). The price "at clock T" is the
  close of the bar labelled T - 1 min. If that bar is NaN, the last available close within the previous 10 minutes;
  else the day is skipped for that symbol.
- Exchange clocks (DST-aware): US cash close 16:00 New York; Xetra 17:30 Frankfurt; LSE 16:30 London; TSE 15:00
  Tokyo (15:30 from 2024-11-05); FX / gold "daily close" 15:00 London.
- US trading days: NYSE calendar built from rules (New Year, MLK, Presidents, Good Friday, Memorial, Juneteenth from
  2022, Independence, Labor, Thanksgiving, Christmas, with Sat->Fri / Sun->Mon observance; 2018-12-05 closure).
  Early closes (13:00): 2016-11-25, 2017-07-03, 2017-11-24, 2018-07-03, 2018-11-23, 2018-12-24, 2019-07-03,
  2019-11-29, 2019-12-24, 2020-11-27, 2020-12-24, 2021-11-26, 2022-11-25, 2023-07-03, 2023-11-24, 2024-07-03,
  2024-11-29, 2024-12-24: the "close" clock becomes 13:00. Other markets: a day is a trading day for a symbol if it
  is Mon-Fri and the panel has >= 30 bars with ticks in that market's cash session.
- "Close-to-close next day" trade (P1, P2, P3, P6 windows): signal from prices at close - 5 min (the "signal
  close", e.g. 15:55 NY) of day t and earlier; entry at close - 4 min of day t (fill one minute after the signal);
  exit at the close clock of the next trading day t+1 (e.g. 16:00 NY = close of bar 15:59). Latency check: entry
  and exit both +1 minute. Spread x1.5 check on both legs.
- Costs: half spread at entry minute + half at exit minute from the panel (actual, not medians); commission 0.6 bp
  round trip for FX and metals, 0 for indices; swap per rollover crossed (17:00 NY) from research/swing/rates.py
  `swap_frac_at(symbol, side, entry_ms)`, x3 on Wednesday for FX/metals and x3 on Friday for indices.
- Eras: IS 2016-01..2021-12, VAL 2022-01..2024-12; PRE 2004-2015 only for P3's FX/gold (Dukascopy H1, bid, 15:00
  London closes = close of the H1 bar starting 14:00 London; cost convention: IC 2016-17 median round-trip spread at
  15:00 London + 0.6 bp; swaps ignored in PRE and said so).
- Statistics: mean bp per trade, t clustered by entry trading date (pooled cells: trades on the same date summed into
  one cluster); by year; VAL/IS ratio; ex-March/April 2020 row for every equity cell; per-trade net Sharpe and
  power = Sharpe x sqrt(1.73 x trades/yr) at the IS and at the VAL size.
- Random-entry control (200 seeds): same count, same era, same hold rule and clocks, entry days drawn from the
  eligible days that are NOT events; side recomputed at the random day by the cell's own side rule where the rule
  defines a side every day (P1, P2, P6); for flip and calendar cells (P3, P4, P5) side mix kept (P3 also run with
  side = sign of the CTA level S on the random day). Report the percentile of the cell's net mean.
- Chance benchmark: max \|t\| of K independent normals for the stream's primary-cell count K, plus a per-family
  permutation null that flips the sign of each trading date's pooled P&L (shared across the family's cells).
- Burn-in: signals use only data from 2016-01-04 onwards (no PRE index data); trades start 2016-04-01 for P1/P2/P6,
  2017-01-03 for P3's indices (252-day lookback); FX/gold in P3 seed lookbacks from Dukascopy 2015 bid closes.

## Step 3: declared cells

### P1 vol-control exposure change (S1), 4 primary + 1 replication = 5 cells
- Daily US500 signal closes c_t (15:55 NY). r_t = ln(c_t / c_{t-1}). EWMA variances v_s = 0.94 v_s + 0.06 r^2,
  v_l = 0.97 v_l + 0.03 r^2 (seeded with the mean r^2 of the first 20 days), sigma_t = sqrt(252 max(v_s, v_l)).
  E_t = min(0.10 / sigma_t, 1.5). f_t = E_t - E_{t-1}.
- Side for the trade after day t: sign(f_t) (sell when the model exposure fell).
- Gate: "all" = every day with f_t != 0; "top" = \|f_t\| >= the 80th percentile of \|f\| over all PRIOR days since
  2016-01-04 (min 60 prior days).
- Windows: "cc" = close-to-close next day (Step 2); "lh" = last hour of day t+1 (side known since day t): entry at
  15:00 NY of t+1 (bar 14:59 close), exit 16:00 NY (bar 15:59 close), no swap; latency check 15:01 / 16:01.
- Primary cells (US500): P1-top-cc (**the primary**), P1-top-lh, P1-all-cc, P1-all-lh.
- Replication: P1-top-cc pooled on US30 + USTEC with US500's signal (index-wide flow), one cell.

### P2 threshold rebalancing, equity-only proxy (S2), 3 primary + 1 international = 4 cells
- Simulated 60/40 portfolios, equity = US500 signal closes, "bond" leg = 0 return (cash proxy; the paper's 10-year
  note leg needs bond data, a user decision; the equity leg dominates the signal, equity daily sd ~3x the note's).
  For each delta in {0.0, 0.1, ..., 2.5} % (26 portfolios): weight w evolves with the day's equity return; at the
  signal close of day t, record dev_delta = w - 0.60; if \|dev_delta\| > delta (delta = 0: always) reset w = 0.60.
  Signal_t = mean over delta of dev_delta. Start 2016-01-04 with w = 0.60.
- Side for the next day: -sign(Signal_t) (sell equities when they are overweight).
- Cells (US500, window "cc"): P2-all (every day; **the primary**), P2-top (\|Signal_t\| >= 67th percentile of
  \|Signal\| over all prior days, min 60), P2-US-pooled (P2-all on US30 + USTEC with US500's signal).
- International (paper section: extends to international markets): P2-intl = P2-all with each index's own signal on
  DE40, UK100, JP225 (own closes), pooled, one cell.
- Not run: the paper's Calendar x week4 signal (round 3/4 tested month-end versions; not a different construction).

### P3 CTA signal flips (S4), 2 primary cells (pooled) + PRE information
- Universe: US500, DE40, JP225, USDJPY, EURUSD, XAUUSD (staples of CTA books). Daily signal closes at each market's
  clock (FX/gold 14:55 London signal close, entry 14:56, exit 15:00 London next trading day).
- S_t = mean over L in {21, 63, 252} trading days of sign(c_t / c_{t-L} - 1). A flip day: S_t != S_{t-1}.
- Side: sign(S_t - S_{t-1}); window "cc".
- P3-all: every flip day, pooled over the 6 symbols (**the primary**). P3-slow: flips caused by the 63- or 252-day
  horizon only (the 21-day component unchanged), pooled.
- Information: per-symbol rows; PRE 2004-15 for USDJPY, EURUSD, XAUUSD (Dukascopy H1 bid 15:00 London closes,
  entry at that close, exit at the next day's), mid-only and cost-convention net.

### P4 buyback windows (S5), 2 primary cells + 1 replication
- Calendar per quarter (Q-end = last day of Mar/Jun/Sep/Dec), from GS's published timing (blackout 4-6 weeks
  before earnings, end 1-2 days after; peak mid-April, reopening late April; ~40 % by mid-December):
  - OPEN window: NYSE trading days from the 10th of the second month of the quarter to the 5th of the third month,
    inclusive (Feb 10 - Mar 5, May 10 - Jun 5, Aug 10 - Sep 5, Nov 10 - Dec 5).
  - PEAK BLACKOUT: from the 25th of the third month to the 20th of the next month, inclusive (Mar 25 - Apr 20, ...).
- Window: 10:00 -> 15:30 New York on each day (Rule 10b-18 keeps buybacks off the open and the last 30 min);
  entry price at 10:00 (bar 09:59 close), exit at 15:30 (bar 15:29 close); no swap.
- P4-open-long: long US500 on OPEN days (**the primary**). P4-LS: long on OPEN days and short on PEAK BLACKOUT
  days (one cell; the mechanism test is also reported as the OPEN minus BLACKOUT difference with a two-sample t).
- Replication: P4-open-long on US30 + USTEC pooled.

### P5 post-OPEX window of weakness (S6), 2 cells
- Monthly OPEX = third Friday of the month (if an NYSE holiday, the Thursday before).
- P5-after-short: short US500 from 09:35 NY on the first trading day after OPEX to 15:55 NY on the last trading day
  of that calendar week (**the primary**). P5-opexweek-long: long US500 from 09:35 NY on the first trading day of
  the OPEX week to 15:55 NY on OPEX day. Swaps per night held (index rules above).

### P6 quarter-end rebalancing with a big divergence (S3), 1 primary + 1 international
- Q = quarter-end months. QTD_t = US500 signal close of day T-5 (the 5th-last NYSE trading day of the quarter) /
  the last signal close of the previous quarter - 1. Event if \|QTD\| >= 5 % (sell-side flags; equity-only proxy).
- Side: -sign(QTD). Trade: entry at the signal close + 1 min of T-5, exit at the close of T-1 (the second-to-last
  trading day; the paper says funds avoid the very last day), 4 nights.
- P6-US500 (**the primary**); P6-intl: same rule on DE40, UK100, JP225 with own QTD, pooled.

### Cell count
Primary cells for the chance benchmark: P1 4, P2 3, P3 2, P4 2, P5 2, P6 1 = **14**; replication / international
cells (P1 1, P2 1, P4 1, P6 1 = 4) are reported alongside and counted in a second benchmark (K = 18). Per-symbol
rows and PRE are information only.

Verdicts use the round-13 bars unchanged (LIVE / DEMO). A cell found here can become a PREREG_DRAFT only if its
declared primary or declared variant meets the bar; nothing chosen after looking.
