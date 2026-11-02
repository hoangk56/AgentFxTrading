# Round 71, stream D3: funding-formula asymmetries on other venues

Written 2026-11-01 18:40 UTC (`date -u` at 18:37:51). Plan in [HYPOTHESES_D3.md](HYPOTHESES_D3.md): written at
18:01 UTC, amended at 18:09 UTC after a data gap, both before any return was computed. HOLD was never requested or
loaded. Every series is cut at ts < 2025-01-01 at load. The Kraken funding endpoint returns only 2025-10 onward, so
those rows were dropped in memory and never written. Outputs: [run_output.txt](run_output.txt) (as declared),
[run_output_clean.txt](run_output_clean.txt) (data-cleaning sensitivity), [calib_output.txt](calib_output.txt),
[kraken_output.txt](kraken_output.txt). Code is in `code/`.

## Answer first: none (no LIVE, no DEMO, no PREREG draft)
- **Only two venues had no interest leg in 2020-24 besides Deribit (D2): OKX and Kraken Futures.** Every other venue
  carries the same 0.01 %/8h anchor: Binance USDT-M / COIN-M, Bybit linear / inverse, BitMEX, Hyperliquid. Pairs among
  those have no structural term.
- **The structural gap was real in 2020-21 and was arbitraged away by 2023-24.** We tested long OKX USDT swap / short
  Binance USDT-M. The funding gap was 1.9-2.2 bp/day for BTC and 3.4-3.8 bp/day for ETH in 2020-21. It fell to
  0.12 / 0.20 bp/day in 2024. OKX's premium had moved up to absorb Binance's anchor before OKX itself adopted the
  anchor (~2025-04, secondary source).
- **BTC-ON and ETH-ON pass the raw-t bars but fail the cash grading in VAL.**
  - BTC-ON: IS +7.31 %/yr (t_nw 4.82), VAL +1.27 % (t 3.11).
  - ETH-ON: IS +12.69 % (t 6.60), VAL +2.02 % (t 4.19).
  - Excess over DFF on the margin (L = 2) in VAL: BTC -2.69 % (t -5.61), ETH -1.94 % (t -3.34). Both are still
    negative at L = 3.
  - The declared rule needs excess > 0 with t >= 1.5 in IS and VAL. Both cells **fail**.
- **The pair cannot be traded now in any case.** OKX's current rule has the 0.01 % anchor, so the asymmetry is gone.
- **Kraken (descriptive only).** Its reconstructed premium shows the same pattern: the gap fell from ~+15 %/yr
  (BTC, 2021-H2) to ~0-4 %/yr in 2023-24. That is below the cash rate on margin.

## Formula table (sources: research/data/funding_formulas/raw/docs/)

| Venue | rule (8h-equivalent) | interest leg | damper | interval / cap | change dates | source |
|---|---|---|---|---|---|---|
| Binance USDT-M / COIN-M | P + clamp(0.01 % - P, +-0.05 %) | 0.01 %/8h | yes | 8h (BTC / ETH) | none known 2020-24 | secondary (no primary page fetched: /bapi/ family); stamps at exactly 0.0001: BTC 50 / 43 / 31 / 39 / 42 % (2020-24) |
| Bybit linear / inverse | P + clamp(I - P, +-0.05 %) | 0.01 %/8h | yes | 8h | none known | api.bybit.com probe (inverse BTCUSD 2020-02-01 = 0.0001); www.bybit.com unreachable (URLError) |
| BitMEX XBTUSD | P + clamp(I - P, +-0.05 %), I = (0.06 % - 0.03 %)/3 | 0.01 %/8h | yes | 8h | none found | BitMEX guide via WebSearch; **API 403, stopped** |
| Hyperliquid | P + clamp(0.01 % - P, +-0.05 %), paid hourly /8 | 0.01 %/8h | yes | 1h, cap 4 %/h | from 2023 | hyperliquid.gitbook.io trading/funding |
| **OKX** swaps | clamp(MA(premium - 0)), premium = mid / index - 1 | **0** | **none** | 8h; rate settled at T computed over the previous period (verified: lag-1 reconstruction corr 0.89 vs lag-0 0.28 in 2021-09) | 2024-03-05: MA window change (interest still 0); ~2025-04: 0.01 % anchor + clamp + impact prices (secondary, unverified) | OKX 2024-01-25 announcement; current help page |
| **Kraken Futures** PI_ / PF_ | TWAP premium / n per hour | **none** | **none** | to 2022-09-29 12:00 UTC: 4h windows, n = 8, cap 0.1 %/h; after: 1h, n = 24, cap 0.25 %/h | 2022-09-29 | support.mtf.kraken.com art. 7009378818333; support.kraken.com art. 360022835911 |

## Data
- **OKX realised funding.** From /api/v5/public/market-data-history (module 3) monthly files: 2021-09, then
  2022-01-16..2024-12. Nothing else exists for 2020-01..2021-08 or 2021-10..2022-01-15.
- **OKX IS funding is reconstructed** from 1H swap-trade and index candles (amendment 18:09). The rule's lag was
  fixed on 2021-09 alone: lag 1, mean corr 0.89 over 10 coins. Mean bias on BTC was -0.01 bp/8h. On the alts the
  reconstruction runs +0.0-0.45 bp/8h too high, which understates the IS gap (conservative).
  - VAL check, not used for any choice: BTC corr 0.81, mean 0.22 vs 0.15 bp/8h realised; ETH corr 0.84.
  - IS is 92-100 % reconstructed; VAL is realised (4 % reconstructed in 2022-01).
- **Kraken.** Funding history is public only from 2025-10 (unusable). The mark / index 1h candles start 2021-07-07,
  so Kraken is descriptive only.
- Requests: 4,380 logged in research/data/funding_formulas/requests.log (4,353 x 200, 2 x 403 BitMEX, 3 x 400 OKX
  bad window, 6 x 404, 16 local errors). WebSearch: 4 of 15. No e-mail or browser UA in any request.

## Results (net of taker 5 bp + half spread per side on both venues, daily book, NW lag 10; L = 2, C = N)

| cell | era | n | net %/yr | Sharpe | t_nw | excess over cash L2 (t) | L3 | x1.5 | late | years | random |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC-ON | IS | 729 | +7.31 | 3.29 | 4.82 | +7.09 (4.65) | +7.16 | +7.08 | +7.32 | 2020 +7.85, 2021 +6.77 | trivial |
| BTC-ON | VAL | 1096 | +1.27 | 1.92 | 3.11 | **-2.69 (-5.61)** | -1.37 | +1.15 | +1.24 | +2.20, +1.64, **-0.03** | trivial |
| BTC-F7 | IS | 729 | +5.67 | 2.70 | 3.68 | +5.45 (3.52) | +5.53 | +4.44 | +5.17 | +7.43, +3.92 | 99 % |
| BTC-F7 | VAL | 1096 | **-2.32** | -2.70 | -3.45 | -6.27 | -4.95 | -4.29 | -2.36 | -1.64, -2.42, -2.88 | 98 % |
| ETH-ON | IS | 729 | +12.69 | 5.04 | 6.60 | +12.47 (6.51) | +12.54 | +12.37 | +12.71 | +11.55, +13.83 | trivial |
| ETH-ON | VAL | 1096 | +2.02 | 2.74 | 4.19 | **-1.94 (-3.34)** | -0.62 | +1.86 | +2.03 | +4.39, +1.41, +0.26 | trivial |
| ETH-F7 | IS | 729 | +9.89 | 4.09 | 5.01 | +9.67 (4.90) | +9.74 | +8.37 | +9.48 | +8.29, +11.49 | 99 % |
| ETH-F7 | VAL | 1096 | **-1.21** | -1.33 | -1.73 | -5.16 | -3.84 | -3.09 | -1.36 | +2.14, -3.34, -2.41 | 100 % |
| B10-ON | IS | 729 | +5.09 | 0.40 | 1.06 | +4.87 (1.02) | +4.94 | +4.51 | +3.98 | +1.47, +8.70 | trivial |
| B10-ON | VAL | 1096 | +0.24 | 0.36 | 0.49 | -3.71 (-6.63) | -2.40 | -0.05 | +0.23 | +0.80, +0.46, -0.54 | trivial |
| B10-F7 | IS | 729 | +7.04 | 1.11 | 2.01 | +6.81 (1.94) | +6.89 | +4.50 | +7.10 | +8.41, +5.66 | 98 % |
| B10-F7 | VAL | 1096 | **-3.49** | -7.52 | -8.48 | -7.44 | -6.12 | -6.17 | -3.60 | all < 0 | 100 % |

- Max-over-cells IS null (joint block bootstrap): the 95th percentile of the max t is 2.28. The BTC / ETH cells clear
  it (p < 0.001); the B10 cells do not (p 0.08-0.43).
- **Decomposition, VAL ON** (%/yr): BTC funding +1.52, price -0.01, costs 0.23; ETH funding +2.41, price -0.06,
  costs 0.32. The price leg (perp-perp basis) is negligible, so the funding gap itself is what shrank.
- **F7 costs.** F7 toggles often and pays 3.8-5.4 %/yr in costs in VAL. That alone is about the whole gap.
- **Liquidation-risk days**: intraday adverse move > 90 % of a leg's equity at L = 2.
  - BTC / ETH: 0-2, all in 2020-21.
  - B10: 21 (IS) and 10 (VAL), from alt spikes.
- **Cleaning sensitivity** (run_output_clean.txt; added after the first run, so it is not a grading input). It drops
  OKX premiums with |p| > 2 %, the first 30 OKX days, and days where |OKX / Binance - 1| > 2 %, which removes thin
  early prints such as ADA 2020-03 and LINK 2020-03.
  - BTC / ETH VAL rows are unchanged.
  - B10-ON IS improves to t 2.23. B10-ON VAL is +0.37 % (t 0.83) and still below cash.
  - No verdict changes.

## Gap by year (holding-day funding, bp/day; valid days)

| | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| BTC Binance / OKX / gap | 4.74 / 2.59 / 2.15 | 8.39 / 6.46 / 1.93 | 1.14 / 0.44 / 0.70 | 2.16 / 1.66 / 0.51 | 3.26 / 3.14 / **0.12** |
| ETH Binance / OKX / gap | 7.54 / 4.09 / 3.45 | 10.28 / 6.49 / 3.80 | 0.22 / -1.14 / 1.36 | 2.27 / 1.80 / 0.47 | 3.54 / 3.34 / **0.20** |
| DFF (%/yr) | 0.37 | 0.08 | 1.69 | 5.03 | 5.14 |

Kraken PI_XBTUSD, reconstructed (Binance - Kraken, %/yr): 2021-H2 +14.8, 2022 +8.4 / +11.2, 2023 +3.9 / -0.1,
2024 +3.7 / +2.5. PI_ETHUSD: +3.6, +3.5 / +12.6, +3.8 / +1.7, +2.5 / -1.1. The 2023-24 levels are below the cash
cost of margin. See kraken_output.txt.

## Grading against the bars
- **LIVE** fails on every cell: the cash rule fails in VAL, BTC-ON's 2024 is negative, and VAL Sharpe x
  sqrt(667/365) gives HOLD power of 2.6 (BTC-ON), 3.7 (ETH-ON) and 0.5 (B10-ON) on raw net. On excess over cash the
  mean is negative, so power is 0.
- **DEMO**: BTC-ON and ETH-ON meet the raw DEMO numbers (t_IS >= 2, VAL net > 0). Their random benchmark is trivial
  (ON has no timing), and the declared cash rule fails, so they are not DEMO.
  - Break-even leverage: ETH-ON VAL needs C/N <= 0.51 (L ~ 4 per venue); BTC-ON needs C/N <= 0.32 (L ~ 6).
  - Both figures were chosen after seeing VAL, and the 2024 gap is ~0.5 %/yr. Not a candidate.
- **F7** loses in VAL on every asset.
- **No PREREG_DRAFT.** The OKX asymmetry no longer exists (anchor added ~2025-04), so even a pass could not be
  registered forward.

## Lessons / pitfalls
- A no-interest funding leg does not keep its structural carry. The market prices the gap away through the premium
  within ~2-3 years: OKX by 2024, Kraken by 2023. Expect D2 (Deribit) to show the same 2023-24 compression; the
  Kraken numbers here are an independent hint.
- Realised-funding archives have holes (OKX 2021-10..2022-01-15; Kraken only the last 8,760 h). Reconstructing
  funding from mark and index works when the lag is calibrated: OKX settles the previous period's average.
- Capital-light carry still has to beat cash on the margin. In 2023-24 DFF (~5 %) was larger than every gap seen.
- BitMEX's API returns 403 from this network. www.bybit.com is unreachable (api.bybit.com works).

## What a user decision could unlock
Nothing material. A maker-only, high-leverage version (L >= 4-6 per venue) of ETH-ON would be chosen after seeing
VAL, and the 2024 gap (~0.5 %/yr) would not cover the venue and ADL risk.
