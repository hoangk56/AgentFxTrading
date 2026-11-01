# Round 44 stream I: aggregate corporate insider trading (SEC Form 4) -> US500, USTEC, US30, US2000

Written 2026-10-30 06:16 UTC. Hypotheses declared in [HYPOTHESES_I.md](HYPOTHESES_I.md) at 06:10 UTC, after the pull,
parse and signal-day counts and before any return. Bars: LIVE / DEMO from research/PROMPT.md. HOLD (2025-01..2026-09)
stayed closed: only data sets for quarters <= 2024 Q4 were requested (the fetcher refuses later ones), filings dated
after 2024-12-31 are dropped at parse with an assert (0 found), IC prices cut at ts < 1735689600000, US2000 files
< 20250101. Nothing from 2025-26 was printed. The index page lists 2025-26 zip links; the probe filtered them out
before printing.

## Answer
No LIVE candidate. One DEMO-number cell, drafted and **not recommended for registration**:
[PREREG_DRAFT_I_large_insider_value_us500.md](PREREG_DRAFT_I_large_insider_value_us500.md) (F3 LARGE_val_W k 1.5 h 1
US500: net IS +25.3 bp, t 2.23 / VAL +2.5, t 0.13). It sits below the best-of-104 null median (2.57). It needs
2020-03/04 to reach t 2 (ex 1.88). It does not beat calendar-matched entries in VAL (0.48), and it measures missing
large-cap selling, not buying. The literature's aggregate insider signal (Seyhun; Lakonishok & Lee; Jiang & Zaman)
works at months. At <= 5 days it is 1-3 bp a day per sd at mid, with t < 1.2 in both eras. Its 20-60 day slope is
positive in IS and negative in VAL. LIVE was ruled out by the count before any return was computed.

## Sources
- SEC DERA Insider Transactions Data Sets, `https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/<YYYY>q<Q>_form345.zip`,
  2014 Q1..2024 Q4. 44 zips plus robots.txt, the index page, the readme PDF and a first 2016 Q1 probe: **47 requests,
  all HTTP 200, 2026-10-30 06:06:42-06:08:19 UTC**, ~450 MB on disk. The full pull took ~1 min at 1-3 s per zip.
  User-Agent "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate insider filing statistics)", no name or
  e-mail, one process, >= 0.3 s spacing. robots.txt has only `User-agent: *` (no ClaudeBot entry) and allows
  `/files/`. Log: `web/requests.log`.
- 2006-13 was not pulled: research/data has no US index prices before 2016, so it could not be graded (no PRE era). 2014-15
  is warm-up for the trailing z only.
- Size ranks come from Vanguard Group 13F-HR info tables, year-ends 2015-2023, already downloaded by round 42 E. Common
  stock value is summed by normalised issuer name and ranked per year. 64 % of officer / director filings matched a
  ranked name. LARGE = rank 1-500 (78k filings), SMALL = rank 1001-3000 (168k).
- Parse: Form 4 only. Codes P + A and S + D. Officers / directors only (pure 10 % owners dropped). One unit per filing.
  Dollar value capped at $10 M per filing. Totals: 606,271 P / S filings, of which 538,873 are by officers / directors.
  Daily means IS: ~52 buyer and ~143 seller filings; $19 M of capped buys and $177 M of capped sales.
- WebSearch: 0. Literature sizes quoted from memory of the papers and marked as order-of-size.

## Power arithmetic (before returns; details in HYPOTHESES_I.md)
Trigger days (z >= 1.0 / 1.5) number 120-240 in IS, 45-150 in VAL and ~26-85 in HOLD. LIVE needs a per-trade Sharpe of
0.36-0.52, i.e. 40-57 bp on a one-day US500 trade. The literature gives ~3-5 bp a day per sd, so a 1-day Sharpe of
~0.05-0.07: LIVE is impossible, and DEMO needed 2-3x the literature's share at short horizons.

## Results (bp per trade, long, entry 09:31 ET the trading day after the filing day; h5 non-overlapping)
| hypothesis | cell (best of family by IS net t) | IS mid (t) | cost | net IS (t) | net VAL (t) | VAL / IS | Sharpe IS, power IS / VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| F1 aggregate net purchases (64 cells) | ALL_val_W k1.5 h5 USTEC | +94.3 (1.69) | 17.6 | +76.7 (1.37) | -29.8 (-0.37) | <0 | 0.22, 0.82 / -0.28 | 0.87 / 0.33 | none: 0 / 64 cells IS t >= 2 |
| F1 primary (count, weekly, k1, h1) | ALL_cnt_W k1 h1 US500 | +3.1 (0.30) | 4.4 | -1.2 (-0.11) | +13.5 (1.13) | flips | -0.01, -0.06 / 0.86 | 0.16 / 0.91 | none: IS ~0, VAL positive (era-dependent) |
| F2 insider surge after a >= 2 % 10-day fall (16 cells) | ALL_cnt_W k1 h5 USTEC | +43.2 (0.44) | 18.1 | +25.1 (0.26) | +43.1 (0.41) | 1.7 | 0.05, 0.16 / 0.31 | 0.24 / 0.69 | none: IS ~0 in every cell. VAL h1 cells +7 to +16 bp but at t < 0.9, and they do not beat fall-day random entries in IS |
| F3 size split (24 cells) | LARGE_val_W k1.5 h1 US500 | +29.8 (2.62) | 4.5 | +25.3 (2.23) | +2.5 (0.13) | 0.10 | 0.195, 1.06 / 0.10 | 1.00 / 0.61 | DEMO numbers, at chance: draft, not recommended |
| F3 small caps -> US2000 | SMALL_cnt_W k1.5 h5 US2000 | +2.6 | 15.6 | -13.0 (-0.14) | +125.3 (2.02) | flips | - | 0.27 / - | none (IS < 0) |
| B1 CEO / CFO only (4) | US500 h5 | +20.9 | 14.8 | +6.1 (0.12) | +30.1 (0.59) | - | - | - | none |
| B2 cluster buying (>= 2 buyers per issuer in 5 days) (4) | US500 h1 | -1.3 | 4.2 | -5.5 (-0.58) | +13.7 (1.29) | flips | - | - | none |

- Spread x1.5 and +1 minute move each best cell by < 1.5 bp. Cost is ~4.5 bp at h1 (half spreads + ~2 bp swap a night,
  so 6 bp over a weekend) and ~15-18 bp at h5 (7 nights of swap).
- Ex 2020-03/04, the draft cell's IS falls from +25.3 to +13.0 (t 1.88). By year (net): 2016 +40, 2017 +12, 2018 +4,
  2019 +10, 2020 +114 (15 of 16 trades in March / April), 2021 +7, 2022 -3, 2023 +33, 2024 +6. Without its top 3
  trades VAL is -10.3.
- Calendar check (post hoc). Triggers over-sample quarter weeks 5-8 and 12, the insider blackout weeks, because the
  large-cap dollar series is ~$0.1 M of buys against ~$50 M of sales a day. Against random entries with the same
  week-of-quarter and weekday mix, the cell beats 1.00 of draws in IS and 0.48 in VAL.
- Correlation with C3, daily (IS + VAL), draft cell: -0.008.

### Slope diagnostic: what is left at <= 5 days
US500 forward mid return in bp per 1 sd of z, entry 09:31 ET the next day, Newey-West t (lag h):
| signal | h1 IS / VAL | h5 IS / VAL | h20 IS / VAL | h60 IS / VAL |
|---|---|---|---|---|
| ALL_cnt_W | +1.1 (0.33) / +3.4 (0.78) | +7.1 (0.50) / +9.6 (0.66) | +45.0 (1.24) / -16.6 (-0.40) | +69.4 (0.72) / -38.3 (-0.53) |
| ALL_val_W | +2.2 (0.60) / +0.4 (0.10) | +14.8 (1.13) / -11.7 (-0.86) | +60.8 (1.62) / -17.1 (-0.48) | +115.9 (1.41) / -84.0 (-1.06) |
| LARGE_cnt_W | +2.2 (0.55) / +5.2 (1.15) | +4.9 (0.32) / +4.0 (0.26) | +57.9 (1.73) / +17.7 (0.56) | +84.1 (1.01) / -60.5 (-1.12) |
| SMALL_cnt_W (US2000) | -1.5 / +5.0 | +0.6 / +17.6 | +29.9 / +8.6 | +125.8 (1.20) / +114.2 (1.21) |
- The IS months-horizon effect is roughly the literature's size: ~2-3 bp a day per sd, or +45 to +60 bp a month. It is
  never significant over 6 years, and it turns negative in VAL for the all-firm and large-cap series. At 1-5 days it is
  1-3 bp a day per sd, against a ~4.5 bp round-trip cost and a 110 bp daily sd. The insider signal is slow and
  information-poor at the horizons the user's constraints allow (<= 5 days).

## Cells and chance
- 104 counted cells (F1 64, F2 16, F3 24) plus 8 declared by-products. In the counted cells, 2 have IS net t >= 2, both
  F3 LARGE_val_W US500 h1 (k 1.5: t 2.23; k 1.0: t 2.09). None has IS t <= -2. Mean IS t: F1 -0.11, F2 -0.14, F3 +0.42.
- Best-of-104 null: 200 circular shifts of all insider z series inside IS, with every cell recomputed. Max IS net t:
  median 2.57, p95 4.10. P(max >= 2.23) = 0.68. The best cell is what chance gives.
- Recurring pattern: the count-based cells are ~0 or negative in IS and positive in VAL (e.g. ALL_cnt_W h5 US500 IS
  -28.8, VAL +56.4). The VAL values beat ~90 % of random longs. The sign is era-dependent, not a stable effect.

## Exhausted after this stream (add to PROMPT "Những họ đã cạn")
- Aggregate SEC Form 4 insider open-market trading (count and dollar net-purchase ratios, daily and weekly, z vs the
  trailing year), contrarian insider surges after falls, CEO / CFO purchases, cluster buying, and large / small-cap
  splits by Vanguard 13F rank -> US500 / USTEC / US30 / US2000 at 1-5 days. The effect lives at months and is not
  stable between 2016-21 and 2022-24.

## Pitfalls
- The data sets' zip path is `/files/structureddata/data/insider-transactions-data-sets/<YYYY>q<Q>_form345.zip`, not
  `form-345-data-sets`. The quarter is by filing date. FILING_DATE is `DD-MON-YYYY`. Acceptance times are not in the
  data sets: use the 22:00 ET Section 16 dating rule and enter the next morning.
- The index page lists 2025-26 zips: filter its links before printing anything.
- Large-cap insider buying is tiny (median ~$0.1 M a day against ~$50 M of sales), so large-cap "net purchase" series
  are sale-volume series. They follow the blackout calendar, so compare against calendar-matched random entries.
- Matching Form 4 issuer names to 13F names catches ~64 % of filings. A CUSIP or CIK map would need per-filing
  documents.
- The whole 2014-24 pull is ~1 minute. SEC served all 47 requests with a generic research UA.

## Directions that need the user
| direction | value |
|---|---|
| IC single-stock CFDs (MT5): trade the firm after its own insider purchase (firm-level drift after insider buys is the robust literature result, Cohen-Malloy-Pomorski 2012 "opportunistic" buys) | LIVE ~2-3 %, DEMO ~10 % (the only part of the insider literature that works at days; index aggregation kills it) |
| Holds > 5 days (the insider signal lives at 1-12 months) | outside the user's constraints; IS slope not significant and VAL negative anyway: < 1 % |
| Paid point-in-time float / index membership (S&P, Russell) for exact size splits | < 1 % |

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r44/I/scripts/`
  - fetch.py: the SEC fetcher, run under python -I; it refuses quarters after 2024.
  - parse345.py: run under python -I, with the HOLD cut.
  - vg13f.py: the 13F size ranks.
  - lib.py, counts.py: series and counts.
  - grade.py: 104 cells, slope diagnostic and null.
  - diag.py: draft-cell checks, C3 correlation, B1 / B2.
- Outputs: `.../scratchpad/r44/I/out/` holds filings.csv, vg_ranks.csv, series.npz, cells.csv, null_maxt_IS.npy,
  counts.log, grade.log and diag.log. Downloads are in `.../scratchpad/r44/I/web/` (requests.log).
