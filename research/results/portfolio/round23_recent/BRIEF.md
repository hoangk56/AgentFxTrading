# Round 23 brief: recent strategies and hypotheses (published or circulated 2024-2026), declared only

Written 2026-10-15 10:57 UTC (from `date -u`), before any round-23 number was computed. Same task as rounds 12-22.
Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. The user asked to "research recent strategies and hypotheses".

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/PROMPT.md (the "exhausted families" list), research/JOURNAL.md (rounds 12-22 at the top), and
research/results/portfolio/round18_decay_dom_2026-10-06.md.

## The rule of this round (from rounds 18-22)
Every cell is declared in full (symbol, side, window, day set, cost, era) in the HYPOTHESES file before any return is
computed; no scan or parameter search. At most a few pre-declared variants per hypothesis (count them). Anything found
after looking is information only and cannot become a candidate this round. The side must come from the source (paper,
mechanism, practitioner note), never from our data.

## Not again (check before declaring)
- Papers already mapped: round12_flows_execution/STREAM_K.md (Step 2, ~30 papers) and round19_declared/STREAM_T.md
  (Step 2, ~34 papers). Ideas triaged in round22_residual/TRIAGE_R.md. Families listed as exhausted in PROMPT.md may be
  retested only if the construction is clearly different; say where it differs.
- A recent mechanism whose flow only exists from 2023-24 (e.g. new NISA, 0DTE options) has no IS/VAL data under the
  fixed eras. Report it with the earliest testable date and its expected power, and put it under "needs the user"
  (it would need a new era rule or post-2026-09-24 data); do not test it on HOLD.

## Data changes since round 13's brief
- The old scratchpad (panel, calendars) is gone. The panel was rebuilt at 11:05 UTC, same layout (mid / spr / n, 26
  symbols, every minute 2016-01-01..2024-12-31, HOLD not included) at
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r23/shared/panel/
  (builder: ../build_panel.py). The minute label is the `ts` of research/data/m1; check research/m1.py for whether
  it is the bar start or end before using exact minutes.
- cb_calendar.json, releases.json and holidays.json are gone: rebuild only what a declared hypothesis needs, into
  .../r23/shared/cal/ so the other stream can reuse it.
- The disk has ~10 GB free: no extra copies of the panel or of tick data; delete big intermediates.

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| N | Newest academic literature, 2025-01 to 2026-10: journal issues (JF, JFE, RFS, JFQA, RoF, JFutM, JIMF, JBF, JEF, FRL, JFinM, IRFA) and working papers (NBER, BIS, Fed FEDS/IFDP, ECB, BoE, BoJ, SNB, CEPR, arXiv q-fin) on intraday to 5-day effects in FX, metals, energy, equity indices and crypto with an explicit side and window. Search several ways (web search, publishers' tables of contents, Crossref by date and DOI prefix, arXiv listing); log the queries. Map every candidate (source, mechanism, side, window, symbols, events/year, reported size, out-of-sample status), drop those in K/T/TRIAGE, declare and test the rest that fit IC's symbols | rounds 12 K and 19 T stopped at papers visible on 2026-10-06 and several sources were rate limited; round 18 says literature-sided rules keep 65-103 % of their VAL size |
| P | Practitioner / structural-flow hypotheses that circulated in 2023-2026 (sell-side flow notes as reported in the press, central-bank and BIS reports, market-structure papers): systematic flows whose timing and side are computable from public prices or calendars, e.g. vol-control and risk-parity de-leveraging, CTA trend-signal flips at known lookbacks, quarter-end pension rebalancing in equity indices, Japanese life-insurer / GPIF hedging calendars, buyback blackout windows, MOC imbalance at the US close, index rebalance days, gold central-bank buying, crypto ETF creation flows. For each: the rule that computes the side from public data before the trade, history of the flow's size, earliest date it existed | gotobi (C3) works because the flow's side and date are known in advance; these are the same shape, and the side comes from a published mechanism, not from our returns |

Both streams: HYPOTHESES_<N|P>.md in research/results/portfolio/round23_recent/ with `date -u` times before numbers,
STREAM_<N|P>.md at the end (with a "needs the user" section and an "untested ideas" section), PREREG_DRAFT_<stream>_*
if a declared rule meets LIVE or DEMO on IS/VAL (state the expected HOLD t on the VAL size, and the power on a
decay-adjusted size). Report each candidate's daily-return correlation with C3
(research/results/portfolio/trades_C3_gotobi_jpy_basket.csv). Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r23/<stream>/.
HOLD (2025-01-01 onwards) is never loaded by the streams. Do not edit code under research/ (scripts stay in the
scratchpad), do not commit. Two streams run at once: at most 2 heavy processes per stream.
