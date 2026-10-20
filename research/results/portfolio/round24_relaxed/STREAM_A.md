# Round 24, stream A: mechanisms that exist only from 2023-24 (new-era split)

Written 2026-10-15 ~12:00 UTC. Cells were declared in [HYPOTHESES_A.md](HYPOTHESES_A.md) at 11:56 UTC. All cells were
computed in one run at 11:58 UTC, so each declared rule saw TEST once. No rule was changed after the run.
Eras: DISCOVERY = mechanism start..2025-06-30, TEST = 2025-07-01..2026-09-24 (IC M1). HOLD was not opened.

## Answer
**No cell reaches LIVE, DEMO or RELAXED.** Every primary cell fails at DISCOVERY: the best DISCOVERY net t of a
positive cell is +0.46 (A1). RELAXED needs 1.5. Four cells are positive in TEST with net t 1.9-2.35 (A1, A1g, B1,
B3), but their DISCOVERY is flat or negative. The best TEST |t| of 10 cells, 2.35, is below the chance p95 of 2.82.
The diagnostics also argue against the ETF mechanism. Signing the 15:00-16:00 ET window by the **same day's** ETF flow
(an oracle nobody can trade) gives +3.1 bp mid in DISCOVERY (t 0.9) and -2.8 bp in TEST. So the creation pressure in
the fixing window does not show in BTC's price at all. This matches Schmidt & Kraft: the window carries volume, not
direction. No PREREG_DRAFT was written.

## Results (bp per trade; net = executable at IC: actual bid/ask at both minutes, 0.6 bp FX commission, swap)
| cell (source) | where | DISC mid (t) / net (t), n | TEST mid (t) / net (t), n | cost RT DISC/TEST | x1.5 / +1 min (TEST net) | random DISC/TEST | power 21 m (TEST size) | tier |
|---|---|---|---|---|---|---|---|---|
| A1 BTC 15:00->16:00 ET, side = sign of T-1 BTC ETF flow (Kaiko 2024, CF Benchmarks, Schmidt & Kraft 2026) | BTCUSD | +4.3 (1.24) / +1.6 (0.46), 366 | +6.8 (2.63) / +5.4 (2.07), 311 | 5.4 / 2.9 | +4.6 / +3.3 | 90 % / 95 % | 2.46 (DISC 0.51) | none (DISC t) |
| A1g same, \|T-1 flow\| >= $300m | BTCUSD | -0.1 (-0.02) / -2.7 (-0.44), 120 | +11.0 (2.34) / +9.7 (2.05), 99 | 5.2 / 2.8 | +9.0 / +6.3 | 51 % / 95 % | 2.44 | none |
| A2 BTC 16:00->16:55 ET, side = -sign(T-1 flow) (pressure ends) | BTCUSD | +0.9 (0.29) / -1.8 (-0.61) | -1.5 (-0.64) / -2.9 (-1.29) | 5.3 / 3.0 | - | 57 % / 51 % | <0 | none |
| A3 ETH 15:00->16:00 ET, side = sign of T-1 ETH ETF flow | ETHUSD | -1.9 (-0.34) / -15.0 (-2.69), 224 | +6.1 (1.51) / -5.3 (-1.32), 308 | 26.2 / 22.9 | - | 56 % / 71 % | <0 | none (IC ETH spread ~23-26 bp) |
| B1 USDJPY long 18:00 UTC -> 00:55 UTC fix on the NAV day after the 1st/8th/12th NISA card-tsumitate order days, gotobi days dropped (Rakuten, SBI, eMAXIS Slim terms; Mizuho, MUFG sizes) | USDJPY | -4.6 (-0.74) / -4.7 (-0.75), 32 | +5.2 (1.95) / +5.0 (1.93), 34 | 1.7 / 1.3 (+swap +1.1 / +0.8) | +4.8 / +4.3 | 11 % / 94 % | 2.34 (DISC -0.86) | none |
| B1b same, on the order day itself | USDJPY | +2.2 (0.45) / +1.0 (0.20), 40 | +3.5 (0.81) / +2.0 (0.45), 40 | 4.0 / 3.4 | - | 66 % / 65 % | 0.54 | none |
| B2 USDJPY short 00:55 -> 02:55 UTC on the NAV day | USDJPY | -2.6 (-1.10) / -3.3 (-1.41) | -0.1 (-0.06) / -0.8 (-0.36) | 0.8 / 0.8 | - | 25 % / 60 % | <0 | none |
| B3 EURJPY long, as B1 | EURJPY | +2.1 (0.37) / +1.3 (0.22), 32 | +6.1 (2.72) / +5.1 (2.35), 34 | 2.6 / 2.1 | +4.7 / +4.3 | 60 % / 99.8 % | 2.85 (DISC 0.26) | none (DISC t) |
| C1 USD-long basket 16:00->16:55 ET after US T+1 settlement (DTCC, Russell, BofA, Citi; side from TIC net foreign equity buying) | EURUSD, GBPUSD, AUDUSD short; USDJPY long | -0.35 (-1.27) / -1.24 (-4.49), 273 | -0.16 (-0.65) / -1.23 (-4.92), 311 | 1.2 / 1.5 | - | 13 % / 16 % | <0 | none (pre-T+1 2022-24 mid +0.10, t 0.5: no change) |
| C2 BTC short 10:00->10:30 ET ("10 a.m. dump" claim, press Feb 2026) | BTCUSD | -0.6 (-0.15) / -3.3 (-0.83) | +1.4 (0.38) / +0.0 (0.00) | 5.4 / 2.8 | - | 43 % / 72 % | 0 | none |

The "random" column is the percentile of the real mean net among 500 random-entry means. For BTC/ETH: same days,
side and hold, entry uniform in 09:30-20:00 ET. For B: same clock on other non-gotobi Japanese business days of the
same month. For C1: entry uniform in 08:00-15:00 ET. By year (net): A1 2024 +0.7, 2025 +4.3, 2026 +5.5. B1 2024 -5.0,
2025 +2.7, 2026 +2.1. B3 2024 +0.0, 2025 +6.1, 2026 +2.5.

Diagnostics (information only, never candidates):
| diagnostic | DISC mid (t) | TEST mid (t) | reading |
|---|---|---|---|
| A0a window signed by the **same day's** BTC ETF flow (untradable oracle) | +3.1 (0.91) | -2.8 (-1.07) | creations / redemptions do not move the 15-16 ET price |
| A0b window signed by BTC's previous 16:00->16:00 ET return | +6.5 (1.88) | +4.3 (1.65) | A1's TEST sign is momentum, not flow (flows follow price: Mazur & Polyzos 2025). Momentum is an excluded family |
| A0c unconditional long 15:00->16:00 ET | -4.7 (-1.36) | +1.0 (0.38) | no direction, as Schmidt & Kraft report |
| B1 by order day, TEST net | 1st: +7.7 (2.55, n 14); 8th: +3.4 (0.58, n 12); 12th: +2.7 (0.57, n 8) | DISC 1st -4.3, 8th -4.4, 12th -6.8 | post hoc, within chance |

## Cells tried and the chance benchmark
10 primary cells (A1, A1g, A2, A3, B1, B1b, B2, B3, C1, C2) and 3 diagnostics plus a by-order-day breakdown, which
are not counted. Chance for the max |t| of 10 normals: median 1.83, p95 2.82.
- DISCOVERY: the best net t of a positive cell is 0.46. The largest |t| are cost artefacts (A3 -2.69, C1 -4.49).
- TEST: the best net t is 2.35 (B3), then 2.07 (A1) and 2.05 (A1g), all within chance. Four of the 10 rules are
  positive in TEST and negative or flat in DISCOVERY. That is the opposite of a stable effect. Two common moves
  plausibly explain it. In TEST, BTC traded with momentum into the US afternoon (A0b), and the yen weakened through
  2025-26 (random-date controls on the same clock remove the drift for B, but not a regime in Tokyo-morning flows).

## Power
Even taken at face value, the TEST effect sizes give power 2.3-2.9 at a 21-month holdout (A1 2.46, B1 2.34, B3
2.85). That passes RELAXED's 1.5 but not LIVE's 3. At the DISCOVERY size, power is 0.5 / -0.9 / 0.3. NISA cells
carry ~24-29 non-gotobi trades a year. With the 2024 sd (32-35 bp over the 7 h long leg), a 5 bp effect needs ~5
years to reach t 2.

## Correlation with C3 (survivors: none; for information)
On DISCOVERY / TEST days: A1 daily -0.03 / -0.07, monthly -0.21 / +0.33 (18 / 15 months); B1 daily 0.00 / -0.01,
monthly +0.09 / +0.25; B3 daily 0.00 / -0.01, monthly +0.15 / +0.23. **Overlap with C3: 25 of the 91 NISA NAV days
(27 %) in 2024-01..2026-09 are gotobi days**, which C3 already trades at the same fix. The 8th often rolls to the
gotobi Friday 9th/10th, and the 1st rolls to the 4th-5th in January. They were dropped from B1-B3. B1b (order day)
dropped 11 of 91.

## Data fetched (no prices)
- US spot BTC ETF daily flows (Farside "Bitcoin ETF Flow - All Data"). farside.co.uk returns 403 here, so two
  captures were used: GitHub firemansghost/btc-risk-dashboard-V3 `public/data/cache/etf/2026-09-08.html` (800 KB,
  rows 2024-01-11..2026-09-04) and the Internet Archive capture of 2026-10-01 03:51 UTC (zstd, rows to 2026-09-30).
  They agree on all 681 common completed rows. Also the SoSoValue history.json from the same repo (not used).
- US spot ETH ETF daily flows: Farside, Internet Archive capture 2026-10-01 03:51 UTC (rows 2024-07-23..2026-09-30).
- Stored in scratchpad r24/A/dl/farside (2.4 MB raw) and r24/A/out/{btc,eth}_flows_wb1001.csv. Holiday calendar
  r24/A/out/cal.json (holidays 0.106).
- No Dukascopy fetch: the IC cache covers every era, and nothing survived to justify extending TEST past 2026-09-24.
  Nothing was written under research/data/.

## Surprises and caveats
- **The ETF fixing window has volume but no price pressure.** Even the same-day flow sign does not predict the
  window's return. Creations seem to be absorbed by liquidity providers who pre-hedge or net them; most ETF flow is
  priced at the BRRNY by agreement, so the market impact is spread outside the window. The paper's verdict (volume
  and volatility, not direction) holds on IC's BTCUSD.
- Flow-date convention: if Farside dated a row by the order date, not the trade date, then A1 itself is the direct
  mechanism test (orders placed T-1 for trade date T). Either way, A1's DISCOVERY is flat (+1.6 net, t 0.46), so the
  verdict does not depend on it.
- In-kind creations began after the SEC's July 2025 approval (inside TEST). A1's TEST gain cannot be tied to it,
  because the same-day oracle is negative in TEST.
- IC's BTC round-trip cost fell from 5.4 bp (2024-H1 2025) to 2.9 bp (TEST). ETH costs 23-26 bp at IC, so no ETH
  window rule can work there.
- C1: the US-close USD funding window shows no USD bid after T+1 (mid -0.35 / -0.16 bp, pre-T+1 +0.10). EURUSD and
  GBPUSD rose slightly after the US close in 2024-25, against the declared side.

## Directions that need the user
- None of the 2024+ mechanisms here has a DISCOVERY effect, so more data alone (post-2026-09 prices) will not rescue
  them. Waiting for TEST-only effects to repeat would be a post-hoc pick: B3 (EURJPY into the fix on NISA NAV days),
  B1 1st-of-month, and A1 / A0b BTC afternoon momentum. Under round 18's rule they should be expected to keep about 1/4
  of their size.
- If the user wants NISA flows tested properly: daily (not monthly) investment-trust FX data does not exist publicly.
  MOF's weekly "investment trust management companies" outward portfolio investment, by week, could size the flow per
  week and condition on it (needs a declared rule; ~70 weeks in DISCOVERY).
- Farside is blocked from this machine. Future flow data would need a GitHub or Internet Archive route, as here, or a
  paid API (SoSoValue, CoinGlass).

## Files
- Hypotheses: research/results/portfolio/round24_relaxed/HYPOTHESES_A.md
- Scripts: /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/4b8ace6a-8940-44d5-a772-50d419f9fb6d/scratchpad/r24/A/scripts/
  (a24.py helpers, run_cells.py cells, parse_farside.py, make_cal.py)
- Outputs: .../scratchpad/r24/A/out/results_A_B_C.json, trades_A_B_C.csv (per trade), run1.log
