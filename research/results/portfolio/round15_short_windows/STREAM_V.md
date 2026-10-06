# Round 15, stream V: 1-10-minute windows at benchmark minutes (metals, AUD/NZD, index CFDs, oil)

2026-10-06. Hypotheses and their UTC times: [HYPOTHESES_V.md](HYPOTHESES_V.md). The design was written at 02:06 UTC
before any number; the survivor checks and the post hoc metals and AUS200 notes were added at 02:10 UTC, after the
scan and before their own numbers.

HOLD was never loaded:
- the panel ends 2024-12-31;
- day lists stop at 2024-12-30;
- the tick loaders assert day <= 2024-12-31;
- C3 rows outside IS/VAL were skipped.

There is no PRE minute data for these symbols, so IS 2016-21 is the discovery era (XTI: 2018-21) and VAL 2022-24 the
check.

## Answer
- **No LIVE or DEMO candidate, and no PREREG draft.** No predicted cell reaches the DEMO bar (IS net t >= 2.0). The
  best predicted IS net t on a real sample is 1.69 (HK50, fade the gap 09:30-09:40 HKT), and its VAL net is -2.13. The
  only higher value, AUS200 at 1.74, is a 50-day data artefact (see the V1 row). Three predicted cells are net > 0 in
  both eras, all with an IS net t of 0.01-0.43, and all three fail spread x1.5 or +1 minute.
- **The effects exist at mid, beyond chance, and cost kills them.**
  - Discovery: 608 predicted cells have IS t >= 2 on the predicted side. The sign-flip null gives a median of 178 and
    a 95th percentile of 258.
  - Confirmation: 141 of those 608 have VAL t >= 1.5 on the same side. The null gives a median of 11 and a 95th
    percentile of 23.
  - The confirmed cells sit at index closes (83), index opens (32), metal benchmarks (16) and elsewhere (10). Their
    mid edges are 0.3-2.7 bp, and the round-trip cost at those minutes is 1-7 bp.
- **The strongest effect in the stream has no side declared in advance, so it cannot be a candidate.** Gold and silver
  fall into and through the LBMA auctions. For silver at 12:00 London (11:59-12:01, short):
  - mid +2.68 bp (t 8.3) in IS and +2.72 bp (t 9.1) in VAL, positive in all 9 years;
  - bid and ask both fall, so it is not a quote artefact;
  - the drop sits mainly in two steps: T-30 s to T, and T+30 s to T+45 s (the end of the auction's first 30-second
    round);
  - gross power 4.5 / 6.9, but the 4.2-4.6 bp round trip is 1.6x the move.

  Gold at the 15:00 PM auction falls +1.09 / +0.94 bp (positive every year). With the entry and exit second chosen on
  IS it nets -0.21 / +0.11 bp: the 0.6 bp commission plus a 0.4-0.9 bp spread equals the move.

## Design (as declared)
- **Benchmarks** (venue clock, DST-aware): the cash opens and closes of the NYSE, Xetra, LSE, TSE (15:30 close from
  2024-11-05), HKEX and ASX; the European open (08:00 London) for US index CFDs; the LBMA gold auctions at 10:30 and
  15:00 and the silver auction at 12:00; the COMEX gold and silver floor opens at 08:20 / 08:25 ET; the NYMEX crude
  open at 09:00 ET and the end of the WTI settlement window at 14:30 ET; US data minutes at 08:30 and 10:00 ET (all
  NYSE days); Sydney 10:00 for AUD/NZD outside J's 09:45-10:15.
- **Days:** the venue's trading days (financial calendars from the `holidays` package). Excluded: 24 Dec - 2 Jan, US
  half days at the NYSE close, and the HKEX Lunar New Year eve at the HK close.
- **Windows:** s = T-20 .. T+20 by 1 minute, L = 1, 2, 3, 5, 10 minutes.
- **Rules:**
  - U: long.
  - M: follow the 10 minutes before entry.
  - G: follow the move since the previous cash close (opens only).
- **Predicted sides** (from the mechanisms in the hypotheses file):

  | family | predicted side |
  |---|---|
  | V1 opens | fade (G-, M-) after T |
  | V2 European open | long (U+) |
  | V3 closes | M+ before T, M- after |
  | V4 LBMA | M+ up to T+1, M- after |
  | V5 COMEX / NYMEX opens | M- after T |
  | V6 WTI settlement | M+ before T, M- after |
  | V7 data minutes | M+ after T |
  | V8 Sydney | none (information only) |

- **Prices and costs:**
  - mid = the last quote before the minute boundary (shared panel);
  - cost = half the actual spread at the entry minute + half at the exit minute, + 0.6 bp for XAU XAG AUD NZD (0 for
    indices and XTI);
  - the tick check reproduces the panel exactly: USTEC +0.02 / +1.07 bp net on both.
- **Cell count:** 25,704 cells (24 benchmarks x 13 symbols, 205 windows per rule). 8,210 carry a predicted side. 115
  are flagged as overlapping J's cells and are information only: USTEC/US30 M+ at 15:50-15:59 ET, and AUS200 M- at
  16:12-16:14 Sydney.
- **Power** = per-trade net Sharpe x sqrt(trades a year x 1.73), on each era's own Sharpe and count.

## Chance (sign-flip permutation, one sign per date shared by all cells, 500 draws)
| step | observed | null median / p95 / p99 |
|---|---|---|
| max \|IS mid t\|, all 25,704 cells | 8.29 (silver 12:00, information cell) | 4.05 / 4.63 / 5.01 |
| max \|IS mid t\|, 8,210 predicted cells | 7.28 (HK50 close, wrong side) | 3.80 / 4.41 / 4.73 |
| max IS t on the predicted side | 6.49 (UK100, fade 16:34-16:39 London) | 3.61 / 4.28 / 4.58 |
| predicted cells with side t_IS >= 2 | 608 | 178 / 258 / 298 |
| ... of which VAL t >= 1.5 on the same side | 141 | 11 / 23 / 36 |

## Results by hypothesis
- Mid and net are in bp per trade, with t in brackets; the power column gives IS / VAL.
- PRE is n/a for every row (no minute data before 2016 for these symbols).
- "conf" is the number of cells with IS t >= 2 that VAL confirms.

| hypothesis (mechanism, source) | cells (pred) / t>=2 / conf | best cell | IS / VAL mid | cost IS / VAL | net IS / VAL | VAL/IS | power | verdict |
|---|---|---|---|---|---|---|---|---|
| V1 opening overreaction, fade the gap or the first minutes (Branch & Ma 2012; Berkman et al. 2012) | 5,740 (1,680) / 204 / 32 | HK50 G- 09:30-09:31 HKT (best IS t) | +2.11 (6.3) / +0.33 (0.4) | 3.29 / 2.81 | -1.17 / -2.49 | 0.15 | <0 | decaying, at cost |
| | | US500 M- 09:41-09:51 ET (best VAL-confirmed) | +0.99 (2.3) / +1.68 (2.3) | 1.59 / 0.49 | -0.60 (-1.4) / +1.19 (1.6) | 1.70 | <0 / 1.24 | fails IS net |
| | | AUS200 M- 10:00 (best IS net t) | n = 50 IS days, 0 VAL | | +2.61 (1.74) / - | | | artefact: the CFD has no quote 10 minutes before 10:00 on most days |
| V2 overnight drift at the European open, long (Boyarchenko, Larsen & Whelan 2023) | 1,640 (1,025) / 71 / 1 | DE40 U+ 08:48-08:53 CET | +0.67 (3.6) / +0.04 (0.2) | 1.11 / 0.33 | -0.44 / -0.29 | 0.05 | <0 | gone in VAL |
| V3 close pressure into the auction, reversal after (Cushing & Madhavan 2000; Bogousslavsky 2021) | 3,280 (1,640) / 207 / 83 | UK100 M- 16:34-16:39 London | +1.65 (6.5) / +1.17 (3.9) | 3.04 / 2.03 | -1.39 / -0.86 | 0.71 | <0 | real, about half the post-close spread |
| | | US30 M- 16:04-16:14 ET | +0.58 (2.4) / +1.05 (4.2) | 0.93 / 0.31 | -0.35 (-1.4) / +0.74 (2.9) | 1.82 | <0 / 2.22 | fails IS net (IC's US30 spread fell 3x in 2022); IS mid at VAL cost would be ~+0.27 |
| | | US30 M+ 15:57-16:00 ET (J5b overlap) | +1.39 (4.4) / -0.04 (-0.1) | 0.91 / 0.29 | +0.48 (1.5) / -0.33 | -0.03 | 0.82 / <0 | gone in VAL |
| V4 LBMA pre-auction momentum, post-auction reversal (Caminschi & Heaney 2014; Evans 2018) | 2,460 (615) / 49 / 8 | XAU M- 10:36-10:38 London | +0.27 (4.2) / +0.05 (0.4) | 1.43 / 0.97 | -1.16 / -0.92 | 0.17 | <0 | below cost (the real effect is the unconditional drop, below) |
| V5 US floor opens, fade (low prior) | 1,230 (315) / 12 / 8 | XAU M- 08:20-08:30 ET | +1.01 (3.3) / +0.85 (2.1) | 1.74 / 1.19 | -0.73 / -0.34 | 0.85 | <0 | stable, below cost |
| V6 WTI settlement pressure | 410 (205) / 4 / 2 | XTI M- 14:30-14:31 ET | +1.65 (2.4) / +0.70 (2.1) | 7.54 / 3.30 | -5.91 / -2.60 | 0.42 | <0 | cost 3-7 bp |
| V7 data-minute continuation (Ederington & Lee 1995) | 10,660 (2,730) / 61 / 7 | UK100 M+ 08:31-08:41 ET | +0.98 (4.1) / -0.25 (-0.7) | 1.61 / 1.26 | -0.62 / -1.51 | -0.25 | <0 | none (61 vs the all-cell chance rate) |
| V8 Sydney 10:00 outside J's cells | 284 (0) | | | | | | | information only |
| (post hoc, info) metals fall into the LBMA auctions | silver 12:00 | XAG short 11:59-12:01 | +2.68 (8.3) / +2.72 (9.1) | 4.19 / 4.60 | -1.51 / -1.88 | 1.02 | gross 4.5 / 6.9 | structural-looking, at 0.6x cost |
| | gold 15:00 | XAU short 14:59-15:01 | +1.09 (5.2) / +0.94 (2.7) | 1.45 / 1.02 | -0.36 / -0.09 | 0.86 | gross 2.8 / 2.0 | at cost |
| | gold 10:30 | XAU short 10:29-10:31 | +0.88 (8.2) / +0.24 (1.9) | 1.44 / 0.99 | -0.56 / -0.75 | 0.27 | <0 | decaying |
| (post hoc, info) AUS200 drop at 10:10 Sydney | ASX open | short 10:10-10:11 | +1.55 (7.2) / +2.05 (9.1) | 2.02 / 1.45 | -0.47 / +0.59 (2.6) | 1.32 | <0 / 1.99 | one-minute drop with a partial rebound next minute; +1 min: net -2.0..-2.8 every year |

Only 3 of the 8,210 predicted cells are net > 0 in both eras; 36 of the 17,494 information cells are.

## Declared survivor checks (predicted, IS t >= 2, IS net > 0, VAL net > 0)
| cell | net IS / VAL (t) | x1.5 | +1 min | ticks +10 s / +30 s / +60 s (IS / VAL) | years > 0 | random entry IS / VAL | C3 daily / monthly | verdict |
|---|---|---|---|---|---|---|---|---|
| USTEC G- 09:30-09:40 ET | +0.02 (0.03) / +1.07 (0.89) | -1.29 / +0.61 | +0.24 / -0.24 | +0.60 / +1.45; -0.28 / +0.36; +0.24 / -0.24 | 5/9 | 100 % / 98 % | -0.006 / -0.065 | fails (IS net t 0) |
| US30 G- 09:49-09:59 ET | +0.01 (0.01) / +0.17 (0.32) | -0.42 / +0.04 | +0.06 / -0.41 | +0.16 / -0.10; +0.17 / -0.12; +0.06 / -0.41 | 3/9 | 100 % / 79 % | -0.038 / +0.085 | fails |
| DE40 M- 09:10-09:20 CET (M1 only) | +0.22 (0.43) / +0.07 (0.11) | -0.20 / -0.11 | -0.28 / -0.35 | n/a | 6/9 | 100 % / 100 % | -0.031 / -0.065 | fails |

The random-entry control is easy to beat at opens: random windows away from T have lower volatility and the same
cost, so their net is about -cost. It does not rescue a cell whose IS net t is 0.

## The metals auction drop at tick level (post hoc, information only)
- **Profile.** Mean change from T-120 s, bid and ask moving together:

  | symbol, auction | at T, bp (IS / VAL) | at T+45 s, bp (IS / VAL) | step T+30 s -> T+45 s, bp |
  |---|---|---|---|
  | XAG 12:00 | -1.3 / -1.5 | -2.6 / -3.0 | -1.3 / -0.65 |
  | XAU 15:00 | -0.5 / -0.4 | -1.2 / -1.1 | |
  | XAU 10:30 | -0.4 / -0.4 | -0.9 / -0.3 | |

  - Partial recovery by T+180 s in IS, none in VAL.
  - XAU's spread widens at 15:00: 0.83 -> 1.00 bp IS, 0.39 -> 0.53 VAL.
  - XAG's ask rises at 15:00 while its bid falls: its spread is 5.3 bp in VAL.
- **Best seconds chosen on IS** (5-s grid, sell at the bid, cover at the ask, + 0.6 bp), net IS / VAL:

  | symbol, auction | net IS / VAL, bp | with fills +10 s | with fills +30 s |
  |---|---|---|---|
  | XAU 15:00 | -0.21 / +0.11 | -0.26 / -0.02 | -0.52 / -0.14 |
  | XAU 10:30 | -0.47 / -0.70 | | |
  | XAU 12:00 | -1.08 / -0.55 | | |
  | XAG 12:00 | -1.47 / -1.71 | | |

- **By year** (mid, short T-60 s .. T+60 s):
  - XAG 12:00: +3.5 +0.9 +2.4 +1.7 +4.3 +3.3 | +2.5 +3.7 +2.0;
  - XAU 15:00: +1.0 +1.5 +0.2 +0.3 +3.0 +0.5 | +1.6 +0.8 +0.4.
- **Overlap with E1 / the ECB slot:** none in symbol. The 12:00 silver and 10:30 gold windows sit inside E1's
  11:00-13:00 London clock span, but E1 trades EURUSD. No cell in this stream trades EUR.

## Surprises
1. **Silver's drop into the 12:00 silver price is the most stable short-window effect in rounds 12-15** (VAL/IS 1.02,
   every year positive, t 8-9 in both eras). Gold shows the same shape at 15:00 and, decaying, at 10:30. This is the
   pattern Abrantes-Metz & Metz (2014) reported for the pre-2015 fixings; it survived the move to the IBA/ICE electronic
   auction. It was not predicted here (V4 declared momentum / reversal rules, not an unconditional short), so it is
   information only.
2. **The HK50 close continues instead of reversing.** Fading at 16:08-16:10 HKT, around the random end of the closing
   auction, has t -7.3 / -3.1. HK50's 2.7-3.3 bp cost makes the sign moot.
3. **US30's post-close reversal (16:04-16:14 ET) is larger in VAL than in IS** (+1.05 vs +0.58 bp). It fails only
   because IC's US30 cost in 2016-21 (0.93 bp) is 3x today's.

## Directions that need the user's decision
- **A clean out-of-sample test of the LBMA metals drop.** It cannot be registered from IS/VAL here.
  - Dukascopy XAU/XAG M1 or ticks for 2004-15 would give a PRE era. That is a new price fetch: the user's call.
  - The other route is the lead's HOLD.
  - Even if it holds, it needs a cheaper venue: silver round trip <= ~1.5 bp, gold <= ~0.7 bp. IC's commission alone is
    0.6 bp.
- **US30 post-close reversal at today's cost:** a forward demo or HOLD test would be the only fair test. Its IS t at
  VAL-level cost is about 1.1, below DEMO.

## Files (scratchpad r15/V/)
- vc.py: helpers, benchmark and rule definitions, HOLD-safe day lists.
- mkcal.py -> cal_v.json: venue calendars (holidays package, scratch venv).
- vscan.py -> cells.json, G.npy, C.npy: the M1 scan.
- vsum.py -> stats.npz, null.npy, vsum_null.txt: per-cell statistics and the sign-flip null.
- vreport.py -> vreport_out.txt and vgroup.py -> vgroup_out.txt: families and candidates.
- vprof.py -> vprof_out.txt: minute profiles.
- vinfo.py -> vinfo_out.txt: information cells.
- vsurv.py -> vsurv_out.txt: survivor checks.
- vtick.py: A -> vtickA_USTEC.txt, vtickA_US30.txt (latency); B -> vtickB.npz (metals ticks).
- vmetal.py -> vmetal_out.txt.
- vasx.py -> vasx_out.txt.
