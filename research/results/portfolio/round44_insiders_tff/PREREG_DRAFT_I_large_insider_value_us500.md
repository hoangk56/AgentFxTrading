# PREREG DRAFT (stream I, round 44): long US500 the morning after a large-cap insider dollar net-purchase surge

Written 2026-10-30 06:15 UTC. **Draft only, not registered. HOLD not opened. Stream I recommends not registering it**
(reasons at the end). It is written because the cell meets the DEMO numbers on IS and VAL, as the round rules require.

## Rule (exactly as graded; declared in HYPOTHESES_I.md 06:10 UTC before returns)
- Data: SEC DERA Insider Transactions Data Sets (quarterly Form 3 / 4 / 5 zips). Form 4 only (no 4/A), non-derivative
  rows with code P + A (open-market purchase) or S + D (open-market sale), shares > 0, 0 < price < 1e6. Filings where any
  reporting owner is a Director or an Officer. One filing is a buyer if its purchase value > its sale value. Per-filing
  dollar value capped at $10 M.
- Universe LARGE: the issuer's normalised name matches Vanguard Group's 13F-HR common-stock holdings of the prior
  year-end at value rank 1-500 (name normaliser `norm()` in scripts/lib.py).
- Filings dated D are assigned to D (rolled forward to the next NYSE trading day when D is not one).
- Series: weekly NPR_val = (VB - VS) / (VB + VS) over the trailing 5 trading days (VB, VS = capped buyer / seller
  dollars); z = (NPR_val - mean) / sd over the previous 250 trading days (>= 200 obs, today excluded).
- Trigger: z >= 1.5 on filing day D. Long US500 at 09:31 ET on the next NYSE trading day, exit 09:31 ET the trading day
  after (h = 1 trading day; over a weekend this pays three nights' swap). One position at a time.
- Bar: DEMO (IS t >= 2.0, VAL net > 0, beats >= 90 % of random entries). Cells tried: 104 in the stream (F1 64, F2 16,
  F3 24) + 8 by-products.

## Numbers (bp per trade, IC US500 quotes, half spread each leg + swap)
| era | n | mid (t) | net (t) | x1.5 spread | +1 min | ex 2020-03/04 | years > 0 | random beat | calendar-matched beat |
|---|---|---|---|---|---|---|---|---|---|
| IS 2016-21 | 130 | +29.8 (2.62) | +25.3 (2.23) | +24.4 | +25.5 | +13.0 (t 1.88) | 6 / 6 | 1.00 | 1.00 |
| VAL 2022-24 | 51 | +6.1 | +2.5 (0.13) | +2.2 | +3.3 | +2.5 | 2 / 3 | 0.61 | 0.48 |
- By year net: 2016 +40.1, 2017 +11.9, 2018 +3.8, 2019 +9.5, 2020 +113.6 (16 trades, 15 in 2020-03/04), 2021 +6.5,
  2022 -3.1, 2023 +32.9, 2024 +6.3.
- Without the top 3 trades: IS +14.8, VAL -10.3. Without the top 5: IS +10.0, VAL -18.0.
- Per-trade Sharpe IS 0.195, VAL 0.018. VAL / IS 0.10 (decaying).
- Expected HOLD trades at the VAL rate: ~29 (2025-01..2026-09). Expected HOLD t at the VAL size: 0.018 x sqrt(29) =
  **0.10**; power at the IS size 1.06.
- Expected demo trades per year: ~17 (VAL rate).
- Daily P&L correlation with C3 (IS + VAL): -0.008.
- Neighbour k 1.0: IS n 210 net +16.5 (t 2.09), VAL n 72 +2.2 (t 0.15), ex 2020-03/04 IS t 1.58.

## Stop and promotion rules (if the lead registers it anyway)
- HOLD: one look; net < 0 -> drop.
- Demo: 0.01 lot (US500), stop the demo if cumulative net after 20 demo trades is < 0.
- Promotion to LIVE only if HOLD + demo pooled t >= 2.5 (LIVE bar otherwise unreachable: power 0.10).

## Why stream I recommends not registering
- **At chance:** the best-of-104 null (200 circular shifts of every insider series inside IS) has a max IS net t median of
  2.57 and p95 4.10; P(max >= 2.23) = 0.68.
- **2020-dependent:** without 2020-03/04 the IS t is 1.88 (< 2.0); 15 of 130 IS trades are in those two months.
- **VAL is noise:** +2.5 bp (t 0.13), beats 61 % of random entries and 48 % of calendar-matched entries (same week-of-
  quarter and weekday mix), negative without its top 3 trades.
- **Mechanism unclear:** large-cap insider purchases are ~$0.1 M a day against ~$50 M of sales, so the z measures
  *missing large-cap selling* (blackout weeks, falls), not informed buying. The count version of the same universe
  (LARGE_cnt_W) does not reproduce it (best IS t 0.7).
