# Round 28, stream R2: the round-level cascade on the minute-only IC symbols (declared before numbers)

Brief: [BRIEF.md](BRIEF.md), stream R2. **Declaration written 2026-10-17 22:40 UTC (`date -u` 22:39:52), before any
return of any kind was computed in this stream.** HOLD (2025-01-01 onwards) is never loaded:
- every IC minute file is cut at ts < 2025-01-01 at load and asserted;
- every tick day request is asserted < 2025-01-01;
- Dukascopy files are cut at 2016-01-01, and the `*_2026` Dukascopy files are never opened;
- the C3 file is read for its IS / VAL rows only.

What was looked at before this declaration (prices only, no returns, no price differences turned into returns):
- the IS (2016-21) median mid of each symbol (`out/spacings.txt`). Every spacing equals the BRIEF table.
- data ranges:
  - IC M1 from 2016-01-03 22:03 UTC (BTCUSD from 2017-08-28);
  - Dukascopy m1 from 2003-12-01, m1c from 2004-01-01, both to 2015-12-31;
  - 0.17 % of EURUSD minutes have ask close < bid close: those spreads are replaced by the last good one.
- synthetic tests of the engine and the fill layer (`code/test_engine.py`, all pass);
- an independent minute-by-minute re-simulation (`code/brute.py`: own 24-hour max / min, own s60, own state machine).
  It ran on 12 symbol-years (EURUSD, USDJPY, US500, HK50, JP225, DE40, AUDJPY, BTCUSD x2, EURJPY Dukascopy, AUDUSD
  m1c; real and placebo lattices) and found 0 event, class or repeat mismatches;
- the event counts of the declared bot by symbol, year and cell (tables below), and the mean count of the 200
  placebo lattices.

R1's directory has not been read, so none of its results either. Its `minute_calibration.txt` did not exist at
22:39 UTC.

## The rule as implemented (BRIEF's G1-XAU50 rule, scaled; minute bars, bar-start labels)
- **Prices.** IC M1 (research/data/m1): bid o / h / l / c and the ask close.
  - The minute's spread s = ask close - bid close.
  - mid = bid + s / 2; ask high = bid high + s.
  - Bar i covers [t_i, t_i + 1 min); its close is the price at t_i + 1 min.
- **Levels.** Minor lattice L = u + m k. A level is MAJOR when k is a multiple of M / m, and SUPER when k is a multiple
  of Sp / m. Real lattice: u = 0. Spacings are from the IS median (table below). BTCUSD: the BRIEF's rule applied
  on the first trading day of each month to the median of the previous 250 UTC-day closes; before 250 days exist, at
  least 20 days are used, so BTC trades from 2017-10.
- **Arming** happens at the close of bar i. All of these must hold:
  - bar i is present;
  - the minute starting at the arming moment (bar i+1) is not in an exclusion;
  - at least 1,500 minutes of data precede it;
  - the bot is flat and i >= (last trigger bar) + 60. Every trigger counts here, minor ones included.
  - The level is the nearest minor level within b = 0.15 % x mid_close(i) of the mid close: upper if L - mid <= b,
    lower if mid - L <= b; ties go to the upper level.
  - Fresh: an upper L must be above M24 = the max of the mid highs (bid high + s / 2) of bars i-1439..i; a lower L
    must be below m24 = the min of the mid lows.
  - L has not triggered in the previous 1,440 minutes (i - last trigger bar of L >= 1440).
  - The order is not marketable: upper, ask close(i) < L + 0.5 s60; lower, bid close(i) > L - 0.5 s60.
    s60 = the median minute spread of the present bars among i-59..i.
- **Order.** Upper: buy stop at L + 0.5 s60(i). Lower: sell stop at L - 0.5 s60(i). Prices and band are fixed at
  arming.
- **Each bar k > i, in this order:**
  1. if minute k is in an exclusion, the order is cancelled at its start;
  2. else, if the bar is present and its ask high >= the buy stop (bid low <= the sell stop), the order triggers in
     bar k;
  3. else, if the bar's mid close has left the band (upper: < L - b; lower: > L + b), the order is cancelled at the
     close.

  Missing bars neither trigger nor cancel. After a cancel at bar k, arming is checked again from the close of bar k.
- **Traded only when L is a MAJOR level.** A trigger at any other minor level is not traded. It still starts the
  60-minute busy window and still counts as L's trigger for the 1,440-minute rule.
- **Exclusions.** A minute is excluded when it lies in any of these windows:
  - [T - 15 min, T + 15 min) around a High-impact timed calendar minute T (r25 ff_events_utc.csv) of the symbol's
    currencies and USD. Indices use their home currency and USD. HK50 uses CNY and USD: the calendar has no HKD
    rows, and its CNY rows are China's releases. BTC uses USD only.
  - 16:55-18:10 New York;
  - JPY pairs (USDJPY, EURJPY, GBPJPY, AUDJPY), 23:00-02:00 UTC (C3's territory);
  - the 15 minutes after a quote gap > 60 minutes (bar labels more than 60 minutes apart).

  Positions never cross 17:00 New York: the exit bar is capped at the bar labelled 16:53 NY (close 16:54 NY). A
  trigger after it exits at its own close. Both cases are counted as capped.
- **Exits.** Market exit h = 30 minutes after the trigger minute (primary): the close of bar k + 30. Secondary exits:
  15 and 60. No protective stop.

## Minute fill model and costs
- **Entry.**
  - Buy: max(stop, bar k's opening ask = bid open + s_k) + slip.
  - Sell: min(stop, opening bid) - slip.
  - slip = SLIP x s60(arming), calibrated below.
  - Entry mid = entry - side x s_k / 2.
- **Exit.** Long at the bid close of the exit bar, short at its ask close (bid close + its spread). A missing exit bar
  uses the first present bar within 10 minutes (not beyond the cap), else the last present bar before it. Counted.
- **net** = side x (exit - entry) / entry mid x 1e4 - commission. Commission: 0.6 bp for FX and JPY pairs, 0 for
  indices and BTC.
- **mid (gross)** = side x (exit mid - entry mid) / entry mid x 1e4.
- **Variants.**
  - Spread x1.5: entry and exit each a further quarter of their minute's spread worse.
  - +1 minute: entry by market at the close of the next present bar (its ask / bid), exit at the close of bar
    k + 1 + h, no slip term.
- **Latency.** Minute fills have no latency dimension: net_L0 = net_L250 = net_L1000 in the CSV.
- **No swap.** No position crosses 17:00 NY.

## Calibration of the minute model against ticks (AUDUSD, US30; days < 2025-01-01)
1. Run the minute engine above on IC AUDUSD and US30 minute data, 2016-24, real lattice, keeping every order.
2. Replay each order on IC ticks (`common.DayLoader`, the research/ticks.py format), from the arming moment (close of
   bar a). The order:
   - triggers at the first tick whose ask >= the buy stop (bid <= the sell stop);
   - unless first some tick's mid leaves the band, or the next excluded minute starts (cancel);
   - with the replay window capped at the minute model's own resolution + 60 minutes.

   Tick fills: the ask (bid) of the first tick at or after the trigger + 0 / 250 / 1,000 ms. Tick exits: the bid
   (ask) of the first tick at or after the trigger + h min + the same latency, capped at 16:54 NY; if there is no
   tick within 10 minutes, the last tick before.
3. **The slippage term.** Take the orders that trigger in the same minute in both models, at all levels. For each,
   d = side x (tick fill at 250 ms - minute base fill) in units of s60(arming); bp is reported too.
   - SLIP = mean(d). AUDUSD's value is used for FX, JPY pairs and the PRE pairs; US30's for the indices and BTC.
   - Reported: median, p90, the share of trigger-minute agreement, minute-only and tick-only triggers.
4. **The bias.** For h = 30 (also 15 and 60):
   - the minute model's mean net (with SLIP) minus the tick model's mean net (250 ms), each on its own triggered
     orders, for all levels and for the major cell;
   - the per-order matched difference, split into entry and exit legs.

   The bias is reported, not subtracted.
5. **Closes-only model** (for the m1c PRE pairs): the same engine on IC AUDUSD closes (o = h = l = c).
   - Reading (b), the close entry: enter at the trigger close's ask / bid, no slip.
   - Reading (a): enter at the stop + SLIP.
   - Both are compared with the tick replay of the same orders.
6. **R1's file.** If R1's minute_calibration.txt exists when step 3 is done, I compare it. I use my own value unless
   I have fewer than 100 matched triggers per calibration symbol; then I use R1's. I will say which I used.

## Spacings (IS 2016-21 median mid; all equal to the BRIEF table)
| symbol | IS median | minor / MAJOR / super | MAJOR, % of price | b / minor |
|---|---|---|---|---|
| EURUSD | 1.1360 | 0.01 / 0.05 / 0.10 | 4.40 | 0.170 |
| GBPUSD | 1.3103 | 0.01 / 0.05 / 0.10 | 3.82 | 0.197 |
| USDCAD | 1.3105 | 0.01 / 0.05 / 0.10 | 3.82 | 0.197 |
| USDCHF | 0.9747 | 0.01 / 0.05 / 0.10 | 5.13 | 0.146 |
| USDJPY | 109.64 | 1 / 5 / 10 | 4.56 | 0.164 |
| EURJPY | 125.40 | 1 / 5 / 10 | 3.99 | 0.188 |
| GBPJPY | 144.12 | 1 / 5 / 10 | 3.47 | 0.216 |
| AUDJPY | 80.82 | 1 / 5 / 10 | 6.19 | 0.121 |
| US500 | 2,847.6 | 50 / 100 / 500 | 3.51 | 0.085 |
| DE40 | 12,396 | 100 / 500 / 1,000 | 4.03 | 0.186 |
| UK100 | 7,115.2 | 100 / 500 / 1,000 | 7.03 | 0.107 |
| JP225 | 22,072 | 500 / 1,000 / 5,000 | 4.53 | 0.066 |
| HK50 | 26,322 | 500 / 1,000 / 5,000 | 3.80 | 0.079 |
| AUS200 | 6,051.5 | 50 / 100 / 500 | 1.65 | 0.182 |
| BTCUSD | adaptive | 2017-10: 50 / 100 / 500 (median 4.2k); 2018-04: 100 / 500 / 1,000; 2021-10: 500 / 1,000 / 5,000 (43k); 2023-04: 100 / 500 / 1,000; 2023-10 on: 500 / 1,000 / 5,000 | 2-11 | - |
| AUDUSD, NZDUSD (PRE) | 0.7372, 0.6894 | 0.01 / 0.05 / 0.10 | 6.8, 7.3 | 0.11, 0.10 |

PRE uses each pair's IS spacing.

## PRE 2004-15 (minute level, labelled; information, not a bar)
- **EURUSD, USDJPY, USDCHF, EURJPY, GBPJPY** (Dukascopy m1, bid o / h / l / c): the same engine and fill model.
  - The spread of every minute is modelled: IC's 2016-17 median spread (bp of the mid) by UTC minute of day and New
    York DST state, x the bid.
  - The calibrated SLIP is used.
  - The early Dukascopy ask is not used.
- **AUDUSD, NZDUSD** (Dukascopy m1c, bid close only): the closes-only engine (o = h = l = c) and the same modelled
  spread.
  - Main PRE reading (b): close entry, labelled `minute_close` in the CSV.
  - Reading (a), stop + SLIP, is reported as the upper bracket.
  - Their IS / VAL belong to R1. Their sd_is_30min comes from my IC minute model (IS, major cell).
- **Exclusions.** The calendar starts in 2007, so 2004-06 have no release exclusion. The rollover, JPY and gap
  exclusions apply in every year.
- **Placebo.** Each PRE placebo grid uses the same 200 offsets as that symbol's IS / VAL draws.

## Cells (per symbol)
- **Sets** (all real-lattice triggers):
  - **major** (primary): the declared trades.
  - **super**: the major triggers at multiples of Sp (dose).
  - **minor**: triggers at minor levels that are not major (dose; never traded by the rule, evaluated as if they
    were).
  - **repeat**: major triggers whose level was triggered on the same side within the previous 5 days. That break
    failed, since the level is fresh again.
  - **down** and **up**: the major triggers split by side.
- **Exits:** 30 (primary), 15, 60 minutes.
- **Count:** 6 x 3 = **18 cells per symbol, K = 270 candidate cells over the 15 symbols.** The primary cell per
  symbol is major h30.
- **Pooled readings**, in sd units, same 18 cells each: my six classes and the R2 set. That is 7 x 18 = 126 pooled
  readings.
  - The six classes: FX USD pairs (EURUSD, GBPUSD, USDCAD, USDCHF); JPY pairs (USDJPY, EURJPY, GBPJPY, AUDJPY);
    US500; European indices (DE40, UK100); Asian indices (JP225, HK50, AUS200); BTC.
  - These are readings of the same trades, not new hypotheses. The lead pools the book across streams.
- **PRE:** every cell for the seven PRE pairs (information).
- **Placebo:** 200 grids per symbol, offset (k + w) x m, k = floor(v R) with v ~ U[0, 1) (uniform in
  {0 .. R-1}), w ~ U[0.3, 0.7]. Seed np.random.default_rng(280000 + the symbol's position in common.SEED_LIST).
  BTC: (floor(v R_t) + w) x m_t per month. Each placebo bot is the full rule on its shifted lattice; its cells come
  from its own triggers.

## Event counts from prices (real lattice; MAJOR triggers per year)
| symbol | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | IS / yr | VAL / yr | super | repeat | down / up | minor (not traded) | placebo major (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 13 | 12 | 12 | 13 | 12 | 9 | 33 | 24 | 8 | 11.8 | 21.7 | 92 | 24 | 77 / 59 | 715 | 178 |
| GBPUSD | 34 | 30 | 23 | 26 | 41 | 19 | 43 | 30 | 13 | 28.8 | 28.7 | 122 | 47 | 132 / 127 | 1002 | 241 |
| USDCAD | 29 | 27 | 25 | 7 | 24 | 16 | 25 | 24 | 24 | 21.3 | 24.3 | 75 | 35 | 98 / 103 | 797 | 204 |
| USDCHF | 12 | 20 | 21 | 15 | 12 | 14 | 21 | 16 | 19 | 15.7 | 18.7 | 106 | 31 | 61 / 89 | 599 | 147 |
| USDJPY | 20 | 11 | 13 | 6 | 19 | 29 | 31 | 28 | 21 | 16.3 | 26.7 | 98 | 25 | 83 / 95 | 670 | 178 |
| EURJPY | 23 | 19 | 24 | 21 | 20 | 16 | 40 | 25 | 28 | 20.5 | 31.0 | 121 | 31 | 100 / 116 | 843 | 216 |
| GBPJPY | 47 | 29 | 26 | 35 | 28 | 29 | 35 | 34 | 35 | 32.3 | 34.7 | 159 | 45 | 157 / 141 | 1187 | 299 |
| AUDJPY | 25 | 9 | 12 | 11 | 20 | 26 | 23 | 26 | 19 | 17.2 | 22.7 | 77 | 22 | 86 / 85 | 656 | 166 |
| US500 | 27 | 12 | 56 | 41 | 68 | 68 | 104 | 67 | 75 | 45.3 | 82.0 | 99 | 97 | 255 / 263 | 564 | 562 |
| DE40 | 49 | 37 | 47 | 30 | 65 | 61 | 72 | 50 | 49 | 48.2 | 57.0 | 222 | 96 | 226 / 234 | 1848 | 454 |
| UK100 | 24 | 20 | 27 | 9 | 34 | 34 | 44 | 26 | 13 | 24.7 | 27.7 | 105 | 49 | 129 / 102 | 855 | 217 |
| JP225 | 36 | 37 | 44 | 30 | 48 | 62 | 69 | 51 | 91 | 42.8 | 70.3 | 56 | 74 | 252 / 216 | 531 | 513 |
| HK50 | 30 | 23 | 52 | 46 | 51 | 52 | 43 | 46 | 36 | 42.3 | 41.7 | 81 | 68 | 194 / 185 | 400 | 399 |
| AUS200 | 81 | 53 | 77 | 74 | 149 | 93 | 125 | 92 | 108 | 87.8 | 108.3 | 171 | 163 | 442 / 410 | 884 | 852 |
| BTCUSD | - | 87 | 82 | 74 | 60 | 123 | 69 | 60 | 219 | 100.2 (4.25 IS years) | 116.0 | 202 | 70 | 299 / 475 | 1049 | 632 |

- The 15 symbols give 3,157 IS and 2,134 VAL major triggers: about 526 a year in IS and 711 in VAL.
- At a per-trade net Sharpe of 0.1, R2's set alone would give power 0.1 x sqrt(1.73 x 711) = 3.5 at the VAL rate.
- Without BTC and AUS200 (their large counts) the rate is ~518 a year in VAL.

PRE (MAJOR triggers per year):

| PRE symbol (source) | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | per yr | super | repeat | down / up | minor | placebo major (mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EURUSD (m1) | 32 | 34 | 14 | 24 | 44 | 38 | 37 | 34 | 28 | 32 | 12 | 25 | 29.5 | 195 | 80 | 195 / 159 | 1546 | 387 |
| USDJPY (m1) | 25 | 26 | 14 | 26 | 29 | 29 | 9 | 6 | 11 | 17 | 11 | 29 | 19.3 | 140 | 39 | 114 / 118 | 934 | 238 |
| USDCHF (m1) | 43 | 31 | 31 | 30 | 46 | 24 | 26 | 22 | 14 | 13 | 14 | 25 | 26.6 | 142 | 61 | 160 / 159 | 1291 | 332 |
| EURJPY (m1) | 38 | 33 | 21 | 28 | 36 | 51 | 27 | 34 | 27 | 34 | 15 | 37 | 31.8 | 173 | 63 | 197 / 184 | 1475 | 364 |
| GBPJPY (m1) | 48 | 36 | 38 | 55 | 49 | 63 | 32 | 25 | 19 | 27 | 24 | 38 | 37.8 | 231 | 72 | 243 / 211 | 1935 | 471 |
| AUDUSD (m1c, closes) | 30 | 16 | 24 | 13 | 34 | 35 | 28 | 38 | 20 | 19 | 17 | 11 | 23.8 | 136 | 51 | 141 / 144 | 1238 | 311 |
| NZDUSD (m1c, closes) | 24 | 22 | 9 | 21 | 28 | 21 | 32 | 28 | 11 | 22 | 11 | 23 | 21.0 | 131 | 48 | 134 / 118 | 1132 | 281 |

Calibration symbols (IC minute model, 2016-24): AUDUSD 782 triggers (144 major), US30 912 (442 major).

## Statistics and bars (L250 = the minute model's single value)
- **Per cell**, by era (IS 2016-21, VAL 2022-24, PRE 2004-15) and by year:
  - mean net and mid in bp, t clustered by the UTC day of the trigger;
  - net at x1.5 and at +1 minute;
  - years > 0 out of 9 (BTC 8);
  - VAL / IS;
  - per-trade net Sharpe; power = Sharpe x sqrt(1.73 x trades a year) at the IS and VAL rates, plus the per-day
    version. Era years: IS 6 (BTC 4.25), VAL 3, PRE 12.
- **Placebo share.** The share of the 200 placebo draws of the same cell whose mean net is below the real cell's,
  IS / VAL / PRE separately.
  - Per symbol, a draw with more trades than the real cell is subsampled to the real count (seeded), as in round 27.
  - Pooled readings sum the same draw index across symbols, in sd units, without subsampling, as the lead's pool.py
    does.
- **sd_is_30min** (per symbol, fixed for VAL and PRE): the sd of the IS major-cell 30-minute net (minute model with
  SLIP). If the symbol has fewer than 30 IS major trades, the sd of all its IS real triggers at 30 minutes is used.
- **LIVE** (per symbol, class or set; round 13, unchanged), all of:
  - IS net t >= 2.5 and VAL net t >= 1.5;
  - >= 2/3 of years net > 0;
  - net > 0 in IS and VAL at x1.5 and at +1 minute;
  - beats >= 95 % of the placebo in IS and in VAL;
  - power at the VAL rate >= 3.
- **DEMO**, all of:
  - IS net t >= 2.0 and VAL net > 0;
  - net > 0 at x1.5 and +1 minute in IS and VAL;
  - beats >= 90 % of the placebo in IS and VAL.
- **Chance.**
  - Max |t| of K = 270 independent normals.
  - A sign-flip null: 1,000 draws, one sign per UTC day shared by every candidate cell, applied to the IS per-trade
    mid return; the max IS mid t over the cells gives p50 / p95.
  - The best observed IS mid and net t are compared with both.
- **Draft.** A cell, class or the set that meets LIVE or DEMO on IS / VAL gets PREREG_DRAFT_R2_<name>.md:
  - the exact rule;
  - expected HOLD trades, and expected HOLD t on the VAL size and at 0.65 of it;
  - the C3 daily correlation (IS + VAL rows of trades_C3_gotobi_jpy_basket.csv).

  The pooled verdict is the lead's.

## Per-trade CSV for the lead (`scratchpad/r28/R2/trades_R2.csv`)
- **Columns:** sym, cls (lead's codes: FX, JPY, USIDX, OTHIDX, BTC), cell, era, year, t_trigger_ms, side (+1 / -1),
  gross_bp, net_L0, net_L250, net_L1000, net_x15, net_p1min, sd_is_30min, fill.
  - cell is one of major / super / minor / repeat / placebo_<k>, k = 0..199.
  - t_trigger_ms is the trigger bar's start; the trigger lies inside that minute.
  - All rows use the 30-minute exit.
  - fill is `minute` (OHLC model) or `minute_close` (closes-only PRE of AUDUSD, NZDUSD).
- **Rows:**
  - every real trade of the four sets, for the 15 symbols in IS / VAL and the seven PRE pairs in PRE (a super or
    repeat trade appears again under its own cell name);
  - the placebo trades of the major cell, all eras.
- The three latency columns carry the same minute-model value.

## Not declared (will not become candidates)
Any other spacing, band, stop offset, hold or exclusion; selections by session, year or volatility; protective
stops; any level set other than those above.

## Addendum 1 (2026-10-17 22:47 UTC, `date -u`): the calibration, before any return of an R2 symbol
Written after the calibration runs and before any return of an R2 symbol was computed. The calibration computed
returns only for R1's AUDUSD and US30, under both models. Nothing below is a cell.

**A forced change: FX slip in bp, not s60 units.** IC's FX minute spreads are often exactly 0. The 60-minute median
spread s60 is 0 in this share of minutes:

| AUDUSD | EURUSD | GBPUSD | USDJPY | EURJPY | indices, BTC |
|---|---|---|---|---|---|
| 23 % | 64 % | 12 % | 27 % | 1 % | 0 % |

20.7 % of AUDUSD's matched triggers have s60 = 0. A slip in s60 units would charge no slippage on those orders,
although the tick fills still slip, so the declared spread-unit slip is undefined for FX.

**The slip used:**
- **FX and JPY pairs, incl. the m1 PRE pairs:** SLIP = AUDUSD's mean (tick L250 fill - minute base fill) on the 758
  same-minute matches, in bp: **+0.558 bp** (median +0.31, p90 +1.65).
- **Indices and BTC:** as declared, US30's mean in s60 units, **0.837 x s60** (= +0.50 bp at US30; median 0.50 s60,
  p90 2.7).

**Agreement with the tick model.** Each model's mean net is computed on its own triggered orders.

| symbol, exit | minute net | tick net (250 ms) | bias, all levels | bias, major |
|---|---|---|---|---|
| AUDUSD, h30 | -1.35 | -1.38 | +0.03 | -0.005 |
| AUDUSD, h15 | - | - | -0.22 | -0.23 |
| AUDUSD, h60 | - | - | -0.09 | +0.08 |
| US30, h30 | -0.45 | -0.35 | -0.09 | +0.00 |
| US30, h15 | - | - | -0.01 | +0.15 |
| US30, h60 | - | - | -0.09 | -0.19 |

- 97-98 % of minute triggers trigger on ticks in the same minute within the same order life; 0.1-0.4 % never do.
- A strict tick replay that cancels at the first tick out of the band and never re-arms would keep 66-67 % of
  minute triggers. That is a re-arming artefact, not a fill difference: a tick bot re-arms as soon as the mid is
  back in the band.

**Closes-only model (IC AUDUSD closes; the m1c PRE reading), h30, all levels / major:**
- Reading (b), the close entry with no slip: bias -0.45 / -1.44 bp (low).
- Reading (a), stop + 0.73 bp: +1.08 / +0.68 (high).
- (b) is the PRE reading for AUDUSD and NZDUSD and is read as a lower bound; (a) is the upper bracket.

**R1's file** (r28/R1/minute_calibration.txt, read at 22:46 UTC) recommends the close entry with no slip for R1's
closes-only minute bot. Its stop-price reading on closes is biased up by +1.7 to +3.5 bp: tick crossings that reverse
inside the minute are invisible on closes. My minute model reads the bar's bid high / low plus its spread, so those
crossings trigger it, and the calibration above shows no such bias. **I use my own calibration** for the OHLC data
(IC 2016-24 and the Dukascopy m1 PRE pairs). R1's recommended close entry is the reading I use where only closes
exist (the m1c PRE pairs).
