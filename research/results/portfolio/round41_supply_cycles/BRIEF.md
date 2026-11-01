# Round 41 brief: sovereign auction supply cycles (US all tenors, JGB, Bund); US equity issuance supply

Written 2026-10-30 (round 40 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-40 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the streams, the round folder
(research/results/portfolio/round41_supply_cycles/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r41/<stream>/`).
Also read the round 37-40 reports (research/results/portfolio/round37_forced_flows_2026-10-29.md,
round38_short_volume_storms_2026-10-29.md, round39_rolls_positioning_2026-10-29.md, round40_news_leverage_2026-10-30.md),
especially "Pitfalls": **do not use web.archive.org**; any downloaded row after 2024-12-31 is cut at parse, before
anything is printed.

**Speed (the user is waiting):** prefer small official files; measure the download budget first and keep the full pull
under ~1 hour. Any background job must log progress, and every wait must also exit when its worker dies (round 40 G
stalled 6.5 h on a crashed parser). Grade IS + VAL as soon as they are complete; PRE is an add-on.

## Streams
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| A | **Sovereign auction supply cycles -> USDJPY, EURUSD, EURJPY, XAU, US500, DE40, JP225.** Official auction calendars and results, free: US Treasury (fiscaldata.treasury.gov auctions query, all coupon tenors, TIPS, FRNs, bills > 52 weeks if relevant; 2004-24), Japan MoF JGB auctions (mof.go.jp results 2004-24: 2 / 5 / 10 / 20 / 30 / 40-year), German Finanzagentur Bund / Bobl / Schatz auctions (state what is reachable). Declared families, sides from Lou, Yan & Zhang 2013 RFS (dealer inventory: yields rise into an auction and fall after) and Beetsma et al. 2016 for euro-area supply: (1) pre-auction concession -> the currency / index side implied by higher local yields over days -5..0 and the reversal 0..+3, sized by DV01-weighted supply; (2) auction-week clusters (several tenors in one week, e.g. US refunding weeks, JGB 30 / 40-year weeks); (3) result surprise (tail vs when-issued where available, bid-to-cover z) as a drift past the first minute only (rounds 25-26 found release-minute pricing). Count auctions and independent weeks per year and do the power arithmetic first. | round 22 R (US 10-year concession only, 1 cell family), round 4 (Treasury auctions as external features), round 13 (coupon / bill settlement payments: no 1-day move), round 21 (refunding as a Fed event). No round used JGB or Bund auctions or DV01-weighted supply across tenors. | Supply is scheduled weeks ahead and must be absorbed by dealers on a mechanical calendar; US + JGB + Bund give ~250-350 auctions a year, so a 1-5 day book has hundreds of trades and IC's cost is a small share of the multi-day sd. |
| B | **US equity issuance supply -> US500, USTEC, US2000 (US30 control).** SEC EDGAR daily index (full-index / daily-index, free, polite UA with no personal email: use a generic contact string as SEC asks for a UA, but never the user's email) 2004-24: counts and, where cheap, sizes of follow-on / shelf takedowns (424B forms), IPO pricings (424B4), large secondary block sales, and buyback authorisations (8-K item 8.01 text only if cheap; otherwise drop). Declared side: equity supply absorbs demand -> lower next 1-5 day index returns (state the literature: Baker & Wurgler equity share, Lou 2014 on issuance clustering, Hirshleifer & Jiang; fix before returns); buyback authorisation clusters -> higher. Use each filing only after its EDGAR acceptance time; enter at the next US open or the next IC session after acceptance. Count events per day and do the power arithmetic first. | round 23 P (buyback blackout calendar: none), round 11 (cross-section, drift after events: dead since 2015), round 38 S (ETF primary flows follow price). No round used EDGAR issuance filings as an aggregate supply series. | Issuance is a daily, mechanical quantity of new shares that index buyers must absorb, available from 2004 on a public timestamp; ~250 signal days a year on 3 indices. |

If a stream's first construction fails, it moves to related scheduled-supply by-products in its row (declare first),
as in rounds 37-40. Two streams this round; each may use up to 3 heavy Python processes (under ~3 GB RAM each).
