# Stream M (round 65): Upbit non-KRW market additions, K2's rule frozen. No LIVE or DEMO rule

Written Sun Nov 1 12:06:35 UTC 2026 (from `date -u`). Hypotheses were declared in [HYPOTHESES_M.md](HYPOTHESES_M.md)
at 11:49:35 UTC, before any Binance price was requested.

HOLD (2025-01-01..) was never requested, loaded or counted:
- every Upbit candle request ends at or before 2025-01-01 00:00 UTC;
- every fapi window ends before then;
- the 1h panels are cut at ts < 2025-01-01;
- only L < 2024-12-28 is used.

Nothing under */coord/hold/ was read except k2rule.py, as instructed.

## Answer first
**None.** On Upbit BTC- / USDT-market additions (no KRW pair yet), K2's frozen rule fails the IS bar and is strong in
VAL.

| era | n | net bp / trade | t (by day) | SR / trade | years |
|---|---|---|---|---|---|
| IS 2020-21 | 16 | **-39** | **-0.08** | | 2020 +572 (8), 2021 -650 (8) |
| VAL 2022-24 | 16 | **+596** | **2.98** | 0.80 | every year positive |

- **Bars.** DEMO needs IS t >= 2.0, and IS fails it. LIVE also needs HOLD power >= 3, and power at VAL size is
  0.80 x sqrt(~10-13 HOLD events) = **2.5-2.9**.
- **The pump before entry is about half of K2's.**

  | era | non-KRW median | non-KRW mean | K2 median | K2 mean |
  |---|---|---|---|---|
  | IS | +3.3 % | +8.6 % | +12.7 % | +21.5 % |
  | VAL | +6.4 % | +7.1 % | +17.2 % | +22.2 % |

  Figures are alt vs BTC, from L - 24 h to entry.
- **The run-up sits before the notice.** From notice to entry the alt already falls (median -1.8 % IS, -5.0 % VAL).
- **No PREREG_DRAFT.**

**K2 survivorship check.** Adding the KRW listings missing from K's list (MATIC as renamed POL; OMNI, STG and BONK,
since delisted from Upbit) barely changes K2:

| era | K2 | K2 + missing |
|---|---|---|
| IS | +1094, t 3.16, n 11 | **+961, t 2.63, n 12** |
| VAL | +423, t 1.37, n 29 | **+465, t 1.61, n 32** |

K's list was not conservatively biased in IS: the one missing IS listing, MATIC, lost 503 bp. In VAL the missing
listings helped. Of J's 9 "missing KRW" coin-events, only these 4 are real tradable KRW listings.

## Data and requests (research/data/upbit_nonkrw/requests.log, 1,963 lines)
**robots.txt.**
- api.upbit.com: 404 (no file), logged 11:41:12.
- fapi.binance.com: blocks only named search engines. Logged at the end; round 64 K had read it before.
- Notices came from stream W's cache only (research/data/upbit_notices/raw, read-only). No notice host was requested.

**Requests.**
- Upbit: 336 × 200 and 93 × 404, at >= 0.3 s. The 404s are delisted markets: the candles API returns 404 for them.
- fapi: 1,530 × 200 and 3 timeouts (retried). No 403, 418 or 429.
- No key, no account and no e-mail. UA `research-script`.

**Upbit use.**
- 60-minute candles, used only to date first candles and as the price guard.
- One `/v1/market/all`. This is the current list, used only to find renamed markets: GAL -> G and MATIC -> POL keep
  their history.

**6 WebSearches** for the opening times of delisted markets:
- BONK USDT 2024-10-22 18:00 KST;
- JASMY 2024-11-20 15:00 KST;
- BONK KRW 2024-11-20 12:30 KST;
- STG KRW 2024-05-30 16:45 KST;
- STG BTC 2023-08 and SRM KRW 2020-10: not found.

Sources: [bloomingbit 78444](https://bloomingbit.io/feed/news/78444),
[bloomingbit 78443](https://bloomingbit.io/feed/news/78443),
[tokenpost 206448](https://www.tokenpost.kr/news/breaking/206448),
[blockmedia 1119831](https://www.blockmedia.co.kr/archives/1119831).

**Pricing.** `code/k2rule.py` is a byte copy of round64 K/coord/hold/k2rule.py; only the log folder line and the
docstring differ (diff shown in the run). run.py adds a URL cache around `k2rule.get`, which does not change any
price.

**Check of the copy.** K2's 40 events, recomputed with this copy, reproduce K's published numbers exactly:
IS +1094 / t 3.16, VAL +423 / t 1.37.

## Events (code/events.py; output events_M.csv, events_build_output.txt)
**Definition** (declared): the coin's first appearance on Upbit in any market, via a BTC or USDT market, with no
KRW pair within 8 days, and a Binance perp >= 7 d old.
- **33 events**: IS 16, VAL 17. Most are 2020-21 BTC-market additions.
- **Mixed notices.** Several "KRW, BTC (A, B)" notices gave B only a BTC market: MASK 2021-10, AUDIO, GAL 2023-01
  and ALT 2024-02. BIGTIME 2024-04 also got BTC / USDT only.

**How L is set.**
- From the first 60m candle: 28 events.
- From a partner coin in the same notice: SNX.
- From a WebSearch: BONK, JASMY.
- From the declared fallback (notice + the year's median lag): SRM, STG.
- **Lag from notice to the first candle:** 1-3 h in 2020-21; ~6.5 h in 2022-23 (notices at 10:00 KST, trading at
  ~16-17:00 KST); 2.5-4 h in 2024.

**Name-collision guard** (Upbit price vs perp within 1.5x).
- 27 events pass, at ratios of 0.95-1.09. 5 events have no Upbit candle to compare (SRM, SNX, STG, BONK, JASMY).
- **GAL fails at 0.017.** Upbit's renamed BTC-G market shows GAL's 2023 prices divided by ~58, which is the GAL -> G
  swap ratio. It is the same coin, not a collision, but it is dropped as declared.
- With GAL kept (H72 +713), VAL would be +603 bp, n 17.

**Excluded.**
- Coins already on Upbit: GAS / NEO / SOL 2024-06, the 2024-11-13 USDT batch, INJ / UNI / RENDER.
- Coins with a KRW pair added at the same notice: 13, all K2-type.
- USDC.

## Results (net bp per trade; costs 42 bp + real funding; t clustered by entry day)
Full output: report_output.txt.

| cell | era | n | gross | fund | **net** | **t** | median | SR | x1.5 cost | +5 min | L + 2 h | drop best | worst | years (n, net) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **H72 (frozen)** | IS | 16 | +18 | -15 | **-39** | **-0.08** | +146 | -0.02 | -60 | -54 | -139 | -195 | -4938 GTC | 2020 (8) +572, 2021 (8) -650 |
| | VAL | 16 | +634 | +4 | **+596** | **2.98** | +460 | 0.80 | +575 | +584 | +533 | +491 | -271 STG | 2022 (5) +779, 2023 (4) +341, 2024 (7) +611 |
| H24 (info) | IS | 16 | +307 | -21 | +244 | 1.37 | +100 | 0.37 | | | | +130 | | 2020 +115, 2021 +374 |
| | VAL | 16 | +413 | 0 | +371 | 2.42 | +385 | 0.65 | | | | +301 | | 2022 +520, 2023 +580, 2024 +146 |
| H72 without the fallback L | IS / VAL | 15 / 15 | | | -36 / +654 | -0.07 / 3.24 | | | | | | | | |

**Random benchmark.**
- Method: gross on 1h closes, bar starting at L + 1 h, 500 draws. Local 1h panels, filled from fapi 1h for the
  event coins.
- Columns: **(a)** = other perps at the same hour; **(b)** = the same coin 30-180 d later.
- The VAL row includes GAL (n 17), since the guard was not applied in random_M.json.

| cell | era | gross | (a) % | (b) % | (a) median | (b) median |
|---|---|---|---|---|---|---|
| H72 | IS | -85 | 66 | 39 | -200 | -13 |
| H72 | VAL | +588 | 100 | 100 | -131 | +31 |
| H24 | IS | +252 | 100 | 94 | | |
| H24 | VAL | +482 | 100 | 100 | | |

**Max over cells.** There are 2 declared cells (H72, H24). The best IS t is 1.37 (H24), below the DEMO bar even
before any multiplicity correction. H72 was fixed in advance as K2's rule, not chosen.

**Why IS fails.** 2021 BTC-market additions in a bull market kept running for the short:
- GTC -4938;
- NEAR -2226;
- SNX -1169;
- OCEAN -629;
- GRT -613.

2020 is positive (+572). The VAL strength comes from many medium wins (median +460, worst -271), so it is not one
tail. The rule is the same in both eras; nothing was retuned.

**Pump timing.** On non-KRW additions the alt rises into the notice, then drifts down before the market opens.

| era | N - 24 h -> entry (median) | notice -> entry (median) |
|---|---|---|
| IS | +5.0 % | -1.8 % |
| VAL | +5.5 % | -5.0 % |

So part of the fade has already happened by L + 1 h. The pre-notice rise looks like either leaks or a sector move.
That is relevant to stream A, which enters at the notice: on these events the notice is close to the top.

## Power
- **Non-KRW pace.** VAL has 16-17 events in 3 years (5.5 / yr); 2024 has 7. Over 1.83 HOLD years that gives n ≈
  10-13.
- **At VAL size** (SR 0.80), power ≈ 2.5-2.9. That is below 3 even before the IS failure.
- **Pooled M + K2 + missing (information only):**

  | era | net | t | n | SR |
  |---|---|---|---|---|
  | IS | +390 | 1.04 | 28 | |
  | VAL | +508 | 2.45 | 48 | 0.36 |

  Power at ~25 events / yr ≈ 0.36 x sqrt(46) ≈ 2.4. Pooling dilutes K2's IS: the M IS events are flat.
- **C3 correlation:** not computed, since no cell has DEMO numbers.

## K2 survivorship check (detail)
**J's 9 KRW coin-events not in K's list, re-checked:**

| coin-event | status | L | era | H72 net | pump |
|---|---|---|---|---|---|
| MATIC 2021-10-15 | genuine. K's map hit POLUSDT, whose perp starts 2024-09. | 06:00, from the renamed KRW-POL | IS | -503 | +14 % |
| OMNI 2024-05-03 | Upbit-delisted | ZETA's KRW L, same notice | VAL | +674 | +3.5 % |
| STG 2024-05-30 | Upbit-delisted | 16:45 KST -> 07:00 UTC | VAL | -616 | +42 % |
| BONK 2024-11-20 | Upbit-delisted | 12:30 KST -> 03:00 UTC | VAL | +2555 | +16 % |
| AUDIO 2021-11, GAL 2023-01, ALT 2024-02 | not KRW listings: BTC only, now M events | | | | |
| GAL 2024-07 | the GALUSDT perp ended 2024-07-11 | | | | |
| USDC | stablecoin | | | | |

- J's 2-hop regex also misses "원화" titles (2020-21). Those found are all in K2 already, except SRM's KRW listing
  (~2020-10-13..15; no addition notice, no candles, no time found). It is excluded.
- **Effect** (H72 / H24): IS +1094 -> +961 (t 3.16 -> 2.63) / +673 -> +587 (t 2.22 -> 1.96). VAL +423 -> +465 (t
  1.37 -> 1.61) / +389 -> +431. Random: 100 % in both eras.
- **For the coordinator's HOLD build of K2** (no HOLD was looked at):
  - The prereg builds HOLD events from the current `/v1/market/all`. That misses renamed and delisted markets in
    the same way.
  - Cross-checking against Upbit's KRW-addition notices (W's notice JSON) would make the HOLD list complete.
  - Delisted markets have no candles, so L must come from the notice body.

## Pitfalls met
- **Delisted markets.** Upbit's candles API answers 404 for delisted markets (SRM, SNX, STG, BONK, JASMY, OMNI, OXT,
  MATIC). Renamed markets keep their history under the new code, sometimes with prices rescaled: GAL -> G / 58.
- **Mixed notices.** "KRW, BTC 마켓 (A, B)" does not mean both coins got KRW. Candles, or the body, are needed per
  coin. J's count of 43 KRW events and the 9 "missing" ones mix these up.
- **Bodies.** Notice bodies were not in W's cache for any addition notice, and I did not fetch notices. So the stated
  opening times come from candles, partners, searches or the fallback.
- **The 200-candle window.** It cannot detect earlier existence of a liquid market. A separate `to = t - 1 h,
  count 1` request did that.
- **Local 1h perp files** are windows (round 63 B), so the random benchmark was filled from fapi 1h for the event
  coins.

## What a user decision could unlock
- **A forward paper log of non-KRW additions** (BTC / USDT market, first Upbit appearance) under the K2 rule, next
  to the K2 paper bot. It costs nothing extra. It cannot be promoted on this evidence, because IS failed.
- **Allow fetching the notice bodies** from api-manager.upbit.com (W already did it politely). That gives exact
  opening times for the delisted markets and fixes L for the 5 non-candle events. It would not change the verdict.

## Files
- **HYPOTHESES_M.md**, **STREAM_M.md**.
- **Events and probes:** additions_titles.csv, events_M.csv, events_build_output.txt, probe*.json / probe*_output.txt.
- **Results:** trades_output.txt, report_output.txt, random_M.json, random_output.txt.
- **Code (M/code/):**
  - titles.py, events.py (notices -> events);
  - fetch.py (Upbit fetcher and log);
  - perps.py (copy of W's);
  - k2rule.py (K2 copy);
  - run.py (trades, random, report).
- **Data (research/data/upbit_nonkrw/):** requests.log, raw/ (Upbit JSON), fapi_cache.json, trades.json,
  event_1h.json, perp1h_close.npz (86 MB, kept out of results/).
