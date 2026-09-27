# C1 Crypto Donchian — does its edge depend on the weekend closure? (2026-09-27)

C1 (`prereg_swing_v2.md`) was chosen on IS 2018-2021 and VAL 2022-2024 and failed its HOLD 2025-2026 (mean R
-0.025). The M1 cache shows that IC's BTCUSD/ETHUSD were closed every weekend until April 2024 (Friday 17:00 to
Sunday 17:05 New York time; weekend share of M1 bars ~2 % in 2018-2023) and have traded 24/7 since (22-29 %; only a
~1 h Friday and a ~3 h Saturday-night pause). So nearly all of IS/VAL was a 5-day market and all of HOLD a 24/7 one.
This is a diagnostic of that one difference. It does not re-test C1: C1 stays failed whatever this finds, and
nothing here is tuned.

## Plan (written before any of the tests below was run)

Code: `research/swing/weekend_test.py`; C1 exactly as registered (`swing_rules.donchian`, n 55, exit 20, shorts,
3 x ATR20 stop, H4 UTC bars, cap 3 per bot, one bot per symbol, $100 x strength scale, 5-day limit, same costs).

- **T1 (main).** 24/7 era = signal bars from 2024-05-01 to the end of the cache (2026-09-24). Run C1 on (a) the real
  M1 data and (b) the same data with every minute from Friday 17:00 to Sunday 17:05 New York time removed (the old
  closure, DST-aware). (b) sees the weekend move as a gap at the Sunday open, as the old market did.
- **T1 phases.** The same (a)/(b) comparison with the H4 bar edges shifted by 1, 2, 3 h, since the HOLD result
  already moved by up to 0.14 R with the bar phase (`crypto_donchian_cbot_2026-09-27.md`). That spread is the
  noise yardstick.
- **T2.** Closed-weekend era (signal bars 2018-01 .. 2024-03), real data: trades whose signal bar is the first H4
  bar after the weekend reopen (it contains the weekend gap) against all other trades.
- **T3.** 24/7 era, real data: trades whose signal bar closes on a Saturday or Sunday (UTC) against weekday ones.

Verdict rule, fixed now:

- **Supported** (the 24/7 switch plausibly explains the weak HOLD) if all of: T1 (b) - (a) >= +0.10 R pooled at the
  registered phase; (b) - (a) > 0 for both BTCUSD and ETHUSD; (b) - (a) > 0 at >= 3 of the 4 phases; (b) mean R > 0.
- **Not supported** if (b) - (a) < +0.10 R pooled at the registered phase, or it is <= 0 at 2 or more phases.
- Anything else: **inconclusive**.
- T2/T3 are supporting detail, not part of the verdict: T2 points the same way if the post-reopen trades' mean R is
  >= 0.20 above the rest with n >= 30; T3 if the weekend-signal trades' mean R is below the weekday ones'.

Limits known in advance: the 24/7 era is ~2.4 years and ~350-400 trades, so a 0.10 R difference is near the noise
level; even "supported" makes a weekday-only variant a hypothesis for a forward test, not a rule to adopt.

## Results (run once, 2026-09-27, `python -m research.swing.weekend_test`)

**Verdict: not supported.** Cutting the old weekend closure out of the 24/7 era changes C1's pooled mean R by
+0.011 at the registered phase (rule: >= +0.10), and by +0.000 to +0.011 at the other phases. The 24/7 switch does
not explain the weak HOLD, so a weekday-only variant of the bot would not bring back the IS/VAL edge.

### T1: 24/7 era (signal bars 2024-05-01 .. 2026-09-24)

This window includes 2024-05..12 from VAL, so its R is not HOLD's -0.025.

| phase | variant | n | mean R | t | net $ |
|---|---|---|---|---|---|
| 0 h (registered) | (a) real | 415 | +0.042 | +0.6 | +4,421 |
| 0 h (registered) | (b) weekends cut | 336 | +0.053 | +0.8 | +3,482 |
| 1 h | (a) real | 414 | +0.151 | +2.0 | +11,697 |
| 1 h | (b) weekends cut | 344 | +0.156 | +2.0 | +9,338 |
| 2 h | (a) real | 396 | +0.107 | +1.4 | +6,620 |
| 2 h | (b) weekends cut | 307 | +0.116 | +1.5 | +4,250 |
| 3 h | (a) real | 410 | +0.092 | +1.3 | +3,018 |
| 3 h | (b) weekends cut | 326 | +0.092 | +1.3 | +1,986 |

(b) - (a), mean R:

| phase | pooled | BTCUSD | ETHUSD |
|---|---|---|---|
| 0 h | +0.011 | +0.072 | -0.058 |
| 1 h | +0.005 | +0.051 | -0.049 |
| 2 h | +0.009 | +0.035 | -0.020 |
| 3 h | +0.000 | +0.092 | -0.102 |

Per symbol at 0 h: BTCUSD (a) n 221 R -0.070, (b) n 179 R +0.002; ETHUSD (a) n 194 R +0.169, (b) n 157 R +0.111.
The two symbols move in opposite directions at every phase (BTCUSD a little better without weekends, ETHUSD worse),
so the pooled effect is nil. The phase moves pooled R by up to 0.11 in both variants, ten times the weekend effect.

### T2: closed-weekend era (signal bars 2018-01 .. 2024-03), registered phase

| signal bar | n | mean R | t | net $ |
|---|---|---|---|---|
| holds the weekend gap | 105 | +0.505 | +3.3 | +10,469 |
| other | 735 | +0.244 | +4.5 | +26,381 |

The bars that held the weekend gap did better (+0.26 R, n 105: this points the way the hypothesis predicts), but
the other 735 trades carried most of the edge on their own (R +0.244, t 4.5). So the gap bars added to IS/VAL; they
were not its source.

### T3: 24/7 era, registered phase

| signal bar closes | n | mean R | t | net $ |
|---|---|---|---|---|
| Saturday/Sunday UTC | 53 | -0.233 | -1.4 | -1,329 |
| Monday-Friday UTC | 362 | +0.082 | +1.1 | +5,751 |

Weekend-signal trades lost (points the same way, n 53, t -1.4). Without them the 24/7 era is still only R +0.082,
far below IS +0.276 / VAL +0.227. T3 is found after the fact on the same data: it is not a filter to adopt without
its own forward test.

## What this means

- The weaker 2024-2026 results are not a weekend-structure artefact. Whatever faded, it faded on weekdays too: on
  this data the 2018-2023 trend edge is simply smaller in 2024-2026, and the number is noisy (the bar phase alone
  moves it by 0.11 R). What made it smaller is not tested here.
- Nothing changes for the demo bots: C1 stays a failed candidate run as a forward test. A "skip weekend signals"
  rule would rest on 53 trades found after the fact; not proposed.
