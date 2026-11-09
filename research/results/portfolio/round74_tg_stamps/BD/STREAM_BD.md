# Stream BD: Binance delisting notices timed by @binance_announcements. No LIVE or DEMO (IS is empty); strong VAL-only 24 h short

Written Mon Nov 2 15:29 UTC 2026 (from `date -u`). Hypotheses declared 14:23:27 UTC before any title or price, one
title-only amendment + power arithmetic at 14:56:42 UTC, before any event price: [HYPOTHESES_BD.md](HYPOTHESES_BD.md).
HOLD (2025-26) never opened: posts >= 2025-01-01 dropped right after parsing (class counts only), every price request
<= 2024-12-31 (asserted in `code/net.py`).

## Answer

**None at LIVE / DEMO, for a structural reason known before prices:** in IS 2020-21 the channel has 24 class-S
coins (spot delistings), and **none had a Binance USDT-M or Bybit perp** on the notice day (2017-era small caps:
ARN, FUEL, INS, MCO, POE, BCPT, OST, SNGLS, PPT, SWRV, DLT, APPC ...). 0 IS trades < the n >= 5 gate. F in IS is one
index contract (DOTECO, edited post).

On VAL the declared cell **S-24h** (short the coin's perp at the worst price of the 1 s bucket after N + 5 s, cover
the same way at N + 24 h, real funding) is strong:

| cell | VAL n (days) | net bp | t (day-clustered) | median | SR/trade | win | x1.5 cost | +10 s late | BTC-hedged | edited kept | random |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-5m | 14 (7) | +198 | 2.08 | +183 | 0.61 | 86 % | +193 | +179 | +185 | +179 (t 2.21) | beats 100 % (a), 86 % of coins vs (b) |
| S-60m | 14 (7) | +592 | 1.92 | +780 | 0.59 | 79 % | +587 | +574 | +602 | +494 (1.82) | 100 % (a) |
| **S-24h** | **14 (7)** | **+1,418** | **3.60** | **+1,755** | **0.96** | 71 % | +1,413 | +1,399 | +1,492 | +1,180 (2.91) | **100 % of sets; event t beats 99.8 % of random t** |
| F-5m | 4 (3) | +500 | 1.59 | | | | | | | | LUNA / ANC / FTT emergencies only |
| F-60m | 3 (3) | -1,700 | -1.22 | | | | | | | | |
| MT-24h (VAL-only by construction) | 15 (5) | +377 | 3.59 | +327 | 0.50 | 67 % | +372 | +380 | +374 | same | 99.9 % of sets |
| MT-5m / 60m | 15 (5) | +12 / +40 | 0.38 / 1.15 | | | | | | | | |

Years (S-24h): 2022 0 trades, 2023 +928 (1), 2024 +1,455 (13). Leave-one-day-out t: 2.69-4.07 (min when dropping
2024-06-03, OMG / WAVES / XEM). Funding cost the short -98 bp / 24 h on average (BOND -776 bp). Random for 24 h
(`code/random24.py`): same coin, random 5m opens in N +- 30 d excluding +- 2 d, 2,000 sets: random mean -23 bp vs event
+1,516 ex-funding; 95th pct of random t 1.84. The 5m / 60m max-over-cells random-t null (95th pct) is 1.96.
Post-hoc: 24 h short entered at N + 5 min still +1,277 bp, at N + 60 min +738 (fees only): **the edge is the 24 h
drift after the notice, not seconds.**

Power at VAL size: SR 0.96 x sqrt(expected HOLD trades). HOLD has 21 class-S posts (count only). At VAL's 0.67 perp
trades per post -> ~14 trades -> **power 3.6**; at 2024's 1.6 per post -> ~34 -> 5.6. The power bar would pass; the
IS bar cannot be graded.

## Events

- @binance_announcements: 8,941 posts parsed (ids 1..9,107; gaps are deleted posts), 6,779 before 2025.
  Class counts pre-2025 (posts / S coins, edited dropped): see HYPOTHESES power section. Coverage with a short
  instrument: S IS 0 / 24, S VAL 14 / 66 (Binance 11, Bybit 3), F VAL 4 / 4, MT VAL 15 / 34.
- The channel does not carry every Binance notice: only 6 futures-delisting titles pre-2025 (round 64 T's 2024 perp
  delistings MBL / SNT / STPT / RAD / CVX have no post). Monitoring tags start 2023-07 (the "Introducing" post).
- Edited posts: 4 S posts in 2021 / 2024 (incl. 2024-08-12 CVP / EPX / FOR / LOOM / REEF / VGX). Primary drops them;
  keeping them gives the same picture (S-24h +1,180, t 2.91, n 17).
- Files: [events_binance_announcements.csv](events_binance_announcements.csv) (pre-2025 only), trades_in.csv,
  [trades.csv](trades.csv), [results.txt](results.txt), results_edited.txt, [random24.txt](random24.txt),
  spot_paths.csv, cells.json.

## Burst timing (the Telegram stamp is late in 2023-24)

- Perp, class S VAL: median r(N - 10 min vs N - 60 s) = +1,180 bp, i.e. the coin had already fallen ~12 % in the 9
  minutes **before** the Telegram post. Onset of -2 % is before N in 10 / 11 events (median -281 s). Posts are
  stamped hh:02-hh:09 while Binance's own notices go out at round times: **the channel lags the website by ~2-7 min in
  2023-24.** After N, the move keeps going: median r(+5 s) -29, r(+5 min) -240, r(+1 h) -824 bp; share of the
  5-minute move done by N + 5 s = 0.07 (median). So no seconds race is left at the Telegram stamp, but the 24 h drift is.
- Spot (info, not shortable): 2018-19 (n 11) and 2020-21 (n 18) show r(-600) = 0 and onset after N (share by
  N + 5 s 0.00): the channel was timely then. Post-entry gross drift r(t) - r(5 s): 2018-19 -375 / -1,754 / -3,667 bp at
  5 min / 1 h / 24 h (t -13.5 / -4.4 / -12.4); 2020-21 -994 / -2,997 / -3,686 (t -4.0 / -7.2 / -9.0); 2022-24 (n 56)
  -866 / -2,440 / -3,584 (t -3.8 / -4.9 / -6.0). The mechanism is the same in every era; only a short instrument was
  missing before 2023.

## Costs

Binance USDT-M taker 5 bp a side, Bybit 5.5 bp, both plus the worst price of the 1 s bucket (A2's F2 fill), real
funding for the 24 h exit (fapi fundingRate / Bybit v5 funding history). Gross S-24h +1,526 bp, funding -98, fees
-10: costs are not what decides this cell. Not modelled: borrow / leverage limits Binance puts on a perp of a coin
being spot-delisted, and the perp's own later delisting (none inside 24 h here).

## Cross-venue (OKX)

@OKXAnnouncements pulled (315 pages, 6,125 posts from 2019-05, through the shared lock). Delisting titles are
mostly unnamed ("OKX will delist several spot pairs", "Delisting ALERT"); pre-2025 named coins: DGD, K-tokens, FEG,
SWRV, PLS, KOL / GM / SRM / UMEE / VALUE / MITH / JFI / SOS, WAVES, YFII, WSM. Too few and almost none in IS:
not graded (declared optional cell dropped). @Bybit_Announcements not pulled (its spot starts 2021; same IS problem).

## Pitfalls found

- Telegram stamps of @binance_announcements are minutes late from ~2023 (not in 2018-21): a "post + 5 s" rule is
  really "website + 2-7 min". Any Binance seconds study must not treat these stamps as first-public times after 2022.
- Delisted coins' perps: most 2020-22 spot delistings had no perp; the Binance perp often went away before the spot
  (YFII, SRM, BTCST, BTS ...). HNT 2023 had a perp but no USDT / BTC spot pair (BUSD era).
- Ticker parsing needs case-insensitive "Delist"; "Binance Staking to Delist" and "Notice of Removal of Trading
  Pairs" are not coin delistings; stablecoins excluded.
- Extreme funding on squeezed delisting perps (BOND -776 bp in 24 h) and short squeezes in the first hour (BOND -2,141
  bp at 60 m): size per trade must be small.
- 7 notice days carry all VAL trades: day-clustered t with 7 clusters is fragile, hence the leave-one-day-out table.

## What a user decision could unlock

S-24h is the strongest VAL result I have seen in this family, but the IS bar is empty by construction (no perps on
2020-21 delisted coins). Options, all yours: (1) accept a **new-era design** where 2022-24 is the design sample and
HOLD 2025-26 is the single test (~14-34 trades, power 3.6-5.6 at the VAL Sharpe), i.e. open HOLD once for S-24h as
declared (entry N + 5 s from the Telegram stamp, exit N + 24 h, Binance perp else Bybit, funding counted); (2) a
forward paper log from the channel (the coordinator's capture route works; seconds do not matter here). MT-24h is
VAL-only and would be a second, separate new-era cell. I did not write a PREREG_DRAFT because the IS bar is not met.

## Data

- research/data/telegram_hist/raw/OKXAnnouncements (pulled here; Binance pages from the coordinator).
- research/data/binance_delist_tg/ (46 MB): `sec/` per-second last / lo / hi / count arrays for 260 (venue, symbol,
  day) files, `.ok` / `.miss` HEAD markers, `k5m/` 5m bars for the 24 h random benchmark, `btc1m/` BTC spot 1m for the
  hedge sensitivity. requests.log: 1,636 requests, 828 x 200, 808 x 404 (HEAD probes for missing perps / spot
  pairs), 0 x 403 / 418 / 429. Zips parsed in memory, none kept.
- Code: `code/events.py` (parse, cut, classify), `instruments.py`, `pull.py`, `net.py`, `analyze.py`, `random24.py`.
