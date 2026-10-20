# Round 24, stream C: RELAXED re-evaluation of effects that already exist (declared before recomputing)

Written 2026-10-15 11:53-11:55 UTC (`date -u` gave 11:53:40 when writing started and 11:55:02 when it was complete), before any stream-C number was
computed, with one disclosed exception: at about 11:50 UTC the engine was validated by rerunning the registered E1
rule (F1 below) and it reproduced the registered IS / VAL numbers exactly (IS 1,525 trades net +1.17 t 3.29; VAL 765,
+1.35 t 2.46). Those numbers were already public in PREREG_M; nothing else was computed. HOLD (2025-01-01 onwards) is
not loaded: the shared panel ends 2024-12-31 and USDCNH bars are cut at 2025-01-01 at load.

**No new parameters.** Every rule below is the one already recorded (source in the table). Where the record is
ambiguous, the reading is fixed here, before the numbers, and flagged "reading". Three rows cannot be rebuilt because
their rule was never written down; they are not recomputed and are scored from the record only (marked "record").

## Data and conventions (all rows unless the row says otherwise)
- Panel `r23/shared/panel` (IC M1, mid = (bid close + ask close) / 2, spr = ask - bid at the minute's last tick,
  bar-start labels, 2016-01-01..2024-12-31). USDCNH (F23 only): IC M1 bid bars from `research/data/USDCNH/m1/*.zbars`
  (cut < 2025-01-01), mid = bid + half of round 7's published 2.93-pip spread, spread = 2.93 pips.
- Price "at time X" = close of the last M1 bar ending at or before X (bar labelled X - 1 min), at most 10 minutes stale
  (else no trade), as in the registered E1 / L code. Calendar rules are quoted at their clock times. A rule whose side
  or selection uses data is quoted at least 1 minute after its last data point, as recorded.
- Costs: half the actual spread at each quote + 0.6 bp commission for FX and metals (0 for indices, energy, crypto) +
  swap for every 17:00 New York rollover crossed (`research.swing.rates.swap_frac_at`, x3 on the symbol's triple day).
- Checks: spread x1.5 (half spreads x1.5); +1 minute (both quotes 1 minute later, same side).
- Eras: IS 2016-01..2021-12 (design), VAL 2022-01..2024-12 (check). XTI IS = 2018-21; BTC IS from its first IC
  quote. Rolling selectors start from 2016 data only (the panel has no 2015), so their first weeks of 2016 have no trade.
- Statistics: mean bp per trade (a basket = one trade; legs summed with their weights), t clustered by UTC day of
  entry; per-trade net Sharpe; **power = per-trade net Sharpe x sqrt(1.73 x trades per year)** on the IS and on the VAL
  size (the VAL one is the expected HOLD t at the VAL size); power on day units also reported.
- Random-entry control, 200 seeds, percentile of the rule's net mean among seed means, per era:
  - "time" (rules traded every day or on data-selected days): same days, same side rule, same hold, entry and exit
    shifted by the same random whole number of minutes in [-180, +180] (not 0), one draw per trade; a side computed from
    data is recomputed at the shifted time by the rule's own formula; draws whose window touches 16:45-18:15 New York
    are dropped (IC's rollover hour; not for N1, which sits there).
  - "day" (rules on calendar event days: FOMC, month-end, quarter-end, holidays, Christmas): same clock window and hold
    on random non-event days of the same era with the same weekday, side rule recomputed.
- Chance: K = number of recomputed rows; expected max |t| of K normals reported next to the best IS t.

## Tiers (as fixed by the round-24 brief; LIVE and DEMO are the user's original bars)
- **LIVE**: IS net t >= 2.5, VAL net t >= 1.5, >= 2/3 of years net > 0, beats >= 95 % of random entries (IS and VAL),
  power >= 3 on the VAL size, net > 0 at x1.5 and +1 minute (IS and VAL).
- **DEMO**: IS net t >= 2.0, VAL net > 0, beats >= 90 % (IS and VAL), net > 0 at x1.5 and +1 minute.
- **RELAXED**: IS net t >= 1.5, VAL net > 0 with t >= 1.0, net > 0 at x1.5 and at +1 minute (IS and VAL), beats >= 80 %
  of random entries (IS and VAL), power >= 1.5 on the VAL (check-era) size, and an economic mechanism (column "mech"
  below, fixed now from the source's own description: "no" = a clock cell picked by a scan with no named flow).
- **Cost needed for LIVE** (per row): the round-trip cost (spread + commission, swap unchanged) at which IS t >= 2.5,
  VAL t >= 1.5 and VAL-size power >= 3 all hold = min(IS mid - 2.5 SE_IS, VAL mid - 1.5 SE_VAL,
  VAL mid - 3 sd_VAL / sqrt(1.73 n_VAL/yr)), on mid + swap. Negative = no cost reaches LIVE.

## The book of RELAXED survivors (declared now, built only from the rows that pass RELAXED)
- One algorithm; one bot per symbol (the project's bot = account x symbol x strategy); each row's trades enter as
  recorded. **Equal risk**: each row's per-trade net is divided by that row's IS per-trade net sd (unit risk per trade).
- **At most 3 positions per bot**: on each symbol, a trade that would open a 4th concurrent position is skipped (entry
  time order; ties by row order in the table below).
- Reported: daily P&L in risk units (sum of the day's trades by entry UTC day), IS and VAL mean, day-clustered t,
  per-year, daily Sharpe, power = daily Sharpe x sqrt(1.73 x active days a year) on the VAL size, correlation with C3
  (`trades_C3_gotobi_jpy_basket.csv`, `usd_at_100_risk` by exit UTC day; daily on the union of days with zeros, and
  monthly), IS + VAL only.
- If no row is RELAXED, the book is reported as empty.

## PREREG_DRAFT_C_* (for each RELAXED survivor)
Exact rule, tier, expected HOLD trades (1.73 x VAL trades/yr), expected HOLD t at the VAL size, at 0.65 of the VAL
mid for rows whose side was declared / PRE / literature, and at 0.25 of the VAL mid for post-hoc picks (round 18), and
a demo stop rule. HOLD is not opened.

## The rows (K = 60 recomputed + 3 record-only)
Clock zone codes: LON Europe/London, NY America/New_York, SYD Australia/Sydney, TOK Asia/Tokyo, CET Europe/Berlin,
HK Asia/Hong_Kong, UTC. "wkd" = Monday-Friday by the local date of the clock; "xmas" = 24 Dec-1 Jan excluded;
"xmas2" = 24 Dec-2 Jan excluded. Ctrl = random-entry control type. Sel = how the side/window was found (PRE / lit /
decl / scan / post) as in STREAM_X.

### A. Round 16 STREAM_X rows
| id | rule (symbol, side, window, days) | sel | mech | ctrl | reading / note |
|---|---|---|---|---|---|
| F1 | EURUSD short 11:00-13:00 LON, wkd, xmas, holidays traded (registered E1) | PRE | yes (ECB fix) | time | |
| F2 | EURUSD short 04:00-08:00 NY, wkd by NY date, xmas | PRE | yes | time | reading: round 14 Q cell "NY 04:00 + 4 h" (STREAM_X wrote "09:00-13:00 London") |
| F3 | F1 on USD-TOP days: U = mean of USDJPY and USDCHF log return from 18:00 NY on the previous weekday to 07:00 LON on the day (close of bar 06:59); trade if U >= 67th pct (np.percentile, linear) of U over the previous 250 trading days of the panel (day excluded, >= 60) | decl | yes | time | reading: previous weekday (Friday for Mondays); history from 2016 only |
| F4 | EURUSD short 12:45-13:00 LON, wkd, xmas, TARGET2 closing days excluded (O2 X-HOMEHOL) | PRE | yes | time | TARGET2 from python-holidays XECB |
| F5 | EURUSD short 12:50-13:00 LON, Fridays, xmas (Good Friday kept) | post | yes | time | |
| F6 | EURUSD long 14:00-14:15 CET, wkd, TARGET2 closing days and xmas2 excluded | post | yes | time | |
| F7 | USDCHF long 10:00-12:00 UTC (19:00-21:00 TOK), wkd by Tokyo date, xmas | PRE | no | time | |
| F8 | F7 on MORN-TOP days: USDCHF log return 06:00 -> 10:00 UTC (close of bar 09:59) >= 67th pct of its previous 250 trading days (>= 60) | decl | no | time | reading as F3 |
| F9 | USDCHF short 08:00-08:30 NY, wkd by NY date, xmas | PRE | yes (ECB-fix rebound) | time | reading: NY clock as recorded (STREAM_X wrote 13:00 UTC) |
| F10 | USDJPY long 11:00-13:00 LON, wkd, xmas | PRE | yes (USD leg of the E1 window) | time | |
| F11 | EURJPY short 11:00-13:00 LON, wkd, xmas | PRE | yes | time | |
| F12 | GBPJPY long 17:30-21:30 LON, wkd, xmas; day dropped if the window intersects 16:45-18:15 NY (half-open) | PRE | no | time | |
| F13 | GBPJPY long 02:45-06:45 SYD, wkd by Sydney date, xmas; same rollover drop (half-open) | PRE | no | time | |
| F14 | EURJPY long 16:00-20:00 LON, wkd, xmas | PRE | no | time | |
| F15 | EURJPY short 05:00-07:00 LON on the last weekday (London date) of Mar/Jun/Sep (Dec lost to xmas), holidays count | PRE | yes (quarter-end) | day | |
| F16 | GBPUSD long 15:00-16:00 LON, last weekday of the month (holidays count), xmas | PRE | yes (WM/R month-end) | day | |
| F17 | Registered rule I: day T = last weekday of the month not an England bank holiday, not 25 Dec / 1 Jan; r = ln(US500 at 16:00 NY on the weekday before T / same at the previous month's T, 3-day stale allowed); if abs(r) >= 0.024471581800513734 buy USD if r > 0 (short EURUSD, long USDJPY, short GBPUSD), sell USD if r < 0; 16:00-17:00 LON; each pair one trade | post | yes | day | t clustered by day (= event) |
| F18 | GBPJPY long 10:28-10:31 NY, last weekday of the month, December excluded | post | yes | day | |
| F19 | short AUDUSD and short NZDUSD 09:45-10:00 SYD, wkd by Sydney date, xmas2 | scan | yes (Sydney 10:00 flows) | time | two legs, one trade each, day-clustered |
| F20 | J5c: AUDUSD short 09:45-10:00 SYD, wkd, xmas2, only if 10:00 SYD in New York time is >= 18:30 | post | yes | time | |
| F21 | long AUDUSD and long NZDUSD 10:00-10:15 SYD, wkd, xmas2 | scan | yes | time | |
| F22 | USDJPY long 16:00-17:00 NY, wkd by NY date, xmas | scan | yes (cash-close flows) | time | reading: exit at 17:00 = close of bar 16:59 (round 10 footnote) |
| F23 | USDCNH long 01:30-08:30 UTC, every UTC weekday, xmas | lit | yes | time | bid bars + published spread |
| F24 | USDJPY long 07:45-08:00 UTC (into the 16:00 Taipei close), every UTC weekday, xmas | decl (best of 108) | yes | time | reading: all weekdays (TWSE calendar not recorded) |
| F25 | R3 currency-strength reversal: 10 IC FX pairs; H1 joint bars of log mid; currency returns = pinv(A) r (8 currencies); strength = sum of the last 4 H1; at each H1 close (decision hour not 20-22 UTC), when flat, trade the pair with the largest abs(strength(base) - strength(quote)), short the stronger currency; fill 1 min after the H1 close; hold 8 h; swap charged | lit | yes (liquidity provision) | time | rebuilt from round 8 HYPOTHESES_R |
| F26 | R2 PCA residual s-score (Avellaneda & Lee) on 10 FX + 3 metals | lit | yes | - | **record**: the round-8 code is gone; recorded net IS -1.15 / VAL -1.62 bp (cost 3.4 / 4.1) fails every tier's IS gate |
| F27 | W1: Wednesdays, 10 IC FX pairs, each long the higher-rate currency (rates.rate on the first day of the month - 1 day), 12:00-16:55 NY, wkd by NY date, xmas; one trade = equal-weight basket of the 10 pairs | lit | yes (carry into the triple rollover) | day | reading: the round-3 row records only this much |
| F28 | S1: USTEC 15-min log return r_w; sd_w = RMS of r_w over the 28 calendar days ending at the previous UTC midnight; event = first crossing of abs(r_w) >= 6 sd_w, none within 60 min after; beta = OLS slope of EURUSD on USTEC non-overlapping 5-min returns over 84 days to the previous midnight (>= 500 pairs); trade EURUSD at -sign(r_w) x sign(beta), entry at the close of bar i+1, exit 240 min later | post (best of grid) | yes (lead-lag) | time | |
| F29 | USDJPY into short-dated Treasury auctions | lit | yes | - | **record**: window, tenor list and code never recorded; recorded IS +4.5 (t 3.3) / VAL +1.0 (t 0.4) mid fails RELAXED VAL t |
| M1 | XAUUSD long 02:15-02:23 UTC, Shanghai SE trading days from 2016-04-19 | post | yes (SGE auction) | time | XSHG from python-holidays |
| M2 | M1 on dip mornings: XAU log return 07:00 UTC on the previous XSHG day -> 02:00 UTC today in the bottom quintile (<= 20th pct) of the previous 250 event days (>= 60) | decl | yes | time | |
| M3 | XAUUSD long 01:00-03:30 UTC, XSHG trading days | post | yes | time | |
| M4 | XAUUSD side = -sign(p(07:00)/p(06:30) - 1 UTC), 07:00-07:30 UTC, XSHG days | decl | yes | time | |
| M5 | Registered rule L (PREREG_L), NYSE days, z at 13:14 NY vs previous 13:30 settlement, 60-day sd (>= 30), 90th pct of the previous 250 abs(z) (>= 60), follow sign(z) 13:15-13:30 NY | decl | yes | time | |
| M6 | M5 with the 80th percentile | decl | yes | time | |
| M7 | XAUUSD follow sign(ln p(13:25 NY) / p(13:30 NY previous NYSE day)), 13:25-13:30 NY, NYSE days | lit | yes | time | reading: NYSE calendar |
| M8 | XAUUSD short 14:59-15:01 LON, England business days, xmas2 | post | yes (LBMA PM) | time | |
| M9 | XAGUSD short 11:59-12:01 LON, same days | post | yes (LBMA silver) | time | |
| M10 | XAUUSD short 10:29-10:31 LON, same days | post | yes (LBMA AM) | time | |
| M11 | XAUUSD side = -sign(p(08:20)/p(08:10) - 1) NY, 08:20-08:30 NY, NYSE days, xmas2 | decl | yes (COMEX open) | time | |
| M12 | XAUUSD long 02:00-06:00 UTC on the last Tokyo-date weekday before an England bank-holiday block that is not itself a holiday, xmas | PRE | no | day | |
| I1 | USTEC follow sign(p(15:51)/p(15:50) - 1) NY, 15:52-16:00 NY, NYSE full days, xmas2 | decl | yes (MOC) | time | |
| I2 | USTEC follow sign(p(15:49)/p(09:30) - 1) NY, 15:52-16:00 NY, only if abs(return) >= 80th pct of the previous 250 days (>= 60), NYSE full days | decl | yes (LETF) | time | |
| I3 | US30 side = -sign(p(16:04)/p(15:54) - 1), 16:04-16:14 NY, NYSE full days, xmas2 | decl | yes | time | |
| I4 | US500 side = -sign(p(09:41)/p(09:31) - 1), 09:41-09:51 NY, NYSE full days, xmas2 | decl | yes | time | |
| I5 | UK100 side = -sign(p(16:34)/p(16:24) - 1), 16:34-16:39 LON, England business days, xmas2 | decl | yes | time | |
| I6 | AUS200 side = -sign(p(16:12)/p(16:00) - 1) SYD, 16:13-16:30 SYD, NSW business days, xmas2 | decl | yes | time | |
| I7 | AUS200 short 10:10-10:11 SYD, NSW business days, xmas2 | post | yes (ASX open) | time | |
| I8 | HK50 side = -sign(p(09:30)/p(16:00 previous weekday) - 1) HK, 09:30-09:31 HK, HK weekdays, xmas2 | decl | yes | time | reading: previous close 16:00 HKT, previous weekday |
| I9 | JP225 follow sign(ln p(14:59 TOK)/S(d-1)), S = p(15:15 TOK) (15:45 from 2024-11-05), 15:00-15:15 TOK (15:30-15:45 after), Tokyo weekdays, xmas | post | yes (LETF) | time | |
| I10 | DE40 follow sign(ln p(17:24 CET)/p(17:35 CET previous weekday)), 17:25-17:35 CET, CET weekdays, 24 / 31 Dec dropped | decl | yes (LETF) | time | |
| I11 | US30 short 15:45-16:00 NY on scheduled FOMC statement days (r23/shared/cal/fomc_2016_2024.json) | post | yes (FOMC) | day | |
| I12 | S4b mirror: weekdays at 08:30 NY; u = half the change of (ln USDJPY - ln EURUSD) from close of bar 08:29 to close of bar 08:30; z = u / sd of u over the previous 250 days (>= 100); event if abs(z) >= 2; b = slope of US30's same-minute move on u over the previous 500 days with abs(z) >= 1 (>= 60); gap = US30 move - b u; trade +sign(gap) if abs(gap) >= sd of US30's minute move over the previous 250 days; entry close of bar 08:31, exit 30 min later | post (side) | no (side from data) | time | reading: subset abs(z) >= 2 (the round-8 subset was not recorded; "7-20 events a year") |
| I13 | US500 night premium | lit | yes | - | **record**: close / open times never recorded; recorded IS +4.9 mid, net +1.9 (after swap), VAL net -3.2: fails |
| E1x | XTIUSD follow sign(ln p(14:15 NY)/p(14:30 NY previous weekday)), 14:15-14:30 NY, US weekdays without federal holidays, 2018-24 | lit | yes (settlement) | time | id E1x (to avoid a clash with the E1 candidate) |
| E2x | XTIUSD side = -sign(p(14:30)/p(14:20) - 1) NY, 14:30-14:31 NY, same days | decl | yes | time | |
| C1 | BTCUSD side = sign(p(23:30 UTC)/p(00:00 UTC same date) - 1), 23:30-24:00 UTC, every date with quotes | lit | yes | time | |
| C2 | BTCUSD Fridays: side = -sign(ln p(08:00)/p(07:00)) UTC, 08:01-09:00 UTC (5-min stale limit) | lit | yes (Deribit expiry) | time | |

### B. Other recorded candidates
| id | rule | sel | mech | ctrl |
|---|---|---|---|---|
| FOMC-A4 | Round 20 A4: on scheduled FOMC statement days, long the currencies (of EUR GBP JPY AUD NZD CAD CHF) whose rate exceeds USD's, equal weight, vs USD through the USD pairs; ranks from research/data/rates at the last value before the first day of the month (monthly series = previous month's value); entry = mid at the minute labelled 16:00 NY on the previous weekday, exit = same on the FOMC day; swap charged; no trade if no currency is above USD | lit | yes | day |
| N1a | Round 23 N1a (Tolusic 2026): 6 USD pairs, sessions Sun-Thu 17:00 NY; P0 = last quote 16:30-16:59 NY; reopen R = first bar at/after 17:00 within 30 min; gap g in pips; if abs(g) >= 1, fade: entry fill at bar t_r + 1, exit fill at bar 18:00 NY | lit | yes | time (gap recomputed at shifted hour: g = mid(H) - mid(H-2 min)) |
| N1b | N1a with entry fill at bar 17:05 NY | lit | yes | time |
| N1c | N1a with abs(g) >= 2 pips | lit | yes | time |
| N3b | Round 23 N3b: XAUUSD long, fill at bar 16:00 NY on the 2nd NYSE day before 25 Dec, exit fill 16:00 NY on the 2nd NYSE day after, capped at 5 x 24 h; swap | lit (post-hoc festival pick) | yes (turn of year) | day |

Notes fixed now:
- F1 = PREREG_M (E1) and M5 = PREREG_L are the two registered DEMO candidates; their HOLD results are already known
  (E1 HOLD net +0.64, L HOLD +1.68); a RELAXED pass here does not reopen HOLD for them.
- Rows sharing a symbol and time (F1/F2/F3/F4/F5 on EURUSD; F19/F20 on AUDUSD) are not independent; the book's 3-position
  cap handles overlap, and the book counts each overlapping pair only once if a later row is a subset of an earlier one
  (F3, F4, F5 inside F1; F20 inside F19) — **the subset row is dropped from the book when both survive**.

## Amendment 1 (2026-10-15 12:01 UTC, after the first full run; disclosed as post hoc)
- **Random control for data-selected rows (F3, F8, M2, M5, M6, I2, I12, F28): shifts forward only** (uniform whole
  minutes in [+1, +180]). The declared symmetric shift lets a random window start before the signal that selected the
  day and so contain the very move used to select it (round 13's pitfall "random entries for selected days must enter
  after the signal"). Seen when F8 beat 0 % / 2 % of its symmetric control. Both versions are reported; the tier uses
  the forward-only one for these eight rows. No other row changes.
- **F17 implementation bug fixed** (not a rule change): the US500 reference is the 16:00 NY close on the previous
  month's day T itself (registered code `hold_I.py.txt`), not on the weekday before it, and day T steps back past
  25 Dec / 1 Jan as in that code. The first run used the wrong reference.
