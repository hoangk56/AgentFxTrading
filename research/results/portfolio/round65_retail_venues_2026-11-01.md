# Round 65: retail-venue attention (H, U, I, W, J, A, C, R, E, M, A2), 2026-11-01

Shared brief: [round65_retail_venues/BRIEF.md](round65_retail_venues/BRIEF.md) (10:36 UTC; streams added as slots
freed). Question: does K2's mechanism (Korean retail chasing new Upbit KRW listings, then fading) generalise, so that
the number of independent HOLD-era events can grow? Subagents never opened HOLD; no PREREG was written this round.

## Answer first
- **No LIVE or DEMO candidate.** The listing chase is specific to Upbit KRW: Bithumb (+5.5 % pump before entry),
  Coinbase (round 64 L), seven other retail venues (I) and Upbit's own BTC / USDT markets (M) do not pump like Upbit
  KRW (+21.5 %). On Upbit itself the pump sits inside the notice minute (A), so only K2's later fade is tradable.
- K2 holds up on a survivorship check (M): adding the 4 KRW listings missing from K's list gives IS +961 bp (t 2.63,
  n 12), VAL +465 (t 1.61, n 32), vs registered IS +1,094 (t 3.16) / VAL +423 (t 1.37).
- **A2-D5L passed HOLD as DEMO** (added after the report was first written): long the Binance perp / short BTC at the
  first trades >= notice + 5 s, exit at the KRW open. IS +1,296 bp (t 3.07, n 12), VAL +520 (t 1.75, n 32), registered
  power 2.97 < 3 so DEMO; **HOLD n 91, +780 bp, t 3.11** (worst-of-1 s fills +540, t 2.25; median +18; +10 s entry only
  +276). Promotion needs a bot that sees the notice within ~3 s ([PREREG_A2_D5L](round65_retail_venues/A2/PREREG_A2_D5L.md)).

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| H | K2 frozen on Bithumb KRW listings (99 events) | none: IS +432 (t 1.92), VAL -75 (t -0.31); 3 of 99 overlap Upbit; pump before entry +5.5 % | [STREAM_H.md](round65_retail_venues/H/STREAM_H.md) |
| U | Upbit KRW volume-share shocks without a listing -> short Binance perp | none: IS pick t 1.03 (below the max-null median 1.23); 2021 negative in all 12 cells; VAL-only fade (k4-ALL-H72 t 1.89) has negative IS | [STREAM_U.md](round65_retail_venues/U/STREAM_U.md) |
| I | Scout of retail venues with dated listings (Bitvavo, Indodax, BtcTurk, Bitkub, CoinDCX, Coinone, bitbank; several 403 / robots-blocked) | no venue usable: pre-entry pump median -6 % to +2.5 % | [STREAM_I.md](round65_retail_venues/I/STREAM_I.md) |
| W | Upbit investment-warning / delisting notices -> short Binance perp | none: IS has 0 tradable events (no warned coin had a Binance perp in 2020-21); VAL W72 +546 bp n 4. Found Upbit's notice JSON (api-manager.upbit.com, robots without rules) | [STREAM_W.md](round65_retail_venues/W/STREAM_W.md) |
| J | Scout of the next wave (11 hypotheses) | best P(LIVE) ~1 %: HK CBBC calls, Upbit non-KRW markets, Binance funding-interval switches, HK leveraged ETFs, BtcTurk USDT premium | [STREAM_J.md](round65_retail_venues/J/STREAM_J.md) |
| A | Chase the Upbit KRW-listing notice on Binance perps (+1 / 5 / 15 min) | none: the move (+1,524 bp IS / +1,953 VAL vs BTC, 100 % of events) is inside the notice minute; N + 1 min -> L +309 / -21 | [STREAM_A.md](round65_retail_venues/A/STREAM_A.md) |
| C | HK CBBC mandatory-call clusters -> HK50 | not testable: no free point-in-time call-level history (HKEX attribute files are paid; launch PDFs on 13 issuer sites) | [STREAM_C.md](round65_retail_venues/C/STREAM_C.md) |
| R | Korean waking-hours rhythm of Upbit-heavy coins | none: all 7 cells negative every year (declared side wrong); the reversed rhythm needs maker fills and still fails IS | [STREAM_R.md](round65_retail_venues/R/STREAM_R.md) |
| E | HK leveraged / inverse ETF close rebalancing -> HK50 | none: no free AUM history (CSOP 403); into the close loses; post-close 16:10-16:29 IS t 1.90, ~0 without 3-4/2020 | [STREAM_E.md](round65_retail_venues/E/STREAM_E.md) |
| M | K2 frozen on Upbit BTC / USDT-market additions; K2 survivorship | none: IS -39 (t -0.08), VAL +596 (t 2.98, n 16); survivorship check keeps K2 (above) | [STREAM_M.md](round65_retail_venues/M/STREAM_M.md) |
| A2 | Seconds after the Upbit notice (aggTrades); D5-L = +5 s entry, exit at the KRW open | **DEMO, HOLD passed**: notice stamps are whole seconds, the burst never leads them; half the move in 1.2 s; HOLD +780 bp t 3.11 | [STREAM_A2.md](round65_retail_venues/A2/STREAM_A2.md), [PREREG_A2_D5L](round65_retail_venues/A2/PREREG_A2_D5L.md) |

## What a user decision could unlock
- HKEX paid "Securities Attribute" files (CBBC call levels / outstanding) for the CBBC call-cluster test (stream C).
- A K2 bot (unchanged from round 64). K2's HOLD event builder uses the current Upbit market list, so a live bot must
  poll Upbit's notices or market list, not a static list (renamed / delisted markets were missing).
- An Upbit-notice latency bot if A2 finds edge left after a few seconds (polling api-manager.upbit.com returned 429 at
  0.3 s; 1.5 s worked).

## Pitfalls found this round
- The Mac's DNS maps hkex.com.hk to 127.0.0.1: HKEX requests went through `ssh agentFx curl`, nothing left on the VPS.
- Upbit candle API is slow (~0.7 s per request) and hides delisted markets (404); Bithumb hides them too ("Code not
  found"); Bithumb's `to` is KST. Upbit's first KRW 1m candle is the stated start + 5 min (buys blocked 5 minutes).
- api-manager.upbit.com returns 429 at 0.3 s between requests; per_page is capped at 20.
- Local Binance 1h files have mixed column layouts: read columns by header name.
- A subagent that has reported can leave a background process alive: the coordinator now stops each finished task.

## Standing after round 65
C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, A2-D5L. Round 66 ([round66_fast_execution/BRIEF.md](round66_fast_execution/BRIEF.md))
tests whether the effects that moved inside the first minute (F wick fade, G catch-up) are capturable by a bot that
reacts at the bar close or within seconds; F-family rules are forward-only (F's HOLD is known).
