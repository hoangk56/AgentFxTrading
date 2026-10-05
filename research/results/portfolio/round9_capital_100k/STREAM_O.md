# Stream O: index options, the volatility risk premium, for a $100,000 account

Read BRIEF.md first. This is a NEW venue for the repo (listed options at a broker such as IBKR; cTrader and IC have
no options). No option data exists in the repo. Question: is selling S&P 500 index volatility (puts, put spreads,
condors, covered calls) a sound strategy for $100k after realistic retail costs, how should it be sized and
filtered, and how bad are the tails?

## Data (public, free)
- CBOE strategy benchmark indices, daily: https://cdn.cboe.com/api/global/us_indices/daily_prices/<NAME>_History.csv
  (redirects to cdn-api.cboe.com: use curl -L with a browser UA). Verified to exist: PUT, WPUT, BXM, CNDR, VIX,
  VIX3M. Find the others on CBOE's strategy-benchmark page and probe the same URL pattern (e.g. BXMD, BXMW, BFLY,
  CLL, CLLZ, PPUT, RXM, VXTH, VIX9D, VIX1D, SKEW, VVIX, SPX, a one-day put-write if one exists). Read each index's
  methodology (strike, tenor, roll day, the price used: e.g. VWAP 11:30-12:00 ET or the special opening quote) and
  write the key facts into your notes.
- S&P 500 total return (Yahoo chart API ^SP500TR or ^GSPC + dividends; say which), T-bill (FRED DTB3) for excess
  returns, realised variance from daily SPX closes.
- Cut every series at 2025-01-01 at load (HOLD closed). Eras: PRE/design up to 2015-12 (1986/1990 onward as
  available), CHECK1 2016-01..2021-12, CHECK2 2022-01..2024-12.

## Families (write each into HYPOTHESES_O.md before computing it)
O-A. Unconditional VRP: VIX^2 vs subsequent 21-day realised variance (size, frequency it pays, by era); PUT, WPUT,
     BXM, BXMD, CNDR, etc. vs SPX: excess return, Sharpe, beta, alpha with Newey-West t (residual-edge-analyzer
     skill is a fit), worst month, max DD, skew, 2008 / 2018-02 / 2020-03 / 2022 behaviour. Is the alpha decaying
     after 2015 (the literature claims option-selling alpha shrank)?
O-B. Realistic retail costs: the indices trade at index-methodology prices with no costs. Model IBKR commissions +
     exchange/regulatory fees per contract (SPX vs XSP vs SPY options; find current fees) and a bid-ask haircut
     (half-spread per trade as % of premium; give a range from public sources). Net-of-cost Sharpe and alpha at
     1x / 1.5x / 2x the haircut.
O-C. Conditioning rules from the literature, chosen on design data only, checked on CHECK1 and CHECK2 once:
     VIX term structure (VIX/VIX3M < 1 sell, else flat), VRP level (VIX - RV20 or VIX^2 - RV^2 above a threshold),
     trend (SPX above its 200-day MA), and their combination. Count the variants; compare the best with chance.
     These are applied to the CBOE index return stream (in the index or in cash) as a timing overlay.
O-D. Tail control and sizing for $100k: cash-secured put-write (notional = capital, i.e. no leverage; one XSP
     contract is ~1/10 SPX notional) vs put spreads (defined risk) vs condors, approximated where no CBOE index
     exists: if you build a Black-Scholes approximation from VIX (+ a skew adjustment from SKEW or a fixed put
     skew), first validate it against PUT/WPUT/CNDR on design data and report the error; label every approximated
     result as such. Give: the number of contracts at $100k, expected annual return, max DD (mark-to-market), worst
     month, and the leverage at which a 2008- or 2020-like month costs 10 / 20 / 30 % of the account.
O-E. Is it just equity beta? Compare each strategy with SPX levered to the same beta (or the same vol): the
     benchmark per BRIEF.md point 5. Correlation with C3 is ~0 by construction (different market/time); state it
     from the data if you can (C3 CSV daily net vs the strategy's daily return, 2016-2024).

## What to return
Per BRIEF.md. In the answer paragraph say: does the VRP pay net of retail costs in 2016-24 (not just 1990-2015),
which construction is best per unit of tail risk, a concrete $100k plan (instrument, tenor, strike rule, contracts,
roll day, exit/hedge rule) with its numbers, and what running it would need (broker, API, code in this repo or not).
