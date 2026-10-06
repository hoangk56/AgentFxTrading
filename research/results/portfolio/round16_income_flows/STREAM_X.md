# Round 16, stream X: what each pending decision is worth

2026-10-06, written 02:20-02:40 UTC. **This stream computes no new returns and loads no price data.** No IS, VAL, PRE or
HOLD series was opened. It does arithmetic on numbers already reported in rounds 3-15, so it needs no hypotheses
file. Every input row cites its source. It is not a candidate search and cannot produce a candidate.

## Answer
- **The rows.** 58 rows, about 45 distinct effects (13 rows are variants of another row). Each is an effect that
  rounds 3-15 reported as real at mid, on the same side, with IS t >= ~2 and VAL > 0. Excluded: gotobi and the Tokyo
  fix (C3's mechanism), and known artefacts. The excluded list is in section 1.
- **At IC's costs (a), no row reaches LIVE-like power (3) on the VAL size.**
  - 15 rows meet the DEMO-like numbers (IS net t >= 2, VAL net > 0).
  - The best VAL-size powers are J5c AUDUSD 2.83 (its HOLD failed), the Friday ECB pre-fix slot 2.09 and E1 1.87.
- **The bar change (e), judging IS at IC's VAL-era cost, adds no LIVE-like row.**
  - DEMO-like rows go from 15 to 18. The three added are SGE dip mornings, gold before UK holidays (decaying) and the
    USTEC LETF close (the 2020 tail).
  - The index effects that motivated the question still fail the IS gate. Their IS mid is small: US30 post-close
    0.58 bp, US500 open fade 0.99 bp, AUS200 open 1.55 bp with +1 minute < 0. At VAL cost their IS t is only
    1.1 / 1.2 / 0.5.
- **Lower costs do create LIVE-like rows, on the VAL size.**

  | scenario | LIVE-like rows (VAL-size power) |
  |---|---|
  | (b) no FX/metals commission | the ECB pre-fix slot every day (3.43), its Friday subset (3.05), J5c (5.06) |
  | (c) half the spread | J5c (3.15); AUS200 open drop (4.47, but not executable: +1 minute < 0 every year) |
  | (d) an institutional venue (EURUSD 0.2 bp, AUD/NZD 0.3-0.4 bp all-in) | the Sydney V: pre-leg AUD+NZD all days (5.54), J5c (4.58), post-leg (3.29) |
  | (d2) a retail-accessible venue (about 0.2 bp per side commission) | Sydney pre-leg (4.77), J5c (3.65) |

- **Decay removes all of them.** Four non-gotobi flow candidates reached HOLD. They kept 0.18-0.81 of their VAL mid:
  E1 0.65, gold settlement big days 0.81, J5c 0.31, month-end I 0.18. C3 kept about 0.9.
  - At a venue cost, LIVE needs the Sydney pre-leg to keep >= 0.67-0.72 of its VAL mid, and the ECB pre-fix slot
    >= 1.03 at 0.2 bp (0.86 at zero cost).
  - At E1's retention (0.65), the best row is the Sydney pre-leg at (d), 2.88, and J5c under (b), 3.07.
  - At J5c's own retention (0.31), no row exceeds 1.13 under any cost.
- **Rare effects are capped by count, not cost.** These are gold settlement big days, month-end I, H3 FOMC US30,
  US30 after 08:30 data, the Deribit Friday BTC fade and EURJPY at quarter-end. Their power stays at 0.6-2.0 even at
  zero cost (gold big days: 1.29 at IC, 1.66 with no commission).
- **Data decisions do not change costs.** So no data decision alone can create a LIVE row: at IC's costs every row
  stays below power 3 whatever it confirms. The data decisions confirm or kill mechanisms:
  - Dukascopy M1 for AUD/NZD gives a 2004-15 test of the Sydney V (mid t about 18).
  - Dukascopy M1 for XAU/XAG gives the LBMA silver drop (t about 15), gold settlement big days (mid t about 3.5 in the
    leveraged-ETF years, with 2004-08 as a no-ETF placebo) and an SGE placebo (the auction starts in 2016-04).
  - New data after 2026-09-24 would confirm a venue-cost Sydney rule within 4-6 months at VAL size (16-19 at 0.65x).
    At IC's cost, E1 needs 37 months and gold big days 78.
- **Ranking.**
  - Highest expected value: a cost structure without IC's 0.6 bp commission floor, tested first on the Sydney V
    (with the free Dukascopy AUD/NZD M1 and the new data as its checks). It is the only decision that can produce a
    LIVE row at all, and only if the Sydney V stops decaying.
  - Low: the bar change, half spreads at IC, softs, EM and EUR crosses at IC, LETF AUM, SGE premium, ECB volumes and
    index PRE.

## Method
- **Inputs per row:** the mid in bp per trade on the side the source used, its t, the cost and the trades a year.
  - SE = mid / t, and sd = SE x sqrt(n).
  - Where the source t is per day (the two-leg Sydney cells) or per event (rule I), sd and power are per cluster.
  - "est" marks an input that was not reported:
    - USDJPY and EURJPY midday t comes from the frontier sd (1 h sd x sqrt 2; round 10 STREAM_D_outputs.md);
    - costs F22, F27, F28, F29, I10, I11 and I12 come from the symbol's typical cost.
- **Net and power:**
  - net t at a cost c = (mid - c) / SE;
  - power on an era's size = net t x sqrt(1.73 / years) = per-trade net Sharpe x sqrt(1.73 x trades a year), as in
    rounds 6-15;
  - the VAL column is the expected HOLD t at the VAL size.
- **Cost scenarios.** Each applies to IS and VAL unless stated.
  - **(a)** IC as reported: IS at the IS cost, VAL at the VAL cost.
  - **(b)** (a) minus the 0.6 bp commission for FX and metals.
    - This is not an IC product. IC's account type without commission widens the spread instead (to verify with
      IC).
    - It models a venue with IC's raw spread and no commission.
  - **(c)** Half the spread with the commission kept: for FX and metals 0.6 + (cost - 0.6) / 2; for indices,
    energies and crypto, cost / 2.
  - **(d)** A stated all-in round trip, the same in both eras, capped at IC's VAL cost. It is optimistic: one futures
    tick, or an institutional FX ECN, with no slippage at fix minutes.

    | symbol | round trip, bp |
    |---|---|
    | EURUSD, USDJPY | 0.20 |
    | USDCHF, AUDUSD, EURJPY, GBPUSD, FX baskets | 0.25-0.35 |
    | AUD+NZD | 0.40 |
    | GBPJPY | 0.45 |
    | USDCNH | 0.60 |
    | XAU | 0.60 (one COMEX tick at ~$2,000 + fees; ~0.35 at today's price) |
    | XAG | 2.0 (one tick) |
    | US30 | 0.30 |
    | USTEC | 0.25 |
    | US500 | 0.55 (IC VAL 0.49 binds) |
    | DE40 | 0.4 |
    | HK50 | 0.6 |
    | UK100 | 0.7 |
    | AUS200 | 1.5 |
    | JP225 | 1.7 (mini) |
    | XTI | 1.5 |
    | BTC | 3.0 |
    | multi-leg PCA book | 1.0 |

  - **(d2)** A retail-accessible lower-cost venue: about 0.2 bp per side commission plus 0.05-0.1 bp spread. EURUSD
    and USDJPY 0.45, other majors and AUD/NZD 0.55, crosses 0.70, CNH 0.8, metals and indices as (d).
  - **(e)** IC's VAL-era cost applied to IS as well (VAL unchanged). **This is a bar change the user has not made;
    report only.**
- **Flags.** These are numbers-only screens. They ignore the random-entry control, spread x1.5, +1 minute, years > 0
  and how the row was selected (many rows are post hoc).
  - **L**: IS net t >= 2.5, VAL net t >= 1.5, VAL-size power >= 3.
  - **D**: IS net t >= 2.0 and VAL net > 0.
- **Retention.** This is the share of the VAL mid that the next era must keep for power 3 at cost c:
  (c + 3 sd / sqrt(1.73 n)) / VAL mid.
  - Observed HOLD / VAL mid of the flow rules registered so far:
    - E1: 1.28 / 1.97 = 0.65;
    - L4-G-d: 2.54 / 3.14 = 0.81;
    - J5c: 0.48 / 1.53 = 0.31;
    - I: about 0.43 / 2.34 = 0.18;
    - M1 (in R): 0.044 / 0.228 = 0.19.
  - C3 (gotobi), for reference: 0.042 / 0.048 = 0.88.
  - These are single draws with wide error bars. The median non-gotobi retention is about 0.3, the best 0.8.

## 1. Effects real at mid in IS and VAL
Side: PRE = fixed on 2004-15 before IS; lit = from the literature / mechanism; decl = declared rule or selector
before the numbers; scan = found by a scan, later confirmed; post = found after looking (VAL often in view).
"dec" = VAL/IS < 0.5 (decaying).

| id | effect | source | n/yr | IS mid (t) | VAL mid (t) | cost IS / VAL | sd IS / VAL | VAL/IS | side | note |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | E1 EURUSD short 11:00-13:00 London, every weekday | r13 STREAM_M 'Candidate evaluations' | 254 | +1.80 (5.1) | +1.97 (3.6) | 0.63 / 0.62 | 13.8 / 15.1 | 1.09 | PRE |  |
| F2 | EURUSD short 09:00-13:00 London (E1, 4 h) | r14 STREAM_Q legs table | 254 | +2.46 (4.8) | +2.48 (3.1) | 0.64 / 0.63 | 20.0 / 22.1 | 1.01 | PRE |  |
| F3 | E1 on top-tercile overnight USD-rise days (USD-TOP) | r14 STREAM_R results table | 84 | +3.10 (4.8) | +3.05 (3.0) | 0.63 / 0.62 | 14.5 / 16.1 | 0.98 | decl | selector family p 0.08 |
| F4 | ECB pre-fix slot EURUSD short 12:45-13:00 London, every weekday | r14 STREAM_R (O2 X-HOMEHOL); r13 STREAM_M | 252 | +1.11 (6.0) | +1.14 (4.6) | 0.67 / 0.62 | 7.2 / 6.8 | 1.03 | PRE | inside E1 |
| F5 | ECB pre-fix slot, Fridays, EURUSD short 12:50-13:00 London | r15 STREAM_S post hoc leads | 50 | +1.76 (6.0) | +1.95 (4.1) | 0.63 / 0.64 | 5.1 / 5.8 | 1.11 | post | inside E1 |
| F6 | ECB fix rebound, EURUSD long 13:00-13:15 London (14:00-14:15 CET) | r10 STREAM_E; r12 STREAM_J R0 | 251 | +0.73 (5.3) | +0.85 (4.1) | 0.65 / 0.64 | 5.3 / 5.7 | 1.16 | post | registered side was the opposite |
| F7 | USDCHF long 10:00-12:00 UTC (E2) | r13 STREAM_M 'Candidate evaluations' | 254 | +1.02 (3.0) | +1.08 (2.2) | 0.94 / 0.89 | 13.1 / 13.6 | 1.06 | PRE |  |
| F8 | USDCHF midday after a top-tercile morning rise (O4 MORN-TOP) | r14 STREAM_R | 82 | +1.97 (3.2) | +1.58 (1.8) | 0.93 / 0.87 | 13.7 / 13.8 | 0.80 | decl |  |
| F9 | USDCHF short 13:00-13:30 UTC (ECB-fix rebound) | r13 STREAM_M families table | 254 | +0.69 (3.5) | +0.58 (1.6) | 1.31 / 1.30 | 7.7 / 10.0 | 0.84 | PRE |  |
| F10 | USDJPY long 11:00-13:00 London | r13 STREAM_M 'same window on every symbol', break-even table | 254 | +0.88 (2.3 est) | +0.95 (1.8 est) | 0.77 / 0.73 | 14.8 / 14.8 est | 1.08 | PRE | t not reported |
| F11 | EURJPY short 11:00-13:00 London | r13 STREAM_M 'same window on every symbol' | 254 | +0.92 (2.3 est) | +1.01 (1.8 est) | 0.86 / 0.89 | 15.8 / 15.8 est | 1.10 | PRE | t not reported; = E1 minus F10 |
| F12 | GBPJPY long 17:30-21:30 London (G1) | r13 STREAM_M 'Candidate evaluations' | 254 | +1.65 (3.3) | +1.43 (1.9) | 1.24 / 1.09 | 19.5 / 20.3 | 0.87 | PRE |  |
| F13 | GBPJPY long 02:45-06:45 Sydney | r14 STREAM_Q legs table | 203 | +2.12 (3.1) | +1.72 (1.9) | 1.18 / 1.09 | 23.9 / 22.3 | 0.81 | PRE |  |
| F14 | EURJPY long 16:00-20:00 London | r14 STREAM_Q legs table | 254 | +1.76 (3.6) | +1.06 (1.4) | 0.86 / 0.89 | 19.1 / 20.9 | 0.60 | PRE |  |
| F15 | EURJPY short 05:00-07:00 London, last weekday of a quarter | r14 STREAM_Q legs table | 3 | +8.65 (3.1) | +9.55 (1.7) | 1.07 / 1.08 | 11.8 / 16.9 | 1.10 | PRE |  |
| F16 | GBPUSD long 15:00-16:00 London, last weekday (WM/R month-end) | r14 STREAM_Q legs; r3 F1 | 11 | +9.71 (2.7) | +1.87 (0.4) | 0.87 / 0.78 | 29.2 / 26.9 | 0.19 dec | PRE |  |
| F17 | Month-end post-fix USD reversal after a large US month (I), 3 USD pairs | r12 STREAM_I (t = net, per event) | 7 | +7.46 (4.2) | +2.34 (1.2) | 0.69 / 0.66 | 11.6 / 9.2 | 0.31 dec | post | per trade, t per event; HOLD net -0.23 |
| F18 | GBPJPY long 10:28-10:31 New York, last weekday | r15 STREAM_S post hoc leads | 12 | +3.51 (6.2) | +1.58 (2.6) | 1.04 / 1.11 | 4.8 / 3.6 | 0.45 dec | post |  |
| F19 | Sydney pre-leg: short AUD+NZD 09:45-10:00 Sydney, all days | r4; r10 STREAM_E; r12 STREAM_J R0 + break-even | 254 | +1.65 (13.1) | +1.48 (10.0) | 1.76 / 2.43 | 4.9 / 4.1 | 0.90 | scan | t per day (2 legs) |
| F20 | J5c: short AUDUSD 09:45-10:00 Sydney outside IC's rollover hour | r12 STREAM_J J5c | 181 | +1.54 (8.9) | +1.53 (7.5) | 1.10 / 0.77 | 5.7 / 4.8 | 0.99 | post | HOLD net -0.25 |
| F21 | Sydney post-leg: long AUD+NZD 10:00-10:15 Sydney | r12 STREAM_J R0 + break-even | 254 | +1.28 (7.6) | +1.44 (6.0) | 1.47 / 1.73 | 6.6 / 6.6 | 1.12 | scan | t per day (2 legs) |
| F22 | USDJPY long 16:00-17:00 New York (hour after the cash close) | r4 benchmark scan; r10 E footnote | 254 | +0.80 (5.9) | +1.00 (3.8) | 0.75 / 0.70 est | 5.3 / 7.3 | 1.25 | scan |  |
| F23 | USDCNH long 01:30-08:30 UTC (CNH home hours) | r7 B; r12 STREAM_L (L7) | 259 | +1.17 (2.6) | +2.03 (2.5) | 1.04 / 1.01 | 17.7 / 22.6 | 1.74 | lit | bid-only bars, published spread |
| F24 | USDJPY long into the TWD close (08:00 Beijing) | r10 A (A4) | 250 | +0.28 (2.1) | +0.95 (4.0) | 0.74 / 0.70 | 5.2 / 6.6 | 3.39 | decl | best of A4 family |
| F25 | Currency-strength reversal, 4 h signal, 8 h hold (R3) | r8 report R table | 250 | +1.68 (2.7) | +1.94 (2.2) | 1.40 / 1.30 | 24.1 / 24.1 | 1.15 | lit |  |
| F26 | PCA residual s-score reversal, 10 FX + 3 metals (R2) | r8 report R table | 250 | +2.28 (2.4) | +2.44 (1.8) | 3.40 / 4.10 | 36.8 / 37.1 | 1.07 | lit | multi-leg; venue 1.0 assumed |
| F27 | High-yielder long into the Wednesday rollover, 12:00-16:55 NY (W1) | r3 W1 row | 52 | +2.20 (3.1) | +1.40 (1.6) | 1.20 / 1.20 est | 12.5 / 10.9 | 0.64 | lit | 'about 1 bp net' |
| F28 | EURUSD reversal 240 min after a 6-sd 15-min USTEC shock (S1) | r8 report S table (net t) | 15 | +4.57 (3.5) | +3.00 (1.9) | 0.70 / 0.70 est | 12.3 / 10.7 | 0.66 | post | best cell of a grid |
| F29 | USDJPY into short-dated Treasury auctions (concession) | r4 external-data table | 48 | +4.50 (3.3) | +1.00 (0.4) | 0.75 / 0.70 est | 23.1 / 30.0 | 0.22 dec | lit |  |
| M1 | SGE auction: XAU long 02:15-02:23 UTC | r10 A/E; r12 STREAM_J break-even | 225 | +0.92 (7.7) | +0.70 (4.3) | 1.59 / 1.04 | 4.4 / 4.2 | 0.76 | post |  |
| M2 | SGE auction on dip mornings (L1-DIP-q) | r12 STREAM_L | 42 | +1.84 (6.0) | +1.36 (3.2) | 1.65 / 1.04 | 4.9 / 4.8 | 0.74 | decl |  |
| M3 | XAU long 01:00-03:30 UTC, Chinese session (A6) | r10 A | 240 | +2.02 (2.8) | +1.70 (1.9) | 1.65 / 1.06 | 27.4 / 24.7 | 0.84 | post |  |
| M4 | XAU fade the 30 min before the Chinese close, 07:00 UTC (A2) | r10 A | 240 | +1.21 (3.9) | +0.86 (1.8) | 1.52 / 1.03 | 11.9 / 12.8 | 0.71 | decl |  |
| M5 | L4-G-d: XAU follows the day into the COMEX settlement, top-decile days | r12 STREAM_L; PREREG_L | 25 | +4.74 (4.3) | +3.14 (2.5) | 1.43 / 1.03 | 13.5 / 10.7 | 0.66 | decl | DEMO candidate |
| M6 | L4-G-q: same, top quintile | r12 STREAM_L | 48 | +2.34 (3.3) | +1.89 (2.4) | 1.40 / 1.00 | 12.0 / 9.4 | 0.81 | decl |  |
| M7 | XAU follow the day 5 min into the settlement, all days | r6 S1 (true commission) | 250 | +0.41 (2.4) | +0.41 (2.1) | 1.30 / 1.00 | 6.6 / 5.3 | 1.00 | lit |  |
| M8 | XAU short 14:59-15:01 London (LBMA PM auction) | r15 STREAM_V metals | 250 | +1.09 (5.2) | +0.94 (2.7) | 1.45 / 1.02 | 8.1 / 9.5 | 0.86 | post |  |
| M9 | XAG short 11:59-12:01 London (LBMA silver auction) | r15 STREAM_V metals | 250 | +2.68 (8.3) | +2.72 (9.1) | 4.19 / 4.60 | 12.5 / 8.2 | 1.01 | post |  |
| M10 | XAU short 10:29-10:31 London (LBMA AM auction) | r15 STREAM_V metals | 250 | +0.88 (8.2) | +0.24 (1.9) | 1.44 / 0.99 | 4.2 / 3.5 | 0.27 dec | post |  |
| M11 | XAU fade the COMEX floor open 08:20-08:30 ET (V5) | r15 STREAM_V | 250 | +1.01 (3.3) | +0.85 (2.1) | 1.74 / 1.19 | 11.9 / 11.1 | 0.84 | decl |  |
| M12 | XAU long 02:00-06:00 UTC on the weekday before a UK holiday | r13 STREAM_M | 4.3 | +6.73 (2.5) | +1.46 (0.3) | 1.89 / 1.04 | 13.6 / 18.7 | 0.22 dec | PRE |  |
| I1 | USTEC follow the MOC imbalance 15:50-16:00 ET | r11 H2; r12 STREAM_J | 246 | +1.53 (2.7) | +1.00 (1.5) | 1.67 / 0.65 | 21.7 / 17.6 | 0.65 | decl | bar-start labels |
| I2 | USTEC follow the day 15:52-16:00 ET, top quintile (L6-LETF) | r12 STREAM_L; r13 STREAM_P | 48 | +3.62 (2.5) | +3.79 (2.2) | 1.68 / 0.68 | 24.6 / 20.7 | 1.05 | decl | IS = 2020 tail (r13 P) |
| I3 | US30 fade 16:04-16:14 ET (post-close reversal) | r15 STREAM_V V3 | 250 | +0.58 (2.4) | +1.05 (4.2) | 0.93 / 0.31 | 9.4 / 6.8 | 1.81 | decl |  |
| I4 | US500 fade 09:41-09:51 ET (opening overreaction) | r15 STREAM_V V1 | 250 | +0.99 (2.3) | +1.68 (2.3) | 1.59 / 0.49 | 16.7 / 20.0 | 1.70 | decl |  |
| I5 | UK100 fade 16:34-16:39 London (after the closing auction) | r15 STREAM_V V3 | 250 | +1.65 (6.5) | +1.17 (3.9) | 3.04 / 2.03 | 9.8 / 8.2 | 0.71 | decl |  |
| I6 | AUS200 fade 16:00-16:12 over 16:13-16:30 Sydney | r11 H2; r12 STREAM_J | 218 | +0.82 (2.2) | +0.71 (2.7) | 2.18 / 1.58 | 13.7 / 6.7 | 0.87 | decl |  |
| I7 | AUS200 short 10:10-10:11 Sydney (ASX open drop) | r15 STREAM_V post hoc | 250 | +1.55 (7.2) | +2.05 (9.1) | 2.02 / 1.45 | 8.3 / 6.2 | 1.32 | post | +1 min net < 0 every year |
| I8 | HK50 fade the gap 09:30-09:31 HKT | r15 STREAM_V V1 | 250 | +2.11 (6.3) | +0.33 (0.4) | 3.29 / 2.81 | 13.0 / 22.6 | 0.16 dec | decl |  |
| I9 | JP225 follow the day 15:00-15:15 Tokyo (after the cash close) | r13 STREAM_P | 250 | +3.39 (5.6) | +0.59 (1.0) | 3.14 / 1.87 | 23.4 / 16.2 | 0.17 dec | post |  |
| I10 | DE40 follow the day 10 min into the Xetra close, all days | r13 STREAM_P (all-days column) | 250 | +1.16 (3.1) | +1.06 (2.7) | 1.20 / 0.53 est | 14.5 / 10.8 | 0.91 | decl | cost of the top-decile row |
| I11 | US30 short 15:45-16:00 ET on FOMC days (H3) | r11 H3 (net t) | 8 | +7.60 (3.1) | +9.80 (1.5) | 0.90 / 0.30 est | 17.1 / 31.4 | 1.29 | post |  |
| I12 | US30 continue 30 min after its 08:30 NY data move (S4b mirror) | r8 report S table (net t) | 13 | +13.90 (2.9) | +5.70 (1.9) | 0.90 / 0.30 est | 42.4 / 18.4 | 0.41 dec | post |  |
| I13 | US500 night premium (close -> open), long | r3 risk-premia table | 250 | +4.90 (3.1) | +1.00 (0.4) | 3.00 / 4.20 | 61.2 / 68.5 | 0.20 dec | lit | cost = spread + long swap |
| E1 | XTI follow the day 15 min into the NYMEX settlement, all days | r6 S1 | 250 | +5.58 (2.0) | +1.81 (1.4) | 5.60 / 3.50 | 88.2 / 35.4 | 0.32 dec | lit |  |
| E2 | XTI fade 14:30-14:31 ET (WTI settlement) | r15 STREAM_V V6 | 250 | +1.65 (2.4) | +0.70 (2.1) | 7.54 / 3.30 | 21.7 / 9.1 | 0.42 dec | decl |  |
| C1 | BTC follow the day 23:30-24:00 UTC | r3; r12 STREAM_J | 250 | +8.80 (4.1) | +2.60 (1.9) | 13.40 / 3.20 | 71.2 / 37.5 | 0.30 dec | lit |  |
| C2 | BTC fade 07-08 UTC move over 08:01-09:00 on Deribit-expiry Fridays (K4) | r12 STREAM_K | 52 | +20.58 (2.3) | +11.23 (3.1) | 11.56 / 3.29 | 126.8 / 44.8 | 0.55 | lit |  |

### Deduplication (kept row first, other versions after)
- **ECB V / E1 (F1-F6).**
  - Kept: E1 from round 13 M (registered, HOLD known); the pre-fix slot from round 14 R; the Friday slot from round 15
    S; the post-fix rebound from round 12 J.
  - Other versions:
    - round 3, "USD into the ECB fix": EURUSD +1.1 bp (t 2.9) / +1.2 (t 2.1);
    - round 4 scan, 15 min into the fix: +0.7 (t 5.5) / +0.8 (t 4.2);
    - round 10 E, EUR rises into the fix;
    - round 12 L3, which reverses at month-end;
    - round 14 Q legs and R selectors;
    - round 15 S, the V moved 16 minutes at the end of 2015.
  - The rows overlap in time on one symbol: they are not independent legs.
- **Sydney V (F19-F21).**
  - Kept: round 12 J (the R0 table, the break-even table, J5c).
  - Other versions:
    - round 4 scan;
    - round 6 S4, passive limits;
    - round 10 E, volatile days: +2.52 (t 5.9) / +2.12 (t 7.2) against 2.0-2.3 bp;
    - round 10 C5;
    - round 12 L2, Mondays 1.7x in VAL;
    - round 15 V8.
- **SGE (M1-M3).**
  - Kept: round 12 J / L.
  - Other versions: round 10 A / E; round 12 J3a, 01:00-02:23.
- **Gold settlement (M5-M7).**
  - Kept: round 12 L and PREREG_L.
  - Other versions: round 6 S1, big days +2.31 (t 3.6) / +1.00 (t 1.5); round 12 J SETT; round 13 P (reproduced; the
    rule does not travel to other symbols).
- **LBMA (M8-M10).**
  - Kept: round 15 V.
  - Other versions: round 6 noted silver into the 12:00 fix at -2.8 bp, under its spread; round 3, gold ETF creations
    at the PM fix: nothing.
- **Month-end WM/R (F16, F17).**
  - Kept: the round 14 Q GBPUSD leg; round 12 I.
  - Other versions:
    - round 3 F1: pooled mid +2.4 (t 3.0) / +2.5 (t 2.2), engine VAL R +0.005;
    - round 15 S: EURUSD 15:45-15:55 month-end, PRE +2.39, IS +1.61, VAL -0.84.
  - Round 3 M1 (month-end value-date USD) is in R units and not in the table:
    - IS t 3.2 / VAL 2.6 per day; VAL-size power at IC 0.76 x 2.6 = 1.97 per day cluster;
    - HOLD t 0.7, PRE t 0.64, retention 0.19;
    - a ~1 bp cost against a ~6 bp edge, so no cost scenario moves it more than ~15 %.
- **USTEC close (I1, I2).** Round 4 (Baltussen, big days +10 bp, t 1.2), round 11 H2, round 12 J / L6, round 13 P
  (the big-day effect is the 2020 tail).
- **Others.** AUS200 close (I6): round 11 H2, round 12 J / L5. USDCNH (F23): round 7 B, round 12 L7 (dividend season
  66 a year, +2.78 (t 3.1) / +2.98 (t 2.2), net t 1.93 / 1.48). BTC (C1): round 3, round 12 J. XTI (E1): round 6 S1,
  round 13 P (top decile ex-2020 +12.8, t 2.0).

### Excluded on purpose
- **C3's mechanism.** Gotobi and Tokyo-fix cells: round 4's USDJPY into the Tokyo fix, and the Tokyo-adjacent
  families of round 13 M and round 15 S.
- **Artefacts:**
  - A7 gold on Chinese holidays (failed its PRE check, t -3.3);
  - W1 after the rollover, and the weekend metals move (quote effects);
  - US30 on the 15th (month composition);
  - index big-day scale-ups (2020);
  - weekly oil -> US500 (a fill artefact).
- **Too small for any venue:**
  - lead-lag after 1 minute: 0.01-0.2 bp per sd;
  - dollar catch-up: +0.1 bp gross per trade;
  - adaptive periodicity: 0.02-0.3 bp per slot;
  - tick lead-lag USTEC -> AUDUSD: +0.25-0.41 bp against a 0.3-0.55 bp venue;
  - JP225 -> DE40 in Asian hours: ~0.65 bp gross in VAL.
- **Too rare:**
  - the dollar's fall over the last 3 days of December (-74 bp IS, t -4.25; -42 VAL; one event a year);
  - USDJPY into 30 September (n 6 / 3).
  - EURJPY at quarter-end is kept as F15 to show the count limit.

## 2. Net Sharpe and power under each cost structure
Cells: VAL-size per-trade net Sharpe / VAL-size power / IS net t at that scenario's IS cost, then the flag. Column (e)
gives the IS net t and the IS-size power with IC's VAL cost applied to IS.

| id | (a) IC as reported | (b) no FX/metal commission | (c) half spread | (d) venue @cost | (d2) retail venue @cost | (e) IC VAL cost on IS: IS t / IS power |
|---|---|---|---|---|---|---|
| F1 | 0.089 / 1.87 / 3.3 D | 0.129 / 2.70 / 5.0 D | 0.090 / 1.88 / 3.3 D | 0.117 / 2.45 / 4.5 D @0.20 | 0.100 / 2.10 / 3.8 D @0.45 | 3.3 / 1.79 D |
| F2 | 0.084 / 1.76 / 3.6 D | 0.111 / 2.33 / 4.7 D | 0.084 / 1.77 / 3.6 D | 0.103 / 2.16 / 4.4 D @0.20 | 0.092 / 1.93 / 3.9 D @0.45 | 3.6 / 1.92 D |
| F3 | 0.151 / 1.82 / 3.8 D | 0.188 / 2.26 / 4.8 D | 0.151 / 1.82 / 3.8 D | 0.177 / 2.13 / 4.5 D @0.20 | 0.161 / 1.94 / 4.1 D @0.45 | 3.8 / 2.06 D |
| F4 | 0.076 / 1.59 / 2.4 D | 0.164 / 3.43 / 5.6 L | 0.078 / 1.62 / 2.6 D | 0.138 / 2.88 / 4.9 D @0.20 | 0.101 / 2.11 / 3.6 D @0.45 | 2.6 / 1.42 D |
| F5 | 0.225 / 2.09 / 3.8 D | 0.328 / 3.05 / 5.8 L | 0.228 / 2.12 / 3.9 D | 0.300 / 2.79 / 5.3 D @0.20 | 0.258 / 2.39 / 4.4 D @0.45 | 3.8 / 2.03 D |
| F6 | 0.037 / 0.77 / 0.6  | 0.142 / 2.97 / 4.9 D | 0.040 / 0.84 / 0.8  | 0.114 / 2.38 / 3.8 D @0.20 | 0.070 / 1.47 / 2.0 D @0.45 | 0.7 / 0.35  |
| F7 | 0.014 / 0.29 / 0.2  | 0.058 / 1.22 / 2.0 D | 0.025 / 0.52 / 0.7  | 0.057 / 1.20 / 2.1 D @0.30 | 0.039 / 0.82 / 1.4  @0.55 | 0.4 / 0.21  |
| F8 | 0.052 / 0.61 / 1.7  | 0.095 / 1.13 / 2.7 D | 0.061 / 0.73 / 2.0  | 0.093 / 1.11 / 2.7 D @0.30 | 0.075 / 0.89 / 2.3 D @0.55 | 1.8 / 0.96  |
| F9 | -0.072 / -1.51 / -3.1  | -0.012 / -0.25 / -0.1  | -0.037 / -0.78 / -1.3  | 0.028 / 0.59 / 2.0  @0.30 | 0.003 / 0.06 / 0.7  @0.55 | -3.1 / -1.66  |
| F10 | 0.015 / 0.31 / 0.3  | 0.055 / 1.16 / 1.9  | 0.019 / 0.40 / 0.5  | 0.051 / 1.06 / 1.8  @0.20 | 0.034 / 0.71 / 1.1  @0.45 | 0.4 / 0.21  |
| F11 | 0.008 / 0.16 / 0.1  | 0.045 / 0.95 / 1.6  | 0.017 / 0.35 / 0.5  | 0.045 / 0.94 / 1.5  @0.30 | 0.020 / 0.41 / 0.5  @0.70 | 0.1 / 0.04  |
| F12 | 0.017 / 0.35 / 0.8  | 0.046 / 0.97 / 2.0 D | 0.029 / 0.60 / 1.5  | 0.048 / 1.01 / 2.4 D @0.45 | 0.036 / 0.75 / 1.9  @0.70 | 1.1 / 0.60  |
| F13 | 0.028 / 0.53 / 1.4  | 0.055 / 1.03 / 2.3 D | 0.039 / 0.73 / 1.8  | 0.057 / 1.07 / 2.4 D @0.45 | 0.046 / 0.86 / 2.1 D @0.70 | 1.5 / 0.81  |
| F14 | 0.008 / 0.17 / 1.8  | 0.037 / 0.77 / 3.1 D | 0.015 / 0.32 / 2.1 D | 0.036 / 0.76 / 3.0 D @0.30 | 0.017 / 0.36 / 2.2 D @0.70 | 1.8 / 0.96  |
| F15 | 0.503 / 1.14 / 2.7 D | 0.538 / 1.23 / 2.9 D | 0.517 / 1.18 / 2.8 D | 0.549 / 1.25 / 3.0 D @0.30 | 0.525 / 1.20 / 2.8 D @0.70 | 2.7 / 1.46 D |
| F16 | 0.041 / 0.18 / 2.5 D | 0.063 / 0.27 / 2.6 D | 0.044 / 0.19 / 2.5 D | 0.058 / 0.26 / 2.6 D @0.30 | 0.049 / 0.21 / 2.5 D @0.55 | 2.5 / 1.33 D |
| F17 | 0.183 / 0.64 / 3.8 D | 0.249 / 0.87 / 4.1 D | 0.187 / 0.65 / 3.8 D | 0.228 / 0.79 / 4.0 D @0.25 | 0.195 / 0.68 / 3.9 D @0.55 | 3.8 / 2.04 D |
| F18 | 0.129 / 0.59 / 4.3 D | 0.293 / 1.34 / 5.4 D | 0.199 / 0.91 / 4.7 D | 0.310 / 1.41 / 5.4 D @0.45 | 0.241 / 1.10 / 4.9 D @0.70 | 4.2 / 2.27 D |
| F19 | -0.233 / -4.87 / -0.9  | -0.086 / -1.80 / 3.9  | -0.009 / -0.18 / 3.7  | 0.264 / 5.54 / 9.9 L @0.40 | 0.228 / 4.77 / 8.7 L @0.55 | -6.2 / -3.33  |
| F20 | 0.160 / 2.83 / 2.5 D | 0.286 / 5.06 / 6.0 L | 0.178 / 3.15 / 4.0 L | 0.259 / 4.58 / 7.2 L @0.30 | 0.206 / 3.65 / 5.7 L @0.55 | 4.5 / 2.39 D |
| F21 | -0.044 / -0.92 / -1.1  | 0.047 / 0.98 / 2.4 D | 0.042 / 0.87 / 1.5  | 0.157 / 3.29 / 5.2 L @0.40 | 0.134 / 2.82 / 4.3 D @0.55 | -2.7 / -1.43  |
| F22 | 0.041 / 0.87 / 0.4  | 0.124 / 2.60 / 4.8 D | 0.048 / 1.01 / 0.9  | 0.110 / 2.31 / 4.4 D @0.20 | 0.076 / 1.59 / 2.6 D @0.45 | 0.7 / 0.40  |
| F23 | 0.045 / 0.95 / 0.3  | 0.072 / 1.52 / 1.6  | 0.054 / 1.15 / 0.8  | 0.063 / 1.34 / 1.3  @0.60 | 0.054 / 1.15 / 0.8  @0.80 | 0.4 / 0.19  |
| F24 | 0.038 / 0.79 / -3.4  | 0.129 / 2.68 / 1.1  | 0.046 / 0.95 / -2.9  | 0.114 / 2.37 / 0.6  @0.20 | 0.076 / 1.58 / -1.3  @0.45 | -3.1 / -1.69  |
| F25 | 0.027 / 0.55 / 0.5  | 0.051 / 1.07 / 1.4  | 0.041 / 0.85 / 1.1  | 0.066 / 1.37 / 2.1 D @0.35 | 0.058 / 1.20 / 1.8  @0.55 | 0.6 / 0.33  |
| F26 | -0.045 / -0.93 / -1.2  | -0.029 / -0.59 / -0.5  | 0.002 / 0.05 / 0.3  | 0.039 / 0.81 / 1.3  @1.00 | 0.023 / 0.47 / 0.7  @1.60 | -1.9 / -1.03  |
| F27 | 0.018 / 0.17 / 1.4  | 0.073 / 0.69 / 2.3 D | 0.046 / 0.43 / 1.8  | 0.096 / 0.91 / 2.6 D @0.35 | 0.078 / 0.74 / 2.3 D @0.55 | 1.4 / 0.76  |
| F28 | 0.215 / 1.10 / 3.0 D | 0.271 / 1.38 / 3.4 D | 0.220 / 1.12 / 3.0 D | 0.262 / 1.33 / 3.4 D @0.20 | 0.239 / 1.22 / 3.2 D @0.45 | 3.0 / 1.60 D |
| F29 | 0.010 / 0.09 / 2.7 D | 0.030 / 0.27 / 3.2 D | 0.012 / 0.11 / 2.8 D | 0.027 / 0.24 / 3.2 D @0.20 | 0.018 / 0.17 / 3.0 D @0.45 | 2.8 / 1.50 D |
| M1 | -0.080 / -1.59 / -5.6  | 0.061 / 1.21 / -0.6  | -0.028 / -0.56 / -1.5  | 0.024 / 0.47 / 2.7 D @0.60 | 0.024 / 0.47 / 2.7 D @0.60 | -1.0 / -0.54  |
| M2 | 0.067 / 0.57 / 0.6  | 0.193 / 1.64 / 2.6 D | 0.113 / 0.96 / 2.3 D | 0.159 / 1.36 / 4.0 D @0.60 | 0.159 / 1.36 / 4.0 D @0.60 | 2.6 / 1.40 D |
| M3 | 0.026 / 0.53 / 0.5  | 0.050 / 1.02 / 1.3  | 0.035 / 0.72 / 1.2  | 0.045 / 0.91 / 2.0  @0.60 | 0.045 / 0.91 / 2.0  @0.60 | 1.3 / 0.71  |
| M4 | -0.013 / -0.27 / -1.0  | 0.034 / 0.68 / 0.9  | 0.004 / 0.07 / 0.5  | 0.020 / 0.41 / 1.9  @0.60 | 0.020 / 0.41 / 1.9  @0.60 | 0.6 / 0.31  |
| M5 | 0.196 / 1.29 / 3.0 D | 0.252 / 1.66 / 3.6 D | 0.216 / 1.42 / 3.4 D | 0.236 / 1.55 / 3.8 D @0.60 | 0.236 / 1.55 / 3.8 D @0.60 | 3.4 / 1.81 D |
| M6 | 0.094 / 0.86 / 1.3  | 0.158 / 1.44 / 2.2 D | 0.115 / 1.05 / 1.9  | 0.137 / 1.24 / 2.5 D @0.60 | 0.137 / 1.24 / 2.5 D @0.60 | 1.9 / 1.01  |
| M7 | -0.110 / -2.29 / -5.2  | 0.002 / 0.04 / -1.7  | -0.073 / -1.52 / -3.2  | -0.036 / -0.74 / -1.1  @0.60 | -0.036 / -0.74 / -1.1  @0.60 | -3.5 / -1.85  |
| M8 | -0.008 / -0.17 / -1.7  | 0.055 / 1.13 / 1.1  | 0.014 / 0.28 / 0.3  | 0.036 / 0.74 / 2.3 D @0.60 | 0.036 / 0.74 / 2.3 D @0.60 | 0.3 / 0.18  |
| M9 | -0.230 / -4.78 / -4.7  | -0.156 / -3.25 / -2.8  | 0.015 / 0.30 / 0.9  | 0.088 / 1.83 / 2.1 D @2.00 | 0.088 / 1.83 / 2.1 D @2.00 | -5.9 / -3.19  |
| M10 | -0.217 / -4.51 / -5.2  | -0.043 / -0.90 / 0.4  | -0.160 / -3.34 / -1.3  | -0.104 / -2.16 / 2.6  @0.60 | -0.104 / -2.16 / 2.6  @0.60 | -1.0 / -0.55  |
| M11 | -0.031 / -0.64 / -2.4  | 0.023 / 0.49 / -0.4  | -0.004 / -0.08 / -0.5  | 0.023 / 0.47 / 1.3  @0.60 | 0.023 / 0.47 / 1.3  @0.60 | -0.6 / -0.32  |
| M12 | 0.022 / 0.06 / 1.8  | 0.054 / 0.15 / 2.0 D | 0.034 / 0.09 / 2.0 D | 0.046 / 0.13 / 2.3 D @0.60 | 0.046 / 0.13 / 2.3 D @0.60 | 2.1 / 1.14 D |
| I1 | 0.020 / 0.41 / -0.2  | 0.020 / 0.41 / -0.2  | 0.038 / 0.79 / 1.2  | 0.043 / 0.88 / 2.3 D @0.25 | 0.043 / 0.88 / 2.3 D @0.25 | 1.6 / 0.84  |
| I2 | 0.150 / 1.37 / 1.3  | 0.150 / 1.37 / 1.3  | 0.167 / 1.52 / 1.9  | 0.171 / 1.56 / 2.3 D @0.25 | 0.171 / 1.56 / 2.3 D @0.25 | 2.0 / 1.09 D |
| I3 | 0.108 / 2.25 / -1.4  | 0.108 / 2.25 / -1.4  | 0.131 / 2.72 / 0.5  | 0.110 / 2.28 / 1.2  @0.30 | 0.110 / 2.28 / 1.2  @0.30 | 1.1 / 0.60  |
| I4 | 0.059 / 1.24 / -1.4  | 0.059 / 1.24 / -1.4  | 0.072 / 1.49 / 0.5  | 0.059 / 1.24 / 1.2  @0.49 | 0.059 / 1.24 / 1.2  @0.49 | 1.2 / 0.62  |
| I5 | -0.105 / -2.18 / -5.5  | -0.105 / -2.18 / -5.5  | 0.019 / 0.39 / 0.5  | 0.057 / 1.19 / 3.7 D @0.70 | 0.057 / 1.19 / 3.7 D @0.70 | -1.5 / -0.80  |
| I6 | -0.130 / -2.52 / -3.6  | -0.130 / -2.52 / -3.6  | -0.012 / -0.23 / -0.7  | -0.118 / -2.29 / -1.8  @1.50 | -0.118 / -2.29 / -1.8  @1.50 | -2.0 / -1.08  |
| I7 | 0.097 / 2.02 / -2.2  | 0.097 / 2.02 / -2.2  | 0.215 / 4.47 / 2.5 L | 0.097 / 2.02 / 0.5  @1.45 | 0.097 / 2.02 / 0.5  @1.45 | 0.5 / 0.25  |
| I8 | -0.110 / -2.28 / -3.5  | -0.110 / -2.28 / -3.5  | -0.048 / -0.99 / 1.4  | -0.012 / -0.25 / 4.5  @0.60 | -0.012 / -0.25 / 4.5  @0.60 | -2.1 / -1.12  |
| I9 | -0.079 / -1.65 / 0.4  | -0.079 / -1.65 / 0.4  | -0.021 / -0.44 / 3.0  | -0.069 / -1.43 / 2.8  @1.70 | -0.069 / -1.43 / 2.8  @1.70 | 2.5 / 1.35  |
| I10 | 0.049 / 1.03 / -0.1  | 0.049 / 1.03 / -0.1  | 0.074 / 1.54 / 1.5  | 0.061 / 1.28 / 2.0 D @0.40 | 0.061 / 1.28 / 2.0 D @0.40 | 1.7 / 0.90  |
| I11 | 0.302 / 1.12 / 2.7 D | 0.302 / 1.12 / 2.7 D | 0.307 / 1.14 / 2.9 D | 0.302 / 1.12 / 3.0 D @0.30 | 0.302 / 1.12 / 3.0 D @0.30 | 3.0 / 1.59 D |
| I12 | 0.294 / 1.39 / 2.7 D | 0.294 / 1.39 / 2.7 D | 0.302 / 1.43 / 2.8 D | 0.294 / 1.39 / 2.8 D @0.30 | 0.294 / 1.39 / 2.8 D @0.30 | 2.8 / 1.52 D |
| I13 | -0.047 / -0.97 / 1.2  | -0.047 / -0.97 / 1.2  | -0.016 / -0.33 / 2.2  | -0.007 / -0.15 / 2.2  @1.50 | -0.007 / -0.15 / 2.2  @1.50 | 0.4 / 0.24  |
| E1 | -0.048 / -0.99 / -0.0  | -0.048 / -0.99 / -0.0  | 0.002 / 0.04 / 1.0  | 0.009 / 0.18 / 1.5  @1.50 | 0.009 / 0.18 / 1.5  @1.50 | 0.7 / 0.49  |
| E2 | -0.285 / -5.92 / -8.6  | -0.285 / -5.92 / -8.6  | -0.104 / -2.16 / -3.1  | -0.088 / -1.82 / 0.2  @1.50 | -0.088 / -1.82 / 0.2  @1.50 | -2.4 / -1.58  |
| C1 | -0.016 / -0.33 / -2.1  | -0.016 / -0.33 / -2.1  | 0.027 / 0.55 / 1.0  | -0.011 / -0.22 / 2.7  @3.00 | -0.011 / -0.22 / 2.7  @3.00 | 2.6 / 1.64  |
| C2 | 0.177 / 1.68 / 1.0  | 0.177 / 1.68 / 1.0  | 0.214 / 2.03 / 1.7  | 0.184 / 1.74 / 2.0  @3.00 | 0.184 / 1.74 / 2.0  @3.00 | 2.0 / 1.29  |

Flags per scenario:
- a: L 0, D 15 -> L:  | D: F1, F2, F3, F4, F5, F15, F16, F17, F18, F20, F28, F29, M5, I11, I12
- b: L 3, D 24 -> L: F4, F5, F20 | D: F1, F2, F3, F6, F7, F8, F12, F13, F14, F15, F16, F17, F18, F21, F22, F27, F28, F29, M2, M5, M6, M12, I11, I12
- c: L 2, D 17 -> L: F20, I7 | D: F1, F2, F3, F4, F5, F14, F15, F16, F17, F18, F28, F29, M2, M5, M12, I11, I12
- d: L 3, D 33 -> L: F19, F20, F21 | D: F1, F2, F3, F4, F5, F6, F7, F8, F12, F13, F14, F15, F16, F17, F18, F22, F25, F27, F28, F29, M1, M2, M5, M6, M8, M9, M12, I1, I2, I5, I10, I11, I12
- d2: L 2, D 31 -> L: F19, F20 | D: F1, F2, F3, F4, F5, F6, F8, F13, F14, F15, F16, F17, F18, F21, F22, F27, F28, F29, M1, M2, M5, M6, M8, M9, M12, I1, I2, I5, I10, I11, I12
- e: L 0, D 18 -> L:  | D: F1, F2, F3, F4, F5, F15, F16, F17, F18, F20, F28, F29, M2, M5, M12, I2, I11, I12

### What each cost decision unlocks
- **(a) IC as reported.** No row reaches 3. This is the frontier result of rounds 10-15.
- **(e) The bar change.** No row reaches L.
  - The index rows it was meant for fail on their small IS mid, not on cost:
    - US30 post-close IS t 1.1;
    - US500 open fade 1.2;
    - AUS200 open drop 0.5 (and not executable);
    - USTEC MOC 1.6.
  - It adds D to M2, M12 and I2. **Low value.**
- **(b) No commission.** The commission is the whole cost of the ECB legs: EURUSD's spread at 12:45-13:15 London is
  0.02-0.07 bp.
  - ECB pre-fix slot: 1.59 -> 3.43.
  - Rebound: 0.77 -> 2.97.
  - E1: 1.87 -> 2.70. Its 2-hour sd of 15 bp makes cost matter less.
  - J5c: 2.83 -> 5.06.
- **(c) Half the spread.** It does little in FX, because the commission stays (J5c is the exception). It matters in
  indices: US30 post-close reaches 2.72, and the AUS200 open drop 4.47 (not executable).
- **(d) Institutional venue.** The Sydney V legs are the only effects with gross power of about 5 or more and a VAL mid >= 1.4 bp.
  At 0.3-0.4 bp they all flag L. At 0.2 bp, E1 is 2.45 and the ECB slot 2.88.
- **(d2) Retail venue.**
  - Sydney pre-leg 4.77, J5c 3.65.
  - The ECB slot is 2.11 and E1 2.10. For EURUSD a retail venue at ~0.45 bp barely beats IC's 0.62.
- **Count-capped rows are insensitive to cost.** These are F15, F17, M5, I11, I12 and C2, at power 0.6-2.0 under
  every scenario.

### LIVE cost, retention and months of new data (rows with power >= 1.5 in some scenario)
- "LIVE cost" is the round trip at which the VAL size gives power 3.
- "Retention" is the share of the VAL mid the next era must keep for power 3 at the (d) cost.
- The months columns are for an expected t of 2.0 / 2.5 on new data. They are computed at VAL size (x1) and at E1's
  HOLD retention (x0.65), for IC's VAL cost (a) and the venue (d).

| id | best scenario power (VAL size) | LIVE cost at VAL size, bp | venue (d) cost | VAL-mid retention needed for power 3 at (d) | months of new data for t 2.0 / 2.5: (a) x1, (a) x0.65, (d) x1, (d) x0.65 |
|---|---|---|---|---|---|
| F1 | 2.70 (b) | -0.20 | 0.20 | 1.20 | 24/37, 99/155, 14/22, 37/58 |
| F2 | 2.33 (b) | -0.68 | 0.20 | 1.36 | 27/42, 96/149, 18/28, 46/72 |
| F3 | 2.26 (b) | -0.97 | 0.20 | 1.38 | 25/39, 80/125, 18/29, 47/73 |
| F4 | 3.43 (b) | +0.16 | 0.20 | 1.03 | 33/51, 604/944, 10/16, 30/47 |
| F5 | 3.05 (b) | +0.07 | 0.20 | 1.07 | 19/30, 83/129, 11/17, 29/45 |
| F6 | 2.97 (b) | +0.03 | 0.20 | 1.20 | 140/219, never, 15/23, 50/78 |
| F19 | 5.54 (d) | +0.90 | 0.40 | 0.67 | never, never, 3/4, 10/16 |
| F20 | 5.06 (b) | +0.72 | 0.30 | 0.72 | 10/16, 119/186, 4/6, 12/19 |
| F21 | 3.29 (d) | +0.49 | 0.40 | 0.94 | never, never, 8/12, 29/45 |
| F22 | 2.60 (b) | -0.04 | 0.20 | 1.24 | 111/173, never, 16/24, 49/77 |
| F23 | 1.52 (b) | -1.18 | 0.60 | 1.88 | 91/143, 991/1549, 46/73, 183/287 |
| F24 | 2.68 (b) | -0.00 | 0.20 | 1.21 | 133/208, never, 15/23, 48/75 |
| M2 | 1.64 (b) | -0.32 | 0.60 | 1.68 | 254/397, never, 45/70, 322/504 |
| M5 | 1.66 (b) | -1.76 | 0.60 | 1.75 | 50/78, 217/339, 34/54, 107/167 |
| M9 | 1.83 (d) | +1.54 | 2.00 | 1.17 | never, never, 25/39, never |
| I2 | 1.56 (d) | -3.02 | 0.25 | 1.86 | 44/69, 134/210, 34/53, 87/136 |
| I3 | 2.72 (c) | +0.06 | 0.30 | 1.23 | 16/26, 65/101, 16/25, 62/96 |
| I7 | 4.47 (c) | +1.16 | 1.45 | 1.14 | 20/32, never, 20/32, never |
| I10 | 1.54 (c) | -0.49 | 0.40 | 1.84 | 79/123, 878/1372, 51/80, 266/415 |
| C2 | 2.03 (c) | -2.94 | 3.00 | 1.53 | 29/46, 115/180, 27/43, 100/157 |

### Power when the next era keeps 1 / 0.65 / 0.31 of the VAL mid (rows with power >= 2 somewhere)
| id | (a) | (b) | (c) | (d) | (d2) |
|---|---|---|---|---|---|
| F1 | 1.87 / 0.91 / -0.01 | 2.70 / 1.74 / 0.82 | 1.88 / 0.93 / 0.00 | 2.45 / 1.50 / 0.57 | 2.10 / 1.15 / 0.22 |
| F2 | 1.76 / 0.93 / 0.13 | 2.33 / 1.50 / 0.70 | 1.77 / 0.95 / 0.15 | 2.16 / 1.34 / 0.54 | 1.93 / 1.10 / 0.30 |
| F3 | 1.82 / 1.02 / 0.24 | 2.26 / 1.47 / 0.69 | 1.82 / 1.03 / 0.25 | 2.13 / 1.33 / 0.56 | 1.94 / 1.14 / 0.37 |
| F4 | 1.59 / 0.37 / -0.82 | 3.43 / 2.21 / 1.02 | 1.62 / 0.40 / -0.79 | 2.88 / 1.66 / 0.47 | 2.11 / 0.89 / -0.30 |
| F5 | 2.09 / 1.00 / -0.06 | 3.05 / 1.96 / 0.90 | 2.12 / 1.03 / -0.02 | 2.79 / 1.70 / 0.65 | 2.39 / 1.31 / 0.25 |
| F6 | 0.77 / -0.32 / -1.38 | 2.97 / 1.88 / 0.82 | 0.84 / -0.25 / -1.31 | 2.38 / 1.29 / 0.23 | 1.47 / 0.38 / -0.68 |
| F19 | -4.87 / -7.53 / -10.11 | -1.80 / -4.45 / -7.04 | -0.18 / -2.84 / -5.42 | 5.54 / 2.88 / 0.30 | 4.77 / 2.11 / -0.47 |
| F20 | 2.83 / 0.84 / -1.10 | 5.06 / 3.07 / 1.13 | 3.15 / 1.15 / -0.78 | 4.58 / 2.59 / 0.65 | 3.65 / 1.65 / -0.28 |
| F21 | -0.92 / -2.51 / -4.06 | 0.98 / -0.61 / -2.16 | 0.87 / -0.72 / -2.27 | 3.29 / 1.70 / 0.15 | 2.82 / 1.22 / -0.33 |
| F22 | 0.87 / -0.14 / -1.13 | 2.60 / 1.59 / 0.61 | 1.01 / 0.00 / -0.98 | 2.31 / 1.30 / 0.32 | 1.59 / 0.58 / -0.40 |
| F24 | 0.79 / -0.26 / -1.28 | 2.68 / 1.63 / 0.61 | 0.95 / -0.10 / -1.12 | 2.37 / 1.32 / 0.30 | 1.58 / 0.53 / -0.49 |
| I3 | 2.25 / 1.13 / 0.05 | 2.25 / 1.13 / 0.05 | 2.72 / 1.60 / 0.52 | 2.28 / 1.16 / 0.08 | 2.28 / 1.16 / 0.08 |
| I7 | 2.02 / -0.40 / -2.75 | 2.02 / -0.40 / -2.75 | 4.47 / 2.05 / -0.30 | 2.02 / -0.40 / -2.75 | 2.02 / -0.40 / -2.75 |
| C2 | 1.68 / 0.85 / 0.04 | 1.68 / 0.85 / 0.04 | 2.03 / 1.20 / 0.39 | 1.74 / 0.91 / 0.10 | 1.74 / 0.91 / 0.10 |

**Reading.**
- With E1's retention (0.65), only J5c without commission (3.07) stays at 3. The Sydney pre-leg at the institutional
  venue is 2.88. With J5c's own HOLD retention (0.31), nothing exceeds 1.13.
- The Sydney V is the only family whose LIVE retention (0.67-0.72 at a venue) is below what the best registered rules
  kept in HOLD (0.65-0.81). Its own AUDUSD HOLD (0.31) is the one measurement against it.
- The ECB slot needs about 100 % retention at 0.2 bp, so it is a LIVE candidate only at zero cost and zero decay.

## 3. Data decisions: what each would test, and the expected power
Expected t uses the reported effect sizes and sd: t = (mid - cost) / sd x sqrt(events). The arithmetic is in
`data_decisions.py` and `data_decisions_out.txt` in the scratch folder.

| decision | what it would test | lead it confirms or kills | expected t / power, or months needed | value for finding LIVE |
|---|---|---|---|---|
| **Dukascopy M1 2004-15: XAU, XAG** | (1) L4-G-d gold settlement big days in PRE. Gold leveraged ETFs (UGL/GLL) exist from Dec 2008, so 2009-15 (~175 events) is the test and 2004-08 (~125) a no-ETF placebo. (2) The LBMA auction drops: the old silver fixing was at 12:00 and the gold PM fixing at 15:00 London (to verify per year). (3) An SGE placebo: the Shanghai auction began in April 2016, so 02:15-02:23 UTC should be flat in PRE | (1) L4-G-d (DEMO candidate); (2) M8, M9; (3) M1, whether SGE is a venue effect or a clock effect | (1) mid t 3.5 at VAL size; net t 1.9 (VAL size) / 3.2 (IS size) at the PRE cost convention; all 2004-15 net 2.5. (2) silver 12:00 mid t ~15; gold 15:00 ~5.7. (3) 0.7 bp detectable at t ~9 | **medium as evidence, low for LIVE**: L4 is count-capped (power 1.3-1.7 at any cost); LBMA and SGE need a venue (silver <= 2 bp still gives only 1.8). Free, quick |
| **Dukascopy M1 2004-15: AUDUSD, NZDUSD** (+ GBPUSD, USDCAD, AUDJPY) | The Sydney V over 12 more years at mid. Use the mid: the PRE cost convention reproduces IC's rollover-hour clash. The other three pairs extend round 13 M's PRE-discovery scan and round 14 Q's book from 11 to 14 symbols at M1 | F19-F21 and J5c: is the V a 21-year structure (supports the venue route) or a 2016-24 regime (kills it)? | pre-leg mid t ~18; J5c-type ~15; even at its HOLD size (+0.48 bp) t ~4.7, so PRE can tell a stable 1.5 bp from a shrinking one. Book: 11 symbols gave 12 stable, net > 0 cells in 3 families; LIVE needs 6-8 independent legs that hold their IS size, and at IC (0.83-1.14 bp for these pairs) a 1 bp leg nets ~0 | **medium**: it is the cheapest check of the only family that a cost decision lifts to LIVE; low on its own |
| **Dukascopy US30 / US500 2004-15** (availability before ~2012 to verify; if the history starts later, the t's roughly halve) | H3 (short US30 15:45-16:00 on FOMC days, 96 events), US30 after 08:30 data (156), US30 post-close reversal (if CFD quotes exist after 16:00) | I11, I12, I3 | H3 t ~3.0 (VAL size) / 3.8 (IS size); I12 ~3.7; I3 mid t ~8.5, net at 0.3 bp ~6.0 | **low**: I11 / I12 are count-capped (power 1.1-1.4); I3 reaches 2.3-2.7 at most |
| **IC symbols not yet pulled: EUR crosses** (EURGBP, EURCHF, EURAUD, EURCAD) | whether E1 and the ECB V are a EUR flow against every currency | E1 family | a leg would carry the same flow as E1 (high correlation), so the book gains little; IC crosses cost ~1-1.5 bp+ against a 1-2 bp move: power < 1 | **low** |
| **IC: Scandinavian pairs** (EURNOK, EURSEK, USDNOK, USDSEK) | a flow with a published size and side: Norges Bank's daily FX purchases or sales for the government (daily NOK amount announced monthly), and Riksbank reserve operations when announced | none yet (new class, gotobi-like structure) | no effect size in the repo, so no power; IC's cost there is several bp (to check). Dukascopy has the same pairs for a free first screen | **low-medium**: a new mechanism class, unknown size, high cost |
| **IC: EM pairs** (USDMXN, USDZAR, USDPLN, USDHUF, USDSGD...) | own fixes (Banxico FIX, WM/R EM), month-end, home hours | analogue of USDCNH (F23, which sits at its ~1 bp cost) | costs 3-30 bp against fix moves of a few bp | **low** |
| **IC: softs** (cocoa, coffee, sugar, cotton) | index-roll (5th-9th business day) and settlement flows | none | round 3: IC's continuous CFDs hide the roll spread; costs 5-20 bp | **low** |
| **IC: share CFDs** | per-stock 1-5 day and intraday effects; the only decision that raises the trade count 10x | none | at 2,500 trades a year LIVE needs a per-trade Sharpe of 0.046; costs ~2-6 bp round trip (commission per share + ~2 bp a night long financing); round 11 G found no 1-5 day cross-sectional predictability in indices / FX; no stock effect size in the repo | **low-medium, speculative, large build** (VPS backtest containers) |
| **Data after 2026-09-24** (IC cache pull or Dukascopy) | the only clean holdout | any registered rule; also today's spreads at the rule minutes | months for t 2.0 / 2.5. At IC cost, VAL size: E1 24 / 37; Friday ECB slot 19 / 30; J5c 10 / 16; L4-G-d 50 / 78; H3 66 / 103; K4 29 / 46; US30 post-close 16 / 26. At 0.65x: E1 99 / 155, J5c 119 / 186. At a venue, VAL size: Sydney pre-leg 3 / 4, J5c 4 / 6, ECB slot 10 / 16 (0.65x: 10 / 16, 12 / 19, 30 / 47) | **high only together with a cost decision** (the Sydney V at a venue resolves in months); at IC's costs it takes years for every lead |
| **Leveraged-ETF AUM** (UGL/GLL/AGQ/ZSL; TQQQ/SQQQ, UPRO/SPXU, 1570/1357) | L4 sized by L(L-1) x AUM x r instead of \|z\|; why silver flipped; the index big-day flow without the 2020 tail | M5, I2 | count fixed at ~25 a year: even a 1.2x Sharpe from sizing gives power ~1.9 at 0.6 bp | **low** for LIVE (mechanism check only) |
| **Deribit OI / gamma history** (paid: Tardis, Laevitas) | the K4 BTC Friday fade, conditioned on the paper's own variable (high ATM OI) | C2 | if half the Fridays carry 2x the edge: power ~2.9 at 3 bp; at 1.5x ~2.1. The 2018-21 IS cost still fails the IS gate (IS net t 1.0; 2.0 under (e)) | **low-medium** |
| **SGE premium / withdrawals** | SGE auction conditioned on Chinese demand | M1, M2 | on the 20 % best mornings at 2.5x the move: power ~2.1 at a 0.6 bp venue; < 0 at IC | **low** |
| **ECB fix volumes / ECB SDW flows** | E1 and the ECB V sized directly | F1-F6 | no public daily fix volume | **low** (feasibility) |
| **Demo runs of E1 / L4-G-d** (pending) | a slow forward holdout at IC's real fills | F1, M5 | as "new data" at IC cost: E1 24-37 months for t 2-2.5 at VAL size, L4 50-78 | **low** for LIVE soon; useful to measure real spreads at 12:45-13:00 London and 13:15 ET |

## 4. Summary
The decision with the highest expected value for finding a LIVE algorithm is a cost structure without IC's 0.6 bp
FX commission floor: a venue at about 0.3-0.55 bp all-in for AUDUSD/NZDUSD at 10:00 Sydney, and at or below 0.2 bp
for EURUSD at the ECB slot. It is the only decision that turns any reported effect into LIVE-like power on the VAL
size (the Sydney V legs at 3.3-5.5, the ECB pre-fix slot at 2.9-3.4). No data decision can do that, because none
changes cost. Its expected value is still modest. The LIVE numbers hold only if the Sydney V keeps at least 0.67-0.72
of its 2022-24 size, and its one out-of-sample reading (AUDUSD 2025-26, mid +0.48 bp) kept 0.31. The ECB slot would
need no decay at all. A venue's own quotes may also not reproduce IC's moves exactly: round 12 J found the post-leg partly reflects IC's
quotes normalising after its rollover hour. The cheap way to price that decision before acting on it is two free data steps: Dukascopy
M1 AUD/NZD 2004-15 (is the V a 21-year structure: mid t ~18) and data after 2026-09-24 (at a venue cost the Sydney
rule reaches t 2.5 in 4-6 months at VAL size, 16-19 months at E1's retention).

Several decisions are low value for LIVE:
- The IS bar change adds no LIVE row; its index targets fail on their IS mid.
- Half spreads at IC lift no FX row, because the commission stays.
- EUR crosses, EM, softs and Scandinavian pairs at IC's costs.
- LETF AUM, SGE premium and ECB volumes are mechanism checks on count-capped or venue-dependent rows.
- Index PRE data tests DEMO-tier rows capped at power 1.1-1.4.
- Demo runs and new data at IC's costs need years per lead: E1 3-13, gold big days 6-28.

Dukascopy XAU/XAG M1 is worth taking as evidence, because it is free and decisive on three mechanisms (gold
settlement big days, the LBMA drops, the SGE placebo), but it cannot make any of them LIVE.

## Caveats
- Power on the VAL size is optimistic for every row. The VAL sizes of post hoc rows were seen during selection: F5,
  F6, F18, F20, M1, M3, M8-M10, I7, I9, I11, I12, F28. Flags are numbers only; they skip the random-entry control,
  x1.5, +1 minute and years > 0.
- The rows are not independent:
  - E1, the ECB slot and its Friday subset share EURUSD 12:45-13:00 London;
  - the three Sydney rows share 10:00 Sydney;
  - EURJPY midday = E1 minus USDJPY midday.
- The venue costs are assumptions, not quotes. Testing the venue route needs that venue's own historical quotes at
  these minutes, and the user's decision on a broker.
- Retention values are single HOLD draws with wide error bars. They are a sensitivity, not an estimate.

## Files (scratch, `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r16/X/`)
- `decision_value.py`: every input with its source, the cost scenarios, the flags, retention and months. Output:
  `decision_value_out.md`.
- `t3_filtered.py`: the LIVE-cost and retention table. Output: `t3_filtered_out.md`.
- `data_decisions.py`: the expected t of the data tests. Output: `data_decisions_out.txt`.
- No repo code was run except `research/.venv/bin/python` on these scripts. No price file was read.
