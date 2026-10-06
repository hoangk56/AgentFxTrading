# Round 12, stream J: other executions of the real-but-sub-cost effects

2026-10-06. Hypotheses (written before their numbers; post hoc additions marked):
research/results/portfolio/round12_flows_execution/HYPOTHESES_J.md. HOLD (2025-01-01 onwards) was never loaded: the
panel ends 2024-12-31, every tick load stopped at 2024-12-31, and the C3 trade list was read with its HOLD rows skipped.
Costs: actual tick (or panel) spread at each fill + 0.6 bp round-trip commission for FX and gold, 0 for indices and
BTC. Passive fills: trade-through only (buy limit fills when the ask goes below it, at the limit price), limit prices
on the symbol's price grid. t is clustered by UTC day.

## Answer
- **No execution turns any of the eight effects into a LIVE candidate.** Spread-timed minutes (J1, J1b), resting
  limits (J2), holding through several flows (J3), lot 0.5-2x (J4) and cheaper symbols (J5a/b) leave every effect
  net <= 0 in IS or VAL. The only exceptions are cells with IS t <= 1.14, or cells that cannot be traded (the
  hindsight cheapest tick).
- **One post hoc lead reaches the DEMO bar: the Sydney-open dip, short AUDUSD 09:45 -> 10:00 Sydney, only on days when
  10:00 Sydney is not inside IC's post-rollover hour.** In the northern winter, 10:00 Sydney is 18:00 New York.
  - Net: +0.44 bp (t 2.54) IS / +0.76 (t 3.77) VAL. Still positive at spread x1.5 and at +60 s, and positive in 8 of
    9 years.
  - It beats 100 % of random entries. Power is 1.4 / 2.9, below the 3 that LIVE needs.
  - It was found after splitting both eras, so VAL is not a clean check.
  - Draft: PREREG_DRAFT_J_sydney_aud_offroll.md. Family J5 is stopped.
- **The cost of the Sydney V was mostly a clock clash, not the flow.** For half the year the window sits in the last
  15 minutes of IC's wide-spread rollover hour. There it costs 2.8 bp (IS) / 5.2 bp (VAL), against 1.2 / 1.0 bp when
  10:00 Sydney is 19:00-20:00 New York. The dip itself has the same size in both seasons, and a placebo at 18:00 New
  York in the northern summer shows no dip. Rounds 4, 6 S4 and 10 E/C all pooled the two seasons.
- **Passive orders cannot work under the conservative fill rule.** A limit order fills only once the touch has moved
  through it, so it never earns the spread. It helps only if a predictable move pushes price through it, and then it
  either cuts off the move's tail (take-profit) or gets adversely selected (entry). Every one of the 26 J2 cells is net
  negative, and only the SGE passive entry beats its market version, in IS only (-0.28 vs -0.67 bp).

## R0: each effect reproduced first (panel mid, original rule)
| effect (source) | published IS / VAL mid, bp (t) | reproduced IS | reproduced VAL | match |
|---|---|---|---|---|
| SGE: XAU long 02:15-02:23 UTC (r10 A/E) | +0.93 (7.9) / +0.72 (4.5) | +0.91 (7.7) | +0.70 (4.3) | yes |
| SYDpre: AUD+NZD short 09:45-10:00 Sydney (r4, r10 E) | +1.65 (13.1) / +1.48 (10.0) | +1.65 (13.1) | +1.48 (10.0) | exact |
| SYDpost: long 10:00-10:15 Sydney | +1.28 / +1.44 | +1.28 (7.6) | +1.44 (6.0) | exact |
| ECB: EUR long 14:00-14:15 Frankfurt (r10 E, flipped) | +0.73 (5.3) / +0.85 (4.1) | +0.73 (5.3) | +0.85 (4.1) | exact |
| SETT: XAU follow the day into the 13:30 ET settlement, big days (r6 S1) | +2.31 (3.6) / +1.00 (1.5) | +2.05 (3.1) | +0.97 (1.5) | IS 11 % lower; calendar or sd convention not recovered |
| MOC: USTEC follow the 15:50 ET imbalance minute (r11 H2) | +1.53 (2.71) / +1.00 (1.54) | +1.55 (2.71) | +0.92 (1.40) | yes, with round 11's bar-START labels |
| ASX: AUS200 fade 16:00-16:12 over 16:13-16:30 Sydney (r11 H2) | +0.82 (2.17) / +0.71 (2.71) | +0.86 (2.27) | +0.73 (2.75) | yes |
| BTC: follow the day over 23:30-24:00 UTC (r3) | +8.8 (4.1) / +2.6 (1.9) | +7.3 (3.4) | +2.4 (1.8) | IS 17 % lower (IC BTC starts 2017-08) |

The tick-level base cells reproduce the panel exactly (SGE +0.92 / +0.70, cost 1.59 / 1.04). Not carried, with
reasons in the hypotheses: the FX residual / currency-strength reversal (round 10 C already ran cost timing and lot by
forecast), USDCNH (bid-only bars), dollar catch-up and periodicity.

## Results
Net and power are per trade; power = per-trade net Sharpe x sqrt(trades a year x 1.73). Cost is the round trip.

| hypothesis (mechanism, source) | where | IS mid / VAL mid, bp (t) | cost IS / VAL | net IS (t) / VAL (t) | power IS / VAL | verdict |
|---|---|---|---|---|---|---|
| **J1** causal spread gate, best cell per effect (r 0.75 or 1.0 x trailing 20-day median spread) | SGE | +1.04 / +0.50 | 1.45 / 0.97 | -0.41 (-2.2) / -0.48 (-1.9) | <0 | fails: saves 0.1 bp, loses mid |
| | SYDpre | +1.44 / +1.00 | 1.51 / 1.77 | -0.06 (-0.4) / -0.77 (-4.4) | <0 | fails |
| | SYDpost | +1.05 / +1.05 | 1.19 / 1.07 | -0.14 (-0.9) / -0.02 (-0.1) | <0 | fails (at cost) |
| | SETT | +1.11 / +0.59 | 1.42 / 0.96 | -0.31 / -0.37 | <0 | fails |
| | MOC | +1.44 / +1.02 | 2.04 / 0.92 | -0.60 / +0.10 | <0 / 0.1 | fails; the gate rarely fires (USTEC spread) |
| | ECB (M1) | -0.08 / -0.18 | 0.63 / 0.62 | -0.71 / -0.80 | <0 | fails: any shift off 14:00-14:15 kills the move |
| | ASX (M1) | +0.65 / +0.54 | 2.40 / 1.57 | -1.75 / -1.03 | <0 | fails |
| | BTC (M1) | +12.95 / +1.61 | 13.50 / 3.17 | -0.55 / -1.56 | <0 | fails |
| oracle (cheapest tick in the same windows, hindsight, a bound) | SGE / SYDpre / SYDpost | +1.53 / +0.98; +1.28 / +0.80; +1.20 / +1.12 | 0.93 / 0.76; 0.96 / 1.19; 0.79 / 0.76 | +0.60 / +0.22; +0.32 / -0.39; +0.42 / +0.36 | 1.6 / 0.6; 1.5 / <0; 1.7 / 1.6 | not tradable, and even this misses LIVE |
| **J1b** entry and exit second chosen on IS (5-s grid, separable; an in-sample optimum) | SYDpre (T-1345 s, T-10 s) | +1.83 / +1.25 | 1.77 / 2.45 | +0.06 (0.4) / -1.20 (-6.7) | 0.2 / <0 | fails; VAL-optimal seconds still -0.78 |
| | SYDpost (T-10 s, T+1525 s) | +1.42 / +1.66 | 1.44 / 1.70 | -0.01 / -0.05 | <0 | at cost |
| | SGE (02:09:05, 02:36) | +1.44 / +0.85 | 1.60 / 1.05 | -0.16 / -0.19 | <0 | fails |
| | MOC (+20 s, +480 s) | +1.68 / +1.19 | 1.67 / 0.65 | +0.01 / +0.54 (0.8) | 0.0 / 0.6 | fails (IS t 0.02) |
| **J2a** pre-leg short, cover with a resting buy limit x bp below (the dip fills it) | SYDpre, best x 2, tau 0 | +1.05 / +0.99 | 1.91 / 2.54 | -0.86 (-10.8) / -1.54 (-12.6) | <0 | fails; fill 49 / 42 % |
| **J2b** SGE passive take-profit y bp above entry | best y 2, to 02:23 | +0.72 / +0.40 | 1.70 / 1.16 | -0.97 / -0.76 | <0 | fails; fill 44 / 54 % |
| **J2c** SGE passive entry at the 02:13 bid (or -0.5 bp) | best x 0.5 | +1.42 / +0.79 | 1.69 / 1.20 | -0.28 (-1.3) / -0.41 (-1.9) | <0 | fails; fill 45 / 63 %, no adverse selection after the fill (+1.46 / +0.61 bp) |
| **J2d** SETT passive take-profit | best y 4, to 13:40 | +1.14 / +0.08 | 1.66 / 1.13 | -0.52 / -1.05 | <0 | fails |
| **J2e** MOC passive take-profit | best y 4, to 16:00 | +0.41 / +0.44 | 1.88 / 0.93 | -1.47 / -0.49 | <0 | fails |
| **J3a** hold gold through the Chinese open drift and the SGE auction | XAU 01:00-02:23 UTC | +1.92 / +1.02 | 1.61 / 1.06 | +0.30 (0.5) / -0.05 (-0.1) | 0.3 / <0 | fails |
| | XAU 02:15-06:23 (AM and PM auctions) | +0.84 / +0.30 | 1.56 / 1.04 | -0.72 / -0.75 | <0 | fails (PM auction alone +0.40 / +0.08 mid) |
| **J3b** EUR long through the ECB fix, held to the WM/R window | EURUSD 14:00 CET-15:45 London | +1.09 / +0.04 | 0.63 / 0.62 | +0.47 (0.7) / -0.57 (-0.5) | 0.4 / <0 | fails: no second same-sign flow |
| **J3c** SETT big-up day, hold long to the next SGE auction (one rollover, swap paid) | XAU 13:15 ET -> 02:23 UTC | +10.8 / +3.8 | 2.97 / 4.07 | +7.83 (2.30) / -0.26 (-0.1) | 1.25 / <0 | fails VAL (the IS gain is overnight gold drift) |
| **J3d** net the Sydney V (stop and reverse at 10:00) | AUD+NZD | +2.93 / +2.91 | 3.22 / 4.16 | -0.29 / -1.25 | <0 | saves nothing: same 4 lot-sides |
| **J4** lot 0.5 / 1 / 2 by causal terciles (C-RV, C-PRE, \|signal\| / sd) | best: MOC, \|imbalance-minute move\| / 60-day RMS | (flat -0.02 / +0.27) | 1.68 / 0.65 | $/trade +1.07 (1.14) / +0.59 (0.64) | 0.6 / 0.5 | fails (IS t 1.14); \|sig\| > RMS days alone +2.76 (1.75) / +1.05 (0.71) |
| | SYDpre (C-RV) | | | $ +0.20 (1.1) / -1.00 (-4.0) | 0.7 / <0 | fails |
| | SGE (C-PRE) | | | $ -0.55 / -0.25 (J1 exec: -0.28 / -0.38) | <0 | fails |
| | SETT all days (\|r\|/sd) | | | $ -0.32 / -0.46 | <0 | fails |
| **J5a** AUD flow in AUDJPY | SYDpre / SYDpost | +1.48 / +1.11; +1.13 / +0.76 | 1.96 / 2.83; 1.61 / 2.03 | -0.48 / -1.71; -0.49 / -1.26 | <0 | fails |
| **J5b** USTEC imbalance signal traded in US30 (cheaper) | US30 15:52-16:00 ET | +0.97 / +0.01 | 0.91 / 0.29 | +0.07 / -0.28 | <0 | fails: the move is not in US30 in VAL |
| **J5c** (post hoc) Sydney V outside IC's rollover hour (10:00 Sydney >= 18:30 NY) | AUD+NZD short 09:45-10:00 | +1.53 (9.4) / +1.61 (8.4) | 1.26 / 1.07 | +0.28 (1.71) / +0.53 (2.82) | 1.2 / 2.9 | fails DEMO (IS t 1.71) and x1.5 in IS |
| | **AUDUSD only** (the cheaper pair) | +1.54 (8.9) / +1.53 (7.5) | 1.10 / 0.77 | **+0.44 (2.54) / +0.76 (3.77)** | 1.36 / 2.86 | **meets DEMO, LIVE except power; PREREG draft** |
| | SYDpost, same filter | +0.83 / +0.95 | 1.20 / 1.03 | -0.38 / -0.08 | <0 | fails |

Stress for the J5c AUD cell:
- **Spread x1.5:** +0.19 / +0.68.
- **+60 s:** +0.34 / +0.41.
- **Both:** +0.10 / +0.33.
- **Winsorised:** +0.38 (2.58) / +0.78 (3.90).
- **Exact second (ticks):** all 35 entry/exit offsets in -60..+60 s are positive in both eras. Exits 5-10 s after 10:00 lose about 0.2 bp.
- **Time placebos at -60 / -30 / +30 / +60 min:** -2.0 / -1.1 / -1.0 / -0.6 IS.
- **C3 correlation:** daily +0.004, monthly -0.08.

## Break-even per effect, and how close the best execution gets
- **Break-even cost** is the mid edge.
- **LIVE cost** is the round trip at which power reaches 3: mid - 3 sd / sqrt(HOLD trades).
- **Gross power** is the power at zero cost.

| effect | mid IS / VAL | gross power IS | base cost IS / VAL | break-even IS / VAL | LIVE cost IS / VAL | best tradable execution | its cost IS / VAL | its net IS / VAL |
|---|---|---|---|---|---|---|---|---|
| SGE | +0.92 / +0.70 | 4.2 | 1.59 / 1.04 | 0.92 / 0.70 | 0.27 / 0.06 (below the 0.6 commission: impossible at IC) | J3a 01:00-02:23 | 1.61 / 1.06 | +0.30 / -0.05 |
| SYDpre (AUD+NZD, all days) | +1.65 / +1.48 | 9.0 (per day 7.0) | 1.76 / 2.43 | 1.65 / 1.48 | 1.10 / 1.03 | J1 r1.0 | 1.51 / 1.77 | -0.06 / -0.77 |
| SYDpre AUD, off-rollover days (J5c) | +1.54 / +1.53 | 4.8 (VAL 5.7) | 1.10 / 0.77 | 1.54 / 1.53 | 0.57 / 0.73 | clock market (the rule) | 1.10 / 0.77 | +0.44 / +0.76 |
| SYDpost | +1.29 / +1.44 | 5.5 | 1.47 / 1.73 | 1.29 / 1.44 | 0.58 / 0.75 (about the commission) | J1 r0.75 | 1.19 / 1.07 | -0.14 / -0.02 |
| ECB | +0.73 / +0.85 | 2.9 | 0.65 / 0.64 | 0.73 / 0.85 | <0 / 0.03 | J3b | 0.63 / 0.62 | +0.47 / -0.57 |
| SETT big days | +2.05 / +0.97 | 1.7 | 1.44 / 1.00 | 2.05 / 0.97 | <0 (LIVE impossible at any cost) | base | 1.44 / 1.00 | +0.61 / -0.03 |
| MOC | +1.55 / +0.92 | 1.5 | 1.68 / 0.65 | 1.55 / 0.92 | <0 | J5b US30 | 0.91 / 0.29 | +0.07 / -0.28 |
| ASX | +0.86 / +0.73 | 1.2 | 2.18 / 1.57 | 0.86 / 0.73 | <0 | base | 2.18 / 1.57 | -1.32 / -0.85 |
| BTC | +7.3 / +2.4 | 2.2 | 13.4 / 3.2 | 7.3 / 2.4 | <0 | J1 r0.75 | 13.5 / 3.2 | -0.55 / -1.56 |

Only SGE, the Sydney legs and (barely) ECB have the gross power for LIVE; SETT, MOC, ASX and BTC cannot reach power 3
even at zero cost. For SGE and SYDpost the LIVE cost is at or below the 0.6 bp commission alone, so no execution at
IC can get there. SYDpre is the one effect where the gap is spread, and the off-rollover-hour filter brings the
cost to 1.10 / 0.77 bp against a 1.5 bp break-even and a 0.57 / 0.73 bp LIVE cost: VAL is 0.04 bp from the LIVE
cost, IS 0.5 bp. The per-trade Sharpe (0.08 IS, 0.17 VAL) gives power 1.4 / 2.9 on ~300 HOLD trades.

## Cells and chance
| family | cells | best IS net t (cell) | max of K normals median / p95 | per-day sign-flip p95 (net, demeaned) |
|---|---|---|---|---|
| J1 | 16 | -0.22 (BTC r0.75): all 16 cells net < 0 in IS | 2.03 / 2.94 | 2.84 |
| J1b | 4 | +0.06 (SYDpre), in-sample optimum | 1.4 / 2.5 | - |
| J2 | 26 (+26 touch sensitivities) | -1.26 (SGE J2c x0.5, -0.28 bp); every cell negative | 2.22 / 3.09 | 2.93 |
| J3 | 5 | +2.30 (J3c, VAL -0.26) | 1.51 / 2.56 | 2.56 |
| J4 | 11 | +1.14 (MOC base, scaled) | 1.9 / 2.8 | - |
| J5 (a, b) | 3 | +0.14 (US30) | 1.26 / 2.38 | 2.39 |
| J5c path (post hoc, after D1's 10 groups) | 12 (2 legs x 2 executions x 3 symbol sets) | +2.54 (AUD SYDpre base); pooled IS+VAL t 4.09 | 1.91 / 2.85 | - |

Mid t's are large everywhere (up to 13), as the earlier rounds found: the effects are real and the families fail on
cost. J5c's IS t alone is inside the range of chance for its selection path. Its VAL t (3.77) was seen during the
selection, so it is not independent evidence. The case for the lead rests on two things: the filter selects on cost
known in advance (the edge on the kept days equals the all-days edge), and IS alone picks the same filter and the
same symbol.

## Surprises, data and cost-model notes
1. **The Sydney V meets IC's rollover hour (D1).** When 10:00 Sydney falls at the following New York times:

   | NY time | SYDpre mid IS / VAL, bp (t) | cost IS / VAL, bp |
   |---|---|---|
   | 18:00 | +1.88 (10.0) / +1.21 (5.4) | 2.78 / 5.19 |
   | 19:00 | +2.14 (4.8) / +1.86 (5.3) | 1.52 / 1.18 |
   | 20:00 | +1.36 (8.1) / +1.53 (6.8) | 1.18 / 1.04 |

   - **Placebo** at 18:00 New York when that is 08:00 Sydney: pre leg -0.13 / -0.25.
   - **The dip belongs to the Sydney clock.** The AUD/NZD mean spread before 10:00 is skewed: in VAL, AUD's mean is
     1.18 bp against a median of 0.30. It drops at 10:01 when 10:00 Sydney = 18:00 New York.
   - **The post leg on rollover days (+2.2 / +2.4 mid) partly reflects quotes normalising after the rollover hour.**
     The summer placebo after 18:00 New York also rises (+0.37 / +0.89, t 2.3 / 3.9).
   - **Every earlier Sydney test mixed the two seasons.**
2. **SETT's edge sits in the first minute after the signal.** With both fills 60 s late, the big-day mid falls from
   +2.05 / +0.97 to +0.37 / +0.17 and the net to -1.09 / -0.83; shifting the whole rule (signal included) by one
   minute gives an all-days mid of -0.05 instead of +0.64. What round 6 read as settlement momentum is mostly one-minute continuation
   of the move measured up to 13:15:00, which a bot cannot capture.
3. **The ECB move is confined to 14:00-14:15 Frankfurt.** Starting earlier (13:51) or ending later turns the mid
   negative (-0.08 / -0.18). EURUSD's spread there is about 0, so the 0.6 bp commission is the whole cost and no
   execution changes it.
4. **Passive fills and adverse selection.**
   - **Resting take-profits truncate the moves.** For SGE, SETT and MOC the fill rate is 44-92 % and the mid kept
     falls to 0.1-1.1 bp. After a take-profit fill, price mostly kept going the trade's way: the post-fill move against
     the limit order is -0.2..-1.3 bp for SGE and MOC, and mixed for SETT.
   - **The J2a cover is selected on days the dip is deep.** Filled minus unfilled moves are -5..-7 bp (t -17..-24).
     The early cover then forgoes the large-dip days that carry the mean.
   - **The SGE passive entry is the one place a resting order is not picked off.** Price rises after the fill
     (+1.46 / +0.61 bp), but only 45-63 % of days fill, and the trade-through fill price eats the gain.
   - **Touch fills (ask <= limit on the grid) change net by <= 0.1 bp.**
5. **The USTEC spread at 15:52-15:54 ET is rarely at or below 0.75 x its trailing median** (gate open 2-3 % of days).
   The minutes after the imbalance print are uniformly wide.
6. **Reproduction gaps:** SETT IS and BTC IS are 11-17 % below the published numbers; VAL matches. Round 11's MOC
   labels are bar-START (the publication minute is the bar 15:50:00-15:50:59). Reading them as bar-END gives +0.38
   instead of +1.55.

## Directions that need the user's decision
- **Run the J5c AUD draft forward.**
  - Demo account, about 170 trades a year from March to November, starting with the 2027 northern summer (or now, if
    the lead registers it first).
  - The lead's HOLD pass. Expected HOLD t is 1.4-2.9, so a pass is unlikely to reach 2.5 alone. Pooling with the demo
    is the realistic route.
- **A commission-free FX or metals account type.** The 0.6 bp commission alone is above the LIVE cost for SGE and
  SYDpost; with no commission (and IC's raw spread), SGE's LIVE cost of 0.27 / 0.06 bp would still need near-zero
  spreads. Testing it needs a broker quote history; this is the user's call.
- **Ticks for EURUSD.** Only M1 bars exist here. ECB timing at second resolution would need EURUSD ticks for
  2016-2024. The commission floor makes it unlikely to matter.

## Files (scratchpad r12/J/)
- **Shared helpers:**
  - jc.py: panel, ticks with a HOLD guard, statistics.
  - effects.py: event lists and original rules.
  - tx.py: tick fills (market, gate, oracle, trade-through limits on the price grid).
- **R0:** r0.py -> r0_out.txt.
- **J1 / J2 on ticks:** jtick.py (one run per effect) -> rows_<EFF>.pkl; summ.py -> summ_*.txt.
- **J1 on M1, J3, J5a/b:** jpanel.py -> rows_panel.pkl, summ_panel.txt.
- **J4:** j4.py -> j4_out.txt.
- **J1b:** j1b.py -> j1b_out.txt.
- **Break-even and chance:** final.py -> final_out.txt.
- **Controls and the Sydney spread profile:** control.py -> control_out.txt.
- **D1:** d1.py -> d1_out.txt.
- **J5c:** j5c.py -> j5c_out.txt; j5c_aud.py -> j5c_aud_out.txt; j5c_rob.py -> j5c_rob_out.txt.
