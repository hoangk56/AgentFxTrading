# Round 20: declared-only — central-bank-day carry, and index expiry settlement auctions (2026-10-06)

Same rule as round 19: every cell declared in full before any return ([round20_declared2/BRIEF.md](round20_declared2/BRIEF.md);
`HYPOTHESES_F/G.md`, `STREAM_F/G.md` in [round20_declared2/](round20_declared2/)).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** The round found the most durable
literature-declared effect so far, the dollar's fall on FOMC days, but at 8 events a year it cannot reach the bars.

## F. Carry on central-bank decision days (Mueller, Tahbaz-Salehi & Vedolin 2017, JF)
- The paper: 1994-2013, 9 currencies vs USD, 16:00-16:00 ET FOMC day; high-rate portfolio +14.5 bp (t 2.49), all
  currencies vs USD +10.8 (t 2.27); BoJ similar, other banks nothing. Here 7 of the 9 currencies (no NOK/SEK); ranking
  rates: FRED files in the repo (2014-26) and BIS daily policy rates for 2003-16 (rates, not prices).
- 7 declared cells. Best: **A4, long the currencies whose rate is above USD's, against USD, 16:00 ET the day before to
  16:00 ET on FOMC days**: PRE +17.7 bp (t 2.09) / IS net +21.6 (t 1.90) / VAL net +31.6 (t 2.40), 6/6 IS and 3/3 VAL
  years, beats 97-100 % of random days, no drift on non-decision days, robust to x1.5 and late fills. **Fails DEMO on
  IS net t (1.90 < 2.0)**; HOLD power 1.1-1.8. Cost (~1 bp) does not bind; 8 events a year do.
- The literal carry spread (high minus low rate) is absent after 2015; the effect is the dollar leg. The pooled 8-bank
  extension and BoJ days are negative in IS (the paper's BoJ result reversed in 2016-21).
- Information only: pooled 2004-24, A4 is +20.0 bp net (t 3.25, n 156; winsorised t 3.38; 2014-24 alone, outside the
  paper's sample, +16.9, t 2.13). C3 correlation -0.03 daily.

## G. European and Hong Kong index expiry settlements
- Rules from the exchanges: DAX Xetra intraday auction 13:00 CET; FTSE 100 EDSP auction 10:10 London; EURO STOXX 50
  average 11:50-12:00 CET; CAC 40 average 15:40-16:00 CET; HSI average of 5-minute quotes on the penultimate business
  day. 108 European and 108 HK expiries 2016-24.
- 64 declared cells (sides from Joensuu 2010, Baltussen, Terstegge & Whelan 2024, Stoll & Whaley 1987/1991, Chow,
  Yung & Zhang 2003). Four quarterly-expiry cells meet the DEMO numbers (short after the settlement: UK100 / STOXX50 /
  DE40 / EU4, IS net t 2.09-2.32) but they are one effect and **fail the random-entry control** (in VAL, shorts at
  random times on the same days earned as much or more); HOLD would hold 7 quarterly days (expected t 0.6-0.9). Max IS
  net t 2.32 vs a null 95th percentile of 2.89.
- Information only: European indices fall over the whole session on quarterly expiry Fridays (EU4 open-to-close short
  +26.8 bp IS / +33.9 VAL, t ~1.5), ~0 in 2016-19 and carried by four 2020-23 days; not a settlement-minute flow.
  Expiry settlement windows now look exhausted on these symbols (US SOQ round 11, Nikkei SQ round 10, Europe and HK here).

## What this says
- Literature-declared effects that are real and durable exist (FOMC-day dollar weakness: positive in 2004-15, 2016-21,
  2022-24 at similar size), but the strongest ones are rare. The LIVE bar needs ~200+ independent events a year at
  this per-event Sharpe (~0.26), or a per-event Sharpe ~1 at 8 a year.
- One declared extension remains (next round): other scheduled Fed / US-policy uncertainty events with the same
  mechanism, which could multiply the count without changing the rule's logic.

## Directions that need the user's decision
- FOMC-day dollar short: a tiny demo (8 trades a year) would take ~7.5 years to reach t 2 alone; or add NOK, SEK, MXN
  and other IC currencies on FOMC days (new price data) to raise the per-event Sharpe; or accept the pooled 2004-24
  evidence as a bar (a rule change). None is applied.
- European index minute data before 2016 or data after 2026-09-24 for the quarterly-expiry weakness (4 a year: never
  LIVE).

## Process and disclosures
HOLD not loaded. Stream F fetched BIS policy rates 2003-16 (rates, not prices). Stream G had seen round 7's pooled
expiry fade before declaring (disclosed); a declared contract-switch filter dropped a real UK100 day (2020-03-20),
which changes no verdict. Scripts in the scratchpad (`r20/F`, `r20/G`). Nothing in `research/` code was edited.
