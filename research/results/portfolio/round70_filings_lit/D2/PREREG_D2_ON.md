# PREREG D2-ON: long Deribit inverse perp / short Binance USDT perp, always on, BTC + ETH (registered)

Written 2026-11-01 17:55 UTC (from `date -u`), before any HOLD (2025-01-01..2026-10-29) number of this rule was
computed. Stream D2 did not request, load or summarise any 2025-26 series; the HOLD switch in the code was never set.
The coordinator opens HOLD once. Rule declared 17:44 UTC in [HYPOTHESES_D2.md](HYPOTHESES_D2.md) (timing amended
17:46 UTC, before any return was computed).

## Rule (fixed)
- Assets BTC and ETH, 50 / 50 of notional N. Per asset: short the Binance USDT-M perp (USDT collateral m = N/2), long
  the Deribit inverse perp (BTC-PERPETUAL / ETH-PERPETUAL) with coin collateral m = N/2 (bought once), inverse size
  V = N - M x S so that the Deribit account's USD delta equals N. Leverage 2 per venue, capital C = N.
- Always on. Daily marks at 00:00 UTC (close of the 23:00 1h bar on both venues; Deribit index at 00:00).
- Rebalance at a mark when |Deribit delta - Binance delta| > 5 % of N or the Binance notional leaves [0.8, 1.2] N; move
  capital between venues when either venue's equity leaves [0.6, 1.6] x m (conversion 0.10 % of the coin amount).
- Costs: Binance taker 0.05 % + 0.01 % half spread; Deribit taker 0.075 % + 0.01 %; spot 0.10 % on collateral.
- Code: `D2/code/d2.py` (`load`, `daily`, `simulate`), `D2/code/hold_run.py`. Data: Deribit public
  `get_funding_rate_history` (hourly `interest_1h`) and `get_tradingview_chart_data` (1h), Binance local
  `binance_1h_full/1h` and `binance/funding`, DFF.

## Evidence before HOLD (IS 2020-21, VAL 2022-24; net of costs, daily book, NW t lag 10)
| | IS | VAL |
|---|---|---|
| net %/yr on N | +22.70 (t 8.30, SR 8.65) | +5.32 (t 7.11, SR 5.07) |
| years | 2020 +19.38, 2021 +26.08 | 2022 +3.97, 2023 +4.51, 2024 +7.50 |
| excess over DFF on C = N | +22.47 (t 8.24) | **+1.37 (t 1.83)**; by year 2022 +2.28, **2023 -0.51**, 2024 +2.34 |
| costs x1.5 / one day late | +22.28 / +22.70 | +5.09 / +5.32 |
| decomposition %/yr | Binance funding +29.70, Deribit funding -5.77, price -0.38, costs -0.85 | +7.95, -1.96, -0.21, -0.46 |

BTC alone: IS +17.99 (t 7.11), VAL +5.30 (t 6.79), VAL excess +1.35 (t 1.71). ETH alone: IS +27.41 (t 8.75), VAL +5.34
(t 6.39), VAL excess +1.39 (t 1.68). Max-over-6-cells null: IS best t 8.75 vs null 95th pct 2.42 (p < 0.001).
Random benchmark: none meaningful for an always-on rule (random side = minus the book).

**Power at VAL size for HOLD (667 days):** raw 6.85, **excess over cash 1.76** (below 3).

## What the evidence says (read before opening HOLD)
- About half of the VAL net is not the D2 mechanism: with coin collateral, half the Deribit delta is spot coins that
  pay no funding, so the book is perp-perp on N/2 plus spot-perp carry on N/2 (round 58's A1, which earned the cash
  rate in round 58's HOLD). The "pure" pair (USD-stable Deribit collateral, descriptive) had VAL excess over cash
  BTC +0.06 % (t 0.05), ETH +0.98 % (t 0.79).
- The funding gap itself (Binance - Deribit, %/yr) shrank: BTC 2020 8.0, 2021 14.1, 2022 6.4, 2023 1.0, 2024 1.6;
  ETH 21.2, 20.2, 6.9, 0.4, 4.6. Deribit longs now pay most of Binance's anchor (premium arbitrage).
- Excess over cash was negative in 2023 for all three ON cells; it is positive in VAL only because 2022's cash rate
  averaged 1.7 %.
- Liquidation check (daily marks, last-trade 1h extremes): at L = 2 the IS book had 1 (BTC) and 4 (ETH) days where an
  intraday move exceeded the leg's equity (2020-03-12, 2021-05-19 Deribit long; ETH 2020-03-13 is a 323 USDT
  last-price wick on Binance, liquidation uses mark price). Live operation needs intraday margin top-ups. At L = 1.5
  the VAL excess drops to +0.93 % (t 1.21) and would fail the IS / VAL cash bar.

Prior for the HOLD bar below: ~35 %; for an economically useful LIVE (excess over cash material): ~5 %.

## Pass bar at HOLD (all of; same form as round 59's B2)
1. BOTH ON net > 0 with t_nw >= 2.5, and excess over DFF on C = N > 0.
2. Net > 0 at costs x1.5 and one day late.
3. 2025 and 2026 (to 10-29) both net > 0.
Reading: the coordinator should treat excess over cash as the decisive number. If HOLD excess t < 1.5, the rule earns
the cash rate (round 58 reading) and is not a LIVE bot even if items 1-3 pass.

## Stop / promotion
- Fail any item: FAIL, family closed (with round 59 B1 / B2: cross-venue funding carry at or below cash).
- Pass with excess t >= 1.5: LIVE candidate, still needs a user decision on venue risk (Deribit + Binance custody,
  coin collateral, intraday margin transfers).
- Pass with excess t < 1.5: report as "registered bar pass, economically rejected" (round 58 A3 precedent).

## HOLD procedure (coordinator, once)
`D2_HOLD=1 python -I pull.py` (Deribit to 2026-10-29 23:59:59 into raw_hold/), `D2_HOLD=1 python -I parse.py`,
then `D2_HOLD=1 python -I hold_run.py`. Check first that local Binance 1h and funding files cover 2025-01..2026-10-29.

## Code hashes at registration (sha256, first 16)
- `D2/code/d2.py` cab8e4c78a0ddf31
- `D2/code/hold_run.py` bf85af6a1b1eea40
- `D2/code/pull.py` 16a501e0fd5f6618
- `D2/code/parse.py` 5ece2f78ab81764a
- `D2/code/fetch.py` 460931425ae4b7fb
- `D2/code/run.py` 72ce52b8224484d9

## Registration (coordinator, 2026-11-01 17:58 UTC, before any HOLD value was read)
Registered as drafted (bar, stop / promotion, reading of excess over cash). Tier on IS / VAL: LIVE bars on raw net,
but graded on excess over cash (capital-heavy coin collateral): VAL excess +1.37 %/yr (t 1.83), power 1.76 < 3, so the
registered tier is **DEMO**; the HOLD bar is the draft's (items 1-3, excess t >= 1.5 for an economically useful pass).
Plumbing amendment before HOLD: d2.py reads Binance 1h from research/data/deribit_funding/hold_binance_1h/ in HOLD
mode only (the 2019-24 rows copied unchanged from binance_1h_full, 2025-26 pulled by coord/hold_binance_1h.py);
IS / VAL re-run unchanged after the edit (BOTH ON IS +22.70 t 8.30, VAL +5.32 t 7.11, excess +1.37 t 1.83).
Hashes now:
- `research/results/portfolio/round70_filings_lit/D2/code/d2.py` 437d39b874bb36c3
- `research/results/portfolio/round70_filings_lit/D2/code/hold_run.py` bf85af6a1b1eea40
- `research/results/portfolio/round70_filings_lit/D2/code/pull.py` 16a501e0fd5f6618
- `research/results/portfolio/round70_filings_lit/D2/code/parse.py` 5ece2f78ab81764a
- `research/results/portfolio/round70_filings_lit/D2/code/fetch.py` 460931425ae4b7fb
- `research/results/portfolio/round70_filings_lit/D2/coord/hold_binance_1h.py` a79ea5d4559d17cb

## HOLD result
(appended after the single run)

Data pulled 18:00-18:08 UTC (Binance 1h 16,008 new rows per asset; Deribit 663 requests, 3 x 404). Run once 2026-11-01
18:08 UTC (`D2_HOLD=1 hold_run.py`, output `coord/hold_output_2026-11-01.txt`):

| HOLD 2025-01..2026-10-29 | net %/yr | t_nw | excess over DFF (C = N) | x1.5 | late | 2025 / 2026 net | 2025 / 2026 excess |
|---|---|---|---|---|---|---|---|
| BOTH ON | +2.64 | 6.77 | **-1.32 (t -3.48)** | +2.43 | +2.64 | +3.28 / +1.55 | -0.93 / -1.48 |

- Item 1 requires excess over DFF > 0: **FAIL**. The book earns less than the cash rate (Binance funding +3.95 %/yr,
  Deribit funding leg now a cost of 1.30, price +0.42, costs 0.43). **Dropped; family closed** with round 59 B1 / B2:
  cross-venue funding carry is at or below cash in 2025-26.
