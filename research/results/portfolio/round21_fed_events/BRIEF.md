# Round 21 brief: declared-only — the FOMC-day dollar premium on other scheduled US-policy uncertainty events

Written 2026-10-06 04:14 UTC (from `date -u`), before any round-21 number was computed. Same task and same rule as
rounds 19-20 (research/results/portfolio/round19_declared/BRIEF.md, "The rule of this round": every cell declared in
full before any return is computed; no scans; post-hoc findings are information only). For data, eras, costs,
constraints, bars, pitfalls, resources and what to return, follow research/results/portfolio/round13_structural/BRIEF.md.
Read research/JOURNAL.md (rounds 12-20 at the top) and research/results/portfolio/round20_declared2/STREAM_F.md first.

## Stream
| stream | direction | why it might escape the limits |
|---|---|---|
| U | round 20 F's A4 rule (long the currencies whose rate is above USD's, against USD, 16:00 ET the day before to 16:00 ET on the event day; Mueller, Tahbaz-Salehi & Vedolin 2017: a premium for bearing monetary-policy uncertainty, resolved on the announcement) applied unchanged to other scheduled US-policy uncertainty events, declared one by one with their mechanism before looking: FOMC minutes releases, the Fed Chair's semi-annual monetary-policy testimony, the Jackson Hole Chair speech, the Treasury's quarterly refunding announcement, and any other scheduled Fed event the literature ties to policy uncertainty (cite it); events pooled with FOMC as a declared second cell; gold (long XAUUSD over the same window) as a declared extra leg; PRE 2004-15 (Dukascopy H1, BIS / FRED rates as round 20 F) | A4 is durable across 2004-24 (pooled t 3.25) but has 8 events a year; if the mechanism is the resolution of Fed uncertainty, the same premium should appear on the other scheduled Fed events, raising the count to ~25-30 a year without a new parameter; round 10 B4a tested only direction-of-surprise drift after FOMC minutes |

Write HYPOTHESES_U.md (with `date -u` times) before numbers, STREAM_U.md at the end, PREREG_DRAFT_U_* if a declared rule
meets LIVE or DEMO on IS/VAL (state the expected HOLD t on the VAL size), all in research/results/portfolio/round21_fed_events/.
Reuse round 20 F's code (.../scratchpad/r20/F/flib.py, run.py; read them first). Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r21/U/.
HOLD (2025-01-01 onwards) is never loaded by the stream.
