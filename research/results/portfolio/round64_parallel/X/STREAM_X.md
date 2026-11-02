# Stream X: cross-venue spot wedge, long cheap Binance spot hedged with the Binance perp (round 64)

Written 2026-11-01 10:33 UTC (from `date -u`). Declared in [HYPOTHESES_X.md](HYPOTHESES_X.md) (09:12 UTC, before any
venue price was requested; addendum 1 at 10:03 UTC from signal counts only, before any return). HOLD (2025+) was never
requested or loaded: every request ends at or before 2024-12-31 23:59:59 UTC, every series is cut at ts < 2025-01-01
(0 rows >= 2025 on disk, venue 1h and Binance 1m checked).

## Answer: none (all 6 cells lose about the cost wall in IS and VAL)
- **Graded rule (Binance spot cheap vs the other venues -> long Binance spot / short Binance USDT-M perp): none.**
  Every cell loses money in every era and every year. Best IS cell by t is still negative, so no cell can be chosen.
  At the 1m primary entry (T + 1 min): k100_H24 IS -59.5 bp (t -5.76, n 386), VAL -76.3 bp (t -4.05, n 169); k60_H24
  IS -56.1 (t -8.31, n 746), VAL -62.0 (t -7.69, n 396). Win rate 1-3 %, 0 / 5 years positive, beats 0-0.5 % of random
  entries (random mean -48..-50 bp = the cost), power at VAL size negative (-4.0 to -9.1).
- **Why:** the signal is real but it is not Binance-spot specific. When Binance spot is 50-200 bp below OKX / KuCoin /
  Bybit / Coinbase spot (relative to the usual gap), the **Binance perp is just as cheap** (B's perp-spot basis
  deviation at the signal: median ~+1 bp). The wedge then closes, about half by Binance rising (spot +43..+64 bp) and
  half by the other venues falling (-17..-56 bp), but the Binance perp rises with Binance spot, so the hedged price leg
  is -1 to -26 bp per trade, and the 42-50 bp of costs is the loss. Long spot / short perp on the same venue cannot
  capture a venue-wide (or other-venue-stale) gap.
- **Mirror (Binance spot rich, would need borrow, information only): none either.** Best k100_H24 IS -2.3 bp
  (n 243), VAL -0.6 bp (n 77); 2 / 5 years positive (2021 +72, 2023 +12).
- No PREREG_DRAFT. No C3 correlation needed (no cell reaches DEMO numbers).

## Setup (as declared)
- Universe: B's point-in-time top-60 USDT-M perps with a spot pair (previous day's membership), BTC / ETH excluded;
  Binance legs from B's loader (`round63_parallel/B/code/basis.py`, imported, not edited).
- Other venues' spot 1h (pulled for this stream): OKX 127, KuCoin 173, Bybit 119, Coinbase 132 coins with bars (of B's
  244 universe coins; venues serve only currently listed pairs). Coinbase USD converted with Coinbase USDT-USD where
  it exists (from 2021-05). Kraken skipped (its OHLC endpoint has no 2020-24 history).
- Cleaning (fixed): power-of-10 scale per coin x venue, venue bar volume > 0, |ln ratio| < 10 %, venue x coin x year
  dropped if hourly return correlation with Binance spot < 0.5 or < 500 hours; Binance spot bars with B's filters.
- Signal: per venue d_v = ln(venue / Binance spot) minus its trailing 168 h median; G = -median_v(d_v), >= 2 usable
  venues. Cheap: G < -k. Exit at the first close where G (with the entry-hour references) has halved, else after H.
- Entry: Binance 1m open at T + 1 min (T = signal close), both legs; exit 1m open at exit hour + 1 min. Funding on the
  short perp at the real stamps; costs 30 bp fees + 4 x 3 / 5 bp half-spread (42-50 bp); Fed funds on the spot leg.
- Coverage of universe coin-hours with >= 2 usable venues: 2020 49.5 %, 2021 56.7 %, 2022 48.6 %, 2023 51.9 %,
  2024 70.4 %. IS had 746 k60_H24 signals on 246 days, so the main split (IS 2020-21 / VAL 2022-24) was kept.

## Cheap side, 1m entry (primary), k60 / k100 cells (net bp per trade; t clustered by entry UTC day)
| cell | era | n | days | net | median | t | win | x1.5 | +2 min (t) | +5 / +15 min | 1h-open entry | spot leg | perp leg | funding | cost | years + |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k60_H6 | IS | 924 | 248 | -54.8 | -48.4 | -10.04 | 2 % | -79.5 | -52.7 (-13.7) | -50.1 / -59.2 | -52.4 | +44.2 | -50.0 | +0.3 | 49.2 | 0 / 2 |
| k60_H6 | VAL | 489 | 187 | -59.7 | -50.2 | -9.13 | 1 % | -84.5 | -61.1 (-7.8) | -59.4 / -55.2 | -61.0 | +40.3 | -47.9 | -2.5 | 49.6 | 0 / 3 |
| k60_H24 | IS | 746 | 246 | -56.1 | -48.5 | -8.31 | 3 % | -80.7 | -53.4 (-11.2) | -50.2 / -61.4 | -53.2 | +55.2 | -62.4 | +0.3 | 49.2 | 0 / 2 |
| k60_H24 | VAL | 396 | 184 | -62.0 | -50.1 | -7.69 | 1 % | -86.8 | -63.6 (-6.6) | -61.4 / -56.3 | -63.6 | +46.6 | -56.0 | -3.1 | 49.5 | 0 / 3 |
| k100_H6 | IS | 492 | 163 | -57.5 | -48.8 | -7.04 | 2 % | -82.0 | -53.6 (-11.5) | -50.8 / -63.6 | -52.9 | +48.9 | -57.4 | +0.1 | 49.0 | 0 / 2 |
| k100_H6 | VAL | 224 | 90 | -70.0 | -50.8 | -4.90 | 2 % | -94.9 | -72.4 (-4.2) | -67.8 / -60.2 | -73.7 | +34.4 | -50.8 | -3.9 | 49.6 | 0 / 3 |
| k100_H24 | IS | 386 | 158 | -59.5 | -48.4 | -5.76 | 3 % | -84.0 | -54.5 (-9.3) | -51.0 / -67.3 | -53.8 | +56.9 | -67.6 | +0.1 | 48.9 | 0 / 2 |
| k100_H24 | VAL | 169 | 89 | -76.3 | -50.3 | -4.05 | 2 % | -101.1 | -79.5 (-3.5) | -73.6 / -62.8 | -81.0 | +49.2 | -70.8 | -5.1 | 49.5 | 0 / 3 |

By year (1m, net bp, n): k100_H24 2020 -47.2 (137), 2021 -66.3 (249), 2022 -58.2 (114), 2023 -128.5 (42), 2024 -66.8
(13); k60_H24 2020 -49.0, 2021 -60.7, 2022 -54.1, 2023 -97.2, 2024 -54.2. Every 1m window was found (0 empty files).
VAL trades per year 56-163; per-trade Sharpe -0.37 to -0.52; power at VAL size -4.0 (k100_H24) to -9.1 (k60_H6).
Ex crash windows (information): k100_H24 IS -49.3 (t -12.3), VAL -76.4; k60_H24 IS -50.8, VAL -62.0.

## All 12 cells at 1h opens (open of h+1; the like-with-like base for the random benchmark)
| cell | IS n | IS net (t) | VAL n | VAL net (t) | x1.5 IS / VAL | 1 h late IS / VAL | random mean IS / VAL | beats random IS / VAL |
|---|---|---|---|---|---|---|---|---|
| k30_H6_cheap | 2975 | -50.0 (-33.1) | 2051 | -53.3 (-28.9) | -74.6 / -78.1 | -52.4 / -50.7 | -48.4 / -49.7 | 0.7 % / 0 % |
| k30_H24_cheap | 2627 | -50.1 (-29.3) | 1869 | -53.7 (-26.5) | -74.7 / -78.4 | -52.9 / -50.8 | -48.4 / -49.7 | 1.9 % / 0 % |
| k60_H6_cheap | 924 | -52.4 (-12.9) | 489 | -61.0 (-8.1) | -77.0 / -85.8 | -57.7 / -51.9 | -48.1 / -50.0 | 0.3 % / 0 % |
| k60_H24_cheap | 746 | -53.2 (-10.6) | 396 | -63.6 (-6.8) | -77.8 / -88.3 | -59.3 / -52.3 | -47.9 / -50.1 | 0.3 % / 0 % |
| k100_H6_cheap | 492 | -52.9 (-9.3) | 224 | -73.7 (-4.5) | -77.5 / -98.5 | -62.6 / -53.6 | -48.1 / -50.2 | 0.5 % / 0 % |
| k100_H24_cheap | 386 | -53.8 (-7.5) | 169 | -81.0 (-3.7) | -78.3 / -105.8 | -65.7 / -54.9 | -47.6 / -50.4 | 0 % / 0 % |
| k30_H6_rich (info) | 2595 | -39.5 (-4.9) | 1716 | -45.7 (-13.3) | -64.2 / -70.6 | -45.4 / -50.9 | - | - |
| k30_H24_rich (info) | 2323 | -38.4 (-4.3) | 1610 | -45.5 (-12.4) | -63.1 / -70.3 | -44.9 / -51.0 | - | - |
| k60_H6_rich (info) | 661 | -15.6 (-0.6) | 268 | -35.4 (-1.7) | -40.3 / -60.1 | -32.6 / -48.5 | - | - |
| k60_H24_rich (info) | 534 | -7.8 (-0.2) | 218 | -32.0 (-1.3) | -32.5 / -56.7 | -28.7 / -48.2 | - | - |
| k100_H6_rich (info) | 305 | -11.7 (-0.4) | 102 | -12.8 (-0.3) | -36.5 / -37.3 | -6.5 / -56.6 | - | - |
| k100_H24_rich (info) | 243 | -2.3 (-0.1) | 77 | -0.6 (-0.0) | -27.1 / -25.0 | +2.8 / -59.4 | - | - |
Random: B's matched entries (same coin, era, hold length, side), 1,000 reps, seed 64. Max-over-6-cells null of t:
IS p95 -14.0, VAL p95 -17.4 (degenerate: random entries pay the cost too); the signal is below even that. Mirror rich
side includes borrow 40 %/yr; its years: k100_H24 2020 -51.7, 2021 +72.0, 2022 -0.8, 2023 +12.4, 2024 -34.6 (n 12).
k30 cells were graded at 1h only (their seed-0 1m subsample was not pulled, see Deviations).

## Where the gap goes (bp per trade, 1h, mean; out/diag.txt)
| cell | era | G at signal | B basis deviation at signal (mean / median) | Binance spot move | venue median move | hedged price leg |
|---|---|---|---|---|---|---|
| k60_H24 | IS | -118.1 | -5.7 / +1.0 | +59.9 | -21.6 | -4.3 |
| k60_H24 | VAL | -104.5 | -12.8 / +0.6 | +43.7 | -28.5 | -11.0 |
| k100_H24 | IS | -177.3 | -6.2 / -0.2 | +64.1 | -51.5 | -5.1 |
| k100_H24 | VAL | -166.6 | -29.1 / +0.9 | +42.6 | -56.3 | -26.3 |
Moves are close-to-close from the signal hour to the last hour of the hold. The perp-vs-venues deviation equals
G + basis deviation (-124 to -196 bp): the whole Binance complex is cheap, not Binance spot. The negative VAL mean of
the basis deviation (median ~0) comes from a few trades where the perp was cheaper still (B's cheap side); there the
long-spot / short-perp hedge loses as the perp catches up.

## Overlap with B
B's rich-side signal (perp-spot basis minus its 168 h median > k at h-1..h+1) fires on only 1.6-7 % of X's cheap
trades. Removing them: k100_H24 IS -62.1 (n 379), VAL -61.8 (n 166); k60_H24 IS -55.6 (n 727), VAL -55.8 (n 389). X is
a different event set from B, and it fails on its own.

## Why this differs from stream V's finding
V measured Binance spot vs other venues' spot at B's (cheap-perp) signal hours, where Binance spot is rich vs the
Binance perp: there the dislocation is Binance-spot specific, and spot falls back to both the perp and the other
venues. X selects on Binance-vs-venues, which mostly picks hours where Binance as a whole (spot and perp) leads a fast
move and the other venues' last trades lag (or Binance-specific flow hits both Binance books). Hedging inside Binance
removes exactly the part that converges.

## Deviations from the declaration
- 1m pricing covered every trade of the four k60 / k100 cells (1,884 unique trades, 100 % priced). The declared seed-0
  1m subsample for the two k30 cells was not pulled: at 1h they are -50 bp per trade with 1-2 % winners and a hedged
  price leg of -1 to -3 bp, so the 1m entry cannot change the verdict (1m and 1h differ by < 6 bp in the k60 / k100
  cells). Their 1m rows in out/m1_main.json are partial coincidences with k60 / k100 windows and are not used.
- OKX was pulled by 3 parallel workers (each >= 0.3 s between requests, ~4-5 req/s combined, under OKX's documented
  20 requests / 2 s), stated in addendum 1 before any return was computed.

## Pitfalls / notes for later rounds
- Cross-venue spot gaps at 1h closes on alts are dominated by venue-wide moves where Binance leads and thinner venues
  lag. A same-venue hedge (Binance perp) neutralises it. Any cross-venue rule has to say which leg is anchored, and the
  hedge must be on the other venue.
- Venues serve only listed pairs (survivorship); Coinbase quotes USD (converted with USDT-USD from 2021-05; before
  that 1:1); Bybit spot starts mid / late 2021; OKX history-candles gives 100 bars per request (the slow part, 16.7k
  requests).
- The 168 h median per venue removes the venue level offsets (quote currency, fees); the median over >= 2 venues is
  needed because single-venue prints are noisy.

## What a user decision could unlock
- The tradable form of the wedge would be **long the Binance complex, short the lagging venue** (spot borrow on the
  venue, or that venue's perp): not tested here, and the venue-median move (-22..-56 bp) is partly stale last trades,
  so the fill on the lagging venue is the open question. That would need venue accounts (as V lists) and 1m data on the
  venue side; prior odds low (BX showed perps across venues move together at B's signals).
- Nothing for the no-borrow, Binance-only form: it is closed.

## Files and data
- Code (X/code): [fetch.py](code/fetch.py) (copy of V's polite GET, own log), [lists.py](code/lists.py),
  [windows.py](code/windows.py), [pull.py](code/pull.py), [pull1m.py](code/pull1m.py), [xv.py](code/xv.py) (venue
  attach, signal, simulate, random), [count.py](code/count.py) (IS signal counts), [run.py](code/run.py) (h1 / m1
  stages), [diag.py](code/diag.py), [corr_c3.py](code/corr_c3.py) (not needed).
- Outputs (X/out): count.txt, h1_main.json, h1_main.log, m1_main.json, diag.txt, trades_main_*.npz,
  trades1m_main_*.npz, trades_1m_main*.csv, windows.json, pull_*.out.
- Data: research/data/xvenue_spot/{okx,kucoin,bybit,coinbase}/<BASE>.csv (1h, 2019-12..2024-12), m1/{spot,perp}/
  (Binance 1m windows around 1,884 trades), lists/, robots/; 351 MB. requests.log: 31,051 lines 09:13-10:30 UTC:
  OKX 16,694 x 200 + 36 x 429 (backed off, retried), Coinbase 5,328, KuCoin 1,624, Bybit 1,521, data-api.binance.vision
  2,891, fapi 2,892 (all 200), 61 network timeouts retried, robots: 404 / 401 (none) on Bybit, KuCoin, Coinbase,
  data-api; OKX and fapi robots allow /api. No 403, no 418. 0 WebSearch.
