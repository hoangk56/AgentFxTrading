# Round 46 brief: balanced-fund / pension rebalancing and risk-parity de-leveraging with the bond leg

Written 2026-10-30 07:45 UTC (round 45 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-45 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round46_rebalancing_bond_leg/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r46/<stream>/`).
Also read the round 37-45 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-5]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com); any row after 2024-12-31 is cut at
parse or load, before anything is printed.

**Speed (the user is waiting):** reuse files already on disk first (round 9 found a US Treasury yield-curve source;
round 41 parsed MoF JGB and Finanzagentur files); keep any new pull under ~1 hour (yield files are small). Background
jobs log progress, and every wait also exits when its worker dies. Grade IS + VAL as soon as they are complete.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| P | **Rebalancing flows computed with the bond leg -> US500, USTEC, US30 (JP225 / DE40 with JGB / Bund legs as a second family, USDJPY / EURUSD as controls).** Daily government yields 2004-24 (US Treasury daily par yield curve, home.treasury.gov or the round 9 source; MoF JGB historical yields; Bundesbank or ECB yield curve; check robots.txt first) -> approximate daily 10-year (and 2-/30-year) bond total returns from yield changes and duration. Declared families, sides and parameters fixed from the literature before any return: (1) Harvey, Mazzoleni & Melone, NBER w33554 (2025): threshold-rebalancing pressure of a 60/40 fund = the drift of the equity weight away from 60 % since the last rebalance, computed from stock and bond returns (the paper's construction, stated in full in HYPOTHESES_P.md with the paper's threshold and its "-16 bp per sd next day" size), side: equity overweight -> short the index next day, and the calendar (month-end) variant; (2) risk-parity / vol-target de-leveraging: trailing stock-bond correlation and realised vol of a 2-asset risk-parity book (declared windows, e.g. 20 / 60 days); a jump in the book's target leverage cut -> short equity next 1-3 days; (3) same constructions for Japan (TOPIX/JP225 vs JGB 10y, GPIF-style 25/25/25/25 is out: undisclosed dates) and Germany (DE40 vs Bund). Entry at the next cash open or the IC session after the signal is computable (yields published after the US close: state the time), hold 1-3 days. Count signal days and do the power arithmetic first (it is a daily signal: say what per-day Sharpe LIVE needs). | round 23 P (HMM equity-only proxy: IS +0.9 bp mid, VAL -0.2; the bond leg was deferred for lack of data, STREAM_P.md "Directions"), round 23 P vol-control and CTA flips, round 9 (yields as macro fair value), round 41 (auction supply, not rebalancing). No round used bond returns to build rebalancing or risk-parity pressure. | The paper reports t > 4 on 1997-2023 with the effect in stock-minus-bond returns; the round 23 failure used equity returns only, which mismeasures the drift whenever bonds move. A daily signal on US indices pays IC's cost once per 1-day hold (~3-5 bp vs a ~100 bp sd). Expect part of the paper's effect to sit in the bond leg, which IC cannot trade: report the equity-leg share. |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each). If the first construction
fails, move to related public, dated by-products in the row (declare first), as in rounds 37-45.
