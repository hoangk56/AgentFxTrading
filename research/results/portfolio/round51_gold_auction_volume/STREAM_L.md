# Round 51 stream L: LBMA gold / silver per-auction volume, rounds, imbalance: data not reachable free

Written 2026-10-30 09:26 UTC (`date -u`). Probe window 09:22-09:25 UTC from this Mac. Verdict: **none (no data)**.
No hypothesis file, no returns, no HOLD contact: no series was loaded, so nothing from 2025-26 was seen or printed.

## Question
Are per-auction LBMA Gold Price (10:30, 15:00 London) / LBMA Silver Price (12:00) volume, number of rounds, imbalance or
participant data for 2015-24 published free (no account, no login)?

## Answer: no
| host / page | robots.txt | what it is | status |
|---|---|---|---|
| www.lbma.org.uk | 200; only `Disallow: /cache/` for `*`; no ClaudeBot rule | Prices pages. LBMA article "LBMA benchmark prices data tables are moving" (Nov 2025): historic price tables moved to the Members' Portal from 2025-11-24; access needs a portal login and an application reviewed by LBMA staff, even for non-commercial use. Only the latest daily price stays public. Volume / rounds are not mentioned. | login: off limits |
| prices.lbma.org.uk (`/json/gold_am.json`, the old price JSON) | robots.txt 401 | Cloudflare **403** on one HEAD request with the research UA. It holds prices only (USD / GBP / EUR), never volume. | stop (403); not retried |
| www.ice.com/report/179 "IBA Gold Auction Historical Transparency Reports" (single / multi-day; the only IBA product with per-auction round prices and volumes) | allowed (`/report-center/category/` disallowed, so that page was not fetched; `/report/179` is allowed) | Page config has `registrationType: IBA_GOLD_AUCTION`, plus an "IBA User Registration Form": "In order to access IBA's data and information you must provide the following information", reviewed by IBA and verified by an e-mail link. | account + e-mail: off limits |
| www.ice.com/report/211, /report/218 "LBMA Gold / Silver Price Monthly Volumes" | allowed | No registration flag. The table columns are monthly **Total / Min / Max / Average daily volume** by category. That is a monthly aggregate, not one row per auction. | free-looking but **monthly only**; rows not pulled |
| www.ice.com/publicdocs/IBA_Gold_Silver_Auction_Factsheet.pdf | allowed | 404 (the search hit is on uat2.ice.com, a test host; not fetched) | none |
| www.theice.com | robots 301 (redirects to ice.com) | same content as ice.com | see above |
| GitHub / third-party sets (alphacast, metalcharts, Nasdaq LBMA Trade Data) | not fetched | Search only: prices, annual / weekly averages, or the paid LBMA Trade Data OTC aggregates (Bloomberg / Eikon). No per-auction volume / rounds set found. goldfixing.com (which had net volume and participant counts before 2015) is offline. | none |

The only public round-count figure is the IBA 2024 licence-holder questionnaire's "typical" count (gold 10:30 ~5 rounds,
15:00 ~6-7, silver 1-2). That is a constant, not a dated series.

## Why the monthly report does not rescue a family
- Family 1 (imbalance / many rounds -> 15 min or close continuation vs reversal) needs per-auction rounds and imbalance.
  Not in a monthly total.
- Family 2 (volume vs the trailing 60 auctions) needs per-auction volume. The monthly min / max / average cannot rank
  single auctions.
- Family 3 (prior-day volume scaling the silver pre-12:00 drop) needs the prior day's volume. A monthly average is known
  only after the month ends, so it cannot condition a day. Even used as a regime label (the last month's average), it
  gives about 108 IS monthly values and is just a slow volume regime, not the auction-flow mechanism the brief asks about.
  Round 10 / 12 measured the drop at +2.7 bp at mid, below IC silver cost, so it would need a >= 3x scale
  from a monthly label. No construction like that is declared, and the brief needs no fallback grid.

## Power (for the record, had data existed)
About 250 auctions a year per fix. At HOLD (~21 months) that is ~435 auctions per fix. LIVE (power >= 3) needs a
per-trade net Sharpe of about 0.14 over all of them, or about 0.32 if a top-quintile condition keeps ~87 HOLD trades.
For 15-minute gold moves (sd ~8-10 bp) that means a net edge of about 1.4 bp unconditional, or about 3 bp on the
quintile, after a ~2-3 bp gold cost. Not tested.

## Directions that need the user
- **IBA registration for report 179** (an IBA account with e-mail verification; the site calls the reports free for
  registered users). It would give per-auction round prices and volumes, probably 2015-; all three declared families
  become testable. Value estimate: low-moderate. The auction price itself is already in the M1 bars, and rounds 10 / 12 / 28
  found auction-minute effects below IC cost. Imbalance / volume is the one ingredient not yet tried. Chance of a LIVE
  cell is probably under 5 %, but it is cheap if the user registers.
- LBMA Members' Portal (application, non-commercial self-certification): price tables only as far as is known. No value
  for this stream.
- Paid: LBMA Trade Data (Nasdaq via Bloomberg / Eikon), the ICE real-time auction feed. Not worth it at this prior.

## Files
- Request log, robots copies, fetched pages: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r51/L/web/`
  (`requests.log`, `robots_*.txt`, `rep_179.html`, `r211.html`, `r218.html`).
- HTML stripper: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r51/L/strip.py`.
