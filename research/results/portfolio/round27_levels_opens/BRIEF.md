# Round 27 brief: gold's round-number cascade with resting stops, and the direction of venue-open jumps

Written 2026-10-17 21:04 UTC (from `date -u`), before any round-27 number was computed. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same task and bars as rounds 25-26 (the user's original LIVE and DEMO
bars, research/PROMPT.md; no RELAXED tier).

**Read first and follow for everything not changed here**: research/results/portfolio/round13_structural/BRIEF.md
(eras, costs, constraints, bars, multiple testing, pitfalls, resources, what to return), research/PROMPT.md (exhausted
families), research/JOURNAL.md (rounds 18-26 at the top), research/results/portfolio/round26_tick_events/BRIEF.md (the
binding tick fill model: latency 0 / 250 / 1000 ms and "one tick later", buy at the ASK / sell at the BID of the first
tick at or after trigger + L, server-side stops trigger on the ASK (buy) / BID (sell), limits fill only when traded
through, 0.6 bp commission for FX and metals) and round26_tick_events/STREAM_S.md + STREAM_J.md (fill facts at IC,
the fixed clock minutes with jumps).

## Why this round looks where it does
- Round 25 C found the only durable new effect of rounds 25-26: **gold continues after it breaks a fresh $10 level**
  (Osler 2003 / 2005 stop-loss cascades; Lucey & O'Connor 2016: barriers in gold, none in silver). At mid it is
  positive in all 12 PRE years (2004-15, declared before it was computed), +3.50 bp (t 4.86) PRE, +2.77 (3.31) IS,
  +2.06 (2.39) VAL, and the $5 half-level placebo is flat. It nets only +1.0-1.9 bp because the M1 rule entered at the
  close of the bar after the break and held 60 minutes. A cascade is triggered stop orders, so most of it may happen
  in the seconds right after the level breaks, which an M1 entry misses. **A resting stop just beyond the level enters
  inside the cascade.** That is a different execution of a PRE-confirmed literature mechanism, tested on ticks with the
  fill model of round 26. Power needed: at ~150-600 events a year and a ~30 bp per-event sd, a net of ~+3-5 bp per
  event would reach LIVE power; the M1 rule's +1 bp does not.
- Round 26 J's clock filter found 13-30 % of large jumps on fixed venue clocks the release calendar misses (Shanghai
  day open 01:00 UTC and afternoon reopen 05:30 UTC, the 21:00 Beijing night session, the CNY fix, European cash
  opens, 07:00 New Zealand, the 15:50 NY imbalance, settlement minutes). Their returns were never computed. Earlier
  rounds tested these venues with sides fixed in advance (rounds 10, 15, 24 B); **taking the side from the opening
  move** (follow it: the new venue's participants carry information; fade it: an opening liquidity gap) is untested.

## Data (read-only; HOLD is never loaded)
- IC ticks: research/ticks.py `load_ticks(symbol, start, end)` for XAUUSD, XAGUSD, XPTUSD, AUDUSD, NZDUSD, US30, USTEC
  (2015-12-29..), XTIUSD, XBRUSD, XNGUSD (2017-12-29..). **Only request days < 2025-01-01.**
- Minute panel 2016-2024 (bar-START labels) at
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/shared/panel/
  and the timed release calendar .../scratchpad/r25/shared/cal/ff_events_utc.csv (+ README).
- PRE 2004-15: Dukascopy M1 only (research/data/duka/m1c/XAUUSD.npz, XAGUSD.npz: keys ts, bid, ask; metals 2004-09
  bid only; research/data/duka/m1 for EURUSD, USDJPY, USDCHF, EURJPY, GBPJPY). A PRE check is minute-level and must be
  labelled so; no Dukascopy ticks exist locally (fetching them is a user decision).
- Round 25 C's gold code and outputs: .../scratchpad/r25/C/ (scripts/, out/), rule text in
  research/results/portfolio/round25_surprises/STREAM_C.md.
- C3 trade list for correlations: research/results/portfolio/trades_C3_gotobi_jpy_basket.csv (IS + VAL rows only).

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| G | **Gold's round-number cascade on ticks.** Declared before numbers: (G1) resting buy stop at L + o and sell stop at L - o around fresh $10 levels L (not crossed in the previous 1,440 minutes, as in round 25 C), o from a small declared grid (e.g. 0, 0.5, 1 typical spread, or fixed cents), armed whenever the price is within a declared distance of L; exits at 5, 15, 30, 60 min (declared) and a declared protective stop variant; one open position at a time; latency 0 / 250 / 1000 ms and one tick later. (G2) the opposite side from Osler's take-profit clustering: a resting limit that fades the first touch of a fresh level (sell limit just below L from below, buy limit just above L from above), declared exits. Dose (declared): $10 vs $50 / $100 levels (larger order clusters), first touch vs repeat. Placebos (declared): the same orders at $5 half-levels and at levels shifted by a random offset (>= 200 draws, the same count). Sessions: full day primary (excluding 16:55-18:10 New York and the timed calendar's High-impact USD minutes +-15), COMEX hours as a declared sub-cell (round 25 C found it after looking: information only). Silver ($0.50 / $1) and platinum ($10) as declared secondary / placebo instruments. PRE: a minute-level replica on Dukascopy 2004-15, labelled | enters inside the cascade instead of a minute after it; the mechanism is published, PRE-confirmed and placebo-checked; HOLD is still clean for this family |
| V | **The direction of venue-open jumps.** Declared clocks (from round 26 J's list, sourced from exchange / fixing schedules, DST-aware): SHFE / SGE day open 09:00 Beijing (01:00 UTC), afternoon reopen 13:30 Beijing, night session 21:00 Beijing (metals; AUD as the China-linked currency), the CNY central-parity release 09:15 Beijing (AUDUSD, NZDUSD, gold), European cash opens 08:00 / 09:00 local (DE40 is not in the tick set: US30 / USTEC / gold only as cross-checks), 07:00 New Zealand (NZDUSD), the 15:50 New York imbalance and settlement minutes (US indices, metals, oil). An event = the opening move from T-1 to T+w (w declared, e.g. 15 / 60 s) exceeding a declared multiple of its trailing same-clock norm. (V1) follow it, (V2) fade it, entering at T+w+L, exits 5 / 15 / 60 min (declared). Controls: the same rule at the same clock on the venue's holidays (venue shut: Chinese holidays for SHFE / SGE / CFETS, UK / German holidays for the European opens, NZ holidays) and at shifted clocks (+-30 min). Say exactly how it differs from rounds 10 A, 15 and 24 B (fixed sides) | the side comes from the market's own opening move, which earlier rounds never conditioned on; a holiday placebo separates venue flow from clock noise |

Both streams: HYPOTHESES_<G|V>.md in research/results/portfolio/round27_levels_opens/ with `date -u` times before
numbers (every cell in full; count cells); STREAM_<G|V>.md at the end (results by era and year, per latency; VAL/IS;
per-event and per-day power on the IS and VAL size; placebos and random controls; chance benchmark for the number of
cells; C3 daily correlation for survivors; "needs the user" and "untested ideas" sections; script paths);
PREREG_DRAFT_<stream>_* only if a declared rule meets LIVE or DEMO on IS/VAL (exact rule, parameters, expected HOLD
events and expected HOLD t on the VAL size and at 0.65 of it). Do NOT open HOLD.

Rules: scripts and outputs only under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r27/<stream>/.
In the repo write ONLY your HYPOTHESES / STREAM / PREREG_DRAFT files in research/results/portfolio/round27_levels_opens/.
Run Python from the repo root (`cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=.
research/.venv/bin/python <script>`, numpy only). Two streams at once: at most 2 heavy processes per stream, each
under ~3 GB RAM; load ticks a day or a month at a time. No price fetches, no git commands that change state, no edits
to research/ code. Never put the user's e-mail address or any personal data into a web request. Files named REPORT.md
or FINDINGS.md may be blocked.
