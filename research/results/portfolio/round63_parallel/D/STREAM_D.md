# Stream D: Binance announcement events on USDT-M perps. Not testable inside the rules; no LIVE or DEMO candidate

Written 2026-10-31 15:24 UTC (from `date -u`). Hypotheses (declared 14:31 UTC, before any count or return):
[HYPOTHESES_D.md](HYPOTHESES_D.md). Code: `code/fetch.py`, `code/count_events.py`, `code/tabulate.py`. Data and
request log: research/data/binance_announcements/.

## Answer

**None.** No rule was graded, because none could be built inside the rules:

1. **The announcement data is off-limits.** Binance's robots.txt disallows `*/bapi/` for `User-agent: *`, and that
   covers the CMS list API. The HTML announcement pages, which robots.txt does allow, answer a plain client with
   HTTP 202 and an empty body: a JavaScript bot challenge. Getting past it would mean posing as a browser. Two
   searches found no open archive with release timestamps, only paid datasets and scrapers that call the same `/bapi/`
   endpoint. Per the brief I stopped this route. No `/bapi/` URL was requested.
2. **The one event type that needs no announcement (S) has no IS sample.** S is a spot listing of a coin that
   already had a USDT-M perp for at least 7 days, timed by the first spot kline. It has **0 events in IS 2020-21**
   and 7 in VAL 2022-24. The declared gate was n_IS >= 20, so no returns were computed.
3. **Even with announcement times, IS 2020-21 holds almost no events.** Counts of exchange-observable dates, no
   prices:

| event type (coin has a USDT-M perp) | 2020 | 2021 | 2022 | 2023 | 2024 | IS / VAL |
|---|---|---|---|---|---|---|
| S: spot listing >= 7 d after the perp (BLUR, BONK, PYTH, WIF, TON, TURBO, 1000CAT) | 0 | 0 | 0 | 2 | 5 | 0 / 7 |
| P: perp's last kline before 2025 (perp delisting) | 1 | 2 | 8 | 0 | 12 | 3 / 20 |
| spot: every main-quote pair ended before 2024-12 | 1 | 1 | 6 | 3 | 16 | 2 / 25 |
| of which real delistings, not token swaps or renames (BZRX, SRM, BTS, XMR, OMG, WAVES, XEM, BOND, LOOM, REEF, UNFI) | 0 | 1 | 1 | 1 | 8 | 1 / 10 |
| Monitoring / Seed tag | - | - | - | (tag starts 2023) | | 0 / ? |

Swaps and renames excluded from the spot-delisting row: LEND->AAVE, BTT redenomination, KEEP / NU->T, HNT, ANC,
COCOS->COMBO, TOMO->VIC, ANT, AGIX / OCEAN->FET, RNDR->RENDER, GAL->G, MATIC->POL, KLAY->KAIA, FRONT.

Power arithmetic (HYPOTHESES section 2): an IS t of 2.0 needs about 44 events at a per-event net Sharpe of 0.3, and
2.5 needs 69. IS 2020-21 has at most ~3-6 forced-flow events of any type, so neither the DEMO nor the LIVE IS bar
can be reached with any announcement data. Binance delisted little in 2020-21, the tags did not exist yet, and
perp-before-spot listings began only in late 2023. This is a structural fail of the era design, not a negative
result about the effect.

## What was done

- robots.txt for www.binance.com (200, saved as raw/robots.txt). The SupportAndAnnouncement sitemap index and its
  English file: no article URLs. Announcement list page 161: 202 with 0 bytes. Two WebSearches.
- data.binance.vision bucket listing: robots.txt is 404, so no restriction. That gave 3,745 spot symbols ever
  (delisted ones included) and, for every candidate pair of the 380 perps listed before 2025 (quotes USDT, BUSD,
  FDUSD, USDC, TUSD, BTC, BNB, ETH; 1000 / 1000000 / 1M prefixes mapped to the base), the first and last monthly 1d
  file, then the first daily file of every pair in the earliest month. About 2,750 requests in total, all 200 apart
  from one SSL timeout that was retried. Outputs: event_dates.csv, spot_first_month.json, spot_symbols.json.
- Cross-check against round 60's api.binance.com spot_first.csv: no pair has an earlier api date than the
  data.binance.vision date.
- Fixed bug: the first pass took the first daily file of the alphabetically first pair in the earliest month. That
  wrongly made APE and OP (spot and perp listed the same day) into events, along with four other coins. The count
  went from 13 to 7 VAL events once the earliest day across all pairs was used.

## Pitfalls / disclosure

- At 14:30 UTC an exploratory count on local data printed the number of perp-first spot listings per year, 2025-26
  included. These were listing dates only, no prices or returns. Most such listings fall after 2024 (the Binance
  Alpha -> futures -> spot pipeline). No price or funding series from 2025+ was loaded.
- data.binance.vision lacks a few pairs, but the api source agreed for every perp checked.
- Pre-listing run-up: even with listing times it cannot be traded without the announcement time, because entering
  before an unknown announcement is look-ahead.

## What a user decision could unlock

1. Allow the Binance CMS `/bapi/` endpoint despite robots.txt, or buy a timestamped dataset (Cryptocurrency Alerting
   historical listings). Even then **IS 2020-21 stays nearly empty**, so this only helps alongside decision 2.
2. A different era split for exchange-event rules, for example design on 2022-23 and validate on 2024. The
   forced-flow event set lives in 2022-24 (about 40-60 delist / tag events, plus Monitoring tags from 2023) and grows
   strongly after 2024. HOLD is unchanged, so only rules with HOLD power >= 3 would matter. At about 30 events a year
   with a per-event Sharpe of 0.3, that is 0.3 x sqrt(55) = 2.2: DEMO at best.
3. A forward-only paper log of Binance announcement events from now on (live WebSocket, with a key: needs the
   user's account).
