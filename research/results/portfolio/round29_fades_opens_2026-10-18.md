# Round 29: fading round levels on index CFDs no round had used, and the Asian venue opens

2026-10-18 (UTC). Same task and bars as rounds 25-28. [round29_fades_opens/BRIEF.md](round29_fades_opens/BRIEF.md)
was written at 00:42 UTC, before any round-29 return. HOLD was never loaded. **This is the last round of this
session: the user asked to stop after round 29.** The research pauses here; the state at the pause is at the end.

## Answer
- **No LIVE or DEMO candidate.**
- **F: fading a fresh minor round level loses everywhere.** This holds on the four European index CFDs no round had
  used and on US2000.
  - Book: IS -3.60 bp per trade (t -4.96), VAL -3.25 (t -3.86), 0 of 9 years positive.
  - Even at zero cost, the best cell's power is 1.46. A cheaper venue would not make it LIVE.
  - The round-28 lead that motivated F was a measurement artefact; it is corrected in round 28's report and the
    journal (below).
- **O: the Asian venue opens.** The direction of the first seconds was tested at the ASX, TSE, A-share / HKEX
  morning and afternoon, and SGE night clocks.
  - Nothing survives costs: the max IS net t is 2.01 against a null median of 2.12 (p 0.63).
  - There is direction at mid (an ASX-open reversal, p 0.021 among the primary cells), but it is 0.4-1.5 bp against a
    1.4-2 bp round trip.
- **Earlier today: the registered HOLD look for gold's $50-level rule** passed at DEMO (n 228, net +2.87 bp, t 1.43).
  It is not LIVE: power 1.40
  ([PREREG_G_gold_round50_cascade.md](round27_levels_opens/PREREG_G_gold_round50_cascade.md)).

## F: fade a fresh minor round level ([STREAM_F.md](round29_fades_opens/STREAM_F.md))
**Setup.**
- Declared at 01:00 UTC ([HYPOTHESES_F.md](round29_fades_opens/HYPOTHESES_F.md)).
- Event: round 28's rule, minor-level cell.
- Primary trade: the opposite side at market at the trigger minute's close, out after 30 minutes.
- Bars are bid only. The spread is IC's published average times an hour-of-day factor taken from DE40 / US500.
- 24 candidate cells.

**Results** (net bp per trade, t):

| set | IS | VAL |
|---|---|---|
| book ES35 + F40 + IT40 + STOXX50 (equal risk) | -3.60 (-4.96); -0.124 sd; n 1,779 | -3.25 (-3.86); -0.113 sd; n 1,126 |
| ES35 | -4.36 (-3.93) | -3.87 (-3.21) |
| F40 | -1.92 (-1.71) | -1.93 (-1.44) |
| IT40 | -5.55 (-2.25) | -3.95 (-1.86) |
| STOXX50 | -3.48 (-2.50) | -4.14 (-2.52) |
| US2000 (control; mid about 0, as predicted) | -2.67 (-3.37) | -2.45 (-2.59) |

**Robustness.**
- Spread x1.5: -0.209 / -0.181 sd.
- Entry one minute later: -0.116 / -0.115 sd.
- The resting limit fade is worse (IS t -5.72): it fills when the price runs through it.

**Why it fails.**
- After the trigger close the price comes back only about +1.2 bp IS / +0.65 bp VAL by 30 minutes, and +2.4 / +1.8 bp
  by 60 minutes.
- The round trip on these CFDs is 4.84 / 3.90 bp.

**Controls and chance.**
- Round levels revert about 1 bp more than shifted grids: the book beats 89 % / 99 % of the shifted grids and
  97.5 % / 87 % of the random entries.
- No cell has IS net > 0; the best IS net t is -0.39.
- The best IS mid t, +2.59 (F40, 15 minutes), is within chance: the sign-flip p95 is 2.69.

**Round 28's index symbols re-run (already seen, information only).** The fade mid is -0.003 sd IS / -0.041 sd VAL.
JP225, HK50 and US500 continue in VAL.

**Correction to round 28.**
- Round 28 R2 measured its "mid" from the modelled stop fill, so the mid included the calibrated stop slippage (0.837
  x the 60-minute median spread).
- For UK100 at 15 minutes, -2.87 of the -2.96 bp "reversion" is that slippage. The price itself returns to the level
  and does not reverse beyond it.
- The same term explains most of why entering a minute late looked better than the stop fill.
- Round 28's report and its journal row are corrected. Its verdict (no continuation outside gold) and its net numbers
  stand.

## O: the Asian venue opens ([STREAM_O.md](round29_fades_opens/STREAM_O.md))
**Setup.**
- Declared at 01:04-01:06 UTC ([HYPOTHESES_O.md](round29_fades_opens/HYPOTHESES_O.md)): round 27 V's method unchanged.
- 2,808 counted cells (39 sets x 72); 24 primary cells; TSE-PM (576 cells) for information only.
- Instruments: AUDUSD, NZDUSD, XAUUSD, XAGUSD, US30, USTEC on IC ticks.
- Calendars: ASX, JPX, HKEX and SSE from the `holidays` package that round 27 used. SGE night sessions follow round
  27's rule plus one correction from SGE's 2024 schedule; 2020-02-03 .. 05-05 is excluded and reported apart.

**Pooled net, primary spec (k 2), bp per trade, IS / VAL:**

| clock (UTC) | fade (V2) | follow (V1) |
|---|---|---|
| ASX-OPEN (23:00 / 00:00) | -0.32 / -0.50 | -3.33 / -1.39 |
| TSE-OPEN (00:00) | -0.86 / -0.53 | -2.64 / -1.41 |
| ASX+TSE | -0.43 / -0.09 | -3.04 / -1.75 |
| CNHK-AM (01:30) | -1.76 / -1.03 | -1.89 / -0.80 |
| CNHK-PM (05:00) | -1.52 / -1.43 | -1.90 / -0.36 |
| SGE-NIGHT (12:00) | -5.06 / -2.24 | -0.20 / -3.39 |

**Best cells.**
- Only one cell has IS t >= 2.0: TSE-OPEN XAUUSD V1 w60 k4 h60, +5.18 (t 2.01, n 43) IS and -5.29 VAL.
- The strongest cell that is positive in both eras: CNHK-AM US30 V1, +17.20 (t 1.76) IS and +5.33 VAL. It is carried
  by 2020; without March-April 2020 IS is +10.7.

**Chance.**
- All counted cells: p 0.63.
- The 24 primary cells: max net t 1.33 against a p95 of 1.36.
- Best per-trade power at the IS size: 1.08.

**Activity checks (no returns).**
- The 00:00 UTC spike is nearly as large on TSE holidays (KRX also opens then).
- The 23:00 UTC winter spike in gold and the US indices is the CME / IC daily reopen.
- AUD's 01:30 UTC spike is the 11:30 Sydney data, not the A-share open.

## Gold's $50 rule against C3, by era (information; lead)
Daily P&L, gold trade days against C3's per-trade file:

| era | daily corr | monthly corr |
|---|---|---|
| IS | -0.021 | -0.242 |
| VAL (registered calendar) | -0.006 | +0.170 |
| HOLD | +0.028 | +0.131 |

The registered promotion bar for a demo run is HOLD + demo pooled t >= 2.5, with >= 100 demo trades and net > 0 at
spread x1.5. Demo trades needed at 130 trades a year:

| demo mean | trades | years |
|---|---|---|
| HOLD mean | 500 | 3.8 |
| VAL mean | 320 | 2.5 |
| half of VAL | about 2,000 | about 15 |

## State at the pause (2026-10-18)
**Running** (VPS; app/cbot_presets.py):
- C3 Gotobi JPY basket (USDJPY, EURJPY, GBPJPY): the only LIVE algorithm.
- EcbWindowBot: F3 live at 0.01 lot and E1 on demo, judged by the stop / promotion rules in
  [PREREG_DRAFT_C_ecb_window_variants.md](round24_relaxed/PREREG_DRAFT_C_ecb_window_variants.md).

**Candidates that passed a registered HOLD below LIVE.** Each has its stop and promotion rules in its file; do not
re-optimise any of them.

| rule | tier | HOLD | file |
|---|---|---|---|
| gold breaks of fresh $50 levels | DEMO | +2.87 bp (t 1.43), n 228 | [PREREG_G_gold_round50_cascade.md](round27_levels_opens/PREREG_G_gold_round50_cascade.md) |
| F3 | RELAXED | +2.00 bp (t 2.16); weak in 2026 | [PREREG_R24_relaxed_hold.md](round24_relaxed/PREREG_R24_relaxed_hold.md) |
| gold into the COMEX settlement on big days | weak DEMO | t 0.37 | [PREREG_L_gold_settlement_bigday.md](round12_flows_execution/PREREG_L_gold_settlement_bigday.md) |
| E1 | weak DEMO | +0.64 bp (t 0.99) | [PREREG_M_eurusd_midday.md](round13_structural/PREREG_M_eurusd_midday.md) |

**Registered forward logs** on data after 2026-09-24 (Dukascopy, the user's choice):
- F3 / E1: rerun `round24_relaxed/prereg_code/fwd_r24.py.txt` with later dates
  ([PREREG_R24_forward.md](round24_relaxed/PREREG_R24_forward.md)).
- B3 / A1: rerun `round24_relaxed/prereg_code/fwd_b3a1.py.txt` with a newer Farside capture
  ([PREREG_R24_forward_B3_A1.md](round24_relaxed/PREREG_R24_forward_B3_A1.md)).

**Decisions only the user can take, most valuable first:**
1. **Run gold's $50 rule on the demo account.**
   - It needs a cBot that places server-side stop orders on ticks.
   - About 130 trades a year at today's gold price; daily correlation with C3 about 0.
   - Promotion would take 2.5-4 years if the edge holds.
   - It is the only mechanism found in 29 rounds, besides C3, with positive net evidence in all four eras (t 2.50
     for 2004-15 at minute level, 2.66 IS, 1.81 VAL, 1.43 HOLD).
2. **IC tick pulls through cTrader backtests on the VPS, plus Dukascopy M1 2004-15**, for USDCNH, USDMXN, USDSGD,
   EURNOK, USDNOK and EURSEK.
   - It costs nothing but a few VPS hours.
   - Hypotheses H-EMFIX, H-CNH and H-NOK are already declared in
     [round25_surprises/HYPOTHESES_A.md](round25_surprises/HYPOTHESES_A.md).
   - Estimated chance: LIVE about 3 %, DEMO about 25 %.
3. **Whether a platform other than cTrader is acceptable.** IC's share CFDs are on MT5 only. The rule (selling after
   the earnings blackout ends) would be built from free data. Estimated chance: LIVE about 3-5 %.
4. **Have a session rerun the forward logs** as data accrues. Each run is one command; no decision is needed beyond
   asking for it.

**Not recommended:**
- IC ticks for the European / Asian index CFDs: rounds 28-29 put their level and open effects below cost.
- The SGE 2020 night-session notice.
- Cross FX, other EM, softs, and a venue change made only for research.
- Paid data.

## Process notes
- F fixed one edge case before reporting: a +1-minute entry could fall on a missing 16:53 New York bar.
- O wrote Addendum 1 after the numbers. It is information only: wider lists of the declared cells, a recomputation
  check, and a fix to the clustering of the TSE-holiday placebo split.
- One Chinese news page was downloaded for the SGE calendar. It was read as data with `python -I`. No request carried
  personal data, and no prices were fetched.

## Files
- [round29_fades_opens/](round29_fades_opens/): BRIEF.md, HYPOTHESES_F.md, STREAM_F.md, HYPOTHESES_O.md, STREAM_O.md.
- Session scratchpad `r29/` (F per-trade CSV, O outputs, the lead's C3-correlation script; not kept).
