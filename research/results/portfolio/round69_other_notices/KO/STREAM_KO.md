# Stream KO (round 69): listing notices of Coinone, Korbit, GOPAX at seconds. Stopped at step 1

Written Sun Nov 1 16:25:11 UTC 2026 (from `date -u`). No HOLD data, no aggTrade and no price were requested, loaded
or computed. No HYPOTHESES_KO.md was written, because the brief makes step 2 conditional on step 1.

## Answer first: none (no allowed data source, the test was not run)
I found no public, robots-allowed, keyless source of **2020-24 notice post times with second precision** on any of
the three venues. The brief says to stop in that case, so stream KO stops here.

- **Coinone:** the notice board is on coinone.co.kr, and its robots.txt says `User-agent: * Disallow: /`. Only named
  crawlers are allowed (Googlebot, Yeti, Claude-User and others), and a plain `research-script` UA is not one of them.
  The keyless public API (api.coinone.co.kr, robots 404) has no notice endpoint: docs.coinone.co.kr/llms.txt lists
  markets, chart, ticker, orderbook, trades, currencies and private endpoints only.
- **Korbit (now "Digital X", Mirae Asset):**
  - The official keyless `GET /v2/notices` (api.digitalx.miraeasset.com, formerly api.korbit.co.kr) returns only the
    **20 most recent** notices, takes no parameters and has no paging. `createdAt` is in ms, but it is the creation
    time, which may not be the publish time.
  - Its robots.txt answered **503** three times, as api.korbit.co.kr did in round 65 and again now. An unreachable
    robots file counts as "disallow", so the endpoint was not called.
  - The full archive is behind the web app's proxy, `portal-prod.korbit.co.kr/api/korbit/v2/contentful?...`
    (Contentful). That host rejects requests without a `platform-identifier` header ("invalid platform-identifier").
    The web bundle fills that header with the mobile app's ids (`rn_android` / `rn_ios`, `korbit_platform_id` 21/41).
    Sending them would mean claiming to be Korbit's app, so it was not tried.
- **GOPAX:** www.gopax.co.kr robots.txt returned **403** (CloudFront "Request blocked"). The host was stopped and
  added to blocked_hosts.txt. api.gopax.co.kr, which serves the documented `/notices` endpoint, was already 403 in
  round 65 and was not retried. gopax.co.kr does not resolve (URLError x3).
- **Results:**
  - Events, median path, verdict: none. There are no events, so there is no path, no cell and no Upbit overlap.
  - Power: 0.
  - PREREG_DRAFT: none.

## What was checked (research/data/ko_notices/requests.log, 26 lines; bodies in raw/)
| host | robots.txt | tried | result |
|---|---|---|---|
| coinone.co.kr, www.coinone.co.kr | 200: `*` disallow all | nothing else | stop (rule) |
| api.coinone.co.kr | 404 (no file) | no call needed: the docs show no notice route | no history |
| docs.coinone.co.kr | 200, allow (except /api-next) | llms.txt | no notice endpoint |
| www.korbit.co.kr / korbit.co.kr | 200, allow (except /auth, /balance, /activity) | home, /notice/, sitemap index, `_app` JS bundle | static Next.js export (no notice data in the HTML); notice data comes from portal-prod |
| portal-prod.korbit.co.kr | 400 "invalid platform-identifier" | nothing else | needs app-impersonating headers: not used |
| api.korbit.co.kr | 503 x3 | nothing else | treated as disallowed |
| api.digitalx.miraeasset.com | 503 x3 | nothing else | treated as disallowed; docs say 20 latest only anyway |
| docs.korbit.co.kr | 200, allow | llms.txt, rest_api/other.md | `/v2/notices`: 20 latest, no parameters |
| digitalx.miraeasset.com | 200, allow (same file as www.korbit) | robots only | - |
| www.gopax.co.kr | **403** | nothing else | stop (rule) |
| gopax.co.kr | DNS error x3 | - | host gone |

- **Pace and identity.** Requests were >= 1.5 s apart per host and backed off on 503 (20 s, 40 s). There were no
  418 / 429 responses. Every request used the plain UA `research-script`, with no e-mail, cookie or key.
- **WebSearch:** 2 of 15. Neither search found a Coinone notice API or an allowed 2020-24 archive. They only turned
  up API wrappers and a Bithumb live scraper.

## Why I did not use a substitute
- **Inferring N from the Binance burst or the venue's 1m candles** defines the notice time from the price it should
  predict. That is circular, and it removes the stamp check.
- **Coinone's first candle (round 65 I, hour precision)** is a listing time, not a notice time. Its examples showed no
  pump anyway (median +1.0 %).
- **News articles** do not qualify: they are not an allowed host, and they give minutes at best.

## What a user decision could unlock
1. **Korbit forward capture.** If api.digitalx.miraeasset.com's robots.txt starts answering (or the user accepts its
   documented public endpoint as allowed), poll `/v2/notices` at a polite pace. Log first-seen time against
   `createdAt` and the Binance burst. Korbit lists few coins a year and has a small share of Korean volume, so power 3
   would take years.
2. **Korbit archive via portal-prod.** This needs the user to get Korbit / Digital X's permission, or to accept sending
   the web app's platform headers. I would not do that without an explicit OK.
3. **Coinone.** Its robots.txt allows only named crawlers. Reading the notice board needs the user's OK to use an
   allowed agent identity, or permission from Coinone. Coinone's history also has the overlap problem: 66 % of its
   coins are also Upbit KRW markets (round 65 I).
4. **GOPAX.** Both hosts return 403. Nothing can be done without permission.

## Problems / notes
- No background process is left running. The two robots probes that hit the 503 back-off ran past the 120 s
  foreground limit and finished in the background; both have exited.
- The Korbit `_app` bundle (711 kB) is kept in raw/ only to document the endpoint and header lookup.

## Files
- **This folder:** STREAM_KO.md.
- **Code (code/):** net.py, a polite fetcher (1.5 s per host, log, 403 = block host, 503 back-off).
- **Data (research/data/ko_notices/):** requests.log, blocked_hosts.txt (www.gopax.co.kr), and raw/ (robots files,
  Korbit home / notice HTML, sitemap index, `_app` JS, Coinone / Korbit llms.txt, Korbit other.md).
