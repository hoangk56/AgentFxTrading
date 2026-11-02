# Stream P hypotheses: PBoC central-parity surprise, USDCNH within seconds of 01:15 UTC

Written 2026-11-01 15:00 UTC (`date -u` gave 15:00:13), before any signed return was computed. Done before this
file: the fix download and parse, an unsigned activity check of the tape (tick counts and |mid change| per second
around 01:15, all years 2016-24, no direction) and a spread check at the declared moments (all years). Neither uses
the fix or a signed price change.

## Mechanism
The CFETS central parity, published at 09:15 Beijing (01:15 UTC) on mainland business days, anchors the onshore
CNY band (+-2 %) and signals the PBoC's preferred direction (counter-cyclical factor 2017-20 and again from 2023).
A fix away from what the CNH market expected moves USDCNH towards the fix. Round 7 found the move takes ~6 minutes
on M1 bars (t 3.1 IS and VAL) and no drift after. The question here is how much of that move is left after a bot
can react (5 or 30 s) at IC's real tick quotes.

## Data
- Fix: SAFE (State Administration of Foreign Exchange) "人民币汇率中间价" query, `www.safe.gov.cn/AppStructured/hlw/
  RMBQuery.do` (POST, one year per request; robots.txt answers 404 = no restriction; plain UA, no account, no e-mail).
  2,313 fixes 2015-07-01..2024-12-31 in `research/data/cny_fix/usdcny_fix.csv` (USD column / 100). Spot checks:
  2015-08-11 6.2298, 2016-01-07 6.5646 (match the published history). Same series as round 7's "official CFETS".
- USDCNH: IC ticks `research/data/USDCNH/t1` 2016-01-01..2024-12-31 (bid / ask, ms UTC), read one day at a time
  with the round 30 decoder (`research.ticks.decode_day` + forward fill of unchanged sides); HOLD guard asserted.
- Tape check (unsigned): |mid change| per second is flat until 01:15:00, a small bump at +0..+2 s from 2019, then a
  clear step at about **+13..+15 s** (2019-24; 2016-18 slower, +20..+30 s) and stays high to at least +35 s. Tick
  counts jump on 5-s marks (-5, 0, +15 s: IC quote batching). So on IC's clock the market starts to react ~10-15 s
  after 01:15:00. Whether a bot can know the fix by 01:15:05 is not testable here (the chinamoney page is behind a
  robot check; the SAFE page updates later in the day). **d = 5 s therefore assumes a feed that delivers the fix
  within ~5 s; the d = 5 cells can at most become DEMO with a live timing test as a promotion condition.** d = 30 s
  is the realistic bot.

## Surprise
- g_t = ln(fix_t / mid_t) x 1e4 bp, mid_t = (bid + ask) / 2 of the last IC tick with ts < 01:15:00.000 UTC on fix
  day t; the quote must be <= 60 s old, else the day is dropped.
- s_t = g_t - median(g over the previous 20 fix days with a valid g; >= 10 needed). Known at 01:15 when the fix is
  out; the median uses only earlier days.
- Days: SAFE fix dates (mainland business days incl. weekend make-up days, which have no IC ticks and drop out).

## Rule and declared cells (8 = the whole grid)
If |s_t| >= k: buy USDCNH if s_t > 0 (fix weaker for CNY than CNH priced), sell if s_t < 0. Enter at the first tick
with ts >= 01:15:00 + d (buy at its ask / sell at its bid), exit at the first tick with ts >= 01:15:00 + H (sell at
bid / buy at ask). One trade a day. Entry tick must be <= 60 s after its target, exit likewise.
- k in {5, 15} bp, d in {5, 30} s, H in {6, 30} min: cells named k5_d5_h6 ... k15_d30_h30.
- Side fixed by the mechanism before data. Parameters: the best IS cell is reported together with all 8; a pass
  requires the cell to pass on IS and VAL unchanged, and the max-over-8 null is reported.

## Costs
- Spread: paid exactly, ask in / bid out at the actual entry and exit ticks (median spread at the moments, data check:
  +5 s 0.4-0.9 bp from 2017, 2.8 in 2016; +6 / +30 min 0.2-0.6 bp; 2016 ~2 bp).
- Commission: 0.6 bp a round trip (round 30, IC raw account).
- Net bp = side x (exit fill - entry fill) / entry mid x 1e4 - 0.6.
- Stress: spread x1.5 (net - 0.5 x half-spreads at both ends - 0.3 bp commission); one step late = both fills
  +60 s (PROMPT "1 phút trễ"); also reported: both fills +30 s and +250 ms latency (round 26 fill model) as info.

## Eras, statistics, benchmarks
- IS 2016-2021, VAL 2022-2024, HOLD never loaded (ticks and fixes stop at 2024-12-31).
- t: one trade a day, so day-clustered t = mean / (sd / sqrt(n)). Years positive out of 9 (IS + VAL).
- Random benchmark (primary): 1,000 draws of n random eligible fix days of the same era with a random side, same
  d / H; the % of draws the cell's net mean beats. Also: sign shuffle on the cell's own days.
- Family: shared per-day sign-flip null of the max IS |t| over the 8 cells (1,000 draws).
- Path first (IS only): mean of side-signed mid change (sign of s) from the pre-01:15 mid at -60, -30, -10, 0, +5,
  +10, +15, +20, +30, +60, +120, +360, +900, +1800 s, by bucket s <= -15, (-15, -5], (-5, 5), [5, 15), >= 15.
- C3 daily-P&L correlation for any cell with DEMO numbers.

## Power arithmetic
- ~450 fixes in HOLD (2025-01..2026-10). If a share q of days has |s| >= k, n_HOLD ~ 450 q. LIVE needs a VAL
  per-trade net Sharpe >= 3 / sqrt(450 q): q = 1 -> 0.14, q = 0.3 -> 0.26, q = 0.1 -> 0.45.
- USDCNH per-trade sd ~3-5 bp over 6 min and ~7-10 bp over 30 min (rough), so a k = 5 cell with q ~ 0.3 needs about
  +1 bp net (+2 bp gross after ~1 bp of costs) per trade; a k = 15 cell needs several bp. Prior: low; round 7
  already found the move done in ~6 min on M1 and the tape shows the reaction starting at ~+10 s, so most of it
  should be gone by d = 30 s.

## Pass bars (unchanged)
LIVE: t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive, beats >= 95 % random, positive at x1.5 and +1 step late,
power at VAL size >= 3. DEMO: t >= 2.0 IS, net > 0 VAL, beats >= 90 % random (plus positive at x1.5 / late).
Pass -> PREREG_DRAFT_P_<name>.md and stop; HOLD stays closed.
