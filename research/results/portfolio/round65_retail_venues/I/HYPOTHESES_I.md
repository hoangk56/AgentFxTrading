# Stream I (round 65): scout retail venues with dated listings (no backtest)

Written 2026-11-01 10:38 UTC (`date -u`: Sun Nov 1 10:38:49 UTC 2026), before any request to a candidate venue.
Scouting only: no trade is simulated, no return is computed beyond the pre-entry pump of a few example listings.
HOLD (2025-01-01..) is never requested: every candle request ends <= 2024-12-31 23:59:59 UTC and every series is cut
at ts < 2025-01-01 at parse.

## Mechanism to look for
K2 works on Upbit because a KRW listing concentrates retail buying in one known hour: the alt is already +21.5 % vs
BTC from L - 24 h to L + 1 h, and it fades over 72 h. Coinbase (L) fails because the pump is absent (+4-7 %). So a
venue is useful only if (a) its listing hour is datable from public data, (b) its listings hit coins that already
trade on a Binance perp, (c) the listing moves the global price (a visible pre-entry pump on Binance), and (d) the
events are not just Upbit / Bithumb events on the same coin a few days apart.

## Venues and checks planned
Candidates (Bithumb skipped: stream H): Coinone, Korbit (Korea); bitFlyer, Coincheck, bitbank (Japan); BtcTurk,
Paribu (Turkey); Bitkub (Thailand); Indodax (Indonesia); WazirX, CoinDCX (India); Bitvavo (EU); Mercado Bitcoin
(Brazil); plus at most a few found by search (e.g. Bitso, BitoPro, Zaif, Tokocrypto) if they have a keyless candle API.

Per venue, in order (stop at the first 403; back off on 418 / 429 / 503; >= 0.30 s between requests per host):
1. robots.txt of the API host (1 request; also the web host only if the docs live there).
2. API docs: read via WebSearch / one docs page request where needed (the 15-search budget is shared by all venues).
3. Market list endpoint (1 request): count markets whose base has a Binance USDT-M perp that started before 2025
   (local research/data/binance/perp_1d, first row = perp start); note whether delisted markets are listed and whether
   the list carries a listing date.
4. Candle endpoint check (1 request): deepest 1h / 1d history reachable for one old market (BTC), so history depth is
   known, and whether a pre-2020 or a delisted market returns candles.
5. 3-5 example listings 2020-24 of coins with a Binance perp >= 7 d old: one daily request to locate the first candle
   (if not already known), one 1h window L - 48 h .. L + 72 h. Pump = alt vs BTC from L - 24 h to L + 1 h on Binance
   (local 1h perp files, K2's definition), plus the venue's own first-hour premium vs Binance where computable.

Events/year estimate: without per-market requests, events are bounded by the market-list overlap with pre-2025
Binance perps; where the list has no listing date I report the bound and a calibrated estimate using the ratio seen
on Upbit (40 events / 139 overlapping KRW markets) and Coinbase (67 / 203). Independence: share of overlapping coins
that are also Upbit KRW markets (research/data/upbit list, read-only); for examples, whether Upbit listed the coin
within 7 days (K's k2_events.csv).

## Ranking
Usable independent events per year 2020-24 = estimated events x (1 - share within 7 days of an Upbit listing), then
history depth, first-candle visibility, delisted visibility, example pump size. A venue is "K2-usable" if it has
history back to 2020-22, a datable first candle, >= ~5 independent events / yr and example pumps clearly above the
Coinbase level (> ~10 %).

## Files
Code: I/code/ (fetch.py polite fetcher, parse scripts run with `python -I`). Data: research/data/retail_venues/
(<venue>/ bodies, requests.log: UTC time, URL, status, bytes). Report: I/STREAM_I.md.
