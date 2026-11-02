# Stream B2 (round 66): Bithumb KRW-listing notice -> Binance perp within seconds. Stopped at step 1

Written Sun Nov 1 14:03:48 UTC 2026 (from `date -u`). No HOLD data, no aggTrade and no price were requested, loaded or
computed. No HYPOTHESES_B2.md was written, because the brief makes step 2 conditional on step 1.

## Answer first: none (no data source, the test was not run)
- I found no public, robots-allowed, keyless source of **Bithumb notice post times for 2020-24 with second
  precision**. The brief says to stop in that case, so stream B2 stops here.
- The only Bithumb host that holds the notice archive is **feed.bithumb.com**. Its robots.txt returned **403** to a
  plain `research-script` UA. Under the network rules a 403 means stop that host, and it was not touched again.
- **api.bithumb.com `/v1/notices`** is keyless and gives `published_at` with whole seconds (KST). But it serves only
  the latest notices (`count` <= 20), with no paging or time cursor, so it has nothing from 2020-24.
  It **is** the route for a future forward capture test.
- No events were built, so there is no median path, no cells, no verdict and no Upbit overlap. H's 99 events
  (H/h_events.csv) only have L to the hour (the first 60-min candle). That is not a notice time.

## What was checked (research/data/bithumb_notice/requests.log; 23 lines; raw copies in raw/)
| host | robots.txt | what I tried | result |
|---|---|---|---|
| feed.bithumb.com (notice board, `pc_url` of every notice) | **403** | nothing else | stop (rule) |
| cafe.bithumb.com (old notice board, before ~2023) | URLError x5 (no connection / DNS) | nothing else | host gone |
| api.bithumb.com | 404 (no file) | documented `GET /v1/notices?count=20`, then 6 undocumented params (`page=1`, `page=2`, `to`, `offset`, `cursor`, `category`) | `count=20` returns the 20 latest (all 2026-10); any extra param falls back to the default 5 latest. No history |
| apidocs.bithumb.com | 200, allows /reference | llms.txt, the "공지사항 조회" page | the endpoint has only `count` (1-20), limit 1 request / s per IP, "newest first by published_at" |
| www.bithumb.com / m.bithumb.com | 200, allow all | sitemap.xml (2,113 URLs), /react/feed/event, main JS bundle | the SPA's `/feed/*` route has only `event` and `event/:id`. Notices link out to feed.bithumb.com. No notice API on www |
| gw.bithumb.com | 404 | nothing else | no route found |

- **Pace.** Bithumb hosts were hit >= 1 s apart. There were no 418 / 429 responses and no e-mail in any request.
- **WebSearch.** 4 searches (GitHub / dataset / Korean queries). The results show:
  - live scrapers of feed.bithumb.com (e.g. github.com/yukionfire/bithumb_notice, keeps 1 year, no archive committed);
  - paid feeds (Apify, CryptoCurrencyAlerting);
  - news articles (minute or date precision, not an allowed host).
  None is an allowed, point-in-time 2020-24 archive with seconds.

## Why I did not use a substitute
- **Inferring N from the Binance burst** (or from Bithumb 1m candles) defines the notice time from the price it is
  meant to predict. That is circular, and it removes the stamp check the brief asks for.
- **Using L** (Bithumb's first KRW candle, hour precision in H) is H's rule, which already failed. It is not a
  seconds-after-notice trade either.

## What a user decision could unlock
1. **Forward capture (no account needed).**
   - Poll `https://api.bithumb.com/v1/notices?count=20` at >= 1 s (the documented limit), e.g. from a Tokyo VPS.
   - Log first-seen time vs `published_at` and the Binance aggTrade burst for each `마켓추가` notice from 2026-11 on.
   - This builds a clean point-in-time event set for a FORWARD registration of A2-D5L on Bithumb. The pace is
     ~25 perp-coin listings a year (H's 2023-24 count), so power 3 would take years unless the per-trade SR is far
     above A2's 0.31.
2. **Access to feed.bithumb.com.** The archive is there. Reading it would need the user to obtain permission or an
   allow-listed UA from Bithumb. That is not something to work around.
3. **A licensed historical dataset** (e.g. CryptoCurrencyAlerting's listing history) would need payment, which is a
   user decision. Check first that its stamps are point in time and have seconds.

## Problems / notes
- One response (`count=20`) printed 2026-10 notice titles and stamps to the terminal while checking the format. It
  holds no prices and was used for nothing except the format check (20 / 20 `YYYY-MM-DD HH:MM:SS`).
- No background process was started.

## Files
- **This folder:** STREAM_B2.md.
- **Code (code/):**
  - net.py: polite fetcher, log, 1 s per Bithumb host.
  - robots.py, g.py: the probes.
- **Data:** research/data/bithumb_notice/requests.log, plus raw/: robots files, apidocs pages, notices_p1 / p2 json,
  sitemap, feed/event html, main JS.
