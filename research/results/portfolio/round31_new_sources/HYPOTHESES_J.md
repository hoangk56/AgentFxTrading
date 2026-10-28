# Round 31, stream J: hypotheses (Japan's public flow and positioning tables)

Written 2026-10-27 18:23-18:40 UTC (`date -u` 18:22:56 at the start). Every rule below is declared **before any of its
returns were computed**. At this time the flow tables were downloaded (or downloading) but none was joined to a price.
Post-hoc additions, if any, are appended at the end with their own time and marked.

## Sources found (history actually offered, probed 18:10-18:25 UTC)

| id | source | URL | history | split long / short? | usable |
|---|---|---|---|---|---|
| S1 | TFX Click 365 daily report (per pair: OHLC, settlement, swap, volume, open interest) | https://www.tfx.co.jp/kawase/document/PRT-010-CSV-003-YYYYMMDD.CSV (list in https://www.tfx.co.jp/historical/fx/) | 2008-08-14 .. now, one file per trading day | **no**: one OI number per pair | yes, as total OI / volume |
| S1w | Click 365 weekly customer buy / sell positions ("為替売買動向", Tuesdays) | https://www.click365.jp/resorces/doc/weekly_sellbuy.xls | only the latest 4 weeks on the site; the Wayback Machine holds 19 snapshots 2013-2022 (and answered 429) | yes | **no** (no history) |
| S1k | Click Kabu 365 (index CFDs incl. Nikkei 225) daily report | /kawase/document/PRT-010-CSV-015-YYYYMMDD.CSV | 2010-11-22 .. now | no (OI only) | possible PRE price proxy for JP225 2010-15 |
| S2 | MoF weekly International Transactions in Securities (designated major investors), net = acquisition - disposition per category | https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/week.csv | week of 2005-01-02 .. now | n/a (flows) | yes, 2005-2024 |
| S3 | JPX weekly trading by investor type (TSE 1st section / Prime, value) | https://www.jpx.co.jp/markets/statistics-equities/investor-type/00-00-archives-NN.html (PDF per week) | 2016 .. now online (no PRE) | purchases and sales per investor type | yes, 2016-2024 |
| S3m | JPX weekly outstanding margin transactions (customers' long and short balances, Tokyo + Nagoya) | https://www.jpx.co.jp/markets/statistics-equities/margin/05.html (`20260925_mtsk.pdf`, the long history table) | weekly from 2002-08-02 | **yes** (long and short balances) | yes (related source found in the row) |
| S3s | JPX daily short-selling ratio | https://www.jpx.co.jp/markets/statistics-equities/short-selling/index.html | only the last ~12 months online | n/a | **no** (no history) |
| S4 | MoF FX intervention record (date, amount, pair) | https://www.mof.go.jp/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv | 1991-04 .. now | n/a | days 2004-2024: 2004 47, 2010 1, 2011 7, 2022 3, 2024 4 (HOLD); **0 in IS 2016-21** |
| -- | FFAJ net positions of OTC retail FX (USD/JPY monthly, non-USD quarterly) | ffaj.or.jp | monthly / quarterly | yes | 12 or 4 points a year: no power at 1-5 days; not used |

Release clocks used (declared):
- S1: trading day D ends 05:55 JST D+1 (20:55 UTC D); the report is posted "the next business day before noon JST".
  Signal time = **04:00 UTC on D+1** (13:00 JST). Outside C3's 23:00-02:00 UTC window on every day.
- S2: released Thursday 08:50 JST (Wednesday 23:50 UTC) for the week ending the previous Saturday. Entry **Thursday
  03:00 UTC** (the next JP business day if Thursday is a JP holiday).
- S3: published on the 4th TSE business day after the week at 15:00 JST. Entry **07:00 UTC** on that day.
- S3m: published Tuesday (2nd business day) 16:00 JST for the previous Friday. Entry **Tuesday 08:00 UTC** (next
  business day if a holiday).

## Common method (applies to every family)
- Prices: IC M1 (`research.m1.load`, ts < 2025-01-01 cut at load) for IS 2016-21 / VAL 2022-24; Dukascopy M1 (USDJPY,
  EURJPY, GBPJPY, EURUSD; m1c GBPUSD, AUDUSD) and H1 (AUDJPY) for PRE 2004-15 where the series exists. JP225 has no
  local PRE price; Click Kabu 365 settlement prices may serve as a PRE proxy (stated if used).
- Every new series (S1-S4) is cut at 2024-12-31 at load; no 2025-26 value is printed or summarised.
- Fills: buy at the ask close, sell at the bid close of the entry minute; same at exit. Variants: +1 minute,
  spread x1.5. Commission 0.6 bp round trip FX, 0 for JP225. Swap from `research.swing.rates.swap_frac_at` per
  17:00 New York rollover crossed (FX triple on Wednesday, JP225 triple on Friday). PRE cost: IC 2016-17 median spread
  at the same minute-of-day + 0.6 bp, plus the 0.6 bp commission; swap PRE from the same model (rates before 2014 are
  forward-filled from the first point: approximate).
- Exit after h weekdays at the entry clock, capped at 5 x 24 h. Daily-signal rules use h in {1, 3} so that at most 3
  positions per pair are open; weekly rules use h in {1, 3, 5} (no overlap).
- t: clustered by entry day for h = 1; for overlapping h = 3 daily rules, clustered by ISO week of entry. Baskets:
  the trade is the equal-weight basket (one cluster per entry).
- Random-entry control: >= 200 seeds; same count, hold and side mix, entry days drawn at random from the same weekday
  set in the same era at the same clock; for signal-driven sides the side sequence is permuted (equivalent to
  assigning the signal of a random week / day).
- Parameters (h, threshold) chosen on IS only; VAL checked once with the IS choice; PRE where the series exists.
- Multiple testing: each family reports its cells and the best |t| against the max-of-K-normals benchmark.

## Power arithmetic (frontier: round 10 STREAM_D_outputs 1-day sd; h-day sd = sd1 x sqrt(h))
LIVE needs per-trade net Sharpe >= 3 / sqrt(1.73 x n per year); DEMO's IS t >= 2 needs >= 2 / sqrt(6 x n per year).

| design | n / yr | sd per trade (bp) | LIVE edge needed (bp) | DEMO edge needed (bp) | LIVE as a correlation |
|---|---|---|---|---|---|
| weekly signal, USDJPY, h = 5 | 52 | 112 | 35 | 12.7 | 0.32 |
| weekly signal, JPY basket (4 pairs, corr ~0.75, sd x0.90), h = 5 | 52 | ~110 | 35 | 12.4 | 0.32 |
| weekly signal, JP225, h = 5 | 52 | 283 | 89 | 32 | 0.32 |
| weekly signal, JP225, h = 1 | 52 | 126 | 40 | 14 | 0.32 |
| daily signal, USDJPY, h = 1 | 250 | 50 | 7.2 | 2.6 | 0.14 |
| daily signal, AUDJPY / GBPJPY, h = 1 | 250 | 67-68 | 9.7 | 3.5 | 0.14 |
| big-move days (top decile, ~25 / pair / yr, ~40 distinct days / yr over 7 pairs), h = 1, per day cluster | ~40 | ~70 (big days are wider) | ~25 | ~9 | 0.36 |

Prior from the literature: weekly flow tables explain at most ~1 % of next-week FX / index variance (correlation
~0.05-0.10). At 0.08 the weekly designs give IS t ~1.4 and LIVE power ~0.8; a daily positioning signal at the typical
sentiment correlation 0.02-0.04 gives IS t ~0.8-1.6 and LIVE power ~0.4-0.8. **So before any number: LIVE is not
reachable by any design here unless the effect is 3-4x the literature size; DEMO is reachable only at the upper end.**
The families are still run because they are new data and the brief asks for the answer, not the prior.

## Family T: TFX Click 365 open interest (S1)
Mechanism / sources: Japanese retail FX margin traders are contrarians (BoJ Review 2023-E-7, Matsuda et al.,
https://www.boj.or.jp/en/research/wps_rev/rev_2023/rev23e07.htm: "widely known as contrarians who take the opposite
positions to market movements"); in non-USD crosses they are persistently net long foreign currency / short yen (carry;
RBA Bulletin March 2009, "Japanese Retail Investors and the Carry Trade"; BoJ Chart 11), while in USD/JPY their net
side flips (net short USD in 2021, long in 2022). Brokers liquidate losing positions automatically at loss-cut levels,
which can produce outsized moves (Kobe University WP 1909, https://www.econ.kobe-u.ac.jp/wp/wp-content/uploads/2023/06/1909.pdf).
The brief's stance: retail positioning is contrarian (fade it).

Signals (day D, causal): dOI = log(OI_D / OI_{D-1}); z_dOI = dOI standardised by its trailing 250-day mean and sd
(no look-ahead); r_D = the pair's IC mid return 20:55 UTC D-1 -> 20:55 UTC D (the TFX trading day).
Pairs: USDJPY, EURJPY, GBPJPY, AUDJPY (JPY block); EURUSD, GBPUSD, AUDUSD (USD block, Click 365 volumes small).

- **T1 fade retail adds in the carry crosses.** In EURJPY, GBPJPY, AUDJPY (retail net long the foreign currency), a
  rise in OI = retail adding longs. Side: short the cross when z_dOI > +k, long when z_dOI < -k (retail cutting:
  fade = buy). Cells: k in {0, 1}, h in {1, 3}: 4 cells x 3 pairs, pooled as a basket per day = 4 primary cells.
  USDJPY excluded (no stable net side). Expected size: correlation 0.02-0.05.
- **T2 big-move days, liquidation vs absorption.** Days with |r_D| in the top decile of the pair's trailing 250-day
  |r| distribution. If OI fell (dOI < 0: positions closed, stop-outs / loss-cuts = forced flow) the move is price
  pressure and reverts: side = -sign(r_D). If OI rose (retail absorbed the move as contrarians), fade the retail: the
  move continues, side = +sign(r_D). Combined: side = sign(r_D) x sign(dOI). Pairs: all 7. Cells: h in {1, 3}; arms
  {both, liquidation arm only, absorption arm only}: 6 primary cells, pooled across pairs (cluster by day).
  Expected: tens of bp on ~40 distinct days a year (the only design here with a plausible DEMO size).
- **T3 crowding level (information).** OI level z (trailing 250-day) in the carry crosses: high OI = crowded retail
  carry; side short the cross when z_OI > 1, h in {1, 3}. 2 cells, pooled.
- **T-vol (information only, no side):** Click 365 volume z as a predictor of next-day |r| (not tradable alone).

## Family M: MoF weekly portfolio flows (S2)
Mechanism / sources: Japanese institutional portfolio flows are persistent week to week (life insurers', pension and
investment-trust programmes) and have price impact (Froot & Ramadorai 2005, "Currency returns, intrinsic value, and
institutional-investor flows", JF; Evans & Lyons 2002 order flow). The question is whether the published week's flow
predicts the coming week's yen while the market already knows it (released 5 days after the week ends).
Signals: weekly net (100 million yen) per category, z against the trailing 52-week mean and sd (causal):
- A = residents' net acquisition of foreign long-term debt + foreign equity and fund shares (outward, yen selling to
  the unhedged share);
- L_eq = non-residents' net acquisition of Japanese equities; L_bd = non-residents' net acquisition of Japanese
  long-term debt.

- **M1 outward flow persistence -> yen weaker.** Side: long the JPY basket (USDJPY, EURJPY, GBPJPY, AUDJPY equal
  weight; also USDJPY alone as a cell) when z_A > k, short when z_A < -k. k in {0, 1}, h in {1, 3, 5}: 6 cells x 2
  instruments = 12.
- **M2 foreign equity buying persistence -> Nikkei up.** Side: long JP225 when z_Leq > k, short when < -k. k in {0, 1},
  h in {1, 3, 5}: 6 cells. (Froot, O'Connell & Seasholes 2001; Richards 2005: foreign flows positively predict
  returns.)
- **M3 foreign JGB buying -> yen stronger.** Side: short the JPY basket when z_Lbd > k, long when < -k. k in {0, 1},
  h in {1, 3, 5}: 6 cells (weak prior: much of it is hedged / bills).
PRE 2005-15 for M1 / M3 (Dukascopy JPY pairs; AUDJPY H1); M2 has no local PRE price.
Note the sign convention of the outward net changed in January 2014 in MoF's notice; we compute net = acquisition -
disposition from the columns, so the convention does not matter.

## Family X: JPX weekly investor type (S3, 2016-2024 only)
Mechanism / sources: foreigners are positive-feedback traders whose net buying persists and predicts returns
(Kamesaka, Nofsinger & Kawakita 2003, "Investment patterns and performance of investor groups in Japan", PBFJ);
individuals are contrarian and their net buying predicts poor returns (same paper; Japanese practitioner use of
"海外投資家の売買動向").
- **X1 foreigners' weekly net buying -> JP225 continues.** Side: long JP225 when z_F > k, short when z_F < -k (z vs
  trailing 52 weeks). k in {0, 1}, h in {1, 3, 5}: 6 cells.
- **X2 fade individuals.** Side: short JP225 when z_I > k (individuals net bought), long when < -k. Same 6 cells.
  (X1 and X2 are strongly negatively correlated by construction; reported as one family of 12 cells.)
- **X3 foreigners' buying -> yen (information).** Short USDJPY when z_F > 0, h in {1, 5}: 2 cells.
No PRE (the weekly archive starts 2016).

## Family G: JPX weekly margin balances (S3m, 2002-2024)
Mechanism / sources: margin traders on the TSE are mostly individuals; margin longs are a contrarian "overhang"
(future forced / scheduled selling: standard margin positions must be closed within 6 months) and a high buy / sell
ratio (信用倍率) is read as bearish by Japanese practitioners; individuals' margin buying into falls is the retail
contrarian pattern (Kamesaka et al. 2003).
Signals: customers' margin long value L and short value S (Tokyo + Nagoya, million yen).
- **G1 change in margin longs -> fade.** dL = log(L_t / L_{t-1}); z vs trailing 52 weeks. Side: short JP225 when
  z_dL > k, long when z_dL < -k. k in {0, 1}, h in {1, 3, 5}: 6 cells.
- **G2 buy / sell ratio level -> fade.** R = L / S, z vs trailing 52 weeks. Short JP225 when z_R > k, long when
  z_R < -k. k in {0, 1}, h in {1, 3, 5}: 6 cells.
PRE: only if a JP225 price proxy (Click Kabu 365 settlement 2010-15) is fetched.

## Family I: MoF intervention record (S4, information only)
IS 2016-21 has no intervention day, so no rule can meet the IS bar; this family is information only.
- **I1 continuation after an intervention day.** Literature: interventions move the rate in the intended direction
  and, in the 2003-04 and 2010-11 episodes, the effect lasted days (Ito 2003; Fatum & Hutchison 2006). Side: the
  intended direction (USD/JPY up for yen-selling interventions), entered at 04:00 UTC the next day, h in {1, 3, 5}.
  Episodes: 2004 (47 days, heavily clustered), 2010-11 (8), 2022 (3, VAL). 3 cells. Note: the day-level record is
  published only weeks later, so a live rule would have to detect the intervention itself (a separate problem).

## Cell count
T 4 + 6 + 2 = 12; M 24; X 14; G 12; I 3. Total 65 declared cells (I is information only).

## Post-hoc additions

### 2026-10-27 18:30 UTC (after the M, G, T and I cells were computed; marked POST HOC)
While checking the TFX alignment (no return of T4 computed yet): the same-day correlation corr(r_D, dOI_D) is strongly
non-zero but its sign differs by pair and era (e.g. AUDJPY IS -0.59, USDJPY VAL +0.63). For contrarian retail traders
that sign reveals their net side: OI rises on down days when they are net long (buying dips) and on up days when they
are net short (selling rallies). This gives a net side without the long / short split.
- **T4 inferred retail flow, faded (POST HOC).** c_D = corr(r, dOI) over the trailing 60 TFX days (causal);
  retail flow f_D = dOI_D x (-sign(c_D)) (> 0 = retail net buying). Side: -sign(f_D) (fade retail) when |z_dOI| > k.
  All 7 pairs, basket per day. k in {0, 1}, h in {1, 3}: 4 cells. Post hoc, so even a pass would be held to round 18's
  1/4 retention for the expected HOLD t.
- Random controls (as declared in the common method) are run for the best IS cell of every family.
