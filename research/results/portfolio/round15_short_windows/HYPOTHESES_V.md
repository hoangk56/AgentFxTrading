# Round 15, stream V: hypotheses (written before their numbers)

Written 2026-10-06 02:06 UTC (`date -u`), before any round-15 stream-V number was computed. Brief: BRIEF.md here and
round13_structural/BRIEF.md. HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31 and every
tick load stops at 2024-12-31 (assertion in the loader).

## Common design (all families)
- Symbols: XAUUSD XAGUSD AUDUSD NZDUSD US30 USTEC XTIUSD (IC ticks; XTI from 2018) and DE40 UK100 JP225 HK50 AUS200
  US500 (M1). Scan on the shared panel mid / spread (r12/shared/panel); survivors re-run on ticks at the exact second.
- Benchmark minute T, DST-aware in the venue's own time zone. Windows [s, s+L] with s = T-20 .. T+20 (minute steps,
  41 starts) and L = 1, 2, 3, 5, 10 minutes: 205 windows per (benchmark, symbol, rule). Price at a minute boundary t
  = mid of the last quote before t (panel bar ending at t).
- Rules (sides) per window:
  - U: long (unconditional); its sign is the cell's mean.
  - M: follow the move of the 10 minutes before entry, side = sign(mid(s) / mid(s-10) - 1); no trade if 0.
  - G (opens of cash index markets only): follow the "gap", side = sign(mid(s) / mid(previous cash close) - 1).
  A predicted side is "+" (follow / long) or "-" (fade / short). A cell's side is the IS sign only if it matches the
  mechanism's prediction below; every other cell (and every cell of a window range without a prediction) is
  information only and cannot become a candidate.
- Days: trading days of the venue (holidays package financial calendars: XNYS, XETR, XLON, XJPX, XHKG, XASX, CME;
  LBMA = London business days), weekdays, 24 Dec - 2 Jan excluded, US half days (day after Thanksgiving, 3 July,
  24 Dec) excluded for US cells, HKEX half days (Lunar New Year eve) excluded for HK50. Data minutes: all NYSE days.
  Quotes staler than 10 minutes = no trade. One trade per day per cell, so t is day-clustered by construction.
- Eras: IS 2016-21 (XTI 2018-21) discovery, VAL 2022-24 check.
- Cost per round trip: half the actual spread at the entry minute + half at the exit minute (panel; ticks for
  survivors) + 0.6 bp commission for XAU XAG AUD NZD, 0 for indices and XTI.
- Per cell: mid bp and t by era (and year for survivors), cost, net, per-trade net Sharpe, power = Sharpe x
  sqrt(trades a year x 1.73) on the IS and on the VAL size, VAL/IS.
- Chance: sign-flip permutation by date (one sign per calendar date shared by every cell), 500 draws, for (a) the max
  |IS mid t| over all cells and over the predicted cells, and (b) the number of predicted cells with IS t >= 2.0 on the
  predicted side that also have VAL t >= 1.5 (VAL dates flipped independently).
- Candidate path: predicted cell, IS mid t >= 2.0 on the predicted side, IS net > 0 -> VAL. A VAL survivor (net > 0
  in VAL) gets ticks, +10 s / +30 s / +60 s on both fills, spread x1.5, by year, a random-entry control (same days,
  same side rule recomputed at a random start minute in T-120..T+120 excluding T-30..T+30, same L, 200 seeds), C3
  correlation. LIVE / DEMO bars as in round 13's brief.
- Not redone (round 12 J): SGE, Sydney V inside 09:45-10:15 Sydney, ECB, USTEC MOC (M rule, s in 15:50-15:59 ET, is
  the J / round 11 H2 cell: information only), AUS200 close fade (M- with s in 16:12-16:14 Sydney is information only),
  gold settlement 13:30 ET.

## Families, mechanisms and predicted sides
| id | benchmark (venue clock) | symbols | predicted rule and side | mechanism, source |
|---|---|---|---|---|
| V1 | Cash opens: NYSE 09:30 ET (US30 US500 USTEC), Xetra 09:00 CET (DE40), LSE 08:00 London (UK100), TSE 09:00 JST (JP225), HKEX 09:30 HKT (HK50), ASX 10:00 Sydney (AUS200) | home index | s >= T: G- (fade the gap) and M- (fade the last 10 minutes); s < T: none | opening-auction overreaction and overnight-intraday reversal: close-to-open moves partly reverse after the open (Branch & Ma 2012; Berkman, Koch, Tuttle & Zhang 2012, attention buying at the open; Amihud & Mendelson 1987, noisier opening prices) |
| V2 | European open 08:00 London (= 09:00 CET) | US30 US500 USTEC DE40 UK100 | U+ (long), all s | overnight drift: US equity futures returns concentrate around the European open as dealers lay off inventory from the US session (Boyarchenko, Larsen & Whelan 2023) |
| V3 | Cash closes: NYSE 16:00 ET, Xetra 17:30 CET, LSE 16:30 London, TSE 15:00 JST (15:30 from 2024-11-05), HKEX 16:00 HKT, ASX 16:10 Sydney | home index | s < T: M+ (pressure into the close / auction); s >= T: M- (price pressure reverses after the auction) | closing-auction and MOC price pressure is temporary (Cushing & Madhavan 2000; Bogousslavsky 2021 end-of-day reversal; the fix pattern of Evans 2018 applied to closes) |
| V4 | LBMA gold auctions 10:30 and 15:00 London (XAUUSD), LBMA silver 12:00 London (XAGUSD) | XAU / XAG (XAG at the gold auctions and XAU at the silver auction: information only) | s < T: M+; s in {T, T+1}: M+ (during the auction rounds); s >= T+2: M- | benchmark-order pre-positioning and leakage of the auction imbalance (Caminschi & Heaney 2014 for the London gold fix; Evans 2018 pre-fix momentum and post-fix reversal at WM/R) |
| V5 | COMEX gold floor open 08:20 ET (XAU), COMEX silver 08:25 ET (XAG), NYMEX crude floor open 09:00 ET (XTI) | XAU XAG XTI | s >= T: M- ; s < T: none | US liquidity arrival absorbs the European-session order imbalance, which partly reverses (low prior: floors are now marginal; the times still mark the US regular session) |
| V6 | NYMEX WTI settlement window end 14:30 ET (settlement = VWAP 14:28-14:30) | XTI | s < T: M+; s >= T: M- | trade-at-settlement and settlement-benchmarked (ETF roll, hedger) orders push price into the window and the pressure reverses after (round 6 S1 found the hourly version real but small) |
| V7 | US data minutes 08:30 and 10:00 ET, all NYSE days | all 13 symbols | s >= T: M+ ; s < T: none | price discovery after scheduled releases continues for a few minutes in CFD quotes (Ederington & Lee 1995; Andersen, Bollerslev, Diebold & Vega 2003); on no-release days the cell is a dilution, accepted (the brief says all days) |
| V8 | Sydney 10:00 (AUDUSD, NZDUSD), windows not contained in J's 09:45-10:15 | AUD NZD | none: information only | J covered the V; these windows have no separate mechanism |

Cell count, declared: 6 opens x 1-3 home symbols ... computed exactly by the scan script and reported (all cells
enter the shared null; the predicted cells are the candidate set). Information-only cells also computed: U and M
rules everywhere a predicted rule exists for another range, G for opens' pre-T windows, the cross cells above, and
V7 on all symbols.

## Expectations written down now
- Cost will kill most cells: index CFD spreads widen at cash opens (TSE, HKEX, ASX opens at 2-4 bp); US30 (VAL 0.3 bp)
  and DE40 are the cheap ones. LIVE needs mid edge >= cost + 0.145 x sd(window), e.g. US30 5-minute window at the
  open with sd ~10 bp: >= 1.5 bp + cost.
- Most likely survivors if any: V1 fade at the NYSE / Xetra open in US30 / DE40, V3 post-close reversal in US30.

## Additions after the scan (written 2026-10-06 02:10 UTC, after the M1 scan numbers; marked post hoc)
- **Survivor checks (as declared above, not post hoc in design):** the three predicted cells that pass "IS t >= 2,
  IS net > 0, VAL net > 0" (NYSE_O USTEC G- s0 L10, NYSE_O US30 G- s+19 L10, XETR_O DE40 M- s+10 L10) get the
  declared checks: ticks for USTEC / US30 (+10 s / +30 s / +60 s on both fills), spread x1.5, by year, random-entry
  control, C3 correlation. Their IS net t is about 0, so they cannot meet DEMO or LIVE whatever the checks say.
- **Post hoc, information only (cannot become a candidate in this stream):** the scan shows gold and silver mids
  falling over the minute before and the minute after the LBMA auctions (10:30 and 15:00 London gold, 12:00 silver),
  in IS and VAL. Mechanism read after the fact: sell-side auction participation / pre-hedging into the auction, the
  pattern Abrantes-Metz & Metz (2014) and Caminschi & Heaney (2014) described for the old fixings. Checks: (a) tick
  level, bid and ask separately (is it a quote artefact of the mid?), 10-second profile T-120 s .. T+180 s, IS and
  VAL; (b) the best entry/exit second chosen on IS (5-s grid) for a short XAU / XAG trade at each auction, its VAL
  net, as an upper bound on what timing can do; (c) by year. Same for the AUS200 drop at 10:10 Sydney (M1 only:
  minute profile and spread). No side, window or second chosen here can be registered from IS/VAL; a clean test
  needs data not yet seen (HOLD, or PRE metals minute data the user would have to approve).
