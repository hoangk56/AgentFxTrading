# Round 45, stream S: JPX daily short-selling ratio and large short-position reports -> JP225

Written 2026-10-30 from 06:34 UTC (`date -u`). Hypotheses with their UTC times: [HYPOTHESES_S.md](HYPOTHESES_S.md)
(families 1 and 3 and the power arithmetic at 06:29, before any return; addendum R5 at 06:32, after R1-R4 and before
R5). No side was changed after its numbers were seen. Bars: research/PROMPT.md / round 13 brief, LIVE and DEMO only.

HOLD (2025-01-01..2026-09-24) stayed closed:
- The ratio copy (stock-marketdata.com plotly page) contains rows to 2026; the parser drops every row after
  2024-12-31 and asserts it before anything is kept or printed. Only trace names, lengths and date spans were probed.
- karauri.net was requested only for TSE days <= 2024-12-30; the parser refuses later dates.
- JPX pages: only page structure (link lists, titles) of the 2025-26 daily archive was read; no 2025-26 file was opened.
- IC M1 cut at ts < 1735689600000 at load.
- Disclosure: one WebSearch result summary quoted two 2025 aggregate short-selling shares from JPX files (the
  November 2025 monthly split and the 2025-12-30 daily split). They are signal values, not prices; they were not used
  and nothing was registered.

## Answer
**No LIVE or DEMO candidate. No PREREG_DRAFT.**
- **Family 1, the TSE-wide daily short-selling ratio 2017-24** (first load in any round; JPX keeps only ~13 months of
  daily files, so the ratio came from a public third-party copy): 27 declared cells on JP225 (level z, residual z net
  of the same-day return, daily change z, the folk rule's absolute 45 % / 50 % levels; next Tokyo open, same-evening
  night session, overnight into the open; 1 and 3 days).
  - On the primary contrarian side, no cell has IS net t >= 1.5. The best are R4 z_chg k2.0 h3 +41.7 bp (t 1.40;
    VAL -138.7, t -3.59) and R3 z_res k1.5 h3 +22.7 (t 1.32; VAL -32.2).
  - The headline cell R1 z_lvl k1.5 h1 nets +0.4 bp (t 0.03) IS and +7.2 (t 0.54) VAL.
  - The informed (Diether-Lee-Werner) alternative side is negative in 23 of 27 cells; its best IS t is 0.87.
  - The best |mid t| over the family (1.80) is below the sign-flip null median (2.06; p 0.70).
- **Family 2** (price-restricted short share, uptick-rule binding days): **no free daily source for <= 2024**. JPX's
  daily split files start 2025-10 and older ones are deleted; the third-party copy has the total only. Dropped before
  any data.
- **Family 3, large short-position reports (holders >= 0.5 %)**: 3,906 karauri.net day pages 2017-24, aggregated daily
  as the net change in reported ratios and the net count of increases minus decreases. 12 declared cells on the
  informed side (build-up -> short JP225 from T+3).
  - Best IS net t +0.91 (z_n k2.0 h1, VAL +0.9 bp); the primary z_pp k1.0 h3 is wrong-signed (IS -42.6 bp, t -2.00).
  - The best |mid t| of 1.59 is inside the null (p50 1.81, p 0.65).
- The power arithmetic held before any return: LIVE needed ~30-50 bp per 1-day JP225 trade (per-trade Sharpe
  0.25-0.5 at ~35-150 HOLD trades); DEMO needed 12-26 bp net in IS. The measured predictability is ~0 at both sides.
- Two VAL-only patterns (contrarian at the night-session entry: R1e0 k1.5 h1 VAL +28.9 bp, t 2.05; R5 k1.5 VAL +17.5,
  t 1.84) have negative IS (-13.2 and -8.2) and are not candidates: selecting them would be choosing by VAL.

## Sources (fetch log: scratchpad `r45/S/web/requests.log`, 3,932 requests; 3 WebSearch, 0 WebFetch; pull 06:21-07:39 UTC, ~13 min over the ~1 h target because karauri.net needs 2 pages a day)
| source | what was fetched | span (used to 2024-12-31) | usable? |
|---|---|---|---|
| www.jpx.co.jp short-selling pages (robots.txt: `Disallow:` empty, all allowed) | index, monthly page, 4 monthly archive pages, 1 daily archive page, `2412e.pdf` (Dec 2024 monthly) and one old daily-split URL from a search result (404) | daily PDFs (with / without price restriction) only from 2025-10 (HOLD); monthly totals 2021-26; old daily files are deleted (404) | **no** for daily; monthly = 12 a year, no power |
| stock-marketdata.com (robots.txt: only /wp-admin/ disallowed) | `karauri.html` and two plotly chart pages (`time-series/charts/japan-indicator-short-selling-value*.html`) | TSE-wide daily ratio 2017-01-04..2024-12-30 (1,953 days, none missing against the TSE calendar), Nikkei close; Nikkei VI 2011+; weekly margin balances 2017+ | **yes** (ratio total only; no restricted / unrestricted split) |
| karauri.net (robots.txt names only MJ12bot, AhrefsBot, BLEXBot, SemrushBot, baiduspider) | `/up/?date=` and `/down/?date=` for every TSE day 2017-01-04..2024-12-30 (3,906 pages + 2 retries of server 500s requests, ~1 s start-to-start) | per-stock 0.5 %-holder short-position increases / decreases by calculation date | **yes** (new / lost reports not pulled: time budget) |
| nikkei225jp.com | robots.txt only: `/_data/` (where its chart data sits) is disallowed | | not used |

Family 2 of the brief (price-restricted short share, uptick-rule binding days) has **no free daily source for <= 2024**
and was dropped before any data.

## Method
- Signal day D = TSE trading day. Ratio public after the close (declared by 18:30 JST). Entry E1 = D+1 00:05 UTC
  (Tokyo open + 5 min), E0 = D 10:05 UTC (OSE night session); h1 / h3 = 1 / 3 TSE days later at the entry clock (<= 120
  h). R5 = D 10:05 -> D+1 00:15 UTC (overnight into the open). Family 3: calculation date T, public after T+2's close,
  entry T+3 00:05 UTC.
- Signals trailing only: z vs the previous 250 TSE days (>= 120), so IS = 2017-06-28..2021-12-30, VAL = 2022-24, no PRE.
  z_res removes the same-day Nikkei return (ratio vs same-day return corr -0.38 in IS: the ratio is high on down days).
- Costs: half the IC spread at both fill minutes (JP225 median 2.7 bp at 00:05 UTC), JP225 swap per rollover (~-1.4 bp
  long / -1.1 bp short a night), 0.6 bp on USDJPY. Variants spread x1.5 and +1 minute. Non-overlapping trades per cell.
- Controls: random entries (200 seeds; (a) same sides at random TSE days of the era, (b) side recomputed from the
  signal's sign at the random day); shared sign-flip-by-day best-of-N null on IS mid t; USDJPY / HK50 as information.
- "P" = declared primary side (family 1: contrarian folk rule, high ratio -> long; family 3: informed, build-up of large
  short positions -> short); "A" = the declared alternative side (DLW informed for family 1).

## Results, family 1 (TSE-wide ratio -> JP225); net bp per trade, t on trades (one per day)
| hypothesis | eras | mid IS (t) / VAL (t) | cost IS | net IS (t) / VAL (t) | VAL / IS | x1.5 / +1 min IS t | ex 2020-03/04 IS t | per-trade SR IS / VAL; power at HOLD n (IS, VAL size) | random IS / VAL (a; b) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **R1 z_lvl k1.5 h1 E1, P (headline)** | IS, VAL | +5.36 (0.47) / +10.85 (0.81) | 4.96 | +0.40 (0.03) n205 / +7.20 (0.54) n93 | 18 | -0.09 / +0.04 | +1.30 | 0.002 / 0.056; 0.02, 0.41 (n 54) | 0.68; 0.80 / 0.81; 0.68 | none |
| R1 z_lvl k1.0 h1 E1, P | IS, VAL | +4.51 (0.64) / +9.17 (1.19) | 4.91 | -0.41 (-0.06) n408 / +5.61 (0.73) n237 | < 0 IS | -0.27 / -0.01 | +0.23 | -0.003 / 0.047; -0.03, 0.56 | 0.72; 0.86 / 0.89; 0.77 | none |
| R1 z_lvl k2.0 h1 E1, P | IS, VAL | +14.31 (0.79) / -24.07 (-0.89) | 4.97 | +9.35 (0.51) n84 / -28.37 (-1.05) n30 | < 0 | +0.44 / +0.36 | +1.01 | 0.056 / -0.193 | 0.81; 0.92 / 0.11; 0.10 | none |
| R1 h3 cells (k 1.0 / 1.5 / 2.0), P | IS, VAL | -7.6 / -11.2 / +7.1 IS | 8.4-8.6 | IS t -1.00 / -0.92 / -0.05; VAL +12.5 / +7.5 / -45.2 | | | | | | none |
| R1e0 (E0 night entry) best, k1.5 h1, P | IS, VAL | -7.70 (-0.68) / +33.22 (2.35) | 5.45 | -13.15 (-1.17) n206 / +28.91 (2.05) n91 | < 0 IS | -1.32 / -1.13 | +0.12 | -0.081 / 0.214 | 0.13; 0.16 / 1.00; 1.00 | none (VAL-only; IS 2020 -88.5 bp a trade) |
| R1e0 other 5 cells, P | IS, VAL | IS mid t -1.16..-0.26 | 5.5-9.4 | IS t -1.47..-0.65; VAL -26.6..+22.1 | | | | | | none |
| R2 ratio >= 45 % h1 E1 (long only), P | IS, VAL | +13.46 (1.23) / +15.24 (1.55) | 5.32 | +8.14 (0.74) n219 / +10.90 (1.11) n166 | 1.34 | +0.60 / +0.85 | +1.43 | 0.050 / 0.086; 0.50, 0.84 (n 97) | 0.88 / 0.89 | none (IS t 0.74; random longs do as well) |
| R2 ratio >= 45 % h3, P | IS, VAL | +25.81 (1.10) / +23.13 (0.99) | 9.27 | +16.54 (0.71) n109 / +15.03 (0.64) n94 | 0.91 | +0.64 / +0.76 | +1.96 | 0.068 / 0.066; 0.50, 0.49 | 0.84 / 0.74 | none |
| R2 ratio >= 50 % h1 / h3, P | IS, VAL | +34.7 / +23.8 IS | 5.3 / 8.9 | IS t +0.52 / +0.23 (n 15 / 14); VAL -14.3 / -43.5 | < 0 | | | | | none |
| R3 z_res k1.5 h1 E1, P | IS, VAL | +14.83 (1.49) / +25.07 (1.95) | 4.91 | +9.93 (0.99) n204 / +21.45 (1.67) n96 | 2.16 | +0.85 / +0.99 | +1.49 | 0.070 / 0.170; 0.52, 1.27 (n 56) | 0.95; 0.985 / 0.965; 0.92 | none (IS t 0.99 < 2) |
| R3 z_res k1.5 h3, P | IS, VAL | +31.17 (1.80) / -25.26 (-0.88) | 8.46 | +22.71 (1.32) n112 / -32.17 (-1.12) n68 | < 0 | +1.23 / +1.33 | +1.47 | 0.124 / -0.136 | 0.93; 0.96 / 0.20; 0.05 | none |
| R3 z_res k1.0 h1 / h3, P | IS, VAL | +3.86 (0.58) / +4.44 (0.30) IS | 4.95 / 8.63 | IS t -0.17 / -0.28; VAL +4.30 / -12.85 | | | | | | none |
| R4 z_chg k2.0 h3, P | IS, VAL | +50.04 (1.67) / -131.83 (-3.40) | 8.31 | +41.72 (1.40) n57 / -138.67 (-3.59) n24 | < 0 | +1.35 / +1.39 | +0.85 | 0.185 / -0.732 | 0.98 / 0.00 | none (sign flips IS -> VAL) |
| R4 other 3 cells, P | IS, VAL | IS mid t +0.40..+0.92 | 4.8-8.2 | IS t -0.00..+0.51; VAL k1.5 h3 -98.6 (t -3.16) | | | | | | none |
| R5 overnight into the open, z_lvl k1.0 / k1.5 / lvl45, P | IS, VAL | -2.17 / -3.01 / +5.00 IS | 5.2-5.6 | IS t -1.59 / -1.13 / -0.08; VAL -2.65 / +17.52 (t 1.84) / -1.01 | | | | | random IS 0.20-0.50 | none |
| Alternative side (DLW informed: high ratio -> short), best IS net t over all 27 cells | IS, VAL | R1e0 k2.0 h1 A: +20.44 (1.16) | 5.17 | +15.27 (0.87) n86 / -27.58 (-1.18) | < 0 | | | | 0.965 / 0.21 | none; 23 / 27 alternative cells have IS net t < 0 |
| Controls (information): USDJPY / HK50, R1 k1.0 / k1.5 h1 | IS, VAL | USDJPY P +3.0 (1.34) / +4.1 (1.26) IS; HK50 +2.5 (0.36) / -4.6 (-0.42) | 1.0 / 5.0 | USDJPY IS t +0.92 / +0.95, VAL +1.54 / -4.32; HK50 IS t -0.37 / -0.89 | | | | | | nothing |

### Cells tried and chance (family 1)
| set | cells (P side) | best \|mid t\| IS | sign-flip null p50 / p95 | p | best IS net t, P / A side |
|---|---|---|---|---|---|
| R1-R4 | 24 | 1.80 (R3 z_res k1.5 h3) | 2.06 / 3.19 | 0.70 | +1.40 (R4 k2.0 h3) / +0.87 |
| R5 | 3 | 0.69 | 1.13 / 2.44 | 0.77 | -0.08 / -0.62 |
No family-1 cell reaches IS net t 2 on either side (DEMO needs 2.0, LIVE 2.5); the best |mid t| is below the null
median.

## Results, family 3 (large short-position reports, karauri.net, calculation date T -> entry T+3 00:05 UTC)
Pages parsed: 1,953 / 1,953 TSE days for both `/up/` and `/down/` (median 180 increase and 240 decrease reports a day).
The reports' daily net change is nearly unrelated to the ratio (corr of z_pp with the same day's z_lvl 0.06). z_pp is
left-skewed: big net reductions (covering, z < -k) are common and big build-ups rare (IS k2.0: 2 build-up days vs 43
reduction days), so most z_pp trades are longs.

| hypothesis | eras | mid IS (t) / VAL (t) | cost IS | net IS (t) / VAL (t) | VAL / IS | x1.5 / +1 min IS t | ex 2020-03/04 IS t | per-trade SR IS / VAL; power at HOLD n (IS, VAL size) | random IS / VAL (a; b) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| K z_pp k1.0 h1, P (informed: build-up -> short) | IS, VAL | -0.00 (-0.00) / +6.73 (0.69) | 5.05 | -5.05 (-0.44) n151 / +3.24 (0.33) n159 | < 0 IS | -0.58 / -0.48 | -1.29 | -0.036 / 0.026 | 0.41; 0.26 / 0.75; 0.92 | none |
| K z_pp k1.0 h3, P | IS, VAL | -34.03 (-1.59) / -13.23 (-0.60) | 8.61 | -42.64 (-2.00) n107 / -20.48 (-0.93) n96 | | -2.07 / -2.08 | -2.06 | -0.193 / -0.095 | 0.05 / 0.23 | none (wrong side) |
| K z_pp k1.0 h3, A | IS, VAL | +34.03 (1.59) / +13.23 (0.60) | 8.10 | +25.93 (1.21) n107 / +6.30 (0.29) n96 | 0.24 | +1.14 / +1.30 | +1.14 | 0.117 / 0.029; 0.88, 0.22 (n 56) | 0.965; 0.985 / 0.75; 0.84 | none (IS t 1.21; alternative side) |
| K z_pp k1.5 / k2.0, h1 / h3, P | IS, VAL | IS mid t -0.56..+0.07 | 5.2-9.0 | IS t -0.79..-0.22; VAL +17.3 / +32.2 / +33.5 / +66.3 (t 1.09-1.70) | < 0 IS | | | | VAL 0.83-0.97 | none (VAL-only, n 26-59) |
| K z_n k2.0 h1, P (best P cell) | IS, VAL | +18.09 (1.28) / +4.75 (0.24) | 5.26 | +12.83 (0.91) n84 / +0.91 (0.05) n33 | 0.07 | +0.80 / +0.97 | +0.73 | 0.100 / 0.008; 0.44, 0.04 (n 19) | 0.89; 0.94 / 0.53; 0.61 | none |
| K z_n other 5 cells, P | IS, VAL | IS mid t +0.20..+0.56 | 4.9-8.8 | IS t -0.42..+0.15; VAL -20.0..+29.2 | | | | | | none |
| K alternative side, other cells | IS, VAL | | | IS t -1.63..+0.37 | | | | | | none |

### Cells tried and chance (family 3)
| set | cells (P side) | best \|mid t\| IS | sign-flip null p50 / p95 | p | best IS net t, P / A side |
|---|---|---|---|---|---|
| K | 12 | 1.59 | 1.81 / 2.66 | 0.65 | +0.91 / +1.21 |

Total across the stream: 39 declared JP225 cells on the primary sides (78 with the alternative sides) + 4 control
cells. No cell is near DEMO (IS net t >= 2 with VAL > 0); the only IS |t| of 2 is a wrong-sign cell.

## Why it does not escape the limits
- **The exchange-wide ratio is a by-product of the day's trading, not a forced next-day flow.** It co-moves with the
  same day's return (corr -0.38) and carries nothing for the next session once that is removed (z_res). Most of the
  ~40 % short share is price-restricted institutional, HFT and arbitrage selling, flat or hedged by the close. This is
  round 38's FINRA result (Wang-Yan-Zheng's null) repeated in Tokyo.
- **The folk rule does not move IC's JP225 at the open.** The overnight-into-the-open cell (R5) is ~0 in IS. The level
  rule (>= 45 %) is long on most days and earns what random longs earn (random control 0.88).
- **Large-holder reports are slow and deliberate, but stale at the index level.** They are disclosed with a ~2-day
  lag. Their daily aggregate is dominated by covering days, and it neither continues (informed side) nor reverses
  reliably (alternative side IS t 1.21, VAL 0.29).
- **Power was never there for LIVE.** At ~35-150 HOLD trades, LIVE needs 30-50 bp per JP225 day trade, several times
  any published index-level short-selling effect. The cost (~5 bp) was not the binding constraint; predictability was.

## Exhausted after this stream (for PROMPT "Những họ đã cạn")
- JPX TSE-wide daily short-selling ratio (level, residual of the same-day return, daily change, the 40-50 % folk-rule
  levels), contrarian and informed sides -> JP225 (USDJPY, HK50 controls) at the next open, the night session,
  overnight into the open, 1-3 days (2017-24).
- Large short-position reports (>= 0.5 % holders): daily aggregate increases minus decreases (ratio sum and count) ->
  JP225 at 1-3 days after the T+2 disclosure (2017-24).
- Not testable with free data: the price-restricted / unrestricted split (uptick-rule binding days) before 2025-10.

## Pitfalls
- JPX keeps only ~13 months of daily short-selling files online (2025-10 onward on 2026-10-30) and deletes older daily
  PDFs (404); monthly PDFs (2021+) carry one row per month. Round 31's "last ~12 months only" still holds.
- stock-marketdata.com chart pages (plotly, `bdata` base64 float64 arrays) hold the TSE-wide ratio from 2017-01-04 and
  rows to the current day: decode with the cut; there is no restricted / unrestricted split.
- karauri.net pages are by *calculation* date (`（YYYY-MM-DD算出）` in the heading); the `f=` parameter filters by
  institution, it is not pagination; ETF rows (e.g. VIX ETFs, "個人" holders) are included.
- nikkei225jp.com's robots.txt disallows `/_data/`, where its chart series live.
- The TSE-wide ratio co-moves with the same day's return (corr -0.38), so a raw "high ratio -> long" cell is partly a
  next-day reversal bet; the residual signal (z_res) separates the two.

## Directions that need the user
| direction | value |
|---|---|
| J-Quants API (JPX's official data API; account; paid plan for > 2 years history): daily short-selling value by industry with and without price restriction from 2008, plus margin and investor-type data | DEMO ~1-2 %, LIVE < 1 % (the total ratio carries nothing; the split adds the uptick-rule family only) |
| Paid daily short-selling split (QUICK / Nikkei NEEDS) for 2008-24 | same as above |

## Scripts and outputs (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r45/S/`)
- `scripts/fetch.sh` (logged single fetches), `scripts/pull_kn.sh` (karauri.net pull), `scripts/probe_plotly.py`
  (names / spans only), `scripts/parse_smd.py` -> `out/smd.npz`, `scripts/parse_kn.py` -> `out/kn_raw.npz`,
  `scripts/signals.py` -> `out/signals.npz`, `scripts/build_kn.py` -> `out/kn.npz`, `scripts/common.py` (engine),
  `scripts/run_cells.py` (R / K) -> `out/cells_R.txt`, `out/cells_K.txt`, `scripts/run_r5.py` -> `out/cells_R5.txt`.
- Downloads under `web/` (p1/ JPX pages, m/ JPX monthly, smd/, kn/, robots/), log `web/requests.log`.

C3 correlation: no survivor, not computed.
