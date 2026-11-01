# Round 62: extreme altcoin funding stamps on Binance (receive through the stamp; payer side after it), 2026-10-31

Declared in [round62_funding_capture/HYPOTHESES.md](round62_funding_capture/HYPOTHESES.md) (13:03 UTC; addenda P1 13:16,
P2 later, each before the data it was checked on). Code `round62_funding_capture/code/` (`capture.py`, `run.py`,
`run_p1.py`, `latency.py`, `aggtrades_vision.py`). Data (git-ignored, research/data/binance/): perp_1h (+-4 days around
24.7k stamps with |f_prev| >= 10 bp, 326 symbols, pre-2025), perp_1m_stamps (T..T+62 min for 4.1k stamps >= 30 bp),
aggtrades_stamps (3 random samples of ~200 stamps from data.binance.vision daily aggTrades, window T-5 s..T+60 s).

## R (declared): receive f through the stamp (T-1h .. T+1h), |f_prev| >= 30 bp
IS n 2,096 -110.6 bp (t -1.54); VAL n 1,985 +2.5 bp (t 0.16); random 0 % / 65 %. Funding +29 / +59 bp, price -120 /
-37 bp, almost all of it in the hour after the stamp (-108 bp t -3.50 / -70 bp t -7.13). **FAIL.**

## P1 (declared after a 25 % look): payer side, open -> close of the 1h bar after the stamp
| | IS 2020-21 | VAL 2022-24 |
|---|---|---|
| all, net / trade | +85.4 bp, t 2.76, n 2,096 | +49.7 bp, t 5.05, n 1,985 |
| 243 symbols unseen when declared | t 2.84 | t 4.47 |
| tiers 10 / 50 / 100 bp | +6.5 / +181 / +174 | +4.6 / +72 / +135 |
| random same-symbol hours beaten | 100 % | 100 % |

Every year positive, costs x1.5 positive, dose monotone, both sides positive, corr with C3 0.02. **But the edge is the
first trade after the stamp**: on 1m klines, entry at T+1 min gives IS +51.5 bp (t 1.24) and VAL -11.6 bp (t -1.13);
the first minute carries +33 (IS) / +62 bp (VAL). P1's "open of the bar" is not an executable price.

## P2 (declared after the first VAL aggTrades sample): entry last trade at T+1 s, exit at T+60 s, taker both legs
Price path after the stamp (VAL sample 1, payer side, vs the last pre-stamp trade): median +4.7 bp at 1 s, +8 at 3 s,
+26 at 5 s, +40 at 10 s, +42 at 59 s; entering at T+5 s already loses.

| sample (random stamps >= 30 bp) | n | net / trade | median | SR | t (day cluster) | years |
|---|---|---|---|---|---|---|
| VAL #1 (seen, seed 7; exit 59 s) | 197 | +25.5 bp | +10.0 | 0.256 | 3.36 | 2022 +31.9, 2023 +14.5, 2024 +32.3 |
| **VAL #2 (fresh, seed 13)** | 198 | **+31.2 bp** | +16.1 | 0.340 | **4.87** | +30.2, +32.1, +30.8 |
| **IS (fresh, seed 11)** | 192 | **+3.3 bp** | +20.7 | 0.034 | **0.15** | 2020 -2.4, 2021 +4.4 |

Entry at T+2 s: VAL #2 +25.2 bp (t 4.37), IS -3.2. IS split: positive-funding stamps (payer = long after) +35.4 bp
(n 128); negative-funding stamps -60.9 bp (n 64). VAL stamps are almost all negative funding, and positive.

**Verdict: no LIVE or DEMO candidate under the user's bars** (P2 fails IS t >= 2.5 / 2.0). The side that works in
2022-24 (short after a large negative stamp) lost in 2020-21. Calling 2022+ a new regime (4h / 1h intervals and wider
caps on Binance alts from 2023, negative-funding squeezes) would be chosen after seeing the data. HOLD not opened.
Decision for the user: accept a new-era test (DISCOVERY 2022-24, HOLD 2025-26 opened once on a declared random
sample of ~600 stamps, LIVE-strength bar). At VAL #2 size the HOLD power would be ~8; at half size ~4. Execution would
need a bot co-located near Binance (Tokyo) that fires within ~1 s of the stamp.

## P2 new-era HOLD (user-approved, registered in [PREREG_P2_post_stamp_1s.md](round62_funding_capture/PREREG_P2_post_stamp_1s.md))
600 random HOLD stamps (576 scored): -5.7 bp / trade (t -1.38), 2025 +5.2, 2026 -15.9, entry T+2 s -12.6. **FAIL**;
P2 is dropped for good. With rounds 58-59, every crypto funding edge found today was strong in 2022-24 and gone in
2025-26.
