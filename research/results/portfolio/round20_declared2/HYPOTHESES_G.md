# Round 20, stream G: hypotheses (index expiry settlement auctions and averaging windows)

Written 2026-10-06 04:06 UTC (`date -u`), before any return of this stream was computed. Nothing in this file was
chosen after looking at returns. HOLD (2025-01-01 onwards) is never loaded: the shared panel ends 2024-12-31 and the
bid-only caches (STOXX50, F40) are cut at ts < 1735689600000 at load. No PRE era (no index minute data before 2016).

Disclosure of what I had seen before writing this: the briefs required reading round 7 B (H5: STOXX50/F40/ES35/IT40
pooled, fade the 60-min move into the monthly settlement for 120 min after: +2.4 bp t 0.9 IS / -3.5 VAL), round 10 A5
(fade the JP225 SQ open: fails), round 11 H2 (fade the US SOQ: sign flips) and round 13 P / round 15 V (closing
auctions: real at mid, below cost). No DE40, UK100 or HK50 expiry-day number has been seen. The windows below are
taken from the settlement rules, not from those results.

## 1. Settlement rules and calendar (exchanges' own documents)

| index (IC symbol) | contract / settlement rule | settlement minute(s), local | expiry days 2016-24 | source |
|---|---|---|---|---|
| DAX (DE40) | Eurex FDAX (quarterly Mar/Jun/Sep/Dec) and ODAX (monthly): final settlement = index from the Xetra intraday auction prices; futures stop at the start of the 13:00 CET auction; on Eurex settlement days the DAX-stock intraday auction lasts 5 min instead of 2, random end | auction 13:00-13:05 (+ random end <= 30 s) Europe/Berlin | 3rd Friday; if not an exchange day, the exchange day before | eurex.com DAX Futures / DAX Options contract specifications; Deutsche Börse Xetra auction schedule ("On Eurex settlement days the intraday auction for DAX stocks has a duration of 5 instead of 2 minutes"). Rule in force before 2016 (the 13:00 auction replaced the opening-price settlement used to 1998; exact switch date not needed, constant over 2016-24) |
| FTSE 100 (UK100) | ICE Futures Europe FTSE 100 futures (quarterly) and options (monthly): EDSP = Expiry Value from the LSE EDSP intraday auction, which begins 10:10:00 and lasts 5-5.5 min (extensions to 10:29 at the latest) | 10:10:00-10:15:30 Europe/London | 3rd Friday of each month (FTSE 250 quarterly); preceding business day if not one | ICE "FTSE 100 Index Futures and Options Contracts" (EDSP note); LSE Market Notice N14/15 (15 July 2015): the EDSP auction stays at 10:10 (the 12:00 daily auction from Feb 2016 does not replace it). The brief's "10:15" is the auction's end |
| EURO STOXX 50 (STOXX50) | Eurex FESX (quarterly) and OESX (monthly): final settlement price = average of the index values calculated 11:50-12:00 CET; futures stop at 12:00 | average 11:50-12:00 Europe/Berlin | 3rd Friday; preceding exchange day if not one | eurex.com EURO STOXX 50 Index Futures / Options contract specifications |
| CAC 40 (F40) | Euronext FCE futures (monthly) and PXA options: EDSP = arithmetic mean of the index values disseminated 15:40-16:00 CET; trading in the expiring future stops 16:00 | average 15:40-16:00 Europe/Paris | 3rd Friday of the month; preceding business day if not one | live.euronext.com CAC 40 index future contract specification (FCE, 2019-06 PDF and current page). The brief's guess is confirmed |
| Hang Seng (HK50) | HKFE HSI futures and options (monthly; quarter months are only further-out listings): Final Settlement Price = average of HSI quotations at 5-minute intervals during the Last Trading Day (from 5 min after the start to 5 min before the end of the continuous session, plus the close) | whole day 09:35-15:55 + close Asia/Hong_Kong | Last Trading Day = the business day before the last business day of the month | HKFE Rules, Contract Specifications for HSI Futures and Options (hkex.com 01-hkferules-hsil.pdf); HKEX HSI futures product page |

Calendar rules used (built in code, printed with the results):
- European third Fridays 2016-01..2024-12; Eurex / Euronext / LSE closed on Good Friday, so the expiries of
  **2019-04-19 and 2022-04-15 move to Thursday 2019-04-18 and 2022-04-14**. No other third Friday 2016-24 is a
  holiday at these venues (third Fridays fall on the 15th-21st).
- Quarterly (Q) = March, June, September, December; monthly (M) = the other 8 months.
- HK: last business day of the month and the business day before it from the XHKG calendar (holidays 0.105,
  `r13/P/cal_P.json`); half days (24 Dec, 31 Dec, Lunar New Year's Eve) count as business days. Typhoon / black-rain
  closures are not in the calendar (not modelled; listed as a limitation).

## 2. Literature and the side

| source | market, settlement | finding used for the side |
|---|---|---|
| Stoll & Whaley 1987 (FAJ 43(2)) | S&P 500, close settlement 1984-85 | high last-hour volume on quarterly expiries; the market tends to fall into the settlement; price reversal the next morning (~0.4 % of the index in recent quarterly expiries) |
| Stoll & Whaley 1991 (FAJ 47(1)), 1997 (AJM 22(2)) | S&P 500 after the 1987 move to the open; Australia | the effects follow the settlement time; reversal after it |
| Schlag 1996 (EFM 2(1)) | DAX, settlement at the open (to 1998) | 3x volume on quarterly Fridays; return reversals significantly higher when the future expires at the open; no clear reversal for options expiring at the close |
| Chow, Yung & Zhang 2003 (JFM 23) | HSI, 5-minute average, 1990-99 | **negative price effect on the expiration day**, some volatility, **no abnormal volume and no price reversal after expiration** |
| Fung & Yung 2009 (JFM 29) | HSI average settlement | volume clusters at the 5-minute marks; no significant reversal; order imbalance does not predict next-day return |
| Alkebäck & Hagelin 2004 (AFE 14(6)) | Sweden, long (averaged) settlement period | high turnover, no significant price effect |
| Joensuu 2010 (Aalto MSc thesis) | EURO STOXX 50, average 11:50-12:00, 2000-09 (40 futures, 80 options expiries, 401 control days) | **intraday returns before expiration significantly higher and after expiration significantly lower on expiration days** (liquidity-driven, market-maker inventory) |
| Baltussen, Terstegge & Whelan 2024 (WP, "The Derivative Payoff Bias") | US a.m. (SOQ) settlement 2003-21 | prices drift **up** into the settlement and revert after it (+18.5 bp, t > 4.5); mechanism: option market makers' negative charm makes them buy the underlying into expiry, or manipulation in an illiquid pre-settlement window; no pattern at the p.m. (close) settlement; they cite the EURO STOXX 50 intraday average as the better design |
| Batrinca, Hesse & Treleaven 2020 (Empirical Economics) | 7 European indices | volume higher on futures and options expiration days (no price result) |
| Illueca & Lafuente 2006 (JFM 26); Agarwalla & Pandey 2013 (JFM 33); Xu 2014 (JFM 34) | Spain (average), India (average), Sweden | volatility / volume effects; price effects weak or absent under averaging |

Sides declared from these: (i) **up into the European settlement, down after it** (Joensuu 2010; the charm channel of
Baltussen et al. 2024); (ii) **fade the move into the settlement after it** (Stoll & Whaley's reversal, sign-free);
(iii) **follow the morning move into the settlement** (the brief's "pressure in the direction of the morning move";
the weakest prior: no paper here states it, declared because the brief names it); (iv) **HK: short over the
settlement day, no reversal** (Chow, Yung & Zhang 2003; Fung & Yung 2009).

## 3. Exact rules

Prices: p(T) = mid at the close of the bar ending at T (local clock, DST via zoneinfo), forward-filled up to 10 min
(first/last available quote), else the trade is dropped. DE40, UK100, HK50: panel mid (bid+ask)/2. STOXX50, F40:
bid close + published spread / 2 (bid-only caches). Return in bp = 1e4 ln(p(B)/p(A)).

Windows per European index (S = settlement window start, E = bar end that closes the settlement, close = cash close):

| symbol | tz | S | E | into window [A, B] | after-60 [A, B] | after-close [A, B] | morning signal (G3) |
|---|---|---|---|---|---|---|---|
| DE40 | Europe/Berlin | 13:00 | 13:06 | [12:00, 13:06] | [13:07, 14:07] | [13:07, 17:30] | 09:05 -> 11:59 |
| UK100 | Europe/London | 10:10 | 10:16 | [09:10, 10:16] | [10:17, 11:17] | [10:17, 16:30] | 08:05 -> 09:09 |
| STOXX50 | Europe/Berlin | 11:50 | 12:00 | [10:50, 12:00] | [12:01, 13:01] | [12:01, 17:30] | 09:05 -> 10:49 |
| F40 | Europe/Paris | 15:40 | 16:00 | [14:40, 16:00] | [16:01, 17:01] | [16:01, 17:30] | 09:05 -> 14:39 |

Rules (one trade per index per expiry day):
- **G1-in** (side fixed: long) over the into window.
- **G1-out60 / G1-outC** (side fixed: short) over after-60 / after-close.
- **G2-out60 / G2-outC** (conditional, fade): side = -sign(r_into), r_into = into-window return to E; trade after-60 /
  after-close. Entry one minute after E (the signal uses data to E only).
- **G3-in** (conditional, follow): side = sign(morning signal return, cash open+5 to A-1); trade the into window.
- **H1** (HK50, side fixed: short) on the HSI Last Trading Day, [09:31, 16:00] Asia/Hong_Kong (the averaging day; the
  window crosses the lunch break; no overnight).
- **H2** (HK50, conditional fade; the literature predicts nothing, it is the control for "no reversal"): next HK
  business day, side = -sign(H1-window return), [09:31, 10:31].

Day sets, separately: **Q** (quarterly expiries, 4 a year) and **M** (the other 8 months; for HK the same split by
calendar month). Pooled **EU4**: for each rule and day set, the equal-weight mean of the four European indices' net
returns on the day (one unit per expiry day).

Counted cells: 6 rules x 4 indices x 2 day sets = 48; EU4 pooled 6 x 2 = 12; HK 2 x 2 = 4. **Total 64.** Any "all
expiries (Q+M)" number is information only. Nothing else is counted; no window, symbol or rule is added after looking.

## 4. Costs, checks and bars

- Costs: half the actual spread at the entry minute + half at the exit minute (DE40, UK100, HK50, from the panel);
  STOXX50 1.5 points and F40 1.79 points per round trip (IC published, round 7 B). No commission, no financing (all
  windows intraday, close before 17:30 CET).
- Robustness for every cell: spread x1.5; both fills +1 minute (conditional sides keep the signal at the original
  time).
- Placebo: the same clock and rule on every non-expiry Friday that is a venue trading day (HK: every non-expiry HK
  trading day), excluding 24 Dec - 2 Jan; report the placebo mean and the expiry-minus-placebo difference t.
- Random-entry control (for cells that are net > 0 in IS and VAL): same expiry days, same window length, start minute
  uniform over the cash session (DE40/STOXX50/F40 09:05-17:30 CET, UK100 08:05-16:30, HK50 09:31-16:00) so that the
  window fits; side fixed for G1 / H, recomputed at the random time for G2 / G3 (r_into over the same length before
  the random start; morning signal to the random start); 500 seeds. H1 spans the session, so its control is the
  placebo days only.
- Statistics: t clustered by UTC day (one trade per day per cell, so per-trade t; EU4 per day). Effect by era (IS
  2016-21, VAL 2022-24) and by year; VAL/IS ratio. Power = per-trade net Sharpe x sqrt(1.73 x trades a year), on IS
  and on VAL size (the VAL column = expected HOLD t).
- Chance: per-UTC-date sign flips shared by all 64 cells (2,000 draws): max |t_IS| at mid and max IS net t (flipped
  mid - cost); also max of 64 normals.
- Data rule declared now: on Q days, if |1-minute mid return| at the minute ending E exceeds 50 bp (a CFD
  contract-switch artefact), the day is dropped from that symbol's cells and listed.
- Bars (round 13 brief): LIVE needs IS t >= 2.5, VAL t >= 1.5, >= 2/3 years > 0, random >= 95 %, power >= 3 (at 4-12
  events a year LIVE needs a per-trade Sharpe of 0.65-1.1; not expected). DEMO: IS net t >= 2.0, VAL net > 0, random
  >= 90 %, plus net > 0 at x1.5 and +1 min in both eras. A cell meeting DEMO -> PREREG_DRAFT_G_<name>.md, family
  stopped, HOLD not opened. C3 daily / monthly correlation (IS+VAL) for any cell net > 0 in both eras.

## Post-hoc additions (information only, cannot become candidates this round)

Added 2026-10-06 04:10 UTC (`date -u`), after the 64 counted cells, the permutation null and the random-entry control were
computed (no declared cell met DEMO: the cells with IS net t >= 2 fail the random control in VAL or IS), before the
numbers below:
- P1: per-year net and the weight of 2020-03-20 in the G1-outC Q cells; UK100 G1-outC Q with 2020-03-20 kept.
- P2: G1-outC Q split at the US cash open (09:30 New York, in UTC): [E+1, US open] and [US open, close], to see
  whether the post-settlement decline is the US third-Friday reversal (Baltussen, Terstegge & Whelan 2024) passing
  into Europe.
- P3: short the whole cash session (open+5 to close) on Q / M expiry days vs placebo Fridays, per index, by era and
  year (the random control showed Q days falling at all hours).
