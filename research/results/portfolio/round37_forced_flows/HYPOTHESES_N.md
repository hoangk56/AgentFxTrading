# Round 37, stream N: hypotheses (Stock Connect quota flows between mainland China and Hong Kong)

Written 2026-10-29 09:37 UTC (`date -u`), before any flow series was joined to a return. At this time only the
unconditional sd and cost of each hold window (no signal) and a 2018-03-05 smoke test of the fill code had been
computed. Additions after this time are marked with their own `date -u` time; post-hoc ones are labelled.

Bars: research/PROMPT.md, LIVE and DEMO only (no RELAXED). Eras: IS 2016-01..2021-12, VAL 2022-01..2024-12, HOLD
2025-01..2026-09 closed (every Eastmoney query filtered `TRADE_DATE <= '2024-12-31'`, the parser drops later rows, IC
prices cut at ts < 2025-01-01). PRE: the flows start 2014-11 but IC HK50 / JP225 / US500 start 2016-01 and Dukascopy
has no HK index, so there is no PRE for the index targets; AUDUSD PRE would be 14 months only and is not run.

## Sources
- East Money data center, `RPT_MUTUAL_DEAL_HISTORY` (https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_DEAL_HISTORY&columns=ALL&filter=(MUTUAL_TYPE="00x")(TRADE_DATE<='2024-12-31')):
  MUTUAL_TYPE 001 Shanghai northbound, 003 Shenzhen northbound, 005 northbound total, 002 / 004 / 006 southbound via
  Shanghai / Shenzhen / total. Daily NET_DEAL_AMT (net buy, RMB / HK$ mn), BUY_AMT, SELL_AMT, DEAL_AMT (turnover),
  QUOTA_BALANCE (daily quota left), from 2014-11-17 (Shenzhen from 2016-12-05).
- `push2his.eastmoney.com/api/qt/kamt.kline/get` timed out at 60 s on the first probe (09:34 UTC); one retry allowed.
- Index-inclusion dates (pre-announced by MSCI / FTSE Russell / S&P DJI months ahead; implementation as of the close
  of the review's last business day): MSCI China A 2.5 % steps effective 2018-06-01 and 2018-09-03 (closes
  2018-05-31, 2018-08-31), 5 -> 10 -> 15 -> 20 % effective 2019-05-28, 2019-08-27, 2019-11-26 (closes 2019-05-27,
  2019-08-26, 2019-11-25); FTSE Russell tranches effective 2019-06-24, 2019-09-23, 2020-03-23 (closes 2019-06-21,
  2019-09-20, 2020-03-20); S&P DJI 2019-09-23 (same close as FTSE's 2nd tranche). The exact closes are checked against
  the northbound flow (the biggest net-buy days should sit on them) before any return; any date that the flow does
  not confirm is reported, not silently moved.

**Publication time assumed.** Northbound daily totals are final at the 15:00 Beijing close (07:00 UTC; they were
published in real time until 2024-05 and as daily totals until 2024-08-16). Southbound totals are final after the HK
closing auction (16:10 HKT, 08:10 UTC). Both are taken as public by **09:30 UTC**; every daily-flow trade is signalled
at the 09:30 UTC bar and filled at the close of the next bar (+1 minute; +2 minutes in the latency variant).

**The 2024-08 publication stop.** From 2024-08-19 HKEX / the exchanges publish only northbound turnover, not net buy.
So (a) the northbound VAL era is 2022-01..2024-08-16; (b) a northbound net-flow rule **cannot run forward** at all: it
is graded for information only and cannot be LIVE or DEMO, whatever its numbers. Southbound net buy is still
published daily, so southbound rules are tradable forward.

## Mechanism and why it might escape the limits
Southbound buying (mainland investors into HK stocks) is a large, persistent flow (2020-24 a two-digit share of HK
turnover) with a hard daily quota and its own holiday calendar. Its closure on HK trading days during mainland
holidays removes a known buyer on dates published a year ahead (a rule-driven absence). Northbound flow is the
"smart money" series; round 35 (Taiwan) found that investor-type flows co-move with the same day and do not predict
the next. Each daily-flow cell is reported with its same-day and next-day correlation so co-movement is not mistaken
for prediction.

## Power arithmetic (before any return; IS unconditional, no signal)
HOLD ~1.73 years, ~425 HK trading days. LIVE needs per-trade net Sharpe x sqrt(HOLD trades) >= 3.

| target / hold | sd (bp) | round-trip cost long (bp, incl. swap) | LIVE net edge at k0 (all days, Sharpe 0.146) | at k1 (~1/3 of days, Sharpe 0.25) |
|---|---|---|---|---|
| HK50 next HK day session 01:30 -> 07:59 UTC | 86 | 3.3 | 12.6 | 21.5 |
| HK50 D 09:30 -> D+1 07:59 (h1) | 118 | 6.2 | 17.2 | 29.5 |
| HK50 h3 (to D+3 07:59) | 200 | 11.3 | 50 (non-overlap count 142, Sharpe 0.25) | 86 |
| HK50 last 30 min 07:29 -> 07:59 | 17.9 | 3.3 | 2.6 net (mid ~5.9) | 4.5 net |
| USDCNH h1 / h3 (09:30 -> 09:30) | 26.9 / 45.4 | 2.2 / 4.2 | 3.9 / 11.4 | 6.7 / 19 |
| AUDUSD h1 / h3 | 60 / 104 | 1.5 / 2.8 | 8.8 / 26 | 15 / 45 |
| JP225 h1 | 126 | 5.6 | 18.4 | 32 |
| US500 h1 | 103 | 4.5 | 15.1 | 26 |

A next-day correlation of ~0.15-0.25 between a flow z-score and the return is needed. The literature and round 35
point to <= 0.05 for investor-type flows on the next day. **Prior: N1 LIVE ~1 %, DEMO ~3 %.**

Event families (Connect calendar, quota, inclusion) have ~4-8 events a year: HOLD ~7-14 events, so LIVE power
would need a per-event Sharpe ~0.8-1.1: **impossible by count; DEMO is the most an event family can reach.** The
inclusion steps (N6) have no forward events after 2020 (MSCI froze at 20 %, FTSE finished 2020): information only.

## Protocol (all families)
- Fills: IC M1, buy at the ask close, sell at the bid close of the fill bar; exit at the close of the exit bar.
  Variants: spread x1.5; +1 minute on both legs.
- Costs: actual spread at both fills; commission 0.6 bp for FX; swap per 17:00 NY rollover from
  `research/swing/rates.swap_frac_at` (HK50 uses USD rate under the peg, as the module does); USDCNH swap =
  (r_USD - 2.5 %)/360 minus the mean calibrated FX markup (CNH rate approximated, stated; USDCNH also reported ex swap).
- USDCNH prices: M1 rebuilt from IC ticks 2016-01..2024-12 in the scratchpad (3.19 M minutes).
- t: per trade for non-overlapping holds (one per day: day-clustered by construction); Newey-West lag h for
  overlapping h3; event families clustered by event block.
- Random control: circular shift of the flow series against the price dates (shift >= 130 trading days, 300 draws,
  side recomputed from the shifted signal); events: 300 sets with every event moved to a random HK trading day
  within +-40 HK days (outside event windows), same hold length.
- Chance: max |t| of K normals for each family, K = the family's counted cells.
- Results with and without 2020-03/04.

## Families and counted cells

### N1 Southbound net buy -> HK50, follow (tradable forward) — 8 cells
- Signal: x_D = NET_DEAL_AMT of MUTUAL_TYPE 006 (southbound total) on HK date D. z_D = (x_D - mean of the previous 60
  southbound days) / their sd (needs >= 40 prior days). Side = sign(z_D): long HK50 when mainland investors bought
  more than usual, short when less (price pressure persists / continues as the flow is persistent).
- k0: every day, side sign(z). k1: only |z| > 1.
- Holds: S = next HK day session (D+1 01:30 -> 07:59 UTC); h1 = D 09:30 -> D+1 07:59; h3 = D 09:30 -> D+3 07:59
  (HK trading days). That is 6 cells.
- N1c: z_{D-1} -> HK50 last 30 min of the HK session on D (07:29 -> 07:59 UTC), follow, k0 / k1 (2 cells). Mechanism:
  southbound buying is persistent and concentrated in the closing auction.

### N2 Northbound net buy -> follow (information only: not published after 2024-08-16) — 18 cells
- x_D = NET_DEAL_AMT of 005 (northbound total) on mainland date D; z as in N1. Side follow: long HK50, short USDCNH
  (northbound buyers buy CNH), long AUDUSD, long JP225, long US500 when z > 0.
- Cells: HK50 {S, h1, h3}, USDCNH {h1, h3}, AUDUSD {h1, h3}, JP225 h1, US500 h1 = 9 targets x {k0, k1}.
- VAL = 2022-01..2024-08-16.

### N3 Co-move vs predict (diagnostic, no cells)
- corr(z_D, same-window return) and corr(z_D, next-window return) for N1 / N2 series and targets, IS and VAL. Same
  window for HK50 = D-1 07:59 -> D 07:59 (HK close to close); FX = D-1 09:30 -> D 09:30.

### N4 Connect-closed days (calendar rule; dates published a year ahead) — 5 cells
The calendar is taken from the data (a HK trading day with HK50 day-session bars and no southbound record = southbound
closed; a mainland trading day with no northbound record while HK is closed = northbound closed). These dates were
known in advance, so using them is not look-ahead.
- E1: short HK50 from the close (07:57 signal, 07:58 fill) of the last southbound-open HK day L before a
  southbound-closed block to the 07:59 close of the block's last southbound-closed HK day (capped at 5 HK days).
  Mechanism: the persistent buyer is absent.
- E2: short HK50 over the day session of L (01:30 -> 07:59). Mechanism: mainland holders who cannot trade through the
  closure cut exposure on the last open day.
- E3a: long HK50 from the close of the block's last closed HK day to the close of the reopening day R. E3b: long HK50
  over R's day session (01:30 -> 07:59). Mechanism: pent-up southbound demand on reopening.
- E4: long USDCNH from 07:00 UTC of the last northbound-open mainland day before a northbound-closed block (HK holiday,
  mainland open) to 07:00 UTC of the block's last day (capped at 5 days). Mechanism: northbound CNH demand absent.
  Expected ~0.
- Placebo (not counted): E1 / E2 structure on US (NYSE closed) and Japanese (TSE closed) holidays when HK trades.

### N5 Quota pressure — up to 4 cells, only if the count allows
- Event: QUOTA_BALANCE < 10 % of the day's quota on a southbound (006 via 002 / 004) or northbound (001 / 003) leg.
- Counted only if IS has >= 20 such days per direction; else reported as a count. Cells: south -> HK50 h1 follow,
  north -> HK50 h1 / USDCNH h1 / AUDUSD h1 follow.

### N6 Index-inclusion steps (information only; no forward events) — 3 cells
- 8 implementation closes D (above). C1: short USDCNH D-3 09:30 -> D 07:00 UTC (pre-funding CNH buying). C2: long
  USDCNH D 07:00 -> D+3 07:00 (unwind). C3: short HK50 D-3 09:30 -> D 07:59 (EM funds sell HK-listed China to fund
  A-share buys). n = 8: a DEMO t needs ~1 sd per event.

### Fallback (declared now, run if the above fail): N7 quarter-end mainland fund window dressing via southbound — 2 cells
- Mainland mutual funds disclose holdings at quarter-end prices (rule). Q1: long HK50 from the close 4 HK days before
  the quarter's last HK day to that last day's close (~4 events / year). Q2: short HK50 over the first 2 HK days of
  the new quarter (close to close). Flow check first (is southbound net buy higher in those windows? flow only).

Counted cells: N1 8 + N2 18 + N4 5 + N5 <= 4 + N6 3 + N7 2 = <= 40. Chance (max of 40 normals): median ~2.5,
95 % ~3.2.

## Addendum 2026-10-29 09:46 UTC (`date -u`), after N1-N6 were graded, before N7 is computed
- N6 date check (flow only, as declared): the 2018 and FTSE closes are local northbound peaks, but the declared 2019
  MSCI closes (05-27, 08-26, 11-25) are not; the flow peaks are one day later (05-28 +5.6, 08-27 +11.3, 11-26
  +21.4 bn, rank 3 of 1,391 IS days), i.e. MSCI implemented as of the close of 28 May / 27 Aug / 26 Nov 2019. N6 is
  reported as declared and with these flow-confirmed dates (both labelled).
- N5 is not graded: only 6 IS days (all 2016-07, Shanghai southbound) meet the quota-pressure test, 0 VAL; < 20.
- **Post-hoc observation (not a hypothesis, not graded):** E3b on the declared long side loses (IS -32 bp), so the
  reopening-day session is weak, the opposite of the pent-up-demand story. It is reported for information only: the
  side would be chosen after looking, and there is no unseen era with HK50 prices except HOLD.
- N7 runs unchanged as declared above (Q1 long HK50 over the last 4 HK days of each quarter, Q2 short over the first 2
  HK days of the new quarter), with the flow check first and a local random control (300 draws, +-40 HK days).
