# Round 44 brief: aggregate corporate insider trading; CFTC Traders in Financial Futures positioning

Written 2026-10-30 (round 43 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-43 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the streams, the round folder
(research/results/portfolio/round44_insiders_tff/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r44/<stream>/`).
Also read the round 37-43 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md and
round4[0-3]_*_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; respect robots.txt (a site that
names ClaudeBot as disallowed is off limits); any downloaded row after 2024-12-31 is cut at parse, before anything is
printed, and nothing is printed from a probe before that cut exists.

**Speed (the user is waiting):** prefer small official bulk files; measure the download budget first and keep the full
pull under ~1 hour. Any background job must log progress, and every wait must also exit when its worker dies. Grade
IS + VAL as soon as they are complete; PRE is an add-on.

## Streams
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| I | **Aggregate corporate insider trading -> US500, US30, USTEC, US2000.** SEC "Insider Transactions Data Sets" (quarterly bulk zips of Forms 3 / 4 / 5 structured data, sec.gov/dera/data, 2006-24; generic research User-Agent, never the user's email; >= 0.2 s spacing): open-market purchases (code P) and sales (code S) by officers / directors, value-weighted and count-based, net purchase ratio by filing date. Declared families, sides from Seyhun 1988 / 1992, Lakonishok & Lee 2001, Jiang & Zaman 2010 (aggregate insider buying predicts higher market returns), fixed before returns: (1) daily / weekly net-purchase z -> long the index 1-5 days (enter after the filing's acceptance date at the next US open); (2) insider buying clusters after market falls (contrarian insider surges); (3) size and index-membership splits (large caps -> US500 / USTEC, small caps -> US2000). Count signal days per year and do the power arithmetic first; state the literature's horizon (often months) and what it implies at <= 5 days. | round 41 B (EDGAR issuance: hot-market indicator), round 42 E (heavyweight earnings), round 38 S (short volume), round 11 (cross-sections, drift after events). No round used insider transactions. | Insider trades are filed within 2 business days on a public timestamp, every day, by thousands of firms; their aggregate is a slow-moving informed-demand signal that index flows do not front-run, and at 1-5 days IC's index cost is a small share of the sd. Expect the effect to live at months: say what is left at 5 days. |
| T | **CFTC Traders in Financial Futures (TFF) positioning -> EURUSD, USDJPY, GBPUSD, AUDUSD, USDCAD, USDCHF, NZDUSD, US500, USTEC, US30, US2000, JP225, VIX-linked US500 (gold / oil via the disaggregated report as controls).** Weekly TFF futures-only files 2006-24 (cftc.gov historical compressed annual files): dealers, asset managers, leveraged funds, other reportables, net and changes. Declared families, sides from the literature fixed before returns: (1) leveraged-fund crowding (z of net) -> reversal 1-3 days after the Friday release (crowded-trade unwinds; Brunnermeier, Nagel & Pedersen 2008 for FX carry; Kang, Rouwenhorst & Tang 2020 for hedging pressure); (2) asset-manager changes -> continuation (slow real-money flow); (3) dealer net short extremes -> hedging-pressure premium. Release Friday 15:30 ET, as-of Tuesday; enter Friday 15:50 ET or the next session open, exit within 120 h. Weekly: say from the count that LIVE is impossible and what DEMO needs, and stop early if DEMO is out of reach. | round 4 / 9 (legacy COT non-commercial), round 39 D (COT small traders, JPX investor types: none), round 23 P (CTA signal flips), round 31 (positioning sources). No round used the TFF split (dealer / asset manager / leveraged). | The TFF split separates leveraged funds (fast, crowded) from asset managers (slow), which the legacy report mixes; crowded leveraged positions unwind mechanically when stopped out. Weekly, so DEMO at most: one cross-sectional book over 11+ markets is the only way to reach DEMO power. |

If a stream's first construction fails, it moves to related public, dated by-products in its row (declare first), as in
rounds 37-43. Two streams this round; each may use up to 3 heavy Python processes (under ~3 GB RAM each).
