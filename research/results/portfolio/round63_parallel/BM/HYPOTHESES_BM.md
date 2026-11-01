# Stream BM: is B's registered cheap-basis rule executable after the hourly close? (round 63)

Written Sat Oct 31 17:34:37 UTC 2026 (from `date -u`), before any 1m kline was requested. Coordinator task: a
robustness check of the already registered and HOLD-opened rule k100_H24_cheap (B/PREREG_B_cheap_basis.md) on all
three eras (IS 2020-21, VAL 2022-24, HOLD 2025-01-01..2026-10-29). HOLD for B is open (coordinator, 15:50 UTC), so this
stream reads HOLD trades by explicit instruction. No new selection, no parameter change: the trade list, exits,
funding, costs and carry are B's.

## Question
B enters at the 1h open of h+1, i.e. the first trade printed after the signal hour's close. On Binance that open equals
the previous close only 32-37 % of the time (BY), but it is still the first print after the dislocated close. Bybit
(BY) showed the edge decays within 1-5 minutes. Is B on Binance a convergence trade a bot can take after reading the
hourly close, or a latency race?

## Mechanism (two readings, fixed before data)
- Convergence: the perp trades cheap to spot because of a forced flow (liquidations / squeeze, deeply negative funding);
  the gap closes over hours, plus funding received. Then the edge survives a few minutes of delay.
- Latency race / stale prints: the signal-hour close and the next open are prints in a thin book; the "gap" is partly
  bid-ask bounce and is repaired within a minute by faster arbitrageurs. Then the edge is gone by +1..+5 min.

## Trade list (step 2)
B's frozen code: `B/code/hold_run.py` harness (imports `basis.py` / `universe.py` unchanged, overrides only
universe.END, basis.CUT and ERAS['HOLD']), `load()` then `simulate(coins, 100, 24, -1)`, unchanged. Hashes verified
17:34 UTC with research.tools.prereg_hashes: basis.py 46a5f647e1fc33f2, universe.py e4a9ae6a1a841feb, pull.py
6234ca2300a998c8 (= PREREG). Expected n: IS 303, VAL 336 (extended data), HOLD 429. All trades are used (no subsample)
unless the pull exceeds ~60 min, in which case a declared seeded random subsample of >= 150 per era.

## Data (step 3)
For each trade, T = start of hour e (= signal hour close), X = start of exit hour x. Perp: fapi.binance.com/fapi/v1/
klines interval 1m; spot: api.binance.com/api/v3/klines interval 1m, window [T - 3 min, X + 20 min], one request per
leg when it fits (perp limit 1500, spot 1000; spot holds > ~16 h need 2). If a spot pair is delisted (HTTP 400 invalid
symbol), fall back to data.binance.vision daily 1m zips. Perp symbol / spot symbol / factor as in B. One process per
host (2 processes), >= 0.3 s between requests, watch X-MBX-USED-WEIGHT-1M (pause above 1,800 on fapi / 4,500 on spot),
back off on 418 / 429 / 503, stop on 403. requests.log (time, URL, status, bytes) in research/data/binance_basis_1m/.

## Re-pricing (step 4, fixed)
- Delay k in {0, 1, 2, 5, 15} minutes. k = 0 is the open of the 1m bar starting at T (= B's 1h open; a reproduction
  check, must match B's entry price on almost all trades). Delay k: both legs enter at the open of the 1m bar starting
  at T + k min. If a leg has no bar at that minute, use the open of its first bar within the next 5 minutes, and if
  none the trade is "missing at k" (counted and reported, not imputed).
- Exit unchanged: open of the 1m bar starting at X (first bar within 5 min if missing); expected to equal B's 1h open.
- Funding exactly as B (stamps in (e, x] by hour index; delay does not change the set: the stamp at T is already
  excluded in B). Costs as B (30 bp fees + 4 x 3 / 5 bp half-spread by rank) and carry as B (hours e..x). So only the
  price leg changes: price_k = -(Sx / Se_k - 1) + (Fx / Fe_k - 1).
- Spread proxy: |perp open(T) - perp close(T - 1 min)| / perp close(T - 1 min), same for spot (median, p75, p90 per era).
- Gap closure: d_h = b_h - m_h (B's signal deviation, < -100 bp). Basis at minute k: b_k = ln(Fo_k / (fac x So_k)).
  Share of trades with b_k - m_h >= d_h / 2 (half the gap already closed) at k = 0, 1, 5.

## Report (step 5)
Per era and delay: n, net mean / median (bp), day-clustered t (B's cl_t), win rate; at +5 the split price-perp-leg /
price-spot-leg / funding / costs / carry; also x1.5 costs at +5 (information).

## Decision rule (fixed now)
- "Executable at +5 min: YES" iff at k = 5 the net mean is > 0 in IS, VAL and HOLD and the HOLD day-clustered t >= 2.0.
  Otherwise NO.
- Also report the share of the k = 0 net kept at k = 5 per era; if < 50 % in two of three eras, call it "mostly a
  latency race" even when YES (the demo would then be sized on the +5 number, not on B's).
- If the funding leg alone carries the +5 result (price leg <= 0 at +5), say so: then the executable edge is "long a
  perp in deeply negative funding, hedged", not basis convergence.

## Power arithmetic (BRIEF)
HOLD 429 trades on 206 days; at k = 0 the per-day SR is ~1.0 (t 14.4 / sqrt(206)). A YES needs HOLD t >= 2, i.e. a
per-day SR >= 2 / sqrt(206) = 0.14, about 1/7 of the k = 0 strength. IS (303 trades, few days; t 2.46 at k = 0) has
little power: IS at k = 5 is mainly a sign check. LIVE is not reachable whatever happens (tier fixed at DEMO by IS t).

## Expectations (stated, not graded)
BY's Bybit result suggests IS dies by +5 min and VAL keeps a decaying part. Prior: P(YES at +5) ~ 0.5, because ~59 %
of HOLD net is funding received, which delay does not touch (~+126 bp funding vs ~-52 bp costs+carry per trade).
