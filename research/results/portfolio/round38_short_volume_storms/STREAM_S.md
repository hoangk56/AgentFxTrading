# Round 38, stream S: FINRA daily short-sale volume and ETF primary-market flows

Written 2026-10-29 13:16 UTC (`date -u`). Hypotheses with their UTC times are in [HYPOTHESES_S.md](HYPOTHESES_S.md):
- S1-S3 (314 cells) were declared at 11:15 UTC, before any return was computed.
- S4 (51 cells) was declared at 11:20 UTC, after the S3 numbers and before any FINRA series was joined to a price.
- S5 (25 cells) was declared at 12:46 UTC, after S1 / S2 / S4.
- S6 (18 cells) was declared at 12:48 UTC, after S5.

No side was changed after its numbers were seen. Bars: research/PROMPT.md, LIVE / DEMO only (no RELAXED).

HOLD (2025-01-01..2026-09-24) stayed closed:
- Every FINRA request was for a date <= 2024-12-31, and the parsers drop later rows.
- The issuer files (which contain 2025-26 rows) were parsed with rows >= 2025-01-01 dropped before anything was kept
  or printed.
- Every IC load was cut at ts < 1735689600000.
- Disclosure: one web search snippet showed a current QQQ NAV / share count of unknown date (likely 2026). It was not
  used.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**

408 declared cells in six families:
- S1: ETF short-volume ratio -> the ETF's underlying.
- S2: heavyweight / whole-tape short ratio, with the DLW side and the DIX side.
- S3: ETF creations / redemptions.
- S4: creation-delay buying.
- S5: country-ETF operational shorting, covered in the next local session.
- S6: Rule 201 short-sale circuit-breaker load.

Results:
- No cell meets DEMO (IS net t >= 2 **and** VAL > 0).
- Two cells reach IS net t >= 2 (S1 DIA -> US30 OC 2.13, S5 EWG -> DE40 2.08; the next best is S3 DIA -> US30 at 1.82).
  All three have VAL < 0.
- Every family's best |mid t| is at or below its best-of-N null median (p 0.33-0.97).
- The fixed books are flat to negative at mid and negative net.
- This matches the literature's prior. Wang, Yan & Zheng 2020 find that abnormal short-term shorting flows do not
  predict returns once FINRA publishes them daily. Evans et al. find no relation between ETF operational shorting and
  the underlying.

The data are real and mechanical, but daily short volume is a by-product of liquidity provision that is already
hedged. It carries no forced flow with a clock after its publication time.

One post-hoc observation, which is **not a candidate**. SPY + IVV share creations are followed by US500 *continuation*
(the side opposite to BDR's reversal):
- The slope is -5.6 bp/sd (IS NW t -1.89) and -8.9 bp/sd (VAL t -2.24) on the declared reversal side.
- Flipped, the k 1.0 H1 cell would be about +8.3 bp net IS (t ~1.4) and +13 bp VAL (t ~1.75), with a per-trade SR of
  ~0.14. HOLD power would be ~1.5 at the VAL size.
- It fails DEMO's IS t 2 even with the side flipped, and the side would be data-chosen. It is the round 31 G pattern
  (flows chase price) on equities.

## Sources (fetch log: scratchpad `r38/S/web/requests.log`, 6,388 requests; the 227 403s are market holidays / probes)
| source | span | usable? |
|---|---|---|
| FINRA Reg SHO daily short volume (cdn.finra.org/equity/regsho/daily/) | FNSQ + FNYX 2009-08-03..2018-07-31, CNMS 2018-08-01..2024-12-31; full files gzipped (417 MB) | yes. FNQC and FNRA are empty, FORF is OTC only. ShortExemptVolume exists from 2011 |
| SSGA NAV history xlsx (SPY, DIA) | 2003-12..2024-12 (cut) | yes (NAV, shares outstanding, TNA). The ssga.com 301 was followed once |
| iShares fund download, Historical sheet (IWM, IVV, EWJ) | 1996 / 2000..2024-12 (cut) | yes |
| Invesco QQQ, USCF USO / UNG daily shares outstanding | none free (no history download on the issuer pages; one search) | no |
| nasdaqtrader.com Rule 201 short-halt lists | Incapsula bot wall (a JavaScript challenge) | no. Not retried; S6 uses FINRA ShortExemptVolume as the proxy |
| Literature (3 searches) | DLW 2009, BJZ 2008, WYZ 2020 JFE, Rapach-Ringgenberg-Zhou 2016, Evans-Moussawi-Pagano-Sedunov (operational shorting), BDR 2021 RF, BFM 2018, SqueezeMetrics DIX 2017 | sides fixed from these |

## Method
- **Signal day D** is a FINRA file date. FINRA posts the file by ~18:00 ET. Issuer rows dated D are taken as available
  the next morning (the variant adds one more day).
- **Clocks:**
  - H1: D+1 13:00 -> D+2 13:00 UTC.
  - H5: D+1 13:00 -> D+6 13:00 UTC.
  - OC: D+1 NY 09:31 -> 15:55.
  - S5 local session: the first local weekday after D, open + 5 min -> close - 5 min.
- **Costs:** half the actual IC spread at each fill minute, 0.6 bp commission on FX / metals, swaps per research.specs /
  swing.rates (XTI -2.5, XNG -4 bp a night).
- **Variants:** spread x1.5, +1 minute both legs, and one extra day of signal lag.
- **Trades:** z is computed against the 60 prior file days. Trades are non-overlapping per cell.
- **IS picks:** per pair x horizon, by IS net t.
- **Books:** risk-scaled by the trailing 60-day sd and clustered by entry day.
- **Controls:**
  - Random entries, 200 seeds: same count and side mix; a second version recomputes the side from the unthresholded
    signal at the random day.
  - Shared sign-flip-by-day null of max |mid t| per family.
  - S6 also uses a matched control by the decile of the return before entry.
- **Eras:** PRE 2010-15 only for the FX / metals targets (Dukascopy bid, IC 2016-17 cost).

## Results (best IS pick per family, declared side)
| hypothesis | eras | mid IS bp (t) / VAL | cost IS | net IS (t) / VAL (t) | VAL/IS | x1.5 / +1m / lag2 (IS / VAL) | SR IS / VAL, power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| S1 DIA SVR lvl k1.5 -> short US30, OC (n 239 / 122) | IS, VAL | +9.8 (2.32) / -4.7 | 0.8 | +9.0 (2.13) / -5.0 (-0.65) | < 0 | 8.6 / 8.0 / 6.6; -5.2 / -6.0 / -8.8 | 0.14 / -0.06; 1.15 / -0.50 | 0.99 / 0.24 | none (VAL < 0; 198-cell null p50 2.85) |
| S1 EWJ SVR lvl k1.0 -> short JP225, H5 | IS, VAL | +42.7 (2.25) / +28.2 | 12.9 | +29.8 (1.57) / +16.7 (0.56) | 0.56 | 28.0 / 29.9 / 27.3; 15.6 / 16.5 / 13.8 | 0.10 / 0.06; 0.8 / 0.42 | 0.98 / 0.81 | none (IS t < 2) |
| S1 books (11 / 4 index / 4 commodity pairs, lvl k1, H1 / H5 / OC) | IS, VAL | mid t -0.9..+1.6 / -0.7..+1.9 | 0.03-0.05 R | IS t -3.6..-0.1 / VAL -2.5..+1.45 | | | day SR <= 0.058 (idx4 OC VAL), power <= 1.1 | <= 0.95 | none |
| S1 FX / metals PRE 2010-15 (12 picks) | PRE | | | PRE t -1.3..+2.5 (GLD chg H5 +2.53 with IS 0.62, VAL -1.52) | | | | | no era agrees |
| S2 DIX side, top-10 ma5 k1.5 -> long USTEC, H5 | IS, VAL | +38.7 (1.47) / -36.8 | 13.9 | +24.8 (0.95) / -48.8 (-1.00) | < 0 | | 0.09 / -0.14 | 0.92 / 0.17 | none |
| S2 DLW side (short on high ratio): best all-tape ma5 k1.5 H5 | IS, VAL | +15.5 (0.77) / +17.8 | 11.0 | +4.5 (0.22) / +7.2 (0.23) | | | | 0.82 / 0.72 | none. NW slope of top-10 on US500 is on the DIX side in IS (t -2.2), ~0 in VAL |
| S3 DIA flow d k1.0 -> reversal US30, OC | IS, VAL | +9.7 (2.01) / -2.1 | 0.9 | +8.8 (1.82) / -2.4 (-0.44) | < 0 | 8.4 / 8.6 / 3.4; -2.6 / -2.1 / -10.2 | 0.10 / -0.03; 1.13 / -0.33 | 0.98 / 0.35 | none |
| S3 flow book (4 pairs) | IS, VAL | mid t -0.6..+0.3 | | IS t -1.9..-0.7 / VAL -2.0..-1.4 | | | | <= 0.72 | none |
| S4 creation-delay (long on ETF minus component SVR), best QQQ ma5 k1.0 OC | IS, VAL | +3.4 (0.84) / -8.6 | 1.7 | +1.8 (0.43) / -9.3 (-1.33) | < 0 | | | 0.79 / 0.12 | none. Book H5 IS t -3.77 (wrong side: mid t -2.2) |
| S5 EWG spread ma5 k1.5 -> long DE40 next Xetra session | IS, VAL | +10.6 (2.26) / -7.3 | 0.8 | +9.8 (2.08) / -7.7 (-1.01) | < 0 | 9.4 / 9.6; -7.8 / -8.2 | 0.13 / -0.09 | 0.97 / 0.12 | none (24-cell null p50 2.07) |
| S5 book (6 country ETFs) | IS, VAL | mid t 0.52 / -0.64 | | t -1.02 / -1.36 | | | power < 0 | | none |
| S6 Rule 201 load z > 1.5 -> long US500, OC | IS, VAL | +0.1 (0.01) / +13.5 (1.70) | 1.6 | -1.6 (-0.15) / +13.0 (1.64) | | | | 0.40 / 0.94; matched control 0.34 / 0.97 | none (IS ~0; VAL-only) |

## Cells tried and chance
| family | cells | best \|mid t\| IS | null p50 / p95 | p | best IS net t (declared side) |
|---|---|---|---|---|---|
| S1 | 198 + 9 books | 2.47 | 2.85 / 3.52 | 0.88 | 2.13 |
| S2 | 56 | 2.14 | 2.18 / 3.27 | 0.57 | 0.95 |
| S3 | 48 + 3 books | 2.06 | 2.37 / 3.10 | 0.78 | 1.82 |
| S4 | 48 + 3 books | 1.99 | 2.40 / 3.26 | 0.82 | 0.43 |
| S5 | 24 + 1 book | 2.26 | 2.07 / 2.93 | 0.33 | 2.08 |
| S6 | 18 | 0.93 | 1.75 / 2.72 | 0.97 | 0.27 |
Total: 408 declared cells. No result beats its chance benchmark.

## Information (not cells): NW slopes of the next mid return on z (scratchpad out/info_slopes.txt)
- **On the declared side, |t| <= 2.2 everywhere, and no pair has the same sign at |t| > 1.5 in both IS and VAL.**
  The exception is the wrong-side SPY + IVV flow continuation described above.
- **SPY SVR -> US500 is positive (declared side) only in VAL:** H1 +7.6 bp/sd (t 2.18), H5 +23 bp/sd (t 2.23). IS is
  ~0 (t -0.06 / +0.17).
- **Power.** Even at the VAL size, an 11-pair book would need an annualised net Sharpe of about 2.3 for LIVE. The best
  book day-SR is 0.058, which is about 0.9 annualised.

## Why it does not escape the limits
- **Predictability.** The power arithmetic held (HYPOTHESES_S.md): daily data give the count, but the per-trade
  predictability is ~0, not 0.05-0.07.
- **Short volume is a hedged by-product.** FINRA short volume is mostly market makers selling into customer buying.
  They hedge immediately (in futures or the basket), so nothing forced remains for the next session.
  - S4 tested the leftover creation buying for US ETFs. S5 tested it for country ETFs, where the basket can only be
    bought at the next local open.
  - Neither shows it: S4's book is significant on the opposite side at mid at H5, and S5 is null.
- **Issuer flows (S3) are a trace of a flow already executed,** as for GLD in round 31. If anything they chase price.
- **Rule 201 load (S6)** is positive only in VAL, and only for US500 (not US2000, where the mechanism should be
  strongest).

## Directions that need the user
| direction | value |
|---|---|
| Rule 201 trigger lists / Reg SHO threshold lists (nasdaqtrader.com sits behind an Incapsula bot wall; an account or a paid feed would be needed) | DEMO ~2 %, LIVE < 1 % (S6's FINRA proxy is null in IS) |
| Paid daily shares outstanding for QQQ, USO, UNG (Bloomberg / ETF Global) | < 1 % (S3 is null on 4 equity ETFs; round 31 G and round 34 E are null on commodity / leveraged funds) |
| Exchange-side short volume (NYSE / Nasdaq / Cboe exchange files) to complete FINRA's TRF-only figure | < 1 % (WYZ: short-horizon flows don't predict once public) |

## Pitfalls for later rounds
- **FINRA files.** Before 2018-08, the consolidated figure is FNSQ + FNYX (FNQC and FNRA exist but are empty; FORF is
  OTC). Old files have no ShortExemptVolume column (it starts in 2011). The SVR level shifts at the 2018-08 CNMS switch,
  so use z vs a trailing window.
- **META ticker.** "META" before 2022-06-09 is an unrelated Roundhill ETF. Use FB before that date.
- **Pull speed.** cdn.finra.org serves ~1 file per 1.1 s spaced start-to-start. Three date segments sharing one
  flock'd per-host stamp kept the >= 1 s rule. The full 2009-24 pull takes ~2 h.
- **Issuer files include 2025-26 rows.** SSGA navhist is oldest-first and iShares is newest-first. Never `head` them;
  parse with the cut.

## Files
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r38/S/`:
- **scripts/**:
  - fetching and parsing: fetch.py, dl_finra.py, parse_finra.py, parse_ishares.py, parse_xlsx.py;
  - panel and shared code: build_panel.py, common.py, signals.py;
  - runs: run_cells.py (S1-S4), run_books.py (S1 / S3 / S4), run_s5.py, run_s6.py, info_slopes.py.
- **out/**:
  - panel.npz, finra.npz, so_*.npz;
  - cells_S{1..4}.tsv, picks_S{1..4}.tsv, null_S{1..4}.txt, books_S{1,3,4}.txt, s5.txt, s6.txt, info_slopes.txt.
- **web/**: finra/, ishares/, ssga/, uscf/, ndq/, probe/, requests.log.

C3 correlation: no survivor, not computed.
