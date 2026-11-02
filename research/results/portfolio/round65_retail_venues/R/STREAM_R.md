# Stream R (round 65): Korean waking-hours rhythm on Upbit-heavy altcoins

Written 2026-11-01 11:42 UTC (from `date -u`). The hypotheses, the 7 books and the side were declared in
[HYPOTHESES_R.md](HYPOTHESES_R.md) at 11:37 UTC. No return of any kind had been computed at that point. HOLD
(2025-01-01..) was never loaded: every series is cut at ts < 2025-01-01, and the last book day is 2024-12-30. No
download, no web search (local data only).

## Answer first: none (no LIVE, no DEMO)
**All 7 declared books lose money in IS and in VAL, in every year 2020-24.**
- IS net runs from -27 to -90 bp/day, with t from -2.2 to -9.7.
- VAL net runs from -45 to -120 bp/day, with t from -9 to -20.
- No PREREG_DRAFT is written.

**The declared side is wrong, not just too small.**
- The hypothesis was that Upbit-heavy coins rise in the Korean day (00-15 UTC) and fall at night (15-24 UTC).
- The gross profile shows the reverse. Upbit-heavy coins fall in the Korean day and rise in the Korean night,
  strongest at 21-24 UTC (06-09 KST, just before Korea wakes up).
- **IS:** high minus low share is -5.5 bp in the day and +13.6 bp at night.
- **VAL:** high minus low share is -27.3 bp in the day and +19.0 bp at night.

**The reversed side was found after the books were run, so it cannot be promoted.**
- Gross it earns +20.5 bp/day in IS (t 2.06) and +47.1 bp/day in VAL (t 7.85).
- Taker cost plus half-spread is about 69 bp/day, so it is net negative at taker cost in both eras.
- It is positive only under an assumed 2 bp maker fill: IS +5.0 (t 0.50), VAL +31.5 (t 5.24). See "What a user
  decision could unlock".

## Gross rhythm by hour (IS first, as declared; r_profile_IS.txt, r_profile_VAL.txt)
Universe A terciles by trailing 30-day Upbit share. Entries are bp per hour, high-share tercile minus low-share
tercile, with the day-clustered t in brackets.

| UTC (KST) | IS | VAL (information) |
|---|---|---|
| 00 (09, Korean open) | -1.7 (t -0.48) | -6.1 (t -3.23) |
| 05 (14) | +3.9 (t +1.93) | -3.2 (t -2.88) |
| 14 (23) | -5.3 (t -2.25) | -2.2 (t -1.64) |
| 21 (06) | +4.6 (t +2.33) | +2.8 (t +2.60) |
| 22 (07) | +6.3 (t +3.04) | +2.3 (t +2.00) |
| 23 (08) | +6.5 (t +2.97) | +4.9 (t +4.73) |
| sum 00-15 (Korean day) | -5.5 | -27.3 |
| sum 15-24 (Korean night) | +13.6 | +19.0 |

- **Day leg vs BTC.** In IS the day leg is +6.4 bp, so in 2020-21 Upbit-heavy coins rose vs BTC in the Korean day,
  but less than low-share alts did.
- **VAL is one-signed.** From 00 to 15 UTC Upbit-heavy coins fall about 27 bp vs both legs. From 15 to 24 UTC they
  recover about 14-19 bp.

## Declared books (net per day per $1 of one side; r_books.txt, r_results.json)
- **t** = the smaller of Newey-West (lag 5) and the plain daily t.
- **rand %** = percentile of the real mean among 500 shuffled-share books.
- **Power** = VAL daily Sharpe x sqrt(667).
- **Universe A** = top-60 perps with an Upbit KRW market: 6.9 / 7.9 coins per tercile in IS / VAL. The first usable
  IS day is 2020-04-11, because few top-60 perps were older than 60 days before then.
- **Universe B** = all of the top 60, with share 0 for coins that have no Upbit market.

| cell | IS net | IS t | IS gross / cost | VAL net | VAL t | VAL gross / cost | rand % IS / VAL | yrs + | VAL ann SR | power |
|---|---|---|---|---|---|---|---|---|---|---|
| A-N-LS | -49.1 | -7.57 | -13.7 / 34.7 | -55.9 | -17.43 | -18.8 / 34.7 | 1 / 0 | 0/5 | -9.6 | -12.9 |
| A-D-LS | -41.3 | -4.42 | -6.8 / 34.7 | -64.0 | -13.13 | -28.3 / 34.7 | 24 / 0 | 0/5 | -7.4 | -10.0 |
| A-N-BTC | -48.7 | -5.28 | -19.8 / 30.0 | -46.4 | -9.35 | -14.0 / 30.0 | 0 / 0 | 0/5 | -5.4 | -7.3 |
| A-D-BTC (IS pick) | -27.4 | -2.22 | +3.3 / 30.0 | -59.3 | -9.43 | -29.3 / 30.0 | 9 / 0 | 0/5 | -5.3 | -7.2 |
| A-FLIP | -90.3 | -9.73 | -20.5 / 69.3 | -119.8 | -20.16 | -47.1 / 69.3 | 0 / 0 | 0/5 | -11.5 | -15.6 |
| B-N-LS | -46.7 | -9.13 | -10.8 / 36.1 | -49.4 | -16.17 | -12.2 / 36.1 | 0 / 0 | 0/5 | -9.3 | -12.5 |
| B-D-LS | -45.2 | -6.83 | -8.9 / 36.1 | -44.6 | -11.55 | -7.1 / 36.1 | 4 / 1 | 0/5 | -6.6 | -8.9 |

- **Funding** is between -0.7 and +1.0 bp/day in every cell.
- **Correlation with BTC** over the window is between -0.30 and +0.14.
- **Costs x 1.5 and one step late (+1 h):** every cell is negative in both eras. The best case is A-D-BTC late, at
  IS -22.0 (t -1.96).
- **Years:** every cell is negative in each of 2020-24 (r_books.txt).
- **Shuffled benchmark:** the shuffled books pay the same costs and average -37.5 bp/day in IS. Most declared books
  sit at or below the 0-24th percentile, because their gross has the wrong sign.
- **Max-over-7-cells null of IS t:** median -2.02, 95th percentile -1.25. The IS pick (A-D-BTC, t -2.22) sits at the
  33rd percentile.
- **C3 correlation:** not computed, because no cell has DEMO numbers.

## Post hoc (information only; r_posthoc.txt, code/posthoc.py): the reversed rhythm
**The book.** Short the high-share tercile and long the low-share tercile from 00 to 15 UTC, then the reverse from
15 to 24 UTC. This is minus A-FLIP: same universe, turnover 8 $/day per $1 side.
- **Gross:** IS +20.5 bp/day (t 2.06), VAL +47.1 (t 7.85).
- **Gross by year:** 2020 +11, 2021 +27, 2022 +48, 2023 +51, 2024 +42.
  - Day part: IS +6.8 (t 0.68), VAL +28.3 (t 5.67).
  - Night part: IS +13.7 (t 2.01), VAL +18.8 (t 5.59).
- **Net at taker cost plus half-spread:** IS -48.3, VAL -24.8.
- **Net at an assumed 2 bp maker fill with no spread:**
  - IS +5.0 (t 0.50); VAL +31.5 (t 5.24, annual Sharpe 3.0).
  - By year: 2020 -4.6, 2021 +12.0, 2022 +33.3, 2023 +35.4, 2024 +25.9.
  - It fails the IS bar even under that assumption.

**It is not a size effect.**
- Terciles by small trailing volume within the same universe give a reversed-flip gross of IS -32.5 (t -2.92) and
  VAL +6.9 (t 1.26).
- Terciles by the share residual after regressing log share on log volume give IS +25.3 (t 2.47) and VAL +42.4
  (t 6.76).
- The rhythm follows the Korean share, not coin size.

**Reading.**
- Prices of Upbit-heavy coins are lifted in the hours before Korea wakes up, 21-24 UTC = 06-09 KST.
- They fade during the Korean session, most strongly at 00 UTC = the 09 KST Upbit daily-candle reset and the Korean
  open.
- That is consistent with Korean retail being net sellers into its own session, or with global pre-positioning ahead
  of it. It is the opposite of the declared "Korean buying lifts, global pulls back".

## What failed and why
1. **Wrong sign.** Korean waking hours are when Upbit-heavy coins underperform, not outperform. Every declared book
   holds the losing side of the rhythm.
2. **Costs.** Even with the right sign, a daily round trip costs 30-36 bp per window book, or about 69 bp for the
   flip, at taker 5 bp plus half-spread. The gross rhythm is 20 bp/day (IS) to 47 bp/day (VAL), so it never covers
   taker cost.
3. **Power arithmetic held.** LIVE needed an annual net Sharpe of about 2.2, i.e. about 60-70 bp of gross per window.
   The real gross per window is 7-28 bp.

## Pitfalls met / biases
- **Mixed 1h layouts.** binance/perp_1h has `t,o,h,l,c,qvol` and the others have `t,o,h,l,c,vol,qvol,n`. Columns are
  read by header name.
- **Survivorship in the Upbit list.** Upbit coins delisted or renamed before stream K's pull (for example LUNA, MATIC,
  EOS) have no candles.
  - In universe A they are simply absent.
  - In universe B they count as zero share.
- **BTT excluded.** BTTUSDT was dropped before any return was computed: the 2022 redenomination reused the Upbit code,
  and stream U skipped it as well.
- **TOKENUSDT** has no funding file and is priced with zero funding.
- **Execution prices.** Entries and exits are at the 1h close, as in round 63 C, plus a half-spread cost. The
  one-step-late check moves both by +1 h. There are no 1m fills, because no book came close to a bar.
- **Small IS window.** The IS universe A is small before mid-2020 (630 IS days from 2020-04-11).

## What a user decision could unlock
- **The reversed rhythm as a new, pre-registered hypothesis, tested on an untouched era.**
  - Short Upbit-heavy vs Upbit-light 00-15 UTC, long 15-24 UTC.
  - It was discovered on IS / VAL, so only HOLD is a clean test. That is the coordinator's call.
- **It needs maker execution with real queue fills to have any chance.**
  - At 2 bp maker its VAL power would be about 0.159 x sqrt(667) = 4.1.
  - Its IS maker-net t is only 0.50, so it cannot meet the IS bar as a re-labelled cell.
  - Taker execution is hopeless.
- **A cheaper variant would be to hold only the strongest window.** That is long Upbit-heavy vs light 21-24 UTC, with
  a gross of IS +17 bp and VAL +10 bp. It is still below the 36 bp taker round trip.

## Files
- **This folder:** HYPOTHESES_R.md, STREAM_R.md, r_profile_IS.txt, r_profile_VAL.txt, r_books.txt, r_results.json,
  r_posthoc.txt.
- **code/:**
  - rdata.py: panel, universe, share.
  - r.py: profile, books, shuffled null.
  - posthoc.py: reversed rhythm and size control.
- **research/data/korea_hours/panel.npz** (192 MB numpy cache, outside results/).
