# Pre-registration P2 (new-era test, approved by the user 2026-10-31): payer side 1 s after an extreme Binance funding stamp

Written 2026-10-31 14:50 UTC (from `date -u`), before any HOLD (2025-01-01..2026-10-29) price was pulled.
Only HOLD funding stamps were read (to count events: 10,035 with |f_prev| >= 30 bp). Rule declared in
[HYPOTHESES.md](HYPOTHESES.md) addendum P2. Approval: the user chose "Cho test kỷ mới" when asked whether P2, which
fails IS 2020-21, may be tested as a new-era rule (DISCOVERY 2022-24, HOLD once, LIVE-strength bar).

## Rule (fixed)
Event: Binance USDT-M stamp T with |f_prev| >= 30 bp (f_prev = previous stamp's realised rate; funding files as in
IS / VAL: full history for symbols ever top-40, first 75 days for other listings). Side: payer of f_prev (long after a
positive stamp, short after a negative one). Entry: last aggTrade price at T + 1 s (taker). Exit: last aggTrade price
at T + 60 s (taker). Costs 0.20 % round trip (0.12 % BTC / ETH). HOLD sample: 600 events drawn with numpy
default_rng(101) from the sorted event list (code/hold_p2.py).

## Evidence before HOLD
VAL sample 1 (seen, shaped the rule): +25.5 bp, t 3.36. VAL sample 2 (fresh): +31.2 bp, SR 0.340, t 4.87, every year
~+30 bp. IS fresh: +3.3 bp, t 0.15 (negative-funding side -60.9 bp in 2020-21): the reason this is a new-era test.
Expected HOLD t at VAL #2 size: 0.34 x sqrt(600) = 8.3; at half size 4.2.

## Pass bar (all of)
1. Net mean > 0 and t (UTC-day clusters) >= 2.5.
2. Entry at T + 2 s net > 0, and costs x1.5 net > 0.
3. 2025 and 2026 each net > 0.
4. >= 500 of the 600 events scored (data available).
Pass = new-era LIVE candidate (the user accepted the new-era split). Execution then needs a bot near Binance's
matching engine (Tokyo) that sends a market order within ~1 s of the stamp; a demo / small-size run measures real
fills before size.

## Code hashes at registration (sha256, first 16)
- `research/results/portfolio/round62_funding_capture/code/hold_p2.py` 1d44634a81da7796
- `research/results/portfolio/round62_funding_capture/code/capture.py` 72279cb1e5b275dd
- `research/results/portfolio/round62_funding_capture/code/event_syms.txt` 0658e3d46edd2c35

## HOLD result (run once 2026-10-31 15:02:46 UTC, hashed code; output code/hold_output_p2_2026-10-31.txt)
576 of 600 events scored (24 missing files). Net -5.7 bp / trade, median -12.4, SR -0.058, t -1.38, win 39 %; 2025
+5.2 bp, 2026 -15.9 bp; entry T+2 s -12.6 bp; costs x1.5 -15.7 bp. Positive-funding stamps +24.1 bp (n 22),
negative -6.9 bp (n 554). **Verdict: FAIL.** The 2022-24 seconds-after-stamp move is gone in 2025-26.
