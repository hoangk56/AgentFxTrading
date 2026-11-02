# PREREG F: fade 5 % idiosyncratic 1-minute wicks on Binance USDT-M altcoin perps, hold 60 min (LIVE candidate)

Registered 2026-11-01 09:44 UTC (from `date -u`) by the coordinator, before any 2025-26 price or funding value of
this rule was read. Draft by stream F: [PREREG_DRAFT_F_wick_fade.md](PREREG_DRAFT_F_wick_fade.md) (09:36 UTC);
hypotheses [HYPOTHESES_F.md](HYPOTHESES_F.md) (08:54 UTC, before any return); report [STREAM_F.md](STREAM_F.md).
HOLD 2025-01-01..2026-10-29 is opened **once**, by `coord/hold/hold_run.py`.

## Rule (frozen, cell "T5 idio H60", the best IS t of 18 declared cells)
- Universe each UTC day d: the top 40 Binance USDT-M perps by mean daily quote volume over d-30..d-1, listed >= 60
  days (round 63 C `xs.daily_universe`), excluding stablecoins, index and TradFi underlyings (round 60 `EXCL_BASE`).
- Event at 1m bar e: r = close_e / close_{e-1} - 1 (consecutive bars), |r| >= 5 %, coin in the universe on e's day,
  not BTCUSDT, |r_BTCUSDT,e| <= 0.2 |r|; guard: bar e has >= 10 trades and quote volume > 0, bar e+1 exists and its
  open is still beyond the halfway point of the move. Same coin's events within 60 bars after an accepted one are
  ignored.
- Trade: long after a crash, short after a spike; enter at the close of bar e+1; exit at the close of bar e+61 (last
  close within 5 minutes before it if missing, else dropped). P&L = side x (exit / entry - 1) - side x funding on
  stamps in (entry, exit] - costs. Costs: taker 5 bp a side; half-spread h = 3 bp (volume rank < 20) or 5 bp (rank
  20-39), 1 bp for ETH; entry half-spread 3h, exit h (round trip 22 / 30 bp).

## IS / VAL (stream F, reproduced exactly by the coordinator's re-implementation `coord/hold/rule.py`)
| era | n | net bp | median | t (day) | S / trade | x1.5 | 2 bars late | mean-OHLC fills | crash / spike |
|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 380 | +273.0 | +274 | 4.05 | 0.224 | +260.2 (3.87) | +297.0 (6.65) | +277.9 (5.14) | +581 / -189 |
| VAL 2022-24 | 770 | +270.5 | +177 | 3.76 | 0.163 | +257.7 (3.58) | +231.9 (3.12) | +255.5 (3.53) | +360 / +132 |

Years 2020-24 all positive (+460 / +237 / +397 / +164 / +236). Random entries beaten 100 % (weak test: random entries
only lose the cost); max-over-18-cells null p95 +0.28 vs real IS t 4.05. Daily-P&L correlation with C3: IS +0.05,
VAL -0.04. LIVE bars on IS / VAL: all pass (IS t 4.05 >= 2.5, VAL t 3.76 >= 1.5, 5/5 years, random 100 %).

Coordinator stress (`coord/stress.py`, IS / VAL only): entry and exit at the mean OHLC of the next bar keep the edge
(above); entry at the worst extreme of bar e+2 and exit at the worst extreme of bar e+62 (paying both full one-minute
ranges) give IS -101.6 (t -0.76), VAL +0.6 (t 0.01). Real fills therefore matter: the demo stop rule caps slippage.
Concentration: LUNA 17.8 % of the IS + VAL net; 59 % of events fall on days with >= 5 events (t is clustered by day).

## Power at VAL size
VAL rate 257 trades / year -> ~470 HOLD trades; per-trade power 0.163 x sqrt(470) = **3.53 >= 3** (LIVE bar).
Day-clustered: 2.93. If HOLD's event rate is half of VAL's, per-trade power ~2.5. Expected HOLD t at VAL size ~2.9.

## HOLD implementation (declared before any HOLD data was read)
- Universe: `hold_univ.py` runs the same `xs.daily_universe` on all 886 perps in research/data/binance/perp_1d with
  the same `EXCL_BASE` filter, and also drops every symbol whose fapi exchangeInfo (fetched 2026-11-01, file hash
  below) `underlyingType` is not COIN: 16 HOLD-era TradFi perps (BZ, DRAM, EWY, INTC, KORU, MRVL, MU, NBIS, SAMSUNG,
  SKHYNIX, SKHY, SNDK, SNXX, SOXL, SOXS, SPCX). On 2020-24 days the universe equals stream F's (0 of 1,827 days differ).
- Data: data.binance.vision USDT-M 1m klines, monthly 2025-01..2026-09 and daily 2026-10-01..29 (`hold_pull.py`);
  funding from research/data/binance/funding, plus the public fapi fundingRate for the 21 symbols missing there
  (`hold_funding.py`). Entries 2025-01-01 00:00 .. 2026-10-29, exits before 2026-10-30 00:00 UTC.

## HOLD pass bar (all of; run once)
1. Net mean > 0 and day-clustered t >= 2.0.
2. Net > 0 at costs x1.5, with the entry two bars late, and with mean-OHLC fills.
3. 2025 and 2026 (to 10-29) each net > 0.
4. Reported, not gates: median, crash / spike split, share of net from the top 5 coins and top 5 days, n vs ~470.

Pass = LIVE candidate (research tier). Fail = dropped, no re-registration of neighbour cells (crash-only, T5 all,
H15) on this HOLD.

## If HOLD passes: demo, then live (user decides; no bot is written by research)
- Execution: stream 1m klines for the universe plus BTCUSDT; market order at the close of bar e+1 for a fixed small
  notional; market exit 60 minutes later; no stop (worst VAL trade ~ -5,000 bp: size for it); log model vs real fill
  prices, book spread at entry, and concurrent positions (crash days fire dozens of coins).
- Stop rule: stop if the cumulative net after 60 demo trades is < 0, or if the median slippage against the model
  entry is > 100 bp.
- Live rule: HOLD + demo pooled day-clustered t >= 2.5 at real fills.

## Code and data hashes (`python -m research.tools.prereg_hashes`, 2026-11-01 09:44 UTC)
- `research/results/portfolio/round64_parallel/F/code/univ.py` 9b56f6a4ecbd2a83
- `research/results/portfolio/round64_parallel/F/code/pull.py` fb61cae7c3b980d9
- `research/results/portfolio/round64_parallel/F/code/events.py` 81e007b5cd04adcb
- `research/results/portfolio/round64_parallel/F/code/report.py` 7e3b78d6ba5476c7
- `research/results/portfolio/round63_parallel/C/code/xs.py` a53fe02181166152
- `research/results/portfolio/round60_new_listings/code/listings.py` 1d728118b613023a
- `research/results/portfolio/round64_parallel/F/coord/hold/rule.py` 3811202d28136b95
- `research/results/portfolio/round64_parallel/F/coord/hold/check_isval.py` 7b6da21787a2fa17
- `research/results/portfolio/round64_parallel/F/coord/hold/hold_univ.py` 84ca87404734aec6
- `research/results/portfolio/round64_parallel/F/coord/hold/hold_pull.py` f5f8c60987059ed1
- `research/results/portfolio/round64_parallel/F/coord/hold/hold_funding.py` b05c70f9572f8630
- `research/results/portfolio/round64_parallel/F/coord/hold/hold_run.py` 39c8ee5c816342a3
- `research/data/binance_1m_wicks_hold/exinfo/exchangeInfo.json` c3fd74cc426f9637

## Data amendment before the run (2026-11-01 10:10 UTC, no HOLD return read yet)
The pull fetched 2,722 files; data.binance.vision returned 404 for the 2026-10-28 daily file of every symbol (55),
nothing else was missing (23 timeouts were retried). That day was filled from the public fapi /fapi/v1/klines
(1,440 bars each) by `coord/hold/hold_fill_1028.py` fdcfc2e0abdcc711. Rule and run code unchanged (hashes above).

## HOLD result
(appended after the single run)

Run once 2026-11-01 10:10 UTC (`coord/hold/hold_run.py`, output `coord/hold/hold_output_2026-11-01.txt`):

| HOLD 2025-01..2026-10-29 | n | net bp | t (day) | median | x1.5 | 2 bars late | mean-OHLC | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| T5 idio H60 | 2,080 | +41.8 | 1.17 | +43.6 | +28.8 (0.80) | +63.2 (0.99) | +53.5 (1.15) | +93.9 (n 449) | +27.5 (n 1,631) |

- Gate 1 (net > 0 and t >= 2.0): **fail** (t 1.17). Gates 2 and 3: pass. **Verdict: FAIL, dropped** as registered
  (no re-registration of crash-only, T5 all or H15 on this HOLD).
- Per-trade S 0.031 vs 0.163 in VAL: the edge per trade fell from +270 to +42 bp (~15 % of VAL size), while n was
  4.4 x the expected 470 (2026: 1,631 events, the top 40 filled with new, thin, volatile coins).
- Crash +50.8 bp (n 1,181), spike +30.0 (n 899). Top-5 coins (AKE, SIREN, ESPORTS, RAVE, LIGHT) = 102 % of the net,
  top-5 days = 134 %: the remaining edge is a few new small caps.
- Reading: liquidation wicks still revert on average, but in 2025-26 the reversal is mostly arbitraged within the
  first minute (the rule enters one full bar late); what is left is below the bar.
