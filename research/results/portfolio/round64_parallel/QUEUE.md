# Round 64 queue: hypotheses ready for the next free slot (coordinator notes)

Written 2026-11-01 08:56 UTC. Each line becomes a stream section appended to BRIEF.md when a slot frees up.

1. (launched 08:58 UTC as stream V) **V: venues that lend coins for B (scouting, no backtest).** Public, keyless endpoints that list borrowable coins and
   hourly rates (Bybit spot-margin public data, OKX public interest-rate / loan-quota, Gate unified margin pairs, KuCoin
   margin currencies). Output: share of B's universe (round63 B universe60.csv) borrowable per venue today, rate
   distribution vs the 40 %/yr B charged, whether the venue's spot tracks Binance spot at B's signals (BX lesson:
   the spot leg is what moves). Feeds the pending user decision "sàn / tài khoản khác vay được coin cho B".
2. (launched 09:06 UTC as stream T, after N finished: inventory route not viable, VAL combined -5.5 %/yr vs cash)
   **T: perp delisting convergence.** Binance USDT-M perps delisted 2020-24 (last kline in perp_1d; settlement at the
   index). Enter T-24 h assuming the announcement came >= 24 h earlier (check the announced lead time from public
   sources without /bapi/), rich-perp side only (short perp / long spot, no borrow), hold to settlement. Small N:
   needs per-trade Sharpe >= ~0.5.
2b. (launched 09:09 UTC as stream X, after V finished: other venues lend B's coins at ~6 %/yr but their spot misses
   the Binance-specific 40-50 bp drop) **X: long cheap Binance spot vs other venues' spot, perp-hedged.**
3. **L: Coinbase USD listing fade** (first Coinbase Exchange candle) on Binance perps, like K2. Run only if K2 shows a
   fade with the right sign.
4. **S: stablecoin peg reversion on Binance spot** (USDC / BUSD / TUSD / FDUSD vs USDT; buy the cheap one with USDT,
   no borrow). Low value: depegs cluster in a few episodes; fee promos change the cost by the month.
