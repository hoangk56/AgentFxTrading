# Strategies

What the cBot does, in outline. The code is the specification: the rules live in `cBot/<Name>.cs` and the values per
symbol in [`app/cbot_presets.py`](../app/cbot_presets.py) (written out in [docker-instances.md](docker-instances.md)).
Defaults quoted below are the cBot's own parameter defaults.

> **Evidence.** None of these descriptions is a claim that the strategy makes money. The offline research
> ([research/README.md](../research/README.md), dated conclusions in [research/JOURNAL.md](../research/JOURNAL.md))
> found that Gotobi passed its pre-registered holdout. The ECB window's F3 passed its holdout only at the relaxed
> tier and E1 is a weak demo candidate; both run to measure them, F3 at the minimum lot.

The bots are rule-based: they never ask the server for a decision. They report positions and telemetry to the server and
poll it for dashboard commands.

| cBot | Symbols in the presets | Timeframe |
| :--- | :--- | :--- |
| `GotobiBot` | USDJPY, EURJPY, GBPJPY | M15 chart, fixed UTC schedule |
| `EcbWindowBot` | EURUSD (rules F3 and E1) | M15 chart, London schedule |

## Gotobi Fix (`cBot/GotobiBot.cs`)

Research candidate C3. On gotobi days (the 5th, 10th, 15th, 20th, 25th and the last day of the month; weekend dates
move to the Friday before) Japanese importers buy USD at the 09:55 Tokyo fixing. The bot buys at 03:00 Tokyo
(18:00 UTC the evening before) and closes at the fix (00:55 UTC), then sells at the fix and closes at 11:55 Tokyo
(02:55 UTC). One position at a time per instance. Each trade risks `RiskPerTradeMoney` dollars at a stop of
3 × ATR20 (H1). Result file: `research/results/portfolio/swing_lab_v2_2026-09-27.md`.

**Orders at the fix.** Orders are asynchronous. At the fix the short's order goes out before the long's close, so
for under a second both are open. A short sent only after the close filled 0.5–1.2 pip worse than the backtest
(`research/results/portfolio/gotobi_live_fills_2026-10-06.md`). A failed order is retried after `OrderRetrySeconds`
(2 s), with the wait doubling after each further failure up to 60 s. Every fill and every close the bot sends logs
the quote when it was sent, the slippage in pips and the broker's latency.

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

## ECB Window (`cBot/EcbWindowBot.cs`)

Research candidates E1 and F3. EUR is sold into the 14:15 CET ECB reference rate, so EURUSD tends to fall over the
London midday. The bot sells EURUSD at 11:00 London and buys it back at 13:00 London, one position at a time, at a
fixed lot (`Lots`). E1 (`UsdTopOnly=false`) trades every weekday; F3 (`UsdTopOnly=true`) only on USD-TOP days: the mean
log change of USDJPY and USDCHF mids from 18:00 New York on the previous weekday to 07:00 London is at or above the
67th percentile (numpy's linear) of the previous 250 weekdays' scores, with at least 60 known. A score needs a quote
within 10 minutes before each time, so Mondays (Friday 18:00 New York is after the close) never qualify. Both skip
24/12-1/1. Pre-registrations: `research/results/portfolio/round13_structural/PREREG_M_eurusd_midday.md` (E1),
`research/results/portfolio/round24_relaxed/PREREG_R24_relaxed_hold.md` (F3, with the stop and promotion rules of
`PREREG_DRAFT_C_ecb_window_variants.md`).

**Selector quotes.** The bars cTrader gives a cBot are bid-only, and the 18:00 New York spread is wide after the
rollover; scoring on bids instead of mids changes ~6 % of the F3 days
(`research/results/portfolio/ecb_window_cbot_2026-10-16.md`). So the bot records the live bid and ask of the selector
symbols at both minutes in a quote log (`/root/ctrader_data/<BotId>_usd_top_quotes.csv`, kept across restarts), reads
its history from that log and from the research seed `cBot/seeds/ecb_usd_top_seed.csv`
(`research/tools/ecb_usd_top_seed.py`), and only for a minute neither holds uses the bid close of an M15 bar. Each
day's verdict is logged with its score, threshold, history count and quote sources; each trade reports them in
`entry_indicators` with the quote at the order, the latency and the spread.

**Timing.** The order goes out at 11:00:00 London; if it cannot within `EntryGraceSeconds` (60) the day is skipped, as
one minute late cost E1 its whole holdout net. The close goes out at 13:00 London. The broker gets a far stop
(`EmergencyStopPips`, 100) that is not part of the rule.

## Removed bots

Crypto Donchian (`CryptoDonchianBot`, research C1: an H4 Donchian breakout on BTCUSD and ETHUSD) failed its
2025-2026 holdout, ran as a forward test and was removed on 2026-10-03. Its research stays in
`research/results/portfolio/crypto_donchian_cbot_2026-09-27.md`; the cBot source is in git history before that date.
