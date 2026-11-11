# B demo: why no signal is fillable (Binance margin API check, 2026-11-11)

The user asked whether "no inventory to borrow" was a misreading of the API. Checked with the demo's own read-only key
on agentFx (`app.basis_b_runner.Binance`), signed GETs only, around 15:30 UTC. No order sent, no return read.

## The demo so far

15 signals since 2026-11-01 (14 closed, 1 open), on four coins: LSK, BMT, GTC, INIT. **All 15 not fillable**: at each
entry `/sapi/v1/margin/available-inventory` gave 0 for the coin and `/sapi/v1/margin/maxBorrowable` answered
`-3045 "The system does not have enough asset now."`. Hourly borrow rate at entry 7.0e-5 to 1.14e-4 (x 8,760 =
61-100 %/yr; the PREREG assumed 40 %/yr).

## The account is not blocked

Same call, same account (about $1k collateral in cross margin), same minute:

| asset | cross inventory | isolated inventory | maxBorrowable | next hourly rate |
|---|---|---|---|---|
| LSK / BMT / GTC / INIT | 0 | 0 | `-3045` | 7.0e-5 .. 1.12e-4 |
| ETH | 0 | 0 | `-3045` | |
| SOL | 0 | 0 | `-3045` | 5.8e-6 |
| BTC | 113.5 | | 0.054 (limit 100) | 5.7e-7 |
| XRP | 1,956,635 | 1,956,635 | 3,730 (limit 730,000) | |
| BNB | 1,785.5 | 1,785.5 | 5.84 (limit 300) | |

183 of the 384 margin assets showed zero inventory; DOGE, ADA, LINK, AVAX, SUI, ARB, OP, USDT, USDC and most large
coins had plenty. The rate conversion in `app/basis_b_status.py` (hourly x 8,760) is right.

## Reading

The API is read correctly and the account can borrow; the four coins B fired on had none to lend, in both margin
modes. B enters when the perp trades more than 100 bp under the spot, a gap that can persist only when the spot
cannot be shorted, so a drained borrow pool is most likely the condition of the signal rather than bad luck. More
collateral would not change it. The demo keeps logging to its 40th signal, where the registered stop (> 30 % not
fillable) will read it; [docs/capital-allocation.md](../../../docs/capital-allocation.md) moves B's share to the reserve.
