# Round 63, stream V: hypotheses (crypto volatility risk premium, short delta-hedged Deribit straddles)

Written 2026-10-31 14:30 UTC (from `date -u`), before any option price, DVOL value or return in this stream was
computed. Data already on disk from round 34 (BTC option trades 2017-06..2024-12) has not been opened for prices yet.

## Mechanism
Option buyers on Deribit (retail upside speculation, miners / funds buying protection, structured-product hedging)
pay an insurance premium to option sellers: implied vol exceeds the realised vol that follows. A short straddle that
is delta-hedged with the perp earns, to first order, (implied variance - realised variance) x vega-like exposure and
carries no market beta. The premium is compensation for crash / jump risk (gap moves cannot be hedged daily), so the
tail is the point of the test, not a side issue. Round 9 found the S&P 500 VRP is mostly beta since 2015; the
crypto premium is said to be larger (DVOL minus realised has historically been positive by ~5-15 points), and the
delta hedge removes the beta, so the question is whether a hedged, cost-paying seller earns more than the cash rate on
its margin with an acceptable tail. Side is fixed: **always short vol**.

## Data (public, no key; all requests end <= 2024-12-31 23:59:59 UTC)
- Deribit BTC option trades 2017-06..2024-12 (round 34 pull, 16.5 M trades, monthly npz: time, expiry, strike, C/P,
  price (BTC), amount, taker direction, trade iv, index price, mark price, block / combo / liquidation flags). Read-only
  from round 34's scratchpad; the derived entry-quote tables are written to research/data/deribit/.
- Deribit ETH option trades: new pull, history.deribit.com `public/get_last_trades_by_currency_and_time`, **Friday
  windows only** (07:30-10:00 UTC, 2021-03..2024-12) to stay under ~45 min; >= 1.1 s between requests, back off on
  429 / 503, stop on 403. Plain UA, no personal data.
- DVOL (BTC, ETH) hourly, `public/get_volatility_index_data` (www.deribit.com), 2021-03..2024-12.
- Binance USDT-M perp 1h klines BTCUSDT, ETHUSDT 2021-01..2024-12 (fapi public), stored under
  research/data/deribit/binance_1h/ (stream's own data folder). Funding: research/data/binance/funding/ (local).
- Cash rate: research/data/rates/DFF.csv.

## Eras (data limit, declared)
DVOL starts 2021-03, so **IS = 2021-03-01..2022-06-30 (~69 weeks), VAL = 2022-07-01..2024-12-31 (~130 weeks)**,
HOLD 2025-01..2026-10 closed (never loaded). This is shorter than the round's crypto IS (2020-21). Option trade data
exists from 2017 for BTC, but DVOL does not, and V2 needs DVOL, so the same split is used for every cell.

## Rules (declared)
Common:
- Entry every Friday 08:30 UTC (just after the 08:00 weekly settlement). ATM strike = listed strike nearest the
  Deribit index at entry. Sell 1 call + 1 put (1 coin each).
- Tenor 7d: the expiry 7 days later (next Friday 08:00). Tenor 30d: the listed Friday expiry closest to 28 days
  (weekly or monthly); a new one is sold every Friday, so up to 4 overlap; each is held to expiry.
- Entry price per leg: Deribit mark of trades of that instrument in 08:00-09:00 UTC (mark at the trade nearest
  08:30). Sale price = mark x (1 - h), h = relative half spread estimated from trades (median |price - mark| / mark of
  trades in the same expiry, |log(K/S)| < 0.1, in the window). Fallback 1: BS at the median trade iv of same-expiry
  near-ATM trades in the window; fallback 2: BS at DVOL x (term ratio = IS median of ATM-iv / DVOL for that tenor).
  The share priced by each route is reported; the BS@DVOL error is measured against trade marks on the entries.
- Settlement: intrinsic at the Binance perp price at 08:00 on expiry (proxy for Deribit's 07:30-08:00 index TWAP;
  basis error stated).
- Delta hedge with the Binance perp: BS delta of the short straddle, iv = the entry iv scaled by DVOL(t) / DVOL(entry),
  rebalanced every 24 h at 08:30 (H1d) or every 4 h (H4h); first hedge at 09:00 (the hour after pricing), unwound at
  expiry 08:00. Perp funding paid / received on the hedge (Binance 8 h stamps).
- Costs: Deribit option fee min(0.03 % of underlying, 12.5 % of the option price) per leg at entry, plus the 0.015 %
  delivery fee (capped at 12.5 % of value) on the leg that expires in the money; half spread h at entry; perp taker
  0.05 % of traded hedge notional.
- Options are coin-settled; USD P&L equals a vanilla option's (payoff paid in coin at the settlement price). The
  account is treated as USD collateral (coin collateral's beta hedged away), stated as an assumption.
- Capital / margin: C = 0.5 x underlying notional at entry per open straddle (Deribit standard initial margin for a short
  ATM straddle is ~0.15 x S per leg + mark, ~0.3-0.35 x S; 0.5 leaves a buffer). Return = P&L / C;
  **graded series = excess over the cash rate: (P&L - C x DFF x days / 360) / C**. Weekly book P&L is marked to
  market Friday to Friday (BS at the scaled iv for open 30d legs).

Cells:
- **V1**: {BTC, ETH} x {7d, 30d} x {H1d, H4h} = 8 cells, always on.
- **V2**: the same 8 cells, trade only when DVOL(entry) - RV30(entry) > tau, RV30 = annualised realised vol of the
  trailing 720 1h log returns of the Binance perp to the entry hour. **Primary tau = 10 vol points**; tau = 0 is
  reported as a sensitivity and counted in the null. 16 cells.
- Total 24 cells. Max-over-cells null: weekly series recentred to mean 0, block bootstrap (4-week blocks) jointly across
  cells, distribution of the max t.

## Checks
- Net > 0 IS and VAL; costs x1.5; one step late (entry priced 09:00-10:00, hedge one bar late).
- t: Newey-West (4 lags) on the weekly excess series (30d book overlaps; 7d weeks are independent trades).
- Years positive (2021 Mar-Dec, 2022, 2023, 2024).
- Random benchmark: V1 = the same trade sold at a random weekday / hour (BS @ scaled DVOL pricing on both rule and
  random to keep pricing consistent), 500 draws; V2 = random subsets of weeks of the same size (shuffled signal),
  1,000 draws. VRP is unconditional, so V1 is not expected to beat random timing; reported anyway against the bar.
- Tail: worst weeks, 2021-05 (May 19 crash), 2022-06 (LUNA / 3AC), 2022-11 (FTX); worst week and max drawdown as % of C;
  peak capital; liquidation check (MTM loss > C - IM).

## Power arithmetic (before building)
Weekly P&L. HOLD 2025-01..2026-10 ~ 95 weeks. LIVE needs per-week net Sharpe x sqrt(95) >= 3 -> per-week Sharpe
>= 0.31 -> **annual Sharpe >= ~2.2 (x sqrt 52)**. IS t >= 2.5 over ~69 weeks needs per-week Sharpe >= 0.30 (annual
2.2); VAL t >= 1.5 over ~130 weeks needs 0.13 (annual 0.95). DEMO: IS t >= 2.0 -> per-week Sharpe >= 0.24 (annual
1.75), VAL net > 0. So both LIVE and DEMO require an IS annual Sharpe of ~1.8-2.2 on the excess series. Short-vol
books commonly show annual Sharpe 1-2 before tails, and one crash week of -5 to -10 sd collapses the sample Sharpe;
the 30d cells overlap (effective n smaller). Prior: V1 7d cells can reach DEMO only if the premium is large and
2021-05 / 2022-06 are survivable; LIVE is unlikely (~5 %). V2 halves n, so its IS t needs a per-week Sharpe of
~0.42 to reach 2.5 with ~35 weeks: LIVE ~3 %.

## Addendum, 2026-10-31 14:41 UTC (from `date -u`), written AFTER the BTC V1 / V2 results were seen
Seen so far (BTC only): the Friday 7d ATM straddle iv is ~0.85 x DVOL, about equal to trailing RV30, so the ATM
straddle carries almost no premium (V1 BTC net ~0, all 12 BTC cells fail). DVOL is a variance-swap-style index that
includes the wings, so the DVOL - RV gap (+11 pts IS, +7 VAL) may sit in the OTM options. One extra family is
declared now, before computing it, and is flagged as **chosen after seeing V1** (selection disclosed; it is added to
the max-over-cells null):
- **V3**: short a delta-hedged ~25-delta strangle instead of the straddle. Call strike = traded strike of the target
  expiry whose BS call delta (trade iv, at the entry index) is closest to +0.25; put strike = closest to -0.25. Same
  entry time, pricing routes (marks, then same-expiry trade iv), half spread (median |price - mark| / mark of trades
  within |log(K/S)| < 0.25 of the expiry), fees (cap at 12.5 % binds more often), hedge, capital C = 0.5 x S0,
  eras and checks. Each leg is marked at its own entry iv scaled by DVOL(t) / DVOL(entry). Cells: {BTC, ETH} x
  {7d, 30d} x {H1d} = 4 cells. No V2 filter on V3.
- Descriptive only (not graded): DVOL vs the realised vol of the following 30 days (the gross variance premium a
  variance swap would earn) per era.
