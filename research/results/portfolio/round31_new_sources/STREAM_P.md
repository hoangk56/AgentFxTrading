# Round 31, stream P: practitioner and community strategies (2026-10-27)

Brief: [BRIEF.md](BRIEF.md) row P; round13_structural/BRIEF.md for costs, fills, controls and bars. Every tested cell
was declared in [HYPOTHESES_P.md](HYPOTHESES_P.md) (file saved 18:28:01 UTC, `date -u`) before its first return
(18:29:05 UTC). HOLD was never loaded: IC M1 is cut at `ts < 2025-01-01` at load, the tick loader refuses any day
>= 2025-01-01, and Dukascopy is cut at 2016-01-01. Written 2026-10-27 ~18:40 UTC.

## Answer
**No LIVE or DEMO candidate; no PREREG_DRAFT.** The census of practitioner and community sources (about 1,550 entries
across Quantpedia, QuantConnect, GitHub, the mql5 code base and Market, GogoJungle, TradingView and Chinese repos)
reduces to two mechanisms with an economic basis that no round had tested. Both were declared (6 cells) and both fail:
- **P1, gold stop cascades beyond prior-day / prior-week / Asian-range extremes** (the design of 2026's best-selling
  mql5 gold EAs: resting buy/sell stops beyond visible extremes, follow the break). After IC's cost every gold cell
  is negative in IS (net -1.6 to -3.2 bp, t -0.8 to -4.2) and at or below zero in VAL. At mid the prior-day break
  does not continue in 2016-24 (IS -1.07 bp, VAL +0.60), although it did in 2004-15 (minute model, mid +2.78, t 4.38):
  **a practitioner breakout that has decayed**. The same engine on $50 levels finds round 27's cascade (IS net +4.9,
  VAL +2.5, every year > 0), so the engine can see a cascade where one exists.
- **P2, Friday position squaring** (trade against the week-to-date move from 13:00 to 20:00 UTC on Fridays, 11
  symbols). The sign is wrong: on the declared side, IS net -4.67 bp (t -1.77, top tercile), VAL -2.90, PRE 2004-15
  -2.45. The Friday afternoon continues the week slightly, as much as any other weekday.

**The census itself is the main result for later rounds.** About 520 entries are indicator or chart rules with no
economic basis. Of the rest, nearly everything maps onto a family that rounds 2-30 exhausted. Commercial EAs mostly
state no rule ("AI", "neural"). The two largest genres with a stated mechanism are already settled:
- Japan's early-morning scalpers (朝スキャ) are round 23 N1's reopen-gap fade: real at mid, 3-5 bp under IC's
  rollover spread.
- Gold breakout EAs are P1 here, plus the September lab's ORB / London breakout / ICT Judas tests.

## Sources (fetch log: scratchpad `r31/P/web/requests.log`; 58 requests 18:14-18:25 UTC, 53 HTTP 200, 5 HTTP 404; 2 web searches)
| source | what was read | coverage | unusable / notes |
|---|---|---|---|
| Quantpedia (quantpedia.com/strategies, screener SSR JSON) | all 82 free strategies (name, markets, rebalancing, keywords), 3 strategy pages read | 1970s-2024 papers | Premium pages not read (paywall). Blog: 1,176 post slugs, 219 matched topic keywords |
| QuantConnect Strategy Library (GitHub QuantConnect/Tutorials "04 Strategy Library") | 84 strategy names | | Forum: robots allow it, but there is no popularity listing; 1 web search |
| GitHub search API | topics forex / forex-trading / trading-strategies, EA, gold, pine; Chinese keywords 外汇 策略, 黄金 策略 | top 30 by stars each | many 2026 "MT5 dashboard" repos are spam-like |
| EA31337-strategies, freqtrade-strategies, je-suis-tm/quant-trading, joshyattridge/smart-money-concepts, vnpy_ctastrategy, paperswithbacktest/awesome-systematic-trading | strategy lists / READMEs | | academic replications in awesome-systematic-trading are multi-week factor papers |
| GeneralTradingSarl/mql4_experts (mirror of the mql5 MQL4 code base; Russian-born community) | 1,125 EA names, keyword-classified | 2005-2020s | names only; rules not read |
| mql5.com Market (MT5 Experts, default listing) | 70 top products listed, 20 product descriptions read | 2026 listing | robots allow product pages; live-signal deal pages are disallowed |
| mql5.com code base (MT5 experts, newest) | ~30 recent free EAs | 2026 | |
| GogoJungle (Japan's EA market) | FX system-trade page: genre keyword counts | 2026 | the ranking URL returned 404; `/markets/` is robots-disallowed |
| TradingView | 2 web searches only (Community Awards 2023; third-party lists) | | robots.txt disallows `/scripts/*`, so no script page was fetched |
| Not reachable or not allowed (from the brief's probe) | myfxbook, forexfactory, gaitame, reddit, DailyFX sentiment; OANDA API (403, account needed) | | positioning data only through stream J's TFX tables |

## Census (mechanism -> family map)
"Tested" cites the round. CP = chart pattern / indicator rule without an economic basis (dropped and counted).
"n/IC" = instrument or data not in IC's 26 symbols or the repo. "> 5 d" = horizon over the user's 5-day cap.

| # | source (URL) | mechanism / claimed rule | instrument | horizon | map |
|---|---|---|---|---|---|
| 1 | quantpedia.com/strategies (#0001, #0002, #0118, #0028) | asset-class TSMOM / momentum / value | multi-asset | monthly | tested r2, r7 D, r9 (> 5 d) |
| 2 | Quantpedia #0005, #0129, #0008, #0009 | FX carry, dollar carry, FX momentum, PPP value | FX | monthly | tested r7 D, r9 |
| 3 | Quantpedia #0021, #0022, #0281, #0664 | commodity momentum, term structure, skewness, return asymmetry | commodity futures | monthly | > 5 d; curves n/IC; r7 D |
| 4 | Quantpedia #0015, #0016, #0071 | country-index momentum / reversal, futures short-term reversal | indices, futures | weekly-3 y | tested r11 G (cross-section 1-5 d) |
| 5 | Quantpedia #0020, #0198, VIX blog posts | volatility risk premium, VIX term structure | options, VIX | monthly / daily | tested r4, r9 O |
| 6 | Quantpedia #0031, #0113, #0114 | sell in May, January barometer / effect | indices | months | > 5 d; r24 B (January) |
| 7 | Quantpedia #0041, #0419 | turn of the month, payday (401k contribution flows) | US indices | days | tested v2 TOM, r3, r13 N, r18 |
| 8 | Quantpedia #0075; blog: pre-ECB / BoE / BoJ / SNB drift | FOMC / pre-announcement drift | indices, FX | 1 day | tested r10 B, r20, r21 |
| 9 | Quantpedia #0083; blog: pre-holiday in commodities | pre-holiday drift | indices, commodities | 1 day | tested r10 (holidays, placebo) |
| 10 | Quantpedia #0102 | option-expiration week | US indices | week | tested r23 P5 |
| 11 | Quantpedia #0100; QC 100; paperswithbacktest gold-silver | WTI/Brent spread, gold/silver ratio reversion | XTI/XBR, XAU/XAG | days | tested r8 R (pairs) |
| 12 | Quantpedia #0096; QC 06 | crude oil predicts equities | indices | monthly | r8 lead-lag; > 5 d |
| 13 | Quantpedia #0050; QC 32 | Fed model; gold market timing | indices, gold | monthly | tested r9 (macro fair value) |
| 14 | Quantpedia #0140 | Ramadan effect | Muslim-country equities | month | n/IC |
| 15 | Quantpedia #0661 (Vojtko & Hanicová) | overnight long when SPY > MA20, VIX < MA, Brain sentiment > MA | US500 | overnight | needs paid BMS data; VIX part tested r4; overnight r3 |
| 16 | Quantpedia #0701, #0753; blog: BTC overnight / intraday / pre-holiday / halving clock | crypto rebalancing premium, BTC clock seasonality, BTC holidays | BTC, ETH | hours-days | clocks tested r3; holidays r23 N4; ETH cost 23-26 bp; halving 1 per 4 y |
| 17 | Quantpedia #0713 | synthetic lending rates (options) | US500 | daily | n/IC (options data) |
| 18 | Quantpedia, ~52 other free strategies (#0003, #0007, #0012-#0014, #0025, #0026, #0033-#0038, #0042, #0044-#0046, #0052, #0055, #0067, #0077-#0091, #0108, #0122-#0162, #0199-#0662) | stock-level factors, earnings, filings, 13F, ESG, mutual funds, REITs | single stocks / ETFs | weeks-years | n/IC (share CFDs = user decision, r25 A) |
| 19 | Quantpedia blog: ETF flows -> next-day ETF return; anticipated ETF rebalances | fund-flow pressure | ETFs | 1 day | GLD: stream G this round; index ETFs n/IC; r23 P |
| 20 | Quantpedia blog: BTC exchange reserves | on-chain flows | BTC | days | stream C this round |
| 21 | Quantpedia blog: front-running commodity / sector seasonality | seasonal drift, entered early | commodities | weeks | > 5 d; r24 B seasonals |
| 22 | Quantpedia blog: weakening morning order flow -> SPY reversal | volume order-flow imbalance | US500 | intraday | no volume in IC data; r17 (price-only OFI) |
| 23 | QuantConnect library 02, 08, 15, 17, 34, 37 | FX mean reversion + momentum, low-frequency momentum, short-term reversal | FX, indices | days-months | tested r2, r7, r11 |
| 24 | QuantConnect 04, 05 (Dual Thrust), forum "Tokyo session breakout" | range / opening-range breakout | futures, FX | intraday | tested Sept. lab (ORB, London breakout); Tokyo = C3 zone |
| 25 | QuantConnect 07, 1023, 1029, 03 | intraday dynamic pairs, ETF arbitrage, copula pairs | ETFs, stocks | intraday | tested r8 |
| 26 | QuantConnect 1026 | intraday ETF momentum (last half-hour) | US indices | intraday | tested r12 K, lab N3, r17 Z |
| 27 | QuantConnect 16 | overnight anomaly | US500 | overnight | tested r3 |
| 28 | QuantConnect 1025; Quantpedia blog LETF posts | leveraged-ETF rebalancing | indices, gold | close | tested r6, r12 L, r13 P |
| 29 | QuantConnect 1024, 1031, 1033, 1036; forum pattern matcher | CNN / SVM / GBM / naive Bayes forecasts | any | any | no economic basis (method, not mechanism) |
| 30 | QuantConnect 61 | lunar cycle | indices | month | no economic basis |
| 31 | QuantConnect 1028 | Ichimoku clouds | energy | days | CP |
| 32 | github.com/EA31337/EA31337-strategies | 70 indicator strategies (AC, ADX, Alligator, Bands, CCI, Ichimoku, MA cross, Pivot, Pinbar, SAR, ZigZag...) | FX | intraday | CP x 70 |
| 33 | github.com/freqtrade/freqtrade-strategies | ~58 indicator combinations (BB/RSI, MACD, Supertrend, TD sequential...) + HourBasedStrategy | crypto | intraday | CP x ~58; hour rule = clock scan r3 |
| 34 | github.com/je-suis-tm/quant-trading | MACD, Heikin-Ashi, Awesome, SAR, Bollinger / RSI patterns, shooting star | any | days | CP x 7 |
| 35 | same | London breakout; Dual Thrust | FX, futures | intraday | tested Sept. lab |
| 36 | same | Oil Money: NOK (and CAD) vs Brent regression residual | USDNOK, Brent | days | tested r8 R (commodity-currency fair value); NOK flows decayed r30 |
| 37 | same | pairs trading; options straddle | stocks, options | days | r8; n/IC |
| 38 | github.com/joshyattridge/smart-money-concepts (ICT/SMC); TradingView SMC [LuxAlgo] | fair value gaps, BOS / CHoCH, order blocks, retracements | any | intraday | CP x 4 |
| 39 | same; mql5 Institutional SMC Robot | liquidity sweep of Asian range / prior extremes, then reverse | FX, gold | intraday | ICT Judas sweep tested Sept. lab (J1-J5, -0.11..-0.21 R) |
| 40 | **mql5.com/en/market/product/172541, 169976, 122237, 111357, 189922, 133653, 153540, 196963; code base "Gold Fractal Breakout"** | **resting buy/sell stops beyond prior-day / swing / Asian-range extremes in gold, follow the break** | **XAUUSD** | **minutes-hours** | **untested at prior-day / prior-week extremes: declared P1 (tested here)** |
| 41 | mql5 Market: My AI Gold, Quantum Titan / Queen / iGold, Nebula, Aikon... | "AI / neural / LSTM" | gold | any | no stated rule |
| 42 | mql5 Market: Tokyo EA, ABS FX Grid; mql4 code base grid / martingale / averaging (71) | grid, martingale, averaging | FX, gold | any | tested r5 (martingale); no edge by construction |
| 43 | mql4 code base: news EAs (18); "Auto news trader" | news straddle | FX | minutes | tested r26 |
| 44 | mql4 code base: "Gaps", "Catching Gaps" | weekend-gap fade | FX | days | tested r19 T (dead since 2016) |
| 45 | mql4 code base: "E-Friday", "awo Holidays", "TokyoSessionEA", "21hour", "Time trader" | weekday, holiday, session-clock entries | FX | hours | tested r3, r10, r13 M (clock / weekday scans) |
| 46 | mql4 code base: "Swaper" | positive-swap carry | FX | days | tested r7 D, r22 (Wednesday carry) |
| 47 | mql4 code base: "10/20 pips a day opposite yesterday's trend" | daily reversal | FX | 1 day | tested r2, r11 |
| 48 | mql4 code base: "Arbitrage" (4) | broker latency arbitrage | FX | ms | not a market mechanism; not possible at one broker |
| 49 | mql4 code base: 266 indicator, 39 breakout / channel, 44 "scalper" names; 473 unclassifiable names; 151 tools | indicators, channel breaks, M1-M5 scalps | FX | intraday | CP (~349); tools are not strategies |
| 50 | mql5 code base "Monday Dip EA" (index D1) | buy indices on Monday after a down Friday | indices | 1 day | tested r25 C MON |
| 51 | mql5 code base "Opening Range Breakout NR4/NR7" | ORB with narrow-range filter | indices | intraday | ORB tested Sept. lab; NR filter = CP |
| 52 | mql5 code base "USDX Trader" | synthetic dollar index | FX | any | currency strength tested r8 |
| 53 | gogojungle.co.jp 朝スキャ (top genre, 36 mentions on the FX page) | early-morning (NY rollover hour) mean-reversion scalps | EURCHF, GBPCHF, EURGBP, USDJPY | minutes | = r23 N1 reopen-gap fade (+1-2 bp mid, IC cost 3-5 bp), r12 rollover; crosses n/IC |
| 54 | GogoJungle "東京朝・継ぎ目アノマリー" 55-min timed EA; USDJPY M5 "アノマリー" EAs | Tokyo morning / fix timing | USDJPY | minutes | the gotobi / Tokyo fix (C3's zone) |
| 55 | GogoJungle AUDCAD range EAs | cross-rate range reversion | AUDCAD | hours | n/IC (crosses = user decision) |
| 56 | github.com/vnpy/vnpy_ctastrategy (Chinese CTA classics) | ATR-RSI, Boll channel, double MA, Dual Thrust, King Keltner, Turtle | futures | intraday-days | CP / breakout x 8 (Donchian / ORB tested) |
| 57 | Chinese GitHub 黄金 repos | SGE Au(T+D) vs London spread arbitrage | gold | days | SGE prices n/IC; SGE auction tested r10 A, r27 V |
| 58 | TradingView Community Awards 2023 (top scripts: Simple Range, S/R signals); Squeeze Momentum [LazyBear], Supertrend, UT Bot; built-in strategies (MA cross, MACD, RSI, Bollinger, Channel breakout, Keltner, Pivot extension, Inside / Outside bar, Consecutive up/down, SAR, Stochastic, Volty Expan Close, Momentum) | indicators | any | any | CP x ~20 |
| 59 | TradingView gold guide "BTP/SLB" | sell gold when it closes above its 200-SMA | gold | days | CP |
| 60 | FX lore: Friday position squaring / prop-firm no-weekend rules (Lien; DailyFX / BabyPips "Friday reversal") | the week's trend partly reverses into the Friday close | FX, gold, US indices | 7 h | **untested: declared P2 (tested here)** |
| 61 | paperswithbacktest/awesome-systematic-trading (61 replications) | academic factor papers (Good carry / bad carry, media tone FX, BTC multi-timeframe trend...) | multi-asset | weeks+ | carry / trend tested r7 D, C1; media tone needs news data (GDELT unreachable) |

**Counts.** About 1,550 entries: Quantpedia 82 + about 40 relevant blog posts; QuantConnect 84; GitHub collections
(EA31337 70, freqtrade ~66, je-suis-tm 17, SMC 7 concepts, vnpy 8, mql4 code base 1,125); mql5 Market 20 read +
code base ~10 with a stated mechanism; GogoJungle 4 genres; TradingView ~25.
- **Dropped as chart patterns without an economic basis: ~520.** EA31337 70, freqtrade ~58, the mql4 code base's
  indicator / breakout / scalper names ~349, TradingView ~22, vnpy 8, je-suis-tm 7, SMC 4, QuantConnect 1. ML and
  "AI" entries without a mechanism (QuantConnect 4, mql4 6, mql5 Market ~6) are dropped too.
- **Not strategies:** 151 tools, and 473 mql4 names that state no rule.
- **Not in IC's 26 or the repo's data:** ~55 single-stock / ETF factors, options, crosses, SGE, Brain sentiment.
- **Already tested by rounds 2-30 or the September lab:** every remaining family except two.
- **Declared and tested here:** 2 families, 6 cells.

## Results (bp per trade; t clustered by UTC day of entry, P2 by Friday; power = per-trade net Sharpe x sqrt(1.73 x trades/yr))
Cost = mid - net (spread at both fills, stop slippage at 250 ms latency, 0.6 bp commission for FX / metals, 0 for
indices). Random control: P1 = 200 placebo grids (random levels at the previous close +- U(0.25, 1) x range, same
engine and side rule); P2 = 200 seeds of random Monday-Thursday entries of the same symbol and week (same era if none
qualifies), side recomputed at the random time.

| hypothesis | eras | IS mid (t) / VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | VAL / IS net | per-trade Sharpe IS / VAL; power IS / VAL size | trades/yr | random control IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| P1-PD gold, prior-day high/low stop, follow, 30 min **(primary)** | IS, VAL; PRE (minute model) | -1.07 (-1.33) / +0.60 (0.80); PRE +2.78 (4.38) | 2.13 / 1.29; PRE 1.62 | **-3.20 (-3.83) / -0.69 (-0.92)**; PRE +1.16 (1.83) | n/a (IS < 0) | -0.114 / -0.039; -2.09 / -0.71 | 196 / 194 | 58 % / 86 % | none; 0/6 IS years > 0; x1.5 -3.74, +1 min -2.09 |
| P1-PW gold, prior-week high/low | IS, VAL | +0.69 (0.37) / +1.00 (0.55) | 2.25 / 1.06 | -1.56 (-0.81) / -0.06 (-0.03) | n/a | -0.056 / -0.003; -0.44 / -0.02 | 35 / 36 | 48 % / 70 % | none |
| P1-AR gold, Asian-range (00-07 UTC) high/low | IS, VAL | -0.41 (-0.81) / -0.00 (-0.00) | 1.80 / 1.10 | -2.21 (-4.21) / -1.10 (-2.17) | n/a | -0.095 / -0.070; -2.19 / -1.61 | 310 / 308 | 84 % / 90 % | none; 0/9 years > 0 |
| P1-X, P1-PD on XAGUSD, US30, USTEC, AUDUSD, NZDUSD (pooled) | IS, VAL | +1.44 (4.30) / +0.93 (1.98) | 2.54 / 1.82 | -1.10 (-3.27) / -0.89 (-1.89) | n/a | -0.045 / -0.038; -1.86 / -1.54 | 988 / 975 | 100 % / 93 % | none: real at mid (index continuation), below cost |
| P2-top Friday squaring, top tercile of \|WTD\|, 11 symbols **(primary)** | IS, VAL, PRE (6 symbols) | -3.39 (-1.29) / -2.09 (-0.39); PRE -1.29 (-0.60) | 1.28 / 0.81 | **-4.67 (-1.77) / -2.90 (-0.55)**; PRE -2.45 (-1.14) | n/a | -0.082 / -0.038; -1.46 / -0.73 (per Friday -0.94 / -0.42) | 183 / 216 | 82 % / 84 % | none, wrong sign in IS and PRE; 1/6 IS years > 0 |
| P2-all, every Friday | IS, VAL, PRE | -0.81 (-0.59) / -3.03 (-1.08); PRE -2.23 (-1.71) | 1.24 / 0.83 | -2.05 (-1.49) / -3.86 (-1.37); PRE -3.38 (-2.59) | n/a | -0.041 / -0.055; -1.27 / -1.69 | 549 / 552 | 0 % / 0 % (control ~0 by symmetry) | none, wrong sign |

Spread x1.5, +1 minute and zero latency change no sign (in `out/p1.out` and `out/p2.out`). No exit was more than 10
minutes late in gold. P1's placebo grids lose about as much as the real levels (placebo mean IS -3.34, VAL -1.54, for
P1-PD). So a gold resting stop pays ~2 bp of cost and slippage whatever the level is, and prior-day extremes add
nothing in IS.

### Information rows (after the declared numbers; not cells)
- **Engine check (R50).** The nearest $50 multiples beyond the previous session's extremes, run through the P1
  engine: IS n 189, mid +7.23, net +4.89 (t 1.05), 6/6 years > 0; VAL n 131, net +2.47, 3/3 years > 0. This is close
  to round 27's G1-XAU50 (IS +5.99, VAL +3.27) with fewer trades, because the levels are defined differently. The
  engine sees the known $50 cascade, so P1's null is not an engine artefact.
- **Overlap with round 27.** 301 of 1,758 P1-PD levels lie within $5 of a $50 multiple. Without them P1-PD is worse:
  IS mid -1.65, net -3.79 (t -3.95); VAL net -1.17. Any cascade at a prior-day extreme comes from its being a round
  number.
- **By break side (post hoc).** Upward PDH breaks are +0.58 mid (t 0.95) in IS and +3.00 (t 2.75) in VAL, net -1.43 /
  +1.80. Downward breaks lose in both eras (net -5.10 / -3.23). The VAL upside matches gold's 2022-24 uptrend; IS
  says no.
- **PRE 2004-15 (minute-close model, Dukascopy bid, IC 2016-17 spread profile + 0.6 bp).** P1-PD mid +2.78 (t 4.38),
  net +1.16 (t 1.83), 8/12 years > 0: 2004-09 mid +3.18, 2010-15 mid +2.38. The same model on IC IS gives mid -0.12,
  net -1.67, and VAL mid +0.40. The model enters at the trigger minute's close, later than the tick engine, so its
  level is not comparable with the tick rows. The sign change from PRE to IS is the result: prior-day breaks in gold
  continued before 2016 and have not since. This fits rounds 13 and 25: stable effects shrink after 2015.
- **P1-X per symbol.** US30 IS mid +3.13 (t 4.96), net +1.69 (t 2.68), but VAL mid -0.10, net -0.50, and 3/6 IS
  years > 0. USTEC IS mid +3.27 (t 4.65), net +0.01. Silver loses to its ~5 bp cost. AUDUSD / NZDUSD +0.8 mid, below
  cost. This is round 25 C's index "crossing momentum" again: real in IS at mid, gone or below cost in VAL. US30 was
  picked from five symbols after looking, and it fails VAL.
- **P2 by class.** IS / VAL net: FX -2.75 / +2.72, gold -9.68 / -6.50, indices -7.71 / -12.45. The Wednesday /
  Thursday same-clock placebos are around 0 in IS (Thursday VAL +8.7, t 1.41). Without March-April 2020, P2-top IS is
  -2.79 (t -1.14).

## Best cell per family, cells tried, chance
| family | cells | best cell on its declared side (IS net t) | best \|t_IS\| at mid |
|---|---|---|---|
| P1 gold extremes (+ replication) | 4 | P1-PW, -0.81 (P1-X pooled -3.27) | 4.30 (P1-X pooled, mid, below cost) |
| P2 Friday squaring | 2 | P2-all, -1.49 | 1.29 (P2-top, wrong sign) |

Chance for 6 cells: max |t| of 6 normals, median 1.60 / 95th 2.64. **No declared cell has a positive IS net t.** The
only |t| above chance is P1-X's pooled mid, a real effect below cost on the declared side; the gold cells' |t| comes
from cost. C3 correlation is not reported: no cell reached IS net t >= 2.

## What the numbers say
- **Practitioner gold breakout EAs trade a cascade that existed before 2016 and is now below cost.** The commercial
  designs place stops beyond prior-day, swing and Asian-range extremes. In 2016-24 those breaks do not continue at
  mid in gold, and IC's resting-stop round trip (~1.3-2.1 bp with slippage) makes every variant lose. The only gold
  levels that still cascade are round $50 numbers (round 27, rechecked here). The EAs' published live results are
  not evidence against this: they come from optimised multi-strategy portfolios on 1-3 years, mostly the 2023-26
  gold uptrend, which a side-symmetric rule cannot use.
- **Friday position squaring does not show in prices.** If leveraged accounts flatten before weekends, they do so on
  both sides, or the flow is too small against a 30-60 bp afternoon sd. On the declared side the week's trend extends
  a little into Friday afternoon (PRE -2.2 mid, IS -0.8, VAL -3.0 on all Fridays), so practitioners have the sign
  wrong. Like the other discretionary flows of round 23 P, it does not reach 1-day prices.
- **The census adds no new family.** Practitioner and community sources repeat the academic map: carry, momentum,
  seasonality, events, ORB, clock windows, gap fades, grids. What they add is execution genres (early-morning
  scalpers, gold breakout stops). Both are now tested and both are below IC's cost. Commercial EAs that state no rule
  ("AI") cannot be tested, and their marketing claims are not data.

## Directions that need the user (value estimates are this stream's judgement)
| direction | what is needed | value |
|---|---|---|
| OANDA order book / position book (open stops and limits by price level, since ~2016) | an OANDA account (API 403 without one) | the only public measure of where stops sit. It would test P1 / round 27's mechanism directly, gold included. ~3-5 % chance of a DEMO rule, ~1 % of LIVE |
| Retail sentiment ratios (IG client sentiment, Myfxbook / DailyFX SSI history) | account or unreachable site | contrarian positioning: stream J's TFX tables test the same idea for free; low added value (~1 %) |
| mql5 Signals deal histories of the top gold EAs (real fills, years) | login; deal pages are robots-disallowed | would show whether any commercial gold EA has a durable edge net of its broker's cost; low (< 1 % LIVE): the declared mechanism already fails |
| Brain Market Sentiment (Quantpedia #0661) | paid | overnight index drift conditioned on sentiment; the VIX part is already tested (round 4); ~0 |
| TradingView script popularity (likes / boosts by market) | robots.txt disallows `/scripts/*`; needs permission or an account export | catalogue only; nearly all scripts are indicators; ~0 |

## Untested ideas (and why)
- Turtle Soup (Connors & Raschke: fade a new 20-day extreme): a daily breakout fade. P1 shows the prior-day follow-up
  is about -1 bp mid in IS, a fade would be about +1 against a ~2 bp round trip, and daily reversal / Donchian
  families are exhausted (rounds 2, 7, 11, lab "rangefade").
- Prop-firm rules (daily-loss reset at 00:00 CE(S)T, news-trading bans): the industry grew from ~2020, so IS 2016-21
  cannot test it. A new-era rule would be the user's call.
- MicroStrategy Monday BTC purchases, 0DTE, and spot ETF flows: post-2020 / post-2024 mechanisms, listed in round 23 /
  24's user directions.

## Scripts and outputs (scratchpad, not in the repo)
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r31/P/`
- `scripts/fetch.sh` (logged fetcher), `scripts/plib.py` (HOLD-cut loaders, clustered t, power, chance).
- `scripts/p1_engine.py` (tick engine for P1 and placebo grids; `R50` = the engine check),
  `scripts/p1_report.py`, `scripts/p1_pre.py` (PRE / minute model).
- `scripts/p2_friday.py`, `scripts/p2_report.py`.
- Outputs: `out/p1.out`, `out/p1_pre.out`, `out/p2.out`, `out/p1_r50.log`; trade lists `out/p1_*_real.npy`,
  `out/p1_*_plac.npy`, `out/p2_recs.npy`, `out/p2_pre.npy`.
- Census: `out/qp_strategies.tsv`, `out/qp_posts.txt`, `out/mql4_names_classified.tsv`, raw pages under `web/`
  (`requests.log`).
