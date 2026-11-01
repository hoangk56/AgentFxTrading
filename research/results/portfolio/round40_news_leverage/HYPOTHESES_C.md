# Round 40, stream C: hypotheses (Chinese margin-financing leverage and forced deleveraging)

Written 2026-10-29 14:23 UTC (`date -u`), after the margin series was downloaded and its signal days counted, and after
the unconditional sd / cost of each target was measured on IC prices. **No signal had been joined to a return when
this file was written.** Sides below are fixed; they will not change after numbers are seen.

## Source
- Eastmoney data centre, report `RPTA_RZRQ_LSHJ` (SSE + SZSE combined margin history; the page behind
  data.eastmoney.com/rzrq/total.html): `https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ&columns=ALL&source=WEB&client=WEB&sortColumns=DIM_DATE&sortTypes=1&pageNumber=N&pageSize=1000&filter=(DIM_DATE<='2024-12-31')`.
  The server caps a page at 800 rows; the last rows were re-fetched in 200-row pages with
  `(DIM_DATE>='2023-06-01')(DIM_DATE<='2024-12-31')`. 3,586 CN trading days 2010-03-31..2024-12-31, no gap > 12
  calendar days; every request carried the <= 2024-12-31 filter and the parser drops any later row.
- Fields used: `RZYE` financing balance (yuan), `RZJME` net financing buy, `RQJMG` net short sales (shares, sell -
  repay), `RQYL` short balance (shares), `ZDF` CSI 300 daily % change (the `NEW` column is the CSI 300 level), `LTSZ`
  float cap. Spot checks: RZYE 0.86 trn end-2012, 1.17 trn end-2015, 1.85 trn end-2024 (match published totals).
- No robots.txt on either Eastmoney host (404 / API error); one request per >= 1.5 s, browser UA, no personal data,
  log in scratchpad `web/requests.log`.
- **Publication time (declared).** The exchanges publish day D's margin totals before the open of the next trading
  day (SSE / SZSE margin implementation rules, information-disclosure article; I could not re-read the article text
  in this session, one WebSearch did not return it). Declared: public by 01:30 UTC (09:30 Beijing) on D+1. Entry at
  the close of the 01:45 UTC bar of D+1 (the next CN trading day). Robustness: entry at 05:00 UTC on D+1 (HK
  afternoon) as the "late" column, in case of a later release in some years.

## Mechanism and literature (sides)
- **Forced deleveraging (C1).** Chinese brokers call a margin account when the maintenance ratio (collateral / debt)
  falls below the line (130 % for most of the sample); the client has about 1-2 trading days to top up, then the
  broker sells (平仓). A large fall in the aggregate financing balance on a down day marks deleveraging under way, and
  the calls issued at D's close are executed D+1..D+2. Brunnermeier & Pedersen (2009, margin / liquidity spirals)
  imply **continuation** at short horizons. Bian, He, Shue & Zhou ("Leverage-induced fire sales and stock market
  crashes", NBER WP, 2018; 2015 account-level data): stocks held by accounts near their call triggers show abnormal
  selling and price declines **that subsequently reverse**. Their effect is cross-sectional (no index-level size) and
  the reversal comes after the selling; at 1-5 days the selling side dominates. **Declared side: continuation
  (risk-off).** Sizes: none at the index level in the literature; prior expectation here 0-10 bp at h1 on HK50,
  because day D's move is already in HK prices (round 37 N: Connect flows co-move, do not predict).
- **Leverage build-up (C2).** Retail margin buying is sentiment (Chinese margin investors chase); the brief fixes the
  side as **reversal** after a surge in net financing buying (risk-off next days).
- **Securities lending (C3).** Short sellers in China are informed on average (Chang, Luo & Ren 2014, J. Banking &
  Finance, cross-section of eligible stocks), so a surge in net short selling -> **continuation of their view**:
  rising net short sales -> risk-off; heavy short covering -> risk-on. Caveats flagged before results: the lending
  market is tiny before 2019 (RQYE 3-7 bn), grows with the 2019-20 STAR / refinancing reforms (120 bn end-2021), and is
  cut by regulation in 2015-08 (T+1 repayment), 2023-10 and 2024-01/07 (refinancing curbs, then suspension).

## Signals (CN trading day D; z vs trailing window excluding D)
| cell set | rule on day D | side (risk) |
|---|---|---|
| C1_k1.5 | CSI 300 ZDF_D < 0 and z60(g_D) <= -1.5, g_D = RZYE_D / RZYE_{D-1} - 1 | risk-off |
| C1_k2.0 | same with z <= -2.0 | risk-off |
| C2a_k2 | z60(g_D) >= +2.0 (one-day surge of net financing buying) | risk-off (reversal) |
| C2b_k2 | z250(g5_D) >= +2.0, g5 = 5-day financing growth (leverage build-up over a week) | risk-off (reversal) |
| C3_k2 | \|z60(n_D)\| >= 2, n_D = RQJMG_D / RQYL_{D-1} (net short sales per share short) | z > 0 risk-off, z < 0 risk-on |

Targets and the trade per risk-off signal: **short HK50, long USDCNH (CNH weaker), short AUDUSD, short JP225, long
XAUUSD (haven; weak prior, could also be sold for cash), short US500 (control: global beta; should be weaker than
HK50 / CNH)**. Risk-on reverses each.
Horizons: S = D+1 01:45 -> 07:59 UTC (HK day session close); h1 / h3 / h5 = D+1 01:45 UTC -> 01:45 UTC 1 / 3 / 5 CN
trading days later, capped at 5 x 24 h (the exit moves back to the last CN trading day within 120 h of entry, so
h5 is often 3-4 CN days; a trade with no CN day inside the cap is dropped). Cap added 14:24 UTC, before any return.
A bot holds at most 3 trades per cell: a signal is skipped while 3 trades of the cell are open.

Cell count: 5 sets x 6 targets x 4 horizons = **120 cells** (C1 48, C2 48, C3 24). Pre-declared primary cell per
family: HK50 h1 (C1_k1.5, C2a_k2, C3_k2). Chance: max |Z| of 120 normals, median 2.76, 95th pct 3.53 (48: 2.45 /
3.27; 24: 2.19 / 3.09).

## Protocol
- IC M1 (ts < 2025-01-01 at load, asserted); USDCNH bid / ask M1 rebuilt from IC ticks 2016-24 by round 37 N
  (read-only). Buy at ask close, sell at bid close; FX commission 0.6 bp; swap per rollover from `swap_frac_at`
  (USDCNH: round 37 N's approximation). Variants: spread x1.5, +1 minute both legs, late entry (05:00 UTC).
- PRE 2012-06..2015 (USDCNH Dukascopy from 2012-06-27; AUDUSD, XAUUSD Dukascopy) at bid-to-bid mid, minus the cell's
  mean IC 2016-17 cost. **2015 (the leverage crash, H1 build-up and H2 deleveraging) is PRE only** because IC starts
  in 2016; PRE is shown with and without 2015. HK50 / JP225 / US500 have no PRE.
- t: cluster-robust by episode (signal days within 5 CN days of the previous one form an episode). Random control:
  200 draws of the same number of non-signal CN days in the same era (C3: side from the sign of z on the drawn day);
  share of draws with mean net below the observed. Results also without 2020-03/04.
- IS 2016-21 picks; VAL 2022-24 checks; HOLD closed.

## Counts and power (before returns)
Signal days / episodes per year:

| set | 2010-15 (PRE era) per yr | IS 2016-21 total | VAL 2022-24 total | HOLD trades expected (1.73 yr at the IS-VAL rate) |
|---|---|---|---|---|
| C1_k1.5 | 8 / 5 (2015: 15 / 6) | 59 / 37 | 33 / 17 | ~17 trades, ~10 episodes |
| C1_k2.0 | 3.5 / 2 (2015: 11 / 4) | 27 / 22 | 16 / 13 | ~8 |
| C2a_k2 | 7.5 / 4 | 46 / 21 | 14 / 10 | ~11 |
| C2b_k2 | 7.5 / 1.5 | 32 / 4 | 18 / 6 | ~9 (2-3 episodes) |
| C3_k2 | 15 / 10 | 92 / 48 | 43 / 25 | ~25 |

Unconditional sd / round trip at the declared clock (IS; VAL in brackets), bp: HK50 S 80 / 3.3, h1 116 (167) / 5.0,
h3 198 / 8.6, h5 254 / 12.1; USDCNH S 15 / 1.2, h1 28 (34) / 1.6, h3 45 / 2.3, h5 58 / 3.1; AUDUSD h1 63 / 1.6;
JP225 h1 119 / 4.8; XAUUSD h1 87 / 1.3; US500 h1 100 / 3.9.

- **LIVE is impossible from the count for every set.** HOLD power 3 with ~8-25 HOLD trades needs a per-trade net
  Sharpe of 0.6-1.06 (HK50 h1: 70-120 bp net per trade, USDCNH h1: 17-30 bp). No literature or prior round suggests
  anything near that.
- **DEMO** (IS t >= 2 on episode-clustered t) needs an IS per-trade Sharpe of about 2 / sqrt(episodes): C1_k1.5 0.33
  (HK50 h1 ~38 bp net, USDCNH h1 ~9 bp net), C1_k2.0 0.43, C2a 0.44, C2b ~1.0 (4 IS episodes: DEMO unreachable in
  practice), C3 0.29 (HK50 h1 ~34 bp).
- So this stream can at most yield a DEMO candidate, and only if the effect is several times what same-day pricing
  suggests. The test is whether forced selling on the mainland carries past day D into HK / CNH.

## Addendum 1 (2026-10-29 14:27 UTC, `date -u`): fallback families after the first construction
Written after the 120 declared cells above were graded (results in STREAM_C.md). Seen so far: C1's declared
continuation side loses on HK50 (the day after a deleveraging down day HK50 rose), and one C3 gold cell meets the DEMO
numbers. The fallback below keeps the declared mechanism's side (continuation after forced selling), fixed from the
mechanism, not from the C1 numbers; I expect it to fail for the same reason C1 did.

- **F1 distance to the margin-call trigger (cost-basis proxy; Bian, He, Shue & Zhou's mechanism at index level).**
  Leverage cost basis B_t = (B_{t-1} x (RZYE_{t-1} - RZCHE_t) + P_t x RZMRE_t) / RZYE_t (repayments at the running
  basis, new buys at the CSI 300 level P_t; start B = P on 2010-03-31). Underwater U_t = P_t / B_t - 1. Event: U_D <=
  -X on a CSI 300 down day, with U above -X on each of the previous 20 CN days (fresh), X in {5 %, 10 %}. Side risk-off:
  short HK50, long USDCNH, short AUDUSD. Horizons S, h1, h3. 2 x 3 x 3 = 18 cells.
- **F2 deleveraging when leverage is high.** C1_k1.5's events kept only when RZYE / LTSZ is above its trailing 250-day
  70th percentile (more accounts near their trigger). Same side and targets, horizons S, h1, h3: 9 cells.
- Same protocol as above. Total after the addendum: 147 cells (max |Z| of 147 normals: median ~2.83).
