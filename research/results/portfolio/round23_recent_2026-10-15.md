# Round 23: recent strategies and hypotheses, 2024-2026 literature and practitioner flows (2026-10-15)

Two streams ([round23_recent/BRIEF.md](round23_recent/BRIEF.md), written 10:57 UTC) worked under the declared-only rule
of rounds 19-22: every cell was declared in full before any return was computed, and the side came from the source.
N mapped the newest literature, 2025-01..2026-10 ([HYPOTHESES_N.md](round23_recent/HYPOTHESES_N.md) at 11:12 UTC,
[STREAM_N.md](round23_recent/STREAM_N.md)). P took practitioner and structural-flow claims from 2023-26
([HYPOTHESES_P.md](round23_recent/HYPOTHESES_P.md) at 11:06 UTC, [STREAM_P.md](round23_recent/STREAM_P.md)). HOLD was
never loaded: the rebuilt minute panel ends at 2024-12-31.

## Answer
**No LIVE candidate.** One declared cell meets the DEMO numbers on IS: N3b, gold long over Christmas, 1 trade a year.
It is drafted in [PREREG_DRAFT_N_gold_christmas.md](round23_recent/PREREG_DRAFT_N_gold_christmas.md) but is not
recommended on its own (see below). HOLD was not opened. The other 27 declared cells fail.

## Results (net bp per trade, t clustered by UTC day; full tables in the STREAM files)
| cell (source) | where | net IS (t) / VAL (t) | verdict |
|---|---|---|---|
| N1 fade the 17:00 NY reopen gap, 1 h (Tolusic 2026) | 6 USD pairs | -2.23 (-19) / -3.14 (-33) | real at mid (+1.0 / +2.0 bp, every pair and year), 3-5 bp below cost |
| N2 contrarian next session after intraday asymmetry (Valenti 2026) | US500 | +2.00 (0.99) / -1.39 | fails |
| N3a gold D-2 to D+2 around 4 festivals (Vojtko & Dujava 2025) | XAUUSD | +22.4 (0.97) / -3.7 | fails |
| **N3b same, Christmas only** | XAUUSD | **+81.8 (3.61, n 6) / +75.8 (2.20, n 3)**; PRE +103.0 (3.17, n 12) | DEMO numbers on IS; power 1.7-1.9 |
| N4 BTC long around NYSE holidays (Quantpedia 2025) | BTCUSD | -42.8 / +56.5 (0.73) | fails |
| N5 fade the pre-market "dark" return / short the pre-market (Perreten 2026) | US500 | -0.32 / +0.44; short side wrong sign in IS | fails |
| P1 vol-control exposure change, top 20 % (S&P Risk Control EWMA; sell-side notes) | US500, US30+USTEC | -2.1 (-0.39) / +10.7 (1.33) | fails; 2020 alone -55 bp |
| P2 threshold rebalancing, equity leg (Harvey, Mazzoleni & Melone, NBER w33554) | US500, +5 indices | -2.2 (-0.73) / -1.4 | fails; paper's next-day effect absent on the equity leg |
| P3 CTA 21/63/252-day signal flips, follow the change (sell-side trigger notes) | 6 pooled | +0.9 (0.34) / +2.8 (0.62) | fails; PRE net t 1.72 but no symbol keeps its sign |
| P4 buyback open window vs blackout (GS estimates, Rule 10b-18) | US500 (+US30, USTEC) | +3.8 (1.22) / +1.1 | fails; blackout days were the strong ones |
| P5 short the week after monthly options expiry | US500 | -26.2 / -50.7 | fails, wrong sign in VAL |
| P6 quarter-end pension rebalancing, \|QTD\| >= 5 % | US500, 3 indices | +36.4 (0.57) / -58.3, n 10 | fails |

Chance: 10 cells in N (max of 10 normals median 1.83, p95 2.80), 14 primary cells in P (best IS mid |t| 1.82 below the
median 1.97). Spread x1.5 and +1 minute change no verdict.

## N3b, why it stays a note
- One trade a year: HOLD holds one event, so the expected HOLD t is ~1.3 at the VAL size and ~0.3 at round 18's
  retention for picks made after seeing data. The paper chose Christmas as its best festival on 2005-2025, which
  covers all our eras, so it counts as such a pick.
- VAL beats only 82 % of random entries (3 trades); DEMO needs 90 %.
- Post-hoc checks (11:18 UTC, information only): the same window around 1 January is as strong, early-December weeks
  are not, and EURUSD, silver and platinum also rise in the window. It is the turn-of-year gold seasonal plus the
  year-end dollar fall, not a festival effect. A declared turn-of-year rule could be tested on data after 2026-09-24.
- Correlation with C3 (IS + VAL): daily -0.004, monthly +0.28 (9 December points).

## What this adds to the standing diagnosis
- The newest papers that state a side and window on IC symbols either restate exhausted families or are below IC's
  cost. N1 is the clearest case: a gap reversal real in every pair and year at mid, whose net profit in the paper comes
  from a constant-spread cost model. At IC the reopen is the 17:00 NY rollover, where spreads are widest.
- Practitioner flows sized at $20-70bn (vol control, CTAs, pensions, buybacks) do not show in 1-5 day index returns.
  Unlike gotobi, they execute at the executor's discretion over hours or days and their triggers are published, so
  they are traded ahead or absorbed.

## Needs the user (added to PROMPT.md)
- N3b as a once-a-year demo, or a declared turn-of-year gold/dollar rule tested on data after 2026-09-24.
- Mechanisms that exist only from 2024: spot BTC/ETH ETF flows into the 16:00 ET NAV, BTC trading into the NY
  benchmark window (Schmidt & Kraft 2026), new-NISA yen selling early in the month (power ~0.5), 0DTE dealer gamma.
  They need a new era rule or post-2026-09 data.
- Bond-leg data (10-year yield or T-note futures) for the rebalancing paper and risk-parity de-leveraging; IC has no
  bond instrument to trade the stock-minus-bond leg.
- Paywalled sources: Ewald et al. 2025 (Quantitative Finance), the only 2025-26 paper with explicit intraday long/short
  times on an IC symbol (ICE Brent); SSRN access for Valenti's exact formula and Tolusic's venue.

## Process and disclosures
The old scratchpad was gone; the minute panel was rebuilt from research/data/m1 with HOLD cut at load
(`r23/shared/build_panel.py`), and a NYSE-closure / festival calendar for 2004-24 was built (`r23/shared/cal/`).
N searched Crossref by ISSN for 30 journals (15,786 records), NBER and Fed Board DOI prefixes, 7 arXiv q-fin categories
and 36 SSRN-via-Crossref queries; 462 of 23,880 records were read by hand, 40 mapped. Scripts and outputs in the
scratchpad (`r23/N`, `r23/P`). Nothing in `research/` code was edited.
