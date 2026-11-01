# Round 63 stream R: auction-cycle concession in sovereign bond futures (hypotheses)

Written 2026-10-31 15:50:54 UTC (from `date -u`), before any yield change around an auction was computed. HOLD
(2025-01-01..) stays closed: every series is cut at date <= 2024-12-31 at parse.

## What earlier rounds did (no repeat)
- Round 41 stream A parsed the auction calendars 2004-24 (US Treasury coupons / TIPS 1,621; JGB 1,358; Bund 1,088)
  and tested whether that supply moves **FX, gold and equity indices** (F1 concession / reversal, F2 heavy weeks,
  F3 result surprises, A2 auction-day mornings). It never computed a **bond yield or bond futures** return: the
  concession in the bonds themselves is untested. Reused here: its parsed `auctions.json` (cut at 2024-12-31).
- Round 46 stream P pulled daily yields 2004-24 (Treasury par curve, all tenors; MoF `jgbcme_all.csv`, all tenors;
  Bundesbank Svensson 10-year only) for a rebalancing signal; it used them as a signal and a 10Y bond leg, not around
  auctions. Reused here: the same raw files, re-parsed with the HOLD cut.
- New in this stream: the yield concession itself, traded as DV01 units of the matching futures contract.

## Mechanism
Dealers must absorb scheduled, pre-announced supply with limited balance sheet; they short / sell ahead and demand a
price concession, so the auctioned tenor's yield rises in the days before the auction and falls back after it as
inventory is distributed (Lou, Yan & Zhang 2013 RFS: ~2-3 bp for US 10Y from day -5 to the auction, reversing over
days after; Fleming & Rosenberg 2008 on dealer inventory; Beetsma et al. 2016 for euro-area auctions). Like gotobi,
a public calendar predicts a forced flow. The side is fixed by the mechanism: short the bond into the auction, long
after it.

## Data (no new pulls planned)
| item | source (already on disk) | use |
|---|---|---|
| US nominal coupon auctions 2004-24 (2/3/5/7/10/20/30Y; TIPS and FRNs out) | fiscaldata `auctions_query` via round 41 `auctions.json` | dates, tenor, offering amount, dealer share, bid-to-cover |
| JGB auctions 2004-24 | MoF xls via round 41 | dates, tenor, amount, tail (avg - lowest price) |
| Bund auctions 2004-24 (`Bund|10 Y` only, see below) | Finanzagentur via round 41 | dates, amount, tail |
| US par yields 2004-24, all tenors (CMT, ~15:30 ET quotes) | home.treasury.gov via round 46 | daily dy per tenor; 3M for carry |
| JGB par yields, all tenors (end of day) | MoF `jgbcme_all.csv` via round 46 (2025-26 rows dropped at parse) | dy per tenor; 1Y for carry |
| Bund 10Y Svensson yield (end of day) | Bundesbank BBSIS via round 46 (endPeriod 2024-12-31) | dy 10Y; ECB deposit rate (2014+) for carry |
Copies cut at 2024-12-31 go to `research/data/ust_auctions/` (yields.json, auctions.json) so the stream can be rerun
after scratchpads vanish.

Only the Bund 10Y yield is on disk, so Germany is tested on 10-year Bund auctions only (FGBL). Schatz / Bobl / Buxl
would need more Bundesbank series; the brief's allowed-host list does not name the Bundesbank, so I do not pull them
(listed as a coordinator decision). Japan: only the 10Y JGB future is liquid (OSE), so the tradable JP pool is 10Y
auctions only; JP all tenors is reported as information (cash JGBs), not a candidate.

## Timing
Auction results come before the yield fix used: US 13:00 ET vs CMT ~15:30 ET; JGB 12:35 JST vs MoF end-of-day;
Bund 11:30 CET vs Svensson end-of-day. So "auction-day close" (t0) is after the auction. Rules use only the calendar
(announced ~1 week ahead in the US, quarterly / annual in JP / DE), so a fill at the day's close is tradable at the
futures settlement (~15:00 ET for CBOT, about 30 minutes before the CMT quote: stated mismatch). t-k / t+k are
business days of the country's yield file.

## Return model (stated approximation)
A trade holds one DV01 unit of the future that matches the auctioned tenor. Return in **bp of yield**:
`long = -(y[t_exit] - y[t_entry])` in the auctioned tenor's par yield, short = the negative. Sharpe and t are
invariant to the DV01 scale; price bp ~= modified duration x yield bp (10Y ~ 8.5, e.g. 1 yield bp ~ 6-8 bp of a ZN
price). Pooled books are equal-DV01 per trade. Carry (unfunded futures, roughly): long earns
`(y_T - y_fin) x calendar_days / 365 / MD_T` in yield-bp terms, with y_fin = US 3M, JP 1Y, DE ECB deposit rate (0
before 2014, when the file starts); roll-down ignored (a few days; < 0.1 yield bp). Basis between the par yield and
the future's CTD is ignored.

## Costs: one tick + commission per side (commission $2.5 / EUR 2 / JPY 500 per contract)
| contract | tick | tick in price bp | +commission | CTD MD (approx) | yield bp per side |
|---|---|---|---|---|---|
| ZT (2Y, $200k) | 1/256 pt (since 2016; 1/128 before) | 0.39 | 0.52 | 1.9 | 0.27 |
| ZF (5Y) | 1/128 pt | 0.78 | 1.01 | 4.1 | 0.25 |
| ZN (10Y) | 1/64 pt | 1.56 | 1.78 | 6.2 | 0.29 |
| ZB (bond) | 1/32 pt | 3.13 | 3.35 | 11 | 0.30 |
| UB (ultra bond, 2010+) | 1/32 pt | 3.13 | 3.35 | 18 | 0.19 |
| FGBL Bund | 0.01 | 1.00 | 1.20 | 8 | 0.15 |
| OSE JGB 10Y | 0.01 | 1.00 | 1.05 | 7 | 0.15 |
Mapping: US 2Y, 3Y -> ZT; 5Y -> ZF; 7Y, 10Y -> ZN; 20Y -> ZB; 30Y -> UB (ZB before 2010). **Declared flat cost:
0.30 yield bp per side for every contract** (round trip 0.60), the max of the table, applied to every trade; the
cost x1.5 check uses 0.45 per side.

## Rules (fixed sides; small grid declared now)
Events: auction days per (country, tenor). Several auctions on one day in one pool are separate trades only when
their tenors differ (each its own yield); same tenor same day = one trade.
- **POSTh** (h = 1, 2, 3): long from t0 close to t+h close (yield falls after the auction).
- **PRE5-1**: short from t-5 close to t-1 close. **PRE5-0**: short from t-5 close to t0 close (concession incl. the
  auction day).
- **CYC**: PRE5-0 then POST3 (short t-5 -> t0, long t0 -> t+3; cost on both legs).
Pools: **US** (all nominal coupons), **JP10** (10Y JGB), **DE10** (10Y Bund), **ALL** = US + JP10 + DE10.
6 rules x 4 pools = 24 cells.
Conditioned cells (6), US and ALL pools:
- **SIZE-PRE5-0** and **SIZE-POST3**: only auctions whose offering amount is above the median of the same
  (country, tenor)'s previous 12 auctions (known at announcement).
- **WEAK-POST3**: only weak auctions, known at the result: US primary-dealer share of the competitive award above the
  tenor's previous-12 median (2004+ where reported); JP / DE tail (average minus lowest accepted price) above the
  previous-12 median. The rounds' data have no when-issued yields, so no WI-vs-stop-out tail for the US.
Total **30 cells**. **Primary cell declared: CYC-ALL** (the paper's full cycle). Secondary of interest: POST3-ALL.

## Eras and grading
PRE 2004-2015 (information), IS 2016-2021, VAL 2022-2024, HOLD closed. Entry date decides the era.
- Per trade: mean net yield bp, n. Book: daily equal-DV01 book of the cell (each trade's daily dy pieces; costs on
  entry / exit days), t by Newey-West (lag 10) on the daily book over all business days in the era; annual Sharpe of
  that book; share of years positive.
- Random benchmark: the same holds on random entry days that are not auction days of the pool's country (any tenor in
  that country) in the window, same count per (tenor, year), same tenor yield; 1,000 seeds; % of seeds with a lower
  mean net per trade.
- Chance: max IS t over the 30 cells under 200 random calendars (the same random draw used for every cell in a
  seed); report the median and p95 of that max.
- Robustness required by the bars: cost x1.5 and one step late (entry and exit one business day later).
- Bars as in the brief (LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, random >= 95 %, HOLD power >= 3;
  DEMO: IS t >= 2.0, VAL net > 0, random >= 90 %).

## Power arithmetic (before computing returns)
- Daily yield sd: US 10Y ~5-6 bp (2016-21), ~7-8 bp (2022-24); 2Y lower, 30Y similar. A 3-day hold has sd ~10 bp, a
  5-day ~13 bp, CYC (8 days) ~16 bp.
- Literature size (LYZ, 1980-2008): ~+2-3 bp into the auction, ~1-2 bp back after. Per-trade Sharpe at that size:
  POST3 ~0.10-0.15, PRE5-0 ~0.15-0.2, CYC ~0.2-0.25, minus 0.6 bp cost (~0.04 Sharpe).
- Trade counts per year: US ~84 nominal coupon auctions (2/3/5/7/10/30 monthly, 20Y monthly from 2020); JP10 12;
  DE10 ~12. ALL ~110 / year, but US auctions cluster in two weekly cycles (2/5/7 at month end; 3/10/30 mid-month) and
  their yield moves are highly correlated across tenors, so independent units are ~25-30 US clusters + 12 + 12 ~ 50
  a year -> ~90 in HOLD (1.83 years).
- LIVE: power = cluster Sharpe x sqrt(90) >= 3 needs a net cluster Sharpe >= 0.32, above the literature size for
  every rule except possibly CYC at the top of the range. **LIVE is reachable only if the effect is at or above the
  literature size and has not decayed since publication.** Equivalent: the daily book needs an annual net Sharpe >=
  ~2.2 for 1.83 years.
- DEMO: IS 2016-21 has ~300 clusters; IS t >= 2 needs a cluster Sharpe >= ~0.12, i.e. about half the literature size
  for CYC / PRE5-0. **DEMO is reachable if the concession survives at half its old size.**
- JP10 and DE10 alone (~12 / year, ~22 in HOLD): power <= 0.25 x sqrt(22) ~ 1.2, DEMO at most.
- HOLD data: the yield files end 2024-12-31; for a HOLD check the coordinator must pull 2025-26 Treasury par yields
  (home.treasury.gov), MoF `jgbcme_all.csv` rows 2025+, Bundesbank 10Y 2025+, and the 2025-26 auction calendars.
