# Round 53, stream M: USDT mints / burns -> BTCUSD, ETHUSD at 5-60 minutes

Written 2026-10-30 09:52-09:58 UTC (`date -u`). Hypotheses declared first in [HYPOTHESES_M.md](HYPOTHESES_M.md)
(09:49 UTC, before any return); no addenda. HOLD was never opened: every series is cut at 2024-12-31 at load / parse.

## Answer
- **No cell reaches DEMO or LIVE. There is no PREREG_DRAFT.** The best IS net t of the 20 cells is +0.72 (mint >= $100M,
  BTC 30 / 60 min). Every VAL net of a long cell is negative. 20 cells were tried, and the best-of-20 chance bar is
  IS t 1.29.
- **The paper's effect is not in the Tron era.**
  - Saggu 2022 reports +24 to +68 bp in 5-30 minutes. In the Tron era (2019-21, 101 events) the BTC mid after a
    >= $10M mint is +5.8 bp at 30 minutes (t 1.08) and -0.2 bp at 5 minutes.
  - The positive IS mid (+14.8 bp at 30 minutes, t 1.76) comes from 10 Omni grants in 2018 (+84 bp). Those were
    traded when IC's BTC spread was ~41 bp.
  - In VAL (2022-24, 41 events, all >= $100M) the mid is +3.4 bp at 5 minutes (cost 3.9 bp), -6.1 bp at 30 minutes
    and -13.2 bp at 60 minutes.
- **The confound is real.** BTC rose +22 bp on average in the hour before an IS mint, against +1 bp for all IS
  minutes.
  - Against the no-mint placebo (same prior-hour BTC return, no mint within 6 h), the IS excess is +10.6 bp at
    30 minutes (t 1.22) and +17.1 bp at 60 minutes (t 1.51).
  - In VAL the excess is -5.0 bp (t -0.65) and -11.4 bp (t -1.35).
  - Against the matched random entries, IS beats 98-99 % of seeds at 30 / 60 minutes and VAL beats 4-14 %.
- **Burns (the short mirror) are negative everywhere.** On 21 IS and 8 VAL events the VAL loss at 5 / 15 minutes is
  large (-26 / -34 bp): BTC kept rising after burns. That matches the paper's "no effect" plus BTC's upward drift.
- **What Ethereum mints would add.**
  - The Ethereum mints would roughly double or triple the count (HOLD ~60-90 events), but they would not change the
    sign. The Tron VAL mid is <= 0 at every horizon beyond 5 minutes, and the 5-minute mid is below IC's cost.
  - A LIVE cell would need Ethereum mints to carry a VAL mid of ~+15 bp net while Tron mints of the same
    weeks show ~-6 bp. The two chains are minted by the same treasury on the same demand, so that is implausible.
  - Revised value of the archive-RPC token: **LIVE < 0.5 %, DEMO ~1-2 %** (round 52 put it at ~2.5 % / ~10 %).
    It no longer ranks among the user decisions worth taking.

## Sources and robots
| host | robots.txt | used for | result |
|---|---|---|---|
| api.trongrid.io (pulled in round 52 Z) | 404 (no file) | USDT-TRC20 Issue / Redeem 2019-01..2024-12 | 248 mints, 34 burns (copied to scratchpad) |
| api.omniexplorer.info | no robots file (serves its HTML API docs at /robots.txt); www.omniexplorer.info / omniexplorer.info: `User-agent: *` Allow / , Disallow /search/* (no ClaudeBot / anthropic-ai rule) | `POST /v1/properties/gethistory/31` pages 0-9, 2 s apart, 2026-10-30 09:47-09:48 UTC, UA "research-script/1.0" | all HTTP 200; 92 grants (2014-19), 5 revokes; cut at parse |
| IC M1 (local) | - | BTCUSD 2017-08-28.., ETHUSD 2017-09-25.., cut at load | - |

These were not used: Ethereum logs (excluded this round), Binance M1 (the weekend mid diagnostic was skipped for
time and declared), web.archive.org and tronscan. No key, no login, no email, and no 403 or bot wall was hit.

## Events (mint >= $10M, clustered within 60 min across chains, first event traded)
- IS (2017-08-28..2021): 137 IC-covered trades. Of these, 35 are Omni (2017-18) and 102 Tron (2019-21).
- VAL (2022-24): 41 trades, all >= $100M.
- 46 post-IC-start clusters were dropped because IC BTC was closed at weekends (2017 7, 2018 2, 2019 8, 2020 14,
  2021 13, 2023 2). 18 Omni grants from 2017 came before IC BTC started.
- HOLD estimate: ~27 (Tron 2023-24 rate x 1.73 y; IC trades weekends since 2024-04).

## Results (bp per trade, net = actual IC spread at both bars + swap; t clustered by day)
| cell | IS mid (t) | IS net (t) n | IS-core 2019-21 net (t) | VAL mid (t) | VAL net (t) n | cost IS / VAL | IS x1.5 / +1 min net | VAL x1.5 / +1 min net | IS ex-2020-03/04 net | Sharpe IS / VAL; HOLD power (VAL Sh x sqrt 27) | random A pct IS / VAL | placebo excess IS / VAL (t) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mint10 BTC 5m | -3.8 (-1.33) | -18.1 (-5.38) 136 | -7.9 (-2.38) | +3.4 (+0.84) | -0.5 (-0.13) 41 | 14.3 / 3.9 | -25.3 / -19.1 | -2.5 / -4.3 | -16.6 | -0.44 / -0.02; -0.1 | 3 / 92 | -4.3 (-1.26) / +2.9 (+0.68) | none |
| mint10 BTC 15m | +3.5 (+0.71) | -11.6 (-2.33) 136 | -4.9 (-1.13) | -0.4 (-0.06) | -4.4 (-0.75) 41 | 15.1 / 4.1 | -18.8 / -10.1 | -6.5 / -5.1 | -9.2 | -0.19 / -0.11; -0.6 | 51 / 47 | +1.2 (+0.23) / -0.3 (-0.05) | none |
| **mint10 BTC 30m (headline)** | +14.8 (+1.76) | -0.8 (-0.10) 135 | -3.4 (-0.61) | -6.1 (-0.84) | -11.0 (-1.53) 41 | 15.7 / 4.9 | -8.0 / -1.9 | -12.9 / -11.8 | +0.5 | -0.01 / -0.24; -1.2 | 98 / 14 | +10.6 (+1.22) / -5.0 (-0.65) | none |
| mint10 BTC 60m | +18.5 (+1.64) | +2.8 (+0.25) 135 | -5.9 (-0.70) | -13.2 (-1.66) | -18.3 (-2.33) 41 | 15.7 / 5.1 | -4.3 / +4.3 | -20.3 / -18.6 | +2.1 | +0.02 / -0.36; -1.9 | 99 / 4 | +17.1 (+1.51) / -11.4 (-1.35) | none |
| mint10 ETH 5m | -4.3 (-1.07) | -119.3 (-10.9) 133 | -138.9 | +4.8 (+1.13) | -10.0 (-2.35) 41 | 115 / 14.8 | -176.7 / -118.8 | -17.4 / -15.3 | -108.4 | -1.09 / -0.36 | 26 / 94 | +10.2 / +3.6 | none |
| mint10 ETH 15m | +8.0 (+1.01) | -107.1 (-8.30) | -134.8 | +2.8 (+0.37) | -11.8 (-1.60) | 115 / 14.6 | -164.3 / -105.3 | -19.1 / -13.9 | -93.9 | -0.80 / -0.25 | 94 / 72 | +22.3 (+1.92) / +3.0 | none |
| mint10 ETH 30m | +15.6 (+1.34) | -100.6 (-6.34) | -132.9 | -4.9 (-0.56) | -20.2 (-2.37) | 116 / 15.4 | -158.0 / -98.6 | -27.7 / -24.2 | -88.2 | -0.62 / -0.38 | 100 / 22 | +29.6 (+2.08) / -3.1 | none |
| mint10 ETH 60m | +22.3 (+1.32) | -94.1 (-4.74) | -136.2 | -9.3 (-0.94) | -24.5 (-2.53) | 116 / 15.2 | -151.4 / -92.3 | -31.7 / -26.5 | -84.1 | -0.44 / -0.40 | 100 / 13 | +39.2 (+2.11) / -4.8 | none |
| mint100 BTC 5m | -2.2 (-0.71) | -12.9 (-3.36) 80 | -5.9 (-1.89) | = mint10 | = mint10 | 10.7 / 3.9 | -18.3 / -17.6 | = | -12.9 | -0.37 / -0.02 | 19 / 94 | +1.0 / +2.9 | none |
| mint100 BTC 15m | +8.3 (+1.37) | -2.9 (-0.50) 81 | -3.9 (-0.83) | = | = | 11.2 / 4.1 | -8.2 / -2.7 | = | -2.2 | -0.05 / -0.11 | 87 / 50 | +11.5 (+1.83) / -0.3 | none |
| mint100 BTC 30m | +20.9 (+1.67) | +8.8 (+0.72) 80 | -0.9 (-0.13) | = | = | 12.1 / 4.9 | +3.2 / +6.6 | = | +9.2 | +0.08 / -0.24; -1.2 | 99 / 14 | +20.8 (+1.64) / -5.0 | none |
| mint100 BTC 60m | +23.6 (+1.40) | +11.8 (+0.72) 80 | -7.9 (-0.71) | = | = | 11.7 / 5.1 | +6.6 / +13.5 | = | +11.3 | +0.08 / -0.36 | 99 / 5 | +25.8 (+1.56) / -11.4 | none |
| mint100 ETH 5-60m | -5.7..+27.5 | -86.9..-54.1 (t -10.6..-2.2) | -78..-87 | = mint10 ETH | = | 81 / 15 | all < 0 | all < 0 | all < 0 | < 0 / < 0 | 18-100 / 12-92 | IS +42..+75 (t 3-5, cost artefact, see pitfalls) / VAL -5..+4 | none |
| burn10 BTC 5m (short) | -1.6 (-0.33) | -12.4 (-2.03) 21 | -11.0 | -21.1 (-4.04) | -25.9 (-4.56) 8 | 10.8 / 4.7 | -17.8 / -8.6 | -28.2 / -32.5 | -12.4 | -0.43 / -1.51 | 38 / 0 | +5.6 / -21.1 (-3.60) | none |
| burn10 BTC 15m | -2.3 | -13.0 (-1.58) | -14.8 | -29.0 (-2.35) | -33.7 (-2.71) | 10.7 / 4.7 | -18.4 / -12.4 | -36.1 / -28.5 | -13.0 | -0.34 / -0.90 | 33 / 0 | +4.0 / -27.4 (-2.17) | none |
| burn10 BTC 30m | -6.8 | -16.6 (-1.77) | -18.3 | +10.1 (+0.75) | +5.3 (+0.40) | 9.7 / 4.9 | -21.4 / -13.0 | +2.8 / +3.5 | -16.6 | -0.38 / +0.13 | 45 / 65 | -2.0 / +7.8 | none |
| burn10 BTC 60m | +6.9 | -2.3 (-0.13) | -3.4 | -34.8 (-1.50) | -39.2 (-1.65) | 9.2 / 4.4 | -6.9 / +2.3 | -41.4 / -41.7 | -2.3 | -0.03 / -0.55 | 64 / 2 | +11.0 / -38.8 | none |

BTC mint >= $10M net by year (30 min): 2017 -25.8 (n24), 2018 +84.4 (10), 2019 -9.7 (21), 2020 -4.7 (42), 2021 +1.6
(38), 2022 -27.8 (11), 2023 -14.4 (14), 2024 +3.6 (16). Two of eight years are positive, against the 2/3 the bar
needs. The 60-minute row has the same pattern. Mids in the Tron era (2019-21) are +5.8 bp at 30 minutes (t 1.08) and
+3.7 bp at 60 minutes. Without 2020-03/04 the IS mid is +16.3 bp (t 1.85), because the March-April 2020 mints were followed by falling
days.

## Cells and the chance benchmark
- 20 declared cells: 8 mint >= $10M (BTC / ETH x 4 horizons), 8 mint >= $100M and 4 burn shorts. No addenda.
- Best-of-20 chance bar: the 95th percentile of the max IS t over cells on the matched random entries (300 seeds) is
  **1.29** (median 0.19).
  - It sits low because the random entries pay the same cost, so this is a lenient bar.
  - The best real IS net t is 0.72, below even that.
- Power at HOLD size (~27 events): every long cell has a negative VAL Sharpe, so power is <= 0. At the best IS
  Sharpe (+0.08) the power would be 0.4. LIVE needs 3.

## Pitfalls met
- **2017-18 IS is an Omni and wide-spread era.** IC's BTC spread was 28-41 bp at the entry minutes, and ETH's IS cost
  is 81-116 bp a round trip (2019-20 IC ETH spreads were very wide). The ETH IS nets mean nothing beyond "untradeable
  then". The ETH placebo excess (IS t 2-5) is the same artefact: placebo minutes sit at other hours and days with
  different spreads, and the event-minus-placebo difference is mostly cost.
- **Demand follows price.** Mints come after BTC has risen (+22 bp in the prior hour in IS). Matching on the prior
  hour matters, and the random-A percentile (98-99 % in IS) mostly reflects the IS mid, which the VAL reverses.
- **Every VAL mint is >= $100M**, so the two size tiers are identical in VAL. All 43 Tron mints of 2022-24 are exactly $1bn
  inventory mints.
- **Weekend drops (46 of 224)** remove the times when retail-led crypto flow would matter most. A 24/7 diagnostic
  (Binance mid) was declared skipped. It could not change the net verdict, because IC traded no weekends until
  2024-04.
- **Burns** are few (29) and their VAL loss is BTC drift. They are not an independent signal.

## Directions that need the user
| direction | value now |
|---|---|
| Ethereum archive-RPC token for USDT / USDC mint times 2017-24 | LIVE < 0.5 %, DEMO ~1-2 % (down from ~2.5 % / ~10 %): the Tron VAL mid is <= 0 beyond 5 min |
| Whale Alert tweet history (paid): the paper's "amplifier" | < 0.5 % / ~1 % (it would condition the same negative VAL events) |
| Single-stock CFDs (MT5), from round 52 | still the most valuable decision (LIVE ~3-5 %, DEMO ~25 %) |

## Files
- This file and [HYPOTHESES_M.md](HYPOTHESES_M.md) (no PREREG_DRAFT).
- Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r53/M/`:
  - Scripts: `scripts/ev.py` (load with the HOLD cut, events, clustering, entry / exit), `scripts/counts.py`
    (counts and spreads before returns), `scripts/run.py` (20 cells, controls, benchmark) and
    `scripts/omni_parse.py` (Omni parse with the cut).
  - Data: `data/tron_Issue.tsv`, `data/tron_Redeem.tsv`, `data/omni_grants.tsv`; raw `web/omni/p0-9.json`.
  - Output: `out/res.json` and `out/run.log`.
  - Fetch log: `web/requests.log`, and the robots copies in `web/robots_*.txt`.
