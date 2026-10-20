# Round 24, stream A: hypotheses (mechanisms that exist only from 2023-24, new-era split)

Declared 2026-10-15 11:56 UTC (`date -u` gave 11:54:52 just before writing), before any return of any cell below was
computed. Nothing in this file was chosen after looking at prices. What was looked at before writing: the flow tables
(dates and totals, not returns), the calendars, the literature listed here, and file sizes / date ranges of
research/data/m1 (no prices). Rules of the round: research/results/portfolio/round24_relaxed/BRIEF.md (new-era split,
RELAXED tier, holds up to 20 days) plus round 13's brief for everything else.

## Data
- Prices: IC M1 cache research/data/m1/{BTCUSD,ETHUSD,USDJPY,EURJPY,EURUSD,GBPUSD,AUDUSD}.npz (ts = minute start ms
  UTC, c = bid close, ca = ask close), loaded only from 2022-01-01 (C1's pre-T+1 information cell) or 2024-01-01 on,
  to the last cached day 2026-09-24. No Dukascopy fetch is planned: the IC cache covers every declared era, and mixing
  venues would mix cost models. If a cell needs it later, it is logged in STREAM_A.md.
- US spot BTC ETF daily net flows (US$m, all funds, "Total"): Farside Investors, "Bitcoin ETF Flow - All Data"
  (farside.co.uk/bitcoin-etf-flow-all-data/). farside.co.uk returns 403 to this machine, so two independent captures
  were used: a GitHub-committed capture of 2026-09-08 (firemansghost/btc-risk-dashboard-V3,
  public/data/cache/etf/2026-09-08.html, rows 2024-01-11..2026-09-04) and the Internet Archive capture of 2026-10-01
  03:51 UTC (rows to 2026-09-30). They agree on all 681 common completed rows. Parsed to
  scratchpad r24/A/out/btc_flows_wb1001.csv.
- US spot ETH ETF daily net flows: Farside "Ethereum ETF Flow - All Data", Internet Archive capture 2026-10-01 03:51
  UTC, rows 2024-07-23..2026-09-30, parsed to r24/A/out/eth_flows_wb1001.csv.
- Calendars: NYSE and Japanese holidays from the `holidays` package (r23/shared/venv_extra), Japanese bank holidays
  Dec 31-Jan 3 added.

## Eras (new-era rule of the brief)
DISCOVERY = mechanism start .. 2025-06-30; TEST = 2025-07-01 .. 2026-09-24 (last IC day). TEST is looked at once per
declared rule. No parameter is chosen on either era: every number below is fixed here.
Mechanism starts: BTC ETFs 2024-01-11 (first trade date with a prior flow row: 2024-01-12); ETH ETFs 2024-07-23
(first usable 2024-07-24); new NISA 2024-01-01 (12th-day cohort from 2024-09); US T+1 equity settlement 2024-05-28.

## Common conventions (all cells)
- "Price at clock time tau" = bid / ask close of the last IC bar with ts < tau and ts >= tau - 10 min; if none, the
  trade is skipped and counted. Buy at the ask, sell at the bid (actual spread at both minutes). Commission 0.6 bp
  round trip on FX, 0 on crypto. Swap: swap_frac_at(symbol, side, entry_ms) per 17:00 New York rollover crossed, x3 on
  the symbol's triple weekday (research/swing/swing.py swap_frac). Only B1, B1b, B3 cross a rollover.
- Variants reported for every cell (not new cells): spread x1.5; both fills +1 minute (tau + 1 min).
- Statistics: net bp per trade; one trade per day per cell so the t is day-clustered; pooled cells cluster by day.
  Results by era and by calendar year.
- Random-entry control, 500 seeds, same count, same sides, same hold:
  BTC / ETH cells: same days, entry clock drawn uniformly on the minute grid in [09:30, 20:00) New York time.
  B cells: same clock, dates drawn from the other non-gotobi Japanese business days of the same month.
  C1: same days, entry drawn uniformly in [08:00, 15:00) New York time.
- Tiers (brief): LIVE (DISCOVERY t >= 2.5, TEST t >= 1.5, >= 2/3 of years > 0, random >= 95 %, power >= 3);
  DEMO (DISCOVERY t >= 2.0, TEST net > 0, random >= 90 %); RELAXED (DISCOVERY net t >= 1.5, TEST net > 0 with
  t >= 1.0, net > 0 at spread x1.5 and at +1 min, random >= 80 %, power on the TEST size >= 1.5, a mechanism).
  Power = per-trade net Sharpe (TEST) x sqrt(expected trades in a 21-month holdout at the rule's rate); also reported
  on the DISCOVERY size.
- Chance benchmark: 10 primary cells (A1, A1g, A2, A3, B1, B1b, B2, B3, C1, C2): max |t| of 10 normals, median 1.83,
  p95 2.82.
- C3 correlation: daily and monthly P&L correlation with research/results/portfolio/trades_C3_gotobi_jpy_basket.csv
  (usd_at_100_risk by exit date) on DISCOVERY.

## (a) Spot BTC / ETH ETF creations into the New York benchmark window

Mechanism and sources.
- The US spot BTC ETFs strike NAV on the CME CF Bitcoin Reference Rate - New York Variant (BRRNY), built from
  constituent-exchange trades between 15:00 and 16:00 New York time (12 five-minute partitions); creations and
  redemptions must trade near the fixing price, so authorised participants, issuers and their liquidity providers
  trade into that window (Kaiko Research 2024, "BTC ETFs' impact on spot market structure": the 15:00-16:00 window
  rose to 6.7 % of BTC spot volume in Q1 2024 from 4.5 % in Q4 2023; CF Benchmarks, "Optimising capital efficiency in
  replicating the BRRNY for the creation and redemption of shares", 2023-12).
- Schmidt & Kraft 2026 (SSRN 7384239, "Keeping New York's hours: Bitcoin's intraday clock after the spot ETFs";
  FRL 110932, "Trading to the fixing"): since January 2024 BTC volume peaks at 10:00 and in the 15:00-16:00 fixing
  window (New York time), both shifting with US DST; "hour of day predicts trading volume and volatility but not the
  direction of returns". So an unconditional side for the window has no source; the side must come from the flow.
- Net creation / redemption on day T is not public until after the window (Farside fills the row in the evening of T
  to the morning of T+1). The latest flow known before the window on T is the row of the previous NYSE trading day
  T-1. Daily ETF flows come in streaks (IBIT's 104-day inflow streak Jan-Apr 2024, press citing Farside), so the T-1
  sign is the public proxy for T's sign. Mazur & Polyzos 2025 (SSRN 5452994): flows follow price; a momentum
  diagnostic (A0b) separates the two.
- ETFs moved from cash-only to also in-kind creations after the SEC's July 2025 approval (inside TEST); pricing at
  the BRRNY did not change. Reported by year so a break would show.

Day set: NYSE trading days T (holidays package NYSE calendar). s_T = sign of the Farside Total of the previous NYSE
trading day; a previous-day Total of exactly 0.0 means no information: no trade.

| cell | symbol | side | entry -> exit (New York time, DST-aware) | extra condition | DISCOVERY |
|---|---|---|---|---|---|
| A1 | BTCUSD | s_T (BTC ETF Total of T-1) | 15:00 -> 16:00 on T | - | 2024-01-12..2025-06-30 |
| A1g | BTCUSD | s_T | 15:00 -> 16:00 on T | \|Total(T-1)\| >= US$300m (big-flow days; a round number fixed here, not from data) | same |
| A2 | BTCUSD | -s_T (the window's pressure ends, partial reversal) | 16:00 -> 16:55 on T (exit before the 17:00 NY rollover) | - | same |
| A3 | ETHUSD | sign of ETH ETF Total of T-1 | 15:00 -> 16:00 on T | - | 2024-07-24..2025-06-30 |

Diagnostics, information only, never candidates: A0a = A1 signed by the same day's Total (untradable oracle; tests
whether the pressure exists at all); A0b = A1 signed by BTC's 16:00->16:00 ET return of T-1 (is the flow sign just
momentum?); A0c = unconditional long 15:00->16:00.

## (b) New NISA accumulation purchases and the yen sold for them

Mechanism and sources.
- New NISA (from 2024-01) made monthly tsumitate purchases of foreign-equity investment trusts (eMAXIS Slim All
  Country / S&P 500 etc.) the largest retail flow out of yen. Size: investment-trust companies' net purchases of
  foreign securities JPY 1.15tn in March 2024 (Mizuho Bank, Karakama, MOF data); MUFG (Halpenny, 2026-10-09) puts the
  annualised NISA-driven outflow at ~JPY 16tn, a record in September 2026 (JITA / MOF data). Mizuho: most of it is
  unhedged outright yen selling. NLI Research and Nomura: tsumitate purchases sell yen mechanically every month.
- Purchase days are fixed by the brokers, not chosen: Rakuten Securities credit-card tsumitate buys on the 1st
  (customers who started before 2021-06-19), the 8th (started 2021-06-20..2024-08-24) and the 12th (started from
  2024-08-25); a day that is a holiday or fund holiday moves to the next business day (rakuten-sec.co.jp,
  rfund/guide/creditcard.html, read 2026-10-15). SBI Securities card tsumitate orders on the 1st for settings made
  before 2024-06-01, after that on a chosen day 3-9 (usedoor.jp 2024-05-29). The 3-9 SBI days are spread and not
  used.
- Foreign-equity funds price a purchase at the NAV of the business day after the order ("購入申込受付日の翌営業日の基準価額",
  eMAXIS Slim All Country, Monex fund page) and convert foreign assets at the TTM (Tokyo 09:55 JST fix); orders are not
  accepted on New York / London fund holidays. So the yen for an order placed on day O is sold on the next Japanese
  business day F, at or around the Tokyo fix, the same clock as gotobi (C3) on other days.

Days: order days O in {1st, 8th, 12th (from 2024-09)} of each month, each rolled forward to the next day that is a
Japanese business day (not Sat/Sun, not a JP holiday, not Dec 31-Jan 3) and not an NYSE holiday. F = the next Japanese
business day after O. Two order days mapping to the same F count once. **C3 exclusion**: F is dropped when it is a
gotobi day by C3's rule (5/10/15/20/25/last day of month, a weekend one moved to the Friday before); the number of
dropped days (overlap with C3) is reported. Side: yen sold, so long USDJPY / EURJPY into the fix; after the fix the
demand is gone (the C3 short-leg mechanism).

| cell | symbol | side | entry -> exit (UTC) | day | 
|---|---|---|---|---|
| B1 | USDJPY | long | 18:00 of the calendar day before F (if that day is Sat/Sun or the market is closed: first quote at or after the Sunday open + 5 min) -> 00:55 on F | F (NAV / FX day) |
| B1b | USDJPY | long | same clock | O itself (alternative: yen sold on the order day), C3 exclusion applied to O |
| B2 | USDJPY | short | 00:55 -> 02:55 on F | F |
| B3 | EURJPY | long | as B1 | F |

DISCOVERY 2024-01-01..2025-06-30, TEST 2025-07-01..2026-09-24. Expected count ~3 F days a month minus gotobi
overlaps: ~45-50 in DISCOVERY, ~40-45 in TEST. Round 23 put the power at ~0.5; reported anyway. Per-order-day (1st /
8th / 12th) breakdown is information only.

## (c) Other 2023-26 mechanisms with a known side

C1. US equity T+1 settlement (from 2024-05-28) and the USD funding window. Since T+1, foreign buyers of US shares must
buy USD between the 16:00 ET equity close and the CLS / custodian cut-offs (CLS 18:00 ET); the DTCC FX white paper
names 16:00-17:00 ET spot liquidity as the key question; Russell Investments (2024-02) expects a "witching hour" of FX
after the US close; BofA (2023-11) and Citi set out the same window. Side: foreigners were net buyers of US equities in
2024-25 (US Treasury TIC data), so the net flow buys USD. Rule: NYSE trading days from 2024-05-28, equal-weight USD-long
basket (short EURUSD, short GBPUSD, short AUDUSD, long USDJPY), 16:00 -> 16:55 ET (exit before the 17:00 rollover);
basket net bp = mean of the four legs' net bp. Information only: the same window 2022-01-03..2024-05-24 (pre-T+1) and
the difference.

C2. The "10 a.m. bitcoin dump" claim (press and social media, 2025-26: Cointelegraph, Yahoo Finance, Traders Union,
February 2026, naming Jane Street, an authorised participant of the spot ETFs; analysts and Dragonfly dispute it;
Schmidt & Kraft find a 10:00 volume peak but no direction). Side short, from the claim. Rule: short BTCUSD 10:00 ->
10:30 New York time on NYSE trading days, DISCOVERY 2024-01-11..2025-06-30. Low prior; declared because the claim is
specific and is a 2024+ ETF-era mechanism.

Considered and not declared: Strategy (MicroStrategy) BTC purchases (executed over the prior week, announced Monday;
no intraday time); the TSE close extension to 15:30 JST (2024-11-05) for JP225 leveraged-ETF rebalancing (exhausted
family: round 13 P / round 17, only the clock is new, and DISCOVERY would hold ~15 top-decile days); US Treasury
buybacks (no IC instrument); 0DTE dealer gamma (no public intraday OI); BoJ ETF purchases (ended 2024-03).
