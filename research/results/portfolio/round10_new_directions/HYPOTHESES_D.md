# Round 10, stream D (lead): hypotheses, each written before its numbers

## D0 feasibility frontier (2026-10-05 17:58 UTC; descriptive, not a hypothesis test)
For each symbol and hold length (15 min, 1 h, 4 h, 1 day), from IS 2016-21 mid returns of the shared panel: the
per-trade sd of the hold's return (bp) and the median executable cost (half spread in + half out at liquid hours,
plus 0.6 bp commission for FX/metals). From these, the gross edge per trade a rule would need for LIVE power 3 at one
trade a day (~430 HOLD trades: net Sharpe >= 0.145) and at one a week (~90: >= 0.32), assuming independent trades.
Purpose: say which symbol x horizon classes can reach the LIVE bar at all.

## D1 FX option pinning into the 10:00 New York cut (2026-10-05 17:58 UTC)
Mechanism: OTC FX options expire daily at the 10:00 New York cut; strikes cluster at round numbers (big figures and
50-pip levels). Dealers long gamma near a large strike sell rallies and buy dips, pinning spot to the strike into
the cut; the hedges unwind after it (Ni, Pearson & Poteshman 2005 for equity options; FX market commentary on
"expiries"). Round 3 tested stop/take-profit clustering at round numbers (Osler) after a cross, and round 4 scanned
the 10:00 NY cut by time only; neither conditioned on the distance to a round strike at the cut.
Why it could escape the limits: daily (~250 events a year per pair, 6 pairs), short window (1 h, low sd), and the
signal is conditional, so the move per event can be larger than the unconditional 10:00 pattern.
Rule (side fixed by the mechanism): at 09:00 NY (DST-aware), L = nearest 50-pip level (JPY pairs: 0.50 yen); if the
mid is within d of L, d in {5, 10, 20} pips, trade toward L from 09:01 to 09:59 NY (exit at 09:59 or when the mid
touches L, whichever first; screen version: to 09:59). Post-cut leg (reported, separate): away from L from 10:00 to
11:00 NY. Pairs EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF. Control: the same rule at 07:00 and 12:00 NY (no
cut), and on US holidays. Mid first, then actual spreads + 0.6 bp. IS 2016-21 to choose d, VAL 2022-24 once.

## D2 index option pinning into the US close on expiry days (2026-10-05 18:20 UTC; written after D1's numbers, before D2's)
Mechanism: SPX/NDX options expire at the 16:00 ET close (weekly Fridays since 2016, Monday/Wednesday weeklies, daily
from 2022-05); dealers long gamma near large round strikes pin the index into the close (Ni, Pearson, Poteshman &
White 2021 for single stocks; Golez & Jackwerth 2012 for S&P 500 futures). Round 7 tested monthly US500 expiry
pinning only (-1.44 bp, t -1.0). Rule: at 15:00 ET, L = nearest 25-point level for US500 (100 for USTEC); if within
d points (US500 d in {3, 5, 10}; USTEC {15, 25, 50}), trade toward L 15:01 -> 15:58 ET. Days: Fridays 2016-2021 and
every weekday from 2022-05 (daily expiries); control: non-expiry weekdays before 2022-05 and the same rule at 13:00
ET. US30 (DJX options are tiny) as a no-pin control. Mid first, then actual spreads.

## D3 the "overnight drift" at the European open (2026-10-05 18:30 UTC; before its numbers)
Mechanism and source: Boyarchenko, Larsen & Whelan (2023, "The Overnight Drift", RFS): E-mini S&P 500 returns
1998-2019 are concentrated in the hour after the European open, 02:00-03:00 ET, as dealers who absorbed customer
selling the previous afternoon lay off inventory when European liquidity arrives. Round 4 tested only the whole
18:30 -> 04:00 ET window (US30 +2.0 bp, t 1.4 / +0.4) and a late-sell-off condition. Side: long (paper). Window
fixed by the paper: 02:00 -> 03:00 ET (DST-aware, New York). Symbols: US30, USTEC (US500 and DE40 are on the
round-3 hour-of-day contamination list, reported for information only, not eligible). Unconditional, and
conditional on the 14:00-16:00 ET return of the previous day < 0 (the paper's inventory condition). Cost: actual
spreads at 02:00 and 03:00 ET (overnight index spreads are wide). Why it could escape: daily, 1-hour window, and a
documented concentration of the whole equity premium (~3-4 bp a night in the paper) in that hour.
