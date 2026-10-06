# Round 16, stream W: cross-border income conversion flows (dividend seasons, coupon and redemption dates)

Hypotheses, with UTC times written before their numbers: [HYPOTHESES_W.md](HYPOTHESES_W.md) (registered 02:28 UTC,
post hoc PH1-PH2 at 02:34 UTC). Eras: PRE 2004-15 (Dukascopy: M1 bid for USDJPY, USDCHF and EURUSD; H1 bid for
AUDUSD and GBPUSD), IS 2016-21 and VAL 2022-24 (IC panel mid). HOLD was never loaded. The panel ends 2024-12-31,
every price lookup refuses t >= 2025-01-01, and no window ends in 2025.

## Answer

**No candidate. No cell meets DEMO or LIVE on its registered side, so there is no PREREG_DRAFT.**
- Cells: 18 registered, plus 2 pooled. Post-hoc information: PH1 and PH2.
- Best registered-side IS net t: **1.52**. This is W4b: short EURUSD into the 16:00 London (WM/R) fix on
  euro-dividend-season days. Gross it was +1.72 bp a trade (t 2.37 on 6 season blocks). VAL fell to +1.06 bp
  (t 0.49), PRE was +0.37, and the net needs > 0.6 bp. It fails DEMO.
- The largest |t| was on the wrong side: W2b, IS t -2.28. The sign-flip null puts max |t_IS| at p50 2.36 and p95
  4.66, so it is chance.
- This was expected before looking. Zheng's (2023) dividend-repatriation effect is about 5 bp over t+1..t+3. A
  1-5-day FX window has sd 60-450 bp per block, and the minimum detectable effect is 50-300 bp per block. Seasonal
  blocks (1-2 a year per country) cannot reach DEMO, so DEMO at best was always the ceiling, and these did not reach
  it. LIVE was impossible by arithmetic: at Zheng's size, power is about 0.3.

## Literature and calendars
| source | what it gives |
|---|---|
| Zheng, J. (2023), "Dividend Flows and the Foreign Exchange Rate", U. Chicago JMP; PhD thesis 2024 (knowledge.uchicago.edu record b5epc-yqe79); SSRN 6415558 | The only direct evidence found. G10, 2001-23, company dividend dates (Compustat Global, CRSP). On a country's top-5 % payment days the currency falls vs USD by -1.5 bp at t0, -4.7 bp at t+2 (se 1.9) and -6.5 bp at t+8. Nothing happens before the date. Post-GFC t+2 is -7.4 bp; pre-GFC it is -1.5 bp. Mechanism: total-return-index funds repatriate dividends once the cash arrives. Index methodology converts at the WM/R 16:00 fix. A US ETF sold JPY 2 business days after Japanese interim dividends (Dec 2022). Strategy "sell k for 1 day after top-5 % days": 4.4 %/yr, Sharpe 0.68 at a 1 bp cost. Concentration: JP June and December, EUR May, CH 50 % of dividends in 2.5 days |
| Hartzmark & Solomon (2022, RFS), "Consuming Dividends"; Schmickler (2022), cited by Zheng | Payment-date reinvestment pressure in equities, not FX |
| Mollick & Soydemir (2008), Global Economy Journal | Japanese net Treasury purchases move USDJPY. No coupon-date result |
| Bloomberg 2019-04-08; KED Global 2022-04-18 | The KRW weakens in the April dividend season. KRW is not tradable here |
| JPX "定時株主総会開催日集計結果" (kako.pdf, 2002-2025) | Daily AGM counts of March-FY companies. Payment date = next TSE day after the AGM. Top AGM day: 64 % of AGMs in 2004, 26 % in 2023 |
| digrin.com, dividendmax.com, dividendhistory.org | SIX payment dates for Nestle, Novartis and Roche, 2004-24. Before 2010 there is only one date per year, treated as the payment date. Novartis 2008 = ADR ex-date + 3 business days |
| Conventions, not fetched | US refunding coupons on 15 Feb/May/Aug/Nov; JGB 10-year redemptions on 20 Mar/Jun/Sep/Dec; OAT on 25 Apr/Oct; Bund on 4 Jan/Jul |

OpenAlex and Semantic Scholar searches (14 queries) found nothing else on dividend-season, coupon-date or
redemption-date FX effects. They also found no BIS or central-bank note with magnitudes.

## Conventions
- **Side**: sell the currency in which the income is paid, against USD. The side comes from who receives the cash
  (a foreign holder who repatriates), never from the data.
- **Conversion days**: P+1..P+3 local business days after payment, following Zheng's step.
- **Measures**:
  - "3day" = 16:00 London on P to 16:00 London on P+3.
  - "held" = seasonal days held 16:00 London to 16:00 London, in chunks of <= 5 days, one round-trip cost per
    chunk.
  - "fix" = 15:45 -> 16:00 London on each conversion day. PRE AUD and GBP use H1 data, so their fix is the hour
    15:00 -> 16:00.
- **JPY**:
  - Gotobi days (as `gotobi_days`) are never used.
  - Returns are measured only from 03:00 UTC to 16:00 London on each non-gotobi day: intraday, no rollover.
  - This never touches the Tokyo fix (00:55 UTC +- 1 h) or C3's legs (18:00 UTC -> 00:55 -> 02:55). The cost:
    Japanese-side conversions at the Tokyo TTM are not captured.
- **Costs**: half the spread at entry and exit, 0.6 bp commission, swap from `swap_frac_at`. PRE uses IC's
  2016-17 median spread by minute.
- **t**: across event blocks. A block is one season per year, or one exact-date event; Swiss events within 10 days
  merge into one block. Block value = the sum over its trades (bp per unit).
- **Power** = block net Sharpe x sqrt(blocks a year x 1.73).

## Results (registered side; gross bp per block (t); net = after costs)

| cell (mechanism) | where | PRE g (t) | IS g (t) | VAL g (t) | cost/trade IS/VAL | net IS (t) / VAL (t) | VAL/IS | power IS / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|
| W1a Swiss big-3 dividends, 3-day | USDCHF long | -37.6 (-1.12) | -29.6 (-1.20) | +80.4 (2.52) | 0.0 / -1.5 | -29.7 (-1.20) / +82.3 (2.57) | -2.71 | -0.64 / 1.95 | fails (IS wrong sign) |
| W1b same, fix | USDCHF | -0.2 (-0.04) | +5.4 (0.63) | +2.2 (0.83) | 0.93 / 0.79 | +2.3 (0.27) / -0.9 | 0.39 | 0.15 / -0.30 | fails |
| W2a JP June (AGM+1 = payment), daytime | USDJPY long | -16.3 (-0.68) | +7.6 (0.43) | +84.9 (1.96) | 0.74 / 0.71 | +5.6 (0.32) / +82.1 (1.91) | 11.2 | 0.17 / 1.45 | fails (IS t); 3 VAL blocks |
| W2b same, fix | USDJPY | +3.7 (1.23) | -2.5 (-1.29) | +14.0 (2.60) | 0.70 / 0.74 | -4.3 (-2.28) / +11.0 (2.21) | -5.7 | -1.22 / 1.68 | fails (IS wrong sign) |
| W3a JP December, daytime | USDJPY long | -3.3 (-0.07) | -13.4 (-0.68) | -52.2 (-0.74) | 0.72 / 0.70 | -17.4 / -55.9 | 3.9 | < 0 | fails |
| W3b same, fix | USDJPY | +13.1 (1.36) | +7.2 (0.86) | -10.3 (-0.68) | 0.69 / 0.70 | +3.3 (0.39) / -14.0 | -1.42 | 0.21 / -0.69 | fails |
| W4a euro area May, held | EURUSD short | +102 (0.93) | -49.6 (-0.45) | +25.0 (0.18) | 0.37 / 0.11 | -51.1 / +24.5 | -0.50 | -0.25 / 0.13 | fails |
| **W4b same, fix** | EURUSD short | +7.4 (0.67) | **+34.5 (2.37)** | +21.5 (0.49) | 0.63 / 0.61 | **+21.9 (1.52)** / +9.2 (0.21) | 0.63 | 0.82 / 0.16 | fails DEMO (net IS t < 2); +1.72 / +1.06 / +0.37 bp per trade IS / VAL / PRE |
| W5a Australia Mar-Apr / Sep-Oct, held | AUDUSD short | -69 (-0.74) | -89 (-1.02) | +167 (1.58) | 4.07 / 2.27 | -104 / +159 | -1.87 | -0.63 / 1.15 | fails |
| W5b same, fix | AUDUSD | -7.6 (-0.21) | +1.7 (0.12) | +6.5 (0.38) | 0.91 / 0.67 | -12.5 / -4.0 | 3.8 | < 0 | fails |
| W5c Australian banks Jul / Dec, held | AUDUSD short | +4.8 (0.13) | -23.6 (-0.50) | -41.1 (-0.38) | 3.29 / 2.00 | -29.9 / -44.8 | 1.74 | < 0 | fails |
| W5d same, fix | AUDUSD | +6.8 (0.87) | +4.3 (0.64) | -1.9 (-0.13) | 0.85 / 0.68 | -2.1 / -7.2 | -0.45 | < 0 | fails |
| W6a pool of the 1-5-day cells | all | -14.3 (-0.54) | -37.2 (-1.56) | +53.2 (1.42) | 1.85 / 0.92 | -42.4 (-1.76) / +50.5 | -1.43 | -0.94 / 1.03 | fails |
| W6b pool of the fix cells | all | +2.4 (0.30) | +6.8 (1.55) | +4.2 (0.66) | 0.81 / 0.68 | -0.2 / -1.9 | 0.62 | < 0 | fails |
| W7a US refunding coupons (15 Feb/May/Aug/Nov), D-1 -> D+2 (near-repeat of round 13 N2b) | short USD vs EUR GBP AUD CHF | -16.3 (-1.35) | +9.8 (0.75) | +16.7 (0.74) | 3.3 / 3.8 | +6.5 (0.49) / +12.9 | 1.71 | 0.27 / 0.43 | fails |
| W7b same, fix D..D+2 | same | -4.5 (-1.84) | +3.9 (1.76) | +6.9 (1.90) | 0.79 / 0.68 | +1.5 (0.69) / +4.9 (1.33) | 1.79 | 0.37 / 1.01 | fails (net IS t; PRE opposite) |
| W8a OAT / Bund redemption days, D-1 -> D+2 | EURUSD short | +14.8 (0.80) | +4.8 (0.32) | +25.9 (0.88) | 0.30 / 0.19 | +4.5 (0.30) / +25.7 | 5.4 | 0.16 / 0.66 | fails |
| W8b same, fix | EURUSD | +0.6 (0.21) | +2.3 (0.70) | +2.8 (0.65) | 0.63 / 0.61 | +0.4 / +0.9 | 1.21 | 0.07 / 0.17 | fails |
| W9a JGB 20th redemptions, D+1..D+3 non-gotobi, daytime | USDJPY long | +3.1 (0.32) | +3.9 (0.30) | +7.0 (0.37) | 0.74 / 0.73 | +2.1 / +5.3 | 1.82 | 0.09 / 0.21 | fails |
| W9b same, fix | USDJPY | +2.2 (1.28) | +2.8 (1.03) | +3.2 (0.87) | 0.72 / 0.71 | +1.0 (0.39) / +1.5 | 1.15 | 0.21 / 0.31 | fails |

Block counts PRE / IS / VAL:
- 12 / 6 / 3 for the June, December and May seasons.
- 24 / 12 / 6 for Australia.
- 28 / 16 / 7 for the Swiss blocks.
- 48 / 24 / 12 for the coupon, redemption and JGB dates.

The x1.5 spread and +1 minute variants change no verdict; see `out/screen_out.txt`. Every cell's year-by-year
numbers are in the same file. Years net > 0 in IS + VAL is at most 8 / 9 (W7b); otherwise 3-6 / 9.

## Controls
- **Random entries.** Each block is moved by 7k days inside its year with the rule re-applied, over 300 seeds.
  - W4b: 92 % IS, 99 % VAL.
  - W7b: 96 % / 96 %.
  - W9b: 98 % / 82 %.
  - Everything else: below 90 % in IS, or the cell is negative.
  - No cell pairs >= 90 % random with IS net t >= 2.
- **Time placebo.** The same rule is shifted k = +-1..+-5 months (`out/placebo_out.txt`).
  - W7b ranks 1/11. Its +-3 shifts land on the same quarterly months; the other 15ths give t -1.8..+0.8.
  - W4b ranks 2/11, but the December shift (k = -5) is stronger: t 5.0.
  - W2a ranks 2/11. The other cells rank in the middle.
- **Other currencies on the same dates.** Zheng predicts no cross effect. Selling AUD, NZD and CAD on W7b's days
  also loses in IS + VAL (t -3.2..-3.9), so W7b is a broad USD move into the fix on those days, not a coupon-holder
  currency effect. In PRE the sign reverses (t +1.4..+2.2).
- **Multiple testing.** 18 registered cells. Observed max |t_IS net| is 2.28 (wrong side). The sign-flip null
  (per ISO week, shared, 2,000 draws) gives p50 2.36 and p95 4.66; 60 % of draws exceed the observed value.
  Nothing stands out from chance.

## Per family: best cell, cells, chance
| family | cells | best registered IS net t (cell) | its VAL | verdict |
|---|---|---|---|---|
| W1 Swiss exact dividend dates | 2 | 0.27 (W1b) | -0.9 bp | none |
| W2 Japan June (JPX AGM calendar) | 2 | 0.32 (W2a) | +82 (t 1.91, 3 blocks) | none |
| W3 Japan December | 2 | 0.39 (W3b) | -14 | none |
| W4 euro area May | 2 | 1.52 (W4b) | +9.2 (t 0.21) | none (closest) |
| W5 Australia | 4 | < 0 | | none |
| W6 pools | 2 | -0.05 | | none |
| W7 US refunding coupons | 2 | 0.69 (W7b) | +4.9 (t 1.33) | none; PRE opposite |
| W8 euro sovereign redemptions | 2 | 0.30 | | none |
| W9 JGB redemptions | 2 | 0.39 | | none |

## Decay and era consistency
- No cell has the same sign with t > 1 in PRE, IS and VAL.
- W9b comes closest: +2.2 / +2.8 / +3.2 bp per block, t 1.28 / 1.03 / 0.87. That is about +1.2 bp a trade
  against a 0.72 bp cost. It is too weak (net t 0.39), and it is not a yen effect. On the same days the USD rises
  into the London fix against the other currencies too: selling them gives t +0.4..+3.1.
- W4b's per-trade gross runs +0.37 (PRE), +1.72 (IS), +1.06 (VAL). It peaks in IS and is not structural.
- W7b runs -1.50 / +1.29 / +2.31 bp a trade, with the PRE sign opposite.
- Expected HOLD t on the VAL size is below 1.1 for every cell. W1a, W2a, W2b and W5a show VAL power 1.15-1.95, but
  all four are wrong-signed or flat in IS and PRE. That is VAL-only noise on 3-7 blocks.

## Post hoc (information only)
- **PH1, Swiss exact dates, event path.** Cumulative USDCHF from P-1, pooled over 63 events:
  - +8.5 bp at t0, +12.4 at t+2 (t 1.0), then -18 at t+8.
  - There is no Zheng-like CHF depreciation step. The PRE floor years 2011-15 are included.
  - Minimum detectable effects (80 % power): 60-90 bp per 3-day trade, 2-7 bp per fix trade, against Zheng's ~5 bp
    per 3 days. The 1-5-day cells could never have detected the published effect.
- **PH2, W7b decomposition.**
  - No consistent day: D+0 is VAL's (+4.9 bp, t 2.6); D+2 is IS's (+2.6, t 2.4).
  - Legs: AUD and GBP carry it.
  - Baseline on other US/UK days: -0.35 (IS) / +0.17 (VAL) bp.
  - The 15th..+2 of the 8 non-refunding months: -1.31 (PRE, t -1.95), -0.52, -0.18.
  - The refunding-quarter days do differ from other 15ths in IS/VAL, but they reverse in PRE. Not registrable.

## What this says
- Income conversion flows exist (Zheng). At the size the literature reports (5-7 bp over days), they are an order of
  magnitude below what 1-5-day FX noise lets anyone detect or trade with 1-2 seasonal blocks a year, even before
  IC's costs.
- The fix-minute version has the power: MDE 2-3 bp a trade. It shows no season-specific conversion at the London
  fix beyond the general clock effects of rounds 13-15.
- The approximations are blunt: Japan from AGM days, other countries from documented windows.
- Zheng's own strategy (about 60 position-days a year in 10 currencies) would at best be DEMO at IC's costs:
  - per-trade Sharpe about 0.1 gross, about 0.07 net of ~1.3 bp;
  - power about 0.9-1.3.
  - NOK and SEK, two of its ten currencies, are not on IC.

## Directions that need the user's decision
1. **Company-level dividend calendars** (Compustat Global, Bloomberg DVD or Refinitiv) for G10, 2004-24. This is
   needed to rebuild Zheng's top-5 % payment days exactly. The expected result is still DEMO at best, by the
   arithmetic above.
2. **EM pairs with concentrated dividend seasons**: KRW in April, TWD in July-August. These need new symbols and
   price series.
3. Not a user decision, and not done: Treasury coupon **amounts** per payment date (fiscaldata auctions, as round 13
   N built for settlements) for a W7b dose test. The prior is low, given the PRE reversal and the cross-currency
   result.

## Process
- **Before the hypotheses.** Calendars were built with no prices loaded:
  - JPX AGM history, parsed with each year resolved by its printed weekday;
  - Swiss payment dates from three aggregators, cross-checked against each other.
- **Hypotheses.** Registered at 02:28 UTC; screen, controls, then post-hoc PH1-PH2 written at 02:34 UTC.
- **C3 correlation.** Not computed: no cell survived.
- **Network.**
  - OpenAlex and Semantic Scholar (Semantic Scholar partly rate-limited);
  - knowledge.uchicago.edu (Zheng's thesis PDF);
  - jpx.co.jp;
  - digrin.com, dividendmax.com, dividendhistory.org;
  - web search.
  No prices were downloaded.

Scripts and outputs (session scratchpad,
`/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/9c63906c-bbbf-42bd-9a64-431d9d3f5de1/scratchpad/r16/W/`):

| file | what it does |
|---|---|
| `code/lit.py`, `code/s2.py`, `code/oa_abs.py` | literature searches (outputs in `lit/`; Zheng's thesis text in `lit/zheng.txt`) |
| `code/cal_jp_agm.py` | JPX AGM distribution -> `cal/jp_agm.json` |
| `cal/ch_div.json` | Nestle, Novartis and Roche payment dates |
| `code/libW.py` | loaders (panel, Dukascopy M1/H1), calendars, gotobi set, costs, swap; refuses HOLD |
| `code/calW.py` | the 18 registered cells' blocks and trades, with a month-shift parameter for placebos |
| `code/evalW.py` | per-block gross and net, era summaries |
| `code/screen.py` | main screen and variants -> `out/screen_out.txt`, `out/screen.pkl` |
| `code/placebo.py` | random entries, time placebo, cross-currency placebo, day-clustered t, sign-flip null -> `out/placebo_out.txt` |
| `code/posthoc.py` | PH1 and PH2 -> `out/posthoc_out.txt` |
