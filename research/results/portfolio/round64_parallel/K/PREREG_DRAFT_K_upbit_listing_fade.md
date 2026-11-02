# PREREG DRAFT K2: fade the Upbit KRW-listing pump on Binance perps (DEMO tier)

Draft written 2026-11-01 09:58 UTC (`date -u`) by stream K of round 64. HOLD (2025-01-01..2026-10-29) has NOT been
opened, counted or requested. Only the coordinator opens HOLD, once. Do not re-optimise (hold, entry lag, cost, event
filter are frozen as below).

## Rule (frozen)
- **Event.** A coin gets its first Upbit KRW-market 60-minute candle at start time L (UTC), and its Binance USDT-M
  perp has a first daily kline at least 7 days before L. One event per coin; a coin whose KRW history starts earlier
  is not an event.
- **Trade.** Short the alt perp and long BTCUSDT perp, equal USD notional. Both legs are filled at the close of the
  1m bar that starts at L + 1 h, i.e. at L + 61 min.
- **Exit.** Both legs at the close of the 1m bar starting at entry + 72 h. No stop.
- **Costs.** 42 bp per trade: 4 taker fills x 5 bp, plus a 10 bp alt half-spread x 2, plus a 1 bp BTC half-spread
  x 2. Funding on both legs is charged / credited at the real Binance stamps in (entry, exit].
- **Sizing.** Fixed notional per event. Perps on margin only, so no fully paid leg and no cash-rate deduction (round
  58's lesson concerns spot legs).

## How to build HOLD events (coordinator)
- Take `/v1/market/all` (current list).
- For every KRW coin whose Binance perp started at least 7 days before its first KRW candle, find L the same way as
  k2.py's `events()`: first 240-minute candle, then the first 60-minute candle.
  - Use `to=2026-10-29T00:00:00Z`, with the floor = 2024-12-25 or the perp start minus 8 days.
- **Keep only L in 2025-01-01..2026-10-26**, so that 72 h of exit data exist.
- **Code (sha256)**, in round64_parallel/K/code/:

  | file | sha256 |
  |---|---|
  | k2.py | f671e399e3ae3f8bef5305e06fab8a29a75ce450c30041b2511c29455b04f571 |
  | kdata.py | da002ebbc9ad534493e5993f011ebb9fea3192556263fa69750d3d868db38327 |
  | fills.py | b058e839e4c5dcadbb2e376f8156f797b18e08297a70f9e52b0013b3234aa012 |
  | net.py | 49cbd7e4c0a87892c7915d183df24e7fe6c392dbcbf31d900adf728654579dad |
  | pull_upbit.py | d356ec5f7e25dc669362edc36791a9cc13587b87c6684d1bdc6374e153f4ea43 |

- **The CUT constants must be moved for HOLD.**
  - kdata.CUT, k2's `CUT - 4 d` filter and the pull's `to` all stop at 2025-01-01 by design.
  - A HOLD run needs a copy with CUT = 2026-10-29 and BTC 1m zips for 2025-01..2026-09 (plus REST for October).
  - The rule logic must stay byte-identical: diff the copy against these hashes.

## IS / VAL numbers (net bp per trade, t clustered by entry day; full output k2_output.txt)
| cell | era | n | gross | funding | net | t | median | sd | SR / trade | years (n, net) |
|---|---|---|---|---|---|---|---|---|---|---|
| **H72, L + 1 h (this draft)** | IS 2020-21 | 11 | +1150 | -14 | **+1094** | **3.16** | +1054 | 909 | 1.20 | 2020 (4) +555, 2021 (7) +1402 |
| | VAL 2022-24 | 29 | +570 | -105 | **+423** | **1.37** | +619 | 1666 | 0.254 | 2022 (3) +378, 2023 (9) +1026, 2024 (17) +111 |
| H72 costs x1.5 | IS / VAL | | | | +1073 / +402 | 3.10 / 1.30 | | | | |
| H72 enter L + 1 h + 5 min | IS / VAL | | | | +997 / +399 | 2.87 / 1.31 | | | | |
| H72 enter L + 2 h | IS / VAL | | | | +913 / +431 | 2.94 / 1.55 | | | | |
| H24 (declared sibling, not chosen) | IS / VAL | 11 / 29 | | | +673 / +389 | 2.22 / 1.96 | +477 / +384 | | 0.85 / 0.36 | 2022 -5 (3 trades) |

**Random benchmark (gross, priced on 1h closes; k2_random.txt).** The H72 events beat 100 % of 500 draws in both
eras, against two kinds of draw:
- other universe alts shorted at the same hour: median -143 bp IS, -72 bp VAL;
- the same coin at random hours 30-180 days after listing: median -47 / -17 bp.

**Post-hoc control (k2_pumpctrl.txt; it chose nothing).** Shorting any universe alt after a non-listing 24 h run-up
of 10 % or 20 % against BTC loses on the mean in both eras: H72 -81 to -293 bp, t -2.3 to -3.0. The medians are
positive. So the K2 effect is specific to the listing, not a generic pump fade.

**Pre-entry run-up.** The alt gains +21.5 % against BTC from L - 24 h to the entry (VAL mean +22.2 %). Upbit announces
the listing before trading opens, so the pump happens before the trade.

**Tails.** The worst VAL trade is ID 2024-02: -4669 bp at H72 (-1695 at H24). Others are CKB 2024-09 (-3098) and
MEW 2024-10 (-1002). Dropping the single best trade gives IS +895 and VAL +266 bp.

**C3 correlation (daily P&L booked on the exit day, k2_c3corr.txt):** IS -0.003, VAL -0.034.

## Tier and power
- **LIVE: no.**
  - VAL t is 1.37, below 1.5.
  - At VAL size the power is SR 0.254 x sqrt(n_HOLD). The VAL pace is 9.7 events a year, so n_HOLD ≈ 17.7 and the
    power ≈ **1.07**, below 3.
  - Even if Upbit listed 30 such coins a year in 2025-26 (n_HOLD ≈ 55), the power would be ≈ 1.9.
- **DEMO: meets every bar.**

  | bar | needed | K2 |
  |---|---|---|
  | IS t | >= 2.0 | 3.16 |
  | VAL net | > 0 | +423 bp |
  | random | >= 90 % | 100 % |
  | x1.5 costs and one step late | positive | positive |
  | years positive | | 5 / 5 |

- **The DEMO case is weak.**
  - IS is 11 trades on 9 days.
  - Both IS and VAL t come from small samples with fat tails, so the clustered t overstates certainty.

## HOLD pass bar and rules
- **HOLD bar (DEMO rule).** HOLD net mean > 0 over all HOLD events. Report also x1.5 costs, L + 2 h entry,
  median, worst trade and per-year means. If net < 0, drop the rule.
- **Demo.**
  - Expected pace: ~10-30 demo trades a year (as many as Upbit's KRW listings of coins with Binance perps).
  - Run it as a paper or demo bot, fixed small notional, detecting new KRW markets by polling `/v1/market/all`
    every few minutes.
  - **Stop rule.** Cut if, after 10 demo trades, the cumulative net is below -2500 bp. Also cut if HOLD + demo pooled
    mean net is < 0 at any point after 20 pooled trades.
- **Promotion to live.** HOLD + demo pooled net t >= 2.5 and pooled n >= 40, unchanged rule.

## Biases and caveats
- **Survivorship.** Upbit's market list holds only current markets, so listings later delisted from Upbit are
  missing. Those are likely coins that faded, so the bias runs against the short (conservative). It is the same in
  HOLD.
- **Missing pre-perp listings.** Listings of coins with no Binance perp at L (most new tokens) are not events.
- **Execution.**
  - The first KRW hour is volatile. A 10 bp alt half-spread is assumed and never measured; the demo measures it.
  - Shorting a just-pumped alt carries squeeze risk (round 60). There is no stop, and none should be added after the
    fact.
