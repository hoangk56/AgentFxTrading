# Round 12, stream K: hypotheses (each written before its numbers)

Stream K = literature pass 2018-2026 for intraday / short-horizon flow, hedging, settlement, benchmark and premium
anomalies not tested in rounds 3-11, then screens of the untested ones. The list of what rounds 3-11 tested is in the
scratch folder (`scratchpad/r12/K/tested_list.md`); the literature table is in STREAM_K.md.

## Common conventions (all K families), 2026-10-06 01:12 UTC, before any round-12 number

- Data: the shared panel (mid, spread at each minute's last tick, 2016-01..2024-12; HOLD not in it). IS 2016-2021
  (energies 2018-21, BTC 2018-21), VAL 2022-2024. No 2025+ data is loaded.
- Clocks: local exchange times with DST (New York, London) via zoneinfo; UTC where stated. Weekdays only (IC crypto
  was closed at weekends until 2024-04).
- "Price at T" = mid close of the last M1 bar that ends at or before T (the bar starting at T-1 min), looking back
  at most 5 minutes; otherwise the day is skipped for that leg. A signal uses prices up to T; the entry fills at the
  price at T+1 min; latency variant T+2 min. Scheduled exits fill at the price at the exit time.
- Cost per leg (round trip) = half the spread at the entry minute + half at the exit minute (actual panel spreads, in
  bp of mid) + 0.6 bp commission for FX and metals; 0 for indices, energies, crypto. No position crosses 20:55 UTC,
  so no swap.
- Statistics: mean bp per trade at mid and net; t clustered by UTC day (per-day sums, cluster-robust SE of the
  per-trade mean). Robustness: the same with each leg's mid return clipped at the IS 0.1 / 99.9 percentiles of its
  family-symbol (rule fixed now, to guard against spiky CFD quotes). Per-trade net Sharpe = net mean / net sd; power
  = Sharpe x sqrt(trades per year x 1.73); also day-clustered power = per-day Sharpe x sqrt(days per year x 1.73).
- Chance: per family, 1,000 permutations that flip the sign of each UTC day (shared by every cell and symbol of the
  family) and record the max |t_IS| over the family's cells; the observed best |t_IS| is compared with the null's
  median and 95th percentile.
- Random-entry control (for any cell net > 0 in IS and VAL): same trade count, side rule and hold, start times drawn
  at random within +-3 h of the real clock on random weekdays of the same era, the side recomputed from the same
  signal construction at the random time; 200 seeds.
- Selection: within each family the IS cell with the best net day-clustered t among cells with IS mid t >= 2 on the
  registered side is "selected" and checked once in VAL. Other cells' VAL numbers are reported, not selected.
- Bars: the brief's LIVE / DEMO bars, unchanged.

## K1 FX intraday time-series momentum into the London 16:00 close (and the Tokyo close), 2026-10-06 01:12 UTC

Sources: Elaut, Frömmel & Lampaert (2018, J. Financial Markets 37, doi 10.1016/j.finmar.2016.09.002): in RUB/USD the
first half-hour predicts the last half-hour, from liquidity provision / late informed trading; Li, Sakkas & Urquhart
(2022, JFM, doi 10.1016/j.finmar.2021.100619): intraday TS momentum in 16 markets, stronger when liquidity is low
and volatility high; Seeck (2026, SSRN 7008318): intraday momentum in spot FX and currency futures, amplified in
JPY (abstract not retrievable; title only). Gao, Han, Li & Zhou (2018) is the origin.
Mechanism: hedgers, benchmark (fix) orders and dealers unloading the day's inventory trade in the direction of the
day's move near the session's close; in FX the London 16:00 WM/R fix is the close where they concentrate.
How it differs from what was tested: rounds 3-10 tested the fix windows unconditionally (round 3, round 4 scan), on
volatile days without a direction from the day's move (round 10 E1), and the US-equity move -> USD at the fix (U1).
The FX pair's own intraday move as the predictor has never been used.
Why it could escape the limits: a daily conditional signal in 10 pairs (~2,500 trades a year) at minutes when FX
spreads are near zero; if the paper-sized slope holds it would add 1-2 bp on the conditional days.
Rule (side = follow, fixed by the papers):
- P1 = ln P(08:30 London) - ln P(08:00 London) (first half-hour of London).
- P2 = ln P(15:30 London) - ln P(23:00 UTC of the previous day) (the whole Asian + European day).
- Entry 15:30 London (+1 min), exit 16:00 London, side = sign(P). Pairs: AUDJPY AUDUSD EURJPY EURUSD GBPJPY GBPUSD
  NZDUSD USDCAD USDCHF USDJPY. UK and US public holidays dropped.
- P3 (Tokyo close, JPY pairs only, Seeck's JPY amplification) = ln P(05:30 UTC) - ln P(00:00 UTC); entry 05:30 UTC
  (+1), exit 06:00 UTC (15:00 Tokyo close); USDJPY EURJPY GBPJPY AUDJPY; Japanese holidays dropped.
- Conditions: all days; high-volatility days (realised vol of 1-min mid returns over the predictor window in the
  top tercile of its trailing 60 values); big signals (|z(P)| >= 1, z from the trailing 60 values).
- Cells: P1, P2 x 10 pairs x 3 conditions = 60; P3 x 4 x 3 = 12; pooled (all pairs, equal weight) P1/P2/P3 x 3 = 9.
  81 cells.

## K3 Opening-range reversal in the US index CFDs (0DTE hedging), 2026-10-06 01:12 UTC

Source: Ladia (2026, SSRN 7124578), "Opening-Range Reversal in Dow Jones Futures: Evidence Consistent with 0DTE
Hedging Pressure" (abstract not retrievable; side from the title: reversal). Context: SPX daily expiries since
2022-05; 0DTE above 40 % of SPX option volume from 2023.
Mechanism: dealers who are net long same-day gamma hedge against the opening move (sell rallies, buy dips), so the
opening range reverses within the next hour.
How it differs: round 11 H scanned unconditional 15/60-min slots; round 6 S5 faded 5-min > 2 sd shocks all day
(no 0DTE split); round 4 followed 09:30-11:30 into 13:00. The fade of the opening range itself, with a 0DTE-era
split, was not tested.
Why it could escape: daily, US30 costs ~0.3 bp in VAL; a gamma-driven reversal after big opening moves could be
several bp.
Rule: OR_k = ln P(09:30+k ET) - ln P(09:30 ET), k in {15, 30} min; entry 09:30+k (+1 min), side = -sign(OR_k),
exit after h in {30, 60} min. Conditions: all days; |OR_k| >= 1 sd of its trailing 60 values. NYSE holidays dropped.
Eligible: US30, USTEC (US500 is on the round-3 contamination list: not used). 2 x 2 x 2 x 2 = 16 cells.
Control (reported, not selectable): UK100 with the 08:00 London open, same k/h/conditions (8 cells; no 0DTE there).
Mechanism check (reported): VAL, and 2022-05..2024-12 vs 2016-01..2022-04, should be at least as strong as IS.

## K4 Deribit 08:00 UTC option-expiry reversal in bitcoin, 2026-10-06 01:12 UTC

Sources: Weiss, Gaudiosi, Zhou & Webb (2026, Finance Research Letters 110340, doi 10.1016/j.frl.2026.110340):
"statistically and economically significant return reversal around expiration" of Deribit BTC options, strongest
with high ATM open interest and negative gamma; Weiss, Gaudiosi & Zhou (2024, SSRN 5012508); Hoang & Phan (2026,
FRL 110008): Deribit activity peaks 08:00-09:00 GMT from the rollover at the 08:00 settlement.
Mechanism: settlement = 30-min average of the Deribit index 07:30-08:00 UTC; hedges of expiring options are traded
into the settlement and unwound after it, so the move into 08:00 reverses.
How it differs: round 3 tested mean returns around perpetual-funding times (00/08/16 UTC, <= 3 bp, no sign); never a
conditional reversal at the option expiry, nor the Friday (weekly/monthly expiry) split.
Why it could escape: BTC moves 30-80 bp an hour; a reversal of a fixed fraction of the pre-expiry move on the large
Friday expiries could exceed IC's 3-7 bp BTC spread.
Rule: m = ln P(08:00 UTC) - ln P(07:00 UTC); entry 08:00 (+1 min), side = -sign(m), exit 08:30 or 09:00 UTC. Day
types: Fridays (weekly + monthly + quarterly expiries), last Friday of the month (monthly/quarterly), Mon-Thu
(daily expiries only; also the funding-time control, since 08:00 UTC is a funding time every day). Conditions: all,
|z(m)| >= 1 (trailing 60 same-type days). BTC eligible: 3 x 2 x 2 = 12 cells. ETH for information (IS spread
~115 bp).
Mechanism check (reported): Friday minus Mon-Thu.
Disclosure: round 3 printed 2025-26 hour-of-day means for BTCUSD; this is a conditional reversal, not an hour mean,
but the lead should weigh it if anything passes.

## K5 CME bitcoin futures expiry: the CF BRR settlement window, 2026-10-06 01:12 UTC

Source: Blasco, Corredor & Satrústegui (2023, IREF, doi 10.1016/j.iref.2023.02.013): monthly expiry effect in
bitcoin volume, volatility and returns, strongest shortly before and after the expiry time (no direction in the
abstract). CME BTC futures (from 2017-12) settle on the last Friday of the month (business day before if a UK
holiday) to the CME CF Bitcoin Reference Rate, computed over 15:00-16:00 London.
Mechanism and side (mine, from the basis trade, written before looking): cash-and-carry holders (long spot, short
futures) who do not roll sell spot across the BRR window to match the settlement, so BTC is pressed down 15:00-16:00
London and rebounds after.
Rule: leg A short BTC 15:00 -> 16:00 London; leg B long 16:00 -> 17:00 London; on CME expiry Fridays 2018-2024.
2 cells (A, B) + the A+B pair reported. ETH (CME ETH futures from 2021-02) for information. Placebo: the same clock
on the other Fridays. ~12 events a year: DEMO tier at most.

## K6 Crude-oil intraday momentum into the settlement, the papers' predictors, 2026-10-06 01:12 UTC

Sources: Wen, Gong, Ma & Xu (2020, Economic Modelling, doi 10.1016/j.econmod.2020.03.004): the first half-hour
return (with the overnight) predicts the last half-hour of the WTI pit session; Wen, Indriawan, Lien & Xu (2022,
Energy Journal, doi 10.5547/01956574.44.4.zwen): on EIA days the third half-hour (10:30-11:00 ET) predicts the last
half-hour; on other days only the first half-hour does.
How it differs: round 6 S1 used everything since the previous settlement up to w minutes before it (w = 5-120);
round 6 S2 followed the first 5 minutes after EIA to 11:30 / 14:30. The papers' predictors and the 30-min target were
not used.
Why it could escape: daily in two energies (no commission); a targeted predictor could be stronger than S1's.
Rule: non-EIA weekdays: r1 = ln P(09:30 ET) - ln P(14:30 ET previous trading day); EIA Wednesdays (weeks with a
federal holiday on Mon-Wed dropped): r3 = ln P(11:00 ET) - ln P(10:30 ET). Entry 14:00 ET (+1), exit 14:30 ET (XTI);
XBR: entry 19:00 London (+1), exit 19:30 London. Side = sign(r). Conditions: all, |z| >= 1 (trailing 60 same-type
days). 2 symbols x 2 day types x 2 conditions = 8 cells. Good Friday and US federal holidays dropped.

## K7 Precious-metal intraday momentum with the first half-hour predictor, 2026-10-06 01:12 UTC

Source: Jin, Kearney, Li & Yang (2019, J. Futures Markets, doi 10.1002/fut.22084): first half-hour predicts the last
half-hour, strongest in metals. Near-tested: round 6 S1 (gold slope t +6.8 / +2.6) used the whole day as predictor.
Rule: XAU r1 = ln P(08:50 ET) - ln P(13:30 ET previous day), entry 13:00 ET (+1), exit 13:30 ET; XAG r1 = ln P(08:55
ET) - ln P(13:25 ET previous day), entry 12:55 (+1), exit 13:25. Side = sign(r1). Conditions: all, |z| >= 1. 4 cells.
Gold hour-of-day is on the round-3 contamination list; this is a conditional sign, not an hour mean (disclosed).

## Declared cell count

K1 81, K3 16 (+8 control), K4 12 (+ETH information), K5 2, K6 8, K7 4: 123 eligible cells.

## Outcome of the first pass (2026-10-06 01:16 UTC)

K1, K3, K5, K6, K7: no cell on the registered side reaches IS net t 2 (details in STREAM_K.md). K4: the selected cell
(BTC, Fridays, fade 08:01 -> 09:00 UTC, all days) is positive at mid in IS and VAL, net > 0 in both, but IS net t is
about 1, below the DEMO bar; Mon-Thu goes the other way. Nothing is pre-registered from these numbers.

## K4 diagnostics, POST HOC (written 2026-10-06 01:16 UTC, after the K4 first-pass numbers, before these)

Purpose: decide whether the Friday 08:00 UTC reversal is an expiry effect or a generic Friday / time-of-day pattern,
and report it for the next round. None of these can make K4 a candidate from IS/VAL; they are diagnostics.
- D1 time placebo on Fridays: the same rule with the clock shifted to h0 in {04, 05, 06, 07, 09, 10, 11, 12} UTC
  (predictor h0-1h -> h0, fade h0+1 min -> h0+60), the side recomputed at each shift; same for Mon-Thu.
- D2 by year 2018-2024 (Fridays, 60 min); Friday minus Mon-Thu, day-level difference with its t.
- D3 random-entry control: 200 seeds; each seed draws, for every real Friday trade, a random start minute within
  +-3 h of 08:00 UTC on a random Friday of the same era, recomputes the side from the prior 60 minutes and holds 60 min.
- D4 sensitivity (reported, not selectable): predictor 07:30 -> 08:00 (the settlement TWAP window) and 06:00 -> 08:00;
  exit at 08:45 and 09:30; quarterly expiries (last Friday of Mar/Jun/Sep/Dec) separately.
- D5 ETH on the same rule at mid (cost reported; IC's ETH spread made it untradeable in IS).

Timestamp note (2026-10-06 01:17 UTC): the first entries were stamped 01:15 / 01:58 by mistake; the file was written at
about 01:12 UTC (before any script ran; the first output file is from 01:14 UTC) and the post-hoc section at 01:16
UTC. The stamps above are corrected; the order of entries was always right.
