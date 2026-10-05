# Stream X: literature + cross-session and regime spillovers (written 2026-10-04 17:58 UTC, before any number)

X1 literature. Use the paper-lookup skill (research/.claude/skills/paper-lookup; stdlib scripts, network to the
scholarly APIs only) to search 2000-2026 for short-horizon (minutes to 5 days) predictability BETWEEN markets:
lead-lag, return/volatility spillover, cross-asset time-series momentum (e.g. Pitkäjärvi, Suominen & Vaittinen 2020),
economic links / information diffusion, FX-equity, commodity-FX, crypto-equity, pairs/stat-arb in FX/commodities/
indices, correlation-regime strategies, network/Granger-causality trading. Build a table: mechanism | paper | horizon
| reported effect size | needs data we lack? | already covered by round 1-7 or by streams L (intraday lead-lag), S
(shock spillover), R (relative value / pairs / PCA residual / currency strength / commodity-currency fair value /
index dispersion) | prior expected bp vs IC cost | power pre-screen. Screen up to ~6 mechanisms that no stream covers.

X2 cross-session spillover (CFDs trade ~24 h, so this is about local-investor flow at the cash open, not stale prices).
- X2a US cash session (13:30-20:00 UTC) return of US500/USTEC -> the next Asian cash session of JP225 (Tokyo open
  00:00 UTC), HK50 (01:30 UTC), AUS200 (23:00/00:00 UTC), and AUDJPY/USDJPY over 23:00-06:00 UTC: continuation or
  reversal (Hamao, Masulis & Ng 1990; Lin, Engle & Ito 1994; Becker, Finnerty & Gupta 1990).
- X2b Asian session (00-07 UTC) of JP225/HK50/AUS200 -> European open 07-10 UTC of DE40/UK100/EURUSD.
- X2c European morning (07-13 UTC) of DE40/UK100 -> US afternoon (14:30-20:00 UTC) of US500/USTEC.
- X2d Overnight (20:00 -> 13:30 UTC) move of the US index CFD vs the following US cash session (gap fade vs
  continuation conditioned on how Asia/Europe moved; differs from the tested single-asset gap fade).

X3 risk-regime conditioning (daily). Regime = US500 trailing 5-day realised vol vs its 60-day level, or the average
pairwise correlation of the 26 symbols' daily returns (trailing 20 days). Hypothesis: in high-vol/high-correlation
regimes carry pairs (AUDJPY, AUDUSD, NZDUSD) fall and safe havens (USDJPY down, USDCHF down, XAU up) rise the next
day; and the reverse after the regime eases. For PRE 2004-15 use AUDJPY's own realised vol (Dukascopy H1) as the
risk proxy for the FX legs.

X4 crypto -> traditional assets. BTC's move while US markets are closed (20:00-13:30 UTC, and weekends where data
exists: IC crypto was closed at weekends until 2024-04, so weekend data is 2024-05..2024-12 only; check feasibility
and say so) -> US500/USTEC at the next US cash open and the first hour.

X5 dollar-gold divergence (daily). Gold and the USD factor normally move opposite; on days both rise (or both fall)
by > 1 sd, does the divergence revert the next 1-3 days (which leg)?

Use the shared panel; daily ideas: build daily closes at 20:00 UTC (and 00:00 UTC for FX) from the panel.
