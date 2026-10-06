# Round 13, stream P: hypotheses (written before any number)

Written 2026-10-06 01:29 UTC (`date -u`), before any return of this stream was computed. The only thing looked at
before writing is quote coverage at the benchmark minutes (share of weekdays with a real bar; coverage.py), no returns.
HOLD (2025-01-01 onwards) is not in the panel and is cut at load for the US2000 cache.

## Mechanism and source
Flows proportional to the day's move are executed at a close or settlement:
- leveraged and inverse ETFs rebalance at the close by L(L-1) x AUM x the day's return (Cheng & Madhavan 2009;
  Ivanov & Lenkey 2014/2018; Baltussen, Da, Lammers & Martens 2021 add short-gamma hedging, same sign);
- settlement-benchmarked / trade-at-settlement and MOC orders that follow the day.
Both are fixed by prospectus or benchmark rules, so they should not decay the way discretionary flows do, unless
liquidity providers learn to pre-position (a decay channel; reported by year and as the VAL / IS ratio). Flows
proportional to the move matter only on big days, which is why round 12 found a 7-12x scale-up in gold's top decile.

Prior strength of the LETF channel by venue (not a side choice, the side is always "follow"): JP225 (Nikkei 225
leveraged/inverse ETFs 1570/1357 are among the largest LETFs in the world relative to their futures market) and
USTEC (TQQQ/SQQQ) strongest; US30/US2000/US500 moderate; HK50 (L&I products from 2016/2019), DE40, UK100, AUS200 and
the energies (UCO/SCO, leveraged ETNs, plus TAS orders at the NYMEX/ICE settlement) weak.

## How this differs from the earlier tests (rows read first)
| earlier test | what it did | difference here |
|---|---|---|
| round 3, Nikkei LETF at the Tokyo close | all days, follow-through into the close; "nothing" (fade after the close IS t -3.6) | top decile of z only, plus dose bins; signal measured from the previous close/settlement and scaled by daily vol |
| round 4, Baltussen into the US close | day's move -> last 30 min, all days and \|z\| > 2: US30 +0.2 / +0.3, USTEC +0.7 / +1.1, USTEC big days +10.0 (t 1.2) / +3.1 | causal top decile (not a fixed 2), 10-15 min windows, executable 1-minute lag, dose slope |
| round 6 S1, energies | all days and \|z\| > 1, slope t; XTI +5.6 (t 2.0) / +1.8 at 15 min, XBR ~0, XNG VAL-only | top decile; actual spreads; dose bins; XBR on the ICE calendar |
| round 11 H2, USTEC MOC | follows the 15:50 imbalance-minute move, not the day's move | signal is the day's move |
| round 12 L6-LETF | USTEC top quintile of the 09:30-15:50 move, 15:52-16:00: net +1.94 (t 1.3) / +3.11 (t 1.8), +1 min -1.92 IS | previous-close reference (LETFs rebalance on close-to-close returns), vol-scaled z, top decile, 9 more venues, shared null |

## Rule P1 (one family, per symbol and window; all choices fixed here)
For symbol X with benchmark time B on its venue's business day d (local clock, DST-aware via zoneinfo):
- S(d) = mid at B (close of the M1 bar ending at B; mid ffilled at most 10 minutes, as in round 12).
- sd(d) = std of the previous 60 daily log returns ln S(k)/S(k-1) over venue days (>= 30 valid), day d excluded.
- Window w in {15, 10} minutes. z(d) = ln( mid at B-w-1 / S(d-1) ) / sd(d).
- thr(d) = 90th percentile of \|z\| over the previous 250 venue days (>= 60 valid), causal.
- Selected (top decile) if \|z(d)\| > thr(d). Side = sign(z(d)) (follow), fixed by the mechanism.
- Trade: enter at the close of the bar ending B-w (one minute after the signal), exit at the close of the bar ending B.
- Mid return in bp, signed. Net = mid - half the actual spread at entry - half at exit (no commission for indices and
  energies). US2000 (bid-only bars): mid = bid + published spread / 2, cost = round 7's published 0.34 points round
  trip. One trade per symbol per day.
- Stress: spread x1.5; **both fills one minute late** (enter B-w+1, exit B+1, same signal; stream J's lesson);
  winsorised 2.5/97.5 % per era.

Benchmarks (B) and venue days:
| cell | symbol | B (local) | days | note |
|---|---|---|---|---|
| P1-XTI | XTIUSD | 14:30 New York (NYMEX settlement 14:28-14:30) | XNYS days minus early closes | data from 2018 (IS 2018-21) |
| P1-XBR | XBRUSD | 19:30 London (ICE Brent settlement 19:28-19:30) | IFEU days (holidays 0.105) minus 24/31 Dec | 2018+; same clock as XTI except DST-mismatch weeks |
| P1-XNG | XNGUSD | 14:30 New York | as XTI | costly (spread 18 / 46 bp); eligible but expected to fail on cost |
| P1-US30 | US30 | 16:00 New York (NYSE close) | XNYS days, NYSE early-close days dropped | |
| P1-USTEC | USTEC | 16:00 New York | same | |
| P1-JP225t | JP225 | TSE close: 15:00 Tokyo, 15:30 from 2024-11-05 | XJPX days | |
| P1-JP225o | JP225 | OSE day-session close: 15:15 Tokyo, 15:45 from 2024-11-05 | XJPX days | where Nikkei LETFs trade futures |
| P1-DE40 | DE40 | 17:35 Frankfurt (end of the Xetra closing auction call 17:30-17:35) | XETR days, 24/31 Dec dropped | |
| P1-UK100 | UK100 | 16:35 London (LSE closing auction 16:30-16:35) | XLON days, 24/31 Dec dropped | |
| P1-HK50 | HK50 | 16:10 Hong Kong (closing auction session 16:00-16:10 from 2016-07-25; 16:00 before) | XHKG days, half days (24/31 Dec, Lunar New Year's Eve) dropped | IC quotes after 16:00 are sparse in 2016-17 |
| P1-AUS200 | AUS200 | 16:12 Sydney (ASX closing single price auction ~16:10-16:12) | XASX days, 24/31 Dec dropped | |
| info: P1-US500 | US500 | 16:00 New York | as US30 | round-3 contamination list: information only |
| info: P1-US2000 | US2000 | 16:00 New York | as US30 | bid-only bars: information only |

DE40 and JP225 are on round 3's hour-of-day contamination list. This rule has a data-dependent side, not an hour
mean; disclosed, kept eligible (as round 12 K did for gold).

Energies: 2020-04-14..2020-04-30 dropped before computing (negative WTI, IC glitches; brief's pitfall list).

Cells counted: 11 eligible symbol-benchmarks x 2 windows = 22, plus 3 pooled top-decile cells at w = 15 (P1-POOL-ALL:
the 11 eligible; P1-POOL-EQ: US30, USTEC, JP225o, DE40, UK100, HK50, AUS200; P1-POOL-EN: XTI, XBR, XNG), day-clustered
by UTC day = **25 counted cells**. The 4 information cells (US500, US2000 x 2 windows) also enter the shared null
(29 in the null). w = 15 is primary (gold's registered window); w = 10 is the secondary declared cell.

## Dose-response (fixed)
Per symbol and era, mean signed momentum (sign(z) x mid return in the window, bp) by \|z\| bin: 0-0.5, 0.5-1, 1-1.5,
1.5-2, 2-3, > 3. Dose slope: OLS of signed momentum on min(\|z\|, 4), t from OLS SE (one observation per day). Uplift:
top-decile minus other days, Welch t. Prediction: slope > 0 and top decile > 3x the all-day mean in both eras. A
symbol with no slope in IS and VAL is a no-mechanism symbol, whatever its top decile shows.

## Statistics and bars
- Mid first: mean bp, day-clustered t (one trade per day per symbol, so the per-day t; pooled cells sum by UTC day),
  by era (IS 2016-21, energies 2018-21; VAL 2022-24; no PRE: no index or energy data before 2016) and by year.
- Net at actual spreads, x1.5, both fills +1 minute.
- Random-entry control, look-ahead free: same selected days, random window end T' in the venue session (below), at
  least 15 minutes from B, side recomputed from S(d-1) to T'-w-1, same w-minute hold, actual spreads, 500 seeds.
  Sessions: XTI/XNG 10:00-17:00 NY; XBR 10:00-19:30 London; US 10:30-16:00 NY; JP225 09:30-15:00 Tokyo (15:30 after
  2024-11-04); DE40 09:30-17:35 Frankfurt; UK100 09:00-16:35 London; HK50 10:00-11:55 and 13:20-16:10 Hong Kong;
  AUS200 10:30-16:12 Sydney. Run on cells that are net > 0 in both eras.
- VAL / IS ratio of the net and mid; expected HOLD t on the VAL size (HOLD ~1.73 years).
- Power = per-trade net Sharpe x sqrt(1.73 x trades a year), on the IS and the VAL sizes; also per UTC day for pooled
  cells.
- Chance: (a) per-UTC-day sign flip shared across all 29 cells (one sign per UTC day applied to every cell's mid on that
  day; net null = flipped mid - cost), 1,000 permutations, max mid \|t\| and max net t; (b) top-decile label
  permutation within symbol-era for the uplift t; (c) max of K normals.
- C3 daily and monthly P&L correlation (IS+VAL) for any survivor.
- Bars as in the brief: DEMO (IS t >= 2.0, VAL net > 0, beats >= 90 % random, years, x1.5 and +1 min > 0) or LIVE.
  If met, write PREREG_DRAFT_P_<name>.md and stop the family.

## Predictions written down
- The scale-up exists where LETF AUM is large relative to the market: JP225 and USTEC top deciles > 3x all days in both
  eras; elsewhere weak.
- Gold's lesson (stream J): most of a momentum-into-benchmark effect may sit in the minute after the signal; if the
  +1 minute version loses more than half of the mid, the cell is not tradable.
- Expected outcome given rounds 3/4/6/11/12: small; costs on JP225/HK50/AUS200/UK100 (2-5 bp) are larger than any
  all-day effect seen so far, so only a top-decile scale-up of 5-10x could clear them.
