# Round 34, stream E: leveraged / inverse ETP rebalancing with the measured dollar dose

Written 2026-10-27 20:49 UTC onwards (`date -u`). Hypotheses with UTC times: [HYPOTHESES_E.md](HYPOTHESES_E.md)
(52 counted cells declared 20:36-20:40 UTC before any return; addendum 1 at 20:41 UTC adds the post-hoc check P1 and
the Nikkei extension X1, declared before X1's data were loaded). Bars: research/PROMPT.md (LIVE / DEMO, no RELAXED).

HOLD hygiene: every fund, COT and VIX series was cut at 2024-12-31 at parse; every IC load at ts < 1735689600000.
**One disclosure:** the first format probe printed TQQQ's header and its five newest rows (2026-10-20..26: NAV, shares,
AUM). These are fund values, not IC prices, and were not saved or used. Later file checks printed dates only.

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- The free issuer data make the dose measurable. These were loaded for the first time here:
  - ProShares, 31 funds from 2006-11 to 2024 (equity 3x / 2x / -1x, gold, silver, crude, natgas, VIX ETPs);
  - Nomura NEXT FUNDS 1570 / 1357 (Nikkei 2x / -2x), 2012 / 2014 to 2024;
  - CFTC open interest as the liquidity denominator.
- The dose is large only in equities:
  - The Nasdaq funds' gamma rose from 0.74x to 2.2x NQ dollar OI between 2016 and 2023, so a 1 % move needs about
    1-2 % of OI to be traded. US30: 0.4-1.1 %. S&P and Russell (ProShares only): 0.05-0.12 %.
  - Gold: 0.005 %. Silver: 0.03-0.07 %. Crude: 0.01-0.035 %. Natgas: 0.002-0.09 %. VIX ETPs: 0.08-0.36 % of VX OI.
- **No counted cell meets DEMO.** That needs IS net t >= 2.0 with VAL net > 0.
  - The four cells with IS t >= 2 are three silver cells and one gold cell (rank by the absolute dose, w 15).
  - Silver flips in VAL (t -3.0 to -6.1). This is the flip rounds 6 and 12 already found.
  - The gold cell has 2 trades a year in IS and none in VAL: gold's dose relative to OI fell after 2015.
- Chance, from a per-day sign-flip null shared by the 52 cells: the max IS net t has p50 1.43 and p95 2.74. The
  observed max, 4.01 (silver H1-roll w 30), is beyond chance (p 0.001), but VAL is -8.1 bp (t -3.0).
- **Does the measured dose add to the plain |z| rule of round 13?** (P1, post hoc.)
  - Silver and oil in IS: yes (|z| x Γ/DOI interaction t +3.7 to +7.7). Both reverse or vanish in VAL.
  - Gold: no (IS t -4.0, VAL +1.0). Gold's settlement momentum (round 12 L4) is not an LETF flow. Its measured dose is
    ~$5m per 1 % move against ~$100bn of COMEX OI.
  - US indices: the interaction is positive in VAL (USTEC t +3.0 at both windows, US500 w 30 +2.1, US30 w 30 +1.9),
    with mixed IS signs. The best index cell is USTEC H1-roll w 30:
    - IS +10.3 bp (t 1.38), and only +3.8 (t 0.9) without 2020;
    - VAL +11.5 (t 2.78);
    - power 0.74 / 2.11.
  - It fails IS, and per the declared rule it cannot be promoted. It is the one result worth a forward look
    ("Directions" below).
- **Nikkei (X1).** The 1570 / 1357 dose (~JPY 17bn per 1 % move) ranked the JP225 OSE close quarter-hour (15:00-15:15)
  no better than round 13's all-days effect. The pipeline reproduces round 13's +3.39 bp (t 5.6) IS / +0.59 VAL.
  - The top dose decile nets +3.11 (t 0.87) IS and -1.43 VAL.
  - The TSE close is nothing.
  - Within top-|z| days, high-Γ days follow more (IS +14.3, t 2.2, vs -3.2) but not in VAL (+3.3, t 1.0).

## Sources
| source | span used | notes |
|---|---|---|
| ProShares `accounts.profunds.com/etfdata/ByFund/<T>-historical_nav.csv` (link on proshares.com; host has no robots.txt) | fund inception (2006-2011) .. 2024-12-31 | TQQQ SQQQ QLD QID PSQ / UPRO SPXU SSO SDS SH / UDOW SDOW DDM DXD DOG / URTY SRTY UWM TWM RWM / UGL GLL AGQ ZSL UCO SCO BOIL KOLD / UVXY SVXY VIXY VIXM. Date, NAV, shares, AUM |
| CFTC legacy futures-only COT `deacot<YYYY>.zip` | 2008-2024 | OI: ES + big SP, NQ mini + big, YM x5 + x10, RTY (CME + ICE mini), VX, GC, SI, CL, NG |
| CBOE VIX daily (copied from round 32 V's download) | 2016-2024 | VIX-futures beta proxy |
| Nomura AM `www.nomura-am.co.jp/fund/etf/history/ETF_1570.csv`, `ETF_1357.csv` (linked from nextfunds.jp; nomura-am has no robots.txt) | 2012-04 / 2014-07 .. 2024-12-30 | net assets, units, creations / redemptions |
| Internet Archive CDX + 7 snapshots of ProShares files (2023-24) | | posting-time check only |
| Unusable | | Direxion (403: TNA/TZA, SPXL/SPXS, SOXL missing, so the S&P and Russell doses are understated); Credit Suisse ETNs UGAZ/DGAZ, TVIX, XIV (delisted, no free shares archive), so natgas before 2020 and VIX before 2018 are understated; USCF USO/UNG/BNO are 1x (L(L-1) = 0, no rebalancing dose; the roll is another family); Rakuten / Daiwa Nikkei LETFs not fetched (small next to 1570 / 1357); no free Nikkei-futures OI series found, so X1 scales Γ by its own rolling median |

Fetch log: scratchpad `r34/E/web/requests.log`. Spacing was >= 1.5 s per host (4 s on web.archive.org), one job per
host, a browser User-Agent and no e-mail. Downloads were parsed with `python -I`.

## Mechanism checks (before returns; scripts/mech_check.py)
- **Leverage.** Median daily NAV-change ratios match the prospectus every year 2009-24:
  - TQQQ/PSQ -3.00, QLD/PSQ -2.00, UPRO/SH -3.00, GLL/UGL -1.00, KOLD/BOIL -1.00;
  - UVXY/VIXY 2.00, then 1.50 from 2018; SVXY/VIXY -1.00, then -0.50.
- **AUM = NAV x shares** in every row.
- **Shares lag.** Daily share changes correlate more with the same day's fund return than with the previous day's
  (TQQQ -0.29 vs -0.19, SQQQ -0.34 vs -0.19, UCO -0.47 vs -0.28, BOIL -0.47 vs -0.18). So the row dated D already
  includes D's creations. The rule uses the row dated < d.
  - Flows are contrarian: they lean against the day's move, which is Ivanov & Lenkey's offset.
- **Posting time.** At 2026-10-27 16:30 ET the file's last row was the previous trading day. At 16:50 ET the
  same-day row was still absent (checked by date only).
  - So row D is posted between D 16:50 ET and D+1 16:30 ET.
  - I could not pin it down further. The Internet Archive's CDX index lists 2016-24 snapshots of these files, but the
    snapshot fetches got HTTP 429, and I stopped after 2 tries.
  - **Robustness:** I reran every cell with the row dated <= d-2, which was public for certain
    (out/analyze_lag2_out.txt). Nothing changes:
    - USTEC w30: IS +9.46 (t 1.28), VAL +10.67 (t 2.54);
    - XAU w15: IS +2.46 (t 1.95), VAL +2.53 (t 1.87);
    - XAG w30: IS +15.91 (t 3.96), VAL -7.20 (t -2.57).

## Results (52 counted cells + information rows)
- **Columns.** All numbers are bp per trade, one trade per target per day. t is per day. Net = mid - half the actual
  spread at entry and at exit (- 0.6 bp for metals).
- **Power** = per-trade net Sharpe x sqrt(1.73 x trades a year). The VAL power is the expected HOLD t at the VAL size.
- **Eras.** IS 2016-21; energies 2018-21. PRE 2009-15 for XAU / XAG only (Dukascopy, cost = IC 2016-17 spread by
  minute + 0.6).

| cell | n/yr IS/VAL | mid IS (t) | mid VAL (t) | cost IS/VAL | net IS (t) | net VAL (t) | x1.5 IS/VAL | +1 min IS/VAL | IS ex-2020 (t) | power IS/VAL | PRE net (t) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H1roll USTEC w15 | 24/29 | +9.72 (1.4) | +5.01 (1.6) | 1.76/0.71 | +7.96 (1.17) | +4.30 (1.38) | +7.08/+3.95 | +2.15/+1.76 | +0.13 (0.0) | 0.63/1.05 | |
| H1roll USTEC w30 | 25/31 | +11.99 (1.6) | +12.20 (2.9) | 1.73/0.72 | +10.26 (1.38) | **+11.49 (2.78)** | +9.39/+11.13 | +2.21/+8.90 | +3.78 (0.9) | 0.74/2.11 | |
| H1roll US500 w15 | 21/30 | +7.97 (1.2) | +2.36 (0.8) | 2.19/0.57 | +5.78 (0.86) | +1.79 (0.62) | +4.68/+1.51 | +0.64/+0.13 | +0.01 (0.0) | 0.46/0.47 | |
| H1roll US500 w30 | 21/31 | +13.02 (1.6) | +5.32 (1.3) | 2.14/0.56 | +10.87 (1.34) | +4.76 (1.15) | +9.80/+4.48 | +3.38/+3.04 | +5.69 (1.2) | 0.72/0.87 | |
| H1roll US30 w15 | 24/24 | +8.41 (1.3) | -1.88 (-0.7) | 1.32/0.31 | +7.09 (1.13) | -2.19 (-0.82) | +6.43/-2.34 | +3.21/-2.29 | -0.39 (-0.1) | 0.60/-0.62 | |
| H1roll US30 w30 | 24/25 | +13.48 (1.8) | -0.17 (0.0) | 1.31/0.30 | +12.17 (1.59) | -0.47 (-0.12) | +11.51/-0.63 | +6.58/-1.03 | +1.60 (0.4) | 0.85/-0.09 | |
| H1roll US2000 w15 | 24/27 | +2.12 (0.4) | -0.63 (-0.2) | 2.40/1.78 | -0.28 (-0.05) | -2.41 (-0.78) | | | | -0.03/-0.59 | |
| H1roll US2000 w30 | 25/27 | -0.06 (0.0) | +0.18 (0.0) | 2.38/1.78 | -2.44 (-0.34) | -1.59 (-0.39) | | | | -0.18/-0.29 | |
| H1roll XAU w15 | 23/22 | +4.10 (3.3) | +4.11 (2.9) | 1.76/1.01 | +2.34 (1.86) | +3.11 (2.17) | +1.46/+2.60 | -0.17/+2.00 | +4.16 (3.3) | 1.00/1.65 | +0.29 (0.2) |
| H1roll XAU w30 | 23/24 | +4.61 (2.8) | +1.68 (0.9) | 1.74/1.01 | +2.87 (1.71) | +0.67 (0.36) | +2.00/+0.17 | +0.95/-0.83 | +3.09 (1.9) | 0.92/0.27 | +3.04 (1.9) |
| H1roll XAG w15 | 25/29 | +14.40 (4.2) | -6.03 (-2.9) | 3.97/4.54 | +10.43 (3.04) | -10.57 (-5.02) | +8.45/-12.84 | +6.35/-8.08 | +6.43 (1.9) | 1.63/-3.81 | +2.77 (0.9) |
| H1roll XAG w30 | 26/28 | +20.48 (4.9) | -3.62 (-1.4) | 3.94/4.49 | +16.54 (4.01) | -8.11 (-3.02) | +14.57/-10.35 | +13.80/-7.87 | +8.17 (2.1) | 2.15/-2.29 | +5.67 (1.3) |
| H1roll XTI w15 | 24/23 | +28.25 (1.6) | -5.78 (-0.9) | 11.87/3.26 | +16.38 (0.96) | -9.04 (-1.40) | | | -0.27 (0.0) | 0.63/-1.06 | |
| H1roll XTI w30 | 24/22 | +34.73 (1.9) | -5.94 (-0.7) | 11.60/3.22 | +23.13 (1.27) | -9.16 (-1.01) | | | -6.03 (-0.7) | 0.83/-0.77 | |
| H1roll XNG w15 | 22/35 | +22.37 (2.1) | -0.51 (-0.1) | 14.7/37.7 | +7.65 (0.71) | -38.25 (-4.08) | | | | 0.46/-3.10 | |
| H1roll XNG w30 | 26/39 | +16.45 (1.3) | +6.85 (0.6) | 14.6/39.0 | +1.81 (0.15) | -32.16 (-2.59) | | | | 0.10/-1.97 | |
| H1abs USTEC w15 / w30 | 53/92, 52/90 | +4.98 (1.5) / +3.45 (0.9) | +1.50 (0.9) / +3.14 (1.4) | ~1.7/0.7 | +3.31 (0.99) / +1.76 (0.45) | +0.77 (0.47) / +2.41 (1.08) | | | | 0.53/0.36, 0.24/0.82 | |
| H1abs US500 w15 / w30 | 7/18 | +18.72 (1.0) / +12.49 (0.6) | +1.14 / +2.14 | 2.8/0.5 | +15.93 (0.84) / +9.77 (0.45) | +0.62 / +1.62 | | | | 0.45/0.12, 0.24/0.25 | |
| H1abs US30 w15 / w30 | 16/12 | +13.52 (1.6) / +14.62 (1.4) | +3.22 / +3.66 | 1.4/0.3 | +12.07 (1.39) / +13.19 (1.27) | +2.90 (0.64) / +3.35 (0.61) | | | -1.64 / -9.02 | 0.74/0.48, 0.68/0.47 | |
| H1abs US2000 w15 / w30 | 4/5 | | -17.6 / -16.7 | | +2.97 / -3.94 | -19.39 (-2.21) / -18.59 (-1.98) | | | | | |
| H1abs XAU w15 / w30 | 2/0 | +16.10 (3.1) / +14.60 (2.2) | no trades | 1.6 | +14.47 (2.84) / +12.95 (1.98) | n/a | | | | 1.52 / 1.06 | -0.38 (-0.3) / +4.43 (2.4) |
| H1abs XAG w15 / w30 | 6/11, 5/11 | +18.56 (2.1) / +38.07 (3.2) | -11.72 (-4.3) / -10.65 (-2.8) | 3.9/4.7 | +14.65 (1.65) / +34.37 (2.94) | -16.42 (-6.09) / -15.23 (-4.04) | | | | 0.89/-4.62, 1.58/-3.06 | +6.94 (1.7) / +10.32 (1.7) |
| H1abs XTI w15 / w30 | 34/40 | +22.48 (1.8) / +32.54 (2.4) | -0.32 / -2.57 | 11/3.4 | +11.17 (0.92) / +21.58 (1.62) | -3.75 (-0.81) / -6.00 (-1.03) | | | | 0.61/-0.62, 1.07/-0.78 | |
| H1abs XNG w15 / w30 | 88/165 | +6.56 / +4.87 | +10.58 (3.1) / +12.99 (2.7) | 13/40.5 | -6.54 / -8.06 | -29.97 / -27.55 | | | | <0 | |
| H2size (8 targets, all days, w15) | 124-249 | USTEC +1.81 (1.3), US500 +0.85, US30 +1.59, US2000 +1.98, XAU +1.24 (3.6), XAG +3.58 (4.6), XTI +5.66, XNG +5.20 | USTEC +0.62, US500 +0.52, US30 -0.46, US2000 -0.05, XAU +0.62 (1.7), XAG -2.40 (-3.1), XTI +1.27, XNG +8.93 | | best +0.60 (US30, t 0.47) | all <= -0.01 | | | | <= 0.25 | XAU -0.49, XAG -1.65 |
| H3rev (fade to next 10:00 NY) | 21-29 | US500 +24.2 (1.5), USTEC +12.8 (1.0), others <= +10.7 or < 0 | US500 -3.6, USTEC -2.1, XAU +19.5 (2.2), others < 0 or noise | 2-45 | best US500 +19.84 (1.26) | best XAU +18.48 (2.09), but XAU IS -8.18 | | | | <= 0.68 IS | XAU +0.43 |
| H4vix US500 w15 / w30 | 23/22, 24/20 | +1.88 (0.5) / -2.81 (-0.6) | -4.82 (-1.8) / -0.28 | 1.7/0.5 | +0.19 (0.05) / -4.48 (-0.97) | -5.29 (-1.98) / -0.74 | | | | 0.02/-1.50 | |
| H5 pooled IDX (4 indices, H1roll w15) | 40/49 days | +2.83 (0.7) | +1.97 (0.9) | 1.8/0.9 | +0.99 (0.25) | +1.07 (0.52) | +0.08/+0.62 | -1.49/-0.49 | -1.77 | 0.14/0.39 | |
| H5 pooled ALL (8 targets) | 80/113 days | +8.27 (3.3) | -0.59 (-0.2) | 4.6/11.6 | +3.65 (1.45) | -12.23 (-3.97) | | | | 0.78/-3.02 | |
| info: XBR with the UCO/SCO dose | 26/23 | ~0 | < 0 | 9.7/2.5 | -9.49 / -10.35 | -7.16 / -5.39 | | | | | |
| X1 JP225 OSE close w15 (1570 / 1357 dose) | 23/28 | +6.69 (1.8) | +0.34 (0.2) | 3.58/1.78 | +3.11 (0.87) | -1.43 (-0.66) | +1.32/-2.32 | +2.30/-4.10 | -2.79 | 0.47/-0.50 | |
| X1 JP225 TSE close w15 | 24/29 | +2.26 (1.0) | -0.01 (0.0) | 3.45/1.71 | -1.18 (-0.54) | -1.72 (-0.87) | | | -3.65 | -0.29/-0.66 | |

Years > 0 (IS + VAL): USTEC w30 5/9; XAU w15 6/9; XAG w30 5/9; most others 2-5 of 7-9. Full per-year rows are in
`out/cells.pkl`.

**Dose-response slope** (information): OLS of the signed window mid on |S| / median, all days, w 15, in bp per unit.
- Indices: IS +0.4 to +1.9 (t 0.9-4.1); VAL -1.0 to +0.4 (t -1.2 to +0.5).
- XAU: +0.48 / +0.66 / +0.84 (t 2.3 / 4.5 / 3.1) in PRE / IS / VAL, the one slope that is positive in every era.
- XAG: +1.91 / +1.17 / -1.77 (t 4.9 / 4.6 / -3.7). XTI: +2.6 (t 2.6) IS, -1.8 VAL.

**Random-entry control** (300 seeds; random days and signal minutes in the era, side recomputed, same window and costs):

| cell | IS actual / random mean | beats | VAL actual / random mean | beats |
|---|---|---|---|---|
| USTEC w30 | +10.26 / -1.48 | 100 % | +11.49 / -0.39 | 100 % |
| US500 w30 | +10.87 / -1.50 | 100 % | +4.76 / -0.62 | 99 % |
| US30 w30 | +12.17 / -0.71 | 100 % | -0.47 / -0.81 | 58 % |
| XAU w15 | +2.34 / -1.52 | 100 % | +3.11 / -0.71 | 99 % |
| XAG w30 | +16.54 / -4.04 | 100 % | -8.11 / -4.59 | 17 % |

This control does not select big days, so beating it only says that big-dose days differ from average days. The
binding failures are the IS t and VAL sign.

**Chance:** 52 counted cells (50 single + 2 pooled), shared per-day sign flips, 1,000 draws.
- Max IS net t: p50 1.43, p95 2.74. Max |IS mid t|: p50 2.24, p95 3.31.
- Observed: silver w30 4.01 (p 0.001), silver w15 3.04 (p 0.025), silver abs w30 2.94 (0.031), gold abs w15 2.84
  (0.042), then gold abs w30 1.98 and gold roll w15 1.86 (p 0.20-0.25).
- The beyond-chance cells are silver, and silver reverses in VAL.

## P1 (post hoc): does Γ/DOI add to |z|?
Top-decile |z| days (round 13's definition) split by Γ/DOI above or below its rolling median; mid bp (t):

| target, w | IS high Γ | IS low Γ | IS interaction t | VAL high Γ | VAL low Γ | VAL interaction t |
|---|---|---|---|---|---|---|
| USTEC 15 | +12.81 (1.6) n104 | -3.98 (-1.4) n42 | +1.1 | +3.12 (0.7) | -6.43 (-1.9) | +3.0 |
| USTEC 30 | +12.06 (1.6) | -12.39 (-1.1) | +0.8 | -0.47 | +1.91 | +3.0 |
| US500 15 | +14.50 (1.4) | +2.40 | -0.4 | +2.88 | -8.22 (-2.9) | +1.3 |
| US500 30 | +8.94 (1.4) | -0.45 | 0.0 | +3.47 | -5.15 | +2.1 |
| US30 15 | +23.14 (1.7) | -0.88 | +5.1 | +0.31 | -3.29 (-1.8) | +1.3 |
| US30 30 | +7.42 | +3.21 | +3.6 | +5.21 | -9.01 (-2.8) | +1.9 |
| US2000 15 | +7.00 | +1.75 | +2.1 | -5.36 | -9.38 (-2.1) | +1.7 |
| XAU 15 | +3.31 (1.5) | +5.87 (4.8) | -4.0 | +3.38 (2.2) | +3.07 (1.9) | +1.0 |
| XAG 30 | +31.12 (3.4) | +7.11 (2.3) | +6.9 | -1.04 | -4.26 | +0.1 |
| XTI 30 | +33.94 (1.4) | +6.36 | +7.7 | -24.07 (-1.2) | +8.45 (1.5) | -0.3 |

- In the indices, the low-Γ top-|z| days carry round 13's VAL reversal: US500 -8.2, US30 -9.0 bp. The high-Γ days do
  not reverse.
- That is the dose mechanism's sign in VAL. It is post hoc and too small to trade: the high-Γ halves are +0.3 to
  +5.2 bp at t <= 0.7 in VAL.

## What this says
- **Measuring the flow did not make it bigger where it matters.** The LETF dose is a real share of the futures market
  only in Nasdaq and Dow. There it does not lift the follow-into-the-close effect above round 13's level in IS once
  2020 is removed.
- **Where earlier rounds saw effects (gold, silver, oil), the measured ProShares dose is far too small to be the
  cause.** The scale is 0.005-0.07 % of OI per 1 % move. Gold's settlement momentum does not rise with the dose (IS
  interaction t -4.0). The round-12 gold DEMO rule is therefore not an LETF rule; something else moves gold into the
  settlement.
- **The one sign consistent with the mechanism is VAL-only.** USTEC, from 2022, as the Nasdaq dose doubled relative to
  OI:
  - the top dose decile follows the day's move into the last 30 minutes (+11.5 bp, t 2.8);
  - the dose interaction is t +3.0;
  - but IS (2016-21) is t 1.38 with 2020, and 0.9 without it.
  - By the bars this is not a candidate. Declared now, it could only be tested on data after 2026-09-24, with its
    rule fixed as H1roll USTEC w30.
- **Next-morning reversal (H3) and VIX-ETP vega rebalancing (H4) have nothing.**
- **The Nikkei LETFs, the world's largest relative to their market, do not scale the OSE quarter-hour effect**, which
  has decayed (round 13).

## Directions that need the user
1. **Forward log of H1roll USTEC w30 on data after 2026-09-24** (rule fixed in HYPOTHESES_E.md: ProShares dose /
   NQ dollar OI, rolling top decile, follow from 15:30 to 16:00 ET). About 25 trades a year, so 1.73 years give 43.
   - At the VAL size (Sharpe 0.24 per trade) the forward t would be ~1.6 after 2 years; DEMO at most.
   - Value: low (LIVE probability < 2 %). Its IS failure is the 2020 tail; the VAL strength may be the 2022 bear
     market.
2. **Direxion daily shares** (TNA/TZA, SPXL/SPXS, SOXL; the site answers 403 to this Mac). It would roughly double the
   S&P and Russell doses.
   - Value: low. US500 / US2000 show no dose effect at the present scale, and Russell's IS is flat.
3. **Credit Suisse ETN shares (UGAZ/DGAZ, TVIX/XIV) from a paid archive.** They are the large natgas and VIX doses of
   2016-20. XNG's IC cost (15-40 bp at 14:30 ET) kills any natgas rule anyway. Value: very low.

## Scripts and outputs
Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/080b5cdb-1558-4c25-a0ea-645ed76134b5/scratchpad/r34/E/`:

| file | what it does |
|---|---|
| scripts/fetch.py | polite fetcher and log |
| scripts/parse_ps.py, parse_cot.py, parse_nf.py | parsers (`-I`, 2024-12-31 cut) |
| scripts/mech_check.py | leverage and shares-lag checks -> out/mech_check.txt |
| scripts/build.py | per-day dose and prices -> out/table.pkl |
| scripts/analyze.py | 52 cells, slopes -> out/analyze_out.txt, out/cells.pkl |
| scripts/controls.py | chance null, random control, P1 -> out/controls_out.txt |
| scripts/jp.py | X1 -> out/jp_out.txt |
| web/requests.log | fetch log |
