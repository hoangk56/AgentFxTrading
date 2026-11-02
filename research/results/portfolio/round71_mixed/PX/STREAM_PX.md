# STREAM_PX: PAXG over the weekend vs gold's reopen

Written 2026-11-01 18:01 UTC (from `date -u`). Hypotheses and the 6 declared cells: [HYPOTHESES_PX.md](HYPOTHESES_PX.md)
(17:57 UTC, placebo addendum 17:58 UTC, both before any return was computed). HOLD not opened, no 2025-26 data read.

## Answer: none (no LIVE, no DEMO)
- **Cheap side (the declared primary, buy PAXG when w <= -k): fails.** Only 5 IS weekends at k 30 (1 at k 60), so IS
  cannot reach t 2.0 by construction, and VAL is net negative in every cell (k 30: -7.7 / -12.4 bp, t -1.1 / -1.9;
  k 60: -13.9 / -33.7 bp). PAXG does drift back up after a cheap Sunday (gross +13 to +17 bp at k 30 in VAL, t 2.0-2.5),
  but less than the ~25 bp round trip (20 bp fees + ~5 bp spreads).
- **Rich side (sell held PAXG when w >= +k, rebuy; reported separately): positive net, far below the bars.** S60-X4h:
  IS +19.3 bp (t 1.14, n 13), VAL +9.2 bp (t 0.61, n 16); S30-X4h: IS -4.6 (t -0.45), VAL +5.5 (t 0.61). Neither is
  positive at costs x1.5 in VAL. HOLD power at VAL size is ~0.5 (about 10-18 trades in HOLD).
- **The wedge is real at mid and weekend-specific**, it just costs more to trade than it gives back. Pooled 2020-24,
  gross reversion S30 +26 bp (t 3.86), S60 +39 bp (t 3.56), L30 +17 to +21 bp (t 2.8-3.1). On weekday nights (gold
  quoted up to the daily break) the same signal has no rich-side reversion (S60 VAL gross -11 bp). Gold's reopen gap
  moves only 9-17 % of the way toward PAXG (corr(w, gap) +0.36), and PAXG gives back ~25-28 % of w by R + 4 h. About
  half the deviation is still there at Monday 06:00 UTC.

## Data
- Binance spot PAXGUSDT 1m klines and aggTrades (weekend windows Fri 18:00 .. Mon 08:00 UTC kept), data.binance.vision
  monthly files 2020-08 .. 2024-12: 106 GETs + 6 HEADs + robots.txt (404), all 200, 219 MB downloaded, 44 MB of npz
  kept, zips deleted ([requests.log](../../../../data/paxg_weekend/requests.log)). No PAXG perp before 2025-03-27
  (perp_1d), XAUTUSDT spot only from 2026: neither usable.
- IC XAUUSD M1 mid (bid close + ask close) / 2 for the Friday anchor and the reopen.

## Weekends and deviation sizes
Weekends with PAXG listed and gold shut: **IS 70** (2020-08-28 .. 2021-12-24; 18 in 2020, 52 in 2021), **VAL 157**
(2022-24; the 2021-12-31 weekend has T in 2022). 17 are irregular (gap > 52 h: Thanksgiving, Christmas / New Year,
Good Friday, the Mon 00:33 / 02:08 IC reopens); excluding them changes nothing material (table below is all weekends).

w = ln(PAXG at Sunday 21:00 / PAXG at gold's last Friday bar), bp:

| era | p1 | p5 | p10 | p25 | p50 | p75 | p90 | p95 | p99 | sd | share <= -30 | <= -60 | >= +30 | >= +60 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IS | -55 | -34 | -17 | -11 | +11 | +41 | +80 | +149 | +278 | 64 | 0.07 | 0.01 | 0.36 | 0.19 |
| VAL | -82 | -59 | -39 | -17 | +0 | +25 | +60 | +69 | +185 | 55 | 0.17 | 0.05 | 0.19 | 0.10 |

Per year sd / median |w|: 2020 47 / 18, 2021 68 / 27, 2022 40 / 17, 2023 52 / 26, 2024 68 / 25. 2021 is skewed rich
(21 of 52 weekends >= +30 bp: crypto bull market, PAXG bid up with crypto), so IS has almost no cheap weekends.

## Measured cost
Half-spread from aggTrades (consecutive opposite-side trades within 5 s, +-5 min window), median / p90 bp:
IS entry 2.80 / 5.24, exit R+30 1.88 / 4.59, exit R+4h 1.90 / 3.26; VAL 2.52 / 2.87, 2.44 / 2.86, 2.50 / 2.92.
Measured in 36-50 % of windows (the rest use the era median). Roll check at entry: IS 1.71, VAL 2.00 bp. Median 3-4
trades in the entry minute and **$6-9k of quote volume in the 11 minutes around Sunday 21:00**: capacity is a few
thousand dollars per weekend even if it worked. Round trip used: 20 bp fees + ~4.5-5 bp spreads.

## Declared cells (net bp per trade after fees + measured spreads + DFF on capital)

| cell | era | n | net | t | SR | gross | x1.5 | 1 bar late | R1 random % | by year (net, n) |
|---|---|---|---|---|---|---|---|---|---|---|
| L30-X30 | IS | 5 | +14.9 | 0.65 | 0.29 | +39.1 | +2.8 | +3.9 | 98.9 | 2020 -14.2 (2), 2021 +34.3 (3) |
| L30-X30 | VAL | 26 | -7.7 | -1.12 | -0.22 | +17.3 | -20.1 | -8.0 | 100.0 | 2022 -5.3 (5), 2023 -1.3 (13), 2024 -19.5 (8) |
| L30-X4h | IS | 5 | +13.5 | 0.87 | 0.39 | +38.0 | +1.2 | +2.5 | 99.2 | 2020 +14.8 (2), 2021 +12.6 (3) |
| L30-X4h | VAL | 26 | -12.4 | -1.91 | -0.38 | +13.0 | -24.9 | -12.7 | 98.4 | 2022 -5.9, 2023 -6.7, 2024 -25.6 |
| L60-X30 | IS | 1 | -15.7 | - | - | +9.0 | -28.0 | -50.5 | 65.5 | 2020 -15.7 (1) |
| L60-X30 | VAL | 8 | -13.9 | -2.48 | -0.88 | +10.7 | -26.1 | -14.0 | 89.1 | all years < 0 |
| L60-X4h | IS | 1 | +17.9 | - | - | +42.6 | +5.6 | -16.9 | 94.7 | 2020 +17.9 (1) |
| L60-X4h | VAL | 8 | -33.7 | -3.82 | -1.35 | -8.5 | -46.1 | -33.8 | 31.9 | all years < 0 |
| S30-X4h | IS | 25 | -4.6 | -0.45 | -0.09 | +20.8 | -17.3 | -2.8 | 94.9 | 2020 +4.2 (4), 2021 -6.3 (21) |
| S30-X4h | VAL | 30 | +5.5 | 0.61 | 0.11 | +30.7 | -7.1 | +6.7 | 100.0 | 2022 +14.7 (7), 2023 -0.8 (9), 2024 +5.0 (14) |
| S60-X4h | IS | 13 | +19.3 | 1.14 | 0.32 | +44.8 | +6.5 | +22.6 | 99.7 | 2020 +43.0 (1), 2021 +17.3 (12) |
| S60-X4h | VAL | 16 | +9.2 | 0.61 | 0.15 | +34.6 | -3.5 | +11.4 | 100.0 | 2022 +8.5 (5), 2023 +16.0 (5), 2024 +4.0 (6) |

R1 = % of 2,000 draws of the same number of random weekends (same side, same clock) with a lower mean net. It is
high everywhere because an unconditional weekend trade just pays the ~25 bp cost; it shows the conditioning matters,
not that the cells pay. Max-over-cells null (w permuted within era, 2,000 times): IS best t +0.87 (long cells, null
95 % +0.28, p 0.006) / +1.14 over all 6 (p 0.003); VAL best long t -1.12, best of 6 +0.61 (p 0.008). The signal
beats a shuffled signal; the bar it fails is the t level (DEMO needs IS t >= 2.0).

Gross (pre-cost) t: L30-X30 IS 1.70 / VAL 2.53, L30-X4h 2.37 / 2.01, S30-X4h 2.02 / 3.37, S60-X4h 2.68 / 2.30.
At zero cost S60-X4h would meet the DEMO numbers; at the real 25 bp it does not.

Power at VAL size (HOLD ~95 weekends x VAL trigger share): L30 ~16 trades (SR < 0), L60 ~5, S30 ~18 (power 0.47),
S60 ~10 (power 0.48). LIVE needs >= 3: out of reach for any cell.

## Path from Friday close to Monday 06:00 by w bucket (means, bp)
Premium = ln(PAXG / (gold mid x Friday ratio)); at T it equals w.

| era | bucket | n | w | gold reopen gap | PAXG T->R+30 | T->R+4h | T->Mon 06 | premium R+30 | R+4h | Mon 06 |
|---|---|---|---|---|---|---|---|---|---|---|
| IS | <= -60 | 1 | -62 | -7 | +9 | +43 | -1 | -59 | -56 | -50 |
| IS | -60..-30 | 4 | -42 | +8 | +47 | +37 | +17 | +2 | -18 | -36 |
| IS | -30..+30 | 40 | +1 | +1 | 0 | -5 | -2 | 0 | -1 | -1 |
| IS | +30..+60 | 12 | +41 | +3 | -23 | +5 | 0 | +15 | +23 | +20 |
| IS | >= +60 | 13 | +130 | +17 | -10 | -45 | -22 | +105 | +68 | +88 |
| VAL | <= -60 | 8 | -87 | -10 | +11 | -9 | -20 | -65 | -65 | -57 |
| VAL | -60..-30 | 18 | -40 | -3 | +20 | +23 | +30 | -32 | -24 | -20 |
| VAL | -30..+30 | 101 | +1 | +1 | +1 | +2 | 0 | 0 | +1 | +2 |
| VAL | +30..+60 | 14 | +47 | -7 | -12 | -26 | -43 | +44 | +42 | +38 |
| VAL | >= +60 | 16 | +109 | +21 | -13 | -35 | -41 | +74 | +65 | +54 |

Slope of gold's reopen gap on w: IS +0.09, VAL +0.17; slope of PAXG T -> R+4h on w: IS -0.25, VAL -0.28.
Reading: weekend PAXG moves carry a little information about gold's reopen, most of the move is noise, and it mean
reverts only slowly (at Monday 06:00 about half the deviation remains). Large cheap weekends (<= -60) keep falling in
VAL. The premium persisting into Monday fits the redemption anchor: creating / redeeming PAXG at Paxos needs business
days and an account, so nothing forces it back within hours.

## Placebo P: weekday nights (gold quoted until the daily break)
Wed / Thu nights only (Mon / Tue nights have a weekend inside the 48 h window and drop out), w' = 48 h change in the
PAXG premium, same thresholds, entries and exits, spreads = weekend era medians (conservative; weekday books are
deeper). IS 128 / VAL 282 nights. Long: L30-X30 VAL gross +6.1 (net -19.0, t -6.8), L60-X4h VAL gross +14.1. Rich
side: S30-X4h VAL gross -5.9, S60-X4h VAL gross -11.2. The rich-side reversion (+31 / +35 bp gross in VAL weekends)
does not exist when gold is quoted, so the weekend effect is not just PAXG premium mean reversion.

## What failed and why
- Cost: 20 bp of Binance spot taker fees plus ~5 bp of spread vs a 13-45 bp gross reversion with a 60-80 bp sd per
  trade. The effect is real at mid; after cost the t is 0.6-1.1 at best.
- Sample: 70 IS weekends, and 2021's crypto bull market left only 5 cheap weekends in IS. The long side can never
  reach IS t 2.0 with 5 trades. I did not redefine the split.
- Large cheap deviations (<= -60 bp) keep going down after the reopen in VAL (net -34 bp): that side is crypto
  de-risking, not noise.
- Capacity: ~$6-9k trades in the 11 minutes around Sunday 21:00. Even a working rule would be a few-thousand-dollar
  trade.

## Pitfalls
- w reduces to PAXG's own weekend return (the Friday ratio cancels): the gold leg matters only at the reopen.
- Binance spot klines include zero-trade minutes with o = h = l = c = previous close (624k of 2.28M bars); 1,424
  minutes are missing (maintenance): forward-filled. The entry-minute "price" is often a stale last trade; the
  half-spread charge covers that only on average.
- aggTrades were kept for weekend windows only; Monday-21:00 entries (Christmas / New Year Monday reopens) and weekday
  placebo nights use era medians.
- IC gold reopen minutes: Sunday 22:02 / 23:02 UTC, but 2023-02-20 00:33 and 2023-09-04 02:08 (late IC quotes on US
  holidays) and Monday 23:02 at Christmas / New Year 2022-23. T is defined relative to R, not to Sunday.

## What a user decision could unlock
- A cheaper PAXG venue (maker or zero-fee): at zero cost S60-X4h meets the DEMO numbers (IS gross t 2.68, VAL 2.30),
  but n stays ~10-16 a year and capacity is thousands of dollars. Low value.
- The PAXG USDT-M perp (from 2025-03, 5 bp taker, shortable) would make the rich side tradable without holding PAXG,
  but it has no pre-2025 history: it could only be a forward registration (not drafted: the spot version is below
  the bars).

## Files
- [HYPOTHESES_PX.md](HYPOTHESES_PX.md), this file.
- code/pull.py (download, run with python -I), code/px.py (all tables; output code/px.out), code/extra.py (gross t,
  Roll, power; output code/extra.out).
- Data: research/data/paxg_weekend/npz/kl_YYYY-MM.npz, ag_YYYY-MM.npz, events_weekend.npz, requests.log.
- No PREREG_DRAFT (no cell passed IS / VAL).
