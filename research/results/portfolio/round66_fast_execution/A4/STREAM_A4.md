# Stream A4 (round 66): Upbit KRW-listing notice -> Bybit perp, coins without a Binance perp. None (IS n = 0)

Written Sun Nov 1 14:43:58 UTC 2026 (from `date -u`). The event screen, the frozen rule, the costs and the power were
declared at 14:39:48 UTC in [HYPOTHESES_A4.md](HYPOTHESES_A4.md), before any trade dump or candle was downloaded.
HOLD (2025-01-01..) was never requested, loaded or counted. Only dump files dated 2023-12-12..2024-12-16 were pulled,
funding was cut at < 2025-01-01, and every N < 2025.

## Answer first
- **None, as declared before any return.** The screen gives **0 IS events and 7 VAL events** (2023-12..2024-12).
  LIVE and DEMO both need an IS t, and parameters must be picked on IS, so no bar can be tested. No PREREG_DRAFT.
  - Why no IS: in 2020-21, Bybit had no USDT perp for any KRW coin that lacked a Binance perp. Bybit's first perps
    for such coins (SAND, FLOW, STX) came in 2021-11.
- **The VAL numbers are the strongest of the A family**, and they are descriptive only. Frozen A2-D5L on Bybit (long
  the alt perp / short BTCUSDT at the first trades >= N + 5 s, exit at the first trades >= L; 22 bp + A2 slippage +
  Bybit funding):
  - VAL net **+5,029 bp/trade, t 3.08**, n 7 on 7 days, median +3,525, SR 1.17, 7 of 7 positive (min +883).
  - Years: 2023 +11,402 (n 1), 2024 +3,967 (n 6). 2022 has no events.
  - Random: beats 100 %. Costs x1.5: +4,920. One step late (N + 10 s): +4,054, t 2.90.
- **Power is below 3 at the 2022-24 pace.** 7 events in 3 years gives ~4.3 HOLD events, so power = 1.17 x sqrt(4.3) =
  **2.41** (an SR of 1.45 is needed). At the 2024 pace alone (6 a year, ~11 HOLD events) it would be 3.87.
- **Median path on Bybit** (alt vs BTC, bp from N - 60 s, n 7):

  | t - N | 0 s | +1 s | +2 s | +3 s | +5 s | +10 s | +30 s | +60 s | +300 s |
  |---|---|---|---|---|---|---|---|---|---|
  | median (bp) | +1 | +24 | +1,139 | +1,713 | +2,315 | +2,896 | +3,247 | +3,531 | +4,278 |

  - The onset (+2 %) comes a median **1.2 s** after N (range 0.2-2.3 s), so the burst never leads the stamp.
  - Half of the +60 s level is reached at 2.4 s; 90 % only at **21 s** (A2's Binance VAL: 3.3 s).
  - Unlike A2's Binance coins (VAL +5 s +1,289 -> +300 s +1,199, flat), the Bybit-only coins keep rising after 5 s.
    These are smaller coins, and Bybit is their main leveraged venue.
- **Capacity is real but smaller than A2's.** The median taker-buy alt notional in the 1 s after N + 5 s is $39k
  ($112k over 5 s). ME, a pre-market perp at N, had $644. A $30k buy walking the real taker-buy prints fills in
  0.1-6.8 s and gives +4,794 bp, t 3.00.

## Events (A4/events.csv; screen A4/events_screen.txt, dump-listing check A4/probe.txt)
| coin | N (UTC) | L (UTC) | L - N | Bybit perp since | L source |
|---|---|---|---|---|---|
| CTC | 2023-12-12 08:00:20 | 09:05 | 65 min | 2022-05-17 | first KRW candle |
| MNT | 2024-03-27 05:13:24 | 09:05 | 232 min | 2023-10-02 | first KRW candle (the body's later time is POKT's postponement) |
| UXLINK | 2024-09-03 10:04:34 | 13:05 | 180 min | 2024-07-19 | KRW-UXLINK 404: stated + 5 min |
| SAFE | 2024-10-24 06:32:30 | 09:05 | 152 min | 2024-04-29 | first KRW candle |
| DRIFT | 2024-11-08 05:44:59 | 09:05 | 200 min | 2024-05-21 | KRW-DRIFT 404: stated + 5 min |
| ME | 2024-12-10 09:24:15 | 12-11 01:40 | 976 min | 2024-11-25 (pre-market perp) | first KRW candle (buy wait extended to 10 min) |
| MOCA | 2024-12-16 01:56:48 | 05:05 | 188 min | 2024-07-12 | first KRW candle |

- **Screen.** The 2020-24 notices give 83 KRW coin listings. 46 of them had a Binance perp >= 7 d old (A / A2's set, with GAL's
  "live at N" variant). Of the other 37, 7 had a Bybit perp >= 7 d old.
  - **Near misses:** the Bybit perp opened < 7 d before N or after N for SUI, SEI, APT, ZRO, MOVE, VANA, CARV and AKT.
  - **No Bybit perp at all:** the 2020-21 small caps, WEMIX and NU.
- **launchTime is the latest launch.** So all 37 public.bybit.com directory listings were checked. The first dump file
  is on launchTime's day or 1-7 d later, and no coin has an earlier Bybit life.

## Results (net bp per trade; results.txt, cells.json, trades.csv)
| set | cell | n (days) | gross | slip | fund | net | t | median | SR | years | rand % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VAL | **H5-L (frozen)** | 7 (7) | 5197 | 196 | +50 | **5029** | **3.08** | 3525 | 1.17 | 2023 +11402, 2024 +3967 | 100 |
| | costs x1.5 | | | | | 4920 | 3.05 | | | | |
| | H10-L (late) | | 4216 | 190 | | 4054 | 2.90 | 2427 | 1.09 | | |
| | info: H2-L | | | | | 6360 | 3.29 | | 1.24 | | |
| | info: H30-L | | | | | 2652 | 2.68 | | 1.01 | | |
| | info: H5-5m | | | | | 3770 | 2.90 | | 1.10 | | |
| | info: U5-L unhedged | | | | | 4982 | 3.04 | | 1.15 | | 100 |
| VAL without ME (declared sensitivity) | H5-L | 6 (6) | 5908 | 208 | +42 | 5720 | 3.27 | 4104 | 1.34 | | 100 |
| IS | all | 0 | | | | | | | | | |

**Per event, H5-L net:** CTC +11,402, MNT +1,324, UXLINK +4,684, SAFE +3,525, DRIFT +2,680, ME +883, MOCA +10,707.
- The entry fills come 5.00-5.25 s after N on the alt and 5.09-5.86 s on BTC.
- The alt entry slippage (half the median 1 s range) is 54-290 bp, against 0-9 bp at N - 10 min.
- Funding is mostly received: the funding column is the sum of both legs' payments, + = received.

**Post-hoc (checks.txt; chooses nothing):**

| fill | net | t | SR | power @ 4.3 | power @ 11 |
|---|---|---|---|---|---|
| declared | 5029 | 3.08 | 1.17 | 2.41 | 3.87 |
| aggressor side | 5006 | 3.07 | 1.16 | 2.40 | 3.84 |
| worst of 1 s | 4436 | 2.88 | 1.09 | 2.25 | 3.61 |
| $30k walk | 4794 | 3.00 | 1.13 | 2.34 | 3.76 |

- Leave-one-out t ranges from 2.60 (drop MOCA) to 3.27 (drop ME). Dropping the min and max gives a mean of +4,584. On
  log returns the mean is +3,745 bp, t 3.64.
- No bad prints: the largest single-print jump in N..N + 10 s is 590-820 bp, normal for a +20-40 % burst.

## Bars
| bar | needed | A4 |
|---|---|---|
| IS t | LIVE 2.5 / DEMO 2.0 | n 0: untestable, fail |
| VAL net, t | DEMO > 0; LIVE t >= 1.5 | +5,029, t 3.08 (descriptive) |
| years positive | >= 2/3 | VAL 2/2 (2022 empty) |
| random | >= 95 % / 90 % | 100 % |
| x1.5, late | > 0 | +4,920 / +4,054 |
| HOLD power at VAL size | >= 3 | 2.41 at the 2022-24 pace (3.87 at the 2024 pace) |

## What failed and why
- **No IS, structurally.** Bybit-only listings are a 2023-24 phenomenon. Before 2022, Bybit listed few USDT perps;
  by 2024, Upbit was listing coins that Bybit had but Binance futures did not. The rule cannot be "picked on IS".
- **Power misses at the declared pace.** 2.3 events a year over 2022-24 gives 4.3 HOLD events. The pace is
  accelerating (0, 1, 6 a year), but the brief fixes the 2022-24 pace.
- **n 7 is tiny.** Two events, CTC (+114 %) and MOCA (+107 %), carry 63 % of the sum. The fills are real taker
  prints, though, and every event is positive.

## Pitfalls met
- **Dump format.** The timestamp is in seconds with 4 decimals (0.1 ms), not ms. side = Buy / Sell is the taker side.
  Header: timestamp, symbol, side, size, price, tickDirection, trdMatchID, grossValue, homeNotional, foreignNotional
  (format_check.txt).
- **Delisted KRW markets.** KRW-UXLINK and KRW-DRIFT return 404 on the candle API, so L = stated + 5 min (A's rule).
- **MNT's body carries POKT's postponed time.** The candle gives L = 09:05, not 10:05.
- **ME.**
  - L is on the next UTC day, so two days were loaded and the random draw uses the 2-day 1 s series.
  - Its Bybit perp was a pre-market contract at N, with 162 prints in N..N + 10 s.
  - Bybit funding for MEUSDT came from the v5 API, starting 2024-11-26.
- **Bybit 2023-24 taker fee.** 5.5 bp (VIP 0 derivatives), per Bybit's fee page and its guide dated 2023-02-17. No
  2023-24 change was found.

## What a user / coordinator decision could unlock
- **A venue-fallback version of A2-D5L.** "Binance perp if >= 7 d old, else Bybit perp if >= 7 d old" is the same
  mechanism and the same frozen trade. Its IS would be A2's 12 events and its VAL A2's 32 plus these 7. This is a
  change to a registered rule, so it is the coordinator's call. It must not be graded on any HOLD the coordinator has
  already opened for A2-D5L; it would be a forward registration.
- **Forward test of A4 alone.** Power 3 needs n = (3 / 1.17)^2 ≈ 6.6 events. That takes ~13 months at the 2024 pace
  (6 a year) and ~34 months at the 2022-24 pace.
- **Execution** is as in A2:
  - notice capture within ~2-3 s;
  - a Bybit account (a user decision; keyless polling cannot trade);
  - alt and BTC market orders by N + 5 s, sized ~$10-30k;
  - watch Bybit's price-limit bands in a +20 % second.

## Files
- **Code (A4/code/):**
  - net.py: polite fetcher and log.
  - events.py: the screen; imports A's events.py / perps.py by path, read-only.
  - probe.py: dump directory listings.
  - pull_L.py: Upbit L; a copy of A3's walk.
  - pull.py: dump stream / cut / delete.
  - analyze.py: A2's trade / slip / clt and the random draw; Bybit fee and data.
  - checks.py: post-hoc.
- **A4/:**
  - HYPOTHESES_A4.md, STREAM_A4.md
  - events_raw.csv, events.csv, events_screen.txt, probe.txt
  - results.txt, checks.txt, cells.json, trades.csv
- **Data (research/data/upbit_bybit_notice/, 13 MB):**
  - npz/: 16 files, 11 MB.
  - up1m/: 13 pages.
  - listing/: 38 directory pages.
  - funding/MEUSDT.csv, format_check.txt, pull.out.
  - requests.log: 77 lines, 14:38-14:43 UTC.
    - 3 robots.txt requests (all 404).
    - 38 listings, 5 HEAD probes, 1 docs page, 1 funding API call, 13 api.upbit.com calls.
    - 16 dumps (1.30 GB), all gz deleted.
    - No 403 / 418 / 429.
