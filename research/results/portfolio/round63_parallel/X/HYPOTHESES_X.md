# Round 63 stream X: VIX-futures roll and leveraged-ETP rebalancing flows (hypotheses)

Written 2026-10-31 16:11 UTC (from `date -u`), before any return was computed. Only one raw file (VX Jan 2016) was
opened, to read the column layout. Bars: BRIEF.md / research/PROMPT.md (LIVE / DEMO), unchanged.

## Mechanism
- VXX / VIXY / UVXY (long) and SVXY / XIV / SVIX (inverse) track the S&P 500 VIX Short-Term Futures Index: a
  constant ~1-month maturity mix of the first two VX futures. Over each roll period (from the Tuesday before one VX
  expiry to the Tuesday before the next) the index moves 1/N of its weight from the front (M1) to the second contract
  (M2) at every daily settlement. The net ETP position is long, so every business day the ETP hedgers sell M1 and buy
  M2 at or near the settlement (largely TAS). The schedule is in the prospectus: a dated, rule-driven flow.
- Two readings of the price pressure, with opposite holding periods, both with sides fixed here:
  - **Temporary impact** (flow-proportional): M1 settles too cheap vs M2 each day and recovers after the settlement.
    Liquidity provider: long M1 / short M2 at the settlement, out at the next open.
  - **Inventory impact** (holdings-proportional): a contract is pushed up while ETPs accumulate it as M2 and pushed down
    while they unload it as M1. The other side of the ETP book, short M1 / long M2 over the roll window, collects it.
    This is the same side as the term-structure carry (short front vol), which round 9 found to be beta, so it is graded
    beta-hedged (M2 leg sized to the IS slope of daily M1 changes on M2 changes) and against US500 and against windows
    not aligned to the roll calendar.
- Leveraged / inverse ETPs (UVXY 2x then 1.5x from 2018-02-27; SVXY -1x then -0.5x; TVIX, XIV) rebalance at the close
  by a dose Σ AUM·L(L-1)·r in the direction of the day's index move r. With daily data only this "into the close" push
  can't be seen (CFE files have Open, High, Low, Close, Settle; Close and Settle are both at the 15:15 CT close, no
  intraday). What can be tested is the reversal afterwards: fade the day's move from the settlement to the next open /
  next settlement on high-dose days.

## Data
- Cboe CFE daily files `cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_<expiry>.csv`, keyless;
  cdn.cboe.com robots.txt is an S3 AccessDenied (no file). One file per monthly expiry, Jan 2013 .. Feb 2025 contracts
  (the Feb 2025 contract is M2 in late Dec 2024). **Rows with Trade Date >= 2025-01-01 are dropped at parse** and never
  printed. Weeklies ignored. Expiry dates = the last trade date in each file (cross-checked with the Wednesday 30
  days before the next month's 3rd Friday).
- ProShares UVXY / SVXY / VIXY AUM (round 34 E download, raw in its old scratchpad): copied, cut at < 2025-01-01, into
  research/data/cboe_vx/proshares/. VXX (iPath), TVIX, XIV are missing: the roll dose is understated (VXX is the
  biggest long ETP), the LETF dose is understated before 2018 (XIV, TVIX).
- US500 daily from the IC M1 cache (2016+) for the beta check. Cash: research/data/rates/DFF.csv (only if capital is
  tied; futures margin is small, so P&L is reported per spread in points and $, not as excess over cash).

ETP pair on date t: M1 = the earliest expiry E with t <= the business day before E (the Tuesday), M2 = the next one.
On expiry Wednesday the new pair starts. Roll fraction per day = 1 / (business days in the roll period).

## Eras
PRE 2013-2015, IS 2016-2021, VAL 2022-2024; HOLD (2025+) never loaded.

## Rules and grid (8 cells, sides fixed)
| cell | rule | entry -> exit | trades / yr |
|---|---|---|---|
| A1a | short M1 / long M2, 1:1, held over the whole roll period | settle on expiry Wed -> settle on Tuesday before next expiry | 12 |
| A1b | same, beta-neutral: short 1 M1 / long h M2, h = IS OLS slope of dM1 on dM2 (fixed from IS) | same | 12 |
| A2a | long M1 / short M2 every roll day (temporary impact) | settle t -> open t+1 | ~250 |
| A2b | same, only days in the top tercile of roll dose (ETP contracts rolled today / OI of the pair; IS tercile threshold fixed) | settle t -> open t+1 | ~80 |
| B1a | fade the day's index move (position against sign r_t in the index-weighted M1/M2 mix), top decile of LETF dose | settle t -> open t+1 | ~25 |
| B1b | same, top quintile | settle t -> open t+1 | ~50 |
| B2a | fade, top decile | settle t -> settle t+1 | ~25 |
| B2b | fade, top quintile | settle t -> settle t+1 | ~50 |

LETF dose_t = Σ_i AUM_i,t-1 · L_i(L_i - 1) · r_t / (dollar OI of M1 + M2), with r_t the return of the index-weighted
mix; thresholds on |dose| are IS quantiles, applied unchanged to VAL.

## Costs (stated)
VX tick 0.05 = $50 per contract (multiplier $1000). Bid-ask one tick on M1 and on M2; a crossed round trip costs one
tick per leg. Commission $2 per contract per side.
- Calendar spread round trip (2 legs): 2 x 0.05 + 4 x $2 = 0.108 points = $108.
- Outright round trip (1 contract-equivalent): 0.05 + $4 = 0.054 points.
- A1: one spread round trip per window (exit of the old pair and entry of the new one counted as separate trades).
  A1b scales the M2 leg's cost by h.
- A2 base: crossed both ways (0.108). Variant stated, not the base: entry by TAS at the settlement (no spread),
  exit crossed at the open (0.05 + $8 = 0.058).
- Checks: costs x1.5, and one step late (A1: enter one settlement later; A2 / B: exit one session later, i.e. at
  open t+2 / settle t+2).

## Benchmarks (c)
- A1: (i) 500 draws of windows of the same length starting at random business days (pair = ETP pair on the start
  day), same sides; the rule must beat >= 95 % (LIVE) / 90 % (DEMO) of draw means; (ii) alpha vs US500 daily
  (NW t); (iii) the mechanism predicts larger returns in windows with a larger ProShares net ETP share of OI (above vs
  below the IS median), reported, not a pass condition.
- A2b / B: 1000 draws of the same number of days at random from the era's eligible days, same sides (for B the side
  is "fade the day's move", so the draw tests whether high dose matters beyond the generic one-day reversal);
  A2a (all days): random-sign books.
- Max-over-cells null: the best t over the 8 cells under sign-randomised (A) / random-day (B) draws.

## Power arithmetic (before data)
LIVE needs net Sharpe per trade (VAL size) x sqrt(HOLD trades) >= 3; HOLD ~1.8 years.
| cell | HOLD trades | per-trade Sharpe needed | prior | reachable bar |
|---|---|---|---|---|
| A1 | ~21 windows | >= 0.65 per window (annual ~2.25) | short-front calendar carry has an annual Sharpe ~0.5-1 with crash tails, and is beta | DEMO at most |
| A2 | ~440 days | >= 0.143 per day | settle->open spread moves ~0.1-0.2 pt sd; roll impact plausibly 0.01-0.03 pt vs 0.108 cost | none expected (cost ~5-10x the plausible effect) |
| B top decile | ~45 | >= 0.45 | round 34: VIX LETF dose 0.08-0.36 % of VX OI, small | none / DEMO |
| B top quintile | ~90 | >= 0.32 | same | none / DEMO |

Expected outcome: no LIVE; A1 may show the known carry but is expected to fail as alpha once beta-hedged.
