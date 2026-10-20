# Round 24 brief: relaxed conditions (new data, a new-era split, a RELAXED tier)

Written 2026-10-15 11:44 UTC (from `date -u`), before any round-24 number was computed. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. After round 23 the user wrote (2026-10-15): "cứ research thử xem, có
thể nới rộng điều kiện" (go ahead and research, the conditions may be relaxed). This brief fixes WHICH conditions are
relaxed, before any number, so the relaxation is not chosen from the results.

**Read first and follow for everything not changed here**: research/results/portfolio/round13_structural/BRIEF.md
(data, costs, pitfalls, resources, what to return), research/results/portfolio/round23_recent/BRIEF.md (the
declared-only rule, the rebuilt panel, the calendar folder), research/PROMPT.md (exhausted families),
research/JOURNAL.md (rounds 18-23 at the top), research/results/portfolio/round23_recent_2026-10-15.md.

## What is relaxed (and what is not)
1. **Data.** Fetching price and flow data is now allowed: Dukascopy M1/H1 bid+ask for any symbol and any date up to
   the latest full day (see the memory note below), public flow data (Farside / issuer ETF flow tables, JITA / Japanese
   investment-trust flow statistics, US Treasury yields, CBOE statistics), official calendars. Store prices under
   research/data/duka/ (git-ignored) as compact npz (int64 ts ms, float32 bid/ask close, uint16 ticks); the disk has
   ~9 GB free, so fetch only the symbols and years a declared hypothesis needs, and log every fetch.
2. **Eras for new mechanisms.** A mechanism that exists only from 2023-24 uses its own split, declared before the
   numbers: DISCOVERY = its start..2025-06-30, TEST = 2025-07-01..latest day fetched. Opening 2025-26 for these is
   allowed; each declared rule looks at TEST once.
3. **A RELAXED tier**, reported next to LIVE and DEMO (both still reported with the user's original bars):
   design-era net t >= 1.5 (day-clustered), check-era net > 0 with t >= 1.0, net > 0 at spread x1.5 and +1 minute,
   beats >= 80 % of random entries, power on the CHECK-era size >= 1.5, and an economic mechanism. A RELAXED candidate
   may only become a small fixed-risk demo with a registered stop rule; it never goes live without passing LIVE or the
   registered promotion rule. HOLD (2025-01..2026-09) may be opened once for a RELAXED candidate after a
   PREREG_DRAFT is written.
4. **Constraints.** Holding up to 20 trading days is allowed for declared seasonal / flow rules (swap is charged).
   Lots stay independent of capital; at most 3 positions per bot.
5. **Not relaxed:** sides come from the mechanism or the source, never from our data; every cell is declared (with
   `date -u` time) before its numbers; executable costs; chance benchmarks for the number of cells; no parameter
   search on the check era.

Dukascopy feed (from earlier rounds): datafeed.dukascopy.com/datafeed/{SYM}/{YYYY}/{MM0}/{DD}/{BID|ASK}_candles_min_1.bi5
(MM0 zero-based; hourly = .../{MM0}/{BID|ASK}_candles_hour_1.bi5), LZMA, records '>5if' = sec offset, open, close,
low, high, volume; scale 1e3 for JPY pairs / XAU / indices, 1e5 other FX (verify per symbol); needs a browser
User-Agent and a kept-alive connection (0.3-1.5 s per file vs 15-35 s one-shot); HTTP 503 = no file; zero-volume flat
minutes = no trading; early ASK files (pre-2010) are junk. Matches IC on 2016 days to ~0.1 bp. Pre-2016 has FX and
metals only; indices / energies start 2012-14. Parallel per-year pulls work. The IC M1 cache research/data/m1 runs
to 2026-09-24 (includes 2025-26).

## Streams
| stream | direction |
|---|---|
| A | **2024+ mechanisms on the new-era split.** (a) Spot BTC / ETH ETF creations: the NAV is struck on the CF Benchmarks NY reference rate around 16:00 ET, so authorised participants and issuers trade into that window; test BTCUSD (and ETHUSD) into/after the window, side by the day's prior net flow or by a fixed mechanism side (Schmidt & Kraft 2026 and others: read and declare from the source); daily flow tables are public (Farside, issuers). (b) New NISA (2024-) accumulation purchases of foreign-equity funds: yen selling on fixed purchase days of the month (find brokers' / fund companies' order and FX-execution days from public sources, JITA monthly flow sizes), USDJPY / EURJPY outside C3's gotobi minutes; report the overlap with C3. (c) any other 2023-26 mechanism with a known side found while reading (US Treasury buybacks have no IC instrument; 0DTE needs CBOE data: fetch only if public). |
| B | **Long history with fetched data.** Pull Dukascopy M1 for AUDUSD, NZDUSD, GBPUSD, USDCAD, XAUUSD, XAGUSD (2004-2015, plus 2016-2026 where useful for one continuous series). Then (a) price the decision round 16 named: the AUD/NZD Sydney-open V and the other effects real at mid (round16_income_flows/STREAM_X.md) on PRE 2004-15 with their sides fixed from IS/VAL; (b) a declared turn-of-year rule (gold long and USD short over the turn of the year, window fixed from the literature, not from round 23's numbers) on 2004-2024, holds up to 20 days allowed, pooled over symbols for power; (c) other literature seasonals with a side that need > 5-day holds (relaxed constraint), declared before numbers. |
| C | **RELAXED re-evaluation of what exists.** Take every effect in round16_income_flows/STREAM_X.md, the round 12-13 DEMO candidates (gold COMEX settlement big days, E1 EURUSD midday short), the FOMC-day dollar short (round 20), round 23's N3b and the reopen-gap fade, with their already-declared rules and sides. Score each against the RELAXED tier on the eras where they were designed and checked (no new parameters). Then: a declared book of the RELAXED survivors (equal risk, at most 3 positions per bot), its IS/VAL net, correlation with C3, and power; and the cost each would need to reach LIVE. Write PREREG_DRAFT_C_* for RELAXED survivors; do not open HOLD (the lead does that once, after reviewing the draft). |

All streams: HYPOTHESES_<A|B|C>.md in research/results/portfolio/round24_relaxed/ with `date -u` times before
numbers, STREAM_<A|B|C>.md at the end, PREREG_DRAFT_<stream>_* for LIVE / DEMO / RELAXED survivors (state the tier and
the expected HOLD / TEST t on the check-era size). Scripts and outputs under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r24/<stream>/.
Fetched data under research/data/duka/ (B, A) or the scratchpad (flow tables). Do not edit code under research/, do
not commit. Three streams run at once: at most 2 heavy processes per stream, each < 3 GB RAM; at most 4 parallel
download connections per stream. Streams B and C do not load 2025-26 prices; stream A loads them only for its TEST
era of 2024+ mechanisms.
