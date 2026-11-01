# Round 53: Tether (USDT) mint events -> BTC / ETH over 5-60 minutes, 2026-10-30

Brief: [round53_usdt_mints/BRIEF.md](round53_usdt_mints/BRIEF.md). Same LIVE / DEMO bars as rounds 25-52. HOLD
(2025-01..2026-09) stayed closed (every series cut at 2024-12-31 at load / parse). HYPOTHESES_M.md written 09:49 UTC,
before any return; no addenda.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Saggu's (2022) +24 to +68 bp within 5-30 minutes of a mint is not in the
Tron era: 2019-21 Tron mints give BTC mid +5.8 bp at 30 min (t 1.08), -0.2 at 5 min; the IS mid (+14.8 bp, t 1.76) comes
from 10 Omni grants in 2018 (+84 bp) when IC's BTC spread was ~41 bp. VAL's 41 events (all $1bn Tron mints) are +3.4 bp
at 5 min (cost 3.9), -6.1 at 30 min, -13.2 at 60 min. Mints follow a rising BTC (+22 bp in the prior hour vs +1 bp on
average); against a no-mint placebo with the same prior-hour return the excess is IS +10.6 bp (t 1.22) and VAL -5.0 at
30 min. Best IS net t +0.72 of 20 cells (chance bar 1.29); every long cell is negative in VAL; 2 of 8 years positive.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| M | USDT mints >= $10M / >= $100M (Omni grants 2017-19 + Tron 2019-24, clustered within 60 min) -> long BTCUSD 5 / 15 / 30 / 60 min from block + 2 min, ETHUSD leg, burns -> short; matched random entries and no-mint placebo; 20 cells | **none**: headline BTC 30 m net IS -0.8 (t -0.1, n 135) / VAL -11.0 (t -1.5, n 41); ETH IS cost 81-116 bp; burns = BTC drift; HOLD power <= 0 | [STREAM_M.md](round53_usdt_mints/STREAM_M.md), [HYPOTHESES_M.md](round53_usdt_mints/HYPOTHESES_M.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Single stablecoin mint / burn events (USDT Omni + Tron) -> BTC / ETH at 5-60 minutes. The Ethereum-mint token
  decision falls to LIVE < 0.5 %, DEMO ~1-2 %.

## Pitfalls
- api.omniexplorer.info `/v1/properties/gethistory/31` (POST, 10 pages) gives the Omni grants / revokes; the host
  serves no robots.txt (omniexplorer.info allows `*`).
- IC BTC 2017-18 spreads were 28-41 bp and ETH IS round trips 81-116 bp: IS nets and "excess" vs placebo on ETH are
  cost artefacts. Every VAL mint is exactly $1bn. 46 of 224 clusters fell on IC's weekend closure.

## Directions that need the user
| direction | value |
|---|---|
| Ethereum archive-RPC token for Ethereum USDT / USDC mints | LIVE < 0.5 %, DEMO ~1-2 % (down from ~2.5 % / ~10 %) |
| Single-stock CFDs on MT5 | LIVE ~3-5 %, DEMO ~25 % (unchanged, most valuable) |

## State after round 53
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. With round 52's census, no free
direction without a user decision has an expected LIVE chance of even 1 %; the next round needs one of the decisions
in research/PROMPT.md ("Hướng cần tôi quyết").
