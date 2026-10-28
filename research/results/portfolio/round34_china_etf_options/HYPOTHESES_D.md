# Round 34, stream D: hypotheses (Deribit option flows -> BTCUSD / ETHUSD at IC, 4 hours to 5 days)

Written 2026-10-27 20:33-20:50 UTC (`date -u` 20:33:18 at the start), **before any return was computed and before any
option series was joined to a price**. Loaded so far: Deribit probe pages (single days 2017-01-02, 2018-06-13,
2019-01-01, 2020-06-17, 2021-05-19, 2022-06-15, 2023-06-14, 2024-06-12; trade counts and fields only) and the first
months of the BTC option trade pull (2017-06..2019-02, running). No IC price has been loaded in this stream yet.

## Source and the bar it can meet
- **Deribit public trade history**: `history.deribit.com/api/v2/public/get_last_trades_by_currency_and_time`
  (currency, kind=option, start / end timestamps, count up to 10,000, sorting asc), no key, no account. No robots.txt
  on history.deribit.com or www.deribit.com (both 404). Every request ends at `end_timestamp` <= 1735689599999
  (before 2025-01-01): **HOLD is never requested**.
- Fields per trade: timestamp (ms), instrument (expiry, strike, call / put), price (in BTC per 1 BTC underlying), amount
  (BTC), **direction = the taker's side** (buy / sell), iv (the trade's implied vol, %), index_price, mark_price,
  block_trade_id (block trades, present from ~2019-20), combo ids (later years).
- Real-time: each trade, its iv and index are public on the tape when it prints; the history endpoint is the same
  tape, not restated. A signal at time t uses trades with timestamp < t only.
- Volume by era (probe days, BTC): 2017 ~100-200 trades a day, 2018 ~600, 2020 ~1,700, 2022-24 ~11,000-26,000. The
  2017-18 signals are built from a few hundred trades a day, so they are noisy; that is the honest IS.
- **Pull plan**: BTC options in full, 2017-06..2024-12 (about 2,000 pages of 10,000 trades at >= 1.1 s between
  requests, one job on the host; raw pages parsed then overwritten, compact monthly npz kept). **ETH options are not
  pulled at first**: ETH's IC spread in 2018-20 (89-254 bp median) makes every ETH IS net negative (rounds 31 C, 33 K),
  so ETH can only be information; if time remains I pull ETH 2022-24 for a VAL-only information check.
- Eras: IC BTCUSD exists from 2017-08-28. **IS 2017-09..2021-12 (4.3 years), VAL 2022-24.** No PRE (Deribit starts
  2016 and IC 2017). The bar stays as written: LIVE needs IS net t >= 2.5 on these 4.3 years, VAL >= 1.5, >= 2/3
  years positive, >= 95 % random, power >= 3; DEMO IS t >= 2.0, VAL net > 0, >= 90 % random. Family B (blocks)
  starts when block trades appear (~2019-20), so its IS is at most ~2 years: DEMO at most in practice.

## Prices, costs, timing (all rules): round 31 C's engine, copied
- IC M1 BTCUSD (research.m1.load), cut ts < 1735689600000 at load. Entry at the close of the IC bar labelled t
  (= price at t + 1 min), stale <= 10 min else no trade; IC closed weekends until 2024-04: signals while closed are
  skipped; exit at the last IC quote at or before t + hold.
- Cost: half the actual IC spread at each leg, no commission, swap long -5 bp per 17:00 NY rollover (x3 Friday),
  short 0 (sensitivity: short -5). Checks: +1 min on both legs, half spreads x1.5.
- Non-overlapping trades per cell; t clustered by entry day; random control 200 seeds on the rule's clock with the side
  recomputed at the random time from the sign of the signal (no threshold); momentum control (OLS of next-h return on
  the continuous signal with past 1 / 7 / 28-day IC returns), IS and VAL.
- **Publication / timing rule.** Deribit trades are public in real time. Daily signals use trades in
  [D 00:00, D+1 00:00) UTC and enter at D+1 00:00 UTC (fill = IC price at 00:01). 4-hour signals use trades in the
  4-hour bar [t-4h, t) and enter at t (fill at t + 1 min), t on the 00/04/08/12/16/20 UTC grid. Expiry rule K uses
  trades up to 07:00 UTC Friday for its condition and enters at 08:00 UTC as round 12 K4 did.
- z-scores use only past values: trailing 60 daily values (daily) or 360 4-hour values (4 h), excluding the current;
  at least 30 values required.

## Derived quantities (per trade; no returns)
- Time to expiry T = (expiry 08:00 UTC - trade time) in years; forward ~ index_price (basis ignored); Black-Scholes
  delta with r = 0 and sigma = the trade's iv: call N(d1), put N(d1) - 1. Trades with T < 1 day, missing iv or
  combo legs are dropped from the delta and iv measures (kept in volume counts).
- Signed delta of a trade = dirn x amount x delta (dirn +1 when the taker bought): the BTC exposure that option
  buyers / sellers took. **Net delta demand** NDD over a window = sum(signed delta) / sum(amount x |delta|), in [-1, 1].
  Positive = takers bought calls and / or sold puts = bullish demand (Easley, O'Hara & Srinivas 1998 "positive"
  volume).
- **Buyer-initiated put share** PBS = put contracts bought by takers / (put + call contracts bought by takers), the
  public analogue of Pan & Poteshman's (2006) open-buy put-call ratio (opens are not observable here).
- **Risk reversal** RR = volume-weighted iv of calls with delta 0.15-0.35 minus that of puts with delta -0.35..-0.15,
  expiries 7-60 days, over the window; needs >= 3 trades on each side, else missing.
- **ATM iv** = volume-weighted iv of options with |delta| 0.40-0.60, expiries 7-45 days. **VRP** = ATM iv minus the
  realised vol of the last 7 days from the trades' index_price (hourly last index of each hour, annualised with 365
  days), both in vol points.
- **Block NDD**: NDD restricted to block trades (`block_trade_id` present), daily; in BTC delta units (sum of signed
  delta, not normalised) z-scored.

## Power arithmetic (before building; per-trade net Sharpe x sqrt(HOLD trades) >= 3, HOLD = 1.73 years)
BTC unconditional IC return sd (round 31 C, IS 2018-21 / VAL 2022-24): 4 h 191 / 95 bp, 1 d 454 / 297, 3 d 697 / 474,
5 d 861 / 652; round 12 K4's Friday 08:01-09:00 trade sd 127 / 45 bp.

| rule shape | trades / yr | HOLD n | Sharpe needed | net edge needed at VAL sd | at IS sd |
|---|---|---|---|---|---|
| daily z > 1, 1 d (~30 % of days, both tails) | ~75 | 130 | 0.26 | 78 bp | 120 bp |
| daily z > 1.5, 3 d non-overlapping | ~30 | 52 | 0.42 | 200 bp | 290 bp |
| daily z > 2, 1 d | ~15 | 26 | 0.59 | 175 bp | 270 bp |
| daily z > 2, 5 d | ~12 | 21 | 0.66 | 430 bp | 570 bp |
| 4-h z > 2, 4 h | ~50 | 87 | 0.32 | 30 bp | 61 bp |
| K: Friday expiry fade on the high-volume half, 1 h | ~26 | 45 | 0.45 | 20 bp | 57 bp |

What the sources imply:
- Pan & Poteshman (2006, RFS): the **open-buy** put-call ratio (non-public CBOE data by investor class) separates the
  next-day returns of stocks by ~40 bp a day (lowest vs highest quintile), ~1 % over a week; they show that the
  public version (all volume, not signed / opened) is much weaker, and the effect is a cross-section of single stocks,
  not one asset's time series. 40 bp is 0.09 sd of BTC's daily return: far below the 0.26-0.66 sd a LIVE needs here.
- Easley, O'Hara & Srinivas (1998, JF): signed "positive" / "negative" option volume leads stock prices, at intraday
  horizons.
- Alexander, Deng, Feng & Wan (2022, J. Financial Markets, doi 10.1016/j.finmar.2022.100764; Deribit tick data):
  ATM prices are driven by volatility traders, **OTM prices also by directional traders with information about the
  direction of future BTC moves**, strongest in the 2021 bubble; market makers manage imbalance better as volume
  grows (i.e. the price pressure decays with time).
- Xing, Zhang & Zhao (2010, JFQA): a steep put smirk (OTM put iv over ATM call iv) predicts lower stock returns
  (weekly, ~10 bp a week in the cross-section).
- Bollerslev, Tauchen & Zhou (2009, RFS): a high variance risk premium predicts higher index returns at
  quarterly horizons; at 1-5 days its slope is small.
- Wei, Koutmos & Zhu (2024, FRL 105739) ask whether Deribit option trading leads or lags attention; the result is not
  in the free abstract, so it is not used for a side.
- Round 12 K4 (Weiss et al. 2024 / 2026): BTC reverses after the Friday 08:00 Deribit expiry, strongest with high ATM
  open interest; IS gross +20.6 bp (t 2.34), net +9.0 (t 1.03) at 2018-21 costs.
So LIVE needs an effect 2.5-7x the literature's sizes; **the realistic target is DEMO** (or the K condition doubling
K4's edge). The test is run anyway because Deribit flow is a measured, real-time, chosen flow nobody here loaded.

## Hypotheses (side fixed by the mechanism / literature; thresholds and holds chosen on IS only from these grids)
Registered side for every flow family = **the informed-trader reading** (follow option demand): Easley-O'Hara-Srinivas,
Pan-Poteshman and Alexander et al. all find the direction of option demand leads the underlying, and dealer delta
hedging of net customer demand pushes spot the same way. The contrarian "sentiment" reading is reported only as
information and can never be registered from this file.

### F1 net delta demand (NDD), follow. 13 cells
- Daily: z(NDD over UTC day D) vs trailing 60 days; z > k -> long, z < -k -> short at D+1 00:00 UTC; k in {1.0, 1.5,
  2.0} x hold {1, 3, 5} days = 9 cells.
- 4 h: z(NDD over the 4-h bar) vs trailing 360 bars; k in {1.5, 2.0} x hold {4 h, 1 d} = 4 cells.

### F2 buyer-initiated put share (PBS), Pan-Poteshman side. 9 cells
- Daily z(PBS) vs trailing 60 days: z > k (puts bought) -> short; z < -k (calls bought) -> long. k {1.0, 1.5, 2.0} x
  hold {1, 3, 5} days.

### F3 risk reversal (RR), follow the skew. 9 cells
- Daily z(RR over day D) vs trailing 60 days: z > k (calls rich vs puts) -> long; z < -k (put smirk steepens) ->
  short (Xing-Zhang-Zhao side). k {1.0, 1.5, 2.0} x hold {1, 3, 5} days.

### F4 variance risk premium (ATM iv - realised 7-day vol), Bollerslev-Tauchen-Zhou side. 6 cells
- Daily z(VRP at D+1 00:00, ATM iv from day D's trades) vs trailing 60 days: z > k -> long, z < -k -> short. k {1.0,
  1.5} x hold {1, 3, 5} days.

### F5 block-trade delta, follow (block trades are where large / institutional option orders print). 4 cells
- Daily z(sum of signed block delta over day D) vs trailing 60 days (days without blocks = 0; the rule starts when
  >= 30 of the trailing 60 days have a block): z > k -> long, z < -k -> short. k {1.5, 2.0} x hold {1, 3} days.

### K expiry fade conditioned on expiring volume (round 12 K4 + the paper's own condition). 4 cells
- Round 12 K4 rule, unchanged: Fridays, m = ln P(08:00) - ln P(07:00) UTC (IC mid), enter 08:00 (+1 min) with side
  -sign(m), exit 09:00 UTC.
- Condition (proxy for the paper's high ATM open interest, which the free API does not give): EXV = BTC amount traded
  in the options **expiring that Friday** with strike within +-5 % of the index at the trade, over the 7 days before
  Friday 07:00 UTC. A Friday qualifies when EXV is above the median (cells 1-2) or the top tercile (cells 3-4) of the
  trailing 26 Fridays' EXV; cells x {all Fridays with expiry, last Friday of the month only}. 4 cells. The
  complement (low EXV) is reported as the mechanism check: it should be weaker.

**Total: 45 BTC cells** (13 + 9 + 9 + 6 + 4 + 4). Chance benchmark: expected max |t| of 45 independent normal cells
~2.5 (95 % ~3.2); families are correlated (F1 and F2 overlap), so the effective count is lower. ETH (if pulled) is
VAL-only information, not counted.

### Mechanism checks reported next to the cells (not selectable)
- Contrarian sides of F1-F3 (= the sign flip of the same cells): information.
- F1 split by moneyness (OTM |delta| < 0.35 vs the rest): Alexander et al. say the directional information is in OTM
  options; if F1 works, OTM-only should be at least as strong.
- Era split 2017-19 vs 2020-21 inside IS (volume grew 10x): the literature says pressure decays as market making
  deepens.

## Round 2: reconstructed dealer gamma (declared 2026-10-27 21:03-21:12 UTC, `date -u` 21:03:36)
State when written: the IS (2017-09..2021) numbers of the 45 round-1 cells (and the information checks) have been
computed and seen; **no VAL number has been seen** (the 2022-24 pull is still running) and **no gamma series has been
computed**. Round-1 IS outcome that motivates this: no cell reaches IS net t 2.0 (best +1.49, F3 RR k1.5 5 d); the
K expiry fade reproduces round 12 K4 (IS gross +21.3, t 2.48; net +8.9, t 1.05), and the expiring-volume condition does
not raise it. These round-2 cells are new variables, not re-cuts of round-1 cells, but they are a second round: their
chance benchmark is counted with round 1 (45 + 10 = 55 cells).

Mechanism (Barbon & Buraschi 2021 "Gamma fragility"; Baltussen, Da, Lammers & Martens 2021 JFE; Ni, Pearson,
Poteshman & White 2021 RFS): when option dealers are net **short gamma**, delta hedging buys rises and sells falls, so
moves continue (intraday momentum); when dealers are **long gamma**, hedging leans against moves, so moves revert.
Round 12's Deribit expiry papers (Weiss et al.) report the Friday reversal is strongest with **negative gamma**
(stated in round 12 HYPOTHESES_K, K4). Round 12 / round 16 list "Deribit OI / gamma history" as paid data. The free
tape lets it be reconstructed:
- Dealer position per instrument = minus the cumulative taker-signed amount since the pull start (2017-06-01): takers
  are customers, makers are dealers (Alexander et al.'s net-buying-pressure convention). Instruments listed before
  2017-06 miss their earlier trades (they expire by 2018); G cells start 2018-01-01.
- Dealer dollar gamma GEX(t) = sum over unexpired instruments of dealer position x BS gamma x S^2 x 1 % (USD per 1 %
  move), S = last index price before t, sigma = the instrument's last traded iv before t, r = 0, T to the 08:00 UTC
  expiry; instruments with T < 1 hour excluded. Computed at every 4-hour bar end and at Friday 07:00 UTC from trades
  before that time only.
- Sign is the variable (mechanism); no threshold on GEX.

Cells (BTC; IC fills, costs and controls as round 1):
- **G1 4-h move continuation / reversal by gamma sign.** At each 4-h bar end t: r = IC mid log return over [t-4h, t);
  zr = r / sd of the trailing 360 4-h returns. If |zr| > k: side = sign(r) when GEX(t) < 0 (follow), -sign(r) when
  GEX(t) > 0 (fade). k in {1.0, 2.0} x hold {4 h, 1 d} = 4 cells.
- **G2 the same, one regime at a time**: G2a only GEX < 0 (follow), G2b only GEX > 0 (fade); k in {1.0, 2.0}, hold
  4 h = 4 cells.
- **G3 round 12 K4 on Fridays with GEX(Friday 07:00 UTC) < 0** (the paper's condition), fade 08:01-09:00: all
  Fridays with an 08:00 expiry, and last Fridays of the month = 2 cells. Mechanism check: GEX > 0 Fridays.
- Random control G1 / G2: random 4-h bar ends with the side recomputed by the same rule (sign of r and of GEX at the
  random time, no |zr| threshold). G3: random expiry Fridays, K4 side recomputed.
- Information (not a cell): the share of time GEX < 0 per year, and its correlation with the round-1 NDD.
Total round 2: 10 cells; total stream 55.
