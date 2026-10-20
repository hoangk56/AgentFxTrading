# Round 25, stream C: older literature (<= 2017) and non-English practitioner lore, declared only (2026-10-17)

Brief: [BRIEF.md](BRIEF.md) row C, round13_structural/BRIEF.md, round23_recent/BRIEF.md. Hypotheses, search log, census
map and lore map: [HYPOTHESES_C.md](HYPOTHESES_C.md). Every tested cell was declared there with its `date -u` time
before any of its returns was computed (Declaration 1, 2026-10-17 19:33:56 UTC: MON, BAR; Declaration 2, 19:53:57
UTC: JPN). HOLD (2025-01-01 onwards) was never loaded: the shared panel ends 2024-12-31, the one Dukascopy file used
(XAUUSD m1c) was cut at 2016-01-01 at load, and the `*_2026.npz` files were not opened.

## Answer
**No LIVE or DEMO candidate; no PREREG_DRAFT.** The census (13,748 literature records, 353 kept and mapped into 39
families; 59 non-English lore claims) finds that almost every short-horizon effect with an explicit side and window in
IC's 26 symbols was already tested in rounds 3-24. Three families were untested and declared (10 cells); all fail:
- **MON** (Abraham & Ikenberry 1994; Wang, Li & Erickson 1997; Sun & Tong 2002): the Monday after a down Friday is not
  lower in 2016-24. US500 short Friday close -> Monday close after a down Friday: IS net -10.2 bp (t -0.69), VAL +6.7
  (t 0.44).
- **BAR** (Donaldson & Kim 1993; Cyree et al. 1999; Osler 2005; Aggarwal & Lucey 2007): following a break of a round
  number (100 index points, $10 gold) for 60 minutes is real at mid in IS when pooled (+1.20 bp, t 2.72), but costs
  2.5 bp (net -1.30, t -2.98; VAL net -0.92), and the half-level placebo is as strong in IS (+1.06, t 2.20). In
  indices it is crossing momentum, not a barrier. The daily version reverses (IS net -8.2, t -3.0).
- **JPN** (lore JA-21: Nikkei first TSE business day up, last business day down, from monthly investment plans and
  employee share plans): IS net +22.5 bp (t 1.96, just under DEMO's 2.0), VAL +0.6 (t 0.04), +1 minute negative in VAL.
  The IS effect does not survive into 2022-24.

**The one durable new effect is gold's round-number continuation, below IC's cost.** It is information: gold was one
leg of the pooled BAR-i cell, so picking it out is post hoc. A break of a $10 level continues for 60 minutes at mid
in every era: PRE 2004-15 +3.50 bp (t 4.86, 12/12 years), IS +2.77 (t 3.31), VAL +2.06 (t 2.39). The $5 half-level
placebo does not continue (PRE +1.31, IS -0.44, VAL -0.84), and random entries with the same side rule are beaten 100 %
in all three eras. PRE was declared before it was computed, so it is an independent era for the mechanism. At IC's
cost it nets +1.10 (t 1.31) IS and +1.02 (t 1.19) VAL, which fails DEMO on the IS t; even at zero cost its VAL-size
power would be ~1.9. A post-hoc split puts the effect in 12:00-17:00 UTC (COMEX / US hours), where it nets
+2.8 / +3.1 / +3.2 bp (t 2.15 / 2.16 / 2.17) in PRE / IS / VAL. Those are DEMO-like numbers, but they were found after
looking, so they stay information only. The power at the VAL size is 1.68, below LIVE even at face value (section "The
post-hoc gold lead").

## Census counts
| stage | count |
|---|---|
| literature queries | OpenAlex 74 topic (19:04-19:08 UTC) + 80 title lookups (7 answered, then the IP's free daily budget ran out); Crossref 74 topic (19:08-19:11) + 73 title lookups (19:11-19:13); arXiv 74 (19:11-19:16; 7 records); Semantic Scholar 18 attempts 19:08-19:53 (2 answered, 16 HTTP 429); SSRN unreachable; 4 web searches + 2 page fetches for missing abstracts |
| lore queries (helper, 19:09-19:48 UTC) | 71 web searches run (ja 39, zh 14, ko 7, de 11), 10 not run (shared session search budget exhausted), 19 direct page opens; 80 pages, 59 read |
| records | 13,748 unique (OpenAlex 9,154; Crossref 5,054; arXiv 7), 8,909 with an abstract, 13,674 dated <= 2017; Semantic Scholar added 149 new, 16 past the filter, none kept |
| filtered (timing word x asset word, <= 2017) | 2,965; 248 auto-dropped (volatility / spread / liquidity / volume titles) |
| triaged by title and abstract | 2,717 in three passes: F 1,030 (92 kept), I 1,023 (176 kept), O 664 (85 kept) |
| dropped at triage, by reason | off-topic 874; emerging / non-listed markets 230; volatility-type 225 (+248 auto); method only 248; single stocks 228; no direction 274; horizon > 5 days 150; surprise-dependent news 99; technical rules 36 |
| mapped | 353 literature rows into 39 families (L1-L39); 59 lore claims (A 12, B 27, C 20) + 14 excluded C3-zone claims |
| literature families dropped, by reason | already tested by rounds 3-24 or an exhausted PROMPT family 27 (L1-L5, L9, L10, L12, L14-L17, L20-L22, L24-L29, L31-L33, L35-L37); no flow / settlement / premium basis or 1 event a year 3 (L11, L19, L23); source's own out-of-sample note says gone, plus power 2 (L8, L34); needs data or symbols outside the 26: 2 (L30, L39); predictable-surprise constructions: 1 (L13, energy releases: no API values in the FF file; anchoring not tested on energy CFDs by B, listed under untested ideas; the FX part of L33 is B's); methodological 1 (L38) |
| lore claims, by decision (59) | tested by earlier rounds (month-end fix, gaps, Tokyo-hour clocks, weekdays, turn of month, expiries, SQ, CB days, overnight, opens) 22; 1 event a year 5 (JA-09, JA-10, JA-11, JA-13, JA-32); data-mined day-of-month counts 4 (JA-05..JA-08); no mechanism and a power shortfall 2 (JA-16, JA-23); refuted by its own source 1 (JA-25); regime ended 1 (JA-27, BoJ ETF); not in the 26: 3 (USDKRW, KO-01..KO-03); grade C, no side or window 20; **declared 1 (JA-21 -> JPN)** |
| declared and tested | 3 families, 10 cells: MON-a..e, BAR-i, BAR-d (from L6, L7, L18), JPN-ab, JPN-a, JPN-b (from JA-21); + information rows (per symbol, half-level placebos, XAUUSD on PRE, the post-hoc session split) |

## Results (bp per trade; t clustered by UTC day of entry; cost = half the actual spread at entry and exit + 0.6 bp for XAUUSD + index financing; power = per-trade net Sharpe x sqrt(1.73 x trades/yr))
| hypothesis (source) | where, trades/yr IS / VAL | PRE / IS / VAL mid (bp, t) | cost IS / VAL | net IS / VAL (t) | x1.5 / +1 min (IS; VAL) | VAL/IS net | power IS / VAL | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| MON-a short Fri 16:01 -> Mon 16:00 NY after a down Friday (Abraham & Ikenberry 1994) | US500, 18 / 20 | - / -5.76 (-0.39) / +7.68 (0.50) | 4.46 / 0.95 | -10.23 (-0.69) / +6.73 (0.44) | -11.2, -9.0; +6.3, +6.4 | n/a (IS < 0) | -0.37 / 0.34 | 44 % / 91 % | fails |
| MON-b follow Friday's sign, both sides | US500, 39 / 42 | - / -0.62 (-0.07) / +16.49 (1.96) | 5.91 / 4.96 | -6.53 (-0.71) / +11.53 (1.38) | -7.5, -5.8; +11.1, +10.6 | n/a | -0.38 / 1.05 | 48 % / 98 % (own weekends, random sides: 45 % / 99 %) | fails (IS) |
| MON-c = MON-a, replication | US30 + USTEC, 38 / 40 | - / -3.00 (-0.20) / -0.80 (-0.05) | 4.01 / 0.89 | -7.01 (-0.48) / -1.69 (-0.11) | -7.8, -6.2; -2.0, -1.8 | n/a | -0.34 / -0.11 | 68 % / 81 % | fails |
| MON-d MON-a on Mondays dated 18-26 (Wang, Li & Erickson 1997; Sun & Tong 2002) | US500, 7 / 7 | - / +6.77 (0.39) / -9.82 (-0.60) | 4.52 / 0.65 | +2.25 (0.13) / -10.47 (-0.64) | +1.2, +2.8; -10.9, -11.4 | < 0 | 0.07 / -0.49 | 73 % / 52 % | fails |
| MON-e "week four" short, last NYSE day before the 18th -> 5 days (Sun & Tong 2002) | US500, 11 / 11 | - / +8.74 (0.39) / +11.26 (0.25) | 7.85 / 0.87 | +0.88 (0.04) / +10.39 (0.24) | -0.1, +0.3; +10.0, +10.9 | 11.8 (IS ~0) | 0.02 / 0.18 | 86 % / 81 % | fails |
| BAR-i follow a fresh break of a round level for 60 min (Osler 2005; Donaldson & Kim 1993; Cyree et al. 1999; Aggarwal & Lucey 2007) | 8 index CFDs (100 pt) + XAUUSD ($10), 2,105 / 2,890 | - / +1.20 (2.72) / +0.49 (1.00) | 2.50 / 1.41 | -1.30 (-2.98) / -0.92 (-1.87) | -2.5, -1.4; -1.6, -1.1 | n/a | -2.01 / -1.75 | 100 % / 87 % | fails: below cost |
| BAR-d follow a daily-close break of a 100-multiple to the next close (Donaldson & Kim 1993; Cyree et al. 1999) | 8 index CFDs, 1,068 / 1,289 | - / -4.13 (-1.52) / +0.34 (0.12) | 4.10 / 3.24 | -8.23 (-3.02) / -2.90 (-1.01) | -9.3, -8.0; -3.5, -3.0 | n/a | -2.61 / -1.05 | 0 % / 58 % | fails (reverses in IS) |
| JPN-ab first TSE day long + last TSE day short (lore JA-21) | JP225, 24 / 23 | - / +28.15 (2.46) / +4.56 (0.30) | 5.67 / 4.00 | +22.48 (1.96) / +0.56 (0.04) | +20.9, +22.9; -0.3, -1.8 | 0.02 | 1.05 / 0.03 | 99 % / 59 % | fails (IS t < 2.0, VAL ~0, +1 min < 0) |
| JPN-a first TSE business day long | JP225, 12 / 11 | - / +27.27 (1.58) / +16.45 (0.80) | 6.74 / 4.68 | +20.53 (1.19) / +11.77 (0.57) | +18.9, +20.6; +10.9, +10.7 | 0.57 | 0.64 / 0.43 | 92 % / 68 % | fails |
| JPN-b last TSE business day short | JP225, 12 / 12 | - / +29.01 (1.92) / -6.99 (-0.31) | 4.62 / 3.34 | +24.40 (1.61) / -10.33 (-0.46) | +22.8, +25.0; -11.2, -14.0 | < 0 | 0.87 / -0.35 | 99 % / 48 % | fails |
| *information* BAR-i half-level placebo (L + 50 pt / + $5) | same, 2,108 / 2,903 | - / +1.06 (2.20) / -0.18 (-0.36) | 2.49 / 1.40 | -1.43 (-2.99) / -1.57 (-3.23) | | | | | as strong as the real cell in IS |
| *information* BAR-i XAUUSD leg | XAUUSD, PRE 233 / IS 247 / VAL 348 | **+3.50 (4.86) / +2.77 (3.31) / +2.06 (2.39)** | PRE 1.57; 1.67 / 1.03 | PRE +1.92 (2.67); +1.10 (1.31) / +1.02 (1.19) | PRE +1.44, +1.30; +0.57, +0.82; +0.81, +0.78 | 0.93 | 0.72 / 0.92 (PRE 0.95) | 100 % / 100 % (PRE 100 %) | real at mid in all eras; below DEMO at IC cost; post hoc |
| *information* XAUUSD $5 placebo | XAUUSD | +1.31 (1.79) / -0.44 (-0.48) / -0.84 (-0.97) | | PRE -0.27; -2.11 / -1.88 | | | | | no effect at half levels |
| *post hoc* XAUUSD BAR-i, entries 12:00-17:00 UTC only | XAUUSD, PRE 106 / IS 105 / VAL 148 | +4.32 (3.28) / +4.62 (3.23) / +4.23 (2.84) | PRE 1.50; 1.52 / 1.00 | PRE +2.83 (2.15); **+3.10 (2.16) / +3.23 (2.17)** | IS +2.63, +2.93; VAL +3.02, +2.91 | 1.04 | 1.16 / 1.68 (PRE 0.82) | 100 % / 100 % (500 seeds) | DEMO-like numbers, but chosen after looking: information only; LIVE out of reach |
| *post hoc* same slice, $5 placebo | XAUUSD | +1.93 (1.50) / +1.45 (0.95) / -0.74 (-0.49) | | PRE +0.43; -0.04 / -1.75 | | | | | none |

Per-symbol BAR-i mid (IS / VAL, bp): US30 +1.20 / -0.39, US500 +3.42 / +1.82, USTEC +3.05 (t 2.29) / -0.49, DE40
+1.02 / +0.57, UK100 -2.48 / +0.56, JP225 +1.23 / +0.26, AUS200 +0.29 / -0.45, HK50 +0.48 / +1.47, XAUUSD +2.77 /
+2.06. Only gold is positive at mid in both eras with t > 2, and only gold beats its own half-level placebo in both
eras. Years net > 0: MON cells 1-3 of 6 in IS; BAR-i pooled 1/6 IS, 1/3 VAL; JPN-ab 5/6 IS, 1/3 VAL (2021 alone is
+83.5 bp); XAUUSD BAR-i 5/6 IS, 2/3 VAL, PRE 9/12 (mid 12/12).

## Best cell per family, cells tried, chance
| family | cells | best cell on its declared side | best \|t_IS mid\| |
|---|---|---|---|
| MON | 5 | MON-b: VAL net +11.5 (t 1.38), IS -6.5 | 0.39 |
| BAR | 2 (+ 17 per-symbol, 19 placebo, 2 PRE information rows) | BAR-i pooled: IS mid +1.20 (t 2.72), net -1.30 | 2.72 |
| JPN | 3 | JPN-ab: IS net +22.5 (t 1.96), VAL +0.6 (t 0.04) | 2.46 |

Chance for the 10 declared cells: max |t| of 10 normals, median 1.83 / 95th 2.81; a sign-flip null per UTC day shared
by all 10 cells, median 1.73 / 95th 2.75. The best declared |t_IS mid| (2.72, BAR-i) sits inside both, and its own
half-level placebo reaches 2.20. Correlation with C3 (IS + VAL, information): daily -0.041 to +0.025, monthly -0.085 to
+0.103 for the 10 cells.

## What the numbers say
- **The weekend effect conditional on Friday is gone from US index CFDs.** The published size (-61 bp after a down
  Friday, 1963-91) would give an IS t of ~5 here; the observed IS mean on the declared short is -5.8 bp at mid. The
  week-four concentration is noise (7 events a year, signs flip between eras). This matches the reverse-weekend
  literature in the map: large caps' Mondays turned positive after 1987.
- **Round numbers matter in gold, not in index CFDs.** Index levels at multiples of 100 behave like half levels.
  Gold's $10 levels do not, consistently for 21 years, as Lucey & O'Connor (2016) found for gold but not silver. The
  size (2-3.5 bp per 60-minute trade) is about twice IC's gold round trip at the VAL era's spreads, but the trade's sd
  (~27-32 bp) is too large for the trade count: LIVE power is out of reach at any cost.
- **The Japanese month-turn lore was an IS-era pattern.** The first- and last-day legs earned +20-24 bp a trade in
  2016-21 and nothing in 2022-24; 2021 alone carries much of IS. The source's chart covers 2013-23, so our IS was in
  its sample.
- **The older literature is mined out for this repo.** 27 of 39 families were already tested in rounds 3-24, mostly
  as clock or calendar scans (rounds 3, 4, 11, 13, 15, 18), fix studies (rounds 3, 10, 12, 15, 19) or event studies
  (rounds 3, 6, 10, 11, 20, 21). Where an older paper had a side, the effect either died after publication (FX weekdays
  in the 1990s, the Monday effect after 1987, oil barriers after 2006, FX weekend gaps after 2016) or is below IC's
  cost. The lore adds mostly the same effects in other words: month-end fixes, gaps, Tokyo hours, turn of month.

## The post-hoc gold lead (information; for the lead and the user)
After the declared numbers, I split the gold leg by UTC session (a choice made after looking). The whole effect sits
in 12:00-17:00 UTC, the COMEX / US hours when stop orders in gold futures would execute:
- net +2.83 (t 2.15) PRE, +3.10 (t 2.16) IS, +3.23 (t 2.17) VAL;
- positive at x1.5 and +1 minute in every era; 5/6 IS years and 3/3 VAL years;
- random control 100 %; the half-level placebo is ~0; C3 correlation daily -0.011, monthly +0.000.

Had it been declared it would meet the DEMO numbers. It was not, so under the round-23 rule it is information only and
no PREREG_DRAFT is written. Even at face value it is not a LIVE route: a VAL per-trade Sharpe of 0.105 at ~148 trades a
year (sd ~31 bp per trade) gives power 1.68 over a 21-month holdout. Round 18's retention for post-hoc picks (~1/4)
puts the expected HOLD t near 0.4 (1.1 at the 0.65 retention of declared rules), so opening HOLD for it is not
recommended. The clean test is data nobody has seen, with the rule fixed now:
- XAUUSD mid (bid/ask mean) M1 closes; levels = multiples of $10. An event is a 1-minute bar whose close is on the other
  side of a level than the previous quote (gap <= 5 minutes), when that level was not crossed in the previous 1,440
  minutes.
- Enter in the direction of the break at the close of the next bar, only if that entry falls in 12:00-16:59 UTC; exit
  60 minutes after entry; one open trade at a time.
- Skip entries or exits in 16:55-18:10 New York and within 15 minutes after a > 60-minute quote gap. Cost = half spread
  at entry + half at exit + 0.6 bp.
- Expected ~150 trades a year. A forward t of 2 needs ~2.5 years at the VAL size, ~6 years at 0.65 of it and ~39 years
  at 1/4 of it.

## Needs the user
- Whether to log the gold rule above on data after 2026-09-24 (Dukascopy XAUUSD M1 would be a new fetch; the rule is
  fixed above). It can at most become a DEMO-tier candidate.
- A gold venue with an all-in round trip near 0.3-0.6 bp (round 16's scenario d) would make the full-day gold rule
  positive in every era (IS ~+2.2, VAL ~+1.5 bp), but its power at the VAL size would still be ~1.3-1.6, a DEMO-level
  effect at best, and its selection is post hoc. Not a reason to change venue on its own.
- Lore outside the 26: Korean month-end exporter USD sales (월말 네고), April dividend repatriation (USDKRW), KOSPI
  expiries; CNY settlement before Spring Festival. These need symbols IC's 26 do not include (stream A's route).
- Full texts that were not readable: Dowling, Cummins & Lucey 2016 (only the IDEAS summary), Cho 2017 and Lucey et al.
  2012 (SSRN unreachable), Cornett, Schwarz & Szakmary 1995 (no abstract anywhere reachable).
- The OpenAlex free budget for this IP ran out after 82 answered calls; a key would need an account e-mail, so the
  remaining lookups went to Crossref. The shared web-search budget also ran out mid-census, which left Korean and
  German lore thinner than planned (10 searches not run).

## Untested ideas
- The full-day gold rule on new data (60 min, fresh in 24 h, side = break direction): ~350 trades a year at a net
  per-trade Sharpe of ~0.04 at IC's cost, so a forward t of 2 needs ~7 years; only a cheaper venue changes that.
- The $100 gold levels, other holds (15-30 minutes; the cascade is fast), and silver / platinum round numbers were not
  computed: they would be choices made after seeing the $10 / 60-minute result.
- Osler's first-touch reversal (take-profit clustering at the round number, without a break) needs bar highs and lows;
  the panel holds closes only, while the M1 cache has bid highs and lows.
- Consensus anchoring (stream B's B1) on energy releases: EIA crude inventories on XTIUSD / XBRUSD and EIA gas
  storage on XNGUSD (the FF file has 939 rows of each with forecasts). B found the anchored part already priced in
  FX; with a 55 % sign hit and a release-minute move of ~30 bp, the edge would be ~3 bp against 3-8 bp of energy
  spread at 10:30 ET. Not declared.
- JA-16 (USDJPY firm in US payroll weeks) and JA-17 (yen selling in the Tokyo lunch hour, 03:00-04:00 UTC) were not
  declared: the first has no mechanism and 12 events a year, and the second sits in round 13 M's clock grid.

## Scripts and outputs (scratchpad, not in the repo)
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/C/`
- Literature harvest: `scripts/harvest.py`, `harvest_classics.py`, `harvest_classics_cr.py`, `queries.txt`,
  `classics.txt`, `merge_lit.py`, `prep_triage.py`, `s2_new.py`. Logs and data: `lit/log.tsv` and `lit/log_s2.tsv`
  (every query with UTC time, status, API total and records saved), `lit/records.tsv` (13,748 records),
  `lit/filtered.tsv`, `lit/triage/triage_{F,I,O}.tsv` (decision and reason for every record), `lit/tested_list.md`
  (what rounds 4-24 tested, compiled for this census), `lit/lore/lore_map.md` and `lit/lore/queries.tsv` (the lore
  census and its query log).
- Engine: `scripts/clib.py` (panel access; clocks; fills at t+1 with a 10-minute first-quote rule; executable costs;
  day-clustered t; power; chance; C3 correlation; PRE loader; IC 2016-17 spread profile) and `nyse.py` (NYSE closures
  and early closes).
- Families: `mon_fam.py`, `bar_fam.py`, `jpn_fam.py`, `pre_bar_xau.py`, `report.py`, and `xau_session_info.py` (the
  post-hoc gold session split, random control, years and C3 correlation).
- Outputs: `out/mon.out`, `out/bar.out`, `out/jpn.out`, `out/pre_bar_xau.out`, `out/xau_session_info.out` and
  `out/report.txt` (every cell and information row with x1.5, +1 minute, years, power, random controls, chance and C3
  correlations); trade lists in `out/mon_trades.pkl`, `out/bar_trades.pkl`, `out/jpn_trades.pkl` and
  `out/pre_bar_xau.pkl`.
