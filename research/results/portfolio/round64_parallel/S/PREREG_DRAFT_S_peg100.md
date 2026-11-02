# PRE-REGISTRATION DRAFT S / peg100: buy a fiat-backed stablecoin on Binance when it trades >= 100 bp below USDT

Draft written 2026-11-01 10:26 UTC (from `date -u`) by stream S (round 64). HOLD (2025-01-01..2026-10-29) NOT opened
and no 2025-26 file downloaded; the coordinator opens it once. Tier: **DEMO at most** (VAL t 1.29-1.34 < 1.5 and HOLD
power ~0.7 rule out LIVE). Read the caveats in [STREAM_S.md](STREAM_S.md) first: VAL rests on one episode (SVB, March
2023), and a standing book with its capital idle in USDT loses to the cash rate in VAL.

## Rule (frozen; code `code/peg.py`, `simulate(sym, d, 100, 7, late=0)`, `net(tr, fill=...)`)
- Pairs: Binance spot X/USDT for X in USDC, BUSD, TUSD, PAX, USDP, FDUSD, DAI, USDS, plus USDS/BUSD (`peg.PAIRS`);
  1m klines from data.binance.vision monthly files. In HOLD only USDC, TUSD, USDP, FDUSD (and any of the others still
  listed) can trade. Fiat-backed USD stablecoin / USDT pairs first listed in 2025-26 are NOT in the primary test; the
  coordinator may report them separately if it names them from listing information before reading their prices.
- d = 1 - close of a 1m bar. Signal: d >= 100 bp at a bar close, no open trade in that pair. Buy at the close of the
  next bar with trades (no entry if that bar is > 1 h after the signal). One open trade per pair, 1 unit notional each.
- Exit: first bar after entry with d <= 50 bp, sell at the close of the next bar with trades; else at the bar at entry
  + 7 days. A data gap > 1 day inside a trade closes it at the last bar before the gap.
- P&L per trade: price return - 2 x 10 bp taker fee - 2 x half-spread (0.5 bp USDC / BUSD / FDUSD, 1.0 bp others) -
  DFF (entry day) x hold days / 365. Reported with two fills: close (declared) and taker-VWAP (buy at the entry
  bar's taker-buy average price, sell at the exit bar's taker-sell average price, fees only; added before HOLD after
  a first look at IS, see HYPOTHESES_S.md addendum).
- Episode = union of trades in any pair whose [entry, exit] padded by 24 h overlap; t clustered by episode.

## IS / VAL numbers (declared cell = best IS cell of a 6-cell grid k {10, 30, 100} x H {1, 7} d)
| era | n | episodes (pos) | excess bp close | t_ep | excess bp taker-fill | t_ep | x1.5 (taker) | 1 bar late (taker) | random beaten (uniform / same discount) |
|---|---|---|---|---|---|---|---|---|---|
| IS 2018-05..2021 | 163 | 29 (25) | +22.1 | 6.97 | +15.2 | 4.52 | +5.2 (t 1.54) | +13.5 (t 3.68) | 100 % / 100 % |
| VAL 2022-24 | 20 | 4 (2) | +65.4 | 1.34 | +50.6 | 1.29 | +40.6 (t 1.03) | +53.0 (t 1.34) | 100 % / 99.4 % |

- Years (taker fill): 2018 +12.6, 2019 +12.0, 2020 +24.8, 2021 +20.3, 2022 no trade, 2023 +86.9, 2024 -3.9 (5 / 6).
- IS 2020-21 only: 40 trades, 8 episodes, taker +24.5 bp, t 4.38. VAL without the SVB week: 9 trades, 3 episodes,
  taker -8.4 bp (t -1.21).
- Max-over-6-cells null: best cell beats 99.8 % (IS) / 100 % (VAL) of random max-over-cells draws.
- Daily P&L correlation with C3: IS +0.004, VAL +0.035.

## Power at VAL size
VAL: 4 episodes in 3 years -> HOLD (1.83 yr) expects ~2.4 episodes. Per-episode Sharpe (taker fill) 0.45 -> power
0.45 x sqrt(2.4) = 0.71; per trade 0.30 x sqrt(12) ~ 1.06. Far below 3: HOLD cannot confirm or kill the rule; it
can only check the sign.

## HOLD pass bar (DEMO)
HOLD net excess > 0 per trade with the taker-VWAP fill (primary) and with the close fill, t by episode reported, plus
episodes, x1.5, one bar late, and the P&L without the largest episode. Fail if taker-fill net excess <= 0. If HOLD
has 0 trades, report "no test" (not a pass). Run once on 2025-01-01..2026-10-29, the coordinator downloading the
same monthly 1m files for the frozen pair list (only monthly files, logged).

## Demo plan (if HOLD passes and the user agrees)
- Expected 1-3 episodes / yr (VAL 1.3 / yr; IS 8 / yr in thin 2018-20 markets). Fixed small notional per pair;
  log the order-book spread and the fill at each signal, and whether the stable pair still had a zero-fee promotion.
- Stop rule: stop after 5 demo episodes if cumulative net excess < 0; stop at once if a stablecoin's issuer halts
  redemptions (the anchor is gone; TUSD 2024 lost -42 to -108 bp per 7-day re-entry).
- Live rule: HOLD + demo pooled t (episode cluster) >= 2.5 with >= 15 pooled episodes.
- Economic gate the bar does not test: a standing book must hold its standby capital on Binance; in VAL the rule
  earned ~+337 bp / yr per unit while cash paid ~395 bp / yr, so it beats cash only if the standby capital can earn
  near the cash rate while staying deployable within minutes (STREAM_S.md).

## Code hashes (sha256, first 16; `python -m research.tools.prereg_hashes`)
At draft time (10:28 UTC): `code/peg.py` c06b86a4c4903e02, `code/run.py` f6f9126eb17f5522, `code/extra.py`
9899c534e4f0a62b. The coordinator re-hashes at freeze time; do not edit these files before HOLD.
