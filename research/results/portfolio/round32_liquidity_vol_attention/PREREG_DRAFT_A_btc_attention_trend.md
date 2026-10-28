# PREREG DRAFT (stream A, round 32): BTC abnormal Wikipedia attention x 20-day trend (Kristoufek 2013), DEMO tier

Drafted 2026-10-27 ~19:05 UTC by stream A. **Not registered; HOLD not opened.** The lead decides whether to register
and open HOLD once. Numbers are from IS / VAL only (scratchpad `r32/A/out/daily_wm.txt`, `diag_btc.txt`,
`a3_cap.txt`).

**Recommendation from the stream: do not spend a HOLD look on this before the forward data after 2026-09-24 exists.**
It meets the DEMO numbers, but:
- its IS t is at the stream-wide chance level (2.83 against a median max |Z| of ~2.92 over 195 cells);
- VAL is 0.29 of IS, so the effect is decaying;
- the IS P&L is mostly the attention main effect plus BTC's 2017-21 drift, not the declared trend interaction;
- the expected HOLD t at the VAL size is ~0.7.

## Mechanism and source
Kristoufek 2013 (Sci Rep 3:3415, "BitCoin meets Google Trends and Wikipedia") describes an asymmetric feedback: when
BTC is above its trend, rising public interest pushes it further up; when it is below its trend, rising interest
pushes it further down. Retail attention leads retail flows (Barber & Odean 2008; Da, Engelberg & Gao 2011). Liu &
Tsyvinski 2021 (RFS) find that attention predicts BTC returns at 1-2 weeks. Declared as A3 in HYPOTHESES_A.md
(2026-10-27 18:57 UTC) before any return was computed.

## Exact rule
- **Attention composite Z(D)** for UTC day D: the mean of z_s(D) over the following series.
  - Series: Wikimedia daily pageviews, agent `user`, all-access, for en Bitcoin, en Cryptocurrency, ja ビットコイン,
    ko 비트코인, de Bitcoin, zh 比特币.
  - `a_s(D) = ln(1+v_D) - ln(1 + median(v_{D-7}, v_{D-14}, v_{D-21}, v_{D-28}))`, clipped to [-2, 2].
  - `z_s(D) = a_s(D) / sd(a_s over D-365..D-1)` (>= 120 values).
- **Trigger.** On weekday E, trigger if Z(E-1) >= **0.5018**. This is the q80 of Z over IS weekday entries
  2017-10-02..2021-12-31. Monday uses Sunday's Z.
- **Side.** sign(mid at 20:55 UTC on the last weekday before E, minus the mean of the 20 weekday 20:55 mids before
  that weekday). Up = long, down = short. A zero or missing trend means no trade.
- **Entry and exit.** Enter BTCUSD at market at E 07:00 UTC. The count for E-1 is complete ~01:00 UTC. Exit 5
  weekdays later at 07:00 UTC, capped at 5 x 24 h. A weekend landing exits on Friday at 20:00 UTC. In practice the hold
  is ~4.5 days.
- **Position limits.** At most 3 open positions. A trigger while 3 are open is skipped. Fixed lot, no stop in the
  research rule. A broker guard stop is for the lead to size.
- **Costs.** Actual IC bid / ask, with long financing at IC's 2026 fraction (-4.96 bp a night, the Friday triple
  covering the weekend) and short financing 0.

## Numbers (IS 2017-10..2021-12, VAL 2022-24; bp per trade on the entry mid; t clustered in 2-week blocks)
| variant | IS n / net (t) | VAL n / net (t) | VAL / IS |
|---|---|---|---|
| uncapped (as declared) | 179 / +234.9 (2.83) | 141 / +68.1 (0.90) | 0.29 |
| 3-position cap (rule above) | 151 / +219.1 (2.35) | 119 / +76.3 (0.92) | 0.35 |
| spread x1.5 | +230.2 (2.77) | +66.2 (0.87) | |
| +1 minute | +232.2 (2.79) | +69.5 (0.92) | |
| +1 day publication lag | +271.2 (3.79) | +54.4 (0.74) | |

- **Mid:** IS +260.9 (t 3.12), VAL +85.0 (t 1.12).
- **Years:**
  - IS: 2017 (Q4) +504, 2018 +329 (all short), 2019 +105, 2020 +364, 2021 +88.
  - VAL: 2022 -71, 2023 +154, 2024 +101.
  - IS without 2017: +201 (t 2.17). Monthly clusters: IS t 2.66, VAL t 0.81.
- **Random control.** 300 seeds, the trend side recomputed at random weekdays at 07:00. Beats 99.0 % (IS) and 98.7 %
  (VAL).
- **Attention vs trend alone.** Trend-following every weekday (same side rule, h5): IS +72.6 (t 1.69), VAL -25.4
  (t -0.64).
- **OLS (h5 long return, IS / VAL).**
  - The interaction I(Z >= q80) x trend: +79 (t 0.65) / +121 (t 1.36).
  - I(Z >= q90): +284 (t 1.47) / +52 (t 0.46).
  - In IS the gain is mostly "high attention -> up" on top of the drift. VAL leans more on the declared interaction.
- **Correlation with C3** (P&L on exit days, IS + VAL): daily 0.011, monthly 0.036.
- **Cells tried.** 24 in A3 (q80 / q90 / q95 / continuous x h1 / h3 / h5 x BTC / ETH) and 195 in the stream. The
  median max |Z| is 2.19 for 24 cells and 2.92 for 195.
- **ETH, same rule (information).** IS +174 (t 1.39), VAL +96 (t 1.24). It points the same way, but IC's ETH cost in
  2018-20 was 90-250 bp.
- **Replication on an independent crowd fails in VAL** (post hoc, declared in the addendum before it was run). Same
  q80 / h5 cell, with Hacker News "bitcoin" story counts in place of Wikipedia:
  - BTC: IS +181.6 (t 2.04), VAL -32.4 (t -0.48). Only 169 of ~370 trigger days are shared with Wikipedia.
  - ETH: IS -8.2, VAL -160.8.
- **Breadth: no dose response in IS** (post hoc). IS net by the number of editions >= 1 sd on the trigger day:
  - 0-1 editions: +294 (n 43); 2-3 editions: +226 (n 74); 4-6 editions: +205 (n 62).
  - VAL is monotone the other way: -35 / +6 / +171.

## Bar and expectations
- **DEMO bar met on IS / VAL.** IS t >= 2.0 (2.83 uncapped, 2.35 capped), VAL net > 0, random >= 90 %, x1.5 and
  +1 min > 0.
- **Not LIVE.** VAL t 0.90 and power ~0.7.
- **Expected HOLD (2025-01..2026-09-24).** ~45 triggers a year, so ~78 trades (fewer with the cap). The expected HOLD
  t at the VAL size is 0.90 x sqrt(1.73 / 3) ≈ **0.68**. At round 18's 1/4-of-VAL rule for post-look selections
  (the cell was chosen on IS, VAL read once) it is ~0.2.
- **Demo.** ~45 trades a year, max 3 open.
  - **Stop rule:** cut if the cumulative net after 40 demo trades is < 0, or if the cumulative net after 80 trades is
    below -1 sd of the trade distribution (≈ -700 bp in total).
  - **Promotion rule:** HOLD + demo pooled t >= 2.5. At the VAL size this needs about 6-7 years of trades.

## Code
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r32/A/scripts/`:
- `sig.py` (composites), `alib.py` (fills / costs, from r31 J `jlib.py` with metals commission), `ev.py` (cells,
  random control), `run_daily.py`, `run_daily_helpers.py` (trend), `a3_cap.py`, `diag_btc.py`, `c3corr.py`.
- For HOLD, the Wikimedia series must be re-downloaded to 2026-09-24. This stream requested data only to 2024-12-31.
