# Round 40: global news event and tone flows (GDELT); Chinese margin-financing leverage, 2026-10-30

Brief: [round40_news_leverage/BRIEF.md](round40_news_leverage/BRIEF.md). Same LIVE / DEMO bars as rounds 25-39. HOLD
(2025-01..2026-09) stayed closed in stream G (no GDELT file after 20241231, IC cut at load). Stream C opened HOLD
once, for one cell the user approved on 2026-10-30 (registered before any 2025+ data was fetched; below).

## Answer
No LIVE or DEMO candidate. GDELT 1.0 daily events 2013-24 (36 GB, aggregated on the fly) carry nothing past the next
morning: country tone continuation has the wrong sign in IS, slope ~0 bp per sd against Tetlock's ~8. Chinese margin
deleveraging does not continue into HK50 / CNH; index CFDs rebound instead. The post-hoc HK50 rebound was registered
at the user's request and failed its HOLD look (net +19.0 bp, t 0.74 < 1.0): dropped for good.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| G | GDELT 1.0 daily Events export 2013-04..2024-12 (4,287 files, entry 08:00 UTC D+1 after the 07:00 stamp): country tone / Goldstein shocks (continuation and reversal), world tone -> BTC / XAU, producer-region conflict -> XBR / XAU, attention (share of world articles), US-China / Russia-Ukraine / Iran / Korea dyads, protests; index book (6), FX book (10); 82 declared cells | **none**: G1 tone continuation index book net IS -6.19 (t -2.45), FX -2.41 (t -2.06), wrong sign; best positive IS cell G2 producer conflict -> long XAU net +44.2 (t 2.67) on 22 trades, VAL -13.8, at chance (p 0.38 over 82); tone reversal and world-tone cells IS t < 2; G3a attention reversal IS t 1.78 is 2020 (ex-2020 0.90) | [STREAM_G.md](round40_news_leverage/STREAM_G.md), [HYPOTHESES_G.md](round40_news_leverage/HYPOTHESES_G.md) |
| C | Eastmoney SSE + SZSE margin financing / securities lending 2010-03..2024-12 (entry 01:45 UTC D+1): deleveraging -> continuation, leverage build-up -> reversal, short-sale surges, underwater / high-leverage variants -> HK50, USDCNH, AUDUSD, XAU, JP225; PRE 2012-15 on Dukascopy with and without 2015; 120 + 27 declared cells | **none**: primary C1 short HK50 h1 net IS -45.7 (t -2.73): the index rebounds; CNH / AUD weaken only in VAL (PRE flat ex-2015); C3 short sales -> long XAU met the DEMO numbers (net IS +23.8, t 2.73 / VAL +8.9) but sits at the 120-cell chance median, PRE negative, VAL < 0 without its 3 best trades: draft not registered | [STREAM_C.md](round40_news_leverage/STREAM_C.md), [HYPOTHESES_C.md](round40_news_leverage/HYPOTHESES_C.md), [PREREG_DRAFT_C_xau_after_short_sales.md](round40_news_leverage/PREREG_DRAFT_C_xau_after_short_sales.md) |
| C, HOLD look | User-approved post-hoc rule C1_k1.5 -> LONG HK50 h1, registered 2026-10-30 17:12 UTC with frozen code (sha256) before any 2025+ fetch; pass = HOLD net > 0 and t >= 1.0; expected HOLD t 0.60 at VAL size, power 0.60 | **fail**: HOLD 24 trades / 17 episodes, net +19.0 bp (t 0.74); IS +35.4 (2.14), VAL +41.1 (0.77); pooled 2016-26 +33.2 (t 1.92). Dropped, no forward log | [PREREG_C1_hk50_rebound.md](round40_news_leverage/PREREG_C1_hk50_rebound.md) |

Correlation with C3: gold short-sale cell +0.11 daily; others not computed.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Machine-coded news (GDELT daily events: tone, Goldstein, attention, conflict in producer regions, dyads, protests)
  -> indices, FX, gold, oil, BTC from the next morning: aggregate news is priced before the file is public.
- Chinese margin financing and securities lending (deleveraging, build-up, short-sale surges) -> HK50, CNH, AUD, gold,
  JP225; the HK50 rebound after deleveraging days failed HOLD.

## Pitfalls
- GDELT 1.0 daily files are stamped D+1 07:00 UTC from 2015-08 (2014 up to 09:20; 2013 re-uploaded in 2014-02); two
  days 404 (2022-11-10, 2023-03-23). GDELT 2.0 15-minute history is ~345k files (>= 96 h politely); daily GKG ~78 MB.
- Parse lat / long as a pair (bad values -> NaN) and assert row alignment; some 2013 files have no valid rows.
- Long background pipelines: waits must also exit when a worker dies (a parser crash stalled stream G for ~6.5 h on
  10-29 / 10-30 while its waiters slept). The coordinator checks process and log progress, not only the agent.
- Eastmoney RPTA_RZRQ_LSHJ: 800 rows a page, 60-80 s a response, transfers can break mid-response; no robots.txt.

## Directions that need the user
| direction | value |
|---|---|
| GDELT 2.0 15-minute history (~96 h of polite requests, or BigQuery with a Google account) | LIVE < 1 %, DEMO ~1 % |
| Paid news sentiment (RavenPack, MarketPsych) | LIVE ~1 %, DEMO ~2 % |
| Wind / iFinD maintenance-ratio distribution and forced-liquidation volumes | LIVE < 1 %, DEMO ~2 % |

## State after round 40
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 41 opens next.
