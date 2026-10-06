# Round 22, stream R: triage of every open idea from rounds 3-21

Written 2026-10-06 05:25 UTC (`date -u`), before any round-22 return was computed.

## Step 1: collection
Every report and STREAM file of rounds 3-21 was read in full (rounds 3-9: 14 files; 10-12: 15; 13-16: 15; 17-21: 15),
listing everything a "next round", "untested", "directions", "information only", "post hoc", "lead" or "needs the
user" passage left open, plus effects described as real but below cost. **About 330 lines** came out (many are the
same effect seen in several rounds; after merging duplicates, ~190 distinct ideas). The per-file reading was split
across four read-only helper passes (rounds 3-9, 10-12, 13-16, 17-21); their lists are condensed into the drop table
and the survivor table below.

## Step 2: drops
| reason | count (distinct) | examples |
|---|---|---|
| needs a user decision (new price data, new symbols, paid data, VPS, venue / commission-free account, bar change, demo) | ~70 | E1 / gold big-day demos; Sydney V, ECB slot, SGE, LBMA silver/gold at a cheaper venue; Dukascopy M1 for GBP/AUD/NZD/CAD/XAU/XAG and index CFDs 2004-15 (N2a US30, US500 Monday reversal T3, H3 FOMC US30 close, I12 US30 08:30, quarterly-expiry Fridays); data after 2026-09-24 (K4 BTC Deribit Friday, X6c oil->US500, F15 on the 15th); USDCNH ask ticks (CFETS 16:30 close); new symbols (USDSGD/HKD/MXN/ZAR fixes, Norges Bank, EM dividend seasons, KOSPI LETF, single stocks, softs); paid data (Zheng dividends, Deribit OI, LETF AUM, SPX dividend payment dates, CME TAS, SGE premium, intraday VIX, real OFI sizes); US30 post-close fade (needs "IS at today's cost"); MTV tightening switch (fed-funds-futures shock) |
| already tested in a later round (JOURNAL) | ~45 | FOMC-day carry (r7 C -> r20 F), other Fed events (r20 -> r21), CNH home hours (r7 -> r12 L7 -> r19 H), E1 analogues (r19 H), home-holiday asymmetry (r10 B), M1 (r3 -> r7 PRE), residual reversal R2b/R3b (r8 PRE), settlement big days elsewhere (r12 -> r13 P), DE40 close dose (r13 -> r17 Z), weekend gap fade (r19 T), Monday/Tuesday, crude weekdays (r19 T), dividend/coupon/redemption flows (r16 W), clock books and E1 selectors (r14), short windows (r15), pre-FOMC / announcement premia (r3, r19 T), turn of month (swing v2), EIA follow-through (r6), Treasury auction concession at 13:00 ET in IS/VAL (r4) |
| post hoc, only evidence is the data that suggested it (r18: such picks keep ~1/4) | ~55 | USD on the 15th (F15, 6-pair basket), CPI-week split, T8/G5 CHF gotobi-adjacent, Friday ECB slot, GBPJPY 10:28 month-end, ECB rebound, ECB fix at month-end, press-conference fade, H3 FOMC US30 short, US30 08:30 continuation, US30 open OFI draft, A7 gold Chinese holidays, J5c, gold on FOMC days, Jackson Hole, minutes-day dollar, year-end dollar fall, USDJPY into the JP half-year end, Q-day fall before the US open, M-day European rise, US big-day reversal in VAL (0DTE), HK50 big-day reversal, XTI overnight continuation, energy Friday continuation, metals Friday quote, macro residual momentum, VAL-only W / I / G / T cells, unremarked pinning cells |
| below cost with no new execution on existing data / killed in their own round / method notes | ~20 | price-only OFI (0.01-0.06 bp per z), sub-minute lead-lag, adaptive periodicity, cost-gated FX book, index MOC / AUS200 auction, gold settlement siblings, LBMA AM, decayed legs (JP225 after close, GBPUSD month-end WM/R, gold before UK holidays), method notes (RC-B controls, winner's-curse discount, 2024 dip) |

## Step 3: what survives (not user-gated, not tested as such, side from a mechanism or the literature)
Size vs cost from round 10's frontier (STREAM_D_outputs.md: edge needed = cost + Sharpe x sd of the hold). Power =
per-trade (or per-day) net Sharpe x sqrt(1.73 x events/yr); "decay-adjusted" multiplies the expected size by 0.65
(the lowest retention of a declared rule in round 18) for unseen effects and by 0.25 for effects whose IS/VAL were
already seen when the idea was formed.

| # | idea | source | mechanism | side (origin) | events/yr | expected size vs cost (bp) | power full / decay-adj. | data | priority |
|---|---|---|---|---|---|---|---|---|---|
| R1 | **Equity premium earned in even weeks of the FOMC cycle** (Cieslak, Morse & Vissing-Jorgensen 2019, JF) | r21 STREAM_U "Considered and not declared" | Fed news reaches markets on a biweekly Board-meeting cycle; accommodating news lowers the premium | long US indices in weeks 0, 2, 4, 6 (paper) | ~125 index-days | even-week day ~+2x the unconditional mean (~+10 bp) vs ~0.5-2 bp spread + 2 bp swap; daily sd ~110 | ~1.3 / ~0.8 | US500/US30/USTEC 2016-24 (no PRE) | **1**: unseen in every era, cost ~1/30 of sd |
| R2 | **Next-day FX reversal stronger after abnormally low volume** (Cespa, Gargano, Riddiough & Sarno 2022, RFS) | r12 STREAM_K "near-tested" (Cespa et al. 2022) | volume reveals asymmetric information; low-volume moves are liquidity moves that revert | against day d's return on low abnormal-volume days (paper) | ~580 pair-days (~250 days) | ~2-4 bp per trade vs ~1.2-1.6 bp (spread + 0.6 + one swap); daily sd ~50 | ~1.5 / ~1.0 (per day) | IC tick count 2016-24; Dukascopy H1 volume 2004-15 (PRE) | **2**: unseen, PRE available, high count |
| R3 | High-yielder bought into the Wednesday triple rollover (W1 "into" variant) | r3 W1 row; STREAM_X F27 | carry seekers buy before the 3-night swap is credited at 17:00 New York | long the higher-rate currency 12:00-16:55 NY Wednesdays (mechanism) | 52 | IS/VAL seen: +2.2 / +1.4 vs ~1.2 | ~0.5 / ~0.1 | Dukascopy M1 2004-15 unseen | 3: PRE is an unseen era; cannot be registered (IS net t ~1.4 seen) |
| R4 | Treasury-auction concession seen in USD (Lou, Yan & Zhang 2013) | r4 external-data table; STREAM_X F29 | dealers absorb supply: yields rise into auctions and fall after; USD follows US yields | USD up into 10-year auctions, down after (mechanism) | ~10 | IS/VAL seen for related cells: +4.5/+1.0 (13:00), +7.3/+22.7 (week before) vs ~1 bp; 4-day sd ~100 | ~0.5 / ~0.1 | Treasury auction calendar (fiscaldata.treasury.gov, official), Dukascopy M1 USDJPY/EURUSD 2004-15 unseen | 4: PRE unseen, count-capped (DEMO at most) |
| R5 | EURJPY short 05:00-07:00 London on the last weekday of a quarter | r14 STREAM_Q, STREAM_X F15 | none stated (Japanese quarter-end repatriation is a guess) | PRE scan | 4 | PRE +10.7 / IS +8.65 / VAL +9.55 vs 1.1 | 1.1-1.3 / ~0.4 | all eras already seen | low: every era seen; only a random control is missing (information) |
| R6 | Dose test of refunding coupons into the fix (W7b with coupon amounts) | r16 STREAM_W Directions #3 | coupon receivers sell USD at the fix | short USD (literature) | 4 blocks | +1-2 bp per trade, PRE sign opposite | <0.4 | Treasury data (official) | low: PRE contradicts |
| R7 | Reserve-scarcity conditioning of settlement-day effects (TGA / reserves) | r13 STREAM_N Directions #4 | reserve drain matters more when reserves are scarce | as N2a | ~12 | base effect failed VAL, no dose response | <0.5 | fiscaldata DTS | low |
| R8 | VIX settlement Wednesdays (Griffin & Shams 2018) | r12 STREAM_K #28 | SOQ manipulation | no index-price side in the paper | 12 | n/a | <1 (stream K) | existing | dropped: no side |
| R9 | BoJ ETF purchases on morning-drop days (Ko 2026; BIS WP 1029) | r19 STREAM_T #22 | BoJ afternoon buying | long JP225 afternoon (paper) | 30-100 | n/a | n/a | BoJ daily purchase data | dropped: programme ended 2024-03, cannot be traded in HOLD or live |
| R10 | Treasury Monday borrowing-estimate release (Wang & Zhao) | r21 STREAM_U | fiscal-uncertainty premium in Treasuries | no FX/index side in the paper | 4 | n/a | n/a | existing | dropped: no side on IC symbols |
| R11 | GBPUSD 11:00-13:00 London short (E1 window on GBP) | r13 STREAM_M | none (GBP has no ECB fix; r19 H found no GBP home-fix effect) | PRE scan | 254 | +0.20 / +0.76 / +1.65 vs 0.8 | <0.5 | H1 PRE exists | dropped: no mechanism |

No surviving idea has a full-size power of 3; the best (R1, R2) are about 1.3-1.5 at full size. **No idea in the
residual list can reach LIVE even if real; R1 and R2 can reach DEMO numbers.** This matches the round-16 decision
table: everything with enough events is below IC's cost unless a user decision changes the cost.

## Step 4: what is tested
R1-R4 (four families), declared in full in HYPOTHESES_R.md before any return. R1 and R2 are unseen in every era and
can produce a DEMO draft; R3 and R4 are declared tests of a mechanism side on the unseen PRE era (2004-15) and are
stated in advance to be information only whatever they show, because their IS/VAL relatives were seen in rounds 3-4
and fail DEMO's IS t.
