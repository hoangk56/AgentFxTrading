# OrbRE2Bot review, 2026-11-06

Independent review of `cBot/OrbRE2Bot.cs` in `kienphan/AgentFxTrading` (upstream commit 94901a1, 2026-11-04). The bot
is not in this repo and does not run on our VPS. Verdict: **no tradable edge on 2016-2026 ticks; not a candidate.**

Code and raw output: [`orb_re2_review/`](orb_re2_review/) (`orb_re2_sim.py`, `orb_re2_report.py`, `orb_re2_checks.py`,
`report.txt`, `checks.txt`). Trades are not kept (62 MB); rerun with
`orb_re2_sim.py tick.json tick XAUUSD US30 USTEC` from that folder.

## The rule, as the code behaves

1. Range: high/low of the bid over the first 15 minutes of the session.
2. Live window: from `max(range end + 1 chart bar, range end + EntryDelayMinutes)` until 180 minutes after the open.
3. Fire on the first tick where the bid is beyond range +/- 0.5 pip, if the bid is on the same side of EMA10 of closed
   D1 bars, and the opposite side has not been seen beyond its boundary since the live window began.
4. Stop = max(0.5 x ATR14(D-1), 10 pips), target = 2R, measured from the fill. One trade a session, flatten at EOD.

## Method

- Tick replay of the rule on the IC cache, 2016-03 to 2026-09-24, with spread and commission from `research/specs.py`.
  DE40 and GBPJPY have no local ticks, so they use M1 pseudo ticks. On the three symbols with both, M1 reads
  0.023-0.035 R per trade below ticks with the same side on every common day, so M1 rows are slightly pessimistic.
- The deployed configuration is not in the repo (it lives in the author's DB). Sessions come from the commit messages
  and tests: XAUUSD 13:00 winter UTC + US DST, delay 30; USTEC 14:30, delay 30; US30 14:30, delay 0; DE40 08:00 Europe
  DST, delay 0, EOD 16:30 assumed; GBPJPY 00:00, EOD 09:00 assumed. Everything else is the code's default, M15 chart.
- The author's 23 sessions fall after our data ends, and the VPS cache has no later ticks for these symbols, so they
  could not be reproduced. This is therefore an out-of-sample test of that claim, but not a replication of it.
- Checks: brute-force tick scans match the simulator's exit, time and R on the traced trades; moving the assumed D1
  roll (22:00, 21:00, 00:00 UTC) changes avg R by at most 0.011.
- No pre-registration. 53 tick cells were read, so one |t| > 2 cell is expected by chance. Nothing here is a verdict
  on a new rule.

## Results (net of costs, in R per trade)

| symbol, data | n | win % | avg R | t | PF | total R | max DD R | 2025+ avg R (n) |
|---|---|---|---|---|---|---|---|---|
| XAUUSD, tick | 1806 | 45.2 | -0.045 | -2.31 | 0.87 | -81.3 | 86.6 | -0.018 (280) |
| US30, tick | 1748 | 47.3 | -0.008 | -0.40 | 0.98 | -13.8 | 37.7 | +0.006 (278) |
| USTEC, tick | 1833 | 50.0 | +0.010 | +0.52 | 1.03 | +18.2 | 29.7 | -0.008 (303) |
| DE40, M1 | 1685 | 47.2 | -0.013 | -0.56 | 0.97 | -21.4 | 43.4 | +0.016 (276) |
| GBPJPY, M1 | 467 | 48.6 | -0.014 | -0.38 | 0.96 | -6.6 | 17.6 | -0.072 (107) |

Exits: 71 % of XAUUSD trades end at EOD, 24 % at the stop, 4 % at the target, so "2R" rarely describes the payoff.

### The filters

| symbol, tick | base avg R (n) | no trend filter | no whipsaw guard | neither |
|---|---|---|---|---|
| XAUUSD | -0.045 (1806) | -0.047 (2725) | -0.028 (2367) | -0.047 (2728) |
| US30 | -0.008 (1748) | +0.001 (2690) | -0.008 (2096) | +0.001 (2690) |
| USTEC | +0.010 (1833) | -0.002 (2685) | +0.011 (2084) | -0.002 (2685) |

The filters remove about a third of the trades without changing the per-trade result beyond noise. Drawdown falls
because exposure falls (XAUUSD 137 R to 87 R), not because the remaining trades are better. Entering at the same
minute with no range at all gives XAUUSD -0.036, US30 -0.006, USTEC +0.016 (always with the D1 trend, delay 30), so
the break adds nothing visible beyond the drift.

### The entry delay

| symbol, tick | delay 0 (real wait 15 min on M15) | 30 | 45 | 60 | 90 | true 0 (M1 chart) |
|---|---|---|---|---|---|---|
| XAUUSD | -0.031 | -0.045 | -0.042 | -0.027 | -0.021 | -0.041 |
| US30 | -0.008 | -0.024 | -0.045 | -0.041 | -0.019 | -0.023 |
| USTEC | +0.043 | +0.010 | +0.010 | +0.008 | +0.019 | +0.041 |

The commit reports XAUUSD -136.65 at delay 0 and +1607.30 at delay 30. Over ten years the two are the same within
noise. For USTEC the commit picked 30 over 0 (-7.28 vs -59.83); over ten years 0 is the better of the two.

### What 23 sessions can show

A 23-session window holds a median of 15 trades. Under the XAUUSD base rule, whose long-run mean is negative:

| 23-session total at or above | +2 R | +3 R | +4 R | +5 R | +6 R | +8 R |
|---|---|---|---|---|---|---|
| share of windows | 20.6 % | 12.0 % | 6.3 % | 3.5 % | 1.6 % | 0.1 % |

PF >= 3.73 (the commit's XAUUSD figure) occurs in 1.7 % of XAUUSD windows, 4.1 % of US30, 2.6 % of USTEC. The commit's
PF and net imply gross wins of about $2,196 and gross losses of about $589. With the code's default stop, the stop in
the last 20 XAUUSD trades of our data averages $512 per 0.1 lot, so +$1,607 is about +3 R. A $328 drawdown is smaller
than one such stop, so the author probably used a different stop; at $300 per R it would be about +5 R. Either value
is ordinary luck for a rule with no edge, more so after choosing across symbols and delays.

### What 2 sessions can show

From the base trades of the tick run (rolling 2-session totals, weekdays with no trade count as 0):

| 2-session total at or above | +1 R | +2 R | +3 R |
|---|---|---|---|
| XAUUSD alone | 12.1 % | 2.0 % | |
| US30 alone | 13.2 % | 4.0 % | |
| USTEC alone | 12.9 % | 3.5 % | |
| the three summed | 26.0 % | 12.0 % | 4.9 % |

After a 2-session total >= +2 R on the three summed (n 328, overlapping), the next 10 sessions average -0.49 R, 44.5 %
of them positive, against -0.30 R and 45.9 % unconditionally: a good run does not carry over. With a per-trade sd of
about 0.83 R, telling +0.1 R from zero at t 2.5 takes about 430 trades.

### The one cell with |t| > 2

USTEC at delay 0: +0.043 R, t +2.16, n 1813, flip -0.061. By period: 2016-20 +0.026, 2021-24 +0.074, 2025-26 +0.012
(n 294, t 0.26). Below the journal's 2.5 bar, chosen after the fact from 53 cells, and flat in the recent period. It
agrees with a public replication that found a small first-candle edge on NQ that costs absorb. Not a candidate.

## Code defects (upstream line numbers)

Measured effect where available; none of them changes the verdict above.

| # | severity | line | defect |
|---|---|---|---|
| 1 | high | 265-266, 277-278 | `_tradesFired`, `_blockedAfterStop` and the whipsaw memory live only in memory. After a restart (watchdog, rebuild) in the same session, with the earlier trade closed, the bot can trade again. Commit 959a81d documents a position closing during such a rebuild |
| 2 | high | 938-950 | `FixedLots > 0` (the default) returns before the `MaxDollarRiskPerTrade` check, so the "hard guardrail" of the header is off. XAUUSD: $512 stop vs $100 limit |
| 3 | medium | 785-789 vs 803 | The break is recorded after the delay, window and position returns, although the comment says "before any gate". The guard is blind until the live window opens. If it saw those minutes, entries would drop 43 % on XAUUSD, 22 % USTEC, 12 % US30 |
| 4 | medium | 136 vs 524 | `EntryDelayMinutes = 0` is documented as the first qualifying tick, but the range is final only after the next bar closes: 15 minutes on M15. Results depend on the chart timeframe |
| 5 | medium | 795, header line 8 | Called a stop order, but it fires on any tick beyond the level, at any distance, with no equivalent of OrbBot's `MaxBreakoutDistancePips`. XAUUSD: 71 % of entries come in the first minute of the live window, overshoot median 0.12 R, p90 0.69 R. Capping it did not improve the result |
| 6 | medium | 870, 889, 916 | A rejected order, wide spread or refused size is retried and logged on every tick, with no backoff, and the signal stays armed, so it may fill much later |
| 7 | low | 1279 | Reconcile builds `openIds` from `BotId` only, so a partially closed adopted position would be reported closed |
| 8 | low | 999 | `EnableTrading = false` also skips the EOD flatten and stop management of open positions |
| 9 | low | 535 | A restart inside a multi-bar range leaves `_orHadWindow` true, so the backfill is skipped and the range is short. Not reachable with 15 minutes on M15 |
| 10 | low | 1003-1009 | No tick after EOD on a Friday early close: the session rolls first, so the position is held until Monday's EOD |
| 11 | low | 930, 603, 326 | "% Equity" uses balance; "Wilder-style" ATR is a simple mean; the start log prints the fast length twice |

`tests/test_orb_re2_bot.py` only asserts substrings of the source, so it cannot catch defects of behaviour.

## Sources

- cTrader `OnBarClosed` reference: https://help.ctrader.com/ctrader-algo/references/General/Robot/OnBarClosed/ (its
  sample reads the closed bar with `Bars.Last(1)`; the author's live log shows one bar of lag, so this should be
  logged on the real platform rather than assumed).
- Replication on index CFDs, 2015-2026 (blog of a product seller, treat as a lead):
  https://www.mql5.com/en/blogs/post/776235
