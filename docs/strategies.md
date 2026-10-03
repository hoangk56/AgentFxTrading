# Strategies

What the cBot does, in outline. The code is the specification: the rules live in `cBot/<Name>.cs` and the values per
symbol in [`app/cbot_presets.py`](../app/cbot_presets.py) (written out in [docker-instances.md](docker-instances.md)).
Defaults quoted below are the cBot's own parameter defaults.

> **Evidence.** None of these descriptions is a claim that the strategy makes money. The offline research
> ([research/README.md](../research/README.md), dated conclusions in [research/JOURNAL.md](../research/JOURNAL.md))
> found that Gotobi passed its pre-registered holdout.

The bot is rule-based: it never asks the server for a decision. It reports positions and telemetry to the server and
polls it for dashboard commands.

| cBot | Symbols in the presets | Timeframe |
| :--- | :--- | :--- |
| `GotobiBot` | USDJPY, EURJPY, GBPJPY | M15 chart, fixed UTC schedule |

## Gotobi Fix (`cBot/GotobiBot.cs`)

Research candidate C3. On gotobi days (the 5th, 10th, 15th, 20th, 25th and the last day of the month; weekend dates
move to the Friday before) Japanese importers buy USD at the 09:55 Tokyo fixing. The bot buys at 03:00 Tokyo
(18:00 UTC the evening before) and closes at the fix (00:55 UTC), then sells at the fix and closes at 11:55 Tokyo
(02:55 UTC). One position at a time per instance. Each trade risks `RiskPerTradeMoney` dollars at a stop of
3 × ATR20 (H1). Result file: `research/results/portfolio/swing_lab_v2_2026-09-27.md`.

**Plain orders.** An order carries no label and no comment, like one placed by hand. The bot treats every position on
its symbol as its own (one bot per symbol and account, nothing traded there by hand) and reads the leg back off the
position: a buy entered in the evening long window is the long of the next day, a sell entered at the fix the short of
that day, and one on a day that is not a trading day a decoy. After a restart the virtual stop is rebuilt from the
H1 ATR at the entry, so the bot keeps no state.

**Camouflage.** So the broker cannot read the strategy off its orders, the bot sends a random 0.8-1.0 × fraction of
the stop to the broker (a dead bot loses at most 1 R), opens each long at its own time within ±60 min of 18:00 UTC, and trades about two decoy
legs per real one on plain weekdays: same hours, 0.01 lot, a 0.5 × ATR stop the bot closes itself. The broker sees
a ~39 % win rate instead of ~56 %. On 2024-01..2026-09 at $200 risk this cost 10 % of the net; decoys at the real lot
would have cost 83 % (`research/results/portfolio/gotobi_camouflage_2026-09-30.md`). With `--VirtualStop=false` the
bot trades the plain strategy with the real stop at the broker; set `--DecoyLegProbability=0` and `--LongEntryJitterMinutes=0` to
backtest the plain strategy.

## Removed bots

Crypto Donchian (`CryptoDonchianBot`, research C1: an H4 Donchian breakout on BTCUSD and ETHUSD) failed its
2025-2026 holdout, ran as a forward test and was removed on 2026-10-03. Its research stays in
`research/results/portfolio/crypto_donchian_cbot_2026-09-27.md`; the cBot source is in git history before that date.
