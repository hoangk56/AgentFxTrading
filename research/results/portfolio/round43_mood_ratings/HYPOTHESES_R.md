# Round 43 stream R: sovereign credit-rating actions -> rated country's index CFD and currency

Declared 2026-10-30 05:30 UTC (from `date -u`), before any return was computed. Events loaded and counted; no price
joined to any event yet.

## Source (declared)
- **countryeconomy.com/ratings/<country>** (Alldatanow S.L., Madrid; compiled public history of Moody's, S&P and Fitch
  long-term foreign-currency sovereign ratings with date and outlook). Free, no login. Terms (legal/terms, 2018) do not
  forbid automated access; robots.txt allows `/ratings/` for `User-agent: *` (it disallows the crawlers
  ClaudeBot / Claude-SearchBot / GPTBot etc. for indexing / training, and explicitly allows user-triggered agents such as
  ChatGPT-User; this was a user-directed fetch of 24 pages at >= 2 s spacing with a browser UA, under the `*` rules).
  Fetched 2026-10-30 05:20-05:23 UTC: italy, spain, france, germany, uk, japan, usa, australia, hong-kong, china, mexico,
  canada, new-zealand, switzerland, norway, sweden, singapore, portugal, greece, ireland, cyprus, slovenia
  (web/ce/*.html in the scratchpad). Parser `scripts/parse.py` keeps the long-term foreign-currency column of each
  agency table and **drops every row dated after 2024-12-31 at parse** (max kept date 2024-12-14).
- Check against known actions: S&P UK AAA -> AA 2016-06-27 (present), Moody's UK Aaa -> Aa1 2013-02-22 (present),
  Fitch UK AA+ -> AA 2016-06-27 (present), Moody's US outlook negative 2023-11-10 (present), S&P France AA -> AA-
  2024-05-31 (present), Moody's France Aa2 -> Aa3 2024-12-14 (present, dated Saturday = EU-time date of a Friday-night
  NY release). **Fitch US AAA -> AA+ 2023-08-01 is missing**: Fitch coverage stops around 2020 for most countries (last
  Fitch row US 2020-03, UK 2020-03, Germany 2020-01, Japan 2020-02). S&P lists changes only (no affirmations);
  Moody's lists changes and some periodic reviews.
- Disclosure: the very first probe of the Italy page printed its flattened text, including 2025-26 rating rows (Moody's
  2025-05 / 2025-11, S&P 2025-04 / 2026-01) before the parse cut existed. No price or return of 2025-26 was seen; the
  HOLD price cut is unaffected. From then on every 2025+ row is dropped at parse.
- Unusable / not reachable: disclosure.spglobal.com (403 incl. robots.txt), fitchratings.com 17g-7 page and
  ratings.moodys.com/sec-17g-7b (JavaScript apps, no static file links; not pursued further), dt.mef.gov.it (403),
  agency EU calendars (S&P site 403; Fitch / Moody's calendars inside the same JS apps / login).

## Event list construction (declared)
- Agencies: **Moody's + S&P only** for the action families (Fitch dropped: incomplete after 2020 -> IS/VAL would not be
  comparable). Fitch rows are used only for family B (EU calendar dates 2014-20).
- An event = a row whose rating or outlook differs from the previous row of the same agency and country.
  Direction: rating change dominates (notch scale); else outlook score Positive +1, Stable 0, Negative -1, "Under
  Review" -1 if the previous outlook was Stable or Negative, +1 if Positive. NEG = rating cut or outlook worsens
  (incl. Positive -> Stable); POS = upgrade or outlook improves (incl. Negative -> Stable). Affirmations are not events.
- Same country, same direction within 3 calendar days (e.g. UK 2016-06-24 Moody's + 06-27 S&P) = one event (first
  date). t is clustered by entry date across countries.
- Timing: release times are not in the source and dates are local / EU / NY dates. To avoid look-ahead the action is
  treated as known only by D+1 05:00 UTC. Entry = first weekday d > D (d = Monday for Fri-Sun dates) at the symbol's
  clock: London 08:05 (European indices, EUR / GBP / CHF / NOK / SEK FX), NY 09:35 (US500, USDCAD, USDMXN), 06:05 UTC
  (JP225, HK50, AUS200, USDJPY, AUDUSD, NZDUSD, USDCNH, USDSGD). Fill at the first quote at / after the clock (+1 min
  for the latency run). Exit at the same clock k = 1, 2, 4 weekdays later, capped so the hold is <= 120 h (k = 4 from
  a Thursday / Friday becomes the last weekday within 120 h).
- Counts (Moody's + S&P changes before merging): PRE 2004-15 ~185, IS 2016-21 ~100, VAL 2022-24 ~47, over 22
  countries; ~70 % are periphery / EM (Cyprus, Greece, Portugal, Slovenia, Ireland, Mexico). Downgrades + negative
  outlooks 2016-24: ~4.5 a year.

## Legs (country -> symbol, side for a NEG event; POS = opposite)
- Index short: italy IT40, spain ES35, france F40, germany DE40, uk UK100, japan JP225, usa US500, australia AUS200,
  hong-kong HK50, china HK50.
- Currency short (sell the rated currency): euro sovereigns (IT, ES, FR, DE, PT, GR, IE, CY, SI) -> sell EURUSD; uk sell
  GBPUSD; japan buy USDJPY; usa buy EURUSD (sell USD); australia sell AUDUSD; new-zealand sell NZDUSD; canada buy
  USDCAD; switzerland buy USDCHF; norway buy USDNOK; sweden buy EURSEK; mexico buy USDMXN; china buy USDCNH;
  singapore buy USDSGD.
- Spillover (Afonso, Furceri & Gomes 2012): euro periphery events (IT, ES, PT, GR, IE, CY, SI) -> short STOXX50.

## Hypotheses (sides fixed here from the literature; never changed after numbers)
- **A1** NEG -> short the local index, k = 1, 2, 4 (3 cells). Literature: downgrades / negative outlooks move spreads
  and equities and spill over (Gande & Parsley 2005; Afonso et al. 2012; Brooks, Faff, Hillier & Hillier 2004), with
  slow-moving rating-constrained holders adjusting over days.
- **A2** NEG -> sell the local currency, k = 1, 2, 4 (3 cells).
- **A3** POS -> long the local index; **A4** POS -> buy the local currency (k = 1, 2, 4; 6 cells). Literature: upgrades
  have little effect; expected ~0 (control of the asymmetric claim).
- **A5** periphery NEG -> short STOXX50 and sell EURUSD; POS -> the reverse (k = 1, 2, 4; 3 cells, signed).
- **A6 (primary book)** all events, all legs above (index + currency + spillover), signed by direction, k = 4; this is
  the cell with the most events. Sub-splits reported, not separately graded: rating changes only vs outlook-only.
- **D0 (diagnostic, not tradable)** mid move from the same clock on D (before the release for EU Friday-evening
  actions) to the entry clock d: does the information move the price at all.
- **B1 (pre-review positioning)** Fitch EU calendar Fridays 2014-20 (affirmations and actions of IT, ES, FR, DE, UK,
  PT, GR, IE, CY, SI), outlook in force Negative -> short the local index / sell the currency (periphery: STOXX50 /
  EURUSD) from Monday London 08:05 of the review week to Friday 16:25 London; Positive outlook -> the reverse
  (1 cell, signed).
- **B2 (non-action relief)** Fitch EU calendar date with no change and outlook Negative -> long the local index / buy
  the currency at the next Monday 08:05 London, k = 1, 2, 4 (3 cells); Positive outlook and no upgrade -> the reverse.
  Family B has no VAL (Fitch rows stop ~2020; no free calendar for 2022-24 reachable), so it **cannot reach DEMO**;
  it is an IS (+ 2014-15 PRE on FX) check only.
- Cells: A 18 + A6 1 + B 4 = 23 graded cells; chance benchmark = max |t| of 23 normals (~2.6 at the 50th percentile of
  the max... reported with a sign-flip permutation over entry dates).

## Costs / controls
- IC M1 bid / ask at the minute for the 26 cached symbols; IT40 / ES35 / F40 / STOXX50 from the bid-only zbars with
  round 7's published spreads (IT40 9.0, ES35 4.2, F40 1.79, STOXX50 1.5 points); USDCNH / USDMXN / USDSGD / USDNOK /
  EURSEK from IC ticks (bid / ask). Commission 0.6 bp for FX. Swap: research/swing/rates.py where modelled (DE40's
  model for the four new euro indices); EM FX without a rate series: -2 bp / night against the position for USDMXN,
  -0.5 bp / night for USDCNH / USDSGD / USDNOK / EURSEK (placeholder, disclosed).
- PRE 2004-15: Dukascopy bid only (EURUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, EURNOK, EURSEK, USDNOK, USDSGD, USDMXN
  2007+, USDCNH 2012+); no index PRE; cost = IC 2016-17 median spread at the clock + 0.6 bp.
- Random control: >= 200 seeds; each event's legs re-drawn on a random weekday of the same era and same weekday as the
  real entry, same side and k.

## Power arithmetic (done before any return)
- LIVE needs power = per-trade net Sharpe x sqrt(HOLD trades) >= 3. HOLD (21 months) would hold ~8 NEG events and
  ~25-30 event dates over all legs, so LIVE needs a per-event Sharpe >= 1.06 (NEG only) or >= 0.55 (A6 book):
  **unreachable by count**; no 1-5 day event rule in 42 rounds has shown more than ~0.2.
- DEMO needs IS day-clustered t >= 2.0: with ~38 index-leg events in IS (A1 + A3) a per-event Sharpe >= 0.32; for A6
  (~85 IS entry dates) >= 0.22. A 4-day index hold has sd ~250 bp, so DEMO needs ~55-80 bp per event net. Expect
  **DEMO at most, more likely none** (developed-market equity reactions in the literature are small; most events are
  periphery / EM sovereigns whose own equity indices IC does not carry).
