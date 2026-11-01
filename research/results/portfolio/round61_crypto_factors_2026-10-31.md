# Round 61: weekly cross-sectional factors on Binance perps (momentum, funding carry), 2026-10-31

Declared in [round61_crypto_factors/HYPOTHESES.md](round61_crypto_factors/HYPOTHESES.md) (12:52 UTC). Registration and
HOLD: [PREREG_X3_crypto_mom_carry.md](round61_crypto_factors/PREREG_X3_crypto_mom_carry.md). Code
`round61_crypto_factors/code/` (`factors.py`, `run.py`, `x3_check.py`, `hold_run.py`). Data from rounds 58 / 60.

Universe: weekly top 40 perps by volume (aged >= 60 d); long 8 / short 8, equal weight, gross 1 per side, 7-day hold,
funding and taker costs included; t Newey-West lag 4 on weekly returns.

| Book | IS 2020-21 mean / wk, t_nw | VAL 2022-24 | HOLD 2025-01..2026-10 | verdict |
|---|---|---|---|---|
| X1 momentum (past 28 d) | +2.20 %, 2.37 | +0.79 %, 1.28 | (reported) +3.29 %, 2.47 | fails IS / VAL t |
| X2 funding carry (short high funding) | +2.58 %, 3.41 | +0.87 %, 1.29 | (reported) -1.01 %, -0.72 | fails VAL t |
| **X3 = 50 / 50** | +2.39 %, **4.32** | +0.83 %, **1.51** | **+1.14 %, 1.16** | **DEMO** (HOLD net > 0) |

X3 before HOLD: 5/5 years positive, costs x1.5 and one day late positive, beats 100 % of shuffled sorts, weekly
correlation with C3 -0.02 / -0.03. It is not LIVE because the HOLD power at VAL size is 0.136 x sqrt(95) = 1.33: a
weekly book needs an annual Sharpe >= ~2.2 to be LIVE-testable on a 21-month HOLD, and X3's VAL annual Sharpe is ~1.0.
Volatility is large (weekly sd 7-12 %, worst HOLD week -30 %).

DEMO terms (stop / promotion) are in the prereg. Building a demo (Binance testnet or a paper log) is the user's call.

Lesson: on a 21-month HOLD any directional book needs annual Sharpe >= 2.2 for LIVE; crypto factors reach ~1.
