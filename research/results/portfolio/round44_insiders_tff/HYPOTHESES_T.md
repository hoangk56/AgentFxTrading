# Round 44, stream T: hypotheses (CFTC Traders in Financial Futures positioning)

Declared 2026-10-30 06:12 UTC (`date -u` 06:11:43 just before writing), before any price was joined to a signal.
Only positions and signal counts had been computed at this time (scratchpad `out/tff.json`, `scripts/counts.py`).

## Sources (probed 2026-10-30 06:06-06:10 UTC)
- **www.cftc.gov is off limits**: its robots.txt (fetched 06:06 UTC, saved `web/robots/cftc.txt`) names `ClaudeBot`,
  `anthropic-ai` and `Claude-Web` with `Disallow: /`. So the official historical compressed files
  (`fut_fin_txt_*.zip`, `fut_disagg_txt_*.zip`) are not fetched. publicreporting.cftc.gov (Socrata) answers 403 to
  robots.txt and to a metadata probe (2 requests, not retried).
- **Used: the Hugging Face mirror `XOOMAR/cftc-commitments-of-traders`** (one CSV, 32.9 MB, public domain, TFF and
  disaggregated futures-only, from 2010-01; huggingface.co robots.txt allows `*`). It contains 2025-26 rows: they are
  cut at parse (as-of <= 2024-12-24; the 2024-12-31 report is released in 2025), before anything is printed.
- **Validation:** for all 17 markets, open interest and non-reportable long / short match the CFTC legacy
  futures-only annual files already on disk from round 39 (fetched 2026-10-29) in every overlapping week (754 / 754
  for the financial markets, 782 / 782 for metals and gas). The mirror has no spreading columns, so long sums are below
  OI; net positions (long - short) are unaffected.
- Coverage (<= 2024-12-24): TFF from 2010-07-20 (754 weeks) for EUR, JPY, GBP, CHF, CAD, AUD, NZD (CME), E-mini S&P
  500 (13874A), Nasdaq-100 mini (209742), DJIA x$5 (124603), Nikkei USD (240741, 695 weeks: reporting gaps), VIX (CFE
  1170E1); E-mini Russell 2000 (CME 239742) only from 2017-08-15. Disaggregated from 2010-01-05: gold (088691), silver
  (084691), natural gas (023651); NYMEX WTI (067651) only from 2022 in the mirror, so the WTI control uses ICE Futures
  Europe WTI (067411, 2010-24).
- Not available here: TFF 2006-09 (the mirror starts 2010-07), so PRE = 2012-07..2015-12 (after a 104-week warm-up)
  on the five FX legs with Dukascopy history (EURUSD, USDJPY, USDCHF, AUDUSD, NZDUSD).

## Market mapping (IC symbol, sign: +1 if long the future = long the IC symbol)
EUR -> EURUSD +1, JPY -> USDJPY -1, GBP -> GBPUSD +1, CHF -> USDCHF -1, CAD -> USDCAD -1, AUD -> AUDUSD +1,
NZD -> NZDUSD +1, ES -> US500 +1, NQ -> USTEC +1, DJ -> US30 +1, RTY -> US2000 +1, NKY -> JP225 +1,
VIX -> US500 -1 (long VIX futures = short US500). Controls: gold -> XAUUSD, silver -> XAGUSD, WTI -> XTIUSD,
gas -> XNGUSD, all +1. 13 financial legs (US500 appears twice: ES and VIX, as separate legs).

## Clock, prices, costs (same panel as round 39 D, copied as `out/panel_r39.npz`)
- As-of Tuesday, release Friday 15:30 ET. Trade Friday 15:50 ET (IC bid / ask close of that minute); exit h1 =
  Monday 15:50 ET (one trading day), h3 = Wednesday 15:45 ET (~120 h, inside the 5-day limit). Weeks with a US
  federal holiday Monday-Friday are skipped (release moves); as-of dates in the 2013-10-01..11-19 and
  2018-12-25..2019-03-05 shutdown catch-ups are skipped. ~42 weeks a year.
- Cost: IC spread at both minutes (half each side), 0.6 bp commission on FX and metals, swap per research/swing/rates.py
  (triple Wednesday; index / energy / BTC weekend rules as round 39). PRE: Dukascopy mids, IC 2016-17 median spread at
  the same minute + 0.6 bp. Stress: spread x1.5; +1 minute on both legs.

## Signals (past-only; x = (category long - short) / OI)
- `lvl`: z of x against the previous 156 weeks (>= 104).
- `chg`: weekly change of x divided by the sd of the previous 52 weekly changes (>= 40); a change across a reporting
  gap > 7 days is missing.

## Families and sides (fixed now from the literature; never changed after seeing numbers)
| family | signal | side | source of the side |
|---|---|---|---|
| H1 leveraged-fund crowding -> reversal | `lvl` of leveraged funds | **against** leveraged funds when \|z\| > k | crowded-trade unwinds (Brunnermeier, Nagel & Pedersen 2008 for FX carry; crowded speculative positions reverse) |
| H1c leveraged-fund weekly change -> reversal | `chg` of leveraged funds | **against** the change when \|z\| > k | Kang, Rouwenhorst & Tang 2020 (speculators demand liquidity short term: their position changes predict returns negatively) |
| H2 asset-manager weekly change -> continuation | `chg` of asset managers | **with** the change when \|z\| > k | slow real-money flow keeps buying in the same direction |
| H3 dealer extremes -> hedging-pressure premium | `lvl` of dealers | **with** dealers when \|z\| > k (dealers net short extreme -> short) | the intermediary absorbing hedging demand is paid for it (Kang, Rouwenhorst & Tang 2020; de Roon, Nijman & Veld 2000) |
| C1, C1c, C3 commodity controls (disaggregated) | managed money `lvl` (C1), managed money `chg` (C1c), swap dealers `lvl` (C3) | as H1, H1c, H3 | controls only: never a candidate on their own |

Parameters: k in {1.0, 1.5} for H1, H1c, H2; k in {1.5, 2.0} for H3 ("extremes"); controls k in {1.0, 1.5}
(C3 {1.5, 2.0}). Cross-sectional variant XS (H1, H1c, H2, H3): each release Friday rank the legs by
direction x z (IC terms), long the 3 highest, short the 3 lowest (needs >= 6 legs with a signal).
Horizons h in {1, 3}.

**Book (the graded unit):** one return per release Friday = mean over the legs open that week of each leg's net
return divided by that symbol's trailing sd of the same-horizon mid return (previous 156 panel Fridays, >= 52, all
Fridays, not only signal weeks); equal-weight bp book shown for information only. t on weekly book returns (all legs
enter on the same Friday, so this is the day-clustered t).

**Cells:** 4 families x (2 thresholds + XS) x 2 horizons = **24 graded book cells**; 3 control families x 2 k x 2 h
= 12 control cells (4 commodity legs); 13 legs x 4 families x 2 k x 2 h = 208 single-market cells (benchmark and
information only).

## Count and power arithmetic (counts only; no returns seen)
- Release Fridays usable: IS 2016-21 252 (245 with a z after the 2018-19 shutdown), VAL 2022-24 124, PRE (z from
  2012-07) ~139. HOLD 2025-01..2026-09-24 would hold ~73 release Fridays.
- Signal weeks (any leg) in IS: H1 k1 245 / k1.5 212; H1c 226 / 163; H2 226 / 180; H3 k1.5 229 / k2 137; XS 245.
  Legs in IS: H1 1,230 / 524, H1c 775 / 358, H2 865 / 429, H3 703 / 293, XS 6 a week.
- **LIVE is impossible from the count:** power = weekly book Sharpe x sqrt(73) >= 3 needs a weekly net Sharpe >= 0.35
  (IS t ~5.6 over 245 weeks). No weekly positioning book in rounds 4, 9, 39 came near (best t ~2); the legs share the
  Friday clock, so legs do not add independent trades.
- **DEMO needs:** book IS net t >= 2.0, i.e. weekly net Sharpe >= 2 / sqrt(245) = 0.128 (annualised ~0.83), VAL net
  > 0, x1.5 and +1 minute > 0, random control >= 90 %. At that size HOLD power would be ~1.1 (DEMO does not need 3).
  With ~6 weakly correlated legs a book Sharpe of 0.128 needs a per-leg net Sharpe of ~0.05 (cost per leg ~0.02-0.05
  sd at h1), so DEMO is within reach in principle only for the book, not for a single market (40-100 IS trades would
  need a per-trade Sharpe of 0.2-0.3). Not out of reach, so the stream proceeds.
- Literature horizon: positioning effects are documented at weeks to months (hedging pressure: months; crowding
  unwinds: weeks); at 1-3 days only a fraction (~1/5 to 1/3 by sqrt-time, less if the drift is front-loaded) is left.

## Controls and benchmarks
- Random control (>= 200 seeds): (a) same sides on random tradable Fridays of the era, per leg; (b) side recomputed
  from the unthresholded signal (direction x sign z) at the random Friday; XS recomputed ranks at random Fridays.
- Chance benchmark: weeks sign-flipped jointly across the 24 graded cells (500 draws) on the IS mid book t: best-of-24.
- Results reported with and without 2020-03/04.
- Fallback if all 24 cells fail (declared now): H4 = leveraged funds minus asset managers disagreement,
  z(lvl_am) - z(lvl_lev), side with asset managers when > k (k in {1.0, 1.5}, XS, h in {1, 3}; 6 cells), the TFF
  analogue of round 39's D3 (which used legacy non-commercial vs small traders and failed VAL).
