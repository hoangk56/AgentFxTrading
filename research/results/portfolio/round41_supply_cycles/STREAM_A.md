# Round 41 stream A: sovereign auction supply cycles (US all tenors, JGB, Bund), 2026-10-30

Hypotheses: [HYPOTHESES_A.md](HYPOTHESES_A.md) (F1-F3 declared 04:38 UTC with three mechanical amendments before any
return; A2 declared 04:46 after F1-F3 were graded). HOLD stayed closed: the requests stopped at 2024-12-31 where the
source allowed it, 2025-26 rows in the JGB and Bund files were dropped at parse (asserted), IC prices cut at load.

## Answer
**No LIVE candidate. One cell meets the DEMO numbers, and I don't recommend registering it.** Across 252 declared
cells, scheduled sovereign supply moves no currency, index or gold over 1-5 days on its declared side net of IC
costs. That holds for every tenor, DV01-weighted, for the JGB and Bund calendars and for result surprises. The one
cell that meets the numbers is A2: short EURUSD on US coupon-auction mornings, 10:05-12:55 ET. It has net +2.17 bp,
IS t 2.51, and VAL +0.33 (t 0.25). Its IS t is at the chance median, and the pre-declared PRE era has the opposite
sign (t -2.20). It is written up as a draft and not registered:
[PREREG_DRAFT_A_us_auction_morning_eurusd.md](PREREG_DRAFT_A_us_auction_morning_eurusd.md).

## Sources (all fetched 04:31-04:34 UTC: 16 requests incl. 5 failed probes (bad URL / HTTP 400 / 404), ~2.7 MB; log in web/requests.log; HYPOTHESES' "8 requests" undercounted the probes)
| source | span used | rows | notes |
|---|---|---|---|
| fiscaldata.treasury.gov `auctions_query` (Note, Bond) | 2003-06..2024-12 (request stops at 2024-12-31) | 1,776; 1,621 used 2004-24 after dropping FRNs | offering amount, yields, bid-to-cover, primary-dealer take, closing time; no when-issued yield, so no US tail |
| MoF `Auction_Results_for_JGBs.xls` | 2004..2024 (file runs to 2026, dropped at parse) | 1,358 (2004-24) | 2/5/10/20/30/40Y, 10Y linker, GX5/GX10; tail = average - lowest price (40Y single-price: no tail); BIFF8 read with a stdlib parser |
| Finanzagentur `emissionshistorie_en.xlsx` | 2004..2024 (file runs to 2026, dropped at parse) | 1,088 (2004-24) | "Auc" + multi-ISIN "M-A" (most 15Y / 30Y supply since 2022); Bubills, secondary sales and syndications out |
Not used: when-issued yields (paid), MoF liquidity-enhancement auctions (off-the-run), euro-area non-German auctions
(the side of "higher BTP yields" for EUR is not fixed by the mechanism).

## Power arithmetic (before returns; in HYPOTHESES)
Auction days per year (2016-24): US ~80-93, JP ~70, DE ~53-81, so ~210 a year. That is still only ~50 independent
weeks per country. LYZ's 2-3 bp concession maps to ~6-12 bp of USDJPY per window against a 5-day sd of ~120 bp. LIVE
needed a daily Sharpe of 0.14 per pair, 4-8x the literature size. DEMO was reachable only at the top of the range. F3
and A2 (intraday) needed ~3 bp net per FX trade for LIVE, so DEMO at most.

## Results
Net bp per trade (t on the book's daily net, clustered by UTC day; overlapping trades split at UTC midnights). PRE
covers FX and XAU only, at mid. Random = share of 200 random-day seeds with a lower mean net. Power = the lower of
per-trade and per-day Sharpe x sqrt(expected HOLD units), at the VAL size.
| hypothesis | PRE mid (t) | IS mid / net (t) | VAL mid / net (t) | VAL/IS | random IS / VAL | power (VAL size) | verdict |
|---|---|---|---|---|---|---|---|
| **F1 primary**: CYC (3-day concession + 3-day reversal), DV01-sized, all 10 pairs | +4.3 (1.87) | -2.2 / **-5.6 (-2.90)** | +3.0 / -0.1 (-0.05) | n/a | 46 / 86 % | -0.04 | none (week sign-flip null p 0.001 on the wrong side) |
| F1 PRE-L sized, all pairs | -1.1 (-0.33) | -7.4 / -10.1 (-2.82) | -0.6 / -1.6 (-0.41) | | 55 / 86 % | -0.46 | none |
| F1 POST3 sized, all pairs (reversal) | +9.5 (2.89) | +3.2 / -0.8 (-0.20) | +5.5 / +0.6 (0.13) | | 41 / 70 % | 0.10 | none (PRE-only at mid) |
| F1 best symbol cell: PRE2 sized US -> long USDJPY | +0.3 (0.05) | +8.8 / +7.8 (1.80) | +12.9 / +14.2 (2.34) | 1.8 | 97 / 56 % | 1.78 | none (IS t < 2; VAL = USDJPY carry; round 22 R4 relative) |
| F1 JP pool, JGB auctions -> JPY up, JP225 down | +1.7 (0.43) | -9.3 / -12.1 (-2.84) | -6.8 / -10.4 (-1.71) | | 20 / 82 % | -1.81 | none, wrong sign (JP225 short loses the equity drift) |
| F2 heavy-week reversal (WPOST), all pairs | +8.8 (2.10) | +8.9 / +4.9 (0.91) | +10.8 / +5.9 (0.79) | 1.2 | 81 / 70 % | 0.60 | none |
| F2 heavy-week reversal, JP pool | -0.7 (-0.09) | +20.8 / +16.5 (1.48) | +30.3 / +27.9 (1.72) | 1.7 | 97 / 84 % | 1.31 | none (IS t < 2; PRE 0) |
| F2 named weeks pre (US refunding / JP super-long / DE long), all pairs | -8.2 (-1.47) | -5.1 / -7.3 (-1.43) | -1.0 / -2.6 (-0.39) | | 52 / 88 % | -0.37 | none |
| F3 surprise H3 (+15 min -> +3 h), all pairs | -1.3 (-1.47) | +0.2 / -1.0 (-1.02) | +2.7 / +1.8 (1.50) | | 52 / 99 % | 1.14 | none (IS 0; results priced in 15 min) |
| F3 surprise D1, all pairs | -3.0 (-1.15) | +2.5 / +0.7 (0.28) | -3.4 / -5.0 (-1.40) | | 84 / 10 % | -1.32 | none |
| A2 primary: AM concession, all auction days, all pairs | -0.04 (-0.08) | +0.23 / -0.91 (-1.50) | +0.66 / -0.13 (-0.14) | | 99 / 70 % | -0.14 | none |
| A2 PM reversal, all pairs | -0.05 (-0.12) | -0.44 / -1.59 (-3.46) | +0.11 / -0.68 (-1.03) | | 0 / 5 % | -0.92 | none (USD keeps rising after US auctions in IS) |
| **A2 AM all, US -> short EURUSD** | -0.74 (-0.82); net -2.00 (-2.20) | +2.80 (3.25) / **+2.17 (2.51)** | +0.95 (0.71) / +0.33 (0.25) | 0.15 | 100 / 64 % | 0.19 | **meets DEMO numbers, at chance, PRE opposite: draft only** |
| A2 AM all, US -> long USDJPY | +0.05 (0.06) | +1.80 (2.08) / +1.08 (1.25) | +3.26 (2.72) / +2.58 (2.15) | 2.4 | 99 / 99 % | 1.63 | none (IS t < 2) |
| A2 AM top, US pool (4 pairs) | +1.9 (1.05) | -0.78 / -1.91 (-1.35) | +4.47 / +3.80 (1.84) | | 70 / 100 % | 1.85 | none (IS < 0) |

x1.5 spread and +1 min change the FX cells by < 0.2 bp (cost is mostly the 0.6 bp commission). Results without
2020-03/04 are in out/grade.json and out/a2.json and change no verdict (the draft cell's IS: +1.77, t 2.19).

## Cells tried and chance
- F1 112 (80 symbol + 32 pooled), F2 56, F3 28: 196 cells. max |N| of 196 has median 2.91 and p95 3.64. Best positive
  IS t 1.80; largest |t| 3.53 (F1 PRE2 top JP -> short JP225, wrong sign). 0 cells with IS t >= 2 and VAL > 0. Mean
  IS t is -0.67: costs and the short-equity legs make most cells negative.
- A2 56 cells (max |N| median 2.50, p95 3.32): one cell with IS t >= 2 and VAL > 0 (the draft, IS t 2.51). Stream
  total 252 cells (median of the best-of-252 null 2.99).

## What this says
- **No multi-day concession at IC-tradable horizons.** Positioning into all-tenor DV01 supply loses its costs in
  every country. US -> USDJPY is the exception, and it is round 22's finding again (dollar up into US auctions in
  2016-24, flat or opposite in 2004-15, VAL = the 2022-24 carry: random windows beat it 44 % of the time). The equity
  legs (short US500 / JP225 / DE40 into supply) lose the equity drift on random days just as much. Turn-of-month
  overlap doesn't explain them: US windows almost never cross a month end.
- **Reversal after auctions** (POST3, WPOST) is positive at mid in PRE 2004-15 (+9.5 bp, t 2.89 pooled). It shrinks
  to +3 to +5 bp in 2016-24, which is below IC's 3-5 bp round-trip cost on a 3-day hold. JGB heavy-week reversal (JPY
  weaker after heavy JGB weeks: +16.5 / +27.9 bp net) is the largest effect but sits at IS t 1.48, and PRE is 0.
- **Result surprises** (US dealer take / bid-to-cover, JGB and Bund tail / cover) leave no drift after 15 minutes.
  This matches rounds 25-26.
- **US auction-day mornings, 2016-24 only:** the dollar rises against EUR and JPY by ~3 bp more than on non-auction
  mornings at mid. It fits the intraday-concession story, but it is absent in 2004-15 (EURUSD 11 of 12 years
  negative), and it continues rather than reverses in the afternoon. With 252 cells it is at the chance level.
- Correlation of the draft cell with C3 (daily): +0.02.

## Pitfalls for later rounds
- MoF's JGB history is BIFF8 `.xls` (no xlrd in the venv): `scripts/xls.py` is a 150-line stdlib reader (OLE + SST
  with CONTINUE). The Finanzagentur file is xlsx (stdlib zipfile + XML). Both include 2025-26 rows: cut at parse.
- The Bund history marks multi-ISIN auctions "M-A": filtering on "Auc" drops nearly all 15Y / 30Y supply after 2022.
  "OH" = secondary-market sales, "Syn" = syndications.
- fiscaldata `auctions_query`: `security_type:in:(Note,Bond)` works. TIPS are flagged by `inflation_index_security`,
  FRNs by `floating_rate`. `closing_time_comp` is null before 2008. It reads 11:30 AM on early-close days. A field
  name that doesn't exist makes the API answer 400.
- With the user's 5-day limit read as 120 h, "business day -5" windows always break it; the longest feasible pre
  window is 3-4 business days.
- US500's 16:15-16:30 ET break swallows exits at 16:15. Exits fall back to the last bar within 20 minutes.

## Directions that need the user
| direction | value |
|---|---|
| When-issued yields at the US bid deadline (Bloomberg / Tradeweb, paid): tail-based surprises | LIVE < 1 %, DEMO ~1 % |
| A venue without the 0.6 bp FX commission (the PRE-era post-auction reversal is ~3-5 bp mid in 2016-24) | LIVE ~1 %, DEMO ~2 % |
| Dealer positions in Treasuries (NY Fed primary-dealer statistics are free weekly; only useful at weekly frequency, so LIVE impossible from the count) | DEMO < 1 % |

## Scripts and outputs
In `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r41/A/`:
- `scripts/fetch.py` (logged fetches), `xls.py`, `xlsx.py` (readers), `parse.py` -> `out/auctions.json` (cut at
  2024-12-31), `events.py` -> `out/events.pkl` (auction days, DV01 z, weeks, surprise W).
- `lib.py` (prices with the HOLD cut, clocks, windows, fills, costs, daily pieces), `gen.py` -> `out/trades.pkl`,
  `out/tables.pkl`, `grade.py` -> `out/grade.json`, `out/grade.txt`, `summ.py`, `null_primary.py`.
- `a2.py` -> `out/a2.json`, `out/a2.txt`; `a2_post.py` -> `out/a2_post.txt` (post hoc diagnostics, information only).
- Downloads in `web/ust/`, `web/mof/`, `web/bund/`; request log `web/requests.log`.
