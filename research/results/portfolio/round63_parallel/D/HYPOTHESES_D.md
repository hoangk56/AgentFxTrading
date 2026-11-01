# Stream D hypotheses: Binance announcement events (forced / rule-driven flows) on USDT-M perps

Written 2026-10-31 14:31 UTC (from `date -u`), before any event return was computed. Stream D of round 63
(../BRIEF.md). Network log: research/data/binance_announcements/requests.log.

## 0. Data access check (done first, 14:28-14:30 UTC)

| request | result |
|---|---|
| https://www.binance.com/robots.txt (plain UA) | 200. The `User-agent: *` group has `Disallow: */bapi/` (only `*/bapi/fe/` is carved out). The CMS list endpoint `/bapi/composite/v1/public/cms/article/list/query` is therefore **disallowed** |
| SupportAndAnnouncement sitemap (allowed, `*/sitemap_output/`) | 200, but the English file lists help / coin pages and only the top-level `/en/support/list/announcement`, no articles |
| https://www.binance.com/en/support/announcement/list/161 (HTML, allowed by robots) | **HTTP 202, empty body**: a bot challenge page that needs JavaScript. Getting past it would mean posing as a browser, which the brief forbids |
| WebSearch x2 (GitHub / open archives of Binance announcements) | none. Only paid datasets, Apify actors, and scrapers that call the same disallowed `/bapi/` endpoint |

Per the brief ("if the API is disallowed or blocked, stop and report, do not disguise") the announcement route is
**stopped**. No `/bapi/` URL was requested.

Consequence: no rule keyed to an announcement time can be built. That rules out spot and perp delisting notices,
Monitoring / Seed tag changes, margin delistings, and the pre-listing run-up of a spot listing.

## 1. What can still be tested inside the rules

These are event types whose trigger time is printed in exchange market data (data.binance.vision, which has no
robots.txt (404), or api / fapi klines), so no announcement is needed:

- **S: spot listing of a coin that already has a USDT-M perp.** T = open time of the first spot kline on Binance
  (any of USDT / BUSD / FDUSD / USDC / BTC quote; the earliest one counts). Eligible if the perp's first 1d kline is
  at least 7 days before T. Mechanism: retail spot demand arrives at a known time, and the run-up into it unwinds
  after (fade). The run-up leg itself needs the announcement time, so it is **not testable** (descriptive only).
  - Rule S-fade (side fixed): short the perp at T + 1 h (variant T + 5 min, reported only as the "move before
    entry"), long BTCUSDT perp for equal notional, hold 1 h / 24 h / 3 d / 7 d (4 cells), exit at market.
  - Costs: 0.05 % taker + 0.075 % half-spread a side (alt), 0.05 % + 0.02 % for the BTC leg, plus the funding paid or
    received on both legs over the hold. Robustness: costs x1.5, one step late (entry T + 2 h).
  - Benchmarks: (a) same coin, 200 random entry times 14-90 days after T; (b) random top-60 alts at the event times.
- **P: perp delisting (last perp kline).** The delisting time can be seen in the data, but the announcement comes an
  unknown 1-10 days earlier. Any entry before the delisting time could therefore be placed before the
  announcement (look-ahead), and entering after the delisting is impossible. **Not declared as a rule.** It is
  counted per year only, to price the user decision in section 3.

## 2. Power arithmetic (before any return)

Bars: IS t >= 2.5 (LIVE) / 2.0 (DEMO), with t ~ SR_ep x sqrt(n). Per-event net Sharpe for alt event trades in
earlier rounds: round 60 listings 0.11-0.20 (30 d); a generous 0.3 for a 1-7 d event leg.
- DEMO IS needs n_IS >= (2.0 / 0.3)^2 ~ 44 events in 2020-21. LIVE IS needs >= 69, and HOLD power >= 3 needs
  >= 100 HOLD events at SR 0.3.
- Gate (declared now): if S has fewer than 20 eligible IS events (2020-21), no IS t can reach 2.0 at a plausible
  SR (at n = 20, SR 0.45 per event would be needed, above anything seen in rounds 58-62). Then S is graded "not
  testable at the bar" and **no returns are computed**, so nothing is fitted on VAL either. The counts per era are
  reported. Counting events looks only at listing dates, not at outcomes, and the HOLD-era count is a single number
  (no prices).

## 3. User decisions that would unlock the stream

- Allow the Binance CMS `/bapi/` endpoint despite robots.txt (the user's call, not mine), or buy a dataset with
  announcement timestamps (e.g. Cryptocurrency Alerting's historical listing dataset).
- With announcement times, the declared design would be: types {spot delist, perp delist, monitoring tag add, spot
  listing of a perp coin}; entry +5 min and +1 h after release (report the move before entry); short tagged / delisted
  coins, long the run-up and short the fade for spot listings; holds 1 h / 24 h / 3 d / 7 d; BTC hedge; same costs.
