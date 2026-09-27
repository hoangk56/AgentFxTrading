# Round 3: flows, settlement conventions and risk premia beyond gotobi (2026-09-27)

Search for a new algorithm for the swing lab: an economic basis, a mechanism different from C3 (gotobi / Tokyo fix)
and C1 (crypto trend breakout), and low correlation with both. The same three constraints as the earlier rounds:
lots never depend on capital, a position is held 5 days at most, a bot holds 3 positions at most. Eras: IS 2016-2021
(selection), VAL 2022-2024 (check), HOLD 2025-01..2026-09-24 (once per pre-registered candidate).

## Answer

**No new algorithm passes.** About forty mechanisms were tested. One candidate reached a pre-registered holdout and
failed it:

| candidate | mechanism | IS | VAL | HOLD | verdict |
|---|---|---|---|---|---|
| **M1** month-end value-date USD | buy USD vs JPY, CHF, EUR 10:00-13:00 UTC on the 3rd-to-last weekday (last day whose T+2 spot settles in the month) | R +0.123, day-clustered t 3.2, 6/6 yrs | R +0.228, t 2.6, 3/3 | R +0.044, t 0.7, 1/2 yrs | **failed** its registered bar ([prereg](prereg_month_end_usd_2026-09-27.md)) |
| F1 month-end WM/R fix reversal | fade the 15:00-16:00 London move after the month-end 16:00 fix (Evans 2018) | R +0.085, t 3.1, 5/6 | R +0.005, t 0.1, 1/3 | not run | failed VAL |
| O1 oil roll-day settlement | short WTI/Brent 12:00-14:30 ET on GSCI roll days (business days 5-9) | R +0.004, t 0.2 | not run | not run | failed IS in the engine |
| U1 equity -> USD rebalancing | after a US equity move of more than 1 sd, trade USD against it at the next London fix (Hau & Rey) | R +0.009, day-clustered t 0.3 | not run | not run | failed IS |
| W1 Wednesday triple-swap rollover | short the high-yielder after Wednesday's 17:00 NY rollover | mid -3.0 bp (t -4.2); executable +1.1 bp (t 1.4) | mid -3.8 bp (t -3.9); executable -0.1 bp | not run | the effect is real in mid prices but not tradeable (see below) |

C3 remains the only algorithm in the repo that has passed out-of-sample years and a pre-registered holdout.

**Data limits.** The cache ends 2026-09-24 and there is no newer data, so HOLD is 2025-01..2026-09-24, the period C1,
C3, C4 and the removed lab already used as their holdout. Two process slips put a little of this round's HOLD in
view before any candidate existed (details in "Process" below). Neither affects M1 except as disclosed in its
prereg.

## M1: the candidate that reached HOLD

**Rule** (`research/swing/swing_rules.month_end_usd`, runner `python -m research.swing.month_end_usd [--hold]`):

- One bot: USDJPY, USDCHF, EURUSD, cap 3 (one position per symbol).
- Day: the third-to-last weekday (Mon-Fri) of the calendar month, by UTC date (holidays not modelled).
- Buy USD (buy USDJPY and USDCHF, sell EURUSD) on the M5 close at 10:00 UTC. Exit on the M5 close at 13:00 UTC, or at
  the stop of 3 x ATR20(H1). Lot = $100 default risk / stop (1x). No rollover is crossed.
- Hypothesis: T+2 spot trades done that day are the last to settle inside the month, so month-end dollar needs are
  bought then, in the European morning, and the move is given back afterwards. After 13:00 the 7-pair USD basket did lose
  9.5 bp (IS) / 7.7 bp (VAL) by 20:00 UTC on the last weekday (t -1.4 / -1.0).

**How it was found.** From the 90,168-cell calendar x window scan below (USDJPY cell: IS +6.4 bp, t 4.3, which is
below the ~4.9 a Bonferroni correction over the scan would need). VAL was visible when the cell was picked. The
three pairs were chosen on IS; GBPUSD, AUDUSD, NZDUSD and USDCAD were about 0 in IS.

**Numbers** ($100 risk per trade; day-clustered t, because three USD pairs on one day are close to one USD bet):

| era | trades (days) | mean R | t | day-clustered t | net $ | years > 0 | max DD |
|---|---|---|---|---|---|---|---|
| IS 2016-2021 | 216 (72) | +0.123 | +4.4 | +3.2 | +2,664 | 6/6 | $351 |
| VAL 2022-2024 | 108 (36) | +0.228 | +3.8 | +2.6 | +2,457 | 3/3 | $391 |
| HOLD 2025-01..2026-09 | 60 (20) | +0.044 | +1.0 | +0.7 | +266 | 1/2 | $160 |

By year: 2016 +$416 · 2017 +$696 · 2018 +$557 · 2019 +$74 · 2020 +$571 · 2021 +$349 · 2022 +$205 · 2023 +$1,394 ·
2024 +$858 · 2025 +$405 · 2026 (to Sep) -$139.

- Per pair, IS / VAL / HOLD mean R: USDJPY +0.143 / +0.217 / +0.032, USDCHF +0.143 / +0.218 / -0.020, EURUSD
  +0.084 / +0.247 / +0.120.
- 1.5x spread: IS +0.121, VAL +0.226, HOLD +0.042.
- Random-day control (1 random other weekday per month, same pairs, window and stop, 500 seeds): real beats 99.2 %
  (IS), 100 % (VAL), 79.4 % (HOLD).
- Placebo, same window on the k-th last weekday (k = 1..10 except 3): day-clustered t between -1.9 and +1.9 (IS) and
  -1.9 and +2.5 (VAL). k = 3 stands about 2 of the placebo's standard deviations out in each era, not more.
- Not an FOMC effect: without the 10 FOMC days, IS t 2.7 and VAL t 2.6. Quarter-ends are not stronger in VAL.
- P&L correlation with C3: daily -0.021, monthly -0.019. With C1: daily -0.017, monthly -0.041.

**Verdict.** It failed two of the four registered criteria (day-clustered t 0.7 < 1.0; random-day control 79.4 % <
80 %). It kept its sign but shrank to about a third of its IS size, which is what a cell picked from a large scan
tends to do. It is not adopted and not re-tested with any change. The only legitimate further test is new data
after 2026-09-24, and at 12 days a year that would take years.

## What was tried and rejected

All numbers are IS / VAL. "Mid" = mid-price returns before costs; "engine" = `research/swing/swing.py` with real bid/ask,
commission and swaps. The round-trip cost in bp is the median spread since 2022 plus commission: US30 0.23,
DE40 0.29, USTEC 0.34, US500 0.66, EURUSD 0.69, USDJPY 0.90, XAUUSD 1.6, BTCUSD 1.8, XAGUSD 5.5.

### Scheduled events and announcement premia

| hypothesis (source) | where | result |
|---|---|---|
| Pre-FOMC drift, 14:00 ET the day before -> 13:55 ET (Lucca & Moench 2015) | US indices, DE40, FX, gold | mid US500 +9.8 bp (t 1.2) / +47.7 (t 3.1). **Not eligible**: the screen also printed HOLD by mistake (US500 -8.5, US30 -9.2, USTEC -0.5, DE40 -6.9 bp) |
| FOMC-cycle even weeks (Cieslak, Morse & Vissing-Jorgensen 2019) | US indices, DE40, UK100 | no even-week premium: US500 even +4.8 bp/day (t 1.1) vs odd +6.6 (t 1.8); VAL +1.5 vs +4.3 |
| NFP-day premium (Savor & Wilson 2013) | US indices, DE40, gold | US500 NFP Friday +12.7 bp (t 1.0) / +16.9 (t 0.8): too few events to tell |
| Post-announcement drift after the 08:30 ET releases (follow a first 5-min move of more than 3 or 5 x its norm) | 6 FX, gold, 4 indices | no follow-through or reversal: no cell has the same sign with \|t\| > 2 in both eras |
| VIX fear premium, FRED VIXCLS (Connors 2008 "VIX stretch", VIX +20 % in 3 days, VIX > 1.2 x MA20) | US indices, 5-day hold | after spikes IS is at or below the unconditional drift (US500 stretch -14.7 bp, spike -29.5 bp); VAL positive (+68.9 bp); the signs disagree |

### Fixes, settlement conventions and benchmark flows

| hypothesis (source) | where | result |
|---|---|---|
| USD rises into the ECB 14:15 CET fix, falls after (Krohn, Mueller & Whelan 2024) | 7 USD pairs | real but tiny: EURUSD +1.1 bp (t 2.9) / +1.2 (t 2.1) against 0.69 bp cost, about 0.02 R net |
| WM/R 16:00 London fix, every day | 7 USD pairs | no pre/post-fix pattern; the reversal after the fix flips sign (all pairs pooled +0.4 bp, t 4.5 / -0.3, t -1.7) |
| **F1** month-end WM/R fix reversal (Evans 2018; Melvin & Prins 2015) | 7 USD pairs, one bot of cap 3 | mid pooled +2.4 bp (t 3.0) / +2.5 (t 2.2); engine R +0.085 (t 3.1) / **+0.005 (t 0.1)**, faded from 2021 |
| **M1** month-end value-date USD demand | USDJPY, USDCHF, EURUSD | passed IS/VAL, **failed HOLD** (above) |
| Gold ETF creations at the LBMA PM price (prior-day or prior-week sign x move into the fix) | XAUUSD, XAGUSD | IS \|t\| <= 2.4, VAL \|t\| <= 1.1, costs larger |
| **O1** commodity-index roll pressure into NYMEX settlement (Mou 2011; Bessembinder et al. 2016) | XTIUSD, XBRUSD, business days 5-9 | mid 12:00->14:29 ET WTI -21 bp (t -2.0) / -12 (t -1.6), mixed by year; engine short R +0.004 (t 0.2). IC's energy CFDs are continuous (no roll gaps), so the front-vs-next spread itself cannot be seen |
| Post-closing-auction reversal (MOC / index flows) | US indices, DE40, UK100, JP225, AUS200 | none. US shows continuation after 16:00 in IS (US500 -1.6 bp, t -3.9); at month-end US30 -2.9 (t -2.1) / +2.5 (t 1.9); quarterly rebalance days also noise |
| Pension month-end rebalancing, month-to-date sign (Harvey, Mazzoleni & Melone 2025) | US indices, DE40, UK100 | the sign flips: US30 last 4 days +59.6 bp (t 2.9) / -75.9 (t -2.4) |
| Nikkei leveraged-ETF rebalancing at the Tokyo close | JP225 | nothing: no follow-through into the close; the fade after it reaches IS t -3.6 (-2.4 bp) and VAL goes the other way (+0.6) |
| Vol-control funds buying when a big day leaves the 21/63-day window | US indices, DE40 | US500 20 trading days after a big day +0.26 daily sd (t 2.1) / -0.16 (t -1.2); the placebo lags are just as large |
| **W1** Wednesday triple-swap rollover flow | 10 FX pairs, carry-signed from FRED rates | mid: after the Wednesday rollover (17:15 NY -> 03:00 NY) the high-yielder falls -3.0 bp (t -4.2) / -3.8 (t -3.9), against -1.4 / +0.3 on Tue/Thu, so the effect scales with the triple day. But 17:15-19:00 NY holds most of it (t -5.5 / -7.9), when the median spread is still 2.9 bp at 17:15 and 2.2 bp at 18:00 (normal 0.1-0.3). At executable prices the best entry/exit nets +1.1 bp (t 1.4) / -0.1: the value-date roll working into the quotes, which the swap compensates. Into the Wednesday rollover (12:00-16:55 NY): +2.2 bp (t 3.1) / +1.4 (t 1.6), about 1 bp net |
| Pre-weekend carry unwind / Monday rebuild | 10 FX, carry-signed | Friday 12-20 UTC -3.7 bp (t -3.9) / -0.1; Monday 00-08 UTC +1.5 (t 2.3) / -0.4 |

### Risk premia

| hypothesis | where | result |
|---|---|---|
| Night (close -> open) equity premium (Cliff, Cooper & Gulen; Hendershott et al.) | 8 indices | US500 night +4.9 bp (t 3.1) / +1.0 (t 0.4); after the long swap and costs +1.9 / **-3.2**; USTEC +7.1 (t 3.8) / +1.6 |
| Weekend premium (Friday close -> Monday) | 22 non-crypto | metals looked positive (XAGUSD +10.1 bp, t 2.7 / +8.5, t 2.4), but it is a rise in the Friday last-hour quote (XAGUSD bid +2.7 / +6.9 bp, t 5.7): buy at ask 1 h before the close, sell 8 h after the reopen: +11.6 bp (t 1.9) / -5.4 |
| **U1** US equity -> USD next day, portfolio rebalancing (Hau & Rey 2006; Camanho, Hau & Rey 2022) | 7 USD pairs | the daily lead is there (USDCHF -4.8 bp per equity sd, t -4.3 / -4.0, t -1.9) but engine IS R +0.009 (day-clustered t 0.3) at the next London fix, and the 1-day hold is also \|t\| < 2 |

### Liquidity provision and microstructure

| hypothesis | where | result |
|---|---|---|
| Asian-hours (23:00-06:00 UTC) mean reversion, M5, fade 2-3 ATR from SMA20 | 10 FX, gold | negative everywhere: EURUSD R -0.086 (t -8.8) / -0.073; XAUUSD -0.232. Engine and fast screen agree |
| Overnight index mean reversion (22:00-06:00 UTC) | US30, USTEC, US500, DE40, UK100 | negative: overnight index spreads are several times the daytime median (UK100 R -0.64, DE40 -0.47, US30 -0.15 IS) |
| Volume-conditioned reversal, tick count as volume (Campbell, Grossman & Wang 1993) | all 26 by class | the signs flip between eras (FX low-volume 3-day fade IS -0.19 sd, t -2.7 / +0.32, t +3.1) |
| Weekend-gap fade (Sunday open) | 22 non-crypto | too few large gaps and no IS signal |
| Stop / take-profit clustering at round numbers (Osler 2003, 2005) | 10 FX | 0.1-0.8 bp after a big-figure cross, no different from a non-round control level |
| Crypto liquidation-cascade fade (\|z\| > 3-5 over 1-6 h, hold 2-8 h) | BTCUSD, ETHUSD | the mid event study is positive and only in crypto (IS +0.3..0.6 hourly sd, t 1.1-1.6); the engine is negative in 24 of 27 IS cells (e.g. L1 k4 H4 R -0.044), because of the fill after the spike and 2018-20 spreads (BTC 3.5-17 bp, ETH 90-250 bp) |
| Crypto perpetual-funding times (00/08/16 UTC; BitMEX 04/12/20) | BTCUSD, ETHUSD | <= 3 bp with no sign kept across eras |
| Crypto intraday momentum (day return -> last 30 min before 00:00 UTC; Wen et al. 2022) | BTCUSD, ETHUSD | BTC +8.8 bp (t 4.1) / +2.6 (t 1.9) mid, against 1.8 bp cost now and 3.5-17 bp in the IS years |
| Friday position-squaring (fade the week into Friday afternoon) | 22 non-crypto | no reversal. Energies continue instead (as a fade: -6.3 % of a weekly sd, t -2.9 / -3.4 %, t -1.5) |
| FX session hand-off (Asia -> London open, London morning -> midday, NY -> afternoon) | 10 FX, 3 indices, oil | every IS cell \|t\| <= 2.0, no consistent sign |

### Cross-asset lead-lag

| hypothesis | where | result |
|---|---|---|
| Daily 26 x 26 lead-lag (vol-scaled, 20:00 UTC closes) | all pairs of symbols | 676 pairs, max IS \|t\| 4.1. Only the equities -> USDCHF cluster keeps its sign in VAL (IS corr -0.08..-0.11, VAL -0.04..-0.07, t -1.1..-1.9); that is U1. Oil -> USDCAD -0.105 (t -3.2) / -0.011; US equities -> BTC +0.099 (t 3.1) / -0.026 |
| Oil -> CAD within the day (a 30 bp hourly oil move -> USDCAD next 1-3 h) | USDCAD | +0.2..0.5 bp |

### Systematic scans (to catch what the hypotheses above missed)

| scan | size | result |
|---|---|---|
| Hour-of-day drift (UTC) | 7 symbols x 24 h | about 1 bp against 0.4-2 bp costs; signs unstable across eras |
| Weekday x session (Asia / Europe / US) | 373 cells | max IS \|t\| 3.7 (BTC Friday Asia -53 bp, VAL +0.6): what chance produces |
| Day of month x 4 h block on composite factors (USD, equities, metals, oil, crypto, EUR, AUD, GBP, CAD) | 1,303 cells | max IS \|t\| 3.5; the top cells do not repeat in VAL |
| Calendar x intraday window: weekday, business day +-1..5 of the month, gotobi; windows 1-8 h from 18:00 UTC the evening before | 90,168 cells (49 with \|t_IS\| >= 4) | top IS t 5.4 (XAUUSD 3rd-last business day 15-16 UTC, VAL -2.8 bp). The ones that repeat are tiny or rollover / Friday-close quote effects, plus the M1 cell. Sanity check: at hour resolution the scan sees gotobi only weakly (USDJPY 18:00->01:00 on gotobi days +2.85 bp, t 2.5), because the effect is timed to the 00:55 fix. So the scan rules out hour-scale calendar flows, not minute-precise fix flows (tested separately above) |

## What this round says

- Outside gotobi, the time-and-calendar flows in these 26 symbols are 0.5-3 bp, the same order as the round-trip
  cost (0.2 bp on US30 to 2 bp on gold and 5 bp on silver). When they are bigger, it is at a moment when the spread
  is wide (rollover, Friday close, Sunday open).
- Two effects are real but priced: the Wednesday value-date roll (compensated by the triple swap) and the ECB-fix
  USD move (about 1 bp).
- Patterns picked from wide scans shrink out of sample, even after a VAL check that was in view (M1). A future
  candidate needs a mechanism written before the data is looked at, or a clean holdout.
- What would change the picture, none of it tested here because the brief fixes the data: (1) new holdout data after
  2026-09-24, as it accumulates; (2) data this repo does not have, such as CFTC positioning, the VIX futures term
  structure or order flow; (3) the 5-day limit, which rules out the multi-week trend and carry premia (the brief fixes
  it; not proposed).

## Process

- **HOLD seen before any candidate existed (disclosed).** (1) The first FOMC event study printed HOLD columns for 9
  symbols on the 14 HOLD FOMC days, so the pre-FOMC drift is not eligible. Three of those days are M1 days (see the
  prereg). (2) The first hour-of-day screen printed 2025-26 hourly means for XAUUSD, XAGUSD, US500, DE40, JP225,
  AUDUSD and BTCUSD, so hour-of-day patterns of those symbols were not used as candidates. After that, every screen
  printed IS and VAL only.
- The exploratory screens ran as scratch scripts on the M1 cache (mid prices, costs quoted separately). Only M1
  went into the repo (`swing_rules.month_end_usd`, `swing/month_end_usd.py`, two tests in `tests/swing/test_swing.py`),
  because only M1 went to HOLD. The engine checks of F1, O1, U1 and the crypto fade used the same `swing.py` with
  rules written the same way.
- Files: [prereg_month_end_usd_2026-09-27.md](prereg_month_end_usd_2026-09-27.md) (registration, hashes, HOLD
  result); `trades_M1_month_end_usd.csv` (git-ignored).
