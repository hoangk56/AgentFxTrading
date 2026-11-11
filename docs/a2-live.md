# A2-D5L executor

`app/a2_live.py` trades research candidate A2-D5L on Binance USDT-M: when Upbit announces a coin for its KRW market,
long that coin's perp and short BTCUSDT at equal notional 5 s after the notice, and close both when the KRW market
opens. Rule, HOLD (+780 bp, t 3.11, n 91) and promotion: `research/results/portfolio/round65_retail_venues/A2/PREREG_A2_D5L.md`.
Its share of the fund: [capital-allocation.md](capital-allocation.md).

**Dry run by default.** Without `A2_LIVE=1` it runs the whole path and takes the fills at the book (ask for a buy,
bid for a sell), with no signed call. Live sends market orders with real money.

## How it works

1. **Notice.** The Telegram capture (`tg_pull.py` on agentFx, `/home/forge/tg_capture_a2`, round 74 TG2) appends every
   @upbit_news post to `pull_log.csv` about 1.5 s after it is posted. The executor reads that file every 0.2 s, keeps
   the KRW-listing posts (the capture's own `krw_listing` / `krw_tickers`) and starts one thread per listed coin. On its
   first start it marks every post already in the file as seen, so it never trades an old notice.
2. **Checks.** A coin is skipped, with the reason in `trades.csv`, when it has no USDT-M perp (`COIN`, `1000COIN`,
   `1000000COIN`), the perp is less than 7 days old at the notice, `A2_MAX_OPEN` events are open, `STOP_A2` exists,
   the order would go out later than `A2_MAX_ENTRY_DELAY_S` after the notice, or the size is under the market minimum.
3. **Entry.** While it waits, cross margin and `A2_LEVERAGE` are set on both symbols. At N + 4.7 s it reads both books
   and sizes each leg at the notional over the alt ask / BTC bid, floored to the lot step; at N + 5 s both market
   orders go out together. If one leg fails, the other is closed at once (reduce-only).
4. **Exit.** Upbit's public `candles/minutes/1?market=KRW-<coin>` is polled every 2 s; its first candle is the KRW open
   (the research's L), and both legs are closed reduce-only. No candle within `A2_MAX_HOLD_H` closes them anyway.
   A failed close is retried every 30 s and each failure is an ERROR (Telegram).
5. **Record.** `A2_STATE_DIR/trades.csv` has one row per event: fills, the book before entry, the KRW open, the exit
   and the net in bp by the registered arithmetic (long alt − short BTC − 20 bp). Open events live in `state.json`, so
   a restart resumes their exits.

**Sizing.** `A2_NOTIONAL_USDT` per leg; the first `A2_PHASEIN_TRADES` live entries (10) use
`A2_PHASEIN_FRACTION` of it (0.25), as in the allocation's phase-in rule. Dry run without a size uses 1,000 USDT.

## Differences from the registered rule

- Entry: the registered fill is each leg's first trade at or after N + 5 s; the executor's order goes out at N + 5 s
  and fills a moment later.
- Exit: the registered exit is each leg's first trade at or after L; the executor learns L from Upbit's first candle,
  up to one poll (2 s) plus the candle's own delay after the first KRW trade.
- No re-listing or stablecoin filter (the capture's notice test only). When L never comes the research used the stated
  time + 5 min; the executor closes at `A2_MAX_HOLD_H`.
- One account per strategy: in one-way mode two events share the BTCUSDT position, so the closes are reduce-only by
  each event's own quantity. Nothing else may trade the account.

## Setting up live (user steps)

1. A Binance **sub-account** used only by this executor, in **one-way** position mode, with USDT in its USDT-M wallet
   (for a notional of N per leg at leverage 3, about 2 N / 3 of margin per event, more for a buffer).
2. An API key on that sub-account with **only futures trading** enabled (no withdrawals, no spot / margin), restricted
   to the agentFx IP.
3. In `/home/forge/AgentFxTrading/.env`: `A2_BINANCE_KEY`, `A2_BINANCE_SECRET`, `A2_NOTIONAL_USDT`, then `A2_LIVE=1`.
4. `.venv/bin/python -m app.a2_live check` prints the mode, the key presence (never the key), the position mode and the
   balance, and sends no order. Restart the loop: `pkill -f "app.a2_live run"` (cron starts it again within a minute).

## Running

Cron on agentFx (forge's crontab), one loop held by flock:

    * * * * * cd /home/forge/AgentFxTrading && /usr/bin/flock -n /tmp/a2_live.lock .venv/bin/python -m app.a2_live run >> logs/a2_live.log 2>&1 # a2-live

| Command | Does |
|---|---|
| `python -m app.a2_live check` | config, key, position mode, balance; no order |
| `python -m app.a2_live status` | open events and the recorded trades |
| `python -m app.a2_live close-all` | closes every open event now |
| `touch $A2_STATE_DIR/STOP_A2` | no new entries; open events still exit normally |

Entries, exits and skips of coins that have a perp go to Telegram (`TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`, as
`app/alerts.py`), and so do ERROR lines.
