# Round 10, stream A: Asian benchmark and venue-session flows (natural experiments with venue-holiday placebos)

Written 2026-10-05 17:50 UTC, before any stream-A number was computed (only the brief, the round 1-9 reports and the
panel's median-spread table were read). Additions after seeing data are marked **post hoc** with their time.

## Why this family could escape the standing limits

The only survivor (C3) is a price-insensitive flow at one known minute that dealers pre-hedge, and its signature is a
venue-holiday placebo: no Tokyo fix, no edge. Round 4's minute-precise scan used 19 Western/Japanese/CNY times; the
Asian commodity benchmarks (SGE), the Chinese futures venues (SHFE/INE/SGE sessions), the Platts MOC windows and the
Asian onshore FX closes/fixes were never tested. A venue-holiday placebo (same clock, venue shut, IC quoting) removes
every clock confound (London open, US data, Asian liquidity profile), and Chinese holidays give ~15 weekdays a year.
Gold is the cheapest venue-linked instrument (IC median spread 0.78 bp IS / 0.41 bp VAL + 0.6 bp commission), so a
2-3 bp flow in XAUUSD would clear cost where the AUD/NZD Sydney V (1.5 bp at 0.9 bp spread) did not.

## Common construction (fixed before computing)

- Data: shared panel mid/spr 2016-01..2024-12 (HOLD never loaded). p(T) = mid of the minute bar ending at T (panel
  index T-1 min), forward-filled up to 10 minutes; an event needs both prices.
- Event days: Monday-Friday UTC dates with IC quotes at both ends. Day types: OPEN = venue trading day; HOL = weekday
  on which the venue is closed (holidays `financial_holidays` XSHG for Chinese venues, XKRX, XTAI, XSES, XNSE / India,
  Indonesia country calendar, XLON / UK England) while IC quotes.
- Return r[a,b] = 1e4 * (p(T+b) - p(T+a)) / p(T+a), signed by the ex-ante side s (+1 = long the symbol).
- Grid per event (minutes rel. to T): pre legs [-60,0], [-30,0], [-15,0]; post legs [0,15], [0,30], [0,60]. A "V"
  means the pre leg is traded with side s and the post leg with side -s (gotobi shape). Primary cell (declared per
  hypothesis) = pre [-30,0] and post [0,30].
- Stats: IS 2016-21 (energies 2018-21), VAL 2022-24. t clustered by UTC day (pooled symbols: day mean first). HOL
  vs OPEN difference-in-means with Welch t. Time placebos: same rule at T +-10, +-30, +-60 min on OPEN days.
- Executable: enter at T+a, exit at T+b on the panel's mid, cost = half spread at the entry minute + half at the exit
  minute + 0.6 bp (FX, metals; 0 energies). Also +1 minute latency and spread x1.5.
- Multiple testing: every cell (event x symbol x window x side-rule) is counted; best |t| compared with the max of K
  normals and a per-day sign-flip permutation shared by all symbols.
- Bars as in the brief (LIVE / DEMO). A family that meets either on IS/VAL stops and gets PREREG_DRAFT_A_<name>.md.

## A1 Shanghai Gold Exchange benchmark auctions

- Mechanism: the Shanghai Gold Benchmark Price (SHAU, CNY/g, launched 2016-04-19) is set by auction at 10:15 and
  14:15 Beijing (02:15 and 06:15 UTC; China has no DST). China is a structural net buyer (importing banks, jewellers);
  members that fill customer buy orders at the benchmark pre-hedge in the international market. Source: SGE notice of
  2016-04 (en.sge.com.cn/eng_news_Announcement/537284), BullionStar / BullionVault descriptions.
- Why it may escape: a price-insensitive buyer at a known minute, like gotobi, in the cheapest venue-linked symbol.
- Rule / side (ex ante): XAUUSD, OPEN days since 2016-04-19: long [-30,0] into each auction, short [0,30] after (V).
  Silver: Shanghai Silver Benchmark (SHAG, since 2019-10-14); auction time not confirmed, so XAGUSD at both 02:15 and
  06:15 UTC, same V, from 2019-10-14 (IS = 2019-10..2021).
- Placebo: Chinese exchange holidays (XSHG) on which IC quotes gold; time placebos 02:15 +-10/30/60.
- Horizon: <= 60 minutes, intraday.

## A2 Chinese futures and SGE session opens and closes

Events (UTC; Beijing - 8 h): (a) day open 01:00 (SHFE, INE, SGE 09:00); (b) SGE night open 12:00 (20:00);
(c) SHFE/INE night open 13:00 (21:00; INE crude since 2018-03-26); (d) SHFE/INE day close 07:00 (15:00) and SGE day
close 07:30 (15:30); (e) night close 18:30 (02:30 Beijing, gold/silver/crude).
Symbols: XAUUSD, XAGUSD for all; XTIUSD, XBRUSD for (a), (c), (d), (e) from 2018-03-26.

- A2-flow (side ex ante): China net buyer of gold/silver/crude -> long [0,30] after each open (a, b, c). Same idea as
  A1 but at the session start, when the opening auction's order imbalance is worked through arbitrageurs.
- A2-cont (side ex ante): at the opens, Chinese (retail-heavy, trend-chasing) participants catch up with the move made
  while the venue was shut; arbitrageurs pass the opening imbalance to the international price. Side = sign of the
  symbol's move during the closure: for (a) from the previous night close 18:30 to 00:59 UTC (from 07:00 UTC if no
  night session that evening); for (c) and (b) from the day close 07:00 to T-1. Trade continuation over [0,15],
  [0,30], [0,60].
- A2-close (side ex ante): closing flows of Chinese day traders are price pressure that reverts: at (d) and (e), side
  = minus the sign of r[-30,0], traded over [0,30] and [0,60].
- Placebo: Chinese exchange holidays (XSHG; the night session is also absent on the eve of a holiday and on Fridays
  before a holiday week, treated as HOL for (b), (c), (e)); time placebos +-10/30/60.
- Why it may escape: Chinese commodity venues are the largest by volume for silver/base metals and a large share of
  gold; their sessions are fixed clock events whose holiday absence is a natural experiment never tested here.

## A3 Platts market-on-close windows (oil)

- Mechanism: Platts Dubai/Oman partials are traded in the Singapore MOC window 16:00-16:30 SGT (08:00-08:30 UTC);
  Dated Brent / North Sea MOC 16:00-16:30 London (DST-aware). Concentrated physical and swap hedging at a known window;
  Asian refiners (Unipec, PetroChina...) are net buyers of partials. Source: Platts methodology (spglobal crude
  specifications, MOC at 16:30 SGT).
- Rules (ex ante): A3-in: long XBR/XTI over the Singapore window [08:00,08:30] (buyer pressure transmitted via EFS
  and Brent/Dubai spreads). A3-rev: the price-pressure signature: side = minus sign of the in-window move, traded over
  [+30,+60] and [+30,+90] after window start, for Singapore (08:00 UTC) and London (16:00 London).
- Placebo: Singapore holidays (XSES) for the Asian window, UK England bank holidays for London.
- Why it may escape: the only oil benchmarks with a fixed minute window in Asian/London hours; energies have no
  commission. Risk: XBR/XTI spreads 3-5 bp IS, so a fade must be > ~4 bp.

## A4 Asian onshore FX closes and fixings (spillover into AUD, NZD, JPY)

Events (UTC, no DST): TAIFX fix 03:00 (Taipei 11:00, TW holidays XTAI) and JISDOR 03:00 (10:00 WIB, Indonesia
holidays) tested as one 03:00 event with each venue's own placebo; KRW onshore close 06:30 (15:30 KST, KR holidays
XKRX; data cut at 2024-06-30, Korean hours extended 2024-07); INR reference window 06:00-07:00 (FBIL 11:30-12:30 IST,
random 15-min window; RBI before 2018-07; India holidays) with T = 06:30; TWD close 08:00 (16:00 Taipei); CNY onshore
day close 08:30 (16:30 Beijing, feeds the next PBOC fix; XSHG).
Symbols: AUDUSD, NZDUSD (USD side -1 = long AUD/NZD), USDJPY (side -1 = short).

- A4-exp (side ex ante, all events except TWD close): Asian exporters (KR, TW, IN inflows, ID) are net USD sellers at
  the fix/close -> USD weaker into T (pre [-30,0] USD short), back after (post [0,30] USD long).
- A4-cbc (side ex ante, TWD close 08:00 only): Taiwan's central bank is widely reported to buy USD in the last minutes
  before the 16:00 close (TWD weakening late) -> USD stronger into 08:00 (pre leg USD long), back after (USD short).
- Placebo: the venue's own holidays; time placebos.
- Why it may escape: a fixed-minute, price-insensitive corporate flow never tested in this repo; holiday placebo
  separates it from the 03:00/06:30/08:00 clock profile (incl. London open in winter at 08:00).
- Note: 03:00 UTC is just after C3's short-leg exit (02:55); correlation with C3 reported for any survivor.

## A5 Others in the theme

- A5a JP225 SQ (Osaka, second Friday of each month; the special quotation uses the cash opening at 09:00 JST =
  00:00 UTC): index-arbitrage unwinding at the opening auction is price pressure -> fade r[00:00,00:15] over
  [00:15,01:15] on SQ Fridays (side = minus sign of the first 15 minutes). Placebo: the other Fridays (and JPX
  holidays moving SQ). ~12 events a year: DEMO tier at best.
- A5b: none else; HKEX/ASX opens and closes and the CNY 09:15 fix were round-4 cells; USDCNH home hours and the PBOC
  fix surprise were round 7.

## Cell count (declared)

A1: XAU 2 auctions x (3 pre + 3 post) = 12, XAG 2 x 6 = 12 -> 24. A2-flow: 3 opens x [0,15],[0,30],[0,60] x
(XAU, XAG) + 2 opens x 3 x (XTI, XBR) = 18 + 12 = 30. A2-cont: same 30. A2-close: 3 closes (07:00, 07:30, 18:30) x 2
windows x 2 metals + 2 closes (07:00, 18:30) x 2 x 2 energies = 12 + 8 = 20. A3: in 2 + rev 2 windows x 2 venues x 2
symbols = 10. A4: 5 events x 3 symbols x 6 legs = 90. A5a: 1. Total ~205 cells (IS screening); the chance max |t| of
205 normals is ~3.3.

## Post hoc additions

### A6 (post hoc, 2026-10-05 18:20 UTC, after the first screen) Chinese-session gold drift

- Seen in the first screen: the A1 short-after-02:15 leg has the wrong sign (XAU rises after the SGE AM auction:
  [0,15] +0.96 bp, t 6.2 IS / +0.80, t 3.7 VAL; on Chinese holidays it falls, diff t -3.7), and the A2-flow long
  after the 01:00 day open has the ex-ante side ([0,60] +1.19 bp t 2.2 IS, +0.45 VAL, diff vs holidays t 2.5). Both
  are below the ~1.1-1.4 bp gold round trip at 15-60 minutes.
- Hypothesis (side = A2-flow's ex-ante side, long; only the window is new): Chinese buying of gold during the
  SGE/SHFE day session (01:00-07:00 UTC) lifts XAUUSD on Chinese trading days and not on Chinese holidays. Paying the
  round trip once over a multi-hour window could clear cost where 15-60 minute legs do not.
- Rules: long XAUUSD at T0, flat at T1 for (T0, T1) in {01:00, 01:30, 02:15} x {03:30, 05:00, 07:00} (9 cells), plus
  the same for XAGUSD (9 cells); OPEN vs XSHG-holiday days; executable as in the common construction.
- Extra out-of-sample era: Dukascopy H1 XAUUSD 2004-2015 (PRE; never used for this hypothesis), long 01:00-07:00
  (and the hourly profile), Chinese holidays from holidays.China (SGE existed since 2002). The window is chosen on IS
  2016-21 before PRE and VAL are read for this rule.
- Profile first (descriptive, not a cell): mean XAU return per 15-min bucket 22:00-10:00 UTC, OPEN vs HOL, IS/VAL.

### A1 minute profile (post hoc diagnostic, 2026-10-05 18:30 UTC; not a new cell)

XAU's rise sits inside the SGE AM auction minutes (bars ending 02:16-02:23 UTC), 9/9 years positive on OPEN days,
negative on Chinese holidays. It is the opposite of A1's ex-ante side, so A1 fails as registered; the flipped side
is reported only as "real but below cost" with its cost gap.

### A7 (post hoc, 2026-10-05 18:30 UTC, from the 15-min profile) Gold without Chinese buyers

- Seen in the profile: on Chinese-holiday weekdays (n 153, IS+VAL) XAU's 15-min buckets 00:45-04:30 UTC are almost
  all negative (cumulative about -8 bp), against about +1.5 bp on OPEN days.
- Mechanism (consistent with A2-flow's ex-ante "China is the net buyer in Asian hours"): when the Chinese venues are
  shut, the Asian session loses its structural bid while the rest of Asia/West still sells into thin hours.
- Rule: short XAUUSD at 01:00, cover at 04:30 UTC (fixed from the profile, IS+VAL both seen: this is post hoc and
  only a fresh era can confirm it) on weekdays that are XSHG holidays and IC quotes; variants excluded from the
  selection: 01:00-07:00. ~17 events a year -> DEMO tier at best.
- Confirmation: Dukascopy H1 XAUUSD 2004-2015 (PRE, unseen for this rule), short 01:00-05:00 UTC (hour bars) on
  Chinese holidays (holidays.China), against OPEN days; cost IC 2016-17 gold spread at those hours + 0.6 bp.
  Robustness: drop 1 Jan and days that are also NYSE/LSE holidays; per year; winsorised means.

#### A7 confirmation criteria (written 2026-10-05 18:40 UTC, after the IS/VAL numbers of A7, before PRE is read)

IS/VAL (seen): XAU short 01:00-04:30 on XSHG holidays, net +6.1 bp (t 3.3) IS, +6.2 (t 2.8) VAL, 9/9 years > 0,
~17 events/yr. Because the window was read off IS+VAL, it only counts if PRE 2004-2015 confirms it:
- PRE rule: Dukascopy H1 XAUUSD bid, short at the 01:00 UTC bar open, cover at the 05:00 UTC bar open, on weekdays in
  holidays.China (statutory + substituted days off) with bars at both ends; cost = 1.6 bp per trade (IC 2016-21 mean
  gold cost at these minutes incl. 0.6 bp commission); t is per-day (one event per day).
- Pass: PRE net > 0 with t >= 2.0, and OPEN days' same-window return not as negative (difference t >= 2).
- Placebo venues (descriptive, IS+VAL): the same short on weekdays that are holidays of Japan (XJPX), Hong Kong
  (XHKG), Korea (XKRX), Singapore (XSES), India (IN) or the US (XNYS) but NOT Chinese holidays. If those also fall,
  the mechanism is "Asian thin-liquidity holiday", not China.

## Outcome (2026-10-05 19:00 UTC)

No candidate, no PREREG draft. A1 has the wrong sign: XAU rises during the SGE AM auction (02:16-02:23 UTC, +0.9 bp,
t 7.9 IS / 4.5 VAL, absent on Chinese holidays), which is 0.3-0.65 bp below cost. A2-A5 have no cell net > 0 in both
IS and VAL. A7 met DEMO numbers on IS/VAL but failed the PRE check written above (2004-15 net -6.2 bp, t -3.3).
Write-up: scratchpad r10/A/STREAM_A.md.
