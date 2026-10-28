# Round 36: Asian central-bank liquidity operations, US household cash payments (Daily Treasury Statement outlays)

2026-10-28 (UTC). Sixth round after the user resumed the research with other sources allowed, and the last before the
pause the user asked for ("xong vòng 36 thì dừng lại nhé", 2026-10-28). Brief:
[round36_asia_liquidity_household_cash/BRIEF.md](round36_asia_liquidity_household_cash/BRIEF.md), written 01:42 UTC
before any return. Same bars as rounds 25-35 (LIVE / DEMO, no RELAXED tier). HOLD stayed closed for every return (series
cut at 2024-12-31, IC prices at ts < 2025-01-01). Disclosed slip, not used: stream A printed the header and first three
rows of the 2025 sheet of HKMA's convertibility.xlsx (three strong-side transactions in May 2025) after its sides were
fixed.

## Answer
- **No LIVE candidate. No DEMO candidate. No PREREG_DRAFT. HOLD not opened.**
- Neither a currency board's mechanical drain nor money the Treasury pays straight to households moves the targets at
  1-5 days by an amount LIVE needs; the closest cells (HIBOR jumps -> HK50, a household-cash surprise -> USTEC) are
  global-rate or timing patterns, not the declared mechanism.

## Streams
| stream | source | cells | best IS net t on the declared side (chance) | verdict | file |
|---|---|---|---|---|---|
| A | HKMA convertibility.xlsx (every currency-board transaction from 2018); Eastmoney mirror of SHIBOR, HKD HIBOR, CNH HIBOR, RRR changes. HKMA API blocked (405 after one large request); pbc.gov.cn robots `Disallow: /`; chinamoney behind a robot check; BoJ not loaded (reserves abundant) | 33 | 1.99 (A3 HIBOR 1M jump -> HK50 h5; null p50 for that family 2.56) | none | [STREAM_A.md](round36_asia_liquidity_household_cash/STREAM_A.md) |
| U | DTS withdrawals 2005-24 (238,748 rows: individual refunds, Social Security / SSI, EIP, unemployment, VA), a Social Security payment calendar (matches 886 / 890 big days), Dukascopy US500 / USTEC H1 2012-15 as PRE | 65 | 1.90 (U3 h3 USTEC; null p50 1.94, p95 2.77) | none | [STREAM_U.md](round36_asia_liquidity_household_cash/STREAM_U.md) |

### A: Asian central-bank liquidity
- A1 short HK50 the weekday after an HKMA weak-side purchase (61 trade days 2018-23), 5 d: IS +15.9 (t 0.50), VAL
  -29.5.
- A3 HIBOR 1M jump -> HK50 5 d: IS +38.9 (t 1.99), VAL +9.6 (t 0.25); the same rule on USTEC gives IS t 1.89, VAL -13.2:
  HIBOR tracks USD rate expectations through the peg, a US-rate signal.
- P1-P3 (SHIBOR rises, CNH HIBOR squeezes, RRR cuts -> USDCNH, HK50, AUDUSD): nothing; RRR cuts' VAL +317 bp HK50 is two
  stimulus days.
- Information (post hoc, not registrable): US indices rose the day after HKMA weak-side purchases (the declared control
  side, short, loses: US500 h1 IS -36.5, t -3.04; VAL -48.2, t -2.62).

### U: US household cash
- Social Security calendar Wednesdays / 1st-3rd, realised refund dose, refund-season Wednesdays (the largest scheduled
  household dose of the year): flat for US500, USTEC, BTC; negative for US2000 in both eras. ETH: IS cost.
- U3 (last 5 DTS days of household cash vs the same window a year earlier, top quintile), 3 d: USTEC IS +33.3 (t 1.90),
  VAL +55.2 (t 2.26), PRE 2012-15 mid +50.2 (t 2.93); US500 IS t 1.35, VAL 1.96. The anatomy does not support the
  mechanism: any single component gives a similar IS mid, 48 % of signals are calendar shifts, and the IS gain sits in
  turn-of-month trades. Power at the VAL size 1.5-1.7.
- The three EIP rounds: inconsistent signs (the 2020-21 market, not the payments).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- HKMA currency-board transactions and HKD / CNH HIBOR, SHIBOR, RRR changes for HK50, USDCNH, AUDUSD.
- US household cash payments from DTS (refunds, Social Security, EIP, transfers), scheduled or realised, for BTC, ETH,
  US2000, USTEC, US500.

## Directions that need the user
| direction | value |
|---|---|
| Retry the HKMA API from another network / later (aggregate balance, scheduled settlements, 2008-15 strong side) | LIVE < 2 %, DEMO ~2 % |
| PBoC daily OMO sizes (paid Wind / CEIC, or permission to use pbc.gov.cn despite its robots.txt) | ~1 % LIVE, ~2 % DEMO |
| Paid retail order-flow data (Nasdaq RTAT) | < 2 % |

## State after round 36 (pause)
- C3 is the only LIVE algorithm. F3 runs live at 0.01 lot and E1 on demo (EcbWindowBot); the gold $50-level rule runs on
  demo (HOLD + demo t 1.45 at the last check, promotion not reached).
- Rounds 31-36 (2026-10-27/28) loaded ~20 public non-price sources; no candidate reached DEMO. Several real effects exist
  at mid or on the same day, but they are priced before publication, predict magnitude not direction, or are 0.03-0.15
  sd per trade.
- Research pauses here at the user's request. Next step the user approved on 2026-10-28: prepare ONE joint
  pre-registration of the VAL-strong rules with fixed sides (rounds 32-36: Deribit Friday expiry fade, USTEC high-LETF
  dose, HN "recession" -> long US500, Coinbase premium -> BTC, U3 household cash -> USTEC, possibly gold LETF dose), with
  a multiplicity-adjusted HOLD bar; it is a bar change (they fail IS), DEMO at most, and HOLD opens only after the user
  confirms the registration.
- Recurring: rebuild the gold bot's USD calendar seed before 2026-12-11; rerun the F3 / E1 forward log on new days.
