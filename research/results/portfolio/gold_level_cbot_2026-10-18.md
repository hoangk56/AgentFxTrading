# GoldLevelBot: the gold $50-level rule as a cBot, checked against its registered holdout

2026-10-18 (UTC). On 2026-10-18 the user approved running the gold rule on the demo account ("1,2,4 ok", decision 1
of the round 29 report). The rule is G1-XAU50, which passed its registered holdout at the DEMO tier:
[PREREG_G_gold_round50_cascade.md](round27_levels_opens/PREREG_G_gold_round50_cascade.md), HOLD n 228, net +2.87 bp
(t 1.43). This file shows that `cBot/GoldLevelBot.cs` trades that rule, and fixes the operating choices that are not
part of it.

## Answer
- **The built cBot reproduces the registered engine trade by trade.** It was backtested in cTrader on IC ticks over
  the whole holdout, 2025-01-02 .. 2026-09-24, as two runs (2025 and 2026) that each start with the bot's own two-day
  replay.
  - All 228 holdout triggers match `prereg_code/trades_HOLD.csv`: the same millisecond, arming time, level, side, stop
    price and s60. No trigger is extra or missing.
  - The bot's model net (the first tick 250 ms after the trigger and after the exit) equals the engine's `net_250` on
    every trade: mean +2.872 in both.
  - The backtester's own fills average +2.856 bp, against the engine's +2.838 at zero latency (the backtester fills
    at the trigger tick). Exits differ by up to 2.6 bp on single trades: the close goes out on the first tick or the
    one-second timer after the exit time.
  - Files: [compare_hold_final_output.txt](gold_level_cbot/compare_hold_final_output.txt); the backtests' trade
    log `gold_level_cbot/bt_hold_trades.csv` stays local (.gitignore keeps `*trades*.csv` out of git).
- **One operating fix came out of the first run.** The first build placed an order only when
  `Symbol.MarketHours.IsOpened()` was true. In the backtest that was false in the first hour after the summer reopen
  (22:02-23:00 UTC), although quotes and fills were there. It missed 7 of the 228 triggers
  ([compare_hold_build1_output.txt](gold_level_cbot/compare_hold_build1_output.txt)). Orders and closes now go by
  fresh quotes (a tick in the last 60 s) and the broker's answer. The bot logs the schedule cTrader reports
  (`Sun 22:02-Mon 20:59, ...` in that backtest).
- **Broker guard stop: $100** (`EmergencyStopUsd`; not part of the rule). Over the 686 IS, VAL and HOLD trades, the
  largest move against the entry before the 30-minute exit was $54 (1.1 % of the price, in HOLD); none reached $75
  ([guard_check_output.txt](gold_level_cbot/guard_check_output.txt)).
- **Demo size: 0.01 lot (1 oz), fixed.** The evidence is bp per trade and fill quality, not dollars. The demo account
  also runs E1 and held about $1,650 in September; at 0.1 lot one 2016-26 tail trade would have cost ~$540.

## How the bot follows the engine
The rule's numbers are the cBot's parameter defaults. `tests/cbot/gold_level/test_gold_level_bot.py` ties each default
to the registered code (`prereg_code/engine.py.txt`, `run_hold.py.txt`, `build_minutes_hold.py.txt`, `fills.py.txt`):

| piece | engine | cBot |
|---|---|---|
| grid, traded levels | $10 levels, trades only grid index % 5 == 0 | `LevelStep` 10, `TradedMultiple` 50 |
| band, freshness | mid within D = 0.2 S = $2; beyond the 24-hour max / min tick mid (`W_up`, plus this minute's earlier ticks) | `ArmBand` 2; ring of 1,442 minute records |
| order | buy stop L + 0.5 s60 / sell stop L - 0.5 s60, s60 = median last-tick spread of the 60 minutes before | `StopOffsetSpreads` 0.5; order price rounded outward to the tick |
| trigger, cancel | ask >= stop / bid <= stop; cancel when the mid leaves the band or `ok` is false, the cancelling tick first | same order in `Step` |
| busy, memory | 60 minutes after any $10 trigger; a level that triggered in 1,440 minutes blocks the scan until its band is left | `BusyMinutes` 60, `LevelMemoryMinutes` 1440, `ArmMode.Blocked` |
| sessions | 18:10 NY (d-1) .. 17:00 NY (d), weekdays d; arming to 15:54 NY | `SessionDay`, `ArmTo` |
| exclusions | +-15 min of a High USD minute; 15 min after the session's first tick or a gap > 60 min | `NearRelease`, `_gapAt` |
| exit | market, 30 minutes after the trigger | `HoldMinutes` 30 |

The server triggers the real orders (`StopTriggerMethod.Trade`: a buy stop on ask >= price). The bot also follows
every tick itself, so the $10 levels that carry no order trigger the same way.

**Restarts.** At start the bot loads about 49 hours of tick history (FreshWindow + LevelMemory + SpreadWindow + 10
minutes) and runs the rule over it without trading. It thus resumes with the rule's own state: the envelope, the busy
window, the levels that triggered and an armed level. In the backtests the history loaded in ~80 s (849 loads for 2.0
days) and the replayed state was the engine's: the 2025 and 2026 runs each start cold and still match every trigger.
A position open at start keeps the exit of its replayed trigger.

**What the bot does not do.** It never sends a market order to chase a trigger. A trigger whose stop order did not
fill within 5 s (`FillWaitSeconds`) is logged as missed. A real order is cancelled 2 s before an exclusion window or
the 15:54 close of arming (`CancelLeadSeconds`) and after an hour without ticks, so the broker cannot fill it where
the rule would not trade.

**Order traffic.** The level arms and disarms each time the mid crosses the edge of the $2 band, so one trade can
take several placements. In the May 2025 test week: 23 placements and cancels for 3 trades. That is the rule as
tested.

## The release calendar
- **The registered calendar rule is unchanged.** High-impact USD minutes come from the official schedules of
  PREREG_G's list, with the same event types and times.
- **Contents of the seed.** `cBot/seeds/usd_high_calendar.csv` holds 679 minutes:
  - the registered rows from 2025-01-01 (`prereg_code/usd_high_2024_2026.csv`, to 2026-09-30);
  - then the same types for 2026-10-01 .. 2027-12-31, built from the publishers' schedules
    ([usd_high_fwd.csv](gold_level_cbot/usd_high_fwd.csv), with
    [usd_high_fwd_detail.csv](gold_level_cbot/usd_high_fwd_detail.csv) giving each row's basis).
  - Tool: `research/tools/usd_high_calendar_seed.py`.
- **Check against the registered list.** September 2026, rebuilt with the forward code, matches it row for row: 25
  rows, 21 minutes ([calendar/sanity.txt](gold_level_cbot/calendar/sanity.txt)). The 15 releases of 2026-10-01 .. 10-17
  are confirmed from the releases themselves.
- **`valid_through=2026-12-11`.** The bot stops arming after that day until the seed is rebuilt.
  - Every major type is known well past that date: BLS, BEA, Census, DOL, FOMC, UMich and Treasury.
  - ISM, JOLTS and Empire State are known to 2026-12-31.
  - 2026-12-11 is the end of the continuing resolution that funds the statistical agencies (CRS R49353). A lapse
    from 2026-12-12 would move BLS, BEA, Census and DOL releases, as in October-November 2025.
- **Known gaps before that day, the only deviations from the registered rule** (a few 30-minute windows, well under
  1 % of the arming minutes):
  - S&P Global's calendar lists its flash US PMI only to 2026-11-11, so the November flash (about the 20th) is missing;
  - the Conference Board's dates are its stated rule (last Tuesday);
  - no Fed Chair appearance is listed after 2026-10-15. The Fed lists them about a week ahead.
- **Rebuilding.** Rerun `gold_level_cbot/calendar/build_fwd.py.txt`'s steps, or a fresh build from the same
  sources. Then rerun the seed tool and deploy; the bot rereads the file every hour.
  - The coverage of each type is in [calendar/coverage.txt](gold_level_cbot/calendar/coverage.txt), and its fetches in
    `calendar/fetch_log.tsv`. No request carried personal data.

## Evidence log and the demo rules
- Each traded trigger is written to `/root/ctrader_data/<BotId>_trades.csv`, one row per trigger:
  - the rule's numbers: trigger and arming time, level, side, stop, order price, s60;
  - the quote at the trigger;
  - the model's entry and exit (time, price, mid) and its net;
  - the real fill and close, and the net of those fills;
  - the entry slippage against the model, in $ and in s60;
  - a missed flag and its reason.
- `python -m research.tools.gold_demo_check <file>` applies the registered DEMO terms:
  - the stop rule: < 0 after 60 trades; below the expected sum minus 1.5 sd after 120, with VAL's mean +3.62 and sd
    22.9; median entry slippage worse than 1 x s60 from 30 trades;
  - the promotion rule: HOLD + demo pooled t >= 2.5 with >= 100 demo trades and net > 0 at spread x1.5.
  - With no demo trade yet the pooled t is the holdout's 1.43.

## Files
- [gold_level_cbot/](gold_level_cbot/): `bt_gold.py` (the VPS backtest runner: throwaway containers, bridge network, URLs
  disabled), `compare_bt.py`, `guard_check.py` and their outputs; the forward calendar and its build in `calendar/`.
- The registered rule and code: [round27_levels_opens/](round27_levels_opens/) (PREREG_G, the draft it builds on, and
  prereg_code/).
