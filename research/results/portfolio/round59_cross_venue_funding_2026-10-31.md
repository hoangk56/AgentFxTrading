# Round 59: cross-venue perp-perp funding spread (Binance vs Bybit), 2026-10-31

Declared in [round59_cross_venue_funding/HYPOTHESES.md](round59_cross_venue_funding/HYPOTHESES.md) (12:02 UTC; B1 first
declared 11:04 UTC in round 58's HYPOTHESES_B.md). Code: `round59_cross_venue_funding/code/` (`xvenue.py`, `b1.py`,
`pull_venues.py`). Why: round 58 showed spot-perp carry since 2025 earns only the cash rate; a perp-perp pair across
venues cancels funding's fixed interest component and needs only margin.

Data: Bybit linear funding + 1d klines for 252 of the 259 symbols ever in round 58's Binance top-30 universe
(research/data/bybit/, git-ignored; ~7 requests/s, no errors). Pairs cover 66 % of universe days (Bybit listings lag).

## B1 (one cell, no grid): trailing-7-day Binance - Bybit funding > 15 %/yr in, < 5 %/yr or sign flip out, K 10

| Era | net ann. | vol | t_nw | excess over cash (margin 2/3) | years | costs x1.5 | late | random beaten |
|---|---|---|---|---|---|---|---|---|
| IS 2020-06..2021-12 | +10.48 % | 1.41 % | 4.65 | +10.46 % (t 4.64) | 2020 +2.33, 2021 +14.28 | +9.13 % | +9.94 % | 100 % |
| VAL 2022-24 | **-0.14 %** | 1.07 % | -0.20 | -1.03 % (t -1.51) | +0.71, **-2.60**, +1.46 | -2.28 % | -0.69 % | 100 % |

Gross split: IS +13.2 %/yr = funding spread +13.2, price divergence -0.03; VAL +4.1 %/yr = funding +4.7, price -0.6,
against ~4.3 %/yr of taker costs (96 episodes/yr, median hold 10 days). Binance was the dearer venue in only 24-34 % of
episodes (Bybit funding usually higher).

**Verdict: FAIL** (VAL net < 0). The spread is real gross in VAL but the same size as taker costs. A maker-only
execution would cut costs to ~1 %/yr, but that variant is chosen after seeing VAL (round 18 lesson: ~1/4 of VAL size
survives HOLD), so it is not registered. HOLD not opened.

## Not run
B2 (Binance vs Hyperliquid): Hyperliquid's fundingHistory is weight-limited (~26 pages/min; hourly funding since
2023-05 needs ~60 pages per coin), and with no IS era B2 could reach RELAXED at most. Left for a user decision.

## B2 (run later the same day): Binance vs Hyperliquid, 30 coins
Hyperliquid funding (hourly since 2023-05, research/data/hyperliquid/, ~26 requests / min API limit) for the 30 overlap
coins with the largest Binance volume before 2025. Same rule and thresholds as B1 (declared 12:02 UTC).
DISCOVERY 2023-06..2024-12: +16.30 %/yr (t_nw 6.81), excess over cash +13.49 % (t 5.79), both years positive, costs
x1.5 +13.79 %. Registered and opened HOLD once
([PREREG_B2_binance_hyperliquid.md](round59_cross_venue_funding/PREREG_B2_binance_hyperliquid.md)): +0.74 %/yr,
t 1.27, excess over cash -0.35 %, costs x1.5 -1.36 %: **FAIL**. Cross-venue funding gaps close within ~18 months of a
venue's growth; every funding-based carry tested in rounds 58-59 is now at or below the cash rate.
