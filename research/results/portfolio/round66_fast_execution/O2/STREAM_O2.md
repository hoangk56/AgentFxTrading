# Stream O2 (round 66): OKX / Bybit listing announcements -> Binance perp within seconds. Verdict: none

Written Sun Nov 1 14:42:47 UTC 2026 (from `date -u`). The rule, the stamp definitions, the grid, the costs and the power
were declared at 14:26:52 UTC in [HYPOTHESES_O2.md](HYPOTHESES_O2.md), before any aggTrade was downloaded. HOLD
(2025-01-01..) was never requested, loaded or counted. Every event has N < 2025-01-01. Only daily aggTrades files dated
2020-02-28..2024-12-12 and monthly 1m klines up to 2024-12 were pulled. The 2025-26 rows that the announcement APIs
return on their first pages were paged through, never parsed into events and never counted.

## Answer first
- **History.** OKX's keyless list goes back to 2017, with a usable second-level stamp for 2020-24, but the stamp has two
  regimes:
  - before the March 2023 migration it is `businessPTime`, whole seconds from the old CMS;
  - after it is `pTime`, in ms.
  Bybit's list starts on 2022-06-01. Its `dateTimestamp` is author-filled: 50 % of rows sit at second 00. Its
  `publishTime` is only present from 2024-03 and is unreliable. **So Bybit has no IS.** This is reported, not re-split.
- **Events.** There are 128 listings of coins whose Binance perp was >= 7 d old:
  - IS: 60 events on 41 days, all OKX.
  - VAL: 68 events on 54 days, of which 46 OKX and 22 Bybit.
- **There is no seconds-level burst.** The median path of alt vs BTC since N - 60 s is:
  - VAL: +1 bp at 0 s, +1 at +2 s, +2 at +5 s, +6 at +30 s, +8 at +60 s, +10 at +300 s.
  - IS: -1 / -1 / -3 / -3 / -5 / -4 bp at the same points.
  - Best subset, OKX pTime 2023-24: median +1 / +2 / +4 / +11 / +20 bp. The mean rises steadily to +65 bp by +60 s.
    That is a drift over tens of seconds, not a 1-3 s jump.
  - A +1 % onset occurs in only 24 / 68 VAL events (median 54 s after N, 0 within 5 s) and 10 / 60 IS events.
  - **The burst neither follows nor leads the stamp.** Nothing happens within seconds, so the stamp cannot be
    confirmed. This applies especially to the 2020-21 OKX businessPTime events, where the path is flat. Unlike Upbit,
    an OKX / Bybit listing of a coin that already trades on Binance is not a seconds event.
- **Declared rule O2-D5S fails the bars.** The rule is A2-D5L frozen: long alt / short BTC at the first trade >= N + 5 s,
  exit at the stated start or N + 60 min.
  - IS: **+107 bp, t 1.88**, n 60 (41 d). By year: 2020 -26, 2021 +281 (1 / 2 positive). Random 99.6 %.
  - VAL: **+166 bp, t 1.94**, n 68 (54 d). By year: 2022 +450 (n 4), 2023 -26, 2024 +234 (2 / 3 positive). Random
    100 %. **Power 0.25 x sqrt(79) = 2.19.**
  - LIVE fails on IS t (needs 2.5), years and power. DEMO fails on IS t (needs 2.0).
  - The money is not in the seconds. D2-S, D5-S, D10-S and D30-S are nearly equal. D5-5m loses: IS -17 bp, t -1.87.
    The mean comes from holding hours until OKX's own market opens (post-hoc, below).

## Data and history check (research/data/okx_bybit_notice/, requests.log 822 lines)
- **Robots and docs, read first:**
  - www.okx.com/robots.txt allows `/api/*?`, and `/help/<slug>` is not disallowed.
  - api.bybit.com and bybit-exchange.github.io return 404 for robots.txt.
  - www.bybit.com is unreachable from this machine (URLError x5). announcements.bybit.com/robots.txt returns 301 to
    it, so no Bybit article page was fetched.
  - data.binance.vision robots.txt returns 404.
  - OKX docs: 5 requests / 2 s. `pTime` is "actual time first published"; `businessPTime` is the "displayed" time.
  - Bybit docs: `dateTimestamp` is "author fills".
- **Request hygiene.** Requests were spaced >= 0.6 s for OKX / Bybit and >= 0.3 s for data.binance.vision. Plain UA,
  no key, no e-mail. No 403 / 418 / 429. There were two transient read errors, both retried.
- **What was fetched:**
  - OKX: 164 pages of all announcement types, 53 pages of new-listings, and 81 article pages, used for the stated start.
  - Bybit: 92 pages.
  - Binance: 230 daily aggTrades zips (133 alt + 97 BTCUSDT, 2.6 GB). Each was parsed with `python -I` and deleted;
    only the windows were kept (npz/, 32 MB).
  - 163 monthly 1m kline zips for the random benchmark (kl/, 36 MB).
  - 19 fapi fundingRate calls, end-capped at 2024-12-31.
- **OKX stamp regimes.**
  - Before ~2023-03-22, `pTime` is the migration time and `businessPTime` has non-round seconds. The latter is used.
  - After that date, `pTime` (ms) is used when it is within 10 min of `businessPTime`.
  - Listing posts are spread over three annTypes: new-listings to 2021-08, others from 2021-09, and trading-updates
    for 2020-21 perpetuals.
  - 2022 has only 4 qualifying events.
- **Stated start S.** It comes from the OKX body: the earliest trading / enable time in (N, N + 24 h], ignoring
  deposit / withdrawal times. For Bybit it comes from the title. It was found for 72 events; the other 56 exit at
  N + 60 min.

## Results (net bp per trade; 20 bp + A2 slippage + real funding; t clustered by notice day; results.txt)
| cell | era | n (days) | gross | slip | net | t | median | SR | x1.5 | late | years | rand % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **D5-S** | IS | 60 (41) | 131 | 3 | **107** | **1.88** | -2 | 0.25 | 95 | 108 | 2020 -26, 2021 +281 | 99.6 | |
| | VAL | 68 (54) | 189 | 4 | **166** | **1.94** | 36 | 0.25 | 154 | 164 | +450 (4), -26, +234 | 100 | **2.19** |
| | VAL OKX | 46 (34) | 276 | 4 | 253 | 2.08 | 71 | 0.33 | 241 | 249 | +450, +80, +289 | | |
| | VAL Bybit | 22 (21) | 8 | 3 | -15 | -0.20 | -44 | -0.04 | -27 | -15 | 2023 -143, 2024 +92 | | |
| D2-S | IS / VAL | | | | 109 / 167 | 1.91 / 1.95 | | 0.25 / 0.25 | | | | 99.5 / 100 | 2.21 |
| D10-S | IS / VAL | | | | 108 / 164 | 1.91 / 1.92 | | | | | | 99.6 / 100 | 2.17 |
| D30-S | IS / VAL | | | | 108 / 157 | 1.91 / 1.85 | | | | | | 99.2 / 100 | 2.10 |
| D60-S | IS / VAL | | | | 113 / 139 | 1.97 / 1.73 | | | | | | 99.4 / 100 | 1.98 |
| D5-5m | IS / VAL | | | | -17 / +11 | -1.87 / 0.61 | | | | | | 77.7 / 100 | 0.68 |

**Column notes:**
- **late:** entry at N + 10 s.
- **rand %:** percentile of the gross mean against 1,000 sets of same-coin, same-month random 1m-kline entries with the
  same hold, outside N +- 1 d.
- **Max-over-6-cells null:** the 95th percentile of net t is 1.72 (IS) and 1.23 (VAL). The S-exit cells beat it; the
  bars still fail.

## Post-hoc (labelled; they do not choose a rule)
- **By exit source, D5-S:**
  - Exit at the stated start: IS +218 bp, t 2.60 (n 35); VAL +323 bp, t 2.17 (n 37).
  - Exit at N + 60 min: IS -49, t -1.40; VAL -21, t -0.40.
- **By listing type:** spot listings IS +199 / VAL +224 (t 1.63 / 1.69); perp listings +73 / +115 (t 1.13 / 1.01).
- **Fat tails:**
  - IS median -2 bp; 10 % trimmed mean +50; 50 % of trades positive. The top trades are CHZ +1,951, SOL, AXS and
    SAND (~+1,000 each).
  - VAL median +36; trimmed +58. The top trades are MOODENG +3,934 and SPELL +3,225.
  - Minimum leave-one-day-out t: 1.55 (IS) / 1.62 (VAL).
- **Reading.** The sign is a pre-listing drift on Binance between the OKX announcement and the opening of OKX's own
  market, which is hours later. It is not a reaction that a fast bot captures. As a new hypothesis it would be
  contaminated: IS / VAL have now been seen with this split. It could only be registered for a forward test.

## What failed and why
- No seconds-level move. These coins already trade on Binance and other global venues, so a new venue adds little
  immediate demand. A2's mechanism (a new KRW retail pool) is absent.
- IS t 1.88 is below DEMO's 2.0, and 2020 is negative. The OKX 2020 perpetual listings were mostly large caps (ADA,
  LINK, XLM, ATOM), with a flat path.
- VAL power 2.19 is below 3. Bybit adds nothing: VAL -15 bp, and dateTimestamp is not a confirmed publish time.
- The 2020-21 businessPTime stamps cannot be verified, because no burst exists to align them.

## Pitfalls
- OKX pTime before 2023-03 is a migration date. Using it as N would put the events two years late.
- Bybit `publishTime` sits up to months after `dateTimestamp`.
- Event parsing comes from titles. Prize-pool coins and multi-coin perp titles were fixed before pricing.
- "Flexible Staking now available" was excluded.
- Shell `pgrep -f pull.py` wait loops match their own command line. Three wait loops hung this way and were stopped.

## Files
- **Code (O2/code/):**
  - net.py: polite fetcher and log.
  - pull_ann.py: announcement pages.
  - events.py: events and stamps.
  - bodies.py: OKX article pages.
  - starts.py: stated start.
  - perps.py: copy of round 65 A's, unchanged.
  - pull.py: aggTrades and klines.
  - analyze.py: A2 trade logic copied. The only change is that the fundingRate request end time is capped below 2025.
- **O2/:** HYPOTHESES_O2.md, STREAM_O2.md, events.csv, events_rejected.csv, events_s.csv, results.txt, cells.json,
  trades.csv.
- **No PREREG_DRAFT:** no rule passed the IS / VAL bars.
