# Research journal

The verdicts, one entry per day, newest first. Each row says what was tested, the verdict, and which file has the
detail. The numbers are copied from those files, and the file wins if the two ever differ.

When you write a new result file, add a row to that day's entry (or start a new entry) and link the file. Don't
repeat its tables here.

## 2026-10-06: GotobiBot live fills vs IC ticks and the cTrader backtest. Execution matches; the fix-time short pays latency

| tested | verdict | detail |
|---|---|---|
| The 24 real Gotobi legs of 30/09 and 05/10 (12 live, 12 demo) against IC ticks at the fill second and against backtest jobs #391-#393 on the same days; plus 26 decoys | **execution matches the backtest**: entry slippage 0.0 pip (live median), commission identical, live and demo feeds identical. One real gap: the short leg at the 00:55 fix fills after the long's close, 11/12 legs worse than the backtest, mean -0.45 pip live / -1.23 demo (n 12, not significant); 2 live short orders failed with TechnicalError and waited 30 s. The edge itself needs ~100 gotobi days to test live | [gotobi_live_fills_2026-10-06.md](results/portfolio/gotobi_live_fills_2026-10-06.md) |

## 2026-10-06: round 22, triage of all residual ideas. No candidate; the search paused here at the user's request

| tested | verdict | detail |
|---|---|---|
| R: every open idea of rounds 3-21 (~190) triaged; 11 survivors need no user decision, none reaching power 3 at full size; 4 declared and tested (FOMC-cycle even weeks, low-volume FX reversal, Wednesday-rollover carry, 10-year auction concession), 13 cells | **none**; the residual list that needs no user decision is exhausted | [round22_residual_2026-10-06.md](results/portfolio/round22_residual_2026-10-06.md), [TRIAGE_R.md](results/portfolio/round22_residual/TRIAGE_R.md) |

Standing after rounds 12-22: C3 is the only LIVE algorithm. Two weak DEMO candidates (E1 EURUSD 11:00-13:00 London
short; gold into the COMEX settlement on big days) await the user; one durable but rare effect (the dollar falls on
FOMC days, 8 a year) is below the bars. The binding constraint is IC's cost and the decay of post-hoc picks; the
remaining routes all need a user decision (see round 16's STREAM_X and round 22's TRIAGE_R).

## 2026-10-06: round 21, the FOMC-day dollar premium on other US-policy events. No candidate

| tested | verdict | detail |
|---|---|---|
| U: round 20's rule A4 unchanged on FOMC minutes, Chair testimony, Jackson Hole, Treasury refunding statements (pooled and alone) and gold over the same windows, 8 declared cells, 2004-24 official calendars | **none**: the non-FOMC events pooled are -3.0 / +6.9 / -11.6 bp (PRE / IS / VAL); pooling with FOMC only dilutes the FOMC days. The premium belongs to the FOMC decision alone, as the literature says | [round21_fed_events_2026-10-06.md](results/portfolio/round21_fed_events_2026-10-06.md) |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates.

## 2026-10-06: round 20, declared-only: central-bank-day carry and index expiry settlements. No candidate

| tested | verdict | detail |
|---|---|---|
| F: Mueller, Tahbaz-Salehi & Vedolin (2017) FOMC-day currency premium, 7 declared cells (+ pooled 8 banks, BoJ) | the dollar falls on FOMC days in every era (A4: PRE +17.7 / IS net +21.6 t 1.90 / VAL +31.6 t 2.40; pooled 2004-24 t 3.25) but **fails DEMO on IS t** with 8 events a year; the carry spread itself and other banks: none | [round20_declared2_2026-10-06.md](results/portfolio/round20_declared2_2026-10-06.md) |
| G: DAX / FTSE / EURO STOXX 50 / CAC / HSI expiry settlement auctions, 64 declared cells | **none**: four quarterly cells meet the DEMO numbers but are one effect and fail the random-entry control (the whole quarterly-expiry session falls, carried by 2020-23) | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates.

## 2026-10-06: round 19, declared-only hypotheses. No candidate

| tested | verdict | detail |
|---|---|---|
| H: E1's mechanism (home currency weakens into its own fix) for CAD, AUD, NZD, GBP, CHF, CNH/CNY, 23 declared cells with official fix-time histories | does not generalise (wrong or no sign in CAD/AUD/NZD/GBP/CHF); exception: USDCNH rises into the CFETS 16:30 Beijing close (+1.22 bp t 4.57 IS / +1.68 t 4.08 VAL, absent on mainland holidays) but nets +0.19 / +0.66 at IC's ~1 bp: below DEMO | [round19_declared_2026-10-06.md](results/portfolio/round19_declared_2026-10-06.md) |
| T: second literature pass, 34 papers, 7 untested families, 63 declared cells (pre-announcement drift, dash for cash, Monday reversal, Tuesday blues, Bitcoin Monday, crude weekdays, FX weekend-gap fade) | **none** beats chance; the weekend-gap fade was real in 2004-15 and is gone since publication | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates.

## 2026-10-06: round 18, decay forensics and calendar day-of-month clocks. No candidate

| tested | verdict | detail |
|---|---|---|
| A: yearly effect series and trend for 49 effects (STREAM_X table + C3), forecasts for 2025-26, comparison with the published HOLD retention of the 6 registered rules | trends cannot separate decay from noise and did not predict HOLD retention; **how the rule was found did**: declared / literature / PRE-sided rules kept 0.65-1.03 of VAL in HOLD (C3, gold big days, E1), post-hoc picks with VAL in view 0.19-0.31 (J5c, I, M1). 2024 was a common low year (Sydney V lowest since 2016). C3 is the only effect flat on every reading | [round18_decay_dom_2026-10-06.md](results/portfolio/round18_decay_dom_2026-10-06.md) |
| B: calendar day-of-month (1-31, n-th last, payment-day convention) x clock windows, 631,915 cells, PRE discovery | **none**: calendar-day cells are noise like business-day cells; information only: USD up in the European morning on the 15th (post hoc, within chance) | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates
(a demo alone would need 5-24 years to reach t 2 at IC's costs).

## 2026-10-06: round 17, quote-based order flow and big-day momentum in European indices. No candidate

| tested | verdict | detail |
|---|---|---|
| Y: signed quote flow (price-only OFI, tick rule, quote intensity) from IC ticks predicting 1-60 min, 7 symbols | **none**: unconditional flow predicts reversal (the own-return reversal); the return-orthogonal part continues at 0.01-0.06 bp per z (1/20 of cost). A post-hoc US30 morning top-0.1 % cell (IS t 2.11, 10 VAL trades) is within chance for ~1,600 cells and not registered | [round17_microstructure_2026-10-06.md](results/portfolio/round17_microstructure_2026-10-06.md) |
| Z: intraday momentum on top-decile move days, European index CFDs (DE40 information only), US30/USTEC comparison, 92 + 12 cells | **none**: +1-2 bp top-decile mid against ~3.7 bp cost; DE40's round-13 slope does not replicate; the US big-day continuation is March-April 2020 | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates.

## 2026-10-06: round 16, income conversion flows and the value of pending decisions. No candidate

| tested | verdict | detail |
|---|---|---|
| W: cross-border income conversion with published dates (Swiss big-3 dividends, Japan June/December, euro-area May, Australian seasons, US refunding coupons, OAT/Bund/JGB redemptions), 18 + 2 cells, PRE where possible | **none**: best net IS t 1.52 (EUR into the fix in May, stronger in December: not dividends); published flows are a few bp in a 60-450 bp 1-5-day block | [round16_income_flows_2026-10-06.md](results/portfolio/round16_income_flows_2026-10-06.md) |
| X: decision value from the ~45 effects real at mid in rounds 3-15 (no new returns) | at IC's costs 0 LIVE-like rows; without the FX commission or at a low-cost venue 2-3 rows (ECB pre-fix slot, Sydney V legs), but only if they stop decaying (Sydney kept 0.31 of VAL in HOLD, needs ~0.7). Cheapest way to price that: Dukascopy AUD/NZD (and XAU/XAG) M1 2004-15, then data after 2026-09-24 | same, [STREAM_X.md](results/portfolio/round16_income_flows/STREAM_X.md) |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates.

## 2026-10-06: round 15, very short windows (1-10 min) at benchmark minutes. No candidate

| tested | verdict | detail |
|---|---|---|
| S: FX, 85,225 cells of 1-10 min around 8 benchmark minutes, PRE 2004-15 discovery, IS/VAL confirmation | **none**: PRE selection at minute scale is worse than chance because the ECB V moved ~16 min earlier at the end of 2015 (in the market, both data sources agree); the best every-weekday window's IS mid is 0.88 bp (EURUSD), under the 0.8-1.2 bp LIVE line. Two post-hoc DEMO-number drafts (Friday ECB pre-fix slot inside E1; GBPJPY month-end 10:28 NY) not registered | [round15_short_windows_2026-10-06.md](results/portfolio/round15_short_windows_2026-10-06.md) |
| V: metals, AUD/NZD, index CFDs, XTI, 25,704 cells around 24 benchmark minutes, sides from written mechanisms | **none**: 141 predicted cells confirmed in VAL (chance 23), all 0.3-2.7 bp against 1-7 bp costs. Information only: silver falls into the 12:00 LBMA auction (+2.7 bp, t 8-9 in IS and VAL, 9/9 years) and gold into the 15:00 one; at IC's costs, at or below zero | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates
awaiting the user.

## 2026-10-06: round 14, books of stable clock effects and conditions that double them. No candidate

| tested | verdict | detail |
|---|---|---|
| Q: one algorithm trading a book of stable clock legs chosen on PRE + IS (12 books, 1-9 legs) | **none**: the best book (3 legs) has VAL power 2.01; the 9-leg book would clear LIVE if its legs kept their IS Sharpe (0.158-0.170 per day), but 5 of 9 keep under 20 % of their IS net in VAL (book VAL Sharpe 0.050). The primary book is E1 (not registered) | [round14_books_2026-10-06.md](results/portfolio/round14_books_2026-10-06.md) |
| R: mechanism-derived conditions for E1 and four other stable clock effects, 96 cells | **none**: selectors scale E1 1.5-1.7x in IS/VAL (1.1x in PRE) but cut the trades, so power stays ~2; not beyond chance as a family. E1 reverses on TARGET2 closing days (no ECB fix; -3.9 bp, t -2.7, 2004-24), which supports its ECB-fix mechanism | same |

Standing: unchanged. C3 is the only LIVE algorithm; E1 and the gold settlement big-day rule are weak DEMO candidates
awaiting the user.

## 2026-10-06: round 13, structural flows that should not decay. One weak DEMO candidate

| tested | verdict | detail |
|---|---|---|
| M: stability-first scan, 270,086 FX/gold clock and calendar cells, discovery on PRE 2004-15 (side fixed there), confirmation on IS and VAL | stable effects exist beyond chance (139 of 500 PRE cells confirm in IS, chance 29) but shrink to a fifth of their PRE size and are mostly below cost. **E1, short EURUSD 11:00-13:00 London every weekday**, met DEMO (IS +1.17 bp t 3.29, VAL +1.35 t 2.46, power 1.8-1.9), registered, **HOLD +0.64 (t 0.99), both fills +1 min 0.00: DEMO candidate**, weak | [round13_structural_2026-10-06.md](results/portfolio/round13_structural_2026-10-06.md), [PREREG_M](results/portfolio/round13_structural/PREREG_M_eurusd_midday.md) |
| N: structural calendars (US tax days, Treasury coupon/bill/refunding settlements, bond-index month-end extension, fiscal-year ends, quarter-end funding, Chinese tax deadline), 58 cells, PRE where possible | **none**: best registered cell (US30 the day after a big coupon settlement, IS t 2.68) is negative in VAL; no dose-response to settlement size; no mechanism keeps its sign over PRE, IS and VAL | same |
| P: round 12's gold big-day settlement rule on XTI/XBR/XNG and ten index closes, 25 cells | **none**: the index big-day scale-up in IS is March-April 2020; in VAL US indices reverse into the close on big days; gold's dose shape is not found elsewhere | same |

Standing: C3 remains the only LIVE algorithm. Two weak DEMO candidates await the user (E1 EURUSD midday, L4-G-d gold
settlement big days); no cBots written.

## 2026-10-06: round 12, hedge flows, other executions, flow-size conditions, literature 2018-26. One weak DEMO candidate

| tested | verdict | detail |
|---|---|---|
| I: month-end equity-hedge flows at the WM/R fix, USD side from month-to-date equity returns (Melvin & Prins 2015); 72 mid + 27 basket cells | the paper's into-fix move is absent; the post-fix reversal on large US months met DEMO on IS/VAL (+6.77 bp per trade t 3.79 / +1.68 t 0.84), registered and **failed HOLD: -0.23 bp (t -0.08)** | [round12_flows_execution_2026-10-06.md](results/portfolio/round12_flows_execution_2026-10-06.md), [PREREG_I](results/portfolio/round12_flows_execution/PREREG_I_month_end_post_fix_usd.md) |
| J: other executions of the sub-cost effects (spread-timed minutes/seconds, passive limits, several flows in one trade, lot by forecast, cheaper twin), 70 cells + post hoc | none clears LIVE: SGE, Sydney post-leg and ECB would need a round trip below the 0.6 bp commission; passive fills are adversely selected. The Sydney V's cost is a clash with IC's post-rollover hour in the northern winter; AUDUSD outside that hour (post hoc) met DEMO (+0.44 t 2.54 / +0.76 t 3.77), registered and **failed HOLD: -0.25 bp (t -0.99)**, the dip shrank to +0.48 | same, [PREREG_J](results/portfolio/round12_flows_execution/PREREG_J_sydney_aud_offroll.md) |
| K: literature 2018-2026 (30 papers), 6 untested families, 123 cells (FX momentum into closes, 0DTE opening range, Deribit / CME BTC expiries, crude and metals intraday momentum) | **none**: no family beats chance on its registered side; closest lead (fade BTC 07-08 UTC on Deribit-expiry Fridays) is killed by 2018-21 BTC costs | same |
| L: flow-size conditions from each mechanism for the strong sub-cost flows, 42 cells | SGE 2x, Sydney 1.7x, ECB wrong sign at month-end; **gold momentum into the COMEX settlement on top-decile move days** met DEMO (+3.48 t 3.19 / +2.11 t 1.70), registered, **HOLD +1.68 bp (t 0.37, 46 trades): DEMO candidate**, weak (three trades decide the mean; silver flips) | same, [PREREG_L](results/portfolio/round12_flows_execution/PREREG_L_gold_settlement_bigday.md) |

Standing: C3 remains the only algorithm that has passed a LIVE holdout. One DEMO candidate (gold settlement big days)
awaits the user's decision on a demo; no cBot written. All three registered candidates decayed from IS to VAL to HOLD.

## 2026-10-06: round 11, multi-day event drift, 1-5 day cross-sections, full index intraday scan. No candidate

| tested | verdict | detail |
|---|---|---|
| F: drift 1-5 days after central-bank decisions and macro surprises (delayed overshooting; 1,877 CB events, 15 non-US release types, US CPI/NFP), entry >= 90 min after the event | **none**: best IS net t 0.64 (F1 5-day continuation +3.0 / +10.2 bp). The 1-day drift was real in 2004-15 (+7.4 bp, t 3.04) and is gone since 2016 | [round11_multiday_cross_section_index_scan_2026-10-06.md](results/portfolio/round11_multiday_cross_section_index_scan_2026-10-06.md), [round10_new_directions/](results/portfolio/round10_new_directions/) (STREAM_F/G/H) |
| G: cross-sectional momentum / reversal at 1-5 days across 8 currencies, 8 indices, 6 commodities (+ dispersion conditioning, Nagel reversal) | **none**: no predictability at mid in IS, VAL or PRE (dollar-neutral currency book \|t\| <= 1.51); every family's best t below chance | same |
| H: every 15 / 60-min window of the commission-free index CFDs (15,913 cells) + 16 mechanism-first index windows (MOC imbalance, 10:00 ET data, closing auctions, SOQ) | **none**: 0 cells clear the frontier; max \|t_IS\| 4.94 vs null p95 4.51, net < 0. Post-hoc lead, not registrable: short US30 15:45-16:00 ET on FOMC days (+6.7 / +9.5 bp, ~8 a year, power ~1.1) | same |

Standing: unchanged. C3 remains the only algorithm that has passed. The search stopped after this round at the user's
request.

## 2026-10-06: round 10, new directions on the existing data. No candidate (LIVE or DEMO)

| tested | verdict | detail |
|---|---|---|
| A: Asian benchmarks and Chinese venue sessions with venue-holiday placebos (SGE gold auctions, SHFE/INE opens and closes, Platts oil windows, Asian FX fixings, Nikkei SQ); 223 cells + 26 post hoc | **none**: 0 cells net > 0 in IS and VAL on the registered side. The SGE 10:15 Beijing auction moves gold +0.93 / +0.72 bp (t 7.9 / 4.5, 9/9 years, absent on Chinese holidays) but the other way from the registered V and below its 1.05-1.6 bp cost. A7 (post hoc, short gold on Chinese holidays) met the DEMO numbers (net t 3.3 / 2.8) and **failed its pre-written 2004-15 check** (t -3.3): a holiday-block artefact | [round10_new_directions_2026-10-06.md](results/portfolio/round10_new_directions_2026-10-06.md), [round10_new_directions/](results/portfolio/round10_new_directions/) |
| B: central-bank decisions (8 banks, 1,877 events 2004-24) and home-market holidays, pooled | **none**: no pre-decision drift outside the Fed, no post-decision continuation (net +0.4 / +0.0 bp), home-holiday asymmetry real in 2004-21 but gone in VAL and ~3 bp; fading the first 5 min of press conferences has one sign in three eras but is post hoc with IS t 1.55 | same |
| C: one cost-gated FX book combining the effects real at mid (residual reversal, dollar catch-up, fixing V, home hours, Wednesday carry, Sydney V, same-slot periodicity) | **none**: best IS t 1.65; the summed forecast stays under the 0.6 bp commission outside the Sydney open, and the edge vanishes at zero-spread minutes; break-even commission ~0.15 bp | same |
| D: feasibility frontier; sub-minute lead-lag on ticks; FX and index option pinning; the European-open overnight drift (Boyarchenko et al. 2023) | **none**. Frontier: one trade a day needs ~1.4 bp gross per 15 min in EURUSD/USDJPY, 2.6 in US30, 2.7 in gold; tick lead-lag +0.1..0.4 bp; no pinning (\|t\| <= 1.9); the drift is gone after 2019 | same |
| E: fixing flows on volatile / active days; follow-through after 16 types of non-US macro releases (~130 a year) | **none**: flows grow ~1.5x on volatile days but spreads grow too; EURUSD rises into the ECB fix (opposite of the registered side; flipped, exactly at cost); no follow-through after non-US data (best IS t 1.32 vs null 2.61) | same |

Standing: unchanged. C3 remains the only algorithm that has passed. Every real flow found in ten rounds sits below
the feasibility line for its symbol except gotobi. What could change it needs a decision: more IC symbols (crosses,
EM pairs, softs), new data after 2026-09-24, or a cost structure without the 0.6 bp FX commission floor.

## 2026-10-05: round 9, what a $100k account changes. No new algorithm; C3 sizing at $100k and at a prop firm

| tested | verdict | detail |
|---|---|---|
| I: the IC cTrader account at $100k with relaxed limits (hold weeks-months, many positions, capital-based lots). I-A: C3 at size (lots, spreads at its minutes, slippage, mark-to-market DD, bootstrap). I-B: macro fair value (gold vs TIPS, USDJPY vs rate spread, commodity FX), COT contrarian, buying the S&P 500 after a drawdown or VIX > 30, carry on IC's net swap, a multi-strategy book | **C3 scales cleanly**: 1 % per leg = 1.4-2.5 lots, ordinary spreads at 18:00 / 00:55 / 02:55 UTC, floating losses add ~10 % to the DD. Risk per leg for a 10 / 20 / 30 % DD tolerance (rule fixed before computing, halved edge): 0.375 / 0.75 / 1.5 %; at 0.75 % ~+15-17 %/yr, MTM max DD 5.3 %. **I-B: none passes** (~237 cells, max \|t\| 2.84 = chance); closest is VIX > 30 (net > 0 in every era, NW t <= 1.91, DD 47 %) | [round9_capital_100k_2026-10-05.md](results/portfolio/round9_capital_100k_2026-10-05.md) (I), [round9_capital_100k/](results/portfolio/round9_capital_100k/) |
| O: S&P 500 index options, the volatility risk premium (16 CBOE strategy indices 1988-2024, retail XSP/SPX costs, 24 timing overlays, put spreads, sizing) | **the premium is real, the alpha is not**: VIX exceeds next-30-day realised vol by 4.1 points (t 15), but PUT's alpha over SPX is +1.5 %/yr (t 1.3) and -3.3 %/yr in 2016-21; every short-vol index lost alpha after 2015 (WPUT -7.2, t -3.1); no overlay survives the checks; real-price put spreads have negative alpha. One XSP put a month = about 35 % SPX + 65 % T-bills | same (O) |
| P: a $100k prop-firm account on cTrader running C3 (rules of 7+ firms, bootstrap of the evaluation and 12 funded months, an account-level daily-loss guard, a no-edge baseline) | **positive EV on paper**: FTMO 2-Step Swing, 1 % per leg with the guard: P(pass) 0.97, median 238 days, E payouts $16.4k in year 1 for a €540 fee (no edge $1.1k, half edge P 0.72 / EV $7.0k). Without the guard, the daily-loss limit fails 20 % of evaluations at 1 %. Firm credit risk is the main risk; Vietnam eligibility for FTMO/The5ers unchecked | same (P) |

Standing: unchanged. C3 remains the only algorithm that has passed. A $100k account would change C3's size and
where it can run, not the search; running it on own capital and on a prop account would be the same bet twice. The
$100k is a research premise (the user: research only, not a real account), so nothing was deployed.

## 2026-10-05: round 8, how the symbols affect each other. No candidate

| tested | verdict | detail |
|---|---|---|
| Four streams on one M1 panel of the 26 symbols (2016-2024, HOLD cut out). L: intraday lead-lag (26 x 26 at 1-60 min, 10 named economic leads, dynamic leads). S: shock spillover (large fast moves -> linked markets, beta-gap catch-up, safe havens, 08:30 New York data). R: relative value (return-spread pairs, Avellaneda-Lee PCA residuals, currency strength meter, commodity-currency fair value, index dispersion). X: literature map (38 papers), cross-session and risk-regime spillovers, crypto -> indices, weekly oil -> equities | **none reached a pre-registration, HOLD not opened**. The lead-lag structure is real (robust matrix: 1,248 cells with \|t\| >= 4 vs ~2 by chance, IS/VAL t corr 0.41) but sits inside the first minute: after a 1-minute delay it is 0.01-0.2 bp per sd against 0.7-7 bp of cost. Shocks diffuse slowly into JP225/HK50/BTC/ETH (1-7 bp vs 2.5-8 bp). FX residual reversal is real in 2004-15, IS and VAL (+1.2..+2.7 bp vs 1.2-1.5 bp). Pairs outside FX pay two legs (4-120 bp) for less. Best cell: US30 continuing after 08:30 New York data, power 2.6 / 1.4 (bar 3), side post hoc. Weekly oil -> US500 fade (Driesprong et al. 2008) is -54 bp per sd in VAL (t -3.2), but its IS t -2.8 came from dropping weeks without quotes; with proper fills IS is -18 (t -1.2) | [round8_inter_symbol_2026-10-05.md](results/portfolio/round8_inter_symbol_2026-10-05.md), [round8_hypotheses/](results/portfolio/round8_hypotheses/) |

Standing: unchanged. What the symbols do to each other is real but either priced within a minute or smaller than
IC's spread, which is widest exactly where quotes lag. C3 remains the only algorithm that has passed.

## 2026-10-05: round 7, new data and relaxed limits. No new algorithm; C3 passes a 2004-2015 era

| tested | verdict | detail |
|---|---|---|
| A: Dukascopy M1 2004-2015 (PRE, never used in this repo; validated against IC on 2016 days) as a fourth era for the registered C3 and M1 rules, unchanged engine, IC 2016-17 spread profile on Dukascopy's bid | **C3 passes** its registered bar: 5,184 legs, R +0.038, day-clustered t 4.8, 10/12 years, every pair > 0 (EURJPY weakest, +0.019), +0.030 at spread x1.5; the edge sits at the 00:55 fix (pivot at 01:05: +0.010), holiday long legs lose again. **M1 fails again**: R +0.020, day-clustered t 0.64, beats 64 % of random days | [round7_new_data_2026-10-05.md](results/portfolio/round7_new_data_2026-10-05.md) (A), [round7_pre_code/](results/portfolio/round7_pre_code/) |
| B: seven IC symbols no round had used (ES35, F40, IT40, STOXX50, US2000, USDCNH; DOGEUSD's cache is empty): large-to-small-cap and core-to-periphery lead-lag, European close and expiry, PBOC fix surprise (official CFETS series), CNH home hours and month-end | none: best gross power 1.9 (needs ~3). The CFDs follow futures (no lead-lag); the fix surprise is priced in 6 minutes; USDCNH Asian-hours drift is real (+1.2 / +2.0 bp) but the size of its ~1 bp cost | same (B) |
| C: literature 2010-2026 (38 mechanisms, 15 not yet tested) and 7 screens: adaptive same-slot periodicity (Heston, Korajczyk & Sadka), quarter-hour openings, US500 expiry pinning, stablecoin issuance, PBOC countercyclical reversal, ISM pre-drift | none: best power 1.3. Adaptive periodicity is real in FX (JPY crosses) but 0.02-0.3 bp per slot against 0.3-3 bp of cost | same (C) |
| D: relaxed limits (hold <= ~3 months, <= 10 positions): 24 published multi-week rules (carry, dollar carry, FX momentum/value, TSMOM, index/commodity momentum) on 2000-2024 daily data at IC's costs | none: IC's financing markup costs 1.4-4.5 %/yr (TSMOM 12 m gross Sharpe 0.60 -> net 0.16); best net 0.20-0.23 at t <= 1.2; after 2015 the premia are ~0 even gross; HOLD (expected t ~1.3 x annual Sharpe) can only falsify slow premia | same (D) |

Standing: unchanged. C3 is the only algorithm that has passed, now over four eras (2004-15, 2016-21, 2022-24,
2025-26). Intraday flows lose to IC's spread and commission, multi-week premia to its financing markup.

## 2026-10-04: round 6, commodity settlement flows, inventory reports, passive execution. No candidate

| tested | verdict | detail |
|---|---|---|
| S1: momentum into the futures settlement (leveraged-ETF rebalancing) in XTI/XBR/XNG/XAU/XAG, XPT as the control; S2: follow-through after the EIA crude / gas reports; S3: the API report; S4: buying the 10:00-Sydney dip with a limit order (tick level); S5: fading 5-minute shocks in US30/USTEC by VIX regime. IS/VAL only, HOLD cut at load | **none reached a pre-registration, HOLD not opened**. The settlement flow is real where leveraged ETFs exist (gold slope t +6.8 / +2.6, silver +8.2 / **-4.3**, platinum control -3.9 / -2.9) but 0.3-2.4 bp against 1-4 bp of cost. EIA follow-through has the right sign in all three energies (XTI +18 / +16 bp to 14:30) but t <= 1.3 at ~50 events a year: expected HOLD t ~0.7 even if real. The API effect also shows on days without a report. Passive buys fill on 85-93 % of days but 0/48 cells net > 0. No index reversal repeats in VAL. Also found: the engine charges metals commission at a fixed $/oz from 2026 prices, ~2 bp instead of 0.6 bp for gold/silver in 2016-21; no verdict changes | [round6_commodity_flows_2026-10-04.md](results/portfolio/round6_commodity_flows_2026-10-04.md) |

Standing: unchanged. C3 is the only algorithm that has passed a holdout. The round's power table says a candidate needs a
per-trade Sharpe of at least 3 / sqrt(its HOLD trade count) before its holdout is worth spending.

## 2026-09-30: cost of camouflaging GotobiBot from the broker

| tested | verdict | detail |
|---|---|---|
| GotobiBot cTrader backtest 2024-01..2026-09, 3 pairs, $200 risk: decoy legs on plain weekdays (2 per real leg, half at the real lot and half at 0.01 lot, 0.5 x ATR virtual stop), a broker stop at 0.8-1.0x or 0.6-1.0x the real stop, and the long entry jittered by ±60 min | **decoys at the real lot cost ~all the edge**: -$7.8 per decoy, basket net $11,738 → $1,991 (0.8-1.0x). Broker-visible win rate 55.7 % → 38.6 %; summed max DD $2,403 → $4,288. Small-lot decoys cost -$0.20 each. The tighter broker stop takes -5.9 % (0.8-1.0x) or -12.0 % (0.6-1.0x) of the real legs' net. **Chosen: 0.8-1.0x stop + jitter + all decoys at 0.01 lot**: net $10,526 (-10.3 %), visible win rate 38.6 %, summed max DD $2,580 (+7 %) | [gotobi_camouflage_2026-09-30.md](results/portfolio/gotobi_camouflage_2026-09-30.md) (Vietnamese) |

## 2026-09-29: Gotobi on Japanese holidays

| tested | verdict | detail |
|---|---|---|
| GotobiBot cTrader backtest 2016-2026 ($50 risk) split by whether the gotobi day had a Tokyo fix (Japanese public holidays + bank holidays 31/12, 2/1, 3/1; `tools/gotobi_holidays.py`) | **holiday days lose**: 45 days, R -0.066 (t -3.4), -$863, against +0.056 (t +9.6) on the other 727. The long leg carries it (R -0.153). Negative in IS, VAL and HOLD. This contradicts the v2 caveat's "~0 effect". The presets now skip them through 2027 (`GOTOBI_SKIP_DATES`) | [gotobi_jp_holidays_2026-09-29.md](results/portfolio/gotobi_jp_holidays_2026-09-29.md) |

## 2026-09-28: C3 sizing and trade management, C1 position cap. No rule improves C3; C1 keeps cap 3

Questions asked while planning a compounding version of GotobiBot. Sizing re-weights the existing C3 trade lists (as
round 5 did); the trade-management rules ran on IS/VAL only, so the holdout is still unseen for them.

| tested | verdict | detail |
|---|---|---|
| C3 at 3 % per trade: risk as a share of the current balance (compounding) vs of the starting balance (fixed $); one pair at a time vs the three-pair basket | sizing changes the $ path, not the edge: over 2016-2026 compounding makes CAGR +60 % / DD 34 % vs +20 % / DD 16 % fixed (research engine), much closer over the 21-month holdout. The pairs' R correlate +0.68..+0.84, so 3 % per pair is ~9 % per gotobi event; one pair at 3 % does no better than the basket at 1 % per pair, and the best pair changes between eras | [c3_sizing_and_trade_management_2026-09-28.md](results/portfolio/c3_sizing_and_trade_management_2026-09-28.md) (sections 1-2) |
| C3 trade management on IS/VAL: averaging down (1 or 2 adds, 1-2-4), pyramiding into winners, holding losing legs to break-even with and without the stop | **rejected**, all of them. An add has mean R about 0 either way (day-clustered \|t\| <= 1.2); averaging down raises DD to 48-59 % at 3 % compounding and 1-2-4 multiplies it by 6-10 at a fixed risk. Holding losers lifts the win rate to 67-81 % but not mean R, skips 20-24 % of legs, and without a stop loses up to 7.7 R on one leg. C3's edge is in its fixed entry and exit times | same (sections 3-4) |
| C1 (CryptoDonchianBot) with MaxPositions 1, 2, 4, 5 and no cap instead of 3, pre-planned verdict rule; return / mark-to-market DD on IS/VAL, t clustered by stacking episode, 4 bar phases | **keep 3**. Cap 1 had the best IS/VAL return / DD (8.40 / 4.82 vs 6.92 / 4.02) but beat cap 3 at only 2 of 4 bar phases, and the 2nd-3rd stacked units earn about what the first does (IS+VAL +0.27 / +0.27 / +0.21 R). The cap scales $, drawdown and peak risk together (cap 1: about half the $ and DD, peak risk 400 vs 1,175 $); caps above 3 are worse. HOLD mean R -0.044..+0.008 at every cap | [crypto_donchian_max_positions_2026-09-28.md](results/portfolio/crypto_donchian_max_positions_2026-09-28.md) |

Standing: unchanged. C3 runs as specified, one leg per pair at a time, and the choice left is its risk per trade.
C1 keeps MaxPositions 3; a lower cap is a way to run its forward test with less risk, not a better rule.

## 2026-09-27: swing lab on 26 symbols, 2016-2026. C3 Gotobi JPY basket passes its holdout

Constraints for every test this day: a lot never depends on account capital (default $ risk x 0.5-2x), a position is
held 5 days at most, and a bot holds 3 positions at most. Eras: IS 2016-21, VAL 2022-24, HOLD 2025-01..2026-09.

| tested | verdict | detail |
|---|---|---|
| Swing lab v1: one portfolio-wide bot, cap 3, SL/TP exits only, 9 families, ~95 configs (`scan/portfolio.py`, removed; see the note at the end) | no strategy cleared the pre-registered bar. Superseded by v2 | [swing_lab_2026-09-27.md](results/portfolio/swing_lab_2026-09-27.md), [full_run_2026-09-27.md](results/portfolio/full_run_2026-09-27.md) |
| R-series: the old lab's positive-but-rejected strategies (TOM, K2, VB1, LC1, GF1, MEF, OD1, N2-GOTOBI, three D1 bank cells, plus N3-IMOM as an addendum), rerun with unchanged code on 2016-2022, which is out of sample for all of them | only N2-GOTOBI passed: n 1002, +0.078R, t +5.7, 7/7 years, beat 10/10 random seeds. Every other strategy failed | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) (R-series) |
| C1 Crypto Donchian H4 (BTCUSD, ETHUSD), pre-registered | **failed** at HOLD: mean R -0.025. Net was +$2,859 only because the lot multiplier sized up the winners. IS +0.276, VAL +0.227 | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md), [swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md) |
| C3 Gotobi JPY basket (USDJPY + EURJPY + GBPJPY, one bot), pre-registered | **passed**: HOLD n 738, R +0.042, t 2.9, all three pairs net > 0. IS +0.043 (t 5.4), VAL +0.041 (t 3.7) | same |
| C4 Gotobi USDJPY with day-type lots, pre-registered | passed the bar, but the sizing is not confirmed: the day-type lots made less than 1x lots at HOLD (+$757 vs +$940) | same |
| Other v2 hypotheses on IS/VAL: the Connors RSI(2) family, turn of the month, time-series momentum, Donchian outside crypto, pairs, FX carry, home-hours depreciation, fixing windows | none worked | [swing_lab_v2_2026-09-27.md](results/portfolio/swing_lab_v2_2026-09-27.md) ("What was tried") |
| `cBot/GotobiBot.cs` (C3) built and backtested with cTrader on IC ticks, 2016-2026 | 33/33 pair-years net positive, 4,574 trades, R +0.049, basket max DD $512 (10.2 R). Also fixed an entry on a stale Monday quote | [gotobi_cbot_backtest_2026-09-27.md](results/portfolio/gotobi_cbot_backtest_2026-09-27.md) |
| `cBot/CryptoDonchianBot.cs` (C1), cTrader backtest 2018-2026 | matches the research engine trade for trade. HOLD R is -0.027 (research: -0.025), so C1 stays a forward test only | [crypto_donchian_cbot_2026-09-27.md](results/portfolio/crypto_donchian_cbot_2026-09-27.md) |
| C1 vs the weekend closure: IC crypto was closed at weekends until 2024-04, so IS/VAL ran on a 5-day market and HOLD on a 24/7 one. C1 rerun on 2024-05..2026-09 with the old closure cut out | **not supported**: pooled mean R +0.042 -> +0.053 (+0.011; bar was +0.10), +0.000..+0.011 at the other bar phases, BTCUSD and ETHUSD in opposite directions. The 24/7 switch does not explain the weak HOLD | [crypto_donchian_weekend_2026-09-27.md](results/portfolio/crypto_donchian_weekend_2026-09-27.md) |
| GotobiBot, VPS Backtest page jobs #366-#374 (3 pairs x $50/$100/$200 risk, 2025-10..2026-09) | all 9 jobs profitable (+0.068R per trade at $50). This is not new evidence, since the period falls inside HOLD. Found two simulation bugs around market closures: a stale Sunday quote, and the 25/12 gotobi | [gotobi_backtest_366-374_2026-09-27.md](results/portfolio/gotobi_backtest_366-374_2026-09-27.md) (Vietnamese) |
| Code provenance of the swing v2 holdouts: the registered code hashes did not match git | the registered sources were rebuilt from the edit log and hash exactly as registered. C1 ran on the registered code, and C3 on its rule as registered. C3/C4 had not recorded their own hashes (a process gap, now `tools/prereg_hashes.py`). A re-run after the folder move gives identical numbers. Verdicts unchanged | [prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) (addendum), [prereg_swing_v2_code/](results/portfolio/prereg_swing_v2_code/) |
| Round 3: new mechanisms other than gotobi and crypto trend (fix and settlement-date flows, month-end, oil roll days, the Wednesday triple rollover, announcement / night / weekend premia, liquidity provision, lead-lag; ~40 hypotheses plus a 90,168-cell calendar x window scan) | none passed. The one registered candidate, M1 (buy USD vs JPY, CHF, EUR 10:00-13:00 UTC on the 3rd-to-last weekday), had IS R +0.123 and VAL +0.228 but **failed** HOLD: R +0.044, day-clustered t 0.7, random-day control 79 % | [flow_search_2026-09-27.md](results/portfolio/flow_search_2026-09-27.md), [prereg_month_end_usd_2026-09-27.md](results/portfolio/prereg_month_end_usd_2026-09-27.md) |
| Round 4: cheap-instrument flows, a minute-precise scan of 19 benchmark times (48,412 cells) and public external data (CFTC COT, Binance funding and order flow, dealer gamma / DIX, VIX term structure, Treasury auctions, 42 FRED/market features) | no candidate, so no HOLD opened. The strongest effect found, the AUD/NZD V-shape around the 10:00 Sydney open (NZDUSD -1.7 bp in the 15 min before, t -13 IS / -9 VAL), is smaller than its cost at executable prices; the external series add no edge that holds from IS to VAL | [flow_search_round4_2026-09-27.md](results/portfolio/flow_search_round4_2026-09-27.md) |
| Round 5: lots may depend on capital, max drawdown 60 % (other rules unchanged). Tested the swap-free equity premium with vol-managed capital-based exposure, a 1-2-4 averaging-down martingale on 26 symbols, and C3 compounded at f % risk per trade | no new algorithm: the equity premium is beta (vol timing beats shuffled leverage 20-53 % in IS, VAL Sharpe 0.2-0.3); the martingale has 73-85 % winners but t <= 1.4 and cycles losing 18-47 ATR units. C3 at 1-4 % risk: CAGR +19..+81 %, max DD 12-43 % (research engine); if its edge were half the estimate, DD stays under 60 % only up to about 3 % risk | [sizing_round5_2026-09-27.md](results/portfolio/sizing_round5_2026-09-27.md) |

Standing at the end of the day: C3 is the only algorithm that survived both out-of-sample years and a pre-registered
holdout. It is now a cBot, running on USDJPY/EURJPY/GBPJPY at $50 risk per trade on both the demo account and a live
account (VPS containers started 2026-09-27). C1 runs as a forward test on the demo account only ($100 risk per trade).
No other strategy is waiting for a demo.

## Before 2026-09-27: the strategy lab (removed)

On 2026-09-26 and 2026-09-25 the strategy lab (`lab/`, `scan/`, `flowrsi/`) tested the TMS+ORB, Judas Sweep and
FlowRSI bots, their canonical rebuilds, an open search on the M1 cache and a 62-strategy baseline over 22 symbols.
None of it passed a pre-registered bar. The one lead was N2-GOTOBI (USDJPY), which met five of the six conditions of
the 2026-09-26 refresh and became C3 above. On 2026-09-27 the three bots and the lab were removed from the repo with
their result files; they remain in git history before that removal, and the R-series verdict of
[prereg_swing_v2.md](results/portfolio/prereg_swing_v2.md) keeps the numbers it relies on.
