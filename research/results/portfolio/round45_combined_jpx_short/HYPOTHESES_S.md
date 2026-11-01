# Round 45, stream S: hypotheses (JPX daily short-selling ratio; large short-position reports)

Written 2026-10-30 06:29 UTC (`date -u`), before any return was joined to a signal. At this time: the ratio series is
parsed (cut at 2024-12-31), signal days are counted (below), the karauri.net pull is running. No JP225 / USDJPY / HK50
return has been computed conditional on any signal. The only price statistics seen are unconditional (JP225 median
spread by UTC hour, the sd of 1-day returns, swap rates) and the same-day correlation of the ratio with the Nikkei
cash return (-0.378 in IS), which is a property of the signal, not a strategy return.

## Sources
| id | source | what | span used | public time (declared) |
|---|---|---|---|---|
| SR | stock-marketdata.com plotly chart `time-series/charts/japan-indicator-short-selling-value.html` (robots.txt: only /wp-admin/ disallowed) | TSE-wide daily short-selling ratio (short-sale value / total auction value, stocks + ETF + REIT + rights, with and without price restriction combined; a copy of JPX's daily "空売り集計"); Nikkei 225 close on the same rows | 2017-01-04 .. 2024-12-30, 1,953 TSE days (rows after 2024-12-31 dropped at parse, asserted) | JPX posts the daily file after the close; declared available by 18:30 JST (09:30 UTC) on day D |
| SR-JPX | www.jpx.co.jp short-selling pages (robots.txt allows all) | daily PDFs (with / without price restriction split) | only 2025-10 onward online (HOLD); monthly PDFs 2021-24 are monthly totals only; old daily URLs return 404 | not usable |
| KN | karauri.net `/up/?date=` and `/down/?date=` (robots.txt disallows only MJ12bot, AhrefsBot, BLEXBot, SemrushBot, baiduspider) | per-stock large short-position reports (holders >= 0.5 % of shares) that increased / decreased on calculation date T: ratio change in % of shares, share change | 2017-01-04 .. 2024-12-30 (requested only for dates <= 2024-12-31) | declared public after the close of T+2 TSE days (conservative; the report is due T+1 and JPX posts it afterwards) |

Family 2 of the brief (price-restricted short share, uptick-rule binding days) needs the with / without restriction
split by day; no free daily copy for <= 2024 was found (JPX daily archive starts 2025-10; stock-marketdata shows the total
only). **Family 2 is dropped before any data: no source.**

## Eras, clocks, costs
- IS 2017-06-28 .. 2021-12-30 (z needs >= 120 past days; the ratio copy starts 2017-01), VAL 2022-01-04 .. 2024-12-30.
  No PRE (no ratio before 2017 in any free source found). HOLD 2025-01..2026-09 closed.
- Day D = TSE trading day of the ratio. Entry E1 (primary) = next TSE day D+1 at 00:05 UTC (09:05 JST, Tokyo open + 5
  min) on IC JP225; variant E0 = D at 10:05 UTC (19:05 JST, OSE night session, after the declared publication time).
- Exits: h1 = one TSE day after the entry at the entry clock (E1: D+2 00:05 UTC; E0: D+1 10:05 UTC); h3 = three TSE
  days after the entry at the entry clock, capped at 120 h. (Wording fixed 06:31 UTC, before any return.)
- Trades non-overlapping per cell (a signal while a position is open is skipped).
- Costs: half the IC spread at the entry and exit minutes (actual M1 ask - bid), JP225 swap per rollover from
  research.swing.rates (about -1.4 bp long, -1.1 bp short per night), 0.6 bp round trip on USDJPY. Variants: spread x1.5,
  +1 minute on both legs.
- Controls (information, never selected): USDJPY at the same clocks (side = JP225 side: a Nikkei rally weakens the yen),
  HK50 at D+1 01:35 UTC (Hong Kong open + 5 min) to the next HK50 trading day 01:35 UTC.

## Signals (all trailing, past values only)
- z_lvl = (ratio_D - mean of the 250 previous TSE days) / their sd (>= 120 days).
- z_res = residual of ratio_D on the same-day Nikkei cash log return, fitted on the previous 250 days only, divided by
  that fit's residual sd (removes the mechanical "high ratio on down days" part, so a result is not just next-day price
  reversal).
- z_chg = trailing z of the day-over-day change in the ratio.
- lvl45 / lvl50 = ratio >= 45 % / >= 50 % (the folk rule's absolute level; practitioner notes say the normal level rose
  to ~40 % after the 2013-14 rule changes and BoJ ETF buying, so 40 % would be most days).
- KN (family 3): for calculation date T, net_pp = sum over reports of the ratio increase (pp of shares outstanding) on
  `/up/` minus the sum of decreases on `/down/`; net_n = number of increase reports minus decrease reports; both as a
  trailing 250-day z. (New and lost reports, `/new/` and `/lost/`, are not pulled, to keep the pull under ~1 h; stated
  limitation.)

## Hypotheses, sides (fixed now) and cells
**Primary side (by mechanism), family 1 = contrarian (folk rule): high ratio -> long JP225, low ratio -> short.**
Reason: the TSE-wide ratio is ~40 % of all auction value and is dominated by price-restricted institutional, HFT and
arbitrage shorts, which are hedged or flat by the close (round 38: FINRA short volume is hedged liquidity provision,
no next-day information), so the informed-short (Diether-Lee-Werner 2009) side has no carrier at the index level. What
can leave a next-session flow is short covering by short-horizon holders (margin shorts by retail and prop, which the
ratio also counts) plus retail who follow the widely published "空売り比率 40 % 超えは底" rule and buy the open. The
DLW / Rapach-Ringgenberg-Zhou informed side (high ratio -> short) is declared as the alternative and reported for
every cell; it can only be a candidate on its own numbers with the doubled cell count.

| family | rule | cells |
|---|---|---|
| R1 | z_lvl > k -> long, z_lvl < -k -> short; k 1.0 / 1.5 / 2.0; h1 / h3; E1 | 6 |
| R1e0 | R1 at entry E0 (same evening, night session) | 6 |
| R2 | lvl45 / lvl50 -> long (one-sided folk rule); h1 / h3; E1 | 4 |
| R3 | z_res, k 1.0 / 1.5, h1 / h3, two-sided as R1; E1 | 4 |
| R4 | z_chg, k 1.5 / 2.0, h1 / h3, two-sided as R1 (a jump in the ratio -> long); E1 | 4 |
| K | **family 3 primary side = informed (build-up of large reported short positions -> short JP225; reductions -> long)**: large reported holders are hedge funds and prime-broker accounts (Morgan Stanley MUFG, Goldman, JPM...) whose positions are deliberate and multi-week; Boehmer-Jones-Zhang 2008 find institutional non-programme shorts informed. net_pp and net_n, k 1.0 / 1.5 / 2.0, h1 / h3; entry T+3 00:05 UTC | 12 |
| headline | R1 k1.5 h1 E1, contrarian | (in R1) |

Total declared JP225 cells: 24 (family 1) + 12 (family 3) = 36 on the primary sides, 72 counting the alternative
sides. Controls: R1 k1.0 / 1.5 h1 on USDJPY and HK50 (4 cells, information).

## Power arithmetic (counts from the parsed series, before any return)
- Signal days: z_lvl k1.0 IS 260 high / 158 low, VAL 105 / 132; k1.5 IS 135 / 75, VAL 47 / 46; k2.0 IS 68 / 20, VAL
  21 / 9. lvl45 IS 224, VAL 167; lvl50 IS 15, VAL 14. z_res and z_chg are similar (z_chg k1.5 IS 75 / 87).
- JP225 1-day sd (00:05 -> 00:05 UTC, 2016-24) 122 bp; IC spread at 00:05 UTC median 2.7 bp, so one round trip with a
  night of swap costs ~4 bp, ~0.03 sd. The cost is small; the problem is the per-trade predictability.
- HOLD ~430 TSE days. Two-sided k1.0 -> ~80-90 trades a year -> ~150 HOLD trades: LIVE needs per-trade net Sharpe
  >= 3 / sqrt(150) = 0.245, i.e. ~30 bp per 1-day trade. k1.5: ~80 HOLD trades -> 0.34 (~41 bp). k2.0: ~35 -> 0.51.
  lvl45: ~100 HOLD trades -> 0.30 (~37 bp). h3 (sd ~210 bp, fewer non-overlapping trades) needs ~50-70 bp.
- DEMO (IS t >= 2, VAL > 0, random >= 90 %): IS n ~418 at k1.0 -> per-trade Sharpe 0.098 (~12 bp net); k1.5 n ~210
  -> 0.14 (~17 bp); k2.0 n ~88 -> 0.21 (~26 bp); lvl45 n 224 -> 0.13 (~16 bp).
- Prior size: aggregate short-flow literature (Wang-Yan-Zheng 2020; round 38's FINRA test) finds ~0 at 1-5 days once
  published; a contrarian folk-rule edge of 3-8 bp per day would give IS t ~0.5-1.4 at k1.0. **LIVE is out of reach
  unless the effect is ~30+ bp a day (several times any published index-level number); DEMO needs 12-26 bp net.**
  Family 3 has the same counts and the same arithmetic.

## Controls and null (fixed now)
- Random entry: 200 seeds, same count and side mix on random tradable TSE days of the same era (a); and (b) side
  recomputed from the unthresholded sign of the signal at the random day.
- Best-of-N: one sign flip per calendar day shared by all cells of a family, 500 draws, max |mid t| over the family's
  cells (both sides counted, so |t|).
- Report by year, IS without 2020-03/04, x1.5 spread, +1 min, VAL / IS.

## Addendum 1 (2026-10-30 06:32 UTC), after the family 1 numbers (R1-R4), before computing R5
R1-R4 were graded at 06:31 UTC (no cell IS net t >= 2 on either side; see STREAM_S.md). One clock the brief names was
not covered: "the folk rule ... may move the open". IC JP225 is a futures CFD, so a retail open is visible only as the
night-to-open move. **R5** (primary side contrarian, as R1): enter D 10:05 UTC (19:05 JST, after publication), exit D+1
00:15 UTC (Tokyo open + 15 min); signals z_lvl k1.0 / k1.5 (two-sided) and lvl45 (long only); 3 cells (6 with the
alternative side). Same costs and controls; no swap unless the hold crosses 21:00 UTC (it does: one rollover).
