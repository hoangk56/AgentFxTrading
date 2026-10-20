# PREREG (round 24, forward): B3 and A1 on data after 2026-09-24 (FWD)

Registered 2026-10-16 16:14 UTC (`date -u`), before any price after 2026-09-24 was fetched or loaded. The user asked
for it on 2026-10-16 ("thử đi") after a question about rules that are strong recently but weak in the past. BTC ETF flow
rows after 2026-09-24 were not parsed either (the parser cuts at the date given).

## Why a forward log and not a HOLD
Both rules come from [STREAM_A.md](STREAM_A.md). There, each was declared before any number, but each **failed its
DISCOVERY**. They are TEST-only survivors, chosen now *because* TEST looked good. Round 18 found that picks made with
the check era in view keep ~1/4 of their size out of sample. So no tier is claimed from TEST; only data nobody has seen
can say anything, and that is data after 2026-09-24.

| rule | DISC net bp (t), n | TEST net bp (t), n | per-trade sd (TEST) | trades / yr |
|---|---|---|---|---|
| B3 long EURJPY 18:00 UTC → 00:55 fix, NISA NAV days | +1.3 (0.22), 32 | +5.1 (2.35), 34 | ~12.7 | ~27 |
| A1 BTCUSD 15:00 → 16:00 NY, side = sign of T-1 BTC ETF flow | +1.6 (0.46), 366 | +5.4 (2.07), 311 | ~45.7 | ~250 |

Known caveats carried over (STREAM_A): A1's TEST sign looks like BTC afternoon momentum rather than ETF flow (the
same-day flow oracle is −2.8 bp in TEST); B3's TEST overlaps a weak-yen regime and, before the gotobi exclusion,
27 % of NAV days were gotobi days.

## Rules (unchanged from HYPOTHESES_A.md; nothing is chosen here)
- **B3**: order days O = the 1st, 8th and (from 2024-09) 12th of each month, each rolled forward to the next day that is
  a Japanese business day (no weekend, JP holiday or 31/12-3/1) and not an NYSE holiday. F = the next Japanese business
  day after O. Same F counted once. F dropped if it is a C3 gotobi day (`swing_rules.gotobi_days`). Long EURJPY from
  18:00 UTC on the calendar day before F (Saturday/Sunday: the close of the first bar at or after the Sunday open + 5
  min) to 00:55 UTC on F. 0.6 bp commission. Swap per rollover from `research/swing/rates.py`.
- **A1**: NYSE trading days T. s = sign of the Farside "Bitcoin ETF Flow - All Data" Total of the previous NYSE trading
  day; no trade when that row is 0 or missing. BTCUSD from 15:00 to 16:00 New York time on T, side s. No commission.
- Price at clock tau = bid/ask close of the last M1 bar with tau − 10 min <= start < tau. Buy at the ask, sell at the
  bid. Variants: half spreads ×1.5; both fills +1 minute.

## Data
- Before 2026-09-25 00:00 UTC: IC M1 (`research/data/m1`), as in TEST.
- From 2026-09-25: Dukascopy M1 bid + ask (`duka_dl.py.txt`; EURJPY every day but Saturday, BTCUSD weekdays; price
  scale EURJPY 1e3, BTCUSD 10, checked on 2026-09-01 against IC before registration). Minutes with zero bid volume or
  no ask = no bar.
- Two cost readings after the cut: (a) Dukascopy's own spread; (b) **IC's median relative spread at the same UTC minute
  of day over 2026-07-01..2026-09-24** (the IC-equivalent reading; the verdict uses (b)).
- BTC ETF flows: Farside via the Internet Archive (farside.co.uk returns 403 here) and the GitHub capture used by
  stream A. Captures are merged oldest first; a date that differs between captures is reported. A FWD day whose T−1
  row is in no capture yet is skipped and counted, then picked up by a later rerun once a capture has it.

## Reproduction before registration
On the IC data (no FWD), `fwd_b3a1.py.txt` reproduces stream A exactly
([prereg_code/fwd_b3a1_repro_ic_2026-09-24.txt](prereg_code/fwd_b3a1_repro_ic_2026-09-24.txt)): B3 DISC n 32 net
+1.27, TEST n 34 net +5.10 (t 2.35), x1.5 +4.72, +1 min +4.30, years 2024 0.0 / 2025 +6.1 / 2026 +2.5. A1 DISC n 366
net +1.61, TEST n 311 net +5.36 (t 2.07), x1.5 +4.64, +1 min +3.30, years +0.7 / +4.3 / +5.5. The first draft of the
script used the quote at Sunday open + 5 min instead of the close of the first bar at or after it; B3 DISC was then
+1.04 and 2024 −0.4. It was changed to the convention above, which matches, before registration.

## Verdict rule (fixed now, on FWD only, cost (b))
Checkpoint 1: B3 at FWD n >= 30 (~13 months), A1 at FWD n >= 250 (~1 year). At a checkpoint:
- **forward-confirmed**: FWD net > 0 with t >= 2.0, and net > 0 at ×1.5 and at +1 min. Then a RELAXED demo
  PREREG_DRAFT may be written (demo only; LIVE still needs its own registered rule).
- **dropped**: FWD net <= 0.
- **open** otherwise: one more checkpoint at twice the count (B3 60, A1 500), where only confirmed (same test) or dropped
  is possible.
Two looks per rule, four in all, so a false confirmation has roughly a 5 % chance per rule; this is disclosed, not
corrected.

Expected FWD t at checkpoint 1: at the full TEST size, B3 ~2.2 and A1 ~1.8; at round 18's ~1/4 retention, ~0.55 and
~0.45. So the log can confirm only if the effect really keeps about its TEST size. Each slice before a checkpoint is
reported (n, mid, net, ×1.5, +1 min, every trade) but decides nothing.

## Code (sha256, first 16 hex; copies in prereg_code/)
- `fwd_b3a1.py.txt` 409f9df8688dbcca
- `parse_farside.py.txt` 0fba0791dce15b3e
- `duka_dl.py.txt` 48c0dcd267209d94 (unchanged from the F3/E1 forward log)

Run from the repo root (a new Dukascopy directory per slice, since the downloader skips an existing symbol-year):
```
DUKA_LAST=<last> python -I duka_dl.py.txt <dk> EURJPY:2026-2026 4 8-12 all
DUKA_LAST=<last> python -I duka_dl.py.txt <dk> BTCUSD:2026-2026 4 8-12 wd
python -I parse_farside.py.txt flows.csv <last> gh_2026-09-08.html ia_<capture>.html ...
PYTHONPATH=. research/.venv/bin/python fwd_b3a1.py <last> --duka <dk> --spread ic --flows flows.csv
PYTHONPATH=. research/.venv/bin/python fwd_b3a1.py <last> --duka <dk> --spread duka --flows flows.csv
```

## FWD result
(appended after each run, below this line; nothing above edited)

### Slice 1: FWD 2026-09-25..2026-10-15 (run 2026-10-16 16:17 UTC)
Dukascopy fetched 16:14-16:17 UTC (EURJPY every day but Saturday, BTCUSD weekdays, 2026-08-01..2026-10-15; no day
missing). BTC ETF flows: the 2026-09-08 GitHub capture plus Internet Archive captures of 2026-10-01 03:51, 2026-10-02
14:14 and 2026-10-10 23:32 UTC; 705 rows to 2026-10-09, no clash between captures. Saved as
[prereg_code/btc_etf_flows_to_2026-10-15.csv](prereg_code/btc_etf_flows_to_2026-10-15.csv). Code unchanged (`cmp`
against prereg_code/). Output: [prereg_code/fwd_b3a1_output_2026-10-15.txt](prereg_code/fwd_b3a1_output_2026-10-15.txt).

Calibration on 2026-08-03..09-24, before FWD (information only;
[calib_b3a1.py.txt](prereg_code/calib_b3a1.py.txt), [output](prereg_code/calib_b3a1_output_2026-10-15.txt)): EURJPY
median |mid difference| 0.05 bp, rule-window return correlation 0.9999 (n 38); BTCUSD 2.62 bp, correlation 0.993,
median |window difference| 2.1 bp (small against A1's ~46 bp per-trade sd). Dukascopy's BTC spread is ~10x IC's
(6.5 bp vs 0.6 bp median), so reading (a) is much more conservative for A1.

| rule | era | n | mid | net (b) IC spread | net (a) Duka spread | x1.5 (b) | +1 min (b) |
|---|---|---|---|---|---|---|---|
| B3 | FWD | 2 | +11.66 | +10.89 | +10.88 | +10.67 | +10.65 |
| A1 | FWD | 12 | -5.48 (t -0.56) | -7.32 (t -0.75) | -11.44 (t -1.17) | -8.25 | -7.67 |

- B3 traded 2026-10-02 (order day 1 October) +10.6 bp and 2026-10-14 (order day 12 October, a JP holiday, rolled to the
  13th) +11.2. The 8 October order day maps to 9 October, a gotobi Friday, and was dropped.
- A1 (b): 09-25 L +3.6, 09-28 L -81.8, 09-29 L -7.0, 09-30 L -42.9, 10-01 S +12.3, 10-02 L +3.4, 10-05 L +5.0, 10-06 S
  -14.2, 10-07 L +1.0, 10-08 S -35.3, 10-09 S +15.3, 10-12 L +52.6. 13-15 October wait for a capture with the 12-14
  October rows (3 days counted as "no flow row").
- Reading: nothing. B3 has 2 of the 30 trades its checkpoint needs, A1 12 of 250; one A1 trade (-81.8) is larger than
  the slice's mean x n. Next rerun: when a newer Farside capture exists, with a new Dukascopy directory.
