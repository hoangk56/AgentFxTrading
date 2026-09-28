# C1 Crypto Donchian: how many positions per bot? (2026-09-28)

`cBot/CryptoDonchianBot.cs` (C1) takes every H4 bar that closes beyond the 55-bar channel, so a breakout that keeps
going stacks up to `MaxPositions` = 3 positions in the same direction (VPS backtest #378, BTCUSD 2026-07-30 ..
2026-09-27, held three longs at once twice). This study asks whether another cap would be better: 1 or 2 (less
stacking), or more than 3 (the bot's parameter stops at 3 today). It does not re-test C1: C1 failed its holdout
(`prereg_swing_v2.md`) and stays a forward test whatever this finds.

## Plan (written before any cap other than 3 was run)

Code: `research/swing/cap_test.py`. C1 exactly as registered (`swing_rules.donchian`, n 55, exit 20, shorts,
3 x ATR20 stop, UTC H4 bars, one bot per symbol on BTCUSD and ETHUSD, $100 x strength scale, 5-day limit, same
costs); only the per-bot cap changes: 1, 2, 3 (registered, the bot today), 4, 5 and none. A signal that finds the
bot full is dropped, as in the bot.

Eras: IS 2018-2021 and VAL 2022-2024 decide. HOLD 2025-01 .. 2026-09 was already seen at cap 3, and the other caps
share most of its trades, so HOLD is reported, not judged.

Measures, pooled over the two bots and per era:

- n, mean R, and t clustered by *episode* (a chain of overlapping positions in one bot), since stacked positions
  ride the same price path and are not independent trades.
- net $ and max drawdown. The drawdown is taken on a mark-to-market equity curve (open positions valued at every
  H4 close, bid for longs and ask for shorts), because three stacked positions lose together before any of them
  closes. The realized-only drawdown of earlier reports is shown next to it.
- **return / DD** = net $ / mark-to-market max DD. It does not depend on the $ risk per trade, so it compares caps
  at the same drawdown budget (a cap-1 bot can take a larger risk per trade for the same drawdown). This is the
  main measure.
- worst episode (summed $ of one chain of stacked positions) and peak $ at risk (sum of the open positions' risk).
- By stack rank: every trade is labelled with the number of the bot's positions open at its entry + 1; mean R
  and clustered t per rank (1, 2, 3 in the cap-3 run; 4 and 5+ in the uncapped run). This shows what the
  second and third units add.
- Bar phase: return / DD on IS+VAL for each cap with the H4 edges shifted by 0, 1, 2, 3 h (the phase moved C1's
  HOLD R by up to 0.14, `crypto_donchian_cbot_2026-09-27.md`), as the noise yardstick.

Verdict rule, fixed now:

- The candidate is the cap with the best IS return / DD. It **replaces 3** only if all of:
  1. its return / DD is at least 1.10 x cap 3's in IS and in VAL;
  2. it beats cap 3's return / DD on IS+VAL at >= 3 of the 4 bar phases;
  3. for a cap below 3: the rank-2 and rank-3 units of the cap-3 run have a lower mean R than the rank-1 units in
     both IS and VAL; for a cap above 3: the rank >= 4 units of the uncapped run have mean R > 0 in IS and in VAL
     and clustered t >= 2.0 on IS+VAL.
- Otherwise the cap **stays at 3**.
- Any change is a setting for the forward test, not a new candidate: it cannot rescue C1's failed holdout. A cap
  above 3 would also need the bot's `MaxValue = 3` raised.

## Results (run once, 2026-09-28, `python -m research.swing.cap_test`)

**Verdict: keep 3.** Cap 1 had the best IS return / DD and cleared the 1.10 x margin in IS and VAL, but failed the
other two conditions: it beats cap 3 at only 2 of the 4 bar phases, and in VAL the stacked units earned more than the
first ones (rank 2-3 mean R +0.237 vs rank 1 +0.214). Caps above 3 are worse than 3 on IS return / DD and at 3 or 4
of the 4 phases.

Cap 3 reproduces the registered run exactly (IS n 553 R +0.276, VAL n 413 R +0.227, HOLD n 302 R -0.025, $+40,311).

### 1. Caps, both bots pooled (registered bar phase)

| cap | era | n | episodes | mean R | t (episodes) | sum R | net $ | max DD $ (MTM) | max DD $ (realized) | return / DD | worst episode $ | peak $ at risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IS | 249 | 249 | +0.301 | +3.1 | +74.9 | +12,670 | 1,509 | 1,033 | 8.40 | -376 | 400 |
| 1 | VAL | 203 | 203 | +0.193 | +1.9 | +39.2 | +6,785 | 1,407 | 1,266 | 4.82 | -213 | 400 |
| 1 | HOLD | 141 | 141 | -0.000 | -0.0 | -0.0 | +2,111 | 2,960 | 2,738 | 0.71 | -204 | 400 |
| 2 | IS | 422 | 227 | +0.295 | +3.2 | +124.3 | +19,577 | 2,760 | 1,357 | 7.09 | -438 | 800 |
| 2 | VAL | 328 | 185 | +0.225 | +2.1 | +73.9 | +10,882 | 2,610 | 2,152 | 4.17 | -413 | 790 |
| 2 | HOLD | 238 | 130 | +0.008 | +0.1 | +1.8 | +3,896 | 3,487 | 3,249 | 1.12 | -339 | 800 |
| **3** | IS | 553 | 217 | +0.276 | +2.9 | +152.5 | +23,269 | 3,365 | 2,002 | 6.92 | -537 | 1,175 |
| **3** | VAL | 413 | 181 | +0.227 | +2.1 | +93.9 | +14,183 | 3,526 | 2,885 | 4.02 | -630 | 1,040 |
| **3** | HOLD | 302 | 127 | -0.025 | -0.2 | -7.5 | +2,859 | 3,964 | 3,578 | 0.72 | -547 | 1,060 |
| 4 | IS | 639 | 212 | +0.270 | +2.8 | +172.8 | +26,969 | 4,721 | 2,241 | 5.71 | -537 | 1,375 |
| 4 | VAL | 470 | 178 | +0.235 | +2.0 | +110.6 | +15,537 | 3,864 | 3,223 | 4.02 | -776 | 1,299 |
| 4 | HOLD | 338 | 126 | -0.032 | -0.3 | -10.9 | +3,355 | 4,166 | 3,588 | 0.81 | -547 | 1,359 |
| 5 | IS | 694 | 209 | +0.268 | +2.9 | +185.7 | +28,314 | 5,158 | 2,551 | 5.49 | -537 | 1,762 |
| 5 | VAL | 509 | 176 | +0.244 | +2.0 | +124.4 | +18,296 | 3,864 | 3,223 | 4.73 | -776 | 1,556 |
| 5 | HOLD | 359 | 126 | -0.036 | -0.3 | -12.9 | +3,512 | 4,366 | 3,788 | 0.80 | -588 | 1,467 |
| none | IS | 765 | 206 | +0.224 | +2.6 | +171.5 | +25,785 | 5,358 | 2,751 | 4.81 | -622 | 2,075 |
| none | VAL | 552 | 173 | +0.269 | +2.0 | +148.7 | +21,207 | 3,864 | 3,223 | 5.49 | -776 | 2,065 |
| none | HOLD | 382 | 125 | -0.044 | -0.4 | -16.7 | +3,764 | 4,971 | 3,929 | 0.76 | -588 | 2,092 |

Clustered by episode, C1's t is lower than the plain t of earlier reports (cap 3: IS 2.9 vs 4.3, VAL 2.1 vs 3.3),
because two or three stacked positions are one bet on one price path.

### 2. Per symbol: mean R / return per DD

| cap | BTCUSD IS | BTCUSD VAL | BTCUSD HOLD | ETHUSD IS | ETHUSD VAL | ETHUSD HOLD |
|---|---|---|---|---|---|---|
| 1 | +0.414 / 7.18 | +0.252 / 3.32 | -0.086 / 0.68 | +0.185 / 4.05 | +0.139 / 3.02 | +0.091 / 0.66 |
| 2 | +0.446 / 10.43 | +0.298 / 4.40 | -0.104 / 0.82 | +0.150 / 3.56 | +0.157 / 2.21 | +0.137 / 1.14 |
| 3 | +0.452 / 9.06 | +0.289 / 4.70 | -0.151 / 0.13 | +0.113 / 2.89 | +0.168 / 2.24 | +0.123 / 1.29 |
| 4 | +0.461 / 8.68 | +0.307 / 4.61 | -0.168 / -0.09 | +0.099 / 2.24 | +0.167 / 2.27 | +0.132 / 1.72 |
| 5 | +0.458 / 8.56 | +0.344 / 6.17 | -0.193 / -0.27 | +0.097 / 2.12 | +0.151 / 2.22 | +0.157 / 2.04 |
| none | +0.404 / 7.47 | +0.408 / 7.71 | -0.201 / -0.34 | +0.062 / 1.50 | +0.137 / 2.13 | +0.142 / 1.93 |

The two symbols pull in opposite directions. BTCUSD's ratio peaks at cap 2 in IS and rises with the cap in VAL;
ETHUSD's is best at cap 1 in IS and VAL (IS falls from 4.05 at cap 1 to 1.50 uncapped). A cap per symbol would be
picked after the fact, and HOLD (seen) turns it round: there ETHUSD does better with more units (0.66 at cap 1,
1.29 at 3) and BTCUSD with fewer.

### 3. Mean R by stack rank (n / mean R / t by episode)

Cap 3 run:

| rank | IS | VAL | HOLD | IS+VAL |
|---|---|---|---|---|
| 1 | 217 / +0.321 / +3.1 | 181 / +0.214 / +2.0 | 127 / +0.041 / +0.3 | 398 / +0.273 / +3.6 |
| 2 | 181 / +0.321 / +2.8 | 132 / +0.197 / +1.6 | 101 / +0.033 / +0.2 | 313 / +0.269 / +3.2 |
| 3 | 155 / +0.159 / +1.5 | 100 / +0.291 / +1.7 | 74 / -0.217 / -1.6 | 255 / +0.211 / +2.3 |

Uncapped run:

| rank | IS | VAL | HOLD | IS+VAL |
|---|---|---|---|---|
| 1 | 206 / +0.277 / +2.6 | 173 / +0.225 / +2.0 | 125 / +0.048 / +0.4 | 379 / +0.253 / +3.3 |
| 2 | 172 / +0.396 / +3.4 | 127 / +0.193 / +1.6 | 98 / +0.051 / +0.3 | 299 / +0.310 / +3.6 |
| 3 | 139 / +0.273 / +2.2 | 84 / +0.210 / +1.3 | 69 / -0.178 / -1.2 | 223 / +0.249 / +2.5 |
| 4 | 92 / +0.246 / +1.5 | 64 / +0.327 / +1.6 | 39 / -0.128 / -0.7 | 156 / +0.279 / +2.2 |
| 5+ | 156 / -0.090 / -0.7 | 104 / +0.449 / +1.6 | 51 / -0.205 / -1.0 | 260 / +0.125 / +0.9 |

In IS/VAL a second or third unit earns about what the first does (+0.27 / +0.27 / +0.21 R), so stacking does not add
worse trades; what it adds is concentration, since those units win and lose together with the first. In HOLD (seen,
not judged) the third units lost (-0.217, t -1.6) while ranks 1-2 were about flat, but in IS the third units were also
the weakest and in VAL the strongest, so this is not a rule.

### 4. Return / DD on IS+VAL by bar phase

| cap | 0 h (registered) | 1 h | 2 h | 3 h |
|---|---|---|---|---|
| 1 | 12.89 | 10.53 | 5.55 | 7.18 |
| 2 | 11.03 | 9.76 | 7.32 | 8.89 |
| 3 | 10.62 | 9.35 | 7.69 | 7.60 |
| 4 | 9.00 | 9.42 | 6.55 | 6.07 |
| 5 | 9.04 | 8.80 | 6.77 | 5.95 |
| none | 8.77 | 8.66 | 6.13 | 5.68 |

Cap 1's lead at 0 h and 1 h turns into a loss at 2 h and 3 h: the ranking of caps 1-3 is within the phase noise.
Caps 4, 5 and none are below cap 3 at 3 or 4 of the 4 phases.

### Verdict checks

- candidate (best IS return / DD besides 3): cap 1
- 1. return / DD >= 1.10 x cap 3 in IS and VAL: **yes** (IS 8.40 vs 6.92, VAL 4.82 vs 4.02)
- 2. beats cap 3 on IS+VAL at >= 3 of 4 phases: **no** (2/4)
- 3. rank 2-3 mean R < rank 1 in IS and VAL: **no** (IS +0.246 vs +0.321, VAL +0.237 vs +0.214)
- **keep 3**

## What this means

- MaxPositions is a risk dial, not an edge dial. Going from 3 to 1 roughly halves the net $ and the mark-to-market
  drawdown, shrinks the worst episode (IS -537 -> -376, VAL -630 -> -213) and cuts the peak $ at risk by two thirds
  (1,175 -> 400 for both bots); the ratio of return to drawdown stays within the phase noise. Above 3 the extra units
  add $, but in IS the drawdown grows faster, and every cap above 3 has a lower ratio than 3 at 3 or 4 of the phases.
- If the forward test should carry less risk, a lower `MaxPositions` does it without touching the lot size. Cutting
  `RiskPerTradeMoney` instead runs into BTCUSD's 0.01 minimum lot (~$30-40 at the stop), which starts skipping weak
  breakouts (`crypto_donchian_cbot_2026-09-27.md`). Neither choice changes C1's status: its holdout failed at every
  cap (HOLD mean R -0.044 .. +0.008).
- VPS backtest #378 as an illustration (9 BTCUSD trades, +$1,536 at cap 3). The signals do not depend on the cap, so
  cap 1 would have kept the trades opened with nothing else open: 5 trades, +$1,021, one position at a time. Cap 2
  would have kept 7, +$1,545. Two months and nine trades say nothing about which cap is better.
- Nothing changes in `cBot/CryptoDonchianBot.cs` or the presets.
