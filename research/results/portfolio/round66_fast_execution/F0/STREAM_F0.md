# Round 66 stream F0: wick fade entered at the event bar's close (0 / 1 / 3 s), result

Written 2026-11-01 13:48 UTC (from `date -u`).
- Hypotheses: [HYPOTHESES_F0.md](HYPOTHESES_F0.md), 12:24 UTC, before any F0 return. Addendum 1 (pull restart
  after a stall) changed only the download mechanics.
- Draft: [PREREG_DRAFT_F0_bar_close_fade.md](PREREG_DRAFT_F0_bar_close_fade.md) (FORWARD test from 2026-10-30).
- Code: `code/` (ev.py event set, pull.py aggTrades streamer, analyze.py cells and costs).
- Outputs: `out/report.txt` (all numbers below), `out/cells.json`, `out/sample_rows.npz` (per-event prices, small).

No 2025-26 file was requested or loaded. F's HOLD is not used to grade anything here.

## Answer: LIVE-tier on IS / VAL for the three H60 cells. PREREG_DRAFT (forward) written; H15 cells none

Entering at the bar close (first trade after close_e), 1 s or 3 s later, then holding to F's exit (close of e+61),
passes every LIVE bar on IS and VAL, at the declared cost, x1.5, 5x half-spread, one step late and at measured
$10k taker fills. The selected cell (best IS t, declared rule) is E0 H60. Because F's HOLD is known for the
neighbouring e+1-close entry, it is registered only as a forward test: ~333 events, ~3.5 months at the HOLD-era pace.

| cell | era | n | net bp | t (day) | S / trade | median | x1.5 | entry 5h | one step late | real 1st trade | real $10k | years + |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **E0 H60** (kline open) | IS | 380 | +317.4 | 4.81 | 0.248 | +352 | +304.6 | +309.6 | +296.2 (E1) | | | 2 / 2 |
| | VAL | 770 | +334.0 | 4.69 | 0.204 | +322 | +321.1 | +326.1 | +334.6 (E1) | | | 3 / 3 |
| **E0a H60** (first aggTrade >= close) | IS | 380 | +319.5 | 4.90 | 0.249 | +353 | +306.8 | +311.8 | +296.2 (4.37) | +328.5 (5.07) | +289.8 (4.10) | 2 / 2 |
| | VAL | 768 | +339.2 | 4.56 | 0.207 | +322 | +326.4 | +331.4 | +334.6 (4.49) | +351.4 (4.73) | +344.3 (4.89) | 3 / 3 |
| E1 H60 | IS | 380 | +296.2 | 4.37 | 0.237 | +357 | +283.4 | +288.4 | +279.5 (E3) | +313.6 | +291.4 (4.19) | 2 / 2 |
| | VAL | 768 | +334.6 | 4.49 | 0.204 | +311 | +321.8 | +326.8 | +335.6 (E3) | +347.4 | +341.3 (4.88) | 3 / 3 |
| E3 H60 | IS | 380 | +279.5 | 3.89 | 0.222 | +345 | +266.7 | +271.7 | +269.1 (E10) | +301.4 | +277.5 (3.92) | 2 / 2 |
| | VAL | 768 | +335.6 | 4.50 | 0.205 | +305 | +322.8 | +327.8 | +337.0 (E10) | +348.1 | +342.4 (4.87) | 3 / 3 |
| E0 H15 | IS | 380 | +130.1 | 1.58 | 0.135 | +227 | +117.4 | +122.4 | | | | 2 / 2 |
| | VAL | 770 | +222.7 | 4.06 | 0.300 | +281 | +209.8 | +214.8 | | | | 3 / 3 |
| E1 H15 | IS | 380 | +111.1 | 1.26 | 0.117 | +214 | | | | | +113.5 (1.25) | |
| | VAL | 768 | +218.2 | 4.00 | 0.294 | +279 | | | | | +226.8 (4.16) | |
| E3 H15 | IS | 380 | +95.7 | 1.01 | 0.100 | +206 | | | | | +101.5 (1.09) | |
| | VAL | 768 | +219.6 | 3.97 | 0.295 | +269 | | | | | +228.3 (4.09) | |

- Years (net bp), E0a H60: 2020 +495, 2021 +285, 2022 +391, 2023 +266, 2024 +349. All H60 cells are 5 / 5.
- Random entries beaten 100 % in every cell (F's 200 draws per event; weak, they only lose the cost).
  Max-over-6 IS t: real 4.81 (declared E0 H60), null median -1.46, p95 +0.14.
- H15 fails the IS bar (t 1.0-1.6 < 2.0) in every entry: none.
- Crash / spike (E0a H60): IS +664 / -197, VAL +445 / +175. The edge is the crash side, as in F.
- Forward power at VAL size: E0a H60 needs 209 trades (per trade) or 333 (day-clustered) -> 3.5 months at 94.5
  events / month. E1 / E3 H60: 342 / 341 events, 3.6 months. H15 cells would need 4.4-4.6 months but fail IS.

**How much the first minute is worth on IS / VAL:** F's e+1-close entry on the same events is IS +273.0 / VAL +270.5.
Entering at the close instead adds +46 / +69 bp; 1 s late keeps +23 / +64; 3 s late +6 / +65. In VAL the gain is
spread across the whole first minute; in IS it decays within seconds.

**Read with the HOLD fact in mind:** F's HOLD at the e+1-close entry was +42 bp (t 1.17) on 2,080 events (brief).
If the forward edge at the bar close is "HOLD + the IS / VAL first-minute gain" (~+90-110 bp), the per-trade Sharpe
would be ~0.05-0.08, and power 3 would need ~1,400-3,600 events (15-38 months), not 333. That is why the draft keeps
a 12-month cap and calls a 3.5-month fail "not detectable". This is a sensitivity, not a grade.

## Measured cost in the first seconds (aggTrades, 1,148 of 1,150 events)
Full spread = buyer-taker VWAP minus seller-taker VWAP in the window, over their mean (bp); half = / 2. It includes
any price move inside the window, so it is an upper-side estimate in fast seconds.

| window | IS median | IS mean | VAL median | VAL mean |
|---|---|---|---|---|
| bar e-1 (calm-ish reference) | 17.9 | 57.0 | 7.3 | 12.1 |
| last 5 s of the event bar | 29.2 | 54.7 | 17.9 | 27.5 |
| [0, 1) s after close_e | 21.2 | 45.1 | 14.7 | 25.1 |
| [1, 3) s | 23.5 | 43.5 | 15.6 | 23.4 |
| [3, 10) s | 25.5 | 50.9 | 16.7 | 25.8 |
| [10, 60) s | 26.2 | 66.3 | 13.8 | 25.1 |
| [0, 10) s after the H60 exit time | 5.3 | 26.7 | 2.5 | 3.9 |

- Entry half-spread in the first second: median **~11 bp IS / ~7 bp VAL**, mean ~23 / ~13 bp. The declared 3h is
  9 bp (rank < 20) / 15 bp (rank 20-39) and the stress 5h is 15 / 25 bp: the model is about right at the median and
  low at the mean in 2020-21. The exit half-spread (~1-3 bp median) is at or below the model h.
- Slippage of our side vs the any-side first trade: first taker-side trade median 0, mean +7.5 (IS) / +3.2 bp (VAL) at
  0 s; **$10k taker VWAP median +4.3 / +3.9 bp, mean +37.7 / +4.8 bp** (IS mean driven by a few thin books).
- Waiting costs: side-signed price drift from the kline open of e+1 to the first trade at 1 s: median 0 / +4.9 bp;
  3 s: +6.2 / +9.1; 10 s: +27.0 / +18.3. The reversal starts within seconds.
- First trade after close_e arrives in median 14 ms (p90 76 ms). 11 events have no trade for > 1 s, 4 for > 3 s,
  3 for 9-24 min (2021-05-19 Binance outage: WAVES, MKR, SRM; and UNFI 2022-09-06).
- Real-fill cells (prices from the taker side at both legs, fees 10 bp only) are higher than the declared-cost cells
  in every H60 row: the 22-30 bp model round trip is conservative on average once fills are measured.

## Findings beyond the cells
- **Binance 1m kline opens are often the previous close.** In 21.5 % of events (IS 16.6 %, VAL 24.0 %) the kline open of
  e+1 is not the first trade after close_e; in all 80 cases checked it equals the last trade before close_e. This is
  the 1m version of round 63 BY's 1h finding. On these events it is harmless on average (side-signed mean -2.0 / +0.9
  bp), but any "open of next bar" entry must use the first trade; the draft does.
- **The H15 rows do not pass IS** at any entry: in 2021 the 15-minute fade earns only +34-78 bp. The reversal takes ~an
  hour, as F found.
- F's guard reads o_{e+1}. Where that open is the previous close, the guard is trivially met (c_e is beyond half-way);
  the forward rule keeps F's guard unchanged.

## Sample, data, pull
- Population, not sample: all 1,150 F events (960 symbol-days, 984 daily files incl. midnight crossings) were pulled
  in the declared random order; 2 events lack a usable window (data ends before e+62). The sample and the full set
  give the same F e+1-close result (IS +273.0 / +273.0, VAL +270.5 / +273.5).
- research/data/wick_aggtrades/: npz/<SYM>_<YYYY-MM-DD>.npz (984 files, 1.0 GB, rows in [close_e - 2 min, close_e + 65
  min]: time, price, qty, is_buyer_maker), progress.json, requests.log (995 lines: robots.txt 404, 4 HEAD probes,
  1 GET speed test, 984 file GETs at 200, 5 timeouts retried OK; 0 x 403 / 418 / 429 / 503), pull.out, pull2.out.
- Each zip was deflate-decoded on the fly and the connection closed after the last needed row (8.2 GB streamed of
  the files); no zip was written to disk.
- Web searches: 0.

## Pitfalls met
- **Stalled first pull.** After 22 files in 2 min, one connection trickled for 56 min (socket timeout per read never
  fired; G0 saw a stall at the same time). The restart (20 s socket timeout, read1 chunks, 150 s wall per file,
  retries) pulled everything in 18.6 min. Total clock in pulls ~77 min, over the ~45 min guideline because of the
  stall; network time actually used ~21 min.
- **python -I and own modules:** pull.py adds only its own code dir to sys.path (downloads never touch disk).
- One early dry run of analyze.py (to check it ran, output discarded unseen) wrote out/ files that were overwritten
  by the real run.

## What a user decision could unlock
- **Register the forward test** (coordinator): data from 2026-10-30, evaluate at >= 333 events and >= 3 months (~mid
  Feb 2027), cap 12 months. It needs the forward pull of daily 1m klines plus daily aggTrades on event days only
  (~1-2 files per event; minutes).
- **Execution, if it ever passes:** a bot on the kline websocket (or aggTrade stream) that sends a market order within
  ~1 s of the bar close; the IS / VAL loss from 0 to 1 s is ~0-25 bp, from 0 to 10 s ~20-50 bp. Expect a first-second
  half-spread of ~7-11 bp median, 25+ bp in thin books, and dozens of concurrent positions on crash days.
