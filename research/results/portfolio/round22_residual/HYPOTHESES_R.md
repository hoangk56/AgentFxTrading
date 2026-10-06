# Round 22, stream R: declared hypotheses

Written 2026-10-06 05:26 UTC (`date -u`), before any round-22 return was computed (the only number computed before
this file is a code check that rebuilds the published E1 cell: IS net +1.17 t 3.29, VAL +1.35 t 2.46, identical to
round 13). Triage and reasons in TRIAGE_R.md. HOLD (2025-01-01 onwards) is never loaded: the panel ends 2024-12-31,
Dukascopy ends 2015-12-31, every event list is cut at 2024-12-31 and asserted.

## Common protocol
- Eras: PRE 2004-15 (where data exists), IS 2016-21, VAL 2022-24. Each event belongs to the era of its entry date.
- Prices: IC panel mid (2016-24); Dukascopy bid M1 (EURUSD, USDJPY, USDCHF, EURJPY, GBPJPY) or H1 (other pairs)
  for PRE. Quotes may be up to 10 minutes stale (round 13 M's grids); otherwise the event is dropped.
- Costs: half the actual spread at the entry minute + half at the exit minute (PRE: IC 2016-17 mean spread by New
  York minute of day); + 0.6 bp commission for FX; 0 for indices. Swap: FX via `research/swing/rates.py`
  `swap_frac_at` (2016-24) and round 20 F's BIS-rate model (PRE) for each 17:00 New York rollover held (Wednesday x3);
  indices -2 bp per calendar night long.
- Robustness: spread x1.5; +1 minute on both fills (PRE H1 cells cannot shift, reported as n/a).
- t: clustered by UTC date unless stated; per era and per year.
- Random-entry control, 300 seeds, look-ahead free (data-dependent sides recomputed at the random time).
- Power: per-trade net Sharpe x sqrt(1.73 x trades/yr), on the IS and the VAL size; expected HOLD t = the VAL power.
- Chance benchmark: the 13 counted cells below; max of 13 |normal| (p95) and a sign-flip null (one random sign per
  UTC date shared by all counted cells), per era.
- C3 daily / monthly P&L correlation (IS + VAL) for any cell that meets DEMO numbers.
- Bars as in round 13's brief (LIVE / DEMO). Families R3 and R4 are **information only whatever they show** (their
  IS/VAL relatives were seen in rounds 3-4 and fail DEMO's IS t); their test is the unseen PRE era.

## R1. Equity premium in even weeks of the FOMC cycle (Cieslak, Morse & Vissing-Jorgensen 2019, JF 74(5))
- Mechanism (paper): since 1994 the US equity premium is earned entirely in weeks 0, 2, 4 and 6 of FOMC cycle time,
  tied to the Board's biweekly meetings and informal Fed communication. Side: long in even weeks (paper). Literature
  prior on decay after publication: unknown; the round-18 rule expects ~0.65 of a declared size.
- Calendar: scheduled FOMC decision days from the shared `cb_calendar.json` (bank FOMC, kind decision,
  scheduled = true; 2015-2024). Trading days: NYSE sessions (python `holidays` NYSE calendar). For each NYSE day t,
  the governing meeting is the latest scheduled decision day d0 with t >= (NYSE day before d0); j = NYSE-day index of
  t minus that of d0 (j >= -1); week w = floor((j + 1) / 5); even = w even. (Paper: week 0 = days -1..3.)
- Trade for day t: long from 16:00 ET on the previous NYSE day to 16:00 ET on day t (panel boundary minutes).
- Counted cells: **A1 US500 even-week days (primary)**; A2 US30 even-week days; A3 USTEC even-week days; A4 US500
  even minus odd (difference of mean net per day; t from a date-clustered regression on an even dummy).
- Placebo (not counted): A5 US500 odd-week days long (predicted mid <= 0 under the paper).
- Clustering: by cycle-week block (meeting x week); per-date t also reported.
- Random-entry control: for each event a random NYSE day of the same weekday in the same era, long, same hold;
  300 seeds.
- Expected: unconditional US500 2016-24 ~+5 bp/day; the paper implies even days ~2x that, odd ~0; daily sd ~110 bp;
  ~125 even days a year; full-size power ~1.3 (DEMO tier at most).

## R2. Next-day FX reversal after abnormally low volume (Cespa, Gargano, Riddiough & Sarno 2022, RFS 35(5))
- Mechanism (paper): volume reveals asymmetric information; "predictability implies a stronger return reversal for
  currency pairs with abnormally low volume", driven by the part of volume unrelated to volatility. Side: against the
  day's return, on low abnormal-volume days (paper).
- Pairs: EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCAD, USDCHF, USDJPY. Day d: 16:00 London (WM/R time) on the previous
  weekday to 16:00 London on d; weekdays only, 24 Dec-1 Jan excluded. r_d = log P(16:00 London d) / P(16:00 London
  previous weekday). P: panel mid (IS/VAL), Dukascopy H1 bid close of the bar ending 16:00 London (PRE).
- Volume V_d: IS/VAL = sum of IC tick counts (panel `n`) over the window; PRE = sum of Dukascopy H1 `vb + va` over
  the window (different proxies by era; disclosed). RV_d = sum of squared hourly log returns over the window (all
  eras). AV_d = log V_d - mean(log V, previous 20 weekdays of the pair); ARV_d likewise for log RV.
- Orthogonal abnormal volume AVo_d = AV_d - b ARV_d, b = OLS slope of AV on ARV over the previous 250 weekdays
  (>= 120 valid). Low tercile: AVo_d <= 33.3rd percentile of AVo over the previous 250 weekdays (causal); high
  tercile: >= 66.7th.
- Trade: side = -sign(r_d) in pair terms; IS/VAL entry 16:01 London on d (fill one minute after the signal), exit
  16:00 London on the next weekday; PRE entry and exit at the H1 boundaries 16:00 London. One rollover (Wed x3,
  Friday trades over the weekend: 1 swap charge Fri->Mon as rates.py counts it).
- Counted cells: **B1 low-AVo tercile, 7 pairs pooled (primary)**; B2 low raw-AV tercile, pooled; B5 B1 minus the
  high-AVo tercile (difference, date-clustered regression).
- Reported, not counted: B3 all days (unconditional reversal baseline); B4 high-AVo tercile.
- Random-entry control for B1: for each event a random weekday of the same pair, same weekday, same era, side
  recomputed at that day (-sign of that day's r); 300 seeds. +1 minute: entry 16:02, exit 16:01 (IS/VAL).
- Warm-up: first 270 weekdays of each data source (PRE events from ~2005-02, IS events from ~2017-01; IS uses the
  panel from 2016-01 for warm-up, so IS events start ~2017-01).
- Expected: ~1/3 of 7 x 250 pair-days; daily sd ~50 bp; paper-size ~2-4 bp vs ~1.3-1.6 bp cost; power ~1-1.5.

## R3. High-yielder bought into the Wednesday triple rollover (round 3 W1, "into" variant) - information only
- Mechanism: carry seekers buy the high-yielding currency before 17:00 New York on Wednesday, when three nights of
  swap are credited, and sell after (round 3 measured the fall after: -3.0 bp t -4.2). Side: long the high-yielder.
- Pairs: EURUSD, USDJPY, USDCHF, EURJPY, GBPJPY (Dukascopy M1 in PRE, panel 2016-24). Rates: round 20 F's causal
  `rank_rates` (BIS before 2016, FRED after; last value before the 1st of the entry month). Trade a pair only if
  |rate difference| >= 0.25 pp; long the higher-rate currency.
- Window: 12:00 -> 16:55 New York. Days dropped when the Wednesday, Thursday or Friday is a holiday of USD or of
  either currency of the pair (the triple day moves), and 24 Dec-1 Jan.
- Counted: **C1 Wednesdays, pooled pairs**; C3 Wednesday minus Mon/Tue/Thu (difference). Reported: C2 Mon/Tue/Thu
  same window (placebo, predicted ~0).
- Random-entry control for C1: random 295-minute windows starting 08:00-12:00 New York on the same Wednesdays, same
  side rule; 300 seeds.

## R4. Treasury-auction concession seen in the dollar (Lou, Yan & Zhang 2013, RFS 26(12)) - information only
- Mechanism: dealers absorb new supply, so Treasury yields rise before auctions and fall after; USD follows US
  yields intraday-to-days. Side: USD up into the auction, down after.
- Events: 10-year note auctions (new issues and reopenings: security type Note, original term 10 years; terms
  "10-Year" or "9-Year xx-Month") from fiscaldata.treasury.gov `auctions_query`, 2004-2024; result at 13:00 ET.
- Cells (counted): **D1 USDJPY long 16:00 ET on the 3rd New York business day before the auction -> 13:00 ET on the
  auction day**; D2 USDJPY short 13:01 ET auction day -> 16:00 ET on the 2nd business day after; D3 EURUSD short over
  D1's window; D4 D1 + D3 pooled (date-clustered).
- Random-entry control: the same windows anchored on random non-auction weekdays with the auction's weekday, same
  era; 300 seeds.

## Cell count
13 counted cells (A1-A4, B1, B2, B5, C1, C3, D1-D4); placebos/baselines A5, B3, B4, C2 reported but not counted.
No other cell or variant will be computed in this round; anything else looked at is reported as post hoc.
