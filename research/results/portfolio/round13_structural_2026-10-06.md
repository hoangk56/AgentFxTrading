# Round 13: structural (non-decaying) flows, structural calendars, the big-day flow mechanism elsewhere (2026-10-06)

Round 12 found that every flow anomaly that cleared IS/VAL, except gotobi, was weaker in VAL than in IS and weaker
again in HOLD. This round looked for effects with gotobi's property: same sign and similar size over decades because
they come from a fixed institutional practice. Three streams ran from one brief
([round13_structural/BRIEF.md](round13_structural/BRIEF.md)); hypotheses with UTC times before their numbers
(`HYPOTHESES_M/N/P.md`), write-ups `STREAM_M/N/P.md`, all in [round13_structural/](round13_structural/).

| stream | direction | why it might escape the limits |
|---|---|---|
| M | stability-first scan of FX and gold clock / calendar cells: discovery on PRE 2004-15 (Dukascopy), side fixed there, confirmation on IS and VAL | no earlier scan used PRE as the discovery era; 21 years of the same sign should select structural effects |
| N | structural calendar flows: US corporate tax days, Treasury coupon / bill / refunding settlements, bond-index month-end extension, fiscal-year ends, quarter-end funding, the Chinese tax deadline | law, settlement systems and index rules do not change when someone trades them |
| P | round 12's gold big-day settlement rule on oil, gas and ten index closes (top-decile day move, follow it into the close) | leveraged-ETF rebalancing is fixed by prospectus and proportional to the day's move |

## Answer

**No LIVE candidate.** One rule met the DEMO numbers on IS/VAL. The lead reproduced it with independent code
(exactly), registered it, and opened HOLD once:

| candidate | PRE / IS / VAL net per trade (t) | HOLD net (t) | verdict |
|---|---|---|---|
| E1: short EURUSD 11:00-13:00 London every weekday (into the euro's midday fall before the 14:15 CET ECB fix) | PRE mid +1.69 (5.2); IS +1.17 (3.29); VAL +1.35 (2.46) | **+0.64 (t 0.99)**, 444 trades; both fills 1 minute late: **-0.00** | **DEMO candidate**, weak |

Registration, code and output: [PREREG_M_eurusd_midday.md](round13_structural/PREREG_M_eurusd_midday.md),
`round13_structural/prereg_code/`.

| tier | candidates |
|---|---|
| LIVE | none |
| DEMO | E1 EURUSD midday short (this round) and L4-G-d gold settlement big days (round 12); both passed the registered "net > 0" HOLD rule with HOLD t below 1. Neither has a cBot; both await the user's decision |

E1 in brief:
- Mechanism: the euro weakens over the European midday into the V around the ECB fix (Ranaldo 2009; Breedon &
  Ranaldo 2013; Krohn, Mueller & Whelan 2024). It follows European local time (on a fixed UTC clock it is weaker).
- Its side has been the same since 2004 (11/12 PRE years, 5/6 IS, 3/3 VAL, 2025 > 0, 2026 to date < 0). Power is
  1.8-1.9, so LIVE is out of reach even if HOLD had matched VAL.
- Caveats: the plateau is narrow; in IS/VAL most of the edge sits in 12:45-13:00 London; in PRE it sat in
  11:45-12:00 (the slot moved at the 2015/16 boundary). In HOLD the edge vanishes with both fills one minute late,
  i.e. it sits in the entry or exit minute.
- Correlation with C3: +0.043 daily, +0.055 monthly.

## M. Stability-first scan (PRE discovery)
- K = 270,086 cells (11 symbols x 4 DST-aware clocks x 28 day types x windows). JPY windows overlapping
  23:00-02:00 UTC and anything touching 16:45-18:15 New York were excluded; no gotobi day types.
- PRE: max |t| 10.98; permutation 95th percentile of the max 5.46. 120 cells above it (set A), top 500 (set B).
- IS confirmation: 47 / 120 (chance 9) and 139 / 500 (chance 29); best IS t 5.08 vs 3.66. VAL: 47 of the 139 with
  t >= 1.5 (chance ~9). So stable effects exist, beyond chance.
- **But they shrink**: set B averages 2.01 bp in PRE, 0.35 in IS, 0.25 in VAL (IS/PRE 0.18, VAL/IS 0.72). Selecting
  on PRE does not avoid the winner's curse or the decay.
- **They are clock effects, not date effects**: 127 of the 139 confirmed cells are "every weekday" cells.
- Most are real and below IC's cost. Break-even / cost, IS / VAL, bp:
  - USDJPY long 11:00-13:00 London: 0.88 / 0.95 against 0.77 / 0.73;
  - USDCHF long 10:00-12:00 UTC: 1.0 / 1.1 against ~0.9;
  - GBPJPY long in the New York afternoon: 1.65 / 1.43 against 1.24 / 1.09;
  - EURUSD short 12:45-13:00 London (ECB pre-leg): 1.09 / 1.12 against 0.63.
- Others: gold before UK holidays (PRE +9.8, IS +6.7, VAL +1.5, decaying, beats 35-42 % of random entries); USD up
  into the Tokyo fix on non-JPY pairs (C3's mechanism, decaying).

## N. Structural calendar flows
- 58 cells (51 declared, 6 bills declared before their numbers, 1 post hoc). Calendars from IRS dates, fiscaldata
  Treasury auction records (net coupon settlement for 16 Sep 2019 = +$54 bn, as in Afonso et al. 2020), the
  Bloomberg index methodology.
- **None.** Chance: max |t_IS| 4.25 (wrong side) against a sign-flip null median 2.72 / 95th percentile 5.00.
  The best registered cell, long US30 the day after a large coupon settlement, is +27.9 bp (t 2.68, 6/6 years) in IS
  and -9.6 in VAL. Settlement size has no dose-response (|t| <= 0.95). The September-2019 repo mechanism is real in
  money markets but does not reach FX, gold or US30 at one day.
- No mechanism has the gotobi signature; cells near t 2 in PRE reverse later (US tax-day reversal +21.3 → +2.8 →
  -16.4). At 4-50 events a year with 35-100 bp sd, even DEMO is out of reach.
- Post-hoc observations (not registrable): the dollar fell over the last 3 business days of December in 6/6 IS years
  (-74 bp, t -4.25) and in VAL (-42), not in PRE; USDJPY rose into the Japanese 30 September half-year end in IS/VAL
  (opposite of repatriation); a "15th of the month" US30 effect was a month-composition artefact.

## P. The big-day close / settlement rule elsewhere
- 25 counted cells + 4 information cells (XTI, XBR, XNG settlements; US30, USTEC, JP225 at the TSE and OSE closes,
  DE40, UK100, HK50, AUS200 closes; pooled). The code reproduces gold's L4-G-d first.
- **None.** Gold's dose shape is found nowhere else. The IS scale-up of the indices is the > 3 sd bin, almost all
  March-April 2020 (pooled +21.8 bp, t 4.2 IS, -2.9 VAL); without 2020 the index top-decile mid is -1.8..+1.7 bp.
  In VAL the US indices reverse into the close on big days (USTEC 2-3 sd -11.6 bp, t -3.1). Round 4's "big days
  +10 bp" and round 12's L6 were the same 2020 tail.
- DE40 has a positive dose slope in both eras, but random windows on the same days earn as much: big-day trend, not
  a close flow. HK50 reverses into its close on big days in every IS year, not in VAL.
- Chance: best IS net t 1.93 vs a shared null 95th percentile 1.90 (that cell's VAL is negative).
- Post hoc: JP225 follows the day's move in the quarter-hour after the Tokyo cash close, +3.4 bp (t 5.6) in every
  IS year, +0.5-0.7 in VAL: structural-looking, decayed to a fifth.

## What this says
- **Stability across eras is real but rare, and it does not protect against shrinkage.** The PRE-selected cells
  confirm well beyond chance, but at a fifth of their PRE size; the one tradable survivor (E1) kept its IS/VAL size
  and lost a third of it in HOLD.
- **The surviving structural effects are daily clock effects of 1-2 bp**, at or just above IC's 0.6-1 bp cost, so
  their power is under 2 with one trade a day. That is the frontier again: LIVE needs about twice E1's net edge, or
  a cost structure without the commission floor.
- **Calendar dates set by law or index rules do not move FX, gold or US30 measurably** at 1-day horizons in this
  data; the variance of a day swamps them.
- **Leveraged-ETF big-day flows are a gold-only finding** so far; in indices the 2016-21 effect was the 2020 crash.
- **Two weak DEMO candidates now exist** (E1, L4-G-d). Each needs a demo to accumulate evidence under its registered
  stop / promotion rules; HOLD gave t below 1 for both.

## Directions that need the user's decision
1. Demo of E1 and/or L4-G-d (cBots not written).
2. Dukascopy M1 2004-15 for GBPUSD, AUDUSD, NZDUSD, USDCAD, AUDJPY, XAUUSD (PRE has only H1 for them, too coarse for
   15-minute clock effects), and Dukascopy index CFD history 2004-15 (USA30, USA500) for a PRE era on indices.
3. A commission-free EURUSD venue: E1 would net ~1.8 bp, power ~2.7, still short of LIVE.
4. External non-price data: daily leveraged-ETF AUM/units (TQQQ/SQQQ, UPRO/SPXU, 1570/1357...) to size the flow
   directly; intraday Treasury futures for the month-end extension; daily TGA / reserves / SOFR (allowed, low prior).
5. New data after 2026-09-24 as the only clean holdout (unchanged).

## Pitfalls (new)
- **Institutional clock timings move.** The euro's 13:00 CET drop and the ECB-fix V shifted 15 minutes at the
  2015/16 boundary; check sub-window slots by era before calling a window "structural".
- **2020 drives big-day results.** Always report big-day / tail-bin effects without March-April 2020.
- **Month-composition artefacts.** A day-of-month effect found in a subset of months must be checked on all months
  and on shifted days (N7).
- **Swap side.** A short-side random control must charge the short swap, not the long one (stream N fixed this).

## Process and disclosures
- HOLD was loaded only by the lead's registered script for E1, once, after registration. The streams never loaded
  it (panel ends 2024-12-31, loaders refuse 2025+, Dukascopy ends 2015).
- E1's window was picked on IS among PRE-carried cells with VAL in view (disclosed in the draft and registration).
- Network: Treasury fiscaldata auction records, IRS / ATO / index methodology pages, OpenAlex and Semantic Scholar
  (rate-limited), SSRN unreachable. No prices downloaded.
- Scripts and outputs of the streams stay in the session scratchpad (`r13/M`, `r13/N`, `r13/P`, listed in each
  STREAM file). Nothing in `research/` code was edited.
