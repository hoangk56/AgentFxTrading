# Stream M8 (round 70): corporate BTC-purchase 8-Ks -> Binance BTCUSDT perp within seconds. Verdict: none

Written Sun Nov 1 17:38 UTC 2026 (from `date -u`). Rule, cells, costs and power were declared at 17:30:53 UTC in
[HYPOTHESES_M8.md](HYPOTHESES_M8.md), after the EDGAR text review and before any price was requested. One post-hoc
addendum (A1, same-clock control) is labelled as such. HOLD was never requested or loaded: all filings were accepted
before 2025-01-01 (asserted), and only daily aggTrades files dated 2020-08-11..2024-12-30 were pulled.

## Answer first
- **No LIVE or DEMO cell, no PREREG_DRAFT.** All 4 declared long cells lose in both eras, and the gross is negative
  too. BTC does not rise after a purchase 8-K. It falls about 10 bp in the next 5 minutes.
- **No one trades the filing at seconds.** Over the first 10 s after acceptance, the per-second trade count is 1.15x
  (IS) and 1.08x (VAL) the T-300..T-10 s baseline; in 2024 MSTR it is 0.75x. The median path from T to T+60 s stays
  within +-2 bp. Upbit listings (round 65 A2) show a 1-3 s jump; nothing like that happens here.
- **Median path (FRESH, bp vs the last trade <= T-60 s):**

| era | T-9m | T-5m | T | +5 s | +30 s | +60 s | +2 m | +5 m | +10 m | +30 m | +60 m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IS (n 15) | +2.3 | +2.4 | 0.0 | +1.9 | +7.2 | +2.4 | +2.8 | +0.9 | +13.9 | -5.7 | -25.6 |
| VAL (n 34) | -5.6 | -2.5 | +0.3 | +0.4 | -0.4 | +0.6 | -0.8 | -6.8 | -7.0 | -7.9 | -4.1 |
| VAL MSTR (n 24) | -5.6 | -2.5 | -0.1 | +0.4 | +1.0 | +1.8 | -1.4 | -8.5 | -12.2 | -27.6 | -24.2 |

  Means from T: +5 m -9.2 (IS) / -8.9 (VAL), +60 m -23.9 / -12.8. In 2024, MSTR events rise +11.4 bp over T-9m..T and
  then lose 19.6 bp by +5 m (sd 14.5). That looks like "buy the Sunday hint, sell the 8-K", but it is post hoc.

## Events (EDGAR; HYPOTHESES_M8.md)
- **FRESH (in the cells):** an 8-K, not item 2.02, whose body or exhibit 99.1 states a completed BTC purchase
  announced on the filing date. **2020: 2, 2021: 13 (IS 15 events, 15 days); 2022: 5, 2023: 6, 2024: 23 (VAL 34
  events, 29 days).**
  - By company: MSTR 39 (all of IS); 2024 others: Semler 6, RIOT 2, MARA 1, KULR 1.
  - 21 of 49 fall on Mondays. 43 were accepted at 11-13 UTC, which is 07:00-08:00 ET (MSTR files at hh:00:30-hh:01:00).
    One was after the close (2020-12-04 17:26 ET).
- **STALE (descriptive):** MSTR 2020-09-15 (completed the day before), MSTR 2024-11-12 (announced 2024-11-11, when
  EDGAR was shut for Veterans Day), Semler 2024-06-06 (announced earlier that day).
  - Path at +5 m: +12.9, -15.9, +9.5 bp. No pattern.
- **Excluded:** convertible / ATM offering 8-Ks (they state only the intended use of proceeds), the 2020-09-14
  treasury policy, impairment and director-pay 8-Ks, MARA / RIOT "BTC Yield"-only 8-Ks, Semler supplements, and the
  MSTR 2.02 earnings releases.
  - Block had no purchase 8-K in 2020-09..2021-03.
  - Tesla disclosed in its 10-K (2021-02-08 12:27:23 UTC), which is a one-event anecdote, below.
- **Acceptance times:** `acceptanceDateTime` is true UTC. Five `-index.htm` "Accepted" values (ET) equal the JSON value
  minus 4 h (EDT) or 5 h (EST). Stamps are whole seconds. The entry lag at the first trade >= T + d was a median 5.07 s
  for d 5 s and 30.04 s for d 30 s.
- **Timing vs the company's own release:**
  - **MSTR 2021-24:** the 8-K text is the announcement ("On <filing date>, MicroStrategy announced ..."), with no
    press-release exhibit. Press reports (Blockworks 2021-11-29) say Saylor's tweet followed the 8-K.
  - **2020-08-11 and 2020-12-04:** same-day press release, order unknown.
  - **Semler / KULR:** they attach a same-day wire release, which probably came minutes before the 8-K.
  - **From mid-2024:** Saylor's Sunday posts pre-announce the Monday buy. The 8-K adds only the size.
  - Tweet seconds would need X, which is not allowed.

## Results (net bp per trade: gross - 10 bp taker - spread - funding; t clustered by day; results.txt)
| cell | era | n (days) | gross | spread | **net** | **t** | median | SR | x1.5 | late | years (net) | rand % | power (n 90) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D5-5m | IS | 15 (15) | -10.8 | 0.06 | **-20.9** | -2.51 | -22.6 | -0.65 | -25.9 | -20.9 | 2020 -24.7, 2021 -20.3 | 8 | |
| | VAL | 34 (29) | -9.6 | 0.02 | **-19.6** | -6.60 | -17.2 | -1.01 | -24.6 | -18.4 | -9.5, -25.8, -20.1 | 0 | -9.6 |
| D5-60m | IS | 15 (15) | -24.8 | 0.05 | **-34.9** | -1.51 | -29.9 | -0.39 | -39.9 | -35.4 | -18.3, -37.4 | 9 | |
| | VAL | 34 (29) | -12.8 | 0.02 | **-22.8** | -2.08 | -16.9 | -0.38 | -27.8 | -21.7 | -13.2, -43.5, -19.5 | 15 | -3.6 |
| D30-5m | IS | 15 (15) | -10.8 | 0.10 | **-20.9** | -2.90 | -22.3 | -0.75 | -25.9 | -20.5 | -27.0, -19.9 | 4 | |
| | VAL | 34 (29) | -8.4 | 0.02 | **-18.4** | -6.50 | -18.5 | -0.97 | -23.4 | -20.9 | -13.6, -24.5, -17.9 | 0 | -9.2 |
| D30-60m | IS | 15 (15) | -25.3 | 0.06 | **-35.4** | -1.64 | -36.0 | -0.42 | -40.4 | -33.5 | -21.5, -37.5 | 9 | |
| | VAL | 34 (29) | -11.7 | 0.02 | **-21.7** | -2.05 | -19.4 | -0.37 | -26.8 | -21.7 | -16.3, -42.4, -17.5 | 19 | -3.5 |

**Column notes:**
- **spread:** the summed half-spreads at entry and exit, from aggTrades (opposite-aggressor neighbours within +-5 s).
  It is negligible on BTCUSDT.
- **Funding:** no hold crossed a funding stamp (0.00).
- **late:** the next d (5 -> 30 s, 30 -> 60 s).
- **rand %:** the percentile of the gross mean vs 1,000 sets of same-day random entries outside [T-2h, T+2h].
- **power:** SR x sqrt(90).
- **Max-over-4-cells null:** the 95 % quantile of the max net t is 1.49 (IS) and 0.57 (VAL). Every observed t is
  negative.
- **MSTR vs others in VAL:**
  - MSTR alone: D5-5m -25.3 (t -6.60), D5-60m -38.2 (t -3.52).
  - The other 10 filings: -5.9 (t -1.35) and +14.1 (t 0.69).

## Post-hoc control (addendum A1, control.txt; does not choose anything)
Same cells at the same UTC clock time 7 and 14 days earlier (same weekday, event days skipped): 76 windows on 70 days.

| cell | era | event gross (t) | control gross (t) | event - control |
|---|---|---|---|---|
| D5-5m | IS | -10.8 (-1.30) | -4.0 (-0.67) | -6.8 |
| D5-5m | VAL | -9.6 (-3.22) | -4.2 (-1.60) | -5.4 |
| D5-60m | VAL | -12.8 (-1.17) | -5.0 (-0.40) | -7.8 |
| D30-5m | VAL | -8.4 (-2.97) | -2.7 (-1.09) | -5.7 |

- About half of the 5-minute fall is the clock: BTC is weak at 07:00-08:00 ET on ordinary days too. The other ~5 bp
  goes with the filing.
- 2024 MSTR controls are flat (+5 m mean -1.3) while the events lose 19.6.
- The mirror short is not tradable even post hoc. D5-5m short nets +0.8 bp (IS) and -0.4 bp (VAL), because the
  10 bp fee eats the 10 bp gross. D5-60m short nets +14.8 (IS, t ~1.1) and +2.8 (VAL).

## Tesla 10-K (one event, anecdote)
The 10-K was accepted at 2021-02-08 12:27:23 UTC.
- For the first 10 minutes BTC is flat to down: -10 bp at +5 s, -19 bp at +5 m, 0 at +10 m.
- The jump starts at +943 s (+50 bp), reaches +500 bp at +1,105 s, and stands at +1,318 bp by +60 m.
- So the market read the filing about 16 minutes after EDGAR acceptance, when wires and Twitter picked it up. A reader
  of the EDGAR feed would have had ~15 minutes.
- It is one event, and since then no first-time corporate buyer of Tesla's size has filed. It cannot be tested.

## What failed and why
- **The disclosed buying is already done, and it is small next to BTC volume.** 2021 buys were $10-15 m. The market
  does not trade the stamp: no activity burst at T.
- **In 2024 the fact of a Monday buy was anticipated.** Prices rose before the stamp and fell after it.
- **IS is 15 MSTR events.** Even a perfect cell would need SR >= 0.65 for IS t 2.5.

## Pitfalls
- EDGAR is closed on federal holidays. A purchase announced on a holiday Monday (2024-11-11) is filed the next day,
  so the 8-K is stale.
- MSTR often files two 8-Ks minutes apart (the convertible closing, then the purchase). Use the purchase filing
  (2024-03-11 11:46:52, 03-19 12:10:31, 06-20 12:12:30, 09-20 13:04:52).
- MARA / RIOT "BTC Yield" 7.01 8-Ks look like purchase disclosures but carry none. Semler 8-K bodies point to ex 99.1,
  which must be fetched to see the purchase.
- The events cluster at 07:00-08:00 ET, so random same-day entries are not a time-matched null. Use the same clock
  time on other days.
- company_tickers.json is a current file (2025-26 names). It was used only to map tickers to CIKs.

## What a user decision could unlock
| direction | value |
|---|---|
| A real-time EDGAR feed (efts / RSS polling, allowed) for unscheduled first-time treasury adoptions by large issuers (Tesla-type, ~16 min lead in the one case) | not testable on <= 2024 data (1 event); forward-only, LIVE < 1 % |
| A pre-registered forward-only short of BTC 5 m after Monday MSTR 8-Ks (post hoc here; gross ~10 bp vs a 10 bp fee) | LIVE < 1 %, DEMO ~1 % (needs a maker entry) |

## Data and requests (research/data/btc_treasury_8k/, requests.log 321 lines, 2026-11-01 17:22:39-17:37:03 UTC)
- **robots.txt:**
  - www.sec.gov has only `User-agent: *`, and Archives is not disallowed.
  - data.sec.gov and data.binance.vision return 404.
- **SEC:** 202 requests, 15.7 MB.
  - data.sec.gov: 9 x 200 + 1 x 404 (robots).
  - www.sec.gov: 189 x 200, plus 3 x 503 that were backed off (30 s) and then returned 200.
  - The User-Agent had no e-mail and no name. There was no 403 / 429.
- **data.binance.vision:** 118 daily `futures/um/daily/aggTrades/BTCUSDT` zips, all 200, 2.89 GB. That is 48 event
  days + 70 control days, 2020-07-28..2024-12-30.
  - UA `research-script`.
  - Each zip was parsed under `python -I` and deleted (tmp/ is empty).
- **Kept:**
  - npz/ (97 MB): trades in [T-10m, T+70m], plus a 1 s last-price / count series per day.
  - raw/ (15 MB): submissions JSON, 8-K primary docs, 7 exhibits, index pages.
  - candidates.csv, filings_parsed.csv, events.csv, controls.csv.
- **WebSearch:** 2 of 15, on tweet vs 8-K timing (inconclusive, apart from the Blockworks 2021 line).

## Files
- **Code (M8/code/):**
  - net.py: polite fetcher and log.
  - edgar1.py, edgar2.py: submissions and primary docs.
  - parse8k.py, review.py: text flags.
  - events.py: FRESH / STALE / TSLA10K.
  - pull.py: aggTrades.
  - analyze.py: path, cells, random, power.
  - controls.py, control_an.py: post-hoc A1.
- **M8/:**
  - HYPOTHESES_M8.md, STREAM_M8.md
  - results.txt, control.txt, trades.csv, cells.json
