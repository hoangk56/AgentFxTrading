# Round 54: single-stock CFDs (IC MT5) — data, cost model and three firm-level flows, 2026-10-30

Brief: [round54_single_stocks/BRIEF.md](round54_single_stocks/BRIEF.md). **The user approved this direction on
2026-10-30.** Research only (no MT5 account, bot or deploy). Same LIVE / DEMO bars as rounds 25-53. HOLD
(2025-01..2026-09) stayed closed: no 2025 / 2026 Dukascopy file was requested, every series cut at 2024-12-31 at
parse / load, EDGAR facts and 8-Ks filed after the cut dropped at parse.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. Two of the three firm-level flows are absent or wrong-signed in IC-listable
US large caps; the third (insider purchases) is real at mid on the first session after the filing but is eaten by the
cost of an opening fill. Opening fills dominate every verdict: Dukascopy's daily open is the session's first quote
(median spread 65 bp vs 7 bp at the close) and IC's $0.02 / share commission adds ~12 bp a round trip (20-40 bp on
cheap names). IC's real 09:30 spread cannot be checked offline.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| D | Dukascopy daily bid / ask for 263 US CFDs (221 stocks, 42 ETFs), 2016-09..2024-12 (all names from 2018), 4,070 files in ~26 min; 31 splits adjusted; IC MT5 cost model (USD 0.02 / share / side, financing EFFR +/- 3 %, max 1,000 shares); stocklib.py | data ready; random 3-day longs open -> close net -30 bp (gross +20, spread 36, commission 8, financing 6) | [DATA_D.md](round54_single_stocks/DATA_D.md) |
| E | H1 Hartzmark-Solomon blackout selling (short top stock-comp / cap quintile t+1..t+3, US500 hedge); H2 large-cap post-earnings drift 1-5 days; 5,340 releases of 204 firms; 28 cells | **none**: H1 wrong sign at mid (top quintile -29.5 bp IS / -29.1 VAL, high-comp tech names outperform), net -93 / -99; H2 full-reaction follow 3 d mid +17.1 (t 1.62) / +9.9 below 27-33 bp cost; best IS net t -0.94 | [STREAM_E.md](round54_single_stocks/STREAM_E.md), [HYPOTHESES_E.md](round54_single_stocks/HYPOTHESES_E.md) |
| I | Cohen-Malloy-Pomorski opportunistic / CEO-CFO / cluster / all officer-director Form 4 purchases 2013-24 on D's stocks; open or D+1-close entry, 1-5 days, hedged / unhedged; 48 cells | **none**: best net IS t +0.42 (VAL -105.5); but the first session after filing is real at mid in both eras: all buys +17.6 / +19.7 bp open -> close D+1 (random-firm 1.00 / 0.99), CEO / CFO +46.5 / +59.3 (1.00 / 1.00); nothing after day 1; opening round trip 95-137 bp | [STREAM_I.md](round54_single_stocks/STREAM_I.md), [HYPOTHESES_I.md](round54_single_stocks/HYPOTHESES_I.md) |
| B | Firm-level buyback windows (round 47 run-rates x true 8-K dates): long top-quintile reopeners 1-5 days vs same-date cross-section or US500, blackout-start shorts; 24 cells | **none**: primary net IS -9.5 (t -0.61) / VAL -29.8; gross IS reopening effect is mostly post-earnings day-2 drift; buyback-vs-low-buyback same week IS t 1.85 / VAL t <= 0.6 | [STREAM_B.md](round54_single_stocks/STREAM_B.md), [HYPOTHESES_B.md](round54_single_stocks/HYPOTHESES_B.md) |

Correlation with C3: nothing survived; for information, insider CEOCFO h3 and ALL h1 cells correlate -0.005 / +0.022
with C3's daily returns.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Hartzmark-Solomon blackout selling on IC-listable large caps (wrong sign); large-cap post-earnings drift at 1-5 days
  at IC cost; firm-level buyback reopening / blackout windows.
- Firm-level insider purchases at open / close entries with 1-5 day holds (the day-1 drift remains open only with an
  intraday entry after the opening auction).

## Pitfalls
- Dukascopy stock CFDs are not split-adjusted (AAPL 4:1 on 2020-08-31); 3:2 ratios on crash days are not splits; old
  tickers (FB, PCLN, CTL, HCN, GPS, FOXA): match on CIK. Daily data has no dividends (IC adjusts on ex-dates).
- The daily open candle is the first quote of the session (median 65 bp spread; 46-103 bp on event mornings): never
  treat it as a tradeable open; enter at the close or at an intraday bar.
- github.com disallows ClaudeBot (the dukascopy-node instrument list came from unpkg.com, which allows it);
  www.sec.gov/robots.txt sometimes returns its rate-threshold page; data.sec.gov has no robots file.
- 28 % of releases lack a stock-comp rank (banks / insurers without the tag); market cap must use the raw price on the
  share-count date. ~78 % of insiders cannot be classified by the CMP rule (no trades in each of 3 prior years).
- Survivorship: today's list of names that existed before 2019.

## Directions that need the user
| direction | value |
|---|---|
| IC MT5 demo login to log real 09:30-09:45 spreads on US share CFDs (settles every open-fill stock rule) | enabling; DEMO ~5 % for the insider day-1 rule |
| A US share venue without per-share commission and with real opening spreads | LIVE < 1 %, DEMO ~3 % (large-cap drift) |
| Small caps (where Hartzmark-Solomon and classic drift live): not at IC / Dukascopy | LIVE ~1 % |
| Paid I/B/E/S surprises | LIVE < 1 %, DEMO ~2 % |

## State after round 54
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 55 tests the insider day-1
drift with an intraday entry after the opening auction (Dukascopy M1 on event days only).
