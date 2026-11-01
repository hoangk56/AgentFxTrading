# Round 38 brief: daily short-sale volume and ETF primary flows; Atlantic storms and supply disruptions

Written 2026-10-29 (round 37 closed the same day with no candidate). Repo: /Users/hoangbk/00.code_base/105.AgentFxTrading.
Same bars as rounds 25-37 (LIVE / DEMO in research/PROMPT.md; no RELAXED tier). Everything in
research/results/portfolio/round37_forced_flows/BRIEF.md applies unchanged (Read first, Data, HOLD closed at
2024-12-31 at load, Network rules, Rules for this round, What to return), except the streams, the round folder
(research/results/portfolio/round38_short_volume_storms/) and the scratchpad
(`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r38/<stream>/`).
Also read the round 37 report (research/results/portfolio/round37_forced_flows_2026-10-29.md), especially "Pitfalls":
**do not use web.archive.org** (it flagged this IP on 2026-10-29).

Reachability probed 2026-10-29 from this Mac (HTTP 200): cdn.finra.org/equity/regsho/daily/ (CNMSshvol from 2018-08;
per-facility FNSQshvol / FNYXshvol files back to at least 2010-01), www.ishares.com product pages, www.nhc.noaa.gov
(HURDAT2 at /data/hurdat/, advisory archive /archive/<year>/), www.eia.gov open data; ssga.com redirects (301; follow it
once and see).

## Streams
| stream | direction | prior work to read, and how this differs | why it might escape the limits |
|---|---|---|---|
| S | **Daily short-sale volume and ETF primary-market flows -> US indices, gold, silver, oil, JPY / EUR.** (1) FINRA Reg SHO daily short volume / total volume for SPY, QQQ, DIA, IWM, GLD, SLV, USO, UNG, EWJ, FXE / FXY if present, and the top-10 index weights aggregated (2010-24 via the per-facility files, CNMS from 2018-08): short-volume ratio level, z vs trailing 60 days, change; side from the literature (short sellers informed -> high short ratio predicts lower next-day returns: Diether, Lee & Werner 2009 RFS; Boehmer, Jones & Zhang; for ETFs short volume is mostly market makers hedging creations, so state which side the ETF literature implies and fix it before returns). (2) ETF shares outstanding / creations-redemptions for SPY, QQQ, IWM, GLD (round 31 G did GLD tonnes: don't redo it), USO, EWJ where an issuer history is free: Brown, Davies & Ringgenberg 2021 RF (ETF flows signal non-fundamental demand and predict reversal of the underlying). Use each value only after it is public (FINRA files ~18:00 ET same day; shares outstanding the next morning: state it). Horizons next session to 5 days; also next-day open-to-close. | round 35 O (declared O7 FINRA ETF short volume, never graded; scripts may be gone with its scratchpad), round 35 T / round 31 J (flow tables co-move, don't predict), round 31 G (GLD holdings = 1-day momentum), round 34 E (LETF rebalancing dose), round 23 P (sell-side flows). | Daily data on 4+ index ETFs and 4+ commodity ETFs gives ~2,000 trades a year, so a small per-trade Sharpe (~0.05-0.07) could carry LIVE power; at 1-5 day horizons IC's cost is a small share of the sd (round 11). The short-volume series and ETF share counts are mechanical by-products of who must trade (market-maker hedging, AP creations), not public news. |
| H | **Atlantic storms and physical supply disruptions -> XNGUSD, XTIUSD, XBRUSD (and USDCAD, US500 as controls).** NHC HURDAT2 tracks and the advisory archive (issue times, forecast cones / watches for the Gulf of Mexico production area and LNG terminals), EIA Gulf of Mexico production shut-in data if reachable, other dated disruptions with a public timestamp (refinery / pipeline outages, e.g. Colonial 2021, Freeport LNG 2022; declare the list from an official source, not from prices). Side from the mechanism, declared per product (Gulf production shut-ins -> crude up; LNG-export outages -> US gas down; demand destruction from landfall -> gas down), horizons from the advisory to 1-5 days. Count events per year first. | round 31 G (NOAA CPC temperature outlooks: priced in the 24 h before posting), round 6 (EIA / API, commodity flows), round 25 (scheduled surprises priced before release). No round used storms or outages. | Forecast-driven supply risk arrives on a published clock (advisories at 03 / 09 / 15 / 21 UTC); storm-season XNG / oil moves are large against cost at 1-5 days. Expect few events (DEMO at most): say so from the count and the power arithmetic before building, and stop early if the count cannot reach DEMO. |

If a stream's first construction fails, it moves to related mechanical by-products of forced trading in its row (declare
first), as in round 37. Two streams this round; each may use up to 3 heavy Python processes (under ~3 GB RAM each).
