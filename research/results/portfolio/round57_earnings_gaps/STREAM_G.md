# Round 57 stream G: large earnings gaps after the opening auction (graded on the A2 subsample: no LIVE or DEMO cell)

Written 2026-10-30 (UTC). Hypotheses: [HYPOTHESES_G.md](HYPOTHESES_G.md) (declared 12:16 UTC; counts addendum A1 12:18;
pull / sample addendum A2 12:27). HOLD stayed closed: no 2025 / 2026 file requested (asserted in the job builders),
every series cut at ts < 2025-01-01 at parse / load.

## Result (added by the coordinating session, 2026-10-30 13:25 UTC)
The pull was resumed at 3 workers (1.2-2 files/s) and stopped at 13:20 UTC by the A2 rule: 3,600 of 9,488 files,
**1,125 of 2,920 events on 374 of 1,010 reaction dates** complete (random dates, seed 573). grade.py then ran once on
that sample, unchanged. Full log: [G_out/grade.log](G_out/grade.log) (code G_out/grade.py.txt).

| cell (net bp per trade) | n IS / VAL | mid IS / VAL | net IS (t) | net VAL (t) | x1.5 / +1m (IS, VAL) | top trade share IS / VAL | yrs > 0 |
|---|---|---|---|---|---|---|---|
| primary follow all 09:45 E0 hedged | 587 / 532 | +15.8 / +16.3 | -3.2 (-0.32) | -5.7 (-0.56) | -9.6, -14.1 / -4.6, -8.6 | - | 4/8 |
| fade all 09:45 E0 hedged | 587 / 532 | -15.8 / -16.3 | -34.9 (-3.46) | -38.3 (-3.72) | all < 0 | - | 0/8 |
| follow 4-8 % down 09:45 E0 H (best IS net t) | 96 / 94 | +69.7 / -6.2 | +52.3 (2.48) | -27.8 (-1.16) | +46.2, -35.9 / +48.0, -33.9 | 0.13 / - | 5/8 |
| follow > 8 % down 09:45 E0 H | 33 / 48 | +104.3 / +50.2 | +80.2 (2.10) | +25.9 (0.64) | +72.8, +17.3 / +68.3, +16.5 | 0.18 / **0.60** | 6/7 |
| follow > 8 % both 09:45 E1 H (reported) | 68 / 92 | +92.4 / +57.7 | +66.5 (1.57) | +25.4 (0.60) | +59.0, +14.2 / +62.9, +20.7 | 0.20 / 0.53 | 6/8 |

- Chance benchmark (max IS mid t over 48 counted cells, date sign flips): median 1.88, p95 2.87; best real 3.31
  (follow 4-8 % down, P 0.021) but its VAL is negative. 2 cells have IS net t >= 2; only the > 8 % down cell is also
  VAL > 0, and **60 % of its VAL sum is one trade** (brief: no single trade > 20 %), VAL t 0.64. Neither meets DEMO.
- The random-firm control printed nan (pool legs not keyed as the code expects); it cannot change the verdict.
- Decomposition (mid, signed by the gap): the 09:45 -> 15:55 leg is +15.6 (t 1.47) IS / +20.7 (t 1.98) VAL for all
  events, but the random pool shows the same leg +14.4 / +24.1 (gap sign of random names): no earnings-specific
  continuation at the 2 % bucket. Only > 8 % gaps show more (+80.6 IS t 2.19 / +22.2 VAL t 0.88).
- Costs at 09:45 for gap firms: spread 11-16 bp a side-pair, commission 5-6 bp, hedge 0.5-2; event firms' 09:45
  spread 14.5 bp vs 10.4 for random firms.
- Power: > 8 % gaps are ~8 % of events: ~60 HOLD trades; at the VAL size and sd ~280-430 bp HOLD t < 1. LIVE out of
  reach even if the full sample confirmed the bucket.
- Concurrency: mean 3.0 events per reaction date, p95 8, max 17: 3-6 bots for the all-gap rule.
- C3 correlation (information): +0.027.

## Status
- No verdict, no results table, no PREREG_DRAFT. The stream was stopped before grading because the Dukascopy datafeed
  served ~0.1-0.7 files/s from 12:18 UTC (12-30 s per request, 30-80 % HTTP 503; no 403 / 429), against round 55's
  4.4 files/s. The declared pull (9,880 event + pool files, 5,798 placebo files) could not fit the one-hour budget.
- Counts (selection only, A1): 5,164 usable releases; 2,920 with |gap| >= 2 % (IS 1,632 / VAL 1,288), 1,010 reaction
  dates, 2.89 events per date (max 17). HOLD n at the VAL rate 743; LIVE needs VAL net Sharpe >= 0.22 per trade under
  the 1/2 rule (~55 bp at sd ~250 bp).
- A code-debug run on the first 59 cached events (2 % of the sample) printed cell values at 12:22 UTC; it is not a
  result and is not quoted (disclosed in A2).

## To resume
- Pull: `scripts/duka.py fetch out/jobs_bydate.txt --workers 6` (resume-safe cache; dates in random order, each date
  with its events and 2 random-pool names). Then `python -I scripts/parse.py` and
  `PYTHONPATH=<repo> research/.venv/bin/python scripts/grade.py` (grades only complete dates, A2 rule).
- Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r57/G/`
  (scripts/, out/ with events_g.csv, pool_g.csv, placebo_g.csv, jobs_*.txt, counts.log; cache/ with requests.log).

## Pitfalls
- The datafeed can throttle for long stretches after heavy same-day pulls (rounds 54-55 pulled ~19k files earlier
  today); more workers only raise the 503 share. Order a long pull by random date so a cut sample is still unbiased.
- Intraday releases (09:30-16:00 ET, 184) have no gap; they are excluded, not shifted to the next day.
