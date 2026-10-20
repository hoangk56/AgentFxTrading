# Round 23, stream N: the newest literature (2025-01 to 2026-10), declared rules only (2026-10-15)

Brief: [BRIEF.md](BRIEF.md) row N and round13_structural/BRIEF.md. Every cell was declared in
[HYPOTHESES_N.md](HYPOTHESES_N.md) at 11:12 UTC (`date -u`) before any of its returns was computed; the diagnostics
declared there at 11:18 UTC came after the main numbers and are information only. HOLD (2025-01 onwards) was not
loaded: the shared panel ends 2024-12-31 and the Dukascopy H1 files end 2015-12-31.

## Answer
**No LIVE candidate. One declared cell meets the DEMO numbers on IS but is not recommended:** long gold from 16:00 New
York two NYSE days before Christmas to two days after (N3b, Vojtko & Dujava 2025): net +81.8 bp (t 3.61, n 6) IS,
+75.8 (t 2.20, n 3) VAL, +103.0 (t 3.17, n 12) PRE, 9/9 years > 0 in 2016-24. It is one trade a year (power 1.7-1.9
at full size; HOLD holds one event), its VAL random-entry percentile is 82 %, the source chose Christmas after seeing
2005-2025, and post-hoc checks show a turn-of-year gold and dollar seasonal rather than a Christmas effect. Draft:
[PREREG_DRAFT_N_gold_christmas.md](PREREG_DRAFT_N_gold_christmas.md) (recommendation: do not open HOLD for it alone).

The other four families fail. The largest new effect is real at mid but sits inside IC's rollover spread: the FX
daily-reopen gap fade (Tolusic 2026) reverts +1.0 / +2.0 bp at mid (t 8.7 / 24.8) and pays 3.2 / 5.1 bp to trade.

## Step 1: search (log in HYPOTHESES_N Step 1; raw files under the scratchpad `r23/N/lit/`)
- Crossref, every 2025-01-01..2026-10-15 record of 30 journals by ISSN (15,786 records) and of the NBER and Fed Board
  DOI prefixes (2,990); the ECB and Bank of Canada prefixes return no 2025-26 records.
- arXiv API, the full q-fin (7 categories) and econ.GN listing for the same dates (6,939 records, API totals
  reconciled).
- Crossref keyword queries restricted to SSRN's prefix (36 queries, 997 rows). SSRN's site did not respond, as in
  rounds 12 and 19, so SSRN-only papers were read from Crossref/OpenAlex abstracts and Quantpedia write-ups.
- A title/abstract filter (timing word x asset word) kept 462 of 23,880 unique records; read by hand. Abstracts from
  OpenAlex (Elsevier abstracts mostly withheld), Crossref and NBER pages. 30 web searches / fetches
  (`lit/web_queries.txt`): BIS, ECB and BoJ working-paper pages gave nothing with a side and window on IC symbols.

## Step 2: map (40 rows in HYPOTHESES_N)
- 5 families declared and tested (N1-N5).
- Already mapped or tested: 13 rows (K/T/TRIAGE or rounds 3-21: Harvey et al. rebalancing, crypto-weekend -> Monday,
  Deribit expiry, BoJ ETF, Treasury auctions, Krohn W-shape, Seeck, Ladia, LETFs, Chinese gold night session, BTC
  ETF window, FOMC crypto volatility, dividend days).
- Excluded families (PROMPT): the SPY noise-area intraday breakout (Zarattini et al.; out of sample Sharpe 0.39 in
  Paz 2026) and Quantpedia's BTC 10-day-high overnight rule (C1-type breakout); gold outside COMEX pit hours
  (unconditional clock window).
- Not declarable: side or window not in the readable text (Ewald et al. 2025 Brent intraday seasonality, the most
  relevant paper, paywalled with an embargoed repository copy; Aalipour et al. 2026 crypto weekday hours; oil skewness
  -> FX), no side (Elms 2026 expiry ranges, European 0DTE costs, ECB communication tone), horizon a month or more
  (Bartram et al. 2025, Guo 2025), symbols not at IC (Chilean pension flows, Chinese crude), too rare (Japanese
  interventions), or data the repo lacks (BTC ETF flows 2024+, Deribit option positions, tweet text).

## Step 3: results (bp per trade; t clustered by UTC day; N3/N4 one trade per event)
Costs = actual spreads at both fills + 0.6 bp FX/metals + swaps (N3/N4). Power = per-trade net Sharpe x
sqrt(1.73 x trades/yr). "Random" = share of random-entry seeds the cell's net mean beats (IS / VAL).

| cell (source) | where | PRE mid / net (t) | IS mid (t) / VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL/IS | power IS / VAL size | trades/yr | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| N1a fade daily-reopen gap >= 1 pip, 1 h (Tolusic 2026) | 6 USD pairs pooled | - | +1.00 (8.72) / +2.00 (24.80) | 3.23 / 5.13 | -2.23 (-19.0) / -3.14 (-33.0) | n/a (both < 0) | -12.4 / -29.4 | 722 / 874 | 0 % / 0 % (mid: 100 % / 100 %) | fails: below cost |
| N1b same, entry 17:05 NY | same | - | +0.68 (6.19) / +1.33 (17.25) | 2.95 / 4.40 | -2.26 (-19.9) / -3.07 (-35.2) | n/a | -13.0 / -30.1 | 722 / 874 | - | fails |
| N1c gap >= 2 pips | same | - | +1.24 (6.70) / +2.47 (26.57) | 3.57 / 5.46 | -2.33 (-12.2) / -2.99 (-28.5) | n/a | -8.6 / -24.4 | 415 / 604 | - | fails |
| N2a next-day session against the day's asymmetry (Valenti 2026) | US500 | - | +3.85 (1.90) / -0.59 (-0.18) | 1.85 / 0.80 | +2.00 (0.99) / -1.39 (-0.42) | -0.69 | 0.53 / -0.32 | 236 / 249 | 96.8 % / 44.2 % | fails (IS net t < 2, VAL < 0) |
| N2b long only after negative asymmetry | US500 | - | +5.93 (2.00) / +1.22 (0.25) | 1.85 / 0.81 | +4.08 (1.38) / +0.41 (0.08) | 0.10 | 0.74 / 0.06 | 118 / 122 | 93.4 % / 43.6 % | fails, decaying |
| N3a long gold D-2 -> D+2, 4 festivals (Vojtko & Dujava 2025) | XAUUSD | +34.7 / +31.7 (0.90) | +26.2 (1.14) / +2.5 (0.07) | 3.80 / 6.27 | +22.4 (0.97) / -3.7 (-0.10) | -0.17 | 0.52 / -0.08 | 4 | 73 % / 40 % | fails |
| **N3b same, Christmas only** | XAUUSD | +106.1 / +103.0 (3.17) | +85.6 (3.73) / +83.1 (2.51) | 3.85 / 7.28 | **+81.8 (3.61) / +75.8 (2.20)** | 0.93 | 1.94 / 1.67 | 1 | 93.2 % / 81.6 % | DEMO numbers on IS; 1/yr; see draft |
| N4a long BTC D-1 -> D+1 around NYSE holidays (Quantpedia 2025) | BTCUSD | - | -10.4 (-0.09) / +77.7 (1.00) | 32.4 / 21.2 | -42.8 (-0.35) / +56.5 (0.73) | n/a | -0.19 / 0.55 | 6 / 9 | 30 % / 79 % | fails |
| N5a fade the "dark" return in the pre-market 04:00-09:30 ET (Perreten 2026) | US500 | - | +1.58 (1.53) / +1.23 (0.69) | 1.90 / 0.79 | -0.32 (-0.31) / +0.44 (0.24) | n/a | -0.16 / 0.19 | 246 / 250 | 78.5 % / 70 % | fails |
| N5b short the pre-market | US500 | - | -2.57 (-2.49) / -0.06 (-0.03) | 1.90 / 0.79 | -4.47 (-4.33) / -0.85 (-0.47) | n/a | -2.32 / -0.36 | 246 / 250 | 49 % / 70.5 % | fails, wrong side in IS |

Spread x1.5 and +1 minute for every cell are in `out/*.out`; none changes a verdict (N3b: +81.3 / +75.6 at x1.5,
+80.5 / +75.2 at +1 minute).

### Per family: best cell, cells tried, chance
| family | cells | best cell on its declared side | best \|t_IS mid\| | chance (max of K normals: median / p95) | verdict |
|---|---|---|---|---|---|
| N1 FX reopen gap fade | 3 (+2 information rows) | N1c, mid +1.24 (t 6.70), net -2.33 | 8.72 (N1a) | 1.26 / 2.39; sign-flip-per-day null shared by the 6 pairs: 0.95 / 2.09 | real at mid, far below cost |
| N2 asymmetry contrarian | 2 | N2b, net +4.08 (t 1.38) IS, +0.41 VAL | 2.00 | 1.05 / 2.24 | fails |
| N3 gold festivals | 2 | N3b, net +81.8 (t 3.61, 5 df) | 3.73 | 1.05 / 2.24 (normal); t5: P(\|t\| >= 3.61) = 0.015 | N3b DEMO numbers on IS, rare |
| N4 BTC holidays | 1 | N4a, net -42.8 IS | 0.09 | 0.67 / 1.96 | fails |
| N5 pre-market reversal | 2 | N5a, net -0.32 IS | 2.49 (N5b, wrong side) | 1.05 / 2.24 | fails |

All 10 cells: expected max |t| of 10 normals 1.83 (p95 2.80). N1's mid t is far beyond it (a real effect below cost);
N3b's net t 3.61 on 6 trades has P = 0.015 alone, ~0.14 as the best of 10 (PRE t 3.17 on 12 is the independent
support).

## What the numbers say
- **N1 (Tolusic 2026).** At IC the "daily reopen" is the 17:00 New York rollover: 85 % of reopen bars are the 17:01
  bar, |gap| averages 1.5-2.9 pips and is >= 1 pip on 42-57 % of days. The gap does revert within the hour, beyond any
  random hour (mid +1.0 bp IS, +2.0 VAL, every pair and year, more for bigger gaps: +1.9 / +3.9 at >= 5 pips). But the
  quotes that make the gap are the rollover's wide quotes: entering one minute after the reopen costs 3.2 / 5.1 bp a
  round trip (EURUSD 1.9 / 3.4, USDCHF 4.8 / 8.7), and waiting to 17:05 lowers the cost and the reversion together
  (net -2.3 / -3.1). The paper's profit factor of 2.63 "net of per-pair spreads" is the rollover spread charged at
  a constant normal-hours level. Holding to the next day's close is worse (-4.2 / -6.1, swap included), as the paper
  says. Same lesson as round 12's Sydney and rollover cells.
- **N2 (Valenti 2026).** The contrarian next-session effect exists in IS at mid (+3.9 bp, t 1.9; 2020 carries +15 bp
  of it) and is gone in VAL (-0.6). Long-only after negative asymmetry keeps a tenth of its IS net in VAL.
- **N3 (Vojtko & Dujava 2025).** The four-festival rule fails (Lunar New Year and Eid are negative in VAL; Diwali ~0);
  only Christmas carries the source's result, in every era. Post hoc (HYPOTHESES_N H1-H3): the same window around 1
  January is as strong (PRE +112, IS +113, t 2.33), weeks in early December are not, and EURUSD, silver and platinum
  rise in the Christmas window too (EURUSD PRE t 2.16, VAL t 4.13). This is the turn-of-year gold seasonal plus the
  year-end dollar fall, not festival gift buying; gold still beats EURUSD by ~70 bp per event.
- **N4 (Quantpedia 2025).** BTC around NYSE holidays: -10 bp mid IS, +78 VAL, on a 400-500 bp sd; IC's crypto swap (~5
  bp a night, x3 on Friday) costs 21-32 bp a trade. 22 of 83 windows could not be filled (no IC BTC quote within 30 min of a fill:
  2016-17 data gaps and some year-end days).
- **N5 (Perreten 2026).** The US500 CFD does not fall in the pre-market: in IS it rises (-2.6 bp for the paper's
  short, t -2.5), and the conditional reversal of the night's move is +1.6 / +1.2 bp at mid against ~1-2 bp cost. The
  paper's result is for single stocks' pre-market trades; the index future trades through the night and its price
  discovery is already done.

## Correlation with C3 (IS + VAL)
N3b only (the one cell with DEMO numbers): daily -0.004, monthly +0.28 (9 December points; C3 has no trade on N3b's
exit days).

## Surprises
- The largest new effect of the round (N1, t 25 at mid in VAL) is a quote-mechanics effect that lives exactly where
  IC's spread is widest; a literature "net" result can be a spread-model artifact.
- Gold's late-December rise is stable over 21 years (PRE 9/12, IS+VAL 9/9) and extends into early January; part of it
  is the dollar.
- The pre-market weakness documented for stocks is the opposite sign on the US500 CFD in 2016-21.

## Needs the user
- **Ewald et al. 2025 (Quant. Finance) full text**: the only 2025-26 paper with explicit intraday long/short times on an
  IC symbol (ICE Brent, 2010-21, significant alphas after costs); the times are not in any readable copy (SSRN
  unreachable, Glasgow copy embargoed to 2027-02). With the paper, its windows could be declared on XBRUSD 2018-24.
- Whether to run N3b on the demo account (one trade a year) or to look at the broader turn-of-year gold / dollar
  window on data after 2026-09-24 (post hoc now).
- Data from 2024 onwards only (no IS/VAL under the fixed eras; earliest testable 2024-01, expected power at 250
  events/yr and an unknown size is unknowable until a new era rule exists): Schmidt & Kraft 2026 (BTC trading into the
  New York benchmark window since the spot ETFs), spot BTC ETF flows (Mazur & Polyzos 2025, Lim 2026), European 0DTE
  (Eurex daily options since 2023).
- Paid / new data: Deribit option positions (Shen, Li & Luo 2026), SSRN access for the full texts of Valenti 2026 (to
  replace my reconstructed asymmetry formula), Aalipour et al. 2026 (crypto weekday hours) and Tolusic 2026 (which
  venue's daily break).

## Untested ideas
- N1 at a venue whose reopen spread is near its normal-hours spread (the reversion is +1-2 bp at mid; at EURUSD's
  normal ~0.2 pip + 0.6 bp commission it would clear cost): a venue decision, same as round 16's.
- The turn-of-year window (≈ 22 Dec -> early January) in gold, silver and EURUSD as a declared rule on new data.
- Valenti's rule with the paper's exact formula once readable (the reconstructed one decays in VAL).
- Ewald et al.'s Brent windows (needs the paper).

## Scripts and outputs (scratchpad, not in the repo)
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r23/N/`
- `scripts/cr_harvest.py`, `cr_query.py`, `ax_harvest.sh`, `oa_abs.sh`, `lit_filter.py`: the literature harvest;
  `lit/` holds the raw records, logs (`lit/cr/log.txt`, `lit/ax/log.txt`, `lit/ssrn/log.txt`, `lit/oa/log.txt`,
  `lit/web_queries.txt`), `lit/filtered.tsv` and the abstracts.
- `scripts/nlib.py` (panel access, New York clock, fills at t+1, actual spreads, swaps, day-clustered t, power),
  `n1_gapfade.py`, `n1_ctrl.py`, `n25_us500.py` (N2, N5), `n34_holidays.py` (N3, N4, PRE), `n3_diag.py` (post hoc).
- Outputs: `out/n1.out` (per pair and year), `out/n1_ctrl.out`, `out/n25.out`, `out/n34.out`, `out/n3_diag.out`,
  `out/*_recs.pkl` (trade lists).
- Calendars (shared, reusable): `r23/shared/cal/cal_N.json` (NYSE closures 2004-24, recurring vs special; Christmas,
  Lunar New Year, Diwali, Eid al-Fitr dates 2004-24) from `r23/shared/cal/make_cal_N.py` with the scratch venv
  `r23/shared/venv_extra` (python holidays 0.106).
