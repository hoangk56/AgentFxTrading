# Round 42 brief: index heavyweight earnings -> index CFDs; Bank of Japan JGB purchase operations -> JPY, JP225

Written 2026-10-30 (round 41 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-41 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the streams, the round folder
(research/results/portfolio/round42_megacap_boj_ops/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r42/<stream>/`).
Also read the round 37-41 reports (research/results/portfolio/round3[7-9]_*_2026-10-29.md, round40_news_leverage_2026-10-30.md,
round41_supply_cycles_2026-10-30.md), especially "Pitfalls": **do not use web.archive.org**; any downloaded row after
2024-12-31 is cut at parse, before anything is printed.

**Speed (the user is waiting):** prefer small official files; measure the download budget first and keep the full pull
under ~1 hour. Any background job must log progress, and every wait must also exit when its worker dies. Grade IS + VAL
as soon as they are complete; PRE is an add-on. A new algorithm must differ in mechanism from C3 (gotobi / JPY fix);
report the daily correlation with C3 for anything that survives.

## Streams
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| E | **Index heavyweight earnings -> USTEC, US500, US30 (DE40 / JP225 controls).** The top ~30-50 US index weights (state the list per year from a public source, fixed before returns; use FB before 2022-06-09 for META), their earnings release times from SEC EDGAR 8-K item 2.02 filings via data.sec.gov/submissions/CIK##########.json (acceptance timestamps; generic research User-Agent, never the user's email; >= 0.2 s spacing). Declared families, sides from the literature fixed before returns: (1) next-session continuation or reversal of the after-hours index CFD reaction to a heavyweight release (index-level post-announcement drift vs overreaction: state which papers imply which, e.g. Savor & Wilson 2016, Patton & Verardo 2012 "learning spillovers", Chan & Marsh 2021 on index reaction); (2) earnings-season clustering: days with >= k heavyweight releases, the index premium on announcement days (Savor & Wilson) at the index level; (3) pre-release drift (positioning / hedging into a heavyweight release). Enter only after the acceptance time; IC CFDs trade after hours, so state the session clock. Count events per year and do the power arithmetic first. | round 41 B (EDGAR issuance: hot-market indicator), round 11 (drift after events dead since 2015, cross-sections), round 23 P (buyback blackout calendar), round 25 A (share CFDs are a user decision: MT5 only). No round used heavyweight earnings at the index level. | ~150-200 heavyweight releases a year, each moving the index CFD by a measurable fraction after hours on a public timestamp; a 1-day hold makes IC's index cost a small share of the sd. |
| J | **Bank of Japan JGB purchase operations (rinban) -> USDJPY, EURJPY, JP225 (XAU control).** BoJ operation results (offer amounts, purchase amounts, offer-to-cover ratio, lowest accepted yield spread / average, by maturity bucket) and the monthly purchase schedules, 2010-24, from boj.or.jp (find the official history files; state what is reachable, polite spacing). Declared families, sides fixed before returns: (1) offer-to-cover z by bucket (high = dealers eager to sell JGBs = upward yield pressure -> JPY up / JP225 down) from the result release (~12:00 / 14:00 JST, state it) to 1-3 days; (2) schedule changes in the monthly plan (cut / raise of amounts or frequency, announced on a known clock) -> 1-5 days; (3) fixed-rate / unlimited operations (YCC defence days 2016-24) as a separate, rarer family. JPY only through the BoJ balance sheet channel, not the Tokyo fix: show the correlation with C3. Count operations and independent days per year and do the power arithmetic first. | round 41 A (JGB auctions: none), round 20-21 (central bank decision days), round 36 (HIBOR / SHIBOR / RRR), round 31 J (MoF weekly flows, intervention record). No round used BoJ operation results. | Operations run several times a week on a published plan, so a daily signal from 2010 gives hundreds of events; offer-to-cover is a mechanical read of dealer inventory that the market sees only at the release time. |

If a stream's first construction fails, it moves to related public, dated by-products in its row (declare first), as in
rounds 37-41. Two streams this round; each may use up to 3 heavy Python processes (under ~3 GB RAM each).
