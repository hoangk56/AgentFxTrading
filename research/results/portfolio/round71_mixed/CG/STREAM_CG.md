# STREAM_CG: CME bitcoin weekend gap fade (round 71)

## Answer: none (no LIVE, no DEMO, no PREREG_DRAFT)

The "CME gap fills" lore does not hold as a trade on Binance BTCUSDT / ETHUSDT perps. All 4 declared cells lose money in
IS and VAL, in 0-1 of 5 years, and in VAL they lose more than every one of 120 hour-of-week placebo anchors. Fading the
weekend move from the CME reopen + 6 min loses -28 to -129 bp/trade in IS (t -0.25 to -0.65) and -191 to -364 bp/trade
in VAL (t -2.0 to -2.7). The gap does get touched often (43-55 % of 2 % gaps within 3 days), which is where the lore comes
from: the median 3-day trade wins (+234 bp IS, +69 bp VAL). But the gaps that don't fill keep running, and those losses
outweigh the wins (negative skew). Weekend moves continue after the CME reopen. They do not revert.

Plan written first: HYPOTHESES_CG.md (2026-11-01 17:50 UTC). No 2025-26 data loaded (1m files 2020-01..2024-12 only,
funding cut < 2025-01-01). HOLD never opened.

## Setup (as declared)
- CME close C = Fri 16:00 Chicago, reopen R = Sun 17:00 Chicago, US DST rule computed in code (48 / 49 / 50 h spans on
  switch weekends). 20 weekends with a non-regular close / reopen are excluded by a fixed list (Good Friday, day after
  Thanksgiving, Friday / Monday Christmas, New Year, July 4). That leaves 241 regular weekends for BTC; ETH starts at the
  2021-02-12 weekend (CME Ether futures launch), 188 weekends.
- m = ln(P(R)/P(C)) on Binance perp 1m closes. If |m| >= k, fade (s = -sign m). Entry at the close of the 1m bar opening
  at R+5 min. Exit when price touches P(C) (filled at P(C)), or at the time stop H. Funding stamps are counted.
  Cost: 12 bp round trip (taker 5 + half-spread 1, each side).
- Cells: k in {2 %, 4 %} x H in {1 d, 3 d}, pooled BTC + ETH, t clustered by weekend.

## Declared cells, net bp/trade (base cost)
| cell | IS net | IS t | IS n (clusters) | VAL net | VAL t | VAL n (clusters) | years + | random % IS / VAL | power at VAL size |
|---|---|---|---|---|---|---|---|---|---|
| G2_1d | -30.5 | -0.46 | 66 (53) | -191.1 | -2.74 | 83 (59) | 0/5 | 38.3 / 0.0 | -2.77 (needs S 0.42) |
| G2_3d (primary) | -68.0 | -0.65 | 66 (53) | -193.9 | -2.00 | 83 (59) | 0/5 | 20.0 / 0.0 | -1.85 |
| G4_1d | -28.2 | -0.25 | 30 (24) | -330.2 | -2.72 | 39 (29) | 1/5 (2020) | 45.8 / 0.0 | -2.70 (needs S 0.62) |
| G4_3d | -129.3 | -0.65 | 30 (24) | -363.7 | -2.42 | 39 (29) | 1/5 (2020) | 6.7 / 0.0 | -2.32 |

The x1.5 cost and one-step-late variants change these by only a few bp; every one stays negative. The best real cell's
max-over-4 null beats 15 % of placebo anchors' best in IS and 0 % in VAL. The by-year, by-coin and by-side tables are in
out/report.txt.

By year (G2_3d): 2020 -5, 2021 -86, 2022 -230, 2023 -238, 2024 -119 bp. Both coins and both sides lose in VAL. The only
positive slices are ETH IS 2 %/1 d (+19 bp, t 0.21) and fading weekend drops in IS (+22-36 bp, t <= 0.36), which is noise.

## Random benchmarks
- (a) The brief's version: the same rule anchored to Mon-Thu 16:00 CT with a 49 h pseudo gap. In VAL the real weekend
  is worse than all 4 weekday anchors in every cell. In IS it beats 0-1 of 4.
- (b) 120 UTC hour-of-week anchors, excluding anchors within 24 h of the Friday close. Placebo medians are about -25 bp
  (IS) and -2 to -48 bp (VAL). The real weekend rule sits at the 7th-46th percentile in IS and the 0th in VAL.
- Fading any 49 h move is a slight loser after costs. The CME weekend is a worse version of it, not a better one.

## Power (declared before data, confirmed)
HOLD covers about 86 regular weekends. At VAL rates that is about 51 trades (2 %) or 24 trades (4 %). Reaching power 3
would need a per-trade Sharpe of 0.42 / 0.62, which is +300-450 bp a trade at the observed sd of 480-890 bp. LIVE was out
of reach a priori. DEMO needed only IS t >= 2, and the sign is wrong anyway.

## Information only (not a candidate): the opposite side
Following the weekend move (out/extra.txt) earns +167 to +340 bp/trade in VAL (t +1.75 to +2.52). In IS it earns +4 to
+105 bp (t 0.04-0.53). That side was not declared. It also fails DEMO's IS t >= 2, and picking it after seeing VAL falls
under the round 18 lesson (such rules keep about 1/4 of their VAL size). VAL is dominated by crash weekends that kept
going (2022-05 / 06 / 11). It fits round 37's continuation beyond salient levels and round 64's finding that crypto
moves continue rather than revert at 1-3 days. Do not register it.

## Pitfalls / problems
- cmegroup.com did not connect (curl error 7, research/data/cme_gap/requests.log; 2 requests, 0 bytes), and 1 WebSearch
  did not settle product-level holiday hours. So holiday weekends are excluded rather than modelled. That is 20 of 261
  weekends; it cannot flip a VAL t of -2.
- The Binance perp price at the CME close stands in for the CME settlement / last trade. The CME-perp basis moves slowly
  over a weekend, so the "gap" seen on the CME chart differs by a basis change of a few bp to tens of bp. That is small
  next to k >= 200 bp.
- A touch exit filled at the target price is optimistic, but the late variant (fill at the close of the next bar) changes
  results by < 10 bp.
- Pulled no new market data; research/data/cme_gap/ holds only the request log.

## Files
- HYPOTHESES_CG.md, STREAM_CG.md
- code/gap.py (calendar, loaders, trade simulation), code/report.py (cells, years, splits, benchmarks), code/extra.py
- out/report.txt, out/extra.txt, out/events.csv (427 weekend x coin rows, 2020-24 only)

## What a user decision could unlock
Nothing in this family. The fade is wrong-signed in both eras, and the continuation side lacks IS support. Real CME BTC
futures prices (a paid CME DataMine feed or an account) would only change the anchor by the basis. That would not
rescue a -190 bp VAL edge.
