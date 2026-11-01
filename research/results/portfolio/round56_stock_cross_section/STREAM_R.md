# Round 56 stream R: large-cap short-term reversal without news vs continuation with news (2026-10-30)

Hypotheses: [HYPOTHESES_R.md](HYPOTHESES_R.md), written 12:03 UTC before any return was computed. Results files:
[R_out/cells.csv](R_out/cells.csv) and [R_out/cells.json](R_out/cells.json) for all 48 cells (by year, legs, random
control and chance benchmark), and [R_out/diag.json](R_out/diag.json) / [R_out/diag_summary.log](R_out/diag_summary.log)
for primary-cell diagnostics. The code is in R_out/grade.py.txt and diag.py.txt. The scratchpad copy is
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r56/R/`.
HOLD stayed closed: D's panel ends on 2024-12-31, `S.dates.max() < 2025-01-01` is asserted, and 8-K rows dated on or
after 2025-01-01 are dropped at parse. Nothing was downloaded.

## Verdict
**No LIVE or DEMO cell, so no PREREG_DRAFT.** Not one of the 48 cells has positive net VAL. The best net IS t is
+0.76 (F3_L5_h5_k3, VAL -86.7 bp). Large caps do reverse a little at mid: the strongest gross figure is
F1_L1_h3_k9 at +22.0 bp IS (t 2.39) and +12.5 VAL (t 1.38). But a close-fill round trip at IC costs ~20-24 bp per
position (spread ~10 bp, commission ~9 bp, financing 1-6 bp), and the gross figure does not survive a change of
start offset (+5.0 / +4.4 bp on offsets 1 and 2). Everything gross sits inside the chance benchmark: the null's p95
max gross IS t over 48 cells is 2.97, against 2.39 for the best real cell. The news filter adds ~2 bp at h = 1 (gross
+5.3 with the filter vs +2.9 without for L1 h1 k9), which points the way Chan / DLS predict but is far below cost.
News continuation (F2) is gross ~0 for the "sign" book and +10-15 bp at best for the k3 extremes, so it is negative
net in every cell.

## Set-up (as declared)
- Universe: 207 D stocks with at least one 8-K 2.02 event (the declared 206; USO counts as a stock in D and is
  excluded by name). About 203 are eligible per day: raw price >= $10, close spread <= 50 bp, quotes on every
  window day, and a 250-day SPY beta.
- Residual: stock minus beta x SPY (primary); stock minus its SIC-mapped sector ETF (variant). Sector counts: XLY 36,
  XLK 29, XLF 27, XLV 25, XLP 24, SPY 21, XLI 18, XLE 13, XLU 9, IYR 5.
- News days: 6,260 firm-days mapped from 6,960 8-K 2.02 filings (16:00 ET rule). The no-news filter covers
  [t-L-1, t].
- Fills: Dukascopy close bid / ask of the traded day, $0.02 / share / side, financing per night. Every position
  is a full round trip. Books are non-overlapping (F1 / F3) or event-based daily (F2). The trade unit is one stock
  position, with t clustered by entry date.
- Effective IS is 2017-05..2021 (SPY starts 2017-02-16, and the beta needs 60 days). PRE (2016-17) could not be
  separated, so 2017 is reported only as one year.

## Results (net bp per position; t clustered by entry date; full table in R_out/cells.csv)
| cell | n IS / VAL | net IS (t) | net VAL (t) | gross IS (t) / VAL (t) | spread / comm / fin IS | x1.5 IS / VAL | +1 day IS / VAL | ex-2020-03/04 IS | years + | beats random IS / VAL | p (max gross null) | power (VAL) | bots |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **F1_L5_h5_k9 (primary)** | 3,810 / 2,680 | -1.3 (-0.09) | -36.9 (-2.51) | +23.8 (1.57) / -12.2 (-0.83) | 10.2 / 8.8 / 6.0 | -6.4 / -42.5 | -6.6 / -33.0 | -12.4 (-0.98) | 1/8 | 1.00 / 0.04 | 0.93 | -1.9 | 6 |
| F1_L5_h5_k3 (best F1 net IS) | 1,268 / 893 | +8.1 (0.36) | -45.6 (-2.12) | +35.4 (1.55) / -19.0 (-0.88) | 11.2 / 10.1 / 6.0 | +2.5 / -51.7 | -4.2 / -24.5 | -6.8 (-0.36) | 3/8 | 1.00 / 0.03 | 0.94 | -1.6 | 2 |
| F1_L1_h3_k9 (best gross IS t) | 6,369 / 4,497 | -0.8 (-0.08) | -9.7 (-1.08) | +22.0 (2.39) / +12.5 (1.38) | 10.3 / 8.9 / 3.6 | -5.9 / -15.3 | -16.9 / -17.5 | +0.8 (0.10) | 3/8 | 1.00 / 1.00 | 0.29 | -0.8 | 6 |
| F1_L1_h1_k9 (daily, most trades) | 19,075 / 13,531 | -14.7 (-4.99) | -16.5 (-5.38) | +5.3 (1.80) / +3.3 (1.08) | 10.0 / 8.9 / 1.2 | -19.7 / -22.1 | -18.8 / -16.8 | -13.3 (-4.89) | 0/8 | 0.72 / 0.70 | 0.77 | -4.1 | 6 |
| F3_L5_h5_k3 (best net IS t overall) | 633 / 311 | +28.9 (0.76) | -86.7 (-2.04) | +57.7 (1.51) / -59.4 (-1.40) | 12.1 / 10.7 / 6.0 | +22.8 / -93.7 | +22.0 / -52.5 | -0.5 (-0.02) | 2/7 | 1.00 / 0.00 | 0.95 | -1.6 | 2 |
| F3_L1_h3_k9 | 3,184 / 1,527 | +7.1 (0.45) | -24.2 (-1.36) | +31.3 (1.99) / -1.1 (-0.06) | 11.3 / 9.3 / 3.6 | +1.4 / -30.5 | -18.7 / -39.2 | +11.1 (0.75) | 3/7 | 1.00 / 0.27 | 0.61 | -1.0 | 6 |
| F2_L1_h3_kk3 (best F2) | 1,020 / 756 | -8.1 (-0.73) | -14.8 (-1.17) | +12.4 (1.13) / +8.5 (0.68) | 9.6 / 7.0 / 3.9 | -12.9 / -21.5 | -7.9 / -15.4 | -9.0 (-0.80) | 3/8 | 0.81 / 0.72 | 1.00 | -0.9 | 8 (p99 24 open) |
| F2_L5_h5_ksign | 2,847 / 2,144 | -16.3 (-1.93) | -14.0 (-1.64) | +4.2 (0.49) / +7.5 (0.88) | 8.1 / 6.4 / 6.0 | -20.3 / -19.0 | -15.2 / -17.4 | -17.9 (-2.26) | 2/8 | 0.97 / 0.94 | 1.00 | +0.3 | 22 (p99 64 open) |

Family ranges:
- **F1** (18 cells): net IS from -49.6 to +8.1 bp, t from -5.17 to +0.36; net VAL from -47.0 to -6.7, all negative.
- **F2** (12 cells): every IS and VAL net is negative.
- **F3** (18 cells, Nagel high-vol state, 544 IS days): net IS t at most +0.76; every VAL net is negative. Most VAL high-vol days fall in 2022,
  where the F3 L5 h5 cells lose 42-90 bp net per position.

Gross (mid) VAL is positive in most F1 L1 cells (+3 to +16 bp), so a small daily / 3-day reversal exists in large
caps. Its size is a third to two thirds of the IC round trip.

## Controls
- **Spread x1.5 / +1 day:** no cell is positive on both in both eras. The +1 day delay is negative in every
  F1 / F2 cell in VAL.
- **Random control** (same formation dates, same long / short counts, names drawn from the eligible pool, 200
  draws). The random books lose ~15-29 bp per position net. Several cells beat 95-100 % of random books in IS
  only because the null pays the same cost with zero gross. That bar is not binding here, because the t bars fail
  first.
- **Chance benchmark** (200 draws of random selection per cell, max over 48 cells): p95 of the max IS gross t is
  2.97 (median 2.15); p95 of the max IS net t is 0.91. No cell exceeds either.
- **Start offset (primary cell):** gross IS by offset 0-4 is +23.8 / +14.9 / +12.3 / +24.1 / +28.6, and VAL is
  -12.2 / -3.9 / -2.6 / +8.5 / +10.6. Net IS is between -12.9 and +3.5 at every offset, and net VAL between
  -36.9 and -14.1. For F1_L1_h3_k9, offsets 1 and 2 give gross +5.0 / +4.4 IS and net t -2.07 / -2.18: offset 0
  was lucky.
- **Sector-ETF residual (variant):** primary net IS +2.6 (t 0.19) / VAL -25.3 (t -2.13). For F1_L1_h3_k9, net IS
  -6.3 / VAL -9.1. No improvement.
- **News filter on / off:** for the primary cell the unfiltered book has gross IS +24.0 / VAL -16.1 (filtered
  +23.8 / -12.2). For L1 h1 k9, gross +2.9 / +2.9 unfiltered vs +5.3 / +3.3 filtered. A news-only reversal book
  (k3 among names with news in the window) has gross -5.6 / +4.8 (L1 h1) and +1.7 / -26.1 (L5 h5). The filter's
  effect is ~2 bp.
- **Long leg alone, SPY-beta hedged (primary):** net IS -6.3 (t -0.32) / VAL -37.4 (t -1.90).
- **By year (primary, net):** 2017 -7.8, 2018 -16.1, 2019 -11.8, 2020 +40.5, 2021 -15.8, 2022 -41.3, 2023 -23.8,
  2024 -45.7. Only the COVID year is positive. The IS sum is -4,959 bp; the top 5 trades sum to +26,317 and the
  bottom 5 to -19,419.
- **Turnover:** 4-9 % of positions repeat (same name, same side) in the next book for the L1 and L5 h5 books,
  18-24 % for L5 h3 and 45-53 % for L5 h1. Netting repeats would cut the round-trip cost by the same 4-53 %; L5 h1 VAL gross is only +0.7-3.1 bp, so no VAL cell turns positive.
- **Dividends** are not in the data. A long-loser / short-winner book pays the dividend drop on its longs and
  collects it on its shorts. The bias is a few bp per position at most, and it cannot rescue a book that is
  negative by 10-40 bp.

## Power at HOLD size
Power = VAL book-date Sharpe x sqrt(HOLD book dates), where HOLD book dates = 435 / h for F1 / F3. It is negative
for every cell except F2_L5_h5_ksign (+0.3). At zero cost, the best VAL gross cell (F1_L1_h3_k6, +16.1 bp, t 1.53,
250 book dates) would give a HOLD t of about 1.53 x sqrt(145 / 250) = 1.2. Even a cost-free venue would not reach
LIVE power 3.

## Bots needed
F1 / F3: 2k / 3 = 2, 4 or 6 bots (k = 3, 6, 9), with one book of 2k positions open at a time. F2 "sign": 11-22 bots
(p99 concurrent positions 33-64). F2 k3: 4-10 bots.

## Correlation with C3
Nothing survived. For information, book P&L by exit date against C3's daily R
(trades_C3_gotobi_jpy_basket.csv, pre-2025 rows): primary +0.046, F1_L1_h3_k9 +0.007, F1_L5_h5_k3 +0.019,
F1_L1_h1_k9 -0.002.

## Pitfalls
1. **Start offset of non-overlapping books.** A 3-day book's gross t of 2.39 at offset 0 fell to ~0.5 at offsets 1
   and 2. Report the mean over offsets, or use overlapping cohorts with HAC errors, before quoting a multi-day
   cross-section figure.
2. **Commission on extreme movers.** Even with the $10 floor, the selected extremes pay ~9-11 bp of commission a
   round trip, against ~4.4 bp at the median price. Big movers skew to cheaper names, and 1/price is averaged.
3. **Spreads of extreme movers** at the close are ~10-12 bp a round trip, not the 7 bp universe median.
4. **The random-control bar** is easy to pass for a dollar-neutral book whose null has zero gross. Use it together
   with the max-t chance benchmark on gross returns.
5. **Same close for signal and fill:** this is the brief's rule. The +1 day variant is as negative as the base, so
   no bounce artefact is hiding a positive result.
6. **Nagel's VIX state** was proxied by SPY 20-day realized volatility (VIX is not on disk). The high-vol state
   paid only in 2020-21; in 2022 F3 L5 h5 lost 42-90 bp net per position.
7. 14 D stocks file no 8-K (foreign issuers: BABA, TSM, BP...) and AAL / AEP / XOM have no 2.02 rows, so they are
   outside the universe. Survivorship (today's list of 2017-18 names) is unchanged from round 54.

## Exhausted (line for PROMPT "Những họ đã cạn")
- vòng 56 (2026-10-30, CFD cổ phiếu): cross-section ngắn hạn của ~200 mã lớn Mỹ. Đã thử đảo chiều của mã không có tin
  (Chan / DLS / Lehmann, phần dư beta SPY hoặc ETF ngành, cửa sổ 1 / 5 ngày, giữ 1-5 ngày, k 3-9, có điều kiện vol
  cao theo Nagel) và đi theo mã có tin 8-K 2.02: đảo chiều có thật ở mid (+3 đến +22 bp) nhưng nằm trong benchmark
  ngẫu nhiên và phụ thuộc ngày bắt đầu, phí khớp đóng cửa ~20-24 bp; không ô nào có net VAL > 0.

## Directions that need the user
| direction | value |
|---|---|
| A spread-only venue (no per-share commission) | Best case F1_L1_h3_k9: gross minus spread and financing ≈ +8 IS / -1.5 VAL bp, and offset-dependent. DEMO < 1 %, LIVE < 0.5 % |
| Mid / small caps, where short-term reversal is several times larger (not at IC / Dukascopy) | LIVE ~1 % (cost scales with the effect) |
| Intraday news timestamps (headline feeds, paid) to separate news from no-news moves more finely than 8-K 2.02 days | LIVE < 1 %, DEMO ~1-2 % |
