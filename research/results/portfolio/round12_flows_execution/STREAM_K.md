# Round 12, stream K: literature 2018-2026 and screens of the untested mechanisms (2026-10-06)

The brief is [BRIEF.md](BRIEF.md). The rules, with UTC times written before the numbers they govern, are in
[HYPOTHESES_K.md](HYPOTHESES_K.md); the K4 diagnostics there are post hoc and marked as such. HOLD (2025-01..2026-09)
was not loaded: every screen ran on the shared panel, which ends 2024-12-31.

## Answer

**No candidate at either bar. No PREREG_DRAFT.** 6 families, 123 eligible cells (plus controls and information
rows). On the registered side, no cell reaches the DEMO bar's IS net t of 2.0.

The closest lead is the **bitcoin reversal after the Deribit Friday 08:00 UTC option expiry** (K4): fade the
07:00-08:00 UTC move from 08:01 to 09:00 UTC on Fridays. It is real at mid in both eras: +20.6 bp (t 2.34) IS and
+11.2 bp (t 3.13) VAL. It is specific to Fridays: Mon-Thu has the same 08:00 funding time but daily expiries only,
and gives -3.2 / -0.8 bp, so the Friday minus Mon-Thu difference has t 2.55 / 2.84. It beats 100 % / 99.5 % of random
entries. IC's 2018-21 BTC spread (11.6 bp a round trip; 27 bp in 2018) leaves IS net at +9.0 bp, t 1.03. That fails
DEMO, and the lead is not registrable. VAL net is +7.9 bp (t 2.20, per-trade Sharpe 0.18, power 1.7).

## Step 1: what rounds 3-11 tested

The list is kept in `scratchpad/r12/K/tested_list.md`. Most of the 2018-2026 literature on intraday flows had already
been covered: fixes and benchmarks (Tokyo, ECB, WM/R, LBMA, SGE, Asian FX, Platts), settlement flows and LETF
rebalancing (commodities, Nikkei, US close), MOC and closing auctions, pinning (FX cut, SPX/NDX daily expiries), the
overnight drift, the European-open window, Treasury auctions, pre/post central-bank drift, macro releases, lead-lag,
crypto funding times, intraday momentum in indices and crypto, COT, GEX/DIX and VIX. The mechanisms below are the ones
that had not been tested.

## Step 2: literature candidates

The search ran on OpenAlex (about 55 queries, filtered to 2018 onwards; the query lists are `lit/q1-q4.txt` and the
results `lit/r*.txt`, `lit/abs*.txt`) and Semantic Scholar (DOI lookups; its search endpoint mostly returned 429).
SSRN pages were unreachable, so for SSRN-only papers the side comes from the title and this is flagged. "Mag" is
the paper's reported size where an abstract gives one; most give none ("n/r"). The status is one of: tested earlier,
near-tested earlier, screened here, or not testable without new data.

| # | paper | mechanism, side, window | mag vs IC cost | events/yr | status | power (est. or screened) |
|---|---|---|---|---|---|---|
| 1 | Elaut, Frömmel & Lampaert 2018 JFM | FX intraday TS momentum: first half-hour -> last half-hour, follow | n/r; FX cost 0.6-1.2 bp | 250/pair | **screened K1** | <= 1.3 |
| 2 | Li, Sakkas & Urquhart 2022 JFM | ITSM in 16 markets, stronger at low liquidity / high vol | n/r | 250 | indices tested (r4, r11 H2); FX **screened K1** | <= 1.3 |
| 3 | Seeck 2026 SSRN 7008318 | FX ITSM amplified in JPY; "cost barrier" (title only) | n/r | 250 | **screened K1** (P3, JPY pairs) | < 0 IS |
| 4 | Ladia 2026 SSRN 7124578 | opening-range reversal in Dow futures, 0DTE hedging; fade (title only) | n/r; US30 0.3-0.9 bp | 250 | **screened K3** | <= 1.2 |
| 5 | Weiss, Gaudiosi, Zhou & Webb 2026 FRL 110340; Weiss et al. 2024 SSRN 5012508; Hoang & Phan 2026 FRL | reversal around the Deribit 08:00 UTC expiry; strongest with high ATM OI, negative gamma | "economically significant"; BTC cost 2.6-27 bp | 52 (Fri) | **screened K4** | 0.7 IS / 1.7 VAL |
| 6 | Blasco, Corredor & Satrústegui 2023 IREF | CME BTC expiry effect at the CF BRR window 15:00-16:00 London; side mine (basis unwind: short into, long after) | n/r | 12 | **screened K5** | signs flip |
| 7 | Wen, Gong, Ma & Xu 2020 EM; Wen, Indriawan, Lien & Xu 2022 EJ | crude ITSM: first half-hour (EIA days: 10:30-11:00) -> last half-hour, follow | n/r; XTI 3.3-8 bp | 200 + 50 | **screened K6**; near S1/S2 | < 0.4 |
| 8 | Jin, Kearney, Li & Yang 2019 JFutM | commodity ITSM, strongest in metals | n/r; XAU 1.0-1.4, XAG 4 bp | 250 | **screened K7**; near S1 | < 0.1 |
| 9 | Shen, Urquhart & Wang 2021 FinRev | BTC ITSM with a volume-defined session | n/r | 365 | near-tested (round 3, Wen 2022) | - |
| 10 | Baltussen, Da, Lammers & Martens 2021 JFE | gamma / LETF hedging -> momentum into the close | 1-3 bp | 250 | tested (r4, r6 S1) | - |
| 11 | Lenkey 2024 QFE (survey) | LETF rebalancing: effects "economically insignificant" | - | - | consistent with r3/r6 | - |
| 12 | Todorov 2023 RoF | VIX / commodity ETF leverage rebalancing | VIX futures | 250 | commodity part tested (S1); VIX futures not at IC | - |
| 13 | Anon. 2026 arXiv, "Preying on Leveraged ETFs" | Korean LETF close rebalancing, front-running | - | 250 | needs KOSPI (not in the data) | - |
| 14 | Schmid, Mayer, Wanner & Rathgeber 2022 EJF | BCOM/GSCI rebalancing | no price effect | 1 | not tested (negative paper, annual) | - |
| 15 | Hartzmark & Solomon 2022 NBER w30688 | dividend-payment days -> market up (reinvestment); multiplier 1.5-2.3 | top quintile of days 4x the bottom | ~50 high days | **untested, needs a dividend payment calendar** | unknown |
| 16 | Krohn, Mueller & Whelan 2024 JF | USD into / out of the fixes | ~1 bp | 250 | tested (r3, r4, r10 E) | - |
| 17 | Boyarchenko, Larsen & Whelan 2023 RFS | overnight drift at the European open | - | 250 | tested (r4, r10 D3) | - |
| 18 | Bondarenko & Muravyev 2023 JFQA | E-mini premium at the European open | - | 250 | tested (r8 X6a) | - |
| 19 | NY Fed SR 1188 (2026) | Treasury-auction intraday price pressure, reverses after | - | ~250 auctions | near-tested (r4 auction cycle, USDJPY/US30) | - |
| 20 | Pirrong 2023 JFutM | trade-at-settlement (TAS) positions push the settlement window | - | 250 | needs CME TAS data | - |
| 21 | Kurth, Eisler, Rej & Bouchaud 2026 arXiv | short-term trend dead since 2009 except on large-tick contracts | - | - | consistent with r3/r11 (no short trend) | - |
| 22 | Boos & Grob 2022 JFM | CTA positions = weighted past returns | - | weekly | near-tested (COT r4, r9) | - |
| 23 | Cespa, Gargano, Riddiough & Sarno 2022 RFS | low FX volume -> next-day reversal | - | 250 | near-tested (r3, tick count) | - |
| 24 | Ranaldo & Somogyi 2021 JFE; "Dealer risk limits" 2024 WP | FX order flow / dealer constraints | - | - | needs CLS or supervisory data | - |
| 25 | Ma, Bouri, Xu & Zhou 2025 GFJ | night session effect, Chinese gold/silver futures | - | 250 | near-tested (r10 A2, A6) | - |
| 26 | Schmidt & Kraft 2026 SSRN; "Spot BTC ETF flows" 2026 SSRN | BTC keeps New York hours after the spot ETFs; ETF flows -> returns | - | 250 | 2024+ only (HOLD era); needs ETF flow data | - |
| 27 | Lachowicz 2025 SSRN | Deribit gamma walls | - | - | needs Deribit OI history | - |
| 28 | Griffin & Shams 2018 RFS | VIX settlement (Wednesday SOQ) | on SPX options, not the index | 12 | not screened (low prior, rare) | < 1 |
| 29 | arXiv 2607.09426 | quarter-hour algorithmic openings | - | - | tested (r7 C) | - |
| 30 | Lou, Polk & Skouras 2019; Akbas et al. 2022 | overnight vs intraday tug of war | stock-level | - | index gap fade tested (r8 X2d) | - |

## Step 3: screens

Costs are the actual spreads at the entry and exit minutes, plus 0.6 bp commission for FX and metals. t is clustered
by UTC day. "Power" is the per-trade net Sharpe x sqrt(1.73 x trades a year). The chance column is a per-day sign
flip shared by all cells of the family: median / 95th percentile of the best |t_IS| at mid.

| family (source) | where | cells | best cell on the registered side (IS mid t >= 2 if any) | IS mid bp (t) / VAL mid | cost IS / VAL | net IS (t) / VAL (t) | power IS / VAL | best \|t_IS\| vs chance | verdict |
|---|---|---|---|---|---|---|---|---|---|
| K1 FX ITSM into 16:00 London / 15:00 Tokyo | 10 pairs | 81 | P2 (day) GBPUSD, \|z\| >= 1 | +2.03 (2.36) / +2.52 (2.40) | 0.81 / 0.72 | +1.22 (1.42) / +1.80 (1.72) | 0.76 / 1.31 | 4.21 (wrong side) vs 2.44 / 3.29 | **fails** IS t |
| K3 opening-range reversal (0DTE) | US30, USTEC (UK100 control) | 16 (+8) | none with IS mid t >= 2; US30 OR30 \|z\|>=1, 60 min | -2.65 (-1.28) / +4.26 (1.72) | 0.87 / 0.26 | -3.51 / +4.00 (1.62) | -0.9 / 1.2 | 2.03 (wrong side) vs 1.81 / 2.86 | **fails** |
| K4 Deribit 08:00 UTC expiry reversal | BTC (ETH info) | 12 | Fridays, all, fade 60 min | +20.58 (2.34) / +11.23 (3.13) | 11.56 / 3.29 | +9.02 (1.03) / +7.94 (2.20) | 0.68 / 1.67 | 2.34 vs 1.74 / 2.85 | **fails** DEMO (IS net t); lead below |
| K5 CME BTC expiry, BRR window | BTC (ETH info) | 2 | short 15:00-16:00 London | -21.0 (-1.34) / +22.0 (1.16) | 10.9 / 3.8 | -31.9 / +18.3 | < 0 | 1.40 vs 1.11 / 2.13 | **fails**, signs flip (long 16-17: +30.4 / -24.1) |
| K6 crude ITSM (Wen et al.) | XTI, XBR | 8 | none; XTI non-EIA all | +4.14 (1.14) / -3.73 (-1.93) | 7.2 / 3.3 | -3.06 / -7.03 | < 0 | 1.15 vs 1.63 / 2.58 | **fails** |
| K7 metals ITSM, first half-hour | XAU, XAG | 4 | XAG all / XAU all | +2.81 (3.94) / -0.88; XAU +0.76 (2.30) / +0.36 | 4.07 / 4.30; 1.44 / 0.99 | -1.26 / -5.18; -0.68 / -0.64 | < 0 | 3.94 vs 1.29 / 2.37 | **fails**: below cost; silver flips in VAL, as in round 6 S1 |

Other numbers worth keeping:
- **K1, pooled over the 10 pairs.**
  - Following the day's move into 16:00 London gives -0.24 bp (t -1.43) IS and +0.15 VAL.
  - Following the first London half-hour gives -0.21 / -0.22.
  - At the Tokyo close (JPY pairs) it gives -0.24 / -0.32.
  - In IS the USD-bloc pairs reverse into the London close instead (USDCHF -1.29 bp, t -4.21; EURUSD -0.90, t -3.24;
    AUDUSD -0.92, t -2.47). This is the wrong side, beyond the null's 95th percentile, and gone in VAL.
  - In VAL only, the JPY and GBP pairs follow big days: GBPJPY +3.62 (t 3.42), USDJPY +3.00 (t 3.05). This was seen
    after the fact; their IS is +1.2..+2.1 (t ~2.2), with net t <= 1.1.
- **K3, the 0DTE mechanism check.**
  - The US30 fade after a big 30-min opening range turns positive in VAL: +4.26 bp, and +2.85 (t 1.11) from 2022-05.
    USTEC goes the other way (VAL -0.5..-4.5).
  - The UK100 control shows no reversal in either era.
  - So the CFDs show no 0DTE reversal.
- **K6.** IS costs at 14:00-14:30 ET were 7-8 bp in XTI and 6.3 in XBR. On non-EIA days XTI follows through in IS
  (+4.1) and reverses in VAL (-3.7); XBR reverses in both (-2.1 / -3.5). EIA-day cells are |t| <= 0.65.

## The K4 lead (diagnostics are post hoc; HYPOTHESES_K.md, "K4 diagnostics")

| check | result |
|---|---|
| time placebo, Fridays, same rule shifted to 04-12 UTC (side recomputed) | IS: 08:00 is the largest cell (+20.6). The others run -2.5..+7.2, except 12:00 (+14.3, t 2.49). VAL: 08:00 +11.2 (t 3.13), but 06:00 and 07:00 also reach +10.3 / +9.6 (t 2.1 / 2.8). So in VAL the Friday-morning reversal is broader than the expiry hour |
| same on Mon-Thu (08:00 is a funding time every day) | 08:00 -3.2 / -0.8; no Mon-Thu hour has IS mid t > 2.3 |
| Friday minus Mon-Thu at 08:00 | +23.8 bp (t 2.55) IS, +12.0 bp (t 2.84) VAL |
| by year, net bp | 2018 -25.6 (cost 27) · 2019 +21.0 · 2020 -1.8 · 2021 +42.0 · 2022 -2.0 · 2023 +14.6 · 2024 +11.2 (4/7 > 0) |
| random-entry control (200 seeds, +-3 h, random Fridays, side recomputed) | beats 100 % (IS), 99.5 % (VAL) |
| spread x1.5 / +1 minute | +3.25 / +8.27 IS; +6.29 / +6.61 VAL |
| clipped at the IS 0.1/99.9 % | net +8.38 (t 1.02) IS, +7.94 VAL |
| sensitivity | predictor = the 07:30-08:00 settlement TWAP window: IS -1.3, VAL +5.2 (the TWAP window alone does not carry it). Exit 09:30: +26.4 (t 2.31) / +14.3 (t 3.18) mid. Quarterly expiries: IS +60 (n 15) / VAL +4.7 (n 12) |
| ETH, same rule | mid +3.2 (t 0.35) IS / +9.3 (t 2.02) VAL; IC's ETH spread was 145 bp IS, 14 bp VAL |
| correlation with C3, IS+VAL | daily -0.03, monthly -0.00 |

What it says:
- The mechanism fits: a reversal after the weekly expiry, absent on daily-expiry days that share the funding time.
- It cannot be a candidate:
  1. IS net t is 1.03, below DEMO's 2.0, at the era's own costs.
  2. IS mid t is 2.34, below this family's chance 95th percentile (2.85). Only VAL stands out.
  3. The diagnostics are post hoc.
  4. At about 52 trades a year and the VAL Sharpe of 0.18, the expected HOLD power is 1.7, so LIVE is out of reach
     even at today's ~2-3 bp BTC cost. That puts it in the DEMO tier at best: at 52 trades a year, t 2.5 needs about
     190 trades, roughly 3.7 years.
- The round-3 contamination list includes BTC hour-of-day means for 2025-26 (printed in round 3). This rule is a
  conditional reversal, not an hour mean, but anyone registering it should weigh that.

## What this adds to the standing diagnosis

- The 2018-2026 literature on intraday flows mostly maps onto mechanisms rounds 3-11 already tested. Of the 30
  candidates above, 6 untested families were screened, 9 need data the repo lacks, and the rest were tested or
  near-tested.
- **Intraday time-series momentum**, the most-cited new family, is absent from IC's FX at the London and Tokyo
  closes. In 2016-21 the USD bloc reverses into the London close instead. In crude and metals the papers' own
  predictors stay under cost (K6, K7), as round 6 S1 found with the whole-day predictor.
- **Derivative-expiry flows in crypto** are the one place where a literature mechanism shows up with the right sign
  in both eras (K4). It is held back by IC's 2018-21 crypto spreads, not by the mid edge. That is round 3's crypto
  intraday-momentum story again.

## Directions for the next round (the user decides on those that need data)

Untested here, on existing data:
- The K4 rule registered for **new data after 2026-09-24 / the demo account** (DEMO tier), with the side fixed
  (fade), Fridays only, 08:01 -> 09:00 UTC, and BTC at current costs. The full set of numbers is above.
- VIX settlement Wednesdays (Griffin & Shams 2018) in US30/USTEC at the 09:30 open: 12 a year, low prior.
- Shen, Urquhart & Wang's volume-defined BTC session ITSM: near round 3; only worth it at current costs.

Needs new data (user decision):
- **Deribit open interest / gamma history** (Tardis.dev or Laevitas, paid; Deribit's free API has current OI only).
  It would let K4 condition on the paper's own variable (high ATM OI, negative dealer gamma), which the abstract
  names as where the effect concentrates. This is the most promising use of new data from this stream.
- **S&P 500 dividend payment calendar** (CRSP or a vendor) for Hartzmark & Solomon's predictable price pressure:
  long the index on top-quintile payment days. It has a daily index-level signal and a published multiplier of
  1.5-2.3, and was never testable here.
- **Spot BTC/ETH ETF daily flows** (issuer files, 2024+), for flow pressure into the 16:00 ET NAV window. It falls
  only in VAL 2024 and HOLD, so it needs data after 2026-09.
- **CME TAS volume/positions, SPX 0DTE open interest (CBOE DataShop)**: dealer-gamma conditioning for the index
  rules (K3 found nothing unconditional).
- **KOSPI 200** (a symbol IC may list) for the Korean LETF front-running paper (2026).

## Scripts and outputs (scratchpad, not in the repo)

`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r12/K/`:
- `scripts/klib.py`: panel access, clocks, trade engine with fills at T+1, actual spreads, latency and spread x1.5,
  day-clustered t, permutation null.
- `scripts/k1_fx_itsm.py`, `k3_orr.py`, `k4567.py` (K4-K7), `k4_diag.py`: the screens.
- `scripts/oa_search.py`, `s2_search.py`, `oa_abs.py`: the literature queries.
- `out/k1.out`, `k3.out`, `K4.out`-`K7.out`, `k4_diag.out`: all cells with IS / VAL mid, cost, net, x1.5, +1 min,
  Sharpe, power, years, and the chance benchmark.
- `out/*_trades.pkl`: trade lists.
- `lit/`: the literature query files and results.
- `tested_list.md`: what rounds 3-11 tested.
