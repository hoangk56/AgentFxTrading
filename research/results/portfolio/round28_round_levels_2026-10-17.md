# Round 28: the gold round-level cascade on the major round levels of the other IC symbols

2026-10-17 (UTC). Same task and bars as rounds 25-27. [round28_round_levels/BRIEF.md](round28_round_levels/BRIEF.md)
declared one rule for 22 symbols at 22:08 UTC, before any round-28 return: level spacings from a fixed sequence
{1, 5} x 10^k nearest to 3.4 % of each symbol's IS median price (gold's $50), the round-27 order logic, a 30-minute
exit, the same exclusions plus C3's JPY window, 200 shifted-grid placebos per symbol, and a pooling script written
before the results ([round28 lead pool.py](#files)). HOLD was never loaded.

## Answer
- **No LIVE candidate. The round-level continuation is specific to gold.** At the major round levels of 21 other
  symbols (FX majors, JPY crosses, US / European / Asian indices, oil, BTC) a resting stop beyond a fresh level shows
  no continuation; the mid move is about 0 and the net is negative in every class.
- **The pooled book fails**: IS -0.093 sd per trade (t -6.55, raw -3.94 bp), VAL -0.024 (t -1.85), 0 of 6 IS years
  positive; without gold IS -0.105 (t -7.33). Per-day power -3.8 / -1.4. Spread x1.5 and +1 minute are worse or the
  same.
- **Gold under the round-28 rule** (a slightly longer arming window and a 0.15 %-of-price band): IS +4.97 bp (t
  2.28), VAL +2.80 (t 1.59), 8 / 9 years; the 31 trades it adds to round 27's rule lose (-7.7 / -6.1 bp). The
  **corrected minute-level PRE** (round 27's PRE script had a one-bar look-ahead in the freshness test) is **+3.90 bp
  (t 2.50)**, positive in both halves of 2004-15, 8 of 12 years, all 200 placebo grids beaten.
- Next: round 27's gold rule is registered as a DEMO candidate and its HOLD is opened once (separate file).
  Done 2026-10-18 ([PREREG_G_gold_round50_cascade.md](round27_levels_opens/PREREG_G_gold_round50_cascade.md)): HOLD
  n 228, net +2.87 bp (t 1.43). It passes the DEMO bar; at power 1.40 it is not LIVE.

## R1: tick symbols ([STREAM_R1.md](round28_round_levels/STREAM_R1.md))
Major levels, 30-minute exit, 250 ms latency; declared at 22:26 UTC in
[HYPOTHESES_R1.md](round28_round_levels/HYPOTHESES_R1.md); engine = round 27's, adapted; 16 synthetic test groups and
a tick-by-tick re-run of 25 real sessions match (max difference 1.3e-6 bp).

| symbol | n IS / VAL | net IS (t) | net VAL (t) | years > 0 | power IS / VAL | placebo beaten IS / VAL |
|---|---|---|---|---|---|---|
| XAUUSD | 282 / 193 | +4.97 (2.28) | +2.80 (1.59) | 8/9 | 1.30 / 1.28 | 1.00 / 1.00 |
| AUDUSD | 101 / 47 | -1.78 | +0.76 | 4/9 | < 0 / 0.27 | 0.36 / 0.76 |
| NZDUSD | 88 / 39 | -1.46 | -2.32 | 3/9 | < 0 | 0.77 / 0.41 |
| US30 | 280 / 196 | -0.79 | +0.63 | 5/9 | < 0 / 0.31 | 0.42 / 0.65 |
| USTEC | 223 / 239 | -1.88 | +1.24 | 4/9 | < 0 / 0.45 | 0.32 / 0.99 |
| XTIUSD | 841 / 911 | -3.26 | -2.56 | 1/7 | < 0 | 0.88 / 0.31 |
| XBRUSD | 894 / 884 | -6.93 (-3.30) | +1.70 | 2/7 | < 0 / 0.77 | 0.05 / 1.00 |

- 8 of 126 cells meet the DEMO numbers, all gold; outside gold the best IS t is +1.32 (US30 repeat touches, VAL
  -3.21 bp). Outside gold the major levels look like the shifted grids at mid: the small positive mid is momentum
  after any fresh 24-hour high or low, not a round-number effect.
- **Minute-vs-tick fill calibration**: a minute model that enters at the stop price overstates by +1.7 to +3.5 bp,
  because 11-17 % of tick triggers reverse inside the minute and lose 12-15 bp each; a minute model that enters at the
  trigger bar's close is unbiased within +-0.8 bp but misses the in-minute continuation (gold +2.91 / +3.03 against the
  tick +4.97 / +2.80).

## R2: minute-only symbols ([STREAM_R2.md](round28_round_levels/STREAM_R2.md))
Declared at 22:40 UTC in [HYPOTHESES_R2.md](round28_round_levels/HYPOTHESES_R2.md) (270 cells). Minute fill model
reading the bar's highs and lows, calibrated on AUDUSD and US30 ticks (97-98 % trigger agreement; remaining bias
<= +-0.23 bp).

| symbol | IS net (t) | VAL net (t) | PRE net (t) | years > 0 |
|---|---|---|---|---|
| EURUSD | +0.47 (0.25) | -2.52 (-1.62) | -0.61 | 3/9 |
| GBPUSD | +0.24 | -1.11 | - | 2/9 |
| USDCAD | -1.33 | -0.95 | - | 4/9 |
| USDCHF | -2.90 (-2.67) | -2.86 (-2.17) | +0.48 | 2/9 |
| USDJPY | -1.47 | +0.74 | -1.18 | 3/9 |
| EURJPY | +0.92 | -0.48 | +0.23 | 3/9 |
| GBPJPY | -3.22 (-2.59) | +1.58 | -0.41 | 2/9 |
| AUDJPY | -2.15 | -3.41 (-2.41) | - | 1/9 |
| US500 | -1.79 | -0.10 | - | 4/9 |
| DE40 | -3.79 (-2.58) | -3.03 | - | 0/9 |
| UK100 | -7.99 (-3.23) | -3.25 | - | 1/9 |
| JP225 | -2.00 | -1.08 | - | 3/9 |
| HK50 | -5.45 (-3.00) | -3.21 | - | 2/9 |
| AUS200 | -5.15 (-4.03) | -2.70 (-2.89) | - | 0/9 |
| BTCUSD | -14.09 (-2.48) | -1.77 | - | 2/8 |
| AUDUSD / NZDUSD (PRE only) | - | - | -1.93 / -2.60 | 4/12 |

- No dose response (set mid at minor / major / super levels: IS -0.021 / -0.029 / -0.054 sd); the declared side split
  (downward breaks stronger in indices and BTC) fails; best IS net t across all cells +1.58 (VAL -0.24).
- Information only (post hoc, the opposite side). **Corrected 2026-10-18 by round 29 F.**
  - This report first said that minor index levels reverse: UK100 100-point levels at 15 minutes "mid" -2.96 bp
    (t -4.35) IS and -2.47 (t -2.87) VAL, AUS200 the same. It also said that in indices and BTC, entering a minute
    after the trigger beats the stop fill.
  - R2's "mid" is measured from the modelled stop fill, so it includes the calibrated stop slippage (0.837 x the
    60-minute median spread). For UK100 at 15 minutes, -2.87 of the -2.96 bp is that slippage. The price itself is
    back at the level, not beyond it.
  - The +1-minute entry has no slippage term, which explains most of its apparent advantage.
  - Faded on four fresh European index CFDs, the pattern loses
    ([round29_fades_opens/STREAM_F.md](round29_fades_opens/STREAM_F.md)).
  - The net columns above are unaffected: they always included the slippage.

## Pooled book (lead, pool.py on both CSVs; major levels, 30 min, 250 ms / minute fills)
| pool | n / yr IS | IS sd / trade (t) [bp] | VAL sd / trade (t) [bp] | years > 0 | power IS / VAL |
|---|---|---|---|---|---|
| book | 1,122 | -0.093 (-6.55) [-3.94] | -0.024 (-1.85) [-0.73] | 0/6, 1/3 | -4.09 / -1.63 |
| book without gold | 1,075 | -0.105 (-7.33) | -0.029 (-2.21) | 0/6, 1/3 | -4.52 / -1.89 |
| gold | 47 | +0.144 (2.28) | +0.081 (1.60) | 5/6, 3/3 | 1.30 / 1.28 |
| FX USD pairs | 109 | -0.091 (-2.45) | -0.104 (-2.48) | | < 0 |
| JPY crosses | 86 | -0.108 (-2.82) | -0.012 | | < 0 |
| US indices | 129 | -0.049 | +0.015 | | -0.73 / 0.38 |
| other indices | 246 | -0.164 (-5.72) | -0.089 (-3.35) | | < 0 |
| oil | 434 | -0.082 (-3.21) | -0.006 | | < 0 |
| BTC | 71 | -0.115 (-2.49) | -0.014 | | < 0 |

PRE (FX and gold, minute level): book -0.027 sd (t -1.03). The real book beats 96.5 % / 99.5 % of the 200 placebo books
in IS / VAL only because randomly shifted levels revert slightly more than real ones; the real levels themselves show
no continuation outside gold.

## What this says
- Gold's round levels are special, as the literature found for gold and not silver (Lucey & O'Connor 2016). The
  continuation does not exist at the comparable levels of FX, indices, oil or BTC; at index levels the first minutes
  after a break even revert.
- A LIVE algorithm cannot be built from this mechanism: gold alone has ~60 breaks a year (power ~1.3-1.5).

## Process notes
- Round 27's minute-level PRE script had a one-bar look-ahead in the 24-hour freshness test (event selection only);
  round 28 R1 fixed it: gold PRE +3.90 (t 2.50) instead of +5.35.
- pool.py first used 6 IS years for oil (its IS is 2018-21); fixed before the pooled run (means and t unaffected).
- R2's FX slippage term was declared in spread units but IC's FX minute spread is often exactly 0 (EURUSD 64 % of
  minutes), so it was set in bp (addendum before any R2 return).

## Files
- [round28_round_levels/](round28_round_levels/): BRIEF.md, HYPOTHESES_R1.md, HYPOTHESES_R2.md, STREAM_R1.md,
  STREAM_R2.md, PREREG_DRAFT_R1_gold_major_cascade.md (a variant of round 27's gold draft; not registered).
- Session scratchpad `r28/` (R1, R2 per-trade CSVs; lead pool.py and its output pool_major_L250.txt; not kept).
