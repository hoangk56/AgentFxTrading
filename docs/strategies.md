# Strategies

What each cBot does, in outline. The code is the specification: the rules live in `cBot/<Name>.cs`, the gates and prompts of
the AI-gated bots in `app/trade_gates.py` and `app/trade_prompts.py`, and the tuned values per symbol in
[`app/cbot_presets.py`](../app/cbot_presets.py) (written out in [docker-instances.md](docker-instances.md)). Defaults
quoted below are the cBot's own parameter defaults, which the presets usually override.

> **Evidence.** None of these descriptions is a claim that the strategy makes money. The offline research
> ([research/README.md](../research/README.md), catalog in [research/STRATEGIES.md](../research/STRATEGIES.md), dated conclusions in
> [research/JOURNAL.md](../research/JOURNAL.md)) found
> no edge that survives multiple-testing correction and out-of-sample years for TMS+ORB, the Judas Sweep or FlowRSI.
> Gotobi passed its pre-registered holdout; Crypto Donchian failed its holdout and runs as a forward test.

| cBot | Symbols in the presets | Timeframe | Decision |
| :--- | :--- | :--- | :--- |
| `AiAgentBot` (TMS + ORB) | 15 (FX, gold, indices, crypto) | M15 (USTEC M5) | AI-gated via `/trade` |
| `AsianRangeJudasSweepBot` | 15 | M15 | AI-gated via `/trade`, or direct LLM call |
| `FlowRsiBot` | 15 | M15 | AI-gated via `/trade` |
| `GotobiBot` | USDJPY, EURJPY, GBPJPY | M15 chart, fixed UTC schedule | Rule-based |
| `CryptoDonchianBot` | BTCUSD, ETHUSD | H1 chart, H4 bars built in the bot | Rule-based |

## TMS + ORB (`cBot/AiAgentBot.cs`)

- **TMS bias** on a macro timeframe (default H1): the TDI green line (RSI, default period 6) crossing its red signal
  line (default 6) sets a BULLISH / BEARISH bias that stays until the next cross. An entry signal also needs the
  Heikin Ashi candle to turn with the bias, the Stochastic (default 6 / 6 / 4) to agree, and to come within
  `Max Bars After Cross` (default 5) of the cross.
- **Opening Range Breakout**: the range is the first `ORB Opening Range` minutes (default 15) from `OrbStartHour`
  (winter UTC, shifted by `SessionDstRule`). A breakout must close beyond the range plus `OrbBufferPips` by at least
  `MinDecisiveBreakoutPips`, and the range must be at least `MinOrWidthPips` wide.
- **Regime**: the bot sends a Kaufman efficiency ratio for the session and recent bars and the number of failed
  breakouts back into the range (`or_flips`). It labels the day `forming`, `trending` (session ER ≥ 0.35, or recent
  ER ≥ 0.45 with ≤ 3 flips), `choppy` or `mixed`. With `TrendTpDisabled=true` a trending day drops the fixed TP and
  leaves the exit to the trailing stop and giveback floor; on a choppy day with 5+ flips the server gates entries unless a fresh, momentum-confirmed breakout overrides it.
- **Exits and protection**: ATR-based SL/TP clamped between min / max ATR multiples, break-even and trailing stop
  in ATR units, partial close at break-even, giveback lock on the peak profit, post-TP re-entry gate, session-end
  flatten (`SessionEndHour`).
- The server's system prompt (`build_system_prompt`) describes the entry models the LLM is asked to follow.

## Asian Range Judas Sweep (`cBot/AsianRangeJudasSweepBot.cs`)

- **Asian range**: high and low between `asianStartHour` and `asianEndHour` (default 00:00-06:00 UTC); a day is
  skipped when the range is outside `minAsianRangePips` / `maxAsianRangePips`.
- **Killzones**: London (default 07-10 UTC) and New York (default 12-16 UTC); the DST rule shifts them by an hour in
  winter.
- **Sweep**: price wicks beyond the Asian high (sell setup) or low (buy setup) by at least `sweepBufferPips` and
  closes back inside the range. With `UseAiGateMode=true` (default) the sweep only triggers an AI review; the LLM
  confirms or rejects with a confidence that must reach `AiConfidenceThreshold`.
- **AI path**: through the server (`/trade`, default) or, with `UseDirectAiApi=true`, straight to an
  OpenAI-compatible endpoint with the bot's own key and model, bypassing the server's gates and risk checks.
- Also: news filter from the server's ForexFactory calendar, break-even, trailing stop, optional DCA and Telegram.

## FlowRSI (`cBot/FlowRsiBot.cs`)

- **Nested RSI**: a fast RSI (default 7) crossing a slow RSI (default 14), with the cross required inside
  oversold / overbought bands.
- **SMC filters**: fair value gap (minimum size `FvgMinPips`), premium / discount zone, liquidity sweep.
- **Macro TMS filter**: a TDI bias on a higher timeframe (default H1) that entries must agree with.
- **AI gate** (`UseAiGateMode`, default on): the server holds without calling the LLM when there is no setup, then
  asks the LLM, whose confidence must reach `AiConfidenceThreshold` (default 65).
- Risk: `RiskPercentage` capped by `MaxRiskPerTradeMoney`; break-even, trailing stop and partial close.

## Gotobi Fix (`cBot/GotobiBot.cs`)

Research candidate C3. On gotobi days (the 5th, 10th, 15th, 20th, 25th and the last day of the month; weekend dates
move to the Friday before) Japanese importers buy USD at the 09:55 Tokyo fixing. The bot buys at 03:00 Tokyo
(18:00 UTC the evening before) and closes at the fix (00:55 UTC), then sells at the fix and closes at 11:55 Tokyo
(02:55 UTC). One position at a time per instance. Each trade risks `RiskPerTradeMoney` dollars at a stop of
3 × ATR20 (H1). Result file: `research/results/portfolio/swing_lab_v2_2026-09-27.md`.

## Crypto Donchian (`cBot/CryptoDonchianBot.cs`)

Research candidate C1, **forward test only**. On a UTC-aligned H4 close above the prior 55-bar high it buys (below
the prior 55-bar low it sells), stacking up to 3 positions on a continuing breakout. A position exits on an H4 close
through the prior 20-bar opposite extreme, at its 3 × ATR20 (H4) stop, or after 5 days. Risk per trade is
`RiskPerTradeMoney` scaled 0.5×-2× by breakout strength; a kill switch can stop the bot after a number of trades if
its mean R falls below a floor. It passed its in-sample and validation years but failed the 2025-2026 holdout, so
run it small and on demo first. Result file: `research/results/portfolio/crypto_donchian_cbot_2026-09-27.md`.
