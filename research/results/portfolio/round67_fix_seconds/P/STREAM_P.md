# Stream P (round 67): PBoC central-parity surprise, USDCNH within seconds of 01:15 UTC

Written 2026-11-01 15:03 UTC. Hypotheses and the 8 cells: [HYPOTHESES_P.md](HYPOTHESES_P.md), 15:00 UTC, before
any signed return. HOLD was never loaded: fixes requested only up to 2024-12-31, ticks read to 2024-12-31, a
`d < 2025-01-01` assert in the loader.

## Answer
- **No LIVE and no DEMO cell. No PREREG_DRAFT.** All 8 declared cells are net < 0 in IS and in VAL.
- **The surprise is real at mid in IS, but small next to the cost.** Gross mid is +0.5..+1.5 bp a trade (IS t 2.5-4.7).
  The round trip at these moments is 1.5-1.7 bp in IS and 1.3-1.4 bp in VAL (spread 0.9-1.1 + commission 0.6).
  The spread is at its widest of the day at +5 / +30 s.
- **VAL has no 6-minute reaction.** After 30 s the 6-minute move is about 0 or negative: k15 d30 h6 VAL gross is
  -0.15 bp. A 30-minute drift remains, +0.8..+1.3 bp gross (t 1.7-2.6), which is still below cost.
- **Distance from the bars.** For IS net t 2.0, a cell would need a round trip of at most 0.1-0.56 bp. For power 3 at
  VAL size, the needed cost is negative: impossible at any venue.

## Data
- **Fix.** SAFE, the official RMB central-parity query at `www.safe.gov.cn/AppStructured/hlw/RMBQuery.do`:
  - one POST per year, 2015-07-01..2024-12-31, giving 2,313 fixes (USD column / 100);
  - robots.txt answers 404, so there is no restriction; plain UA, no account, no e-mail;
  - 16 requests in all, logged in `research/data/cny_fix/requests.log`;
  - 3 POSTs got "connection reset" and were retried later, one at a time.
  - Spot checks match the published history: 2015-08-11 6.2298, 2016-01-07 6.5646.
- **Not used:**
  - chinamoney.com.cn: robots.txt 404, but the data sit behind a robot-check key (round 36);
  - pbc.gov.cn: robots `Disallow: /` (round 36).
- **The bare GET of the query page shows the latest fixes (2026, i.e. HOLD).** Its body was deleted unread; only
  the log line remains.
- **USDCNH ticks.** IC t1 2016-24, loaded one day at a time (round 30 decoder). Of 2,190 fix days in 2016-24, 2,180
  have ticks (weekend make-up days have none). Valid s: IS 1,446 days, VAL 724.

## Release time on the tape
Source: `out/release_time.txt`, unsigned activity per second, all weekdays.
- |mid change| per second is flat until 01:15:00, with a small bump at 0..+2 s from 2019.
- Then comes a step:
  - at about +13..+15 s in 2019-24 (0.05-0.09 rising to 0.2-0.4 bp per second);
  - later in 2016-18 (+20..+32 s).
- Tick counts spike on 5-s marks (-5, 0, +15 s), which looks like IC quote batching.
- **The signed move towards the fix starts only after +20 s.** In IS, 17 % of the 0 -> 30 min move is done by
  +30 s, 60 % by +60 s and 82 % by +6 min.
- So d = 5 s enters before the market reacts, but only if a feed delivers the fix by 01:15:05. That cannot be
  checked here (the timing of the chinamoney release is behind its robot check). d = 30 s is the realistic bot.

## Path by surprise bucket (IS 2016-21, side-signed mid change in bp from the pre-01:15 mid; `out/path_IS.txt`)
s = ln(fix / CNH mid at 01:14:59.9) minus the trailing 20-day median of that gap.

| bucket | n | mean s | +5 s | +15 s | +30 s | +60 s | +2 min | +6 min | +15 min | +30 min |
|---|---|---|---|---|---|---|---|---|---|---|
| s <= -15 | 244 | -33.2 | -0.02 | +0.10 | +0.21 | +0.69 | +0.93 | +1.07 (t 2.6) | +1.17 | +1.50 |
| -15 < s <= -5 | 284 | -9.4 | -0.01 | +0.05 | +0.16 | +0.49 | +0.46 | +0.37 | +0.32 | +0.45 |
| \|s\| < 5 | 374 | 0.0 | 0.00 | -0.03 | 0.00 | +0.10 | +0.16 | +0.04 | +0.06 | -0.17 |
| 5 <= s < 15 | 292 | +9.4 | -0.02 | 0.00 | +0.12 | +0.23 | +0.31 | +0.29 | -0.11 | +0.06 |
| s >= 15 | 252 | +33.4 | +0.02 | -0.03 | +0.09 | +0.66 | +0.85 | +1.10 (t 3.4) | +1.14 | +1.52 |

- **Size of the effect.** A 33 bp surprise moves CNH about 1 bp. The IS slope is +3.1 bp per 100 bp of s
  (corr 0.16).
- **VAL, information computed after the cells.**
  - The slope is +0.24 bp per 100 bp of s.
  - The \|s\| >= 15 path is +0.33 at +30 s, +0.18 at +6 min and +1.18 at +30 min (`out/path_VAL_info.txt`).
- **Why s is a poor proxy in VAL.** The fix-to-CNH gap became large and persistent: its median is -16 / -35 / -138 bp
  in 2022 / 23 / 24, against about -3..-17 in IS. Changes in the counter-cyclical gap are mostly policy, not news
  the market didn't expect.

## Declared cells (`out/cells.txt`)
Notes on the table:
- bp per trade, one trade a day, so t is day-clustered.
- Cost = actual half-spreads at the entry and exit ticks + 0.6 bp commission.
- "rand" = % of 1,000 random draws (same n, random eligible days of the era, random side) that the net beats.
- "late" = both fills +60 s.

| cell | era | n | gross mid (t) | cost | net (t) | sd | Sharpe/trade | x1.5 | +60 s late | rand % | years net > 0 | power at VAL size |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k5_d5_h6 | IS | 1,067 | +0.69 (4.58) | 1.56 | -0.87 (-5.81) | 4.91 | -0.18 | -1.65 | -1.34 | 100 | 0/6 | |
| | VAL | 624 | +0.23 (1.00) | 1.30 | -1.07 (-4.68) | 5.74 | -0.19 | -1.73 | -1.16 | 84 | 0/3 | -3.69 |
| k5_d5_h30 | IS | 1,069 | +0.84 (2.74) | 1.54 | -0.70 (-2.27) | 10.05 | -0.07 | -1.47 | -1.07 | 100 | 1/6 | |
| | VAL | 624 | +1.06 (2.59) | 1.28 | -0.23 (-0.56) | 10.20 | -0.02 | -0.87 | -0.30 | 100 | 1/3 | -0.44 |
| k5_d30_h6 | IS | 1,068 | +0.54 (4.29) | 1.54 | -1.01 (-7.93) | 4.15 | -0.24 | -1.78 | -1.40 | 100 | 0/6 | |
| | VAL | 624 | -0.04 (-0.22) | 1.33 | -1.36 (-8.34) | 4.08 | -0.33 | -2.03 | -1.04 | 35 | 0/3 | -6.57 |
| k5_d30_h30 | IS | 1,070 | +0.69 (2.46) | 1.52 | -0.83 (-2.90) | 9.34 | -0.09 | -1.59 | -1.13 | 99 | 2/6 | |
| | VAL | 624 | +0.79 (2.12) | 1.31 | -0.52 (-1.37) | 9.37 | -0.06 | -1.17 | -0.19 | 99 | 0/3 | -1.08 |
| k15_d5_h6 | IS | 494 | +1.08 (4.11) | 1.66 | -0.57 (-2.18) | 5.84 | -0.10 | -1.40 | -1.22 | 100 | 0/6 | |
| | VAL | 411 | +0.28 (0.88) | 1.33 | -1.06 (-3.33) | 6.44 | -0.16 | -1.72 | -1.33 | 81 | 0/3 | -2.62 |
| k15_d5_h30 | IS | 495 | +1.50 (2.69) | 1.64 | -0.13 (-0.24) | 12.46 | -0.01 | -0.95 | -0.65 | 100 | 3/6 | |
| | VAL | 411 | +1.27 (2.33) | 1.31 | -0.04 (-0.07) | 11.13 | -0.00 | -0.70 | -0.32 | 99 | 2/3 | -0.06 |
| k15_d30_h6 | IS | 494 | +0.95 (4.65) | 1.64 | -0.68 (-3.30) | 4.60 | -0.15 | -1.50 | -1.31 | 100 | 0/6 | |
| | VAL | 411 | -0.15 (-0.71) | 1.37 | -1.53 (-6.98) | 4.43 | -0.35 | -2.21 | -1.14 | 14 | 0/3 | -5.51 |
| k15_d30_h30 | IS | 495 | +1.37 (2.76) | 1.62 | -0.25 (-0.49) | 11.27 | -0.02 | -1.05 | -0.74 | 100 | 3/6 | |
| | VAL | 411 | +0.84 (1.72) | 1.35 | -0.51 (-1.03) | 9.99 | -0.05 | -1.18 | -0.13 | 96 | 0/3 | -0.81 |

- **Years.** By year, every cell is negative in 2016-18. The k15 30-minute cells are positive in 2019-21, when the IS
  spread was 0.2-0.5 bp. Detail is in `out/cells.txt`.
- **Latency.** +250 ms changes net by <= 0.01 bp. Both fills +30 s are reported in `out/cells.txt`.
- **Random benchmark.** "rand 100 %" only says the cell beats random days with random sides, which lose the full
  cost. It does not make the cell profitable.
- **Family check.** The max IS gross-mid t over the 8 cells is 4.65, against a shared sign-flip null p95 of 2.23
  (p < 0.001). The direction carries information. The net does not survive.
- **Most favourable cell.** k15_d5_h30 has VAL net -0.04 (t -0.07). It is still negative and needs a fix feed
  within 5 s.
- **C3 correlation.** Not computed: no cell has DEMO numbers.

## What failed and why
- **Cost against the move.** The informative move is about 1 bp for a 30 bp surprise. It sits at the minute when
  IC's CNH spread is widest (0.4-0.9 bp from 2017, 2.8 in 2016) and pays 0.6 bp of commission on top.
- **No early edge to take.** The first 20 s carry nothing signed, so being fast does not help. By +60 s most of the
  6-minute move is done.
- **VAL loses the 6-minute leg.** The surprise proxy (gap to a trailing median) degrades in 2022-24 because the
  counter-cyclical gap widened to -138 bp in 2024.
- **A better expectation model would not rescue this.** For example, the previous close plus the basket overnight.
  Even a perfect proxy's IS gross would need to more than double to reach DEMO at IC's cost. LIVE is impossible at
  any cost at VAL size.

## Pitfalls
- **SAFE server.** It resets some POSTs; retry one at a time.
- **The query page's default view shows the newest fixes (HOLD).** Never fetch it without dates.
- **Weekend make-up working days** have fixes but no IC ticks.
- **IC timestamps.** They cluster on 5-s marks, and the visible reaction starts 13-30 s after 01:15:00 depending on
  the year. "01:15 + 5 s" is therefore before the IC market moves.

## What a user decision could unlock
Nothing worth it:
- a venue with a CNH round trip below ~0.4 bp at 01:15 would at most reach DEMO in IS, on a cell that does not net
  positive in VAL;
- LIVE is out of reach.

## Files
- `P/HYPOTHESES_P.md`, `P/STREAM_P.md`.
- `P/code/`:
  - `fetch.py`: logged, polite fetcher;
  - `parse_safe.py`;
  - `plib.py`: day-by-day tick loader with HOLD guard;
  - `release_time.py`, `spread_check.py`: data checks;
  - `build.py`: per-day quote table;
  - `analyze.py`: path and cells.
- `P/out/`: release_time.txt, spread_check.txt, path_IS.txt, cells.txt, path_VAL_info.txt.
- `research/data/cny_fix/`:
  - requests.log;
  - raw/ (SAFE pages, robots bodies);
  - usdcny_fix.csv;
  - cache/days.npz and cell_trades.npz (small; outside results/).
