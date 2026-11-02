# PREREG A2-D5L: long the Binance perp 5 s after an Upbit KRW-listing notice, exit at the KRW open (DEMO tier)

Registered 2026-11-01 13:24 UTC (from `date -u`) by the coordinator, before any 2025-26 notice body, listing time or
price for this rule was read. Draft with full IS / VAL tables and checks: [PREREG_DRAFT_A2_D5L.md](PREREG_DRAFT_A2_D5L.md)
(stream A2, 12:22 UTC); hypotheses [HYPOTHESES_A2.md](HYPOTHESES_A2.md) (12:04 UTC, cell-choice rule declared there:
best IS t among d >= 5 cells). HOLD 2025-01-01..2026-10-29 is opened once by `coord/hold/hold_run.py`.

## Rule (frozen)
Event: an Upbit notice that puts a coin on the KRW market (stream A's builder; no stablecoins, no BTC / USDT-only, no
re-listings), coin's Binance USDT-M perp traded >= 7 days before N. N = `first_listed_at` (whole seconds, KST -> UTC),
L = first Upbit KRW 1m candle. Long the alt perp / short BTCUSDT perp in equal notional at each leg's first aggTrade
>= N + 5 s; exit each leg at its first aggTrade >= L. Costs 20 bp + declared slippage (half the median 1 s range in the
60 s after each fill, 4 fills) + real funding.

## IS / VAL (stream A2; reproduced exactly by `coord/hold/check_isval.py`)
IS n 12 (9 notice days) +1,296.1 bp, t 3.07; VAL n 32 (32 days) +519.9, t 1.75; 5 / 5 years positive; random 100 %;
x1.5 +477.5 (VAL), d 10 s +454.1; aggressor-side fills +515.5 (t 1.73); worst price of the 1 s after entry +373.4 (t 1.34).
LIVE bars pass except power: VAL Sharpe per event 0.309 x sqrt(92 expected HOLD events) = **2.97 < 3**, so **DEMO**.
Known before registration (public, not returns): K2's registered HOLD had 92 Upbit KRW listings of coins with a
Binance perp; K2's HOLD result concerns L + 1 h .. L + 73 h, not the N -> L window traded here.

## HOLD implementation (declared)
- `hold_events.py`: titles from stream W's notice list (2025-01-01..2026-10-29 UTC, A's keys and filters), bodies from
  W's cache or api-manager.upbit.com (>= 1.5 s), A's events.py with the window moved and perps.CUT = 2026-10-30,
  L by A's pull_first logic (Upbit 1m candles); L fallbacks as A2's events.py (sibling L, else stated + 5 min, else
  drop); rows with L < N dropped. Events whose notice body format is not parsed by A's markets() are missed (reported).
- `hold_pull.py`: data.binance.vision daily aggTrades (A2's fetch / parse), windows N - 10 min..N + 30 min and
  L - 10 min..L + 5 min, every UTC day touched.
- `hold_run.py`: `core.grade` (A2's analyze.trade + verbatim checks.fill / trade).

## HOLD pass bar (DEMO), stop and promotion
- Pass: HOLD net > 0 per trade and day-clustered t >= 1.0. Fail: drop the seconds-level reaction family for good.
- Reported: n, notice days, aggressor-side and worst-of-1 s fills, x1.5, d 10 s, years, share of events whose burst
  starts after N + 5 s, median path at +2 / +5 / +300 s.
- Promotion to LIVE (unchanged rule): HOLD + forward demo pooled t >= 2.5 on real fills, with notice detection
  <= 3 s after N on >= 80 % of live notices (forward capture test). The bot (Upbit notice polling >= 1.5 s or Upbit's
  private feed, Binance USDT-M account) is a user decision.

## Hashes (`python -m research.tools.prereg_hashes`, 13:24 UTC)
- `research/results/portfolio/round65_retail_venues/A2/code/analyze.py` 01c530f8cd5d1884
- `research/results/portfolio/round65_retail_venues/A2/code/checks.py` 7f332ed6be5c300c
- `research/results/portfolio/round65_retail_venues/A2/code/pull.py` 5c6530d4d0ceb16a
- `research/results/portfolio/round65_retail_venues/A2/code/net.py` c5a3928cd5013717
- `research/results/portfolio/round65_retail_venues/A/code/events.py` 5cf8c452116e5cb2
- `research/results/portfolio/round65_retail_venues/A/code/perps.py` 43f047f8d6e185bb
- `research/results/portfolio/round65_retail_venues/A/code/pull_first.py` ad8eda4f80f5e475
- `research/results/portfolio/round65_retail_venues/A2/coord/hold/core.py` 2342f619ac84ab51
- `research/results/portfolio/round65_retail_venues/A2/coord/hold/check_isval.py` 6216f27d733fd9da
- `research/results/portfolio/round65_retail_venues/A2/coord/hold/hold_events.py` 812316f8099dead8
- `research/results/portfolio/round65_retail_venues/A2/coord/hold/hold_pull.py` 0308eda72dacd0d3
- `research/results/portfolio/round65_retail_venues/A2/coord/hold/hold_run.py` 21d13adaef6b39b2

## HOLD result
(appended after the single run)

Events built 2026-11-01 13:25-13:34 UTC (`hold_events.py`: 91 HOLD events vs 92 expected); aggTrades pulled 13:34-13:48 UTC
(178 / 178 files, no missing day). Run once 2026-11-01 13:49 UTC (`hold_run.py`, output
`coord/hold/hold_output_2026-11-01.txt`):

| HOLD 2025-01..2026-10-29 | n (days) | net bp | t (day) | median | x1.5 | d 10 s | aggressor fills | worst of 1 s | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|
| A2-D5L | 91 (87) | **+780.3** | **3.11** | +17.8 | +716.4 | +275.9 | +780.6 (t 3.11) | +540.0 (t 2.25) | +1,233.6 | +274.2 |

- **DEMO bar (net > 0, t >= 1.0): PASS.** A2-D5L is a DEMO candidate that passed HOLD with t 3.11.
- Descriptive (not gates, computed after the run on the same trades): win rate 51 %, top-5 events = 54 % of the sum
  (largest +9,704 bp), mean without the top 5 +383.5, 10 % trimmed mean +426.7, minimum leave-one-out t 2.91.
- The +2 % burst started before N + 5 s in every HOLD event (competition is fast); the median path is +1,387 bp at
  +2 s, +1,629 at +5 s and +1,624 at +300 s, so the median trade is flat after entry and the mean comes from coins that
  keep rising into the KRW open. Speed matters: entering at +10 s keeps only +276 bp.
- Tier stays **DEMO** (registered power 2.97 < 3; the bar is not lowered). Promotion to LIVE as registered: HOLD +
  forward demo pooled t >= 2.5 on real fills, with notice detection <= 3 s after N on >= 80 % of live notices. HOLD
  alone is t 3.11, so promotion depends only on whether a bot can see the notice within ~3 s and fill near the
  modelled price: a user decision (polling api-manager.upbit.com >= 1.5 s, or Upbit's private feed; Binance USDT-M).
- Request log note: the 4 requests in research/data/upbit_hold_a2/requests.log before 13:24:52 UTC are fapi fundingRate
  calls for 2023-24 (IS / VAL) made by `check_isval.py`, not HOLD data.
- Note found later (round 66 A5): stream A's `perp_for` checks the 7-day age with day-precision daily klines, so a
  perp 6-7 days old can pass (ARB 2023-03-30, 6.42 d, a VAL event at -42 bp). The hashed code is the registered rule;
  the text ">= 7 days" means "first daily kline <= N - 7 d", as implemented.

## Public-data forward log (supplementary; added 2026-11-01 14:55 UTC)
`coord/forward/fwd_a2.py` (sha 3d74943ef23f8597) runs the same pipeline on notices from 2026-10-30 (re-fetched list,
fapi 1d perp-age check because local perp_1d ends 2026-10-30) and appends each new graded event to
research/data/upbit_fwd_a2/fwd_log.csv. Checked against the HOLD event list on 2026-10-24..29 (same 2 events) before
the first forward run. First slice (2026-10-30): 0 events. This log does not replace the registered promotion test
(real fills, detection <= 3 s); it can be pooled with HOLD as public-data evidence. Re-run any time.
