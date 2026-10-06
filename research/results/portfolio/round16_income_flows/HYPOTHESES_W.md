# Round 16, stream W: hypotheses (cross-border income conversion flows)

Written 2026-10-06 02:28 UTC (`date -u`), before any return of this stream was computed. The JPX AGM history
was parsed and the Swiss payers' dividend pages fetched before this time; no price was loaded. HOLD (>= 2025-01-01)
is never loaded: the panel ends 2024-12-31, Dukascopy ends 2015-12-31, and every lookup refuses t >= 2025-01-01.

## What the literature says (sources in STREAM_W.md)
- Zheng (2023, U. Chicago JMP / thesis 2024, SSRN 6415558): G10, 2001-2023, company-level dividend dates
  (Compustat Global, CRSP). On a country's top-5 % dividend payment dates the local currency falls vs USD:
  cumulative -1.5 bp at t0, -2.3 t+1, **-4.7 t+2**, -5.2 t+3, -6.5 t+8 (two-way FE, se 1.2-3.0 bp); before the
  date nothing (+3.0 at t-2). Post-GFC -7.4 bp at t+2, pre-GFC -1.5. Mechanism: benchmark funds (ETFs, mutual
  funds) repatriate dividends shortly after the cash arrives because total-return indices assume reinvestment
  pro rata (in other currencies); case study: a US ETF sold JPY 2 business days after Japanese interim dividends
  (Dec 2022). Strategy "sell currency k for 1 day if its past-2-day dividends are in its top 5 %": 4.4 %/yr gross,
  Sharpe 0.68, on ~25 % of days, at 1 bp cost. Concentration: Japan June and December (top 5 % of days > 60 % of
  the year's dividends), euro area May (50 % within 18.5 days), Switzerland 50 % within 2.5 days, US spread.
  Index methodology converts at the WM/R London 16:00 fix on the ex-date.
- Market reports: Korean won weakness in April dividend season (Bloomberg 2019-04-08; KED Global 2022) - not
  tradable here (no KRW).

## The arithmetic before looking (prior power)
- Zheng's effect is ~5-6 bp over t+1..t+3 per large-payment event (7 bp post-GFC). A 3-day FX return has sd ~
  80-100 bp. Per-event Sharpe ~0.06. With ~3 Swiss events a year: expected IS t ~0.27 (18 events), PRE ~0.4.
  Pooling every seasonal block below (~10 a year): IS t ~0.5, PRE ~0.7. DEMO needs IS t >= 2, i.e. an effect ~4-7x
  Zheng's. Without company-level dates the seasonal windows dilute it further. **Expected verdict: nothing
  detectable at 1-5-day horizons; DEMO at best for any seasonal effect; LIVE impossible** (17 HOLD events x
  Sharpe 0.06 -> power 0.26).
- The only route with power is the fix minute: if conversions are executed at the WM/R 16:00 London fix, the
  15 minutes into it have sd ~3-5 bp; 0.5 bp a day over ~180 IS conversion days would give t ~1.7, but cost
  (0.6 bp commission + spread) needs > ~1 bp a day to be net positive.

## Conventions (all cells)
- Side from the mechanism, never from data: **sell the currency in which the income is paid, buy USD** (the
  receiver is a foreign holder who repatriates). USD-paid income: sell USD.
- P = payment date (local business day). Conversion days = P+1, P+2, P+3 local business days that are also London
  business days (Zheng's step is t+1..t+3).
- "3-day" measure: enter 16:00 London on P, exit 16:00 London on P+3 (one trade, <= 5 days, 3 rollovers' swap).
- Seasonal blocks (no exact dates): conversion days = documented payment window shifted +2 business days; the
  position is held over contiguous business days in chunks of <= 5 days (one round-trip cost per chunk) from
  16:00 London to 16:00 London.
- **JPY cells**: no gotobi day (5/10/15/20/25/month-end, weekend moved to the Friday before, as
  `research/swing/swing_rules.gotobi_days`) is ever a conversion day, and JPY returns are measured only in the
  daytime segment **03:00 UTC -> 16:00 London of each non-gotobi conversion day** (one intraday trade per day, no
  rollover). This never overlaps the Tokyo fix (00:55 UTC +- 1 h) nor C3's legs (18:00 UTC -> 00:55 -> 02:55 UTC).
  The cost: Japanese-side conversions executed at the Tokyo TTM are deliberately not captured.
- "Fix" measure: on each conversion day, 15:45 -> 16:00 London (bar-end labels), sell the paying currency. PRE
  symbols with H1 only (AUDUSD): 15:00 -> 16:00 London.
- Data: PRE 2004-15 Dukascopy (M1 bid for USDJPY USDCHF EURUSD; H1 for AUDUSD GBPUSD USDCAD NZDUSD), IS 2016-21,
  VAL 2022-24 (IC panel mid). Costs per the round-13 brief (half spread at entry and exit, 0.6 bp commission,
  `swap_frac_at` for rollovers; PRE: IC 2016-17 median spread by minute of day). Variants x1.5 spread, +1 minute.
- t clustered by event block (one block per country-season-year; exact-date events within 10 days of each other
  merge). Report PRE / IS / VAL, by year, VAL/IS, power (IS and VAL size).
- Placebos: (i) the same block rule shifted by k = +-1..+-5 months (same years); (ii) the block's dates applied to
  other currencies (Zheng finds no cross effect); (iii) GBP, CAD, NZD (no concentrated season) on the pooled
  calendar; (iv) random entries: 500 seeds, same number of days per block from non-block business days of the same
  year with the same weekday mix. Shared sign-flip null across the registered cells for the max |t|.

## Registered cells (20), side and rule fixed now

| id | mechanism / source | where | rule |
|---|---|---|---|
| W1a | Swiss big-3 dividends (Nestle, Novartis, Roche ~ half of SMI dividends; Zheng: CH 50 % in 2.5 days). Dates: SIX pay dates (dividendmax.com, 2011-24), earlier = ADR ex-date (dividendhistory.org, digrin.com) + 2 Swiss business days | USDCHF long | 3-day from P |
| W1b | same | USDCHF long | fix, P+1..P+3 |
| W2a | Japanese year-end dividends after June AGMs. AGM date distribution per year: JPX "定時株主総会開催日集計結果" 2002-2025 (kako.pdf). P = TSE business day after each of the year's top-2 AGM days | USDJPY long | daytime 03:00 UTC -> 16:00 London on P+1..P+3, gotobi excluded |
| W2b | same | USDJPY long | fix on the same days |
| W3a | Japanese interim dividends, early December (Zheng case study: payments 30 Nov - 2 Dec 2022) - documented window only: payment Nov 28 - Dec 8 -> conversion = TSE business days Dec 1 - Dec 11 | USDJPY long | daytime, gotobi excluded |
| W3b | same | USDJPY long | fix |
| W4a | Euro-area dividend season (Zheng: concentrated in May; DE AGMs pay 1-3 days after the AGM, FR/IT/ES May-June) - documented window: conversion = TARGET days from the 3rd of May to the 2nd of June | EURUSD short | held fix-to-fix, <= 5-day chunks |
| W4b | same | EURUSD short | fix, every block day |
| W5a | Australian main season (BHP, CBA, Rio, CSL, Woodside, Wesfarmers, Telstra pay late Mar / early Apr and late Sep / early Oct) - conversion = AU and UK business days Mar 22 - Apr 14 and Sep 22 - Oct 14 | AUDUSD short | held, <= 5-day chunks |
| W5b | same | AUDUSD short | fix (PRE: hour into the fix) |
| W5c | Australian banks (NAB, ANZ, Westpac pay early July and mid-December) - conversion Jul 3 - Jul 14, Dec 14 - Dec 22 | AUDUSD short | held, <= 5-day chunks |
| W5d | same | AUDUSD short | fix |
| W6a | pool of W1a, W2a, W3a, W4a, W5a, W5c (sign-aligned per-block mean) | all | block-clustered |
| W6b | pool of the fix cells W1b..W5d | all | block-clustered |
| W7a | US Treasury coupon on the refunding quarter (15 Feb/May/Aug/Nov, next US business day): foreign private holders convert coupons to home currency. **Near-repeat**: round 13 N2b tested these days at 1 day (USD3, long USD) | USD4 = short USD vs EUR, GBP, AUD, long CHF... i.e. EURUSD, GBPUSD, AUDUSD long, USDCHF short (no JPY: the 15th is gotobi) | 16:00 London D-1 -> 16:00 London D+2 |
| W7b | same | USD4 | fix on D, D+1, D+2 |
| W8a | Euro sovereign large redemption / coupon dates (OAT 25 Apr, 25 Oct; Bund 4 Jan, 4 Jul; next TARGET day): non-resident holders (~half) that do not roll sell EUR. Weak prior: official holders reinvest in EUR, and index funds drop bonds < 1 year to maturity before redemption | EURUSD short | 16:00 London D-1 -> D+2 |
| W8b | same | EURUSD short | fix D..D+2 |
| W9a | JGB quarterly redemptions (20 Mar/Jun/Sep/Dec): domestic receivers reinvest partly abroad, foreign holders repatriate - both sell JPY. The 20th itself is gotobi: days D+1..D+3 TSE business days, gotobi excluded (the 25th) | USDJPY long | daytime 03:00 UTC -> 16:00 London |
| W9b | same | USDJPY long | fix on the same days |

Not tested (and why): UK dividends (spread through the year in Zheng, so GBP serves as a placebo currency);
US dividends (paid by the base currency, concentrated in quarter-end months = quarter-end funding already tested
in round 13 N5); Bund 15 Feb / 15 Aug (same day as the US coupon, opposite side); company-level calendars for
Japan, the euro area and Australia (Compustat Global / Bloomberg DVD: a user decision).

## Post-hoc additions
Written 2026-10-06 02:34 UTC, after the registered screen and controls (no cell met DEMO), before these numbers.
All are **post hoc, information only, not registrable**:
- PH1: Zheng-style event path for the Swiss exact dates: cumulative USDCHF 16:00-London change from P-3 to P+8,
  pooled 2004-24 and by era, to compare with Zheng's -4.7 bp at t+2; and the minimum detectable effect (80 %
  power, 5 % two-sided) of each 1-5-day cell on its own block sd.
- PH2: W7b decomposition: by day (D, D+1, D+2), by leg, by era; and the same 15:45 -> 16:00 London USD move on
  every other US and UK business day (the unconditional baseline) per era; and on the 15th of the non-refunding
  months.
