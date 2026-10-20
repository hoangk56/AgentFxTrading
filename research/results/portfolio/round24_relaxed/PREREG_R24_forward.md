# PREREG (round 24, forward): F3 and E1 on data after 2026-09-24 (FWD)

Registered 2026-10-15 17:02 UTC (`date -u`), before any price after 2026-09-24 was fetched or loaded. After the round
24 report the user chose to fetch data after 2026-09-24 (2026-10-15, option 2: "dữ liệu sau 2026-09-24").

## What is read
- FWD = 2026-09-25..2026-10-14 (the last full UTC day before registration): 14 weekdays. Expected trades: F3 ~4-5
  (one day in three), E1 14.
- Rules exactly as registered: F3 in [PREREG_R24_relaxed_hold.md](PREREG_R24_relaxed_hold.md) (E1 on USD-TOP days, the
  250-day selector history runs through the IC data), E1 in
  [round13_structural/PREREG_M_eurusd_midday.md](../round13_structural/PREREG_M_eurusd_midday.md). Nothing is chosen
  here.
- Data: IC M1 (research/data/m1) up to 2026-09-24 23:59 UTC, Dukascopy M1 bid + ask for EURUSD, USDJPY, USDCHF from
  2026-09-25 (zero-volume minutes = no bar). Costs: (a) Dukascopy's own spread at each quote + 0.6 bp; (b) IC's median
  spread at the same UTC minute over 2026-07-01..2026-09-24 + 0.6 bp. (b) is the IC-equivalent reading.
- A calibration check on the overlap 2026-08-03..2026-09-24 (before FWD) compares Dukascopy with IC at the quote
  minutes.

## Bars
None gate anything: at ~5 trades F3's FWD t has sd ~1 around an expected ~0.4 at the HOLD size. FWD is reported (n,
mid, net, x1.5, +1 minute, each trade) and pooled with HOLD (HOLD + FWD), the statistic of the promotion rule. FWD is
the first slice of a rolling forward log: the same code is rerun with a later last date as data accumulates, each
rerun appended below with its date, nothing above edited. FWD does not replace a demo: it has no fills.

## Code (sha256, first 16 hex; copies in prereg_code/)
- `fwd_r24.py.txt` c30c663bc8c13980 (reproduces HOLD exactly on the IC panel before registration: F3 n 117 net +2.00
  t 2.16; E1 n 444 net +0.64 t 0.99)
- `build_panel_fwd.py.txt` 49259065a10feca4
- `calib.py.txt` 552c72a334f705db
- `duka_dl.py.txt` 48c0dcd267209d94 (stream B's downloader with an end-date cap)
- `clib.py.txt` e66aa4f31f7e29c2, `eng.py.txt` beb456eba773d396 (unchanged from the HOLD run)

Run: `DUKA_LAST=2026-10-14 duka_dl.py <dir> EURUSD:2026-2026,USDJPY:2026-2026,USDCHF:2026-2026 4 8-10 wd`, then
`build_panel_fwd.py`, `calib.py`, and `R24_PANEL=<panel>/{duka,icspr} fwd_r24.py 2026-10-14`.

## FWD result
(appended after the run, below this line; nothing above edited)

### Slice 1: FWD 2026-09-25..2026-10-14 (run 2026-10-15 17:08 UTC)
Dukascopy fetched 17:03-17:07 UTC (EURUSD, USDJPY, USDCHF, 2026-08-03..2026-10-14 weekdays; FWD days complete; four
EURUSD days of 7-12 August missing and four early-August days without ASK, all in the calibration window). Code
unchanged (`cmp` against prereg_code/). Output: [prereg_code/fwd_output_2026-10-14.txt](prereg_code/fwd_output_2026-10-14.txt),
[prereg_code/calib_output_2026-10-14.txt](prereg_code/calib_output_2026-10-14.txt).

Calibration (2026-08-03..09-24, minute by minute): median |mid difference| Dukascopy vs IC 0.04 bp (EURUSD), 0.06
(USDCHF), 0.03 (USDJPY); Dukascopy's spread at the quote minutes is wider (EURUSD 0.26 bp vs IC 0.00-0.09; USDCHF
~1.0 vs 0.12-0.25), so cost (a) is conservative and (b) is the IC-equivalent.

| rule | era | n | mid (t) | net (a) Duka spread (t) | net (b) IC spread (t) | x1.5 (b) | +1 min (b) |
|---|---|---|---|---|---|---|---|
| F3 | FWD | 2 | -8.51 | -9.45 | -9.18 | -9.21 | -12.44 |
| F3 | HOLD + FWD | 119 | +2.44 (2.56) | +1.81 (1.89) | +1.81 (1.89) | +1.79 | +1.16 |
| E1 | FWD | 14 | -2.29 (-0.64) | -3.13 (-0.87) | -2.95 (-0.82) | -2.99 | -3.82 |
| E1 | HOLD + FWD | 458 | +1.17 (1.83) | +0.52 (0.82) | +0.53 (0.83) | +0.51 | -0.12 |

- F3 traded 2 of 14 days (1 October -30.9 bp, 7 October +12.5), fewer than the ~5 expected; E1's 14 trades (b):
  09-25 -10.5, 09-28 -0.6, 09-29 -16.4, 09-30 +6.4, 10-01 -30.9, 10-02 +15.3, 10-05 +0.7, 10-06 -24.0, 10-07 +12.5,
  10-08 +3.1, 10-09 +6.1, 10-12 +4.0, 10-13 -7.2, 10-14 +0.2.
- Reading: too few trades to say anything about either rule (F3's FWD per-trade sd is ~10-20 bp; two trades carry
  no information). Both are negative in this slice, which continues F3's 2026 weakness (-0.91 over 48 HOLD trades).
  HOLD + FWD for F3 is now net +1.81 (t 1.89); the promotion rule needs 2.5 with demo trades.

### Slice 2: FWD 2026-09-25..2026-10-16 (run 2026-10-17 19:20 UTC)
Dukascopy fetched 18:55-19:20 UTC into a new directory (EURUSD, USDJPY, USDCHF, 2026-08-03..2026-10-16 weekdays). The
first pass hit many HTTP 503s (USDJPY lost 2026-10-02 and the ASK of 2026-10-01, both FWD days); USDJPY, then EURUSD
and USDCHF, were fetched again into a fresh directory with no FWD day missing (EURUSD lacks 2026-08-03 and the ASK of
08-06, both in the calibration window). Panel T0 2024-01-01, cut 2026-09-25, end 2026-10-17 (exclusive), IC spread
reference 2026-07-01..09-24. Code unchanged (`cmp` against prereg_code/). Slice 1 reproduces trade by trade. Output:
[prereg_code/fwd_output_2026-10-16.txt](prereg_code/fwd_output_2026-10-16.txt),
[prereg_code/calib_output_2026-10-16.txt](prereg_code/calib_output_2026-10-16.txt) (median |mid difference| 0.04 /
0.06 / 0.03 bp for EURUSD / USDCHF / USDJPY, as in slice 1).

| rule | era | n | mid (t) | net (a) Duka spread (t) | net (b) IC spread (t) | x1.5 (b) | +1 min (b) |
|---|---|---|---|---|---|---|---|
| F3 | FWD | 2 | -8.51 | -9.45 | -9.18 | -9.21 | -12.44 |
| F3 | HOLD + FWD | 119 | +2.44 (2.56) | +1.81 (1.89) | +1.81 (1.89) | +1.79 | +1.16 |
| E1 | FWD | 16 | -1.61 (-0.50) | -2.46 (-0.77) | -2.27 (-0.71) | -2.31 | -3.32 |
| E1 | HOLD + FWD | 460 | +1.18 (1.85) | +0.53 (0.84) | +0.54 (0.85) | +0.52 | -0.12 |

- New days: 2026-10-15 and 10-16 were not USD-TOP days (no F3 trade); E1 (b) 10-15 +8.0, 10-16 -3.0.
- Reading: unchanged, too few trades. F3 has had no trade since 7 October.
