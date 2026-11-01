# Round 40, stream G: hypotheses (GDELT news event and tone flows)

Declared 2026-10-29 14:08 UTC (`date -u`), before any GDELT series was joined to a price. Only file sizes, the
column layout and one IS day's world totals (2016-06-01) had been looked at. Sides, aggregation, thresholds, horizons
and books below are fixed; nothing is changed after returns are seen. Post-hoc additions, if any, go in a separate
section marked as such with their own time.

## Source and why not the 15-minute files
- Measured 2026-10-29 14:01-14:05 UTC (HEAD / one GET each, logged in the scratchpad `web/requests.log`):
  - GDELT 2.0 15-minute Events export: 95-270 KB per file; 2015-02..2024-12 is ~345k files, ~60 GB. At the network
    rule of >= 1 s between requests to one host that is >= 96 h of sequential requests: not feasible this round.
  - GDELT 1.0 daily GKG: 78 MB per day (2016-06-01), ~285 GB for 2015-24: not feasible; GKG is dropped (the Events
    `AvgTone` is already the mean tone of the documents mentioning each event).
  - GDELT 1.0 daily Events export (`http://data.gdeltproject.org/events/YYYYMMDD.export.CSV.zip`): 4,289 files
    2013-04-01..2024-12-31 (none missing from 2015; 4 missing in 2014), 40 GB. Same CAMEO coding and fields
    (QuadClass, GoldsteinScale, NumArticles, AvgTone, ActionGeo, actor countries, DATEADDED). **This is the source.**
    Every file is aggregated on the fly into a compact per-day array and the zip is deleted; no raw rows are kept.
- No file stamped after 20241231 is requested. Rows whose DATEADDED is not the file's own day are dropped (and counted).
- Publication: the file for day D carries Last-Modified D+1 07:00:19-07:29:36 UTC on the three files probed (2014, 2016,
  2020). A sample of ~60 HEAD requests across 2015-24 will be taken after the bulk download to check the clock; the
  entry clock below is 08:00 UTC and is moved later (declared before returns) if any sampled file is later than 07:45.
- What is lost against the 15-minute stream: any sub-day timing test. The brief allows daily signals; the cost is that
  everything that happened on day D before 08:00 UTC D+1 is already in the entry price (by design: we test day 1+).

## Aggregation (per DATEADDED day D; declared before download, coded in scripts/agg.py)
Per key, sums over events: count, NumArticles, NumMentions, NumSources, sum(NumArticles x AvgTone),
sum(NumArticles x GoldsteinScale), sum(AvgTone); split by QuadClass (1-4) and all; all events and root events only.
Keys: ActionGeo country (FIPS 10-4), actor country (distinct of Actor1 / Actor2 CountryCode, CAMEO), world, and seven
lat/long boxes on ActionGeo (HORMUZ 25.5-27.5 N 55-57.5 E; PGULF 24-30.5 N 47.5-56.5 E; BABELM 11.5-13.5 N 42.5-44.5 E;
REDSEA 12.5-28 N 32.5-43.5 E; SUEZ 29.8-31.4 N 32.2-32.7 E; MALACCA 1-6.5 N 95.5-104 E; BOSPORUS 40.9-41.3 N 28.9-29.2 E).

Signals (all "geo" = ActionGeo country, all events, all quads unless said):
- TONE_c = sum(art x tone) / sum(art); GOLD_c = sum(art x Goldstein) / sum(art).
- VOL_c = articles of c / world articles (attention share); CONF_r = QuadClass-4 articles in region r / world articles.
- Blocks: the entry on weekday E uses the files of the calendar days after the previous weekday up to E-1 (Monday:
  Fri + Sat + Sun pooled as sums; Tue-Fri: the previous day). Pooled ratios for TONE / GOLD, mean daily share for
  VOL / CONF.
- z = (block value - mean) / sd of the daily values over the 60 calendar days before the block's first day (>= 40
  valid days). VOL and CONF in logs. FX pairs use the relative series TONE_base - TONE_quote (daily), z of the block
  difference against the trailing 60-day daily differences. 30 / 90-day windows are reported for robustness only,
  never for selection.

Country groups (FIPS): USD = US; EUR = GM + FR + IT + SP + NL + BE pooled; JPY = JA; GBP = UK; AUD = AS; NZD = NZ;
CAD = CA; CHF = SZ; CN = CH + HK (for HK50). Index legs: US -> US500, JA -> JP225, UK -> UK100, GM -> DE40, AS -> AUS200,
CN -> HK50. FX legs (relative signal base - quote): EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCAD, USDCHF, USDJPY, EURJPY,
GBPJPY, AUDJPY. Global legs: WORLD tone -> BTCUSD (same sign), XAUUSD (opposite sign: bad world news -> gold up).

## Clock, horizons, costs
- Entry at the 08:00 UTC M1 bar close of weekday E (latency variant: 08:01 for entry and exit). Exits at 08:00 UTC:
  C1 = E -> next weekday; C3 = E -> 3rd weekday after E; R = enter the next weekday after E, exit 3 weekdays later.
  Every hold is <= 5 calendar days and <= 3 overlapping positions per leg.
- Executable cost: half the actual IC spread at the entry and exit minute, x1.5 variant; commission 0.6 bp round trip
  for FX and metals; swap per rollover from research/swing/rates.py swap_frac_at (indices, energies, BTC by the
  research model, triple on Wednesday for FX / metals and Friday for indices, energies, BTC). IC M1 cut at
  ts < 1735689600000 at load. PRE (2013-07..2015-12, FX and XAU only, Dukascopy M1): mid, IC 2016-17 median spread at
  08:00 + 0.6 bp.
- Eras: IS 2016-2021, VAL 2022-2024, PRE 2013-07..2015-12 where Dukascopy has the symbol. HOLD closed.

## Families, sides and cells (58 cells; the unit of a cell is an equal-weight book over its legs)

### G1. Country tone / Goldstein shocks (30 cells)
- Mechanism: slow diffusion of news to inattentive investors (Hong & Stein 1999; Hong, Lim & Stein 2000; DellaVigna &
  Pollet 2009) gives continuation of aggregate tone shocks; media pessimism as noise-trader sentiment (Tetlock 2007)
  gives a day-1 move in the tone's direction followed by reversal within the week.
- What the papers imply (sides fixed from them):
  - Continuation at day 1: Tetlock 2007 (WSJ "Abreast of the Market" pessimism, 1 sd -> -8.1 bp next-day DJIA,
    1984-99), Garcia 2013 (NYT columns 1905-2005: ~3 bp per sd in expansions, ~12 bp in recessions next day),
    Tetlock, Saar-Tsechansky & Macskassy 2008 (firm news, continuation, no reversal), Heston & Sinha 2017 (daily news
    -> 1-2 days; weekly aggregated news -> continuation for weeks).
  - Reversal at days 2-5: Tetlock 2007 (the day-1 pessimism effect reverses within a week), Garcia 2013 (reverses by
    day 4), Da, Engelberg & Gao 2015 (FEARS: low same-day returns, reversal over the next 2 days).
- Rule: z > k -> long the asset (base currency for FX), z < -k -> short, for C1 and C3 (continuation); R takes the
  opposite side, entering one weekday later (reversal).
- Cells: signal {TONE, GOLD} x k {1.0, 2.0} x horizon {C1, C3, R} x book {IDX (6 legs), FX (10 legs)} = 24, plus the
  GLOBAL book (BTC, XAU) on world TONE only: k {1.0, 2.0} x {C1, C3, R} = 6.
- Control (reported for every G1 cell that is positive in IS): OLS of the leg return on the continuous z with the
  asset's own previous-day (E-1 -> E 08:00) and previous-5-day returns as controls, day-clustered; tone partly
  reports the day's move, so a tone "effect" that is just 1-day momentum / reversal does not count.

### G2. Material-conflict intensity in oil producers and shipping lanes -> oil and gold long (16 cells)
- Mechanism: conflict raises the supply-risk premium in crude and the haven demand for gold (Kilian 2009 supply
  shocks; Caldara & Iacoviello 2022 geopolitical-risk acts; Baur & Smales 2020 gold and geopolitical risk); the test
  is whether aggregate intensity carries past day 0 (rounds 26 and 38 H found single disruptions priced in minute 1).
- Regions, from official lists: PROD = every country that was an OPEC member in 2013-24 (opec.org member list:
  Algeria, Angola, Congo, Ecuador, Equatorial Guinea, Gabon, Iran, Iraq, Kuwait, Libya, Nigeria, Qatar, Saudi Arabia,
  UAE, Venezuela) plus the non-OPEC signatories of the OPEC+ Declaration of Cooperation (Azerbaijan, Bahrain, Brunei,
  Kazakhstan, Malaysia, Mexico, Oman, Russia, Sudan, South Sudan); FIPS AG AO CF EC EK GB IR IZ KU LY NI QA SA AE VE AJ BA
  BX KZ MY MX MU RS SU OD. LANES = the EIA "World Oil Transit Chokepoints" lanes with conflict exposure, as the declared
  boxes PGULF + REDSEA + SUEZ + MALACCA + BOSPORUS (Hormuz and Bab el-Mandeb lie inside PGULF / REDSEA; Danish straits,
  Panama and the Cape are left out: no material conflict to measure).
- Signal CONF_r (log share of world articles that are QuadClass-4 events in r), z vs trailing 60 days; rule z > k ->
  long; no short side.
- Cells: region {PROD, LANES} x k {1.5, 2.5} x horizon {C1, C3} x target {XBRUSD, XAUUSD} = 16. XTIUSD is reported as
  a duplicate check of XBR, not a cell. Energies from 2018 (IS = 2018-21).

### G3. News-volume surprise (attention) for a country (12 cells)
- G3a, attention-amplified reversal (Barber & Odean 2008 attention-driven buying and its reversal; Seasholes & Wu
  2007; Da, Engelberg & Gao 2015): when VOL z > k for the country, side = minus the sign of the asset's previous-day
  return (E-1 08:00 -> E 08:00). IDX book (the country's index); FX book (pair active when max(z_base, z_quote) > k,
  side minus the sign of the pair's previous-day return). k {1.5, 2.5} x {C1, C3} x {IDX, FX} = 8 cells.
- G3b, attention risk premium (Andrei & Hasler 2015: attention raises the required return; spikes in country news
  volume are mostly bad-news days): VOL z > k -> long the country's index. k {1.5, 2.5} x {C1, C3} = 4 cells.
- Random controls for G3a recompute the side (minus the previous-day return's sign) at the random day.

## Statistics and bars
- Per cell: daily book series (mean net over active legs per entry day); mean bp, Newey-West t with lag = hold in
  days (C1: 1, C3 / R: 3) on the entry-day series; trade-level n, mean, per-trade Sharpe; year by year; with and
  without 2020-03/04; spread x1.5 and +1 minute variants; random-entry control (>= 200 seeds, same legs, counts,
  side mix and weekday mix, random entry days in the same era); best-of-58 sign-flip null (flip by entry day, shared
  by every cell and leg) on IS.
- Bars as research/PROMPT.md: LIVE = IS t >= 2.5, VAL >= 1.5, >= 2/3 years > 0, >= 95 % of random, power at the VAL
  size >= 3; DEMO = IS t >= 2.0, VAL > 0, >= 90 % of random; both positive at x1.5 and +1 minute.

## Event count and power arithmetic
To be appended below (with its own `date -u` time) from the signal series alone, before any return is computed.

## Addendum 1 (2026-10-29 14:23 UTC, before any return): publication clock, two more families
### Publication clock (from the HEAD sample, scratchpad out/lm_sample.tsv)
- Every sampled file from 2015-08 to 2024 carries Last-Modified D+1 07:00:06-07:01:02 UTC: the 08:00 UTC entry stands
  for IS and VAL.
- 2014 files: D+1 07:43-09:20 UTC; 2013 files were re-uploaded on 2014-02-15 (no original clock); several 2015-H1 files
  return no Last-Modified. PRE therefore uses a **10:00 UTC** entry / exit clock (10:01 for latency) on the same rules,
  and is flagged as only approximately point-in-time before 2014.

### G4. Bilateral tension (dyads; actor-country pairs, CAMEO) -> exposed assets (16 cells)
- Mechanism: aggregate conflict coverage between two named states is a geopolitical-risk shock (Caldara & Iacoviello
  2022: threats and acts); slow diffusion -> continuation in the exposed assets; side fixed by exposure, never by data.
- Signal: log(QuadClass 3 + 4 articles of the dyad / world articles), z vs 60 days, z > k -> trade; pooled dyads summed.
- Books (sides): US-CHN (D_CHN_USA): short AUDUSD, short AUDJPY, short HK50. RUS-UKR (D_RUS_UKR): long XBRUSD, long
  XAUUSD, short DE40. IRAN (D_IRN_USA + D_IRN_ISR + D_IRN_SAU): long XBRUSD, long XAUUSD. KOREA (D_PRK_USA + D_KOR_PRK +
  D_JPN_PRK): short USDJPY, short JP225.
- Cells: 4 books x k {1.5, 2.5} x horizon {C1, C3} = 16.

### G5. Domestic unrest (CAMEO root 14 "protest") -> that country's index and currency, short (8 cells)
- Mechanism: protest surges are political-risk news (Caldara & Iacoviello's country GPR; event-study evidence of
  equity losses around mass protests); continuation by slow diffusion.
- Signal: log(root-14 articles with ActionGeo in the country group / world articles), z vs 60 days; z > k -> short the
  country's index (IDX legs as G1) or its currency against USD (FX legs EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCAD long,
  USDCHF long, USDJPY long, i.e. the non-USD currency sold; USD protests are not traded in FX).
- Cells: k {1.5, 2.5} x {C1, C3} x {IDX, FX} = 8.

Total declared cells: 58 + 24 = 82. Nulls are reported for G1-G3 (58), G4-G5 (24) and all 82.
Dyad and root-14 keys were added to the aggregator at 14:22 UTC; the ~440 days aggregated before that are fetched
again for those keys only (same files, same cut).

## Event count and power arithmetic (2026-10-30 03:39 UTC, from the signal series and price availability only; no signal-conditioned return computed yet)
Output: scratchpad out/count_power.txt. HOLD = 1.73 years at the VAL rate. "Sh need" = per-trade net Sharpe for HOLD
power 3 (3 / sqrt(HOLD trades)); day units in brackets (book-days). "bp need" = that Sharpe x the legs' mean
unconditional sd for the hold (all weekdays 2016-24: 1 day ~45-75 bp FX, ~100-140 bp indices, 85 XAU, 258 XBR, 440 BTC).

| cells | trades / year (VAL) | HOLD trades (book-days) | Sh need trade (day) | bp need | bar reachable |
|---|---|---|---|---|---|
| G1 IDX k1 (C1 / C3 / R) | ~400 | ~690 (~360) | 0.114 (0.157) | 13 / 22 / 22 | LIVE only at the top of the literature size (Tetlock 2007 ~8 bp per sd, ~12 bp at a mean \|z\| of 1.5, before any decay) |
| G1 FX k1 | ~710 | ~1,230 (~390) | 0.085 (0.151) | 5 / 8.5 / 8.5 | LIVE in trade units, but 10 legs share USD / JPY: the day unit (0.15) is the binding one |
| G1 k2 (IDX / FX) | 65-125 | 110-215 (100-140) | 0.21-0.29 | 12-54 | LIVE needs 2-3x the literature size; DEMO reachable |
| G1 GLOBAL k1 / k2 | 140 / 25 | 245 / 44 | 0.19 / 0.45 | 50-210 | k1 LIVE needs ~50 bp a day on BTC / XAU: very unlikely; k2 DEMO at most |
| G2 (oil / gold on conflict) | 4-21 | 7-36 | 0.50-1.14 | 42-500 | **LIVE impossible** from the count; DEMO at most |
| G3a / G3b k1.5 | 90-280 | 145-485 | 0.14-0.24 | 8-45 | LIVE needs a strong effect; DEMO reachable |
| G3 k2.5 | 22-72 | 37-125 | 0.27-0.49 | 15-92 | DEMO at most in practice |
| G4 dyads k1.5 | 47-61 | 80-105 (33-47 book-days) | 0.29-0.33 (0.44-0.52) | 27-91 | episode-clustered (20-27 days a year); DEMO at most |
| G4 dyads k2.5 | 1-15 | 1-26 | 0.59-3.95 | 54-600 | **LIVE impossible** (RUS-UKR k2.5: 1-2 VAL trades a year) |
| G5 protests k1.5 / k2.5 | 115-123 / 19-20 | ~200 / ~34 | 0.21 / 0.51 | 11-97 | k1.5 LIVE only at ~0.2 Sharpe per trade; k2.5 DEMO at most |

Reading: the only cells where LIVE is arithmetically possible at a plausible size are G1 k1 (IDX and FX, ~1 trade per
leg every 2-3 days) and G1 / G3 / G5 at k1.5-2 if the effect is 2-3x Tetlock's undecayed size. Everything driven by
conflict counts (G2, G4) is too rare for LIVE whatever the size.
