# Round 55: insider-purchase day-1 drift with an intraday entry after the opening auction (single-stock CFDs), 2026-10-30

Brief: [round55_insider_intraday/BRIEF.md](round55_insider_intraday/BRIEF.md). Continues the user-approved single-stock
CFD direction (2026-10-30). Research only (no MT5 account, bot or deploy). Same LIVE / DEMO bars as rounds 25-54. HOLD
(2025-01..2026-09) stayed closed: no 2025 / 2026 Dukascopy file was requested (latest 2024-12-30, asserted), every series
cut at ts < 2025 at parse.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. None of 48 cells reaches net IS t >= 2 (best +0.36, CEO / CFO 09:35 entry,
D+2 exit, hedged; p 0.34 against the best-of-48 random-pool null). The primary cell (all buys, 09:45 entry, 15:55 exit,
US500-hedged) is -14.0 bp IS (t -1.97) / -21.4 VAL (t -2.54), negative in 8 of 8 years. Two reasons:
- In VAL only +6.4 bp of round 54's day-1 drift is left after 09:45 (39 % of the day's move); the round trip costs
  ~24 bp (Dukascopy spread ~12 bp at 09:45 plus IC's $0.02 / share commission ~12 bp).
- Round 54's CEO / CFO IS figure (+46.5 bp) rests mostly on one penny-price trade (RRC at $1.6 on 2020-03-12, +2,853 bp).
  Without it CEO / CFO IS day-1 is +15 bp, all of it before 09:35.

HYPOTHESES_M.md (honesty note on the round 54 VAL look, the 1/4 HOLD rule) was written before any M1 request. HOLD power
at zero cost was 0.2-0.35 under the 1/4 rule, so LIVE was out of reach on the event count alone.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| M | Round 54 I's insider buys (ALL / OPP / CEOCFO / CLUSTER, routine placebo), long from the first M1 bar at or after 09:35 / 09:45 / 10:00 ET of D+1 at the ask, exit 15:55 at the bid (D+2 15:55 variant), US500-hedged and unhedged; Dukascopy M1 bid / ask for 7,686 firm-days (event firms D+1 / D+2 plus 3 random firms per date), 15,372 files in ~57 min; 48 cells + 12 placebo | **none**: best net IS t +0.36 (null p95 1.07); primary -14.0 (t -1.97) / -21.4 (t -2.54); spread x1.5, +1 min, ex-2020-03/04 all worse; no cell's HOLD power > 0.38 even at zero cost | [STREAM_M.md](round55_insider_intraday/STREAM_M.md), [HYPOTHESES_M.md](round55_insider_intraday/HYPOTHESES_M.md) |

Spread profile (median bp, event and random firms alike after 09:31): 09:30 ~57-70, 09:31 ~21, 09:35 ~15, 09:45 ~11,
10:00 ~10, 10:30 ~8, 15:55 ~5. 2017 is tight (~5 bp at 09:45); 2018-24 sit at 9-15 bp, widest in 2022.

Correlation with C3: nothing survived; for information -0.050 (primary) / -0.028 (best cell).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Insider purchases on the firm (Cohen-Malloy-Pomorski families) as a long at any entry time on D+1 (open, 09:35-10:00,
  close) with holds of 0-5 days: closed together with round 54.

## Pitfalls
- Check a cell's top trades before quoting a family mean: one sub-$5 trade made round 54's CEO / CFO IS figure. At IC,
  sub-$5 names also pay 40+ bp commission a side.
- March 2020 circuit-breaker halts leave 15-30 minute gaps; a "first bar within 5 minutes" rule drops 26-35 events per
  offset.
- Dukascopy stock M1: scale 1e3, bar time = start of minute, 390 bars from 09:30 ET, raw prices matching D's daily
  candles; a 503 on stock M1 meant "retry", not "missing" (17 files failed 12 tries, all came back on one retry).
- 3 random firms per date make the random-firm share coarse; a few crash days pulled the pool's IS intraday mean to
  -15.8 bp, so "beats random 1.00" in IS is inflated.

## Directions that need the user
| direction | value |
|---|---|
| IC MT5 demo login to log real 09:31-10:00 spreads on US share CFDs | low now: the ~12 bp commission alone exceeds the +6 bp VAL drift left after 09:45; DEMO < 2 % |
| A spread-only venue (no per-share commission) | ALL 09:45 unhedged ~+8 IS / ~-6 VAL bp; DEMO ~2 %, LIVE < 1 % |
| Holds > 5 days (CMP's horizon) | outside the fixed constraints |

## State after round 55
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. IC's ~12 bp round-trip
commission is now the binding cost on single-stock CFDs: a stock rule needs > ~20 bp per trade at a close or
mid-session fill. Round 56 tests the cross-section of the daily panel already on disk (no new pull).
