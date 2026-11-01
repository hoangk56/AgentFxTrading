# Round 44 stream I: hypotheses (aggregate corporate insider trading -> US500, USTEC, US30, US2000)

Declared 2026-10-30 06:10 UTC (`date -u`: Fri Oct 30 06:10:29 UTC 2026), after the data pull and parse and the signal
day counts, **before any return was computed or any insider series was joined to prices**. Bars: LIVE / DEMO from
research/PROMPT.md (no RELAXED tier). HOLD 2025-01-01..2026-09-24 closed.

## Source (pulled 2026-10-30 06:06-06:08 UTC, 47 requests, all HTTP 200, ~1 min, ~570 MB)
- SEC DERA "Insider Transactions Data Sets" (structured Forms 3 / 4 / 5):
  `https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/<YYYY>q<Q>_form345.zip`, 2014 Q1 ..
  2024 Q4 (44 quarters; 2014-15 is warm-up for trailing z-scores only, no US index prices exist in research/data before
  2016, so there is no PRE era). Index page `https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets`,
  readme `https://www.sec.gov/files/insider_transactions_readme.pdf`. robots.txt (`User-agent: *` only, no ClaudeBot
  entry) allows `/files/`. User-Agent "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate insider filing
  statistics)", no name or e-mail, one process, >= 0.3 s spacing.
- Size ranks: Vanguard Group 13F-HR year-end info tables 2015-2023 (CIK 102909), downloaded by round 42 E; common-stock
  value summed by normalised issuer name and ranked per list year (year-end Y -> filings in Y+1). Vanguard's total-
  market funds hold almost every US stock in proportion to float, so its value rank is a market-cap rank proxy.
- Prices: IC M1 US500 / USTEC / US30 (bid c, ask ca), US2000 bid zbars with the fixed 0.34 pt spread (round 7); cut
  ts < 1735689600000 at load.

## Parse (fixed before returns; parse345.py under python -I)
- HOLD cut at parse: submissions with FILING_DATE > 2024-12-31 dropped first (0 found; asserted).
- Form type "4" only (no 4/A, no Form 5). Transactions: non-derivative table, code P with A (open-market purchase) and
  code S with D (open-market sale), shares > 0, 0 < price < 1e6. One unit = one filing (accession).
- Insiders = filings where any reporting owner is a Director or an Officer (pure 10 % owners / other dropped), as in
  Lakonishok & Lee 2001. 606,271 P/S filings, 538,873 by officers / directors.
- A filing is a buyer if its purchase value > its sale value, else a seller. Value per filing capped at $10 M (keeps
  single mega-sales from dominating).
- Timing: the data sets give FILING_DATE only. A Form 4 accepted by 22:00 ET is dated that day (Reg S-T 232.13), so a
  filing dated D is public by 22:00 ET on D. Entry = 09:31 ET on the first NYSE trading day after D.
- Universes: ALL; LARGE = issuer name matched to Vanguard rank 1-500 (US500 proxy); SMALL = rank 1001-3000 (Russell 2000
  proxy). Match rate 64 % of officer / director filings (347k); LARGE 78k filings, SMALL 168k.

## Series (trailing only)
- Daily (D): NPR_cnt = (B - S) / (B + S) over that day's filings (B, S = buyer / seller filing counts); NPR_val =
  (VB - VS) / (VB + VS) with capped dollar values. Weekly (W): the same over the trailing 5 trading days.
- z = (x - mean) / sd over the previous 250 trading days (>= 200 obs), today excluded.

## Signal-day counts (z >= k, trading days; HOLD = VAL rate x 435 / 753)
| signal | k 1.0 IS / VAL / HOLD | k 1.5 IS / VAL / HOLD |
|---|---|---|
| ALL cnt D | 223 / 117 / ~68 | 143 / 57 / ~33 |
| ALL cnt W | 225 / 114 / ~66 | 153 / 57 / ~33 |
| ALL val D | 203 / 109 / ~63 | 128 / 71 / ~41 |
| ALL val W | 189 / 127 / ~73 | 128 / 82 / ~47 |
| LARGE cnt W | 237 / 116 / ~67 | 147 / 72 / ~42 |
| LARGE val W | 214 / 72 / ~42 | 134 / 51 / ~29 |
| SMALL cnt W | 237 / 114 / ~66 | 160 / 70 / ~40 |
| SMALL val W | 208 / 148 / ~85 | 124 / 82 / ~47 |
Per year 13-90 trigger days (2018 and 2022 highest: the falls). Weekly triggers cluster in runs, so h5 trades
(non-overlapping) are fewer: roughly 1/2 to 1/3 of the trigger days.

## Power arithmetic (before returns)
- LIVE needs per-trade net Sharpe >= 3 / sqrt(HOLD n): n ~68 -> 0.36, n ~33 -> 0.52. US500 1-day sd ~110 bp, so h1
  needs ~40-57 bp per trade; h5 (sd ~230 bp, ~25 non-overlapping HOLD trades) needs Sharpe 0.6 = ~140 bp.
- Literature size: Seyhun 1988 / 1992 and Lakonishok & Lee 2001 find aggregate insider net purchases predict the market
  over the next 1-12 months (Seyhun: ~1-2 months; L&L: 6-12 months); Jiang & Zaman 2010 find the 1-12 month predictive
  power comes from cash-flow news. Order of size: ~0.5-1 % more next-month market return per sd of aggregate net
  purchases, i.e. ~3-5 bp a day per sd. On trigger days (mean z ~1.5): h1 ~5-8 bp vs sd 110 -> Sharpe ~0.05-0.07;
  h5 ~25-40 bp vs sd 230 -> Sharpe ~0.1-0.17 at mid, minus ~1-3 bp spread and ~2 bp swap per night long (h5 ~ -12 to -14 bp
  incl. the weekend).
- So **LIVE is out of reach** for every cell (needs 5-10x the literature effect at 1 day). DEMO (IS t >= 2) needs
  per-trade Sharpe ~0.13-0.17 at h1 (n 143-223) or ~0.2-0.3 at h5 (n ~60-100 non-overlapping): only possible if the
  short-horizon slice is 2-3x the monthly-rate share. Expected: no candidate; the slope diagnostic below says what is
  left at <= 5 days versus 20 / 60 days.

## Families, sides and cells (sides from the literature, long only; fixed now)
All trades: long at 09:31 ET on the trading day after the trigger filing day, exit 09:31 ET h trading days later.
h in {1, 5}; for h 5 one position per symbol (triggers during an open trade are skipped; trades do not overlap).
- **F1 aggregate net purchases** (Seyhun; L&L; Jiang & Zaman): signals ALL_cnt_D, ALL_cnt_W, ALL_val_D, ALL_val_W;
  z >= k, k in {1.0, 1.5}; symbols US500, USTEC, US30, US2000. 4 x 2 x 2 x 4 = 64 cells. Side long.
- **F2 contrarian insider surge after a fall** (insiders buy dips; Seyhun 1988, L&L "contrarian beliefs"): ALL_cnt_W
  or ALL_val_W z >= 1.0 AND US500 mid return over the prior 10 trading days (09:31 -> 09:31, ending at the entry clock)
  <= -2.0 %; h {1, 5}; 4 symbols. 2 x 2 x 4 = 16 cells. Side long. Random control drawn **only from days with the same
  fall condition**, so the cell tests insider buying on top of the short-term reversal after falls.
- **F3 size / membership splits**: LARGE_cnt_W, LARGE_val_W -> US500, USTEC; SMALL_cnt_W, SMALL_val_W -> US2000;
  k {1.0, 1.5}; h {1, 5}. 6 x 2 x 2 = 24 cells. Side long.
- Total 104 counted cells.
- Diagnostic (not graded, no side choice): OLS slope of the US500 forward mid return at h 1, 5, 20, 60 trading days on
  ALL_cnt_W z and ALL_val_W z, IS and VAL, Newey-West t (lag h), to state what share of the literature's monthly
  effect lives at <= 5 days.

## Grading (round 13 / 37 rules)
- Costs: half spread at entry and exit minute (actual IC quotes; US2000 0.34 pt fixed), swap per calendar night via
  research/swing/rates.swap_frac_at (US2000 uses US500's rate). Variants: spread x1.5, both legs +1 minute (09:32).
- t: h1 per-trade t (non-overlapping, one per day = day-clustered); h5 non-overlapping trades, plain t and Newey-West
  lag 1, the smaller |t|.
- Random entry: 200 seeds, same count, weekday mix, era, h, long side (F2: from fall-condition days only); report the
  share of seeds the cell beats.
- Chance benchmark: 200 circular shifts of every insider z series inside IS (same offset for all), all 104 cells
  recomputed, distribution of the best IS net t.
- Report with / without 2020-03/04, by year, VAL / IS ratio, power at IS and VAL size on HOLD n.
- A cell meeting DEMO / LIVE numbers on IS + VAL -> PREREG_DRAFT_I_<name>.md; HOLD not opened.
- If F1-F3 all fail, declared by-products (written here before returns, graded only if reached): **B1** CEO / CFO-only
  purchases (officer title containing CEO / CFO / Chief Executive / Chief Financial) as a cleaner informed subset of
  ALL_cnt_W, same rule, US500 / US2000, k 1.0, h {1, 5} (4 cells); **B2** cluster buying: number of distinct issuers with
  >= 2 officer / director buyer filings in the trailing 5 days, z >= 1.0, long US2000 / US500, h {1, 5} (4 cells).
