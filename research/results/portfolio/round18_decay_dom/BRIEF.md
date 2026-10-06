# Round 18 brief: which effects do not decay, and calendar day-of-month clocks

Written 2026-10-06 02:55 UTC (from `date -u`), before any round-18 number was computed. Same task
as rounds 12-17. Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/JOURNAL.md (rounds 12-17 at the top), research/PROMPT.md (current diagnosis, Vietnamese) and
research/results/portfolio/round16_income_flows/STREAM_X.md (the table of ~45 effects real at mid). Take every
timestamp you write from `date -u`.

## Streams
| stream | direction | why it matters |
|---|---|---|
| A | decay forensics: for each effect in STREAM_X's table (and C3 as the reference: its trade list is research/results/portfolio/trades_C3_gotobi_jpy_basket.csv, IS+VAL rows only), rebuild the yearly mid effect 2016-2024 (and 2004-15 where Dukascopy covers the symbol), fit the trend (bp per year, and the ratio of the last 3 years to the first 3), test for a structural break, and give a decay-adjusted forecast of its 2025-26 size with an interval; then rank the effects by forecast net Sharpe at IC's costs and at the venue costs of STREAM_X; say which effects look gotobi-like (flat) and whether that predicts which registered rules held in HOLD (C3 0.88, E1 0.65, gold big days 0.81, J5c 0.31, I ~0, M1 0.19) | the round-12 lesson is that decay decides; a flat-trend effect is the only kind that a holdout or a demo can confirm; this tells the user which demo, if any, is worth running and whether any effect deserves a fresh pre-registration with a decay-adjusted bar |
| B | calendar day-of-month (1-31, and "n-th last calendar day") x clock windows (15 min - 4 h, DST-aware local clocks) for FX and gold, discovery on PRE 2004-15 (side fixed there), confirmation on IS and VAL, as round 13 M did for business-day types; exclude JPY pairs entirely on gotobi days (5, 10, 15, 20, 25, 30, last day) and the Tokyo-fix hours on all days (C3), and report separately any non-JPY effect on gotobi days as C3-related information only | round 13 M's 28 day types used business-day-of-month and month/quarter ends, not calendar days; corporate payment practices (paydays, payment terms, "5/10" style settlement in other countries) are set on calendar days; the last unscanned calendar dimension on the existing data |

Both: HYPOTHESES_<A|B>.md (A may state it computes from existing returns, but it does load prices to rebuild yearly
effects, so it writes hypotheses for its trend tests first) in research/results/portfolio/round18_decay_dom/, with UTC
times before numbers; STREAM_<A|B>.md at the end; PREREG_DRAFT_* if a rule meets LIVE or DEMO on IS/VAL. Scripts and
outputs under /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r18/<stream>/.
HOLD (2025-01-01 onwards) is never loaded by the streams; the 2025-26 HOLD readings that are already published (the
registered rules' HOLD results in the PREREG files) may be used by A as published numbers only.
