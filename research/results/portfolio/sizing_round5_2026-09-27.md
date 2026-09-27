# Round 5: capital-based lots with a 60 % drawdown limit (2026-09-27)

The user relaxed one constraint: **a lot may depend on account capital, and the loss may not exceed 60 % of the
account**, read here as a maximum peak-to-trough drawdown of 60 %. The other rules are unchanged (a position is held
5 days at most, a bot holds 3 positions at most) and so is the pass bar. Previous rounds:
[flow_search_2026-09-27.md](flow_search_2026-09-27.md), [flow_search_round4_2026-09-27.md](flow_search_round4_2026-09-27.md).

## Answer

**No new algorithm.** Sizing multiplies a strategy's expectancy per trade (mean R); it cannot create one. Every
earlier rejection was for mean R that was about zero or unstable, not for size, so those verdicts stand. The
relaxation opens three things, and each was tested:

| what the relaxation allows | test | verdict |
|---|---|---|
| Harvesting a risk premium at meaningful size (it earns from exposure, not timing): the equity premium, swap-free, with volatility-managed capital-based exposure (Moreira & Muir 2017) | US30, USTEC, US500; IS/VAL | beta without skill: vol timing does not beat constant exposure or a shuffled-leverage control; VAL Sharpe 0.2-0.3. Not a candidate |
| Loss-dependent sizing: a 1-2-4 martingale that averages down | 26 symbols; IS/VAL | high win rate (73-85 %) with insignificant expectancy and extreme tails. Not a candidate |
| Compounding a real edge (C3) | C3 research and cTrader trade lists | this is where the relaxation has value; numbers and stress test below |

## 1. Swap-free equity premium with volatility-managed, capital-based exposure

**Why swap-free.** IC's long index swap is about the policy rate plus ~5 %/yr, fitted to the 2026 swaps
(`research/swing/rates.py`). The strategy goes flat from 16:45 to 18:15 New York every weekday (around the 17:00
rollover) and over weekends: long 18:15 NY -> 16:45 NY the next weekday (Sunday 18:15 for Mondays), bought at the ask
and sold at the bid.

| | return while held (mid) | flat window + weekends | cost of the daily round trip | Sharpe while held |
|---|---|---|---|---|
| US500 IS / VAL | +18.8 / +8.5 %/yr | -3.2 / +0.3 %/yr | 4.7 / 2.5 %/yr (median 2.1 / 1.1 bp a day) | 1.20 / 0.52 |
| US30 IS / VAL | +17.2 / +8.0 %/yr | -3.2 / -0.2 %/yr | 3.0 / 0.9 %/yr (1.2 / 0.4 bp a day) | 1.06 / 0.58 |
| USTEC IS / VAL | +21.7 / +7.5 %/yr | -1.1 / +1.6 %/yr | 7.6 / 2.9 %/yr (2.8 / 1.4 bp a day) | 1.14 / 0.34 |

**Volatility management.** Exposure = equity x (15 %/yr target) / EWMA volatility (half-life 10 days), capped at 3x.
The control holds constant exposure at the vol-managed strategy's mean IS leverage. The random-sizing control (the
analogue of "beats random entries" for a strategy that is always in the market) shuffles the same leverage series
across days, 500 seeds.

| | vol-managed CAGR / Sharpe / max DD | constant exposure CAGR / Sharpe / max DD | real beats shuffled leverage |
|---|---|---|---|
| US30 IS | +11.9 % / 0.77 / 19 % | +18.3 % / 0.82 / 34 % | 53 % |
| US30 VAL | +2.4 % / 0.23 / 20 % | +3.1 % / 0.26 / 28 % | 49 % |
| USTEC IS | +8.3 % / 0.58 / 20 % | +15.3 % / 0.79 / 23 % | 20 % |
| USTEC VAL | +2.9 % / 0.26 / 24 % | -0.9 % / 0.08 / 38 % | 87 % |
| US500 IS | +10.4 % / 0.69 / 23 % | +19.4 % / 0.87 / 31 % | 25 % |
| US500 VAL | +1.9 % / 0.20 / 21 % | +1.0 % / 0.16 / 34 % | 60 % |

Volatility management lowers drawdown but adds no Sharpe, and the timing does no better than shuffled leverage. What
is left is the equity premium itself: VAL Sharpe 0.2-0.3 (t about 0.4). It would look "positive in all three eras"
simply because 2016-2026 was a bull market, and everyone already knows that 2025-26 was one too. So HOLD could not
test it. It is an investment in the index, not an algorithm with an edge, and it is not registered.

## 2. Averaging down (martingale)

The canonical design was fixed before running. After a daily (20:00 UTC) close more than 1.5 x ATR20(D1) from the
previous close, fade it: 1 unit at the next minute's open, 2 units if price moves another 1 ATR against, 4 units at
2 ATR. Exit everything when price returns to the first entry (or at +0.5 ATR if nothing was added), otherwise at 5
days. No stop: the 60 % drawdown budget is the stop. Real bid/ask and commission; P&L in (1 unit x daily ATR).

| | cycles | mean per cycle | t | win | worst cycle |
|---|---|---|---|---|---|
| 7 FX majors, 1-2-4, IS / VAL | 242 / 138 | +0.189 / +0.299 | 1.3 / 1.4 | 76 / 78 % | -17.8 / -13.2 |
| same, flat adds 1-1-1 | 242 / 138 | +0.023 / +0.106 | 0.3 / 1.0 | 74 / 75 % | -8.9 / -6.9 |
| same, no adds (the fade alone) | 242 / 138 | -0.048 / +0.009 | -0.9 / 0.1 | 61 / 62 % | -4.0 / -3.3 |
| random days, same 1-2-4 (40 seeds) | | -0.025 +/- 0.09 / -0.026 +/- 0.10 | | | |
| FX (all 10 pairs) | 349 / 209 | +0.167 / +0.264 | 1.1 / 1.2 | 76 / 80 % | -27.6 / -19.6 |
| indices | 386 / 172 | +0.144 / +0.138 | 0.6 / 0.6 | 85 / 82 % | -46.8 / -27.7 |
| metals | 115 / 58 | +0.089 / -0.152 | 0.2 / -0.5 | 73 / 76 % | -29.0 / -12.2 |
| energies | 85 / 43 | +0.142 / +0.245 | 0.4 / 0.6 | 85 / 81 % | -19.4 / -11.2 |
| crypto | 87 / 68 | -0.290 / -0.872 | -0.5 / -1.1 | 82 / 81 % | -21.5 / -33.0 |

The FX 1-2-4 beats the random-day control, so what little there is sits in the deep adds: moves extended 2.5-3.5 ATR
tend to revert a bit. But t is 1.1-1.4 per era, the fade alone has no edge, and single cycles lose 18-47 units. That
is the averaging-down profile (a high win rate paid for by rare large losses), not a significant expectancy. With a
60 % drawdown budget, the tail sets the size, and one bad cycle can use most of it.

## 3. What the relaxation is worth: compounding C3

`python -m research.swing.account <trades> --risk ...` (new, `research/swing/account.py`): each trade risks f x equity
at its entry. This is not a new test; C3's holdout was already used.

| risk / trade | research engine (4,590 trades, R +0.042): CAGR / max DD | cTrader IC ticks (4,574 trades, R +0.049): CAGR / max DD |
|---|---|---|
| 1 % | +19 % / 12 % | +22 % / 10 % |
| 2 % | +39 % / 24 % | +47 % / 19 % |
| 3 % | +60 % / 34 % | +75 % / 28 % |
| 4 % | +81 % / 43 % | +105 % / 36 % |
| 6 % | +122 % / 59 % | +169 % / 50 % |

Research engine by year at 2 %: 2016 +74 %, 2017 +46 %, 2018 +22 %, 2019 +35 %, 2020 +20 %, 2021 +50 %, 2022 +53 %,
2023 +16 %, 2024 +46 %, 2025 +32 %, 2026 (to Sep) +34 %. The cTrader figures apply 2026 swaps to every year, which
flatters 2016-2021.

**Stress: the true edge smaller than estimated** (every trade's R shifted down):

| true mean R | 1 % | 2 % | 3 % | 4 % | 6 % |
|---|---|---|---|---|---|
| +0.042 (as estimated) | +19 % / DD 12 % | +39 % / 23 % | +60 % / 34 % | +81 % / 43 % | +122 % / 59 % |
| +0.021 (halved) | +9 % / 16 % | +16 % / 30 % | +22 % / 42 % | +27 % / 54 % | +30 % / 73 % |
| 0 (no edge) | -1 % / 30 % | -3 % / 57 % | -7 % / 76 % | -12 % / 89 % | -25 % / 98 % |

C3's edge is estimated at +0.042 R with a HOLD t of 2.9, so a halved edge is well within its uncertainty. Over ten
years of this trade sequence, the 60 % limit held in all three scenarios only at 2 % or less, and at 3 % or less if
the edge is at least half of the estimate. The compound multiples in the first table are illustrations. Lot limits,
liquidity at the Tokyo fix and slippage would cap them long before x30 or more. This is research output, not a
recommendation of how much of an account to risk.

## Files

- `research/swing/account.py` (capital-based compounding simulator, test in `research/tests/swing/test_swing.py`).
- The equity-premium and martingale screens ran as scratch scripts on the M1 cache (designs described above); neither
  reached a candidate, so neither is in the repo.
