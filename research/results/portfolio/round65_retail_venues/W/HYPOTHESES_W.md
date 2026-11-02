# Stream W hypotheses: Upbit warning / delisting notices -> Binance USDT-M perp

Written Sun Nov 1 11:11:57 UTC 2026 (from `date -u`), after the notice history and the event list were built and
before any price or return was requested or computed. HOLD (2025-01-01..) is never requested, loaded or counted.

## Data (reachability established)
- **Upbit notices.** `https://api-manager.upbit.com/api/v1/announcements?os=web&page=P&per_page=20&category=all`
  (the JSON the upbit.com notice page itself calls) and `/api/v1/announcements/<id>` (body).
  - robots.txt of api-manager.upbit.com: 200, one comment line, no rules (nothing disallowed).
  - robots.txt of upbit.com and sg.upbit.com: `User-agent: * / Disallow: /` -> those hosts are not used.
  - api.upbit.com robots.txt: 404 (not needed here).
  - 298 list pages = 5,953 notices, 2017-10-27..2026-10; first_listed_at is the post time (KST, converted to UTC).
    The ids missing from the list (94 in 2020-21) were sampled (6 of 6) and are "뉴스" press items, not deleted
    notices. 116 candidate bodies fetched.
  - Timestamps checked against news for LTC (warning 2022-05-23, delisting notice 2022-06-08, end 06-20), OMG / SRM
    (warning 2023-03-29), KAVA (warning 2022-11): consistent.
- **Binance.** k2rule.py copied to W/code/k2rule.py (only the log folder changed: research/data/upbit_notices/);
  public fapi 1m klines for fills, local / fapi funding. Local 1h perp files for random draws. Spot BTC-pair 1h
  monthly klines from data.binance.vision (<= 2024-12 files only) for the mechanism check M.

## Mechanism
The mirror of K2. An Upbit warning designation (투자유의 / 거래 유의 종목 지정: deposits stop at once, delisting
review) or an end-of-trading-support notice gives Korean retail holders a dated reason to sell on one venue. Deposits
are closed, so arbitrage into Upbit is blocked and the selling should spill into the global price through
arbitrageurs who can withdraw. Side fixed: **short the alt USDT-M perp, long BTCUSDT perp, equal notional.**
A third, weaker class: 유의 촉구 (caution urge, no deposit stop), an attention shock on a large coin.

## Events (declared filters; built by code/events.py from titles and bodies, no prices)
- W = title contains 유의 종목 지정 (any spacing), excluding 기간 연장 / 해제 / 유지 and swap- or migration-driven
  designations (스왑, 전환, 추가( in the title, e.g. NU->T, ENJ mainnet).
- D = title contains 거래(지원) 종료, excluding 사유 및 / 정정 / 스왑 / 관련 안내 follow-ups; coin must have its own
  block with an end date (coins lifted in the same notice are not events). Deadline parsed from the block / title.
- U = title contains 유의 촉구 with a coin ticker in the title, excluding 스왑 / 전환 (e.g. LSK network change).
- W and D: the KRW market must be among the target markets (BTC-market-only notices, e.g. LINA, LUNA, FOR, are not
  Korean-retail KRW flows). U: no market filter (none stated).
- Binance perp SYM (or 1000SYM) trading >= 7 d before the notice and >= 1 d after it; first notice per (class,
  coin) within 30 d.
- **Resulting counts.** IS 2020-21: **0 events in every class**. Upbit's 2020-21 warnings / delistings (377
  coin-notice rows 2020-24, 310 of them in 2020-21) were small Korean or privacy coins with no Binance perp at the
  time (near misses: BTS perp started 4 days after its warning, ZEN 7 months after). VAL 2022-24: W 4 (LTC, KAVA,
  WAVES, OMG), D 3 (LTC, OMG, ENJ KRW), U 15 (TRX, WAVES x3, CRV x2, KAVA, MKR, LINA, KNC, XRP, OGN, OCEAN, STX,
  STMX). List: events_kept.csv; all rows: events_all.csv.

## Rule and grid (7 cells)
- Entry: close of the 1m bar starting at floor_minute(N) + 60 min (k2rule.px; up to 4 later minutes), N = post time.
- Exit: entry + 24 h or + 72 h (W, D, U); for D also "to deadline": the 1m bar starting at Upbit's end time.
- Cells: W24, W72, D24, D72, D-deadline, U24, U72.
- Costs: 42 bp per trade (K2) + real funding on both legs (k2rule.trade). Sensitivities: costs x1.5, entry 5 min
  later, entry at N + 2 h.
- t clustered by entry day. Random benchmark (gross, local 1h closes): (a) other universe perps shorted vs BTC at
  the same hour, (b) the same coin at random hours 30-180 d before N; 500 draws of the event-count mean.
- Overlap with Binance's own perp delistings (round 64 T events_all.csv) within 30 d, reported.

## Mechanism check M (descriptive, not a tradable rule)
For W and D events with a KRW market 2020-24 whose coin had a Binance spot SYM/BTC pair: gross ln(alt/BTC) change
from N + 1 h to N + 25 h and N + 73 h (1h closes), the run-up N - 24 h -> N + 1 h, and the same coin at random hours
N - 40 d .. N - 7 d. Spot shorting needs a borrow, so this only tests whether the forced flow moves the global price
(it gives an IS look the perp cannot).

## Bars and power (arithmetic before returns)
- With IS n = 0 the IS bars (LIVE t >= 2.5, DEMO t >= 2.0) **cannot be met by any cell**: the verdict is "none" for
  every cell by construction, whatever VAL shows. VAL and M are reported as descriptive evidence only; parameters are
  not chosen on VAL.
- Power at HOLD (1.83 yr, VAL pace): W 1.33 / yr -> n ~2.4, needs per-trade SR >= 1.94; D 1.0 / yr -> n ~1.8, needs
  SR >= 2.2; U 5 / yr -> n ~9.2, needs SR >= 0.99. K2's VAL SR was 0.25. LIVE is out of reach for every class even
  pooled (W + D + U ~ 7.3 / yr -> n ~13, needs SR >= 0.83).
- No PREREG_DRAFT unless a cell meets the IS bars, which it cannot.
