# Round 16 brief: cross-border income conversion flows, and what each pending user decision would unlock

Written 2026-10-06 02:17 UTC (file time; an earlier header gave a later, estimated time), before any round-16 number was computed. Same task as rounds 12-15. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/JOURNAL.md (rounds 12-15 at the top) and research/PROMPT.md (the current diagnosis, in Vietnamese).

## Where things stand after 15 rounds
Hundreds of clock / calendar / benchmark effects are real at mid, beyond chance, in IS and VAL; they are 0.3-2.7 bp
per trade against IC's 0.6-7 bp round trips, and most shrink from IS to VAL to HOLD. Two weak DEMO candidates (E1
EURUSD 11:00-13:00 London short; gold into the COMEX settlement on big days) await the user. The binding constraint is
IC's cost, not the absence of effects. Two directions follow:

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| W | cross-border income conversion flows with known dates and direction: dividend payment seasons (e.g. Japanese companies late June / early December, European April-May, Australian Feb-Mar / Aug-Sep, UK, Swiss April; foreign holders convert or repatriate), US Treasury coupon payment dates (15th and month-end; foreign holders' conversion), large bond redemption dates (e.g. JGB redemptions on the 20th of Mar/Jun/Sep/Dec, Bund / OAT / BTP redemption dates) and their reinvestment, at 1-5-day horizons where cost is a small share of sd, and at the fix minutes where the conversion is executed | a different kind of mechanism from the clock / calendar flows scanned so far: the size is set by published payout and redemption schedules, the side by who receives the cash; rounds 3-15 tested month-end, turn of month, tax and settlement dates, fiscal-year ends, not income conversion; C3 owns gotobi and the Tokyo fix, so JPY cells must avoid both (state how) |
| X | decision value: for every effect that rounds 3-15 found real at mid in IS and VAL (collect them from the round reports and STREAM files, with their mid, cost, sd, trade count and VAL/IS ratio), compute the per-trade net Sharpe and LIVE power under the cost structures the user could choose: (a) today's IC costs applied to IS as well (a bar change, report only), (b) no FX/metals commission, (c) half the spread, (d) a lower-cost venue at a stated round trip; and what new symbols / data (Dukascopy M1 2004-15 for more symbols, IC symbols not yet pulled, data after 2026-09-24) would test, with the expected power. No new screens of returns: only arithmetic on the numbers already found, plus the decay-adjusted (VAL-size) power | the user has several pending decisions; a table of "what each one unlocks, at what expected power" lets them choose; this is not a candidate search and cannot produce one |

W writes HYPOTHESES_W.md (UTC times before numbers), STREAM_W.md and PREREG_DRAFT_* if a rule meets LIVE or DEMO on
IS/VAL; X writes STREAM_X.md (no hypotheses file needed: it computes no new returns; say so). All in
research/results/portfolio/round16_income_flows/. Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r16/<stream>/.
