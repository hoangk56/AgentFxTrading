# Depth logger — the order book at the Gotobi minutes

`cBot/DepthLoggerBot.cs` records IC's depth of market for USDJPY, EURJPY and GBPJPY during three UTC windows:
17:58-18:03 (long entry), 00:53-00:58 (the Tokyo fix, where the long exit and the short entry both sell) and
02:53-02:58 (short exit). It never trades and never calls the server. The cTrader tick history has no volumes, so
this book is the only way to price a 5-30 lot Gotobi order before running one.

It is a measurement tool, not a strategy: it has no preset in `app/cbot_presets.py`, and its container name does not
start with `cbot-`, so the dashboard and the watchdog leave it alone.

## Running it

Build it like the other cBots ([deployment.md](deployment.md#building-the-cbots), `NAME=DepthLoggerBot`), then copy
the `.algo` out of the repo checkout so a deploy never touches it:

```bash
sudo mkdir -p /home/forge/ctrader/depth_logger
sudo cp /home/forge/ctrader/cAlgo/Sources/Robots/DepthLoggerBot.algo /home/forge/ctrader/depth_logger/

docker run -d \
  --name depthlog-live-jpy \
  --restart unless-stopped \
  --network host \
  -v /home/forge/ctrader:/root \
  ghcr.io/spotware/ctrader-console:latest \
  run /root/depth_logger/DepthLoggerBot.algo \
  --ctid=your_email@example.com \
  --pwd-file=/root/ctrader_data/ctid_live-live_pwd \
  --account=YOUR_LIVE_ACCOUNT_ID \
  --symbol=USDJPY \
  --period=m15 \
  --full-access
```

`--symbol` only attaches the cBot; the recorded symbols come from `--SymbolList`. Other parameters: `--WindowList`
(UTC `HH:mm-HH:mm`, comma-separated), `--MinIntervalMs` (200), `--MaxLevels` (20 a side), `--OutputDir`
(`/root/depth_logs`, i.e. `/home/forge/ctrader/depth_logs` on the host).

Each window ends with a log line `[Depth] window closed: USDJPY 273 rows, …`; zero rows means the book was empty.

## Output and analysis

One file per symbol and UTC day, `depth_SYMBOL_yyyyMMdd.csv`: `ts_ms` (UTC), `src` (`U` book update, at most one per
`MinIntervalMs`; `T` the 1 s timer), `bids` and `asks` as `price:units` levels joined by `|`, best first. About
1 MB per symbol and day.

```bash
mkdir -p /tmp/depth
ssh agentFx 'sudo -n tar cf - -C /home/forge/ctrader/depth_logs .' | tar xf - -C /tmp/depth
research/.venv/bin/python -m research.tools.depth_cost /tmp/depth
```

`research/tools/depth_cost.py` prices 1-30 lots per leg (doubled at the fix) at each event, on gotobi and other days,
under two readings of IC's tiered book (`walk`: levels add up; `tier`: each level is a separate full-amount quote).

Stop it with `docker rm -f depthlog-live-jpy` once enough gotobi days are in.
