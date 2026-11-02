# Round 64 stream F: liquidation-wick fade on altcoin perps (1m), hypotheses

Written 2026-11-01 08:54 UTC (from `date -u`), before any 1m return was computed. At this time only the universe
(daily quote volume and listing age, no prices) and the pull list existed; the 1m pull had just started and no file
had been opened beyond a format probe (SOLUSDT 2023-06, header row only read). HOLD is never requested (monthly files
<= 2024-12) and every series is cut at ts < 2025-01-01 at load.

## Mechanism and side (fixed now)
Altcoin USDT-M perps are thin relative to the leverage on them. A liquidation or stop cascade sells (buys) at market
into a book that refills only after a delay, so a one-minute close prints beyond what information justifies. Liquidity
providers who step in after the cascade earn the overshoot (Nagel 2012, liquidity provision premium; Grossman-Miller).
Side: **fade** the event minute. Long after a crash, short after a spike. Both legs are the perp itself; no borrow.
Round 26 J faded IC jumps on BTC / ETH at 23-26 bp IC cost (at mid it was real, net it was below cost); round 31 / 63 O
looked at liquidations / OI at 1 h or longer (continuation / weak rebound). This stream is the 1-minute altcoin version
at Binance taker cost.

## Data
- Universe: point-in-time top 40 USDT-M perps by mean daily quote volume over days d-30..d-1, listed >= 60 days
  (round 63 C `xs.daily_universe`, the perp-only twin of round 58 `carry.universe`), recomputed each UTC day, delisted
  coins included. 212 symbols, 2,759 symbol-months (any day in the top 40), plus BTCUSDT every month.
- 1m klines: data.binance.vision futures/um monthly 1m, 2020-01..2024-12, stored as npz in
  research/data/binance_1m_wicks/npz (zips deleted after conversion), requests.log.
- Funding: research/data/binance/funding (via round 63 C's panel cache, hourly stamp grid).
- If the pull exceeds ~45 min, the remaining months are dropped in a fixed order (latest-added first) and reported.

## Events
- r_e = c_e / c_{e-1} - 1, close-to-close of consecutive minutes e-1, e. Coin must be in the top 40 on the UTC day of e.
- Thresholds (3): **T3** |r_e| >= 3 %; **T5** |r_e| >= 5 %; **TZ** |r_e| >= max(1 %, 10 x sigma), sigma = sd of 1m
  close-to-close returns over minutes e-1440..e-1 (>= 1,000 valid minutes).
- Idiosyncratic filter (2): **all** (no filter) / **idio**: |r_BTC,e| <= 0.2 x |r_e| in the same minute (BTCUSDT itself
  excluded from idio).
- Bad-print guard (declared now, applied to every cell): minute e has >= 10 trades and quote volume > 0; minute e+1
  exists and its **open** is still on the shocked side of the half-way point (crash: o_{e+1} <= c_{e-1} x (1 + r_e / 2);
  spike: o_{e+1} >= c_{e-1} x (1 + r_e / 2)). A bad close print snaps back at the next open and is removed; this uses
  only information known before the entry (close of e+1). QC only (not part of the rule): a random sample of <= 300
  guarded events is checked against the spot pair's 1m bar (api.binance.com public klines) to report the share that
  also moved >= half as much in spot.
- De-duplication: after a guarded event, the same coin's events in minutes e+1..e+60 are dropped (same event set for
  every H).

## Trade
- Entry at the close of minute e+1 (one full bar late). "Late" check: close of e+2 (two bars late), same exit length.
- Exit at the close of minute entry + H, H in {5, 15, 60} min. A missing exit minute uses the last close before it if
  the gap <= 5 min, else the trade is dropped.
- P&L = side x (c_exit / c_entry - 1) - funding paid (stamps in (entry, exit]) - costs.
- Grid: 3 thresholds x 2 filters x 3 H = **18 cells**, both sides pooled (crash longs + spike shorts). Sides are
  reported separately as information. The cell is chosen on IS (best day-clustered net t) and checked on VAL unchanged;
  all 18 are reported.

## Costs (declared)
- Taker 5 bp a side.
- Half-spread proxy h: 1 bp (BTC, ETH), 3 bp (volume rank < 20 that day), 5 bp (rank 20-39), as round 63 C / O.
- Entry is in the minute right after a wick, so the entry half-spread is **3 x h**; exit half-spread 1 x h.
- Round trip = 10 + 4h = 14 / 22 / 30 bp. Robustness: costs x 1.5 (21 / 33 / 45 bp) and the two-bars-late entry.

## Statistics and bars
- Eras: IS 2020-01-01..2021-12-31, VAL 2022-01-01..2024-12-31. t clustered by entry UTC day.
- Years: 2020..2024 net per year; LIVE needs >= 2/3 positive (4 of 5).
- Random benchmark (per cell, 200 replications): for each event, a random minute of the same coin, same era, same
  decile of trailing sigma (deciles per coin-era over in-universe minutes), side recomputed at the random minute
  (fade that minute's own 1m return), the same H, the same cost as the real trade. "Random %" = share of replications
  whose mean net is below the real mean net. Max-over-18-cells null: per replication the max IS t over the 18 random
  cells, compared with the real max IS t.
- Pitfall checks: IS without 2020-03-12..13 and without March-April 2020; VAL without LUNA (2022-05) and FTX
  (2022-11) months; concentration (top 3 coins removed).
- Bars as in BRIEF: LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years, >= 95 % random, HOLD power >= 3, positive at x1.5 and
  late; DEMO t >= 2.0 IS, net > 0 VAL, >= 90 % random. A pass writes PREREG_DRAFT_F_<name>.md and stops.
- Daily-P&L correlation with C3 (trades_C3_gotobi_jpy_basket.csv, IS / VAL only) for any cell at DEMO numbers.

## Power arithmetic (before data)
HOLD 2025-01..2026-10 is ~22 months; VAL is 36 months, so expected HOLD trades n_H = 0.61 x n_VAL.
Power = S x sqrt(n_H), S = net mean / sd per trade at VAL size. Needed S >= 3 / sqrt(0.61 n_VAL):
- n_VAL = 300 (likely for T5-idio) -> S >= 0.22; n_VAL = 1,000 -> S >= 0.12; n_VAL = 3,000 (T3 / TZ all) -> S >= 0.07.
- A wick fade's per-trade sd at 15 min is likely 150-300 bp, so a 15-min fade needs ~+20-35 bp net per trade with
  ~1,000 VAL trades, or ~+45-65 bp with 300. Events cluster on crash days, so I also report a day-clustered power
  (VAL clustered t x sqrt(0.61)); clustered LIVE would need a VAL clustered t >= 3.84 at the VAL rate.
- Expected bars per cell: T3 / TZ (many events) can in principle reach LIVE if the fade survives ~22-30 bp of cost;
  T5 / idio cells (hundreds of events) can reach DEMO, LIVE only with S >= ~0.2 (a large overshoot).

## Addendum 1 (2026-11-01 08:57 UTC, before any return)
api.binance.com/robots.txt is "User-agent: * / Disallow: /", so the spot QC does not use the REST API. It uses the
spot daily 1m files on data.binance.vision instead (one file per sampled event day; robots.txt there is 404). Same
sample size and test. Nothing else changes.

## Addendum 2 (2026-11-01 08:59 UTC, before any return)
The pull slowed from ~1.7 to ~0.15 files/s after 4 min (hung reads). Restarted with a 40 s timeout and 6 threads (still
>= 0.25 s between request starts), and the remaining files are ordered odd calendar months first (Jan, Mar, ...,
every year), then even months. If the pull is not done by 09:45 UTC it is stopped and only **complete** months
(every pull-list symbol of that month present or 404) are used; the months dropped are listed in STREAM_F.md.
