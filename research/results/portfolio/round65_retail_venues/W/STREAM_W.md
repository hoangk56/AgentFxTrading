# Stream W (round 65): Upbit warning / delisting notices -> Binance USDT-M perp. No LIVE or DEMO rule

Written Sun Nov 1 11:18:59 UTC 2026 (from `date -u`). Hypotheses declared at 11:11:57 UTC in
[HYPOTHESES_W.md](HYPOTHESES_W.md), after the notice history and event list were built and before any price was
requested. HOLD (2025-01-01..) was never requested, loaded or counted: every series is cut at ts < 2025-01-01, and
only data.binance.vision files dated <= 2024-12 were downloaded.

## Answer first
**None, for all 7 cells. The reason is structural: IS 2020-21 has zero tradable events.** The data exist, and the
mechanism shows on Binance spot. But no Upbit-warned or Upbit-delisted coin had a live Binance perp in 2020-21.

- **The notice history is reachable.** Upbit's own notice JSON at api-manager.upbit.com has no robots rules. It holds
  5,953 notices back to 2017-10, with the original post time. Detail is below.
- **IS is empty in every cell.** Upbit's 2020-21 actions hit small Korean coins and privacy coins: 310 coin-notice
  rows, none with a perp at the time. So the IS bars (t >= 2.5 LIVE, >= 2.0 DEMO) cannot be met.
- **VAL 2022-24 is small and only descriptive.**
  - W72 (warning designation, hold 72 h): +546 bp net, t 1.85, n 4, beats 100 % / 98 % of random entries.
  - U24 (caution urge, hold 24 h): +154 bp, t 1.11, n 15.
  - The delisting-notice cells are about zero or negative.
- **Power at VAL size stays below 1.5.** Best cell W72: SR 0.92 x sqrt(~2.4 HOLD events) ≈ 1.4. LIVE needs 3.
- **No PREREG_DRAFT.**

## Data and reachability (research/data/upbit_notices/requests.log, 998 lines)
**robots.txt, read first and logged:**

| host | robots.txt | used? |
|---|---|---|
| upbit.com | `User-agent: * / Disallow: /` | no |
| sg.upbit.com | `User-agent: * / Disallow: /` | no |
| api-manager.upbit.com | 200, one comment line, no rules | yes |
| api.upbit.com | 404 | not needed |
| data.binance.vision | 404 | yes |
| fapi.binance.com | robots read in round 64 K (blocks named search engines only) | yes, via k2rule |

**Source.** `/api/v1/announcements?os=web&page=P&per_page=20&category=all` is the JSON that the upbit.com notice page
calls itself.
- 298 pages, 5,953 notices, 2017-10-27 onward.
- `first_listed_at` is the original post time (KST); titles carry later edit suffixes.
- `/api/v1/announcements/<id>` returns the body: target markets, reason, and the trading end time. 116 bodies were
  fetched.

**Completeness check.** 94 ids are missing from the 2020-21 list. I fetched 6 of them, and all 6 are 뉴스 (press)
items, not deleted notices.

**Point-in-time check.** 4 WebSearches against news; the times are consistent:
- LTC: warning 2022-05-23, delisting notice 2022-06-08, end 06-20;
- OMG / SRM: warning 2023-03-29;
- KAVA: warning 2022-11.

**Request counts and limits.**
- No account, no key, no e-mail; plain `research-script` User-Agent.
- 904 × 200, 84 × 404 (spot months for coins not on Binance), 1 × 400 (`per_page=100` is rejected), 1 URL error
  (retried). No 403.
- Throttling: 8 × 429 after ~107 list pages at 0.3 s. The script backed off, and I resumed at 1.5 s per request.

**Binance data.**
- fapi 1m fills and funding through `code/k2rule.py`, a copy with only its log folder changed (405 fapi requests).
- Local perp 1h closes for the random draws, cached to research/data/upbit_notices/perp1h_close.npz.
- data.binance.vision spot SYM/BTC monthly 1h files: 72 files, used only for the mechanism check M.

## Events (code/events.py; declared filters in HYPOTHESES_W.md)
Event classes:
- **W:** 유의 종목 지정 (warning designation). Deposits stop at the post time.
- **D:** 거래지원 종료 (end of trading support).
- **U:** 유의 촉구 (caution urge).

Filters:
- W and D must hit the KRW market. This drops the BTC-market-only notices for LINA, LUNA, FOR and others.
- Swap- or migration-driven notices are dropped: NU->T, ENJ mainnet, LSK network change.
- The perp must trade from 7 d before the notice to 1 d after.
- First notice per class and coin within 30 d.

Counts:

| | IS 2020-21 | VAL 2022-24 |
|---|---|---|
| coin-notice rows (all coins) | 310 | 67 |
| W with perp | 0 | 4: LTC 05-23, KAVA 11-02, WAVES 12-08 (2022), OMG 2023-03-29 |
| D with perp | 0 | 3: LTC 2022-06-08, OMG 2023-04-12, ENJ (KRW only) 2023-09-26 |
| U with perp | 0 | 15: TRX, WAVES x3, CRV x2, KAVA, MKR, LINA, KNC, XRP, OGN, OCEAN, STX, STMX |

Near misses in IS:
- BTS: warned 2021-01-28, but its perp started 4 days later.
- ZEN: warned 2020-04, but its perp started 2020-11.
- LUNA 2022-05: its warning and its delisting covered only the BTC market, and the perp settled 05-12.

**Overlap with Binance's own perp delistings (round 64 T):** none within 30 d. WAVES was delisted by Binance in
2024-06; the Upbit WAVES notices are from 2022. Upbit and Binance delistings are independent event sets.

## Results, VAL 2022-24 only (net bp per trade; costs 42 bp + real funding; t clustered by entry day)
Entry: the 1m close at the post minute + 60 min. Columns:
- **+5 min:** entry 5 minutes later.
- **N + 2 h:** entry 2 hours after the post.
- **rand A:** percentile against other perps shorted vs BTC at the same hour.
- **rand B:** percentile against the same coin at random hours 30-180 d before the notice.
- Both random columns are on gross returns from 1h closes, 500 draws.

Full output: run_output.txt, cells.json, trades.csv.

| cell | n | price | funding | **net** | **t** | median | SR / trade | x1.5 costs | +5 min | N + 2 h | rand A % | rand B % | years (n, net) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W24 | 4 | +337 | -83 | +212 | 0.86 | +106 | 0.43 | +191 | +190 | +158 | 99 | 95 | 2022 (3) -14, 2023 (1) +888 |
| **W72** | 4 | +724 | -136 | **+546** | **1.85** | +568 | 0.92 | +525 | +491 | +498 | 100 | 98 | 2022 (3) +325, 2023 (1) +1209 |
| D24 | 3 | -81 | -45 | -169 | -1.48 | -278 | -0.86 | -190 | -143 | -148 | 44 | 31 | 2022 +59, 2023 (2) -282 |
| D72 | 3 | +93 | -56 | -5 | -0.03 | -118 | -0.02 | -26 | +11 | +54 | 78 | 67 | 2022 +350, 2023 (2) -183 |
| D to Upbit end (~12-14 d) | 3 | +211 | -162 | +7 | 0.01 | +138 | 0.00 | -14 | -42 | -12 | 60 | 47 | LTC -1921, OMG +1805, ENJ +138 |
| U24 | 15 | +204 | -8 | +154 | 1.11 | +11 | 0.28 | +133 | +146 | +225 | 100 | 98 | 2022 (6) -15, 2023 (4) +197, 2024 (5) +323 |
| U72 | 15 | +119 | -29 | +48 | 0.25 | +102 | 0.06 | +27 | +26 | +96 | 99 | 71 | 2022 (6) -294, 2023 (4) +70, 2024 (5) +442 |

IS: n = 0 in every cell.

**Trades in the W72 cell:** LTC +799, KAVA -160, WAVES +336, OMG +1209 bp.

**U24 has a fat tail.** Its mean is driven by STMX (+1647) and CRV 2023-07 (+1047). The median is +11 bp.

**Max-over-cells.** 7 cells with n 3-15 each. The best VAL t is 1.85 (W72, n 4). That is well inside what 7
correlated tiny cells give by chance, so nothing is chosen. Parameters could not be chosen on IS.

## Mechanism check M (descriptive; Binance spot SYM/BTC, 1h closes; mcheck_output.txt)
This uses the same notices on Binance spot, which reaches 2020-21. Spot is not tradable short without a borrow, so
M grades no rule. Gross short-alt-vs-BTC return from N + 1 h. t is clustered by notice day: the events sit on only
3-5 days per cell, so these t values are fragile.

| class / hold | era | n (days) | gross mean | t (days) | median | win | beats random same coin % | run-up N - 24 h -> entry (median) |
|---|---|---|---|---|---|---|---|---|
| W 24 h | IS | 21 (5) | +507 | 1.91 | +567 | 76 % | 100 | -1.0 % |
| W 72 h | IS | 21 (5) | +240 | 0.42 | +676 | 67 % | 78 | |
| W 24 h | VAL | 5 (5) | +276 | 1.35 | +216 | 80 % | 93 | -3.5 % |
| W 72 h | VAL | 5 (5) | +620 | 2.64 | +584 | 80 % | 98 | |
| D 24 h | IS | 12 (4) | +136 | 0.88 | +77 | 50 % | 67 | -3.4 % |
| D 72 h | IS | 12 (4) | +703 | 6.58 | +627 | 100 % | 96 | |
| D 24 h / 72 h | VAL | 3 | -21 / +197 | | | | 30 / 47 | -5.2 % |

**Reading.**
- After an Upbit warning, the coin falls on Binance as well. In IS the mean is about -5 % vs BTC in 24 h, and the
  median is about -6 % at 72 h.
- After a delisting notice, the 72 h fall is +703 bp for the short in IS: all 12 events were wins, but they sit on
  4 notice days.
- The pre-notice run-up is small or negative. This is not a pump fade (K2's +21.5 % has no mirror here). It is a
  dated sell flow.
- The mechanism is real. The perp market simply did not list these coins when Upbit acted on them.
- Caveats:
  - 2021-01-28 BTS (-4521 bp) shows the squeeze risk.
  - Some BTC-pair tickers could be name collisions with other coins (e.g. GO). No price-level guard was possible,
    because delisted Upbit markets have no candles.

## Power (arithmetic in HYPOTHESES_W.md)
**HOLD event counts.** VAL paces are W 1.33 / yr, D 1.0 / yr and U 5 / yr. Over 1.83 years that gives HOLD n of
about 2.4 (W), 1.8 (D) and 9.2 (U).

**Power at VAL size:**

| cell | power | calculation |
|---|---|---|
| W72 | ≈ 1.4 | SR 0.92 x sqrt(2.4) |
| W24 | ≈ 0.7 | SR 0.43 x sqrt(2.4) |
| U24 | ≈ 0.85 | SR 0.28 x sqrt(9.2) |
| D cells | ≤ 0 | |

**Pooling.** Pooling all classes (~7 events a year) would still need a per-trade SR >= 0.83. Since 2022 Korean
warnings are joint DAXA actions (Upbit, Bithumb, Coinone, Korbit, Gopax). So Bithumb or other Korean venues add no
independent events.

**Correlation with C3:** not computed, since no cell has DEMO numbers.

## Pitfalls met
- **robots.txt.** upbit.com disallows everything for generic agents. Only api-manager.upbit.com (no rules) was used;
  the notice pages themselves were never requested.
- **API limits.** `per_page` is capped at 20 (100 gives a 400). Rapid paging (~100 requests at 0.3 s) triggers 429;
  1.5 s per request worked.
- **Edited titles.** Titles gain edit suffixes after the fact ("(완료)", "(기간 연장)", "- X 유의 종목 해제").
  - Classification by title can therefore use outcome text.
  - To avoid that, coins lifted in the same notice are excluded only through the body's per-coin blocks, and
    extension or lift notices are excluded as their own notices.
- **Mostly BTC-market notices.** Many Upbit notices touch only BTC-market pairs (2020-02 18종, LUNA 2022-05, LINA
  2023). A KRW filter matters for the "Korean retail" mechanism.
- **Clustered notices.** Notices come in clusters on a few days (8, 17, 25 coins at once), so independent days, not
  coins, set the effective sample.
- **The trading window opens late.** Upbit-only coins become perp-tradable mostly after their Upbit troubles are
  over. The perp universe and the Upbit warning universe overlap only from 2022.

## What a user decision could unlock
- **A spot-borrow route.** For coins on Binance cross margin, or another venue's lending, a short-spot version
  could test IS on the 2020-21 events (check M: W24 +507 bp gross, 21 events, 5 days). Round 64 already found the
  inventory route costly, and borrow for a coin under a Korean warning may be unavailable. Low priority.
- **A forward paper log.** Poll `api-manager.upbit.com/api/v1/announcements` for 유의 종목 지정 on coins with a
  Binance perp; short perp / long BTC at N + 1 h for 72 h. Expected 1-2 events a year, so it can never reach LIVE
  power. It is a monitoring add-on to the K2 paper bot at most.

## Files
- Code (W/code/):
  - fetch.py: polite fetcher and log;
  - pull_list.py, pull_detail.py: notices;
  - events.py: event classes and filters;
  - perps.py: perp availability, incl. round 64 T relisted perps;
  - k2rule.py: K2 pricing, log folder changed;
  - run.py: cells and random draws;
  - pull_spot.py, mcheck.py: check M.
- Outputs (W/):
  - HYPOTHESES_W.md;
  - events_all.csv (377 rows), events_kept.csv (22);
  - run_output.txt, cells.json, trades.csv;
  - mcheck_output.txt.
- Data (research/data/upbit_notices/, 70 MB, git-ignored):
  - raw/list_all/ (298 pages), raw/detail/ (122 bodies), raw/cand_titles.json, raw robots files;
  - spot1h/ (72 zips);
  - perp1h_close.npz;
  - requests.log.
