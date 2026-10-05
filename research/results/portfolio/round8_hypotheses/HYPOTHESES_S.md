# Stream S hypotheses: exact rules (written 2026-10-05 ~01:00 UTC, before any return/response number was computed)

The mechanisms are those of STREAM_S.md (S1-S4, written 2026-10-04 17:58 UTC). This file fixes the operational
definitions. Only a data-coverage check was run before this file (bar coverage by hour, spread sign); no returns,
responses or event counts were looked at.

## Common conventions
- Price P[s, i] = panel mid of minute i (close of bar i, i.e. the price at T0 + 60 (i+1) s). Forward-filled; age =
  minutes since the last real bar. ln prices.
- A return over a window ending at minute i is valid only if bar i exists (age 0) and the start point has age <= 2.
- Entry: the signal is known at the close of bar i (the event's last minute). Entry fill = close of bar i+L, L = 1
  (main) and L = 2 (latency variant). The target must have a real bar at the entry minute (age 0), otherwise the
  event-target pair is skipped (the target is not trading).
- Exit at entry + H minutes (close of that bar; forward-filled price and spread with age <= 5, else the pair is
  dropped). "EOD" = close of the 19:59 UTC bar (20:00 UTC), only for entries at or before 19:50 UTC.
- Cost (bp) = (max(spr_entry, 0)/2 / P_entry + max(spr_exit, 0)/2 / P_exit) * 1e4 at the actual minutes, + 0.6 bp for
  FX and metals (XAU, XAG, XPT), 0 for indices, energies, crypto. Holds that cross 17:00 New York (IC rollover) pay
  research/swing/rates.py swap_frac_at x research/specs.rollovers (triple day as in swing.swap_frac).
- Mid response (bp) is signed so that > 0 = continuation in the hypothesised direction. Reversal = -response. Net is
  computed for the side being judged (continuation side: mid - cost; reversal side: -mid - cost).
- t-stats are clustered by UTC day of the event (sum within a day, t over days); when targets are pooled, all pairs of
  one day form one cluster.
- Eras: IS 2016-01..2021-12, VAL 2022-01..2024-12, by event time. HOLD is not in the panel and stays closed.
- Power = per-trade net Sharpe (mean/sd) x sqrt(events per year x 1.75).

## S1 large source shocks -> linked targets (continuation vs reversal)
- Sources (10): US500, USTEC, DE40, JP225, XAUUSD, XTIUSD, BTCUSD, USDJPY, EURUSD, AUDUSD.
- Window w in {5, 15} min: r_w[i] = ln P[i] - ln P[i-w].
- Scale sd_w(day) = sqrt(mean r_w^2) over every valid minute of the 28 calendar days (~20 trading days) ending at the
  previous UTC midnight (causal, all hours pooled).
- Event: |r_w[i]| >= k sd_w, k in {4, 6}; first crossing; no new event for the same (source, w, k) within 60 minutes
  after an event. Direction d = sign(r_w[i]).
- Beta / correlation of target T to source S: OLS slope and correlation of non-overlapping 5-min grid returns (both
  valid), summed over the 84 calendar days (~60 trading days) ending at the previous UTC midnight; >= 500 pairs.
- Signed response of T: d x sign(beta) x (ln P_T[exit] - ln P_T[entry]) in bp.
- Horizons H in {5, 15, 60, 240, EOD}. Targets: the other 25 symbols.
- Primary grid: 10 sources x 2 w x 2 k x 25 targets x 5 H at L = 1 = 5,000 cells (each judged both ways, |t| the
  same). L = 2 and the session split (Asia 00-07, Europe 07-12:30, US 12:30-20, late 20-24 UTC) are secondary,
  applied to the best cells only. Chance: max |t| of 5,000 independent normals ~ 4.1 (cells are correlated, so the
  effective K is smaller and the benchmark ~3.5-4).
- Also descriptive: the target's own contemporaneous move over the event window (checks that beta signs mean
  something).

## S2 beta-gap catch-up
- Same events as S1. For a linked target (trailing |corr| >= 0.3), gap = r_T,w[i] - beta x r_S,w[i] (same window),
  z = gap / sd_T,w (the target's trailing scale, same definition as S1).
- Trade T in the gap-closing direction (-sign(gap)) when |z| >= c, c in {1, 2, 3}; entry L = 1 (L = 2 variant);
  H in {15, 60, 240, EOD}.
- Grid: 10 sources x 2 w x 2 k x 3 c x 4 H = 480 pooled cells (all linked targets of one source pooled), plus a per-
  target breakdown only for the best pooled cells. Chance for 480: max |t| ~ 3.5.

## S3 safe-haven spillover
- Events on US500 (P as above):
  E1- : 60-min log return <= -1 % (first crossing, at most one per UTC day).
  E2- : ln(P / P at the close of the 19:59 UTC bar of the previous weekday) <= -2 % (first crossing per day).
  E1+ / E2+ : the mirrors (+1 % in 60 min, +2 % since the previous 20:00 UTC).
- Targets and the safe-haven direction during an equity DROP (Ranaldo & Soderlind 2010: CHF, JPY and, less, EUR
  appreciate against USD when US stocks fall; gold rises): USDJPY short, USDCHF short, XAUUSD long, AUDJPY short,
  EURUSD long. In a rebound the signs flip.
- Horizons from entry (L = 1): 60, 240, 480, 1440 min (swap charged when crossing 17:00 NY).
- Grid: 4 event types x 5 targets x 4 H = 80 cells. Chance for 80: max |t| ~ 2.9.

## S4 scheduled US data at 08:30 New York
- Event days: every weekday, t0 = 08:30 New York (12:30 UTC in US DST, 13:30 UTC otherwise; zoneinfo).
- USD reaction u_m = 1/2 [ (ln USDJPY - ln EURUSD)(close of bar t0+m-1) - (same)(close of bar t0-1) ], m in {1, 5}
  (the first 1 or 5 minutes after the release). z = u_m / sd of u_m over the previous 250 event days (causal, >= 100).
- Subsets: all weekdays; |z| >= 1; |z| >= 2; first Friday of the month (NFP proxy).
- Implied direction of target T: sign(b_T x u_m), b_T = slope of T's own move over the same m minutes on u_m over the
  previous 500 event days with |z| >= 1 (causal; needs >= 60 such days, so the first ~1-2 years are warm-up).
- Targets (slower assets): XAUUSD, XAGUSD, US500, USTEC, US30, DE40, UK100, JP225, AUDJPY, AUDUSD, NZDUSD, GBPUSD,
  USDCAD, USDCHF, EURJPY, GBPJPY, XTIUSD, XBRUSD (18).
- S4a continuation: trade T in the implied direction from entry = close of bar t0+m (L = 1; +1 variant), H in
  {15, 30, 60, 120} min (all before 20:00 UTC, no swap).
- S4b catch-up: gap = T's own move over the m minutes - b_T u_m; trade -sign(gap) when |gap| >= 1 x sd of T's own
  m-minute move on the previous 250 event days; same H.
- Grid: S4a 2 m x 4 subsets x 18 targets x 4 H = 576 cells; S4b 2 m x 3 subsets (all, |z|>=1, first Fri) x 18 x 4 =
  432. Chance for ~1,000 cells: max |t| ~ 3.7.

## Controls for any cell that clears the screens
- Random-entry control: same count, same target, same side, same hold, entry moved to a random day of the same era
  with the same weekday and the same minute of day; >= 200 seeds; the real cell must beat >= 95 % of seeds.
- Spread x1.5 and L = 2 must stay net > 0; >= 2/3 of years net > 0.

## Added 2026-10-05 ~01:45 UTC, after the S1-S4 screens (POST HOC: written after IS and VAL of S2 were seen)
S2r gap extension. S2's gap-closing trade was negative on average in BOTH eras (mean cell t -0.58 IS, -0.66 VAL;
corr of cell t across eras +0.28), i.e. the part of a linked target's move that beta does not explain kept going.
Rule fixed now: at each S1 event (same 40 event sets), among linked targets (trailing |corr| >= 0.3) with |z| >= 2,
take the at most 3 with the largest |z| (the position cap), trade each in the direction sign(gap), entry L = 1,
hold H in {15, 60, 240} min. Because the direction was chosen after seeing both eras, IS/VAL numbers here are
descriptive only; the only clean test available is PRE (Dukascopy M1 2004-2015: EURUSD, USDJPY, USDCHF, EURJPY,
GBPJPY), and only for FX->FX pairs. It is run on PRE only if the FX-only version on IS/VAL has power >= 3 (otherwise
a PRE pass could not lead to a candidate anyway).
Also a correlation-preserving chance benchmark for S2 (flip all events of one source on one day together, 200 draws).

## Added 2026-10-05 ~01:55 UTC (POST HOC: written after S4b's reverse side was seen in IS and VAL)
S4b's gap-CLOSING trade lost in US indices at m = 1, H = 30 in both eras (US30/US500/USTEC mid -12..-14 bp IS,
-6..-10 VAL), i.e. the index's first-minute move beyond the USD-implied move kept going. Two questions, computed once:
S4c own-move drift (not cross-asset, a control for S4b): index first-minute move at 08:30 NY (close of the 08:29 bar to
close of the 08:30 bar), z = move / RMS of the same move over the previous 250 weekdays (>= 100); trade sign(move)
when |z| >= 1 (and >= 2), entry close of the 08:31 bar, H in {15, 30, 60}; US30, US500, USTEC; 18 cells.
S4b-rev as registered grid's mirror: the S4b reverse side is counted with the S4b grid (432 x 2 = 864 directional
cells, chance max |t| ~3.4). Neither can become a candidate from IS/VAL alone (VAL seen); there is no PRE for indices.
