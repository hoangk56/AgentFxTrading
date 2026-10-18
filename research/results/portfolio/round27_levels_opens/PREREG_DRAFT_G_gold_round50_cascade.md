# Draft pre-registration: gold continues after a fresh $50 level breaks, entered with a resting stop (round 27 G)

Draft written 2026-10-17 21:56 UTC (`date -u`) by stream G. **HOLD (2025-01-01..2026-09) has not been opened.** The
lead decides whether to register this and open HOLD. Tier: **DEMO numbers on IS / VAL**. It is not LIVE: power at
the VAL size is 1.45 against the 3 that LIVE needs. Details: [STREAM_G.md](STREAM_G.md); the rule was declared in
[HYPOTHESES_G.md](HYPOTHESES_G.md) at 21:23 UTC, before any return was computed.

## Rule (cell G1-XAU50, c = 0.5, h = 30, no protective stop; exactly as tested)
- **Instrument and data.** XAUUSD at IC Markets (cTrader), tick quotes. mid = (bid + ask) / 2.
- **Levels.** $10 levels L = 10k. A trade is taken only when L is a multiple of $50.
- **Arming window.** From 18:10 New York (day d-1) to 15:54 New York (day d). No arming within +-15 minutes of a
  High-impact USD release minute (the timed calendar), and none within 15 minutes after a tick gap > 60 minutes.
- **Arming.** The bot arms only while flat, i.e. 60 minutes or more after its last trigger. It arms on the nearest
  $10 level within $2 of the mid:
  - an upper level L (mid in [L - 2, L)) if L is above the highest tick mid of the previous 1,440 clock minutes;
  - a lower level L (mid in (L, L + 2]) if L is below the lowest tick mid of that window;
  - in both cases only if this level has not triggered in the previous 1,440 minutes and the order would not be
    marketable when placed.
- **Order.** Upper level: a buy stop at L + 0.5 x s60. Lower level: a sell stop at L - 0.5 x s60.
  - s60 = the median, over the 60 clock minutes before the arming minute, of each minute's last-tick spread.
  - The order price is fixed when the order is placed.
  - The order is cancelled when the mid leaves the $2 band (upper: mid < L - 2; lower: mid > L + 2) or an exclusion
    window starts. It can re-arm later.
- **Trigger.** The stop triggers server-side: the buy stop when the ASK reaches it, the sell stop when the BID does.
  - The trade is taken only if L is a multiple of $50.
  - A trigger at another $10 level is not traded. It still starts the 60-minute busy window and still counts as this
    level's trigger for the 1,440-minute rule (this is how the tested cell is defined).
- **Exit.** A market order 30 minutes after the trigger. No protective stop. The position never crosses 17:00 New
  York, so no swap. At most one position open; lot fixed (not a function of capital).
- **Side.** The direction of the break (continuation). It comes from the source (Osler 2003 / 2005, stop-loss orders
  clustered beyond round numbers), not from our data.

## Numbers on IS (2016-21) and VAL (2022-24)
Model and units:
- Latency L = 250 ms. Fills at the ASK / BID of the first tick at or after the trigger + L.
- Commission 0.6 bp round trip.
- bp per trade, t clustered by UTC day.

| reading | IS | VAL |
|---|---|---|
| trades (per year) | 271 (45.2) | 185 (61.7) |
| mid, bp (t) | +7.72 (3.41) | +4.29 (2.37) |
| net L0 / tick / 250 / 1000 ms | +6.10 / +6.05 / **+5.99 (t 2.66)** / +5.85 | +3.39 / +3.25 / **+3.27 (t 1.81)** / +3.25 |
| net at spread x1.5 | +5.42 | +3.05 |
| net, both fills +1 minute | +6.19 | +2.87 |
| per-trade net Sharpe; power at its own rate | 0.172; 1.52 | 0.140; **1.45** |
| per-day power | 1.42 | 1.37 |
| random control: 200 offset grids, share beaten (draw median) | 0.96 (-1.74) | 0.995 (+0.42) |
| random control, offsets $3-7 from the real levels only | 1.00 | 1.00 |
| $5 half-level placebo, same cell | -4.86 | -0.85 |

Net by year:

| 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|
| +4.84 | +4.86 | +6.17 | +0.19 | +8.26 | +8.45 | +2.28 | +5.24 | +3.04 |

Nine of nine years are positive. VAL / IS = 0.55.

Robustness:
- The median trade is about 0 (IS -0.18, VAL -0.70), so the payoff is a right tail. Trimmed at the IS 1 / 99 %
  quantiles: +4.36 IS / +3.27 VAL. The top 5 trades make 890 of the 2,227 bp total.
- Without March-April 2020, IS is +6.09 (t 2.66).
- Downward breaks carry IS (+11.85 vs +1.33 upward). VAL is more even (+3.71 vs +2.81).
- PRE 2004-15, Dukascopy, minute level (labelled). Entry at the trigger close, which is unbiased and understates the
  tick result in the IS calibration (+1.51 there vs +5.99 on ticks):
  - net +5.35 (t 3.12), mid +6.94 (t 4.05);
  - 2004-09 +7.15 (t 2.30), 2010-15 +3.82 (t 2.18); 8 of 12 years positive;
  - the $5 placebo is -0.51 at minute level.

## Cell count, selection, chance
- **Cells.** 384 candidate cells were declared (192 in G1). 18 G1 cells meet the DEMO numbers: 13 at $50 levels and
  5 on repeat touches. None meets LIVE: VAL-size power is at most 1.51.
- **The declared primary fails.** All $10 levels, c 0.5, h 60: IS net +0.66 (t 0.76).
- **How this cell was picked.** The $50 dose set and the offset c = 0.5 were declared (c = 0.5 is the family's
  declared primary offset). The 30-minute hold was picked after looking at IS / VAL:
  - h = 15 is also DEMO (IS +5.17, t 3.27; VAL +2.18, t 1.53; VAL power 1.21);
  - h = 60, the declared primary hold, missed the VAL random control (0.89 against the 0.90 needed).

  So treat the expected HOLD retention as below the 0.65 of fully declared rules.
- **Chance.** G1 sign-flip null (one sign per UTC day shared by the 192 cells): the max IS mid t has p95 3.11. This
  cell's IS mid t is 3.41; the family's maximum is 5.56 (the $100 levels, c 1, h 15), and no null draw reached it.
  Max |t| of 192 independent normals: p95 3.63.

## Expected HOLD (21 months)
- About 107 events (61.7 a year x 1.73).
- Expected HOLD t:
  - 1.45 at the VAL effect size;
  - 0.94 at 0.65 of it (the retention of declared rules);
  - 0.36 at 0.25 of it (the retention of post-hoc picks).
- If registered as DEMO: open HOLD once; **net < 0 in HOLD = reject.**

## DEMO terms (if run on the demo account)
- About 60 trades a year.
- Stop rule: stop if cumulative net is below 0 after 60 demo trades, or below -1.5 sd of the expected sum after 120.
- Promotion rule: HOLD + demo pooled net t >= 2.5. At the VAL Sharpe (0.140) that needs about 320 trades, i.e.
  about 5 years at this event rate.
- LIVE is out of reach at IC's cost unless the effect is larger than in VAL. LIVE needs power 3, i.e. a per-trade
  Sharpe of 0.29 at ~107 HOLD events; VAL gives 0.14.

## Correlation with C3
IS + VAL rows only: daily -0.008, monthly -0.141. The h = 15 version: daily +0.001, monthly -0.006.

## Recommendation
Opening HOLD alone has low value: the expected t is 0.9-1.45 and the bar is only net > 0. A demo or forward log
(data after 2026-09-24) would build evidence without using HOLD, but at ~60 events a year it would take years. The
mechanism is the most robust found in rounds 25-27:
- it is present in PRE, IS and VAL;
- it rises with the dose ($10 < $50 <= $100);
- shifting the levels by $3 or more removes it.

It is not fast enough to trade at IC's cost with power.
