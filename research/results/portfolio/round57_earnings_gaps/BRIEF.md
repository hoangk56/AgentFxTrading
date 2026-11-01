# Round 57 brief: large earnings gaps on US large-cap CFDs, entered after the opening auction (continuation vs fade)

Written 2026-10-30 12:35 UTC. Continues the user-approved single-stock CFD direction (2026-10-30). Research only: no
MT5 account, bot or deploy. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds 25-56 (LIVE /
DEMO in research/PROMPT.md; no RELAXED tier); fixed constraints: lot not capital-dependent, hold <= 5 days, <= 3
positions per bot (state the bots needed). Everything in research/results/portfolio/round54_single_stocks/BRIEF.md
applies (network rules incl. the Dukascopy datafeed exception with the established browser UA, HOLD cut, costs, what
to return), except the stream, the round folder (research/results/portfolio/round57_earnings_gaps/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r57/<stream>/`).

Read first: round54_single_stocks_2026-10-30.md (+ DATA_D.md, STREAM_E.md: 5,340 releases, H2 full-reaction follow from
the close was +17 / +10 bp at mid, below cost), round55_insider_intraday_2026-10-30.md (+ STREAM_M.md: the M1 pull
code in `.../scratchpad/r55/M/scripts/duka.py`, format, spread profile 09:30-10:30, halts, 503 = retry; read only),
round56_stock_cross_section_2026-10-30.md (start-day and extreme-mover cost pitfalls), round42_megacap_boj_ops/STREAM_E.md
(index-level after-hours continuation / reversal: absent). Data on disk: `.../r54/D/out/` panel and stocklib,
`.../r54/E/out/events.csv` (8-K 2.02 acceptance date / time ET per release; release before 09:30 -> reaction day = D,
after 16:00 -> D+1).

**Why this, why now:** rounds 54-56 show a stock rule at IC needs > ~20 bp per position at a mid-session or close fill.
An earnings gap is the one large-cap event with moves of several percent; the question is whether the post-09:45 part of
the reaction day continues or fades by more than the ~20-25 bp round trip. Seen before: round 54 E saw daily
open-to-close and close-based drifts (not the post-09:45 part): say so in HYPOTHESES and size HOLD at ~1/2 of VAL.

**Speed:** M1 only for the reaction day (and the next day for the hold variant) of releases whose gap is large, gap =
the reaction day's first quote / prior close from D's daily panel (|gap| >= 2 %, plus all of the top gap quintile if
that is fewer), plus a random-firm control of 2 names per reaction date; estimate the file count first and keep the pull
under ~1 hour (round 55 ran ~4.4 files/s); never a 2025 / 2026 file.

## Stream
| stream | direction | detail |
|---|---|---|
| G | **Large earnings gaps: from the first M1 bar at or after 09:45 / 10:00 ET of the reaction day, follow the gap (continuation; primary per the gap-momentum / PEAD literature) or fade it (declared alternative), exit 15:55 the same day, or 15:55 of the next 1-4 days (declared variants).** | Declared before returns: gap buckets (2-4 %, 4-8 %, > 8 %, by sign), a condition on the 09:30-09:45 move (gap extends vs retraces) as a declared variant, hedged with US500 M1 on the same minutes and unhedged. Costs: Dukascopy M1 bid / ask at the traded bars, USD 0.02 / share / side (cheap names!), financing per night. Controls: random firms same dates and minutes, non-earnings large gaps of the same size from the daily panel as a placebo only if M1 is pulled for them within the time budget, by year, ex-2020-03/04, spread x1.5, +1 minute, chance benchmark (max-t over cells), top-trade check (no single trade > 20 % of a cell's sum). Count events, power first. Concurrency: earnings season clusters, so count positions per day and bots needed. |

One stream; up to 3 heavy Python processes for the pull, 2 for grading (under ~3 GB RAM each). If a cell meets DEMO or
LIVE numbers, write PREREG_DRAFT_G_*.md (including the IC MT5 symbol check and the IC open-spread caveat) but do NOT
open HOLD.
