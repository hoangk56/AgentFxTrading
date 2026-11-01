# Round 39 stream R: scheduled futures-roll flows -> XTI, XBR, XNG (XAU, XAG, US500 controls)

Hypotheses declared first: [HYPOTHESES_R.md](HYPOTHESES_R.md) (2026-10-29 13:29 UTC; tracking addendum 13:31 UTC,
before any return). HOLD stayed closed: IC M1 cut at ts < 1735689600000 at load; the EIA settlement json (parsed in
round 38 H, cut at 2024-12-31, futures series end 2024-04-05) was graded on 1995-2017 only.

## Answer
**No LIVE or DEMO candidate, and none was reachable.** The count and the literature settle it before any return: a
roll window comes 12 times a year per commodity (48 IS windows on IC's 2018-21 energies, ~21 in HOLD). The sources put
the whole roll pressure in the calendar spread at 25-38 bp per roll. That is a per-window Sharpe of ~0.05 on an
outright crude CFD (5-day sd ~500 bp). DEMO would need ~150 bp a window (IS t >= 2 on 48 windows), and LIVE would need
~350 bp (power 3 on 21 HOLD windows). A small declared check (15 cells) confirmed the prior. The spread pressure is
there in exchange data (contract 2 minus contract 1 widens +17.7 bp, t 2.11, during BD 5-9 and narrows -34.7 bp,
t -2.81, after, 1995-2017). But contract 1 alone does not move with it: CL1 over the roll window is -6.8 bp gross
(t -0.22, wrong sign for the short). On IC no cell has a right-side IS t above 0.44. The stream stopped there, as the
brief requires when DEMO is out of reach.

## Sources
| source | span used | status |
|---|---|---|
| Bessembinder, Carrion, Tuttle & Venkataraman, "Predatory or sunshine trading? Evidence from crude oil ETF rolls" (March 2014 draft of the 2016 JFE paper), cftc.gov PDF | text | used for sides and sizes: USO rolled on one day until 2009-02, then over four days ~2 weeks before expiry; the C2-C1 spread widens 25 bp per roll in 2006-12 and 38 bp in 2000-06, ~0 in the 1990s; it narrows 26 bp after the roll; >99 % of temporary impact reverses within 10 min |
| Mou 2011 (SSRN 1716841), Stoll & Whaley 2010 | abstracts / BCTV's summary | spread front-running Sharpe up to 4.39 in 2000-10, 3.6 %/yr cost to index investors; Stoll & Whaley: little or no price effect at roll dates |
| S&P GSCI (BD 5-9, 20 %/day), BCOM (BD 6-10) schedules | as stated in the brief and the literature | methodology PDFs not fetched; every cell uses the GSCI BD 5-9 window, which also covers BCOM and pre-2020 USO |
| EIA daily NYMEX settlements CL1/CL2, NG1/NG2 (round 38 H's parse) | 1995-2017 (PRE) | usable; contract-1 expiries from CME rules; windows containing an expiry dropped |
| IC M1 XTIUSD, XBRUSD, XNGUSD; XAUUSD, XAGUSD, US500 | 2018-2024 | usable |
| IC rollover notices | - | not fetched; IC's construction inferred from prices (below) |

Requests: 2 web searches, 1 fetch (cftc.gov PDF, logged in `web/requests.log`); web.archive.org not used.

## What IC's energy CFDs track (brief part 2)
This was a price-level comparison at 14:29 ET with the EIA settlements, 2018-01..2024-04 (`out/track.txt`). Define
x = (IC - CL1) / (CL2 - CL1) on days with a calendar spread above $0.25.
- **XTIUSD is not on one contract.** It is a continuously interpolated price. The median x is -0.38 at BD1 (just after
  the CL1 expiry), -0.26 at BD4, -0.08 at BD9 and +0.20 at BD13, then falls back to about -0.55 after the next expiry
  (BD 15-17). There is no switch day; the weight on contract 1 is about 1.1-1.3 through BD 0-13, so the CFD does carry
  contract 1, the one being sold.
- **XNGUSD sits on NG1** (median x -0.14..-0.04 at BD 1-13) through every window. NG1 expires 3 BD before month end.
- **XBRUSD shows no switch jump.** Jumps above 4x the median in the XBR - XTI gap are spread evenly over BD 1-23 (108
  of 1,724 days), the same continuous construction as XTI.
- Consequence: the declared per-day "C1" tag (|IC - C1| < |C2 - C1| / 3) is ill-posed for an interpolated price; 51 %
  of XTI days were "?". All windows are kept (addendum, before returns), and the C1-only filter is reported as a
  variant. The interpolation adds about +0.18 x (CL2 - CL1) of drift to XTI against CL1 over BD4 -> BD9, roughly
  +5-10 bp in contango.

## Results
Cells: R1 = short over the roll window (BD4 -> BD9 settlement); R2 = long after it (BD9 -> BD13); R3 = short before it
(BD0 -> BD4, front-runners). Entries are at the settlement minute (14:29 ET bar close; XBR 19:29 London). Net = mid
minus half the spread at both minutes, minus swap for every calendar night (XTI / XBR 2.5 bp, XNG 4, US500 2, metals 1
+ 0.6 commission). t is on windows (one trade per window). Random entry = same side and hold from BD >= 14 days of IS,
300 seeds.

| hypothesis | eras | mid bp (t) | cost bp | net IS (t) / VAL (t) | VAL / IS | per-window Sharpe IS; power (21 HOLD windows) at IS / VAL size | random IS | verdict |
|---|---|---|---|---|---|---|---|---|
| R1 XTI short roll window | IS / VAL | +61.5 (0.54) / -97.2 (-1.40) | ~25 (spread ~5 + swap 17.5) | +36.6 (0.32) / -118.1 (-1.70) | < 0 | +0.047; 0.22 / < 0 | 88 % | none (IS rests on 2020: ex 2020-03/04 -99.8, t -1.63) |
| R1 XBR | IS / VAL | +69.8 (0.66) / -86.6 (-1.40) | ~24 | +45.9 (0.44) / -106.7 (-1.72) | < 0 | +0.064; 0.29 / < 0 | 89 % | none (ex 2020 -66.4) |
| R1 XNG | IS / VAL | -33.3 (-0.30) / -229.1 (-1.35) | ~40-67 | -73.7 (-0.67) / -296.6 (-1.75) | - | < 0 | 48 % | none |
| R2 XTI long after roll | IS / VAL | -79.7 (-0.56) / -101.1 (-1.28) | ~22 | -102.2 (-0.71) / -119.1 (-1.52) | - | < 0 | 6 % | none |
| R2 XBR | IS / VAL | -0.2 (0.00) / -94.1 (-1.32) | ~21 | -21.4 (-0.24) / -111.4 (-1.57) | - | < 0 | 38 % | none |
| R2 XNG | IS / VAL | -87.5 (-0.84) / -181.7 (-0.99) | ~36-63 | -123.6 (-1.19) / -245.1 (-1.34) | - | < 0 | 5 % | none |
| R3 XTI short pre-roll | IS / VAL | -184.9 (-1.60) / +34.3 (0.29) | ~22 | -207.5 (-1.79) / +16.1 (0.14) | - | < 0 | 23 % | none |
| R3 XBR | IS / VAL | -148.2 (-1.71) / +44.2 (0.38) | ~21 | -170.0 (-1.94) / +26.7 (0.23) | - | < 0 | 5 % | none |
| R3 XNG | IS / VAL | -36.3 (-0.32) / +47.0 (0.26) | ~37-64 | -73.5 (-0.65) / -17.3 (-0.10) | - | < 0 | 56 % | none |
| R1 controls XAU / XAG / US500 | IS / VAL | +6.8 / +36.3 / -18.9 (IS) | 8-11 / 8-11 / 15 | -1.7 / +25.3 / -34.5 (IS, all \|t\| < 0.8); VAL all < 0 | - | - | 87 / 91 / 69 % | the controls behave like the energies: noise |
| C1-only variants (XTI, XNG) | IS / VAL | n 4-9 per era | - | best XTI R2 +161 (t 1.26) / +60.5 (0.35) | - | n too small | - | none |

PRE on exchange settlements (contract 1, gross, 1995-2017, 221-276 windows; also shown as 1995-99 / 2000-11 /
2012-17 in `out/grade.txt`):

| cell | contract 1 gross bp (t), signed by the declared side | per-window Sharpe | C2 - C1 spread change over the window, bp of price (t) |
|---|---|---|---|
| CL R1 (short) | -6.8 (-0.22); by sub-era +13.3 / -60.3 / +83.4 | -0.013 | **+17.7 (2.11)**; +30.7 / +15.7 / +10.8 |
| CL R2 (long) | -6.0 (-0.18) | -0.012 | **-34.7 (-2.81)**; -19.2 / -53.5 / -11.9 |
| CL R3 (short) | +22.7 (0.77) | +0.046 | +10.7 (3.68) |
| NG R1 (short) | +5.9 (0.14) | +0.008 | +24.1 (2.11) |
| NG R2 (long) | +75.4 (1.74) | +0.105 | -49.5 (-3.90) |
| NG R3 (short) | +79.6 (2.11); 2012-17 +125.9 (2.18) | +0.127 | +30.6 (3.57) |

- **The mechanism is real, but in the spread only.** C2 - C1 widens into and through the roll window and narrows after
  it, as BCTV report. The effect is shrinking (CL R1 widening 30.7 -> 15.7 -> 10.8 bp across the three PRE sub-eras).
  It was already there in 1995-99, before index investing, so part of it is the term structure's own drift as
  contract 1 nears expiry. Contract 1's outright price does not carry it in any sub-era: the sign flips between
  sub-eras, and the per-window Sharpe is at most 0.05 for crude.
- NG R3 (short NG1 BD0 -> BD4) is the only PRE cell at t ~2 (one of 6 PRE cells, inside the best-of-15 null). On IC it
  is -73.5 bp (t -0.65) in IS and -17.3 in VAL.
- On IC, every energy cell is negative in VAL whatever the side. VAL 2022-24 energies fell, and swap costs 17-28 bp a
  window. The IS positives of XTI / XBR R1 come from 2020 alone (XTI 2020 +486 bp a window).

## Cells tried and the chance benchmark
15 declared trade cells (9 IC, 6 PRE) plus 3 controls and 6 C1-only variants. The largest right-side t is 2.11 (NG R3,
PRE, gross). On IC, the best right-side IS t is +0.44 (XBR R1, net). The expected maximum |t| of 15 independent
normals is ~2.0, and the crude cells are correlated, so fewer tests are effective. Nothing stands out from chance. The
roll-related flows declared as R4 (GSCI / BCOM January reweighting, 1 a year, 4 in IS) and R6 (metals rolls, gold's
calendar spread is pure financing) were ruled out by count / arithmetic and not computed. R5 (IC's own CFD roll) has no
switch day to study: IC interpolates continuously.

## PREREG_DRAFT
None.

## Correlation with C3
Not computed (nothing survived).

## Directions that need the user
| direction | value |
|---|---|
| A broker / venue with dated (single-contract) energy CFDs or futures access, to trade the C2 - C1 calendar spread over the roll (CL 2012-17: R1 +10.8 bp, sd 63.5, per-window Sharpe 0.17; R2 +8.9, sd 48.2, 0.19; gross, before two legs of cost; shrinking since 2000-11) | LIVE < 1 % (power ~0.8 on 21 HOLD windows even before cost), DEMO ~1-2 % |
| IC's written rollover / interpolation rule for XTI / XBR / XNG (would confirm the price-level inference; no edge expected) | < 1 % |

## Exhausted (add to PROMPT "Những họ đã cạn")
- Scheduled commodity-index / ETF roll flows (GSCI BD 5-9, BCOM BD 6-10, pre-2020 USO) on outright energy CFDs: the
  pressure is in the calendar spread (+18 / -35 bp around the window on CL, 1995-2017, shrinking). Contract 1 alone does
  not show it (PRE 1995-2017 and IC 2018-24). 12 windows a year cannot reach DEMO at any size the literature supports.
  IC's XTI / XBR are continuously interpolated between the front two contracts (no roll day), and XNG follows NG1.

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r39/R/scripts/common.py`,
  `track.py` (contract tracking), `xbrjump.py` (XBR switch search), `grade.py` (cells, controls, random entry).
- Outputs: `.../scratchpad/r39/R/out/track.txt`, `xbrjump.txt`, `grade.txt`, `grade.json`, `spread_sd.txt`;
  literature PDF and its text extract in `.../scratchpad/r39/R/web/lit/`; fetch log `.../scratchpad/r39/R/web/requests.log`.
