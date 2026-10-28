# Round 32: US liquidity tables, implied volatility of other assets, public attention

2026-10-27 (UTC). Second round after the user resumed the research on 2026-10-27 ("research đến khi nào tìm được thuật
toán live thì thôi", other sources allowed). Brief: [round32_liquidity_vol_attention/BRIEF.md](round32_liquidity_vol_attention/BRIEF.md),
written 18:42 UTC before any return. Same bars as rounds 25-31 (LIVE / DEMO, no RELAXED tier). HOLD 2025-01..2026-09
stayed closed in all three streams (new series cut at 2024-12-31 at parse, IC prices at ts < 2025-01-01).

## Answer
- **No LIVE candidate. No DEMO candidate. HOLD not opened.**
- Stream A wrote two PREREG_DRAFTs at the DEMO edge; neither is a clean DEMO pass, so the lead did not spend a HOLD look
  on them (reasons below).
- All three sources are public, dated and new here. None carries a 1-5 day signal that survives IS -> VAL at a size
  LIVE needs: liquidity and fiscal cash drains are priced or regime-dependent, per-asset VRPs flip sign between eras,
  and attention spikes are either the 1-day reversal / momentum already exhausted or a fear-reversal effect at chance.

## Streams
| stream | source | cells | best IS net t (chance) | verdict | file |
|---|---|---|---|---|---|
| L | Daily Treasury Statement (TGA, withheld taxes), NY Fed reverse repo, Fed H.4.1 (WALCL, reserves) 2005-24 | 82 | 1.43 on the declared side (circular-shift null max p50 2.98, p95 3.83); largest \|t\| 2.29 is the wrong side | none | [STREAM_L.md](round32_liquidity_vol_attention/STREAM_L.md) |
| V | CBOE daily indices: GVZ, OVX, VXN, VXD, RVX, VXEFA, VXSLV, VVIX, SKEW, VIX9D, COR1M/3M, DSPX, VIXEQ (EVZ is off the CDN) | 216 | 1.57 (random-date null best-of-180 p50 3.20) | none | [STREAM_V.md](round32_liquidity_vol_attention/STREAM_V.md) |
| A | Wikimedia pageviews 2015-24, Hacker News Algolia story counts 2007-24 | 60 + post hoc | 2.83 (median max of the family 2.92) | two drafts at the DEMO edge, not registered | [STREAM_A.md](round32_liquidity_vol_attention/STREAM_A.md) |

### L: net liquidity and cash drains
- "Net liquidity (Fed assets - TGA - RRP) drives equities": weekly changes give ~+7 bp a day on the 7-leg basket at
  mid (IS t 1.88), half of the ~+15 bp LIVE needs; at 5 days the sign is not stable (basket IS +8.1, VAL -4.2).
  Best cell L1a US500 1 day: IS net +9.3 bp (t 1.43), VAL +6.7 (t 0.73), power 0.77 / 0.55.
- Fed asset changes alone point the wrong way (IS 5 days -17.5 bp, t -2.12; VAL -29.7, t -2.23): QE is priced at its
  announcement, before the balance sheet moves.
- Realised TGA + RRP drain tails (|z| > 1.5) are negative in IS and positive in VAL (basket +27.6 bp, t 2.74, 59
  events): a regime (also positive 2011-14, negative 2009-10 and 2015-21), post hoc, not registrable.
- Debt-ceiling TGA rebuilds (9 events 2013-23): the indices rose in the week after 5 / 5 IC-era resolutions, against
  the drain story.

### V: per-asset implied vol and option-market shape
- Per-asset VRP (GVZ, OVX, VXN, VXD, RVX, silver) predicts the next 5 days with the wrong sign in IS (US30 NW t -3.15,
  USTEC -2.39, US2000 -2.41) and turns positive in VAL.
- Asset-specific IV shocks (the part VIX does not explain): gold's declared side loses in IS and VAL and wins in PRE;
  VXEFA -> EURUSD flips sign (IS t -2.67, VAL +1.48).
- "High VVIX / SKEW -> long indices" is the 1-day reversal: with the prior 1- and 5-day returns as controls z(VVIX) adds
  nothing (USTEC IS t -0.45). The ex-2020 IS t 2.73 is post hoc and removes exactly the crash the rule loses in.
- Implied correlation risk premium (COR1M etc., new on the same CDN): IS +48.9 bp (t 1.45), VAL +6.0 (t 0.10).
- No family above VAL-size power 1.35 (LIVE needs 3).

### A: attention
- **HN "recession" spike -> long US500 (and EURUSD), next 07:00 UTC, hold 3 days** (Da, Engelberg & Gao FEARS
  reversal; [PREREG_DRAFT_A_hn_fear_reversal.md](round32_liquidity_vol_attention/PREREG_DRAFT_A_hn_fear_reversal.md)):
  US500 net IS +32.9 bp (t 2.51), VAL +100.4 (t 2.70), 9 / 9 years positive; random control IS 87.9 % (< 90 %), VAL
  99.8 %. EURUSD leg: IS t 2.09, VAL +19.0, but PRE 2008-15 -22.0 (t -1.30). Episode-level t 1.35 IS (21 episodes),
  2.35 VAL (9). Correlation with C3 ~0.
  - **Lead's decision: not registered, HOLD not opened.** It misses DEMO on the IS random control; the family's best
    t equals chance (2.51 vs a median max of 2.53); the trades cluster in ~3 episodes a year, so the trade-level t
    overstates the evidence; the expected HOLD t is ~1.5 at the VAL size and ~0.4 at the usual 1/4 retention.
- **Abnormal Bitcoin Wikipedia attention -> follow the 20-day trend 5 days** (Kristoufek;
  [PREREG_DRAFT_A_btc_attention_trend.md](round32_liquidity_vol_attention/PREREG_DRAFT_A_btc_attention_trend.md)):
  IS +235 bp (t 2.83), VAL +68 (t 0.90). It is BTC's 2017-21 momentum: a pure momentum control makes +350 bp (t 3.59)
  in IS; VAL / IS 0.29; the HN replication fails in VAL; expected HOLD t ~0.7. Not recommended (the stream agrees).
- Own-asset attention -> retail price pressure (gold, US500, Japanese FX), FEARS on Wikipedia pageviews (wrong side in
  IS), Moat et al. 2013 weekly rule: nothing.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- US fiscal / Fed liquidity as a 1-5 day signal (net liquidity, TGA / RRP drains, H.4.1, debt-ceiling rebuilds).
- Per-asset implied vol, VRP, vol-of-vol, SKEW, implied correlation (CBOE CDN, 2006-24) for gold, silver, oil, US
  indices, EURUSD.
- Attention from Wikipedia pageviews and Hacker News (own-asset attention, FEARS, Moat): only the HN fear reversal is
  at the edge and it is at chance.

## Directions that need the user
| direction | value (chance of a LIVE candidate) |
|---|---|
| Google Trends / SVI history (unreachable here, no public API) for FEARS on the original series | LIVE ~1 %, DEMO ~5 % |
| X / Twitter counts (paid API, account) for BTC attention | ~1 % |
| CME CVOL (EUR / JPY implied vol; DataMine account) | ~1-2 % |
| Strike-level option OI / gamma on GLD / USO / QQQ (ORATS, CBOE DataShop; paid) | ~1-2 % |
| Forward log of the HN fear rule on data after 2026-09-24 (free; the user already chose to download post-09-24 data, but the rule misses DEMO, so it was not registered) | DEMO at most; ~13 trades a year, a verdict needs years |
| Forward log of L3's VAL pattern (realised drain tails), registered now on the VAL design | DEMO at most, ~3-5 % |

## State after round 32
Unchanged from round 31: C3 is the only LIVE algorithm; F3 runs live at 0.01 lot and E1 on demo (EcbWindowBot);
the gold $50-level rule runs on demo (1 demo trade so far, +10.24 bp vs the model's +10.46; HOLD + demo t 1.45). Round
33 (cross-venue premiums, SGE premium, SNB deposits) ran in parallel; round 34 (Chinese futures positioning, ETF /
ETP rebalancing dose, Deribit option flows) is open.
