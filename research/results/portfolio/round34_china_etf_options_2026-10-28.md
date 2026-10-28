# Round 34: Chinese futures-exchange positioning, ETF / ETP rebalancing dose from issuer data, Deribit option flows

2026-10-27 / 28 (UTC). Fourth round after the user resumed the research with other sources allowed. Brief:
[round34_china_etf_options/BRIEF.md](round34_china_etf_options/BRIEF.md), written 2026-10-27 20:27 UTC before any
return. Same bars as rounds 25-33 (LIVE / DEMO, no RELAXED tier). Each source is a measured quantity of a real flow or
position, not a public price signal. HOLD stayed closed (new series cut at 2024-12-31, IC prices at ts < 2025-01-01;
Deribit was never requested past 2024). Disclosed slips, none used: stream E's first format probe printed TQQQ's five
newest NAV / shares rows (2026-10-20..26); stream H saw a WebSearch summary quoting 2026 SHFE position-price
correlations.

## Answer
- **No LIVE candidate. No DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- Two effects hold their side in VAL but fail IS, so they are DEMO-or-nothing under any future data and are listed for
  the user (forward logs need no bar change, a promotion would): the leveraged-ETF dose on USTEC into the close, and the
  Friday 08:00 UTC Deribit expiry fade on negative-gamma / high-volume Fridays.

## Streams
| stream | source | cells | best IS net t on the declared side (chance) | verdict | file |
|---|---|---|---|---|---|
| H | SHFE member rankings 2008-24 (incl. a new daily split: brokers' clients vs other members = a Chinese "COT", from 2012-03), SHFE / INE daily warrants | 38 | +1.46 (median best of 38 ~2.38) | none | [STREAM_H.md](round34_china_etf_options/STREAM_H.md) |
| E | ProShares history for 31 leveraged / inverse funds 2006-24 (accounts.profunds.com), CFTC OI as denominator, NEXT FUNDS 1570 / 1357 | 52 | USTEC H1-roll 1.38; silver cells up to 4.01 but reverse in VAL (null p50 1.43, p95 2.74) | none | [STREAM_E.md](round34_china_etf_options/STREAM_E.md) |
| D | Deribit BTC option trades 2017-06..2024 (16.5 M, public history API), dealer gamma rebuilt from signed trades | 55 | +1.49 (chance ~2.54) | none | [STREAM_D.md](round34_china_etf_options/STREAM_D.md) |

### H: SHFE / INE tables
- Top-20 net change, follow (the Chinese "spider-web" lore): gold IS +2.9 bp (t 0.70), VAL -7.4; PRE and VAL negative in
  all 4 gold cells; silver ~0.
- Commercials' (non-broker members) net change, follow (Kang, Rouwenhorst & Tang 2020): gold 3 d IS -13.2 (t -2.97),
  VAL +7.7 (t 1.29): every metal cell <= 0 in IS and > 0 in VAL, sign not stable.
- Named seats (Yongan, CITIC): Yongan gold IS +13.4 (t 1.46), VAL -47.4 (t -2.28).
- Warehouse warrant draws (gold, silver, copper -> AUD, INE crude -> oil): IS t <= 0.98; crude wrong side in both eras.
- Information: within the SHFE day commercials trade against the move (corr of their net change with gold's same-window
  return -0.32 PRE, -0.25 IS, -0.14 VAL), clients chase it; no premium follows over 1-3 days at IC. Same conclusion as
  round 33 S: the Chinese venue carries no next-day information for London / COMEX.
- INE publishes no crude member rankings; CFFEX index rankings answer at ~60 s per request (not fetched).

### E: leveraged / inverse ETP rebalancing with the measured dose
- Dose Γ = Σ AUM x L(L-1) per unit return: Nasdaq Γ / futures dollar OI rose from 0.74 (2016) to 2.2 (2023), so a 1 %
  move needs 1-2 % of OI traded; Dow 0.4-1.1 %; S&P and Russell 0.05-0.12 %; gold 0.005 %, silver 0.03-0.07 %, crude
  0.01-0.035 %, natgas up to 0.09 %; VIX ETPs 0.08-0.36 % of VX OI.
- H1-roll USTEC w30 (top dose decile, follow into 16:00 ET): IS +10.26 bp (t 1.38; ex-2020 +3.78, t 0.9), VAL +11.49
  (t 2.78), random 100 % / 100 %. Fails DEMO on IS t; its IS is the 2020 tail and its VAL may be the 2022 bear market.
- US500 / US30: IS t 1.34 / 1.59, VAL weak; US2000 negative.
- Silver: IS +16.54 (t 4.01) but VAL -8.11 (t -3.02); absolute-dose silver VAL t -6.1 / -4.0. Gold: H1-roll w15 IS
  t 1.86, VAL 2.17, PRE 0.2; absolute-dose ~2 trades a year.
- P1 (post hoc): the dose adds nothing to gold's settlement momentum (interaction t -4.0 in IS): round 12's gold
  big-day DEMO rule is not an LETF flow (dose ~$5 m per 1 % against ~$100 bn of OI). In US indices round 13's VAL
  big-day reversal sits on low-dose days; high-dose days don't reverse (fits the mechanism, too small to trade).
- VIX-ETP dose -> US500, next-morning fade, pooled books, JP225 with NEXT FUNDS: nothing.
- Direxion (403) and the delisted Credit Suisse ETNs are missing, so S&P / Russell doses are understated.

### D: Deribit option flows
- Net delta demand, put share bought, risk reversal, implied minus realised vol, block-trade delta (F1-F5): option order
  flow forecasts nothing at 4 h-5 days (1-day slopes 0 ± 10 bp per sd in both eras, with or without momentum
  controls). Best F3 risk reversal 5 d IS +147 bp (t 1.49), VAL -1. F4's 1-day slope is opposite to the literature.
- Dealer-gamma follow / fade of 4-hour moves (G1 / G2): wrong sign (IS down to t -3.9).
- **Friday 08:00 UTC expiry fade (round 12 K4)**: on high-volume Fridays net IS +6.1 (t 0.80), VAL **+16.7 (t 3.24)**,
  VAL power 2.47; on negative-dealer-gamma Fridays (G3, the paper's condition) IS +18.8 (t 1.42), VAL +9.0 (t 2.40);
  positive-gamma Fridays lose (IS -4, VAL -9). A 10-20 bp gross effect over 1 hour, ~50 times a year: at 2017-21 IC
  costs (11-12 bp round trip) it fails IS, and both K and G3 lose in 2018. G (gamma) was declared after round 1's IS
  numbers, before any VAL or gamma value.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- SHFE member rankings (top-20, named seats, clients vs commercials) and SHFE / INE warehouse warrants for XAU / XAG /
  oil / AUD at 1-3 days.
- Leveraged / inverse ETP rebalancing with the measured dose (ProShares 2006-24) for US indices, metals, energy, VIX,
  JP225: the dose does not make the flow tradeable; gold's settlement momentum is not an LETF flow.
- Deribit BTC option order flow (delta demand, puts, risk reversal, VRP, blocks, dealer gamma) at 4 h-5 days.

## Directions that need the user
| direction | value |
|---|---|
| Forward demo log of the Deribit Friday expiry fade (K4 high-volume or G3 negative-gamma; rule fixed in HYPOTHESES_D.md, inputs computable live from the free tape). It fails IS, so promotion would need a bar decision (e.g. a 2020-24 design window) | ~25 % for a DEMO that survives HOLD, ~2 % LIVE |
| Forward log of E's H1-roll USTEC w30 on data after 2026-09-24 (rule fixed in HYPOTHESES_E.md; ~25 trades a year, expected t ~1.6 after 2 years at VAL size) | DEMO at most, LIVE < 2 % |
| Paid Deribit OI / Greeks history (Tardis, Laevitas, Amberdata) | ~2 % |
| CFFEX rankings for HK50 (2.5-day throttled crawl, or Wind / JoinQuant / Tushare account) | ~1 % |
| Direxion shares (403 here), Credit Suisse ETN archive (paid) | low / very low |

## State after round 34
Unchanged: C3 is the only LIVE algorithm; F3 live 0.01 lot, E1 and the gold $50-level rule on demo. Round 35 (OCC
option volume by underlying, Asian equity-derivative positioning: TAIFEX, KRX) is open.
