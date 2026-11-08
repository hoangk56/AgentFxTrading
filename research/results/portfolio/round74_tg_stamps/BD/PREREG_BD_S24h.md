# PREREG BD-S24h: short the perp of a coin Binance spot-delists, from the Telegram post + 5 s to + 24 h (new-era test)

Registered 2026-11-02 16:07:59 UTC (from `date -u`) by stream BD, before any 2025-26 price, funding or return for this rule was
requested or looked at (2025-26 class-S titles were only counted: 21 posts). Approval: the user, 2026-11-02, for a
**new-era design**: the design era is VAL 2022-01-01..2024-12-31, because IS 2020-21 has no tradable event (24 class-S
coins, none with a Binance USDT-M or Bybit perp on the notice day). The test is the registered HOLD
2025-01-01..2026-10-29, opened **exactly once, by the coordinator**, with `code/hold_s24h.py --open-hold-once`.
Design documents: [HYPOTHESES_BD.md](HYPOTHESES_BD.md) (cell declared 14:23:27 UTC, before any title or price),
[STREAM_BD.md](STREAM_BD.md) (VAL run).

## Rule (frozen, unchanged from the VAL run; no re-tuning)
- Events: posts of @binance_announcements (Telegram post time N, whole seconds, from the saved t.me preview pages,
  `coord/parse.py`), title = first non-empty line, class **S** by `events.classify` (spot delisting of the coin; X /
  MT / F / M / O / P excluded first, as declared in HYPOTHESES_BD.md + amendment 1). **Edited posts dropped.** Window:
  2025-01-01 00:00:00 <= N < 2026-10-30 00:00:00 UTC.
- Coins: `events.coins` (tickers after "Delist", else "(TICKER)" groups of the body), stablecoins / fiat tokens excluded.
  One trade per coin.
- Instrument (first that exists on the notice day): Binance USDT-M `<C>USDT`, `1000<C>USDT`, else Bybit linear
  `<C>USDT` (data.binance.vision / public.bybit.com daily files, `pull.exists`). None: no trade.
- Entry: SHORT at the **worst price of the 1 s bucket** (lowest trade of that second) of the first trade at or after
  N + 5 s. Exit: buy back at the worst price (highest trade) of the 1 s bucket of the first trade at or after N + 24 h.
  A coin with no trade in the second N - 60 s (reference price NaN) is dropped, as in the VAL run.
- Costs: taker 5 bp a side (Binance USDT-M) / 5.5 bp (Bybit), plus the worst-of-1 s fills; **real funding** over the
  hold (fapi fundingRate / Bybit v5 funding history; the short receives positive funding). Unhedged.
- t: mean net per trade over its day-clustered standard error (`analyze.clt`, clusters = notice UTC day).

## Design-era numbers (VAL 2022-24, STREAM_BD; reproduced exactly by `hold_s24h.py --dry-val`)
| | n (days) | net bp | t (day) | median | SR/trade | win | x1.5 | +10 s entry | BTC-hedged | edited kept |
|---|---|---|---|---|---|---|---|---|---|---|
| S-24h VAL | 14 (7) | **+1,418** | **3.60** | +1,755 | 0.96 | 71 % | +1,413 | +1,399 | +1,492 | +1,180 (t 2.91, n 17) |

- Years: 2022 0 trades, 2023 +928 (1 trade), 2024 +1,455 (13). Leave-one-day-out t 2.69..4.07. Gross +1,526, funding
  -98, fees -10.
- Random (same coin, random 5m opens in N +- 30 d excluding +- 2 d, 2,000 sets, `random24.py`): random mean -23 bp vs
  event +1,516 ex-funding; the event beats 100 % of random sets, the event t (3.99 ex-funding) beats 99.8 % of random t
  (95th pct 1.84).
- Post-hoc (not a cell): a 24 h short entered at N + 5 min still +1,277, at N + 60 min +738 (fees only): the edge is
  the 24 h drift after the notice, not seconds.
- Power at VAL size: SR 0.96 x sqrt(14 expected HOLD trades) = **3.6** (bar 3).

## Expected HOLD size
HOLD has 21 class-S posts in 2025-26 (count only, from events.py, edited and post-10-29 posts included). At VAL's 0.67
graded trades per class-S post: **~14 trades** (power 3.6); at 2024's 1.6 per post: ~34 (power 5.6). Fewer if many
delisted coins have no perp, or many posts are edited.

## HOLD pass bar (fixed now)
- **LIVE** if, on HOLD, all four hold: net > 0 per trade, day-clustered t >= 2.5, net > 0 at costs x1.5, and net > 0
  with the entry at N + 10 s (exit unchanged). **Fail** otherwise.
- If HOLD has **n < 8 graded trades: "not gradable"** (neither pass nor fail; the cell stays a forward-log candidate).
- Also reported, not gates: n, notice days, per-year net (2025, 2026), BTC-hedged net, the edited-kept variant (info
  only), the random same-coin benchmark (random24.py method, 2,000 sets, seed 7424), post-hoc N + 5 min / 60 min
  entries, leave-one-day-out t, coins dropped (no perp / no reference price / no 24 h exit) and events skipped because
  their files were not published yet.
- No change to the rule, costs, window or bar after the run. The result is appended below, once.

## Limits (honest)
- The design sample is thin: **14 trades on 7 notice days, 13 of 14 in 2024** (2022 had no tradable coin, 2023 one).
  A day-clustered t over 7 clusters is fragile; the HOLD test is in effect the first real test of the mechanism with a
  short instrument. If the true Sharpe per trade is half the VAL one (0.48), the expected HOLD t at 14 trades is ~1.8
  and the bar likely fails.
- No IS: the BRIEF's LIVE bar (t >= 2.5 IS) cannot be met by construction; this is the user-approved new-era design,
  with HOLD as the single test at the IS-level t bar.
- The Telegram stamp lags Binance's own notice by ~2-7 min in 2023-24 (the coin had already fallen ~12 % median in the
  9 minutes before N). Entry "N + 5 s" is really "website + minutes"; the rule trades the 24 h drift, which survives
  later entries in VAL. A live version would use the same channel (no seconds race).
- Not modelled: borrow / leverage limits or reduce-only status Binance may put on a perp of a coin being
  spot-delisted, the perp's own delisting inside the 24 h (such a trade has no exit price and is dropped and counted as
  "entry but no 24 h exit"), short squeezes and extreme funding (BOND 2024: -776 bp funding in 24 h). Size per trade
  must be small.
- Data: Telegram pages saved 2026-11-02 (edited flag as seen then). data.binance.vision / public.bybit.com daily files
  exist up to ~2 days before 2026-11-02; the last exit day is 2026-10-30. Events whose notice day or next day has no
  BTCUSDT reference file on either site are **skipped and listed** (not filled from REST). 5m bars for the random
  benchmark: monthly files, else daily files for an unpublished month (Binance), Bybit v5 kline REST.

## HOLD implementation (declared)
- `code/hold_s24h.py --open-hold-once`: refuses if `BD/HOLD_OPENED` exists, creates it first (UTC time, command),
  then: events (`events.load` / `title` / `classify` / `coins`, window cut right after parsing), instruments (same
  order as `instruments.py`), per-second arrays (`pull.build`: aggTrades / Bybit ticks for the notice day and the next
  day, into `research/data/binance_delist_tg/hold/`), trades (`analyze.trade` with `analyze.fill` / `analyze.funding`),
  stats (`analyze.clt`), random benchmark (random24.py method). Copies with only the date limit moved: `arr_w`
  (analyze.arr), `btc_w` (analyze.btc), `bars_w` (random24.bars, UTC months + daily fallback), `guard_w` (net.guard:
  refuses any URL date > 2026-10-30 or time >= 2026-10-31 00:00 UTC).
- Outputs: `BD/hold_results.txt`, `BD/trades_hold.csv` (every HOLD coin with its status), `BD/HOLD_OPENED`.
- Dry-val (`--dry-val`, VAL window, the VAL guard <= 2024 kept on top): reproduces every S-24h VAL number of
  cells.json / cells_edited.json / random24.txt exactly (14 fields x 2 variants + the random and post-hoc lines),
  both from the VAL caches and with `--fresh <empty dir>` (every price, bar, BTC and funding file fetched again):
  `BD/dryval_results.txt` (the `--fresh` run of 16:03-16:07 UTC: 578 requests, 232 x 200, 346 x 404 HEAD probes,
  every URL <= 2024-12-31; "DRY-VAL REPRODUCED EXACTLY"; the cached run at 16:03 UTC gave the same).
- Command for the coordinator (once):
  `cd /Users/hoangbk/00.code_base/105.AgentFxTrading/research/results/portfolio/round74_tg_stamps/BD/code && /Users/hoangbk/00.code_base/105.AgentFxTrading/research/.venv/bin/python -I hold_s24h.py --open-hold-once`

## Hashes (`python -m research.tools.prereg_hashes`, Mon Nov  2 16:07:59 UTC 2026)
- `research/results/portfolio/round74_tg_stamps/BD/code/hold_s24h.py` fe55b153d533e935
- `research/results/portfolio/round74_tg_stamps/BD/code/analyze.py` 55152636dd8a1c28
- `research/results/portfolio/round74_tg_stamps/BD/code/events.py` 4afe87f292430b45
- `research/results/portfolio/round74_tg_stamps/BD/code/pull.py` e7bf77f75e569af9
- `research/results/portfolio/round74_tg_stamps/BD/code/net.py` 7aba8f715a97617d
- `research/results/portfolio/round74_tg_stamps/coord/parse.py` 9ba2c9e9e7f7cb48
- `research/results/portfolio/round74_tg_stamps/BD/cells.json` 495cc02ab47074da (dry-val target, read at import)
- `research/results/portfolio/round74_tg_stamps/BD/cells_edited.json` e6614b5f2523710f (dry-val target)

Do not edit these files until the HOLD run. `instruments.py` and `random24.py` are not imported (their logic is copied
into hold_s24h.py and checked by the dry-val).

## HOLD result
(appended after the single run)
