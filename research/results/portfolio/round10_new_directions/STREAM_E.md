# Round 10, stream E: size-conditioned fixed-time flows (E1), non-US macro releases (E2)

2026-10-05. Hypotheses, written before computing: research/results/portfolio/round10_new_directions/HYPOTHESES_E.md.
HOLD (2025+) was never loaded: the shared panel ends 2024-12-31. Costs: actual panel spread at the entry and exit
minutes (half each) + 0.6 bp commission (FX, gold). t clustered by UTC day.

## E1 Size-conditioned fixed-time flows: no candidate

Mechanism under test: a flow that is roughly fixed in money moves price more (in bp) on illiquid / volatile days,
while the fix-minute spread stays near normal. Two causal conditioning variables, declared in advance: C-RV (20-day
realised vol, top tercile vs a trailing 250-day threshold) and C-PRE (activity in the 60 minutes before entry relative
to the previous 20 event days, same causal tercile). 8 legs x 2 variables = 16 judged TOP cells.

| leg (side, source) | where | TOP cell | IS mid (t) / VAL mid (t) | spread+comm TOP (IS+VAL mean) | net IS (t) / VAL (t) | power IS/VAL | TOP-BOT mid (Welch t) IS / VAL |
|---|---|---|---|---|---|---|---|
| ECB-pre (USD long into 14:15 CET; Krohn et al.) | EURUSD | RV | -0.68 (-1.9) / -0.87 (-2.0) | 0.65 | -1.33 / -1.50 | <0 | +0.25 (0.7) / +0.01 |
| | | PRE | -0.90 (-3.4) / -0.65 (-1.6) | 0.64 | -1.55 / -1.28 | <0 | -0.23 / +0.36 |
| ECB-post (USD short after) | EURUSD | RV | +0.19 (0.5) / +0.24 (0.5) | 0.82 | -0.71 / -0.49 | <0 | +0.60 (1.5) / +0.44 |
| | | PRE | -0.04 / +0.49 (0.9) | 0.78 | -0.84 / -0.24 | <0 | +0.08 / +0.77 (1.2) |
| WMR-pre (USD long into 16:00 London) | EURUSD+GBPUSD | RV | +0.41 (0.7) / -1.30 (-2.0) | 0.73 | -0.34 / -2.00 | <0 | +0.02 / -1.75 (-3.1) |
| | | PRE | +1.01 (2.1) / -0.43 (-0.8) | 0.70 | +0.30 (0.6) / -1.10 | +0.4 / <0 | +0.83 (1.7) / -0.05 |
| WMR-post (USD short after) | EURUSD+GBPUSD | RV | +0.57 (1.4) / +0.85 (1.5) | 0.73 | -0.18 / +0.15 | <0 / +0.3 | +0.61 (1.6) / +0.45 (1.0) |
| | | PRE | +0.23 (0.7) / +1.43 (2.9) | 0.70 | -0.49 / +0.77 (1.6) | <0 / +1.5 | +0.15 / +1.34 (2.9) |
| SGE (gold long 02:15-02:23 UTC, data-derived side from stream A) | XAUUSD | RV | +0.86 (2.9) / +0.70 (2.4) | 1.56 | -1.11 / -0.37 | <0 | -0.20 / +0.47 |
| | | PRE | +1.31 (4.9) / +1.02 (3.3) | 1.35 | -0.21 (-0.8) / -0.04 (-0.1) | <0 | +0.68 (2.2) / +0.63 (1.7) |
| NYC (USDJPY long 17:01-18:00 NY) | USDJPY | RV | -0.41 / -0.93 (-3.3) | 1.98 | -2.14 / -3.10 | <0 | +0.37 / +1.39 (3.9) |
| | | PRE | -0.56 / -1.12 (-2.5) | 1.81 | -2.11 / -3.47 | <0 | -0.07 / +0.77 |
| SYD-pre (short AUD/NZD 09:45-10:00 Sydney) | AUDUSD+NZDUSD | RV | +2.52 (5.9) / +2.12 (7.2) | 2.27 | +0.69 (1.7) / -0.62 (-1.9) | +1.1 / <0 | **+1.06 (3.0) / +0.98 (3.8)** |
| | | PRE | +1.95 (7.1) / +1.81 (5.7) | 2.24 | +0.00 / -1.02 | 0 / <0 | +0.37 (1.4) / +0.77 (2.7) |
| SYD-post (long AUD/NZD 10:00-10:15 Sydney) | AUDUSD+NZDUSD | RV | +0.88 (1.7) / +2.40 (5.1) | 1.71 | -0.67 / +0.52 (1.1) | <0 / +1.1 | -0.20 / +1.68 (4.1) |
| | | PRE | +1.62 (5.1) / +1.13 (2.3) | 1.71 | +0.03 / -0.81 | 0 / <0 | +0.55 (1.7) / -0.69 |

Unconditional reference (mid IS / VAL, bp): ECB-pre -0.73 (t -5.3) / -0.85 (t -4.1); ECB-post 0.0 / 0.0; WMR-pre
+0.30 / -0.19; WMR-post +0.29 / +0.53; SGE +0.91 (7.7) / +0.70 (4.3); NYC -0.43 / -1.62; SYD-pre +1.65 (13.1) /
+1.48 (10.0); SYD-post +1.28 (7.6) / +1.44 (6.0).

- Cells net > 0 in both IS and VAL: **0 of 16** (so no random-entry control, latency or C3 correlation applies).
  The closest, SGE x C-PRE, is -0.21 / -0.04 bp net (+1 minute -0.08 / -0.47, spread x1.5 -0.66 / -0.28).
- Chance: best |t_IS| of the 16 judged cells at mid is 7.14 (SYD-pre x C-PRE), far beyond the per-day sign-flip
  null (95 % of max |t| = 2.89; 16 normals: 2.97), but that is the unconditional Sydney V, not the conditioning.
- **Mechanism check.** The illiquidity scaling is real where the flow is real: SYD-pre's move is +1.0 bp larger in
  the high-vol tercile in both eras (t 3.0 / 3.8), SGE's +0.65 bp larger on active mornings (t 2.2 / 1.7). But the
  scaling is only ~1.5x, and at Sydney the spread rises with it (TOP 1.67 vs 1.15 bp average of the entry/exit
  spreads under C-RV), eating half of the gain. At the ECB and WM/R fixes there is no consistent scaling.
- **Side surprises.** (1) EURUSD *rises* into the ECB 14:15 CET fix (-0.73 bp at the registered USD-long side, t -5.3
  / -4.1); the registered Krohn-Mueller-Whelan side is wrong for this pair and window. Post hoc flipped (long EURUSD
  14:00-14:15 CET), net is +0.08 (t 0.6) / +0.21 (t 1.0), per-trade Sharpe 0.015 / 0.038, power < 0.6: real but at
  cost (EURUSD's spread at that minute is ~0, so cost is the 0.6 bp commission; the move is 0.7-0.9 bp). (2) The NYC leg
  was registered from round 4's "hour after the NY close" (+0.8 bp); round 4 meant the 16:00 cash close. At 17:01-18:00
  NY, USDJPY falls (-0.43 / -1.62 at mid) and the spread is ~1.1 bp: fails by > 2 bp.
- Regime note: the causal C-RV threshold puts 36 % of VAL days in TOP (22 % in IS), because 2022 vol rose above its
  trailing 250-day range.

Per-trade net Sharpe / power of the 16 judged cells (IS / VAL): all <= 0.09 / power <= 1.5; the best IS power is
SYD-pre x C-RV +1.1 (VAL -1.9) and the best VAL power WMR-post x C-PRE +1.5 (IS -0.9). Day-clustered power is not
higher (the two-symbol legs' positions are positively correlated). Files: e1.py -> e1_out.txt; e1_perm.py ->
e1_perm_out.txt.

## E2 Non-US scheduled macro releases, pooled: no candidate

Calendars (cal/releases.json, cal/sources.txt) come from official archives only (ONS calendar with per-event times,
ABS, StatCan The Daily, Eurostat euro-indicator feed, ZEW notices, archived ifo pages, Stats NZ, BoJ, FSO embargo
times, BLS), built by a helper agent that did not open prices. 16 types, complete for every year, ~128-136 events a
year after merging same-minute releases (1,167 events, IS 767 / VAL 400). Dropped: euro-area/German flash PMI (no
public, official, dated archive). Release-time changes are handled per event: UK 09:30 -> 07:00 from April 2020,
Swiss CPI 09:15 -> 08:30 from 2019, ZEW 11:00 -> 11:05 from 2021.

Rule (registered): reaction r0 over the first 5 minutes after the release (from the last quote before it), trade
sign(r0) from minute T+6 for h minutes; ALL events, or LARGE = |r0| >= the RMS of the previous 12 reactions of that
release type. Implementation note: NZ releases in the northern winter (10:45 NZDT = 21:45 UTC = 16:45 New York) come
just before the NY rollover; the first run dropped them by mistake; they are now held through it and pay swap (x3 on
Wednesdays). The pooled numbers moved by <= 0.4 bp.

| cell (h, subset) | IS mid bp (t) n | VAL mid (t) n | cost (mean) | net IS (t) / VAL (t) | x1.5 IS/VAL | +1 min IS/VAL | Sharpe IS/VAL | power IS/VAL |
|---|---|---|---|---|---|---|---|---|
| **30, ALL** | -0.11 (-0.3) 766 | +0.30 (0.6) 400 | ~0.9 | -1.08 (-2.5) / -0.68 (-1.3) | -1.27/-0.87 | -1.18/-0.50 | -0.09/-0.06 | <0 |
| 30, LARGE | +1.21 (1.3) 186 | +2.09 (2.4) 153 | ~0.9 | +0.31 (0.33) / +1.15 (1.31) | +0.15/+0.98 | **-0.12**/+1.49 | +0.024/+0.103 | 0.18/0.97 |
| **120, ALL (primary)** | +0.04 (0.05) 767 | -0.69 (-0.7) 400 | ~0.9 | -0.88 (-1.05) / -1.56 (-1.57) | -1.04/-1.69 | -0.89/-1.43 | -0.04/-0.08 | <0 |
| 120, LARGE | +0.51 (0.3) 186 | +2.83 (1.6) 153 | ~0.9 | -0.36 / +1.98 (1.1) | -0.49/+1.85 | -0.70/+2.18 | -0.02/+0.09 | <0/0.85 |
| 240, ALL | -0.30 (-0.3) 767 | +0.66 (0.5) 400 | ~0.9 | -1.22 / -0.20 | -1.38/-0.34 | -1.33/+0.05 | -0.04/-0.01 | <0 |
| 240, LARGE | +0.72 (0.4) 186 | +4.03 (1.6) 153 | ~0.9 | -0.15 / +3.18 (1.3) | -0.28/+3.06 | -0.53/+3.44 | -0.01/+0.11 | <0/1.0 |

- Cells tried: 6 pooled (per-type and per-pair splits are descriptive). Best |t_IS| at mid 1.32 (h30 LARGE); the
  per-day sign-flip null's 95 % of max |t| is 2.61 (p 0.59): **nothing beyond chance**. The primary cell is flat in
  IS and negative in VAL.
- The only cell net > 0 in both eras, h30 LARGE, has IS t 0.33 (DEMO needs 2.0, LIVE 2.5), turns negative at +1
  minute in IS, and is positive in 7/9 years only through a few large events (median net +0.19 / +0.59, 52 % of trades
  > 0). Random-entry control (200 seeds, same rule on non-release weekdays at the same local clock, within +-8 weeks):
  beats 99 % IS / 96 % VAL, but that only says that continuation on quiet days loses the cost (null mean -1.40 /
  -0.71). C3 correlation (IS+VAL, for the record): daily 0.01, monthly -0.02.
- Per release type (h30 / h120, mid, descriptive): nothing is consistent across eras. AU quarterly CPI +6.5 (t 2.3) /
  +2.0 at h30 IS / VAL (n 24 / 12), but the AU monthly CPI indicator goes the other way (-6.4, t -2.1, n 16). UK CPI
  and labour flip from IS (-1.4 / -3.8 at h30) to VAL (+4.3 / +3.6, t 2.2 / 2.6). USDCAD LARGE +3.3 / +3.8 net (t 1.4 /
  1.5), stronger on NFP-clash days (n 13 / 7), i.e. partly a US-data effect that rounds 3 and 8 already covered.
  The German surveys (Ifo, ZEW) and the EA flash HICP move EURUSD only 3-4 bp in 5 minutes and do not continue.
  NZ releases cost ~2-2.9 bp (spreads around 21:45-22:45 UTC) against 22-32 bp reactions that do not continue.
- E2-pre (report only, no side): the unsigned pre-release drift is |t| < 1.7 everywhere except USDCAD IS -2.6 bp
  (t -3.2) / -1.1 (t -1.2) over the hour before 08:30 ET. Signed by the later reaction (a leakage check no bot can
  use), r[-15,0] is |t| <= 2.3 with mixed signs (AUDUSD IS -1.8, t -2.2 / VAL +1.2; USDJPY VAL -2.8, t -2.3): no
  leakage pattern. Pre-release 15-minute |moves| are larger than on non-release days at the same clock for NZDUSD
  (8.2 vs 3.0 bp IS; this window includes the pre-rollover spike) and GBPUSD/USDCAD (+15-25 %), not for EUR/CHF/JPY.
- Files: e2.py -> e2_out.txt (+ e2_rows.pkl); e2_perm.py -> e2_perm_out.txt; e2_detail.py -> e2_detail_out.txt.

## Verdict
No candidate in either family; no PREREG draft. The size-conditioning idea is half right: where a fixed-time flow is
real (Sydney V, SGE auction) its move does grow with volatility/activity (~1.5x in the top tercile, t 2-4 in both
eras), but not enough, and at Sydney the spread grows with it. Non-US data releases show no continuation after the
first 5 minutes, pooled or by currency, as at 08:30 New York.
