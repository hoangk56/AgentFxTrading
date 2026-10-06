# Stream F hypotheses (round 11): multi-day drift after monetary-policy and macro surprises (1-5 days)

Written 2026-10-06 00:30 UTC, before any stream-F return or event-window number was computed. Before this file only
the brief (with its round-11 addendum), the round-10 report, STREAM_B.md, STREAM_E.md, the journal, the panel's meta /
spread table, the calendars' formats (cb_calendar.json, releases.json; no prices) and literature abstracts (OpenAlex,
Semantic Scholar) were read. The US CPI and pre-2016 NFP release dates were read from the BLS archive pages (file
names cpi_MMDDYYYY / empsit_MMDDYYYY), without prices. Additions after seeing data will be marked **post hoc** with
their time. HOLD (2025+) is not loaded anywhere: the panel ends 2024-12-31, Dukascopy files end 2015-12-31.

## What round 10 already covered (not redone)
B2: follow the first 15 min after a decision, exit 20:50 UTC the same day (net +0.4 / +0.0 bp). E2: follow the first
5 min after a non-US release for 30-240 min. Both intraday. This stream starts where they stopped: entry at the first
20:50 UTC at least 90 minutes after the event, so the intraday reaction and the B2 window are excluded, and the hold
is 1-5 days.

## Why the family could escape the standing limits
- Size vs cost: a 1-5 day hold has an sd of 40-110 bp in FX; a drift of even 10-15 % of a 30-80 bp decision reaction
  is 5-10 bp, against ~1 bp spread+commission plus 0-3 bp of swap. Cost is not binding (unlike rounds 3-10's flows).
- Not the intraday result: information priced "within minutes" (rounds 3, 8, 10) is about the jump; the delayed
  overshooting literature and Neuhierl & Weber's monetary momentum are about days-to-weeks continuation from slow
  portfolio rebalancing / order flow (Evans & Lyons 2005: news-induced end-user trades "remain significant for days"
  and have persistent price effects).
- Count: 8 banks give ~62-66 scheduled decisions a year (~75 FX legs); ~130 non-US releases + 24 US (NFP, CPI).
- Second out-of-sample era: PRE 2004-15 with the 2004-15 events already in cb_calendar.json and BLS dates.

Honest prior: the FX literature for the post-Volcker era (Kim, Moon & Velasco 2017, "Delayed overshooting: is it an
'80s puzzle?", JPE Macro; Inoue & Rossi 2019, JIE; Faust, Rogers, Swanson & Wright 2003, JME) finds Dornbusch-style
immediate overshooting, i.e. no continuation after the impact. Delayed overshooting (Eichenbaum & Evans 1995; Scholl &
Uhlig 2008) is mostly a monthly-VAR, 1980s finding. So F1's expected effect is ~0 (or a small reversal); it is tested
because the brief asks and because days-horizon continuation has not been measured in this repo. Neuhierl & Weber
(2018, NBER w24748, "Monetary Momentum") report a stock-return drift in the direction of the FOMC surprise that
"continues to increase to more than 4.5 % 15 days after the meeting" (cumulative expansionary minus contractionary
difference), and say it holds in many international equity markets: that gives F2 a side.

Power arithmetic (before computing): LIVE needs per-trade net Sharpe >= 3 / sqrt(n/yr x 1.73). F1 ~75 legs/yr ->
0.26; F3 ~150 legs/yr -> 0.19. A 5-day FX hold with sd ~70 bp would need a drift of ~18 bp (F1) / ~13 bp (F3) net per
leg. DEMO needs IS t >= 2: F1 ~450 IS legs on ~370 dates -> Sharpe >= ~0.10 (~7 bp at 5 days).

## Common conventions (all families)
- Prices: shared panel mid; at a window start / entry / exit the last quote at or before the minute with age <= 60
  min (else the leg is dropped and counted). ln returns in bp.
- Event time T: cb_calendar.json `utc` for scheduled decisions (unscheduled excluded). BoJ without a published time:
  the surprise window is 02:00 -> 06:30 UTC (statement window, before the 15:30 JST presser); with a time (2006-15
  partly) the normal rule. Releases: releases.json local time -> UTC; US CPI and NFP at 08:30 New York.
- Entry E: the first 20:50 UTC (on a weekday) that is >= T + 90 min. Exit: 20:50 UTC on the h-th weekday after the
  entry day, h in {1, 3, 5}, capped so that exit - entry <= 5 x 24 h (if the h-th weekday is later, exit at the last
  weekday 20:50 within 5 days). Signal known at E-1 min, fill at E (the 20:50 bar close).
- Cost per leg: half the actual panel spread at the entry minute + half at the exit minute, + 0.6 bp for FX; swap:
  `swap_frac_at(sym, side, entry_ms)` x `research.specs.rollovers(entry, exit, triple weekday from SWAPS, default
  Wednesday)`; indices use the same function (IDX_CCY rates). Variants: spread x1.5; latency = entry AND exit 60 min
  later (21:50 UTC); +1 minute (20:51).
- PRE 2004-15: Dukascopy bid close. M1 for EURUSD, USDJPY, USDCHF; H1 for GBPUSD, AUDUSD, NZDUSD, USDCAD (surprise
  from the close of the last H1 bar ending <= T to the close of the first H1 bar ending >= T+30; entry / exit at the
  close of the H1 bar ending 21:00 UTC). Spread = IC 2016-17 median spread of that symbol at that minute of day (from
  the panel), + 0.6 bp. Swap in PRE: markup only (mean of IC's long and short markups per rollover from rates.markups),
  because the FRED series in research/data/rates start in 2014.
- Statistics: mean per leg; t clustered by event date (legs of one date summed); robustness: t clustered by ISO week
  of the entry (holds of different banks overlap within a week) and winsorised 1/99 %. Years positive. Per-trade
  Sharpe and power = Sharpe x sqrt(n/yr x 1.73); day-clustered power on date sums.
- Positions: one bot per bank (F1/F2) or per pair (F3). Banks meet >= 3 weeks apart, so a bank bot holds <= 3 legs
  (FOMC bot: EURUSD + USDJPY [+ US500 in F2]). F3: a pair bot skips a new signal if 3 positions of that bot are open.
  The max number of concurrent positions over all bots is reported.
- Random-entry control (300 seeds): for each event, a random weekday with the same weekday, within +-8 weeks, not an
  event day of that bank / release type, same UTC clock time T; the surprise and side are recomputed on that day with
  the same rule (round-10 pitfall), same entry/exit rule and h. Reported: share of seeds whose mean net < candidate's.
- Chance: per family, one sign flip per event date shared by all cells of the family, 1000 draws, 95th percentile of
  the max |t| (IS); and the expected max of K |normals|.
- Survivors only: C3 daily and monthly P&L correlation on IS+VAL (research/results/portfolio/trades_C3_gotobi_jpy_basket.csv).

## F1 Post-decision currency drift (delayed overshooting), 8 central banks
- Mechanism / source: Eichenbaum & Evans (1995); Scholl & Uhlig (2008): the currency of a surprise tightener keeps
  appreciating after the impact (delayed overshooting). Counter-prior: Kim, Moon & Velasco (2017), Inoue & Rossi (2019).
- Legs (home currency vs USD): FOMC -> EURUSD, USDJPY (USD side); ECB -> EURUSD; BoE -> GBPUSD; BoJ -> USDJPY;
  RBA -> AUDUSD; BoC -> USDCAD; RBNZ -> NZDUSD; SNB -> USDCHF.
- Surprise s (home currency up > 0), two definitions fixed now:
  S30 = home-currency return from the last quote at/before T to the close of the bar ending T+30 (BoJ no-time: 02:00
  -> 06:30 UTC). FOMC: USD return = mean of (-r EURUSD, +r USDJPY).
  SDAY = home-currency return from the same start to the entry signal minute (E-1): the whole decision-day reaction.
- Side: continuation, long the home currency if s > 0 (short if s < 0; s = 0 skipped).
- Subsets: ALL; LARGE = |S30| >= 1.5 x the median |S30| of the same bank's previous 8 scheduled decisions (needs >= 4
  previous in-panel decisions; PRE uses PRE history).
- Cells: {S30, SDAY} x h {1, 3, 5} x {ALL, LARGE} = 12. **Primary: S30, ALL, h 5.**
- PRE check, written now: for any F1 cell that meets DEMO/LIVE on IS/VAL, the same cell on PRE (FOMC, ECB, SNB, BoJ on
  M1; BoE, RBA, BoC, RBNZ on H1) must have net mean > 0 with event-date t >= 1.0. Otherwise it is rejected.

## F2 Post-decision equity drift (monetary momentum), home index
- Mechanism / source: Neuhierl & Weber (2018): stocks drift in the direction of the policy surprise for >= 15 days
  after the FOMC; expansionary (dovish) -> up, contractionary (hawkish) -> down; "many international equity markets".
- Legs: FOMC -> US500; ECB -> DE40; BoE -> UK100; BoJ -> JP225; RBA -> AUS200 (BoC, RBNZ, SNB have no index here).
- Surprise: the same s (S30, SDAY) of the home currency; hawkish = home currency up.
- Side: short the index if s > 0, long if s < 0. The literature is about the Fed; the other banks are an
  extrapolation, so the FOMC-only split is also reported (descriptive, not a cell).
- Cells: {S30, SDAY} x h {1, 3, 5} x {ALL, LARGE} = 12. **Primary: S30, ALL, h 5.** No PRE (no index data before 2016).

## F3 Post-release drift after macro data, 1-5 days
- Mechanism / source: Evans & Lyons (2005, JIMF): macro news induces end-user order flow that "remain[s] significant
  for days" with persistent price effects; currency markets do not absorb news instantaneously.
- Events: releases.json's 15 non-US types (2016-24, home pair from its `pair` field) + US NFP and US CPI (BLS archive
  dates 2004-24, 08:30 New York; legs EURUSD and USDJPY, USD side as in F1). One leg per pair per release minute
  (same-minute releases on the same pair merged). The Oct-2023 UK extra release is not used.
- Surprise r0 = home-currency return from the last quote at/before T to the close of the bar ending T+5 (E2's
  definition). LARGE = |r0| >= RMS of the previous 12 r0 of that type (E2's definition).
- Side: continuation (long the home currency if r0 > 0).
- Cells: h {1, 3, 5} x {ALL, LARGE} = 6, pooled over all types. **Primary: ALL, h 5.** Per-type and US-only splits
  descriptive.
- PRE check, written now: US NFP + CPI on EURUSD/USDJPY M1 2004-15 for any surviving cell: net > 0, t >= 1.0.

## F4 FOMC-cycle even weeks (Cieslak, Morse & Vissing-Jorgensen 2019, JF "Stock returns over the FOMC cycle")
- Mechanism / source: the US equity premium is earned in even weeks of the FOMC cycle (weeks 0, 2, 4, 6 counted from
  FOMC day 0), linked to Fed information flows (board meetings, policy news). Side: long. The pre-FOMC day (week 0's
  days -1, 0) was round 3's announcement premium and is excluded here.
- Rule: long US500, US trading days (NYSE calendar) relative to scheduled FOMC day 0; entry 20:50 UTC on the trading
  day before the window, exit 20:50 UTC on its last day; windows: W0post = days 1-3 (entry day 0); W2 = days 10-14
  (entry day 9); W4 = days 20-24 (entry day 19); W6 = days 30-34 (entry day 29, only if the next FOMC day is > day 34).
  Holds capped at 5 x 24 h as above (a window spanning a weekend is cut at the last weekday within 5 days).
- Cells: W0post, W2, W4, W6, pooled even weeks (W2+W4+W6) = 5 on US500 (US30 as a robustness line, not a cell).
- Control: random 5-day-or-shorter long windows (same length) at random cycle positions, 300 seeds: beats the plain
  equity drift? No PRE (no index data before 2016).

## Verdict rules (from the brief)
LIVE: IS event-date t >= 2.5, VAL >= 1.5, >= 2/3 years net > 0, beats >= 95 % of random entries, power >= 3, > 0 at
spread x1.5 and latency. DEMO: IS t >= 2.0, VAL net > 0, beats >= 90 %, > 0 at x1.5 and latency. A family that meets
either on its primary or any cell (counted against chance) gets a PRE check (where written) and, if it passes, a
PREREG_DRAFT_F_<name>.md; then the family stops.
