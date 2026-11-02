# Round 67: scheduled releases traded within seconds (P, R2), 2026-11-01

Shared brief: [round67_fix_seconds/BRIEF.md](round67_fix_seconds/BRIEF.md) (14:51 UTC). The coordinator also built the
public-data forward log for A2-D5L ([PREREG_A2_D5L](round65_retail_venues/A2/PREREG_A2_D5L.md), `coord/forward/fwd_a2.py`).

## Answer first
- **No LIVE or DEMO candidate.**
- P: the PBoC central-parity surprise moves USDCNH the right way at mid (IS gross +0.5..+1.5 bp, t 2.5-4.7), but the move
  starts only ~20 s after 01:15:00 and the IC round trip is 1.3-1.7 bp: every cell is net <= 0 in IS and VAL.
- R2: Upbit-heavy altcoins fall from an Upbit KRW-listing notice to the KRW open (Korean retail rotating into the new
  coin). VAL is strong (BTC-hedged, exit at L: +71 bp per notice, t 3.96, power 3.09, random 100 %), but IS fails
  (t 0.74, 9 notices, 6 posted at the open so the trade only pays costs). Not registrable without lowering the IS bar.

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| P | PBoC USD/CNY central-parity surprise -> USDCNH within seconds of 01:15 UTC (SAFE's official parity, IC ticks) | none: best k15_d5_h30 IS -0.13 bp (t -0.24), VAL -0.04; 82 % of the 30-min move done by 6 min; VAL has no 6-min reaction after 30 s | [STREAM_P.md](round67_fix_seconds/P/STREAM_P.md) |
| R2 | Short Upbit-heavy alts (top tercile by Upbit share) vs BTC from an Upbit KRW-listing notice to the KRW open | none on the bars: IS +77 bp (t 0.74, n 9), VAL +71 (t 3.96, n 32), 4/5 years, power 3.09 at VAL size | [STREAM_R2.md](round67_fix_seconds/R2/STREAM_R2.md) |

## What a user decision could unlock
- R2 BTC-L could be registered for HOLD only with an explicit exception to the IS bar (IS has 9 notices, 3 with a
  window). The research rule says never lower a bar, so it is not registered; an Upbit-notice bot (A2-D5L) could log
  R2 alongside as a forward-only observation.

## Pitfalls
- SAFE's RMB central-parity query (www.safe.gov.cn/AppStructured/hlw/RMBQuery.do, robots 404) serves the official
  parity by year; pbc.gov.cn disallows all, chinamoney needs a robot-check key. The default view shows HOLD-era fixes.
- The fix-to-CNH gap drifted from -16 bp (2022) to -138 bp (2024): a trailing-median surprise proxy weakens.
- Upbit's notice list keeps old pinned notices on the first pages: a "stop when a page is older than X" loop must use
  the newest notice of the page, not the oldest (bug found and fixed in fwd_a2.py before its first real run).

## Standing after round 67
C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L (public-data forward log running).
Forward-registered LIVE candidate: F0.
