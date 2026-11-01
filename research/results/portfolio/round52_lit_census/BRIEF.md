# Round 52 brief: census of untested mechanisms (literature 2024-26 and practitioner notes) against 51 rounds, then grade the best one

Written 2026-10-30 09:26 UTC (round 51 closed the same day: LBMA auction volume needs an account). Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds 25-51 (LIVE / DEMO in research/PROMPT.md; no
RELAXED tier). Everything in research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first,
Data, HOLD closed at 2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the
round folder (research/results/portfolio/round52_lit_census/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r52/<stream>/`).
Network rules as in rounds 37-51: **no web.archive.org**; respect robots.txt (ClaudeBot / anthropic-ai disallowed =
off limits: cftc.gov, countryeconomy.com, data-api.ecb.europa.eu); **a 403 / bot-wall is a stop, never retry with a
browser User-Agent**; no logins; never an email address in any request (OpenAlex / Crossref `mailto` included); any
row after 2024-12-31 is cut at parse or load, before anything is printed.

**Speed (the user is waiting):** the census is reading, not downloading: ~1 hour for phase 1, then grade at most one
direction (pull under ~1 hour). Share the session's web-search budget sparingly (~40 searches at most).

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| Z | **Phase 1 (census):** list mechanisms published or circulated 2024-26 (SSRN / NBER / arXiv q-fin / BIS / Fed / ECB working papers; sell-side flow notes as reported in the press) on 1-hour to 5-day returns of FX majors, gold / silver, oil, major index CFDs or BTC / ETH, plus any older mechanism not in research/PROMPT.md's "Những họ đã cạn" list and the round 31 P / round 23 / round 25 C censuses. For each: mechanism, data needed and whether it is free from this Mac (robots), first year, signals per year, the paper's size, and a **power estimate at IC cost** using the frontier table (round 10, round 25 STREAM_A). Mark each as already tested (cite the round), untestable (why), or open. Write CENSUS_Z.md, ranked by expected chance of a LIVE cell. **Phase 2:** if the top open item has an expected LIVE chance >= 2 % and free data, declare it in HYPOTHESES_Z.md (sides and parameters from the source, power first) and grade it IS / VAL as in rounds 37-51; otherwise stop after phase 1 and say so. | round 23 (2025-26 papers + sell-side flows), round 25 C (old-literature census empty), round 31 P (~1,550 community strategies), round 22 TRIAGE_R, and the exhausted list in research/PROMPT.md. This round's job is to find what all of those missed, not to re-list them. | 51 rounds have closed the obvious directions; a disciplined census against that record is the cheapest way to find a mechanism with a dated, forced flow or a public clock that no round has touched, or to show there is none left without user decisions. |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each) in phase 2.
