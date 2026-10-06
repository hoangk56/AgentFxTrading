# Round 15 brief: very short windows (1-14 minutes) at stable benchmark minutes

Written 2026-10-06 02:01 UTC (file time; an earlier header gave a later, estimated time), before any round-15 number was computed. Same task as rounds 12-14 (keep researching
until a LIVE candidate passes its holdout). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
round14_books_2026-10-06.md, round13_structural_2026-10-06.md with round13_structural/STREAM_M.md, and
round12_flows_execution/STREAM_J.md (which already did second-level entry/exit timing for the SGE auction, the Sydney
open, the ECB fix, the USTEC MOC window, the AUS200 close and the gold settlement: do not redo those cells).

## Why this direction
LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3, i.e. ~0.145 at one trade a day. For a window of length w the
required mid edge is cost + 0.145 x sd(w). sd shrinks with sqrt(w) (EURUSD ~5.4 bp at 15 min, ~2.4 at 3 min, ~1.4 at
1 min) while the cost per round trip does not, so a short window only helps if the flow is concentrated in a few
minutes, which is how fixing / auction flows behave (the ECB V sits in 12:45-13:15 London; round 10 found the SGE move
in its 8 auction minutes). Rounds 4 (48k benchmark cells) and 13 (270k cells) scanned windows of 15 minutes and more;
nobody scanned 1-14-minute windows systematically. Required mid edge, one trade a day: EURUSD at 0.63 bp cost about
0.83 bp at 1 min, 0.98 at 3 min, 1.13 at 5 min, 1.3 at 10 min; scale for other symbols with the frontier table
(round10_new_directions/STREAM_D_outputs.md). Spreads widen at some benchmark minutes: always use the actual spread
of the entry and exit minute (ticks where they exist).

## Streams
| stream | scope | design |
|---|---|---|
| S | FX with PRE M1: EURUSD, USDCHF (all hours), USDJPY / EURJPY / GBPJPY (excluding 23:00-02:00 UTC, C3's Tokyo-fix territory, and gotobi day types) | discovery on PRE 2004-15 Dukascopy M1, side fixed there, confirmation on IS and VAL (as round 13 M). Cells: every window of length 1, 2, 3, 5, 10 minutes starting at each minute within +-30 minutes of declared benchmark minutes (ECB 14:15 CET reference rate, WM/R 16:00 London, 10:00 New York option cut, 15:00 Tokyo option cut, London 08:00 and Frankfurt 09:00 CET opens, US 08:30 / 10:00 ET data minutes on all days, CME 14:00/15:00 ET closes of FX futures), DST-aware, day types: every weekday, by weekday, month-end; plus an unrestricted scan of all 1-5-minute windows of the day for EURUSD as a control on how special the benchmark minutes are |
| V | symbols with IC ticks or M1 but no PRE minute data: XAUUSD, XAGUSD, AUDUSD, NZDUSD, US30, USTEC (ticks), DE40, UK100, JP225, HK50, AUS200, US500, XTI (M1) | IS discovery / VAL check (side fixed by IS sign only if a mechanism predicts it; otherwise the cell is information only). Benchmark minutes not covered by round 12 J: LBMA gold auctions 10:30 / 15:00 London, LBMA silver 12:00, COMEX gold open 08:20 ET, NYMEX oil open 09:00 ET and settlement minute, cash opens and closes of NYSE (09:30 / 16:00), Xetra (09:00 / 17:30 CET), LSE (08:00 / 16:30), TSE (09:00 / 15:00 JST, 15:30 from 2024-11-05), HKEX (09:30 / 16:00), ASX (10:00 / 16:10), Sydney 10:00 for AUD/NZD only outside the cells J did, 08:30 / 10:00 ET data minutes; windows of 1, 2, 3, 5, 10 minutes starting within +-20 minutes of each |

Both streams: write HYPOTHESES_<S|V>.md in research/results/portfolio/round15_short_windows/ with UTC times before the
numbers (`date -u`), STREAM_<S|V>.md there at the end, PREREG_DRAFT_* if a rule meets LIVE or DEMO on IS/VAL. Scripts
and outputs under /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r15/<stream>/.
Per cell: mid bp and day-clustered t by era, cost at those minutes, net, per-trade net Sharpe, power on the IS and the
VAL size, VAL/IS ratio. Chance: a permutation null that flips the sign of each date, shared by all cells of a stream,
for the max |t| at the discovery step and the number of confirmations at the next. Survivors: by year, x1.5, both
fills +1 minute (and +10 s / +30 s where ticks exist: a 3-minute window is very sensitive to latency), a random-entry
control, C3 correlation. Overlap with E1 / the ECB slot must be stated (a 12:45-13:00 London cell is part of E1).
