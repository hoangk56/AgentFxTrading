# Round 19: declared-only hypotheses — home currency into its own fix; a second literature pass (2026-10-06)

Round 18 found that rules declared from a mechanism, the literature or 2004-15 held 65-103 % of their size in the
holdout, while post-hoc picks held 19-31 %. This round therefore declared every cell in full before computing and ran no
scans ([round19_declared/BRIEF.md](round19_declared/BRIEF.md); `HYPOTHESES_H/T.md`, `STREAM_H/T.md` in
[round19_declared/](round19_declared/)).

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.**

## H. The E1 mechanism in other currencies (23 declared cells)
- Fixes from official sources with their time history: Bank of Canada noon rate (to 2017-04-28) and daily average
  (08:00-16:00 ET, from 2017-05-01), RBA 16:00 Sydney, RBNZ (11:10 NZ to 2015-04, then the 14:00 NZFMA fix), WM/R 16:00
  London for GBP, SNB 11:00 Zurich, TMA USD/CNY(HK) 11:00 Hong Kong, CFETS 16:30 Beijing close. Side: the home
  currency weakens into its fix (120 min) and recovers after (15 / 60 min). The pipeline reproduces E1 exactly.
- **E1's mechanism does not generalise.** CAD, AUD, NZD, GBP and CHF show no weakening into their fixes in any era;
  CHF and the CAD noon rate move the wrong way; INTO cells have the predicted sign in 2/8 (IS) and 3/7 (VAL). The RBA,
  SNB and BoE rates are observations of the market rather than dealing fixes.
- **The renminbi is the exception:** USDCNH rises into the CFETS 16:30 Beijing close, +1.22 bp (t 4.57) IS / +1.68
  (t 4.08) VAL, beyond chance (null 95th percentile 3.14), beats 100 % of random windows, and the effect disappears on
  mainland holidays (business day minus holiday t 2.10, 53 blocks). It is a sharper, mechanism-checked version of
  round 7's "CNH home hours". At IC's ~1.04 bp cost (published spread; IC's USDCNH cache is bid-only) it nets +0.19
  (t 0.69) IS / +0.66 (t 1.61) VAL: below DEMO (needs a round trip <= 0.69 bp), far below LIVE.

## T. Second literature pass (34 papers mapped, 7 families, 63 declared cells)
- Search through Crossref venue filters (OpenAlex was rate-limited), central-bank working-paper prefixes, arXiv, web
  search for BIS papers.
- None beats chance (expected max |z| ~2.6 over 63 cells):
  - pre-announcement drift before NFP/ISM/GDP (Hu, Pan, Wang & Zhu 2022): none on IC's indices;
  - dash for cash (Etula et al. 2020): VAL gain is 2022-23 only;
  - Monday-move reversal (Ülkü & Andonov 2016): the 1-day version is +14.1 bp net (t 1.83) IS / +4.6 VAL, shrinking;
  - "Tuesday blues" in AUS200: wrong side; the paper's conditional version used look-ahead;
  - Bitcoin Monday, crude Monday/Wednesday (April 2020 drives IS);
  - FX weekend-gap fade (Dao, McGroarty & Urquhart 2016): strong in PRE (EURUSD +32 bp t 3.4, USDJPY +26 t 2.5), gone
    since publication.

## What this says
- Declared-only testing works as a filter: 86 declared cells, two real effects (the CNY close; the weekend-gap fade in
  2004-15), no false candidates. But the real ones are either below IC's cost or already gone.
- The fix effect that holds is where the fix is binding for the flow (the ECB reference rate for EUR, the CFETS close
  for CNY, the Tokyo TTM for JPY = C3). Fixes that only observe the market do not move it.

## Directions that need the user's decision
- IC USDCNH ask / tick data 2016-24 (the CNY-close cost is a published average); even at the true spread DEMO needs
  <= 0.69 bp.
- Price series for other binding-fix currencies (USDSGD, USDHKD TMA 11:00, USDMXN Banxico 12:00, USDZAR, Scandinavian)
  — where the CNY-close mechanism would be tested next. New symbols, so the user's decision.
- Dukascopy index CFDs 2004-15 (Monday reversal); an S&P 500 dividend-payment calendar (Hartzmark & Solomon); the BoJ's
  ETF selling schedule once public (a new flow, from 2026).

## Process and disclosures
HOLD not loaded. Stream H had seen round 7's hourly USDCNH profile before declaring (disclosed). Stream T's two
corrections written after seeing numbers (AUS200 executable variant, a first-quote fix for XBR) are information only.
Scripts in the scratchpad (`r19/H`, `r19/T`). Nothing in `research/` code was edited.
