# Round 46, stream P: 60/40 threshold / calendar rebalancing and risk-parity de-leveraging with the bond leg (2026-10-30)

Brief: [BRIEF.md](BRIEF.md) row P, plus round37_forced_flows/BRIEF.md. All 17 cells were declared in
[HYPOTHESES_P.md](HYPOTHESES_P.md) between 07:53 and 07:54:22 UTC (file mtime), before any return was computed. The first grading run
started at 07:57:41 UTC. No cell was added or changed after that. HOLD stayed closed:
- Treasury requests stop at 2024.
- MoF and Bundesbank rows after 2024-12-31 were dropped at parse. Only row counts were printed.
- IC M1 was cut at ts < 1735689600000 at load.

Written 2026-10-30 07:59 UTC.

## Answer

**No candidate at LIVE or DEMO, and no PREREG_DRAFT.** Adding the bond leg does not rescue round 23's P2.

- The primary cell is F1-thr-all-full: the paper's Threshold signal built from US500 and the 10-year Treasury, short
  the index when the fund is overweight equities. It is **-0.0 bp mid and -2.1 bp net in IS (t -0.68)**. VAL is
  +6.1 (t 1.35), and all of VAL is 2022.
- No cell has an IS net t above +0.27. The best IS mid |t| (1.19) is below the F1 family's sign-flip null median
  (1.48), and below the max-of-17-normals median (2.05).

The bond leg changes the signal: its correlation with round 23's equity-only signal is 0.83. It does not change the
outcome. In the paper's own spread, stock minus bond, the bond leg adds +0.4 bp in IS and -0.4 bp in VAL, so the
missing piece was not the bond leg.

The linear slope does exist in this sample: IS equity -20 bp per sd (t -2.57), about the paper's -15.9. But it comes
from turmoil days. A signal-sized position (post hoc, information only) makes +3.7 bp per unit lot in IS (t 0.74),
and -4.3 (t -1.46) once March-April 2020 is removed. This matches the paper's own skewness of 5.23.

## Sources (robots.txt read before any data request)

| host | robots.txt | fetched | span used | status |
|---|---|---|---|---|
| home.treasury.gov | `User-agent: * Allow: /` | daily par yield curve CSV, one file per year | 2004-2024 (21 requests) | used: 10Y and 3M |
| www.mof.go.jp | 404 (no rules) | `jgbcme_all.csv` (JGB par yields) | 2014-2024 used, later rows dropped at parse | used: 10Y |
| api.statistiken.bundesbank.de | 404 (no rules); www.bundesbank.de disallows only `/.enodia/challenge` | BBSIS Svensson 10.0-year yield on Federal securities, daily, `endPeriod=2024-12-31` | 2014-2024 | used |
| www.nber.org | `*` rules only, no AI-bot block | w33554 PDF, full text | - | read (Appendix B construction, Tables 1, 3, 6) |
| data-api.ecb.europa.eu | **disallows ClaudeBot / Claude-Web / anthropic-ai** | nothing | - | off limits |
| cdn.cboe.com | robots.txt answers 403 | nothing | - | treated as off limits (no SPX PRE 2004-15) |

The whole pull was 31 requests, < 4 MB, about 2 minutes. No web.archive.org, no logins, no e-mail in any request,
and a generic research UA. There is no PRE row because no index price history before 2016 was reachable within the
rules: IC M1 starts in 2016 and CBOE was skipped.

## Results (bp per trade; t clustered by entry date; costs = actual IC spreads at both fills, swaps per 17:00 NY rollover, 0.6 bp FX commission)

Column notes:
- pow = per-trade net Sharpe x sqrt(1.73 x trades/yr), at the VAL size.
- ctrl = the share of 200 random-entry seeds the cell's net beats, IS / VAL. Every-day cells use random sides with the
  cell's long share on the same days. Event cells use random non-event days with the side set by the rule.

| cell | where | IS mid (t) | IS net (t) | VAL mid (t) | VAL net (t) | cost IS/VAL | n/yr | x1.5 IS/VAL | +1 min IS/VAL | ex-2020-03/04 IS (t) | pow VAL | ctrl | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **F1-thr-all-full** (primary) | US500 | -0.0 (-0.00) | -2.1 (-0.68) | +7.0 (1.53) | +6.1 (1.35) | 2.1/0.8 | 196 | -3.1/+5.7 | -2.8/+5.9 | -3.9 (-1.55) | 1.02 | 98/100* | none |
| F1-thr-all-lag (paper close-to-close) | US500 | +3.7 (1.19) | +0.5 (0.18) | +4.4 (1.09) | +3.3 (0.81) | 3.1/1.1 | 244 | -0.3/+3.0 | -0.1/+2.9 | -4.4 (-1.81) | 0.62 | 100/100* | none |
| F1-thr-top-full (top tercile) | US500 | -0.0 (-0.00) | -2.2 (-0.36) | +8.0 (1.10) | +7.2 (0.99) | 2.2/0.8 | 71/60 | -3.3/+6.8 | -3.4/+7.6 | -7.7 (-1.96) | 0.75 | 48/60 | none |
| F1-cal-wk4-full | US500 | +1.2 (0.21) | -0.9 (-0.15) | +2.4 (0.24) | +1.6 (0.16) | 2.1/0.8 | 47 | -1.9/+1.2 | -2.3/+0.7 | -0.5 (-0.09) | 0.12 | 60/44 | none |
| F1-combo-full (paper Table 6 position, sign) | US500 | -0.3 (-0.11) | -2.4 (-0.79) | +6.1 (1.34) | +5.3 (1.16) | 2.1/0.8 | 196 | -3.5/+4.9 | -3.3/+4.9 | -4.7 (-1.88) | 0.88 | 94/95* | none |
| F1-paperreg-full (paper Table 1 coefficients incl. momentum) | US500 | +3.0 (0.86) | +1.0 (0.27) | -5.3 (-1.16) | -6.1 (-1.34) | 2.0/0.8 | 169/197 | -0.0/-6.5 | +0.4/-6.6 | -3.0 (-1.09) | <0 | 88/12 | none |
| F1-thr-pool3-full | US500+USTEC+US30 | +0.8 (0.24) | -1.2 (-0.38) | +7.6 (1.63) | +6.9 (1.48) | 2.0/0.7 | 589 | -2.2/+6.6 | -2.0/+6.8 | -3.2 (-1.21) | 1.85** | 100/100* | none |
| F2-rp20-1d (RP equity cut, bottom decile) | US500 | -4.5 (-0.27) | -6.6 (-0.41) | +16.0 (1.06) | +15.2 (1.01) | 2.2/0.8 | 19 | -7.7/+14.8 | -7.4/+14.6 | -11.6 (-1.23) | 0.76 | 62/94 | none |
| F2-rp60-1d | US500 | -2.6 (-0.15) | -4.8 (-0.28) | +1.6 (0.10) | +0.8 (0.05) | 2.2/0.8 | 20 | -5.9/+0.4 | -5.4/-0.0 | -6.9 (-0.68) | 0.04 | 76/68 | none |
| F2-rp20-3d | US500 | +0.8 (0.03) | -3.5 (-0.12) | +26.2 (0.85) | +25.5 (0.83) | 4.3/0.7 | 17 | -4.5/+25.1 | -4.4/+24.3 | -34.1 (-1.61) | 0.63 | 85/94 | none |
| F2-rp60-3d | US500 | +9.7 (0.32) | +5.3 (0.18) | +3.5 (0.13) | +2.5 (0.09) | 4.4/0.9 | 17 | +4.2/+2.1 | +6.2/+1.6 | -41.8 (-2.14) | 0.07 | 97/72 | none |
| F3-JP-thr-all-lag (JP225 + JGB 10Y) | JP225 | +1.5 (0.46) | -3.3 (-1.01) | -1.6 (-0.32) | -5.1 (-1.00) | 4.8/3.5 | 239 | -4.9/-6.0 | -3.7/-5.9 | -1.1 (-0.36) | <0 | 90/51 | none |
| F3-DE-thr-all-lag (DE40 + Bund 10Y) | DE40 | +1.9 (0.60) | -0.6 (-0.18) | -3.0 (-0.77) | -4.5 (-1.17) | 2.5/1.5 | 252 | -1.0/-4.7 | -0.6/-4.6 | -0.3 (-0.12) | <0 | 86/34 | none |
| F3-US2intl (US signal -> next local open-close) | JP225+DE40 | +0.3 (0.21) | -1.7 (-1.08) | +0.8 (0.36) | -0.3 (-0.13) | 2.0/1.1 | 487 | -2.7/-0.8 | -2.5/-1.1 | -2.4 (-1.64) | <0 | 76/82 | none |
| F3-rp60-1d-JPDE | JP225+DE40 | +1.7 (0.16) | -1.9 (-0.17) | -0.5 (-0.03) | -2.6 (-0.15) | 3.6/2.1 | 54/48 | -2.9/-3.1 | -1.4/-2.2 | -10.2 (-1.37) | <0 | 89/66 | none |
| C-USDJPY (placebo) | USDJPY | +1.2 (0.87) | -0.1 (-0.09) | -2.1 (-0.83) | -3.9 (-1.53) | 1.3/1.8 | 239 | -0.2/-4.0 | -0.1/-4.0 | -0.3 (-0.26) | <0 | 90/46 | control |
| C-EURUSD (placebo) | EURUSD | -1.2 (-1.11) | -2.1 (-1.92) | -2.4 (-1.31) | -3.2 (-1.75) | 0.9/0.8 | 252 | -2.1/-3.2 | -2.2/-3.2 | -1.6 (-1.49) | <0 | 12/3 | control |

\* For the every-day cells the control randomises only the side, keeping the rule's long share (16-22 %). A random
mostly-short mix pays the index drift, so "beats 98-100 %" does not offset a negative net. It is the round 23
caveat again.

\*\* For the pooled cell, power counts three correlated (~0.9) trades per day, so it is overstated.

Net per trade by year. F1 runs 2016-24; F1-paperreg starts in 2017; F2 is the 1-day cells.

| cell | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| F1-thr-all-full | +1.7 | -8.4 | -2.7 | -2.4 | -0.6 | +0.3 | **+22.4** | +3.7 | -7.8 |
| F1-thr-all-lag | +3.3 | -4.9 | -0.8 | -9.0 | **+17.5** | -2.9 | **+15.6** | +3.1 | -8.8 |
| F1-paperreg-full | - | -4.5 | +2.0 | -5.7 | +14.2 | -2.0 | -9.7 | -7.5 | -1.2 |
| F2-rp20-1d | +3.2 | -5.1 | -5.0 | -32.5 | +18.4 | -19.1 | +55.0 | -2.7 | -6.7 |
| F2-rp60-1d | -29.0 | -3.0 | +20.0 | -52.1 | +15.1 | -18.0 | +34.1 | -19.1 | -20.3 |

Every rebalancing cell has 3-5 positive years out of 9. The positive years are 2020 (the March-April crash and
rebound) and 2022 (when stocks and bonds fell together). This is the paper's turmoil concentration: skewness 5.23,
and Sharpe falls from 1.11 to 0.90 without 2008-09 and 2020-03. Each 1-day cell pays one IC round trip (0.8-2 bp at
US500, 3.5-4.8 at JP225) on every day, including the many quiet ones.

## Cells tried and chance

- 17 declared cells: F1 7, F2 4, F3 4, controls 2. Max |t| of 17 normals has a median of 2.05 and a 95th percentile
  of 2.97.
- Family sign-flip null on IS mid t (500 draws, flips per entry date shared across the family):

| family | cells | best IS mid \|t\| | null median / 95th |
|---|---|---|---|
| F1 threshold / calendar (US) | 7 | 1.19 | 1.48 / 2.63 |
| F2 risk-parity de-leveraging | 4 | 0.32 | 1.22 / 2.40 |
| F3 Japan / Germany | 4 | 0.60 | 1.38 / 2.51 |
| controls | 2 | 1.11 | 1.01 / 2.11 |

Nothing is above its null median. The best IS net t on a declared side is +0.27 (F1-paperreg). The DEMO bar needs
2.0, and LIVE needs 2.5 plus power 3. The power arithmetic in HYPOTHESES_P.md already ruled LIVE out a priori: an
every-day cell needs ~16-17 bp net per day, above the paper's full ~13 bp mid.

## Information rows

- **The paper's regression in our data.** HC t; US500 next close-to-close return, and XA = US500 minus the 10y bond
  next day, both on the standardised Threshold signal. Paper Table 3: equity -15.9, XA -20.

  | era | equity, univariate | equity, with Mom | bond | XA | Mom coefficient |
  |---|---|---|---|---|---|
  | IS | -20.3 bp/sd (t -2.57) | -31.6 (t -2.69) | +1.0 (t 0.41) | -21.3 (t -2.23) | +26 bp (t 1.84) |
  | VAL | -9.4 (t -1.86) | -1.6 (t -0.20) | +3.6 (t 1.35) | -13.0 (t -2.36) | -15 bp |

  The equity-leg share of the XA slope is ~95 % in IS and ~72 % in VAL; the paper's is 80 %. The slope is real in
  IS, but it is a tail effect:
  - **Sign rule:** IS mid ~0. The rule is short 84 % of days and pays the drift.
  - **Size-weighted position** (post hoc, never a cell; -z capped at 3, lag timing, net per unit lot): IS +3.7
    (t 0.74), VAL +4.6 (t 1.00). IS without March-April 2020 is -4.3 (t -1.46). By year it is 2020 +30.3,
    2022 +17.7, and the other 7 years between -7.6 and +5.3.
- **Sign rule split into legs** (close-to-close mid):
  - IS: equity +1.55 (t 0.50), bond +0.36, XA +1.92 (t 0.52).
  - VAL: equity +6.38 (t 1.58), bond -0.42, XA +5.96 (t 1.37).
- **Signals:**
  - Threshold sd: US 0.43 %, JP 0.45 %, DE 0.44 % (paper ~0.5 %).
  - Correlation with the equity-only signal of round 23: US 0.83, JP 0.94, DE 0.84.
  - Correlation of the "full" signal (bonds through day t) with the "lag" signal (bonds through t-1): 0.90.
- **RP triggers vs equity-only vol-control:** 56-68 % of risk-parity cut days are also bottom-decile days of the
  equity-only inverse vol, so F2 is largely round 23 P1 again.
- **C3 correlation:** not computed, because no cell survives.

## Pitfalls

- **The 20:00 NY entry drops Fridays.** IC is shut over the weekend, which removes 423 Friday signals (~20 % of
  days) from every "full" cell, so n/yr is 196, not 250. The lag-timing cells keep every day and fail the same way.
  A Friday rule would have to enter at the Sunday reopen.
- **Bond and yield files:**
  - MoF `jgbcme_all.csv` is Shift-JIS with a title row before the header, and 10Y is "-" before 1986.
  - Bundesbank BBSIS has rows for every calendar day, with "." on non-trading days, and runs to the current date
    (cut at parse).
  - Treasury per-year CSVs list the newest date first. 2004-05 have no 30-year column.
- **Robots:** data-api.ecb.europa.eu names ClaudeBot, Claude-Web and anthropic-ai, so the ECB yield curves are off
  limits. The Bundesbank SDMX API (no robots.txt) is the substitute for Bund yields. cdn.cboe.com answers 403 to
  robots.txt.
- **Publication times not verified:**
  - The "full" US timing assumes the Treasury par curve (15:30 ET quotes) is out by 18:00 ET. It makes no difference
    here, because the lag-bond variant fails too.
  - MoF and Bundesbank publication times were not checked, so Japan and Germany use lagged bonds only.
- **Slope vs trade:** a significant linear slope (t -2.6) can coexist with a zero sign-rule P&L when the slope comes
  from a few turmoil days. Grade the trade you can place, and report it with and without March-April 2020.

## Directions that need the user

| direction | value |
|---|---|
| A bond CFD / futures venue (TY or Bund futures) to trade the XA spread the paper measures. The bond leg added nothing here (+0.4 / -0.4 bp), so this is not worth an account. | LIVE < 1 %, DEMO ~1 % |
| Paid long S&P / Treasury futures history (Bloomberg ES1 / TY1, 1997-2015) for a PRE replication of the turmoil concentration. It could only confirm a rare-event (2008 / 2020 / 2022) effect, which no 21-month holdout can grade. | LIVE < 1 %, DEMO ~2 % |

Nothing else in this row is open. Quarter-end strengthening means ~4 events a year, with no power. Using 2-year or
30-year bonds is the same construction with a different duration, and since the bond leg carries none of the effect
it would not change the verdict.

## Files

- Round folder: [HYPOTHESES_P.md](HYPOTHESES_P.md), STREAM_P.md (this file). There is no PREREG_DRAFT.
- Scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r46/P/`:
  - Scripts: `scripts/fetch.py`, `scripts/parse_yields.py` (HOLD cut at parse), `scripts/lib46.py`,
    `scripts/build.py` (signals), `scripts/run.py` (17 cells, controls, nulls, regression), `scripts/posthoc.py`.
  - Outputs: `out/grade.txt`, `out/run.log`, `out/posthoc.txt`, `out/sig.pkl`, `out/cells.pkl`, `out/yields.pkl`.
  - Downloads: `web/` (with `web/requests.log` and `web/robots/`). Paper text: `lit/hmm.txt`.
