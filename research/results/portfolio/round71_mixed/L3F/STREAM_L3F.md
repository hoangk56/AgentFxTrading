# Round 71, stream L3F: extreme negative funding, follow the day's direction for 24 h

Written 2026-11-01 17:52 UTC (`date -u`). The plan is in [HYPOTHESES_L3F.md](HYPOTHESES_L3F.md), written at
17:49 UTC before any return was computed. Code: [code/l3f.py](code/l3f.py), [code/run.py](code/run.py), and
[code/sanity.py](code/sanity.py), which spot-checks BTC events from March 2020. Output: [run_out.txt](run_out.txt),
[results_L3F.json](results_L3F.json). I used local data only, with every series cut at ts < 2025-01-01 at load.
I made no requests and no web searches, and I never read HOLD.

## Answer first: none (no LIVE, no DEMO, no PREREG_DRAFT)
- **No cell passes.** All four cells fail the IS t bar: the best IS t is 1.05, against a bar of 2.0 for DEMO and
  2.5 for LIVE.
- **All four cells lose in VAL.** On BTC / ETH the loss is significant: C1 VAL -94 bp / trade, t -2.82.
- **Only 2021 is positive in the selected cell (C1).** Every year from 2022 to 2024 is negative.
- **The paper's effect is not there before 2025 on Binance.** SSRN 7520320 reports +3.6 pp, stable across years.
  Following the day's sign after an extreme negative stamp does not work in 2020-24 on BTC / ETH or on the
  point-in-time top 10.

## Results (net of taker 5 bp a side + half-spread + funding; t clustered by entry UTC day)
| cell | universe, q | IS n | IS net bp | IS t | VAL n | VAL net bp | VAL t | VAL SR / trade | random entries IS / VAL | shuffled side IS / VAL |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 (picked on IS) | BTC / ETH, p5 | 83 | +66.2 | 1.05 | 209 | -94.4 | -2.82 | -0.224 | 96.2 % / 0.0 % | 90.7 % / 0.6 % |
| C2 | BTC / ETH, p10 | 107 | +53.8 | 0.96 | 303 | -67.3 | -2.95 | -0.172 | 96.4 % / 0.2 % | 91.0 % / 0.6 % |
| C3 | top 10 + BTC / ETH, p5 | 326 | +23.1 | 0.35 | 1,115 | -41.7 | -1.26 | -0.054 | 92.8 % / 15.4 % | 74.2 % / 13.1 % |
| C4 | top 10 + BTC / ETH, p10 | 477 | -11.8 | -0.24 | 1,704 | -41.3 | -1.60 | -0.058 | 76.2 % / 11.2 % | 52.4 % / 8.2 % |

**Max-over-cells null.** C1's IS t of 1.05 beats 87.5 % of the random-entry max-of-4 t. The null's 95th
percentile is 1.45.

**Power.** VAL Sharpe per trade is negative in every cell, so HOLD power at VAL size is below zero. At the VAL event
rate, C1 would see ~127 trades in a 1.83-year window. Even C1's IS Sharpe of 0.129 would give power 0.129 x
sqrt(127) = 1.5, below the 3 that LIVE needs.

### By year, net bp / trade (n)
| cell | 2020 | 2021 | 2022 | 2023 | 2024 | years > 0 |
|---|---|---|---|---|---|---|
| C1 | -72.5 (37) | +177.7 (46) | -113.9 (106) | -79.7 (52) | -68.9 (51) | 1 / 5 |
| C2 | -37.3 (52) | +140.0 (55) | -80.4 (149) | -62.1 (91) | -43.9 (63) | 1 / 5 |
| C3 | +85.3 (117) | -11.7 (209) | -20.5 (472) | -96.0 (273) | -28.8 (370) | 1 / 5 |
| C4 | +51.0 (169) | -46.3 (308) | -30.2 (750) | -83.5 (469) | -17.5 (485) | 1 / 5 |

### Robustness checks on C1
- **Costs x1.5:** IS +60.2 bp, t 0.95. VAL -100.4 bp.
- **One step late:** IS +65.0 bp, t 1.01. VAL -88.3 bp.
- **Daily book, Newey-West t:** IS 1.22, VAL -2.39.

### Decomposition (C1)
- **The price move is the whole result.** Gross price is IS +78.9 / VAL -82.3 bp. Funding over the 24 h is about
  0 bp, because the long and short sides offset.
- **IS: the long side carries it.** Long on up days earns +117 bp (n 43, t 1.44); short on down days earns +11.5 bp.
- **VAL: both sides lose.** Long on up days loses -41.9 bp. Short on down days loses -137 bp (t -2.59).
- **On the top 10 (C3 / C4) the split is larger.** In IS, long on up days earns +231 / +137 bp (t 2.53 / 2.09)
  and short on down days loses -150 / -156 bp. In VAL both sides are near -40 bp.
- The "long on up days" half is a sub-split I looked at after the fact. It is not a declared cell, and it fails VAL
  anyway.

## What failed and why
- **In 2022-24 the day's move after an extreme negative stamp reverses over the next 24 h.** That is the opposite of
  the paper's continuation, and it is clearest on BTC / ETH.
- **Flipping to a fade rule would be chosen after seeing VAL, and it loses in IS.** On C1, a fade earns about
  -91 bp in IS and about +70 bp in VAL net. The sign changes across eras, so there is no stable effect.
- **The paper's stability claim likely rests on something we do not have.** It may be its 2025-26 sample, SOL, or
  an event definition its abstract does not give. Our declared trailing-180-day percentile event does not reproduce
  it on 2020-24 Binance data.
- **This fits the earlier verdicts.** One-day momentum failed at IC (rounds 2 / 7), and round 62 found that the
  post-stamp information lies in the first seconds, not over a day.

## Pitfalls handled
- **Degenerate events.** In 2021 the BTC 5th percentile sat at the 0.01 % floor, so the event also requires
  f8 < 0.
- **Mixed funding intervals.** Alts moved to 4h / 1h stamps, so every rate is normalised to an 8h equivalent.
- **Tradable entry.** Entry is the close of the bar [T, T+1h), one hour after the signal. That is tradable, and it
  skips round 62's first-minute move.
- **One position per coin,** so the 4h / 8h stamps of one coin do not stack.
- **No look-ahead in the universe.** It uses the previous UTC day's round 58 ranking.
- **No HOLD data.** binance_basis/perp_1h runs to 2026-10, and it is cut at load. binance_1h_full, the primary
  source, ends 2024-12-31.

## User decisions
None that would unlock this. A fade version would be a new hypothesis chosen from VAL, and IS rejects it.
