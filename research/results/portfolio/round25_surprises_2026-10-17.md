# Round 25: predictable release surprises, an older-literature census, and what each data decision is worth

2026-10-17 (UTC). The user asked (2026-10-18 local): "research kỹ đến khi nào có thuật toán chạy live được thì thôi".
The user's original LIVE and DEMO bars apply; the round-24 RELAXED tier was not re-allowed and is not used.
[round25_surprises/BRIEF.md](round25_surprises/BRIEF.md) fixed the three streams at 18:52 UTC, before any round-25
number. HOLD (2025-01..2026-09) stayed closed in every stream.

## Answer
- **No LIVE candidate, no DEMO candidate, nothing registered, HOLD not opened.** C3 is still the only LIVE algorithm.
- **B: the predictable part of a release surprise is already in the price.** For the first time the project used
  published consensus forecasts (ForexFactory calendar 2007-2025). The consensus is predictable: anchoring to the
  previous print calls the surprise sign 54-57 % of the time, and national flash CPIs call the euro-area flash HICP
  surprise 76-92 % of the time. But FX prices both before the release; 144 declared cells make at most ~1 bp gross
  against a 0.8-1.9 bp release-minute round trip.
- **C: the pre-2018 literature and non-English practitioner lore add nothing new.** 13,748 records, 353 mapped into 39
  families, 27 families already tested here. 10 declared cells, none passes. Gold's $10 levels act as barriers in
  every era since 2004 (continuation after a break), but net only about half of IC's cost; the post-hoc COMEX-hours
  slice nets ~+3 bp in every era with power 1.68 at the VAL size: information only.
- **A: no pending user decision has an expected LIVE candidate.** Best chances: single-stock CFDs (employee selling
  after the earnings blackout, ~3-5 % LIVE / ~25 % DEMO, but IC's share CFDs are MT5-only), an EM fix book led by
  USDMXN (~2 %), Norges Bank's pre-announced NOK flow (~1 %), a cheaper venue (~1 %).
- **Forward log (data after 2026-09-24, user-chosen):** slice 2 to 2026-10-16 appended; F3 still 2 trades, E1 16.

## B. Predictable release surprises ([STREAM_B.md](round25_surprises/STREAM_B.md))
144 cells declared at 19:08 UTC in [HYPOTHESES_B.md](round25_surprises/HYPOTHESES_B.md). Calendar: ForexFactory
2007-01..2024-12 (public Hugging Face dataset, MIT; 2025 rows cut at load). 32.7 % of high-impact rows had lost their
time (rows sharing a slot sit at 00:00 Tehran) and were re-timed from the type's own rows, slot partners and official
schedules; the CSV's +04:30 summer labels are wrong in 2023-24 (Iran dropped DST); early subscriber releases (Markit
PMIs to 2013, MNI Chicago) were found from the release-minute activity spike. Timed calendar for reuse:
scratchpad `r25/shared/cal/ff_events_utc.csv`.

| family (source) | PRE / IS / VAL mid bp (t) | cost IS / VAL | net IS / VAL (t) | power IS / VAL | verdict |
|---|---|---|---|---|---|
| B0 realised surprise sign (validation only) | NFP +12.6 (5.9), core CPI +10.3 (7.0), ISM +5.7 (6.7), AUD jobs +9.4 (3.9), CAD jobs +18.0 (7.2), 1-min, IS | - | - | - | times, signs, units confirmed; 56 types kept |
| B1 anchoring, sign(F - previous first print) (Campbell & Sharpe 2009), all currencies, entry T-1, 15 min | -0.06 / +0.71 (1.39) / +0.40 | 1.72 / 1.32 | -1.01 (-1.98) / -0.92 | < 0 | fails |
| B1, entry T-2 | +0.15 / +0.68 / +0.32 | 0.88 / 0.84 | -0.20 / -0.53 | < 0 | fails |
| B1 USD pool, 5 min (best B1 gross) | +0.34 / +0.82 (1.89) / +1.11 | 1.17 / 1.10 | -0.35 / 0.00 | < 0 | fails |
| B2 early indicators vs a stale consensus (ADP -> NFP, Fed surveys -> ISM, flash -> final PMI, national CPIs -> EA HICP, Tokyo -> national CPI, claims -> NFP, CN PMI -> Caixin), pooled | -0.81 / -0.22 / -1.51 (-2.07) | 0.98 / 0.93 | -1.21 (-3.25) / -2.44 (-3.33) | < 0 | fails |
| B3a Cleveland Fed CPI nowcast vs consensus | -5.18 / +6.41 (2.00) / -15.80 | 1.57 / 1.88 | +4.84 (1.50) / -17.67 | 1.09 / < 0 | fails (IS is 2017) |
| B3b core PCE nowcast; B3c GDPNow | mixed signs | ~1-1.6 | IS < 0 | < 0 | fail |

- Chance: 144 cells, best |IS gross t| 2.23 (wrong sign); per-day sign-flip null p50 2.46, p95 3.21.
- **FX sees through the anchoring.** Regressing the 5-minute move on the realised surprise and the anchoring
  predictor gives the predictor -0.58 (t -3.1) in PRE and -0.41 (t -2.7) in IS, close to the rational-pricing value
  (-0.32 / -0.29), far from a naive market's 0. Same finding as Campbell & Sharpe for Treasury yields.
- **IC's spread doubles in the last minute before a release**: 1.7 bp round trip entering at T-1 against 0.9 at T-2
  on high-impact slots. Any release rule should enter at least two minutes early.
- C3 daily correlation -0.01..+0.03.

## C. Older literature and practitioner lore ([STREAM_C.md](round25_surprises/STREAM_C.md))
Census (OpenAlex, Crossref, arXiv, Semantic Scholar; queries logged): 13,748 unique records, 2,717 read by title and
abstract, 353 mapped into 39 families: 27 already tested in rounds 3-24, 3 without basis or with one event a year, 2
gone by their own sources, 2 outside the 26 symbols, 1 needs API values, 1 methodological. Lore (71 searches in
Japanese, Chinese, Korean, German; 59 claims): 22 tested before, 1 declared. 10 cells declared at 19:33 and 19:53 UTC
in [HYPOTHESES_C.md](round25_surprises/HYPOTHESES_C.md).

| cell (source) | where | IS / VAL mid (t) | net IS / VAL (t) | random IS / VAL | verdict |
|---|---|---|---|---|---|
| MON-a short Friday -> Monday after a down Friday (Abraham & Ikenberry 1994); b-e variants | US500, US30, USTEC | -5.8 / +7.7 | -10.2 / +6.7 | 44 / 91 % | fails; the published -61 bp would give IS t ~5 |
| BAR-i follow a round-level break for 60 min (Osler 2005; Donaldson & Kim 1993) | 8 indices (100 pts) + gold ($10) | +1.20 (2.72) / +0.49 | -1.30 (-2.98) / -0.92 | 100 / 87 % | fails; in indices a half-level placebo matches it |
| BAR-d daily-close break of a 100 level | 8 indices | -4.1 / +0.3 | -8.2 / -2.9 | 0 / 58 % | fails (reverses) |
| JPN-ab first Tokyo trading day long, last short (Japanese lore JA-21) | JP225 | +28.2 (2.46) / +4.6 | +22.5 (1.96) / +0.6 | 99 / 59 % | fails (IS t < 2, 2021 carries it, +1 min < 0) |
| info: gold leg of BAR-i | XAUUSD | PRE +3.50 (4.86) / IS +2.77 (3.31) / VAL +2.06 (2.39) | PRE +1.92 / +1.10 / +1.02 | 100 % in all eras | real at mid in every era, $5 placebo flat; below DEMO |
| post hoc: same, entries 12:00-17:00 UTC | XAUUSD | PRE +4.32 / +4.62 / +4.23 | +2.83 (2.15) / +3.10 (2.16) / +3.23 (2.17) | 100 % | picked after looking: information only; power 1.68 at the VAL size |

- Chance: max of 10 normals p95 2.81; best declared IS |t| 2.72.
- The gold barrier matches Lucey & O'Connor (2016): barriers in gold, none in silver. Even at zero cost its power is
  below 3. STREAM_C fixes an exact rule should the user want it logged on data after 2026-09-24 (a forward t of 2
  needs ~2.5 years at the VAL size).

## A. What each pending decision is worth ([STREAM_A.md](round25_surprises/STREAM_A.md))
No price was fetched. Power = per-trade net Sharpe x sqrt(1.73 x trades a year) at full VAL size / x0.65 / x0.30
(round 18 and 16 retention factors). Declared cells for the top routes, written before any of their data exists, are
in [HYPOTHESES_A.md](round25_surprises/HYPOTHESES_A.md) (H-NOK, H-STK, H-CNH, H-EMFIX).

| route | effect vs cost (bp) | events / yr | power full / x0.65 / x0.30 | chance of LIVE |
|---|---|---|---|---|
| single-stock CFDs: short high stock-pay firms for 3 nights after the earnings blackout lifts (Hartzmark & Solomon NBER w30688: -87.5 bp, t -5.8, 2002-20) | 40-90 vs ~9 | 50-150 | 0.6-2.6 / 0.3-1.6 / 0.1-0.6 | ~3-5 % (DEMO ~25 %); IC share CFDs are MT5-only |
| EM fix book: USDMXN over the Banxico FIX window + USDCNH CFETS close + USDSGD ABS | MXN ~4.2 vs 2.07 if E1-like | ~245 per leg | 1.96-3.48 / 0.55-1.40 / 0 | ~2 % |
| Norges Bank's pre-announced daily NOK amount (EURNOK) | 0-3 vs 2.9-5.6 | ~225 | -0.3-0.8 / ~0 / 0 | ~1 % |
| cheaper venue (Fusion cTrader 0.45 bp round trip, IBKR 0.20 bp/side) | J5c 1.53 vs 0.6; ECB slot 1.14 vs 0.45 | 50-254 | only J5c >= 3 at full size (its HOLD already failed) | ~1 % |
| USDCNH bid/ask ticks (CFETS close unchanged) | 1.22 / 1.68 vs 0.8-1.0 | ~237 | 1.2-1.6 / 0.1-0.5 / 0 | 0 % LIVE, DEMO ~15 % |
| paid data (Deribit OI, CLS flows), FX crosses, softs, PLN/CZK/HUF/ZAR/TRY/HKD | - | - | <= 2.9 optimistic, mostly < 1 | <= 1 % each, ~0 for crosses / softs / other EM |

- USDMXN is the cheapest EM pair per unit of risk at IC (2.07 bp against a ~32 bp sd over the three-hour FIX window),
  but the FIX is the mean of three random snapshots in 09:00-12:00 Mexico City and no dealing-at-FIX convention or
  price-pressure study was found. The NBP, CNB and MNB rates are accounting rates (round 19's observation class).
- Norges Bank's daily NOK amounts since 2000 are saved (scratchpad `r25/A/web/nok/nb_fx_monthly.csv`): it bought NOK
  every month in IS and sold almost every month in VAL, a clean dose-response design.
- The US earnings-announcement premium has been gone since 2004; the stock-level blackout result was dropped from the
  published AER 2025 version of Hartzmark & Solomon.

## Forward log ([round24_relaxed/PREREG_R24_forward.md](round24_relaxed/PREREG_R24_forward.md), slice 2)
Dukascopy EURUSD / USDJPY / USDCHF to 2026-10-16 (a first pass lost two FWD days to HTTP 503s and was refetched into
a fresh directory); registered code unchanged; slice 1 reproduces trade by trade.
| rule | FWD n | FWD net (b) | HOLD + FWD net (t) |
|---|---|---|---|
| F3 | 2 (no trade since 7 October) | -9.18 | +1.81 (1.89), n 119 |
| E1 | 16 | -2.27 (t -0.71) | +0.54 (0.85), n 460 |

## What this says
- Public information is priced by the time a retail bot can act on it. Round 8 showed it for other markets' moves
  (priced within a minute), rounds 3 and 10-11 for the realised surprise (no drift), and now round 25 for the
  predictable part of the surprise itself (priced before the release).
- The older literature is mapped: what remains untested is either one event a year, outside the 26 symbols, or
  gone. Gold's round-number barrier is the one durable new effect, and it is a DEMO-size effect at best.
- The decision memo turns the open user decisions into numbers. None of them is expected to produce a LIVE
  algorithm; the largest chances (3-5 %) need either a new platform (MT5 share CFDs) or IC tick pulls on the VPS.

## Needs the user
- **Cheap FX data pulls** (stream A's first recommendation): IC ticks 2016-24 via cTrader backtest downloads on the
  VPS for USDCNH, USDMXN, USDSGD, EURNOK, USDNOK, EURSEK (hours of VPS time, ~1-2 GB each), plus Dukascopy M1 2004-15
  for the same pairs. Tests H-EMFIX, H-CNH, H-NOK as declared. Combined chance: LIVE ~3 %, DEMO ~25 %.
- **A non-cTrader platform for share CFDs** (IC: MT5 only): needed before the stock route is worth a 1-2 day build on
  free data (Dukascopy US stock CFDs 2017-24 + SEC EDGAR).
- **Gold barrier rule** on data after 2026-09-24 (a new Dukascopy XAUUSD fetch; DEMO at best).
- Consensus data for 2025-01..2026-09 only if a future release rule needs HOLD (the FF file ends 2025-04-07).

## Process notes
- HOLD stayed closed: the panel ends 2024-12-31, Dukascopy PRE 2015-12-31, FF rows from 2025 cut at load. Stream B
  printed the first rows of the GDPNow track-record sheet once; they include 2025-26 quarters (macro numbers, no
  prices) and were cut at load in the cells.
- **Stream C's first OpenAlex request carried the user's e-mail address in its contact parameter** (one request;
  no other request carried it). Future briefs forbid putting the user's address in any request.
- The session's shared web-search budget (200 searches) ran out at ~19:17 UTC and OpenAlex's free daily budget at
  ~19:11 UTC; later lookups used Crossref and direct fetches. Plan literature passes within these budgets.
- A Dukascopy first pass can lose whole days to HTTP 503s on a busy server; check every forward day and refetch into
  a new directory before running a registered log.

## Files
- [round25_surprises/](round25_surprises/): BRIEF.md; HYPOTHESES_A/B/C.md; STREAM_A/B/C.md.
- [round24_relaxed/prereg_code/fwd_output_2026-10-16.txt](round24_relaxed/prereg_code/fwd_output_2026-10-16.txt) and
  calib_output_2026-10-16.txt (forward slice 2).
- Scratchpad `r25/` (A, B, C, lead, shared panel and calendar); not kept.
