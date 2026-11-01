# Draft pre-registration: BTCUSD follows a fresh record break, entered with a resting stop (round 37 A). NOT RECOMMENDED

Draft written 2026-10-29 09:57 UTC (`date -u`) by stream A. **HOLD (2025-01..2026-09) has not been opened.** The rule
was declared in [HYPOTHESES_A.md](HYPOTHESES_A.md) at 09:31 UTC, before any return. It is one of the 12 per-symbol
candidate cells of family A. Details: [STREAM_A.md](STREAM_A.md).

It meets the DEMO numbers on IS / VAL. **Stream A recommends not registering it.**
- It has ~5 trades a year.
- VAL is positive only through one trade.
- HOLD power is 0.57, and promotion to LIVE would take decades of demo.

The draft exists because the process asks for one whenever a declared cell meets a bar.

## Rule (cell A-BTCUSD, K = 5, h = 30; exactly as tested)
- **Instrument.** BTCUSD at IC Markets (cTrader). mid = (bid + ask) / 2.
- **NY session.** Day d runs from 17:00 New York (d-1) to 17:00 New York (d). H_d / L_d are the session's minute mid
  high / low.
- **Levels at the start of session d** (only sessions < d are used):
  - H52 = max H over the sessions in [d - 365 days, d - 1];
  - L52 = min L over the same sessions;
  - ATH = max(4,480, max H of all sessions since 2017-08-28).
  - When ATH = H52 they are one level.
- **Fresh.** The level was set >= 5 sessions before d, i.e. the max H (min L) of the last 5 sessions is below
  (above) it.
- **Order.**
  - Upper levels: a buy stop at R + 0.5 x s60.
  - Lower level: a sell stop at R - 0.5 x s60.
  - s60 = the median closing minute spread of the previous 60 minutes, updated each minute.
- **Armed minutes.**
  - 18:10 NY (d-1) .. 15:54 NY (d);
  - not within +-15 min of a High-impact USD release minute;
  - not within 15 min after a quote gap > 60 min;
  - one position at a time, with a 60-minute busy window after each trigger.
- **Trigger and consumption.** The first reach of the stop in session d decides. If it falls in a non-armed minute
  (including a gap open beyond the level), the level is consumed: no trade.
- **Exit.** Market, 30 minutes after the trigger, capped at 16:54 NY. No protective stop and no swap.
- **Side.** The direction of the break (Osler 2005; Huddart, Lang & Yetman 2009), from the mechanism.

## Numbers
Minute model: entry at the trigger bar's close ask / bid, exit at the close bid / ask 30 minutes later. IC spread, no
commission. t is clustered by UTC day.

| reading | IS (2017-08..2021) | VAL (2022-24) |
|---|---|---|
| trades (a year) | 9 (~2; 52-week levels from 2018-08) | 15 (5) |
| mid, bp (t) | +142.1 (3.35) | +63.2 (0.90) |
| net, bp (t) | **+126.1 (3.17)** | **+52.5 (0.75)** |
| net at spread x1.5 / +1 minute | +118.1 / +138.8 | +47.2 / +51.4 |
| years > 0 | 5/5 | 2/3 |
| per-trade Sharpe; power at the era rate | 1.06; 1.70 | 0.19; **0.57** |
| placebo levels / random times beaten | 0.990 / 1.000 | 0.995 / 0.995 |
| family sign-flip null (48 cells), p of IS net t | 0.036 | |

Fragility:
- **VAL rests on one trade**: +955 bp on 2023-10-23, the false ETF-approval rally. Without it VAL is -12 bp a trade
  (n 14).
- **The five VAL 52-week-low breaks (2022) average -67 bp.** Eight of the nine IS trades and the VAL gains are up-breaks in
  bull phases.
- The K = 1 version (n 27 / 28) is +7 / +17 bp, t 0.24 / 0.44.
- The C3 correlation is about 0 (daily -0.007, monthly +0.008).

## Expected HOLD and DEMO terms (if the lead registers it anyway)
- **HOLD.** About 9 trades (5 a year x 1.73). Expected HOLD t is 0.57 at the VAL Sharpe and ~0.15 at the 1/4
  retention of post-hoc-looking cells. Bar: **net < 0 = reject**.
- **Demo.** About 5 trades a year.
  - Stop rule: cumulative net < 0 after 20 demo trades.
  - Promotion rule: HOLD + demo pooled t >= 2.5. At the VAL Sharpe (0.19) that needs ~170 trades, i.e. ~30 years.
    This is why the draft is not recommended.
