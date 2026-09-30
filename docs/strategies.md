# Strategies

What each cBot does, in outline. The code is the specification: the rules live in `cBot/<Name>.cs` and the values per
symbol in [`app/cbot_presets.py`](../app/cbot_presets.py) (written out in [docker-instances.md](docker-instances.md)).
Defaults quoted below are the cBot's own parameter defaults.

> **Evidence.** None of these descriptions is a claim that the strategy makes money. The offline research
> ([research/README.md](../research/README.md), dated conclusions in [research/JOURNAL.md](../research/JOURNAL.md))
> found that Gotobi passed its pre-registered holdout; Crypto Donchian failed its holdout and runs as a forward test.

Both bots are rule-based: they never ask the server for a decision. They report positions and telemetry to it and
poll it for dashboard commands.

| cBot | Symbols in the presets | Timeframe |
| :--- | :--- | :--- |
| `GotobiBot` | USDJPY, EURJPY, GBPJPY | M15 chart, fixed UTC schedule |
| `CryptoDonchianBot` | BTCUSD, ETHUSD | H1 chart, H4 bars built in the bot |

## Gotobi Fix (`cBot/GotobiBot.cs`)

Research candidate C3. On gotobi days (the 5th, 10th, 15th, 20th, 25th and the last day of the month; weekend dates
move to the Friday before) Japanese importers buy USD at the 09:55 Tokyo fixing. The bot buys at 03:00 Tokyo
(18:00 UTC the evening before) and closes at the fix (00:55 UTC), then sells at the fix and closes at 11:55 Tokyo
(02:55 UTC). One position at a time per instance. Each trade risks `RiskPerTradeMoney` dollars at a stop of
3 × ATR20 (H1). Result file: `research/results/portfolio/swing_lab_v2_2026-09-27.md`.

**Camouflage.** So the broker cannot read the strategy off its orders, a live or demo bot with the trade tag key
([deployment.md](deployment.md#running-bots)) sends a random 0.8-1.0 × fraction of the stop to the broker (a dead
bot loses at most 1 R), opens each long at its own time within ±60 min of 18:00 UTC, and trades about two decoy
legs per real one on plain weekdays: same hours, 0.01 lot, a 0.5 × ATR stop the bot closes itself. The broker sees
a ~39 % win rate instead of ~56 %. On 2024-01..2026-09 at $200 risk this cost 10 % of the net; decoys at the real lot
would have cost 83 % (`research/results/portfolio/gotobi_camouflage_2026-09-30.md`). Without the key, or with
`--VirtualStop=false`, the bot trades as before; set `--DecoyLegProbability=0` and `--LongEntryJitterMinutes=0` to
backtest the plain strategy.

## Crypto Donchian (`cBot/CryptoDonchianBot.cs`)

Research candidate C1, **forward test only**. On a UTC-aligned H4 close above the prior 55-bar high it buys (below
the prior 55-bar low it sells), stacking up to 3 positions on a continuing breakout. A position exits on an H4 close
through the prior 20-bar opposite extreme, at its 3 × ATR20 (H4) stop, or after 5 days. Risk per trade is
`RiskPerTradeMoney` scaled 0.5×-2× by breakout strength; a kill switch can stop the bot after a number of trades if
its mean R falls below a floor. It passed its in-sample and validation years but failed the 2025-2026 holdout, so
run it small and on demo first. Result file: `research/results/portfolio/crypto_donchian_cbot_2026-09-27.md`.
