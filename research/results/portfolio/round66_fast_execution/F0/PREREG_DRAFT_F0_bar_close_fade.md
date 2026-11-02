# PREREG DRAFT F0: fade 5 % idiosyncratic 1-minute wicks, entered at the first trade after the event bar's close, hold to the close of bar e+61 (FORWARD test)

Draft by stream F0, 2026-11-01 13:47 UTC (from `date -u`). Hypotheses [HYPOTHESES_F0.md](HYPOTHESES_F0.md) (12:24 UTC,
before any F0 return; addendum 1 changed only the pull mechanics); report [STREAM_F0.md](STREAM_F0.md). The
coordinator registers it (or not). **No HOLD (2025-01-01..2026-10-29) is used:** F's HOLD is known for the next-bar
entry, so this F-family rule can only be tested on data from **2026-10-30 00:00 UTC** onward.

## Rule (frozen; cell "E0 H60", the best IS t of the 6 declared cells, in its tradable form)
- Universe and events: exactly F's registered rule (round64_parallel/F/PREREG_F_wick_fade.md, "Rule"): top-40 USDT-M
  perps by mean daily quote volume d-30..d-1, listed >= 60 days, F's exclusions (EXCL_BASE, non-COIN underlyings);
  r = c_e / c_{e-1} - 1, |r| >= 5 %, not BTCUSDT, |r_BTCUSDT,e| <= 0.2 |r|; guard (bar e >= 10 trades and qv > 0;
  bar e+1 exists and its kline open is beyond the half-way point); one event per coin per 60 bars.
- Side: long after a crash, short after a spike (pooled).
- **Entry: the price of the first aggTrade with time >= close_e** (close_e = open time of bar e+1). Not the kline open:
  in 21.5 % of IS / VAL events the Binance 1m kline open of e+1 equals the last trade before close_e (the previous
  close), which is not a tradable post-signal price.
- Exit: close of bar e+61 (F's exit; last close within 5 min if missing, else dropped).
- P&L = side x (exit / entry - 1) - side x funding on stamps in (close_e, exit] - costs. Costs: taker 5 bp a side,
  entry half-spread 3h, exit h, h = 1 (ETH) / 3 (rank < 20) / 5 bp (rank 20-39): 22 / 30 bp round trip.

## IS / VAL (all 1,150 F events; aggTrades for 1,148)
| era | n | net bp | median | t (day) | S / trade | x1.5 | 5h stress | 1 s late (E1) | 3 s late (E3) | real fills $10k | years + |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IS 2020-21 | 380 | +319.5 | +353 | 4.90 | 0.249 | +306.8 (4.71) | +311.8 (4.79) | +296.2 (4.37) | +279.5 (3.89) | +289.8 (4.10) | 2 / 2 |
| VAL 2022-24 | 768 | +339.2 | +322 | 4.56 | 0.207 | +326.4 (4.38) | +331.4 (4.45) | +334.6 (4.49) | +335.6 (4.50) | +344.3 (4.89) | 3 / 3 |

Years +495 / +285 / +391 / +266 / +349. Random entries beaten 100 % (weak: random draws only lose the cost).
Max-over-6-cells IS t null p95 +0.14 vs real 4.81 (declared E0) / 4.90 (tradable E0). Crash / spike: IS +664 / -197,
VAL +445 / +175. Real fills = same-side taker VWAP for $10k at entry and at exit, fees only. For comparison, F's
registered e+1-close entry on the same events: IS +273.0, VAL +270.5.

## Forward size for power 3 (at VAL size)
- Per trade: (3 / 0.207)^2 = **209** trades. Day-clustered: 768 x (3 / 4.56)^2 = **333** trades. Registered size:
  **333 events**.
- Pace: F's registered HOLD count, 2,080 events in 22 months (94.5 / month): 333 events ~ **3.5 months**, i.e. data to
  about 2027-02-15. Evaluate at the first month end on which n >= 333 and >= 3 full months have passed; hard cap 12
  months (2027-10-29), evaluate whatever n then.
- Caution: power at VAL size assumes the VAL edge. F's HOLD at the e+1-close entry was +42 bp (t 1.17, 2,080
  events; a public fact from the brief). If the forward edge is of that order (S ~ 0.03-0.06), 333 events have power
  ~0.6-1.1 and a fail at 3.5 months would be "not detectable", not "absent"; the cap allows ~1,100 events.

## Forward implementation (declared now)
- Data: data.binance.vision USDT-M daily 1m klines (universe, events, exits) and daily aggTrades (entry) from
  2026-10-30; 1d klines for the universe; funding from the public fapi fundingRate. Same code paths as F (events.py /
  report.py selection) and F0 (ev.py, analyze.py entry logic). Missing daily files: fill from the public fapi
  klines as F's coordinator did for 2026-10-28; aggTrades missing -> event reported, excluded from the entry
  variants that need it, counted.
- A live / demo bot, if built, logs its own fills next to these public-data fills.

## Pass bar (all of; run once at the evaluation date) = F's HOLD bars
1. Net mean > 0 and day-clustered t >= 2.0.
2. Net > 0 at costs x1.5, at the 1 s-late entry (E1), and with $10k same-side taker VWAP fills at both legs.
3. Each half of the forward window (by event count) net > 0.
4. Reported, not gates: median, crash / spike split, share of net from the top 5 coins and top 5 days, n vs 333,
   measured first-second spread vs the 3h model.
Pass = LIVE candidate (research tier). Fail = dropped; no re-registration of neighbours (E1, E3, H15, crash-only) on
the same forward data.

## Code hashes (`python -m research.tools.prereg_hashes`, 2026-11-01 13:46 UTC)
- `research/results/portfolio/round66_fast_execution/F0/code/ev.py` d3fbda578aac36fe
- `research/results/portfolio/round66_fast_execution/F0/code/pull.py` 75107157fb6ba0cd
- `research/results/portfolio/round66_fast_execution/F0/code/analyze.py` 934ef60959f3f457
- `research/results/portfolio/round64_parallel/F/code/events.py` 81e007b5cd04adcb
- `research/results/portfolio/round64_parallel/F/code/report.py` 7e3b78d6ba5476c7
