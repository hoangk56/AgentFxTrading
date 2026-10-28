# Round 34 brief: Chinese futures-exchange positioning, ETF / ETP rebalancing dose from issuer data, crypto option flows

Written 2026-10-27 20:27 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as
rounds 25-33 (the user's LIVE and DEMO bars in research/PROMPT.md; no RELAXED tier).

**Why this round exists.** The user asked on 2026-10-27 to keep researching until a LIVE algorithm is found, using other
sources. Rounds 31-33 loaded public non-price tables and found no candidate: Japan flows / retail OI (31 J), practitioner
communities (31 P), crypto on-chain and Binance positioning (31 C), US liquidity (32 L), per-asset implied vol (32 V),
attention (32 A: one sub-DEMO draft), crypto cross-venue premiums (33 K), SGE premium and SNB deposits (33 S, finishing).
Round 31 G (GLD / IAU / SLV holdings, NOAA outlooks) may still be running. This round takes three more sources no round
has loaded, each a **measured quantity of a real flow or position**, not a public price signal:
- who holds the Chinese metal and oil futures (exchange-published member rankings);
- how many dollars leveraged / inverse ETPs must trade at the close (issuer shares outstanding x NAV x leverage);
- what option buyers paid for on the main crypto option venue (trade-level history with implied vols).

Reachable from this Mac (probed 2026-10-27 20:27 UTC, HTTP 200): www.shfe.com.cn, www.ine.cn, www.proshares.com,
www.uscfinvestments.com, history.deribit.com (public API, no key). www.direxion.com answers 403; www.ishares.com 301.

**Everything not changed here follows research/results/portfolio/round31_new_sources/BRIEF.md**: read it first,
including its "Read first" list, Data section (HOLD 2025-01-01..2026-09-24 closed, new series cut at 2024-12-31 at
load), network rules (no accounts / logins / payment / CAPTCHA, robots.txt, >= 1 s between requests to one host and the
API's own rate limits, no e-mail in any request, downloads under `web/` parsed with `python -I`, every fetch logged),
test rules, PREREG_DRAFT rule and what to return. Also read round 32's BRIEF.md "Rules added" (publication lags, power
arithmetic first) and round 33's (same-timestamp rule for two-leg quantities), and the STREAM files in round31_new_sources/,
round32_liquidity_vol_attention/ and round33_cross_venue/ (what the last three rounds already found).

## Streams
| stream | direction | why it might escape the limits | already done (don't redo) |
|---|---|---|---|
| H | **Chinese futures exchanges' public position and stock tables.** SHFE (and INE for crude, from 2018-03) publish after each session the top-20 member rankings by volume, long OI and short OI per contract, and weekly / daily warehouse stocks (gold, silver, copper; INE crude). Build the net long of the top-20 (and of named broker groups if stable, e.g. the "foreign-linked" or the big retail brokers) per metal, and its change. Hypotheses from the mechanism: Chinese speculative crowding in silver / gold (top-20 net long change, z) that has to unwind or continues as momentum (state the side from the literature on Chinese futures positioning before any return); warehouse-stock draws as physical demand. Targets XAUUSD, XAGUSD, XTIUSD / XBRUSD (INE), maybe AUDUSD (copper proxy, declare it); horizons 1-5 days; entry after publication (SHFE posts after 15:00 Beijing for the day session: state the time you can verify, and do not use night-session data before it is published). | Positioning of a segmented, retail-heavy venue (like round 31 J's TFX, but with long / short split and per-member detail) that crosses to London / COMEX via arbitrage; never loaded here. | rounds 10 A / 24 B / 27 V / 29 O: SHFE / SGE session clocks and opens (time of day only, below cost); round 33 S: SGE premium (read STREAM_S.md); round 4 / 9 CFTC COT (weekly US positioning) |
| E | **ETF / ETP rebalancing with the measured dose.** Daily shares outstanding and NAV from issuers' public history files (ProShares: leveraged / inverse equity, gold, silver, crude, natgas, VIX funds; USCF: USO / UNG / BNO; other issuers you can reach without an account; delisted funds such as UGAZ / DGAZ / UWT / DWT / TVIX only if a free archive has them). Compute each day's required rebalance in dollars = sum over funds of AUM x L x (L - 1) x the day's return up to the rebalance time, and scale it by a liquidity measure you declare (e.g. the underlying's average daily dollar volume or futures OI from a free source, or the IC M1 activity). Hypotheses (Cheng & Madhavan 2009; Shum et al. 2016; Barbon et al. 2021; Ivanov & Lenkey 2018 for the null): a large dose pushes price in the day's direction into the close / settlement (US500, USTEC, US30, US2000 into 16:00 ET; XAU / XAG into the COMEX settlement; XTI / XBR / XNG into the NYMEX settlement) and reverts the next morning; VIX ETPs' rebalance as a vol-buying flow at the close (target US500). Horizon: the last 5-60 minutes into the close and the next session. | Rounds 6 S1 and 13 tested the leveraged-ETF flow as a big-day dummy without size: real only in gold, in indices only 3-4/2020. The dose x liquidity can make the flow >= 3x larger on the days it matters (natgas LETFs were a large share of NG futures OI in some years), which is the "condition that makes a real flow bigger" PROMPT asks for. | round 6 S1 (settlement momentum dummy), round 12 L (gold settlement big days, DEMO weak), round 13 (LETF big days), round 31 G (GLD / IAU / SLV holdings: read STREAM_G.md if it exists) |
| D | **Crypto option flows from Deribit's public trade history** (history.deribit.com `public/get_last_trades_by_currency_and_time` or by instrument, with each option trade's price, amount, direction, iv and index price; expired instruments via `get_instruments?expired=true`). Build daily / 4-hourly: put-call volume imbalance, buyer-initiated put minus call premium, 25-delta-like skew and ATM implied vol from trade ivs, block trades, and the gap between implied and realised vol. Hypotheses from the literature (option-implied information for crypto, e.g. Alexander & Imeraj; skew and order-imbalance predictability in equity options, Pan & Poteshman 2006; Easley, O'Hara & Srinivas 1998) with the side fixed before any return. Targets BTCUSD, ETHUSD at IC; horizons 4 hours to 5 days. State the history start per currency (Deribit options from ~2016; volume thin before ~2019) and which bar the shortened IS can still meet. | Option buyers' net demand is a flow that informed traders choose (Pan & Poteshman) and that dealers must hedge in the perp / spot; never built here (round 12 K only used the Friday 08:00 expiry clock, and needed paid OI). | round 12 K Deribit expiry clock (fade BTC 07:00-08:00 on Fridays, lead); round 4 / 9 Binance funding and taker flow; round 31 C (Bitfinex / Binance positioning, liquidations); round 33 K (premiums); round 32 V (CBOE implied vols) |

## Rules added for this round
- Round 31 G and round 33 S may still be running: use **at most 1 heavy Python process** per stream while
  `ps aux | grep -c "[r]esearch/.venv/bin/python"` is above 4, each under ~3 GB RAM. Downloads: one request at a time
  per host from your stream (round 31 C ran two jobs at once against one host: don't).
- Publication time is part of the rule (write it into HYPOTHESES before the first return): SHFE / INE rankings after the
  day session (and say whether the posted table includes the previous night session); issuer shares outstanding are
  T+1 for many funds (shares created on day D appear in the file dated D or D+1: verify on known big-creation days and use
  only values public before the entry); Deribit trades are public in real time, so a 4-hour signal may use trades up to
  the bar close.
- Do the power arithmetic first (round 16 STREAM_X frontier, round 10 minimum-edge table): state the per-trade edge your
  hypothesis needs for LIVE at its trade count.
- Write ONLY `HYPOTHESES_<stream>.md`, `STREAM_<stream>.md` and `PREREG_DRAFT_*` in
  research/results/portfolio/round34_china_etf_options/. Scripts, data and outputs under
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r34/<stream>/`.
- A series that starts after 2016 shortens IS: say which bar it can still meet (LIVE's IS t >= 2.5 still applies, no
  rescaling).
- Keep going inside your stream: an unusable or null first source is not the end; move to related free sources you
  discover (e.g. DCE / ZCE / CFFEX rankings for a proxy, other ETP issuers, other crypto option venues' public history).
