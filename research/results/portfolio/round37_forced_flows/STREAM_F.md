# Round 37, stream F: perpetual-funding settlement pressure, conditioned on the rate paid -> BTCUSD / ETHUSD at IC

Written 2026-10-29 09:38 UTC (`date -u`). The hypotheses ([HYPOTHESES_F.md](HYPOTHESES_F.md)) were declared at 09:32
UTC, before any funding signal was joined to a return. HOLD was never loaded:
- every series was requested with endTime 2024-12-31 23:59:59 UTC;
- IC M1 was cut at ts < 1735689600000 at load.

## Answer

**No LIVE, no DEMO, no PREREG_DRAFT.**

### F1: perp funding settlement pressure

- **The PRE leg is real at mid.** The rule shorts into the 00/08/16 UTC stamp when the predicted rate is large
  (\|f̂\| >= 3 bp); the price is lower at the stamp than 15 min before, in both eras:
  - PP-A3 w15: IS +6.0 bp (t 1.97), VAL +6.5 (t 2.40).
  - It beats 97.5 % / 95 % of random entries.
  - The dose slope is about -1 to -2 bp of return per bp of predicted funding, IS and VAL.
  - The 04/12/20 and ±2 h placebos are flat.
  - It replicates on ETH at mid: VAL +10.3 bp, t 2.94.
- **It cannot be traded at the era's cost.**
  - IS (2019-09..2021) cost at those minutes is 7.3-8.0 bp a round trip, against a mid of +6 to +9. Best IS net t
    of the 36 cells: +0.38.
  - Even cost-free, the IS mid t (1.97 / 1.91) stays below DEMO's 2.0.
  - Family-wise the best IS mid t (2.37) is what chance gives (day sign-flip null p50 1.95, p95 3.04, p 0.27).
- **The POST leg has no rebound.** The declared "reopen after the stamp" side is flat in IS and negative in VAL.
- **LIVE was out of reach by arithmetic before any number.** Large rates are an IS-era phenomenon: weekday stamps
  with \|f\| >= 3 bp were 19-30 % in 2020-21 against 0.5-7 % in 2022-24. So the expected HOLD count is ~50-65
  trades, and the payer's concession is bounded by f (a few bp). Power at the VAL size:
  - A3: 0.64 (1.28 even at today's ~1.7 bp BTC round trip);
  - A5: 1.71 (n ~20).

### F2: CME BTC monthly expiry, the BRR window, only in high-carry months

- 10 IS events.
- Leg A (short into the BRR window) has the wrong sign, -11.5 bp.
- Leg B (long after the window) is +65.6 bp (t 1.93), with 1 VAL event.
- None.

## Sources (every fetch in scratchpad `r37/F/web/requests.log`, 122 requests, >= 1.2 s per host)

| series | span loaded (cut 2024-12-31) | use / status |
|---|---|---|
| Binance USDT-M BTCUSDT funding, `fapi.binance.com/fapi/v1/fundingRate` | 2019-09-10 08:00 .. 2024-12-31, 5,819 stamps (00/08/16, no gaps) | PL predictor and realised rate. **data.binance.vision monthly fundingRate zips exist only from 2020-01** (2019-09..12 are 404; its S3 listing shows 2020-01..05 only), so the REST endpoint was used |
| Binance ETHUSDT funding | 2019-11-27 .. 2024-12-31, 5,585 | ETH information cells |
| Binance BTCUSDT premium index, 1 h klines (`/fapi/v1/premiumIndexKlines`) | 2019-12-24 .. 2024-12-31, 44,036 h | PP predictor (Binance formula), corr 0.83 with the realised rate (PL 0.79) |
| Bybit inverse BTCUSD funding (`api.bybit.com/v5/market/funding/history`) | **2018-11-15** .. 2024-12-31, 6,714 | IS-early check (before Binance), F2 carry before 2019-09 |
| Bybit linear BTCUSDT funding | 2020-03-26 .. 2024-12-31, 5,227 | signal statistics only |
| OKX `/api/v5/public/funding-rate-history` | **last ~3 months only**; `after=2021-01-01` and `after=2025-01-01` return empty | unusable for history |
| BitMEX API / `public.bitmex.com` | - | API 403. The public host serves a wind-down page ("BitMEX ceased trading on 23 September 2026"). Unusable (2 tries) |
| IC M1 BTCUSD / ETHUSD (local cache) | 2017-08-28 / 2017-09-25 .. 2024-12-31 | prices, actual spreads |

## Method (as declared)

- **Predictors**, both known before the window opens:
  - **PP** = Binance's formula P + clamp(1 bp - P, ±5 bp), with P the linearly weighted hourly premium closes
    T-8h..T-1h;
  - **PL** = the last published rate (stamp T-8h).
- **Tiers**: A3 \|f̂\| >= 3 bp, A5 >= 5 bp.
- **Legs**:
  - PRE: side -sign(f̂), from the close of IC bar T-w to the close of bar T-1;
  - POST: +sign(f̂), from the close of bar T to the close of bar T+w;
  - V: both legs.
- **Windows** w = 15 / 30 / 60 min.
- **Cost**: half the actual spread at each leg. No commission, no swap.
- **Checks**: spread x1.5, +1 min on both legs.
- **Statistics**: t clustered by UTC day.
- **Random control** (200 seeds): a random start minute within the stamp's ±8 h, >= 90 min from any stamp; the side
  and f̂ are recomputed at the random time.
- **Placebos**: the stamp shifted by ±2 h and ±4 h (±4 h = BitMEX's 04/12/20 clock).
- **Multiple testing**: a day-block sign-flip null, max over the 36 cells.
- **Eras**:
  - IS 2019-09-10..2021-12 (shortened: the Binance series start);
  - VAL 2022-24;
  - IS-early 2018-11-15..2019-09-09 on Bybit PL.

IS has 2.3 years and ~400 weekday stamps at A3. DEMO's IS t 2 needs a per-trade Sharpe of 0.10 there.

## Results (BTCUSD at IC, bp per trade; full grid in `r37/F/out/f1_BTCUSD.txt`)

| hypothesis | eras | mid IS / VAL (bp, t) | cost IS / VAL | net IS / VAL (t) | VAL / IS (mid) | per-trade Sharpe IS / VAL; power at VAL size (HOLD n) | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| F1 PP-A3 w15 PRE (short into the stamp when f̂ >= 3 bp) | IS, VAL | +5.98 (1.97) / +6.54 (2.40) | 7.31 / 4.17 | -1.33 (-0.47) / +2.37 (0.88) | 1.09 | -0.026 / +0.087; 0.64 (54) | 97.5 / 95.5 % | none (IS net) |
| F1 PP-A5 w15 PRE | IS, VAL | +8.86 (1.91) / +15.34 (2.68) | 7.70 / 4.31 | +1.16 (0.27) / +11.03 (1.98) | 1.73 | +0.019 / +0.379; 1.71 (20) | 97.0 / 97.5 % | none (IS net t; x1.5 IS -2.69; +1 min VAL +1.62) |
| F1 PP-A3 w30 PRE | IS, VAL | +3.38 (0.98) / +7.62 (1.01) | 7.55 / 4.28 | -4.17 / +3.34 (0.45) | 2.25 | -0.06 / +0.05 | 70.5 / 93 % | none |
| F1 PP-A5 w60 PRE (best IS net t of 36) | IS, VAL | +10.98 (1.69) / +9.47 (0.45) | 8.51 / 4.77 | +2.46 (0.38) / +4.70 (0.22) | 0.86 | 0.02 / 0.04 | - | none |
| F1 PL-A3 w15 PRE (best IS mid t of 36) | IS, VAL | +6.09 (2.37) / +3.33 (0.96) | 7.48 / 3.56 | -1.39 (-0.58) / -0.23 | 0.55 | -0.03 / -0.01; -0.05 (42) | 97.5 / 79 % | none |
| F1 POST legs (reopen side), 12 cells | IS, VAL | -5.3..+5.2 / -16.1..+4.9 | 7.7-8.6 / 3.8-4.8 | all IS < 0 (-2.8..-0.6 t) | - | < 0 | - | none (no rebound) |
| F1 V legs, 12 cells | IS, VAL | -6.1..+13.7 | 15-17 / 7.5-9.2 | all IS < 0 | - | < 0 | - | none |
| F1 IS-early, Bybit PL, PRE A3 / A5 w15-30 (2018-11..2019-09) | IS-early | +1.8 (0.60) .. +6.8 (1.25) | 8.0-8.2 | -6.3 .. -1.2 | - | < 0 | - | same sign, weaker |
| F1 ETHUSD, 36 cells (information) | IS, VAL | PL-A3 w15 PRE +5.10 (1.53) / +10.28 (2.94) | 82 / 11.4 | -76.8 (-13.9) / -1.11 | - | - | - | none (IS cost) |
| F2 hot-carry CME expiry, A short 15-16 London | IS, VAL | -11.5 (-0.40) / n 1 | 8.3 | -19.8 / - | - | - | - | none (wrong sign) |
| F2 hot-carry CME expiry, B long 16-17 London | IS, VAL | +65.6 (1.93) / n 1 | 7.1 | +58.5 (1.73) / - | - | 0.58 / -; n 10 | - | none (IS t < 2, no VAL) |
| F2 control: cold months / all months (= round 12 K5) | IS, VAL | A -21.0 / +22.0; B +33.3 / -27.1 | | | | | | signs flip, as round 12 found |

### F1 diagnostics (`r37/F/out/f1_diag.txt`)

- **By year**, PP-A3 w15 PRE, mid / net bp:

  | year | n | mid | net |
  |---|---|---|---|
  | 2020 | 154 | +7.4 | +1.2 |
  | 2021 | 250 | +5.1 | -2.9 |
  | 2022 | 6 | +21.9 | +7.4 |
  | 2023 | 18 | +8.2 | +5.0 |
  | 2024 | 68 | +4.7 | +1.2 |

  The mid is positive in 5 of 5 years and the net in 4 of 5. Net IS is negative because of 2021's cost.
- **Without 2020-03/04**: IS mid +3.50 (t 1.65), net -3.47.
- **Sign split**: positive funding carries the count; negative-funding stamps are few but large (IS n 20, +59 bp,
  mostly the 2020-03 and 2021-05 crashes).

  | era | positive-funding stamps | negative-funding stamps |
  |---|---|---|
  | IS | +3.22 (t 1.51), n 384 | +59 bp, n 20 |
  | VAL | +5.44 (t 2.10) | +19.9, n 7 |

- **Placebos**, PP-A3 w15 PRE, IS / VAL:
  - ±4 h (04/12/20 UTC): -2.2 (t -1.08) / -1.9 (t -0.48);
  - +2 h: -0.1 / -5.6;
  - -2 h: +5.6 (t 1.41) / +1.2.
- **Minute profile** (post hoc, information), signed move per slice:
  - IS: [-10, -5) +3.1 and [-2, 0) +1.9 (t 2.3), then -2.0 over [0, 10).
  - VAL: spread evenly over the 30 min before T, then -5.5 (t -1.3) over [0, 10).

  So the price keeps falling after the stamp instead of rebounding. That fits funding debits tipping thin-margin
  payers into liquidation, not payers reopening. The opposite side was not declared, so this is not registrable.
- **Mechanism dose** (all stamps, PRE return on PP): w15 IS -1.92 (t -2.04), VAL -0.94 (t -1.79); w60 IS -1.98 (t
  -3.47), VAL -2.06 (t -1.06). The size is about the funding paid, as the arbitrage bound in HYPOTHESES_F says.
- **Break-even**: IS net t 2 would need a round-trip cost <= 0.7 bp; IC's was 7.3. At today's ~1.7 bp (short side,
  paper_desk_costs_2026-10-29.md), PP-A5 VAL net would be +13.6 bp, but HOLD power at n ~20 is only 2.07.

## Cells and chance

| family | cells | best IS t (net) | best IS t (mid) | chance benchmark |
|---|---|---|---|---|
| F1 BTC | 36 | +0.38 (PP-A5 w60 PRE); most negative -2.79 (a POST cell) | +2.37 (PL-A3 w15 PRE) | day sign-flip null, max over the 36 cells: p50 1.95, p95 3.04, p = 0.27 |
| F1 ETH (information) | 36 | all IS net t <= -8 (cost 82 bp) | +2.07 | - |
| F2 | 2 (+2 controls, +2 K5 replication) | +1.73 (B) | +1.93 | expected max \|t\| of 2 ~ 1.1 |
| Dropped before any return | quarterly delivery basis (4 a year, round 12 K4 clock); funding interval / cap changes (no BTC event 2019-24); index-constituent changes (no public history) | | | |

## Correlation with C3

No survivor, so not computed.

## What this says

1. **The funding-paid pressure exists and has the declared sign into the stamp, at about the size of the funding.**
   It is the first conditional stamp effect in the repo: round 3's unconditional clock showed <= 3 bp and no sign.
   But it is a few bp on a 25-55 bp 15-min sd. In IS it sits exactly at IC's 2020-21 BTC cost at those minutes.
2. **The trade count disappears when the cost falls.** 2020-21 had hundreds of large-funding stamps at 7-8 bp cost.
   2022-24 had 92 (A3) / 35 (A5) at 4 bp. The bound "concession <= f" caps the edge at a few bp, so no conditioning on
   the rate can reach LIVE's power 3 in a 21-month HOLD unless funding returns to 2021 levels.
3. **The declared after-stamp rebound is absent.** The post-stamp drift is down, a liquidation-at-debit story. It was
   not declared and is left as information.
4. **Settlement-window variants conditioned on carry (CME BRR) are too rare.** 10 hot-carry expiries in IS, 1 in VAL,
   and signs as unstable as round 12 K5's.

## Directions that need the user

- **Grade BTC's IS at today's cost.** This is a rule change, like the pending one for indices. It would not rescue
  F1: the IS mid t is 1.97 / 1.91 even at zero cost, and HOLD power at the VAL size is <= 2.1. Value ~1 %.
- **Older BitMEX funding (2016-19, 04/12/20 stamps, the venue that dominated before Binance)** via a paid archive
  (Tardis or Kaiko). It would add IS stamps at 2017-19 costs (8-27 bp a round trip at IC), so value < 1 %.
- **A demo-only log of PP-A5 w15 PRE on post-2026-09 data.** It would have to be registered before looking, with
  ~10-20 trades a year at current funding levels. That is far too slow to ever reach a promotion t of 2.5. Not
  recommended.

## Files

- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r37/F/scripts/`):
  - `fetch.py` (logged fetcher), `pull_funding.py`;
  - `signal_stats.py`, `power_inputs.py` (pre-declaration, signal / unconditional only);
  - `f1.py` (36 cells, x1.5, +1 min, dose slope), `f1_diag.py` (flip null, years, sign / hour split, random control,
    placebos, minute profile, IS-early), `f1_placebo2.py`;
  - `f2.py`.
- Outputs (`r37/F/out/`): `f1_BTCUSD.txt`, `f1_ETHUSD.txt`, `f1_diag.txt`, `f2.txt`, `f1_BTCUSD_cells.npy`.
- Raw downloads (`r37/F/web/`): `binance_funding_*.json`, `binance_premium_1h_BTCUSDT.json`, `bybit_funding_*.json`,
  `requests.log`.
