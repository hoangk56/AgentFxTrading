# Round 41 stream B: US equity issuance supply from SEC EDGAR -> US500, USTEC, US2000 (US30 control)

Written 2026-10-30 (UTC). Hypotheses with timestamps, before any return: [HYPOTHESES_B.md](HYPOTHESES_B.md) (main grid
04:34 UTC, parse corrections and counts 04:38, by-products 04:40). Same LIVE / DEMO bars as research/PROMPT.md.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. EDGAR issuance counts were loaded as an aggregate daily supply series for
the first time (IPO prospectuses, shelf takedowns, secondary sales, tender offers, IPO lock-up expiries, IPO
effectiveness notices). On the declared short side, supply days are followed by *higher* index prices in IS: issuance
comes in hot markets (Pastor & Veronesi), so the short pays the drift and the bull run. The one sign-consistent piece
is a small continuous slope: the next-day return falls by ~5 bp per sd of shelf / total supply in IS (t ~ -2.1) and
~2-5 bp in VAL (t -0.4 to -1.0). That is 0.06 Sharpe a day at mid, so HOLD power is <= 1.2 at zero cost. LIVE was
ruled out by the count before any return was computed.

## Sources
- SEC EDGAR quarterly full index `full-index/<YYYY>/QTR<q>/master.gz`, 2015 Q1..2024 Q4: 40 files, all HTTP 200
  with a generic research User-Agent (no name or e-mail), sequential with >= 0.25 s spacing, 26 s and ~131 MB in
  total (log: scratchpad `web/requests.log`). No 2025+ file was requested; 0 rows dated after 2024-12-31 (the cut is
  also applied at parse). 10.56 M index rows.
- Only index files were requested (brief rule), so there are **no acceptance times and no offering sizes**. Timing
  used instead: a filing dated D was accepted by 22:00 ET on D at the latest (Reg S-T 232.13), and every entry is
  after that (E1 = 09:31 ET on the next trading day, E2 = 04:00 ET on the next trading day).
- Not used / unusable: 8-K item 8.01 buyback authorisations (the item list sits in each filing's header, not in the
  index: ~70k 8-Ks a year, dropped as not cheap); offering sizes (need the documents); PRE 2004-15 (no US index price
  series in research/data before 2016, so there was no reason to pull 2004-14 indexes).
- Prices: IC M1 US500 / USTEC / US30 (bid c, ask ca) and US2000 bid zbars (fixed 0.34 pt spread, round 7), all cut
  before 2025-01-01 at load.
- Parse lessons (fixed before returns): the index repeats a co-registrant filing once per CIK, with the CIK in the
  path, so you have to count distinct accession numbers (one 424B5 on 2016-06-30 had 646 guarantor rows). SC TO-I is
  ~75 % closed-end / interval funds and BDCs, so the name filter applies to it too.

## Event counts and power (before returns)
Filings per trading day IS / VAL: IPO (424B4 + 424B1, SPAC / fund / ABS / bank names dropped) 2.0 / 1.6, SHELF (424B5)
9.8 / 9.1, SEC (424B7) 0.75 / 0.79, BUY (SC TO-I, filtered) 0.43 / 0.43, LOCKUP (IPO + 180 days) 1.9 / 1.8. Trigger
days z >= 1.0: 200-300 IS, 90-160 VAL, 52-91 HOLD at the VAL rate; z >= 1.5: 51-140 / 33-87 / 19-50. So LIVE needs a
per-trade net Sharpe of 0.31-0.69 (35-75 bp on a 1-day US500 trade). The inelastic-markets size is ~0.5-6 bp, and a
square-root upper bound ~11 bp. DEMO needed a Sharpe of 0.12-0.28 in IS.

## Main grid (144 counted cells: 6 signals x k {1.0, 1.5} x h {1, 3} days x {E1, E2} x 3 symbols)
Best cell per family by IS net t (any clock). mid / net in bp per trade with the declared side, t = min(day-clustered,
Newey-West lag 3 for h = 3); power = per-trade net Sharpe x sqrt(expected HOLD trades), at IS and VAL size.

| hypothesis (side) | cell | IS mid (t) | cost | net IS (t) | net VAL (t) | VAL / IS | Sharpe IS, power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| B1 IPO 424B4/B1 (short) | US2000 k1.5 h1 E1 | -6.7 (-0.52) | 3.5 | -10.2 (-0.79) | +8.1 (0.47) | <0 | -0.07, -0.38 / 0.36 | 0.40 / 0.66 | none; 16 / 24 cells IS t <= -2 (wrong side) |
| B2 SHELF 424B5 (short) | US2000 k1.5 h1 E1 | +32.7 (1.59) | 3.5 | +29.2 (1.42) | -29.0 (-1.30) | <0 | 0.20, 0.89 / -0.99 | 0.98 / 0.16 | none |
| B3 SECONDARY 424B7 (short) | US500 k1.5 h1 E1 | +9.4 (0.93) | 2.9 | +6.5 (0.65) | -28.2 (-2.52) | <0 | 0.06, 0.36 / -1.92 | 0.98 / 0.01 | none |
| B4 ALL-EQ B1+B2+B3 (short) | US2000 k1.5 h1 E1 | +18.8 (1.02) | 3.6 | +15.2 (0.83) | -63.0 (-2.91) | <0 | 0.11, 0.50 / -2.22 | 0.93 / 0.02 | none; VAL index *rises* after heavy-supply days (US500 k1.5 h1 -55.4 bp for the short, t -3.98) |
| B5 BUYBACK SC TO-I (long) | USTEC k1.0 h3 E2 | +40.0 (3.10) | 12.2 | +27.8 (2.16) | +16.9 (0.82) | 0.61 | 0.14, 1.31 / 0.63 | **0.76** / 0.78 | none: meets t >= 2 / VAL > 0 but beats only 76 % of random longs (DEMO needs 90 %); null p 0.35; it is the long drift |
| B6 LOCKUP IPO + 180 d (short) | US2000 k1.0 h1 E1 | +11.6 (1.04) | 3.0 | +8.6 (0.77) | +14.4 (0.95) | 1.7 | 0.05, 0.37 / 0.72 | 0.92 / 0.85 | none; k1.5 h3 flips sign: IS t -1.2..-2.5, VAL t +2.0..+2.8 |

- Cells: 144 counted (+48 US30 control). Only 2 cells reach IS net t >= 2, both B5 USTEC k1 h3 (E2 2.16, E1 2.07).
  Best-of-144 null (200 circular shifts of every signal inside IS, all cells recomputed) gives max IS t median 1.93,
  p95 3.07, and P(max >= 2.16) = 0.35. 34 of 144 cells have IS t <= -2 against the declared side. Mean IS t over
  cells -0.80, mean VAL t -0.38.
- Spread x1.5 and +1 minute change every best cell by < 2 bp (cost is 3-4 bp for h1, 5-12 bp for h3 incl. swap).
  Ex 2020-03/04, no best cell changes sign (B5 USTEC k1 h3 E2 IS +27.8 -> +20.3; B4 US500 k1 h3 -28.9 -> -28.3).
- Years: no supply-side cell is positive in >= 2/3 of IS years and >= 2/3 of VAL years at once. The k1.5 shorts are
  4-5/6 IS years positive and 0/3 VAL years.

## By-products (declared 04:40 UTC, after the main grid failed; 18 cells, all E1, k 1.0, short)
| by-product | best cell | IS mid (t) | net IS (t) | net VAL (t) | random IS / VAL | verdict |
|---|---|---|---|---|---|---|
| (a) IPO pipeline: EFFECT on a recent S-1 / F-1 filer with no prior 424B4 (531-1,291 a year) | US2000 h1 | -20.1 (-2.21) | -23.5 (-2.58) | +0.1 (0.00) | 0.07 / 0.58 | none: all 6 cells IS t -2.6..-5.2, the wrong side (index rises after IPO-pipeline days; US500 h3 -47.2 bp, t -5.20); VAL ~0 |
| (b) settlement day of B4 triggers (D + 2 / D + 3) | US2000 h3 | -15.2 (-0.69) | -21.1 (-0.95) | +7.2 (0.23) | 0.53 / 0.67 | none: 5 / 6 cells IS t <= -1.1, wrong side |
| (c) weekly B4 supply -> short next week (56 IS / 29 VAL weeks) | US2000 h3 | +11.8 (0.31) | +6.8 (0.18) | -38.9 (-0.73) | 0.70 / 0.32 | none: other 5 cells IS t -1.4..-2.9, wrong side |

Family total 162 cells; no cell is positive on the declared side in both IS and VAL with IS t >= 2.

## Mechanism diagnostic (declared, not a cell)
OLS of the next-day E1 -> E1 mid return on z_D (HC t). Per sd of supply z, in bp:

| signal | US500 IS / VAL | USTEC IS / VAL | US2000 IS / VAL |
|---|---|---|---|
| ALL-EQ | -4.66 (-2.16) / -1.28 (-0.37) | -3.86 (-1.50) / -2.35 (-0.51) | -6.00 (-2.04) / -4.48 (-0.95) |
| SHELF | -5.04 (-2.23) / -2.18 (-0.64) | -4.96 (-1.80) / -3.31 (-0.72) | -5.96 (-1.97) / -4.78 (-1.02) |
| IPO | -1.25 (-0.52) / -2.08 (-0.58) | +0.77 (0.27) / -2.55 (-0.53) | -2.13 (-0.63) / -3.92 (-0.79) |
| SECONDARY | -1.33 (-0.51) / +4.66 (1.20) | -1.50 (-0.48) / +5.20 (1.01) | +0.96 (0.27) / +3.30 (0.61) |

- Shelf (424B5) supply has the declared sign in all 6 symbol x era cells. It survives the prior-5-day return
  control (US500 IS -4.50, t -2.09) and dropping 2020-03/04 (US500 -4.90, t -2.25). corr(z, prior 20-day return)
  = +0.12 IS / +0.17 VAL: supply follows rises.
- That is a per-day Sharpe of ~0.056 IS / ~0.013 VAL at mid, so HOLD power at 435 days is 1.2 / 0.28 before
  costs. A daily z-weighted long / short book would pay ~1.5 bp a day on US500. It cannot reach DEMO (it would need
  an IS net t >= 2 after cost) or LIVE. It was not declared as a tradable cell, and VAL is now seen, so it is
  reported, not graded.
- The trigger-day shorts fail for two reasons. They bear the 2016-21 drift (~+5 bp a day), and the extreme-supply
  days (k 1.5) come in rallies that kept going in VAL.

## Correlation with C3
Not computed (nothing survived).

## Exhausted (add to PROMPT "Những họ đã cạn")
- Aggregate US equity issuance from the EDGAR index (IPO 424B4/B1, shelf 424B5, secondary 424B7, IPO effectiveness,
  settlement day, weekly totals), issuer tender offers (SC TO-I), IPO lock-up expiries (IPO + 180 days) ->
  US500 / USTEC / US2000 at 1-3 days. Issuance is a hot-market indicator, not a supply shock the index has to absorb.
  The small shelf-supply slope (~5 bp per sd IS, ~2-5 VAL) is far below LIVE power.

## Pitfalls
- master.gz repeats co-registrant filings per CIK, with the CIK in the path: dedupe by accession number (basename).
- SC TO-I is mostly funds and BDCs. 424B2 is bank structured notes, and 424B5 also carries corporate debt that a
  name filter only partly removes. SPAC IPOs (2020-21) use 424B4: drop "ACQUISITION" names.
- The index has filing dates only. An acceptance time needs each filing's header, which this brief did not allow.
- The whole 2015-24 index pull takes ~30 s. SEC accepted a generic research UA with no contact address (HTTP 200 x 40).

## Directions that need the user
| direction | value |
|---|---|
| Per-filing headers / documents (acceptance time to the second, offering size in dollars, 8-K item 8.01 buybacks): ~10k 424B + ~70k 8-K requests a year, hours of polite crawling (allowed by SEC, outside this brief) | LIVE < 1 %, DEMO ~1 % (the size-weighted series is the only untested part; issuance follows rallies whatever its size) |
| Paid dealogic / SDC new-issue data with pricing times and sizes | LIVE < 1 %, DEMO ~1 % |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r41/B/scripts/`
  (fetch.py, parse_index.py [python -I], lib.py, counts.py, grade.py, byproducts.py, diag2.py).
- Outputs: `.../scratchpad/r41/B/out/` (daily_counts.csv, cells.csv, byproducts.csv, grade.log, byproducts.log,
  diag2.log, null_maxt_IS.npy). Downloads: `.../scratchpad/r41/B/web/` (requests.log).
