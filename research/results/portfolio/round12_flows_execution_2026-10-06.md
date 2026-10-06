# Round 12: hedge-rebalancing flows, other executions and conditions for sub-cost effects, literature 2018-2026 (2026-10-06)

The user asked (`research/PROMPT.md`) to keep searching until a LIVE candidate passes its holdout. Four streams ran in
parallel from one brief ([round12_flows_execution/BRIEF.md](round12_flows_execution/BRIEF.md)), each writing its
hypotheses with UTC times before the numbers (`HYPOTHESES_I/J/K/L.md`) and a write-up (`STREAM_I/J/K/L.md`), all in
[round12_flows_execution/](round12_flows_execution/).

| stream | direction | why it might escape the limits |
|---|---|---|
| I | month-end hedge rebalancing at the WM/R 16:00 London fix, USD side from month-to-date equity returns (Melvin & Prins 2015) | earlier month-end tests had no equity signal; a flow whose side and size are predictable from public data is what made gotobi work |
| J | other executions of the real-but-sub-cost effects (spread-timed minutes and seconds, passive limits, one trade through several flows, lot by forecast, cheaper twin symbol) | asked for by the user; cost, not the mid edge, kills these effects |
| K | literature 2018-2026 on intraday / short-horizon flows, 30 papers mapped, 6 untested families screened | rounds 7 and 8 covered 2010-2026 broadly; this pass targeted dealer hedging, benchmarks, expiries, post-2020 structure |
| L | flow-size conditions derived from each mechanism (calendar dates the flow's owners must trade on, prior moves they respond to) | the effects are real at t 4-13; round 10 E got 1.5x from volatility; 3x is needed |

## Answer

**No LIVE candidate.** Three rules met the DEMO numbers on IS/VAL. The lead reproduced each one with independent
code, registered it with code hashes, and opened HOLD (2025-01..2026-09) once per rule:

| candidate | IS net / t | VAL net / t | HOLD net / t | verdict |
|---|---|---|---|---|
| I: month-end post-fix USD reversal after a large US equity month (EURUSD, USDJPY, GBPUSD, 16:00-17:00 London) | +6.77 bp / 3.79 | +1.68 / 0.84 | **-0.23 / -0.08** (36 trades) | **rejected** |
| J5c: short AUDUSD 09:45-10:00 Sydney, only when 10:00 Sydney is outside IC's post-rollover hour | +0.44 / 2.54 | +0.76 / 3.77 | **-0.25 / -0.99** (314 trades) | **rejected** |
| L4-G-d: gold follows the day's move into the COMEX settlement (13:15-13:30 ET) on top-decile move days | +3.48 / 3.19 | +2.11 / 1.70 | **+1.68 / 0.37** (46 trades) | **DEMO candidate**, weak |

Registrations, code and HOLD outputs: [PREREG_I_month_end_post_fix_usd.md](round12_flows_execution/PREREG_I_month_end_post_fix_usd.md),
[PREREG_J_sydney_aud_offroll.md](round12_flows_execution/PREREG_J_sydney_aud_offroll.md),
[PREREG_L_gold_settlement_bigday.md](round12_flows_execution/PREREG_L_gold_settlement_bigday.md),
`round12_flows_execution/prereg_code/`.

| tier | candidates |
|---|---|
| LIVE | none |
| DEMO | **L4-G-d gold settlement big days**: passed its registered HOLD rule (net > 0), but HOLD t is 0.37 and the mean rests on three trades (2.5 % winsorised +0.23 bp). Stop and promotion rules are in the registration (promotion: HOLD + demo pooled t >= 2.5). No cBot written, nothing deployed |

### The DEMO candidate in brief (for the user's decision)
- Rule: on NYSE business days, z = gold's move from the previous 13:30 ET mid to 13:14 ET divided by the sd of the
  last 60 daily settlement-to-settlement returns. If |z| is above the 90th percentile of the last 250 days, enter
  XAUUSD at 13:15:00 ET in the direction of z, exit at 13:30:00 ET. About 25 trades a year, 15 minutes each.
- Mechanism: leveraged and inverse gold funds and settlement-benchmarked orders trade in the day's direction at the
  COMEX settlement, in proportion to the day's move (Cheng & Madhavan 2009); platinum, without such funds, reverses.
- Weaknesses: silver (the twin) flips sign in VAL; most of the edge is on short trades; stream J found that round 6's
  settlement momentum is mostly continuation in the first minute after the signal, and the HOLD "+1 minute" version
  is +0.55 bp; HOLD alone gives almost no evidence.
- Correlation with C3: daily +0.015, monthly -0.14.

## I. Month-end equity-hedge flows at the WM/R fix
- The paper's own effect (USD into the fix, signed by relative month-to-date equity returns) is absent in 2016-21:
  -1.14 bp (t -0.54). Only the reversal after the fix is there, and only on the US signal.
- 72 mid cells + 27 basket cells. The best basket (gated at the IS median |S&P month-to-date| of 2.45 %) had IS gross
  t 4.17 against a permutation 95th percentile of 3.11. The same rule on ordinary days had the opposite sign in IS.
- It decayed: +6.8 bp per trade in IS, +1.7 in VAL, -0.2 in HOLD, as round 3's unconditional F1 decayed from 2021.

## J. Other executions of the sub-cost effects
- 70 declared cells; every spread-timed, passive and multi-flow execution is net < 0 in IS. The best non-post-hoc
  cell is J3c (hold a big-up settlement day's gold long to the next SGE auction): +7.83 (t 2.30) IS, -0.26 VAL.
- **The break-even cost of each effect, against the cost the LIVE bar would need** (round trip, bp, IS / VAL):
  - SGE auction: break-even 0.92 / 0.70; LIVE needs 0.27 / 0.06.
  - Sydney pre-leg: break-even 1.65 / 1.48; LIVE needs 1.10 / 1.03.
  - Sydney post-leg: break-even 1.29 / 1.44; LIVE needs 0.58 / 0.75.
  - ECB fix: break-even 0.73 / 0.85; LIVE needs < 0 / 0.03.
  - SGE, Sydney post-leg and ECB need less than the 0.6 bp commission alone, so no execution at IC reaches LIVE.
  - Gold settlement, MOC, AUS200 and BTC have gross power of only 1.2-2.2, so they fail LIVE even at zero cost.
- **Passive limit orders cannot capture the spread** under a trade-through fill rule. They fill on the days the
  move runs against the trade, and take-profits cut off the tail of the move. Changing to touch fills moves the net by
  0.1 bp or less.
- **The Sydney V's high cost is a clock clash.** In the northern winter, 10:00 Sydney is 18:00 New York, the last
  minute of IC's wide-spread hour after the rollover: the round trip costs 2.8 / 5.2 bp, against 1.2 / 1.0 at
  19:00-20:00 New York. Rounds 4, 6 and 10 pooled both seasons. J5c traded only the cheap season; the cost filter
  worked in HOLD (0.73 bp), but the dip shrank to +0.48 bp.

## K. Literature 2018-2026
- 30 papers mapped. 9 need data the repo lacks; most of the rest were tested or near-tested in rounds 3-11. 123
  cells across 6 families: FX intraday momentum into the closes, opening-range reversal (0DTE), the Deribit 08:00 UTC
  expiry, CME BTC expiry, crude and metals intraday momentum.
- No family's best IS |t| on the registered side beats its chance 95th percentile. FX runs the other way: USD pairs
  reverse into the London close in IS (USDCHF t -4.2), and this is gone in VAL.
- Closest lead: fading BTC's 07:00-08:00 UTC move over 08:01-09:00 on Fridays (the weekly Deribit expiry). Mid
  +20.6 (t 2.34) IS / +11.2 (t 3.13) VAL, but IC's 2018-21 BTC cost (11.6 bp) leaves IS net t 1.03; power 1.7 even
  at today's cost. Not registrable.

## L. Conditions that scale the strong flows
- 42 cells, all 7 base effects reproduced. Scaling found: SGE auction 2x after gold fell while China was shut (still
  below cost); the Sydney V at most 1.7x (Mondays, but the spread rises too); the ECB fix has the opposite sign at
  month-end; AUS200, USTEC MOC and USDCNH conditions fail IS t or VAL.
- Gold settlement momentum on top-decile move days scales 7x / 12x at mid and became the DEMO candidate above.
  Silver's top decile is +11.8 (t 4.2) IS and -4.8 (t -2.2) VAL.

## What this says
- **All three candidates decayed in time, from IS to VAL to HOLD.** I went +6.8 → +1.7 → -0.2 bp per trade, J5c's mid
  dip +1.54 → +1.53 → +0.48, and L4 +3.5 → +2.1 → +1.7 with t falling to 0.4. Every flow anomaly found in twelve
  rounds that cleared IS/VAL has weakened in 2025-26, except gotobi. A rule whose VAL effect is already well below its
  IS effect should be expected to fail HOLD; the next rounds should require the effect not to shrink from IS to VAL,
  rather than only VAL > 0.
- **The execution route is closed at IC's costs.** For the strongest sub-cost flows, LIVE would need a round-trip
  cost below the 0.6 bp commission. Passive orders do not help, because the fills are adversely selected.
- **Selection by flow size works but is not enough.** Mechanism-derived conditions roughly double a flow (SGE, Sydney)
  or select large-move days (gold settlement). On the selected days the per-trade Sharpe rises, but the trade count
  falls, so power stays below 2.
- **Holdout budget.** HOLD was opened three times this round, on DEMO-tier candidates with expected HOLD t of 0.5-2.9.
  The 2025-01..2026-09 holdout is now even less clean. New data after 2026-09-24 is the only clean test left.

## Directions that need the user's decision
1. **Demo of L4-G-d** (gold settlement big days), under its registered stop and promotion rules. It needs a cBot
   (not written).
2. **Dukascopy XAUUSD M1 2004-2015** for a PRE check of L4-G-d (~300 events; only H1 is local). One daily S&P 500
   series 2003-15 for a PRE check of rule I (already rejected; low value now).
3. **New data after 2026-09-24** (IC cache pull or Dukascopy), as the only clean holdout left.
4. **A commission-free FX/metals cost structure**, which would put the SGE auction, the Sydney post-leg and the ECB
   fix within reach of LIVE. Testing it needs another broker's quote history.
5. Paid or new external data that would condition the leads directly:
   - Deribit open interest / gamma history (Tardis, Laevitas), for the K4 BTC expiry lead;
   - leveraged gold and silver fund AUM and creations (UGL/GLL/AGQ/ZSL), for L4;
   - SGE premium and withdrawals, for the SGE auction;
   - the S&P 500 dividend-payment calendar (Hartzmark & Solomon 2022);
   - BTC/ETH spot ETF flows from 2024, which only have usable samples after 2026-09.
6. **DTCC FX-option trade reports** with strikes, for option pinning: public only from 2024-12 (earlier files are in
   S3 Deep Archive), which is inside HOLD.

## Pitfalls (for the next round)
- **Random-entry controls for data-dependent sides.** If the side is set by data up to minute t, a random window
  before t contains the move that set the side. Recompute the side at the random time, or sample only after the
  signal. Stream L's first control showed a VAL null of +1.67 bp ("beats 61.8 %") because of this.
- **Seasonal cost clashes with IC's rollover hour.** The wide-spread hour after 17:00 New York is fixed in New York
  time, so venue times in other zones move in and out of it with each DST change. Split by New York clock time before
  pooling seasons.
- **Bar-start vs bar-end minute labels.** Round 11's USTEC MOC numbers use bar-start labels; read as bar-end, the
  same cell gives +0.38 instead of +1.55 bp.
- **First-minute continuation.** Check every momentum-into-a-benchmark rule with both fills one minute late; the gold
  settlement edge is mostly in the minute after the signal.
- **Decay.** Compare IS and VAL effect sizes, not only signs (see "What this says").

## Process and disclosures
- HOLD was loaded only by the lead's registered scripts, once per candidate, after registration (hashes in each
  PREREG file). The streams never loaded it: the panel ends 2024-12-31 and their M1/tick loads were cut at
  2025-01-01.
- Every candidate was picked with VAL in view (disclosed in each draft and registration); the HOLD rules were the
  DEMO rules: reject if net per trade <= 0.
- Network: literature APIs (OpenAlex, Semantic Scholar mostly rate-limited, SSRN unreachable; for two SSRN-only
  papers the side came from the title), the Melvin & Prins working paper (ECB workshop PDF), one practitioner
  replication (its sample overlaps HOLD; used only for sides and windows), DTCC S3 header probes. No prices were
  downloaded.
- Scripts and outputs of the streams stay in the session scratchpad (listed in each STREAM file). The registered
  scripts and their outputs are in `round12_flows_execution/prereg_code/`. Nothing in `research/` code was edited.
- Correlation with C3 (IS + VAL): I -0.05 daily / +0.01 monthly; J5c +0.004 / -0.08; L4-G-d +0.015 / -0.14.
