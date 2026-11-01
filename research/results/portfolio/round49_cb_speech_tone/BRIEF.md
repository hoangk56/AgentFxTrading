# Round 49 brief: central-bank speech text tone (Fed, ECB) on a public clock

Written 2026-10-30 08:35 UTC (round 48 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-48 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round49_cb_speech_tone/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r49/<stream>/`).
Also read the round 37-48 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-8]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com, data-api.ecb.europa.eu: check
www.ecb.europa.eu and www.federalreserve.gov separately); any row after 2024-12-31 is cut at parse or load, before
anything is printed.

**Speed (the user is waiting):** round 21 built official Fed speech / testimony calendars 2004-24 (reuse its files if
they survive; see round21_fed_events/); prefer index pages / feeds that list many speeches per request; keep the pull
under ~1 hour. Background jobs log progress, and every wait also exits when its worker dies. Grade IS + VAL as soon as
they are complete.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| T | **Hawkish / dovish tone of Fed Board and ECB speech texts -> EURUSD, USDJPY, XAU, US500 (DE40 / STOXX50 for the ECB).** Speech texts and their delivery / posting times 2010-24 (federalreserve.gov newsevents speeches; ecb.europa.eu press/key speeches; check robots.txt first). Tone fixed before any return: a declared dictionary score (state the list and its source, e.g. Apel & Blix Grimaldi 2012 hawk/dove word pairs, or Gorodnichenko, Pfajfar & Shapiro style terms), standardised against the speaker's own trailing speeches (surprise vs the speaker's usual tone), and an optional speaker weight (Chair / President / voters vs non-voters, declared). Declared families, sides fixed before returns: (1) tone surprise -> drift in the policy direction (hawkish -> currency up, gold down, index down) from the posting time + 5 / 15 minutes to the NY close and to 1 day (slow diffusion of long texts); (2) the same restricted to speeches outside blackout periods and away from scheduled data (state the filter); (3) the cross-bank difference (Fed tone minus ECB tone over a trailing week) -> EURUSD 1-5 days. Count speeches per year and do the power arithmetic first. | round 21 (Fed events: Jackson Hole, testimony, minutes as calendar events: none; tone not measured), round 25 B (scheduled events and surprises priced before release), round 26 (tick jumps at releases), round 40 G (GDELT news tone: priced before publication). No round scored central-bank speech text. | ~100-200 Board and ~150-250 ECB speeches a year give a count that event rounds lacked; text arrives on a public clock and is long, so its content may diffuse over hours (the literature finds Fed speech tone moves yields over the day). Expect most of it to be priced within minutes, as in rounds 25-26: say what is left after +15 minutes. |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each). If the first construction
fails, move to related public, dated by-products in the row (declare first), as in rounds 37-48.
