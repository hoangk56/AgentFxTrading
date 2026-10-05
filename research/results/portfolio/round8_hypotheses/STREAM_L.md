# Stream L: intraday lead-lag between symbols (written 2026-10-04 17:58 UTC, before any number)

Question: does one symbol's recent move predict another symbol's next minutes-to-hours move, by enough to pay costs?
M1 resolution: sub-minute leads cannot be seen or traded by a cTrader bot anyway, so only >= 1-minute leads count.

L1 systematic matrix (catch what the named hypotheses miss). For every ordered pair (leader A, follower B) among the
26 symbols: signal = A's log return over the last k minutes (k in {1, 5, 15, 60}), vol-scaled by A's trailing 20-day
sd at that horizon; target = B's mid return over the next h minutes (h in {1, 5, 15, 60}) starting at t+1 (1 minute
after the signal minute closes). Control for B's own past k-minute return (partial slope). Separate sessions: Asia
23-07, Europe 07-13, US 13-20 UTC. Use non-overlapping sampling (step = max(k,h)) or day-clustered t. Report the cell
count K and the chance max |t|. Take the top cells by IS |t| and report their VAL sign/size, bp per 1-sd leader move
and in the top decile of |leader move|, against the follower's median spread at those times.

L2 named economic leads (each written before its numbers):
- L2a JP225 -> USDJPY in Tokyo hours 00-06 UTC (Japanese equity / yen co-movement; exporters' hedging, Abenomics).
- L2b US500/USTEC -> AUDJPY, USDJPY, AUDUSD in US hours (risk-on/off carry; Ranaldo & Söderlind 2010).
- L2c XAUUSD -> AUDUSD (Australia is a gold exporter; Chen & Rogoff 2003 commodity currencies).
- L2d XAUUSD -> XAGUSD / XPTUSD (gold as the price-discovery leader in precious metals; e.g. Lucey & Li).
- L2e XTIUSD/XBRUSD -> USDCAD at 1-15 min (round 3 tested only 1-3 h after a 30 bp hourly oil move).
- L2f DE40 -> EURUSD and UK100 -> GBPUSD around the European cash open 07-09 UTC.
- L2g BTCUSD -> ETHUSD at 1-15 min (Bitcoin as the crypto price leader; e.g. Sifat, Mohamad & Shariff 2019).
- L2h USD factor (equal-weight mean of the USD legs of EURUSD GBPUSD AUDUSD NZDUSD USDCAD USDCHF USDJPY, signed so +
  = USD up) -> XAUUSD and -> each USD pair's deviation from the factor (laggard pair catches up with the dollar).
- L2i US500 -> AUS200 / JP225 / HK50 during their cash sessions.
- L2j majors -> crosses at 1 min (EURUSD & USDJPY -> EURJPY; GBPUSD & USDJPY -> GBPJPY; AUDUSD & USDJPY -> AUDJPY):
  do IC's cross quotes lag the synthetic product by a minute? (expected: no; quantify the deviation vs spread).

L3 dynamic lead-lag (Huth & Abergel 2014, "High frequency lead/lag relationships - empirical facts"; de Jong &
Nijman 1997; Hayashi & Yoshida 2005): leads may exist only in some periods. For each L2 pair, each day estimate the
trailing 20-trading-day lagged cross-correlation at lags 1..5 minutes (leader -> follower minus the reverse), and
trade the follower the next day only when the trailing lead estimate is strong (top tercile). Strictly causal.

Turn the best cell of each family into a tradeable rule (enter follower at t+1 when |leader move| > threshold, exit
after h minutes, no stop or a wide one) and give net bp at the actual spreads, +1 min latency, x1.5 spread.
