# Stream IB (round 71): trades protected by a barrier to entry (scouting, no backtest)

Written 2026-11-01 18:14 UTC (`date -u`), after [HYPOTHESES_IB.md](HYPOTHESES_IB.md) (18:05 UTC, before any request). No price
series was loaded for analysis and no return was computed. Every probe asked for a month <= 2024-12, and every
parser asserts ts < 2025-01-01. HOLD was never requested.

- Requests: 20, logged in research/data/scout_ib/requests.log, with bodies under research/data/scout_ib/raw/<host>/.
  The probes covered 8 hosts (robots first), with >= 1.2 s between requests per host, no e-mail and no contact header.
- WebSearch: 11 of 15.
- Code: code/fetch.py, parse_probes.py and count_listings.py (all run with `python -I`).

## Answer first
- **No idea here is likely to reach LIVE. The best is ~1.5 % (IB7).** The nine ideas together give maybe 4-6 % of at
  least one LIVE candidate. The common problem is the same as in rounds 63-70: the barrier-protected events are
  few (10-50 independent events a year), so HOLD power stays below 3 unless the per-event Sharpe is >= 0.35.
- **The best new construction is IB7, the withdrawal-closed window of new Binance spot listings.** Binance opens
  deposits before trading but withdrawals only ~24 h after trading starts, at the same clock time.
  - So during the first day, a Binance *premium* can be arbitraged in (buy elsewhere, deposit, sell on Binance). A
    Binance *discount* cannot be arbitraged out (buy on Binance, withdraw, sell elsewhere).
  - Launchpool / airdrop supply is credited on Binance and cannot leave either.
  - Declared side: long Binance spot when it trades below the coin's perp / another venue, hedge short on a perp, and
    exit at the withdrawal-open clock.
  - It needs **no borrow**: the long is spot, the short is a perp. That is the barrier B could not cross.
  - Its data is all free and point-in-time: data.binance.vision spot, local perp_1d, and the Bybit public spot trade
    archive (200).
  - Its weakness is IS: 2020-21 listings rarely had a perp within the window.
- **Two barriers turned out to exclude the user, not the bots.**
  - Binance Global TRY pairs: from 2025-11-13, non-Turkish users can no longer place TRY orders (IB3, TRY variant).
  - Coinbase availability in Vietnam is unconfirmed (IB4).
- **One planned data source does not exist.** status.coinbase.com has no listing posts (IB4 as first planned). It holds
  incidents / transfer delays only, ~120 per quarter in 2022-12..2023-02.
- **Data blocked or needing a user decision:** Binance Launchpool calendar (IB5; the only list found is a 37-row
  Kaggle set, account needed); Binance Margin delisting announcements (IB8; /bapi/ forbidden; only news reposts); the
  onshore CNY close (IB6; FRED timed out twice, chinamoney has no spot-close history found).

## Ranked table
Power = net Sharpe per independent event at a plausible size (half the naive mechanism, net of taker costs) x
sqrt(HOLD events over ~1.83 yr). LIVE needs >= 3. For daily books it is the annual Sharpe x sqrt(1.83). P includes
the chance that the data or the venue fail.

| # | mechanism | barrier (who it keeps out) | venue / account the user needs | free point-in-time data, status (2026-11-01) | events / yr pre-2025 | HOLD power, plausible | P(LIVE) | P(DEMO) | duplicate check |
|---|---|---|---|---|---|---|---|---|---|
| IB7 | New Binance spot listing: a discount vs perp / other venues cannot be arbitraged until withdrawals open (~trading start + 24 h). Long the spot discount, short the perp, exit at the withdrawal clock | settlement / transfer lock (withdrawals closed), Binance-only airdrop supply; bots cannot move coins out; no borrow needed | Binance spot + USDT-M perp (existing account); optional Bybit perp | data.binance.vision spot 1m / aggTrades (200), local spot_first.csv + perp_1d; Bybit public spot archive (TONUSDT monthly from 2022-12, 200); withdrawal time = first kline + 24 h (search: the usual rule, a few exceptions; exact times are in the Zenodo file, user OK) | listings 77 / 82 / 31 / 41 / 56 (2020-24); perp before or within 7 d: 15 / 8 / 6 / 21 / 50 | ~1.7-2.6 (Sharpe 0.2-0.3, ~40 events / yr; IS thin) | 1.5 % | 6 % | X (R64, unconditioned spot gap), A3 / J7 (perp-first spot listing), N0 (fade the new perp). New: conditioned on the transfer lock, long side only, exit on the lock's clock |
| IB1 | Staking / custody wrappers trade below redemption value when holders need liquidity. Long wrapper / short ETH (BTC) perp; exit on reversion or redeem | capital lock-up: unstake queue (days to weeks; none at all before 2023-04-12), custodian redemption (WBTC); small size | Binance spot WBETH/ETH (+ BETH before 2023-04), Binance ETH staking redemption; Coinbase cbETH | BETHETH 1d 2022-06 (200: close 0.944-0.975, ~4.1k ETH/day); WBETHETH 2024-06 (200); WBTCBTC 2024-08 (200: 0.9976-1.0010); Coinbase CBETH-ETH 2023 daily (200, 274 candles). Fair value needs the wrapper's exchange rate (on-chain, needs an RPC; a smooth-trend proxy otherwise) | 2-6 discount episodes; daily book | ~1-1.5 (needs annual Sharpe >= 2.2) | 0.7 % | 4 % | none in `tried:` (S = stablecoins, Q1 = COIN-M vs USDT-M). Literature: Nethermind (LST discount arbitrage lasts the withdrawal duration), arXiv 2402.17748 |
| IB8 | Binance Margin pair delisting: positions are force-closed at a pre-announced UTC time (borrow suspended ~2 days before). Retail margin is net long, so this is forced selling: short the perp into the close time, exit just after | operational rule with a public clock; only margin users are forced | Binance USDT-M perp | announcement times only on binance.com (/bapi/ forbidden) and news reposts (not allowed hosts); the official CMS announcement feed (developers.binance.com) is forward-only and may need a key | ~10-20 batches / yr, several coins each | ~1.6 (Sharpe 0.3 per batch, ~27 HOLD clusters) | 0.5 % | 3 % | D (R63, Binance notices; not tested, robots), L7 (spot delist, Zenodo) |
| IB3 | Local-fiat books on Binance (ALT/BRL; ALT/TRY): local retail can fund only by local rails, so an ALT/fiat premium over ALT/USDT x USDT/fiat is a local retail flow. It can be sold on the same venue (unlike K1, where the premium closed on Upbit) | fiat rail / KYC of the local currency, tiny capacity | Binance spot. **TRY: closed to non-Turkish users from 2025-11-13**; BRL: unverified | SOLTRY 1d 2023-06 (200: 39.7 M TRY / day, 7.7k trades / day); SOLBRL 1d 2023-06 (200: 0.45 M BRL / day, 805 trades / day, thin) | hundreds of premium spikes, clustered on TRY / BRL shock days (~20-40 clusters) | ~1-1.5; costs 3 legs x 10 bp | 0.5 % | 2 % | K1 (kimchi per coin), J5 (BtcTurk USDT premium). New: same venue, so it can be closed without a transfer |
| IB2 | USD stablecoins (USDC, earlier BUSD / USDP / TUSD) redeem at par only over bank wires for KYC'd institutions. Fedwire closes at weekends and US holidays (SEN / Signet 24/7 rails ended 2023-03), so weekend USDC discounts vs USDT close on Monday | fiat-rail closure, institutional KYC | Binance spot USDCUSDT (zero fee from 2023-06-30 per search; BUSD pairs zero fee from 2022-07); tick 0.0001 = 1 bp | USDCUSDT 1m monthly (HEAD 200, 1.4 MB / month, from 2018-12) | ~60 weekends + holidays | ~1-2 at 0-1 bp spread; IS has 7.5-10 bp fees, so it cannot pass IS on taker fills | 0.3 % | 2 % | S (R64, stablecoin depeg buys: only SVB week). New: time-of-week cycle at bp scale, not depeg thresholds |
| IB5 | Binance Launchpool / Launchpad: retail locks BNB for 7-30 days to farm. BNB is bid into the window and offered after it ends (long BNB / short BTC before, short after: two declared legs) | capital lock-up, Binance-only retail | Binance USDT-M BNBUSDT | **blocked**: no free calendar (Kaggle "Launchpool history" 37 rows, account; Binance /bapi/ forbidden; Zenodo file categories unverified, user OK) | 10-25 | < 1.5 (BNB beta, few events) | 0.3 % | 2 % | U / I4 (unlocks), N1 (short new perps), J11 (Upbit airdrops) |
| IB4 | Coinbase per-network transfer incidents ("Delayed transactions (SOL)", "sends unavailable"; minute stamps): during them Coinbase's coin price cannot be arbitraged, and the Coinbase-Binance gap closes at resolution | transfer barrier at one venue | **Coinbase account (Vietnam availability unconfirmed)**; the gap closes on Coinbase, so Binance alone does not capture it | status.coinbase.com robots: `Disallow: /api/`, `/embed/` only; history.json?page=16 (200: 120 incidents in 2022-12..2023-02, ~40 per-coin transfer delays) | ~150 incidents | ~1 (UC found the Upbit analog dead) | 0.3 % | 1.5 % | UC (R68, Upbit suspensions), K1. Planned listing-stamp version is dead: no listing posts on the status page |
| IB9 | Pre-launch perps (Hyperliquid hyperps, Bybit / Binance pre-market) converge to the spot listing price; no spot hedge, internal-EMA mark, funding cap | no spot to hedge (borrow-like) | Hyperliquid (non-custodial, no KYC) | api.hyperliquid.xyz robots 404; candleSnapshot HYPE 1d 2024 (200, 27 candles from 2024-12-05); no pre-2025 hyperp confirmed (search: PUMP, MON hyperps are 2025) | ~0 pre-2025 | n/a: **forward-only** | 0.2 % | 1.5 % | N0 / N1 (new perps), L6 (24/7 perps, forward-only) |
| IB6 | Capital controls separate CNY (onshore) and CNH. A stretched CNH-CNY spread converges over 1-5 days; trade USDCNH toward CNY | jurisdiction (onshore market closed to foreigners) | IC USDCNH (existing) | **not reached**: FRED robots timed out twice (host dropped); chinamoney.com.cn robots 404, but no onshore spot-close history found (central parity is not the spot, R67) | ~20-40 stretched days | ~1 (CNH spread at IC 1.15 bp RT) | 0.2 % | 1 % | H-CNH (CFETS close, R30), P (PBOC fix, R67), HIBOR (R35-36) |

## Sections

### IB7. Withdrawal-closed window of new Binance spot listings (best)
- **Mechanism.** Binance opens deposits hours before trading and withdrawals usually 24 h after trading starts, at
  the same clock time (search: TON 2024-08-08 10:00 UTC trading, 2024-08-09 10:00 withdrawals; the rule is the
  same in 2026 notices; OSMO, ARB are exceptions). During that day the only arbitrage route is into Binance, which
  caps a Binance premium. A Binance discount, caused by airdrop / Launchpool supply credited on Binance or by sellers
  who deposited early, cannot be arbitraged out. Holders cannot leave, and outside buyers cannot take coins away.
- **Why bots avoid it.** The arbitrage they would run is physically blocked. Market makers can hedge on the perp, but
  the leg that closes the gap (withdraw) is shut. The user crosses the barrier simply by waiting for the clock: long
  Binance spot, short the perp, exit at the withdrawal time.
- **Rule to declare (when tested).** At listing + {15, 60} min, if ln(Binance spot / reference) <= -k (k in {50, 100}
  bp), go long spot (first aggTrade after the signal) and short the reference perp, exit at listing + 24 h + {0, 30}
  min. Reference: the Binance perp if it is live, else the Bybit perp. Grid 8 cells; random = same coin, random
  minute in the window.
- **Data.** data.binance.vision spot aggTrades (daily files for the event days), local spot_first.csv / perp_1d,
  Bybit public archive (spot and trading) for the reference.
  - The withdrawal-open time is approximated as first kline + 24 h. The Zenodo file (L1) has exact announcement
    times but needs the user's OK. A sensitivity check should drop the listings where the rule is known to differ.
  - Count from local metadata (no prices): 2020 77 / 2021 82 / 2022 31 / 2023 41 / 2024 56 spot USDT listings (ex
    stables / leveraged tokens). A Binance perp existed before, or within 7 days of, the spot open for 15 / 8 / 6 / 21 /
    50 of them. Day resolution, so "within 7 d" is an upper bound on a same-window hedge.
- **Power.** ~40 usable events a year from 2023 (~73 in HOLD). Per-event Sharpe 0.2-0.3 gives 1.7-2.6. IS (2020-21)
  has few hedgeable events unless the Bybit perp covers them. The standard IS bar (t >= 2.5) is the likely failure, as
  with A3 / A4.
- **Pitfalls.**
  - N0 found that big early moves of new perps continue, so the perp leg's own drift matters; report the long-spot and
    the hedge legs separately.
  - The first minutes of a listing have huge spreads: enter at aggTrades, never 1m opens.
  - Bybit v5 kline answered "Not supported symbols" for TONUSDT spot. Use the public archive, which has TONUSDT
    monthly trade files from 2022-12.

### IB1. Wrapper discount vs redemption (BETH / WBETH / cbETH / WBTC)
- **Mechanism.** A wrapper is worth its redemption value, but redeeming locks capital: BETH could not be redeemed at
  all until Shapella (2023-04-12). After that, Binance quotes a demand-dependent delay with a per-user daily quota
  ("15 days to several weeks" at launch). Ethereum's exit queue reached 9+ days in 2025 (search, HOLD-era: not used
  for the rule).
- **Why bots avoid it.** Capital lock and a per-user daily quota make it small, multi-day and non-atomic, which is
  the "limits to arbitrage" case (Nethermind: the trade "will last as long as the withdrawal duration").
- **Probes.**
  - BETH/ETH 2022-06: 0.944-0.975, ~4.1k ETH/day.
  - WBETH/ETH 2024-06: 1.040-1.042 (the exchange rate accrues).
  - cbETH/ETH 2023: 0.977-1.049 (accrual + discount).
  - WBTC/BTC 2024-08 (custody change): 0.9976-1.0010.
- **Rule sketch.** Long the wrapper / short the ETH perp when the discount to fair value is >= max(30 bp, queue days x
  cash rate x 2). Exit when the discount is < 10 bp or redeem.
- **Data gap.** Fair value needs the wrapper's exchange rate (contract `exchangeRate()`, archive RPC = user decision);
  a smooth-trend proxy is weaker.
- **Power.** Few episodes (2022-06 Celsius / 3AC, 2022-11 FTX, 2023-04 Shapella), so HOLD power is ~1-1.5.
  DEMO-grade at best.

### IB8. Binance Margin delisting forced close
- **Mechanism.** Binance suspends isolated borrowing about two days before, then auto-closes all cross / isolated
  positions at the stated time and blocks changes for ~3 h (search, 2025-26 notices). This is a mandated flow with a
  public clock. Its side comes from the composition of retail margin (net long, so forced selling), which is an
  assumption to declare.
- **Data.** The announcement times are the barrier for us: binance.com /bapi/ is forbidden, and news reposts are
  not allowed hosts. The official CMS announcement stream is documented for developers and could log events forward
  with the user's key.
- **Power.** ~1.6 at best. Forward-only unless the user OKs a dated list.

### IB3. Local-fiat books on Binance (BRL; TRY now gated)
- **Mechanism.** It is K1's local premium, but on a venue where the user can also sell it: sell ALT/BRL, buy ALT/USDT,
  sell USDT/BRL (three legs, ~30 bp at taker), or keep a small inventory.
- **Problems.**
  - TRY, the deep book (SOLTRY ~39.7 M TRY / day in 2023-06), is closed to non-Turkish users from 2025-11-13 (search,
    CoinTurk report). It cannot run live for the user.
  - The BRL books are ~100x thinner (SOLBRL ~0.45 M BRL / day, ~805 trades / day): capacity is a few hundred dollars
    per event.
  - Triangle quoting on Binance is bot-dominated; premia beyond 30 bp are probably stale-print artefacts on 1m
    klines. Only aggTrades can tell.
- P(LIVE) 0.5 %.

### IB2. Weekend fiat-rail cycle of USD stablecoins
- **Mechanism.** Redemption happens only over bank wires for KYC'd institutions. Weekend sellers of USDC cannot reach
  par until Monday, and 24/7 rails disappeared with Silvergate / Signature in 2023-03. In the SVB weekend, Coinbase
  paused USDC:USD conversions "while banks are closed".
- **Barrier for the user.** Fees, not KYC. Binance stable pairs were zero-fee from 2023-06-30 (USDC/USDT; BUSD pairs
  from 2022-07). Earlier, 7.5-10 bp taker fees dwarf a 1-2 bp cycle, so IS 2020-21 cannot pass on taker fills.
- It is effectively a VAL / forward rule. Distinct from S (depeg thresholds) because it is a time-of-week cycle; S
  found reversion only in the SVB week, which bounds this from above.

### IB5. Launchpool BNB lock
- The calendar is not free (37-row Kaggle set behind an account; binance.com forbidden), so the idea cannot be tested
  without a user decision. BNB is also a high-beta exchange token and has few events.

### IB4. Coinbase transfer incidents (status page)
- **Data works.** robots disallows only /api/ and /embed/; history.json pages hold minute-stamped incidents back to at
  least 2022-12; ~40 of 120 incidents per quarter are per-coin transfer delays.
- **But.**
  - The trade must be on Coinbase. Vietnam availability is unconfirmed: a third-party review calls it a poor choice
    for Vietnamese users, and there is no official list.
  - UC (R68) found Upbit's suspension notices dead.
  - The listing-stamp version (J9's missing list) fails: the status page carries no listing posts.

### IB9. Pre-launch perps
- Hyperliquid's API serves 2024 candles (HYPE 1d from 2024-12-05), but the hyperps found by search (PUMP, MON) are
  2025. BitMEX's pre-launch HYPE future started 2024-12-02. No IS / VAL events, so forward-only (like L6).

### IB6. CNH vs onshore CNY
- No onshore spot-close series was reached (FRED timeout, host dropped after two tries). Even with it, IC's 1.15 bp
  round trip vs a few stretched days a year gives power ~1. It is a neighbour of H-CNH / P, which were both below fees.

## Considered and dropped (no slot)
- **Vietnamese stocks / VN30F** (no-short rule, T+2, ETF reviews, VN30F expiry). These are real barriers and the user
  has a DNSE account, but they are a separate research program (106.dnse-stock/docs/research, R2-R24, incl. ETF /
  expiry / warrant rounds). Do not duplicate them here.
- **Selling the Upbit premium during deposit suspensions** (Upbit KYC, Korean residents only: the user cannot cross).
  bitFlyer FX SFD band (Japanese KYC). Kalshi (US-only).
- **Shorting hard-to-borrow US stocks via CFD at flat financing.** IC / Dukascopy CFD lists hold large caps only, and
  borrow-fee history is paid.
- **ETF / ETN creation suspensions** (USO 2020, TVIX 2012): a few per decade.
- **MiCA USDT delistings for EEA users and Binance country exits** (forced conversions with deadlines): one-offs, and
  mostly in HOLD.
- **Airdrop / fork snapshot basis on Binance** (spot carries the airdrop, the perp does not): the analog of J11, and
  the announcement times are on binance.com.
- **Chain halts** (SOL 2021-23): every venue is locked equally, so there is no venue-specific gap.

## What a user decision could unlock
1. Use of the Zenodo listing file (L1 / L7). It gives exact withdrawal / announcement times for IB7 and possibly margin
   / Launchpool categories (IB5, IB8).
2. An archive Ethereum RPC for wrapper exchange rates (IB1). It is the same decision as J8.
3. A Binance API key used only to log the CMS announcement stream forward (IB8, and A2-type bots).
4. Confirmation that Coinbase Advanced and Binance BRL pairs are open to a Vietnamese account (IB4, IB3).

## Requests (research/data/scout_ib/requests.log)
| host | robots | probe | result |
|---|---|---|---|
| data.binance.vision | 404 (S3 NoSuchKey) | BETHETH, WBETHETH, WBTCBTC, SOLTRY, SOLBRL 1d monthly; USDCUSDT 1m HEAD | all 200 |
| api.exchange.coinbase.com | 401 (no file) | CBETH-ETH daily 2023 | 200 |
| status.coinbase.com | 200: Disallow /api/, /embed/ | history.json?page=16 | 200; incidents only |
| api.bybit.com | 404 | v5 spot kline TONUSDT 2024-08-08 | 200 but retCode 10001 "Not supported symbols" |
| public.bybit.com | 404 | /spot/TONUSDT/ index | 200, monthly files from 2022-12 |
| api.hyperliquid.xyz | 404 | candleSnapshot HYPE 1d, end 2024-12-31 | 200, 27 candles |
| fred.stlouisfed.org | timeout x2 | none | host dropped |
| www.chinamoney.com.cn | 404 | none | no spot-close source identified |

## Search sources used
- Binance withdrawal timing: <https://forklog.com/en/binance-announces-toncoin-listing-for-spot-trading/amp>,
  <https://www.onebullex.com/news/articles/binance-confirms-hype-listing-with-usdt-usdc-and-try-pairs-on-september-24>
- Margin delist mechanics: <https://en.cryptonomist.ch/2026/07/21/binance-delists-margin-pairs/>,
  <https://www.digitaltoday.co.kr/en/view/98785/binance-to-delist-12-margin-trading-pairs-on-sept-3-including-sui-avax-link>
- WBETH / BETH redemption: <https://binance.com/en/wbeth>,
  <https://www.fxstreet.com/cryptocurrencies/news/binance-to-support-ether-staking-withdrawals-from-april-19-202304130944>
- LST arbitrage: <https://nethermind.io/blog/how-the-shanghai-upgrade-will-impact-mev>, <https://arxiv.org/pdf/2402.17748v1>,
  <https://blockworks.com/news/ethereum-stakers-9-day-wait-steth>
- TRY gating: <https://en.coin-turk.com/binance-takes-major-step-in-turkish-crypto-market/>
- USDC weekend / SVB: <https://www.theblock.co/post/219887/biggest-usdc-burn-on-record-just-occurred-net-redemptions-since-friday-reach-4-5-billion>
- Zero-fee stable pairs: <https://www.aicoin.com/en/news-flash/2626497>
- Launchpool list: <https://baselight.app/u/kaggle/dataset/bryanchungweather_binance_launchpool_history_record>
- Hyperps: <https://coinfomania.com/hyperliquid-pump-usd-hyperp-launch/>, <https://blog.bitmex.com/hypeusdtz25>
- Coinbase Vietnam: <https://tradersunion.com/brokers/crypto/view/coinbase/is-coinbase-legal-in-vietnam/>
