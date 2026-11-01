# Round 60: short new Binance USDT-M perp listings, BTC-hedged, held 30 days, 2026-10-31

Declared in [round60_new_listings/HYPOTHESES.md](round60_new_listings/HYPOTHESES.md) (12:38 UTC, before any
post-listing return). Code: `round60_new_listings/code/` (`listings.py`, `run.py`; `explore_stop.py` is post-hoc).
Data: round 58's perp 1d klines (886 USDT perps incl. delisted), funding for the first 75 days of the 496 listings not
already pulled (research/data/binance/funding_window/), first spot kline of 884 spot pairs (spot_first.csv) for groups.
Events: first 1d kline per base asset, excluding re-denominations, stable / index / TradFi perps.

## N1 (registered form): short at L0 + 1 close, long BTCUSDT equal notional, exit L0 + 31; fixed quantity

| Variant | Era | n | mean / ep | median | sd | SR / ep | t (entry-month cluster) | years (mean %) |
|---|---|---|---|---|---|---|---|---|
| **N1** | IS 2020-21 | 126 | +9.62 % | +17.8 % | 47.6 % | 0.202 | **1.11** | 2020 +15.6, 2021 +1.4 |
| **N1** | VAL 2022-24 | 248 | +6.55 % | +20.7 % | 58.5 % | 0.112 | **1.30** | +4.2, +3.0, +9.7 |
| costs x1.5 | IS / VAL | | +9.41 / +6.34 % | | | | 1.09 / 1.25 | |
| k = 2 | IS / VAL | | +7.47 / +7.72 % | | | | 0.83 / 1.45 | |
| unhedged | IS / VAL | | +4.73 / +0.34 % | | | | 0.42 / 0.06 | 2023 -5.1 |
| k 7 / H 14 / H 60 | VAL | | +4.9 / +2.1 / +11.5 % | | | | 0.90 / 0.67 / 1.74 | H 60 IS -20.7 % (2021 -89 %) |
| group NEW (no spot / spot <= 30 d) | IS / VAL | 39 / 138 | +28.0 / +1.8 % | | | | 2.72 / 0.23 | VAL 2022 -20.5 |
| group OLD (spot >= 180 d) | IS / VAL | 61 / 93 | +2.7 / +12.2 % | | | | 0.37 / 2.70 | |

Random benchmark (random alt listed >= 365 d, top-60 volume, same dates / hedge): N1 beats 100 % in both eras (random
median -16.3 % IS, +1.2 % VAL). Tails: adverse move > 100 % in 13 / 126 (IS) and 21 / 248 (VAL) episodes; worst
BANDUSDT -200 %, LUNAUSDT -192 % (IS), 1000BONK -345 %, GAS -325 %, GMT -324 % (VAL).

**Verdict: no LIVE or DEMO candidate.** N1 fails t in both eras (1.11 / 1.30 vs 2.5 / 1.5). The effect is real in the
median (new listings fall ~20 % against BTC in their first month, beating random alts every era) but the squeeze tail
makes the mean noisy, and which group carries it flips between eras (NEW in IS, OLD in VAL).

Post-hoc (after IS / VAL were seen, not registrable): a stop on the alt's daily high at +30 / +50 / +100 % gives VAL
t 2.54 / 3.39 / 2.66 but IS 1.83 / 1.21 / 1.07; at a quarter of VAL size (round 18 rule) the HOLD power would be ~0.9.
HOLD not opened.
