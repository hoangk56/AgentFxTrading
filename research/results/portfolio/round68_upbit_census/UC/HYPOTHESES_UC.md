# Stream UC (round 68) hypotheses: census of Upbit notice categories at seconds

Written Sun Nov 1 15:26:33 UTC 2026 (from `date -u`). At this point only titles / categories / stamps from stream W's
list cache (research/data/upbit_notices/raw/list_all, read-only), local perp start dates (perp_1d, N0's k1m launch
cache: first-bar time only) and two robots.txt files have been read; a body pull for one category (DWSUSP, below) is
running. **No aggTrade has been downloaded, no price, path or return computed or looked at.** HOLD (2025-01-01..) is
never requested, loaded or counted: notices with N >= 2025-01-01 are dropped at load, and every requested daily file is
dated <= 2024-12-31 (an event whose N + 61 min would cross into 2025 is dropped).

## Question
Does any Upbit notice category other than the KRW listing (A2's set) move the named coin's Binance USDT-M perp vs
BTCUSDT perp in a direction still open 5 s after the notice stamp `first_listed_at` (whole seconds, publish time,
A2's check)?

## Notices and category rules (code/census.py; declared before prices)
- Source rows: all 3,349 list rows with 2020-01-01 <= N < 2025-01-01 UTC; Upbit category NFT dropped (no coins).
- Title cleaning: trailing edit suffixes that carry outcome text ("(완료)", "(기간 연장 …)", "(재개 …)", "(종료)",
  "(변경 …)", "(연기 …)", "(정정)"…) are stripped before classification and coin extraction. Spaces are removed.
- **Excluded first:** LISTING = stream A's notice ids (A/notice_events.csv), any 거래 / 이벤트 title that announces a
  market addition or opening (마켓 (디지털 자산|코인) 추가, 신규 상장, 신규 거래 지원, 거래 지원 개시 / 예정,
  마켓 오픈, 상장 기념, 마켓 TOP 트레이딩; BTC- and USDT-market additions too: tested in round 65). ROUTINE =
  payment / result / holdings / audit / terms titles (지급 안내, 지급 완료, 당첨, 결과, 보유수량, 실사, 이용약관,
  개인정보): repeated distributions (weekly GAS / VTHO, monthly airdrop payouts) and admin notices, not news.
- **Categories (first match wins, in this order):**

| # | name | title rule (regex on the cleaned title) | declared side | mechanism |
|---|---|---|---|---|
| 1 | WARN | 유의종목지정, 유의촉구, 거래지원종료, 투자유의 | short | stream W's flows (warning, delisting, caution urge) |
| 2 | SWAP | 스왑, 심볼변경, 리브랜딩, 액면분할, 티커/이름/명칭변경, 마이그레이션, 토큰전환, 컨버전, 리디노미네이션 | none | mechanical; direction unknown |
| 3 | AIRDROP | (에어드랍 / 스테이킹 / 지급)(및…)?(지원)(예정)?안내, 스테이킹 지원 디지털 자산 추가, 보유 회원 대상 … 지원 | long | Upbit holders get a new token or yield: Korean retail buys the base coin on Upbit |
| 4 | NETUP | 하드포크, 업그레이드, 메인넷, 업데이트, 월렛, 지갑, 노드, 체인전환, 합병, 머지 (with 중단 / 지연 / 제한 / 지원 / 안내) | none | scheduled technical event, already public on the chain's own channels |
| 5 | RESUME | 재개 | none | |
| 6 | DWSUSP | (입출금 / 입금 / 출금)…(일시)?(중단 / 지연 / 제한 / 순단), with no planned reason in the title | short | an unscheduled deposit / withdrawal halt signals chain trouble (halt, exploit, congestion) and blocks arbitrage into Upbit |
| 7 | TRDSUSP | 거래 (일시) 중단 / 정지 / 제한, 시장가 주문, 주문 제한, 가격 제한 | none | |
| 8 | EVENT | 이벤트 (not listing promotions) | long | promotion of an already-listed coin |
| 9 | SUPPLY | 유통량 (circulation-plan change) | none | revision can go either way |
| 10 | OTHER | any other title naming a coin (fees, min deposits, AMAs, snapshots…) | none | |

- **DWSUSP body re-labelling (declared, uses bodies only):** for every DWSUSP notice naming a coin with a perp, the
  body is fetched (api-manager.upbit.com, >= 1.6 s, logged). If the body states a planned reason (업그레이드, 하드포크,
  메인넷, 업데이트, 정기 / 지갑 / 노드 점검, 월렛, 마이그레이션, 스왑, 전환, 합병, 에어드랍, 스냅샷) the row moves to
  NETUP (planned, no side). DWSUSP then holds suspensions whose title and body give no planned reason (network
  instability / issue / unstated).
- **Coins:** tickers in parentheses in the title, plus bare upper-case tokens that are a Binance perp base (stop list:
  KRW, BTC, USDT, ERC, NFT, …). Titles without a ticker (e.g. "Tron 네트워크 계열 디지털 자산 …") give no event.
  BTC itself is excluded (it is the hedge leg). Aliases: BEAM -> BEAMX; 1000x perps.
- **Perp age (A5 pitfall fixed):** the perp's first trade must be <= N - 7 d at minute precision (N0's k1m first bar with
  trades, 961 of 1,025 perp rows); without a k1m file, the first active perp_1d day + 1 d (i.e. the end of the first day).
  The perp must still trade >= 1 d after N.
- **Dedup:** first notice per (category, perp) within 7 d (the same coin's follow-up notices in a week are not new
  news). Multi-coin notices keep every coin; t is clustered by notice day.

## Counts before the body re-labelling (title rules only; coin-events with a perp >= 7 d old, after dedup)
| category | 2020 | 2021 | 2022 | 2023 | 2024 | IS | VAL | IS / VAL days | side |
|---|---|---|---|---|---|---|---|---|---|
| WARN | 0 | 0 | 13 | 12 | 6 | 0 | 31 | 0 / 26 | short |
| SWAP | 0 | 3 | 2 | 1 | 6 | 3 | 9 | 3 / 9 | none |
| AIRDROP | 1 | 9 | 3 | 5 | 2 | 10 | 10 | 9 / 10 | long |
| NETUP | 18 | 42 | 37 | 55 | 97 | 60 | 189 | 55 / 151 | none |
| RESUME | 5 | 4 | 4 | 5 | 3 | 9 | 12 | 8 / 12 | none |
| DWSUSP | 49 | 102 | 97 | 72 | 19 | 151 | 188 | 130 / 146 | short |
| TRDSUSP | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | none |
| EVENT | 0 | 0 | 0 | 1 | 2 | 0 | 3 | 0 / 3 | long |
| SUPPLY | 0 | 0 | 0 | 4 | 14 | 0 | 18 | 0 / 17 | none |
| OTHER | 4 | 10 | 5 | 1 | 9 | 14 | 15 | 11 / 12 | none |

Notices per category 2020..2024 (all, with or without coin): LISTING 198, ROUTINE 624, WARN 120, SWAP 71, AIRDROP 47,
NETUP 377, RESUME 81, DWSUSP 619, TRDSUSP 1, EVENT 12, SUPPLY 36, OTHER 516.

**Testable (side + >= 20 IS + >= 20 VAL):** only DWSUSP can qualify (final counts after the body re-labelling are
appended below before any price). WARN (IS 0) and AIRDROP (10 / 10) have a side but too few events: path and
side-adjusted descriptive numbers only. No-side categories: path and |move| only; they can never become a rule.

## The frozen trade (A2's analyze.py logic, copied unchanged except as stated)
- side x (alt USDT-M perp minus BTCUSDT perp), equal notional; short side = short alt / long BTC.
- Entry: first aggTrade with time >= N + 5 s on each leg. Exit: first aggTrade >= N + 5 min, or >= N + 60 min
  (2 cells per category). An exit trade more than 60 s after the target time voids the trade (thin books).
- Costs: 20 bp (4 taker fills x 5 bp) + A2's slippage (half the median 1 s range over bins with trades in the 60 s from
  each of the 4 fills) + real funding at stamps in (entry, exit] (local funding files; else public fapi fundingRate,
  endTime clipped to < 2025-01-01).
- Exit choice: the better IS t of the two exits, then checked on VAL unchanged. Robustness: costs x1.5; one step late
  (entry at N + 10 s). Years: IS 2020, 2021; VAL 2022, 2023, 2024. t clustered by notice day (A2's clt).
- Path: r(t) = ln(alt / BTC) since N - 60 s at t - N in {-60, -30, -10, -5, -2, -1, 0, +1, +2, +3, +5, +10, +20, +30,
  +60, +120, +300, +600, +1800} s; quartiles, mean, median |r| per category and era; and the N + 5 s -> N + 30 min
  move (signed and |.|).

## Random benchmark and max-over-categories null
- Same coin, same UTC day as N, entry at a random second with trades, same hold, the whole hold outside
  [N - 15 min, N + 75 min] of any event of that coin that day; side-adjusted gross from the 1 s series; 1,000 draw
  sets of one draw per event. Percentile of the event gross mean.
- Max-over-categories: each draw set is scored as net t (draw gross minus that event's 20 bp + slippage, clustered by
  day) on every testable (category, exit) cell; the 95th percentile of the per-set maximum is the bar a selected cell's
  t must clear as well. With only DWSUSP testable this is a 2-cell max.

## Data pull (declared before pulling; research/data/upbit_census/)
- data.binance.vision `futures/um/daily/aggTrades` (robots.txt 404, logged), >= 0.3 s, plain UA, no key, no e-mail.
  Each zip streamed to tmp/, parsed with `python -I`, deleted. Kept per (symbol, day): trades in [N - 10 min,
  N + 30 min] and [N + 3595 s, N + 3665 s] (the +60 min exit needs trades there; the brief's window plus this 70 s
  exit window) and a 1 s last-price / count series of the day (random benchmark). Both days when the window
  crosses 00:00 UTC.
- Priority order and subsample (declared): (1) all testable-category events in random order (seed 68), so a budget
  stop leaves a random subsample; (2) WARN (all), AIRDROP (all); (3) NETUP random 25 IS + 25 VAL (seed 68); (4) RESUME,
  SWAP, SUPPLY, OTHER, EVENT (all, small). Budget 45 min of pull time; whatever (2)-(4) the budget does not reach is
  reported as not pulled. HEAD probes put BTCUSDT days at 5-50 MB and most alts at 0.3-30 MB.

## Bars and power arithmetic (before any return)
- Bars unchanged (BRIEF): LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 years positive, random >= 95 %, power >= 3, positive at
  costs x1.5 and one step late; DEMO t >= 2.0 IS, VAL net > 0, random >= 90 %. A cell must also beat the
  max-over-categories null.
- HOLD n = the category's VAL pace (events / 3 years) x 1.83 years. Power = VAL SR per trade x sqrt(n_HOLD).
  At the title-rule count (188 VAL DWSUSP), n_HOLD ~ 115 -> LIVE needs VAL SR >= 0.28; the 2024 pace (19) would give
  n_HOLD ~ 35 and SR >= 0.51. The final count after re-labelling is used (appended below).
- IS t >= 2.5 with ~130 notice days needs a per-trade SR of ~0.22 (t ~ SR x sqrt(days)); DEMO's 2.0 needs ~0.18.
- Prior: these are large-cap coins (ETH, SOL, XRP, ADA, DOT, …) and the news (a chain halt) is usually public on the
  chain's own channels before Upbit posts. An open move after N + 5 s large enough to pay 20 bp + slippage is unlikely;
  the expected answer is "none", and the path is the main deliverable.

## Addendum 1 (Sun Nov  1 15:28:07 UTC 2026), before any price is read
- The Upbit body endpoint returns 429 after ~10 requests a minute even at 1.6-3.6 s spacing; the fetcher backs off
  (30 s sleep, gap x1.5 per 429). The body pull will take ~30 min.
- So the aggTrade pull started first (15:27:57 UTC) on a label-independent set: step 1 = **every title-rule DWSUSP row**
  (339 coin-events, a superset of the final DWSUSP; rows that the body rule moves to NETUP are pulled anyway), shuffled
  with seed 68; then steps 2-4 as declared (pull_list_v1.csv, 523 rows; 2 rows dropped for N + 61 min >= 2025). The
  pull script prints only row counts. Labels are fixed (final census + pull_list.csv) before analyze.py is run; rows
  that the re-labelling newly exposes after the 7-d dedup are appended at the end of the pull list.

## Addendum 2 (Sun Nov  1 16:13:16 UTC 2026): final labels and counts, still before any price is read
- **The addendum-1 body rule failed on boilerplate.** Every Upbit suspension body starts "업데이트 일자 : …" and ends
  "본 공지를 통하여 … 업데이트 하겠습니다", and most say "월렛 시스템 점검", so the word list moved 344 of 351
  DWSUSP notices to NETUP. Found by reading bodies only (no price).
- **Replacement rule (code/reason.py):** the reason is read from the *original* suspension sentence only: the last
  Korean sentence before the English part that announces a 중단 / 지연 / 제한 (updates sit above it). Then:
  - PLANNED (업그레이드, 하드포크, 메인넷, 마이그레이션, 스왑, 에어드랍, 스냅샷, 전환, 합병, 소프트포크, 분할)
    -> NETUP (no side);
  - CHAIN (네트워크 불안정 / 장애 / 이슈 / 혼잡 / 지연, 블록 생성 중단, 노드 문제, 보안, 해킹, 오류 …) or
    "네트워크 점검" (the chain side is checked) -> **DWSUSP (short, as declared)**;
  - Upbit's own "월렛 시스템 점검" or no readable reason -> new category **DWWALLET (no side)**: Upbit-internal
    maintenance carries no news about the coin.
  - On the 351 bodies: WALLET 224, UNKNOWN 57 (mostly "네트워크 점검"), CHAIN 37, PLANNED 33.
- **Final kept counts** (perp >= 7 d at minute precision, 7-d dedup):

| category | 2020 | 2021 | 2022 | 2023 | 2024 | IS | VAL | IS / VAL days | side |
|---|---|---|---|---|---|---|---|---|---|
| WARN | 0 | 0 | 13 | 12 | 6 | 0 | 31 | 0 / 26 | short |
| SWAP | 0 | 3 | 2 | 1 | 6 | 3 | 9 | 3 / 9 | none |
| AIRDROP | 1 | 9 | 3 | 5 | 2 | 10 | 10 | 9 / 10 | long |
| NETUP | 21 | 52 | 50 | 69 | 97 | 73 | 216 | 63 / 166 | none |
| RESUME | 5 | 4 | 4 | 5 | 3 | 9 | 12 | 8 / 12 | none |
| **DWSUSP** | 10 | 18 | 23 | 17 | 16 | **28** | **56** | 27 / 46 | **short** |
| DWWALLET | 36 | 76 | 66 | 45 | 3 | 112 | 114 | 98 / 98 | none |
| TRDSUSP | 0 | 0 | 0 | 0 | 0 | 0 | 0 | | none |
| EVENT | 0 | 0 | 0 | 1 | 2 | 0 | 3 | 0 / 3 | long |
| SUPPLY | 0 | 0 | 0 | 4 | 14 | 0 | 18 | 0 / 17 | none |
| OTHER | 4 | 10 | 5 | 1 | 9 | 14 | 15 | 11 / 12 | none |

- **Testable: DWSUSP only** (short alt / long BTC; 2 cells D5-5m, D5-60m). The max-over-categories null is therefore a
  2-cell max. WARN, AIRDROP, EVENT: side-adjusted descriptive numbers only. Others: path and |move| only.
- Data in hand: all DWSUSP, DWWALLET, WARN, AIRDROP, RESUME, SWAP, SUPPLY, OTHER, EVENT events and the NETUP random
  25 IS + 25 VAL sample (+ any NETUP rows from title-DWSUSP: all pulled). Total pull 37 min, 958 daily files, 0 misses.
- **Power (final):** DWSUSP VAL pace 56 / 3 yr -> n_HOLD ≈ 34. LIVE needs VAL SR per trade >= 3 / sqrt(34) = 0.51.
  IS t >= 2.5 on 27 notice days needs SR ≈ 0.48; DEMO's 2.0 needs ≈ 0.38. Only a large, consistent post-5 s drift can
  pass; the expected answer stays "none".
