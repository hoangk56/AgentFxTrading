# PREREG DRAFT (stream A, round 32): buy risk after a spike in Hacker News "recession" stories (FEARS reversal), DEMO tier

Drafted 2026-10-27 19:13 UTC by stream A. **Not registered, HOLD not opened.** All numbers are IS / VAL / PRE only
(scratchpad `r32/A/out/daily_hn.txt`, `diag_hnfear.txt`, `hnfear_book.txt`).

**Why this is drafted.** The declared family A5-A2 (HYPOTHESES_A.md, 2026-10-27 18:57 UTC) applies Da, Engelberg &
Gao 2015 ("The Sum of All FEARS", RFS 28(1)) to a crowd series: a jump in fear-word attention marks a sentiment-driven
sell-off, and the sell-off reverses over the next days.
- The cells were chosen on IS (q95, h3). With those cells the **EURUSD leg meets the DEMO numbers**.
- The **US500 leg misses DEMO only on its IS random control** (87.9 % vs 90 %). It has the strongest VAL in stream A
  (net t 2.70, 3 / 3 years).

**The stream's view.** This is the only result of the stream with a clean VAL, but it rests on few episodes:
- 21 IS episodes (episode-level t 1.35) and 9 VAL episodes (t 2.35).
- The family's best IS t (2.51) is at chance for its 60 cells (median max 2.53).
- In PRE 2008-15 both FX legs lose: EURUSD -22.0 bp (t -1.30), USDJPY -12.4. US500 has no PRE data.
- The Wikimedia FEARS twin (A2, the same mechanism on pageviews) is negative in IS.

If the lead spends one HOLD look in this stream, it should go to the US500 leg of this rule, not to the BTC draft. A
forward log on data after 2026-09-24 would be the cleaner test.

## Exact rule
- **Series.** Daily counts c(D) of Hacker News stories whose text matches "recession".
  - Source: Algolia `search_by_date`, `tags=story`, `typoTolerance=false`, UTC day of `created_at_i`.
  - `c7(D)` = sum of c over D-6..D.
  - `a(D) = ln(1+c7(D)) - ln(1 + median(c7(D-7), c7(D-14), c7(D-21), c7(D-28)))`, clipped to [-2, 2].
  - `Z(D) = a(D) / sd(a over D-365..D-1)` (>= 120 values, sd > 0).
- **Trigger.** On weekday E, trigger if Z(E-1) >= **1.821**. This is the q95 of Z over IS weekday entries 2016-2021.
  Monday uses Sunday's Z.
- **Trade.** **Long US500** (primary) and **long EURUSD** (second leg), at market at E 07:00 UTC. Exit 3 weekdays
  later at 07:00 UTC; a weekend landing exits Friday 20:00 UTC. Fixed lot, at most 3 open positions per symbol. Each
  trigger day inside an episode opens a new position until the cap.
- **Costs.** Actual IC bid / ask, 0.6 bp commission (EURUSD), swap by `swap_frac_at` (US500 Friday triple, EURUSD
  Wednesday).
- **Caveat on the data.** HN moderation removes some stories after the fact. Today's API counts may differ slightly
  from what was visible in real time; forward use must count stories live.

## Numbers (bp per trade; t clustered in 2-week blocks; power = t x sqrt(1.73 / era years))
| leg / era | n | mid (t) | net (t) | years > 0 | random (300-1000 seeds) | x1.5 / +1 min / +1 day lag |
|---|---|---|---|---|---|---|
| US500 IS 2016-21 | 79 | +42.4 (3.25) | **+32.9 (2.51)** | 6 / 6 | 87.9 % | +31.8 / +32.5 / +27.1 (t 1.34) |
| US500 VAL 2022-24 | 28 | +110.6 (2.94) | **+100.4 (2.70)** | 3 / 3 | 99.8 % | +99.9 / +99.5 / +70.6 (t 1.44) |
| EURUSD PRE 2008-15 | 114 | -19.6 (-1.16) | -22.0 (-1.30) | 2 / 7 | | |
| EURUSD IS | 79 | +17.7 (2.53) | **+14.7 (2.09)** | 4 / 6 | 99 % | +14.6 / +14.6 / +10.4 |
| EURUSD VAL | 28 | +22.0 (0.98) | +19.0 (0.85) | 3 / 3 | 93 % | +18.9 / +18.9 / +11.6 |
| USDJPY (declared, not in the rule) PRE / IS / VAL | 114 / 79 / 28 | | -12.4 / +2.7 / +13.7 | | | |
| book US500 + EURUSD (equal IS risk, post hoc) | 79 / 28 days | | IS 0.27 sd per day (t 3.04), VAL 0.59 sd (t 1.74) | | | |

- **US500 excess over the unconditional long h3.** IS +21.9 bp; VAL +100.1 bp.
- **US500 by episode.**
  - IS: 17 / 21 episodes positive. The worst is 2018-10-18 (-292); the best are 2019-06 (+245) and 2021-10 (+127).
  - VAL: 8 / 9 positive. Among them: 2022-05 (+166), 2024-08-05 yen-carry unwind (+164), 2022-01-27 (+486); the
    loser is 2022-03-29 (-106).
  - The March 2020 crash did not trigger.
- **Neighbouring US500 cells (IS net t).**
  - q95 h5: 2.00. q90 h3: 0.82. q80 h3: 0.71. q95 h1: 0.99.
  - Continuous sign rule: -2.37. Moderate fear spikes are followed by falls; only the top 5 % reverse.
- **Correlation with C3** (book, IS + VAL): daily -0.003, monthly -0.13.

## Bar and expectations
- **US500 leg.**
  - LIVE fails: random 87.9 % < 95 %, and power at the VAL size is 2.70 x sqrt(1.73 / 3) = 2.05 < 3.
  - DEMO fails narrowly, on the IS random control.
- **EURUSD leg.** Meets DEMO on IS / VAL (IS t 2.09, VAL net > 0, random 99 / 93 %), but PRE is negative.
- **Trades.** ~13 trigger days a year in ~4-6 episodes, so ~23 per leg in HOLD.
- **Expected HOLD t.** At the VAL size: US500 ~2.0, EURUSD ~0.65. With the episode clustering, count on ~1.5 for US500.
- **Demo (if run).** ~13 trades a year per leg.
  - **Stop rule:** cut if the cumulative US500 net after 6 episodes is < 0.
  - **Promotion rule:** HOLD + demo pooled t >= 2.5, clustered by episode. At the VAL size this needs about 4-5 years.

## Code
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/A/scripts/`:
- `fetch_hn.py` (download), `sig.py` (Z), `ev.py` / `alib.py` (fills, costs, t, random control);
- `run_daily.py hn`, `diag_hnfear.py`, `hnfear_book.py`.
