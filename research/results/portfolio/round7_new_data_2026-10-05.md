# Round 7: a new 2004-2015 era, seven new IC symbols, a literature screen and multi-week premia (2026-10-05)

Rounds 3-6 ended with the same diagnosis: on the 26 IC symbols over 2016-2024, the flows that exist outside gotobi
are 0.3-3 bp, the size of IC's round-trip cost, and the larger effects are too rare for the 21-month holdout. What
would change that was new data or a looser brief. On 2026-10-04 the user chose all four of these directions:

| stream | what | data |
|---|---|---|
| A | a new unseen era, PRE = 2004-01..2015-12, from Dukascopy's free datafeed: an out-of-sample check of the live C3 and of the failed M1 | Dukascopy M1 bid/ask, 5 pairs, 2003-12..2015-12; H1 for 11 symbols |
| B | IC symbols no round had used: ES35, F40, IT40, STOXX50, US2000, USDCNH, DOGEUSD | IC M1 bid bars 2016-2026 already in the VPS cache |
| C | a literature search 2010-2026 for short-horizon mechanisms not yet tested, then screens | the 26 IC symbols (M1) + public series |
| D | relaxed limits (hold up to ~3 months, up to 10 positions per bot, lots still capital-independent): the canonical multi-week premia at their published parameters | FRED + Yahoo daily 2000-2024, checked against IC |

The brief is otherwise `research/PROMPT.md`. HOLD (2025-01..2026-09) was not opened: no candidate reached a
pre-registration.

## Answer

**No new algorithm. The live C3 passes a new 12-year era that nothing in this repo had touched.**

| | verdict | key numbers |
|---|---|---|
| **C3 Gotobi on PRE 2004-2015** (rule unchanged, registered bar) | **passes** | 5,184 legs, mean R +0.038, day-clustered t 4.8, 10/12 years net > 0, every pair > 0, x1.5 spread +0.030 (t 3.8) |
| M1 month-end USD on PRE (registered HOLD bar) | **fails again** | R +0.020, day-clustered t 0.64 (bar 1.0), beats 64 % of random days (bar 80 %) |
| A: multi-week premia, 24 rules, relaxed limits (D) | none passes | the financing markup alone costs 1.4-4.5 %/yr; best net Sharpe 0.20-0.23 (t <= 1.2); after 2015 even the gross premia are ~0 |
| New symbols, 10 hypotheses (B) | none passes | best gross power 1.9 (needs ~3); USDCNH Asian hours real but ~1 bp = its cost |
| Literature, 7 untested mechanisms (C) | none passes | best power 1.3; adaptive same-slot periodicity real in FX, 0.02-0.3 bp per slot vs 0.3-3 bp cost |

## A. The PRE era (Dukascopy 2004-2015)

### Data and protocol

- Dukascopy's datafeed (`datafeed.dukascopy.com`) needs a browser User-Agent and is only usable over kept-alive
  connections: a fresh request takes 15-35 s (TLS handshake), a kept-alive one 0.3-1.5 s; the server caps an IP at
  about 5 files/s over 8-10 connections. A missing file answers 503, not 404. 43.7k files (425 MB) in about 5 h.
- Before 2016 Dukascopy has FX and metals only: indices and energies start 2012-2014 (US500, USTEC, UK100, JP225,
  HK50, WTI, Brent 2012; AUS200, natural gas 2013; US30, DE40 2014).
- Validation on 12 days of 2016 against IC: time shift 0 min on every day (DST weeks included), mean |mid difference|
  0.05-0.12 bp, 1-minute return correlation 0.99 or better (`round7_pre_code/validate_output.txt`).
- Dukascopy's early **ask** is not usable as a cost (USDJPY 2004: bid = ask in 41 % of minutes, ask < bid in 16 %;
  GBPJPY 2004-08: a fixed 4-4.5 pip spread). The judged cost is therefore Dukascopy's bid plus IC's 2016-17 spread
  profile by minute of day (with its own profile for the first hour after a reopen), commission 0.6 bp, swaps from
  FRED rates minus 1 %/yr per side. Dukascopy's own spread is reported as a variant.
- The engine is the repo's unchanged `swing.py` / `swing_rules.py` (hashes equal to the M1 prereg's), run by a
  wrapper that swaps only the data, commission and swap inputs. On 2016-17 the same engine on Dukascopy vs IC gives
  per-pair mean R within 0.003, trade R correlation 0.987-0.9997, 98-99 % identical entry/exit minutes.
- The rules, the bars, three amendments (all about costs, each made before any PRE number) and the code hashes are in
  `round7_pre_code/REGISTRATION_PRE.txt` (final 16:13 UTC; the first PRE result is 16:47 UTC). Each registered run
  was executed once.

### C3 on PRE

Bar (registered): pooled mean R > 0 with day-clustered t >= 2.0; each pair mean R > 0; >= 8/12 years net > 0; mean
R > 0 at spread x1.5. $100 risk per leg.

| | legs | mean R | t | day-clustered t | years > 0 | net $ |
|---|---|---|---|---|---|---|
| **C3, all gotobi days** | 5,184 | **+0.0380** | 7.8 | **4.8** | 10/12 | +19,722 |
| USDJPY | 1,728 | +0.0677 | 7.6 | 7.4 | 12/12 | +11,700 |
| EURJPY | 1,728 | +0.0193 | 2.3 | 2.3 | 8/12 | +3,327 |
| GBPJPY | 1,728 | +0.0272 | 3.4 | 3.3 | 10/12 | +4,695 |
| long legs / short legs | 2,592 each | +0.037 / +0.039 | 4.6 / 7.2 | 2.9 / 4.5 | 8 / 11 | +9,557 / +10,165 |
| JP holidays skipped (as the live bots) | 4,896 | +0.0396 | 7.8 | 4.8 | 10/12 | +19,406 |
| spread x1.5 | 5,184 | +0.0302 | 6.2 | 3.8 | 10/12 | +15,642 |

**Verdict: passes**, with and without the holidays. Max drawdown $1,617 (16 R).

- By year, $: 2004 +2,138 · 2005 +3,339 · 2006 +1,938 · 2007 -36 · 2008 +329 · 2009 +218 · 2010 +1,926 ·
  2011 +4,524 · 2012 -245 · 2013 +3,903 · 2014 +889 · 2015 +798. Sub-periods 2004-07 +0.043, 2008-11 +0.041,
  2012-15 +0.031.
- Same cost settings on IC data: IS 2016-21 +0.047 (day-clustered t 3.8), VAL 2022-24 +0.048 (t 2.6). PRE is a bit
  weaker, with EURJPY the weakest pair (IS +0.042, PRE +0.019).
- Before costs: PRE +0.064, IS +0.086, VAL +0.069. With Dukascopy's own (unreliable) spreads: +0.027 (t 3.4), EURJPY
  +0.008 (t 0.9). Engine's 2026 commission constant +0.034; 2 % swap markup +0.035; no swap +0.037.
- **The fix is the mechanism.** Ending the long leg / starting the short leg at 00:55 UTC: +0.037 / +0.039. Moving the
  pivot to 01:05: +0.010 / +0.012; to 01:55: -0.001 / -0.009. The same legs on non-gotobi weekdays: -0.011 R (t -3.5).
- **Holidays again.** On the 48 Japanese-holiday gotobi days the long leg loses (R -0.049, t -2.0) and the short leg
  makes +0.071, as on IC 2016-2026 ([gotobi_jp_holidays_2026-09-29.md](gotobi_jp_holidays_2026-09-29.md)). This
  supports the bots' `SkipDates`.
- Reported only, by nominal day: 5th +0.022, 10th +0.045, 15th +0.071, 20th +0.054, **25th +0.003**, month-end
  +0.035. C4's day-type lots weighted the 20th and 25th up from IS; the 25th is ~0 here, which agrees with C4's HOLD.
  No sizing change is proposed.
- Caveat: the gotobi / Tokyo-fix effect itself was documented in the literature on 2000s data (e.g. Ito & Yamada,
  "Puzzles in the Tokyo fixing in the forex market", 2017), so PRE is out of sample for this repo's rule (times,
  stop, pairs, all chosen on 2016-2021) but not for the discovery of the mechanism.
- Per-leg Sharpe on PRE 0.109 (C3 in its 2025-26 holdout: 0.107).

### M1 on PRE

The registered HOLD bar of [prereg_month_end_usd_2026-09-27.md](prereg_month_end_usd_2026-09-27.md), unchanged.

| | trades (days) | mean R | day-clustered t | net $ | years > 0 |
|---|---|---|---|---|---|
| M1 | 432 (144) | +0.020 | 0.64 | +883 | 8/12 |
| spread x1.5 | 432 | +0.017 | 0.54 | +748 | |
| before costs | 432 | +0.042 | 1.31 | +1,804 | |

USDJPY +0.033, USDCHF -0.001, EURUSD +0.029; 2004-07 -0.074, 2008-11 +0.066, 2012-15 +0.070. Random-day control:
real beats 64.4 % of 500 seeds. The k-th-last-weekday placebo runs from t -2.2 to +2.2, so k = 3 is not special.
**Fails** criteria 2 and 4, now in two independent holdouts (IS-size effect would have given t ~4.5 here). M1 stays
rejected.

## B. Seven new IC symbols

IC M1 bid bars 2016-2024 (HOLD cut at load). DOGEUSD's cache files are all empty, so 6 symbols. Costs from IC's
published average spreads: ES35 4.2 pts and IT40 9.0 (fixed), F40 1.79, STOXX50 1.5, US2000 0.34 (2-5 bp round
trip); USDCNH 2.93 pips + commission (~1.0 bp); index financing ~2 bp a night per leg. Rules written before the
numbers (scratch `HYPOTHESES.md`).

| hypothesis (source) | IS 2016-21 gross | VAL 2022-24 gross | verdict |
|---|---|---|---|
| US30/USTEC lead US2000, 5-60 min and daily (Lo & MacKinlay 1990; Chordia & Swaminathan 2000) | +0.34 bp (t 2.8) at 5 min; daily wrong sign | -0.03 | no lead: the CFDs follow futures |
| STOXX50 leads IT40/ES35/F40; periphery catch-up next day | intraday \|mean\| <= 0.3 bp; IT40 +3.9 (t 2.2) | +0.1; ES35 +3.4 | eras disagree, cost ~12 bp |
| fade the periphery after a big STOXX50 day | IT40 +1.6 (t 0.3) | +5.6 (t 1.0) | nothing |
| momentum into the European close (Baltussen et al. 2021) | STOXX50 +1.2 (t 0.8) | +3.7 (t 2.4) | VAL only, <= spread |
| fade after the close auction; monthly expiry | -0.7..+1.2; +2.4 | -0.5..0.0; -3.5 | nothing |
| PBOC fix surprise (official CFETS central parity 2015-2024) | priced in 6 min (t 3.1); 1 day -1.7 | 6 min t 3.1; -0.6 | no drift |
| CNH home hours: long USDCNH 01:30-08:30 UTC (Breedon & Ranaldo 2013) | +1.17 (t 2.6) | +2.03 (t 2.5) | real, ~= cost: net +0.1 / +1.0, power 0.2 / 1.0 |
| exporter month-end CNH; CNH -> AUD/NZD; US2000 intraday momentum | +6.4; <= 0.06; +1.7 | -2.0; wrong sign; 0.0 | nothing |

## C. Literature 2010-2026 and seven screens

38 mechanisms found (OpenAlex, Semantic Scholar, arXiv); 23 were already on the rejected list. Of the other 15, 7
were screened, 2 ruled out by the power rule before testing (FOMC-day FX carry, Mueller, Tahbaz-Salehi & Vedolin
2017: <= 1.5; weekly Japanese MoF portfolio flows: <= 1.6), 6 are untestable here (BoJ ETF buying ended 2024-03;
Google Trends FEARS; FX order flow; Korean LETF front-running; BTC ETF benchmark; commodity-note dates).

| test (source) | IS / VAL | power (bar ~3) |
|---|---|---|
| adaptive same-slot periodicity, 30-min slots, lags 5-40 days / 4-26 weeks (Heston, Korajczyk & Sadka 2010; Keloharju et al. 2016) | real in FX, strongest in JPY crosses (40-day slope t EURJPY +4.2 / +2.6), reversed in indices; 0.02-0.3 bp per slot vs 0.3-3 bp cost; the IS-best cell is <= 0 net in VAL for all 26 symbols | <= 0.8 |
| quarter-hour algorithmic openings (arXiv 2607.09426) | no continuation with t >= 2 in both eras | <= 0.6 |
| US500 option-expiry pinning (Ni, Pearson, Poteshman & White 2021) | -1.44 bp (t -1.0) / -1.27, controls the same | < 0 |
| stablecoin issuance -> BTC/ETH (Griffin & Shams 2020) | BTC +68.7 bp (t 1.4) / +38.8 (t 1.3); IS weekly slope wrong sign | 0.9-1.3 |
| PBOC countercyclical reversal, USDCNH | +0.63 bp (t 2.1) / +0.45 (t 0.9) | < 0 net |
| ISM pre-announcement drift (Kurov et al. 2019) | flips sign between eras | 0.3 |

## D. Multi-week premia with relaxed limits

24 rules at their published parameters, monthly rebalance, <= 10 legs per bot (TSMOM as three bots: FX 10,
commodities 6, indices 8). Daily data 2000-2024 from FRED (FX noon rates, short rates, CPI) and Yahoo (indices,
front-month futures; Stooq now answers with a bot check); checked against IC 2016-2024 (FX daily correlation 1.000,
US indices 0.999, others >= 0.96 daily, >= 0.99 monthly for metals and indices). Financing = rate differential minus
IC's fitted markups (FX 0.6-1.7 %/yr per side, metals 1.0 / 0.5 %, indices about r + 5.3 % long and r - 3.9 % short).
Spread and commission are 0.00-0.34 %/yr, so the financing markup decides everything.

| rule (source) | gross Sharpe | net Sharpe (t) | net Sharpe 2000-15 / 2016-21 / 2022-24 | markup drag %/yr |
|---|---|---|---|---|
| TSMOM 12 m, 24 instruments (Moskowitz, Ooi & Pedersen 2012) | 0.60 (t 3.0) | 0.16 (0.78) | 0.48 / -0.47 / -0.50 | 4.5 |
| TSMOM 12 m, FX only | 0.42 | 0.23 (1.17) | 0.42 / -0.20 / 0.26 | 1.9 |
| TSMOM 12 m, commodities / indices | 0.44 / 0.46 | 0.20 / -0.04 | | 2.5 / 5.0 |
| dollar carry (Lustig, Roussanov & Verdelhan 2014) | 0.34 | 0.20 (1.02) | 0.15 / 0.13 / 0.62 | 1.4 |
| equal-weight carry (Burnside et al.) | 0.40 | 0.19 (0.97) | 0.18 / 0.15 / 0.41 | 2.1 |
| G10 carry top 3 / bottom 3 (LRV 2011) | 0.37 | 0.05 (0.25) | 0.13 / -0.23 / 0.16 | 3.2 |
| FX momentum 1 m / 3 m / 12-1 (Menkhoff et al. 2012) | -0.12 / -0.12 / 0.13 | -0.43 / -0.44 / -0.18 | | ~3 |
| FX value 5 y (Asness, Moskowitz & Pedersen 2013) | 0.09 | -0.20 | | 2.9 |
| index momentum 12-1 / index carry proxy | 0.19 / -0.07 | -0.64 / -0.97 | | 8.2 / 9.0 |
| commodity momentum / 5-year reversal | -0.40 / 0.32 | -0.70 / 0.04 | | 2.9 / 2.4 |

- **IC's financing kills the premia.** Inside TSMOM_ALL the index bot earns 2.4 %/yr gross and pays 2.5 %/yr of
  markup; the markup alone takes US500's excess return from 7.4 to 2.1 %/yr. Every rule with index legs is net
  negative.
- **After 2015 the premia are weak even gross:** TSMOM 12 m gross Sharpe 0.04 in 2016-21 and 0.01 in 2022-24; FX
  momentum and value are negative gross after publication. Cheaper financing would not rescue 2016-2024.
- Commodity carry cannot be computed (IC shows no futures curve). Energies use the repo's constant 2026 swap.
- **Power:** HOLD's expected t is about 1.32 x the annual Sharpe, so a slow premium with net Sharpe 0.2-0.6 can only
  be falsified by HOLD, never confirmed. A bar for such rules was proposed (published parameters frozen; net > 0 in
  2000-15, 2016-21, 2022-24 and after publication separately; Newey-West net t >= 2.5 over 2000-2024; >= 15/25
  years; positive at spread x1.5 and markup x1.25; gross above the 95th percentile of random books). Nothing meets
  it; the closest, equal-weight carry, is positive in every era but at t 0.97.

## What this says

- **C3 now has support over 2004-2024**: three eras chosen and checked in order (IS, VAL, the 2025-26 holdout) plus a
  fourth, older one that was never looked at, with the same mechanism signature (the edge sits at the 00:55 fix and
  vanishes 10 minutes away; holiday long legs lose). Nothing in this round argues for changing the live bots.
- **The binding constraint is IC's cost structure, in both horizons.** Intraday flows (new symbols, CNH, adaptive
  periodicity, leveraged-ETF settlement) are 0.02-3 bp against 0.3-5 bp of spread and commission. Multi-week premia
  are 2-6 %/yr against 1.4-4.5 %/yr of financing markup on top of the rate differential. All seven rounds agree.
- What could still change the picture, all decisions rather than more screening of these symbols:
  1. **A cheaper venue for the slow premia** (exchange futures, where financing is the rate differential without a
     markup). The premia are also weak gross since 2015, so even then the expected gain is small.
  2. **The PRE data for FX event studies.** Dukascopy M1 for USDJPY, EURJPY, GBPJPY, USDCHF, EURUSD 2004-2015 and H1
     for 11 symbols are now local (`research/data/duka/`, git-ignored). Twelve more years make rare FX events (monthly,
     central-bank days) testable with power, but the rare-event screens of rounds 3-4 were weak already in IS.
  3. **More of C3's own mechanism** is excluded by the brief (new rules must differ from gotobi / the Tokyo fix).

## Process

- **HOLD stayed closed** in every stream: M1 caches and new-symbol bars cut at `ts < 2025-01-01` on load, FRED and
  Yahoo fetched with end date 2024-12-31, DefiLlama post-2024 rows dropped at load. Disclosures: (1) stream D's first
  Yahoo request printed one live S&P 500 quote (~2026-10-02) in a response header, a price level with no returns;
  (2) the swap markups of `research/swing/rates.py` are fitted on 2025-26 rates by design (a cost parameter; stream D
  computed them in a sealed step that only output the constants, stream A used a fixed 1 % instead).
- **Data pulled.** IC: ticks of the 16 symbols missing locally were pulled from the VPS cache and turned into
  `data/m1/*.npz` (DE40's 2016-2021 comes from the cache's old name DE30; prices are continuous across the rename),
  then the ticks were deleted; M15 for all symbols; M1 bars for the 7 new symbols. Dukascopy: as above.
- **Not done.** A tick sample of the new symbols from the VPS (for exact spreads) needed a throwaway backtest
  container started with the demo bot's credentials; the permission classifier denied reading them and nothing
  was retried. No candidate needed it.
- **Code.** The screens are scratch scripts, as in rounds 3-6. Stream A's registered PRE runs are kept in
  [round7_pre_code/](round7_pre_code/): the registration, the Dukascopy fetcher/converter, the engine wrapper
  (`run_pre.py.txt`; its `HERE / "data"` paths now live in `research/data/duka/`) and their outputs. Nothing in
  `research/` code was edited.
- C3 correlation of new rules: not computed, since none survived.
