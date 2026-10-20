# PREREG DRAFT (round 24, stream C): long the higher-rate currencies against USD over FOMC days (round 20 A4). Tier RELAXED

Draft written 2026-10-15 12:04 UTC (`date -u`). HOLD (2025-01 onwards) was not opened; the lead decides whether to
register it. The rule is round 20's A4, unchanged ([round20_declared2/HYPOTHESES_F.md](../round20_declared2/HYPOTHESES_F.md),
declared 2026-10-06 04:03 UTC; re-declared for this stream in [HYPOTHESES_C.md](HYPOTHESES_C.md) at 11:53-11:55 UTC).
No parameter was changed or chosen here.

## Rule (exact)
- Source: Mueller, Tahbaz-Salehi & Vedolin (2017, JF): the dollar falls against higher-rate currencies on FOMC
  days (a premium for bearing US policy-rate uncertainty). Side from the paper, not from our data.
- Days: scheduled FOMC statement days (`r23/shared/cal/fomc_2016_2024.json`; for HOLD and the demo, the Fed's published
  calendar; unscheduled meetings excluded).
- Universe: EUR, GBP, JPY, AUD, NZD, CAD, CHF against USD, traded through EURUSD, GBPUSD, AUDUSD, NZDUSD (long) and
  USDJPY, USDCAD, USDCHF (short).
- Ranks: each currency's short rate = the last value of its research/data/rates series dated before the first day of
  the entry month (monthly series: the previous month's value). Long every currency whose rate is above USD's, equal
  weight (1/k of the risk each); **no trade if no currency is above USD**.
- Entry: mid at the minute labelled 16:00 New York (fill on the 16:00 bar) on the weekday before the statement; exit:
  same on the statement day. One rollover crossed (swap charged). Fixed lot, no stop.
- Costs: half the actual spread at each fill + 0.6 bp per leg, swap per rollover.

## Numbers (stream C recompute = round 20 exactly; net bp per basket, t clustered by day)
| era | events | mid (t) | net (t) | x1.5 | +1 min | per-event Sharpe | power (VAL / IS size) | random days beaten | years > 0 |
|---|---|---|---|---|---|---|---|---|---|
| IS 2016-21 | 37 (10 FOMC days without a trade) | +23.00 (2.02) | +21.62 (1.90) | +21.35 | +21.41 | 0.31 | 1.02 | 97.5 % | 6/6 |
| VAL 2022-24 | 23 | +32.94 (2.50) | +31.60 (2.40) | +31.32 | +31.19 | 0.50 | **1.82** | 100 % | 3/3 |

By year (net): 2016 +6.6, 2017 +45.4, 2018 +14.0, 2019 +41.1 (1 event), 2020 +31.6, 2021 +6.5, 2022 +23.7,
2023 +49.4, 2024 +20.3. Round 20 also had PRE 2004-15 +16.6 net (t 1.97) on Dukascopy and pooled 2004-24 +20.0 (t 3.25,
n 156). VAL/IS = 1.43 (not decaying). Correlation with C3 (IS + VAL): daily +0.000, monthly -0.108.

## Tiers
- **RELAXED: passes** (IS t 1.90 >= 1.5; VAL net > 0, t 2.40 >= 1.0; x1.5 and +1 minute > 0; random 97.5 / 100 %;
  VAL-size power 1.82 >= 1.5; mechanism from the literature).
- DEMO: fails on IS t (1.90 < 2.0). LIVE: fails on IS t and power.
- Cost needed for LIVE: none (the round-trip cost would have to be about -19 bp); 8 events a year cap the power, not
  the cost (~1.2 bp against a 63 bp sd).

## Expected HOLD (2025-01..2026-09)
- Expected events at the 2016-24 rate: 1.73 x 7.7 = **~13**. Expected HOLD t: **1.82 at the VAL size**, 1.16 at 0.65 of
  the VAL mid (the retention of declared / literature rules in round 18), 0.40 at 0.25.
- **Caveat the lead must check before opening HOLD (rates only, no prices):** in 2025-26 the US policy rate was at or
  near the top of the eight, so many HOLD FOMC days may have no currency above USD and therefore no trade. Count the
  HOLD trades from the rate files first; with fewer than ~8 events the expected HOLD t is below 1.4 even at the VAL
  size, and HOLD then cannot say much.
- One HOLD look. Reject if HOLD net per event <= 0 at the registered costs.

## Demo (if registered; demo account only, fixed small risk, never live without the promotion rule)
- Expected demo trades: up to 8 events a year (fewer while USD is the highest rate), each a basket of up to 7 pairs
  (more than 3 positions on one bot: run one bot per pair, each with at most one position).
- Stop rule: after 16 demo events, stop if HOLD + demo pooled net per event <= 0, or if the realised mean round-trip
  cost exceeds 3 bp per basket.
- Promotion rule (RELAXED -> LIVE): HOLD + demo pooled day-clustered net t >= 2.5 at the costs paid. At the VAL
  per-event Sharpe (0.5) that needs ~25 events (about 3 years of FOMC days); at 0.65 retention ~60.
- Multiple testing: one of 7 round-20 cells (A1-A4, B1-B3) and one of 60 recomputed rows in stream C; it is a
  literature rule re-evaluated, not a new pick.
