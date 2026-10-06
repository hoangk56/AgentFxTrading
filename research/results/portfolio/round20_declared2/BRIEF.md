# Round 20 brief: declared-only — central-bank-day carry, and European index expiry settlement auctions

Written 2026-10-06 03:57 UTC (from `date -u`), before any round-20 number was computed. Same task and same rule as
round 19 (read research/results/portfolio/round19_declared/BRIEF.md, "The rule of this round": every cell declared in
full before any return is computed; no scans; post-hoc findings are information only). For data, eras, costs,
constraints, bars, pitfalls, resources and what to return, follow research/results/portfolio/round13_structural/BRIEF.md.
Read research/JOURNAL.md (rounds 12-19 at the top) first.

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| F | carry on central-bank decision days: long high-interest vs short low-interest currencies over the decision day (Mueller, Tahbaz-Salehi & Vedolin 2017 for FOMC days; declare whether to extend to the other 7 banks pooled, from the paper's mechanism of monetary-policy uncertainty resolution), ranking currencies by the policy / short rates already in research/data/rates/ (causal), basket construction declared from the paper; hold across the decision (declare entry and exit times; swaps from research/swing/rates.py or the round-7 markups), with the central-bank calendar of round 10 (.../scratchpad/r12/shared/cal/cb_calendar.json) | a risk premium paid on a known day (not a flow), with an explicit side in the literature; PRE 2004-15 on Dukascopy H1 gives a third era; round 10 B and round 11 F tested direction-of-surprise drift on decision days, not carry |
| G | European index expiry settlement auctions on monthly / quarterly expiry Fridays: Xetra intraday auction 13:00 CET (DAX / DE40 final settlement), FTSE 100 EDSP intraday auction 10:15 London (UK100), EURO STOXX 50 settlement = average 11:50-12:00 CET (STOXX50), CAC 40 settlement (F40; check: average 15:40-16:00 CET), HSI settlement (average of 5-minute quotes on the penultimate business day; HK50), with the dates and rule changes from the exchanges' own documents; side from the expiration-day literature (price pressure into the settlement, reversal after: Stoll & Whaley 1987, 1991; Chow, Yung & Zhang 2003; Alkebäck & Hagelin 2004), declared before looking | binding auctions where expiry hedges are unwound; round 11 H2 tested only the US special opening quotation and round 10 A5 the Nikkei SQ open; the European and HK settlement auctions were never declared and tested |

Both: HYPOTHESES_<F|G>.md in research/results/portfolio/round20_declared2/ with `date -u` times before numbers,
STREAM_<F|G>.md at the end, PREREG_DRAFT_* if a declared rule meets LIVE or DEMO on IS/VAL (state the expected HOLD t
on the VAL size). Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r20/<stream>/.
HOLD (2025-01-01 onwards) is never loaded by the streams.
