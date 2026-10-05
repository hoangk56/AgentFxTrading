# Round 8: how the symbols affect each other (2026-10-05)

The user asked for research into algorithms and strategies built on the interaction between symbols: one market
leading another, shocks spreading across markets, linked symbols diverging and converging, and spillovers between
trading sessions. Rounds 2-7 had touched this only in places. The table below lists those tests; none of them was
redone:

| already rejected | where |
|---|---|
| daily 26 x 26 lead-lag on 20:00-UTC closes; US equities -> USD next day (U1); oil -> USDCAD over 1-3 h | [flow_search_2026-09-27.md](flow_search_2026-09-27.md) |
| pairs mean reversion of price levels, 14 pairs, <= 5 days | [swing_lab_v2_2026-09-27.md](swing_lab_v2_2026-09-27.md) |
| US30/USTEC -> US2000, STOXX50 -> periphery | [round7_new_data_2026-10-05.md](round7_new_data_2026-10-05.md) (B) |
| cross-sectional D1 momentum, FX reversal on 2025-26 data | removed lab (JOURNAL, before 2026-09-27) |

Round 8 ran four streams in parallel on one shared M1 panel of the 26 IC symbols. The panel holds mid and spread at
each minute's last tick, 2016-01..2024-12; HOLD is not in it. The brief and the streams' rules are in
[round8_hypotheses/](round8_hypotheses/), all written before the numbers they govern. The constraints are the user's:
lots independent of capital, each position held <= 5 days, at most 3 positions per bot. The pass bar is that of
rounds 3-7:
- net > 0 in IS and in VAL;
- IS day-clustered t >= 2.5 and VAL t >= 1.5;
- >= 2/3 of years net positive;
- beats >= 95 % of random entries;
- still positive at spread x1.5 and at +1 minute latency;
- power = per-trade net Sharpe x sqrt(expected HOLD trades) >= 3.

| stream | question | cells |
|---|---|---|
| L | intraday lead-lag, 1-60 minutes: a 26 x 26 matrix, 10 named economic leads, dynamic (time-varying) leads | ~32,000 |
| S | shock spillover: a large fast move in one market -> linked markets; beta-gap catch-up; safe havens after equity drops; cross-market response to 08:30 New York data | ~6,700 |
| R | relative value, minutes to 5 days: return-spread pairs with rolling hedge ratios, Avellaneda-Lee PCA residuals, currency strength meter, commodity-currency fair value, index dispersion | ~10,000 |
| X | literature map (38 papers, 32 mechanisms), cross-session spillovers, risk-regime conditioning, crypto -> indices, dollar-gold divergence, weekly oil -> equities | 193 |

## Answer

**No candidate. Nothing was pre-registered and HOLD (2025-01..2026-09) stayed closed.**

The interaction between the symbols is real and measurable. The robust 26 x 26 lead-lag matrix has 1,248 cells
with |t| >= 4 where about 2 are expected by chance, and the IS and VAL t-values correlate at 0.41. But every part a
bot can act on is a fraction of IC's cost:

| what is real | size | cost it has to beat |
|---|---|---|
| lead-lag after a 1-minute delay | 0.01-0.2 bp per 1-sd leader move; the response in the same minute is 3-15x larger and cannot be traded | FX 0.7-1.2 bp, index CFDs 2.4-7 bp |
| a lagging USD pair catching up with the dollar factor (L2h-ii) | +0.04 bp per sd (t 11.8 IS / 7.1 VAL); the trading rule earns +0.1 bp | 0.8-0.9 bp |
| slow diffusion of shocks into JP225 / HK50 / BTC / ETH | 1-7 bp over 15-240 min | 2.5-8 bp (ETH 14-132) |
| FX residual / currency-strength reversal | +1.2..+2.7 bp per trade, positive at mid in IS, VAL and 2004-15 | 1.2-1.5 bp per FX round trip |
| relative value outside FX | the pair moves about as much as its cost or less | two legs: 4-9 bp in indices and metals, 27 bp in oil, 120 bp in BTC/ETH (IS) |
| weekly oil -> next-week US500, fade (Driesprong et al. 2008) | VAL -54 bp per oil sd (t -3.2); IS weak (see the lead's check) | ~2 bp plus ~8 bp of weekly index financing |

The best cell overall, US30 continuing in its own direction after the 08:30 New York data, reaches power 2.6 IS /
1.4 VAL against a bar of 3, and its side was chosen after looking at the data.

## L. Intraday lead-lag

Rule: the leader's k-minute return, scaled by its trailing 20-day sd, predicts the follower's return over the next
h minutes, starting one minute after the signal. The slope is a partial slope (controlling for the follower's own
past return), with day-clustered t. Sessions are Asia 23-07, Europe 07-13 and US 13-20 UTC, and trades close inside
the session. The trading version enters when |signal| reaches the IS P90/P95/P99 and pays the actual spread at the
entry and exit minutes plus commission.

| hypothesis | best cell | slope IS (t) / VAL (t), bp per sd | rule net IS / VAL, bp | power | verdict |
|---|---|---|---|---|---|
| L1 robust matrix, best gross / cost | Asia k5 h15 JP225 -> DE40 | +0.31 (8.2) / +0.10 (3.0) | -3.11 / -1.75 (cost 5.2 / 2.4) | -3.6 | real, under half of cost |
| L2a JP225 -> USDJPY, 00-06 UTC | k1 h15 | +0.045 (1.9) / +0.027 (1.3) | -0.77 / -0.56 | -5.2 | no |
| L2b US500 -> AUDJPY (risk-on carry) | k15 h1 | +0.014 (4.9) / +0.006 (1.8) | -1.09 / -1.35 | -8.0 | no |
| L2c XAU -> AUDUSD | US k15 h1 | +0.009 (3.3) / +0.001 (0.2) | -0.87 / -0.76 | -6.2 | no |
| L2d XAU -> XPT | Asia k5 h1 | +0.077 (5.9) / +0.037 (3.4) | -27.0 / -30.4 | -43 | real; XPT's spread kills it |
| L2e oil -> USDCAD at 1-15 min | XTI k15 h1 | -0.004 (-2.4) / -0.004 (-2.5) | -0.77 / -0.73 | -31 | no |
| L2f DE40 -> EURUSD, UK100 -> GBPUSD at the European open | UK100 k15 h15 | +0.12 (2.1) / +0.01 (0.2) | -0.14 / -0.57 | -0.3 | no |
| L2g BTC -> ETH | k15 h15 | -1.35 (-2.6) / -0.30 (-0.8), wrong sign | -127 / -14 | -51 | no |
| L2h-i USD factor -> XAU | Europe k1 h15 | -0.085 (-2.4) / -0.065 (-2.0) | -1.34 / -0.91 | -6.5 | no |
| L2h-ii a lagging USD pair catches up with the dollar factor | 7 pairs, US k1 h15 | +0.042 (11.8) / +0.035 (7.1) | -0.78 / -0.71 (gross +0.11 / +0.09) | -13.6 | real and robust, 1/8 of cost |
| L2i US500 -> AUS200 / JP225 / HK50 | HK50 k5 h5 | +0.20 (4.1) / -0.08 (-0.8) | -2.62 / -2.59 | -3.7 | no |
| L2j JPY crosses vs their synthetic | AUDJPY deviation, Asia | -0.13 per bp (-3.3) / -0.01 | -1.28 / -1.31 | -8.1 | no lag |
| L3 dynamic: trade only on days with a strong trailing lead | XAU -> XPT; US500 -> AUDJPY | +0.28 (4.6) / -0.05; +0.035 (3.2) / +0.020 | -23.5 / -26.5; -0.63 / -1.13 | <= -2.1 | no |

- **The lead sits inside the first minute.** The table below compares the follower's response in the same minute
  (cannot be traded) with its response one minute later (bp per sd, t in brackets). The lead's own check confirms
  the US500 -> AUDJPY row: k1 in US hours, same minute +0.040 (t 5.5) / +0.046 (t 6.9), one minute later +0.009
  (t 1.2) / -0.001 (t -0.2).

  | pair | same minute | one minute later |
  |---|---|---|
  | US500 -> AUDJPY | +0.054 (t 13.9) | +0.013 |
  | BTC -> ETH | +0.84 (t 12.5) | +0.15 (VAL -0.16) |
  | oil -> USDCAD | -0.015..-0.017 (t -5.5..-8.0) | ~-0.003 |
  | JP225 -> USDJPY | +0.033 (t 4.0) | +0.004 |

- **European index CFDs lag in Asian hours**, behind JP225, HK50, AUS200, the US indices and AUDJPY (VAL t 2-5). But
  UK100 and DE40 cost 5-7 bp a round trip then (2.5-5 bp in VAL): the spread prices the stale quote.
- **JPY crosses do not lag their synthetic.** The median |cross - EURUSD x USDJPY| at the minute close is
  0.08-0.10 bp against a 0.23-0.50 bp spread, and the cross does not converge a minute later.
- **Chance.** 31,200 matrix cells (650 ordered pairs x 4 k x 4 h x 3 sessions); 711 L2 cells; 24 L3 pair-windows.

## S. Shock spillover

Event: a source's 5- or 15-minute return of >= 4 or 6 x its trailing 20-day sd. Sources are US500, USTEC, DE40,
JP225, XAU, XTI, BTC, USDJPY, EURUSD and AUDUSD. Entry is the minute after the event; costs are the actual spreads at
those minutes; t is clustered by event day.

| hypothesis (source) | best cell | IS / VAL net bp (t) | power IS / VAL | verdict |
|---|---|---|---|---|
| S1 linked targets continue or revert (Hou 2007; Cohen & Frazzini 2008) | USTEC 15-min 6-sd shock -> EURUSD reversal, 240 min | +3.87 (2.98) / +2.31 (1.45) | 1.70 / 1.04 | fails VAL t and power; IS max |t| 4.02 vs a permutation null median 3.67 |
| S1, cheap target | US500 5-min 6-sd -> USDJPY continuation to 20:00 UTC | +4.53 (1.66) / +3.04 (1.64) | ~0.9 / ~1.3 | consistent, too weak |
| S2 the beta gap closes | DE40 w15 k4, to 20:00 UTC | +2.05 (0.69) / -1.94 (-0.26) | < 0.5 | rejected: the gap extends (mean cell t -0.58 / -0.66) |
| S3 safe havens after equity drops (Ranaldo & Söderlind 2010) | US500 +1 % in 60 min -> short XAU, 60 min | +4.45 (1.37) / +5.39 (1.79) | 0.81 / 1.37 | fails; 11-43 events a year, clustered in 2020 and 2022 |
| S4a 08:30 New York: the USD reaction -> slower assets (Andersen et al. 2007) | GBPJPY 5 min -> 120 min | +12.11 (2.49) / +6.88 (1.10) | 1.93 / 0.85 | chance (max 2.80 vs ~3.1) |
| S4b the target's own news gap closes (registered side) | AUDJPY, 120 min | +9.70 (2.91) / -3.15 (-0.73) | 2.24 / -0.56 | fails VAL |
| S4b mirror: the gap keeps going (side not registered) | US30, 1 min -> 30 min | +13.00 (2.71) / +5.38 (1.83) | **2.56 / 1.41** | closest cell of the round; 7-20 events a year, post-hoc side |

- **The grid as a whole is not chance.** 77 cells have |t_IS| >= 3, against a null 99th percentile of 29; 29 cells
  pass the mid screen in both eras, against 13. But no cell is net positive in both eras.
- **What is real:** shocks in DE40, US500, USTEC, USDJPY, AUDUSD and XAU keep going for 15-240 minutes in JP225, HK50,
  BTC and ETH. The move is 1-7 bp at mid. USDJPY costs only 0.7 bp but moves 2-5 bp (net t 1.2-1.7 per era).
- **Spreads at the next minute after a shock** are only 5-20 % above the same-hour median (BTC is the exception:
  14.5 vs 3.9 bp). The blow-out happens inside the shock minute. The panel holds each minute's last tick, so slippage
  within the minute is not modelled and live fills would be worse.
- **The permutation null.** Flipping each source's sign independently understates chance, because sources shock on
  the same days; flip one sign per day, shared by all sources.

## R. Relative value between linked symbols

| hypothesis (source) | best cell | IS / VAL net bp (t) | cost IS / VAL | power | verdict |
|---|---|---|---|---|---|
| R1 intraday pairs on return spreads with a rolling hedge (Gatev et al. 2006; Elliott et al. 2005; Krauss 2017), 9,720 cells | EURUSD/USDCHF H1, 3-day window, z 2.5 | +12.0 (1.6) / +17.0 (1.8) | 3.2 / 2.6 | 1.13 | fails IS t; 8 trades a year |
| R1, best IS net t | JP225/HK50 H1, HK50 leg only | +59.4 (3.1) / -65.0 (-2.2) | 7.9 / 8.4 | 0.12 | VAL reverses |
| R2 Avellaneda-Lee PCA s-score (2010), 10 FX + 3 metals | k3, OU 5 days, s 1.25 | -1.15 / -1.62 (mid +2.28 (2.4) / +2.44 (1.8)) | 3.4 / 4.1 | -0.74 | real at mid, below cost |
| R2, 8 indices | k3, OU 60 days, s 2.0 | +5.8 (0.8) / -15.7 (-1.6) | 8.3 / 6.7 | -0.36 | fails |
| R3 currency strength meter (popular retail method) | 4 h lookback, 8 h hold, reversal | +0.32 (0.5) / +0.65 (0.7) (mid +1.68 (2.7) / +1.94 (2.2)) | 1.4 / 1.3 | 0.42 | real at mid, about equal to cost; momentum versions flip between eras |
| R4 commodity-currency fair value (Chen & Rogoff 2003; Ferraro, Rogoff & Rossi 2015) | NZDUSD vs AUDUSD, 5 days, z 2 | +35.4 (2.3) / -1.6 (-0.1) | 2.8 / 2.8 | 0.60 | fails; AUD vs gold + US500 and CAD vs oil + US500 do not revert in IS |
| R5 index dispersion (laggard vs leader) | dollar-neutral, every group | within +-3 bp at mid (|t| <= 1.7) | 4.4 / 4.6 | < 0.8 | fails; the single-leg winners are the long-index drift |
| R2b / R3b, post hoc: FX only, entries 07-17 UTC, registered for 2004-15 (Dukascopy H1) | | IC IS / VAL about 0; PRE -1.33 (t -1.8) / -1.20 (t -1.7) | PRE 1.5-1.7 | < 0.3 | fail the registered PRE bar |

Median IS mid / cost / net per trade over each pair's two-leg R1 cells (bp):

| pair | mid | cost | net |
|---|---|---|---|
| EUR/GBP | +0.8 | 1.6 | -0.7 |
| EUR/CHF | +2.1 | 2.4 | -0.2 |
| AUD/NZD | +0.8 | 3.5 | -2.7 |
| gold/silver | +0.4 | 4.1 | -3.4 |
| US30/US500 | -1.4 | 5.8 | -8.1 |
| US500/USTEC | -1.8 | 6.6 | -8.3 |
| DE40/UK100 | -2.5 | 8.3 | -10.8 |
| JP225/HK50 | +2.0 | 8.1 | -6.6 |
| WTI/Brent | -4.5 | 26.8 | -32.7 |
| BTC/ETH | -45 | 120 | -168 |

- **The reversion happens too early to catch.** Variance ratios of the pair residuals are below 1 (AUD/NZD 0.78 at
  1 h, 0.61 at 5 days), but most of the drop has happened within the first hour. That part is microstructure, which a
  fill at the next minute cannot capture.
- **Chance.** In R1 only 1.2 % of cells have IS mid t > 2, against 2.3 % with no effect at all; the best IS net t is
  3.07 against an expected maximum of 3.73. Of the per-pair IS winners, 9 of 29 are net positive in VAL.

## X. Literature map, cross-session and regime spillovers

The literature search covered OpenAlex, Semantic Scholar and arXiv, about 50 queries. It found 38 papers on 32
mechanisms:

| group | papers |
|---|---|
| already tested in rounds 1-7 | Hau & Rey; Hendershott, Livdan & Rösch; Krohn, Mueller & Whelan; Ferraro, Rogoff & Rossi; Gatev et al.; Pu et al. network momentum |
| covered by streams L / S / R | Hasbrouck 2003; Huth & Abergel; Bennett, Cucuringu & Reinert 2022; Billio et al. 2012; Andersen et al. 2007; Aït-Sahalia et al. 2015; Ranaldo & Söderlind 2010; Baur & Lucey 2010; Avellaneda & Lee 2010; Chen & Rogoff |
| need data the repo lacks | bonds (Pitkäjärvi, Suominen & Vaittinen 2020, cross-asset time-series momentum); industry portfolios (Hong, Torous & Valkanov 2007); order flow (Menkhoff et al. 2016); options (Driessen, Maenhout & Vilkov 2009) |
| measured at monthly or quarterly horizons (Rapach, Strauss & Zhou 2013; Chen, Rogoff & Rossi 2010; Pitkäjärvi et al.) | cannot reach power 3 with a 5-day hold |

Screens:

| hypothesis (source) | best cell | IS / VAL net bp (t) | power | verdict |
|---|---|---|---|---|
| X2a US cash session -> next Asian cash session (Lin, Engle & Ito 1994; Hamao, Masulis & Ng 1990; Becker, Finnerty & Gupta 1990) | JP225, HK50, AUS200, AUDJPY, USDJPY | IS slopes all negative (reversal, t -2.2..-3.4); VAL mixed | <= 0 | rejected |
| X2b Asia -> European open | DE40, UK100, EURUSD | all < 0 | <= 0 | rejected |
| X2c European morning -> US session (incl. Gao, Han, Li & Zhou 2018) | US500 1 h, z >= 1.5 | +0.7 (0.2) / +7.1 (1.5) | 0.49 | rejected |
| X2d US overnight gap confirmed by Asia and Europe | US500, first hour | +1.0 (0.5) / +6.7 (1.7) | 0.65 | rejected |
| X3 realised-vol ratio / absorption ratio (Kritzman et al. 2011) -> carry vs havens next day | 46 cells | -0.3 / +6.7 (1.2) | 0.39 | rejected; sign wrong in IS, right in VAL; 2004-15 disagrees with both |
| X4 BTC overnight -> US cash open | 24 cells | +1.6 / +0.8 | 0.18 | rejected |
| X6b weekend crypto -> Monday (Mourey et al. 2025) | 13 / 10 events | -42 / +51 | ~0 | untestable: IC crypto was closed at weekends until 2024-04 |
| X5 dollar-gold divergence | 45 events | +13 / -3 | 0.12 | rejected; follow-up F2 flips in 2004-15 |
| X6a long US500 07-11 London (Bondarenko & Muravyev) | | -0.8 / -0.7 | < 0 | rejected; the control window earns the same |
| X6c weekly oil -> next-week US500, fade (Driesprong, Jacobsen & Maat 2008), sign from the paper | z-sized trade (lot clip(\|z\|, 0.5, 2)) | +30.5 (0.99) / +56.1 (2.43) | 1.10 | fails the IS t, the IS control (94 %) and power |
| X6d commodity currencies -> commodities, weekly (Chen, Rogoff & Rossi 2010) | XTI | VAL < 0, the slope flips | ~0 | rejected |

**Lead's check of X6c (oil -> US500).** Stream X reported an IS slope of -48.6 bp per oil sd (t -2.82, n 144),
negative in 7/7 years. Rerunning its exact code reproduces those numbers. That version drops a week when either
symbol has no bar in the 5 minutes before the timestamp, and it drops 35 IS weeks that way. They include
holiday-Friday ends and the limit-down Monday of 16 March 2020, which removes two large weeks against the fade:
- 2020-03-13: oil -22 %, next week US500 -3 %;
- 2020-04-03: oil +29 %, next week US500 +8 %.

With fills at the first quote after Monday 07:00 and the last quote before Friday 20:00 UTC, all 179 IS weeks:

| | slope, bp per oil sd (t) |
|---|---|
| IS | -18.3 (t -1.21) |
| IS, z clipped at 2.5 | -12.7 (t -0.67) |
| IS without 2020 | -14.1 (t -0.75) |
| VAL | -53.9 (t -3.18) |

By year: 2018 -95, 2019 -13, 2020 -19, 2021 **+11**, 2022 -61, 2023 -86, 2024 -18. The effect is mostly a 2022-24
phenomenon, so X6c is weaker than stream X reported. With VAL already seen, it can only be watched on new data; it
cannot become a candidate.

## What this says

- **Cross-market information is priced within the first minute.** Lead-lags that are significant at t 5-14 in the
  same minute fall to 0.01-0.2 bp once a bot acts a minute later. This is the regime the literature describes: leads
  measured in milliseconds to seconds at the futures venues, while the CFDs follow those futures.
- **Where a lag survives, the spread charges for it.** Stale quotes (European indices at night, platinum, ETH before
  2020) are exactly where the spread is 5-30 bp.
- **Relative value pays two spreads and earns about one.** FX is the only class cheap enough to come close: its
  short-horizon residual reversal is real in three eras, at about +2 bp against 1.2-1.5 bp of cost. That leaves a
  per-trade Sharpe of 0.03-0.05 even before costs, so power stays near 1.5 at zero cost.
- **The conditional and rare effects lack power.** Shock continuation into US30 after US data, oil -> equities
  weekly, and safe-haven flows are 5-50 bp per event, but at 7-50 events a year a 21-month holdout reaches only
  t ~1-2.
- **This round adds an eighth reason to the standing diagnosis:** on IC's cost structure, what the symbols do to each
  other is real but too small or too rare to trade with a bot that acts a minute later. C3 remains the only algorithm
  that has passed.
- **What could change this is decisions, not another screen:**
  1. sub-minute data and execution (tick level, not M1). Most of the lead-lag lives there, but cTrader's retail
     latency and the broker's terms on latency arbitrage make this unrealistic;
  2. a venue with cheaper index and metals spreads, for the slow-diffusion effect (JP225/HK50 continuation after
     shocks: 1-7 bp against 2.5-3.6 bp);
  3. new data after 2026-09-24 to watch X6c and the S4b US30 cell forward; neither can be registered now.

## Process

- **HOLD stayed closed.** The panel ([round8_hypotheses/build_panel.py.txt](round8_hypotheses/build_panel.py.txt))
  stops at 2024-12-31; no stream loaded the full M1 files.
- **Order of work.** Every rule is in [round8_hypotheses/](round8_hypotheses/) (BRIEF, STREAM_*, HYPOTHESES_*),
  written before the numbers it governs. Additions made after a look at the data are marked post hoc there: S2r, S4c,
  the robust L1 matrix, the UK100 and oil diagnostics, F1-F3, R2b/R3b. Their timestamps mix UTC and the Mac's local
  clock (UTC+7).
- **Reproduction.** The screens are scratch scripts, as in rounds 3-6; only the rules and the panel builder are kept.
  Subagents cannot write files named FINDINGS/REPORT, so each stream's write-up came back as text and this report
  condenses it.
- **Pitfalls found, for the next round:**
  - Spiky CFD quotes break day-clustered t on minute data: one UK100 Asian-hours day carried ~20 % of a
    cross-product, and a shifted-day null gave max |t| 9.6. Winsorise, or use a permutation null.
  - IC data glitches book fake mean-reversion profits:
    - UK100 -41 % for 55 minutes on 2017-04-17;
    - ETH -63 % on 2019-05-01;
    - BTC/ETH on 2017-12-22;
    - XTI/XBR in April 2020.
  - Multi-leg trades must not be filtered on quotes at exit time. A first hedged R2 run dropped trades whose HK50
    leg had no exit quote and produced a fake index result (t +12 IS, +9 VAL), which vanished with forward-filled
    closes.
  - Weeks with missing quotes are not random (holidays, limit-down sessions). Fill at the first or last available
    quote rather than dropping them (X6c above).
  - XBR opens an hour after XTI on Sunday, and HK50 has a lunch gap: take pair returns only where both legs quote.
  - EURUSD's median spread at the minute close is 0.0 bp, so FX cost is mostly the 0.6 bp commission.
- **Network.** Stream R's first call to `research.swing.rates.swap_frac_at` fetched five FRED rate files
  (IUDSOIA, IRSTCI01AUM156N, IRSTCI01CAM156N, IR3TIB01CHM156N, IR3TIB01NZM156N) into the git-ignored
  `research/data/rates/`, against the brief's no-network rule. Stream X used only the scholarly APIs. Stream S used
  IC's 2026 constant swaps where those files were missing at the time, which affects only S3's long holds.
- C3 correlation of new rules: not computed, since none survived.
