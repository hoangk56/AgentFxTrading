# STREAM_C: HK CBBC mandatory-call clusters -> HK50

Written 2026-11-01 11:37 UTC. Plan: HYPOTHESES_C.md (written before any return; none was computed).

## Answer
**None. The stream stopped at the data gate.** There is no free point-in-time history of HSI CBBC **call levels**
for 2016-24 that can be pulled within the brief's limits.

Street quantities do have a free, point-in-time history. Every issuer files a daily trading summary on hkexnews
(XLS, with out-in-market units and total issue size per CBBC, from at least 2016-03), but these files carry no call
level. Call levels exist only per CBBC: in launch announcements, which the hkexnews search does not index and which
sit on issuers' own websites, and on HKEX summary pages, which are kept for live or just-expired CBBCs only.

No backtest, cell verdict, random benchmark or PREREG_DRAFT exists.

## What was checked
All requests went through agentFx with curl (UA `research-script`, >= 1.2 s apart). There were 22 requests and 0
errors, logged in research/data/hk_cbbc/requests.log. I used 2 WebSearch.

| source | result |
|---|---|
| www.hkex.com.hk/robots.txt | 200. It disallows only the Listing-Rules contingency paths. |
| www1 / www.hkexnews.hk/robots.txt | 404 (no rules). |
| HKEX `/eng/cbbc/mce/mce.htm` | MCEs of the latest day only ("Updated: 30 October 2026"), with call level and listing date. |
| HKEX `/eng/cbbc/newissue/newlist.htm` | "past month" only. Has call level and total issue size: 2,401 CBBCs, 1,560 of them on HSI. No archive selector. The one download is the current `.xls`. |
| HKEX `/eng/cbbc/expire/expired.htm` | "past month" only (including MCEs). Has call level and last trading date, but no size. No archive. |
| HKEX `cbbcsummarydelist.asp?id=` | id 435594 (expired 10-2026) has full terms: call, strike, launch, size. ids 300000, 430000 and 435000 return an empty template (4,944 B). Old CBBCs are not kept. |
| HKEX `/eng/ods/historicalData.aspx` | "Securities Attribute" daily / monthly CSVs (CBBC call price plus outstanding) are **paid** products (J and WebSearch). |
| hkexnews `titleSearchServlet.do`, title "Bull", 2016-03-08 and 2018-06-12 | 14 and 17 XLS per day: "Daily Trading Summary" and "Pre-Listing Trading Summary" of CBBCs from about 11-13 issuers. |
| hkexnews daily summary XLS (SG, GS, BNP, HSBC, JPM 2018-06-12) | HKEX template with columns: short name, code, bought, avg price, sold, avg price, **units still out in market**, total issue size, % out, currency, active-quote flag. **No call level, no strike, no ratio.** The files are OLE2 BIFF8 (SG, HSBC, JPM, BNP) or XML Spreadsheet 2003 (GS pre-listing). C/code/xls.py parses both with the stdlib only. |
| hkexnews title "Launch", 2018-06-12; all 314 docs that day | No CBBC launch announcement is indexed. The day's only structured-product docs are the DW / CBBC trading reports. |
| hkexnews `prefix.do?type=I&name=57166` | Inactive CBBCs keep a stockId (SG#HSI RP1808Z = 179605; codes are reused). |
| hkexnews title search, stockId 179605, 2017-18 | 0 documents. The per-CBBC listing documents are not on hkexnews. |
| WebSearch | Launch announcements are "hkexdoc" PDFs on issuer sites (warrants.ubs.com, warrants.hsbc.com.hk). warrants.com.hk shows a live call-level distribution only. No free historical dataset was found. |

## Why the remaining routes do not fit
- **Street quantities alone.** About 12 issuer files a day x ~2,230 HK trading days in 2016-24 is ~27,000 requests,
  or ~9 h at 1.2 s per request. That is 12 times the 45-minute pull limit, and the call levels would still be
  missing.
- **Call levels from launch PDFs.** At ~1,000-1,500 new HSI CBBCs a month (1,560 in the past month), 2016-24 has
  roughly 100k+ CBBCs. Their PDFs are spread across ~13 issuer websites with no common index, each website has its
  own robots.txt, and the PDFs need a text extractor that is not in numpy / stdlib. This does not fit the limits.
- **Call levels inferred from prices.** For a bull CBBC, strike ≈ HSI − avg price x ratio. The average price is
  taken at an unknown time of day: an error of about ±150-300 HSI points, against a call-to-strike gap of ~100
  points and the 100-point bands the rule needs. The ratio is also not in the file. This proxy would blur exactly
  the band the hypothesis is about.
- **Power, even with data.** At J's estimate (Sharpe 0.08-0.16 per trade, ~270 HOLD trades), HOLD power is 1.3-2.6.
  LIVE needs net Sharpe >= 0.18 per trade, so DEMO is the realistic ceiling.

## What a user decision could unlock
1. Buy HKEX's Securities Attribute monthly files for 2016-24: CBBC call level and outstanding units by day. The
   step-2 plan in HYPOTHESES_C.md (12 cells) would then run in one session.
2. Allow a long, slow pull of the issuer daily summaries (~9 h at 1 request per 1.2 s, from agentFx), plus a
   call-level source such as option 1 or issuer PDFs. Street units alone are not enough.
3. Start a forward archive now. Snapshot newlist / expired / MCE and the daily summaries each evening. This gives
   only a live-era test, with no IS, so it cannot be registered under the current bars.

## Pitfalls noted
- Codes are reused: the same code 57166 has been ten different CBBCs. Key any panel on hkexnews stockId or on the
  (code, name, listing date) triple.
- Daily summaries are filed in the evening of trade date D (17:00-22:30 HKT). Use them for day D+1 only.
- I fetched HKEX's current CBBC pages (2026 content) only to check retention and column headers. Their bodies were
  deleted after the check (noted in requests.log). No 2025-26 price or CBBC value was summarised.
- HK50 M1 was not loaded.

## Files
- research/results/portfolio/round65_retail_venues/C/HYPOTHESES_C.md, STREAM_C.md
- C/code/fetch.sh (agentFx fetch plus log; leaves nothing on agentFx), C/code/xls.py (stdlib BIFF8 reader)
- research/data/hk_cbbc/requests.log, plus raw/ probes (robots, 2016 and 2018 title-search JSON, six 2018-06-12
  issuer XLS, empty delist templates)
