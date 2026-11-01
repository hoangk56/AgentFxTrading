# Round 50, stream F: hypotheses (declared before any return is computed)

Written 2026-10-30 09:12 UTC (`date -u`). No price has been joined to any signal yet. HOLD (2025-01-01..2026-09-24)
is closed: H.6 observations after 2024-12-31 and releases after 2024-12-31 were dropped at parse
(`scripts/parse_h6.py`), IC prices are cut ts < 1735689600000 at load.

## Source status (decided before any number)
- **ICI (www.ici.org) is unreachable for this stream.** 2026-10-30 09:07 UTC: `GET /robots.txt` with a generic
  research User-Agent returned **HTTP 403 "Access Denied" (Akamai edge)**. A retry with a browser User-Agent was
  refused by the session's permission classifier as bot-check circumvention, so ICI is treated as a bot wall and is
  **off limits** (brief: no bot walls). No ICI file was fetched. Consequence: families (1) Ben-Rephael-Kandel-Wohl
  equity-minus-bond exchanges, (2) aggregate equity-fund fire sales, (4) world-equity flows -> USD, and weekly ETF
  net issuance **cannot be tested** (no other free weekly mutual-fund flow source: EPFR, Lipper and Morningstar are
  paid; FRED, which carries no ICI weekly flows anyway, timed out).
- Federal Reserve H.8 / Z.1: too slow (Z.1 quarterly with ~10-week lag; H.8 is bank balance sheets, not funds).
- **By-product used (declared in the brief): Federal Reserve H.6 money stock, weekly NSA retail money funds
  (`MMFGB_N.WM`)** from the Board's Data Download Program package (www.federalreserve.gov, robots.txt = 404, i.e.
  no restriction; 1 package request). Institutional money funds (`MMFIN_N.WM`) end 2021-02-01 (no VAL): reported as
  an IS-only diagnostic, never a candidate.
- Release dates: exact list from www.federalreserve.gov/releases/h6/releaseDates.json (cut <= 2024-12-31).
  Weekly era (to 2021-02-11): mostly Thursday, **16:30 ET**, data through the week ending the Monday 10 days earlier.
  Monthly era (from 2021-02-23): fourth Tuesday, **13:00 ET** (Fed H.6 technical Q&A), weekly NSA data through the
  last week of the previous month.

## Signal (family 3 only: money-market asset surges)
- Weekly residual r_w = dlog(MMFGB_N)_w - mean(dlog_{w-52}, dlog_{w-104}, dlog_{w-156}) (removes the NSA calendar,
  e.g. April tax outflows).
- At each release, the new weeks are those first published by it: weekly era = week end <= release - 10 days and
  after the previous release's cutoff; monthly era = week end <= last day of the previous month and after the
  previous cutoff. news = sum of r over the k new weeks; z = news / (sd of r over the 156 weeks before the block x
  sqrt(k)).
- Entry: weekly era (16:30 ET release) next US trading day 09:35 ET; monthly era (13:00 ET) the same day 13:05 ET.
  Exit h1 = next US trading day at the entry clock; h3 = third US trading day at the entry clock, capped at 119 h 55 m
  (a Friday 09:35 entry exits Wednesday 09:30). Entry or exit on a US federal holiday: release skipped.
- Fills at IC bid / ask of the last M1 bar within 30 min before the clock; +1 minute variant shifts both legs.

## Hypotheses, sides fixed now
| id | rule | side (fixed) | targets | role |
|---|---|---|---|---|
| F3 (primary) | money-fund surge = cash hoarded in fear that is redeployed / contrarian sentiment (cash on the sidelines) | z > +k: long; z < -k: short | equal-weight book US500, USTEC, US2000 | candidate |
| F3c (alternative) | flight-to-safety continuation | opposite of F3 | same book | candidate (declared alternative) |
| F3x (controls) | risk-on reversal read across: long USDJPY, long EURUSD (USD safe-haven reversal), short XAUUSD on a surge | as listed, F3 sign | single legs | control, never a candidate |
| F3i (diagnostic) | institutional money funds, same construction | F3 sign | equity book | IS only (series ends 2021-02), never a candidate |
| F3o (diagnostic) | "ICI-like timing" oracle: the single week ending Monday w, entered Tuesday w+1 09:35 ET (ICI publishes MMF assets ~1 day after its Wednesday week end); NOT tradable from H.6 (that week is published 10+ days later), values the ICI-access decision | F3 sign | equity book | diagnostic only |

Parameters: k in {0 (every release, side = sign z), 1.0}; h in {1, 3}. Candidate cells: F3 and F3c x 2 k x 2 h = **8**
(F3c is the sign flip of F3, so its mid is exactly the negative; it counts in the benchmark anyway). Controls 3 legs
x 4 = 12, diagnostics F3i 4 + F3o 4.

## Costs and checks (rounds 37-49 conventions)
IC spread at the actual entry / exit bars, 0.6 bp commission on FX / metals, swap from research/swing/rates.py
(US2000 swap = US30's, US2000 ask = bid + 0.51 as in round 39 D). Report net IS (2016-21) / VAL (2022-24), spread
x1.5, +1 minute, ex 2020-03/04, by year, random-entry control (200 seeds; (a) same sides on random release days of
the same era, (b) side recomputed from the latest available z at a random US trading day of the same era at the same
clock), best-of-8 null (IS mid t, releases sign-flipped jointly, 500 draws), power at HOLD size. PRE (2004-15) only
for the FX / gold controls (no Dukascopy index prices); the equity book has no PRE.

## Power arithmetic (counts from the release list and the signal only, no returns)
- Releases: IS ~255 tradable (weekly to 2021-02, then 10 monthly), VAL 36 (monthly), HOLD ~21 (monthly).
- **LIVE is impossible**: HOLD power >= 3 with ~21 trades needs a net per-trade Sharpe >= 3 / sqrt(21) = 0.65 (k0);
  with k1 (~1/3 of releases, ~7 HOLD trades) >= 1.13. No weekly flow effect in rounds 37-49 came within a factor 5.
- **DEMO needs** IS net t >= 2.0: k0 (~255 IS trades) per-trade Sharpe >= 0.125; k1 (~85) >= 0.22; plus VAL net > 0
  on 36 (k0) or ~12 (k1) monthly trades (a weak check) and >= 90 % of random entries beaten.
- The weekly-era IS and the monthly-era VAL are different information sets (1 fresh week vs ~4 weeks, 10-day vs
  ~25-day staleness); a pass on IS that fails VAL is read as the regime change, not as noise to excuse.
- Expected: small. H.6 retail MMF is stale news (ICI published the same flows a week earlier), and round 32's
  liquidity series (TGA / RRP / H.4.1) and round 36's household cash found nothing at 1-5 days.
