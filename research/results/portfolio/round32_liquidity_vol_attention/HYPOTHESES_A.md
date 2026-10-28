# Round 32, stream A: hypotheses (public attention and crowd data)

Written 2026-10-27 18:57 UTC (`date -u`), **before any return was joined to an attention series**. What was loaded by
then: Wikimedia daily pageviews (36 edition-articles, 2015-07-01..2024-12-31, requested with end date 20241231, so no
2025-26 value was ever downloaded) and the unconditional sd / cost of D+1 07:00 UTC -> +h weekday returns per symbol
(no signal joined). HN Algolia story counts were still downloading. HOLD 2025-01-01..2026-09-24 stays closed.

## Data and publication lags (part of every rule)
- **Wikimedia pageviews** (`/metrics/pageviews/per-article/<lang>.wikipedia/all-access/user/<title>/daily/...`).
  Agent `user` (excludes self-identified spiders; the `automated` class exists only from 2020-05). The count for UTC
  day D is complete after D+1 ~01:00 UTC. **Every entry is at D+1 07:00 UTC or later** (6 h margin). The signal of a
  weekday entry E is the last complete day E-1 (Monday uses Sunday). Lag check: the same rule entered at E+1 07:00
  (one more day of delay) is reported for every selected cell.
- **HN Algolia** (`hn.algolia.com/api/v1/search_by_date`, tags=story, no typo tolerance): story timestamps are
  public in real time; same entry convention (D+1 07:00 UTC).
- No history before 2015-07 exists for per-article pageviews through the API (the legacy pagecounts endpoint has only
  project totals; the raw hourly dumps are hundreds of GB). So the eras are **IS 2016-01..2021-12** (BTC / ETH from
  IC's start 2017-09) and **VAL 2022-01..2024-12**; no PRE for Wikimedia. HN starts 2007-02, so the HN fear rule has a
  **PRE 2008-2015** era on USDJPY and EURUSD (Dukascopy M1, PRE cost convention).

## Signal construction (fixed now)
- Per series s: `a_s(D) = ln(1+v_D) - ln(1 + median(v_{D-7}, v_{D-14}, v_{D-21}, v_{D-28}))` (same-weekday 4-week
  baseline, removes the weekly cycle; the daily analogue of Da, Engelberg & Gao's ASVI), clipped to [-2, +2].
- `z_s(D) = a_s(D) / sd(a_s over D-365..D-1)` (at least 120 values, else missing).
- Target composite `Z(D)` = mean of the available `z_s(D)` of its member series.
- Membership rule (views only, no returns): a series enters only if its IS median >= 100 views a day and its level
  has no page-move break (median VAL / IS between 0.2 and 5). This drops ja 日本円, 円高, 円安 (2-11 views a day),
  ko 이더리움 (63), de Rezession (38) and en Depression_(economics) (266 -> 23, the page was moved).
- HN series (low counts): `c7(D)` = stories over D-6..D; `a(D) = ln(1+c7_D) - ln(1+median(c7 at D-7, -14, -21, -28))`,
  then z as above.

| composite | members |
|---|---|
| BTC | en Bitcoin, en Cryptocurrency, ja ビットコイン, ko 비트코인, de Bitcoin, zh 比特币 |
| ETH | en Ethereum, ja イーサリアム, de Ethereum, zh 以太坊 |
| GOLD | en Gold, en Gold_as_an_investment, de Gold, de Goldpreis, ja 金, zh 金, hi सोना |
| SPX | en S&P_500, en Stock_market |
| JPFX | ja 外国為替証拠金取引 (FX margin trading), en Japanese_yen |
| FEARS | en Recession, en Stock_market_crash, en Financial_crisis, en Inflation, en Unemployment, en Bankruptcy, de Börsenkrach |
| FIN (A4 only) | FEARS en members + en Stock_market + en S&P_500 |
| HN-BTC / HN-ETH / HN-FEAR | HN stories matching "bitcoin" / "ethereum" / "recession" |

## Cells (common grid)
Entry D+1 07:00 UTC (weekdays), exit h weekdays later at 07:00 (r31 J `exit_ms`: capped at 5 x 24 h, a weekend landing
exits Friday 20:00 UTC). Threshold variants: **q80, q90, q95** = enter when Z(D) >= that quantile of Z over the era-IS
weekdays (fixed side), and **C** = trade every weekday, side = declared side x sign(Z(D)) (long-high / short-low
version of the same mechanism, the only variant with LIVE-sized trade counts). h in {1, 3, 5}. **12 cells per
family x target.** Parameters (threshold, h) chosen on IS by net t, then VAL read once.

Costs: actual IC bid / ask at entry and exit minutes (r31 J `trade`), commission 0.6 bp round trip for FX **and
metals**, swap by `swap_frac_at` per 17:00 NY rollover (FX / metals triple Wednesday, others Friday); BTC / ETH use
IC's 2026 fraction (long -4.96 / -4.82 bp a night, short 0) with the Friday triple covering the weekend. Robustness:
spread x1.5, +1 minute, +1 day lag. t: per trade for h = 1; clustered in 10-weekday blocks for h = 3, 5 (overlap).
Random control for a cell near a bar: same count, side mix and h on random weekdays of the same era at 07:00, 500
seeds; for data-dependent sides (A3) the side is recomputed at the random date.

## Hypotheses
| id | mechanism and source | rule (side fixed) | targets | cells |
|---|---|---|---|---|
| A1 | Abnormal attention to an asset -> retail net buying (Barber & Odean 2008, RFS 21(2): individuals are net buyers of attention-grabbing assets) -> temporary price pressure over the next 1-2 weeks (Da, Engelberg & Gao 2011, JF 66(5); for BTC, Liu & Tsyvinski 2021, RFS 34(6): +1 sd Google searches -> about +2.3 % over 2 weeks; one-week tweets +2.5 %) | Z_own(D) >= q -> **long** (C: long if Z > 0, short if Z <= 0) | BTCUSD (BTC), ETHUSD (ETH), XAUUSD (GOLD), US500 (SPX), USDJPY (JPFX: Japanese retail FX traders mostly hold foreign currency against the yen, BoJ Review 2023-E-7, so attention to FX margin trading -> **long USDJPY**) | 60 |
| A2 | Fear-word attention = household sentiment (Da, Engelberg & Gao 2015, RFS 28(1), "FEARS"): a rise coincides with low returns on day t and **predicts a reversal over t+1..t+2** | FEARS Z(D) >= q -> **long** the risk asset at D+1 07:00 (C: long if Z > 0 else short) | US500; USDJPY (yen safe-haven bid reverses -> long USDJPY); EURUSD (USD safe-haven bid reverses -> long EURUSD); BTCUSD (risk asset) | 48 |
| A3 | Kristoufek 2013 (Sci Rep 3:3415): BTC attention amplifies the current deviation from trend (above trend: more interest -> up; below trend: more interest -> down) | Z_own(D) >= q -> side = sign(mid at D 20:55 UTC - mean of the 20 previous 20:55 mids) (C: side = sign(trend) x sign(Z)) | BTCUSD, ETHUSD | 24 |
| A4 | Moat, Curme, Avakian, Kenett, Stanley & Preis 2013 (Sci Rep 3:1801): rising views of financial-topic Wikipedia pages precede stock falls; weekly rule, page views of week t vs the mean of the previous dt weeks; rise -> short the DJIA from the close of week t+1's first trading day for one week, fall -> long. Reported +27 bp vs -21 bp next-week DJIA (2007-12..2012-04) | per FIN page, sign of (week t views - mean of previous dt weeks), weeks Mon-Sun UTC; position = -mean of the page signs (in [-1, 1]); enter **Monday 20:55 UTC** of week t+1, h = 5 (exits Friday 20:00 UTC by the cap) | US500 | 3 (dt = 1, 2, 3; dt = 3 is the paper's main value) |
| A5 | A1 and A2 on a second crowd: Hacker News story counts (tech-heavy retail crowd, real-time) | HN-BTC / HN-ETH Z >= q -> long BTC / ETH; HN-FEAR Z >= q -> long US500, USDJPY, EURUSD (C variants as above) | BTCUSD, ETHUSD, US500, USDJPY, EURUSD; PRE 2008-15 for USDJPY, EURUSD | 60 |
| I1 | information only, a data check: attention predicts next-day volatility (Urquhart 2018, Econ Lett 166; Smith 2012 for FX) | corr(Z(D), abs return D+1 07:00 -> D+2 07:00) | each composite on its target | not graded |

**Total graded cells: 195** (A1 60, A2 48, A3 24, A4 3, A5 60). Chance benchmark: median of max |Z| over 195
independent cells ~2.92 (12 cells ~1.91, 24 ~2.19, 48 ~2.45, 60 ~2.53).

## Power arithmetic (before any return; frontier convention of r16 STREAM_X / r10: power = per-trade net Sharpe x sqrt(1.73 x trades a year))
Unconditional sd of the D+1 07:00 -> +h trade (bp, mid; IS / VAL) and median round-trip cost incl. long swap (VAL):

| symbol | sd h1 | sd h5 | cost h1 / h5 (VAL) |
|---|---|---|---|
| BTCUSD | 497 / 351 | 915 / 648 | 8 / 27 (IS 14 / 30) |
| ETHUSD | 603 / 437 | 1140 / 806 | 20 / 35 (IS 123 / 138: IC's ETH spread 2018-20) |
| XAUUSD | 85 / 88 | 163 / 163 | 2.6 / 6.4 |
| US500 | 102 / 111 | 178 / 208 | 3.9 / 12.5 |
| USDJPY | 51 / 67 | 98 / 126 | ~0 (positive carry long) |
| EURUSD | 44 / 50 | 82 / 91 | 1.3 / 3.5 |

Trades a year and the per-trade net Sharpe LIVE needs (power 3 over the 1.73-year HOLD): q95 ~13 -> 0.64; q90 ~26 ->
0.45; q80 ~52 -> 0.32; C (every weekday, h1) ~255 -> 0.14 (h5 overlapping: ~0.14 x sqrt(5) per trade, ~0.32).
Net edge per trade LIVE needs at the VAL sd:

| symbol | q80, h1 | C, h1 |
|---|---|---|
| BTCUSD | ~111 bp | ~50 bp |
| ETHUSD | ~140 | ~62 |
| XAUUSD | ~28 | ~12.4 |
| US500 | ~35 | ~15.6 |
| USDJPY | ~21 | ~9.5 |
| EURUSD | ~16 | ~7.0 |

DEMO needs IS t >= 2: at q80 (~310 IS trades) a per-trade Sharpe ~0.11; at C (~1,500) ~0.052.

What the literature implies:
- A1 BTC (Liu & Tsyvinski): 2.3 % per sd over 10 trading days = ~23 bp a day per sd, against a daily sd of 350-500
  bp: a z-weighted daily position has Sharpe ~0.05 -> **power ~1.0 for C, ~1.5-1.8 for q80 / h5**. Their sample was
  2011-2018 (the bubble years); our IS starts 2017-09.
- A1 on XAU / US500 / USDJPY: Da et al. 2011 find the price pressure in small, retail-held stocks and little in large
  caps; for an index or a major the prior is a correlation <= 0.02 -> power < 0.5.
- A2 (FEARS): a few bp of reversal per sd on a 100 bp daily sd -> Sharpe <= 0.05 -> power <= 1.
- A4 (Moat): (+27 + 21) / 2 = ~24 bp per weekly trade against a ~250-300 bp weekly sd -> Sharpe ~0.08-0.10 at 52
  trades a year -> **power ~0.8-0.9** even at the paper's (crisis-period, pre-publication) size.
- **Prior: LIVE needs 2-3x the literature's effect on BTC and >= 5x elsewhere; DEMO is reachable only for A1-BTC /
  A3 at about the literature's size.**

## Addendum 2026-10-27 19:01 UTC (after the Wikimedia A1-A4 results, before any HN return)
**Post hoc, marked as such.** Two BTC cells met DEMO numbers on Wikimedia: A1 q90 h3 and A3 q80 h5. Checks added,
none of them graded as a new family:
- **A3-HN** (replication on an independent crowd): the A3 rule with the HN-BTC composite in place of the Wikimedia
  BTC composite, the same q80 / h5 cell only (threshold = q80 of HN-BTC Z over IS weekdays). Expected if the A3 effect
  is attention and not the IS bull drift: IS and VAL net > 0. Also A3-HN on ETH (q80 h5).
- Diagnostics already run on A1 / A3 (years, 2017 removed, monthly clusters, an OLS with prior 1 / 5-day returns and
  the trend sign, a prior-5-day-return momentum control, the 3-open-positions cap) are reported as post hoc.
- Correction 19:14 UTC: the chance benchmarks above were recomputed exactly (48 cells 2.43 -> 2.45, 60 cells 2.50 -> 2.53). Nothing else in this file was changed after the first return.
