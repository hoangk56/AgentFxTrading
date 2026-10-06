# Round 11, stream G: cross-sectional momentum / reversal at 1-5 day horizons

Written 2026-10-06 00:30 UTC, before any stream-G return was computed. The only data look so far was quote
coverage by clock time (which symbols have a bar at 07-20 UTC), used to pick the snapshot times below. HOLD
(2025-01..2026-09) stays closed: the shared panel stops at 2024-12-31; no other price file is opened past that date.
Eras: IS 2016-2021 (choices), VAL 2022-2024 (one check of the IS-chosen cell per family), PRE 2004-2015 (Dukascopy
H1, FX only) with criteria written here.

## Why this could escape the standing limits

- Round 8 tested relative value intraday (currency strength 4 h / 8 h, PCA residuals, pairs): real at mid (+1.7..+2.7
  bp) but about equal to the 1.2-1.5 bp FX round trip, because a 4-8 h move is only ~10-20 bp. Round 7 tested
  multi-week premia (momentum 1-12 m, carry, value): killed by IC's financing markup (2-9 %/yr). The 1-5 day horizon
  sits between: a 1-day long-short currency position moves ~50-80 bp (sd), cost ~1.5-3 bp per round trip per leg
  plus a few bp of swap markup per night. A real effect of a few bp per day would clear cost by a margin that the
  intraday effects never did.
- Breadth: one rebalance a day across 8 currencies gives ~250 trades a year (~430 in HOLD), so the power bar
  (per-trade net Sharpe x sqrt(HOLD trades) >= 3) needs a per-trade Sharpe of ~0.145, not the 0.3-0.4 of rare events.
- This construction (cross-sectional rank of 8 currencies / 8 indices / 6 commodities at 1-5 days, entered at a
  fixed liquid time) was never screened on IS/VAL or PRE. The removed lab's cross-sectional FX reversal used only
  2023-26 lab data (2025-26 is HOLD; it is not reused here). Rounds 7-8 tested single-symbol 1-5 day rules (Connors,
  TSMOM, carry), monthly cross-sectional momentum, and intraday cross-sectional reversal; none of these is this test.
- Not gotobi / Tokyo fix: snapshot times are 20:00 and 14:00 UTC, no calendar conditioning.

## Side, fixed from the literature before computing

- Currencies: **momentum** (long the past winner, short the past loser). Menkhoff, Sarno, Schmeling & Schrimpf
  (2012, JFE) find cross-sectional currency momentum strongest at the shortest formation they test (1 month), not
  reversal. Raza, Marshall & Visaltanachoti (2014, JIMF, "Is there momentum or reversal in weekly currency
  returns?") study 1-4 week formation in weekly currency returns and, as I recall the paper (abstract not
  retrievable from the APIs today), report momentum rather than reversal. Zaremba, Long & Karathanasopoulos
  (2019, JIFMIM, "Short-term momentum (almost) everywhere"): in equity indices, bonds, bills, commodities and
  currencies the most recent month's return predicts positively (no short-term reversal), strongest when
  cross-sectional return dispersion is high. The liquidity-provision reversal (Lehmann 1990; Nagel 2012) is a
  stock-level finding; Zaremba et al. report it does not carry over to asset classes. Round 8's intraday (4-8 h)
  currency-strength reversal is a different horizon and is not used to set this side.
- Equity indices: **momentum** (Zaremba et al. 2019 for country indices at 1 month; Moskowitz, Ooi & Pedersen 2012
  TSMOM positive at short look-backs).
- Commodities: **momentum** (Kwon, Kang & Yun 2019, FRL, "Weekly momentum in the commodity futures market": strong
  1-week momentum, no short-term reversal; Han 2023 JFM: momentum first, reversal later).
- The Nagel reversal is kept only as the declared competitor in G2 (G2n below): it is the exact mirror at mid, so it
  is counted in the cell total and reported, but the primary side is momentum.

## Common definitions

- Trading days: Mon-Fri. Snapshot time T: FX 20:00 UTC; indices and commodities 14:00 UTC (HK50 has no quote after
  ~17:00 UTC, so 14:00 is the latest liquid minute at which all 8 indices quote; commodities use the same time).
- Price at a minute = panel mid (bid+ask close /2) of the last bar at or before that minute (forward fill, look-back
  up to 3 days for signals and exits; never drop an exit).
- Formation: r_k(s, d) = log(mid at T on day d / mid at T on trading day d-k), k in {1, 3, 5}.
- Signal on data up to minute T; fill at the close of minute T+1 (latency stress: T+2; entry-1-hour stress: T+61);
  entry requires a bar within the 5 minutes up to the fill minute for every leg (known at fill time), otherwise
  that rebalance is skipped. Exit at the close of minute T+1 on the exit day (forward-filled quote).
- Holds (all <= 5 calendar days, the user's limit): h = 1 trading day (Fri -> Mon is 3 calendar days); h = 3
  trading days (<= 5 calendar days; run as 3 staggered bots, each rebalancing every 3rd trading day, so each bot
  holds <= 2 positions); h = W weekly (enter Monday, exit Friday at T+1; 4 trading days; one bot). A 5-trading-day
  hold would span 7 calendar days and is not allowed, W replaces it.
- Costs per leg (bp of that leg's price): 0.5 x actual spread at the fill minute + 0.5 x actual spread at the exit
  minute + commission (0.6 bp FX and metals; 0 indices, energies). Swap per rollover (specs.rollovers, 17:00 NY,
  triple Wednesday for FX / metals / energies, Friday for indices), using the FRED short rates in
  research/data/rates (no 2025-26 price file is read for this):
  - FX base/quote: long (r_b - r_q)/360 - m, short (r_q - r_b)/360 - m, m = 1.0 %/yr / 360 per side (round 7 D's
    fitted FX markups are 0.6-1.7 %/yr);
  - indices (currency of the index; HK50 uses USD): long -(r + 5.3 %)/360, short (r - 3.9 %)/360 (round 7 D fit);
  - metals (USD): long -(r + 1.0 %)/360, short (r - 0.5 %)/360 (round 7 D);
  - energies: -2.5 bp per night either side, XNG -4 bp (the brief).
- Trade = one rebalance's long-short book (1-2 legs). P&L in bp of one leg's notional. Main cost model closes and
  reopens at every rebalance; a "persist" variant (no exit/entry cost when the next book is identical) is reported
  as information only.
- Statistics: mid and net bp per trade; t clustered by entry UTC day (h = 1: one trade per day) and by ISO week of
  entry (binding for h = 3 and W, which overlap / are weekly); trades per year; per-trade net Sharpe; power per trade
  = Sharpe x sqrt(trades/yr x 1.73); power per week = Sharpe of weekly summed net P&L x sqrt(90); years positive.
- Controls: random-entry control = same entry days and holds, random ordered pair of distinct currencies (or
  symbols), >= 200 seeds, percentile of the rule's net mean; spread x1.5; fill +1 minute; entry +1 hour.
  Chance benchmark per family: per-week sign flips shared by all cells of the family (1,000 permutations), 95th
  percentile of the best |t_IS|, and the max of K independent normals.
- Selection: per family the IS-best cell by IS net t (week-clustered); VAL read once for that cell (all cells'
  VAL printed for information, but the verdict uses the IS-chosen cell).

## G1. G8 currency cross-section, momentum

Mechanism: short-horizon currency momentum (Menkhoff et al. 2012; Raza et al. 2014; Zaremba et al. 2019): slow
diffusion of order-flow information across currencies / trend-chasing speculative flow.
Rule: currencies USD EUR GBP JPY CHF CAD AUD NZD. Return of c vs USD from the 7 USD pairs (EURUSD GBPUSD AUDUSD
NZDUSD: + pair return; USDJPY USDCHF USDCAD: - pair return; USD = 0). Rank r_k(c) at 20:00 UTC; long the top
currency A, short the bottom B. Execution: if the pair A/B or B/A is one of the 10 panel pairs (7 USD pairs +
AUDJPY EURJPY GBPJPY), one position in it; otherwise two USD legs (long A vs USD, short B vs USD), whose USD
exposures cancel. Cells: k {1,3,5} x h {1,3,W} = 9. Equal notional per leg.

## G2. G1 conditioned on cross-sectional dispersion (causal VIX proxy)

No VIX series offline. Proxy D(d) = mean over the previous 20 trading days of the cross-sectional sd of the 8
currencies' 1-day (20:00 -> 20:00 UTC) returns, known at T on day d. "High" = D(d) above the 67th percentile of D
over the previous 252 trading days (a trailing percentile, so the regime drift of round 10's tercile pitfall is
partly absorbed).
- G2m (primary): momentum (G1's rule) only on high days (Zaremba et al. 2019: short-term momentum strongest in
  periods of elevated dispersion). 9 cells.
- G2s: momentum every day, lot 2x on high days, 0.5x otherwise (within the user's 0.5-2x). 9 cells.
- G2n (declared competitor): Nagel (2012) reversal (long the bottom, short the top) only on high days. Mirror of G2m
  at mid; 9 cells counted.

## G3. Cross-section within asset classes, momentum, one bot per class (2 positions)

Ranking on vol-adjusted returns z = r_k(s) / sd_IS(s), sd_IS = sd of the symbol's IS daily 14:00 -> 14:00 UTC log
returns (a constant per symbol from IS only); long the top z, short the bottom z; leg notionals weighted by
1/sd_IS(s) normalised so the class median weight is 1 (constant lots per symbol, no capital dependence). Snapshot
14:00 UTC. A symbol enters the cross-section on a day only if it quoted within 3 days; a rebalance needs >= 6 of
the 8 indices, all 6 commodities in G3c, all 3 in G3c2.
- G3i indices: AUS200 DE40 HK50 JP225 UK100 US30 US500 USTEC (2016-24). 9 cells (k x h).
- G3c commodities: XAUUSD XAGUSD XPTUSD XTIUSD XBRUSD XNGUSD; requires all 6 ranked, so effectively 2018-2024
  (IS = 2018-21). 9 cells.
- G3c2 cheap commodities: XAUUSD XAGUSD XTIUSD (drops the 18-46 bp XNG / 20-26 bp XPT spreads and the XBR duplicate
  of XTI); 2018-2024. 9 cells.
Total declared cells: G1 9 + G2 27 + G3 27 = 63.

## G4. PRE 2004-2015 check for G1 / G2 (criteria fixed now, before PRE is read)

Data: Dukascopy H1 bid closes of the 7 USD pairs (AUDJPY EURJPY GBPJPY for the cross legs; ask is junk early, not
used). The panel rule fills one minute after a 20:00 snapshot; H1 cannot do that, so in PRE the signal uses the
close of the 18:00 bar (19:00 UTC) and fills at the close of the 19:00 bar (20:00 UTC), exits at the 20:00 UTC price
h days later (1-hour latency, causal). Cost per leg: 0.5 x (IC 2016-17 median spread of that pair at 20:00 UTC) x 2
+ 0.6 bp; swaps from FRED short rates 2003-2015 (fetched to the scratchpad, cut at 2015-12-31) with m = 1 %/yr.
Applied to the IS-chosen cell of G1 and of G2m (whatever their VAL outcome).
**Pass** = PRE mid of the same sign as IS, PRE net mean > 0, and PRE week-clustered net t >= 1.5. Also reported:
years positive, 2004-07 / 2008-11 / 2012-15 sub-periods. A family that passes IS/VAL but fails this is rejected
(round 10's A7 lesson).

## Bars

As in the brief: LIVE (IS t >= 2.5, VAL t >= 1.5, both net > 0, >= 2/3 years positive, >= 95 % of random entries,
spread x1.5 and +1 min still > 0, power >= 3) / DEMO (IS t >= 2.0, VAL net > 0, >= 90 % of random entries). For the
overlapping (h = 3) and weekly cells the week-clustered t is the one checked against the bar.

## Additions

### DG (added 2026-10-06 00:33 UTC, after the G1-G3 IS/VAL numbers; diagnostic only, not a tradeable cell)
To read the sign and size of any cross-sectional predictability with more power than a top-vs-bottom book: each
day, the cross-sectional slope of the next-h-day mid return on the demeaned rank of the k-day return (8 currencies;
8 indices), i.e. a rank-weighted, dollar-neutral portfolio with weights (rank - 4.5)/sum|.|; mid only; k {1,3,5},
h 1; IS, VAL, and for currencies PRE (Dukascopy H1, the same 19:00/20:00 UTC timing as G4). It needs 7 positions,
so it is not a bot; it only says whether there is anything at mid to trade.

### G5 and DG2 (added 2026-10-06 00:34 UTC, POST HOC: after G1-G4 and DG were all null)
Why: DG weights by rank, so a nonlinear effect concentrated in large moves (Nagel's liquidity-shock reversal; or
overshooting momentum after large order-flow shocks) could hide in it.
- DG2 (diagnostic): Lehmann (1990) return weights, w_i = (r_k,i - mean r_k) / sum|.|, currencies, k {1,3,5}, h 1,
  mid only, IS / VAL / PRE. Reported with the momentum sign (a negative value means reversal).
- G5 (tradeable, momentum side as in G1): G1's top-vs-bottom book, k 1, only on days when the formation spread
  (top minus bottom k-day return) is above its trailing-252-trading-day 90th percentile; h {1, 3}. 2 cells. PRE
  criteria as G4 (same sign of mid, net > 0, week-clustered t >= 1.5). Being post hoc, it can at most become a
  watch item, not a pre-registration, unless it passes IS/VAL and PRE cleanly.
