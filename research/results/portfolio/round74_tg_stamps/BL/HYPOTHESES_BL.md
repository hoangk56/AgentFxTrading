# Stream BL (round 74) hypotheses: Binance listing announcements timed by the official Telegram channel

Written Mon Nov 2 14:24:33 UTC 2026 (from `date -u`), before any price, any event count and any parsed title of the
channel. Section 6 (counts, power) is appended later from titles only, still before any price.

## 1. Mechanism
- **L1 (Binance spot listing, "Binance Will List X").** A Binance spot listing opens the coin to the largest retail
  spot venue: new demand (retail buyers, index / bot coverage), better liquidity and attention. Before the spot market
  opens, traders who want exposure buy the coin where it already trades (other venues' perps). This is the Binance
  analogue of A2-D5L (Upbit KRW listing -> long the Binance perp from N + 5 s). Side: **long**, fixed by the mechanism.
- **L2 (Binance USDⓈ-M perp launch, "Binance Futures Will Launch USDⓈ-M X Perpetual") for coins already on Binance
  spot.** The perp brings leveraged long demand and attention, and at launch the perp usually trades at a premium, so
  basis arbitrageurs buy spot and short the perp. Both push Binance spot up between the post and the perp's first
  hours. The opposite story (the perp enables shorting) acts over days to weeks, not inside the hold windows here.
  Side: **long Binance spot**, fixed by the mechanism; the short side is not tested.
- **L3 (margin / Convert / Earn).** Not run: it is not cheap (many title formats, weak demand story, no single
  tradable minute). Declared here so it is not added later.

## 2. Data
- Event times: Telegram post time N (whole seconds, UTC) of `@binance_announcements` from the coordinator's raw pages
  (research/data/telegram_hist/raw/binance_announcements/), parsed with `coord/parse.py` under `python -I`. Event lists
  are cut at N < 2025-01-01 right after parsing; 2025-26 posts are only counted (title regex), never priced.
- **Edited posts:** primary sample drops every post with `edited` True; a check reruns the chosen cell with them.
- L1 venue for the coin before the Binance spot open (first that applies, the venue's first trade >= 24 h before N
  and >= 1 trade in [N - 10 min, N]):
  1. Binance USDT-M perp (data.binance.vision futures/um daily aggTrades), 5 bp taker a side.
  2. Bybit USDT linear perp (public.bybit.com/trading daily dumps), 5.5 bp taker a side (published base tier 0.055 %).
  3. OKX USDT swap (static.okx.com/cdn/okex/traderecords daily trade dumps; robots.txt 404, a HEAD of a 2023 file was
     200 on 2026-11-02 14:24 UTC), 5 bp taker a side (base tier 0.05 %).
  Spot open O = first Binance spot trade of the coin (data.binance.vision spot aggTrades of the first listed pair).
- L2: Binance spot aggTrades (data.binance.vision spot daily aggTrades) of the coin's main pair (USDT, else BUSD, else
  BTC) on N's day (and the next day if a window crosses midnight). Perp first trade P from futures/um aggTrades (or
  round 66 N0's local launch-day files in research/data/perp_launch/agg/). Spot must have traded >= 7 d before N.
- Every price request ends <= 2024-12-31 23:59:59 UTC. Zips are streamed to tmp, cut to windows, deleted.

## 3. Title regexes (case-insensitive; applied to the first line of the post text; may be widened only after
reading titles, before any price, and every change is logged in section 6)
- L1 include: `^\s*Binance (Will List|Lists|Lists New|Adds|Will Add)\b` and at least one ticker `\(([A-Z0-9]{2,15})\)`.
- L1 exclude: `Futures|Perpetual|Margin|Launchpool|Launchpad|Convert|Earn|Savings|Staking|Pre-?Market|Alpha|
  Options|Pool|Trading Pairs|Opens Trading|Delist|Copy Trading|Loan|Simple Earn|NFT`.
- L2 include: `Binance Futures Will Launch .*(USD[ⓈS]-?M|USDT[- ]Margined|USDT-M).*Perpetual` (one or several coins:
  every coin named is an event; coin parsing from the title words before "Perpetual").
- L2 exclude: `Coin-Margined|COIN-M|Quarterly|Delivery|Pre-Market|Options|Leveraged Token`.
- Multi-coin titles: each coin is one event; t is clustered by post day, so a multi-coin post counts once for t.
- Corrections / reposts: if the same coin and type appear twice within 7 days, keep the first post.

## 4. Rules and the small grid (side fixed long)
- Entry: the first trade at or after N + 5 s; fill = the **worst (highest) trade price in the 1 s after that first
  trade** (A2's worst-of-1 s fill). Exit: the first trade at or after the exit time; fill = the worst (lowest) price
  in its 1 s.
- L1 exits: X5 = N + 5 min, X60 = N + 60 min, XO = spot open O (only if N + 5 min < O <= N + 48 h; else the event is
  dropped from XO). 3 cells on the perp venue, unhedged.
- L2 exits: X5, X60, XP = perp first trade P (only if N + 5 min < P <= N + 48 h). 3 cells, Binance spot, unhedged.
- Cell choice: per rule, the cell with the best IS t; checked on VAL unchanged.
- Costs: fees (above) both sides + the worst-of-1 s fill + real funding on perp legs crossing a funding stamp when the
  local funding file exists (Binance: research/data/binance/funding; Bybit / OKX: 0 with a note). Costs x1.5 = fees x1.5
  plus the fill gap (worst-of-second minus first trade) x1.5. One step late = entry at N + 10 s.
- Readings, not graded: BTC-hedged versions; d = 2 s / 30 s.

## 5. Eras, bars, null
- IS 2018-01-01..2021-12-31 (declared: Binance perps start 2019-09, so 2018-19 add only what exists), VAL
  2022-01-01..2024-12-31, HOLD 2025-01-01..2026-10-29 never opened by this stream.
- Bars as the brief (LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years positive, random >= 95 %, power >= 3; DEMO: IS t
  >= 2.0, VAL net > 0, random >= 90 %), net > 0 at costs x1.5 and one step late, t clustered by post day.
- Random benchmark: 1,000 sets of same-coin, same-UTC-day entries (uniform second, outside [N - 1 h, N + 2 h], same
  hold length, same fill rule); percentile of the event gross mean.
- Max-over-cells null: for each random set, the max t over the 3 cells of a rule; report its 95th percentile.
- Burst timing (like A2): median path of ln(P / P(N - 60 s)) at N + 0, 1, 2, 3, 5, 10, 30, 60, 300, 3600 s; onset =
  first second the price is >= +2 % (L1) / +1 % (L2) above P(N - 60 s); share of the +60 s and +5 min move done
  before N + 5 s; pre-N drift N - 60 min -> N (would show the Telegram post lags the website).
- Gates before grading: n_IS >= 20 events for a rule, else the rule is reported "not testable" (as round 63 D).

## 6. Counts and power (appended Mon Nov 2 14:59:28 UTC 2026 from titles, file listings and HEADs only, before any price)
Channel: 8,941 posts parsed (ids 1..9,107), 6,779 before 2025, 2,154 in 2025-01..2026-10 (titles counted only).

Regex changes after reading titles, before any price (code/classify.py):
- L1 exclude also `Fiat|Gateway|Peer-to-peer|P2P|Purchases|Payment|Card|Buy Crypto` (fiat-gateway notices such as
  "Binance Adds Czech Koruny (CZK) ... Fiat Gateways" matched the include regex).
- L1 drops pegged assets (stablecoins, fiat tokens, staking wrappers: FDUSD, AEUR, EURI, UST, BNSOL, ...): no
  listing-demand mechanism.
- L2 include also the 2019-20 format `Binance Futures (Will Launch|Launches) XXX/USDT Perpetual`.
- Not included by design (declared regexes): Launchpool / Pre-Market / HODLer "Introducing X" posts, "Binance Adds X
  on Earn, Convert, Margin & Futures" (post-listing product notices), "Listing Postponed / Advanced" notices.

| coins (posts) per year | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | HOLD 25-26 (count only) |
|---|---|---|---|---|---|---|---|---|---|
| L1 spot listings | 15 | 53 | 19 | 65 | 81 | 21 | 16 | 26 | 32 coins (26 posts) |
| L1 with a declared venue (perp >= 24 h before N) | 0 | 0 | 0 | 0 | 4 | 3 | 5 | 11 | unknown (not checked) |
| L2 USDⓈ-M perp launches | - | - | 2 | 38 | 33 | 1 | 0 | 0 | **0** |

- L1 venues: Binance perp 6 (all 2023-24), Bybit perp 14, OKX swap 3 (Bybit / OKX dumps start 2020 / 2021-09). IS
  2018-21 = **4** events (AGLD, BICO, PEOPLE, SPELL), VAL 2022-24 = **19**. An OKX **spot** venue (not declared; HEAD
  count only) would add 4 IS (ILV, YGG, ALCX, CVX) and 8 VAL: IS 8, still below the gate.
- L2: the channel stopped carrying "Binance Futures Will Launch" posts after 2021-08 (one 2022 index perp, none in
  2023-26). IS 73, VAL 1, HOLD 0.

Power arithmetic:
- L1: the declared gate n_IS >= 20 fails (4). IS t >= 2.0 at a per-trade SR of 0.5 would need ~16 day-clusters; 4
  cannot reach any bar. HOLD trades ~10-32 (32 titles x the VAL venue share 30 % .. all of them), so LIVE power 3 needs
  SR 0.53-0.95 per trade. **L1 is not gradeable.**
- L2: VAL n = 1 and HOLD n = 0, so VAL t and HOLD power are 0 by construction. **L2 is not gradeable.**

Readings declared now (not graded, no cell chosen on them):
- L1 VAL (19 events): all three cells, with **XO frozen now as the headline cell** because it is the A2-D5L analogue
  (exit at the listing venue's open); X5 / X60 shown as info. Burst timing on the same events.
- L2 IS (73 events, coins on Binance spot >= 7 d before N): the three cells and the burst timing on Binance spot, as an
  IS-only reading of whether the Telegram stamp leads the spot move.

## How L1 differs from round 63 D
Round 63 D needed a >= 7 d Binance USDT-M perp and had no announcement time, so it timed the event by the first spot
kline (the open, not the news), which left 0 IS events. L1 times the trade by the Telegram post N (the news), accepts a
venue with >= 24 h of history on Binance perps, Bybit or OKX, and exits at or before the spot open. It also differs
from round 66 O2 (OKX / Bybit's own notices) and N0 (fading the new perp itself): L2 trades Binance **spot** from the
perp-launch post.
