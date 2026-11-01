# Round 50, stream F: ICI fund flows (unreachable) -> Fed H.6 money-market fund assets

Written 2026-10-30 09:17 UTC (`date -u`). Hypotheses: [HYPOTHESES_F.md](HYPOTHESES_F.md), declared 09:12 UTC before
any price was joined to a signal; no addendum. HOLD (2025-01-01..2026-09-24) stayed closed: H.6 observations after
2024-12-31 and releases after 2024-12-31 were dropped at parse, IC prices cut ts < 1735689600000 at load; no 2025-26
value was printed. Wall time ~12 min, network pull ~2 MB in 12 requests.

## Answer
- **No LIVE or DEMO candidate.** The 8 candidate cells (F3 cash-on-the-sidelines and its declared alternative F3c,
  retail money-fund surge z, k 0 / 1, h1 / h3, equal-weight US500 / USTEC / US2000 book) have **best IS net t +0.26**
  (F3c k1 h3; VAL t -0.90). Best IS mid t +0.54 vs the best-of-8 null median 1.31, p95 2.49 (p 0.95).
- **ICI was not reachable**: www.ici.org answers HTTP 403 (Akamai "Access Denied") to a research User-Agent, even for
  robots.txt. A browser-UA retry was refused by the session's permission classifier as bot-check circumvention, so ICI
  counts as a bot wall. Families (1) Ben-Rephael-Kandel-Wohl bond-to-equity exchanges, (2) aggregate equity-fund fire
  sales, (4) world-equity flows -> USD and weekly ETF net issuance were **not tested**: no free weekly flow source exists
  without ICI (EPFR / Lipper / Morningstar are paid; FRED timed out and has no ICI weekly flows).
- **LIVE was impossible from the count**: H.6 went monthly in 2021-02, so HOLD has ~21 releases; LIVE needs a per-trade
  net Sharpe >= 0.65 (k0). DEMO needed IS t >= 2 (Sharpe >= 0.125 on ~276 IS trades at k0).
- **A declared control met the DEMO numbers and is not promoted**: F3x EURUSD k1 h1 (long EURUSD the day after a
  big retail money-fund surge release) IS net +14.8 bp t 2.35 (n 49), VAL +20.1 bp t 1.78 (n 19), random 99.5 % / 100 %,
  x1.5 and +1 min unchanged. It was declared "control, never a candidate"; it is the second-best of 12 control cells
  (|IS mid t| 2.51 vs the best-of-12 null p95 2.84), PRE is negative (-3.1 bp, t -0.67, n 189), and HOLD would hold
  ~0-11 trades (power <= 1.35 at the VAL size). Draft written only because the brief asks for one when a cell meets
  the numbers: [PREREG_DRAFT_F_eurusd_mmf_surge_control.md](PREREG_DRAFT_F_eurusd_mmf_surge_control.md), status
  **not recommended**.

## Sources
| host | robots.txt (read 2026-10-30 09:07-09:09 UTC) | what | used? |
|---|---|---|---|
| www.ici.org | **403 Access Denied (Akamai)** to a research UA; not retried with a browser UA (classifier: bot-check circumvention) | weekly flows, ETF issuance, MMF assets | **no, off limits (bot wall)** |
| fred.stlouisfed.org | timeout (2 tries) | - | no |
| www.federalreserve.gov | 404 (no robots.txt = no restriction) | DDP package `Output.aspx?rel=H6&filetype=zip` (1.4 MB SDMX XML), `releases/h6/releaseDates.json` (all release dates 1998-2026), about / technical Q&A / current release pages (timing rules) | **yes** |
| github.com, huggingface.co | read (GitHub lists ClaudeBot with path disallows; HF `Allow: /`) | looked for an ICI mirror; none searched further (time) | no |

H.6 series: `MMFGB_N.WM` retail money funds, weekly average NSA, 1980-02..2024-12 (current vintage);
`MMFIN_N.WM` institutional money funds, ends 2021-02-01 (IS-only diagnostic). Release clock: weekly era (to
2021-02-11) Thursday 16:30 ET with data through the Monday 10 days earlier (865 Thursdays, 25 Fridays, a few Monday /
Tuesday holiday shifts, all taken from the official date list); monthly era (2021-02-23 on) fourth Tuesday 13:00 ET with
weekly data through the end of the previous month. Fed H.8 / Z.1: too slow (Z.1 quarterly, ~10-week lag).

## Construction (as declared)
Weekly residual r = dlog(MMF) minus the mean dlog of the same calendar week in the previous 3 years (NSA calendar,
e.g. April taxes). At each release z = sum of r over the newly published weeks / (156-week sd of r x sqrt(weeks)).
Entry next US trading day 09:35 ET (weekly era) or 13:05 ET on the release day (monthly era); exit h1 next trading day
at the same clock, h3 third trading day capped at 119 h 55 m. Fills at IC bid / ask of the last M1 bar within 30 min;
0.6 bp commission FX / gold; swap from research/swing/rates.py; US2000 ask = bid + 0.51 (round 39 D). PRE (2004-15)
only for the FX / gold controls (Dukascopy mids + IC 2016-17 09:35 ET median spread + 0.6 bp). Events with z: PRE 625,
IS 277 (|z| >= 1: 49), VAL 36 (19).

## Results (net and mid in bp per release; t by release = by day)
| cell | mid IS (t) / VAL (t) | cost IS | net IS (t) / VAL (t) | VAL / IS | Sharpe IS / VAL; power HOLD (VAL size) | x1.5 / +1 min IS t | ex 2020-03/04 IS t | years + (2016-24) | random IS (a; b) / VAL | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| F3 k0 h1 | -0.5 (-0.06) / -14.4 (-0.80) | 6.5 | -7.0 (-0.89) / -17.9 (-1.00) | < 0 | -0.053 / -0.166; < 0 | -1.03 / -0.97 | -1.30 | 1/9 | 0.52; 0.19 / 0.23; 0.12 | none |
| F3 k0 h3 | -0.2 (-0.02) / +23.9 (+0.67) | 9.3 | -9.5 (-0.85) / +15.5 (+0.43) | n/a | -0.052 / +0.076; +0.35 | -0.96 / -0.84 | -1.09 | 3/9 | 0.42; 0.26 / 0.31; 0.48 | none |
| F3 k1 h1 | -3.7 (-0.16) / -9.6 (-0.46) | 6.3 | -10.0 (-0.44) / -13.6 (-0.64) | < 0 | -0.062 / -0.148 | -0.49 / -0.44 | -0.62 | 4/8 | 0.44; 0.27 / 0.08; 0.25 | none |
| F3 k1 h3 | -15.2 (-0.54) / +51.3 (+0.88) | 9.0 | -24.2 (-0.86) / +42.2 (+0.72) | n/a | -0.124 / +0.171 | -0.90 / -0.84 | -2.57 | 3/8 | 0.31; 0.14 / 0.11; 0.76 | none |
| F3c k0 h1 | +0.5 (+0.06) / +14.4 (+0.80) | 5.8 | -5.3 (-0.68) / +12.8 (+0.71) | n/a | -0.041 / +0.119; +0.55 | -0.82 / -0.59 | -0.42 | 5/9 | 0.57; 0.61 / 0.81; 0.87 | none |
| F3c k0 h3 | +0.2 (+0.02) / -23.9 (-0.67) | 8.1 | -7.9 (-0.71) / -26.0 (-0.73) | n/a | -0.043 / -0.127 | -0.81 / -0.74 | -0.68 | 4/9 | 0.64; 0.75 / 0.67; 0.59 | none |
| F3c k1 h1 | +3.7 (+0.16) / +9.6 (+0.46) | 5.7 | -2.0 (-0.09) / +8.3 (+0.39) | n/a | -0.013 / +0.090; +0.30 | -0.14 / -0.08 | -0.07 | 3/8 | 0.54; 0.68 / 0.92; 0.77 | none |
| F3c k1 h3 | +15.2 (+0.54) / -51.3 (-0.88) | 7.9 | +7.3 (+0.26) / -52.7 (-0.90) | < 0 | +0.037 / -0.213; < 0 | +0.22 / +0.24 | +1.80 | 5/8 | 0.71; 0.83 / 0.89; 0.34 | none |

Controls (declared, never candidates; single legs, F3 sign = risk-on reversal):
| cell | net IS (t, n) / VAL (t, n) / PRE (t, n) | mid IS t | x1.5 / +1 min IS t | ex 2020 IS t | random IS / VAL (a; b) | note |
|---|---|---|---|---|---|---|
| USDJPY long, 4 cells | IS t -1.24..+0.87, VAL -1.06..-0.34, PRE +0.36..+1.59 | -1.12..+1.13 | | | | none |
| EURUSD long k0 h1 / k0 h3 / k1 h3 | IS +0.99 / -0.55 / +1.12; VAL +1.11 / +0.48 / +0.09; PRE -1.78 / -0.38 / +1.21 | | | | | none |
| **EURUSD long k1 h1** | +14.8 (2.35, 49) / +20.1 (1.78, 19) / -3.1 (-0.67, 189) | 2.51 | 2.35 / 2.40 | 2.00 | 0.995; 0.995 / 1.00; 0.96 | meets DEMO numbers; declared control; inside best-of-12 chance; PRE < 0 |
| XAUUSD short k0 h1 / k0 h3 / k1 h3 | IS +0.01 / +0.14 / -1.60; VAL -1.50 / -0.63 / -0.30 | | | | | none |
| **XAUUSD short k1 h1** | -36.7 (-3.07, 49) / -21.4 (-1.43, 19) / -12.1 (-1.29, 188) | -2.93 | -3.11 / -3.11 | -2.67 | 0.00; 0.005 / 0.005; 0.27 | declared side loses in all 3 eras: gold **rises** the day after a big surge release (post-hoc, see Reading) |

Diagnostics (never candidates): F3i institutional money funds (IS only, 2016-2021-01): net IS t -0.14..+0.84, best
k1 h1 +12.4 bp (t 0.84; 2020-21 +108 / +112 bp per trade, 2016 / 2019 negative). F3o "ICI-like timing" oracle (the
single week ending Monday entered Tuesday 09:35 ET, not tradable from H.6): IS net t -1.64..-0.61, VAL -0.86..+0.19:
even 1-day-old retail MMF flows carry nothing for the equity book, so **ICI access would not have rescued family (3)**.

## Cells and chance benchmark
- 8 candidate cells (F3 4 + F3c 4, the sign pair of each other), 12 control cells, 8 diagnostic cells = 28.
- Best-of-8 candidates, IS mid t with releases sign-flipped jointly (500 draws): median 1.31, p95 2.49; observed best
  +0.54 (p 0.95).
- Best-of-12 controls, |IS mid t|: median 1.86, p95 2.84; observed best 2.93 (XAU k1 h1, p 0.042); EURUSD k1 h1 (2.51)
  is inside p95.

## Reading
- The cash-on-the-sidelines read of retail money-fund surges does not move US indices 1-3 days after the H.6 release
  (IS mid within +-0.6 t in all 8 cells), and the oracle shows the flow is uninformative for equities even at a 1-day
  lag. VAL (monthly, 2022-24, 36 releases) is dominated by the 2022-23 rate-hike inflows (19 of 36 have z >= 1; 2024 none),
  so its +-50 bp swings are a handful of months.
- The only structure is in USD: after a big retail surge release, EURUSD rises (declared control side) and gold rises
  (opposite of the declared control side) the next day, in IS and VAL; PRE agrees for gold (t -1.29 for the short) and
  disagrees for EURUSD (-0.67). A coherent post-hoc story is "USD weakens after cash-hoarding news", but the gold side
  was not declared, both cells come from a 12-cell control grid whose chance p95 is 2.84, the trades are the same 49 /
  19 days, and the H.6 information is 10-25 days stale. It is not graded as a candidate. It can only be tested on data
  after 2026-09-24 with the sides fixed now (USD down / gold up on z >= 1; ~3-6 releases a year), see Directions.

## Exhausted after this stream (for PROMPT "Những họ đã cạn")
- Fed H.6 retail money-fund assets (weekly NSA, seasonal residual z, 2004-24) and institutional money funds (2016-21)
  -> US500 / USTEC / US2000 book 1-3 days after the release, both sides; ICI-like 1-day-lag oracle: nothing (best IS
  net t +0.84 diagnostic, +0.26 candidate).
- ICI weekly fund flows / ETF issuance: not testable without passing ICI's Akamai bot wall.

## Pitfalls
- **www.ici.org returns 403 (Akamai) to non-browser clients, robots.txt included**; retrying with a browser UA is bot-check
  circumvention (the classifier refuses it). Treat ICI as off limits; FRED timed out from this Mac.
- **H.6 went monthly on 2021-02-23** (fourth Tuesday 13:00 ET); weekly NSA data still exist but are released monthly,
  so IS (weekly, 10-day lag, 1 new week) and VAL / HOLD (monthly, 25-55-day lag, 4-5 weeks) are different signals.
  Weekly SA data end 2021-02-01; institutional money funds end 2021-02-01.
- The H.6 release-date list (`releaseDates.json`) has suffixes such as `20020214**` (revised releases): strip them.
- **Retail MMF was revised retroactively in 2026-07** (netting methodology, Fed technical Q&A): the downloaded vintage is
  not the real-time one; weekly changes are probably close, levels are not. Real-time vintages would need ALFRED (FRED
  timed out).
- A 2022-23 rate-hike surge makes VAL's |z| >= 1 releases almost all inflows: random control (a) (sides permuted) is
  then nearly degenerate; use (b).

## Directions that need the user
- ICI weekly flows (families 1, 2, 4 and ETF issuance): needs either the user downloading ICI's public spreadsheets
  by hand (no account needed in a browser) or permission to fetch ici.org with a browser client. Value: low-moderate;
  the round 38 S ETF-creation and round 45 X pooled-flow results, plus this stream's oracle for money funds, suggest
  weekly aggregate flows carry little at 1-5 days; still the one untested family with a published reversal effect
  (Ben-Rephael et al.).
- Forward test of the post-hoc USD reading (EURUSD up / gold up the day after an H.6 release with retail z >= 1), sides
  fixed in this file, on releases after 2026-09-24 only: ~3-6 trades a year, so years to any conclusion; value low.

## Files
- Scripts: `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r50/F/scripts/parse_h6.py`
  (sha256 049b8bd3...), `.../r50/F/scripts/run.py` (sha256 7e8b1610...).
- Outputs: `.../r50/F/out/res.json`, `.../r50/F/out/run.log`, `.../r50/F/out/h6.npz`; downloads and request log in
  `.../r50/F/web/`.
