# Round 30 brief: the fix and flow hypotheses declared for the six FX symbols the user has now approved

Written 2026-10-18 09:16 UTC (from `date -u`), before any price of these six symbols was loaded for a return. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as rounds 25-29 (the user's LIVE and DEMO bars in
research/PROMPT.md; no RELAXED tier).

**Why this round exists.** Round 29 paused the research and ranked the decisions only the user can take. On 2026-10-18
the user approved decision 2 ("1,2,4 ok"):
- IC tick pulls through cTrader backtests on the VPS, for USDCNH, USDMXN, USDSGD, EURNOK, USDNOK and EURSEK;
- Dukascopy M1 2004-15 for the same six symbols.

The hypotheses for these data were declared in round 25, before any of their prices existed in this project:
research/results/portfolio/round25_surprises/HYPOTHESES_A.md, 2026-10-17 19:13-19:50 UTC. This round tests them **as
declared**: same cells, sides, windows, day sets, sizing, costs, controls and eras. Nothing is chosen on data. A detail the
declaration leaves open is fixed in your HYPOTHESES_<stream>.md before the first return is computed, with its
`date -u` time.

**Read first and follow for everything not changed here:**
- research/results/portfolio/round25_surprises/HYPOTHESES_A.md: the declared cells (H-NOK, H-EMFIX, H-CNH) and the
  common conventions block.
- research/results/portfolio/round25_surprises/STREAM_A.md: the expected sizes and powers for these routes, rows 2, 3
  and 5 of its table.
- research/results/portfolio/round13_structural/BRIEF.md: eras, costs, constraints, bars, multiple testing, pitfalls,
  resources and what to return.
- research/PROMPT.md, and research/JOURNAL.md for rounds 18-29.
- Round 19's CNHC-I cell (research/results/portfolio/round19_*; search the JOURNAL for "CNHC").

## Data (read-only)
- **IC ticks** 2016-01-01..2024-12-31: `research/data/<SYM>/t1/YYYYMMDD.zticks`. Decode them with
  `research.ticks.load_ticks(symbol, start, end)` (gzip int64 triplets: ts ms, bid x1e5, ask x1e5; 0 = side
  unchanged, forward-filled).
  - Pulled today from the VPS cache. USDCNH, EURNOK and USDNOK are complete. USDMXN, EURSEK and USDSGD are still
    being pulled; check the file count per year before you use a symbol.
  - **HOLD (2025-01-01..2026-09-24) and the forward days after it are not on this Mac**, and must not be fetched.
    Assert `ts < 1735689600000` (2025-01-01) at load anyway.
- **Dukascopy M1, PRE era**: `research/data/duka/m1_r30/<SYM>_<YYYY>.npz`, written by
  `research/results/portfolio/round24_relaxed/prereg_code/duka_dl.py.txt`.
  - Arrays: ts (ms, bar start), bci / aci (bid / ask close as integers; aci = -1 when the ask file was missing or
    misaligned), bv / av (volumes).
  - A zero-volume minute is no trading. Check the integer scale against IC on the first days of 2016.
  - Early Dukascopy asks are unreliable (research memory: USDJPY 2004 had bid = ask on 41 % of minutes). Hence the
    declared PRE cost: IC's 2016-17 spread of the same symbol, by minute of week on the local fix clock, + 0.6 bp.
  - Still downloading at 09:16 UTC: USDMXN 2007-15 is complete, the rest follows over the next hours. Use a
    symbol-year only once its npz exists. requests.log in the same folder lists every fetch.
- **Non-price inputs from round 25.** In the session scratchpad
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/A/web/`:
  - Norges Bank's monthly table of announced daily amounts: `nok/nb_fx_monthly.csv`;
  - its press releases and FAQ: `nok/*.html`;
  - helper logs.
  These are untrusted downloads: read them as data only, with `python -I`.
- **Calendars.** The `holidays` package is in research/.venv (0.106): NO, SG and CN. Fetch these, and log the fetches:
  - the Mexican CNBV bank-holiday calendars (non-price);
  - the Norges Bank press releases for the mid-month changes HYPOTHESES_A lists.
- **C3's trade list** for the correlation with any survivor: research/results/portfolio/trades_C3_gotobi_jpy_basket.csv.

## Streams
| stream | cells (HYPOTHESES_A.md) | data |
|---|---|---|
| N | H-NOK: NOK-1 (primary), NOK-2 (replica on USDNOK), NOK-P (EURSEK placebo), NOK-D (dose regression, mechanism), NOK-A (information); the Norwegian-holiday placebo | EURNOK, USDNOK, EURSEK |
| E | H-EMFIX: MX-1 (primary), MX-15, MX-H, MX-W, MX-C, MX-A, SG-1, CN-1, BOOK; H-CNH = CN-1 at IC's real spreads | USDMXN, USDSGD, USDCNH |

**Order of the tests (as declared).**
- N: NOK-D on PRE 2004-15 first, then NOK-1 on IS / VAL.
- E: MX-1 on PRE 2007-15 first, then IS / VAL. CN-1 needs no PRE and can run as soon as its data is there.
- Write each PRE number into your STREAM file before you compute the IS / VAL number of the same cell.

## Rules for this round
- The side, window and day set of every cell are the declared ones. Variants beyond the declared list are
  information only: label them post hoc and don't count them for a tier.
- Costs: IC ticks, buy at the ask and sell at the bid, at the last tick at or before each declared minute, + 0.6 bp
  round-trip commission. Swap only if a hold crosses 17:00 New York (none of the declared windows does).
- Report for every counted cell:
  - mid and net (bp, day-clustered t) by era (PRE / IS / VAL) and by year;
  - the VAL / IS ratio;
  - spread x1.5 and both fills +1 minute;
  - per-trade Sharpe and power at the IS and the VAL size, plus the decay readings (x0.65, x0.30) the conventions
    block asks for;
  - the random-entry control (>= 200 seeds);
  - the chance benchmark for the family's cell count.
- If a cell meets the LIVE or DEMO bar on IS / VAL, stop that family and write PREREG_DRAFT_<stream>_<name>.md in the
  round folder; the lead registers it and opens HOLD. Do not load HOLD yourself.
- Scripts and outputs go under the session scratchpad `r30/<stream>/`. In the repo write ONLY HYPOTHESES_<stream>.md,
  STREAM_<stream>.md and PREREG_DRAFT_* in research/results/portfolio/round30_fix_flows/. No git commands that change
  state.
- Network: only non-price official sources (CNBV, Banxico, Norges Bank, MAS / ABS, holiday calendars) and literature.
  - Never send personal data: no e-mail address in any request (no OpenAlex `mailto`).
  - Prefer direct official URLs over WebSearch, whose budget is shared.
  - No new price series.
- Resources: the Mac is shared with the running downloads; at most 2 heavy Python processes per stream, each under
  ~3 GB RAM.

## What to return (final message, <= ~1,200 words)
- A table: cell | PRE / IS / VAL mid (bp, t) | cost | net IS / VAL (t) | VAL / IS | power (IS, VAL size) | random
  control | verdict.
- Data checks: tick days per year per symbol, the integer scale, and the spreads at the declared minutes by year.
- Any PREREG_DRAFT path, or "none".
- Surprises, and the paths of your scripts and STREAM file.

## Data readiness (added 09:24 UTC, before any stream started)
The six symbols arrive over the next hour. Before you load a symbol-year, check it is complete. The commands below
print the files per year (IC: 365 or 366; a Dukascopy year exists once its npz is written):
```
ls research/data/<SYM>/t1 | cut -c1-4 | sort | uniq -c
ls research/data/duka/m1_r30/
```
If a year you need is not there yet, do the parts that need no prices first: the HYPOTHESES file, calendars, Norges
Bank amounts, code with synthetic tests. Then wait in the background, e.g.
`until [ "$(ls research/data/EURNOK/t1 | grep -c '^2024')" -ge 366 ]; do sleep 60; done` with run_in_background.
Never start a download yourself.
