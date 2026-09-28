# C3: sizing and trade management (2026-09-28)

Questions asked while planning a compounding version of the Gotobi bot (C3, `cBot/GotobiBot.cs`): what compounding
changes compared with a fixed $ risk, whether one position at a time beats the three-pair basket, and whether
averaging down, pyramiding or holding losing legs improves C3. Previous round on sizing:
[sizing_round5_2026-09-27.md](sizing_round5_2026-09-27.md).

## Answer

**Sizing changes the $ path, not the edge, and no trade-management rule improves C3.** Compounding at 3 % grows much
faster than a fixed $ risk over ten years but with about twice the drawdown, and the two are much closer over the
21-month holdout. Adds to a leg, against it or in its favour, earn a mean R of about zero; averaging down and
holding losers raise the drawdown, and holding losers also lowers mean R. C3's edge is in its fixed entry and exit times; nothing about the price path in between adds to
it. Sections 3 and 4 were run on IS 2016-2021 and VAL 2022-2024 only, so the 2025-26 holdout is still unseen for
those rules.

## Method

- Trade lists: `trades_C3_gotobi_jpy_basket.csv` (research engine, 4,590 trades, R +0.042) and
  `gotobi_cbot_trades.csv` (cTrader on IC ticks, 4,574 trades, R +0.049, read at $50 risk per trade).
- Account curves use `research/swing/account.py`: each trade's P&L is realized at its exit, and a trade opened while
  others run is sized off the equity realized so far. "Compounding" = each trade risks f x that equity; "fixed" =
  each trade risks f x the starting balance. Max DD is on realized equity, so it leaves out floating losses.
- Sections 3 and 4 re-simulate each C3 leg on the M1 cache (bid OHLC plus the ask at each minute's close), with
  spread, commission and swaps (`research/swing/rates.py`) as in `research/swing/swing.py`. The re-simulation
  reproduces C3 exactly (IS R +0.043, VAL +0.041; 3 % compounding CAGR +62 % / DD 34 % and +57 % / DD 29 %).
- "t_day" sums R over each gotobi day (3 pairs, both legs) and tests those daily sums, because the three pairs move
  together.
- The probes ran as scratch scripts on the M1 cache, like the round-5 screens; they are not in the repo. The designs
  are described in each section.

## 1. Compounding vs a fixed $ risk (3 % per trade)

`R shifted` moves every trade's R down by 0.021 (half of the research engine's estimate).

| trades | edge | compounding: multiple / CAGR / max DD | fixed: multiple / CAGR / max DD |
|---|---|---|---|
| research engine 2016-2026 | as estimated (R +0.042) | x154 / +60 % / 34 % | x6.8 / +20 % / 16 % |
| research engine 2016-2026 | R shifted (+0.021) | x8.6 / +22 % / 42 % | x3.9 / +14 % / 22 % |
| research engine 2016-2026 | none (R 0) | x0.45 / -7 % / 77 % | x1.00 / 0 % / 58 % |
| cTrader 2016-2026 | as estimated (R +0.049) | x400 / +75 % / 28 % | x7.7 / +21 % / 12 % |
| cTrader 2016-2026 | R shifted (+0.028) | x22.6 / +34 % / 32 % | x4.8 / +16 % / 17 % |
| cTrader 2016-2026 | none (R 0) | x0.49 / -6 % / 73 % | x1.00 / 0 % / 55 % |
| research engine HOLD 2025-01..2026-09 | as estimated (R +0.042) | x2.25 / +61 % / 23 % | x1.93 / +47 % / 15 % |
| research engine HOLD | R shifted (+0.021) | x1.42 / +23 % / 25 % | x1.47 / +25 % / 20 % |
| research engine HOLD | none (R 0) | x0.89 / -7 % / 29 % | x1.00 / 0 % / 30 % |

Win rate, mean R and the number of trades are the same under both sizings. Over ten years compounding multiplies the
return and roughly doubles the drawdown. Over 21 months the gap is much smaller, and with a weaker edge the fixed
risk is slightly ahead. With no edge, compounding still loses (volatility drag) while the fixed risk stays flat. As in round
5, the ten-year multiples are illustrations: the 5-lot cap, liquidity at the Tokyo fix and slippage would stop them
long before.

## 2. One pair at a time vs the basket (research engine, 3 % per trade)

The three pairs enter at the same minutes, so the basket holds up to 3 positions at once. Their R on the same entry
correlate strongly: USDJPY-EURJPY +0.72, USDJPY-GBPJPY +0.68, EURJPY-GBPJPY +0.84 (about 1,510 shared entries each).
At 3 % per pair, a gotobi event therefore carries about 9 % of the account on one yen move. "One position at a time"
across the basket means trading a single pair. The t column is the plain per-trade t.

| | 2016-2026: n / R / t | compounding CAGR / DD | fixed CAGR / DD | HOLD: n / R / t | compounding CAGR / DD | fixed CAGR / DD |
|---|---|---|---|---|---|---|
| basket, 3 % per pair (9 % per event) | 4,590 / +0.042 / 7.2 | +60 % / 34 % | +20 % / 16 % | 738 / +0.042 / 2.9 | +61 % / 23 % | +47 % / 15 % |
| basket, 1 % per pair (3 % per event) | same trades | +19 % / 12 % | +11 % / 7 % | same trades | +19 % / 8 % | +17 % / 7 % |
| USDJPY only, 3 % | 1,530 / +0.058 / 5.2 | +27 % / 16 % | +13 % / 7 % | 246 / +0.038 / 1.3 | +16 % / 15 % | +16 % / 13 % |
| EURJPY only, 3 % | 1,530 / +0.041 / 4.2 | +18 % / 13 % | +10 % / 8 % | 246 / +0.057 / 2.4 | +27 % / 6 % | +23 % / 6 % |
| GBPJPY only, 3 % | 1,530 / +0.028 / 3.0 | +12 % / 13 % | +8 % / 9 % | 246 / +0.031 / 1.5 | +14 % / 7 % | +13 % / 6 % |

At the same risk per event (3 %), a single pair returns about what the basket does, usually with a larger drawdown.
The best pair changes between periods (USDJPY over ten years, EURJPY in HOLD), so choosing one now would be choosing
on hindsight. Only the basket was pre-registered and passed.

## 3. Adding to a leg: averaging down and pyramiding (IS / VAL)

**Design.** An add is a limit order a x ATR20(H1) from the leg's entry: against the position for averaging down (a
buy fills when the ask touches the level, a sell when the bid does), in its favour for pyramiding. The add shares the
leg's stop price (3 x ATR from the first entry) and its exit (the scheduled time or the stop), and risks the same
amount at its own stop distance. When the add fills in the minute the stop is hit, it is counted as stopped out. R of
an add = net move per unit / its own stop distance.

**Averaging down, 3 % compounding.** Base: IS n 2,568, R +0.043 / VAL n 1,284, R +0.041.

| a (ATR against) | add stop | adds IS / VAL | R of the add, IS (t_day) | R of the add, VAL (t_day) | IS CAGR / DD | VAL CAGR / DD |
|---|---|---|---|---|---|---|
| no add (C3) | | | | | +62 % / 34 % | +57 % / 29 % |
| 0.5 | 2.5 ATR | 1,274 (50 %) / 668 (52 %) | +0.022 (1.2) | +0.004 (0.2) | +65 % / 55 % | +44 % / 50 % |
| 1.0 | 2.0 ATR | 614 (24 %) / 326 (25 %) | +0.019 (0.6) | -0.015 (-0.3) | +59 % / 59 % | +38 % / 48 % |
| 1.5 | 1.5 ATR | 303 (12 %) / 160 (12 %) | +0.010 (0.2) | +0.002 (0.0) | +54 % / 52 % | +47 % / 50 % |
| 2.0 | 1.0 ATR | 156 (6 %) / 90 (7 %) | +0.051 (0.3) | +0.067 (0.4) | +57 % / 55 % | +55 % / 50 % |
| 2.5 | 0.5 ATR | 89 (3 %) / 51 (4 %) | -0.197 (-1.1) | -0.010 (0.0) | +43 % / 58 % | +48 % / 49 % |

**Averaging down, fixed $ risk** (C3 as the bot runs it; 1 R = the bot's $ risk per trade). Multi-add variants add
at both levels; "1-2-4" adds 2 R and then 4 R.

| variant | IS total R / max DD R / worst day R / t_day | VAL total R / max DD R / worst day R / t_day |
|---|---|---|
| no add (C3) | +110.8 / 12.6 / -4.2 / 3.5 | +52.5 / 11.0 / -4.6 / 2.2 |
| C3 at 2 R per trade (for comparison) | +221.6 / 25.2 / -8.4 / 3.5 | +105.0 / 22.0 / -9.2 / 2.2 |
| 1 add at 1 ATR | +122.6 / 22.3 / -7.5 / 2.7 | +47.7 / 19.8 / -8.9 / 1.4 |
| 1 add at 0.5 ATR | +138.5 / 23.3 / -8.1 / 2.7 | +55.5 / 20.5 / -9.0 / 1.5 |
| 2 adds at 0.5 / 1 ATR | +150.2 / 37.9 / -11.4 / 2.2 | +50.7 / 29.3 / -13.4 / 1.1 |
| 2 adds at 1 / 2 ATR | +130.5 / 41.7 / -9.3 / 2.1 | +53.7 / 29.9 / -12.7 / 1.2 |
| 1-2-4 at 0.5 / 1 ATR | +213.3 / 119.1 / -25.2 / 1.5 | +39.3 / 65.6 / -31.0 / 0.4 |
| 1-2-4 at 1 / 2 ATR | +166.1 / 125.8 / -21.9 / 1.1 | +67.0 / 72.7 / -28.3 / 0.7 |

**Pyramiding (adding in the leg's favour), 3 % compounding.**

| a (ATR in favour) | add stop | adds IS / VAL | R of the add, IS (t_day) | R of the add, VAL (t_day) | IS CAGR / DD | VAL CAGR / DD |
|---|---|---|---|---|---|---|
| 0.5 | 3.5 ATR | 1,727 (67 %) / 904 (70 %) | +0.007 (0.6) | -0.010 (-0.6) | +55 % / 48 % | +28 % / 47 % |
| 1.0 | 4.0 ATR | 944 (37 %) / 478 (37 %) | +0.003 (0.2) | -0.007 (-0.3) | +55 % / 37 % | +44 % / 35 % |
| 1.5 | 4.5 ATR | 476 (19 %) / 222 (17 %) | +0.004 (0.2) | +0.005 (0.2) | +58 % / 36 % | +54 % / 30 % |
| 2.0 | 5.0 ATR | 223 (9 %) / 110 (9 %) | +0.027 (0.7) | +0.018 (0.4) | +63 % / 34 % | +57 % / 30 % |
| 2.5 | 5.5 ATR | 119 (5 %) / 46 (4 %) | +0.042 (0.7) | +0.087 (1.0) | +63 % / 35 % | +61 % / 29 % |

Once a leg has moved a x ATR either way, the rest of the leg has a mean R of about zero: no add reaches a day-clustered
|t| above 1.2 in either era. Averaging down raises the drawdown from 29-34 % to 48-59 % at 3 % compounding and
roughly doubles it at a fixed risk, where 1-2-4 multiplies it by 6-10. The extra return in IS does not repeat in VAL.
At the same drawdown, doubling C3's own risk earns more than any averaging-down variant.

## 4. Holding losing legs to break-even (IS / VAL)

**Design.** At the scheduled exit (00:55 UTC for the long leg, 02:55 UTC for the short leg), a leg whose net P&L is
negative stays open until the price is back at break-even (entry + commission, filled as a limit), its stop, or 5
days after entry (the lab's hold limit). One position per symbol as in GotobiBot: a leg is skipped while an earlier
one is still held on that symbol. R = net / the C3 stop distance, so without a stop a loss can exceed 1 R. MAE =
worst unrealized R; "worst day MAE" adds the MAE of the legs entered on one gotobi day (an upper bound, since the
worst points need not coincide). Compounding at 3 %.

| variant | legs IS / VAL | win IS / VAL | R IS (t_day) | R VAL (t_day) | worst leg R IS / VAL | worst day MAE IS / VAL | IS CAGR / DD | VAL CAGR / DD |
|---|---|---|---|---|---|---|---|---|
| C3 (stop, exit on schedule) | 2,568 / 1,284 | 56 % / 56 % | +0.043 (3.5) | +0.041 (2.2) | -2.1 / -1.1 | -5.2 / -5.2 | +62 % / 34 % | +57 % / 29 % |
| no stop, exit on schedule | 2,568 / 1,284 | 56 % / 56 % | +0.046 (3.7) | +0.040 (2.1) | -2.6 / -2.9 | -9.3 / -9.5 | +67 % / 32 % | +53 % / 35 % |
| stop kept, hold losers | 2,077 / 1,019 | 67 % / 75 % | +0.043 (2.7) | +0.035 (1.7) | -2.8 / -1.1 | -3.8 / -4.5 | +45 % / 42 % | +34 % / 51 % |
| no stop, hold losers | 1,988 / 972 | 69 % / 81 % | +0.021 (0.8) | +0.037 (1.2) | -7.7 / -6.8 | -23.5 / -15.5 | -5 % / 90 % | +21 % / 56 % |

Held legs: with the stop, IS 827 (630 back to break-even, 197 stopped) and VAL 411 (308 / 103); without it, IS 842
(746 back to break-even, 96 still losing at 5 days) and VAL 413 (369 / 44). The median hold of a held leg is 7-8
hours.

Holding lifts the win rate, but the rescued legs close at about break-even while the unrescued ones lose more, so
mean R does not rise and t_day falls. Holding also costs legs (20-24 % fewer): a long held past the fix blocks the
short leg after it, and after the fix the yen tends to move against that long, which is why C3 has a short leg.
Without a stop, the worst leg loses 7.7 R (about 23 % of the account at 3 %) and one gotobi day's floating loss can
reach 23.5 R. The drawdowns in this table count realized P&L only, so they understate the floating loss of held legs.
Removing the stop but keeping the schedule changes mean R little and widens the tails (worst day MAE -9.3 R vs
-5.2 R).
