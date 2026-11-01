# Round 55 brief: insider-purchase day-1 drift with an intraday entry after the opening auction (single-stock CFDs)

Written 2026-10-30 10:45 UTC. Continues the user-approved single-stock CFD direction (2026-10-30). Research only: no
MT5 account, bot or deploy. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds 25-54 (LIVE /
DEMO in research/PROMPT.md; no RELAXED tier); fixed constraints: lot not capital-dependent, hold <= 5 days, <= 3
positions per bot (state the bots needed). Everything in research/results/portfolio/round54_single_stocks/BRIEF.md
applies (network rules incl. the Dukascopy datafeed exception, HOLD cut, costs, what to return), except the stream, the
round folder (research/results/portfolio/round55_insider_intraday/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r55/<stream>/`).

Read first: research/results/portfolio/round54_single_stocks_2026-10-30.md, round54_single_stocks/STREAM_I.md and
HYPOTHESES_I.md (events, CMP classification, the day-1 finding), DATA_D.md (Dukascopy format, splits, stocklib,
pitfalls), and the round 54 scratchpads (`.../scratchpad/r54/D/out/`, `.../r54/I/out/events.csv`; read only).

**Honesty about what was seen:** round 54 I saw the D+1 open-to-close mid in both IS and VAL (all buys +17.6 / +19.7
bp, CEO / CFO +46.5 / +59.3). An intraday-entry rule designed now is chosen after that look: say so in HYPOTHESES, keep
the side and families from Cohen-Malloy-Pomorski / round 54 unchanged, fix the entry offsets and exit before loading
any M1 return, and size HOLD expectations at ~1/4 of the VAL effect (round 18 rule) in the power arithmetic.

**Speed:** M1 only on the event days that matter (D+1 for each event firm, plus SPY / US500 for the hedge, plus a
random-firm control sample on the same days); keep the pull under ~1 hour; never a 2025 / 2026 file.

## Stream
| stream | direction | detail |
|---|---|---|
| M | **Long the insider-purchase firm on the first regular session after the filing date, entering after the opening auction at a normal spread, exit at the close (or the next day's close as a declared variant).** | Families unchanged from round 54 I: ALL (officer / director open-market buys), OPP, CEOCFO, CLUSTER; routine-only as placebo. Entry offsets declared before any return: e.g. 09:35, 09:45, 10:00 ET (first M1 bar at or after, at the ask), exit 15:55 ET at the bid (and D+2 15:55 as a variant); hedged with SPY or IC US500 on the same minutes, and unhedged. Costs: Dukascopy M1 bid / ask at the traded bars (report the spread profile 09:30-10:30 for event firms and the random-firm sample, by year), USD 0.02 / share / side, financing for the overnight variant. Controls: random firms from D's list on the same dates and minutes; the routine placebo; by year; ex-2020-03/04; spread x1.5; +1 minute. Count events, power first (with the 1/4 rule). Report how much of round 54's open-to-close drift is left after each offset. |

One stream; up to 3 heavy Python processes for the pull, 2 for grading (under ~3 GB RAM each). If a cell meets DEMO or
LIVE numbers, write PREREG_DRAFT_M_*.md (including the MT5 symbol check and the IC open-spread caveat) but do NOT open
HOLD.
