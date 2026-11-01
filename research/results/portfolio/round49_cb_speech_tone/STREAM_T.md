# Round 49, stream T: hawkish / dovish tone of Fed Board and ECB speech texts -> EURUSD, USDJPY, XAU, US500, DE40

Written 2026-10-30 09:03 UTC. Declared before any return in [HYPOTHESES_T.md](HYPOTHESES_T.md) (08:41 UTC; the first
return was computed at ~08:45 UTC in a smoke test of the grader, after the file existed). No addendum. HOLD stayed closed:
the Fed list and the ECB CSV were cut at < 2025-01-01 at parse (no speech page after 2024-12-31 was requested), IC M1 at
ts < 1735689600000 at load (assert), Dukascopy ends 2015, FOMC calendar rows after 2024 dropped at parse.

## Answer
**No LIVE or DEMO candidate, no PREREG_DRAFT.** 0 of 76 cells reach IS net t 2 (best +1.59, US500 F2 NY close k1, n 48;
chance p95 of the best-of-76 IS t = 2.71). The primary declared cell (Fed BOOK, posting + 15 min, 1 day, |x| >= 1) is
IS +2.92 bp (t 0.57), VAL +17.50 (t 1.26), PRE -3.17 (t -0.53). The dictionary measures tone correctly (yearly mean
Fed tone -0.30 in 2015-16, +0.40 in 2022-23; ECB +0.3 in 2005-07, -0.4 in 2014-16, +0.45 in 2022), but the market does
not react to it within 15 minutes (signed T-1 -> T+15 moves -1.2 to +0.7 bp, |t| <= 1.3, in every era), and the later
drift exists only in VAL, almost entirely in 2022.

The one pattern worth noting: Fed tone surprises with |x| >= 1 drift in the policy direction on all four legs from
+15 min to the NY close in VAL (BOOK +16.7 bp, t 3.12, random 1.00, x1.5 +16.6, +1 min +17.2), but 2022 alone is +52.4
bp, 2023 +15.9, 2024 +3.6. IS is +3.0 (t 1.24) and PRE (FX + gold, 2010-15) is -3.7 (t -0.86). That is a regime effect
of the 2022 hiking cycle, when every Fed word moved rates, and it was already fading in 2024. It is not a candidate:
it fails DEMO's IS t, and round 18 found that rules seen to work only in VAL keep 19-31 % of their VAL size in HOLD.

## Sources (robots read first)
| host | robots.txt | used | requests |
|---|---|---|---|
| www.federalreserve.gov | 404 (no robots file, so no rules) | `json/ne-speeches.json` (1,349 rows; 1,157 dated 2006-01..2024-12, posting time ET in `d`); 1,156 speech pages `newsevents/speech/*.htm` (0 errors); `monetarypolicy/fomccalendars.htm`, `fomchistorical2009..2020.htm` | ~1,170, 1.2 s spacing, 08:38-09:02 UTC |
| www.ecb.europa.eu | `User-agent: *`, Crawl-delay 5, no ClaudeBot / anthropic-ai / Claude-Web entry; path not disallowed | `press/key/shared/data/all_ECB_speeches.csv` (ECB's own speech dataset, 58 MB, 2,865 rows 1997-2024 after the cut; **dates only, no times**) | 2 (HEAD + GET) |
Not used: data-api.ecb.europa.eu (disallows ClaudeBot), web.archive.org. No logins, no e-mail in any request, plain UA.
The FOMC calendar fetch (13 requests, 1.5 s spacing) overlapped the last ~4 minutes of the speech fetch on the same host
for ~20 s (a waiter mistook a pgrep miss for a dead worker): about 1.5 requests a second for those 20 s.

Counts after the declared filters (H + D >= 5 and a speaker history): Fed 482 speeches with a signal 2010-24
(PRE 162, IS 182, VAL 138: ~30 / year IS, 46 / year VAL), fewer than the ~40 / year assumed in the power section
(43 % of Board speeches are on regulation / payments and have < 5 dictionary hits). ECB 1,341 English speeches with a
signal 1999-2024; 309 IS and 143 VAL trading days.

## Results (net bp per trade; t day-clustered, F3 3-day Newey-West)
| hypothesis | eras | mid IS (t) | cost IS | net PRE / IS / VAL (t) | VAL / IS | Sharpe IS, VAL; power at VAL size | random IS / VAL | x1.5, +1 min (IS) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **F1 Fed BOOK L15 1d k1 (primary)**, n 66 / 77 / 40 | PRE, IS, VAL | +4.62 (0.91) | 1.70 | -3.17 (-0.53) / +2.92 (0.57) / +17.50 (1.26) | 6.0 | 0.069, 0.282; 1.36 | 0.85 / 0.99 | +2.61, +2.70 | none (IS t) |
| F1 Fed BOOK L15 NY close k1, n 67 / 80 / 40 | PRE, IS, VAL | +4.17 (1.65) | 1.14 | -3.69 (-0.86) / +3.04 (1.24) / +16.74 (3.12) | 5.5 | 0.122, 0.543; 2.61 | 0.95 / 1.00 | +2.70, +3.27 | none (IS t; VAL = 2022 +52 bp) |
| F1 Fed BOOK L15 NY close k0, n 140 / 170 / 124 | PRE, IS, VAL | +1.61 (0.98) | 1.16 | -3.01 (-1.00) / +0.45 (0.44) / +5.78 (1.44) | 13 | 0.017, 0.184; 1.56 | 0.79 / 0.99 | +0.10, +0.42 | none |
| F1 Fed US500 L15 NY close k1 (best F1 IS t), n 77 / 38 | IS, VAL | +13.01 (1.84) | 1.60 | - / +11.41 (1.58) / +26.58 (1.87) | 2.3 | 0.190, 0.315; 1.48 | 0.97 / 1.00 | +10.61, +12.02 | none (IS t < 2; 2022 +152, 2024 -7) |
| F1 Fed EURUSD L15 NY close k1, n 67 / 80 / 40 | PRE, IS, VAL | +3.13 (1.35) | 0.69 | +4.01 (0.79) / +2.44 (1.08) / +10.43 (1.91) | 4.3 | 0.110, 0.390; 1.87 | 0.84 / 1.00 | +2.40, +2.46 | none |
| F1 Fed USDJPY (8 cells) | PRE, IS, VAL | -3.8 to +5.3 | 0.8 | PRE -8.8 to +10.3; IS best +4.21 (1.02) | - | - | 0.12-0.84 | - | none (PRE close cells t -2.2 to -2.6, wrong sign) |
| F1 Fed XAUUSD (8 cells) | PRE, IS, VAL | -7.1 to +2.4 | 1.5 | PRE all < 0; IS best +0.95 (0.59) | - | - | 0.17-0.73 | - | none |
| F1 Fed all 40 cells | | | | IS t -1.12 to +1.58; VAL > 0 in 37 / 40 | | | | | none |
| F2 Fed filtered (outside blackout, no 08:15-10:45 ET entry, no NFP / minutes day; keeps 305 / 482), 20 cells | PRE, IS, VAL | | | best IS: US500 NY close k1 +14.01 (1.59), n 48 / 26, VAL +19.5 (0.99); BOOK close k1 IS +2.28 (0.69), VAL +14.6 (2.06), PRE -9.3 (-1.88) | | | 0.97 / 0.94 | | none (filter does not raise IS) |
| F1 ECB BOOK 1d k1 (primary), n 163 / 65 | IS, VAL | -4.44 (-1.07) | 1.80 | - / -6.24 (-1.51) / +10.27 (1.83) | < 0 | -0.118, 0.228 | 0.21 / 0.96 | -6.45, -6.76 | none (wrong sign in IS) |
| F1 ECB EURUSD (4 cells) | IS, VAL | -4.6 to -0.2 | 0.6-1.0 | IS -0.85 to -4.73 (t to -2.05); VAL -3.1 to -6.9 | - | < 0 | 0.08-0.52 | | none (wrong sign: hawkish ECB speech -> EUR down next day) |
| F1 ECB DE40 close k0 (best ECB), n 308 / 143 | IS, VAL | +7.80 (1.66) | 1.08 | - / +6.73 (1.43) / +13.32 (1.80) | 2.0 | 0.081, 0.150; 1.37 | 0.93 / 0.97 | +6.19, +6.34 | none (IS t; 2020 -16, 2024 -12) |
| F3 cross-bank tone gap -> EURUSD (4 cells), n 1,136 / 584 (k0) | IS, VAL | -1.8 to +2.5 | 1.0-1.8 | IS -3.56 to +0.81 (best t 0.14); VAL -5.33 to +0.47 | - | <= 0.01 | 0.26-0.80 | | none |

PRE = Dukascopy 2010-15 (EURUSD, USDJPY, XAUUSD; BOOK over those three legs; cost = IC 2016-17 median half spread by ET
hour x 2 + 0.6 bp). Ex 2020-03/04 changes nothing (no speech cell depends on those months: the ex-2020 IS means equal the
full IS means for every Fed cell, and ECB / F3 cells move by < 0.5 bp). By year for the NY-close BOOK k1 cell:
16 -4.1, 17 -3.5, 18 +11.9, 19 -1.3, 20 +17.0, 21 +5.1, 22 +52.4, 23 +15.9, 24 +3.6.

Diagnostic (declared, not a cell), Fed speeches with a signal, signed in the bank direction, posting T-1 -> T+15 min:
EURUSD IS +0.36 (t 0.45), VAL -1.15 (-1.31), PRE -0.30; USDJPY +0.02 / -0.12 / +0.11; XAU +0.69 / +1.32 / +0.31;
US500 +0.08 / -0.63. Slope of the move on x: EURUSD IS +1.24 bp per unit (t 2.37), VAL -1.34 (t -1.68), PRE -0.46.
There is no reaction on publication that keeps its sign across eras. Typical |move| in those 16 minutes: 5-6 bp FX,
10-11 bp XAU / US500.

Information subset (declared, not counted): Chair only, BOOK L15 k1: 1 day IS +8.5 (t 1.11, n 20), VAL +49.6 (n 6),
PRE -2.1 (n 28); NY close IS +11.8 (t 1.98, n 21), VAL +19.0 (n 6), PRE -2.7. ECB President only, BOOK 1d k1:
IS -0.5 (n 60), VAL +8.1 (n 34). About 4 Chair speeches a year pass the filters: no power.

## Cells tried and chance
76 counted cells: F1 Fed 40, F1 ECB 12, F2 Fed 20, F3 4. Chance benchmark: a per-signal sign flip shared across cells
(1,000 draws), 95 % quantile of the max IS net t = **2.71**. Observed max IS t +1.59, min -2.06 (F1 ECB EURUSD 1d k0,
wrong sign). Under the null a few cells would show |t| >= 2 by chance; 1 does, with the wrong sign.

## Power arithmetic (realised)
Fed cells reach at best a VAL Sharpe per trade of 0.54 on 40 VAL trades (~23 HOLD trades a year at k = 1): power at the
VAL size 2.61, under 3 even if VAL's 2022-dominated size held; at the IS size (Sharpe 0.12) it is 0.59. k = 0 cells have
power <= 1.6 at the VAL size. ECB and F3 are <= 1.6 and <= 0.06. LIVE is out of reach in every family, as the
declaration expected. DEMO fails on IS t everywhere.

## What this says
Central-bank speech text on a public clock carries no information past +15 minutes that keeps its sign across eras.
At publication the dictionary tone is not even priced in a consistent direction, which suggests the market reads
speeches by content our pair counts do not capture (forward guidance, data dependence), or that speeches were priced
from earlier media reports and prepared-text leaks. The 2022 drift is the known regime result (speech effects grow
when policy is uncertain) and cannot be traded from a 2016-21 design. Hawkish ECB speeches are followed by a *weaker*
euro the next day in IS (t -2.05 at k = 0), the opposite of the mechanism.

## Exhausted after this round (for PROMPT "Những họ đã cạn")
- Dictionary hawk / dove tone of Fed Board speeches (posting time + 5 / 15 min to the NY close or 1 day; outside
  blackout and off data clocks) and of ECB speeches (date only, next London day), and the Fed-minus-ECB weekly tone gap
  -> EURUSD, USDJPY, XAU, US500, DE40.

## Pitfalls
- federalreserve.gov has no robots.txt (404); `json/ne-speeches.json` covers 2006 onward with ET posting times in `d`,
  and rows run to today: cut at parse. Speech pages: text after `class='location'`, cut at the first footnote anchor
  (`<a name="fn1"`, `<a href="#f1"`) or `id="lastUpdate"`.
- 43 % of Board speeches (regulation, payments, community banking) have < 5 tone hits: speech counts overstate signals.
- The ECB speech CSV (`press/key/shared/data/all_ECB_speeches.csv`, pipe-separated, full texts) has no times and
  includes German / French texts (filter by the share of "the"), interviews and press-conference introductory
  statements; it runs to 2026: cut at parse. www.ecb.europa.eu asks for Crawl-delay 5.
- FOMC historical pages write two-month meetings as "Jan/Feb 31-1" (2016+) or "July 31-August 1" (before): parse both.
- A waiter that checks `pgrep -f <script>` can miss a live worker; check by PID.

## Directions that need the user
| direction | value |
|---|---|
| Reuters / Bloomberg headline timestamps for Fed and ECB speeches (paid), to find when the text first reached the market | LIVE < 1 %, DEMO ~1-2 % |
| Intraday Treasury / Bund futures (paid) to trade the rates channel where the speech literature finds the effect | LIVE < 1 %, DEMO ~2 % |
| An LLM / FinBERT-style tone score instead of the declared dictionary (no new data, but a new declared construction; the 2022 VAL pattern means any new score must be designed on 2010-21 only) | LIVE < 1 %, DEMO ~2 % |

## Files
- Hypotheses: research/results/portfolio/round49_cb_speech_tone/HYPOTHESES_T.md; this file.
- Scripts (scratchpad `/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/a4a9bef6-96f0-4934-8440-9b5af3c564e7/scratchpad/r49/T/scripts/`):
  `fetch_fed.py`, `fetch_fomc.sh`, `tone.py` (dictionary), `build_speeches.py` (scores, surprises, weights ->
  `out/speeches.csv`), `grade.py` (76 cells, random control, chance), `diag.py` (reaction at publication),
  `chair.py` (Chair / President subset). Outputs in `out/` (`grade.txt`, `cells.csv`, `trades.npz`, `diag.txt`,
  `bench.json`); downloads in `web/`.
- Correlation with C3: not computed (nothing survived).
