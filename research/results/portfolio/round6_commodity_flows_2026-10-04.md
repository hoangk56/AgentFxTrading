# Round 6: commodity settlement flows, inventory reports, passive execution and index liquidity provision (2026-10-04)

Continuation of rounds 3-5 ([flow_search_2026-09-27.md](flow_search_2026-09-27.md),
[flow_search_round4_2026-09-27.md](flow_search_round4_2026-09-27.md),
[sizing_round5_2026-09-27.md](sizing_round5_2026-09-27.md)). The brief is the one in `research/PROMPT.md`: lots never
depend on capital, a position is held 5 days at most, a bot holds 3 positions at most, a mechanism other than
gotobi / the Tokyo fix and crypto trend, IS 2016-2021 to choose, VAL 2022-2024 to check, HOLD opened once per
pre-registered candidate. Energies start in 2018, so their IS is 2018-2021.

This round looked where the earlier rounds had not: conditional intraday flows in energies and metals (the old lab and
the 552-config bank never had energies), the weekly EIA/API inventory reports, passive (limit-order) execution of a
known liquidity effect, and short-term liquidity provision in the cheapest instruments.

## Answer

**No new candidate. Nothing reached a pre-registration, so HOLD was not opened.**

| # | hypothesis (source) | where | IS | VAL | verdict |
|---|---|---|---|---|---|
| S1 | momentum into the futures settlement: leveraged / inverse ETFs rebalance in the direction of the day's move at the settlement (Cheng & Madhavan 2009) | XTI, XBR, XNG, XAU, XAG; XPT as the control (no sizeable leveraged ETF) | gold slope t +6.8, silver +8.2, platinum -3.9 | gold +2.6, **silver -4.3**, platinum -2.9 | the mechanism shows up (momentum where leveraged ETFs exist, reversal where they do not), but 0.3-2.4 bp against 1-4 bp of cost; silver flipped in VAL |
| S2 | follow-through after the EIA reports (crude Wednesday 10:30 ET, gas storage Thursday 10:30 ET) | XTI, XBR, XNG | +7.5..+18 bp, t 0.7-1.3 | +14..+31 bp, t 1.0-1.2 | right sign everywhere, but about 50 events a year: a 21-month HOLD would show t of about 0.7 even if the effect is real |
| S3 | the API report (Tuesday 16:30 ET) leaks into Wednesday | XTI | +41.5 bp, t 2.0 | +13.9 bp, t 1.0 | the same clock on days without an API report gives the same numbers: not an API effect |
| S4 | buy the 10:00-Sydney dip with a limit order (round 4's AUD/NZD V-shape at a passive price) | NZDUSD, AUDUSD | best -0.03 bp | best -0.16 bp | the dip is in both quotes and limit buys fill on 85-93 % of days, but 0 of 48 cells nets above zero |
| S5 | liquidity provision: fade 5-minute shocks in the US cash session, more when VIX is high (Nagel 2012) | US30, USTEC | best +2.7 bp (t 2.5, USTEC high VIX) | same cell +0.2 bp (t 0.1) | no reversal that repeats |

What this adds to rounds 3-4: the leveraged-ETF settlement flow is a fourth real flow, next to the Sydney open, the
Tokyo fix and the ECB fix, that is smaller than IC's round-trip cost. The inventory-report drift may be real but is too
rare to test in the holdout we have.

One correction to the cost model came out of S1. The research engine overstates metals commission before 2025 (see
"Cost model" below). No earlier verdict changes, but intraday metals screens were stricter than IC's real costs.

## Statistical power: what a 21-month holdout can confirm

HOLD (2025-01..2026-09) is 1.73 years. To expect t = 2.5 there, a strategy needs a per-trade Sharpe ratio (mean net
R / sd of R) of at least 2.5 / sqrt(n). To reach that bar with 80 % probability, it needs 3.34 / sqrt(n):

| trades in HOLD | per-trade Sharpe for E[t] = 2.5 | for 80 % power |
|---|---|---|
| ~430 (one a day) | 0.12 | 0.16 |
| ~80 (one a week) | 0.28 | 0.37 |
| ~20 (one a month) | 0.56 | 0.75 |

C3 passed with 738 legs at a per-leg Sharpe of 0.107. A weekly event therefore needs an edge about three times C3's per
trade. The two effects of this round that kept their sign:

| effect, net of cost, at its screened size | per-trade Sharpe | HOLD n | expected HOLD t | P(t >= 2.5) |
|---|---|---|---|---|
| S2 EIA crude follow-through, XTI, VAL size (+16.0 bp - 3.4 spread, sd 166 bp) | 0.076 | ~80 | 0.68 | 3 % |
| S1 gold settlement momentum, big days, 15 min, IS size (+2.31 - 1.30 bp, sd 11.8) | 0.086 | ~124 | 0.95 | 6 % |
| same, VAL size (+1.00 - 0.96 bp) | 0.004 | ~124 | 0.05 | 1 % |

So none of them is worth a pre-registration. The table also gives a rule for screening: a candidate whose IS/VAL
per-trade Sharpe times sqrt(its HOLD count) is below about 3 cannot pass however real it is. Its HOLD should not be
spent on it.

## S1: momentum into the settlement

For each US weekday (federal holidays dropped): r_day = log price from the previous day's settlement to w minutes
before today's; r_in = the last w minutes into the settlement; r_post = the 30 minutes after it. The statistic is
sign(r_day) x r_in (momentum > 0), on all days and on big days (|r_day| > 1 sd of the past 60 daily settlement
returns), plus the regression slope of r_in on r_day in sd units. Mid prices from the M1 cache. Settlement times:
NYMEX WTI and Henry Hub 14:30 ET, ICE Brent 19:30 London, COMEX gold 13:30 ET, silver 13:25 ET, NYMEX platinum
13:05 ET. Cost = median round-trip spread at entry plus commission.

| symbol | w | IS momentum, bp (t) | IS slope t | VAL momentum, bp (t) | VAL slope t | cost IS / VAL, bp |
|---|---|---|---|---|---|---|
| XTIUSD | 15 | +5.58 (2.0) | +2.6 | +1.81 (1.4) | -0.4 | 5.6 / 3.5 |
| XTIUSD | 120 | +2.46 (0.5) | +4.5 | +0.32 (0.1) | +0.8 | 5.4 / 3.5 |
| XBRUSD | 15 | +0.33 (0.2) | +0.1 | +0.57 (0.5) | -1.3 | 4.9 / 2.8 |
| XNGUSD | 30 | +2.52 (0.8) | -0.6 | +10.87 (3.1) | +2.4 | 13.0 / 44.7 |
| XAUUSD | 5 | +0.41 (2.4) | +5.1 | +0.41 (2.1) | +3.0 | 1.3 / 1.0 * |
| XAUUSD | 15 | +0.58 (2.3); big days +2.31 (3.6) | +6.8 | +0.29 (0.9); big days +1.00 (1.5) | +2.6 | 1.3 / 1.0 * |
| XAGUSD | 15 | +2.43 (4.5); after the settlement -6.89 (-4.1) | +8.2 | -1.55 (-2.6); after +0.41 (0.3) | -4.3 | 3.9 / 4.3 |
| XPTUSD | 15 | -1.64 (-1.9) | -3.9 | -1.87 (-2.5) | -2.9 | 19.3 / 25.7 |

\* gold cost with commission at $30 per $1M per side (0.6 bp round trip); the screen printed 2.1 / 1.7 bp with the
engine's commission (next section).

- **Silver** in IS looks like price pressure: momentum into the settlement (t +4.5, slope t +8.2), then a reversal
  after it (-6.9 bp, t -4.1). It is gone from 2021 and slightly reversed in VAL. The yearly big-day means are
  +10.0 / +3.3 / +2.0 / +6.4 / -1.1 / +2.7 bp for 2016-21, then -0.7 / -2.5 / -2.7 bp for 2022-24 (5-minute window).
- **Gold** keeps the momentum in VAL (slope t +3.0 at 5 min, +2.6 at 15 min). At its size it nets about +1.0 bp
  (IS) and +0.04 bp (VAL) on big days after the corrected cost.
- **Platinum**, the control without a sizeable leveraged ETF, reverses into its settlement in both eras. The sign
  pattern fits the rebalancing story, which makes the gold/silver flow believable. It is still too small to trade.
- **Oil** depends on 2020 (big-day XTI +55 bp at 5 min in 2020, -3..+7 bp in the other years). **Natural gas**
  momentum appears only in VAL, when IC's XNG spread at 14:00-14:30 ET was about 45 bp.

## S2 and S3: inventory reports

S2: r0 = the first k minutes after 10:30 ET on the release day (weeks with a federal holiday up to the release are
dropped, because the release moves). Follow-through = sign(r0) x the move from 10:30+k to the end time. The control is
the same clock on the other weekdays.

| symbol | k | to 11:30 IS / VAL, bp (t) | to 14:30 IS / VAL | big events (\|r0\| > median) to 14:30 IS / VAL | spread at entry IS / VAL |
|---|---|---|---|---|---|
| XTIUSD | 5 | -0.5 (-0.1) / +13.4 (1.9) | +18.0 (1.3) / +16.0 (1.1) | +23.1 (1.0) / +31.4 (1.7) | 5.9 / 3.4 |
| XBRUSD | 5 | -0.5 (-0.1) / +12.3 (2.0) | +7.5 (0.7) / +13.8 (1.0) | +19.3 (1.2) / +33.8 (2.0) | 5.5 / 2.8 |
| XNGUSD | 5 | +11.6 (1.5) / -0.6 (0.0) | +17.8 (1.2) / +30.8 (1.2) | +11.6 (0.5) / +53.4 (1.4) | 12.6 / 47.1 |
| XTIUSD | 1 | -4.3 (-0.6) / -0.3 (0.0) | -10.4 (-0.7) / -9.3 (-0.6) | | 6.4 / 3.5 |

- After 5 minutes, oil and gas continue in the direction of the report in both eras. The first minute bounces back
  (k = 1). Control weekdays reach |t| <= 2.4 with mixed signs, so the event cells are not outliers. There is no
  pre-release drift that holds in both eras (09:30-10:29 XTI -1.0 / -11.3 bp, XBR +0.2 / -9.7, XNG -10.3 / +3.1).
- XNG's VAL spread (45-47 bp) leaves only crude. Crude is about 50 events a year, so the power table above applies.
- S3 (API, XTI): follow the first 5 minutes after Tuesday 16:30 ET to Wednesday 09:30 ET: +41.5 bp (t 2.0) / +13.9
  (t 1.0). The same clock on Monday gives +27.2 (0.8) / +17.0 (1.2) and on Wednesday +20.8 (0.9) / +22.3 (1.6), with
  first moves of only 3-4 bp. The follow-through is generic overnight continuation, not information from the API
  report, and it crosses the 17:00 ET break, which costs about 2.5 bp of swap a night.

## S4: the 10:00-Sydney dip at a passive price

Round 4 found a V-shape in AUD and NZD around 10:00 Sydney (t -13), smaller than the round-trip cost at market prices.
The M1 quote path shows where it sits. All of the dip is in the minute before 10:00, in both quotes, and it is gone
5-10 minutes later (bp from the T-30 mid; Tue-Fri):

| | T-5 bid / ask | T bid / ask | T+10 bid / ask |
|---|---|---|---|
| NZDUSD IS | -1.02 / +0.35 | -2.35 / -1.01 | -0.75 / +0.10 |
| NZDUSD VAL | -1.05 / +1.19 | -2.59 / -0.23 | -0.22 / +0.60 |
| AUDUSD IS | -0.67 / +0.18 | -2.07 / -1.27 | -0.57 / -0.09 |
| AUDUSD VAL | -0.44 / +0.75 | -1.63 / -0.48 | -0.08 / +0.09 |

On cTrader, a retail buy limit fills when the ask reaches it, so a passive buy can catch the dip. Tick simulation:
at T-3 min, a buy limit x bp below the ask, live until T+3 min. Exit at the bid at T+10 min, or at a sell limit y bp
above the fill. Commission is 0.6 bp. That is 4 x-offsets (0.5-3 bp) x 3 targets (0, 1, 2 bp), plus one variant
placed at T-10, live 5 min, held 15 min. Controls at 09:00 and 11:00 Sydney.

| | fill rate at 10:00 | best net per fill, bp (t) | controls 09:00 / 11:00, net per fill |
|---|---|---|---|
| AUDUSD | 53-94 % | x 3.0, y 0: -0.03 (-0.1) IS, -0.16 (-0.6) VAL | -1.6..-2.3 / -0.8..-1.6 |
| NZDUSD | 47-93 % | x 2.0, y 0: -0.87 (-3.9) IS, -1.05 (-3.8) VAL | (similar) |

The 10:00 cells are 1-2 bp better than the controls, which is the dip. But the bid 10 minutes later is never far
enough above the ask at the fill to pay for commission. Targets (y > 0) make it worse, because the rebound rarely
clears the spread. Passive execution does not rescue the effect.

## S5: liquidity provision in the US cash session

5-minute mid bars 09:35-15:50 ET. An event is a 5-minute return beyond k = 2, 3 or 4 sd of the same clock slot over
the previous 20 days. Outcome = -sign x the next 5 / 15 / 30 minutes (reversal > 0); t on day-clustered sums. The split
is by the previous day's VIX close (FRED VIXCLS), at the IS terciles.

| | best IS cell | same cell in VAL | VAL range over the 18 cells (all VIX) |
|---|---|---|---|
| US30 (cost 0.9 / 0.3 bp) | h 30, k 4, high VIX: +2.52 bp (t 1.3) | -4.60 (t -1.6) | -2.53..+0.03 bp |
| USTEC (cost 1.6 / 0.7 bp) | h 5, k 4, high VIX: +2.67 (t 2.5) | +0.22 (t 0.1) | -4.14..+0.25 bp |

No reversal survives into VAL, high VIX or not. In VAL, large USTEC moves continue over 30 minutes (k 3, high VIX
-5.0 bp, t -2.1).

## Cost model: metals commission

`research/specs.py` gives XAUUSD a fixed `comm_per_unit` of $0.2579 per oz round trip, measured from the 2026 cTrader
reports. That is $30 per $1M per side at $4,298/oz. `research/specs_ext.py` does the same for silver ($65.3/oz) and
platinum ($1,791.9/oz), and `m1bars.comm_price` applies the number at every date. The docstring of `specs_ext.py`
states the broker's schedule: per $1M notional for FX and metals. Under that schedule, the engine's commission is too
high whenever the metal traded below its 2026 price:

| year | 2016 | 2018 | 2020 | 2022 | 2024 | 2026 |
|---|---|---|---|---|---|---|
| gold median $/oz | 1,257 | 1,263 | 1,774 | 1,805 | 2,381 | 4,527 |
| engine commission, bp (true 0.6) | 2.05 | 2.04 | 1.45 | 1.43 | 1.08 | 0.57 |
| silver engine commission, bp (true 0.6) | 2.29 | 2.45 | 2.13 | 1.80 | 1.35 | 0.54 |

Effect on earlier verdicts:
- For D1/H4 swing trades it is about 0.01 R a trade, which changes nothing.
- For intraday gold/silver screens, costs were 0.5-1.7 bp too high. The rounds 3-4 tables quote gold at 1.6 bp and
  silver at 5.5 bp; corrected, they would be about 1.0 and 4.3. None of the gold/silver effects rejected in rounds 3-4
  becomes tradeable at the corrected cost: silver into the 12:00 fix (-2.8 bp) is still under silver's spread, and
  gold at the LBMA PM fixing failed VAL on t.
- Gold hour-of-day patterns stay excluded, because their HOLD was printed in round 3.

The engine is not changed in this round. The fix is to compute metals commission as a fraction of price (as `swing.py`
already does for swaps). It does not touch FX, indices, energies or crypto, or C3.

## What this says

- Six rounds now tell the same story. The flows that exist in these symbols (the gotobi fix aside) are 0.3-3 bp. That
  is the size of IC's round-trip cost at the moment they happen. This round's new examples are the leveraged-ETF
  settlement flow in gold/silver, the platinum reversal, and the oil follow-through after EIA. Executing passively does
  not change that on cTrader, where limit orders fill against the broker's quote.
- The rarer and larger effects (inventory reports, monthly events) are too infrequent for the one holdout we have. The
  power table shows the size a candidate needs before a pre-registration is worth writing.
- What would change the picture is the same as at the end of round 4. Nothing more can be screened from these
  symbols over 2016-2024:
  1. **A new clean holdout.** The cache ends 2026-09-24/28, and every day after it is unseen for all candidates. IC also
     serves FX ticks from 05/2014, which is 19 months no strategy has used (pulling them needs throwaway backtest
     containers on the VPS, which is the user's call). For the commodity and index effects above, pre-2016 data adds
     little: energies start in 2018 and most indices in 2016.
  2. **Lower execution cost** for the 1-3 bp flows. That is a broker question, not a research one.
  3. **The 5-day and 3-position limits**, which still rule out the multi-week premia. This is not proposed.

## Process

- **Data.** `research/data/` had been removed from this machine. The tick caches of 10 symbols (XTIUSD, XBRUSD, XNGUSD,
  XAUUSD, XAGUSD, XPTUSD, NZDUSD, AUDUSD, US30, USTEC) were pulled from the VPS cache and the M1 files rebuilt with
  `python -m research.m1`. A single ssh stream ran at 0.15-0.5 MB/s. One stream per (symbol, year), 8-10 in
  parallel, reached about 1.8 MB/s. One stream (XPTUSD 2022) failed without an error and was caught by counting the
  tick days per year; it was re-pulled and the M1 file rebuilt before the final XPT numbers. All other symbols have
  365/366 days for every year of 2016-2024 (energies from 2018).
- **HOLD kept closed.** The screening loader dropped every M1 row at or after 2025-01-01 before computing anything, so
  no HOLD number was computed or printed. The round-3 contamination list (pre-FOMC drift; hour-of-day patterns of
  XAUUSD, XAGUSD, US500, DE40, JP225, AUDUSD, BTCUSD) still applies. S1 times the US settlement, not an hour-of-day
  effect. S4 uses AUDUSD at the Sydney open, the round-4 event whose finding rests on NZDUSD.
- **Code.** The screens ran as scratch scripts on the M1 cache and the ticks (mid prices; costs from the real
  bid/ask, commission at $30 per $1M per side for FX and metals, none for energies and indices), as in rounds 3-4.
  Nothing went into the repo, because nothing reached a pre-registration. External data: FRED VIXCLS (S5).
- **Look-ahead.** Volatility scalings are causal: S1 uses the past 60 daily settlement returns, S5 the same clock slot
  over the previous 20 days and the previous day's VIX. Two thresholds are screening shortcuts, not tradeable rules:
  S2's "big event" cut is the era median of |r0|, and S5's VIX terciles come from IS. Both can only flatter the
  screens, and the screens still failed. S1/S2/S3/S5 measure mid prices and quote costs separately. S4 is
  tick-level at executable prices.
- C3 correlation was not computed, since no candidate exists.
