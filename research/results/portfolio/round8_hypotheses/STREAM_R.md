# Stream R: relative value between symbols, intraday to 5 days (written 2026-10-04 17:58 UTC, before any number)

Question: do linked symbols that diverge converge again within the holding limit, by more than two legs of cost?
Differs from the rejected swing-v2 pairs test (price LEVEL cointegration, <= 5 days, half-lives too long): here the
spread is built from RETURNS with a rolling hedge ratio and z-scored over short windows, and horizons are minutes to
days; plus factor-residual and currency-strength constructions that were never tested.

R1 intraday pairs. Spread_t = cumulative log return of Y - beta x X over a trailing window W (W = 1, 3, 5 days),
beta from a trailing 20-day OLS of 15-min returns (causal); z = spread / trailing sd. Bars M5, M15, H1. Enter both
legs at |z| >= 2, 2.5, 3 against the divergence; exit at z crossing 0 (or 0.5), or after 4 h, 1 day, 5 days; a stop
at |z| >= z_in + 2 as a variant. Costs on both legs. Pairs: EURUSD/GBPUSD, EURUSD/USDCHF (inverse), AUDUSD/NZDUSD,
XAUUSD/XAGUSD, XAUUSD/XPTUSD, XTIUSD/XBRUSD, US30/US500, US500/USTEC, DE40/UK100, US500/DE40, JP225/HK50,
BTCUSD/ETHUSD, AUDUSD/XAUUSD, USDCAD/XTIUSD, USDJPY/JP225. Sources: Gatev, Goetzmann & Rouwenhorst 2006; Elliott, van
der Hoek & Malcolm 2005; Krauss 2017 survey. Also report the one-leg version (trade only the more liquid/cheaper leg).

R2 factor-residual stat-arb (Avellaneda & Lee 2010). Universe blocks: 10 FX + 3 metals; 8 indices; all 26. Trailing
60-day PCA of H1 returns (k = 1, 2, 3 factors), residual cumulated as an OU process, s-score; enter |s| > 1.25,
exit |s| < 0.5 (their parameters), hold <= 5 days, trade the single symbol (no factor hedge) and the hedged version
(residual = symbol - factor-mimicking basket) as two variants. Cap 3 positions per bot: pick the 3 largest |s|.

R3 currency strength meter (popular retail inter-symbol method; academic cousin: cross-sectional currency momentum /
reversal intraday). Each H1 bar, solve the 8 currency index returns (USD EUR JPY GBP AUD NZD CAD CHF) from the 10 FX
pairs by least squares (sum-to-zero). Strength = cumulative over lookback L in {4, 8, 24} h. Trade the pair of the
strongest vs the weakest currency (if quoted at IC among the 10, else the best available), momentum and reversal
versions, hold 4, 8, 24 h; one position at a time. Differs from the tested D1 N=20 momentum.

R4 commodity-currency fair value (Chen & Rogoff 2003; Ferraro, Rogoff & Rossi 2015: oil and CAD move together at
daily frequency, contemporaneously). Trailing 60-day regression of H1 returns: AUDUSD on XAUUSD + US500; USDCAD on
XTIUSD + US500; NZDUSD on AUDUSD. Cumulative residual over 1-5 days, z-scored; trade the currency toward fair value
when |z| >= 2; hold <= 5 days.

R5 index dispersion. Residual of each index's session return vs the cross-index factor (US30 / US500 / USTEC; Asia:
JP225 / HK50 / AUS200; Europe: DE40 / UK100): does the session's laggard/leader revert or continue next session?

For every family give the turnover, the cost per round trip (both legs), gross and net bp, and the chance benchmark.
