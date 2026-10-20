# Round 23, stream P: practitioner / structural-flow hypotheses (2026-10-15)

Brief: [BRIEF.md](BRIEF.md) row P, and round13_structural/BRIEF.md for everything else. Every cell was declared in
[HYPOTHESES_P.md](HYPOTHESES_P.md) at 11:06 UTC (`date -u`), before any return was computed. One wording fix to P1's
"lh" window was made before the first run. No post-hoc cell was added. HOLD (2025-01 onwards) was not loaded: the
shared panel ends 2024-12-31, and Dukascopy H1 was read only for 2003-12..2015-12. Written 2026-10-15 11:14 UTC.

## Answer

**No candidate at LIVE or DEMO, and no PREREG_DRAFT.** I declared 6 families with 18 cells (14 primary, 4
replication or international). No cell has an IS net t of 2.0 or more on its declared side.

- The best IS net t is **+1.35**, for P3-slow (CTA flips at the 63/252-day horizons). It is negative in VAL.
- The best IS mid t of every family falls inside that family's permutation-null 95th percentile.
- Across all 14 primary cells, the best |t| (1.82) is below the max-of-14-normals median of 1.97.

The flows these practitioner notes describe are either absent from IC's CFD prices at a 1-5 day horizon, or the
wrong way round:
- Buyback blackout days were stronger than open-window days in IS.
- The "window of weakness" week after OPEX lost money short in VAL.
- Big-divergence quarter-ends moved with the quarter's trend, not against it.

## Step 1: source map

The full table is in HYPOTHESES_P.md (S1-S16): source, side rule, flow size, earliest date, events/yr, expected size
against cost, and a-priori power. Sources found with web search:
- **S1, vol-control:** S&P DJI Risk Control methodology (EWMA 0.94 / 0.97, max, leverage up to 150 %; SEC FWP for
  the S&P 500 Risk Control 10 % index); Barclays 2018 ($225bn of sales, ~$500bn tied to vol targeting); Nomura
  vol-control notes via SpotGamma.
- **S2-S3, pension rebalancing:** Harvey, Mazzoleni & Melone, NBER w33554 (2025). The threshold signal, -16 bp per
  sd next day, t > 4, 1997-2023. I read the full text.
- **S4, CTA flips:** Goldman, Nomura and BofA CTA trigger notes as reported (Hedgeweek, SpotGamma); Hurst, Ooi &
  Pedersen lookbacks.
- **S5, buybacks:** Goldman buyback-desk blackout estimates as republished (Tickmill 2024-12, 2025-07, 2026-04;
  ETF Trends/ValueWalk); SEC Rule 10b-18 timing.
- **S6, post-OPEX:** Karsan's "window of weakness"; McElligott's post-OPEX / post-VIX-expiry window (SpotGamma
  reposts 2020-21).

Relatives I did not retest, because the construction would be the same:
- MOC imbalance: round 11, round 12 J.
- S&P quarterly rebalance / quad witching: round 3, round 20 G.
- LETF, intraday momentum into the close, pinning, month-end WM/R, expiry auctions: rounds 3, 6, 10, 12, 13, 17, 20.
- HMM's Calendar x week4 month-end signal: rounds 3-4.

## Step 3: results (bp per trade; t clustered by entry date; costs = actual spreads at both fills + 0.6 bp FX/metals + swaps)

Abbreviations: "ctrl %" = the share of 200 random-entry seeds the cell beats, IS / VAL. "pow" = per-trade net Sharpe
x sqrt(1.73 x trades/yr), at the IS and at the VAL size.

| cell (mechanism) | where | IS mid (t) | VAL mid (t) | cost IS/VAL | net IS (t) | net VAL (t) | VAL/IS net | pow IS/VAL | n/yr | ctrl % | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1-top-cc vol-control Δexposure, top 20 %, close->close **(primary)** | US500 | +1.5 (0.28) | +12.5 (1.56) | 3.6/1.8 | -2.1 (-0.39) | +10.7 (1.33) | <0 | -0.21/1.01 | 59/48 | 16/81 | fails; IS 2020 -55 bp/trade, ex-Mar/Apr-2020 +2.2 (0.48) |
| P1-top-lh, last hour of t+1 | US500 | -1.1 (-0.43) | +3.8 (1.04) | 1.7/0.5 | -2.7 (-1.12) | +3.3 (0.90) | <0 | -0.60/0.68 | 59/48 | 25/80 | fails |
| P1-all-cc, every day | US500 | +5.6 (1.80) | +8.0 (1.99) | 3.9/3.2 | +1.7 (0.54) | +4.8 (1.20) | 2.9 | 0.29/0.91 | 231/251 | 80/94 | fails (mostly long = drift) |
| P1-all-lh | US500 | -0.4 (-0.32) | +2.1 (1.47) | 1.7/0.5 | -2.0 (-1.83) | +1.6 (1.10) | <0 | -0.98/0.84 | 229/249 | 56/93 | fails |
| P1-top-cc replication | US30+USTEC | +0.7 (0.12) | +12.5 (1.47) | 3.3/1.8 | -2.7 (-0.47) | +10.7 (1.26) | <0 | -0.34/1.25 | 118/97 | 2/90 | fails |
| P2-all HMM threshold rebalancing, equity-only **(primary)** | US500 | +0.9 (0.29) | -0.2 (-0.04) | 3.1/1.2 | -2.2 (-0.73) | -1.4 (-0.34) | - | -0.39/-0.26 | 238/251 | 100/78* | fails |
| P2-top, top tercile of the signal | US500 | +9.1 (1.64) | -1.5 (-0.25) | 3.1/1.0 | +6.0 (1.09) | -2.5 (-0.42) | <0 | 0.58/-0.32 | 84/71 | 100/42 | fails; ex-2020 -2.4 |
| P2-all pooled | US30+USTEC | +0.9 (0.29) | +0.9 (0.21) | 2.7/1.3 | -1.7 (-0.55) | -0.4 (-0.09) | - | <0 | 476/501 | 100/85* | fails |
| P2-intl, own signals | DE40+UK100+JP225 | +1.9 (0.86) | +1.7 (0.66) | 3.5/2.4 | -1.6 (-0.74) | -0.7 (-0.25) | - | <0 | 733/761 | 100/91* | fails (mid ~ cost/2) |
| P3-all CTA 21/63/252 flips, follow the change **(primary)** | 6 pooled | +3.1 (1.20) | +4.9 (1.10) | 2.2/2.1 | +0.9 (0.34) | +2.8 (0.62) | 3.1 | 0.20/0.51 | 239/225 | 92/92 | fails |
| P3-slow, 63/252-day flips only | 6 pooled | +8.0 (1.82) | -0.1 (-0.02) | 2.1/2.1 | +5.9 (1.35) | -2.2 (-0.31) | <0 | 0.81/-0.23 | 96/93 | 98/46 | fails; ex-2020 +1.2 (0.36) |
| P4-open-long, buyback open window 10:00-15:30 NY **(primary)** | US500 | +5.3 (1.72) | +1.5 (0.30) | 1.5/0.5 | +3.8 (1.22) | +1.1 (0.21) | 0.28 | 0.66/0.16 | 69/68 | 100/41 | fails; the mechanism test is the wrong way (below) |
| P4-LS, long open / short peak blackout | US500 | -1.5 (-0.64) | +0.5 (0.14) | 1.6/0.5 | -3.1 (-1.32) | +0.1 (0.01) | - | -0.71/0.01 | 138/139 | 27/54 | fails |
| P4-open-long replication | US30+USTEC | +4.4 (1.34) | +0.6 (0.10) | 1.2/0.4 | +3.2 (0.97) | +0.1 (0.02) | 0.04 | 0.70/0.02 | 137/136 | 100/23 | fails |
| P5-after-short, week after monthly OPEX **(primary)** | US500 | -21.5 (-0.76) | -50.3 (-1.46) | 4.7/0.4 | -26.2 (-0.93) | -50.7 (-1.47) | - | <0 | 12/12 | 78/19 | fails, wrong sign |
| P5-opexweek-long | US500 | +21.9 (1.15) | -29.2 (-0.71) | 8.3/10.4 | +13.6 (0.72) | -39.7 (-0.96) | <0 | 0.38/-0.73 | 12/12 | 25/2 | fails |
| P6 quarter-end, \|QTD\| >= 5 %, against QTD, T-5 -> T-1 **(primary)** | US500 | +43.4 (0.68) | -55.9 (-1.07) | 7.1/2.4 | +36.4 (0.57) | -58.3 (-1.12) | <0 | 0.34/-0.85 | 2/2 | 78/28 | fails (n 10 / 6) |
| P6-intl | DE40+UK100+JP225 | -34.9 (-1.03) | -78.4 (-2.02) | 8.3/3.6 | -43.2 (-1.27) | -82.0 (-2.13) | - | <0 | 6/3 | 15/5 | fails, wrong sign |

\* For the every-day cells the control permutes the sides over the same days. The permuted mix of a mostly-short
rule pays the index drift, so "beats 100 %" does not make up for a negative net.

The spread x1.5 and +1-minute rows (`out/post.out`) change no sign in IS. In VAL, P4-open-long +1 min drops from
+1.06 to +0.28.

PRE 2004-15 (information, Dukascopy H1 bid at 15:00 London, IC 2016-17 spread + 0.6 bp, swaps ignored):

| cell | PRE mid (t) | PRE net (t) | years net > 0 |
|---|---|---|---|
| P3-all, pooled | +5.1 (2.18) | +4.0 (1.72) | 9/12 |
| P3-slow, pooled | -0.5 | -1.6 | 4/11 |

The same FX/gold legs in IS:
- USDJPY: +5.6 (2.16) IS, +9.4 VAL.
- EURUSD: -1.4 IS, -4.3 VAL.
- XAUUSD: +10.8 (1.96) IS, -4.2 VAL.

No symbol holds the sign over PRE, IS and VAL in both variants.

P4 mechanism test (10:00-15:30 NY, long, mid):

| | open window | peak blackout | neutral | open - blackout |
|---|---|---|---|---|
| US500 IS | +5.3 (1.72) | **+8.2 (2.39)** | -2.6 | -2.9 (t -0.63) |
| US500 VAL | +1.5 | +0.4 | +2.5 | +1.1 (t 0.15) |

US30 and USTEC look the same: blackout days are at least as strong as open-window days. The open-long cell beats
random neutral days in IS only because neutral days (early in the quarter's first and third months) were weak.

## Best cell per family and chance

The chance benchmark is a sign flip per entry date, shared by the family's cells, 500 draws, on IS mid t.

| family | cells | best IS mid \|t\| | null median / 95th | best IS net t on the declared side |
|---|---|---|---|---|
| P1 vol-control | 5 | 1.80 (P1-all-cc) | 1.40 / 2.56 | 0.54 |
| P2 threshold rebalancing | 4 | 1.64 (P2-top) | 1.25 / 2.33 | 1.09 |
| P3 CTA flips | 2 | 1.82 (P3-slow) | 0.92 / 2.15 | 1.35 |
| P4 buyback windows | 3 | 1.72 (P4-open-long) | 0.99 / 2.28 | 1.22 |
| P5 post-OPEX | 2 | 1.15 | 1.07 / 2.12 | 0.72 |
| P6 quarter-end | 2 | 1.03 | 1.20 / 2.23 | 0.57 |

Max |t| of K normals is 1.97 / 2.91 (median / 95th) for K = 14, and 2.08 / 2.98 for K = 18. Nothing exceeds chance.

**Correlation with C3** (IS+VAL, information, since no cell survives). Daily P&L correlations are -0.012 to
+0.051, and monthly -0.11 to +0.11, for P1-top-cc, P1-all-cc, P2-all, P2-top, P3-all, P3-slow and P4-open-long. These
flows are independent of C3, but none has an edge.

## What this says

- **Vol-control (P1).** The model's de-leveraging days lost in IS:
  - 2020 alone was -55 bp per trade. Selling after the March 2020 vol jumps met the rebound.
  - VAL was +10.7 bp (t 1.33), carried by 2022 (+33).
  - The flow, if real, is swamped by the volatility-regime reversal after big days that rounds 13 and 17 saw in US
    indices. VAL/IS has no meaning when IS is negative.
- **HMM threshold rebalancing (P2).** It does not reproduce on the equity leg in 2016-24:
  - The every-day cell is +0.9 bp mid in IS and -0.2 in VAL. If the paper's -16 bp per sd carried over, IS mid
    would be about 10 bp.
  - The paper's effect sits in stock-minus-bond returns over 1997-2023. Part of it may be in the bond leg, which is
    not testable here (no bond data, and no bond CFD among IC's 26 symbols).
  - The top-tercile cell is 2020.
- **CTA flips (P3).** The next-day follow-through after a flip is +3-5 bp mid on a ~100 bp daily sd: about 1/30 sd,
  below cost plus swap in IS. The slow-horizon version decays to 0 in VAL. This is round 2/7/11's TSMOM conclusion
  seen from the flow side.
- **Buyback windows (P4).** The mechanism's sign is not in the data: blackout days are as strong as or stronger than
  open-window days. Peak blackout overlaps earnings season, and the earnings-season drift dominates any buyback bid
  of ~1 % of volume.
- **Post-OPEX weakness (P5) and quarter-end pension selling (P6).** These are 12 and 2 events a year. Both are
  wrong-signed in VAL, and neither has power even if real: at most 0.4 at the IS size.
- **The common pattern.** Flows that the sell side sizes at $20-70bn a week are visible in the press but not in 1-5
  day index returns net of IC's cost. Either they are absorbed within the day (round 12's lesson for every flow but
  gotobi), or they are pre-positioned, because the trigger levels are published.
  - Gotobi differs: its executors are price-insensitive and fix-bound, and its timing is to the minute.
  - Every flow tested here executes over hours or days at the executor's discretion.

## Surprises

- Peak buyback blackout (late in the quarter's last month to the 20th of the next) was the strongest 10:00-15:30 NY
  window in IS for all three US indices (+6-9 bp/day, t 1.8-2.4). This is the opposite of the practitioner claim.
  It is post-hoc information only: it is the earnings season.
- In VAL, the week after monthly OPEX gained (short -50 bp/week) and OPEX week lost. The "window of weakness" has
  no sign in 2022-24.
- In VAL, all six big-divergence US quarter-ends moved with the quarter's trend (n 6). Combined with round 4's
  month-end sign flip, quarter-end pension selling is not visible in index CFDs.

## Directions that need the user

| direction | earliest testable date | expected power | what is needed |
|---|---|---|---|
| Spot BTC/ETH ETF creation flows into the 16:00 ET NAV window | 2024-01-11 (BTC), 2024-07-23 (ETH) | unknown; ~250/yr, so it could matter if > 5 bp net | issuer / Farside daily flow files; post-2026-09 BTC data (2024 is VAL's last year, the rest is HOLD) |
| New-NISA retail yen selling early in the month | 2024-01 | ~0.5 at 12/yr even at 20 bp | a new era rule or data after 2026-09-24 |
| HMM rebalancing with the bond leg (stock minus 10-year) | 1997 (paper) | not tradeable at IC without a bond CFD; the equity leg failed here | 10-year yield or T-note futures history (price data) and a bond instrument |
| Risk-parity de-leveraging (stock-bond correlation and vol) | ~2010 | unknown | bond price data |
| True buyback blackout fraction from an earnings calendar | 2004+ | low (the mechanism sign failed on the calendar proxy) | S&P 500 earnings dates (vendor) |
| US Treasury buybacks | 2024-05 | n/a at IC | bonds not listed |
| SPX 0DTE dealer gamma (K3 found nothing unconditional) | 2022-05 | unknown | CBOE OI data |

## Untested ideas (and why)

- **Japanese life insurers' semiannual hedge plans and GPIF rebalancing.** Plans are published in late April and
  October, and GPIF's dates are undisclosed. No side is computable before the trade, and there are 2 events a year.
- **Central-bank gold buying.** PBoC reserves are published on the 7th and WGC data quarterly, so the side is known
  only after the release.
- **Russell reconstitution (US2000, 1/yr), MSCI / FTSE / Nikkei rebalances.** The index-level side needs
  constituent flows, and there is no power at 1-2 events a year.
- **GSCI/BCOM roll front-running (Goldman roll, 5th-9th business day).** It is a calendar-spread trade, and IC's
  single-contract CFDs cannot hold it.
- **Quarter-end window dressing / "leaning for the tape"** (Carhart, Kaniel, Musto & Reed 2002), last 30 minutes of
  the quarter. It is pre-2016 literature, 4 events a year, and power < 0.5. Not declared.
- **BoJ JGB purchase operations.** The side depends on the result, published after the operation.
- **HMM Calendar x week4.** Rounds 3-4 tested it, and the construction would be the same.

## Process notes

- Clock labels are bar starts. The price at clock T is the close of the bar labelled T - 1 min, and fills are one
  minute after the signal.
- The NYSE calendar was built from rules, with early closes listed.
- The P3 FX/gold lookbacks were seeded with 2015 Dukascopy 15:00 London closes. Index trades start 2017-01-03.
- The P6 IS events start in 2017, because 2016-Q1 is inside the burn-in and the other 2016 quarters had
  |QTD| < 5 %.
- Nothing under `research/` was edited, and no git command was run.

## Files

- Scripts, in `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r23/P/`:
  - `plib.py`: clocks, NYSE calendar, costs and stats.
  - `cells.py`: legs and controls.
  - `p126.py`: P1, P2 and P6.
  - `p345.py`: P3, P4 and P5.
  - `post.py`: chance benchmarks, the C3 correlation and the summary.
- Outputs, in `.../r23/P/out/`:
  - `p126.out`, `p345.out`, `post.out`.
  - `p126.pkl`, `p345.pkl`: the trade lists.
- Literature: `.../r23/P/lit/hmm.txt`, the full text of NBER w33554.
