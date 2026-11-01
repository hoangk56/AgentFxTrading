# Round 41: sovereign auction supply cycles (US all tenors, JGB, Bund); US equity issuance supply, 2026-10-30

Brief: [round41_supply_cycles/BRIEF.md](round41_supply_cycles/BRIEF.md). Same LIVE / DEMO bars as rounds 25-40. HOLD
(2025-01..2026-09) stayed closed in both streams (Treasury request to 2024-12-31, JGB / Bund 2025-26 rows dropped at
parse with an assert, EDGAR index files 2015-24 only, IC cut at load; disclosures in STREAM_A.md and STREAM_B.md).
Both pulls were small (A ~4 minutes, B 26 s).

## Answer
No LIVE candidate; one DEMO-number cell, not registered. Scheduled bond supply (DV01-weighted, all tenors, three
countries), heavy auction weeks and result surprises move no currency, index or gold on the declared side over 1-5 days
after IC's cost; result surprises are priced within 15 minutes. EDGAR equity issuance is a hot-market indicator: indices
rise after heavy-issuance days.

## Streams
| stream | tested | verdict | detail |
|---|---|---|---|
| A | US Treasury coupon / TIPS (1,621), JGB (1,358), Bund (1,088) auctions 2004-24: DV01-sized concession into the auction and reversal after (F1), heavy / named auction weeks (F2), result surprise from 15 min to next day (F3), then auction-day morning / afternoon FX (A2, declared after F1-F3 failed); 10 pairs + XAU + US500 / JP225 / DE40; PRE 2004-15 on Dukascopy; 252 cells | **none**: F1 primary net IS -5.6 (t -2.90); best F1 cell US supply -> long USDJPY IS t 1.80 / VAL 2.34 repeats round 22 (VAL is carry); post-auction reversal real at mid only in PRE (+9.5, t 2.89), +3-5 bp since 2016 vs 3-5 bp cost; A2 US morning -> short EURUSD met the DEMO numbers (net IS +2.17, t 2.51) but VAL +0.33 (t 0.25), PRE net t -2.20 (11 / 12 years negative), IS t at the best-of-56 null median: draft not registered | [STREAM_A.md](round41_supply_cycles/STREAM_A.md), [HYPOTHESES_A.md](round41_supply_cycles/HYPOTHESES_A.md), [PREREG_DRAFT_A_us_auction_morning_eurusd.md](round41_supply_cycles/PREREG_DRAFT_A_us_auction_morning_eurusd.md) |
| B | SEC EDGAR quarterly full index 2015-24 counted by accession: IPO (424B4 / B1), shelf takedowns (424B5), secondaries (424B7), all equity, issuer tender offers (SC TO-I), lock-up expiries, EFFECT notices, settlement days, weekly supply -> US500, USTEC, US2000 (US30 control); entry next open / 04:00 ET after the 22:00 ET acceptance limit; 162 cells | **none**: short side loses (34 / 144 cells IS t <= -2 against it; corr(supply z, prior 20-day return) +0.12 / +0.17); best buyback SC TO-I -> long USTEC h3 net IS +27.8 (t 2.16) / VAL +16.9, beats only 76 % of random longs (long drift), best-of-144 p 0.35. Diagnostic slope at mid ~-5 bp per sd IS, ~-1-5 VAL (HOLD power ~1.2 / 0.3 before cost) | [STREAM_B.md](round41_supply_cycles/STREAM_B.md), [HYPOTHESES_B.md](round41_supply_cycles/HYPOTHESES_B.md) |

Correlation with C3: A2 draft cell +0.02 daily; others not computed.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Sovereign auction supply (US all tenors, JGB, Bund; DV01-weighted concession / reversal, heavy weeks, result
  surprises, auction-day sessions) -> FX, gold, indices at 15 min to 5 days.
- Aggregate EDGAR equity issuance (IPO, shelf, secondary, effectiveness, settlement day, weekly), issuer tender
  offers and lock-up expiries -> US indices at 1-3 days.

## Pitfalls
- MoF `Auction_Results_for_JGBs.xls` is old binary .xls (stdlib reader `xls.py` in the stream A scratchpad); the Bund
  history marks multi-ISIN auctions "M-A" (most 15Y / 30Y supply from 2022); fiscaldata returns 400 for an unknown field
  and `closing_time_comp` is null before 2008.
- A "business day -5" window breaks the 5-day (120 h) hold limit.
- EDGAR master.gz: count by accession (co-registrant rows repeat per CIK); SC TO-I is mostly funds / BDCs; 424B2 is
  bank notes, 424B5 also carries corporate debt; SPAC IPOs file 424B4. The full 2015-24 index pull takes ~30 s.
- US500 has a 16:15-16:30 ET break: exits timed at 16:15 fall into it.

## Directions that need the user
| direction | value |
|---|---|
| A venue without the 0.6 bp FX commission (post-auction reversal ~3-5 bp mid since 2016) | LIVE ~1 %, DEMO ~2 % |
| Paid when-issued yields (US tail surprises); paid new-issue data (Dealogic / SDC) | LIVE < 1 %, DEMO ~1 % each |
| Crawling EDGAR per-filing documents (acceptance times, sizes, 8-K buybacks; hours of polite crawling) | LIVE < 1 %, DEMO ~1 % |

## State after round 41
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 42 opens next.
