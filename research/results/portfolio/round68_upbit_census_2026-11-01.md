# Round 68: census of Upbit notice types (UC), 2026-11-01

Brief: [round68_upbit_census/BRIEF.md](round68_upbit_census/BRIEF.md). Question: does any Upbit notice category other
than KRW listings move the named coin's Binance perp in a direction still open 5 s after the stamp?

## Answer first
- **No LIVE or DEMO candidate.** Of 11 declared categories only DWSUSP (deposit / withdrawal halts blamed on the
  coin's own chain, declared short) had enough events: it loses (5 min exit IS -49 bp t -4.34, VAL -49 t -6.29; 0/5
  years). Every category with n >= 10 except OTHER *rises* within 1-3 s of the stamp (Korean retail reads any notice as
  attention), then mostly fades; no category moves before the stamp.
- AIRDROP (declared long) has IS +311 bp (t 3.38, n 10) but VAL +84 (t 0.87, n 10): too few events, power ~0.7.
- Upbit's KRW-listing notice (A2-D5L, DEMO, HOLD t 3.11) remains the only notice type with a tradable edge.

## Details
| category | IS / VAL events | side | median at +5 s (IS / VAL) | +5 s -> +30 min |
|---|---|---|---|---|
| DWSUSP (chain-blamed halts) | 28 / 56 | short | +11 / +5 | +18 / +11 |
| DWWALLET (Upbit wallet maintenance) | 112 / 114 | none | +8 / +5 | +20 / +8 |
| NETUP (network upgrades) | 73 / 216 | none | +21 / +7 | +100 / +12 |
| AIRDROP | 10 / 10 | long | +60 / +14 | +479 / +6 |
| WARN (caution designation) | 0 / 31 | short | - / +5 | - / -22 |

Max-over-categories null (p95 of max t): IS 0.66, VAL -0.10. File: [STREAM_UC.md](round68_upbit_census/UC/STREAM_UC.md).

## Pitfalls
- api-manager.upbit.com's body endpoint returns 429 at ~10 requests a minute (list pages tolerate 1.5 s); use >= 6 s
  for bodies.
- Halt notices share boilerplate ("planned maintenance" wording); classify by the original suspension sentence.

## Standing after round 68
C3 is the only LIVE algorithm. DEMO that passed HOLD: B, X3, K2, Q1, A2-D5L. Forward-registered LIVE candidate: F0.
