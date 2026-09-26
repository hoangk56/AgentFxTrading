# FlowRSI pair optimization — research plan (2026-09-25)

## Baseline (jobs #27–#41)

Live presets (PR #60, .algo sha 1d4c7513), $2000, ticks, 01/01–24/09/2026, AI gate and news off.

| Pair | Positions | ROI | mean R | Jan–May / Jun–Sep | Months up |
|---|---|---|---|---|---|
| UK100 | 289 | −2.1 % | −0.01 | −0.05 / +0.04 | 5/9 |
| DE40 | 350 | −4.7 % | −0.02 | −0.01 / −0.03 | 5/9 |
| USDJPY | 270 | −4.6 % | −0.03 | −0.04 / −0.03 | 4/9 |
| EURUSD | 205 | −3.9 % | −0.04 | −0.14 / +0.13 | 3/9 |
| AUDUSD | 227 | −8.5 % | −0.07 | −0.06 / −0.10 | 3/9 |
| EURJPY | 258 | −10.6 % | −0.08 | −0.01 / −0.16 | 2/9 |
| BTCUSD | 408 | −20.7 % | −0.11 | −0.07 / −0.16 | 4/9 |
| USTEC | 285 | −17.9 % | −0.13 | −0.08 / −0.20 | 2/9 |
| GBPUSD | 302 | −21.2 % | −0.16 | −0.20 / −0.07 | 1/9 |
| US30 | 274 | −21.2 % | −0.17 | −0.21 / −0.12 | 1/9 |
| GBPJPY | 296 | −23.8 % | −0.18 | −0.22 / −0.14 | 2/9 |
| USDCAD | 220 | −21.0 % | −0.21 | −0.28 / −0.09 | 2/9 |
| AUDJPY | 269 | −30.8 % | −0.27 | −0.30 / −0.23 | 0/9 |
| ETHUSD | 384 | −43.2 % | −0.29 | −0.25 / −0.35 | 0/9 |
| XAUUSD | 0 | — | — | — | — |

- Pooled 4037 positions: mean −0.13R, t −7.3. Hit rate 45 %, avg win +1.0R, avg loss −1.06R;
  break-even needs 51.5 %.
- A 00–08 UTC-only subset is +0.03R Jan–May, −0.10R Jun–Sep: a session filter does not create an edge.
- XAUUSD: SL floor 1500p × 1 oz minimum = $15+ > 1.5 × (0.5 % × $2000); `MaxMinLotRiskMultiple` refuses
  every entry. The ~$1650 live demo is blocked the same way.
- The SL floor sets the stop on 39–73 % of full losses on the 8 forex pairs, 0–4 % on indices/crypto.

R = position net ÷ (0.5 % × balance before the position). Positions = history deals grouped by
(entryTime, direction, entryPrice).

## Phase 1 — one change at a time, 2026 (jobs #42–#96)

| | Override | Pairs | Jobs |
|---|---|---|---|
| H1 | `EnableMacroTmsFilter=false` | 14 | 14 |
| H2 | `MinSlFloorPips` 25 (AUDUSD/EURUSD/GBPUSD/USDCAD), 30 (4 JPY) | 8 forex | 8 |
| H3 | `EnableSmcFilter=false` | 14 | 14 |
| H4 | `EnablePartialClose=false` | 14 | 14 |
| XAU | base + H1–H4 (H2 = floor 2500), $10k, `MaxRiskPerTradeMoney=1000` | XAUUSD | 5 |

**Keep rule (fixed before results):** a hypothesis is kept when mean R improves on ≥ 70 % of the pairs
it touches (10/14; H2 6/8) **and** pooled mean R improves in both Jan–May and Jun–Sep. XAU is judged
against its own $10k base and does not vote on the others.

## Phase 2 — combine and hold out 2025

- Combo = kept hypotheses. Run it on 2026 (15 jobs) to check interactions.
- 01/01–31/12/2025: base and combo for all 15 pairs (30 jobs). Cold 2025 ticks may time out once;
  the worker reruns once (PR #56).
- **Pass:** combo pooled mean R on 2025 > 0 with t ≥ 2. Enable only pairs with mean R ≥ 0 under the
  combo in both 2026 and 2025.
- **Fail** (nothing kept in phase 1, or the combo fails 2025): stop parameter tuning and redesign the
  FlowRSI entry signal.

## Phase 3 — deploy (only on pass)

`app/cbot_presets.py` + `docs/docker-instances.md` (sync test), branch → PR opened by the user,
recreate bots with `PUT /api/bots/{name}`; stop the pairs that failed.

## Caveats

- Backtests run with the AI gate off; live adds it on top.
- Min-lot positions (indices) can risk up to 1.5× the 0.5 % target, so their R is overstated; every
  variant shares the same normalization.

## Phase 1 result (2026-09-25 09:05 UTC) and decision

| | Pairs improved | Pooled mean R | Jan–May | Jun–Sep | Verdict |
|---|---|---|---|---|---|
| H1 macro off | 11/14 | −0.131 → −0.084 | −0.139 → −0.101 | −0.119 → −0.060 | kept |
| H2 SL floor 25/30 | 7/8 | −0.134 → −0.080 | −0.159 → −0.108 | −0.096 → −0.036 | kept |
| H3 SMC off | 9/14 | −0.131 → −0.113 | better | better | dropped |
| H4 no partial | 8/14 | −0.131 → −0.123 | better | better | dropped |

XAU ($10k base +0.01R): only H2 improved both halves (+0.03R); H1 −0.05R in both halves.
Kept changes only shrink the loss (H1 t −6.1, H2 t −2.9). **The user stopped here (phase 2 not run) and chose
to redesign the FlowRSI entry signal.**
