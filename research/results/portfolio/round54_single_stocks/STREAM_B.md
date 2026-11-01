# Round 54 stream B: firm-level buyback windows on single-stock CFDs (long at window reopening, short at blackout start)

Written 2026-10-30 10:41 UTC. Hypotheses were declared before any return, in [HYPOTHESES_B.md](HYPOTHESES_B.md):
- main grid at 10:08:33 UTC, before stream D's prices existed;
- addendum B1 at 10:37:04 UTC, after reading only stocklib.py's source and D's CSV headers, and before any price was loaded.

Same LIVE / DEMO bars as research/PROMPT.md. HOLD stayed closed:
- stocklib cuts at 2024-12-31 at load (asserted); US500 IC m1 was cut at ts < 1735689600000 at load (asserted);
- round 47's XBRL facts / 8-K files were already cut at parse (filed <= 2024-12-31);
- nothing from 2025-26 was loaded or printed. No network request was made by this stream.

## Answer
There is no LIVE or DEMO candidate and no PREREG_DRAFT. **All 24 counted cells are net negative in both IS and VAL.**
- **Cost kills it.** Every trade enters at the Dukascopy daily open, and the open candle's spread is very wide (D: median
  65 bp round trip across names). For these large caps the mean round-trip cost is 36-49 bp. The best IS net t is +0.48
  (blackout-start short, D10, 5 days), against a declared chance benchmark of 0.94. 0 cells reach IS t 2.
- **The reopening long has gross IS, but it decays and is mostly post-earnings drift.**
  - Q5 reopeners, gross, minus the same-date cross-section, IS: +20.6 bp at 1 day (t 2.53) and +36.3 bp at 3 days (t 2.73).
    VAL: +2.7 and +8.9 bp.
  - Against low / no-buyback reopeners in the same week (both groups 2 days after their own release), Q5 is ahead by
    +19 / +24 / +26 bp at 1 / 3 / 5 days in IS, but with t 1.85 / 1.22 / 0.99. In VAL the gap is +10 / +12 / -23 bp
    (t <= 0.6).
  - The 3-day IS figure owes much to 2020 (+106 bp that year).
  - Post hoc, a gross sign-flip benchmark over the 24 cells has a 95 % quantile of 2.77. The best gross cell is at 2.73,
    so even the gross pattern is within chance.
- **The mirror (short at blackout start) fails.** Gross is about 0 in IS and the wrong sign in VAL: the stocks rise, by
  -18 to -60 bp for the short. Its events also cluster: 436 IS events fall on only 84-87 dates, because E + 3 months -
  14 days is the same calendar date for every calendar-quarter firm.
- **Even with optimistic costs it fails.** Primary cells with every fill paying the closing spread (addendum B1, information
  only): IS +14.0 / +20.8 bp (t 0.89 / 1.57), but VAL -8.7 / -11.3 bp.

## Data and construction
- **Firms.** D's 219 stocks intersected with round 47's top-200 Vanguard entities gives **170 firms**, with a median of 128
  firms ranked per date.
- **Events from 2016.** 6,023 in total. Per year from 2018 (2017 is partial, as D's data start 2017-01..11):
  - Q5 reopenings: ~92-109 a year, 89 firms.
  - D10 reopenings: ~46-56 a year.
  - Blackout starts: the same counts.
- **Ranking.** BY = 4 x run-rate / Vanguard 13F value at year-end Y-1. This is a ranking proxy for buyback / market cap
  (values > 1 just mean Vanguard owns ~8 %). Q5 = cross-sectional 0.8 quantile on the event date, among intersection
  firms quoted the day before.
- **Window rule.** Round 47 W14 + A1. The reopening day r is the release session + 2 trading days. The blackout start is
  the first trading day >= E + 3 months - 14 days.
- **Trades.** Long at the open of r (short at the open of c), exit at the close of day + h - 1, h = 1 / 3 / 5.
  - Hedges: XS (minus the equal-weight mid return of D's non-ETF names over the same span) and US500 (IC 09:31 / 15:59
    ET bid / ask, beta 1).
  - Costs from D's stocklib: open / close candle spreads, USD 0.02 per share per side, financing (EFFR ± 3 %) / 360.
    D-flagged jump spans are excluded.

## Results (net bp per trade, entry-date-clustered t)
"rnd" is the share of 200 random-firm draws (same dates, side and hedge) beaten, IS / VAL. Power is the VAL net Sharpe x
sqrt(HOLD n).

| cell | IS n (dates) | gross IS (t) / VAL | cost | net IS (t) / VAL (t) | x1.5 IS / VAL | +1 day IS / VAL | ex-2020 IS (t) | years > 0 | power | rnd | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reopen Q5 h3 US500 **(primary)** | 432 (288) | +31.2 (1.98) / +12.1 | 41.2 | -9.5 (-0.61) / -29.8 (-2.24) | -25 / -46 | -32 / -41 | -13.0 (-0.89) | 1/8 | -1.60 | 1.00 / 0.93 | none |
| reopen Q5 h3 XS (primary mechanism) | 442 (297) | +36.3 (2.73) / +8.9 | 39.6 | -2.4 (-0.18) / -32.2 (-2.52) | -17 / -48 | -24 / -35 | -4.3 (-0.34) | 2/8 | -1.77 | 0.99 / 0.94 | none |
| reopen Q5 h1 XS | 442 (297) | +20.6 (2.53) / +2.7 | 36.4 | -15.0 (-1.87) / -34.9 (-4.15) | -30 / -52 | -30 / -32 | -14.3 (-1.95) | 0/8 | -2.93 | 1.00 / 0.95 | none |
| reopen Q5 h5 XS | 442 (297) | +26.1 (1.79) / +9.8 | 43.5 | -15.6 (-1.07) / -36.4 (-1.95) | -30 / -52 | -44 / -29 | -12.0 (-0.83) | 1/8 | -1.50 | 0.98 / 0.90 | none |
| reopen D10 h1 XS | 223 (179) | +27.7 (2.44) / +9.1 | 34.4 | -5.6 (-0.49) / -27.1 (-2.38) | -19 / -43 | -39 / -22 | -2.3 (-0.21) | 1/8 | -1.64 | 1.00 / 0.97 | none |
| reopen D10 h3 XS | 223 (179) | +22.8 (1.21) / +16.6 | 37.8 | -13.4 (-0.72) / -23.4 (-1.27) | -27 / -39 | -52 / -18 | -7.7 (-0.41) | 3/8 | -0.89 | 0.98 / 0.93 | none |
| bstart Q5 h1 XS (mirror, short) | 450 (87) | +1.0 (0.12) / -6.1 | 37.3 | -37.2 (-4.32) / -42.2 (-5.16) | -54 / -58 | -47 / -31 | -35.8 (-4.64) | 0/8 | -4.85 | 0.86 / 0.93 | none |
| bstart Q5 h5 XS (mirror) | 449 (87) | +28.0 (1.43) / -38.7 | 37.6 | -11.6 (-0.61) / -73.3 (-6.53) | -27 / -89 | -22 / -63 | -14.6 (-0.73) | 2/8 | -3.34 | 0.99 / 0.18 | none |
| bstart D10 h5 US500 (best IS net t) | 219 (62) | +65.0 (1.94) / -39.0 | 48.9 | +15.4 (0.48) / -86.8 (-3.78) | -0 / -104 | +35 / -80 | +4.9 (0.15) | 1/8 | -2.87 | 0.99 / 0.03 | none |

All 24 rows, with net by year, are in `out/cells.csv` and `out/grade.log`.

**Random-firm control.** The reopening cells beat 98-100 % of random firms in IS and 90-97 % in VAL. This is partly a cost
artefact: Q5 firms are megacaps with tighter open quotes than the random D names, and the control compares nets. It does
not rescue any cell, because every net is < 0.

### Mechanism contrast (declared): XS gross of Q5 reopeners minus Q1-3 reopeners, same ISO week
| h | IS diff (t), weeks | VAL diff (t), weeks | Q5 / Q1-3 alone, IS | Q5 / Q1-3 alone, VAL |
|---|---|---|---|---|
| 1 | +19.3 (1.85), 134 | +10.4 (0.59), 81 | +20.6 / +6.0 | +2.7 / +4.1 |
| 3 | +24.4 (1.22), 134 | +12.4 (0.41), 81 | +36.3 / +6.1 | +8.9 / +10.1 |
| 5 | +26.3 (0.99), 134 | -23.2 (-0.58), 81 | +26.1 / +1.0 | +9.7 / +15.7 |

In VAL, the big buyers do no better than low-buyback firms reopening in the same weeks. The IS gap is within ~1-2 se, and
with 9 cells looked at (3 h x 2 eras, plus the gross cells) it is not evidence of a buyback bid.

### Post hoc (information, labelled; not used for any verdict)
- **Gross by year, Q5 h1 XS:** 17 +6, 18 +27, 19 +19, 20 +23, 21 +18, 22 0, 23 -11, 24 +20 bp. IS ex-2020-03/04 is
  +20.1 (t 2.85).
  - h3 XS is +22 +15 +28 +106 -7 +5 +3 +19: 2020 dominates. It is +33.3 (t 2.63) ex-03/04, so the rest of 2020 carries it.
- **Gross sign-flip benchmark over the 24 cells (IS):** the 95 % quantile is 2.77 (median 1.41). The best observed gross is
  2.73 (reopen Q5 h3 XS).

## Cells tried and chance
- **24 counted cells:** 2 sides x Q5 / D10 x h 1 / 3 / 5 x 2 hedges.
- **Declared chance benchmark:** a per-entry-date sign flip on gross, shared by all cells, then costs; 1,000 draws. The
  95 % quantile of the max IS net t is 0.94 (median -0.56). The best observed is 0.48.
- **Post hoc gross benchmark:** 2.77 against a best of 2.73.
- **Information (not counted):** the 6 mechanism-contrast rows and 2 optimistic-spread rows.

## Power, bots, positions
- **HOLD size, counted as declared:** HOLD n ~ VAL events / 3 x 1.73 ~ 165 (Q5) and ~83 (D10). VAL power is negative in
  every cell.
- **Even at the IS gross size and zero cost, LIVE is out of reach.** Q5 h1 XS: Sharpe 20.6 / ~150 ~ 0.14, x sqrt(165) ~
  1.8, under 3. That matches the count arithmetic declared beforehand.
- **Positions.** The rule would trade 86-88 different stocks.
  - Q5 h3: max 10 concurrent positions, 95 % quantile 6, mean 2.3 on the ~105 active days a year.
  - Q5 h5: max 12, q95 8.
  - That means ~4 multi-symbol bots of <= 3 positions each, or one bot per stock (~88), plus a US500 hedge bot that needs
    up to ~4 bots, or a netted hedge.
- Correlation with C3: not computed (nothing survived; the C3 trade file is present).

## Exhausted (add to PROMPT "Những họ đã cạn")
- **The trade.** Firm-level buyback windows on single-stock CFDs:
  - top 200 US issuers x Dukascopy's 219 US stock CFDs, 170 firms;
  - ranked by buyback run-rate as filed / Vanguard 13F value, Q5 / D10;
  - long from the open of window reopening (release + 2 trading days) for 1 / 3 / 5 days, and the mirror short at
    blackout start (E + 3 months - 14 days);
  - hedged by the same-date cross-section and by US500.
- **The verdict.**
  - All nets are < 0 at Dukascopy open-candle costs (36-49 bp round trip).
  - At optimistic close-spread costs, VAL is still < 0.
  - The gross reopening pattern (+20-36 bp IS) shrinks to +3-9 bp in VAL. It is not separable from low-buyback reopeners
    in the same week, and it sits within the 24-cell chance benchmark.
  - The blackout-start short has the wrong sign in VAL.

## Pitfalls
- **Dukascopy daily open candle.** The "open" of the Dukascopy daily candle is the first quote of the session, with a
  median 65 bp spread (D). Any open entry pays it, so the cost model decides the verdict. Use a close entry, or a later
  intraday bar from the M1 / tick data, in future designs. IC's real MT5 opening spread is unknown.
- **Blackout start clusters on the calendar.** E + 3 months - 14 days is the same date for all calendar-quarter firms:
  436 IS events sit on ~86 dates. Clustered t is essential, and the mirror is in effect a ~16-date-a-year calendar trade.
- **The ranking proxy.** Vanguard 13F value is about 6-9 % of market cap. BY therefore reads > 1 for heavy buyers (AAPL ~1.0
  in 2016). It is a rank only. It misranks dual-class and founder-held firms, where Vanguard holds less.
- **Reopening sits at release + 2 days.** The reopening long is also a post-earnings day-2 trade, so its gross includes
  drift and reversal common to all reporters (Q1-3 reopeners: +6 bp at h1 in IS). The same-week Q5 - Q1-3 contrast is
  the separation test.
- **Random-firm control on nets is biased toward megacap cells.** They have tighter spreads than the random D names. Read
  the control on gross as well.
- **Dividends** are not in D's prices. The declared "share of trades with an ex-day inside" could not be measured (no
  dividend file). Longs are biased down and shorts up by any dividend inside the hold: ~0.2-1 % a quarter, and ex-dates
  rarely fall at release + 2 days.
- **Old tickers.** D's tickers are the old Dukascopy names (FB, PCLN, CTL...). Map by CIK (S.idx(cik)), as done here.

## Directions that need the user
| direction | value |
|---|---|
| IC MT5 demo account to log real opening and closing spreads of US megacap CFDs. This tells whether any open-entry single-stock rule can be cheaper than Dukascopy's 65 bp open candle. | Useful for every round 54 stream; for this one LIVE < 1 %, DEMO ~2 % (the VAL gross is only +3-9 bp) |
| A re-declared close-entry or intraday-entry variant (enter at the close of r - 1 or 10:00 ET on M1) | VAL gross is already seen for open -> close, so it is not clean. Needs fresh data after 2026-09 to test: < 1 % |

## Files
- **Hypotheses:** [HYPOTHESES_B.md](HYPOTHESES_B.md) (main grid + addendum B1).
- **Scripts:** `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/B/scripts/`
  - events.py: reopen / blackout events and BY, with no prices.
  - us500.py: the IC US500 09:31 / 15:59 ET table, cut < 2025.
  - grade.py: the 24 cells, controls, contrast and concurrency.
  - posthoc.py: by-year gross and the gross benchmark.
- **Outputs:** `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r54/B/out/`
  - events.csv, members.csv, rr.npz and us500.npz;
  - grade.log, cells.csv, trades.npz and maxt_null.npy;
  - posthoc.log.
