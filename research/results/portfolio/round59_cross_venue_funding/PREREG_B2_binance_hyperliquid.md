# Pre-registration B2: Binance vs Hyperliquid perp-perp funding spread (round 59), 2026-10-31

Written before any HOLD (2025-01-01..2026-10-29) number of this rule was computed (time in "Run" from `date -u`).
Rule declared 12:02 UTC in [HYPOTHESES.md](HYPOTHESES.md) (B2 = B1's rule and thresholds, venue Hyperliquid).

## Rule (fixed)
Coins: the 30 in `code/hl_top30.txt` (Binance USDT-M perps also on Hyperliquid, ranked by mean Binance volume
2023-06..2024-12; the same 30 in HOLD, no additions). Each day at 00:00 UTC: signal = trailing-7-day mean of
(Binance daily funding - Hyperliquid daily funding) x 365. Enter when |signal| > 15 %/yr (short the dearer venue, long
the other, equal coin quantity), exit when |signal| < 5 %/yr or the sign flips; K = 10 pairs ranked by |signal|;
constant notional. Costs per side: Binance 0.05 % + Hyperliquid 0.045 % taker + 4 x 0.03 % half-spread (0.01 % BTC /
ETH). Code `code/xvenue.py` `simulate`, `code/b2_hold.py`.

## Evidence before HOLD (DISCOVERY 2023-06..2024-12; Hyperliquid starts 2023-05, so no IS 2020-21 era exists)
Net +16.30 %/yr, vol 1.52 %, t_nw 6.81; excess over Fed funds on 2/3 margin +13.49 % (t 5.79); 2023 +14.79 %, 2024
+11.11 %; costs x1.5 +13.79 %; one day late +15.45 %; beats 100 % of random pair books; 190 episodes, median 15 days.
Expected HOLD t at DISCOVERY size ~7.

## Tier rule
The user's LIVE bar needs IS 2016/2020-21 and VAL eras; a 2023+ venue cannot have them. The HOLD bar below is the
LIVE-strength test for a new-era rule (round 24's new-era split, but with LIVE thresholds instead of RELAXED). If it
passes, B2 is reported as "new-era LIVE candidate": LIVE needs the user to accept the new-era split.

## Pass bar at HOLD (all of)
1. Net > 0, t_nw >= 2.5, and excess over cash > 0.
2. Net > 0 at costs x1.5 and with the signal lagged a day.
3. 2025 and 2026 (to 10-29) both net > 0.
4. Beats >= 80 % of 500 random pair books.

## Code hashes at registration (sha256, first 16)
- `research/results/portfolio/round59_cross_venue_funding/code/xvenue.py` 78c8e9384157d23d
- `research/results/portfolio/round59_cross_venue_funding/code/b2_hold.py` ca1dcd42065a6208
- `research/results/portfolio/round59_cross_venue_funding/code/hl_top30.txt` a555c6db46a39f7f
- `research/results/portfolio/round58_unconstrained_carry/code/carry.py` 50a3b95efc5d83ad
## Run: Sat Oct 31 14:35:53 UTC 2026

## HOLD result (run once, hashed code; output code/hold_output_b2_2026-10-31.txt)
Net +0.74 %/yr, vol 0.79 %, t_nw 1.27; excess over cash -0.35 % (t -0.64); 2025 +0.99 %, 2026 +0.36 %; costs x1.5
-1.36 %/yr; late +0.18 %; random beaten 100 %; 180 episodes. **Verdict: FAIL** (items 1, 2). The 2023-24 spread
(+16 %/yr) was arbitraged away in 2025-26, like the spot-perp carry in round 58.
