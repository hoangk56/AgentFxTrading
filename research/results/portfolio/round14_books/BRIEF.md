# Round 14 brief: books of stable clock effects, and conditions that double them

Written 2026-10-06 01:45 UTC (file time; an earlier header gave a later, estimated time), before any round-14 number was computed. Same task as rounds 12-13 (keep researching
until a LIVE candidate passes its holdout). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/results/portfolio/round13_structural_2026-10-06.md and round13_structural/STREAM_M.md (the stability-first
scan) and round12_flows_execution_2026-10-06.md.

## Where things stand
- LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3. At one trade a day that is a net Sharpe of ~0.145 per
  trade; E1 (short EURUSD 11:00-13:00 London) has 0.084 IS / 0.089 VAL, so LIVE needs roughly twice E1.
- Stream M of round 13 found 139 clock / calendar cells whose side was fixed in PRE 2004-15 and confirmed in IS
  (chance 29), 47 of them with VAL t >= 1.5 (chance ~9). Most are "every weekday" clock effects of 0.3-2 bp, many below
  IC's cost (break-evens 0.9-1.7 bp against 0.6-1.2 bp of cost). Their scripts and outputs (cells.npz, step*.out) are
  in /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r13/M/.
- Two weak DEMO candidates exist (E1; gold settlement big days, round 12). Do not re-optimise them; you may use E1 as a
  component or as the object of conditioning, with the multiple-testing count stated.
- HOLD 2025-01..2026-09 must stay closed for the streams (the lead registers and opens it once per candidate).

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| Q | one bot (or one algorithm of a few bots, each <= 3 positions) trading several stable clock effects in different symbols / times, chosen on PRE + IS only by a rule written before looking (e.g. every PRE-carried cell confirmed in IS with net > 0 at IS cost, non-overlapping in time per symbol, at most k per day); report the book's per-day net Sharpe in IS and VAL, its correlation structure, and the power on day-clustered units | a sum of k independent edges has Sharpe ~sqrt(k) x the average; round 10 C combined sub-cost signals inside one FX trade (fails on the commission); here each component pays its own cost but must be net > 0 on its own, and they come from 21-year-stable clocks |
| R | conditions, derived from the mechanism before looking, under which the stable clock effects (E1 first, then the other VAL-confirmed cells with the largest break-even margins) are about twice their average: weekday, ECB meeting / fix-size proxies, month-end, the euro's or the dollar's move earlier in the day or the day before, realised-vol regime only if it differs from round 10 E's construction, European holidays (with placebos), DST weeks when London-New York offsets change | E1 is net > 0 in every era at about half the LIVE size; a mechanism-based selector that keeps ~half the days at twice the edge would reach the line; round 12 L found real 2x scalings (SGE) but on effects far below cost |

Both streams: write HYPOTHESES_<Q|R>.md in research/results/portfolio/round14_books/ with UTC times before the numbers,
STREAM_<Q|R>.md there at the end, PREREG_DRAFT_* if a rule meets LIVE or DEMO on IS/VAL. Scripts and outputs under
.../scratchpad/r14/<stream>/. For every survivor: by-era and by-year effects, VAL/IS ratio, expected HOLD t on the
VAL size, x1.5, both fills +1 minute, random-entry control, chance benchmark over all cells tried, C3 correlation.
