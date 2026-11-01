# Stream U: short Binance perps around scheduled token unlocks (BTC-hedged), 2026-10-31

Written 2026-10-31 15:59 UTC (from `date -u`). Declared in [HYPOTHESES_U.md](HYPOTHESES_U.md) (15:50 UTC, power
table appended 15:54 UTC, both before any price was loaded). Code: `code/` (`map_protocols.py`, `pull_schedules.py`,
`pull_funding.py`, `events.py`, `run.py`); full tables in `code/output_primary.txt` and `code/output_fallback.txt`.
HOLD (2025-01-01..) was never loaded: prices are cut at ts < 2025-01-01, and events whose exit falls in 2025 are dropped.

## Answer: no LIVE or DEMO candidate
All 8 declared cells lose money in IS (2020-21) and make money in VAL (2022-24). The VAL effect is real but small
(+0.7 to +1.4 % per event, t_week 0.8-1.7), it sits mostly in 2024, and it fails both the IS bar (t >= 2.5 LIVE,
>= 2.0 DEMO) and, on the fallback split, the DISCOVERY bar. No PREREG_DRAFT is written.

## Data
- Schedule: DefiLlama emissions. `api.llama.fi/emissions` answers HTTP 402 (paid plan), so it was not used. The same
  schedules are served keyless by the public dataset host `defillama-datasets.llama.fi` (`emissionsIndex`, then
  `emissions/<slug>`), with no robots.txt on that host and `defillama.com/robots.txt` = `Allow: /`. The data come from
  the open-source repo DefiLlama/emissions-adapters. 119 requests, all 200 except one 404 (`ooia`). Snapshot
  2026-10-31, saved in research/data/token_unlocks/ (raw/, emissions/, protocol_map.json, requests.log). The
  coordinator may want to confirm that using the dataset host is acceptable given the 402 on the API.
- 359 protocols with unlock events; 193 match a Binance perp symbol; 117 had a perp before 2025 and a pre-2025 event
  (one, IOTA, dropped as a symbol collision). Events after exclusions: see the table in HYPOTHESES_U.md (X = 1 %: 33 IS
  events on 10 coins, 427 VAL events on 45 coins).
- Funding: research/data/binance/funding/ plus a new pull for 12 event coins that only had a 75-day window (ALT, AXL,
  BICO, CYBER, FXS, GLMR, GRASS, HFT, LISTA, MANTA, MAV, ZETA): fapi/v1/fundingRate, endTime 2024-12-31 23:59:59.999,
  into research/data/token_unlocks/funding/. Random-coin draws (benchmark B) on coins without full funding count zero
  funding after the first 75 days.

## Rule (as declared)
Event = cliff of >= X % of documented circulating supply (X 1 / 3 %), one per coin per window. Short the coin perp,
long BTCUSDT perp, equal notional, fixed quantity; entry at the close t-7 or t-3 days, exit at t+0 (last close before
the unlock day) or t+3. Costs 0.15 % a side on the coin (0.05 taker + 0.10 half-spread), 0.06 % on BTC, funding on both
legs. t clustered by week of the unlock (unlocks bunch on month starts).

## Primary split: IS 2020-21 / VAL 2022-24

| X | entry -> exit | IS n | IS mean | IS t_wk | VAL n | VAL mean | VAL median | VAL t_wk | VAL x1.5 (t) | VAL 1 day late (t) | rand A pct | rand B pct | VAL years (mean %) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 % | t-7 -> t+0 | 33 | -2.89 % | -0.53 | 426 | **+1.39 %** | +2.59 % | **1.68** | +1.18 % (1.42) | +1.89 % (2.29) | 100 | 100 | +0.9 / +0.5 / +2.1 |
| 1 % | t-7 -> t+3 | 33 | -9.81 % | -1.24 | 420 | +1.43 % | +3.99 % | 1.23 | +1.22 % (1.05) | +2.03 % (1.59) | 99 | 91 | +0.8 / -0.7 / +2.9 |
| 1 % | t-3 -> t+0 | 33 | -2.20 % | -0.73 | 427 | +0.68 % | +1.23 % | 1.41 | +0.47 % (0.98) | +0.53 % (1.27) | 99 | 98 | -0.4 / -0.2 / +1.6 |
| 1 % | t-3 -> t+3 | 33 | -7.85 % | -1.66 | 422 | +0.82 % | +2.67 % | 1.04 | +0.61 % (0.77) | +0.91 % (1.10) | 96 | 66 | -0.2 / -1.2 / +2.3 |
| 3 % | t-7 -> t+0 | 23 | -3.28 % | -0.44 | 225 | +1.42 % | +2.30 % | 1.39 | +1.21 % (1.18) | +2.08 % (2.02) | 99 | 97 | +0.5 / +0.1 / +2.4 |
| 3 % | t-7 -> t+3 | 23 | -11.30 % | -1.04 | 222 | +1.31 % | +4.16 % | 0.89 | +1.10 % (0.75) | +2.19 % (1.42) | 97 | 69 | -0.2 / -2.0 / +3.6 |
| 3 % | t-3 -> t+0 | 23 | -2.99 % | -0.78 | 225 | +0.73 % | +1.30 % | 1.12 | +0.52 % (0.80) | +0.21 % (0.33) | 99 | 95 | -0.5 / -0.1 / +1.5 |
| 3 % | t-3 -> t+3 | 23 | -9.15 % | -1.53 | 222 | +0.83 % | +2.96 % | 0.76 | +0.62 % (0.57) | +0.68 % (0.67) | 93 | 63 | -0.9 / -1.7 / +2.8 |

IS by year (X 1 %, t-7 -> t+0): 2020 -3.5 % (7 events), 2021 -2.7 % (26). IS is 10 coins, 13 of the 33 events are COMP,
and the 2021 bull run squeezed every short (ALPHA 2021-01-29 -144 %, AVAX 2021-01-23 -51 %).
Selection on IS would pick the least-bad cell (1 %, t-3 -> t+0, -2.2 %); it is negative, so nothing goes to VAL.

Random benchmarks (1000 resamples of the mean): A = same coin on a random day of the same era with no cliff >= 0.5 %
within +-10 days; B = a random other perp (alive >= 60 days, no nearby cliff) on the event date. In VAL the event mean
beats A in 93-100 % and B in 63-100 % of resamples (VAL random A means -0.15 to -0.91 %: shorting these coins on
ordinary days loses after costs). Max-over-8-cells null: VAL best cell (1 %, t-7 -> t+3, +1.43 %) beats the best of
8 random-A cells in 95 % and of 8 random-B cells in only 57 %. In IS the best cell sits at 0 % (A) / 3 % (B).

VAL concentration (1 %, t-7 -> t+0, post-hoc): broad, not one coin. 2024: 226 events, 38 coins, 24 positive, leave-one-
coin-out mean >= +1.80 %. 2022 / 2023 means +0.9 / +0.5 % (APE, ENS, GMT, OP lead).

Squeeze tails (adverse coin move from entry): VAL 1 %, t-7 -> t+0: 20 / 426 events > 30 %, 4 > 50 % (OP 2024-11-28
-51 %, APT 2023-01-11 -40 %, BIGTIME 2024-12-05 -38 %, IMX 2023-02-05 -38 %). Exits at t+3 double the tail: 38 > 30 %,
12 > 50 %, worst BIGTIME 2023-11-30 -154 %, ENS 2024-01-08 -73 %. Holding past the date adds tail without adding mean.

## Fallback split (sensitivity, declared before prices): DISCOVERY 2021-01..2023-06 / VAL2 2023-07..2024-12

| X | entry -> exit | DISC n | DISC mean | DISC t_wk | VAL2 n | VAL2 mean | VAL2 t_wk | VAL2 rand A / B pct |
|---|---|---|---|---|---|---|---|---|
| 1 % | t-7 -> t+0 | 146 | +0.43 % | 0.26 | 306 | +1.50 % | 1.49 | 100 / 100 |
| 1 % | t-3 -> t+0 | 146 | -0.44 % | -0.46 | 307 | +0.96 % | 1.65 | 100 / 98 |
| 3 % | t-7 -> t+0 | 86 | -0.62 % | -0.26 | 161 | +1.87 % | 1.56 | 100 / 99 |
| 3 % | t-7 -> t+3 | 86 | -3.17 % | -0.93 | 158 | +1.95 % | 1.09 | 99 / 87 |

(other four cells in `code/output_fallback.txt`; all DISC t between -1.40 and +0.26.) DISCOVERY fails too (best t 0.26;
max-over-cells pct 7 / 25). VAL2 is the 2024-heavy period again (2023 H2 ~0 %, 2024 +1.5 to +3.6 %).

## Power at VAL size
Best VAL cell (1 %, t-7 -> t+0): per-event net Sharpe 0.12, 426 events, t_week 1.68. HOLD at the 2024 event rate is
~400 events, so power ~= 1.68 x sqrt(400 / 426) ~= 1.6 (week-clustered; 2.4 if events were independent). Below 3 even
if IS had passed; at 2024 size (mean +2.1 %) it would be ~2.5.

## What failed and why
- IS: the early sample is thin (10 coins) and sits in the 2020-21 alt rally; shorting anything with supply into that
  lost. The mechanism did not hold there, so the side "short into unlocks" has no in-sample support.
- VAL: the effect exists (pre-unlock week, coin -1.4 % vs BTC net, beats same-coin random dates), but it is about
  1/10 of an event sd and is driven by 2024, the year the "low float / high FDV" VC-token selloff was the dominant
  narrative. 2022-23 alone is +0.5-0.9 % per event, t well below 1.5.
- Costs matter: 0.42 % round trip on a +1.4 % edge; costs x1.5 drops VAL t to 1.42. One day late helps (t 2.29),
  consistent with the decline running into the date rather than a pre-positioned jump.
- Post-hoc only, not registrable: insider-heavy cliffs (>= 50 % team + investors) at 3 %, t-7 -> t+3 show VAL +4.1 %
  (t 2.85) but IS +0.4 % (12 events) and DISCOVERY +0.45 % (t 0.13); a split chosen after seeing VAL.

## Pitfalls
- Today's schedule, not the ex-ante one: adapters may encode revised (delayed / resized) cliffs. Spot checks of large
  cliffs match the launch documents (ARB 2024-03-16, OP 2023-05-31, SUI 2024-05-01, TIA 2024-10-30); PYTH (2024-05-19)
  and JTO (2024-12-06) sit one day before the commonly cited date, which only shifts the t+0 exit one day earlier.
- Documented circulating supply misses early supply for older coins (SOL 2021-01-07 "1321 %", AVAX "334 %"), so sizes
  are unreliable before ~2022; this affects which IS events pass X, not the sign.
- Survivorship: only protocols DefiLlama still tracks (dead VC tokens dropped from the index are missing).
- Symbol mapping by ticker; one collision found (IOTA). Funding for benchmark-B coins outside the 384-symbol funding
  set is zero after their first 75 days.

## What a user decision could unlock
Nothing on the current bars: IS and DISCOVERY are both negative or flat, so neither split reaches DEMO (t >= 2.0).
If the user treats 2024 as a new regime, the pre-unlock-week short (1 %, t-7 -> t+0) could be run as a forward paper
log on 2025-26 data, but that would be a new-era test with VAL2-only support (t 1.49), not a DEMO candidate.
