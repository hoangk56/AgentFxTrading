# Round 37, stream A: record-level stops (and other salient-level stop clusters) with the gold $50 construction

Written 2026-10-29 09:56 UTC (`date -u`). All rules, cells, controls and bars were declared in
[HYPOTHESES_A.md](HYPOTHESES_A.md):
- A / F / B / PRE at 09:31 UTC, before any count or return;
- the event counts and cell A1 (K = 1) at 09:42, before any return;
- family C at 09:51, after the A / B results and before any C return.

HOLD was never loaded. Every IC series is cut at ts < 2025-01-01 at load, tick days are asserted < 2025-01-01, and
Dukascopy is cut at 2016-01-01.

## Answer
- **No family reaches LIVE or DEMO at the book level.** Records (A), FX records (F), calendar-period extremes (B) and
  previous-week / 200-day-average levels (C) all fail. The best book net IS t is +1.97 (A1 H52 h60, VAL t 1.27,
  placebo 0.91 / 0.95), just under DEMO's 2.0.
- **The counts rule LIVE out for records before any return.**
  - Fresh (K >= 5) record breaks are ~45 a year across the 12 A symbols, so LIVE would need a per-trade Sharpe of
    0.34; gold $50 has 0.14-0.17.
  - Only B and C (~500 a year) have the count for LIVE, at ~0.10.
- **Records continue at mid, but no more than any fresh extreme does, and the move is below cost.**
  - A primary book (all record types, K = 5, 30 min): mid +7.3 bp (t 2.37) IS, +8.0 (t 0.96) VAL. Cost 2.9 / 2.3 bp.
    Net +0.077 sd (t 0.66) / +0.101 sd (t 0.56). Placebo levels beaten 0.895 / 0.985.
  - Up-breaks carry it. 52-week-high breaks over 60 minutes: net +0.24 sd (t 1.72) IS, +0.32 (t 1.78) VAL, power
    1.09 / 1.37. Placebo IS 0.825, so it fails DEMO.
  - **52-week-low breaks lose** (IS -0.41 sd, VAL -0.16), the opposite of gold's down-break asymmetry.
  - The declared dose predictions fail. K = 20 (older records) is weaker than K = 5 (A20 book net -0.009 / +0.044
    sd); ATH is about equal to H52.
- **B, C and their FX versions reproduce the "real at mid, below cost" pattern of rounds 15 / 28 / 31.**
  - The mid effect is beyond chance. C PW book IS mid t 4.02 (sign-flip null p 0.001); BF h60 mid t 3.40 (p 0.010).
  - It is 1-3.7 bp against a 1-4 bp round trip. Net IS: B -2.23 bp (t -2.11), C -0.96 (t -1.09), BF -0.14, CF
    -1.24 (t -4.88).
  - At zero cost the C PW book's mid Sharpe (~0.08 a trade at ~460 a year) gives power ~2.3. **A cheaper venue would
    not make it LIVE either.**
- **Cells with DEMO numbers on their own (none drafted as a recommendation):**
  - **BTCUSD records, K = 5, 30 min (a declared candidate cell).**
    - IS n 9: +126 bp (t 3.17), 5/5 years positive. VAL n 15: +52.5 bp (t 0.75). Placebo 0.99 / 0.995.
    - Family null p 0.036 (48 cells).
    - VAL is positive only through one +955 bp trade (2023-10-23); without it VAL is -12 bp a trade. ~5 trades a
      year, so HOLD power is 0.57.
    - Written up, not recommended:
      [PREREG_DRAFT_A_btc_record_stop.md](PREREG_DRAFT_A_btc_record_stop.md).
  - **USDJPY period extremes, 30 min (a per-symbol reading, not a declared candidate).**
    - IS +2.15 bp (t 2.09), VAL +4.19 (t 2.06), 6/6 IS years positive. Placebo 0.995 / 0.955.
    - It is the best of 52 B / BF cells at a null p of 0.446, i.e. chance. EURJPY / GBPJPY / AUDJPY do not repeat it.
    - Not drafted.
- **PRE 2005-15 (Dukascopy, minute model).**
  - Gold + silver records: +14.3 bp net (sd t 1.96), 8 / 10 years positive, n 69 (6 a year). IC 2016-24 is weaker:
    gold +6.2 / +7.2 bp (t 0.8), silver negative.
  - FX records lose (-3.7 bp, t -2.06). Period extremes are flat (-0.85 bp).
- **Not P1 or Donchian relabelled.**
  - Record trade days are 2.1 % of P1-PD days (symbol-sessions with an armed prior-day break), 5.0 % of daily
    Donchian-20 days and 7.8 % of Donchian-55 days.
  - The prior-day extreme had triggered within 60 minutes before the record trigger in only 22 % of trades (median
    266 minutes earlier).
  - B overlaps P1 far more: in 67 % of B trades P1 had triggered within the hour, and in most cases it is the same
    minute (median 1 minute: the period high is often also yesterday's high).
  - 84 % of record trade days close beyond a 20-day Donchian level, but that is known only at the close. The non-D20
    record days lose (IS -0.07 sd, VAL -0.15), the usual ex-post split, not a rule.
- **Gold overlap with round 27.** 6 IS / 2 VAL gold record levels lie within $5 of a $50 multiple. The record trades
  away from $50 levels make +5.8 bp IS / -3.1 VAL (n 15 / 6), so records add nothing to gold's $50 rule.

## Sources and data
- **No new downloads.** Five Crossref lookups for the DOIs (`web/requests.log`) and no web searches.
- Literature:
  - Osler 2003 (JF, 10.1111/1540-6261.00588) and Osler 2005 (JIMF, 10.1016/j.jimonfin.2004.12.002);
  - Huddart, Lang & Yetman 2009 (Management Science, 10.1287/mnsc.1080.0920);
  - George & Hwang 2004 (JF);
  - Li & Yu 2012 (JFE, 10.1016/j.jfineco.2011.04.003).
- IC M1 for 12 A symbols and 10 FX; IC ticks (< 2025) for USTEC, US30, XAU and XAG, which use the 250 ms tick model;
  US2000 from bid zbars with round 29's declared spread model.
- Dukascopy 2004-15: XAU and XAG m1c, FX m1 / m1c (PRE), and H1 seeds for the 2015 52-week window of XAU and FX.
- **Unusable or missing**:
  - `research/data/duka/raw/*IDX*` (index folders) hold only a few probe files, so there is no index PRE.
  - Round 25's ForexFactory file is gone with its scratchpad. The news exclusion uses the USD-only calendar copies in
    the repo (`gold_level_cbot/ff_usd_high_2015_2023.csv` + `usd_high_2024_2026.csv` rows < 2025); there is no
    exclusion for other currencies and none in PRE.
  - IC quote glitch days from round 13's pitfall list are dropped for real trades and controls: UK100 2017-04-17
    (one L52 trade had -10,179 bp of quote spread) and BTC 2017-12-22.
- ATH seeds are declared public pre-2016 intraday highs (approximate for the CFD basis). They affect only the first
  ATH events of 2016-17 and JP225 / HK50 / AUS200.

## Fills (tick symbols)
| family | n | slip median / p90 (bp) | delay median | net L0 / L250 / L1000 (bp) | minute model, same trades |
|---|---|---|---|---|---|
| A (USTEC, US30, XAU, XAG) | 150 | +0.27 / +2.43 | 448 ms | -1.25 / -1.34 / -1.28 | -5.73 |
| B | 1,566 | +0.44 / +4.12 | 436 ms | -0.09 / -0.39 / -0.39 | -0.38 |

- Latency is not the constraint; cost is, as in rounds 26-28.
- The minute model is the decision model for the other eight symbols and for every placebo draw. It is unbiased
  under the null (round 28) and a lower bound when the move is fast.

## Results
Units:
- Books are at equal risk, net / the symbol's IS sd of unconditional 30-minute mid returns ("sd"); raw bp in brackets.
- t is clustered by UTC day. Power = per-trade net Sharpe x sqrt(1.73 x trades a year) at the era's own rate.
- Placebo = share of 200 shifted-level draws (same freshness rule, minute model, subsampled to the real count) below
  the real mean.
- Random = share of 200 random-armed-minute draws (side = sign of the prior 60-minute move) below the real mean.

Full lines are in `out/an_*.txt` and the bp summary in `out/summary.txt`.

| cell | n IS / VAL (a year) | mid bp IS / VAL (t) | cost bp | net IS / VAL, sd (t) [bp] | VAL/IS | Sharpe; power IS / VAL | placebo IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **A primary: records K5, all types, h30** | 267 / 133 (44 / 44) | +7.28 (2.37) / +7.99 (0.96) | 2.87 / 2.32 | +0.077 (0.66) [+4.42] / +0.101 (0.56) [+5.68] | 1.30 | 0.044 / 0.050; 0.38 / 0.44 | 0.895 / 0.985 | 0.81 / 0.85 | none |
| A H52 K5 h60 | 210 / 93 | +9.93 (2.67) / +12.25 (2.07) | 2.51 / 1.97 | +0.242 (1.72) [+7.42] / +0.319 (1.78) [+10.28] | 1.32 | 0.140 / 0.187; 1.09 / 1.37 | 0.825 / 0.950 | 0.985 / 0.960 | none (IS t, placebo) |
| A ATH K5 h60 | 152 / 55 | +10.23 (2.44) / +11.97 (2.05) | 2.54 / 0.81 | +0.176 (1.40) / +0.335 (1.87) | 1.91 | 0.121 / 0.256; 0.80 / 1.44 | 0.870 / 0.975 | 0.975 / 0.985 | none |
| A L52 K5 h30 | 34 / 33 | -1.14 / -6.23 | 3.71 / 3.63 | -0.407 (-1.11) / -0.158 (-0.38) | - | negative | 0.755 / 0.890 | 0.00 / 0.31 | none (reverses) |
| A20 (K20) all types h30 | 126 / 74 | +9.07 (1.50) / +8.53 (0.60) | 3.55 / 2.49 | -0.009 (-0.04) / +0.044 (0.16) | - | ~0 | 0.470 / 0.925 | 0.09 / 0.69 | none (dose fails) |
| A1 (K1) all types h30 | 562 / 264 (94 / 88) | +3.73 (1.80) / +2.67 (0.59) | 3.14 / 2.14 | +0.012 (0.15) / -0.015 (-0.14) | - | ~0 | 0.985 / 0.945 | 0.87 / 0.58 | none |
| A1 H52 h60 (best book net t) | 461 / 191 | +6.71 (3.04) / +4.43 (1.09) | 2.55 / 1.82 | +0.170 (**1.97**) [+4.16] / +0.157 (1.27) | 0.93 | 0.102 / 0.096; 1.17 / 1.01 | 0.910 / 0.950 | 1.00 / 0.98 | none (IS t 1.97 < 2.0) |
| A BTCUSD K5 h30 (candidate) | 9 / 15 | +142 (3.35) / +63 (0.90) | ~16 / ~11 | [+126.1 (3.17)] / [+52.5 (0.75)] | 0.42 | 1.06 / 0.19; 1.70 / 0.57 | 0.990 / 0.995 | 1.00 / 0.995 | DEMO numbers; draft not recommended |
| F FX records K5 h30 | 183 / 108 (31 / 36) | +0.67 (0.20) / -0.78 (-0.48) | 1.08 / 0.91 | -0.017 (-0.04) / -0.181 (-0.96) | - | ~0 / -0.09 | 0.510 / 0.365 | 0.53 / 0.11 | none |
| B period extremes book h30 | 2,975 / 1,510 (496 / 503) | +1.86 (1.88) / +3.03 (2.47) | 4.09 / 2.21 | -0.072 (-1.75) [-2.23] / +0.009 (0.20) | - | -0.042 / 0.005; -1.22 / 0.16 | 0.805 / 1.000 | 0.99 / 0.99 | none |
| B PM (prev. month) h30 | 648 / 339 | +2.46 (0.86) / +3.94 (1.54) | 5.16 / 2.41 | -0.050 (-0.56) / +0.056 (0.66) | - | ~0 | 0.775 / 0.965 | 0.91 / 0.975 | none |
| B EV (NFP / CPI / FOMC-day range) h30 | 2,218 / 1,098 | +1.36 (1.45) / +2.37 (1.97) | 3.65 / 2.15 | -0.085 (-2.04) / +0.004 (0.07) | - | -0.054 / 0.003 | 0.650 / 0.950 | 0.975 / 0.99 | none |
| BF FX period book h30 | 2,402 / 1,167 | +0.84 (2.39) / +1.50 (2.99) | 0.98 / 0.91 | -0.019 (-0.47) / +0.060 (0.99) | - | -0.012 / 0.033; -0.30 / 0.87 | 1.000 / 0.995 | 1.00 / 1.00 | none |
| BF FX period book h60 | 2,402 / 1,167 | +1.33 (3.33) / +2.35 (2.80) | 0.98 / 0.91 | +0.042 (0.89) / +0.168 (1.73) | 4.0 | 0.021 / 0.065; 0.55 / 1.69 | 1.000 / 1.000 | 1.00 / 1.00 | none (IS t) |
| BF USDJPY h30 (reading) | 184 / 80 | +2.93 (2.85) / +4.93 (2.42) | 0.78 / 0.74 | [+2.15 (2.09)] / [+4.19 (2.06)] | 1.95 | 0.149 / 0.227; 1.09 / 1.54 | 0.995 / 0.955 | 1.00 / 0.995 | DEMO numbers, null p 0.45: chance |
| C book (PW + MA200) h30 | 3,100 / 1,639 (517 / 546) | +2.94 (3.31) / +3.69 (3.97) | 3.90 / 2.15 | -0.027 (-0.82) / +0.047 (1.24) | - | -0.017 / 0.031; -0.50 / 0.97 | 1.000 / 1.000 | 1.00 / 1.00 | none |
| C PW (prev. week) h30 | 2,740 / 1,437 | +3.35 (3.63) / +3.71 (3.61) | 3.97 / 2.17 | -0.020 (-0.57) / +0.048 (1.17) | - | ~0 / 0.032 | 1.000 / 0.995 | 1.00 / 1.00 | none (real at mid, below cost) |
| C MA200 h30 | 360 / 202 | -0.17 / +3.57 (1.77) | 3.32 / 2.03 | -0.081 (-0.85) / +0.038 (0.41) | - | ~0 | 0.950 / 0.845 | 0.82 / 0.91 | none |
| CF FX (PW + MA200) h30 | 2,625 / 1,353 | -0.26 / +0.75 (1.81) | 0.98 / 0.89 | -0.141 (-4.58) / -0.015 (-0.30) | - | -0.079; -2.16 | 0.750 / 0.865 | 0.00 / 0.95 | none |
| PRE gold + silver records h30 | 69 (6) | +17.4 (1.89) | 3.10 | +0.560 (1.96) [+14.27 (1.55)] | - | 0.222; 0.73 | 1.000 | 1.000 | PRE only |
| PRE FX records h30 | 257 (23) | -2.59 (-1.45) | 1.11 | -0.269 (-1.80) [-3.69 (-2.06)] | - | -0.10 | 0.675 | 0.05 | fails |
| PRE period extremes h30 | 1,195 (109) | +0.71 (0.54) | 1.56 | +0.004 (0.06) | - | ~0 | 0.995 | 0.965 | fails |

Readings that are not in the table:
- **x1.5 and +1 minute** lower net by 0.03-0.08 sd. They turn no failing cell into a passing one, and they flip A1's
  small IS net (+0.012 sd) negative.
- **Without March-April 2020**, IS changes by <= 0.03 sd in the books, except L52, which gets worse (-0.41 to -0.65
  sd).
- **A primary book by year (bp):** 2016 -5.8, 2017 +3.2, 2018 -1.6, 2019 +6.7, 2020 +8.9, 2021 +10.7, 2022 -9.0,
  2023 +17.7, 2024 +7.0. Years > 0 in sd units: 3/6 IS, 2/3 VAL.
- **PRE gold + silver by year (bp):** 2005 +4.9, 2006 +23.0, 2007 +13.8, 2008 +37.7, 2009 +22.1, 2010 -2.5, 2011
  +1.6, 2013 +45.9, 2014 +22.7, 2015 -23.6.
- **Per-symbol A, K5 h30 (bp, IS / VAL):**

  | US500 | USTEC | US30 | US2000 | DE40 | UK100 | JP225 | AUS200 | HK50 | XAU | XAG | BTC |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | +4.2 / +6.4 | -1.4 / +3.2 | -1.4 / -7.2 | +8.3 / -24.0 | -1.6 / +1.2 | (glitch dropped) / -1.0 | +9.3 / +29.8 | -1.8 / -3.2 | -6.5 / +3.8 | +6.2 / +7.2 | -11.1 / -13.9 | +126 / +52 |

  n is 3-40 per cell. Only US500, JP225 and BTC are positive in both eras with t > 1.5 in one of them.

## Cells tried and chance
The sign-flip null uses one sign per UTC day, shared by all candidate cells of the pooled families; 2,000 draws
(`out/null_*.txt`).

| families | candidate cells | best IS net t (cell) | best IS mid t (cell) | null max p50 / p95 | p of best net / mid | max-of-K normals p50 / p95 |
|---|---|---|---|---|---|---|
| A + A20 + A1 | 48 | +3.17 (BTC K5 h30, n 9) | +3.35 (A1 H52 h60) | 1.85 / 3.04 | 0.036 / 0.021 | 2.45 / 3.27 |
| F | 19 | +0.98 | +1.15 | 1.54 / 2.55 | 0.89 / 0.79 | 2.10 / 2.99 |
| B + BF | 52 | +2.09 (BF USDJPY h30) | +3.40 (BF h60) | 2.03 / 2.96 | 0.45 / 0.010 | 2.48 / 3.29 |
| C + CF | 40 | +1.28 (C US2000) | +4.02 (C PW h30) | 1.96 / 2.95 | 0.93 / 0.001 | 2.38 / 3.22 |

- 159 candidate cells in all, plus per-symbol and PRE readings (~400 readings).
- **Beyond chance at mid**: continuation after a fresh salient extreme (previous week, period ranges, 52-week highs)
  is real, +1 to +7 bp over 30-60 minutes.
- **Within chance net**: the USDJPY reading. BTC's p 0.036 rests on 9 IS trades and one VAL trade.

## Correlation with C3 (IS + VAL)
| cell | daily | monthly |
|---|---|---|
| BTC K5 h30 | -0.007 | +0.008 |
| A H52 h60 book | -0.015 | -0.085 |
| BF USDJPY h30 | +0.028 | +0.110 |

## Needs the user
- **OANDA order book / position book** (an account): the only public view of where stops actually rest. It would
  test whether records hold more stops than other levels at all. Round 31's estimate stands: DEMO ~3-5 %, LIVE ~1 %.
  After this round, LIVE is lower for records specifically, because their count caps power.
- **A venue with lower index cost does not help.** At zero cost the C PW book (the strongest mid effect, t 4.0) has
  power ~2.3, and B ~1.5.
- Nothing else in this direction needs a decision.

## Untested ideas (not declared, so not candidates)
- **BTC records over a longer history** (Bitstamp / Coinbase klines from 2013, free) would give a PRE era for the only
  symbol with large record continuation. Still ~5 events a year, so DEMO at most.
- **Gold-only salient book** ($50 levels + records + previous-week extremes in one bot). Gold's B / C / record legs are
  each +1 to +7 bp with t < 1.5 in IS, so pooled power stays below 2.

## Scripts and outputs
Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r37/A/`.
Code is in `code/`; run it from the repo root with `PYTHONPATH=.:<code dir> research/.venv/bin/python`.

| script | what it does |
|---|---|
| `acommon.py` | HOLD-guarded IC / Dukascopy loaders, NY sessions, s60, armed mask, calendar, clustered t |
| `records.py` | level table (H52 / L52 / ATH, ages), first-reach engine, minute fills |
| `events.py` | per-symbol preparation (seeds, armed minutes, reach arrays) |
| `levels.py` | level specs for A / F (records), B (PM / PQ / PY / EV), C (PW / MA200) |
| `engine.py` | triggers + busy rule, minute returns, the tick model (first ASK / BID beyond the stop; 0 / 250 / 1000 ms, +1 min) |
| `run.py` | one family: events, tick refinement, 200 placebo-level draws, 200 random-time draws, overlap flags |
| `count.py` | prices-only counts |
| `analyze.py` | tables and verdicts |
| `null.py` | sign-flip null |
| `overlap.py` | P1 / Donchian / gold-$50 overlap, side and age splits, fill diagnostics |
| `summary.py` | bp summary |

Outputs are in `out/`: `count_*.txt`, `an_A.txt`, `an_B.txt`, `an_C.txt`, `an_F_PRE.txt`, `null_*.txt`,
`overlap.txt`, `summary.txt` and the per-family pickles `run_<FAM>_<SYM>.pkl`.
