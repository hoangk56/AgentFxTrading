# Round 26, stream J: unscheduled jumps on IC ticks. Declared hypotheses

Written 2026-10-17 20:17 UTC (from `date -u`), before any forward return of any jump was computed. Brief:
[BRIEF.md](BRIEF.md) (row J; its "Execution model" is binding) and round 13's brief (eras, costs, bars).

What was looked at before this file (no forward return in any of it): tick density, ms timestamps and median spreads
on 3 days; a detection prototype on 6 instrument-days and event counts per instrument-day for k in {4..16} on 30
random weekdays 2018-24, unmasked (counts only). Those counts set the k grid below: k = 4-5 fires 10-20 times a day
per instrument at W = 60 s (an ordinary active minute, not a jump), k = 16 fires 0.1-0.6 times a day before
exclusions.

## Question and sides (from the literature, fixed now)
A jump of the mid over seconds outside scheduled releases is either:
- unscheduled information (news, a large informed order, a policy headline): prices adjust to a new level and the
  move continues or at least holds. Sources: Lahaye, Laurent & Neely (2011, J. Applied Econometrics) on FX jumps and
  cojumps; Evans (2011, J. Banking & Finance) on intraday jumps and news; Joulin, Lefevre, Grunberg & Bouchaud
  (2008, arXiv 0803.1769) on news jumps, whose volatility persists, versus endogenous jumps, which relax quickly.
  **J1 = continuation: trade in the jump's direction.**
- a liquidity event (a thin book, a stop cascade, an algorithm running through an empty book, a quote glitch): the
  price overshoots and comes back. Sources: Golub, Keane & Poon (2012, arXiv 1211.6667) on mini flash crashes;
  BIS Markets Committee (2017) on the sterling flash event of 7 October 2016; Christensen, Oomen & Renò (2022,
  J. Econometrics, "The drift burst hypothesis": V-shaped drift bursts that revert); Johnson et al. (2013, Sci.
  Reports) on sub-second extreme events; Brogaard et al. (2018, JFE) on liquidity provision during extreme moves.
  **J2 = reversal: trade against the jump.**

Mechanism split, declared before numbers: a jump that several instruments make at once, the same way, is
information (J1's home); a jump one instrument makes alone is a venue or liquidity event (J2's home). Citations are
from memory; no literature fetch is planned for this stream.

## How this differs from the earlier shock tests
| earlier test | what it did | what is new here |
|---|---|---|
| round 3 (flow_search_2026-09-27, "Liquidity provision"): Asian-hours mean reversion; crypto liquidation-cascade fade; volume-conditioned reversal | M5 fades of 2-3 ATR from SMA20 over hours; BTC/ETH \|z\| > 3-5 over 1-6 h held 2-8 h; tick-count-conditioned 1-3 day fades | detection over <= 10 / 30 / 60 s, held 1-15 min, on 10 non-crypto instruments, entry at a fill-level latency at the actual bid/ask |
| round 6 S5: fade 5-minute shocks in the US cash session (Nagel 2012) | 5-min mid bars 09:35-15:50 ET, shock > 2-4 sd of the same clock slot over 20 days, US30/USTEC, entry at the next 5-min bar, releases not removed | second-level jumps against the local 1-minute sd, all sessions, all 10 tick instruments, scheduled releases / central-bank windows / market-structure clocks removed, both sides and a mechanism split |
| round 17 Y: price-only order flow; 1-minute inventory reversal | unconditional regressions of 1-60 min returns on 1-30 min signed quote flow; all minutes | event study of rare jumps (top tail only), conditioned on unscheduled timing and on cross-instrument co-movement |
| round 8 S: shock spillover | a source's 5/15-min shock -> other symbols from the next minute | the jumping instrument itself, at ms latency; co-movement is used as a label of information, not as a lead |

## Data
- IC ticks (`research/ticks.py` decoder), one UTC day at a time with the previous day carried for look-backs, for
  AUDUSD, NZDUSD, XAUUSD, XAGUSD, XPTUSD, US30, USTEC on 2016-01-01..2024-12-31 and XTIUSD, XBRUSD, XNGUSD on
  2018-01-01..2024-12-31 (warm-up from 2015-12-31 / 2017-12-31). **Every requested day is asserted < 2025-01-01;
  HOLD is never loaded.** Ticks before both sides are known are dropped; a side marked unchanged carries its last
  value across midnight.
- Calendar: r25/shared/cal/ff_events_utc.csv (column `utc` = release minute, bar-start label).
- Minute panel 2016-2024 (r25/shared/panel) for the information-only panel co-move label and sanity checks.
- C3 trade list for the daily correlation of any survivor (and of the best cell, information).

## Jump definition (fixed)
- mid m = (bid + ask) / 2; spread s = ask - bid.
- Local sd sigma(t), bp: bipower variation (jump-robust; Barndorff-Nielsen & Shephard 2004, as in Lee & Mykland
  2008) of the 60 one-minute log-mid returns of the complete minutes before the minute containing t:
  sigma^2 = (pi/2) x mean(|r_j| |r_j-1|). Minute prices are the prevailing mid at each minute end (last tick at or
  before it). A return is invalid if its two minute-ends straddle a quote gap >= 10 min. sigma needs >= 45 valid
  products and sigma > 0, else no detection.
- Threshold theta(t), bp = max(k x sigma(t), 2 x median spread of the trailing 60 minutes (each minute's last
  spread)). The floor keeps moves smaller than two normal spreads out (they cannot pay a round trip).
- At each tick i: U_i = m_i - min(prevailing mids over [t_i - W, t_i]), D_i = max(...) - m_i, in bp of m_i. A jump
  fires at the first tick with max(U_i, D_i) >= theta(t_i). Direction d = +1 if U_i >= D_i else -1. Detection time
  t_d = that tick's timestamp (the tick that completes the move).
- Grid: **W in {10, 30, 60} s x k in {6, 10, 16}** = 9 event sets, each detected separately.
- One event per instrument per 15 min per event set (dead time from each allowed detection).

## Exclusions (no detection inside; all DST-aware, NY = America/New_York, London = Europe/London)
- E1 timed calendar: [T - 30 min, T + 31 min) around every High or Medium row with a time whose currency is in the
  instrument's set: AUDUSD {AUD, NZD, CNY, USD, All}; NZDUSD {NZD, AUD, CNY, USD, All}; metals, indices, energies
  {USD, All}.
- E2 central-bank decisions, all instruments, any impact: [T - 30 min, T + 120 min] around USD Federal Funds Rate /
  FOMC Statement; EUR Main Refinancing Rate / Monetary Policy Statement / ECB Press Conference; GBP Official Bank
  Rate / MPC Official Bank Rate Votes / Monetary Policy Summary; AUD Cash Rate / RBA Rate Statement; NZD Official
  Cash Rate / RBNZ Rate Statement; CAD Overnight Rate / BOC Rate Statement; CHF SNB Policy Rate / SNB Monetary Policy
  Assessment. BOJ (unfixed time): 01:30-07:30 UTC on any day with a JPY BOJ Policy Rate / Monetary Policy Statement /
  BOJ Press Conference / BOJ Outlook Report row.
- E3 untimed High / Medium rows of the instrument's currency set: the whole UTC day of `wdate`.
- E4 votes: High rows whose event contains "Election", "Referendum" or "Vote" (not "MPC ... Votes") for USD, EUR,
  GBP, JPY, AUD, NZD, CAD, CHF: the `wdate` UTC day and the next one, all instruments.
- E5 energy reports for XTIUSD, XBRUSD, XNGUSD: "Crude Oil Inventories", "Natural Gas Storage", "API Weekly
  Statistical Bulletin" rows of any impact, +-30 min; and the API slot Tuesdays and Wednesdays 16:00-16:35 NY.
- E6 rollover: 16:35-18:10 NY every day, all instruments (detection stops at 16:35 so that the longest hold, 15 min
  + 60 s, ends before 16:55).
- E7 market-structure clocks: US30, USTEC 09:25-09:45 and 15:55-16:15 NY; XTI, XBR, XNG 14:20-14:40 NY; XAU, XAG,
  XPT 08:15-08:30 NY, 13:25-13:40 NY, 09:40-09:55, 10:25-10:40, 11:55-12:10, 13:55-14:10, 14:55-15:10 London;
  AUDUSD, NZDUSD 15:55-16:10 London.
- E8 reopen: the first 30 min after a quote gap >= 10 min of that instrument.
- E9 known IC artefacts: XTIUSD and XBRUSD 2020-04-15..2020-04-30; energies on Good Friday.
The counts table reports raw detections (same rule, no exclusion, own dead time) and the share each exclusion removes.

## Labels
- Session of t_d: US = [08:00, 16:35) NY; Europe = London >= 07:00 and NY < 08:00; Asia = the rest outside the
  rollover (from 18:10 NY to 07:00 London).
- Class: FX {AUDUSD, NZDUSD}; METALS {XAUUSD, XAGUSD, XPTUSD}; INDICES {US30, USTEC}; ENERGY {XTIUSD, XBRUSD,
  XNGUSD}. LIQUID set (from IC's typical spreads, known costs, not returns) {AUDUSD, NZDUSD, XAUUSD, US30, USTEC}.
- Mechanism (causal: only ticks up to t_d): for each other instrument p with a valid sigma_p and a tick in the last
  10 min, z_p = (m_p(t_d) - m_p(t_d - 60 s)) / m_p(t_d - 60 s) x 1e4 / sigma_p(t_d). Groups: G_USD {AUDUSD, NZDUSD,
  XAUUSD, XAGUSD, XPTUSD}, G_IDX {US30, USTEC}, G_OIL {XTIUSD, XBRUSD}; XNGUSD has no group.
  **CO** = some same-group partner has d x z_p >= 2. **SINGLE** = no other instrument has \|z_p\| >= 2. OTHER = the
  rest (reported, no cell).
- Information-only (not causal, no cell): panel co-move = how many of the panel's EURUSD, GBPUSD, USDJPY, USDCHF,
  USDCAD move >= 2 x their trailing 60-min rms 1-minute sd in the USD direction implied by a G_USD jump, from the close
  of the minute before the detection minute to the close of the minute after it (US500 for G_IDX); spike = the next
  tick takes back >= 50 % of the move; spread state = spread at detection / trailing median.

## Trades (execution model of the brief)
- J1 side = d; J2 side = -d.
- Entry at the first tick with ts >= t_d + L, **L = 250 ms decision latency**; reported also L = 0 (the detection
  tick itself), 1,000 ms and "next tick" (tick i_d + 1); bar check "+1 minute" = L = 60,000 ms. Buy at the ASK, sell
  at the BID of that tick.
- Exit at the first tick with ts >= t_d + L + h (next-tick variant: ts(i_d + 1) + h), h in {1, 5, 15} min; a long
  exits at the BID, a short at the ASK.
- Stop variant: a resting server-side stop at theta from the entry mid (long: sell stop, triggers at the first later
  tick with BID <= m_e (1 - theta/1e4), fills at that tick's BID; short: buy stop, ASK >= m_e (1 + theta/1e4), fills at
  that ASK). A spread spike can trigger it; the share of stop fills where the mid had not reached the level is
  reported.
- Costs: commission 0.6 bp round trip for FX and metals, 0 for indices and energies; spreads are the actual ticks'.
  Net = side x (exit fill - entry fill) / m_e x 1e4 - commission. Mid = side x (exit mid - entry mid) / m_e x 1e4.
  Spread paid = mid - net - commission (reported). Spread x1.5 = net - 0.5 x spread paid.
- No hold reaches the 16:55 NY rollover; no hold reaches a calendar release (detection stops 30 min before it).

## Cells (counted)
For each family J1 and J2:
9 event sets (W x k) x h {1, 5, 15} x stop {none, theta} x mechanism {ALL, CO, SINGLE} x instrument set {LIQUID,
ALL10, FX, METALS, INDICES, ENERGY} x session {ALL, Asia, Europe, US} = 9 x 3 x 2 x 3 x 6 x 4 = **3,888 cells per
family, 7,776 in all**. Every cell is decided at L = 250 ms; L = 0 / 1,000 ms / next tick are execution variants,
not cells.
**Primary cells (the literature's mapping):** J1-CO-LIQUID-ALL sessions and J2-SINGLE-LIQUID-ALL sessions, each 9 x 3
x 2 = 54 cells (108 primary). Everything else is secondary and counts in the chance benchmark.

## Statistics and bars
- Per cell: n events, mid and net bp per event at each latency, t clustered by UTC day, by era (IS 2016-21, energies
  2018-21; VAL 2022-24) and by year, VAL/IS, spread paid, stop-hit share and spread-triggered stop share, per-trade
  and per-day net Sharpe, power = Sharpe x sqrt(1.73 x events (or event days) per year) on the IS and on the VAL
  size.
- Random-time control RT (>= 200 seeds): for each event, 200 times drawn uniformly from the same instrument's allowed
  seconds (all exclusions, valid sigma, a tick in the last 60 s) in the same session of the same UTC day; the side is
  recomputed by the rule at that time (d_r = sign of the prevailing-mid change over the trailing W; a random sign if
  0), stop distance = theta at that time, same L, h and exits. A cell beats seed j if its mean net exceeds the mean
  over its events' j-th draws.
- Direction control RD (>= 200 seeds): the same events with the side drawn at random per event (J1 or J2 outcome).
- Chance benchmark: (i) the 95 % max-\|t\| of K independent normals for K = cells with >= 10 IS events; (ii) a
  permutation null that flips the sign of the jump direction per UTC day (one flip per day shared by all
  instruments and cells; 1,000 draws) for the max IS net t over the counted cells, and for the 108 primary cells.
- Bars, as round 13's brief (not lowered): LIVE: IS day-clustered net t >= 2.5, VAL >= 1.5, net > 0 in IS and VAL,
  >= 2/3 of years net > 0, > 0 at spread x1.5 and at +1 minute (L = 60 s), beats >= 95 % of RT, power >= 3.
  DEMO: IS t >= 2.0, net > 0 in VAL, beats >= 90 % of RT, > 0 at spread x1.5 and +1 minute; no power requirement.
  A cell whose IS t lies within the permutation null's 95 % max is reported as "within chance" in its verdict.
- PRE (Dukascopy M1, minute-level, labelled) only if a family meets a bar on IS/VAL.
- A rule meeting LIVE or DEMO on IS/VAL gets PREREG_DRAFT_J_<name>.md (rule, parameters, cell count, expected HOLD
  events and expected HOLD t on the VAL size and at 0.65 of it, C3 daily correlation) and its family stops there. HOLD
  is not opened.

## Prior
Round 8 found cross-market information priced within a minute and round 17 found 1-minute inventory reversal of
~0.05 bp; IC's cost after a jump is about one widened spread plus 0.6 bp in FX and metals. A 6-16 sigma jump is
5-40 bp in FX and gold, so a 10-20 % continuation or reversal would be 1-5 bp: the question is whether it beats the
spread actually paid. Prior chance of a LIVE pass: low (a few %).

## Additions after numbers
(anything added below this line after a number was seen is information only, unless it says otherwise)

### Addendum 1, 2026-10-17 20:33 UTC: scheduled clock spikes (written after event COUNTS, before any cell return)
What was seen: the full pass of the declared definition (D1, 126,435 events) and a sanity listing. Seen: event counts
by UTC minute and instrument, NaN shares, and the 25 largest single-event \|mid\| moves (glitch screen; XPT
2020-06-24 +668 bp and back, XTI March-May 2020, XNG 2022-06-14). No cell statistic (no mean, t or control over any
cell) has been computed.
Finding (counts only): D1 events pile up at fixed clock minutes that my E7 list missed: 01:00 and 05:30 UTC (09:00
and 13:30 Beijing, the SHFE / INE / SGE day-session open and afternoon reopen: XAGUSD 189x and 86x the average
minute, XTIUSD 102x, XAUUSD 62x), 13:00 UTC (21:00 Beijing night session, energies), the European cash open for US30
/ USTEC (07:00 UTC in summer, 08:00 in winter), 07:00 New Zealand for NZDUSD (19:00 / 18:00 UTC), 15:50 NY for USTEC
(MOC imbalance), 13:24 NY for XAGUSD (silver settlement minute), and 00:00 UTC in NY summer for several symbols. These
are scheduled market-structure events, not unscheduled jumps.
Declared now:
- **E10 count-based clock filter.** Using D1 events of IS (2016-21) only, all 9 sets pooled, per instrument and per
  season (NY daylight time or not): count events per UTC minute of day; flag every minute with a count >= max(15, 8 x
  that instrument-season's mean count per minute). Exclude [flagged minute - 2, flagged minute + 5) on every day of
  that season, IS and VAL, for that instrument. The flags come from counts only (no returns) and from IS only.
- **D2 = D1 + E10** is the primary definition for verdicts; D1 is reported for every cell. The pass is rerun with
  E10 in the exclusion intervals (so the random-time control pools also avoid E10). Chance benchmarks are computed for
  D2's 7,776 cells; D1's cells are reported as the same family (15,552 cells counted in all).
- **Extra requirements (only raise the bar):** a cell passes only if it also (a) keeps its pass with per-event net
  winsorised at the 1st / 99th percentiles of the cell's own IS distribution (same cut applied to VAL), and (b) stays
  net > 0 in IS without March-April 2020 (round 13 pitfall: big-move results must be reported without 3-4/2020).
- XPT, XTI, XBR, XNG glitch-like events stay in (no post-hoc deletion); (a) is the declared protection.

### Addendum 2, 2026-10-17 20:43 UTC: the declared PRE check (after cell results were seen)
Seen by now: all D1 and D2 cells. Three D2 cells meet the DEMO numbers, all one effect: J2 (fade) of k16 jumps
within 10-30 s in METALS with the CO label, 15-min hold, Asia or all sessions. This file declared a PRE check "only if
a family meets a bar on IS/VAL"; it is defined now, after the result, so it is a check, not a discovery.
- Dukascopy has only M1 closes for metals (no ticks, no intrabar range): a 10-30 s window cannot be seen. Proxy P:
  1-minute close-to-close mid return r_m >= 16 x the bipower sigma of the trailing 60 one-minute returns, direction
  d; CO = the other metal (XAUUSD <-> XAGUSD) has d x r_m >= 2 x its own sigma in the same minute; Asia session; the
  exclusions E1-E7, E9, E10 at the minute start; 15-min dead time; fade at the close of minute m, exit at the close
  of m + 15; cost = IC's 2016-17 median spread of that UTC minute of day (panel) + 0.6 bp.
- **Calibration first:** P on IC's M1 panel 2016-24 (IS / VAL). P is a meaningful stand-in only if it reproduces the
  tick result's sign and rough size (J2 mid > 0 in IS and VAL); otherwise the PRE check is reported as not
  meaningful for this rule and not run as evidence.
- PRE window 2008-2015 (Dukascopy silver is unreliable before 2008; the calendar starts 2007). Mid = (bid + ask) / 2
  where both exist, else bid.

### Addendum 3, 2026-10-17 20:58 UTC: information only (added after all results)
- The declared information-only panel label looks up to ~2 minutes ahead. A causal version was added after seeing
  it: the label from the detection minute's own close, with the outcome entered at L 60 s. Information only; no
  cell, no bar.
- The stop's "spread-triggered" flag was redefined: a stop fill is spread-only when the stop side would not have
  crossed the level at the entry spread. The first definition (mid not at the level) flagged nearly every fill. Only
  the reported share changes; no return and no bar is affected (checked: identical events and returns).
