# Round 33 brief: cross-venue premiums and margin positioning (crypto, gold), central-bank balance sheets (CHF)

Written 2026-10-27 19:02 UTC (from `date -u`). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading. Same bars as
rounds 25-32 (the user's LIVE and DEMO bars in research/PROMPT.md; no RELAXED tier).

**Why this round exists.** The user asked on 2026-10-27 to keep researching until a LIVE algorithm is found, using other
sources. Rounds 31-32 opened public non-price tables: Japan's flows and retail open interest (J), practitioner
communities (P), US fiscal / Fed liquidity (L) and per-asset implied vol (V) gave nothing; round 31 C (crypto on-chain,
Binance positioning), G (gold ETF holdings, natgas weather) and round 32 A (attention) may still be running. This round
uses a different kind of source: **the same asset priced or positioned in a second, segmented market**. A premium
between two venues that capital cannot freely arbitrage measures local demand that has to cross over through a known
channel (Korean retail into BTC, Chinese buyers into gold, US institutions via Coinbase), and margin-lending books show
leveraged positioning directly. Reachable from this Mac (probed 2026-10-27 19:00 UTC, HTTP 200): api.exchange.coinbase.com
(candles), api.upbit.com (KRW candles), api-pub.bitfinex.com (margin position stats), www.sge.com.cn and en.sge.com.cn,
data.snb.ch, www.boj.or.jp. LBMA's price JSON answers 403; BitMEX 403.

**Everything not changed here follows research/results/portfolio/round31_new_sources/BRIEF.md**: read it first,
including its "Read first" list, Data section (HOLD 2025-01-01..2026-09-24 closed, new series cut at 2024-12-31 at
load), network rules (no accounts / logins / payment, robots.txt, >= 1 s between requests to one host and the API's own
rate limits, no e-mail in any request, downloads under `web/` parsed with `python -I`, every fetch logged), test
rules, PREREG_DRAFT rule and what to return. Read round 32's BRIEF.md "Rules added" (publication lags, power
arithmetic first) and the STREAM files already in round31_new_sources/ and round32_liquidity_vol_attention/.

## Streams
| stream | direction | why it might escape the limits | already done (don't redo) |
|---|---|---|---|
| K | **Crypto cross-venue premiums and margin books.** (1) Coinbase premium: Coinbase BTC-USD / ETH-USD vs Binance BTCUSDT / ETHUSDT (data.binance.vision) at the same minute or hour, from 2017; (2) Korean "kimchi" premium: Upbit KRW-BTC vs Binance in USD (KRW rate from a free official source, e.g. Bank of Korea ECOS if reachable without a key, else BIS / ECB reference rates), from 2017-10; (3) Bitfinex margin long / short position sizes (stats1 pos.size, long and short, from ~2017 if the history goes back) and margin funding. Hypotheses from the mechanism: a rising US-venue premium = US institutional buying that continues (ETF and treasury flows route through Coinbase); an extreme Korean premium = retail frenzy that reverts; a surge in Bitfinex longs = levered crowding (sides from the literature: e.g. Makarov & Schoar 2020 on premiums). Targets BTCUSD, ETHUSD at IC, hours to 5 days. | The premium is a price of segmentation that persists for days (capital controls, fiat rails), so the flow it measures crosses over at a known pace; never tested here. Crypto's daily sd dwarfs IC's cost. | round 4 / 9 Binance funding and taker flow; round 12 C stablecoin issuance; round 24 A ETF flows into NAV; round 31 C (on-chain, Binance metrics, liquidations): read STREAM_C.md if it exists and don't duplicate |
| S | **Gold in segmented markets and central-bank balance sheets.** (1) SGE's daily Shanghai Gold Benchmark Price (AM / PM, CNY per gram, from 2016-04) and SGE Au99.99 daily close (history depth to check) vs London gold in CNY at the same time (IC XAUUSD x the USD/CNY rate, USDCNH M1 is in research/data): the onshore premium as Chinese demand; (2) any free Indian premium source you can reach; (3) SNB weekly sight deposits (data.snb.ch, cube snbgwdzid; weekly since ~2009), a public proxy of SNB FX intervention, for USDCHF / EURCHF-proxy (USDCHF and EURUSD) over 1-5 days, and BoJ current-account / operations data only if it is a mechanical flow not already tested. | A large onshore premium means import quotas bind and Chinese buying must be met by London / Swiss flows over the next days; SNB intervention is persistent and its weekly footprint is public with a lag. Neither has been loaded here. | rounds 24 B / 27 V SGE session and night clocks (time-of-day only, below cost); round 31 G GLD holdings; PROMPT lists "premium SGE" under paid data: check whether the free SGE benchmark makes it free |

## Rules added for this round
- Other streams may still run: use **at most 1 heavy Python process** per stream while
  `ps aux | grep -c "[r]esearch/.venv/bin/python"` is above 4, each under ~3 GB RAM.
- Premiums need both legs at the same timestamp: state the timestamp rule and the FX conversion rate's time in
  HYPOTHESES before the first return. A premium computed with a stale leg is a look-ahead / artefact source.
- Write ONLY `HYPOTHESES_<stream>.md`, `STREAM_<stream>.md` and `PREREG_DRAFT_*` in
  research/results/portfolio/round33_cross_venue/. Scripts, data and outputs under
  `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r33/<stream>/`.
- A series that starts after 2016 shortens IS: say which bar it can still meet (an IS from 2017-10 is 4.2 years; LIVE's
  IS t >= 2.5 still applies, no rescaling).
- Keep going inside your stream: an unusable or null first source is not the end.
