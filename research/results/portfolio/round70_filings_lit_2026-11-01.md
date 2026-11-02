# Round 70: corporate BTC-purchase filings at seconds (M8), literature scout 2025-26 (LIT), funding-formula carry (D2), 2026-11-01

Brief: [round70_filings_lit/BRIEF.md](round70_filings_lit/BRIEF.md) (17:20 UTC; D2 added 17:38 UTC).

## Answer first
- **No LIVE or DEMO candidate so far.** M8: BTC does not rise after a company's BTC-purchase 8-K (acceptance time to the
  second); it falls ~10 bp in 5 minutes, about half of which happens on ordinary days at the same clock time; every
  long cell loses (VAL D5-5m -19.6 bp, t -6.60). LIT: 11 ideas, best P(LIVE) ~2 %; L2 (funding-formula carry) became
  stream D2 (running) and round 71 D3; L3 / L5 became forward-only streams in round 71.
- **D2 (registered, HOLD failed):** long Deribit perp / short Binance perp, always on: IS +22.7 %/yr (t 8.30), VAL +5.32
  (t 7.11) but excess over cash only +1.37 (t 1.83) -> DEMO; HOLD +2.64 %/yr (t 6.77), excess over cash **-1.32 (t -3.48)**:
  FAIL ([PREREG_D2_ON](round70_filings_lit/D2/PREREG_D2_ON.md)). Cross-venue funding carry is closed.

## Streams
| Stream | Hypothesis | Verdict | Detail |
|---|---|---|---|
| M8 | Long BTC perp 5 / 30 s after a corporate BTC-purchase 8-K (MSTR 2020-24, Semler, RIOT, MARA, KULR), exit 5 / 60 min | none: IS n 15, VAL n 34; all cells negative; trade count in the first 10 s 1.08x baseline (nobody trades the stamp) | [STREAM_M8.md](round70_filings_lit/M8/STREAM_M8.md) |
| LIT | 2025-26 literature scout | L1 Binance listing-announcement times (Zenodo dataset built from /bapi/ + web.archive.org: **needs the user's OK**), L2 funding-formula carry (-> D2 / D3), L3 / L5 (contaminated -> forward-only), L4 Polymarket digitals (new-era) | [STREAM_LIT.md](round70_filings_lit/LIT/STREAM_LIT.md) |
| D2 | Long Deribit perp (no interest leg) / short Binance perp (0.01 %/8h interest leg) | registered DEMO (excess over cash), **HOLD failed** (excess -1.32 %/yr) | [STREAM_D2.md](round70_filings_lit/D2/STREAM_D2.md), [PREREG_D2_ON](round70_filings_lit/D2/PREREG_D2_ON.md) |

## What a user decision could unlock
- L1: using the Zenodo dataset of Binance announcement times (doi 10.5281/zenodo.22976615), built by its authors from
  sources this project does not call (/bapi/, web.archive.org); it would make round 63 D's Binance-listing test
  possible (A2-style trade on Coinbase spot / Bybit perp), forward-only for 2025-26 (the dataset covers it).
