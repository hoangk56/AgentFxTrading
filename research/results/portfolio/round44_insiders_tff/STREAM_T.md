# Round 44, stream T: CFTC Traders in Financial Futures (TFF) positioning

Written 2026-10-30 from 06:15 UTC (`date -u`). Hypotheses: [HYPOTHESES_T.md](HYPOTHESES_T.md), declared 06:12 UTC
before any price was joined to a signal (the H4 fallback was declared in the same file; its numbers were computed
at 06:14). HOLD (2025-01-01..2026-09-24) stayed closed: the positions mirror holds 2025-26 rows, cut at parse to as-of
<= 2024-12-24 (the 2024-12-31 report is released in 2025) before anything was printed; IC prices come from the
round 39 D panel, built with ts < 1735689600000. No 2025-26 value was printed. Total wall time ~10 min, network
pull 33 MB.

## Answer
- **No LIVE or DEMO candidate. No PREREG_DRAFT.**
- **LIVE was impossible from the count** (HOLD ~73 release Fridays: a weekly book net Sharpe >= 0.35 is needed, i.e.
  IS t ~5.6). **DEMO needed** a book IS net t >= 2.0 (weekly Sharpe >= 0.128); it was reachable on paper only for the
  13-leg book.
- 24 graded book cells (H1 leveraged-fund crowding reversal, H1c against leveraged-fund weekly changes, H2 with
  asset-manager weekly changes, H3 with dealer extremes; 2 thresholds + a 3-long / 3-short cross-section; h1 / h3)
  plus 6 fallback cells (H4 asset managers vs leveraged funds): **best IS net t +0.76** (H1 XS h1, VAL t -2.11; H4 XS
  h1 the same +0.76, VAL -1.04). No cell has IS t >= 2. The best IS mid t (+1.87, H1 XS h1) is inside the
  best-of-24 null (median 1.60, p95 2.72; p 0.34).
- The TFF split does not rescue weekly positioning at 1-3 days: leveraged-fund crowding has a small mid reversal in
  IS (+2-14 bp, t 0.7-1.6) that turns negative in VAL; asset-manager continuation is wrong-signed in IS (H2 XS h3 net
  t -3.00, H2 k1.5 h3 -2.05; VAL ~0, PRE +0.20); dealer extremes carry nothing.
- Commodity control C1c (against managed-money weekly changes, disaggregated report, gold / silver / WTI / gas) is the
  only family positive in IS and VAL in all 4 cells, as Kang, Rouwenhorst & Tang (2020) report for commodities. It is a
  control (never a candidate by declaration), and even so it is below the DEMO bar: IS t 0.66-1.35 (0.71-1.55 without
  2020-03/04), PRE negative in 3 of 4 cells.

## Sources
| source | what | history used | usable? |
|---|---|---|---|
| www.cftc.gov historical compressed files (`fut_fin_txt_*`, `fut_disagg_txt_*`) | robots.txt read 06:06 UTC: `User-agent: ClaudeBot`, `anthropic-ai`, `Claude-Web` -> `Disallow: /` (Cloudflare-managed block) | none fetched | **off limits** (brief rule) |
| publicreporting.cftc.gov (Socrata) | robots.txt and one metadata probe: 403 / 403 | | no |
| Hugging Face search (5 API queries) | 6 COT datasets: FinzData (last 12 months only), Chainticks (2026 legacy parquet), Arimancy / ZipLime / Farmaanaa (parquet; no parquet reader in the venv), **XOOMAR** (CSV) | | XOOMAR only |
| **`XOOMAR/cftc-commitments-of-traders`** (huggingface.co, robots `Allow: /`) | one CSV, 32.9 MB: TFF + disaggregated futures-only, dealer / asset manager / leveraged / other / non-reportable long and short, OI | TFF 2010-07-20..2024-12-24 (754 weeks); E-mini Russell (CME) from 2017-08-15; Nikkei USD 695 weeks (reporting gaps); disaggregated 2010-01-05..2024-12-24 | **yes** |
| validation | OI and non-reportable long / short vs the CFTC legacy futures-only files already on disk (round 39, fetched 2026-10-29) | 754 / 754 weeks match exactly for every financial market, 782 / 782 for metals and gas | mirror is faithful |

Unusable or missing: TFF 2006-09 (mirror starts 2010-07, so PRE = 2012-07..2015 on the five Dukascopy FX legs);
NYMEX WTI 067651 is only in the mirror from 2022 (the WTI control uses ICE WTI 067411); no spreading or
concentration columns (net positions are unaffected); options-and-futures-combined TFF not in the mirror.
Fetch log: scratchpad `web/requests.log` (21 requests, 0 WebSearch, 0 WebFetch).

## Construction (as declared)
x = (category long - short) / OI. `lvl` = z vs the previous 156 weeks (>= 104); `chg` = weekly change / sd of the
previous 52 changes (>= 40, no change across a reporting gap). As-of Tuesday, release Friday 15:30 ET; enter Friday
15:50 ET at IC bid / ask, exit Monday 15:50 ET (h1) or Wednesday 15:45 ET (h3, ~120 h). Holiday weeks and the 2013 /
2018-19 shutdown catch-ups skipped (~42 weeks a year). 13 legs: EUR, JPY, GBP, CHF, CAD, AUD, NZD -> FX majors; ES ->
US500; NQ -> USTEC; DJ -> US30; RTY -> US2000; NKY -> JP225; VIX -> US500 with sign -1. Cost: IC spread both minutes,
0.6 bp commission FX / metals, swap; PRE Dukascopy mids + IC 2016-17 spread + 0.6 bp. Graded book: weekly mean over
open legs of net / the symbol's trailing 156-week sd of the same-horizon mid return (>= 52 weeks; index legs
therefore enter from 2017-02); the equal-weight bp book (all legs from 2016) gives the same verdict (best main IS net
t +1.04, H1 k1.5 h3, VAL -0.74).

## Results (book cells; net in sd units x 100 per week; mid / cost in bp of the equal-weight book)
| cell | mid IS (t) / VAL (t), bp | cost IS bp | net IS (t) / VAL (t) / PRE (t), sd x100 | VAL/IS | Sharpe IS / VAL; power HOLD n 73 (IS, VAL size) | x1.5 / +1 min IS t | ex 2020-03/04 IS t | years + | random IS / VAL (a; b) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 k1.0 h1 | +2.8 (+0.86) / -4.6 (-1.05) | 3.3 | +2.2 (+0.54) / -11.2 (-2.32) / -4.8 (-0.74) | < 0 | +0.035 / -0.213; +0.30, -1.82 | +0.39 / +0.57 | +0.37 | 4/9 | not run | none |
| H1 k1.0 h3 | +3.2 (+0.66) / -2.2 (-0.30) | 4.9 | -3.0 (-0.79) / -3.4 (-0.69) / -1.1 (-0.16) | n/a | -0.051 / -0.063 | -0.89 / -0.82 | -0.76 | 1/9 | not run | none |
| H1 k1.5 h1 | +6.0 (+1.20) / +2.3 (+0.40) | 3.4 | +3.7 (+0.60) / -2.6 (-0.49) / -7.9 (-0.77) | < 0 | +0.043 / -0.048; +0.37, -0.41 | +0.49 / +0.65 | +0.67 | 7/9 | not run | none |
| H1 k1.5 h3 | +14.4 (+1.59) / -1.3 (-0.11) | 5.0 | +1.6 (+0.25) / -3.4 (-0.51) / -3.6 (-0.36) | < 0 | +0.018 / -0.048; +0.15, -0.41 | +0.19 / +0.21 | -0.13 | 4/9 | not run | none |
| H1 XS h1 | +2.4 (+1.21) / -1.2 (-0.41) | 3.0 | +2.4 (+0.76) / -7.6 (-2.11) / -10.8 (-1.96) | < 0 | +0.049 / -0.191; +0.42, -1.63 | +0.57 / +0.79 | +0.16 | 3/9 | not run | none |
| H1 XS h3 | +4.0 (+1.19) / -0.5 (-0.10) | 4.5 | -1.3 (-0.42) / -3.6 (-0.99) / -6.1 (-0.96) | n/a | -0.027 / -0.089 | -0.52 / -0.41 | -0.59 | 4/9 | not run | none |
| H1c k1.0 h1 | -1.6 (-0.35) / +1.6 (+0.31) | 3.2 | -3.0 (-0.61) / +4.3 (+0.84) / -8.4 (-1.20) | n/a | -0.042 / +0.080 | -0.72 / -0.59 | -0.76 | 4/9 | not run | none |
| H1c k1.0 h3 | +7.2 (+0.89) / +6.8 (+0.68) | 4.9 | +2.1 (+0.41) / -1.4 (-0.22) / -3.7 (-0.59) | < 0 | +0.028 / -0.021; +0.24, -0.18 | +0.34 / +0.37 | +0.65 | 5/9 | not run | none |
| H1c k1.5 h1 | -6.7 (-1.11) / +3.3 (+0.44) | 3.0 | -6.7 (-1.01) / +13.1 (+1.55) / +5.4 (+0.66) | n/a | -0.084 / +0.176 | -1.09 / -1.05 | -0.91 | 5/9 | not run | none |
| H1c k1.5 h3 | +4.3 (+0.41) / +10.1 (+0.73) | 4.5 | +2.3 (+0.35) / +6.0 (+0.73) / +4.1 (+0.44) | 2.59 | +0.029 / +0.082; +0.25, +0.70 | +0.30 / +0.32 | +0.89 | 4/9 | 0.76; 0.73 / 0.86; 0.80 | none (IS t 0.35) |
| H1c XS h1 | -0.5 (-0.19) / -0.8 (-0.30) | 3.0 | -5.2 (-1.72) / -2.3 (-0.63) / -4.6 (-1.10) | n/a | -0.111 / -0.057 | -1.91 / -1.68 | -1.74 | 1/9 | not run | none |
| H1c XS h3 | +1.8 (+0.45) / +1.8 (+0.35) | 4.6 | -2.2 (-0.66) / -1.5 (-0.43) / -4.9 (-0.95) | n/a | -0.042 / -0.039 | -0.76 / -0.68 | -0.27 | 4/9 | not run | none |
| H2 k1.0 h1 | +7.5 (+1.50) / -6.2 (-1.09) | 2.8 | +2.5 (+0.46) / -8.7 (-1.39) / -0.9 (-0.14) | < 0 | +0.032 / -0.129; +0.27, -1.10 | +0.36 / +0.51 | -1.07 | 3/9 | not run | none |
| H2 k1.0 h3 | +5.9 (+0.67) / -2.3 (-0.23) | 4.1 | -3.4 (-0.65) / -2.4 (-0.35) / -3.0 (-0.46) | n/a | -0.044 / -0.032 | -0.71 / -0.59 | -1.18 | 2/9 | not run | none |
| H2 k1.5 h1 | +5.1 (+0.79) / -6.5 (-0.88) | 2.8 | +0.2 (+0.03) / -12.6 (-1.36) / +3.5 (+0.33) | < 0 | +0.002 / -0.137 | -0.05 / +0.09 | -0.90 | 3/9 | not run | none |
| H2 k1.5 h3 | -10.5 (-1.01) / +0.5 (+0.05) | 4.1 | -15.3 (-2.05) / -2.0 (-0.24) / -8.7 (-0.92) | n/a | -0.157 / -0.024 | -2.09 / -2.01 | -2.25 | 2/9 | not run | none |
| H2 XS h1 | +0.7 (+0.36) / -2.0 (-0.67) | 2.8 | -3.4 (-1.01) / -4.1 (-0.97) / -3.0 (-0.64) | n/a | -0.065 / -0.088 | -1.17 / -0.92 | -2.13 | 3/9 | not run | none |
| H2 XS h3 | -1.3 (-0.37) / +1.6 (+0.28) | 4.2 | -8.7 (-3.00) / -0.9 (-0.23) / +1.0 (+0.20) | n/a | -0.193 / -0.021 | -3.11 / -2.95 | -3.10 | 2/9 | not run | none (wrong sign in IS only) |
| H3 k1.5 h1 | -4.3 (-0.85) / -10.9 (-1.24) | 3.1 | -7.8 (-1.20) / -4.6 (-0.73) / -9.5 (-0.84) | n/a | -0.084 / -0.071 | -1.28 / -1.18 | -0.93 | 4/9 | not run | none |
| H3 k1.5 h3 | -2.2 (-0.28) / +3.9 (+0.27) | 4.6 | -6.3 (-1.06) / -0.3 (-0.04) / -0.4 (-0.04) | n/a | -0.073 / -0.004 | -1.11 / -1.10 | -1.18 | 3/9 | not run | none |
| H3 k2.0 h1 | +5.8 (+0.92) / -12.3 (-0.88) | 3.2 | +5.2 (+0.59) / -3.7 (-0.41) / -16.0 (-1.19) | < 0 | +0.056 / -0.051; +0.48, -0.44 | +0.53 / +0.63 | +0.68 | 6/9 | not run | none |
| H3 k2.0 h3 | +9.6 (+1.00) / +18.5 (+0.84) | 4.5 | -1.3 (-0.15) / +8.8 (+0.92) / -22.4 (-1.47) | n/a | -0.014 / +0.110 | -0.18 / -0.16 | -0.67 | 6/9 | not run | none |
| H3 XS h1 | +0.3 (+0.16) / -4.7 (-1.26) | 2.7 | -2.7 (-0.78) / -6.4 (-1.48) / -7.4 (-1.30) | n/a | -0.050 / -0.134 | -0.93 / -0.78 | -0.45 | 4/9 | not run | none |
| H3 XS h3 | +4.2 (+1.23) / +4.9 (+0.73) | 4.2 | -1.2 (-0.38) / +1.3 (+0.28) / -4.8 (-0.81) | n/a | -0.024 / +0.026 | -0.47 / -0.41 | -0.70 | 4/9 | not run | none |
| H4 k1.0 h1 (fallback) | -0.5 (-0.13) / +3.7 (+0.86) | 3.2 | +1.5 (+0.35) / -2.3 (-0.56) / -8.7 (-1.49) | < 0 | +0.023 / -0.050 | +0.21 / +0.37 | -0.23 | 3/9 | not run | none |
| H4 k1.0 h3 | -6.0 (-0.99) / -5.4 (-0.63) | 5.0 | -5.4 (-1.36) / -3.5 (-0.74) / -0.8 (-0.13) | n/a | -0.087 / -0.067 | -1.45 / -1.32 | -2.05 | 2/9 | not run | none |
| H4 k1.5 h1 | -1.8 (-0.42) / +6.6 (+1.22) | 3.4 | -0.5 (-0.10) / +2.2 (+0.41) / -1.7 (-0.25) | n/a | -0.006 / +0.037 | -0.22 / -0.07 | -0.83 | 5/9 | not run | none |
| H4 k1.5 h3 | -4.6 (-0.69) / -9.0 (-0.84) | 5.1 | -4.6 (-1.07) / -8.0 (-1.51) / -2.2 (-0.35) | n/a | -0.068 / -0.137 | -1.15 / -1.01 | -1.67 | 2/9 | not run | none |
| H4 XS h1 | +0.9 (+0.34) / +2.5 (+0.89) | 3.0 | +2.5 (+0.76) / -3.7 (-1.04) / -3.1 (-0.50) | < 0 | +0.049 / -0.094; +0.42, -0.80 | +0.58 / +0.82 | -0.28 | 3/9 | not run | none |
| H4 XS h3 | -0.7 (-0.16) / +2.7 (+0.55) | 4.6 | -3.2 (-1.05) / +0.3 (+0.08) / +0.8 (+0.14) | n/a | -0.067 / +0.007 | -1.16 / -0.99 | -2.08 | 3/9 | not run | none |
| C1c k1.0 h1 (control) | +49.7 (+1.74) / +12.9 (+0.35) | 9.4 | +13.8 (+1.35) / +5.7 (+0.57) / -5.8 (-0.69) | 0.42 | +0.126 / +0.070; +1.07, +0.60 | +1.25 / +1.36 | +0.87 | 7/9 | 0.97; 0.95 / 0.92; 0.95 | control; IS t < 2 |
| C1c k1.0 h3 (control) | +44.8 (+1.41) / +82.4 (+1.48) | 12.7 | +5.6 (+0.71) / +11.2 (+1.22) / -4.8 (-0.61) | 1.99 | +0.060 / +0.138; +0.51, +1.18 | +0.61 / +0.68 | +0.77 | 4/9 | 0.94; 0.90 / 0.97; 0.96 | control; IS t < 2 |
| C1c k1.5 h1 (control) | +71.0 (+1.45) / +54.7 (+1.10) | 11.9 | +20.5 (+1.26) / +18.4 (+1.34) / +6.0 (+0.46) | 0.90 | +0.158 / +0.197; +1.35, +1.69 | +1.18 / +1.25 | +0.71 | 6/9 | 0.98; 0.98 / 0.97; 0.98 | control; IS t < 2 |
| C1c k1.5 h3 (control) | +38.5 (+0.63) / +148.9 (+2.14) | 15.9 | +9.9 (+0.66) / +24.4 (+2.06) / -5.1 (-0.42) | 2.46 | +0.073 / +0.289; +0.63, +2.47 | +0.60 / +0.65 | +1.55 | 6/9 | 0.90; 0.85 / 1.00; 0.99 | control; IS t < 2 |

Other controls (C1 managed-money crowding, C3 swap dealers, 8 cells): IS net t -1.30..+0.10, VAL -1.28..-0.02: none.
"Random" was run only where IS t >= 1 or IS and VAL were both > 0 (as declared, it cannot rescue a cell below the
IS bar). Random (a) = same sides on random tradable Fridays per leg; (b) side recomputed from the unthresholded
signal at the random Friday; 200 seeds.

## Cells and chance benchmark
- 24 graded + 6 fallback book cells (30), 12 commodity control cells, 208 single-market cells.
- Best-of-24 graded cells, IS mid t with weeks sign-flipped jointly (500 draws): median 1.60, p95 2.72; observed best
  1.87 (p 0.34).
- Single-market cells (208): IS net t > 2 in 6, < -2 in 16 (chance ~5 each side; the extra losers are cost), mean t
  +0.01. The best with VAL data: H3 k2 h3 NQ +82.5 bp (t 3.24, n 27; VAL +10.6, t 0.20), H1 k1.5 h1 CAD +13.8 (2.85,
  n 40; VAL +1.8, t 0.41), H1 k1.5 h3 NQ +69.4 (2.77, n 50; VAL -31.8). None has IS t >= 2 with VAL t >= 1.

## Reading
- Leveraged-fund crowding (H1) is the cleanest TFF idea and the only one with a positive IS mid in every cell
  (+2.4..+14.4 bp), but it is small (Sharpe <= 0.05 a week), and every VAL is negative (2022-23 losses: book -15.1
  and -7.8 sd x100 a week). Weekly crowding information is already 3 days old at release (as-of Tuesday).
- Asset-manager flow does not continue over 1-3 days; if anything it reverses in 2016-21 (H2 XS h3 IS net t -3.00),
  but VAL (-0.23) and PRE (+0.20) do not repeat it, so it is not a usable reversed rule either.
- The KRT liquidity effect (fade speculators' weekly position change) is visible in commodities (C1c, positive IS and
  VAL in 4 / 4 cells) but not in financial futures (H1c: IS t -1.72..+0.41). In commodities its IS is 2020-heavy
  (C1c k1 h1 2020 week mean +69 sd x100 vs +4.8..+12.1 other IS years) and its PRE is negative, so it does not reach
  DEMO; see "Directions".

## Exhausted after this stream (for PROMPT "Những họ đã cạn")
- CFTC TFF futures-only positions 2010-24 (leveraged-fund level and change, asset-manager change, dealer level,
  asset managers vs leveraged funds, threshold and 3 / 3 cross-section books over 13 legs incl. VIX -> US500),
  1-3 days after the Friday release: no cell above IS net t +0.76.
- Disaggregated managed-money level and swap-dealer level on gold, silver, WTI, gas: none; managed-money change
  (KRT) positive but IS t <= 1.35.

## Pitfalls
- **www.cftc.gov's robots.txt names ClaudeBot, anthropic-ai and Claude-Web with `Disallow: /`** (Cloudflare-managed
  block, read 2026-10-30): do not fetch cftc.gov files again (round 39 fetched the legacy annual zips on 10-29; those
  on-disk copies in r39/D/web/s7 are usable as a check). publicreporting.cftc.gov answers 403.
- The Hugging Face mirror `XOOMAR/cftc-commitments-of-traders` matches CFTC exactly (OI, non-reportable) but starts
  2010 (TFF from 2010-07-20), has no spreading columns, keys NYMEX WTI 067651 only from 2022, and contains 2025-26
  rows: never `head` it; parse with the cut. Other HF COT sets are parquet (no reader in the venv) or last-12-months.
- The vol-scaled book needs 52 weeks of IC history per symbol, so IC-only legs (indices) start 2017-02 in that book;
  check the equal-weight bp book for 2016.

## Directions that need the user
| direction | value (chance of a candidate) |
|---|---|
| A parquet reader in a scratch venv (pyarrow), to use ZipLime's point-in-time COT mirror (release timestamps, TFF from 2006, options + futures) | DEMO < 1 %, LIVE ~0 % (the futures-only TFF set already shows nothing at 1-3 days) |
| Commodity KRT rule (fade managed-money weekly change) on all IC commodity CFDs (XAU, XAG, XPT, XTI, XBR, XNG) as a fresh declared family: IS is already seen for 4 of 6 legs and 2020-heavy | DEMO ~2 %, LIVE ~0 % (weekly) |
| Permission to fetch www.cftc.gov despite its ClaudeBot block (e.g. a user-run download into research/data) | only needed for 2006-09 TFF or post-2024 data; ~0 % for this family |

## Scripts and outputs (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r44/T/`)
- `scripts/fetch.sh` (logged fetches), `scripts/tff_parse.py` (mirror -> `out/tff.json`, cut at parse),
  `scripts/validate.py` (vs CFTC legacy files on disk), `scripts/sig.py` (signals), `scripts/counts.py`,
  `scripts/run.py` (grading, random control, benchmark, singles -> `out/cells.json`, `out/run.log`),
  `scripts/run_h4.py` (-> `out/cells_h4.json`), `scripts/table.py`; price panel `out/panel_r39.npz` (copy of round
  39 D's panel; its builder copied as `scripts/build_panel_r39_copy.py`).
- Downloads: `web/s1` (HF search JSON), `web/s2` (dataset cards), `web/s3/cot.csv` (mirror), `web/robots/`, log
  `web/requests.log`.
