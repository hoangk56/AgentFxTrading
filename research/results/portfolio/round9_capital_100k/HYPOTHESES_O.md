# Stream O hypotheses (S&P 500 index options, volatility risk premium, $100k at a listed-options broker)

Written before the numbers of each family were computed. Eras: PRE = start..2015-12 (design), CHECK1 = 2016-01..
2021-12, CHECK2 = 2022-01..2024-12. Every series is cut at < 2025-01-01 at load (fetch scripts). Excess returns are
over the 13-week T-bill (Yahoo ^IRX, discount rate; FRED is not reachable from this sandbox). The equity benchmark is
the S&P 500 total return index (Yahoo ^SP500TR, from 1988-01). Statistics: monthly (calendar month-end) returns for
Sharpe / beta / alpha, Newey-West (HAC) standard errors with 6 lags on monthly data; daily index values for the
mark-to-market max drawdown. Methodology facts per index: METHODOLOGY_NOTES.txt.

Shared bar for a slow premium (BRIEF point 5): net > 0 in PRE, CHECK1 and CHECK2 separately; HAC t of the net mean
excess return >= 2.5 over 1990/96..2024; majority of calendar years > 0; still > 0 at cost x1.5; and beats the obvious
benchmark at the same risk: alpha vs SPX TR (same beta) > 0 with HAC t >= 2.0, and Sharpe >= SPX's Sharpe
(same vol), both net of costs.

## O-A. Unconditional VRP (written 2026-10-05, before computing)

- **A1 VIX^2 vs realised variance.** Mechanism: investors pay for crash insurance; index option implied variance
  exceeds the expected realised variance (Carr & Wu 2009 "Variance risk premiums"; Bollerslev, Tauchen & Zhou 2009).
  Rule: on each trading day t, VRP_t = (VIX_t/100)^2 - RV_(t+1..t+21), RV = 252/21 * sum of squared daily log
  returns of the SPX close over the next 21 trading days. Report mean in variance units and in vol points
  (VIX - sqrt(RV)*100), the share of days/months with VRP > 0, by era, HAC t (lags 21 on daily overlapping data;
  also non-overlapping monthly samples at month-end). Same for VIX9D vs next 6 trading days (2011+) and VIX1D vs
  the next day's squared close-to-close return (2022-05+), as short-tenor comparisons.
  Success: mean VRP > 0 in every era with HAC t >= 2.5 in PRE and > 0 in CHECK1 and CHECK2.
- **A2 option-selling indices vs SPX.** Mechanism: same premium, harvested by systematic selling. Instruments:
  PUT (Yahoo ^PUT 1996-08..2006 spliced with CBOE 2007+, after checking the overlap), PUTY, WPUT, BXM, BXMD, BXY,
  CNDR, BFLY, CMBO; references PUTD, PUTVM, CLL, CLLZ, PPUT (a put BUYER), VXTH, RXM. For each: annual excess
  return, vol, Sharpe, beta and annualised alpha vs SPX TR excess with HAC t (monthly), worst month, max DD (daily),
  monthly skew, and episode returns: 2008-09-01..2008-11-30, 2018-02 (calendar month), 2020-02-19..2020-03-23,
  2022 calendar year. Alpha decay: alpha PRE vs 2016-2024, and the HAC t of the difference (dummy regression).
  Success (gross, at index prices): alpha > 0 with HAC t >= 2.5 over the full sample and > 0 in CHECK1 and CHECK2.
  Expected from the literature (Israelov & Nielsen 2015 "Covered calls uncovered"; Ungar & Moran 2009): put-write
  beats SPX on Sharpe pre-2015 with beta ~0.5-0.6; post-2015 alpha smaller.

## O-B. Realistic retail costs (written 2026-10-05, before computing)

- Commissions + fees per contract (METHODOLOGY_NOTES.txt): SPX $1.45, XSP $0.80, plus SEC fee $27.80 per $1M of
  sale proceeds. Contracts per $ of account: notional / (100 x SPX) for SPX, / (10 x SPX) for XSP.
- Bid-ask haircut: half the quoted spread as a % of each leg's premium, by leg type (ATM / OTM put 25-40 delta,
  wings 5-10 delta) and tenor (weekly / monthly), measured on a current CBOE delayed-quote snapshot of the SPX
  and XSP chains (cdn.cboe.com delayed_quotes; used ONLY for spread ratios, no levels printed; it is from
  2026-10, outside both the design data and HOLD). Spreads were wider before ~2010, so x1.5 and x2 are the stress.
- Premium per roll per leg (to turn % of premium into % of account) from the BS-from-VIX model of O-D, at each
  historical roll date.
- Index pricing conventions decide how much haircut applies on top of each index: VWAP indices (PUT, PUTY, BXM,
  BXMD, BXY, CMBO): 0.5 x half-spread (VWAP sits between mid and bid); mid indices (CNDR, BFLY): 1.0 x half-spread on
  every leg; bid index (WPUT): 0 at the base (already at the bid) plus commissions. Held to expiry and cash settled,
  so no exit cost unless a rule exits early (then a full half-spread at exit).
- Report gross and net Sharpe / alpha at haircut x1 / x1.5 / x2. Success: as the shared bar, net at x1 and > 0 at
  x1.5.

## O-C. Conditioning overlays (written 2026-10-05, before computing; design PRE only, CHECK1/CHECK2 once)

Applied to the PUT index (main) and CNDR and WPUT (secondary) as a timing overlay: decision at each roll date (the
index roll dates: 3rd Friday for monthly indices, every Friday for WPUT) from the PREVIOUS close's signal; ON =
hold the index until the next roll, OFF = hold T-bills. Costs as O-B are charged only when ON (no extra exits,
since decisions are at the roll). Literature: term-structure slope (Johnson 2017 "Risk premia and the VIX term
structure"; Simon & Campasano 2014), VRP level (Bollerslev, Tauchen & Zhou 2009), trend (Faber 2007; the
put-write drawdowns cluster in bear markets).
- C1 term structure: ON if VIX/VIX3M < 1 (VIX3M from 2009-09, so PRE design has only 2009-09..2015-12).
- C2 VRP level: ON if VIX - RV20 > theta, RV20 = sqrt(252/20 * sum of last 20 squared log returns)*100,
  theta in {0, 2, 4} vol points; theta chosen on PRE by net Sharpe.
- C3 trend: ON if SPX close > its 200-day simple MA.
- C4 combinations: C1 & C3, C2(theta*) & C3, C1 & C2(theta*).
Cells: 1 + 3 + 1 + 3 = 8 per index x 3 indices = 24. Selection: the PRE net Sharpe winner per index, and only
cells whose PRE net Sharpe beats the unconditional index by >= 0.10 move to the CHECK eras. Chance benchmark: for
each cell, 1,000 random ON/OFF sequences with the same ON fraction at the same roll dates (block-free, roll-level),
p-value of the PRE Sharpe gain; and E[max |t|] of 24 independent nulls ~ 2.0. Success: Sharpe gain > 0 in CHECK1 and
CHECK2, and the timed strategy itself passes the shared bar.

## O-D. Tail control and sizing for $100k (written 2026-10-05, before computing)

- Build a Black-Scholes repricer from VIX: sigma_ATM = a x VIX/100; sigma(K) = sigma_ATM x (1 - b x z),
  z = ln(K/F)/(sigma_ATM sqrt(T)), floored at 0.5 sigma_ATM; dividend yield from SP500TR vs SPX (trailing 252 d);
  r from ^IRX. Daily mark-to-market at the SPX close and VIX close. Sale at the roll-day average of SPX open and
  close with VIX close; settlement at the roll-day SPX open (proxy for the SOQ). Calibrate a on PUT and b on PUTY
  and CNDR over PRE only (grid a in {0.80..1.00}, b in {0..0.4}, minimise the mean monthly return error), then
  report the error (mean, tracking error, correlation of monthly returns) on PUT, PUTY, WPUT, CNDR, BFLY separately
  for PRE and CHECK1+CHECK2. Every result from this model is labelled APPROX.
- Constructions (APPROX unless a CBOE index exists): cash-secured ATM put (PUT), 2% OTM put (PUTY), 25-delta put,
  monthly put spread short 25-delta / long 10-delta, put spread short 2% OTM / long 7% OTM (sized so the max loss
  is 10 % / 20 % of the account per month), iron condor (CNDR), weekly ATM put (WPUT). Strike rule chosen on PRE
  by net Sharpe per unit of the 2008 + 2020 worst month (count the cells).
- Sizing at $100,000: leverage L = put notional / account in {0.5, 1, 1.5, 2, 3}; the number of XSP / SPX contracts
  at SPX = 5,000 and 6,000; expected annual return, max DD (mark-to-market), worst month; the leverage at which the
  worst 2008-like and 2020-like month costs 10 / 20 / 30 % of the account. Also Reg-T margin (broad-based index:
  15 % of underlying minus OTM amount, min 10 %) vs IBKR portfolio margin (needs >= $110k to open).
- Success for a "plan": the chosen construction passes the shared bar net of costs (or its CBOE index does) and a
  20 % account loss needs a move worse than the 2008 and 2020 months at the proposed size.

## O-E. Is it just equity beta? (written 2026-10-05, before computing)

- Compare every strategy (net) with SPX TR levered to the same beta (alpha with HAC t) and to the same vol (Sharpe,
  max DD, worst month at equal vol). Mechanism to reject: the put-write is a 0.5-beta equity position with a short
  crash option; if alpha ~0 net, it is beta plus negative skew.
- C3 correlation: C3's cTrader backtest trade CSV (research/results/portfolio/gotobi_cbot_trades.csv, net per trade
  at $50 risk, holidays dropped as the live bot skips them) aggregated to daily net by close date, 2016-01..2024-12
  only, correlated with the daily and monthly returns of PUT / the chosen construction. (The C3 CSV is allowed in
  full per BRIEF, but only 2016-2024 is used here to stay out of HOLD for the options side.) Expected ~0.

### O-D addendum (written after the first calibration, before the variant below was computed)
- First calibration (fixed skew) chose a = 0.875, b = 0.20 on PRE. Validation (out/D_validation.csv) shows the model
  overstates OTM-wing and weekly structures after 2015 (CNDR +0.34 %/month, BFLY +0.45, WPUT +0.65 / +0.35 with
  VIX9D) while PUT and PUTY stay within 0.05 %/month. Variant D-SK: scale b by (SKEW_t - 100) / (PRE mean of SKEW -
  100), grid a in {0.85, 0.875, 0.90} x b0 in {0.10, 0.15, 0.20, 0.25, 0.30, 0.35}, same PRE objective; adopt it for
  put-spread results only if its CHECK error on CNDR is smaller than the fixed model's. Cells for the model: 81 + 18.

### O-D construction cells (written before computing them)
- Correction: the selection metric cannot use 2020 (CHECK1). Strike/structure is chosen on PRE (1990-2015) by
  net annual excess return / |worst PRE month| (return per unit of tail; PRE's worst month is Oct-2008-like), with
  net Sharpe as the tie-break. 2008, 2018-02, 2020-03 and 2022 are then reported for the chosen cell and all others.
- Model: SKEW-scaled APPROX (a = 0.85, b0 = 0.15; out/D_calib_best_skew.json), weekly legs priced off VIX9D when
  available. Costs: XSP half-spread snapshot x1 on every leg (fills at mid -/+ half-spread; no VWAP discount since
  this is a retail order), XSP fees $0.80/contract. Monthly rolls on the 3rd Friday, held to expiry.
- Cells (11): cash-secured short put at L = 1: ATM, 2 % OTM, 5 % OTM, 25-delta, 10-delta; put spreads sized to a 10 %
  max monthly loss: 25/10-delta, 30/10-delta, 25/5-delta, 2 %/7 % OTM; iron condor 20/5-delta (CNDR rule); weekly
  ATM put (L = 1). The CNDR CHECK error of the model (+0.23 %/month optimistic) is the stated error bar for spreads.
- Exit rules (stop-losses) are NOT tested in this round: defined-risk spreads are the tail control.

### O-D addendum 2 (written before computing): a put spread from real index prices
- Synthetic 2 %/5 % OTM monthly put spread from two CBOE indices with the same roll day and VWAP pricing:
  excess return per $ of notional = (PUTY - T-bill) + (PPUT - SPX TR) (PPUT = SPX + long 5 % OTM put). Max loss ~3 %
  of notional per cycle; scaled x(0.10/0.03) to the 10 % max-loss sizing. Costs: XSP half-spread x1 at k = 0.5 on both
  legs (VWAP indices), from the model's premiums. Used (1) to measure the APPROX model's bias on a put spread
  (APPROX PS_P2_P5 at the same sizing, 1990-2015 and 2016-24), (2) as a real-price construction cell (1 cell).
