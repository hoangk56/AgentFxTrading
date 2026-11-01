# Stream BX: B's cheap-basis signal hedged with the Bybit linear perp instead of spot (round 63)

Written 2026-10-31 16:07 UTC (from `date -u`). Declared in [HYPOTHESES_BX.md](HYPOTHESES_BX.md) (15:58 UTC, before
any Bybit 1h kline was requested). HOLD (2025+) never requested or loaded; all series cut at ts < 2025-01-01.

## Answer: none (both rules fail VAL)
- **Primary P (long Binance perp / short Bybit perp on every covered B trade): none.** IS +66 bp (t 2.58, n 39, 14
  days, 25 of 39 trades on 2021-05-19 / 2021-09-07), **VAL -34.2 bp (t -6.18, n 315)**, 2022 / 2023 / 2024 all
  negative.
- **Variant V50 (Bybit perp >= 50 bp richer than the Binance perp at the signal): none.** IS +195 bp (t 3.63, n 14,
  4 days), **VAL -35.8 bp (t -1.72, n 50)**.
- Why: the Bybit perp is as cheap as the Binance perp at B's signals. VAL price convergence of the perp-perp spread is
  **-0.8 bp per trade** (B's perp-spot price leg on the same trades +154.9 bp); corr(Binance perp, Bybit perp hold
  returns) = 0.998. The dislocation B trades is **spot vs all perps**, not a Binance-perp event: in the sampled trades
  it is mostly spot moving to the perps (e.g. PEOPLE 2022-05-21: Binance perp -216, Bybit perp -240, spot -316 bp).
  The funding legs cancel too (VAL Binance received +49.1, Bybit paid -42.2 bp). What is left is ~40 bp of costs.
- No PREREG_DRAFT. A BX HOLD is not worth opening (VAL fails outright).

## Coverage (share of B's trades with a Bybit 1h bar at the entry hour, volume > 0, and an exit bar within 24 h)
| era | B trades | covered | no Bybit perp in the windows | listed later than the entry | no exit bar |
|---|---|---|---|---|---|
| IS 2020-21 | 303 | **39 (12.9 %)** | 138 | 126 | 0 |
| VAL 2022-24 | 333 | **315 (94.6 %)** | 1 | 14 | 3 |
Bybit listed most alt USDT perps only from 2021-09 (e.g. AVAXUSDT first daily bar 2021-09-15), so IS is almost absent:
the IS sample is 14 days, too few to grade anything. Lag-1 coverage: IS 44 / 349, VAL 350 / 369.

## Results (net bp per trade, taker, t clustered by entry UTC day)
| cell | era | n | days | net | median | t | win | x1.5 | 1 h late (n / net / t) | random % (mean) |
|---|---|---|---|---|---|---|---|---|---|---|
| P | IS | 39 | 14 | +66.2 | +15.9 | 2.58 | 59 % | +46.4 (t 1.81) | 44 / +61.7 / 0.85 | 99.3 (-25.4) |
| P | VAL | 315 | 140 | **-34.2** | -36.2 | **-6.18** | 16 % | -54.3 | 350 / -43.3 / -8.88 | 89.0 (-40.7) |
| V50 | IS | 14 | 4 | +195.4 | +140.8 | 3.63 | 100 % | +175.6 | 18 / +41.2 / 0.61 | 100 (-33.5) |
| V50 | VAL | 50 | 17 | **-35.8** | -37.7 | -1.72 | 22 % | -55.7 | 62 / -61.8 / -4.02 | 72.6 (-41.5) |

Years (n, net bp): P 2021 (39, +66), 2022 (95, -45), 2023 (145, -23), 2024 (75, -42): 1 / 4 positive. V50 2021
(14, +195), 2022 (11, -38), 2023 (16, -29), 2024 (23, -39, all on 2024-10-28): 1 / 4. No 2020 trades are covered.
Max-over-2-cells random null of t: IS p95 0.40, VAL p95 -0.50. Power at VAL size (per trade SR x sqrt(1.8 x VAL n / 3)):
P -4.99 (day -3.61), V50 -1.66: negative, no bar reachable.

## Decomposition (bp per trade)
| cell | era | perp-perp price | Binance funding received | Bybit funding paid | costs | B net on the same trades | B price leg | spot - Bybit perp return |
|---|---|---|---|---|---|---|---|---|
| P | IS | +62.0 | +83.8 | -40.1 | -39.6 | +219.3 | +184.2 | -122.2 |
| P | VAL | **-0.8** | +49.1 | -42.2 | -40.1 | +154.2 | +154.9 | -155.6 |
| V50 | IS | +146.9 | +122.0 | -34.0 | -39.6 | +434.4 | +360.4 | -213.5 |
| V50 | VAL | +16.8 | +59.1 | -71.9 | -39.7 | +100.0 | +90.1 | -73.2 |
Bybit-minus-Binance perp log spread at the signal close: IS p10 / p50 / p90 = -94 / +32 / +146 bp, VAL -57 / +4 / +134
bp; only 16 % of VAL signals have Bybit >= 50 bp richer. VAL by spread bin: < -50 bp n 36, net -72; -50..+50 n 229,
-28 (price +5); +50..+100 n 11, -68 (price +19); > +100 n 39, -27 (price +16). Even where Bybit is richer at the signal
close, the spread does not converge by more than the costs (Bybit catches down within the hour or is itself stale).

## What this says about B (information for the coordinator)
- B's convergence is spot vs perps, not Binance-perp-specific: both perps lead and spot follows. A perp on another
  venue is not a hedge; a borrow-free version would need a short instrument that tracks Binance spot (another venue's
  spot needs the same borrow; a dated future / option is not available on most of these alts).
- Since the Binance perp and spot converge mostly by spot moving, B's P&L comes from shorting a spot price that lags
  the perps. The fill risk B flagged (entry-bar open prices on spot) is the central question: if the lagging spot is
  thin, the modelled 3-5 bp half-spread on the spot short is the part most likely to be wrong.
- B's HOLD has been seen (+213.5 bp, 59 % funding). A BX HOLD would trade the same signal days, so it would only test
  the Bybit substitution, which VAL already rejects (-34 bp, t -6.2): it adds nothing worth spending HOLD on.

## Pitfalls / checks
- Scale: Bybit symbol map 1000SHIB -> SHIB1000USDT (others same name); scale = median close ratio rounded to a power of
  10 (VAL median spread +4 bp confirms alignment). Bybit returned transient `retCode 10016` twice (retried, both ok)
  and `10001` for the TURBO candidate name only; a first pull attempt treated a transient error as "not listed", so it
  was stopped, the retry fixed and the missing markers deleted before the final pull.
- Funding stamps in (e, x] as in B on both venues (Bybit from research/data/bybit/funding, 7 symbols pulled).
- Bybit half-spread fixed at 5 bp per side; even at 0 bp spread on Bybit the VAL net would be ~ -24 bp (P).

## Files
- [HYPOTHESES_BX.md](HYPOTHESES_BX.md); code: [code/events.py](code/events.py) (reruns B's frozen rule, lists events),
  [code/pull.py](code/pull.py) (Bybit klines / funding), [code/bx.py](code/bx.py) (grading); outputs
  [out/bx_results.json](out/bx_results.json), out/bx_trades_{P,V50}_lag{0,1}.npz, out/bx_run.log, out/events.csv.
- Data: research/data/bybit_1h/kline/ (104 symbols with bars, 39 not listed on Bybit in the windows), funding/ (7 symbols),
  requests.log (402 requests incl. the aborted first attempt, 16:00-16:06 UTC, no 403 / 418 / 429).

## What a user decision could unlock
Nothing on the perp-perp route. The open question stays B's: whether spot can be shorted (margin borrow availability
and rate) at the signal hours, and whether the lagging spot is fillable near the bar open. A live borrow / book probe
on Binance margin (user account, demo size) is the only test left for B's signal.
