# Round 16: cross-border income conversion flows, and what each pending decision would unlock (2026-10-06)

Two streams from one brief ([round16_income_flows/BRIEF.md](round16_income_flows/BRIEF.md)), write-ups in
[round16_income_flows/](round16_income_flows/): W tested a new class of mechanism (income conversion with published
dates and a known side); X priced the user's pending decisions from the numbers rounds 3-15 already found (no new
returns computed).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** By arithmetic on everything found so far, no
effect reaches LIVE at IC's costs; the only decision that can lift any of them to LIVE-like power is a cost structure
without the 0.6 bp FX commission floor, and only if the Sydney-open dip stops shrinking.

## W. Income conversion flows
- Direct evidence is thin: Zheng (2023) finds the paying currency falls ~5-7 bp vs USD a few days after a country's
  top-5 % dividend days. A 1-5-day FX block has an sd of 60-450 bp, so the smallest detectable effect was ~10x that;
  written down before looking (02:28 UTC).
- 18 registered cells + 2 pooled: Swiss big-3 dividends (exact dates), Japan June / December dividend seasons (JPX AGM
  calendar; gotobi days and the Tokyo fix excluded), the euro-area May season, Australian miner and bank seasons, US
  refunding coupons, OAT / Bund redemptions, JGB redemptions on the 20th; held 1-3 days or at the 16:00 London fix.
- **None.** Best net IS t 1.52 (EUR falling into the fix in the May season, +0.37 / +1.72 bp per trade IS / VAL, and
  stronger in December than in May, so not a dividend effect). Largest |t| 2.28 is on the wrong side; a weekly sign-flip
  null has median 2.36. The refunding-coupon "USD falls into the fix" is a broad dollar move (it shows in every
  currency and reverses in PRE). Zheng's own strategy at IC's costs would be DEMO at best (power ~1).

## X. Decision value (computes no new returns)
58 rows, ~45 distinct effects real at mid in IS and VAL (rounds 3-15), each with its source, sd, cost, VAL/IS ratio
and whether its side was fixed beforehand. Count of LIVE-like / DEMO-like rows (numbers only, no control or latency
checks):

| cost scenario | LIVE-like | DEMO-like | best rows |
|---|---|---|---|
| IC as reported | 0 | 15 | J5c 2.83 (failed HOLD), Friday ECB slot 2.09, E1 1.87 |
| IC's VAL-era cost applied to IS (a bar change, not applied) | 0 | 18 | the index rows it was meant for fail on their small IS mid |
| no FX/metals commission (not an IC product; IC's commission-free account widens spreads) | 3 | 24 | ECB pre-fix slot every day 3.43, its Friday subset 3.05, J5c 5.06; E1 2.70 |
| half the spread, commission kept | 2 | 17 | J5c 3.15 |
| a low-cost venue (EURUSD/USDJPY 0.2 bp, AUD/NZD 0.3-0.4, XAU 0.6, US30 0.3) | 3 | 33 | the Sydney V legs (pre-leg 5.54, J5c 4.58, post-leg 3.29); E1 2.45 |

- **Decay decides it.** Registered non-gotobi rules kept 0.18-0.81 of their VAL mid in HOLD (C3 kept 0.88). At a
  venue cost, LIVE needs the Sydney pre-leg to keep >= 0.67-0.72 of its VAL size; its one HOLD reading (J5c) kept
  0.31. The ECB slot would need no decay at all.
- **Rare effects are capped by count, not cost** (power 0.6-2.0 under every scenario): gold settlement big days,
  month-end I, FOMC US30, US30 after 08:30 data, the Deribit Friday BTC fade, EURJPY at quarter-end.
- **Data decisions change no costs**, so none can create a LIVE row at IC's costs; their value is to confirm or kill
  mechanisms. Most useful: Dukascopy AUD/NZD M1 2004-15 (does the Sydney V predate 2016? mid t ~18 expected) and
  XAU/XAG M1 2004-15 (gold big days with leveraged ETFs from 2008-12 and a no-ETF placebo before; the LBMA drops; an SGE
  placebo, the auction started in 2016-04). New data after 2026-09-24 resolves a Sydney rule in 4-6 months at a venue
  cost, but E1 would take 3-13 years at IC's cost. Low value: EUR crosses / EM / softs at IC's cost, leveraged-ETF AUM,
  SGE premium, the IS-cost bar change, demo runs at IC's cost (except to measure real spreads).
- Caveat: VAL-size power is optimistic (many rows post hoc), rows overlap (E1 and the ECB slots; the Sydney legs), and
  the venue costs are assumptions, not quotes.

Full tables: [round16_income_flows/STREAM_X.md](round16_income_flows/STREAM_X.md); W:
[round16_income_flows/STREAM_W.md](round16_income_flows/STREAM_W.md).

## What this says
- A new mechanism class (income conversion) adds nothing measurable at 1-5 days: the published flows are a few bp in
  a 60-450 bp block.
- After sixteen rounds the ranking of the user's decisions is clear: a cheaper cost structure first (and only with the
  venue's own quote history to check the moves), Dukascopy AUD/NZD and XAU/XAG M1 2004-15 as the cheap way to price it,
  data after 2026-09-24 to resolve it. Everything else is low value for finding a LIVE algorithm.

## Directions that need the user's decision
As in X's ranking above, plus from W: company-level dividend calendars (Compustat / Bloomberg / Refinitiv) to rebuild
Zheng's top-5 % days (expected DEMO at best), EM pairs with concentrated dividend seasons (KRW April, TWD July-August).

## Process and disclosures
HOLD was not loaded (W's price lookups refuse 2025+; X loaded no prices). Network: OpenAlex / Semantic Scholar, the
Zheng thesis, JPX AGM-date history, dividend-history sites for Swiss payment dates; no prices downloaded. Scripts and
outputs in the scratchpad (`r16/W`, `r16/X`). Nothing in `research/` code was edited.
