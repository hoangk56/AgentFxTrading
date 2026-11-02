# Stream M8 hypotheses (round 70): corporate BTC-purchase 8-Ks -> Binance BTCUSDT perp within seconds

Written Sun Nov 1 17:30:53 UTC 2026 (from `date -u`), after the EDGAR pull and text review, **before any price was
requested or read**. HOLD (2025-01-01..) is never requested: only filings with acceptance <= 2024-12-31 are kept
(asserted in code), and only daily aggTrades files dated <= 2024-12-31 will be requested.

## Mechanism
A listed company's 8-K that discloses a completed BTC purchase is public information about a large, price-insensitive
buyer, released at a known second. If traders read it as continuing demand (the company keeps buying, others copy),
the BTC perp may keep drifting up after the stamp. Side fixed: **long BTC**. Counter-prior: purchase sizes are small
next to BTC daily volume, the buying is already done when it is disclosed, and from mid-2024 Saylor's Sunday posts
pre-announce the Monday 8-K, so the news may already be in the price.

## Data (EDGAR, done; research/data/btc_treasury_8k/, requests.log)
- robots: www.sec.gov has only a `User-agent: *` block (Archives not disallowed); data.sec.gov and data.binance.vision
  robots.txt return 404. UA "Mozilla/5.0 (compatible; offline-market-research/1.0; aggregate filing timestamps)",
  no name or e-mail, one sequential process, >= 0.3 s per host. 203 requests so far, 15.7 MB; 3 transient 503 on
  www.sec.gov (backed off 30 s, then 200), no 403 / 429.
- Submissions JSON for MSTR (1050446, + older page), Semler (1554859), MARA (1507605), KULR (1662684), RIOT (1167419),
  Block (1512673, + older page), Tesla (1318605). company_tickers.json was used only to map tickers to CIKs.
- 163 candidate filings (MSTR all 8-Ks 2020-24; Semler / MARA 2024; KULR / RIOT 2024-11..12; Block 2020-09..2021-03;
  Tesla 2021-01..03 incl. the 10-K), each primary document fetched and parsed under `python -I`; exhibit 99.1 press
  releases fetched for 7 Semler / KULR filings whose 8-K body only points to the release.

## Acceptance time check
- `acceptanceDateTime` in the submissions JSON is **true UTC**: 5 filing `-index.htm` pages show "Accepted" in ET
  that equals JSON UTC - 4 h (EDT, 2020-08-11, 2022-03-29) or - 5 h (EST, 2021-02-17, 2024-12-23, 2024-12-26).
- Whole seconds; the real public time on EDGAR is acceptance + dissemination lag (normally seconds; unknown per
  filing). Entry is at acceptance + d with d >= 5 s.
- EDGAR is closed on US federal holidays: the 27,200 BTC purchase was announced on 2024-11-11 (Veterans Day) and the
  8-K came at 2024-11-12 13:01 UTC, so that filing is STALE.

## Event definition (fixed now)
- **FRESH** = an 8-K (not item 2.02 earnings) whose body or exhibit 99.1 states a completed BTC purchase announced on
  the filing date, with no earlier-date announcement in the text. If one filing day has two filings (e.g. the
  convertible-closing 8-K and the purchase 8-K minutes apart), the event is the purchase filing. Not events:
  convertible / ATM offering 8-Ks that only state intended use of proceeds, treasury-policy 8-Ks (2020-09-14),
  impairment, director pay, MARA / RIOT "BTC Yield" 8-Ks without a purchase, Semler supplementary disclosures.
- **STALE** = the 8-K reports a purchase already announced on an earlier date: MSTR 2020-09-15, MSTR 2024-11-12,
  Semler 2024-06-06. Descriptive only (path), not in the cells.
- Tesla's BTC purchase was disclosed in its 10-K (2021-02-08 12:27:23 UTC), not an 8-K: reported as a one-event
  path, not in the cells. Block (Square) had no purchase 8-K in 2020-09..2021-03.
- **Counts (FRESH):** 2020: 2, 2021: 13 (IS 15 events, 15 days); 2022: 5, 2023: 6, 2024: 23 (VAL 34 events, 29
  days). 2024 split: MSTR 13, Semler 6, RIOT 2, MARA 1, KULR 1. MSTR total 39. Weekdays: Mon 21, Tue 9, Thu 7,
  Fri 7, Wed 5. Acceptance hour UTC: 11: 3, 12: 18, 13: 25, 14: 2, 22: 1 (2020-12-04 17:26 ET, after the US close).

## Timing vs the company's own press release / tweet
- MSTR 2021-24 purchase 8-Ks are item 8.01 (+7.01 from 2024-09) **with no press-release exhibit**: the 8-K text is
  the announcement ("On <filing date>, MicroStrategy announced that ... acquired approximately N bitcoins"). Press
  reports (e.g. Blockworks 2021-11-29) describe Saylor's tweet as following the 8-K filing on Monday morning. Exact
  tweet seconds are not available without X; treated as "8-K first or simultaneous". 2020-08-11 (press release
  attached as ex 99.1, 8-K 07:12 ET) and 2020-12-04 (8-K 17:26 ET, "On December 4 announced") are same-day with the
  release order unknown.
- Semler and KULR 8-Ks attach the press release as ex 99.1 dated the filing day: the wire release most likely came
  first by minutes (order unknown). MARA 2024-12-02 and RIOT 2024-12-13 / 12-16 are 8.01 / 7.01 text with no exhibit.
- From mid-2024 Saylor posted a Sunday hint of a Monday purchase; the content (size) is new at the 8-K, the fact of
  buying is partly anticipated. This is a reason to expect a weaker effect in 2024, declared before prices.

## Rule and declared cells (4)
- Signal time T = acceptanceDateTime (UTC). Long BTCUSDT perp at the **first aggTrade with time >= T + d**, exit at
  the first aggTrade >= entry time + H. Cells: **d in {5 s, 30 s} x H in {5 min, 60 min}** = 4 cells, run on all FRESH
  events (pooled companies). No parameter is chosen after seeing prices beyond picking among these 4 on IS t.
- Cell choice rule: the cell with the best IS net t; VAL checked unchanged. Every cell is reported.
- One step late: d 5 -> 30 s, d 30 -> 60 s (same H).
- Descriptive (not cells): MSTR-only split; STALE; Tesla 10-K; path -60 s .. +60 min (median and mean, bp vs the last
  trade at or before T - 60 s and vs T); pre-stamp drift T - 10 min .. T; per-second trade count around T (does
  activity jump at T, i.e. does anyone trade the filing?).

## Costs
- Taker 5 bp a side (10 bp round trip) + half the quoted spread at each fill, the spread estimated from aggTrades as
  the median |price difference| between consecutive trades of opposite aggressor side within +-5 s of the fill
  (BTCUSDT tick 0.1, so ~0.01-0.03 bp: expected negligible). Funding: real rate from
  research/data/binance/funding/BTCUSDT.csv if a funding stamp (00 / 08 / 16 UTC) falls inside the hold (expected:
  never, since events are 11-14 UTC and holds <= 60 min). x1.5 costs = 15 bp + 1.5 x spread.

## Statistics and benchmarks
- t clustered by event day (several companies file on some 2024 days). Years positive counted per calendar year.
- Random benchmark: 1,000 sets of same-day random entries (one per event, uniform second of the same UTC day outside
  [T - 2 h, T + 2 h], with a full hold inside the day), same H, from the 1 s last-price series; percentile of the
  observed gross mean. Max-over-4-cells null: the 95 % quantile of the max IS net t over the 4 cells across the same
  random sets (null on the random entries, net of the same 10 bp).
- Limits: same-day random entries are not time-of-day matched (events cluster at 12-13 UTC, before the US cash open).

## Power arithmetic (before prices)
- HOLD count at VAL size: MSTR filed weekly from 2024-11; at that cadence (~1 a week) HOLD 2025-01..2026-10 has ~90
  MSTR purchase 8-Ks, plus other filers. Use n_HOLD = 90 (conservative, MSTR only).
- LIVE needs SR_VAL x sqrt(90) >= 3 -> SR >= 0.32 per trade. With an assumed BTC 60-min sd of ~60-80 bp that is a
  net mean >= ~20-25 bp (gross >= ~30-35 bp); at 5 min (sd ~20-25 bp) a net mean >= ~7 bp (gross >= ~17 bp).
- IS t >= 2.5 with 15 independent events needs SR >= 0.65; t >= 2.0 (DEMO) needs SR >= 0.52. That is, at 60 min,
  gross ~ +50 bp a trade in 2020-21. VAL t >= 1.5 with 29 days needs SR >= 0.28.
- Prior: P(LIVE) ~1-2 %, P(DEMO) ~4 %. Disclosed buys are completed buys and sizes (median ~3,000 BTC for MSTR,
  ~200-300 for the others) are small next to BTC daily volume; in IS the 2021 buys were $10-15 m.

## Addendum A1 (post-hoc, Sun Nov  1 17:34:18 UTC 2026, after the cell results)
The declared long cells are all negative (BTC falls ~10 bp in the 5 min after the stamp in IS and VAL). This addendum
does not change the verdict and cannot create a candidate (the side was fixed long). Post-hoc question only: is the
fall about the filing or about the clock (MSTR files at ~08:00 ET)? Control: the same UTC clock time 7 and 14 days
before each FRESH event (same weekday), skipping event days: 76 control windows on 70 days, same 4 holds, same costs.
