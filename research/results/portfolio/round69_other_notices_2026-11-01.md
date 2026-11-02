# Round 69: listing notices of other retail venues at seconds (KO, JP), 2026-11-01

Brief: [round69_other_notices/BRIEF.md](round69_other_notices/BRIEF.md) (16:16 UTC).

## Answer first
- **No LIVE or DEMO candidate.** Korean venues other than Upbit / Bithumb have no allowed notice history (KO); Japanese
  listing notices (bitbank blog, Coincheck press / news) do not move the Binance perp at all (JP: VAL median 0 bp at
  +5 s, +2 bp at +300 s; A2-D5L frozen IS +1,898 bp t 1.62 n 9 from 2021 multi-day drift, VAL +36 t 0.26).
- With rounds 65-69, Upbit's KRW-listing notice is confirmed as the only retail-venue announcement with a seconds-level
  edge on Binance (A2-D5L, DEMO, HOLD t 3.11).

## Streams
| Stream | Sources | Verdict | Detail |
|---|---|---|---|
| KO | Coinone (robots disallow all), Korbit (API keeps 20 latest; archive needs app headers: not sent), GOPAX (403) | not testable | [STREAM_KO.md](round69_other_notices/KO/STREAM_KO.md) |
| JP | bitbank blog (publishedAt s), Coincheck corporate press / news (2020-21 stamps date-only), GMO (from 2026-02), bitFlyer (timeouts), BITPoint (403) | none: 43 events, no burst within 300 s; 5-min exits lose the cost (t -4.9 / -5.6) | [STREAM_JP.md](round69_other_notices/JP/STREAM_JP.md) |

## Standing after round 69
C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L. Forward-registered LIVE candidate: F0.
