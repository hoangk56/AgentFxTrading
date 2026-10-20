# Round 26 brief: information events at the tick level (stop entries at scheduled releases, unscheduled jumps)

Written 2026-10-17 20:04 UTC (from `date -u`), before any round-26 number was computed. Repo:
/Users/hoangbk/00.code_base/105.AgentFxTrading. Same task as round 25 ("research kỹ đến khi nào có thuật toán chạy live
được thì thôi"), the user's original LIVE and DEMO bars (research/PROMPT.md), no RELAXED tier.

**Read first and follow for everything not changed here**: research/results/portfolio/round13_structural/BRIEF.md
(eras, costs, constraints, bars, multiple testing, pitfalls, resources, what to return), research/PROMPT.md (exhausted
families), research/JOURNAL.md (rounds 18-25 at the top), research/results/portfolio/round25_surprises_2026-10-17.md
and round25_surprises/STREAM_B.md (the timed release calendar, the release-minute move B0, the spread map before
releases).

## Why this round looks where it does
- Round 25 B: released numbers move prices hard in the release minute (realised-surprise-oriented 1-minute moves of
  5-40 bp, t 4-9: NFP +12.6, core CPI +10.3, CAD jobs +18.0 bp), but the part of the surprise predictable from public
  data is priced before the release. Every release rule tested so far had to know the side before the release
  (rounds 3, 10, 11, 25) or entered after 5 minutes (round 3: no follow-through). **No round has tested an entry that
  takes its side from the market's own first move inside the release minute**, i.e. resting stop orders on both
  sides (a news straddle). It needs no forecast: it pays if the price keeps moving after the stop triggers, and it
  dies on slippage and spread spikes. Only tick data at fill-level detail can tell which.
- The opposite execution, resting limit orders that catch the overshoot of the first seconds, is the other declared
  side. Round 12 found passive limits adversely selected on ordinary days; at releases the overshoot literature
  predicts the reverse, so it is tested as its own family.
- Outside scheduled releases, large jumps over seconds are either unscheduled news (continue) or liquidity events and
  flash moves (revert). Earlier rounds faded 5-minute shocks in the US cash session (round 6 S5), crypto cascades over
  hours (round 3) and 1-minute inventory moves (round 17), all at minute resolution. Second-level detection on ticks,
  outside the timed release calendar, with an explicit fill latency, is new.

## Data (read-only; HOLD is never loaded)
- **IC ticks** (ms, bid/ask): research/ticks.py `load_ticks(symbol, start_date, end_date)` for AUDUSD, NZDUSD, XAUUSD,
  XAGUSD, XPTUSD, US30, USTEC (2015-12-29..), XTIUSD, XBRUSD, XNGUSD (2017-12-29..). **Only request days <
  2025-01-01.** No EURUSD / USDJPY / GBPUSD / USDCAD ticks exist locally (their M1 is in the panel; pulling their
  ticks from the VPS is a user decision: say if a family needs them).
- Minute panel 2016-2024 (26 symbols, mid / spr / n, minute label = bar START):
  /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r25/shared/panel/
- **Timed release calendar** (round 25 B): .../scratchpad/r25/shared/cal/ff_events_utc.csv and its README
  (ForexFactory 2007-2024, 2025 rows cut; column `utc` = release minute = bar label T; impact High / Medium / Low;
  `cur`, `event`, `good` = side of "good for the currency"). Use High (and declared Medium) rows with a time;
  US-energy reports (EIA crude Wednesdays, natural gas Thursdays, 10:30 ET) are in it as USD rows. Check its README
  for the time-source column before trusting a row.
- PRE 2004-15: Dukascopy M1 only (no ticks; fetching Dukascopy ticks is a user decision). A minute-level PRE check
  is allowed where it is meaningful, labelled as such.
- C3 trade list for the correlation: research/results/portfolio/trades_C3_gotobi_jpy_basket.csv (IS + VAL only).

## Execution model (fixed now; report every variant)
- Fills from ticks: a buy fills at the ASK of the first tick with timestamp >= trigger time + L, a sell at the BID;
  latency L in {0, 250, 1000} ms, reported for all; also "one tick later". Commission 0.6 bp round trip for FX and
  metals, 0 for indices and energy. Stop orders rest at the broker (cTrader server-side): a buy stop triggers when
  the ASK reaches the level, a sell stop when the BID does; a buy limit fills only when the ASK trades at or below the
  limit, a sell limit when the BID trades at or above it (a touch by the other side is not a fill).
- **A spread spike alone can trigger a stop.** Model it as it happens in the ticks (the ask jumps up on a widening:
  a buy stop triggers even if the mid does not move) and report how often it happens.
- Positions placed or exited at or near the 17:00 New York rollover hour pay that hour's spreads; avoid it or report it.
- The usual random controls do not apply directly to an entry that takes its side from the market: use (a) the same
  orders placed at the same clock time on non-release days of the same weekday (placebo days), and (b) random times
  within the same session, both with the same parameters; report both.

## Streams
| stream | direction | why it might escape the limits |
|---|---|---|
| S | **Scheduled releases on ticks.** Declared families: (S1) OCO stop straddle: at T-2 min (round 25: the spread doubles in the last minute) rest a buy stop at ask + k and a sell stop at bid - k, k fixed in advance as a multiple of the event type's IS median absolute 1-minute release move or as fixed bp (declare the grid and count it), cancel both at T+2 min if none fills, cancel the other leg on a fill; exit at T+h (h = 1, 3, 5, 15 min, declared) or by a declared protective stop; sides come from the trigger. (S2) overshoot fade: resting limits at the opposite levels (buy limit at bid - k2, sell limit at ask + k2) placed at T-2 min, exit at T+h; and a market-order fade at T+1 min after a first-minute move > declared multiple of its norm. Events: High-impact rows in the timed calendar with an IS release-minute activity spike (round 25 B0's 56 types), instruments with ticks (USD releases: AUDUSD, NZDUSD, XAUUSD, US30, USTEC as declared sets; AUD / NZD releases: AUDUSD / NZDUSD; EIA crude: XTIUSD / XBRUSD; gas storage: XNGUSD). Pool by declared sets, t clustered by event day | the release minute is the largest predictable-time move in the data; a straddle takes its side from the first seconds, so the pricing-before-release result of round 25 does not apply; the question is only whether the move after a stop fill beats IC's release-minute spreads and slippage |
| J | **Unscheduled jumps on ticks.** Declared: a jump = the mid moves >= k_j x its local 1-minute sd (causal, e.g. trailing 60-minute) within <= 10 / 30 / 60 s (declared), with no High / Medium calendar row for the currency (or USD) within +-30 min and outside the 16:55-18:10 New York rollover window; sides declared from the literature: (J1) continuation for h = 1, 5, 15 min (unscheduled news), (J2) reversal (liquidity / flash events: Golub, Keane & Poon 2012; BIS 2017 on the sterling flash event), entering at the first tick >= detection + L. Split by session (Asia / Europe / US), by instrument class, by whether the jump co-moves across instruments (a common USD move vs one symbol alone: declared as the mechanism split, information first). Say exactly how this differs from round 3 (crypto cascades over hours), round 6 S5 (5-min shocks in the US cash session) and round 17 (1-min inventory reversal) | second-level detection with explicit latency has never been run; a co-move split separates information (several symbols move) from a single venue's liquidity hole (one symbol moves), which earlier minute-level tests could not |

Both streams: HYPOTHESES_<S|J>.md in research/results/portfolio/round26_tick_events/ with `date -u` times before
numbers (every cell in full: instrument set, levels, latency, exit, day set, cost model, eras, count); STREAM_<S|J>.md
at the end (results table with IS / VAL mid and net per latency, VAL/IS, per-event and per-day power on the IS and
VAL size, placebo-day and random-time controls, chance benchmark for the number of cells, by year; "needs the user"
and "untested ideas" sections; script paths); PREREG_DRAFT_<stream>_* only if a declared rule meets LIVE or DEMO on
IS/VAL (exact rule, parameters, expected HOLD events and expected HOLD t on the VAL size and at 0.65 of it). Do NOT
open HOLD. Report each survivor's daily-return correlation with C3.

Rules: scripts and outputs only under
/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r26/<stream>/.
In the repo write ONLY your HYPOTHESES / STREAM / PREREG_DRAFT files in research/results/portfolio/round26_tick_events/.
Run Python from the repo root (`cd /Users/hoangbk/00.code_base/105.AgentFxTrading && PYTHONPATH=.
research/.venv/bin/python <script>`, numpy only). Two streams run at once: at most 2 heavy processes per stream, each
under ~3 GB RAM; load ticks a month or a day at a time. No price fetches, no git commands that change state, no edits to
research/ code. **Never put the user's e-mail address (or any personal data) in any web request**, e.g. as an API
"mailto" / contact parameter. Files named REPORT.md or FINDINGS.md may be blocked.
