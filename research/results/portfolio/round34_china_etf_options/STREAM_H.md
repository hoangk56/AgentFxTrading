# Round 34, stream H: Chinese futures exchanges' position and stock tables (SHFE / INE) -> XAU, XAG, XTI / XBR, AUD

Written 2026-10-28 from 01:25 UTC. Hypotheses: [HYPOTHESES_H.md](HYPOTHESES_H.md). The main file was written at
20:36 UTC on 10-27. Amendments 1-3 came later (20:39, 23:14 and 01:21 UTC), each before the returns of the cells it
covers. Bars: research/PROMPT.md, LIVE / DEMO only (no RELAXED).

HOLD (2025-01..2026-09-24) stayed closed. No file dated after 2024-12-31 was requested, and IC prices were loaded at
ts < 2025-01-01. One disclosure: a WebSearch summary quoted 2026 descriptive correlations between position and price
(details in HYPOTHESES_H.md). They were not used.

## Answer
**No LIVE or DEMO candidate, and no PREREG_DRAFT.**

- 38 declared cells were tested in six families.
- On the declared side, the best IS net t is +1.46 (C, Yongan seat on gold, h1). Its VAL is -47 bp (t -2.28).
- The largest |IS t| anywhere is -2.97, on the **wrong** side. This is B on gold at h3: "follow the commercials" lost
  -13.2 bp per trade in IS. It then turned positive in VAL (+7.7, t 1.29), and PRE is -3.2.
- No cell keeps one sign across PRE, IS and VAL with t > 1.

**The new source is real but carries no direction.** SHFE publishes a complete daily split of each metal's open
interest between brokers' clients (期货公司) and non-futures-company members (非期货公司: banks, miners, refiners). It
runs from 2012-03 for gold and silver and from 2013-06 for copper. In effect it is a daily, same-day Chinese "COT"
that no round had loaded.

Within the SHFE trading day, the commercials trade against the move: the same-window correlation of their net change
with gold's return is -0.32 in PRE, -0.25 in IS and -0.14 in VAL. Clients chase it. This is Kang, Rouwenhorst & Tang's
liquidity-provision picture, but the expected premium does not follow over the next 1-3 days at IC.

## Sources and spans
| source | fetched | span used | notes |
|---|---|---|---|
| SHFE member rankings `…/data/tradedata/future/dailydata/pm{date}.dat` (JSON; ranks 1-20 for volume, long OI and short OI per contract) | 4,435 weekdays, 2008-01-02..2024-12-31; 161 x 404 (holidays from 2016) | gold 2008-01-10..2024-12-31 (4,127 days); silver 2012-05-15.. (3,073); copper 2008-01.. (4,133) | client / commercial split: per contract 2012-03..2015, product rows `<p>all` from 2016 |
| SHFE daily warrant report `{date}dailystock.dat` | 2012-05..2024-03-27. The pull was stopped at the lead's request, about 190 files short of 2024-12-31 | 2014-05-19..2024-03-27 (2,401 days; 404 before 2014-05-19) | gold, silver, copper totals |
| INE daily warrant report (crude, `www.ine.cn/…/{date}dailystock.dat`) | 2018-03-26..2024-12-31 | 2018-03-30..2024-12-31 (1,637 days) | |
| Unusable: INE crude member rankings | probed | | INE never publishes sc (crude) in its ranking file: 2018 is empty, later files list only nr / lu / ec. No oil positioning family is possible |
| Unusable: SHFE weekly stock report | 889 requests | | My bug: weekly files live under `/weeklydata/`, the pull used `/dailydata/` (all 404). The declared W4 (weekly copper) was replaced before its returns by W4' (daily copper warrants), Amendment 3 |
| Unusable: CFFEX index-futures rankings (the spider-web rule's own market, proxy for HK50) | 3 requests | | About 60 s per request over http, and https hangs: a full pull would take about 2.5 days |

**Publication time.**
- The `update_date` fields of 2,340 SHFE files fall between 15:xx and 20:59 Beijing on the same day.
- 59 files are later or re-generated on another day. Their signals were dropped: entry is 13:00 UTC = 21:00 Beijing.
- On INE, 21 files were re-generated later and were dropped the same way.
- Files before 2015 carry no time, so the same clock is assumed for them.
- The day's table includes the preceding night session. OI is at the 15:00 Beijing close.

## Power before the numbers (from HYPOTHESES_H.md)
- Rule sizes LIVE needs: XAU about 12 bp per trade at k 0 h1 and about 22 bp at k 1. XAG 22 / 39 bp. XTI / XBR
  35-89 bp.
- Literature-sized positioning effects (|rho| about 0.03-0.05) give a LIVE power of only about 1.0.
- So LIVE needed about 3x the literature's size. The data show no effect at all.

## Results
Net and mid are in bp per trade. t is per trade for h1 and Newey-West (lag 3) for the overlapping h3 trades.

Cost per trade, approximate, including swap: XAU 1.1-2.0 bp; XAG about 5; AUD about 3; XTI / XBR 14-20 at h3.

"pow" is per-trade Sharpe x sqrt(1.73 x trades per year / h). "rand" is the share of 200 random-entry seeds that the
cell beats, IS / VAL. The full lines (with spread x1.5, +1 min and the circular-shift control) are in `out/cells_*.txt`.

| hypothesis (side) | cell | eras | mid IS (t) / VAL (t) | net PRE (t) | net IS (t) | net VAL (t) | VAL / IS | pow IS / VAL | rand IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| A top-20 net change, follow (spider-web lore) | au k1 h1 (IS-best) | PRE 2008-15, IS, VAL | +4.81 (1.15) / -6.07 (-0.99) | -6.80 (-1.15) | +2.92 (0.70) | -7.40 (-1.21) | < 0 | 0.37 / -0.92 | 0.89 / 0.25 | none |
| A, silver | ag k1 h3 (IS-best) | PRE 2012-15 | +11.26 (0.79) / +9.74 (0.39) | +13.79 (0.68) | +6.41 (0.45) | +4.31 (0.17) | 0.67 | 0.13 / 0.08 | 0.78 / 0.63 | none |
| B commercials' (non-FCM) net change, follow (KRT 2020 liquidity premium) | au k1 h1 (IS-best of a negative family) | PRE 2012-15 | -1.94 (-0.44) / +1.65 (0.26) | +2.95 (0.48) | -3.75 (-0.85) | +0.68 (0.11) | < 0 | -0.45 / 0.08 | 0.32 / 0.62 | none |
| B, gold, h3 | au k0 h3 | | -10.86 (-2.44) / +9.26 (1.55) | -3.21 (-0.50) | **-13.19 (-2.97)** | +7.66 (1.29) | sign flip | -1.01 / 0.60 | 0.01 / 0.95 | none (wrong side in IS, flips in VAL) |
| B, silver | ag k1 h3 | | -13.47 (-0.79) / +44.19 (1.61) | -9.65 (-0.46) | -18.28 (-1.07) | +38.62 (1.41) | sign flip | -0.34 / 0.72 | 0.18 / 0.96 | none |
| C named seats, follow (Yongan, CITIC), k1 h1 fixed | Yongan au | PRE / IS / VAL n 238 / 155 / 17 | +15.12 (1.64) / -46.2 (-2.24) | -6.87 (-0.80) | +13.39 (1.46) | -47.38 (-2.28) | < 0 | 0.78 / -1.73 | 0.995 / 0.005 | none |
| C | Yongan ag | | +16.52 (1.64) / -13.55 (-0.77) | -1.66 | +12.22 (1.21) | -18.21 (-1.03) | < 0 | 0.65 / -0.78 | 0.955 / 0.24 | none |
| C | CITIC au / ag | | | | +0.08 / -0.72 | -8.83 / -14.50 | | | | none |
| A-cu -> AUDUSD (Amendment 2) | k0 h3 (IS-best) | PRE 2008-15 | +3.65 (1.27) / -4.75 (-1.07) | -6.57 (-2.03) | +0.81 (0.28) | -7.36 (-1.67) | < 0 | 0.09 / -0.74 | 0.93 / 0.15 | none |
| B-cu -> AUDUSD | all 4 cells | PRE 2013-15 | | | -1.02 .. -2.67 | -0.78 .. -7.32 | | | | none |
| W1 silver warrant draw -> long XAG (k1) | h3 (IS-best) | PRE 2014-15, IS, VAL to 2024-03 | +23.65 (1.22) / +12.75 (0.42) | +6.22 (0.13) | +18.95 (0.98) | +6.76 (0.22) | 0.36 | 0.43 / 0.14 | 0.975 / 0.72 | none |
| W2 gold warrant draw -> long XAU | h3 | | +11.50 (0.80) / -22.19 (-0.98) | +1.10 | +9.42 (0.66) | -23.93 (-1.08) | < 0 | 0.27 / -0.65 | 0.87 / 0.12 | none |
| W3 INE crude warrant draw -> long XBR / XTI | all 4 | IS 2018-04..21 | XBR h1 -9.6 / -13.8; XTI h3 -243 / -87 | n/a | -19.5 .. -263 (t -0.77 .. -1.31) | -19.7 .. -100.6 (t -1.32 .. -2.66) | | < 0 | <= 0.29 / <= 0.16 | none (wrong side in both eras; XTI IS carries the April 2020 IC artefacts) |
| W4' copper warrant draw -> long AUD (Amendment 3) | h3 | PRE 2014-15 | +9.55 (0.92) / -6.68 (-0.67) | -13.68 (-0.69) | +6.75 (0.65) | -9.34 (-0.94) | < 0 | 0.32 / -0.51 | 0.95 / 0.23 | none |

### Remaining cells (IS net t)
- **A gold:** k0 h1 -0.11, k0 h3 +0.15, k1 h3 +0.13.
  - PRE is negative in all four A-gold cells (t -1.15 to -2.34).
  - VAL is negative in all four (h3 k1 -26.9 bp, t -2.12).
- **A silver:** k0 h1 -0.81, k0 h3 -1.07, k1 h1 -0.32.
- **B gold:** k0 h1 -1.80, k1 h3 -1.01.
- **B silver:** k0 h1 -0.99, k0 h3 -2.28, k1 h1 -1.65. Every B cell in metals is <= 0 in IS and > 0 in VAL.
- **W1 h1:** -0.32. **W2 h1:** +0.30. **W4' h1:** +0.49.
- **Spread x1.5 and +1 minute** change no verdict. XAU and AUD costs are small at 13:00 UTC.

## Multiple testing
- 38 cells. The median of the max |Z| over 38 independent cells is about 2.38, and the 95th percentile about 3.0.
- The best declared-side IS t (+1.46) is below the median.
- The largest |t| (2.97, wrong side) sits at the null's 95th percentile. Its sign reverses in VAL.
- No cell beats 95 % of its random-entry or circular-shift control in both IS and VAL.

## Information worth keeping
1. **Same-day correlation of the SHFE trading day's return** (previous weekday 13:00 UTC -> 07:00 UTC) with the
   position changes:

   | position change | metal | PRE | IS | VAL |
   |---|---|---|---|---|
   | non-FCM (commercials) net | gold | -0.32 | -0.25 | -0.14 |
   | non-FCM (commercials) net | silver | -0.12 | -0.17 | -0.01 |
   | top-20 net | gold | -0.08 | +0.13 | +0.08 |
   | top-20 net | silver | +0.13 | +0.11 | +0.30 |

   Chinese commercials absorb the clients' trend-chasing within the day. The table is a clean daily
   speculator / hedger split for SHFE gold, silver and copper from 2012-13.
2. **Gold structure.** The commercials (banks, miners) are structurally net short gold: on 2020-01-02 they held 75k
   long against 140k short. Brokers' clients are the mirror image.
3. **None of the position or warrant series predicts London gold, silver, oil or AUD over 1-3 days after
   publication.** This is the same pattern as round 33 S's SGE premium: the arbitrage-linked Chinese venue carries no
   next-day information for London / COMEX at IC.

## Directions that need the user
- **CFFEX index-futures rankings for HK50.** This is the rule the spider-web lore was built on. It needs no account,
  but the server throttles requests to about 60 s each. That means a 2.5-day crawl, or a vendor copy (Wind / JoinQuant
  / Tushare need accounts or tokens). Value: low. The same rule failed on SHFE metals here, and HK50 costs about
  3.5 bp. LIVE chance about 1 %.
- **INE crude member positions.** Not published, so no route.
- **Weekly stock files.** Re-pulling them from `/weeklydata/` (about 890 requests, 30 min) needs no decision. Value:
  about 0, because the daily warrants of the same metals show nothing. Not done, at the lead's stop.
- **The last daily warrant files (2024-03-28..2024-12-31).** About 190 requests, no decision needed. W1 / W2 / W4' VAL
  would gain 9 months; it would not change a verdict whose IS t <= 0.98.

## Files
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r34/H/`:
- **Fetch:** `scripts/fetch.py` (single logged fetch), `scripts/dl.py` (sequential gzip downloader, 1.2 s spacing,
  one job per host, stops at 2024-12-31). Log: `web/requests.log`.
- **Parse** (with `python -I`): `scripts/parse_pm.py` writes `clean/rank_{au,ag,cu}.npz` and
  `clean/pm_update_dates.json`; `scripts/parse_stock.py` writes `clean/stocks.npz` and
  `clean/stock_update_dates.json`.
- **Engine:** `scripts/px.py` (from round 31 G; spread profile = first 2 years, so energies use 2018-19) and
  `scripts/lib.py` (13:00 UTC fills, costs, swaps, random control).
- **Cells:** `scripts/cells.py {A,B,C,Acu,Bcu,W}` writes `out/cells_*.txt` and `out/cells_*.json`.
- **Information:** `scripts/contemp.py` (same-window correlations).

Correlation with C3 was not computed, because no rule survived.
