# Stream UC (round 68): census of Upbit notice categories at seconds. None

Written Sun Nov 1 16:14:25 UTC 2026 (from `date -u`). Categories, sides, the trade and the power arithmetic were
declared in [HYPOTHESES_UC.md](HYPOTHESES_UC.md) at 15:26:33 UTC. Two addenda followed, both before any price was read:
- 15:28: the price pull started on a set that does not depend on labels;
- 16:10: the body re-labelling rule was fixed (the first version matched boilerplate) and the final counts were added.

HOLD (2025-01-01..) was never requested, loaded or counted. The last daily file pulled is 2024-12-27, and every
funding request ends before 2025.

## Answer first
- **None.** Only one category qualifies for testing: DWSUSP, a deposit / withdrawal halt on Upbit whose original
  notice blames the coin's own chain. It needs a declared side and >= 20 IS and >= 20 VAL events, and has 28 IS and
  56 VAL.
- **The declared side (short) loses at both exits in both eras:**

| cell | era | net bp/trade | t | n (days) | random % |
|---|---|---|---|---|---|
| D5-5m | IS | -49 | -4.34 | 28 (27) | 0 |
| D5-5m | VAL | -49 | -6.29 | 56 (46) | 0 |
| D5-60m | IS | -18 | -0.61 | 25 (24) | 62 |
| D5-60m | VAL | -64 | -1.54 | 56 (46) | 0 |

  - Years: 0 of 5 positive in both cells.
  - Power at VAL size (n_HOLD ≈ 34): -4.8 for 5m, -1.3 for 60m.
  - Max-over-categories null (95th percentile of the max net t): 0.66 IS, -0.10 VAL. No cell beats it.
  - No PREREG_DRAFT.
- **What the census does show: within 1-3 s of any notice that names a coin, the coin rises vs BTC on Binance.**
  - This holds whatever the news: chain trouble, Upbit wallet maintenance, upgrades, swaps, airdrops, even
    warnings.
  - There is no move before the stamp. Paths are flat from N - 60 s to N, then rise.
  - Medians at N + 5 s (IS / VAL): DWSUSP +11 / +5 bp, DWWALLET +8 / +5, NETUP +21 / +7, AIRDROP +60 / +14,
    WARN (VAL) +5.
  - So the "bad news" categories move up, not down, in the first seconds. This fits bots that buy any coin named in
    an Upbit post, much like the listing reaction (A2).
  - The part still open after N + 5 s is small next to 20 bp + slippage. Post hoc, the long version of every pooled
    category is about zero in VAL: +1 bp at 5m (t 0.12), +11 bp at 60m (t 0.73). Details in the post-hoc table below.

## Data (research/data/upbit_census/, requests.log 1,384 lines)
- **robots.txt (logged):** api-manager.upbit.com 200 (one comment line, no rules); data.binance.vision 404.
- **Upbit bodies.** 351 bodies of the title-rule DWSUSP notices that name a perp coin, saved in raw/detail/.
  - Requests: 352 × 200 and 21 × 429.
  - The endpoint allows about 10 requests a minute, so the fetcher backed off. A fixed 6 s gap ran almost clean.
    W's note that "1.5 s worked" does not hold for the body endpoint now.
  - Titles, categories and stamps came from stream W's list cache (read-only).
- **Binance aggTrades.** data.binance.vision daily `futures/um/daily/aggTrades`.
  - 958 files for 533 events: 11.0 GB downloaded in 37 min (36 + 1 min), 0 misses, no 403 / 418 / 429.
  - Plus 11 HEAD size probes.
  - Zips were deleted after parsing. npz/ holds 292 MB: trades in [N - 10 min, N + 30 min] and
    [N + 3595 s, N + 3665 s] (the 60-min exit window), plus a 1 s series per day.
- **Funding.** Local files, plus 26 public fapi fundingRate requests (endTime clipped to < 2025).
- **Subsample (declared).** NETUP was sampled at a random 25 IS + 25 VAL, seed 68. The NETUP path table therefore has
  37 IS / 52 VAL events: the sample plus NETUP rows that came in through the title-DWSUSP superset. Every other
  category was pulled in full.

## Categories and counts (code/census.py, code/reason.py; coin-events, perp >= 7 d at minute precision, 7-d dedup)
| category | rule (title; DW* also body) | side | 2020 | 2021 | 2022 | 2023 | 2024 | IS | VAL |
|---|---|---|---|---|---|---|---|---|---|
| WARN | 유의 종목 지정 / 유의 촉구 / 거래지원 종료 | short | 0 | 0 | 13 | 12 | 6 | 0 | 31 |
| SWAP | swap / rebrand / symbol change / redenomination / migration | none | 0 | 3 | 2 | 1 | 6 | 3 | 9 |
| AIRDROP | airdrop / staking support for holders | long | 1 | 9 | 3 | 5 | 2 | 10 | 10 |
| NETUP | upgrade / hard fork / mainnet (title or original-sentence reason) | none | 21 | 52 | 50 | 69 | 97 | 73 | 216 |
| RESUME | 재개 | none | 5 | 4 | 4 | 5 | 3 | 9 | 12 |
| **DWSUSP** | D/W halt; reason = chain trouble or "네트워크 점검" | **short** | 10 | 18 | 23 | 17 | 16 | **28** | **56** |
| DWWALLET | D/W halt; reason = Upbit's own 월렛 시스템 점검 / none | none | 36 | 76 | 66 | 45 | 3 | 112 | 114 |
| TRDSUSP | trading halt / order limits | none | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| EVENT | non-listing promotions | long | 0 | 0 | 0 | 1 | 2 | 0 | 3 |
| SUPPLY | 유통량 plan change | none | 0 | 0 | 0 | 4 | 14 | 0 | 18 |
| OTHER | any other coin-named title (fees, AMAs, snapshots…) | none | 4 | 10 | 5 | 1 | 9 | 14 | 15 |

Notices excluded before categorising:
- LISTING: 198 notices, A2's set plus every market-opening title or event.
- ROUTINE: 624 notices (payouts, results, terms, audits).
- Titles with no coin: server maintenance, KRW rails, policy.

## Path per category (median r = ln alt/BTC since N - 60 s, bp; raw sign; results.txt has the quartiles)
| category | era | n | 0 s | +1 s | +2 s | +5 s | +10 s | +60 s | +300 s | +30 min | median N+5s->30min | median abs. 30-min move |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DWSUSP | IS | 28 | -2 | 7 | 12 | 11 | 15 | 51 | 30 | 33 | +18 | 48 |
| DWSUSP | VAL | 56 | 1 | 1 | 2 | 5 | 6 | 13 | 23 | 14 | +11 | 31 |
| DWWALLET | IS | 112 | 2 | 4 | 4 | 8 | 11 | 27 | 18 | 36 | +20 | 54 |
| DWWALLET | VAL | 114 | -0 | 3 | 3 | 5 | 5 | 14 | 14 | 13 | +8 | 29 |
| NETUP (sample) | IS | 37 | 0 | 10 | 12 | 21 | 32 | 84 | 96 | 163 | +100 | 163 |
| NETUP (sample) | VAL | 52 | 0 | 5 | 6 | 7 | 9 | 16 | 16 | 24 | +12 | 48 |
| AIRDROP | IS | 10 | 1 | 26 | 32 | 60 | 86 | 303 | 378 | 594 | +479 | 594 |
| AIRDROP | VAL | 10 | 2 | 7 | 8 | 14 | 14 | 50 | 21 | 17 | +6 | 17 |
| WARN | VAL | 31 | 1 | 2 | 2 | 5 | 10 | 17 | 0 | -13 | -22 | 108 |
| RESUME | IS / VAL | 9 / 12 | 3 / 0 | 3 / 0 | 4 / 1 | 5 / 4 | 4 / 8 | 9 / 8 | 14 / 12 | 9 / 25 | +1 / +20 | 92 / 42 |
| SWAP | IS / VAL | 3 / 9 | -2 / 4 | 12 / 17 | 14 / 13 | 19 / 16 | 67 / 32 | 168 / 69 | 173 / 50 | 84 / 51 | +65 / +38 | 84 / 51 |
| SUPPLY | VAL | 18 | -2 | 2 | 4 | 8 | 17 | 11 | -11 | 9 | -6 | 33 |
| OTHER | IS / VAL | 14 / 15 | -2 / -9 | -1 / -5 | 0 / -1 | 3 / 4 | 4 / 6 | 8 / 3 | 5 / -17 | -6 / -12 | -19 / -14 | 44 / 44 |
| EVENT | VAL | 3 | -4 | -6 | -5 | -6 | -7 | 23 | -11 | -15 | -9 | 27 |

**Reading the path table:**
- **Nothing leads the stamp.** From -60 s to 0 s the medians stay within ±3 bp in every category with n >= 10.
- **The reaction starts within 1 s and is upward.** This holds in every category with n >= 10 except OTHER.
- **IS (2020-21) reactions are larger and keep drifting.** NETUP IS median +100 bp from N + 5 s to N + 30 min;
  AIRDROP IS +479 bp. In VAL (2022-24) the reactions shrink to about +5-15 bp, with little drift after N + 5 s.

## Declared-side results (net bp per trade; 20 bp + A2 slippage + real funding; t clustered by notice day; results.txt)
| cell | era | n (days) | gross | slip | fund | **net** | **t** | median | SR | x1.5 | late (N + 10 s) | years (net, n) | random % | power |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DWSUSP D5-5m | IS | 28 (27) | -25.1 | 4.2 | 0.5 | **-48.8** | **-4.34** | -47 | -0.85 | -60.8 | -39.8 | 2020 -48 (10), 2021 -49 (18) | 0.0 | |
| | VAL | 56 (46) | -25.9 | 2.8 | 0.0 | **-48.7** | **-6.29** | -41 | -0.83 | -60.1 | -42.1 | 2022 -56 (23), 2023 -41 (17), 2024 -46 (16) | 0.0 | -4.84 |
| DWSUSP D5-60m | IS | 25 (24) | 5.8 | 4.0 | 0.7 | **-17.5** | **-0.61** | -9 | -0.12 | -29.5 | -7.8 | 2020 -37 (7), 2021 -10 (18) | 62.3 | |
| | VAL | 56 (46) | -41.2 | 2.5 | -0.0 | **-63.7** | **-1.54** | -24 | -0.21 | -74.9 | -56.9 | 2022 -37 (23), 2023 -139 (17), 2024 -21 (16) | 0.0 | -1.25 |

Notes:
- **Exit choice.** By the declared rule (better IS t), the exit is 60m. Its IS t is -0.61, so both the LIVE bar
  (2.5) and the DEMO bar (2.0) fail.
- **D5-60m IS n.** It has 3 fewer events: those exits had no trade within 60 s of N + 60 min (thin books), so the
  trade is void.
- **Max-over-categories null.** It is a 2-cell max (only DWSUSP is testable). 95th percentile of the max net t:
  0.66 IS, -0.10 VAL.
- **Power at VAL size.** SR x sqrt(34), with n_HOLD = 56 / 3 x 1.83.

**Declared-side categories with too few events** (descriptive only; code inline, same trade):

| category | cell | IS net (t, n) | VAL net (t, n) | power at VAL size |
|---|---|---|---|---|
| AIRDROP (long) | D5-5m | +311 (3.38, 10) | +84 (0.87, 10) | 0.28 x sqrt(6.1) ≈ 0.7 |
| AIRDROP (long) | D5-60m | +458 (3.90, 10) | +147 (0.97, 10) | ≈ 0.8 |
| WARN (short) | D5-5m | n 0 | -68 (-1.08, 31) | < 0 |
| WARN (short) | D5-60m | n 0 | -106 (-0.94, 31) | < 0 |
| EVENT (long) | D5-5m / D5-60m | n 0 | -3 / -200 (n 3) | < 0 |

- **AIRDROP's IS is 9 events in 2021**, holder airdrops of APENFT, AQUA, SOLO, BOBA and others. VAL medians are
  negative (-11 / -29) and the HOLD pace is about 3 a year, so it can never reach power 3, and it is below the
  20-event floor.
- **WARN's seconds-scale short loses.** At 24-72 h, stream W found the opposite. At seconds the coin first goes up.

## Post-hoc (labelled; not a rule): the long side on every category (posthoc.txt)
The long side was chosen after seeing the paths. It is reported only so that the coordinator can judge whether an
"any coin-named Upbit notice" rule deserves its own brief. Net bp, D5 entry:

| group | 5m IS | 5m VAL | 60m IS | 60m VAL |
|---|---|---|---|---|
| POOL, all coin-named categories (excluding LISTING) | +19 (t 2.03, n 212) | +1 (0.12, 319) | +25 (1.63, 209) | +11 (0.73, 318) |
| DWSUSP flipped to long | +0 (0.04) | +3 (0.39) | -30 (-1.06) | +19 (0.46) |
| DWWALLET | -9 (-0.80) | -2 (-0.25) | +10 (0.47) | -11 (-0.86) |
| NETUP (sample) | +48 (2.07, 36) | -8 (-0.97, 52) | +51 (1.56) | +25 (1.22) |

- VAL is about zero everywhere, and VAL medians are -13 to -23 bp.
- The 2020-21 IS drift did not survive into 2022-24. The likely reason: faster bots now take the move inside the
  first 5 s.
- Even a fresh, properly declared "long any coin-named notice" rule would, on these numbers, fail VAL.

## What failed and why
- **The mechanism had the wrong sign at seconds.** A chain-trouble deposit halt was expected to be bad news. On
  Binance it is met within 1 s by buying, as is every other coin-named Upbit post. The prior news of the outage (on
  the chain's own channels) was apparently already priced, and what Upbit's post adds is attention, not information.
- **Costs dominate.** In VAL the post-5 s move is +5 to +15 bp at the median, against 20 bp fees plus 3-11 bp of
  slippage.
- **Category sizes are small.** Only DWSUSP passed the 20 / 20 floor. AIRDROP, the one category with a strong IS,
  has 10 / 10 events and about 3 a year.

## Pitfalls met
- **Body boilerplate.** Every suspension body contains "업데이트 일자" and "…업데이트 하겠습니다", and most contain
  "월렛 시스템 점검". A word search over the whole body put 98 % of halts in "planned" (addendum 2). The reason has to
  be read from the original suspension sentence: the last Korean 중단 sentence before the English part.
- **Upbit rate limit.** The body endpoint 429s at about 10 requests a minute, even at 1.6-3.6 s spacing. A
  multiplicative backoff made the pull very slow; a fixed 6 s gap ran nearly clean.
- **Perp age.** Minute precision was taken from N0's k1m first bars (A5's ARB pitfall). 961 of 1,025 perp rows had
  it; the rest use the end of the first perp_1d day.
- **Midnight windows.** KST 09:00 is 00:00 UTC, and many notices sit near it. Windows crossing midnight load both
  daily files.
- **Edited titles.** Outcome suffixes such as "(완료)", "(입출금 재개 안내)" and "(기간 연장)" are stripped before
  classification. The stamp is `first_listed_at`.

## What a user decision could unlock
- Nothing on the current bars. If the coordinator wants it, AIRDROP could be logged forward (paper, about 3 events
  a year): a monitoring note, not a rule.

## Files
- **Code (UC/code/):**
  - census.py: categories and counts;
  - reason.py: the body reason sentence;
  - net.py: fetcher and log;
  - robots.py, probe.py: robots.txt reads and HEAD size probes;
  - pull_bodies.py: Upbit bodies;
  - make_pull_list.py: the declared pull order;
  - pull.py: aggTrades;
  - analyze.py: path, cells, random benchmark and max null (A2 logic);
  - posthoc.py: the post-hoc long table.
- **UC/:**
  - HYPOTHESES_UC.md, STREAM_UC.md;
  - events_all.csv, events_kept.csv, events_kept_titleonly.csv;
  - pull_list.csv, pull_list_v1.csv, title_dwsusp_keys.txt;
  - results.txt, cells.json, trades.csv, posthoc.txt, nhold.json.
- **Data (research/data/upbit_census/):**
  - requests.log;
  - raw/detail/ (351 bodies), raw/robots_*.txt;
  - npz/ (958 files, 292 MB);
  - pull.out, pull_bodies.out, analyze.out.
