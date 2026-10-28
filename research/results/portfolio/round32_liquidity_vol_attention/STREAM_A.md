# Round 32, stream A: public attention and crowd data (Wikipedia pageviews, Hacker News)

Written 2026-10-27, 18:44-19:15 UTC (`date -u`). Hypotheses were declared before any return was computed:
[HYPOTHESES_A.md](HYPOTHESES_A.md), written 18:57 UTC, with a post-hoc addendum at 19:01. HOLD
(2025-01..2026-09-24) stayed closed:
- every Wikimedia request ended at 2024-12-31;
- HN timestamps were cut at < 2025-01-01;
- IC prices were cut at ts < 2025-01-01 when loaded.

## Answer
- **No LIVE candidate.**
- **Two drafts at the DEMO edge.** Neither is a clean DEMO pass:
  1. **[PREREG_DRAFT_A_hn_fear_reversal.md](PREREG_DRAFT_A_hn_fear_reversal.md).** After a spike in Hacker News
     "recession" stories (top 5 % of days), buy US500 and EURUSD at the next 07:00 UTC and hold 3 days. This is Da,
     Engelberg & Gao's FEARS reversal.
     - US500: net IS +32.9 bp (t 2.51), VAL +100.4 (t 2.70), 9 / 9 years > 0, random control 87.9 % / 99.8 %.
       It misses DEMO only on the IS random control.
     - EURUSD: meets the DEMO numbers (IS t 2.09, VAL +19.0, random 99 / 93 %), but PRE 2008-15 is -22.0 (t -1.30).
     - Episode-level t is 1.35 in IS (21 episodes) and 2.35 in VAL (9 episodes). The family is at chance (best of 60
       cells 2.51, median max 2.53).
     - The stream's pick if one HOLD look is spent here.
  2. **[PREREG_DRAFT_A_btc_attention_trend.md](PREREG_DRAFT_A_btc_attention_trend.md).** Kristoufek's rule on BTC:
     when abnormal Wikipedia attention to Bitcoin is in its top 20 %, follow the 20-day trend for 5 days.
     - Net IS +235 bp (t 2.83), VAL +68 (t 0.90), random control 99 / 99 %. This meets the DEMO numbers.
     - VAL is only 0.29 of IS; the Hacker News replication fails in VAL (-32 bp); there is no dose response in IS.
     - Expected HOLD t ~0.7. Not recommended for HOLD.
- **The other families give nothing.**
  - Own-asset attention leading to retail price pressure (gold, US500, Japanese retail FX) has no effect.
  - FEARS on Wikipedia pageviews goes the wrong way in IS.
  - Moat et al. 2013's weekly Wikipedia rule fails.
  - The BTC "attention -> long" cells (IS t up to 2.71) are BTC's 2017-21 drift and momentum. A momentum control
    (prior 5-day return in the top decile, long, 3 days) makes +350 bp (t 3.59) in IS, the same as the attention cell,
    and VAL random is 78 %.
- **Power before the numbers (HYPOTHESES_A).** At the literature's effect sizes, LIVE was out of reach: power ≈ 1.0
  for BTC, below 1 for FEARS / Moat, and below 0.5 for indices and majors. LIVE needed 2-3x the literature on BTC and
  >= 5x elsewhere. The data match that.

## Sources (fetch log: scratchpad `web/requests.log`, 710 lines)
| source | fetched | history used | usable? |
|---|---|---|---|
| Wikimedia REST pageviews, per article, daily, agent `user` | 36 edition-articles, one request each with end date 20241231; 20 answered 429 with a browser UA at 1.1 s spacing, all retried at 5 s + 60 s back-off | 2015-07-01..2024-12-31 (de Ethereum from 2016-02, zh 以太坊 from 2016-06) | **yes.** 30 series kept. Dropped by the views-only rule (IS median < 100, or a page-move break): ja 日本円 / 円高 / 円安 (2-11 views a day; the real articles sit under other titles), ko 이더리움, de Rezession, en Depression_(economics) (266 -> 23 a day after a page move) |
| Wikimedia per-article data before 2015-07 | not fetched | | **no.** The API's legacy endpoint has project totals only; the hourly pagecounts dumps (2007-2016) are hundreds of GB. No PRE for pageviews |
| Hacker News via Algolia `search_by_date` (stories; windows split below 1,000 hits) | 646 requests, all 200 | "bitcoin" 26,136 stories (2009-24), "ethereum" 4,706 (2014-24), "recession" 2,159 (2007-24) | **yes.** Low counts, so the 7-day sum is used. PRE 2008-15 exists for FX |
| Literature | 3 WebSearch, 2 WebFetch | Moat et al. 2013 full text (PMC); FEARS working-paper PDF (403); Liu & Tsyvinski via a secondary summary | |
| Not tried, out of scope or reach | | | Google Trends (unreachable per brief), Reddit (unreachable in r31), X / Twitter (account + paid API), GitHub commit activity (60 req/h unauthenticated; developer activity is not a retail-flow proxy), Stack Exchange (300 req/day; same crowd as HN, lower counts) |

Publication lag, built into every rule:
- **Wikimedia:** a UTC day's count is complete ~01:00 UTC the next day. Entry is at D+1 07:00 UTC.
- **HN:** stories are public in real time; the same entry is used.
- **Lag check:** every selected cell was rerun with one more day of delay.

## Results
- **Units.** bp per trade on the entry mid; costs are actual IC bid / ask, plus 0.6 bp commission (FX and gold),
  plus swap. BTC / ETH pay IC's 2026 long financing of -4.96 / -4.82 bp a night.
- **t.** Per trade for h1; for h3 / h5, clustered in 2-week blocks.
- **pow.** Net t x sqrt(1.73 / 6) on IS and x sqrt(1.73 / 3) on VAL, i.e. the expected HOLD t at that era's size. For
  BTC / ETH, whose IS is 4.25 years, multiply the IS value by 1.19.
- **Cell choice.** Cells were chosen per family x target on IS net t from 12 (q80 / q90 / q95 / continuous x h1 / h3
  / h5).

| hypothesis (IS-chosen cell) | eras | mid IS (t) / VAL (t) | cost (VAL, approx.) | net IS (t) / VAL (t) [/ PRE] | VAL / IS | per-trade Sharpe IS / VAL; pow IS, VAL | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| A1 BTC Wikipedia attention -> long, q90 h3 | IS 17-21, VAL | +388 (2.92) / +114 (1.01) | ~25 | +355 (2.71) / +90 (0.79) | 0.25 | 0.37 / 0.15; 1.46, 0.60 | 1.00 / 0.78 | none (VAL random < 90 %; = BTC momentum, see below) |
| A1 ETH -> long, q80 h3 | IS, VAL | +303 (2.56) / -2 (-0.02) | 35 (IS ~140) | +172 (1.43) / -37 (-0.37) | < 0 | 0.14 / -0.05 | n/r | none |
| A1 GOLD (7 editions incl. de / ja / zh / hi) -> long, q90 h1 | IS, VAL | +6.0 (0.82) / +9.3 (0.75) | 2.6 | +3.6 (0.48) / +6.1 (0.49) | 1.7 | 0.04 / 0.06; 0.26, 0.37 | n/r | none |
| A1 SPX (S&P 500, Stock market) -> long, q80 h5 | IS, VAL | +17.8 (0.98) / +44.5 (1.94) | 12.5 | +7.7 (0.43) / +32.2 (1.40) | 4.2 | 0.04 / 0.16; 0.23, 1.06 | n/r | none (IS t) |
| A1 JPFX (ja FX margin trading, Japanese yen) -> long USDJPY, q95 h1 | IS, VAL | +10.3 (1.60) / +4.0 (0.46) | ~0 | +9.5 (1.48) / +4.2 (0.48) | 0.44 | 0.17 / 0.06; 0.80, 0.36 | n/r | none |
| A2 FEARS (Wikipedia, 7 pages) -> long US500, q95 h1 | IS, VAL | -6.0 (-0.32) / +8.3 (0.37) | 3.9 | -10.7 (-0.57) / +3.5 (0.15) | | < 0 | n/r | none; the declared side is wrong in IS (continuous h3 mid -11.1, t -2.05), and VAL goes back to the declared side |
| A2 FEARS -> long USDJPY, C h5 | IS, VAL | +8.8 (1.81) / -4.1 (-0.70) | ~0 | +7.0 (1.44) / -6.2 (-1.02) | < 0 | 0.07 / -0.05 | n/r | none |
| A2 FEARS -> long EURUSD, q90 h5 | IS, VAL | -0.1 / -5.6 | 3.5 | -3.5 (-0.20) / -8.9 (-0.75) | | < 0 | n/r | none |
| A2 FEARS -> long BTC, q95 h1 | IS, VAL | +45.6 (0.50) / +4.2 (0.05) | 8 | +14.2 (0.16) / -8.9 (-0.10) | | ~0 | n/r | none |
| **A3 BTC attention x 20-day trend, q80 h5** | IS, VAL | +261 (3.12) / +85 (1.12) | ~27 | **+235 (2.83) / +68 (0.90)**; 3-position cap +219 (2.35) / +76 (0.92) | 0.29 | 0.24 / 0.10; 1.52 (1.81 at 4.25 y), 0.68 | 0.99 / 0.99 | **DEMO numbers, drafted** (decaying; HN replication fails) |
| A3 ETH, q80 h5 | IS, VAL | +310 (2.53) / +125 (1.62) | 35 (IS ~140) | +174 (1.39) / +96 (1.24) | 0.55 | 0.15 / 0.11; 0.75, 0.94 | n/r | none (IS t) |
| A4 Moat et al. weekly FIN pages -> US500, dt 1 (IS-best of 1 / 2 / 3) | IS, VAL | +7.2 (0.89) / -2.1 (-0.18) | ~4 | +3.7 (0.46) / -5.0 (-0.44); dt 3 (paper's): +3.3 (0.37) / -11.7 (-1.04) | < 0 | 0.03 / -0.04 | 0.81 / 0.58 | none |
| A5 HN "bitcoin" -> long BTC, q80 h3 | IS, VAL | +261 (2.78) / +41 (0.59) | 25 | +229 (2.45) / +16 (0.24) | 0.07 | 0.24 / 0.03; 1.32, 0.18 | 1.00 / 0.46 | none (= BTC drift) |
| A5 HN "ethereum" -> long ETH, q90 h5 | IS, VAL | +135 (0.95) / +109 (0.73) | 35 (IS ~140) | -26 (-0.18) / +73 (0.49) | | | n/r | none |
| **A5 HN "recession" -> long US500, q95 h3** | IS, VAL | +42.4 (3.25) / +110.6 (2.94) | ~10 | **+32.9 (2.51) / +100.4 (2.70)** | 3.1 | 0.27 / 0.65; 1.35, 2.05 | **0.879** / 0.998 | **misses DEMO on the IS random control; drafted with the EURUSD leg** |
| A5 HN "recession" -> long USDJPY, q95 h5 | PRE 08-15, IS, VAL | +5.8 (0.43) / +18.7 (0.56) | ~0 | +4.8 (0.35) / +20.1 (0.60) / PRE -5.3 (-0.22) | | 0.06 / 0.15 | n/r | none |
| **A5 HN "recession" -> long EURUSD, q95 h3** | PRE, IS, VAL | +17.7 (2.53) / +22.0 (0.98) | 3.1 | **+14.7 (2.09) / +19.0 (0.85)** / PRE -22.0 (-1.30) | 1.3 | 0.27 / 0.21; 1.12, 0.64 | 0.99 / 0.93 | **DEMO numbers on IS / VAL, PRE negative; drafted** |

"n/r" = not run. The random control was run only for cells with IS net t > 1.5:
- same count and h, on random weekdays of the same era at 07:00;
- sides permuted, or for A3 recomputed from the trend at the random date;
- 300 seeds; 1,000 for the HN-recession US500 cell.

### Post-hoc diagnostics (declared in the addendum, not graded)
- **A1 BTC is momentum in the BTC bull era.**
  - Years: IS 2017 Q4 +1,220 bp, 2018 +534 (n 2), 2019 +339, 2020 +396, 2021 -119; VAL 2022 -220, 2023 +37,
    2024 +238.
  - A momentum-only control (prior 5-day return >= the IS q90, long h3) gives IS +350 (t 3.59) and VAL +55 (t 0.56).
  - OLS of the h3 long return on I(Z >= q90) with prior 1d / 5d returns and the trend: +288 (t 1.72) IS, +54 (t 0.46)
    VAL.
- **A3 BTC.**
  - IS years are all positive (2018 is all short, +329). Without 2017: +201 (t 2.17). Monthly clusters: IS t 2.66.
  - Trend-following alone (same side every weekday): IS +73 (t 1.69), VAL -25.
  - The OLS interaction (attention x trend): IS +79 (t 0.65), VAL +121 (t 1.36). So the IS gain is "high attention ->
    up" plus drift; VAL leans on the declared interaction.
  - Breadth (editions >= 1 sd): no dose response in IS (+294 / +226 / +205 from narrow to broad); VAL monotone
    (-35 / +6 / +171).
  - Replication with HN "bitcoin": IS +182 (t 2.04), VAL -32 (t -0.48). ETH: IS -8, VAL -161.
  - Correlation with C3: daily 0.011, monthly 0.036.
- **HN recession -> US500.**
  - IS: 79 trades in 21 episodes, 17 positive, episode-level t 1.35; excess over the unconditional long h3: +21.9 bp.
  - VAL: 28 trades in 9 episodes, 8 positive, episode-level t 2.35; excess +100.1 bp.
  - The March 2020 crash did not trigger.
  - Only the top 5 % reverses: q80 / q90 h3 IS t 0.71 / 0.82, and the continuous rule is negative (t -2.37).
  - US500 + EURUSD book at equal IS risk: IS t 3.04, VAL 1.74.
  - The FX legs fail in PRE 2008-15: EURUSD -22.0 (t -1.30), USDJPY -12.4. US500 has no PRE.
  - Correlation with C3: daily -0.003, monthly -0.13.
- **I1, attention vs next-day |return| (data check).** corr +0.07 BTC, +0.06 FEARS -> US500, about 0 for gold and
  USDJPY. It is weak because the abnormal measure is relative to the same weekday 1-4 weeks back. Pageview spikes
  lag the move that caused them.

## Multiple testing
| family | cells | best IS net t | median max \|Z\| for K | against chance |
|---|---|---|---|---|
| A1 (Wikipedia, own asset) | 60 | 2.71 (BTC) | 2.53 | slightly above; explained by BTC momentum |
| A2 (Wikipedia FEARS) | 48 | 1.44 (positive side) | 2.45 | below |
| A3 (attention x trend) | 24 | 2.83 (BTC) | 2.19 | above |
| A4 (Moat weekly) | 3 | 0.46 | 1.26 | below |
| A5 (HN) | 60 | 2.51 (US500 recession) | 2.53 | at chance |
| **stream** | **195** (+2 post hoc) | **2.83** | **2.92** | **at chance** |

The cells are highly correlated within a target, because thresholds and holds are nested. The effective K is
smaller, so the benchmark above is conservative for any one family but right for the stream. The large negative t's
(ETH continuous h1 -7.1, US500 FEARS continuous h3 -3.48) are costs of daily flipping, and the wrong side,
respectively.

## What this says
1. **Public attention measured by Wikipedia or HN does not carry a 1-5 day price-pressure signal on gold, US500 or
   the yen.** The Barber-Odean / Da (2011) retail-buying story needs a retail-held asset with an attention-driven flow.
   At IC's majors and indices it is below even the literature's small size.
2. **On BTC, attention spikes coincide with momentum in the 2017-21 bull market.** Conditioning on attention adds
   nothing beyond prior returns in IS, and the effect is gone in VAL. The trend interaction (Kristoufek) survives
   random controls in both eras but decays (VAL / IS 0.29) and fails an independent crowd series.
3. **The fear-reversal mechanism (Da et al. 2015) shows up only at the extreme tail of a slow crowd series (HN
   "recession", 7-day sum), and only for US equities in 2016-24.**
   - Moderate fear predicts further falls: the continuous rule's IS t is negative on both Wikipedia and HN.
   - The extreme-tail cell is strong in VAL but rests on ~30 episodes in nine years, and its FX legs fail in 2008-15.
   - That pattern looks like "buy capitulation" in a bull market, not a stable flow.
4. **Not a LIVE route at IC.** Attention data are daily and spiky, so trades come in clusters and the honest unit is
   the episode: 3-6 a year. The LIVE frontier at 1-5 days (per-trade Sharpe 0.32 at 52 trades a year) cannot be met
   by an episodic signal. A continuous attention signal would be needed, and none was positive.

## Directions that need the user (one-line value estimates)
- **Google Trends or SVI history** (the actual series of Da et al. 2011 / 2015; unreachable from this Mac, no public
  API). Same mechanism as tested here on a broader crowd. LIVE ~1 %, DEMO ~5 %.
- **X / Twitter post counts** (Liu & Tsyvinski's strongest BTC attention proxy; paid API with an account). BTC
  attention was momentum in IS and nothing in VAL here. LIVE ~1 %.
- **Wikimedia hourly pagecounts dumps 2007-2016** (free, but hundreds of GB). They would give a PRE era for the
  pageview rules and intraday entry hours sooner after a spike. LIVE < 1 %. Worth it only if the HN fear rule passes
  a forward check.
- **Forward log on data after 2026-09-24** for the HN-recession rule. HN is live and free; the rule needs only the
  IC US500 / EURUSD quotes the lead already pulls. This is the cleanest test of the one interesting result. DEMO at
  most; ~13 trades and ~5 episodes a year.

## Scripts and outputs
Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/A/`

- **Fetching:**
  - `scripts/fetch.sh`: logged curl, 1.1 s sleep;
  - `scripts/wm_list.txt`: the 36 articles;
  - `scripts/fetch_hn.py`: Algolia window enumeration;
  - `scripts/parse_wm.py`: run with `python -I`; cuts at 2024-12-31.
- **Signals and engine:**
  - `scripts/sig.py`: abnormal attention, z, composites, weekly FIN totals;
  - `scripts/alib.py`: r31 J's `jlib.py` with metals commission and metals' Wednesday triple;
  - `scripts/ev.py`: cells, t, random control;
  - `scripts/run_daily_helpers.py`: trend sign.
- **Runs:**
  - `scripts/power.py`: unconditional sd and cost;
  - `scripts/run_daily.py wm|hn`: A1, A2, A3, A5;
  - `scripts/run_A4.py`: A4 and I1;
  - `scripts/diag_btc.py`, `a3_cap.py`, `a3_breadth.py`, `a3hn.py`, `c3corr.py`, `diag_hnfear.py`,
    `hnfear_book.py`.
- **Outputs:**
  - `out/daily_wm.txt` / `.json`, `out/daily_hn.txt` / `.json`, `out/A4_I1.txt`, `out/diag_*.txt`, `out/a3_*.txt`,
    `out/hnfear_book.txt`;
  - parsed series `out/wm.npz` and `out/sig.npz`;
  - raw downloads in `web/wm/` and `web/hn/`.
