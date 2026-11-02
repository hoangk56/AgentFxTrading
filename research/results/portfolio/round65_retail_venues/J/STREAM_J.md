# Stream J (round 65): the next wave of hypotheses (scouting only, nothing backtested)

Written 2026-11-01 11:25 UTC (`date -u` at 11:24:45). The plan is in [HYPOTHESES_J.md](HYPOTHESES_J.md), written at 11:16
UTC before any request or count. No return was computed and no price series was loaded. HOLD (2025-01-01..) was
never requested. Every count below uses records dated < 2025-01-01, and HOLD event rates are extrapolated from 2024.
Requests: 16 in total, logged in research/data/scout_j/requests.log, with bodies under research/data/scout_j/<host>/. WebSearch: 4 of 15.

## Answer first
- **No hypothesis here is likely to reach LIVE.** The best is ~1 %. Taken together, the 11 give maybe 4-6 % of at
  least one LIVE candidate. They are not independent: three are Hong Kong close / retail ideas, and four are crypto
  venue events.
- **The K2 mechanism (Korean retail listing chase) cannot be grown much before 2025.** I counted Upbit's own notice
  history (titles only, < 2025) against Binance perps that were >= 7 days old:
  - KRW-market additions: **43** coin-events in 2020-24. Only **9** are missing from K's survivor list, so
    survivor bias in K2 is small.
  - BTC / USDT-market additions: **32** (17 of them in 2024).
  - Holder airdrop-support notices: **16**.
  - Binance's own spot listings of coins that were perp-first: **6** (2023-24). Pre-2025 power cannot come from more
    Korean or Binance listing events.
- **Gotobi analogues in other currencies fail on the instrument, not on the mechanism.** The cases checked: Korean
  month-end exporter nego (USDKRW), the Russian tax-period RUB conversion, TWD / INR / THB fixes, and Chile's AFP
  switches. None has a tradable instrument with free intraday history, or the events are too few. Japan's own
  LETF doses into the Tokyo close were already tested in round 34 (X1: IS +6.7 bp t 1.8, VAL +0.3). I list them under
  "dropped" rather than repeat them.
- **The most testable new ideas are in Hong Kong** (J1 CBBC call clusters, J4 HK leveraged / inverse ETF doses). HK
  retail is the world's largest CBBC market, and the issuers' hedge unwinds are rule-driven at public call levels.
  HKEX's robots.txt allows the CBBC pages. The Mac's DNS maps hkex.com.hk to 127.0.0.1, so I probed it from the agentFx
  VPS. A free *history* of outstanding CBBCs by call level is not confirmed. The local HK50 m1 / m15 caches cover the
  price side.
- **The rest of this section is advice for K2 itself, not a new hypothesis.** Funding cost K2 -512 bp per trade in
  HOLD (gross +775). A frozen-rule variant that changes only the short leg is a cheaper lever than any new event
  source. Two candidates:
  - close a few seconds before each 00 / 08 / 16 UTC stamp and reopen after it: ~9 extra round trips, ~90 bp, against
    ~512 bp of funding;
  - short the venue with the lowest funding (Bybit funding is local for 252 symbols).

  Round 62's finding (the paying side gains in the seconds after a stamp) has to be priced in. Separately, Upbit's
  2024 notices show new listing rules: a buy-wait period and a minimum sell price for new listings (for example the
  VANA 2024-12-16 notice). This is a structural change at the edge of HOLD that the K2 demo should record.

## Ranked table
Power = net Sharpe per trade at a plausible VAL size x sqrt(HOLD events, ~1.8 years). LIVE needs >= 3. P columns
include the chance that the data or the venue fails.

| # | hypothesis | instrument | free data, status (2026-11-01) | events / yr (pre-2025) | HOLD power at plausible size | P(LIVE) | P(DEMO) |
|---|---|---|---|---|---|---|---|
| J1 | HK CBBC mandatory-call clusters: issuer hedge unwind after a dense call band breaks | HK50 CFD (IC) / HSI futures | hkex.com.hk robots 200, CBBC paths allowed (via agentFx); call-level history: launch notices on hkexnews (not yet probed); street-position history **not confirmed**; HK50 m1 local | ~100-200 band breaks (est.) | 1.3-2.6 (Sharpe 0.08-0.16, n ~270) | 1.0 % | 4 % |
| J2 | Upbit non-KRW market additions (BTC / USDT) plus K2's list rebuilt from notices (adds coins later delisted) | Binance USDT-M perp short, BTC perp long | api-manager.upbit.com robots 200 (no rules), list page 200 (2021-12 page); counts done from W's cache | non-KRW 32 in 2020-24 (2024: 17), +9 KRW not in K2 | ~1 (Sharpe 0.15, n ~40) | 1.0 % | 6 % |
| J3 | Binance funding-interval switch (8 h -> 4 h when funding hits the cap): the crowded side's carry multiplies | Binance USDT-M perp | local funding files (no request needed) | 55 switches in 2022-24 in the local subset (full universe larger) | 1.4-2.1 (Sharpe 0.15, n 90-200) | 0.7 % | 3 % |
| J4 | HK leveraged / inverse ETF close rebalancing (CSOP HSTECH 2x, HSI -2x: dose 2x / 6x the day's return) | HK50 into the 16:00-16:10 closing auction | issuer NAV / units history **not probed**; sign rule works without it; HK50 m1 local | ~50-70 big-move days | ~1 (Sharpe 0.1, n ~110) | 0.6 % | 3 % |
| J5 | Turkish retail flight into USDT: BtcTurk USDT/TRY premium over USDTRY leads the managed official rate | USDTRY (IC / Dukascopy) | graph-api.btcturk.com robots 404 (none), USDTTRY 1h 200 (2024-12-01); Dukascopy USDTRY tick hour 200 (2024-01-02) | ~30-60 signal days, few episodes | ~0.9 | 0.5 % | 2.5 % |
| J6 | Southbound Stock Connect eligibility additions after Hang Seng index reviews (mainland retail access) | HK single stocks (IB; user decision) | HKEX / HSI notices (robots allow); **no free HK stock prices** on the allowed list | 100-200 stock-events on ~4 dates | < 1 at date level | 0.5 % | 3 % |
| J7 | Binance spot listing of a perp-first coin (Binance's retail base gets spot access), K2 rule frozen | Binance perp short, BTC long | local spot_first.csv + perp_1d | **2 (2023) + 4 (2024)**; IS empty | new-era rule only; 2.2 if K2-size and ~80 HOLD events | 0.4 % | 2 % |
| J8 | MakerDAO OSM: liquidations fire one hour after the delayed oracle price, known in advance | ETH perp short | on-chain vault state needs an archive RPC (**user decision**, as in round 52) | ~10-30 liquidation hours | ~1.8 if Sharpe 0.3, n ~36 | 0.3 % | 1.5 % |
| J9 | Coinbase roadmap additions (the US retail pump happens at the roadmap post, not the first candle) | Binance perp short, BTC long | coinbase.com robots 200; roadmap history lives on X / blog: **no free point-in-time list** | ~30-60 (2021-24, est.) | ~1.4 if Sharpe 0.15 | 0.2 % | 1 % |
| J10 | S&P 500 additions / deletions (index-fund demand at the effective close) | Dukascopy US stock CFDs | en.wikipedia.org robots 200; revision API 200 (revision as of 2024-12-26, point-in-time) | ~20-30, many names outside Dukascopy's 263 | ~0.7 | 0.2 % | 1.5 % |
| J11 | Upbit holder airdrop-support notices (crypto record date): buy before the snapshot, short after | Binance perp | Upbit notices (as J2) | **16 in 2020-24** | < 0.5 | 0.1 % | 1 % |

## Hypotheses

### J1. HK CBBC mandatory-call clusters -> HK50
- **Forced flow.** Issuers sell bull CBBCs to HK retail and hedge long in HSI futures. A mandatory call event (MCE) is
  triggered by a rule: the index trades at or through the call price. The issuer then unwinds the hedge (sells
  futures) within minutes. Bear CBBCs work the other way. The call levels and issue sizes are public at launch.
- **Timing.** The first print through a band of call levels that is dense in hedge notional (from launch notices,
  net of earlier MCEs).
- **Side.** Declare continuation in the break direction from the next minute for 15-30 minutes. As a second, declared
  cell, fade after 30 minutes.
- **Instrument.** HK50 CFD at IC (HK50 spread ~3-5 bp is the cost to beat) or HSI futures.
- **Data.**
  - hkex.com.hk robots.txt returned 200 via agentFx and disallows only Listing-Rules contingency paths.
  - historicalData.aspx answers 302.
  - The MCE page is "today" only.
  - A free, point-in-time history of call levels is plausible from the issuers' launch announcements on hkexnews.hk.
    That host is not yet probed, and it means thousands of PDFs.
  - Street holdings by call level have no free history found. Without them, use issue size as the weight.
  - Prices: research/data/m1/HK50.npz and HK50/m15 (from 2015-03).
- **Why new.** Rounds 28, 29 and 37 tested round-number and extreme-level stops on HK50 (no continuation), and round
  34 tested ETF doses. Neither used a *measured* rule-triggered hedge size. Lei 2015 (J. Futures Markets 35(6)) finds
  abnormal returns and volume around MCEs on single stocks. Cheung, Chou & Lei 2015 find VPIN spikes around call
  events.
- **Risk.** Call bands sit at round numbers, so J1 may reduce to round 28. The first test should be whether the band
  weight adds anything over round-number distance.

### J2. Upbit BTC / USDT-market additions, and K2 rebuilt from Upbit notices
- **Forced flow.** Korean retail chases newly accessible coins on Upbit (K2). A BTC / USDT-market addition gives a
  weaker funnel, because KRW holders need two hops.
- **Timing.** The notice time (first_listed_at) and the trading start stated in the notice body, then entry at
  start + 1 h (K2's rule, unchanged).
- **Side.** Short the Binance perp and long the BTC perp, 72 h, at K2's costs.
- **Data.**
  - api-manager.upbit.com robots.txt returned 200 with no rules. My one list request (page 200) returned the
    2021-12 notices.
  - Counts come from stream W's cached titles (code/upbit_events.py, output upbit_events.txt):
    - KRW: 43 coin-events in 2020-24 (2021 8, 2022 2, 2023 10, 2024 23). Of these, 9 are not in K's survivor list:
      MATIC, AUDIO, GAL x2, ALT, OMNI, STG, USDC, BONK. USDC and the duplicate GAL must be dropped.
    - BTC / USDT: 32 (2020 1, 2021 5, 2022 5, 2023 4, 2024 17).
- **Why new.** K used `/v1/market/all` KRW markets only, so it missed delisted coins and non-KRW markets.
- **Expected.** The non-KRW pump should be smaller (stream I and H: no pump outside Upbit KRW). This mostly adds
  ~8 events a year to K2's pool. Report it as a separate cell, not pooled with K2.

### J3. Binance funding-interval switch
- **Forced flow.** By Binance's rule, when a perp's funding sits at the cap / floor, the settlement interval is cut
  (8 h -> 4 h, sometimes 1-2 h). The crowded side's carry doubles or more from that moment, and leveraged holders
  close.
- **Timing.** The first stamp on the new interval. It is visible in the funding history with no announcement needed
  (point-in-time: the switch is known at the first shortened stamp).
- **Side.** Declare fading the crowded side, i.e. the receiving side's direction (with positive capped funding, longs
  pay, so short), from stamp + 1 minute for 4-24 h, with funding charged.
- **Data.** Local: binance/funding (385 symbols) shows 37 switches (2022 4, 2023 26, 2024 7). funding_window
  (first 75 days of 497 others) shows 18 more. The full universe needs fapi fundingRate for the rest (public).
- **Why new.** Round 62 traded the minutes around extreme stamps (dead after the first seconds). This uses a rule
  *state change*, and holds through several stamps.
- **Risk.** The event counts are small before 2025. The mechanism is close to the carry family (round 58).

### J4. HK leveraged / inverse ETF close rebalancing -> HK50
- **Forced flow.** A daily-reset ETF must trade AUM x (L^2 - L) x the day's return at the close. That is 2x for a 2x
  fund and 6x for a -2x fund, in the same direction as the move. CSOP's HSTECH 2x / -2x and HSI -2x products are among
  Asia's largest, and largely held by mainland retail via Connect (from 2021-22).
- **Timing.** The HKEX closing auction (16:00-16:10).
- **Side.** With the day's move from 15:30 to the close (to the CAS reference).
- **Data.** HK50 m1 local. Daily units / AUM from the issuer: not probed (one request on csopasset.com is the next
  step). A sign-only rule needs no AUM.
- **Why new.** Round 34 did US ProShares doses and Japan's 1570 / 1357 (X1: no VAL edge), never HK products. Japan's
  X1 failure is the prior, so P is low.

### J5. BtcTurk USDT/TRY premium -> USDTRY
- **Forced flow.** Turkish savers who are limited at banks buy USDT on BtcTurk / Binance TR. When state banks hold the
  official rate (2021-23), the crypto rate leads, and the official rate follows when the policy gives way.
- **Timing.** Daily at 09:00 Istanbul.
- **Side.** Long USDTRY when the premium is > k % (declare k in {1, 2}).
- **Data.**
  - BtcTurk USDTTRY 1h candles returned 200 for 2024-12-01 (keyless; robots 404 = no file). The history start must
    be checked (stream I saw 1d from 2017).
  - Dukascopy USDTRY tick hours returned 200 (2024-01-02, 10 kB).
- **Why new.** The kimchi / Coinbase premiums (rounds 33 and 64) were tested on crypto targets, never a premium on a
  local stablecoin -> the fiat rate.
- **Costs.** Costs kill it unless the move is large: USDTRY spread at IC ~20-60 bp, and the long carry pays the TRY
  rate (~0.1 %/day). Episodes are few (2018-08, 2020-11, 2021-12, 2023-06), so power is set by episodes, not days.

### J6. Southbound Connect eligibility additions
- **Forced flow.** A stock added to Southbound Connect after a Hang Seng index review becomes buyable by mainland
  retail.
- **Timing.** The announcement (review date, after the close) and the effective date are known in advance.
- **Side.** Long from the announcement to the effective date.
- **Data and status.** HKEX / HSI notices are public. **HK stock prices are not on the allowed free list**
  (stooq is banned), and the venue is IB: a user decision. Events cluster on ~4 dates a year, so power at the date
  level is < 1.
- **Why new.** Rounds 37 and 40 used Connect flows at index level only.

### J7. Binance spot listing of a perp-first coin
- **Forced flow.** Binance's retail spot users get access (the K2 mechanism on the largest retail venue).
- **Timing.** The first spot kline.
- **Side and rule.** K2's rule, frozen.
- **Data.** Local spot_first.csv and perp_1d: only **6 events before 2025** (BLUR, BONK 2023; PYTH, TON, TURBO, WIF
  2024, median lag 109-210 days). Most pre-2025 coins got spot and perp within 7 days (2020 15 ... 2024 47).
- **Why new.** Round 63 D failed for want of announcement times; the first kline needs none.
- **Verdict.** A new-era rule only: no IS / VAL test is possible. Park it as forward-log only, if anything.

### J8. MakerDAO OSM delayed liquidations
- **Forced flow.** Maker's Oracle Security Module publishes the next price one hour ahead. Vaults whose liquidation
  price lies between the current and next OSM price will be liquidated at the next poke, and the collateral is
  auctioned and sold.
- **Timing.** Known an hour in advance, on-chain.
- **Side.** Short the ETH perp for the hour before the poke when queued liquidations exceed X.
- **Data.** Needs an archive RPC for vault state (user decision). There is no keyless free source.
- **Why new.** No round touched DeFi protocol rules. Event counts are low (drawdown hours only), and the effect is
  ETH-only.

### J9. Coinbase roadmap additions
- **Forced flow.** US retail chases the roadmap post. Stream L found no pump at the first candle because the pump
  happens 48-72 h earlier.
- **Timing.** The roadmap post time.
- **Side.** Short the Binance perp from the post + 1 h, K2's rule.
- **Data.** coinbase.com robots returned 200. The roadmap history is on X and Coinbase's blog, with no free
  point-in-time list.
- **Prior.** Coin Metrics found "markets under consideration" announcements did not move prices. The TIE (2026,
  contaminated by 2025-26 data) says the roadmap is the catalyst.

### J10. S&P 500 additions / deletions
- **Forced flow.** Index funds must buy or sell at the effective-date close (S&P rule, announced ~5 days ahead).
- **Side.** Long additions from announcement + 1 day to the close before the effective date. Short deletions only if
  covered.
- **Data.** The Wikipedia revision API returned the point-in-time revision (2024-12-26). Announcement times need S&P
  press releases (not probed). Dukascopy covers only 263 large names, so most deletions are missing.
- **Prior.** Greenwood & Sammon (2022) show the index effect has disappeared.

### J11. Upbit holder airdrop-support notices
- **Forced flow.** Korean holders on Upbit must hold at the snapshot to get the airdrop (a record date, like round 63
  I9's perks).
- **Side.** Long into the snapshot, short after.
- **Data and status.** Upbit notices: **16 events in 2020-24** with a Binance perp. There is no power. Kept only so
  the coordinator does not re-scout it.

## Dropped (no slot)
- **Japan 1570 / 1357 LETF close doses -> JP225.** Already round 34 X1 (VAL +0.3 bp).
- **Leveraged tokens (Binance BLVT, FTX BULL / BEAR) daily rebalance -> perps.** data.binance.vision has the BLVT
  klines (HEAD 200, BTCUPUSDT 2021-05), but there is no AUM history. FTX ended in 2022-11, and Binance BLVT AUM was small after 2022.
  Whether the BLVTs still existed in HOLD was not checked.
- **Russian tax-period RUB conversion; Kazakh tenge.** No tradable instrument since 2022.
- **Korean month-end exporter nego (USDKRW), Taiwan life-insurer TWD hedging, INR / THB fixes.** No free intraday
  data or tradable instrument.
- **Chile "Felices y Forrados" AFP switch calls (Da, Larrain, Sialm & Tessada 2018).** < 10 a year, damped by the 2019
  rule.
- **BoJ ETF purchases after a weak morning.** The rule ended in 2021 (purchases stopped in 2024): no HOLD events.
- **GBTC 6-month private-placement unlocks.** 2020-21 only.
- **MicroStrategy 8-K purchase reports.** Backward-looking, and mostly HOLD-era.
- **Upbit deposit / withdrawal suspensions** (~150-250 notices a year). The local premium closes on Upbit (K1), so
  there is no global flow.
- **TSE 6-month margin expiry (信用期日).** Weekly JPX data, no JP stock prices.
- **Robinhood crypto listings.** ~3 a year.

## Requests (research/data/scout_j/requests.log)
| host | robots.txt | probe | result |
|---|---|---|---|
| api-manager.upbit.com | 200 (no rules) | announcements page 200 (Dec 2021) | usable |
| www.hkex.com.hk | 200 via agentFx (Mac DNS -> 127.0.0.1; local attempts logged as URLError) | historicalData.aspx 302 | CBBC pages allowed; history unconfirmed |
| nextfunds.jp | 200 (`Disallow: /mt/`) | none (page carries 2026 NAV) | not needed (J4 dropped for Japan) |
| graph-api.btcturk.com | 404 (none) | USDTTRY 1h 200 (2024-12-01) | usable |
| datafeed.dukascopy.com | 404 (none) | USDTRY 2024-01-02 10h 200 | usable |
| www.coinbase.com | 200 | none | no roadmap history source |
| en.wikipedia.org | 200 | revision API 200 | usable, point-in-time |
| data.binance.vision | 404 (none) | HEAD BLVT monthly 200 | klines exist, no AUM |

Code:
- [code/probe.py](code/probe.py) (requests);
- [code/counts_local.py](code/counts_local.py) (J3 / J7 counts, output [counts_local.txt](counts_local.txt));
- [code/counts_upbit_notices.py](code/counts_upbit_notices.py) and [code/upbit_events.py](code/upbit_events.py)
  (outputs [counts_upbit_notices.txt](counts_upbit_notices.txt) and [upbit_events.txt](upbit_events.txt)).

WebSearch (4): HKEX CBBC history, NEXT FUNDS 1570 AUM history, Coinbase roadmap studies, the USDT/TRY premium. No
e-mail, key or account was used anywhere. HOLD contamination: only The TIE's 2026 note (J9) uses 2025-26 data.

## Suggested order for the coordinator
1. J1, if one hkexnews probe shows the launch notices are machine-readable. The first test is band weight vs
   round-number distance on HK50 m1.
2. The K2 funding-leg variant (not a hypothesis; see "Answer first"). It is the cheapest lever on the one rule that
   passed HOLD with a behavioural flow.
3. J2 as a separate cell (fapi only, ~40 events).
4. J3 (local data plus a fapi funding pull).
5. J4 / J5 only as quick checks. J6-J11 need user decisions or have no power.
