# Round 39, stream D: retail and broker-client positioning histories (hypotheses, declared before returns)

Brief: [BRIEF.md](BRIEF.md) row D; shared rules in [../round37_forced_flows/BRIEF.md](../round37_forced_flows/BRIEF.md).
Scratchpad: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r39/D/`
(scripts in `scripts/`, downloads in `web/`, fetch log `web/requests.log`). HOLD 2025-01-01..2026-09-24 closed: every
series cut at 2024-12-31 at parse; requests ask only for dates <= 2024-12-31 where the endpoint takes a date.

## Part 1: source list, declared 2026-10-29 13:27 UTC (`date -u`), before any download

Order of probing (stop a source after 2 failed requests to its host; >= 1.5 s between requests to one host):

| # | source | what it would give | expected public timestamp | prior status |
|---|---|---|---|---|
| S1 | Dukascopy SWFX Sentiment Index (www.dukascopy.com/swiss/english/marketwatch/sentiment/, its widget backend on freeserv.dukascopy.com) | long / short share of Dukascopy (SWFX) clients' volume or positions per instrument (FX majors, crosses, XAU, XAG, indices, BTC); history step 30 min-1 day if served | value stamped at its period end; published live | round 31: "dukascopy.com sentiment pages not reachable" (not retried since) |
| S2 | FXCM Speculative Sentiment Index (fxcm/MarketData on GitHub, fxcm-api docs, DailyFX SSI archive) | net long / short ratio of FXCM clients, ~25 symbols, hourly / daily | DailyFX published SSI at fixed times | first search: history is premium (e-mail sale) or login (DailyFX archive): expected unusable |
| S3 | Myfxbook Community Outlook | % long / short of linked accounts per symbol | live | round 31: myfxbook not reachable; first search: current snapshot only |
| S4 | IG Client Sentiment (DailyFX / IG pages) | % of IG clients long per market | live | current only, expected unusable |
| S5 | FXSSI / other sentiment aggregators, broker pages (Saxo, Swissquote, Forex.com, ThinkMarkets, Admirals), Japanese retail broker ratio pages (Gaitame, Minnano FX, Traders, SBI FX) | client long / short ratios | live | round 31: gaitame.com not reachable |
| S6 | Archived research datasets of retail positioning: GitHub, Hugging Face, Zenodo, Mendeley Data, Figshare, OSF (scraped SSI / Myfxbook / OANDA / Dukascopy histories, replication files of Heimer & Simon, Kuo & Lin and similar) | point-in-time history if a scraper committed with timestamps | commit / scrape time | not searched before |
| S7 (fallback, related by-product) | CFTC Commitments of Traders, **non-reportable (small trader) positions**, legacy futures-only (cftc.gov `deacot{year}.zip`, public, no key) | weekly small-trader net long per CME / COMEX / NYMEX market (FX futures, gold, silver, crude, gas, ES, NQ, YM, Nikkei, BTC from 2018) | released Friday 15:30 ET for Tuesday's positions | rounds 4 / 9 used **non-commercial** net (S1-S3, H4); non-reportable positions never loaded |
| S8 (fallback) | AAII Sentiment Survey (weekly, retail investors, since 1987) | % bullish / bearish | released Thursday | 0 hits in results/ |

OANDA's order / position book is excluded (account: a user decision, per the brief). No account, login, key or
CAPTCHA will be used; the widget's own public page parameters are used only if they are the ones any anonymous visitor's
browser sends.

## Part 1 outcome: probes 2026-10-29 13:27-13:34 UTC (fetch log `web/requests.log`)

| # | result | usable? |
|---|---|---|
| S1 Dukascopy SWFX | www.dukascopy.com timed out twice from this Mac (and from WebFetch); freeserv.dukascopy.com answers (204 on `/2.0/`) but every widget path, including the known economic-calendar one, returns 403 to an anonymous request (embed referrer check; not circumvented). Dukascopy's public page offers only now / 6 h / 1 day / 1 month checkpoints; the 30-minute history is in the JForex API (`IFXSentimentIndex`), which needs a (demo) account | **no** |
| S2 FXCM SSI | `sampledata.fxcorporate.com/sentiment/{sym}.csv.gz` (32 symbols) is a free one-month sample: EURUSD file = 2018-01-02..2018-02-01, minute step, 12 series (SSIHist, LongAmountK, orders, NET variants). Directory listing 403, other paths 404. The full history is FXCM's paid "premium data"; the DailyFX SSI archive needs an FXCM login | **no** (one month: information only, not used) |
| S3 Myfxbook | www.myfxbook.com timed out (as in round 31) | **no** |
| S4 IG / DailyFX | dailyfx.com 403; IG client sentiment is a current snapshot only | **no** |
| S5 FXSSI | page reachable; its ratio history API (`/api/ratios`, time1 / time2) sends a user token and anonymous use ends in a sign-in wall after 10 minutes: an account. Not queried (the auto-mode classifier also refused the anonymous probe as access circumvention). Gaitame timed out | **no** |
| S6 datasets | Hugging Face (7 queries) and Zenodo (4 queries) list no retail positioning history; 2 web searches found only Apify scrapers of the current Myfxbook outlook | **no** |
| S7 CFTC COT legacy futures-only | `www.cftc.gov/files/dea/history/deacot{2004..2024}.zip`: 21 files, 200; 17 markets parsed (counts and dates only), 2004-01-06..2024-12-31 (RTY 579 weeks, NZD from 2004-08, BTC from 2018-04-10, Nikkei USD to 2024-12-17) | **yes** |
| S8 AAII | `aaii.com/files/surveys/sentiment.xls` 403 (members' file) | **no** |

**Conclusion of the probe: no free broker-client positioning history reaches 2016-21 with a public timestamp from this
machine.** What would be needed: a Dukascopy JForex demo account (SWFX sentiment history, 30 min, ~2010+), FXCM premium
SSI (paid), FXSSI / Myfxbook accounts, or OANDA's order / position book (account). Per the brief the stream moves to the
related positioning by-product that is public and dated: S7, the small-trader (non-reportable) positions in CFTC COT.

## Part 2: hypotheses on S7 (CFTC non-reportable = small traders), declared 2026-10-29 13:36 UTC (`date -u`)

No COT value has been printed or joined to a price; only row counts and date ranges above.

### Mechanism and side (fixed here, never flipped)
Non-reportable positions are the traders below the CFTC reporting thresholds: retail and small speculators (plus a few
small hedgers). The literature on retail FX / futures traders (Heimer & Simon 2015, Kuo & Lin 2016 on retail FX
losses; Oberlechner 2001; Wang 2003 "Investor sentiment, market timing and futures returns": small traders have no
timing ability, large speculators' sentiment continues, hedgers' reverses; round 31: Japanese retail OI shows the retail
side, not the direction) says small traders are on the losing side. **Declared side everywhere: against the small
traders** (contrarian to their net position or to its change), or, in D3, with the large speculators when they disagree
with small traders. Expected size from the literature: ~0 (Wang 2003 finds no small-trader timing information), so the
prior is "none"; the stream exists because no round loaded this series.

### Data and timing
- x(m, w) = (non-reportable long - non-reportable short) / open interest, futures-only, market m, report as of Tuesday w.
  IC side mapping: EUR, GBP, AUD, NZD, gold, silver, WTI, gas, ES, NQ, DJ, RTY, Nikkei (USD), BTC: futures long = IC
  long (EURUSD, GBPUSD, AUDUSD, NZDUSD, XAUUSD, XAGUSD, XTIUSD, XNGUSD, US500, USTEC, US30, US2000, JP225, BTCUSD);
  JPY, CHF, CAD futures long = IC short USDJPY, USDCHF, USDCAD.
- Public time: Friday 15:30 ET after the Tuesday as-of date. **Weeks with a US federal holiday Monday-Friday of the
  release week are skipped** (release can move), and as-of dates 2013-10-01..2013-11-19 and 2018-12-25..2019-03-05
  (shutdown catch-ups) are skipped. Reports released in 2025 (as-of 2024-12-31) are dropped.
- Entry: Friday 15:50 ET at the IC bid / ask (latency variant 15:51; spread x1.5 variant). Exit: h1 = Monday 15:50 ET,
  h3 = Wednesday 15:45 ET (<= 120 h, the 5-day cap). One trade per market per week, no overlap (h3 exits before the
  next Friday).
- Costs: actual IC spread at both minutes, + 0.6 bp commission on FX and metals, swap per rollover
  (`swap_frac_at`, US2000 uses US30's; energies and BTC IC's 2026 fraction). PRE (2005-15, Dukascopy EURUSD, USDJPY,
  USDCHF from duka/m1; AUDUSD, NZDUSD, XAUUSD, XAGUSD from duka/m1c): IC 2016-17 median spread at the same minute
  + 0.6 bp.
- Eras: PRE 2005-15 (where Dukascopy exists), IS 2016-21 (params), VAL 2022-24. IC energies start 2018 per the cache
  (cells use what exists); BTC from the first COT week in 2018 with IC prices.

### Families (all sides contrarian to small traders)
| id | signal at week w (past only) | rule | params |
|---|---|---|---|
| D1 crowded extreme | z1 = (x_w - mean x_{w-156..w-1}) / sd (>= 104 past weeks) | side = -sign(z1) when abs(z1) > k | k in {1.0, 1.5}; h in {h1, h3} |
| D2 change of positioning | dx_w = x_w - x_{w-1}; z2 = dx_w / sd(dx over w-52..w-1) (>= 40 weeks) | side = -sign(z2) when abs(z2) > k | k in {1.0, 1.5}; h1, h3 |
| D3 small vs large speculators | zL = 156-week z of non-commercial net / OI, z1 as in D1; d = zL - z1 | side = sign(d) when abs(d) > k (with the large specs, against small traders) | k in {1.0, 2.0}; h1, h3 |
| D4 FX cross-section | each week rank the 7 currency futures by z1 (retail long foreign currency vs USD) | short the 2 most retail-long currencies vs USD, long the 2 most retail-short, equal weight | h1, h3 |

Cells: D1, D2, D3: 17 markets x 2 k x 2 h = 68 each (204); D4: 2. **Primary grading = the pooled book per family and
(k, h)** (equal-weight mean across markets with a signal that week, one return per week: 12 book cells + D4's 2 = 14);
single-market cells are secondary and judged against the best-of-204 null.

### Power arithmetic (before any return)
- About 43 tradable weeks a year after holiday skips. IS ~258 weeks, VAL ~129, HOLD (2025-01..2026-09) ~75.
- LIVE needs HOLD power >= 3: weekly Sharpe >= 3 / sqrt(75) = 0.35 per book week (annual ~2.3), i.e. an IS t of ~5.6.
  No COT study reports anything close; **LIVE is out of reach for every cell from the count**, single markets
  included (same count).
- DEMO needs IS t >= 2 (weekly Sharpe ~0.125 on 258 weeks), VAL net > 0, random >= 90 %. Reachable only if small-trader
  positioning carries ~0.1-0.15 sd per week, which the literature does not support. Expected verdict: none.

### Controls
- Random: 200 seeds of random tradable Fridays in the same era with the same side sequence; and the side recomputed
  from the unthresholded signal at the random week.
- Day-clustered t (one return per week per book, so plain t on weekly returns; single markets plain t).
- Report 2020-03/04 excluded as well. Chance: median and p95 of the best |t| over N cells by simulation with the
  observed cross-cell correlation (sign-flip of weeks applied to all cells at once).

## Part 3: second fallback sources, declared 2026-10-29 13:39 UTC (`date -u`), after part 2's numbers (part 2: no cell
passes; results in STREAM_D.md), before any download of these

| # | source | gives | public time |
|---|---|---|---|
| S9 | JPX weekly "Trading by Type of Investors" for **derivatives** (www.jpx.co.jp statistics-derivatives / investor type; Nikkei 225 futures, mini, options) | individuals' (retail) and foreigners' weekly net buying of Nikkei 225 futures | Thursday after the week (~15:00 JST) |
| S10 | NAAIM Exposure Index (naaim.org, weekly) | active managers' equity exposure (not retail; a positioning survey) | Wednesday / Thursday |

Hypotheses (written now, sides from the literature, never flipped):
- J1 (S9): fade individuals' Nikkei 225 futures net buying (Kuo & Lin / Japanese individuals as contrarian
  liquidity providers who lose short term; round 31 X2 tested **cash** individuals and failed, this is futures):
  z of the week's individuals' net (futures + mini in large-contract equivalents) vs 52 weeks, abs(z) > k, k in
  {1.0, 1.5}; JP225 entry at the release day 07:00 UTC (16:00 JST), exits +1 day and +3 days at 07:00 UTC; side
  -sign(z). 4 cells.
- J2 (S9): follow foreigners' Nikkei 225 futures net buying (Kamesaka-Nofsinger-Kawakita: foreigners' flows lead),
  same z, k, clocks; side +sign(z). 4 cells.
- N1 (S10): fade NAAIM extremes on US500: z of the index vs 52 weeks, abs(z) > k, k in {1.0, 1.5}, entry Thursday
  15:50 ET after the Wednesday release, exits Friday 15:50 ET (h1) and Tuesday 15:50 ET (h3); side -sign(z). 4 cells.
Power: weekly, ~45 trades a year at most, HOLD ~80: LIVE impossible (weekly Sharpe 0.34 needed); DEMO needs IS t >= 2.
Chance benchmark: best of 12 (median best |t| ~1.9).

Part 3 note (written 13:55 UTC, after the J run; the NAAIM page was read at ~13:42, before any J data were joined): NAAIM moved to subscription access on 2026-08-01 (page notice), so N1 is
dropped unrun. J1 / J2 run as declared (8 cells); JPX codes: 301 = Nikkei 225 Futures, 313 = Nikkei 225 mini,
investor 50 = individuals, 60 = foreigners.
