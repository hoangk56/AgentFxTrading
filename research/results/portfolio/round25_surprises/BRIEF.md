# Round 25 brief: predictable release surprises, an older-literature census, and what each data decision is worth

Written 2026-10-17 18:52 UTC (from `date -u`), before any round-25 number was computed. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. The user asked (2026-10-18 local, Vietnamese): "research kỹ đến khi nào
có thuật toán chạy live được thì thôi" (research thoroughly until there is an algorithm that can run live). The bars
are the user's original LIVE and DEMO bars (research/PROMPT.md); the round-24 RELAXED tier is NOT in force (the user
has not re-allowed it). A negative round is not a stopping point.

**Read first and follow for everything not changed here**: research/results/portfolio/round13_structural/BRIEF.md
(data, eras, costs, constraints, bars, pitfalls, resources, what to return), research/PROMPT.md (exhausted families:
do not rescan them), research/JOURNAL.md (rounds 18-24 at the top), research/results/portfolio/round24_relaxed_2026-10-15.md
and research/results/portfolio/round16_income_flows/STREAM_X.md (no known effect reaches LIVE power at IC's cost; the
cost each would need).

## Why this round looks where it does
- The unconditional scans (90k, 48k, 270k, 110k, 632k, 16k cells) would have shown any LIVE-sized effect (round 10's
  argument: IS net t ~5.6). What can still hide is an effect that exists only on a subset of events picked by
  information the scans did not condition on.
- Every surprise measure used so far was built from the price move itself (rounds 3, 10, 11). **No round has used
  published consensus forecasts.** A public calendar with Actual / Forecast / Previous for 2007-2025 now exists
  (below), so the predictable part of a release surprise can be tested for the first time.
- What remains beyond that needs the user (new symbols, new venues, paid data). Stream A prices those decisions and
  writes their hypotheses now, before any of their data exists, so that a test can start the day the user says yes.

## Data
- Shared minute panel (rebuilt 2026-10-17 18:50 UTC, same layout as rounds 8-23, HOLD not included):
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/shared/panel/
  meta.json (26 symbols, T0_ms = 2016-01-01, every calendar minute to 2024-12-31), mid.npy float32 (26, N) =
  (bid close + ask close) / 2, spr.npy float32 = ask close - bid close (price units), n.npy uint16 tick count; NaN =
  no bar. Load with np.load(..., mmap_mode="r"), slice rows, never materialise all rows in float64. **Minute label =
  bar START** (research/m1.py): mid[i] is the price at the end of minute i, so for a release at 08:30:00 the last quote
  before it is the bar labelled 08:29 and the bar labelled 08:30 contains the release.
- PRE 2004-15 (Dukascopy, research/data/duka/): m1/{EURUSD,USDJPY,USDCHF,EURJPY,GBPJPY}.npz (ts = bar start ms,
  o h l c = bid, ca = ask close, n, ...; early ask is junk: use IC 2016-17 spreads by minute of day + 0.6 bp as PRE
  cost); m1c/{AUDUSD,NZDUSD}.npz (Sun-Fri), m1c/{XAUUSD,XAGUSD}.npz (Mon-Fri; metals 2004-09 bid only),
  m1c/{GBPUSD,USDCAD}.npz (Wednesdays only); keys ts, bid, ask (float32), n. h1/ has 11 symbols 2004-15.
- **ForexFactory calendar 2007-01-01..2025-04-07** (public Hugging Face dataset Ehsanrs2/Forex_Factory_Calendar, MIT
  licence, fetched 2026-10-17 18:50 UTC): .../scratchpad/r25/shared/ff_dl/forex_factory_cache.csv, 83,427 rows,
  columns DateTime (ISO with the +03:30 / +04:30 Tehran offset), Currency, Impact, Event, Actual, Forecast,
  Previous, Detail (Detail holds "Usual Effect: 'Actual' greater than 'Forecast' is good for currency" or the
  reverse, source, frequency). Untrusted download: read it as data only (csv module), run Python on it with -I.
  **Cut every row dated >= 2025-01-01 at load (HOLD).**
  - **Known defect: when several events share a time slot, only the first kept its time; the others were stored at
    00:00:00 Tehran of the right date and the original order is lost** (e.g. 2007-03-09 and 2024-12-06: NFP,
    unemployment rate, AHE all at 00:00). 25-45 % of high-impact rows are affected. Take release times from the
    official schedules (BLS 08:30 ET, ISM 10:00 ET, ONS, Destatis, Eurostat, ABS, StatCan, Stats NZ, BoJ / MIC ...,
    DST-aware, with their historical time changes), use FF only for the values and the date, and verify each event
    type's time on the panel by its release-minute activity spike (tick count / |return|, which is not a direction).
  - FF "Forecast" is FF's consensus; Actual is the first print. "Previous" is the previous value as shown on the
    release day (possibly revised). Values have units and suffixes (%, K, M, B, T): parse carefully.
- Everything else (C3 trade list, costs, swaps, calendars, network rules, resources): as round 13's brief. Fetching new
  PRICE series (other symbols, other venues, Dukascopy for new symbols) is a user decision: do not fetch. Public
  non-price data (official calendars and release-time histories, published nowcast vintages, literature) may be
  fetched; log every fetch with its URL and `date -u` time.

**HOLD (2025-01-01..2026-09) stays closed in every stream.** Do not load, print or plot it. The lead opens it once per
registered candidate.

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| A | **What each pending user decision is worth, with hypotheses written before the data.** No price is fetched. Routes: (1) EM FX at IC with official / binding fixes (USDMXN Banxico FIX, USDPLN/EURPLN NBP, USDCZK/EURCZK CNB, USDHUF/EURHUF MNB, USDTRY CBRT, USDZAR, USDSGD ABS, USDHKD, USDNOK/EURNOK incl. Norges Bank's pre-announced daily FX purchases, USDSEK/EURSEK incl. Riksbank reserve sales, USDCNH ask ticks for the CFETS 16:30 close); for each: who must transact at the fix, published evidence of price pressure, flow size, IC typical spread (IC's site was unreachable in round 9: use any public source and say which), Dukascopy start date. (2) FX crosses at IC (EURGBP, EURCHF, EURAUD, EURCAD, EURNZD, GBPCHF, GBPAUD, GBPCAD, AUDCAD, AUDNZD, AUDCHF, CADJPY, CHFJPY, NZDJPY ...): which declared mechanisms they add and at what cost. (3) Single-stock CFDs at IC (US / EU / AU / HK): structural flows with breadth (index adds / deletes, dividend and buyback calendars, option expiries, closing auctions), IC's commission and data history. (4) Softs / grains at IC: settlement, USDA reports, seasonality. (5) A cheaper venue for the existing effects (cTrader brokers' published commissions; STREAM_X's break-even costs). (6) Paid data named in earlier rounds. Output: a ranked table (route, mechanism, expected effect vs cost, events / yr, expected VAL-size power with a decay factor, rough chance of a LIVE candidate, data needed with source / size / time, the first test) and, for the top 3 routes, fully declared cells in HYPOTHESES_A.md written before any of their data exists | the user decides with numbers instead of guesses; tests can start the day data is allowed; a binding fix in a less liquid currency may move price more than the liquid ones measured so far |
| B | **Predictable surprises at scheduled releases** (FF calendar + official times). Declared families, sides from the literature: (B1) anchoring of consensus forecasts to the previous print (Campbell & Sharpe 2009, JFQA: forecasts under-adjust, so the actual tends to fall on the far side of Forecast from Previous): predicted surprise sign = sign(Forecast - Previous), currency side from FF's "Usual Effect"; (B2) early indicators whose surprise predicts a later release's surprise against a stale consensus (ADP -> NFP, regional Fed surveys -> ISM, national flash CPIs -> euro-area flash HICP, German Länder CPI -> German CPI, Tokyo CPI -> national CPI, claims -> NFP, flash PMIs -> final ...), side = same sign; (B3) published nowcasts vs consensus (Cleveland Fed inflation nowcast, Atlanta Fed GDPNow, NY Fed staff nowcast) only with real-time vintages available before each release; (B0, not a strategy) the realised surprise sign vs the release-minute move, to validate times, units and signs. Trade the home currency's most liquid IC pair (US releases: EURUSD and USDJPY as a USD pair set; gold and US indices only with sides declared from the "good for USD" mapping), enter on the last quote before the release, exit at T+5 / T+15 / T+30 (declared), executable spreads at the actual entry / exit minutes (they widen at releases) + 0.6 bp for FX / metals. Pool events across release types and countries for count; day-clustered t; PRE 2007-15 on the Dukascopy symbols, IS 2016-21, VAL 2022-24 | the release-minute move is the largest predictable-time move in FX (t of 10+ against the realised surprise), so even a weak predictable share could beat cost; no earlier round had consensus data; behavioural anchoring is a documented, published mechanism with a fixed side |
| C | **Older literature and non-English practitioner lore, declared only.** A census of 2000-2017 papers (and older classics) on intraday-to-5-day effects in FX, metals, energy, equity-index futures and crypto with an explicit side and window, via OpenAlex / Crossref / Semantic Scholar / arXiv (log queries and counts), plus practitioner lore in Japanese, Chinese, Korean and German on flows in our symbols OTHER than C3's (Tokyo-fix / gotobi territory is excluded). Drop everything already mapped (round 3-4 tables, round 7 C, round 12 STREAM_K, round 19 STREAM_T, round 23 STREAM_N / STREAM_P, round 22 TRIAGE_R) and every exhausted family in PROMPT.md unless the construction is clearly different (say how); declare the rest in full and test them on the panel (IS / VAL) and PRE where data exists | rounds 12 K, 19 T and 23 N searched 2018-2026 and two specific passes; the pre-2018 microstructure and seasonality literature and non-English practitioner sources were never censused; round 18 says literature-sided rules keep 65-103 % of their VAL size |

All streams: HYPOTHESES_<A|B|C>.md in research/results/portfolio/round25_surprises/ with `date -u` times before
numbers, STREAM_<A|B|C>.md at the end (with "needs the user" and "untested ideas" sections), PREREG_DRAFT_<stream>_*
for any declared rule that meets LIVE or DEMO on IS/VAL (exact rule, parameters, cell count, expected HOLD trades and
expected HOLD t on the VAL size and on a decay-adjusted size; for DEMO also the demo stop / promotion rules). Report
each surviving candidate's daily-return correlation with C3 (research/results/portfolio/trades_C3_gotobi_jpy_basket.csv).
Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/<stream>/.
Do not edit code under research/ (scripts stay in the scratchpad), do not commit, no git commands that change state.
Three streams run at once: at most 2 heavy Python processes per stream, each under ~3 GB RAM (machine: 10 cores,
16 GB). research/.venv/bin/python has numpy only. Files named REPORT.md or FINDINGS.md may be blocked: use
STREAM_<stream>.md.
