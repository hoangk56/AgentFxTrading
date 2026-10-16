# EcbWindowBot: the F3 / E1 rules as a cBot, checked against the registered code (2026-10-16)

The user asked on 2026-10-16 for F3 live at a small lot and E1 on demo. `cBot/EcbWindowBot.cs` implements both
(`UsdTopOnly` true = F3, false = E1). This file records how its conventions were pinned to the registered rules and what
the one part outside the rules (a broker guard stop) costs. No era here is new: IS, VAL and HOLD were all opened before
(round 13, round 24), so nothing below is evidence for the rules, only for the cBot matching them.

Scripts and outputs in [ecb_window_cbot/](ecb_window_cbot/) (scratch scripts, run from the repo root with the research
venv; `f3_check.py` reads `research/data/m1`).

## 1. The registered rule, rebuilt

`f3_check.py` rebuilds F3 and E1 from the IC M1 cache: F3 IS n 381 net +2.38 bp (t 3.27), VAL n 207 +3.00 (t 2.59),
HOLD n 117 +1.99 (t 2.15); E1 IS +1.16, VAL +1.34, HOLD +0.63 (registered: F3 +2.39 / +3.01 / +2.00, E1 +1.17 / +1.35 /
+0.64; the last-digit gaps come from this script's 10-bar quote window, one bar shorter than the registered `clib`).

- **F3 never trades a Monday.** Its score needs a quote at 18:00 New York on the previous weekday, and Friday 18:00
  New York is after IC's close, so every Monday score is unknown (705 F3 days 2016-2026: Mon 0, Tue 195, Wed 175,
  Thu 155, Fri 180). The cBot keeps this: no quote in the window = no score.
- **The quote at a minute** is the M1 bar ending at it or up to 10 bars before it (`clib.quote_k`, `back=10`): a tick
  less than 11 minutes old. The cBot (`QuoteMaxAgeMinutes` = 10, `QuoteWindowStart`) and the seed tool
  (`research/tools/ecb_usd_top_seed.py`) use exactly that.

## 2. Bid bars would change the F3 days

cTrader gives a cBot bid-only bars. Scoring on bid closes instead of mids changes the selected set on 46 of 714 F3 days
2016-2026 (`f3_diag_lib.py`): the window (10 vs 15 minutes) changes 1 day, the price (bid vs mid) the other 45, spread
over Tuesday-Friday (the 18:00 New York spread is wide after the 17:00 rollover). On bid M15 closes F3 would read
HOLD n 122 +1.80 (t 1.97) instead of n 117 +1.99.

So the cBot does not score on bars. It records the live USDJPY/USDCHF bid and ask at 18:00 New York and 07:00 London
(the last tick in the window above) in a quote log on the cTrader home volume, reads its history from that log and from
`cBot/seeds/ecb_usd_top_seed.csv`, and uses an M15 bid close only for a minute neither holds, logging the source of
every decision. The seed holds the research's quotes for 2025-01-01..2026-10-15: the IC M1 cache to 2026-09-24,
Dukascopy M1 after (no Dukascopy file for 2026-10-16 yet when fetched).

**Port check** (`seed_port_check.py`): `Decide()` written in Python on the seed selects exactly the registered F3 days
of 2026-01-01..2026-09-24: 48 of 191 weekdays, 0 differences.

## 3. cTrader backtests of the built cBot

Built on the VPS in a temporary home (`ctrader-console build`, 0 errors, no new warning), then backtested on IC ticks
with the seed mounted and the server URLs disabled (demo login, 1 GB / 2 CPU like the Backtest page):

- **F3, 2026-06-01..2026-09-24, 0.01 lot**: 19 trades on exactly the 19 registered F3 days of that span
  (`bt_jun_sep.txt` vs `expected_f3_jun_sep.txt`), every one a sell filled at 11:00:00 London and closed at 13:00:00
  London, none left open. In a backtest the bot also captures the selector quotes from the tick stream, so this checks
  the live-capture path as well as the seed.
- **E1, 2026-09-01..2026-09-24, 0.1 lot**: 18 trades, every weekday including Mondays, 11:00:00 -> 13:00:00 London.

## 4. The broker guard stop (not part of the rule)

The rule has no stop: it exits at 13:00 London. A bot or VPS that dies with a position open would hold it, so the
broker gets a far stop. `stop_check.py` replays each trade's M1 path (bid high + spread against the sell):

| stop | F3 IS / VAL / HOLD net bp | E1 IS / VAL / HOLD net bp | E1 trades touched 2016-2026 |
|---|---|---|---|
| none (the rule) | +2.38 / +3.00 / +1.99 | +1.16 / +1.34 / +0.63 | - |
| 60 pips | +2.39 / +2.78 / +1.99 | +1.05 / +1.27 / +0.82 | 0.69 % (19) |
| 80 pips | +2.38 / +2.92 / +1.99 | +1.09 / +1.27 / +0.66 | 0.33 % (9) |
| 100 pips | +2.38 / +3.00 / +1.99 | +1.15 / +1.34 / +0.60 | 0.11 % (3) |

Chosen: **100 pips** (`EmergencyStopPips`, preset `ECB_BROKER_STOP_PIPS`): no F3 number moves, E1 moves by <= 0.03 bp.
Largest adverse excursion of an E1 trade 2016-2026: 133 pips.

## Other choices outside the rule
- **Entry grace 60 s.** The rule sells at the 11:00 quote; E1's HOLD net fell to 0.00 with both fills one minute late
  (PREREG_M), so a day whose order cannot go out within 60 s is skipped, not chased.
- **Lots.** F3 live 0.01 (the minimum: a measurement of fills, since F3 has not met its promotion rule), E1 demo 0.1.
  Fixed, never read off the account.
- **Max hold 180 min** after the entry, as a last guard after a restart; the window itself closes at 120 min.
