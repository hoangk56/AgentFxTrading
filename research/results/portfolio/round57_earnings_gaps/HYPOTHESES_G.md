# Round 57 stream G hypotheses: large earnings gaps on US large-cap CFDs, entered after the opening auction

Declared 2026-10-30 12:16 UTC (file written; `date -u` read at 12:15:08 and 12:16:19), before any M1 file was requested and before any return
(of any horizon, at any fill) was computed. The only quantity computed before the counts addendum below is the
selection variable itself (the gap = reaction-day first quote / prior close), which is known at 09:30 ET and is not an
outcome. Same LIVE / DEMO bars as research/PROMPT.md (no RELAXED tier). Fixed constraints: lot not capital-dependent,
hold <= 5 days, <= 3 positions per bot (bots needed are reported).

HOLD 2025-01-01..2026-09-24 stays closed: no 2025 / 2026 Dukascopy file is requested (job builder asserts every date
<= 2024-12-31), every series is cut at ts < 2025-01-01 (1735689600000 ms) at parse / load: stream D's panel (cut in
stocklib), IC US500 M1 (cut at load before any use), 8-K events (already cut at 2024-12-31 in round 54 E). At most a
PREREG_DRAFT is written; HOLD is never opened.

## Honesty note: what earlier rounds already saw
- Round 54 E computed, for all 5,340 releases, the reaction-day open-to-close return R_oc (Dukascopy daily open first
  quote -> close, minus US500) and the full reaction R_ear, and graded *subsequent* drift from the day-0 close (1-5
  days) following / reversing them: R_oc follow 3 d mid -2.9 / -2.6 bp, R_ear follow 3 d mid +17.1 / +9.9 bp. It did
  not print the open-to-close return conditional on the gap's sign or size, and nothing after 09:45 at M1. But R_oc
  contains this stream's same-day window (09:45 -> 15:55 is a subset of open -> close), and its quintile thresholds and
  the 1-5 day drift after the close (relevant to the E1-E4 exits here, which run from 09:45 of day 0 to the close of
  day h) were seen in IS and VAL. So the E1-E4 exits are partly seen (their close-to-close tail is round 54's H2), and
  the same-day exit is unseen at the gap-conditioned level but not independent of round 54's R_oc distribution.
- Round 42 E saw index-level after-hours continuation and open-to-close reversal on heavyweight earnings days: absent.
- Rounds 55-56: the spread profile (09:45 ~11 bp, 15:55 ~5 bp on Dukascopy M1), IC commission ~12 bp a round trip,
  and the large-cap no-news reversal / news continuation cross-section (nothing).
- Consequence: HOLD power is computed at **1/2 of the VAL net size** (brief), not at the VAL size.

## Universe and events
- Firms: stream D's non-ETF stocks with a CIK (D's symbols.csv plus round 54 E's hand CIKs), Dukascopy daily bid / ask
  2016-09..2024-12 (most names from 2017, all from 2018). IS = first data..2021-12-31, VAL = 2022-01-01..2024-12-31.
- Releases: round 54 E's `events.csv` (8-K item 2.02 acceptance date / time ET, first 2.02 filed 10-100 days after the
  fiscal period end, one per firm-quarter).
- Reaction day j: acceptance before 09:30 ET -> the first session on or after the acceptance date; acceptance at or
  after 16:00 ET -> the first session after the acceptance date; acceptance 09:30-15:59:59 -> **excluded** (the gap
  does not contain the news). Require j within 4 calendar days of the acceptance date and valid quotes on j-1 and j.
- Filters (declared now, from the r54-r56 pitfalls): raw prior close (bid / ask mid, day j-1) >= USD 10; no split or
  flagged jump between j-1 and the exit day (D's `adj` / `cjump`); not in 2020-03-09..2020-03-20 only for the
  ex-2020-03/04 variant (that variant drops all of 2020-03-01..2020-04-30).
- Gap g = mid of day j's first quote (D's daily open bid / ask, split-adjusted) / mid of day j-1's close - 1.
- Selection: |g| >= 2 %. If that set is smaller than the top quintile of |g| (IS distribution of all usable releases),
  the top IS quintile of |g| is used instead (the brief's "plus all of the top quintile if that is fewer"; which one
  applies is fixed in the counts addendum before any M1 request).
- Buckets of |g|: [2 %, 4 %), [4 %, 8 %), >= 8 %, each split by the sign of g (up / down).

## Trades
- **Side.** Primary: **follow** the gap (long if g > 0, short if g < 0): gap momentum / announcement-day continuation
  (PEAD starts on the reaction day: Bernard & Thomas 1989; the brief's gap-momentum / PEAD prior; underreaction to
  earnings news should show as a same-direction drift after the opening auction). Declared alternative: **fade**
  (gap fill / opening overreaction to large news, the intraday-reversal reading). Both sides are counted; no
  literature size is claimed for the post-09:45 window.
- **Entry.** The first M1 bar with volume at or after 09:45 ET (primary) or 10:00 ET (variant), within 5 minutes
  (else no trade), filled at that bar's **open ask (long) / open bid (short)** from Dukascopy M1 bid / ask.
- **Exit.**
  - E0 (primary): the first M1 bar with volume in 15:55-15:59 ET of day j, at the bar's open bid (long) / ask (short).
  - E1, E2, E4 (declared variants): the Dukascopy **daily close** bid / ask of day j+1, j+2, j+4 (the session's last
    quote, ~16:00 ET). The brief allows 15:55 M1 of the next 1-4 days; the daily close candle is used instead to keep
    the pull inside one hour (one M1 day per event). E3 is not graded (keeps the grid at 4 exits).
- **Hedge.** H: the opposite position in IC US500, 1:1 notional, at the same minutes (US500 M1 from
  research/data/m1/US500.npz: bid open + mean spread of the minute; for E1-E4 the US500 bar at 15:59 ET of the exit
  day). U: unhedged. Primary: hedged.
- **One position per firm**: earnings are quarterly, so no overlap within a firm.

## Costs (IC MT5 US share CFDs, stream D's model)
- Spread: Dukascopy M1 bid / ask of the traded bar (entry, E0 exit), D's daily close bid / ask for E1-E4.
- Commission: USD 0.02 per share per side on the raw price (= 2 / price-in-cents bp per side).
- Financing per calendar night held (Fri->Mon = 3): long pays (EFFR + 3 %) / 360, short pays (3 % - EFFR) / 360 (a
  credit when EFFR > 3 %); EFFR on the entry date (stocklib `effr`).
- Hedge leg: US500 mean spread of the minute at both fills; swap 2.0 bp a night for a long US500 hedge, 0.5 bp for a
  short one (round 54 E).
- Dividends are not in the data (IC adjusts): holds E1-E4 that cross an ex-date are biased by the dividend (shorts
  look better, longs worse); reported as a caveat, not corrected.
- Variants: spread x1.5 (both legs), +1 minute (entry searched from offset + 1 and E0 exit from 15:56).

## Cells (48 counted)
1. Main grid, all |g| >= 2 %: side {follow, fade} x entry {09:45, 10:00} x exit {E0, E1, E2, E4} x hedge {H, U}
   = 32 cells.
2. Buckets at the primary timing (09:45, E0, H): side {follow, fade} x |g| bucket {2-4, 4-8, >8} x gap sign {up,
   down} = 12 cells.
3. Opening-move condition at the primary timing: m = sign(g) x (mid at the entry bar / mid at the first bar with
   volume in 09:30-09:34 - 1); "extends" m > 0, "retraces" m < 0 (m = 0 dropped); side {follow, fade} x {extends,
   retraces} = 4 cells.
- **Primary cell: follow, |g| >= 2 %, 09:45 entry, E0 exit (15:55 same day), US500-hedged.**
- Reported, not counted: E3; all buckets / conditions at other timings; the non-earnings placebo.

## Controls and statistics
- t: clustered by reaction date (sum of demeaned returns per date).
- Random-firm control: for each reaction date, 2 random non-ETF D stocks (seed 57) with raw price >= USD 10, valid
  quotes on j-1, j and j+4, no release of their own mapped to j-1..j+1, and no split / jump in the window; same entry
  and exit minutes, same hedge and costs; **side recomputed from the random firm's own gap sign** (the rule applied to a
  non-event firm; PROMPT pitfall). 1,000 seeds each pick one of the 2 names per event; "beats" = share of seeds whose
  mean net is below the cell's.
- Placebo (reported, not counted, only if its M1 fits the time budget): non-earnings large gaps of the same size
  (|g| >= 2 %, no release mapped within j-3..j+3), sampled at random up to the event count, same rules.
- Chance benchmark: per-reaction-date sign flips (1,000 draws, shared across all 48 cells) of each cell's **mid**
  (gross) per-trade returns; max over cells of the clustered t; the best observed IS mid t and net t are compared with
  its p95 (gross null, r56 pitfall: a net-null is too easy).
- Top-trade check: no single trade > 20 % of a cell's IS (or VAL) sum when the sum is positive.
- By year, ex-2020-03/04 (IS), x1.5, +1 minute.
- Power at HOLD size: HOLD n = VAL n / 3 x 1.73; power = (VAL net / 2) / sd x sqrt(HOLD n).
- Concurrency: positions open per trading day (E0: per reaction date; E1-E4: overlapping holds), share of days > 3,
  bots needed at <= 3 positions per bot.
- C3 daily-return correlation for any surviving cell (research/results/portfolio/trades_C3_gotobi_jpy_basket.csv).

## Bars (no threshold is lowered)
- DEMO: net IS t >= 2.0, net VAL > 0, beats random >= 90 %, net > 0 at spread x1.5 and +1 minute (IS and VAL).
- LIVE: net IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, beats random >= 95 %, power >= 3 at the 1/2 rule.
- Any cell is also read against the max-t chance benchmark and the top-trade check before a PREREG_DRAFT.

## Power arithmetic (before counts)
- Expected: ~5,300 releases, ~90 % outside market hours, perhaps 40-55 % with |g| >= 2 %, i.e. ~2,000-2,500 events,
  ~250-300 a year; VAL ~800-900, HOLD n ~ VAL n / 3 x 1.73 ~ 450-520.
- LIVE needs Sharpe at the HOLD size of 3 / sqrt(500) ~ 0.13 per trade; under the 1/2 rule the VAL net Sharpe must be
  >= ~0.27. With a 09:45 -> 15:55 sd on earnings-gap days of ~200-300 bp, that is a VAL net of >= ~55-80 bp per trade,
  i.e. a mid edge of ~80-105 bp after the ~25 bp cost. Large-cap gap continuation of that size after 09:45 would be a
  known anomaly; expect LIVE out of reach and DEMO the realistic ceiling (IS t >= 2 needs ~15-20 bp net at IS n ~1,300
  if the sd is ~250 bp and date clustering is mild).
- Exact counts, IS / VAL / HOLD n and the M1 file estimate are appended below before any M1 request.

## Addendum A1: counts, power and pull size (2026-10-30 12:18 UTC, before any M1 request; selection variable only)
From `scratchpad/r57/G/scripts/events.py` (output `out/counts.log`); no outcome after day j's first quote was read.
- 11,754 release rows -> 5,164 usable (4,794 not in D's stock list, 184 intraday releases excluded, 934 outside the
  panel / > 4 days, 625 without quotes j-1 / j / j+4 or with a split / jump, 53 under USD 10). IS 3,013, VAL 2,151.
- IS |gap| 80th percentile 4.82 %, so |gap| >= 2 % (2,920 events) is larger than the top quintile (1,150): **the
  |gap| >= 2 % rule applies.** IS 1,632, VAL 1,288; ~400 a year from 2018 (99 in 2017).
- Buckets IS / VAL: 2-4 % up 419 / 297, down 414 / 295; 4-8 % up 304 / 242, down 295 / 223; > 8 % up 101 / 106,
  down 99 / 125.
- 1,010 distinct reaction dates, 2.89 events per date on average, max 17.
- **Power:** HOLD n at the VAL rate = 1,288 / 3 x 1.73 = 743. LIVE power 3 needs a net Sharpe of 0.110 per trade at
  HOLD size, i.e. **>= 0.22 at the VAL size under the 1/2 rule** (at sd ~250 bp: VAL net >= ~55 bp per trade). The
  bucket cells (VAL 106-297) need VAL Sharpe 0.37-0.62: LIVE is out of reach for any single bucket.
- Pull: events + random pool (2 names per reaction date, seed 57) = 4,940 firm-days, 9,880 files (~37 min at 4.4
  files/s); placebo (non-earnings |gap| >= 2 %, 21,711 candidates, 2,920 sampled at random) = 2,899 firm-days, 5,798
  files (~22 min). Both are pulled in parallel (2 processes); the placebo job list is shuffled so that a pull cut at
  the one-hour mark is still a random subset. Datafeed robots.txt answered 404 at 12:18 UTC (no ClaudeBot entry).

## Addendum A2: pull throttled, sample rule (2026-10-30 12:27 UTC)
- The datafeed answered at ~0.1-0.7 files/s from 12:18 (latency 12-30 s on kept-alive connections, 30-80 % HTTP 503),
  against round 55's 4.4 files/s; 12 workers gave no more than 4-6 (mostly more 503s). Throttling or server load, not
  a bot wall (no 403 / 429). The full pull (9,880 + 5,798 files) cannot finish inside the one-hour budget.
- Rule fixed now, before any graded run on the pulled data: the placebo pull is dropped; the job list is re-ordered by
  **reaction date in a random order (seed 573)**, each date carrying all its events plus its 2 random-pool names, at
  6 workers. The pull stops at ~13:20 UTC (one hour after it began) or when complete. The graded sample is every
  reaction date whose files are all present: a random subset of dates, so unbiased but with lower power. The same 48
  cells, sides, costs and bars apply; the power and the bars are computed on the sample actually graded, and the
  power at HOLD size still uses the full-sample event rate (743 HOLD trades) as the rule's real trade count.
- Disclosure: a code-debug run of grade.py at 12:22 UTC on the 59 events already cached (2 % of the sample, IS 37 /
  VAL 22) printed cell results. Nothing in the design was changed after it; the declared grid above was fixed before.
