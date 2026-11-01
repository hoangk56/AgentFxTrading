# Round 58: no operational limits, delta-neutral perp funding carry on Binance, 2026-10-31

On 2026-10-31 the user asked to continue until there is a LIVE bot, "lần này không có ràng buộc gì cả". Read as: the
fixed limits (hold <= 5 days, <= 3 positions per bot, capital-independent lot) and the IC / cTrader-only venue are
lifted; the statistical LIVE bar is kept. The one family those limits had made untestable is the spot-perp funding
carry (long spot, short the USDT-M perpetual, collect funding for weeks or months). Hypotheses:
[round58_unconstrained_carry/HYPOTHESES_A.md](round58_unconstrained_carry/HYPOTHESES_A.md) (10:57 UTC, before any
data). Registration and HOLD: [PREREG_A_funding_carry.md](round58_unconstrained_carry/PREREG_A_funding_carry.md).
Code: `round58_unconstrained_carry/code/` (`carry.py` panel + book simulator, `hold_run.py` registered look).

## Data
Binance public REST, 2026-10-31 (request logs in research/data/binance/*/requests.log, git-ignored): 1d klines of 891
USDT perps incl. delisted (REST serves delisted symbols), funding stamps + spot 1d klines of 384 symbols (every symbol
that was ever top-40 by perp volume, aged >= 60 days, in any era). Funding from 2019-09-10.

## Results (net of 0.17-0.25 % per side, daily book returns, Newey-West t lag 10)

| Rule | IS 2020-21 | VAL 2022-24 | HOLD 2025-01..2026-10-29 | verdict |
|---|---|---|---|---|
| A1 BTC always on (baseline) | +23.5 %/yr, t_nw 6.9 | +7.8 %/yr, 9.8 | (+5.1 % 2025, +2.5 % 2026) | premium, not a rule |
| A3 BTC + ETH, enter 14-day funding > 10 %/yr, exit < 0 | +26.9 %, t_nw 7.30 | +6.1 %, 6.97 | **+1.91 %, t_nw 5.62**, 2025 +3.41, 2026 +0.08 | registered bar PASS; **economically rejected** |
| A2 top-30 coins, K 10, 7-day > 10 %, exit < 0 | +29.3 %, 6.89 | +8.8 %, 6.63 | +1.36 %, 1.73; late -0.21 % | FAIL |

A3 / A2 both beat 96-100 % of random coin / timing draws in every era, stayed positive at costs x1.5 and one day late
before HOLD, and correlate 0.02-0.05 with C3's daily R. 18-cell grids on IS were flat (2020-21 funding was high almost
every day).

## Why A3 is not a LIVE bot although it passed the registered bar
Funding embeds an interest component (Binance's default 0.01 % per 8h = 10.95 %/yr, clamped toward the premium), and
capital tied up in the spot leg cannot also earn the cash rate. Excess return over the Fed funds rate on the deployed
capital (`DFF`, research/data/rates):

| A3 | deployed | cash rate | A3 net | excess over cash | t_nw |
|---|---|---|---|---|---|
| IS | 88 % | 0.23 %/yr | +26.9 % | +26.7 %/yr | 7.27 |
| VAL | 61 % | 3.95 % | +6.1 % | +3.3 % | 4.34 |
| HOLD | 45 % | 3.97 % | +1.91 % | **+0.01 %** | **0.02** |

In HOLD the carry paid exactly the cash rate and nothing for the venue, ADL and basis risk (always-on BTC funding 5.1 %
in 2025, 3.1 % in 2026, vs ~4 % cash). The premium that existed in 2020-24 has been arbitraged to cash (Ethena-scale
basis capital from 2024). The LIVE bar never needed a cash benchmark before (IC strategies use little margin); this
round shows it must have one for any capital-heavy carry. The verdict "not LIVE" is an economic reading added after
HOLD, stated as such; the registered bar result is reported unchanged in the prereg.

## Tail and execution notes (for the record)
- Worst day A3 -1.17 % (2020-03-12 basis blow-out); A2 -0.78 % IS, -1.11 % HOLD.
- The short leg needs coin-margined collateral: BTC and ETH rose 6x and 24x within single IS episodes.
- Daily data cannot show intraday ADL of the profitable short in a crash or a venue failure.

## Not run
Stream B (Binance vs Bybit perp-perp funding spread, [HYPOTHESES_B.md](round58_unconstrained_carry/HYPOTHESES_B.md)):
not run this round. After the cash finding, B is the more relevant carry test, since it needs no spot capital (both
legs are margin) and so is not a disguised cash rate.

## Lessons
- Any rule that ties up capital (spot legs, fully funded positions) must be graded on excess over the cash rate.
- Removing the operational limits opened carry, and the carry turned out to be cash since 2025.
