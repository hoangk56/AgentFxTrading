# PREREG K2: fade the Upbit KRW-listing pump on Binance perps (DEMO tier)

Registered 2026-11-01 10:21 UTC (from `date -u`) by the coordinator, before any 2025-26 listing date or price was read.
Draft: [PREREG_DRAFT_K_upbit_listing_fade.md](PREREG_DRAFT_K_upbit_listing_fade.md) (stream K, 09:58 UTC), which holds
the full IS / VAL tables, random benchmark, post-hoc pump control and caveats. HOLD 2025-01-01..2026-10-29 is opened
once by `coord/hold/hold_run.py`.

## Rule (frozen, as the draft)
Event: a coin's first Upbit KRW 60-minute candle L (UTC), its Binance USDT-M perp listed >= 7 days before L. Short the
alt perp, long BTCUSDT perp in equal notional, both at the close of the 1m bar starting at L + 1 h; exit both 72 h later;
cost 42 bp; funding of both legs at the real stamps. No stop.

## IS / VAL (stream K; reproduced exactly by `coord/hold/k2rule.py` + `check_isval.py` from public fapi 1m prices)
IS 2020-21: n 11, +1,094 bp, t 3.16. VAL 2022-24: n 29, +423 bp, t 1.37. 5 / 5 years positive, random 100 %, positive
at x1.5 and late entries. DEMO bars pass; LIVE bars do not (VAL t < 1.5, power at VAL size ~1.07 with ~18 HOLD events).

Context known before registration: stream L ran K2's frozen rule on Coinbase listings and it failed (IS -621 bp,
VAL +151); the Upbit pump before entry (+21.5 %) is what Coinbase listings lack. This does not change K2's rule.

## HOLD implementation (declared)
- Events (`hold_events.py`): current Upbit KRW markets (market_all.json, fetched by stream K on 2026-11-01) mapped to
  Binance perps (base+USDT, else 1000+base+USDT; stablecoins and BTC excluded; fapi underlyingType COIN); no KRW candle
  before 2025-01-01; L in 2025-01-01..2026-10-25; perp first daily kline <= L - 7 d. Survivorship: Upbit-delisted
  markets are missing (likely against the short, as in IS / VAL).
- Prices / funding: `k2rule.py` (public fapi 1m klines, local funding or fapi fundingRate).

## HOLD pass bar (DEMO rule) and what follows
- Pass: HOLD net mean > 0. Fail (net <= 0): drop the rule. Reported: x1.5, L + 2 h entry, median, worst, per year, n.
- If it passes: DEMO only (power ~1). Demo plan, stop rule (after 10 demo trades cumulative net < -2,500 bp, or HOLD +
  demo pooled mean < 0 after 20 pooled trades) and promotion (HOLD + demo pooled t >= 2.5, n >= 40) as in the draft.
  The user decides on any bot.

## Hashes (`python -m research.tools.prereg_hashes`, 10:21 UTC; stream K's code hashes are in the draft)
- `research/results/portfolio/round64_parallel/K/coord/hold/k2rule.py` f7392095f3d89c6a
- `research/results/portfolio/round64_parallel/K/coord/hold/check_isval.py` d32c89a871a19ecf
- `research/results/portfolio/round64_parallel/K/coord/hold/hold_events.py` 13dc152014891824
- `research/results/portfolio/round64_parallel/K/coord/hold/hold_run.py` 57d968165170046e
- `research/data/upbit/raw/market_all.json` bbdc54fd06e29930

## HOLD result
(appended after the single run)

Events found 2026-11-01 10:25 UTC (`hold_events.py`): 92 HOLD listings (vs ~18 expected at the VAL pace: Upbit listed
many more coins that already had Binance perps in 2025-26). Run once 2026-11-01 10:30 UTC (`hold_run.py`, output
`coord/hold/hold_output_2026-11-01.txt`):

| HOLD 2025-01..2026-10 | n | net bp | t (day) | median | gross | funding | x1.5 | L + 2 h | worst / best | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K2 H72 | 92 | **+221** | 0.88 | +656 | +775 | -512 | +200 | +160 | -9,959 / +4,032 | -110 (n 45) | +539 (n 47) |

- **DEMO bar (net > 0): PASS.** K2 is a DEMO candidate that passed HOLD. Not LIVE (t 0.88; the bar for promotion is
  HOLD + demo pooled t >= 2.5 with n >= 40, unchanged rule).
- The price leg still fades (+775 bp gross), but shorting just-listed coins paid -512 bp of funding on average in
  2025-26 (crowded shorts after listing pumps): the funding leg is what changed since VAL (-105 bp).
- 2025 net negative, 2026 positive; the tail (-9,959 bp) is the round-60 squeeze risk; no stop was registered.

## Public-data forward log (supplementary; added 2026-11-01 18:41 UTC)
`coord/forward/fwd_k2.py` (sha 479ccefb5fb40b71) applies the registered rule (k2rule.trade unchanged) to Upbit KRW
listings with L >= 2026-10-26 (fresh market list, fapi 1d perp-age check) and appends to
research/data/upbit_fwd_k2/fwd_log.csv. First slice: 1 event (see the log). Supplementary to the registered promotion
test (demo trades); re-run any time.
