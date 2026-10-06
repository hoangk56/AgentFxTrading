# Round 17 brief: quote-based order-flow imbalance, and big-day intraday momentum in European indices

Written 2026-10-06 02:39 UTC (file time; an earlier header gave a later, estimated time), before any round-17 number was computed. Same task as rounds 12-16. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/JOURNAL.md (rounds 12-16 at the top) and research/results/portfolio/round16_income_flows/STREAM_X.md (the
table of ~45 effects real at mid, with sd, cost and decay).

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| Y | order-flow imbalance from IC quotes: signed quote changes (tick rule on mid changes, Cont, Kukanov & Stoikov 2014 OFI from best bid/ask changes, quote-update intensity) over the last 1-30 minutes as a predictor of the next 1-60 minutes, in AUDUSD, NZDUSD, XAUUSD, XAGUSD, US30, USTEC, XTI (IC ticks; load only days < 2025-01-01); conditional on high-information or thin-liquidity times; sides from the literature (persistent order flow -> continuation, Hasbrouck; inventory -> reversal at short lags), fixed before looking | a state variable no round used: round 8 used price lead-lag and round 3 tick counts as volume; signed flow is the closest public proxy to the institutional orders behind every effect found so far; the question is whether its predictive part outlives the first minute and clears the cost |
| Z | intraday momentum on big-move days in European indices: the move from the cash open to a cut (e.g. 13:30 CET) predicts the rest of the cash session (to 17:30 CET), gated on the day's move being in its top decile (round 12 L4 gate) or by dose; side from Gao, Han, Li & Zhou (2018) and Baltussen et al. (2021) (continuation); DE40 is where round 13 P saw it (random windows on big days earned as much as the close window, dose slope t +3.3 IS / +4.0 VAL), so **DE40 is information only**, and the clean test is STOXX50, F40, ES35, IT40 (bid-only, published spreads, round 7 B) and UK100; also US30 / USTEC from their own open as a comparison | a hold of several hours on days when the move is large makes cost a small share of sd; the replication on other European indices is out of sample with respect to the DE40 observation; round 4 and round 8 tested intraday momentum into the US close and European morning -> US session, not big-day European sessions |

Both: HYPOTHESES_<Y|Z>.md in research/results/portfolio/round17_microstructure/ with UTC times before numbers,
STREAM_<Y|Z>.md at the end, PREREG_DRAFT_* if a rule meets LIVE or DEMO on IS/VAL. Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r17/<stream>/.
For survivors: by era and year, VAL/IS ratio, expected HOLD t on the VAL size, x1.5, both fills +1 minute (Y: +1 s,
+5 s, +30 s too), a look-ahead-free random-entry control, a shared permutation null over the family, C3 correlation,
and for Z the result with March-April 2020 removed.
