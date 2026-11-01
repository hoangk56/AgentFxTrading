# Round 47 brief: dollar-weighted corporate buyback capacity from filed repurchases and true earnings dates

Written 2026-10-30 08:01 UTC (round 46 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-46 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the stream, the round folder
(research/results/portfolio/round47_buyback_capacity/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r47/<stream>/`).
Also read the round 37-46 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-6]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
disallows ClaudeBot / anthropic-ai is off limits, e.g. cftc.gov, countryeconomy.com, data-api.ecb.europa.eu); any row
after 2024-12-31 is cut at parse or load, before anything is printed.

**Speed (the user is waiting):** reuse files already on disk first (round 42 E built EDGAR submissions JSON and
earnings acceptance times for the top-40 US firms, round 44 I has Vanguard 13F ranks, round 41 B the EDGAR indexes);
keep any new pull under ~1 hour (SEC: generic research User-Agent, never an email, >= 0.15 s spacing). Background jobs
log progress, and every wait also exits when its worker dies. Grade IS + VAL as soon as they are complete.

## Stream
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| B | **Daily open-window buyback capacity -> US500, USTEC, US30 (US2000 as a low-buyback control).** For the ~150-300 largest US firms (membership by year from round 44's 13F ranks or round 42's list, fixed before returns), take quarterly repurchase dollars from SEC XBRL company facts (`PaymentsForRepurchaseOfCommonStock`, as filed, using the filing date as the public date: no look-ahead) and each firm's true earnings dates (8-K item 2.02 or 10-Q / 10-K acceptance, from submissions JSON). Declared blackout convention fixed before returns (e.g. from 2 weeks before quarter end, or from quarter end, to 2 business days after the earnings release; state the source: Goldman desk / company policies / literature). Signal: index-level dollar capacity in the open window = sum of trailing repurchase run-rate of firms whose window is open, scaled by total cap; its daily level and its change (windows reopening after earnings). Declared families, sides fixed before returns: (1) high open capacity -> long the index 10:00-15:30 NY or close-to-close, 1-5 days; (2) reopening surges (capacity jump after a cluster of releases) -> long 1-3 days; (3) within earnings season, compare days by capacity to separate the buyback bid from the earnings-season drift (declare the comparison). Count days, do the power arithmetic first. | round 23 P4 (calendar proxy of the blackout: blackout days as strong as open days, earnings drift dominated), round 41 B (EDGAR issuance; SC TO-I tender offers USTEC IS t 2.16 at 76 % random), round 42 E (heavyweight earnings at index level), round 44 I (insiders). No round measured each firm's real window and dollar run-rate. | Buybacks are ~$0.8-1 tn a year, concentrated in the largest index weights; their timing is set by each firm's own earnings date, which differs from the calendar proxy by weeks for many large firms. A daily, dollar-weighted capacity series is a different, informative measure and gives ~250 signals a year at a ~3-5 bp index cost. Expect the earnings-season drift to confound it: say how much is left after (3). |

One stream this round; it may use up to 3 heavy Python processes (under ~3 GB RAM each). If the first construction
fails, move to related public, dated by-products in the row (declare first), as in rounds 37-46.
