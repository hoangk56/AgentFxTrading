# Stream JP (round 69): seconds after Japanese venues' listing notices. None

Written Sun Nov 1 17:17:11 UTC 2026 (from `date -u`). The events, rule, costs and power were declared in
[HYPOTHESES_JP.md](HYPOTHESES_JP.md) at 17:11:57 UTC, before any aggTrade was downloaded. HOLD (2025-01-01..) was
never requested, loaded or counted: every event has N, L < 2025-01-01, only daily files dated 2020-07..2024-11 were
pulled, notice rows dated >= 2025 were dropped unprinted, and every kline series was cut at ts < 2025-01-01 at load.

## Answer first
- **Step 1 passed for two venues.**
  - **bitbank** has its full 2020-24 notice history on bitbank.cc/blog, robots-allowed, with `publishedAt` to the
    second.
  - **Coincheck** has the same on corporate.coincheck.com /press and /news (CMS `publishedAt`, seconds). Its 2020 to
    mid-2021 press stamps all sit at 10:00:00 JST, a fixed release time or a date-only placeholder (flagged `P10`).
  - **GMO Coin:** no pre-2026 notice archive.
  - **bitFlyer:** host times out from this network.
  - **BITPoint:** robots.txt 403, so I stopped there.
- **Japanese listing notices do not move the Binance perp.** There are 43 events: IS 9 on 9 days, VAL 34 on 24 days.
  - The median alt-vs-BTC path since N - 60 s, in VAL: 0 s -1 bp, +1 s -1, +2 s -1, +5 s 0, +10 s 0, +30 s +1,
    +60 s 0, +300 s +2.
  - In IS: +5 s +4, +30 s +16, +60 s +8, +300 s -1.
  - **No event reaches +2 % within 300 s.** Two IS events cross +0.5 %, both about 280 s before N (moves already under
    way). The alt trade count in the first minute is 0.93x the pre-N rate (VAL median).
  - So the stamps cannot be confirmed from the tape. There is no burst to line them up with.
- **A2-D5L frozen:** long alt / short BTC at the first trades >= N + 5 s, exit at the venue's trading start L.
  - **IS: +1,898 bp net, t 1.62**, n 9 (9 days), median +222, SR 0.54, beats 98.6 % of random entries. Years: 2020
    -195, 2021 +2,945.
  - **VAL: +36 bp, t 0.26**, n 34 (24 days), median +26, SR 0.05, beats 77.2 % of random entries. Years: 2022 +317,
    2023 +4, 2024 -672.
  - **HOLD power at VAL size: 0.05 x sqrt(21) = 0.23.**
  - **Verdict: none.** IS t < 2.0 fails DEMO and LIVE. VAL random 77 % < 90 % and VAL t 0.26 < 1.5. No PREREG_DRAFT.
- **The IS mean is multi-day 2021 alt drift, not a notice effect.**
  - Holds are 3-15 days, and one event (Coincheck ENJ, 2021-01-19 → 01-26, P10 stamp) carries +10,277 bp.
  - Without it (post hoc), IS is +851 bp, t 1.44, median +99. Without all P10 stamps: n 5, +1,338 bp, t 1.48.
  - The 5-minute version of the same trade loses its costs in both eras, because its gross is about zero:
    - D5-5m: IS -26 bp (t -4.9), VAL -17 bp (t -5.6).

## Step 1: what was checked (research/data/jp_notices/requests.log, 1,819 lines)
| venue | host / robots.txt | notice source found | post time | 2020-24 coverage | verdict |
|---|---|---|---|---|---|
| bitbank | bitbank.cc: only `/account/` disallowed | `/blog/tags/information?page=N` (59 pages) and `/blog?page=N` (109 pages, every tag), server-rendered: `<time dateTime=publishedAt>`, title, summary | seconds (pre-2024-08 rows carried over from the old CMS: e.g. 2022-03-24T01:56:53Z; 42 % of 2020-24 rows at second :00, 27 % at hh:00:00 = scheduled posts or minute-only) | 587 rows 2019-12..2024 | **used** |
| bitbank | support.bitbank.cc (Zendesk) API allowed | FAQ only, no notice section | - | - | not a notice source |
| Coincheck | coincheck.com: `Disallow: /api`; `/ja/info`, `/ja/announcements` 404 | no notice list on the main site | - | - | not used |
| Coincheck | corporate.coincheck.com: allows `/news`, `/press`; disallows `/2017/`..`/2021/`, `/archive`, `/en` | one page per post from the news (1,183) and press (320) sitemaps; NUXT payload gives `publishedAt` / `createdAt` / `updatedAt` | seconds; **press 2020 - mid-2021 at 01:00:00 UTC (96 % of 2020, 67 % of 2021)** | 589 news + 207 press rows 2020-24 | **used**, P10 flagged |
| GMO Coin | coin.z.com: `Allow: /` | `/jp/news/` WordPress, sitemap months 2026-02..2026-10 only; old お知らせ list not served (`wp-json` returns the HTML shell) | - | none | **no source** |
| bitFlyer | bitflyer.com, www.bitflyer.com: 7 timeouts (no TCP answer from this network); api.bitflyer.com robots 404 | not reachable | - | - | **no source** |
| BITPoint | www.bitpoint.co.jp robots.txt **403** | stop (rule) | - | - | **no source** |

- **Request pace.** Notice hosts were hit >= 1.5 s apart and data.binance.vision >= 0.3 s apart.
- **No blocks met.** There were no 418 / 429 responses. The 403 host (BITPoint) is in blocked_hosts.txt and was not
  retried.
- **Clean requests.** Plain UA `research-script`, no e-mail, no key.
- **Web searches.** 3 of 15 were used.

## Events (code/events.py; frozen in HYPOTHESES_JP.md)
- **N:** the post stamp of the venue's first notice that it will list a new coin. **L:** the stamp of its own "trading
  started" notice.
  - For 7 Coincheck same-day notices with no later clock time (OMG, SAND, IMX, APE, AXS, AVAX, SHIB), L = N + 60 min.
  - Holds: bitbank 50-314 h; Coincheck 1 h or 95-357 h.
- **Screen:** perp >= 7 d at N and still trading at N + 1 d.
  - Dropped: XYM, BOBA, FLR, OAS, DAI, PLT, FNCT, WBTC, BRIL, BC (no perp); bitbank ASTR and Coincheck QTUM (perp
    < 7 d).
- **IS:** bitbank XLM, QTUM, BAT, OMG, LINK; Coincheck BAT, IOST, ENJ, OMG (all P10).
- **VAL:** bitbank 23 (MKR, ENJ, MATIC, DOT, DOGE, ADA, AVAX, AXS, SAND, APE, GALA, CHZ, MANA, GRT, RNDR, BNB, ARB, OP,
  KLAY, IMX, MASK, SOL, CYBER); Coincheck 11 (SAND, DOT, CHZ, LINK, MKR, MATIC, IMX, APE, AXS, AVAX, SHIB).
- **Upbit overlap:** none. No coin appears in an Upbit listing title within 7 days of N.
- **Perp age at N:** 112-1,527 d. These are mature large caps.

## Path (results.txt; bp, alt vs BTC since N - 60 s; q25 / median / q75)
| t - N | -10 s | -1 s | 0 | +1 s | +2 s | +5 s | +10 s | +30 s | +60 s | +300 s |
|---|---|---|---|---|---|---|---|---|---|---|
| IS (9) | -7 / 3 / 6 | -4 / 4 / 7 | -3 / 2 / 10 | -2 / 4 / 11 | -2 / 4 / 7 | -2 / 4 / 14 | 0 / 2 / 13 | 8 / 16 / 22 | -6 / 8 / 17 | -12 / -1 / 4 |
| VAL (34) | -3 / 0 / 3 | -4 / -1 / 3 | -4 / -1 / 3 | -4 / -1 / 3 | -4 / -1 / 4 | -4 / 0 / 4 | -6 / 0 / 3 | -6 / 1 / 3 | -8 / 0 / 3 | -4 / 2 / 15 |

- **Price onset (a).** No event reaches r >= +2 % within N ± 300 s; A2's VAL median onset was 0.7 s.
  - At r >= +0.5 % there are 2 IS events: Coincheck ENJ -276 s and OMG -300 s, moves under way before N. There are 0
    in VAL.
- **Trade-count onset (b).** 29 of 43 events have one, 83 % of them before N. It is the same noise A2 saw on thin
  books. The base rate is 0-20 trades / s, and the 10 trades / s floor triggers on random clusters.
- **Stamp vs burst.** There is no burst, so I cannot say whether the stamps (bitbank seconds, Coincheck seconds, P10
  10:00 JST) are the moment the public saw the notice. Either they are, and the market ignores JP notices, or the news
  reaches the market another way. Neither gives a seconds trade.

## Rule results (net bp per trade; 20 bp + slippage + real funding; t clustered by notice day)
| cell | era | n (days) | gross | slip | fund | **net** | **t** | median | SR | x1.5 | late (d 10) | years (net) | yrs + | rand % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D5-L** | IS | 9 (9) | 1924 | 4 | -2 | **1898** | **1.62** | 222 | 0.54 | 1886 | 1899 | 2020 -195 (3), 2021 +2945 (6) | 1/2 | 98.6 | |
| | VAL | 34 (24) | 46 | 1 | 11 | **36** | **0.26** | 26 | 0.05 | 26 | 37 | 2022 +317 (10), 2023 +4 (21), 2024 -672 (3) | 2/3 | 77.2 | **0.23** |
| D5-5m (descr.) | IS | 9 (9) | -5 | 1 | 0 | -26 | -4.94 | -26 | -1.65 | -37 | -26 | -16, -31 | 0/2 | | |
| | VAL | 34 (24) | 4 | 1 | 0 | -17 | -5.63 | -17 | -1.03 | -27 | -16 | -15, -19, -11 | 0/3 | | -4.68 |
| D2-5m (descr.) | VAL | 34 (24) | 4 | 1 | 0 | -17 | -5.63 | -17 | -1.04 | -27 | -17 | | 0/3 | | |
| D30-5m (descr.) | VAL | 34 (24) | 4 | 1 | 0 | -16 | -6.92 | -16 | -1.12 | -27 | -16 | | 0/3 | | |

- **Power** = SR x sqrt(n_HOLD), with n_HOLD = 34 / 3 years x 1.83 ≈ 21.
- **Random benchmark (declared change from A2).** Same coin, one random 1h-open entry per event within N ± 180 d. The
  hold matches the event's, and the whole hold lies outside [N - 7 d, L + 7 d] and before 2025. There are 1,000 draw
  sets.
  - The 95th percentile of the random net t is 1.43 (IS) and 1.05 (VAL). The IS t of 1.62 is only just above it.
  - KLAY and CYBER have sparse local 1h files, so they use daily opens with the hold rounded to days. This was forced
    by the data, not declared.
- **Bars.**
  - LIVE fails IS t (1.62 < 2.5), VAL t (0.26 < 1.5), random (77 % < 95 %) and power (0.23 < 3).
  - DEMO fails IS t (1.62 < 2.0) and random (77 % < 90 %).
  - VAL net > 0 and x1.5 > 0 pass, but only by +26-36 bp on a ~5 % per-trade noise.

## Why it fails
- **No reaction.** Japanese listings come 112-1,527 days after the coin has a Binance perp, and the coins are global
  large caps (ADA, DOT, SOL, BNB, AVAX, LINK).
  - A JPY spot listing on a venue that foreigners cannot use does not change global demand at the seconds scale.
  - Stream I found the same at the 1h / day scale (bitbank median -6 %).
- **The L exit is days later.** That turns the trade into a 3-15-day alt-vs-BTC bet.
  - In 2021 that bet paid because alts rallied: Coincheck ENJ +103 %, bitbank BAT +43 %, QTUM +20 %. The random
    benchmark (98.6 %) cannot remove a regime-wide alt rally inside a ±180-day window.
  - In 2022-24 the same bet is flat.
- **Few events and few days.** IS has 9 events on 9 days, and the 2020 events are slow or negative.

## Pitfalls met
- **Coincheck P10 stamps.** Press releases of 2020 to mid-2021 are stamped exactly 10:00:00 JST, so they are either a
  release-time policy or a migration default. The tape cannot decide, because nothing moves. A future Coincheck test
  should treat them as minute-level at best.
- **Hidden bitbank notices.** Two notices sit under the `maintenance` tag, not `information`: the GRT notice
  2023-06-12 and the MASK start 2024-02-08. Only the full `/blog` index finds them.
- **Coincheck has no keyless notice list.**
  - The corporate site is a Studio.design SPA whose lists load from a CMS API that needs a Firebase key, so I did not
    use it.
  - Instead I read one page per post from the sitemaps: 1,503 pages in ~40 min at 1.5 s per request.
- **Same-coin repeats across venues.** Several coins appear on both venues (BAT, OMG, ENJ, DOT, SAND, CHZ, LINK, MKR,
  MATIC, IMX, APE, AXS, AVAX). These are separate notices on separate days and are counted separately.
- **One parse deviation from A2's pull.** Whole-day zips were not parsed with `loadtxt`. A byte-offset binary search on
  `transact_time` extracts only the window lines, with the same columns and values. Overlapping windows on a day are
  merged, so there are no duplicate rows.

## What a user decision could unlock
- Nothing on the seconds scale: the market does not react to these notices.
- bitFlyer (unreachable from this network) could be checked from a Japanese or other host if the user wants
  completeness. Its listings are rarer still (about 9 markets) and the prior is the same.
- A multi-day "JP listing drift" test (N → L, 3-15 days) would be a different hypothesis: a regime-dependent alt beta.
  It would need its own registration and a beta-hedged benchmark. I do not recommend it on this evidence (VAL +36 bp).

## Files
- **This folder (JP/):**
  - HYPOTHESES_JP.md, STREAM_JP.md
  - results.txt, cells.json, trades.csv
- **Code (JP/code/):**
  - net.py: polite fetcher and log; 1.5 s per notice host; 403 stops the host.
  - probe.py, probe1.py: robots / page probes.
  - pull_bitbank.py: bitbank notice lists.
  - pull_coincheck.py, pull_coincheck_press.py: Coincheck news / press pages.
  - cc_titles.py, cc_bodies.py: Coincheck titles and stated start times.
  - events.py: frozen events and screen.
  - pull.py: aggTrades windows.
  - analyze.py: path, onset, rule, random benchmark.
- **Data (research/data/jp_notices/, 41 MB):**
  - requests.log, blocked_hosts.txt
  - bitbank_notices.csv, bitbank_all.csv
  - coincheck_news.csv, coincheck_press.csv (2020-24 rows only)
  - raw/: robots files, sitemaps, list pages, bodies
  - npz/: 139 window files, 7.4 MB. Zips were deleted.
- **Network totals:** 139 data.binance.vision daily files and 2 fapi fundingRate calls. No background process is left
  running.
