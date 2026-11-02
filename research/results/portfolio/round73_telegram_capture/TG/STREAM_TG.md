# STREAM_TG: public Telegram reposts of Upbit notices as a keyless capture route for A2-D5L

Written 2026-11-02 03:31 UTC (`date -u`). Scouting and latency measurement only: no P&L, no prices, no HOLD.
Pre-registration: HYPOTHESES_TG.md (02:52 UTC, before any fetch).

## Answer first
- **Not established; borderline.** The decision rule in HYPOTHESES_TG.md is not met, because the preview delay was not
  observed (no post arrived during either probe). The tested 2 s poll also models below 80 % from this Mac.
  - The channel is fast enough. The official Upbit channel **@upbit_news** reposted **100 % of KRW-listing notices**
    (124 / 124) since it went live (2025-08-20).
    - 95 % of them were stamped **<= 2 s after N**; in 2026, 80 / 80 were stamped <= 1 s.
    - No post was stamped before N.
  - The t.me/s web preview is keyless, `cache-control: no-store`, and has not rate-limited us so far:
    - 2 x 60 polls at 2 s on one keep-alive connection: all 200, response 0.48 s median.
    - 833 paging requests at 0.9 req/s over 15 min: no 429.
  - The weak link is the poll period and the network round trip (model: channel lag + poll phase U(0,T) + response
    time; unmatched notices count as misses):

    | @upbit_news, share seen <= 3 s after N | T = 1 s | T = 1.1 s | T = 1.5 s | T = 2 s | T = 3 s |
    |---|---|---|---|---|---|
    | since 2025-08-20, Mac RTT (0.48 s) | 89 % | 88 % | 82 % | **71 %** | 50 % |
    | 2026, Mac RTT | 96 % | 95 % | 89 % | **78 %** | 55 % |
    | since 2025-08-20, poller near Telegram (0.1 s) | 93 % | 93 % | 90 % | 84 % | 63 % |
    | 2026, poller near Telegram (0.1 s) | 99 % | 99 % | 97 % | 90 % | 68 % |

  - So a keyless poll of `t.me/s/upbit_news` every ~1-1.5 s from one IP plausibly meets "<= 3 s on >= 80 %", **if**:
    - the preview shows a new post at once (not observed);
    - Telegram tolerates ~1 req/s 24/7 from one IP (only 15 min was observed).

    At 2 s it fails from this Mac (71-78 %) and passes only from a host near Telegram's servers.
- No third-party repost channel beats the official one. Every third-party channel is 0.3-1 s slower; at T = 2 s they
  model at 33-58 %.
- **A route that needs an account (user decision):** a Telegram user account with an MTProto client (e.g. Telethon)
  subscribed to @upbit_news.
  - Updates are pushed, so there is no poll term. End to end it is about the channel lag (100 % <= 2 s stamped in
    2026) plus a sub-second delivery.
  - It would comfortably pass on history.
  - The Bot API is not a route: a bot cannot read a channel it does not administer.
- **Cheapest next step (user decision; it exceeds this brief's 60-request probe cap):** a forward logger that polls
  `t.me/s/upbit_news` at 1.1-1.5 s from one IP.
  - It logs first-seen time vs N for every new post, for 2-3 days. @upbit_news posts about 4 notices / day, so roughly
    10 posts would also measure the preview delay.
  - It would settle both open conditions (preview freshness, sustained allowance) before A2's promotion test.

## 1. Candidate channels (11 / 15 WebSearch used)
| handle | owner | t.me/s history | content | effective start |
|---|---|---|---|---|
| @upbit_news | **official** (Dunamu; announced 2025-08-22) | yes, full (id 1..2049) | every Upbit notice, `[category] title` + link | 2025-08-20 (id 1 "Channel created" 2025-05-02, nothing until id 106) |
| @newlistingsfeed | third party (newlistings.pro; paid WebSocket bot, "Plus" channel) | yes, full | listings on many venues, `$X listed on Upbit spot (KRW)` | 2024-03-16 |
| @coin_listing | third party (paid WS bot @coinlisting_ws_bot) | yes, full | `[UPBIT] $X listed on Upbit (KRW)`; newer posts print a ms detection time | 2017-10-11 |
| @CLWfeed | third party (cryptolisting.ws; free feed "delayed by 150ms", paid WS) | yes, full | `UPBIT Listing – $X`, `Detected (UTC): ...µs` | 2026-06-16 |
| @BWEnews | third party news (方程式新闻) | yes; paged 250 pages back to 2022-12-16 only | mixed news incl. Upbit listings | (cap) |
| @upbit_bim "업비트 공지알람" | unknown; one listing site labels it [FAKE] | **no preview** (0 posts shown) | - | - |
| @UpbitGlobal_Official | Upbit Singapore | not fetched | SG market news, not KRW notices | - |

Others seen in search but not channels a keyless reader can use: DWF Labs listing bot (a bot, needs an account), PKCryptolisting / Apify
monitors / Tokenearly (paid or keyed services), Bithumb official alert channel (not Upbit).

## 2. Historical lag (lag = Telegram post stamp - N, whole seconds)
Notices: 302 KRW-listing notices from the read-only cache `research/data/upbit_notices/raw/list_all` (A2's title
filter from `fwd_a2.build_events`; ends with NIL 2026-10-27). Match = earliest post in [N - 1 h, N + 24 h]:
- contains a ticker of the title (short tickers only as `$X`, `(X)` or `X listed`);
- mentions Upbit / 업비트 (not required for the official channel);
- has no delisting / warning words, and is not a 마켓 post without KRW / 원화.

Shares are of all notices in the window, so misses count as > 3 s.

| channel | window (N, UTC) | notices | matched | median s | p80 s | p90 s | <=2 s | <=3 s | before N | >60 s |
|---|---|---|---|---|---|---|---|---|---|---|
| upbit_news | since start 2025-08-20 | 124 | 124 (100%) | 1 | 1 | 2.0 | 95% | 95% | 0 | 3 |
| upbit_news | 2026 | 80 | 80 (100%) | 1 | 1 | 1.0 | 100% | 100% | 0 | 0 |
| upbit_news | since 2026-06-16 | 43 | 43 (100%) | 1 | 1 | 1.0 | 100% | 100% | 0 | 0 |
| newlistingsfeed | since start 2024-03 | 199 | 188 (94%) | 1 | 2 | 3.3 | 78% | 85% | 0 | 10 |
| newlistingsfeed | since 2025-08-20 | 124 | 124 (100%) | 1 | 2 | 2.0 | 95% | 98% | 0 | 3 |
| newlistingsfeed | 2026 | 80 | 80 (100%) | 1 | 2 | 2.0 | 95% | 99% | 0 | 1 |
| coin_listing | since start 2017-11 | 281 | 211 (75%) | 1 | 2 | 4.0 | 60% | 67% | 0 | 2 |
| coin_listing | since 2025-08-20 | 124 | 121 (98%) | 1 | 2 | 3.0 | 86% | 92% | 0 | 0 |
| coin_listing | 2026 | 80 | 78 (98%) | 1 | 2 | 3.0 | 81% | 89% | 0 | 0 |
| CLWfeed | since start 2026-06-19 | 42 | 42 (100%) | 2 | 2 | 2.0 | 90% | 95% | 0 | 0 |
| BWEnews | since 2023-01 (paged) | 213 | 195 (92%) | 2 | 3 | 3.0 | 62% | 83% | 0 | 0 |
| BWEnews | since 2025-08-20 | 124 | 124 (100%) | 2 | 3 | 3.0 | 78% | 97% | 0 | 0 |
| BWEnews | 2026 | 80 | 80 (100%) | 2 | 3 | 3.0 | 74% | 95% | 0 | 0 |

- @upbit_news lag values: 0 s 27 times, 1 s 81, 2 s 10, 4 s 1 (F, 2025-10-21), 52-62 s 5 times (AERO, TREE, WLFI, USD1, RED,
  all within the channel's first two weeks, 2025-08-22..09-05).
  - Since 2025-09-06: 118 / 119 <= 2 s.
  - Before 2025-08-20 the channel posted nothing, so those 23 notices are outside its life, not misses.
- Sub-second stamps printed inside third-party posts (detector time) show when a notice first becomes visible to
  outside pollers:
  - CLWfeed: detect - N median 1.27 s (p90 1.71, min 0.57, max 3.09; n 42). Telegram stamp - detect median 0.63 s.
  - coin_listing: detect - N median 0.86 s (p90 1.56, min 0.33; n 27). Telegram stamp - detect median 0.23 s.

  No outside detector beats ~0.3 s after N. The official channel's 0-1 s stamps are as fast as the best detectors.
- Posts before N: none. One coin_listing match 296 s before N (AGLD, 2024-11-13) was a USDT-market post, a matcher
  false positive, and was removed by the KRW rule.

**What whole-second stamps mean for a 3 s gate.** N (`first_listed_at`) and the Telegram `<time datetime>` are both
whole seconds, so a measured lag L means a true lag in (L - 1, L + 1).
- L <= 2 guarantees < 3 s.
- L = 3 is ambiguous (2-4 s).
- The "<= 2 s" column is therefore the safe count, and "<= 3 s" an optimistic one.

The end-to-end model draws the true lag as L + U(0,1) - U(0,1) (resampled to >= 0). Telegram stamps the time a post is
created, not the time it shows in the preview; that preview delay is the one term not measured.

## 3. Live refresh probe of t.me/s (best 2 channels)
`https://t.me/robots.txt` returns 404 (no rules); it was logged first. Every request used the default Python UA, no
browser headers and no e-mail, from one IP (Mac, residential).

| probe | period | requests | status | response time | new posts seen | headers |
|---|---|---|---|---|---|---|
| upbit_news 03:08:36 UTC | 2 s | 60 / 60 | all 200 | median 0.477 s, p90 0.587, max 1.43 | none (top id 2049 throughout) | `cache-control: no-store` |
| newlistingsfeed 03:26:54 UTC | 2 s | 60 / 60 | all 200 | median 0.481 s, p90 0.612, max 1.23 | none | `no-store` |

- **Allowance:** no 429 or non-200 in 1,229 t.me requests.
  - Pager, keep-alive: 833 requests in 15.3 min at 0.905 req/s, median gap 1.10 s, max 2.94 s.
  - The first pager opened a new TCP/TLS connection per request. It met a **~16.5 s stall about every 15-20
    requests** (29 stalls in ~390 requests), with no error code. Over one keep-alive connection, stalls vanished.
  - A poller must therefore reuse one connection. It is unknown whether ~1 req/s holds for hours or days.
- **Preview freshness:** not observed. @upbit_news posts ~4.3 times a day, mostly 01-10 UTC, so a 2-minute probe had
  ~1-2 % odds of seeing one. `no-store` points to a page built per request, but this is not proof that the page is
  fresh.

## 4. Verdict on the brief's question
End to end = channel lag + preview delay + poll period / 2 (+ response time).
- For @upbit_news: ~1 s + (unknown, assumed 0) + T/2 + 0.48 s.
- Gate "<= 3 s on >= 80 %":
  - T <= 1.5 s from this Mac: 82-96 %, depending on window.
  - T = 2 s: 71-78 % from this Mac; 84-90 % from a poller near Telegram's servers.

The third-party channels cannot meet the gate keyless:
- At T = 1 s they model 49-79 % from this Mac (newlistingsfeed 75-79 %, coin_listing 70-76 %, CLWfeed 54 %, BWEnews 49-53 %).
- At T = 2 s: 33-58 %.

So the one plausible keyless route is @upbit_news via t.me/s at ~1-1.5 s, conditional on two facts not yet observed.
The account route (MTProto client on a user account) needs no polling and passes on history; it is a user decision.

## Pitfalls / caveats
- Telegram's stamp is the creation time; preview visibility and MTProto push delivery add unmeasured delays.
- The response times are from a residential Mac in Vietnam; agentFx (Helsinki) is not measured. Run nothing at
  t.me from agentFx without checking: Upbit already blocks that IP, and Telegram's rules for servers are unknown.
- The sustained allowance was observed only for 15 min at 0.9 req/s and 2 min at 0.5 req/s. A 24/7 poller may draw a
  limit later. Rotating IPs to dodge one is not allowed.
- The matcher depends on tickers in titles. The A2 filter's pre-2019 notices have Korean-name-only titles, so old
  coin_listing stats undercount. All 2025-26 rows were checked against misses: 3 coin_listing misses in 2026, none for
  upbit_news / newlistingsfeed / BWEnews.
- The channel's history is public, but its reliability is a single-operator risk (Upbit itself). The channel went
  silent for 3.5 months after creation, and its first two weeks had ~1-minute lags.
- @upbit_bim has no public preview and is flagged fake by a listing site; it was not used.

## Files
- TG/HYPOTHESES_TG.md, TG/STREAM_TG.md, TG/summary_table.txt, TG/e2e.txt, TG/lag_<channel>.csv (5 channels).
- TG/code/:
  - fetch and probe: tg.py (fetcher, 1.1 s gap lock, keep-alive, log), pageback.py, probe.py;
  - parse and analysis: parse.py (stdlib HTML parser), notices.py (A2 filter), analyze.py (matching), summary.py,
    e2e.py (end-to-end model);
  - helpers: clw_detect.py, peek.py, posttimes.py.
- research/data/telegram_upbit/:
  - requests.log (1,229 requests: 1,228 x 200, robots 404);
  - raw/<channel>/b*.html (116 MB, untrusted, parsed with `python -I`);
  - probe_upbit_news_20261102T030836.csv, probe_newlistingsfeed_20261102T032654.csv;
  - pageback1.out, pageback2.out.
