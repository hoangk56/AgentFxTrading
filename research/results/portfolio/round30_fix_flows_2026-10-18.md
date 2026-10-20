# Round 30: the fix and flow hypotheses declared for the six FX symbols the user approved

2026-10-18 (UTC). On 2026-10-18 the user approved three of round 29's decisions ("1,2,4 ok"):
1. the gold $50-level rule on the demo account;
2. IC tick pulls and Dukascopy M1 2004-15 for USDCNH, USDMXN, USDSGD, EURNOK, USDNOK and EURSEK;
4. rerunning the forward logs.

This round is item 2. It tests the hypotheses round 25 declared for those symbols before any of their prices existed
in this project (round25_surprises/HYPOTHESES_A.md: H-NOK, H-EMFIX, H-CNH), exactly as declared. Brief:
[round30_fix_flows/BRIEF.md](round30_fix_flows/BRIEF.md), written 09:16 UTC before any return. Same bars as rounds
25-29, no RELAXED tier. HOLD was never loaded: the HOLD years of the six symbols stay on the VPS.

## Answer
- **No LIVE or DEMO candidate.** No PREREG_DRAFT.
- **H-EMFIX.** The Banxico FIX does not behave like a dealing fix in 2016-24.
  - MX-1 (long USDMXN 09:00 -> 12:00 Mexico City) had a mid effect in PRE 2007-15: +2.28 bp (t 2.87).
  - The effect reverses in IS (-0.82) and VAL (-2.55). Net is -2.69 (t -2.64) / -4.28 (t -3.37), with 0 of 9 years
    positive.
  - SG-1 (USDSGD into the ABS VWAP) has no effect, and the BOOK fails.
- **H-CNH.** Round 19's CNY-close cell (long USDCNH 06:30 -> 08:30 UTC) is real at mid: IS +1.23 (t 4.61), VAL +1.71
  (t 4.16).
  - At IC's real bid / ask it nets +0.08 (t 0.30) IS and +0.65 (t 1.58) VAL.
  - DEMO needs an IS round trip <= 0.70 bp; IC's is 1.15. LIVE is impossible at any spread.
- **H-NOK.** NOK-1 (EURNOK in Norges Bank's direction, 09:00 -> 16:00 Oslo) nets IS +2.33 (t 1.65) and VAL -4.99
  (t -2.24): it fails both bars.
  - The dose slope NOK-D is +6.00 bp per NOK bn a day (t 2.80) in IS but +0.34 (t 0.22) in VAL. Norges Bank sold up
    to NOK 4.3 bn a day in VAL, so the decay is the familiar IS > VAL pattern.
  - The announcement (NOK-A) is priced within its first minute.
  - NOK-2, the USDNOK replica, fails the same way: IS net +1.87 (t 1.04), VAL -3.39.
  - The EURSEK placebo NOK-P is about zero at mid in every era. So the IS move was NOK-specific, a NOK flow or the
    krone's 2020-21 recovery, and it was gone in 2022-24, when Norges Bank's NOK sales were the largest on record.

## Stream E: EM fixes and the CNY close ([STREAM_E.md](round30_fix_flows/STREAM_E.md))
Details fixed before any price was loaded: [HYPOTHESES_E.md](round30_fix_flows/HYPOTHESES_E.md), 09:37-09:38 UTC.
Each PRE number was written with its time before the same cell's IS / VAL. bp per trade, day-clustered t.
- PRE: Dukascopy bid with IC's 2016-17 spread profile + 0.6 bp.
- IS / VAL: buy at the IC ask, sell at the bid, + 0.6 bp.

| cell | PRE mid (t) | IS mid (t) | VAL mid (t) | cost IS / VAL | net IS (t) / VAL (t) | power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|
| MX-1 USDMXN 09:00 -> 12:00 MX | +2.28 (2.87) | -0.82 (-0.80) | -2.55 (-2.01) | 1.87 / 1.73 | -2.69 (-2.64) / -4.28 (-3.37) | -1.42 / -2.56 | 15 / 1 % | fails: reverses after 2015 |
| SG-1 USDSGD 09:00 -> 11:00 SGT | -0.15 (-0.41) | -0.24 (-0.97) | -0.23 (-0.65) | 1.06 / 1.17 | -1.30 (-5.22) / -1.39 (-3.99) | -2.80 / -3.03 | 9 / 23 % | fails: no effect |
| CN-1 USDCNH 06:30 -> 08:30 UTC | +0.10 (0.46) | +1.23 (4.61) | +1.71 (4.16) | 1.15 / 1.06 | +0.08 (0.30) / +0.65 (1.58) | 0.16 / 1.20 | 100 / 100 % | fails DEMO: IS net t 0.30 |
| BOOK (R per day) | +0.032 (0.82) | +0.070 (1.60) | +0.072 (1.18) | legs | -0.191 (-4.40) / -0.187 (-3.07) | -2.36 / -2.33 | 94 / 85 % | fails |

- **Stress tests, IS / VAL net.**
  - MX-1: spread x1.5 -3.33 / -4.84; both fills +1 minute -1.94 / -4.15.
  - CN-1: spread x1.5 -0.20 / +0.42; both fills +1 minute +0.06 / +0.62.
- **Information cells.** None supports the FIX as a dealing fix.
  - MX-15, the rebound: about 0.
  - MX-H, the FIX-less holidays: in the predicted direction in PRE, the opposite in IS + VAL.
  - MX-W splits MX-1 at the WMR minute. The PRE effect sits in 09:00 -> WMR (+1.81, t 3.40). After the WMR minute IS
    and VAL reverse (-1.50 / -3.08), which is Krohn-Mueller-Whelan's USD reversal after WMR, not the FIX.
  - MX-C, the 2-hour-gap days: VAL follows the Mexico City clock, but with the wrong sign.
  - MX-A, the 2015 auctions: no response to the auction size.
- **CNHC-I check.** Round 19's cell reproduced from the bid bars: IS +1.228 (t 4.59), VAL +1.689 (t 4.09). PRE
  2012-15 has no effect. Post hoc, that fits the August 2015 change that made the 16:30 close feed the next day's
  central parity.
- **Chance.** Among the 4 counted cells the best IS mid |t| is CN-1's 4.61 (sign-flip p95 2.45). It was already known
  from round 19.
- **Correlation with C3 (IS + VAL), daily:**

  | leg | daily corr | detail |
  |---|---|---|
  | SG-1 | +0.052 | no gotobi dependence |
  | MX-1 | +0.02 | |
  | CN-1 | -0.004 | |

## Stream N: Norges Bank's pre-announced daily NOK flow ([STREAM_N.md](round30_fix_flows/STREAM_N.md))
Details fixed before any return: [HYPOTHESES_N.md](round30_fix_flows/HYPOTHESES_N.md), 09:33 UTC.
- The mid-month amount changes are dated from Norges Bank's press releases.
- The calendar is `holidays.NO` plus 24 and 31 December.
- The random control uses 1,000 seeds.
- Amendment 1, 09:59 UTC and before any return: a glitch filter for Dukascopy's early junk quotes.

| cell | PRE mid (t) / net | IS mid (t) | VAL mid (t) | cost IS / VAL | net IS (t) | net VAL (t) | power IS / VAL size | random IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| NOK-1 EURNOK 09:00 -> 16:00 Oslo, side = Norges Bank's, size clip(\|A\|/1000, 0.5, 2) | +1.29 (1.85) / -0.43 | +5.36 (3.78) | +0.07 (0.03) | 3.03 / 5.06 | +2.33 (1.65) | -4.99 (-2.24) | +0.89 / -1.70 | 100 % / 8.9 % | fails LIVE and DEMO |
| NOK-D slope, bp per NOK bn a day (mechanism) | +3.22 (1.40) | +6.00 (2.80) | +0.34 (0.22) | | | | | | pooled 2004-24 +2.24 (t 3.09), but decays |
| NOK-A 10:00 -> 10:15 on announcement days (information) | +4.43 (1.86) | +3.98 (1.76) | +11.37 (1.68) | | net from 10:01: -4.95 | -5.07 | | | priced within the first minute |
| Norwegian-bank-holiday placebo | pooled -0.44 (t -0.07, n 45) | | | | | | | | about 0, too few days |
| NOK-2 USDNOK (declared replica, not independent) | +1.41 (1.52) / -0.57 | +5.10 (2.84) | +0.98 (0.30) | 3.23 / 4.37 | +1.87 (1.04) | -3.39 (-1.03) | +0.56 / -0.78 | 100 % / 4.6 % | fails LIVE and DEMO; 2 / 9 years |
| NOK-P EURSEK (placebo, predicted 0) | -0.03 (-0.05) / -1.66 | -0.16 (-0.20) | +0.09 (0.05) | 2.52 / 4.23 | -2.69 (-3.30) | -4.14 (-2.38) | | 31.9 % / 45.2 % | about 0 at mid, as predicted |

- **NOK-1 detail.**
  - Stress tests: spread x1.5 gives IS +1.11 / VAL -7.18; both fills +1 minute give +1.34 / -1.44.
  - 3 of 9 years are net positive.
  - 80 % of the IS mid P&L is from 2020-21, the years of the largest NOK purchases and of the krone's recovery after
    March 2020.
- **A quote artefact at 09:00 Oslo.** IC's EURNOK bid and ask both rise into 09:00 Oslo and fall back in the next
  minute: +2.33 / -2.30 bp in VAL, +0.87 / -0.78 in IS. It follows the Oslo clock in both DST seasons; EURSEK shows at
  most +0.3. It costs the declared 09:00 entry about 2.3 bp in VAL, but does not change the verdict.
- **Costs** are below round 25's estimates:
  - EURNOK's real round trip is 1.6-4 bp (round 25 assumed 2.9-5.6);
  - USDMXN's is about 1.8 bp (2.07 assumed).

## Data (decision 2)
- **IC ticks.** A VPS script ran throwaway `ctrader-console backtest` containers (GotobiBot with both legs off and
  URLs disabled, bridge network, one year a container, 4 in parallel at low CPU priority). It filled the shared
  backtest cache with 3,946 tick days per symbol (2016-01-01..2026-10-17), about 7 GB.
  - 2016-24 was copied to `research/data/<SYM>/t1/`. 2025-26, the HOLD and the forward days, stays on the VPS only.
  - Script: `scratchpad r30/pull/pull_ticks_r30.py` (not kept); the method is in the research memory notes.
- **Dukascopy M1 2004-15**, in `research/data/duka/m1_r30/<SYM>_<YYYY>.npz` (`round24_relaxed/prereg_code/duka_dl.py.txt`):
  - USDMXN 2007-15, USDCNH 2012-15 and USDSGD 2004-15 are complete;
  - EURNOK, USDNOK and EURSEK 2004-15 are complete as well (61 symbol-years in all, by 11:38 UTC);
  - EURNOK 2011 lost about 37 weekdays to HTTP 503s, and Dukascopy EURNOK barely trades in 2004-05.
  - Both sources are at x1e5. The early Dukascopy asks are junk (bid = ask on most minutes before ~2010).

## Decision 1: the gold $50 rule is on demo
`cBot/GoldLevelBot.cs`, PR #18, was deployed 2026-10-18 10:07 UTC as `cbot-demo-demo-xauusd-levels-gold50` on the demo
account: 0.01 lot, fixed, with a $100 broker guard.
- A cTrader backtest over the holdout matches all 228 engine triggers, and the bot's model net equals the engine's on
  every trade ([gold_level_cbot_2026-10-18.md](gold_level_cbot_2026-10-18.md)).
- **The release-calendar seed is valid through 2026-12-11.** After that the bot stops arming until the seed is rebuilt.
- Score the demo with `python -m research.tools.gold_demo_check <trade log>`, which applies the registered stop and
  promotion rules.

## Decision 4: the forward logs
- F3 / E1: no new trading day since slice 2 (to 2026-10-16). Monday 2026-10-19 is the next one; Dukascopy has a day
  once it is over.
- B3 / A1: blocked.
  - farside.co.uk still answers 403 (a Cloudflare challenge).
  - The GitHub capture stops at 2026-09-08.
  - The Internet Archive answered HTTP 429 to all 26 capture-list requests, from the morning to 11:22 UTC. The
    calendar build had used the archive heavily earlier that morning.
  - The slice waits for an archive capture with the 2026-10-12..10-15 rows; rerun it in a later session.

## State after round 30
- **Running.**
  - C3, the Gotobi JPY basket: live, the only LIVE algorithm.
  - EcbWindowBot: F3 live at 0.01 lot, E1 on demo.
  - GoldLevelBot (gold $50 levels): on demo.
- **Candidates below LIVE that passed a HOLD:** as in round 29's table; the gold rule now runs.
- **Decisions still the user's:**
  - whether a platform other than cTrader is acceptable (IC share CFDs are on MT5 only; round 25's STREAM_A put the
    post-blackout rule's chance of a LIVE at ~3-5 %);
  - whether research should continue past the approved items.
- **Recurring tasks, no decision needed:**
  - rebuild the gold calendar seed before 2026-12-11;
  - rerun the forward logs as days accrue.
- With round 30, the routes round 25's STREAM_A priced at >= 1 % for LIVE that remain untried are the MT5 share CFDs
  and a cheaper venue. A venue change made only for research is not recommended.

## Files
- [round30_fix_flows/](round30_fix_flows/): BRIEF.md, HYPOTHESES_E.md, STREAM_E.md, HYPOTHESES_N.md, STREAM_N.md.
- Session scratchpad `r30/` (E and N scripts and outputs, the VPS pull script, the Dukascopy logs; not kept).
