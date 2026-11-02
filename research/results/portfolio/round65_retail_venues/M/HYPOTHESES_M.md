# Stream M hypotheses (round 65): Upbit non-KRW market additions, K2's rule frozen

Written Sun Nov 1 11:49:35 UTC 2026 (from `date -u`). This was before any return, price path or pump was computed.

What had been done by then:
- notice titles parsed (stream W's cache, read-only);
- Upbit 60-minute candle *timestamps* requested to date the first candle of each market (events.py probe / before);
- the current market list read once for renamed markets;
- 6 WebSearches for the opening times of delisted markets.

No Binance price had been requested. HOLD (2025-01-01..) is never requested, loaded or counted. Every Upbit request
ends at or before 2024-12-31 23:59:59 UTC, and only events with L < 2024-12-28 are used.

## Mechanism
K2 says Korean retail chases a coin when Upbit opens it, arbitrageurs carry the pump to Binance, and it fades within
72 h. A BTC- or USDT-market addition opens the coin to Upbit users with no KRW pair yet. That funnel is weaker, since
KRW holders must first buy BTC or USDT. My prior (J2, stream I / H) is a smaller pump and a smaller fade, possibly none.

## Event definition (declared; events.py)
**M event.** An Upbit notice that adds coin X to the BTC and/or USDT market, with all of these true:
1. **First Upbit appearance.**
   - No earlier Upbit addition notice names X (titles from 2017-10).
   - No candle on KRW-X, BTC-X or USDT-X exists before notice - 1 h. This is checked with the candle API
     (`to = t - 1 h, count 1`).
2. **No KRW pair at L.** The KRW-X candles start more than 8 days after the notice, or KRW-X does not exist.
   - Some notices have KRW in a mixed title such as "KRW, BTC (A, B)". There, the coins without KRW candles are M
     events: MASK 2021-10, AUDIO 2021-11, GAL 2023-01 (via BTC-G after the rename), ALT 2024-02 and BIGTIME 2024-04.
   - AUDIO has had no KRW market ever, and no KRW delisting notice.
3. **A tradable perp.** The Binance USDT-M perp trades from >= 7 d before the notice to >= 4 d after (local perp_1d,
   cut at 2025-01-01).
4. The notice falls in 2020-01-01 <= t < 2024-12-28.

**L = the start of the first 60-minute candle of the new BTC- / USDT-X market.** If both open, I take the earlier.

**When the market is now delisted (404)**, L comes from, in this order:
- (a) the same notice's partner coin in the same market: SNX takes GRT's 08:00;
- (b) a WebSearch of the stated opening time, floored to the hour:
  - BONK USDT 2024-10-22 18:00 KST -> 09:00 UTC;
  - JASMY 2024-11-20 15:00 KST -> 06:00 UTC;
- (c) the notice time + the median notice -> first-candle lag of that year's candle-dated M events, floored:
  - SRM 2020-10-07;
  - STG 2023-08-10.

  These fallback events are flagged, and a sensitivity check without them is reported.

**Name-collision guard.** Upbit's BTC-market (or USDT) close of the entry hour x BTCUSDT must lie within 1/1.5..1.5x
of the Binance perp's entry price (after 1000x scaling). The guard is skipped when no Upbit candle exists.

**Event list (dates only, 33 events).**

| era | year | events |
|---|---|---|
| IS | 2020 | VET, XTZ, LINK, COMP, ALGO, SRM (fallback), FIL, UNI |
| IS | 2021 | NEAR, GRT, SNX (partner), MASK, AUDIO, GTC, OCEAN, LPT |
| VAL | 2022 | API3, ARPA, ENS, APE, RAY |
| VAL | 2023 | GAL, MAGIC, MINA, STG (fallback), ID |
| VAL | 2024 | ALT, BIGTIME, PEPE (USDT), MEW, BONK (USDT, search), JASMY (search), SWELL |

Expected counts: IS 16, VAL 17.
- Many of these coins get a KRW listing weeks or months later (K2 events). They are separate events with separate
  dates, and none falls within 72 h.
- Excluded:
  - coins already on KRW: the GAS / NEO / SOL 2024-06 batch, the 2024-11-13 USDT batch, and INJ / UNI / RENDER in
    the KRW + USDT notices;
  - coins already on BTC: FIL, ARPA, AGLD, OXT, NEAR, XLM, BNT, ASTR, EGLD in the USDT batch;
  - coins without a perp: most 2020 BTC-market coins (MLK, PXL, CHZ ...), PUFFER, BRETT (perp opened on the notice
    day), NCT.

## Rule (frozen; K2 exactly, k2rule.py copied with only the log folder changed)
- Short the alt perp / long BTCUSDT perp, equal notional.
- Fill at the close of the 1m bar starting at L + 1 h (fallback up to 4 later minutes).
- Exit at entry + 72 h.
- Cost 42 bp plus real funding (k2rule.trade).
- Pre-entry pump: alt vs BTC from L - 24 h to entry, from k2rule.px fills. K2's figure is +21.5 %.
- Reported but not chosen:
  - H24, as K2's declared sibling;
  - costs x1.5;
  - entry +5 min;
  - entry at L + 2 h.

**Grid: one primary cell (H72).** H24 is reported as information, so the max-over-cells null is that of 2 cells.

**Random benchmark (as K2's k2.random_k2):** gross short-alt / long-BTC on local 1h closes (bar starting at L + 1 h,
500 draws), against two kinds of draw:
- (a) other perps listed >= 30 d before, at the same hour;
- (b) the same coin at random hours 30-180 d after L.

## Bars and power
- **DEMO:** IS t >= 2.0, VAL net > 0, random >= 90 %, x1.5 costs and one step late positive.
- **LIVE:** additionally IS t >= 2.5, VAL t >= 1.5, >= 2/3 of years positive, random >= 95 %, and HOLD power >= 3.
- **Power at K2's VAL size** (SR 0.25 / trade):
  - The VAL pace of non-KRW additions is 17 / 3 yr = 5.7 / yr. The 2024 pace is 7 / yr.
  - So n_HOLD ≈ 10-13 and power ≈ 0.25 x sqrt(10..13) ≈ **0.8-0.9**.
  - Even pooled with K2 (~10 / yr), n_HOLD ≈ 28 gives power ≈ 1.3.
  - LIVE would need a VAL SR per trade >= 0.95 on these events alone. **LIVE is out of reach by arithmetic, so DEMO
    is the only reachable tier.**
- **Expected result:** a smaller pump than K2, so a smaller or no fade.

## K2 survivorship check (separate; KRW listings missing from K's event list)
J's 9 coin-events, re-checked with candles:

| J's coin-event | finding | in the check? |
|---|---|---|
| MATIC 2021-10-15 | genuine. The market was renamed POL, so K's current-list map put it on POLUSDT (perp 2024-09). L = KRW-POL first 60m candle 06:00 UTC. IS. | yes |
| OMNI 2024-05-03 | delisted from Upbit since. L = partner ZETA's KRW L, 09:00. VAL. | yes |
| STG 2024-05-30 | delisted from Upbit since. WebSearch: 16:45 KST -> L 07:00 UTC. VAL. | yes |
| BONK 2024-11-20 | delisted from Upbit since. WebSearch: 12:30 KST -> L 03:00 UTC. VAL. | yes |
| AUDIO 2021-11 | BTC only (M event) | no |
| GAL 2023-01 | BTC only (M event) | no |
| ALT 2024-02 | BTC only; its KRW market opens after 2024 (M event) | no |
| GAL 2024-07 | the GALUSDT perp stops 2024-07-11, so it is untradable | no |
| USDC | stablecoin | no |

Not resolvable: SRM's 2020-10 KRW listing. A 2020-10-15 "원화마켓 오픈 이벤트" exists, but there is no addition
notice and no candles. It is excluded and reported.

**Check.** I recompute K2's 40 events with the same k2rule copy, then add these 4 (IS +1, VAL +3), and report the IS
/ VAL net, t and n with and without them. It is information only: the K2 rule is not changed.
