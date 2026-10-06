# Round 19 brief: declared-only hypotheses (home currency into its own fix; a second literature pass)

Written 2026-10-06 03:11 UTC (from `date -u`), before any round-19 number was computed. Same task as rounds 12-18.
Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.

**Read the round-13 brief first and follow it for everything not changed here**: research/results/portfolio/
round13_structural/BRIEF.md (data, eras, costs, constraints, bars, pitfalls, resources, what to return). Then read
research/JOURNAL.md (rounds 12-18 at the top) and research/results/portfolio/round18_decay_dom_2026-10-06.md.

## The rule of this round (from round 18)
Rules declared from a mechanism, the literature or 2004-15 kept 65-103 % of their VAL size in the holdout; picks made
after seeing the data kept 19-31 %. **So every cell in this round is declared in full (symbol, side, window, day set,
cost) in the HYPOTHESES file before any return is computed, and no scan or parameter search is run.** At most a few
pre-declared variants per hypothesis (count them). Anything found after looking is reported as information only and
cannot become a candidate this round.

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| H | the E1 mechanism in other currencies: a home currency weakens into its own reference-rate fixing during its home hours and recovers after (Ranaldo 2009; Breedon & Ranaldo 2013; Krohn, Mueller & Whelan 2024; E1 / the ECB V in rounds 10-15). Fixes to research and declare from official sources with their history of times: Bank of Canada (noon ET until 2017-02-28, then 16:30 ET daily rate), RBA (16:00 Sydney), RBNZ (around 15:00 NZ, check), SNB (none? check), Bank of England / WM/R 16:00 London for GBP, CFETS 09:15 / 16:30 Beijing for CNH, and any other on IC's symbols; JPY is excluded (C3) | E1 is the one stable structural FX effect (11/12 PRE years, IS, VAL, HOLD > 0) and its mechanism (the ECB fix) passed a mechanism check (it reverses on TARGET2 closing days); its analogues in other currencies were never declared and tested as such (round 10 A4 tested Asian fixings on AUD/NZD/USDJPY as proxies, round 10 E the WM/R and ECB fixes) |
| T | a second literature pass for intraday / short-horizon effects with an explicit side and window in the paper, on IC's symbols, not tested in rounds 3-18 (the tested lists are in round12_flows_execution/STREAM_K.md and the JOURNAL); declare each from the paper before computing; PRE wherever data exists | round 18 says literature-sided rules hold up; round 12 K mapped 30 papers and screened 6; SSRN / Semantic Scholar were partly unreachable then, so search differently (OpenAlex concepts, arXiv q-fin, central-bank and BIS working papers, journals' tables of contents) |

Both: HYPOTHESES_<H|T>.md in research/results/portfolio/round19_declared/ with `date -u` times before numbers,
STREAM_<H|T>.md at the end, PREREG_DRAFT_* if a declared rule meets LIVE or DEMO on IS/VAL (state the expected HOLD t
on the VAL size). Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r19/<stream>/.
HOLD (2025-01-01 onwards) is never loaded by the streams.
