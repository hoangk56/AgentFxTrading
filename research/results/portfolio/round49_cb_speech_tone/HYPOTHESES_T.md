# Round 49, stream T: hypotheses (declared before any return)

Written 2026-10-30 08:41 UTC (`date -u` 08:40:32 just before writing). No price series has been joined to any speech
yet. Data loaded so far: the Fed speech list `json/ne-speeches.json` (dates / times / speakers, cut at < 2025-01-01 at
parse) and the ECB speech dataset CSV (cut at < 2025-01-01 at parse); Fed speech pages are being fetched (dated
< 2025-01-01 only). IC M1 is cut at ts < 1735689600000 at load; Dukascopy ends 2015.

## Sources and robots
- www.federalreserve.gov: `/robots.txt` answers 404 (no rules). List: `https://www.federalreserve.gov/json/ne-speeches.json`
  (1,349 rows, 1,157 dated 2006-01..2024-12; field `d` = posting / delivery time in ET, `s` = speaker with title,
  `l` = page). Texts: the `l` pages (Board members only: Chair, Vice Chairs, Governors). 1.2 s spacing, plain UA.
- www.ecb.europa.eu: robots.txt `User-agent: *`, Crawl-delay 5, no ClaudeBot / anthropic-ai / Claude-Web entry; the
  path used is not disallowed. One request: `https://www.ecb.europa.eu/press/key/shared/data/all_ECB_speeches.csv`
  (ECB's own speech dataset: date | speakers | title | subtitle | contents; 2,865 rows 1997-2024 after the cut). It has
  **dates only, no times**, so the ECB legs are daily-clock rules. data-api.ecb.europa.eu is not used.
- FOMC meeting dates (for blackout): federalreserve.gov `fomccalendars.htm` and `fomchistorical{YYYY}.htm`, fetched
  after the speech pull.

## Tone dictionary (fixed; in the style of Apel & Blix Grimaldi 2012, "The information content of central bank
minutes", Riksbank WP 261: a hawkish / dovish score from (noun, modifier) pairs in a window)
Text is lower-cased, tags stripped, split into sentences at `.;?!` and into tokens `[a-z]+`. For each noun occurrence,
look at modifiers within 3 tokens before or after it in the same sentence. Nouns (singular / plural forms listed):
- **P (prices, hawkish when up):** inflation, price, prices, cost, costs, wage, wages, pressures (only as
  "inflationary pressure(s)" / "price pressure(s)", counted once via the first noun), expectations (only in
  "inflation expectations", counted once via "inflation").
- **A (activity, hawkish when strong / up):** growth, economy, activity, demand, spending, consumption, investment,
  employment, hiring, payrolls, output, recovery, expansion; "labor market" / "labour market" counted as one noun.
- **U (slack, hawkish when down):** unemployment, slack, joblessness.
- **R (policy rate, hawkish when up):** rate, rates (only within 2 tokens after "interest", "policy", "funds",
  "deposit" or "refinancing").
Modifiers:
- **UP:** increase, increases, increased, increasing, rise, rises, rising, rose, risen, higher, high, strong, stronger,
  strengthening, robust, solid, accelerate, accelerates, accelerated, accelerating, upward, elevated, expanding, firm,
  firming, tight, tighter, tightening, persistent, surge, surged, surging, hot.
- **DOWN:** decrease, decreases, decreased, decreasing, decline, declines, declined, declining, fall, falls, falling,
  fell, fallen, lower, low, weak, weaker, weakening, weakness, sluggish, subdued, slow, slower, slowing, slowed,
  decelerate, decelerated, decelerating, downward, moderating, soft, softer, softening, muted, contracting, contraction,
  slack, subpar.
A noun occurrence with only UP modifiers in its window counts +1 hawkish for P / A / R and +1 dovish for U; only DOWN
modifiers count the reverse; both or neither: 0.
- **Explicit policy words** (counted once each, outside the pairs): hawkish +1: tighten, tightened, tightening (when
  not already used as a pair modifier), hike, hikes, hiking, restrictive; dovish +1: easing, ease, eased, accommodative,
  accommodation, stimulus, stimulative.
Speech score s = (H - D) / (H + D), defined only when H + D >= 5 (speeches below are not traded).
Fed text: the `#article` block of the page with the "References" list and footnotes removed (text after a heading
"References" or "Footnotes"/"Notes" dropped). ECB text: the `contents` field; only English texts (share of the token
"the" >= 3 % of tokens) and titles not starting with "Interview" / "Introductory statement" (press-conference
statements are scheduled policy communication, priced at the decision).

## Standardisation and weights
- Surprise u_i = s_i - mean of the same speaker's previous up to 8 valid scores (min 3; with fewer, the mean of the
  bank's previous 20 valid scores). Warm-up history: Fed 2006-09, ECB 1997-2009 (not traded).
- z_i = u_i / sd of the bank's previous 60 valid u (min 30).
- Speaker weight w: Fed Chair / Chairman 2, Vice Chair / Vice Chairman (monetary) 1.5, Vice Chair for Supervision and
  Governors 1 (title in the `s` field at the time). ECB President 2 (Trichet to 2011-10-31, Draghi 2011-11-01..2019-10-31,
  Lagarde from 2019-11-01), Vice-President (Papademos to 2010-05-31, Constâncio 2010-06-01..2018-05-31, de Guindos
  from 2018-06-01) and chief economist (Stark to 2011-12-31, Praet 2012-01-01..2019-05-31, Lane from 2019-06-01) 1.5,
  other speakers 1.
- Signal x_i = w_i z_i. A trade needs |x| >= k, k in {0 (any x != 0), 1}. Position size is 1 (sign only).
- Side: x > 0 (hawkish surprise) -> the bank's currency up, gold down, index down.
  Fed: short EURUSD, long USDJPY, short XAUUSD, short US500. ECB: long EURUSD, short DE40. (STOXX50 has no M1 cache
  in research/data/m1, so DE40 only.) BOOK = equal-weight mean of the legs' net per signal.

## Timestamps and fills
- Fed posting time T = field `d` (America/New_York). Entry at T + L, L in {5, 15} min; fill at the close of the IC M1
  bar starting at the clock (round 46 `trades_vec` convention: mid +- half the spread at that bar, both legs).
- Exits: (a) NY close: 16:45 ET for FX / XAU (before the 17:00 rollover), 15:58 ET for US500; if T + L is later than
  the exit clock minus 10 min, the exit is the next weekday's clock. (b) 1 day: T + L + 24 h (Friday -> Monday same clock).
- Entries in a closed market (Fri 16:55 ET to Sun 18:05 ET, the 16:55-18:05 ET rollover hour for FX / XAU, the
  16:15-16:30 and 16:59-18:00 ET US500 breaks) are dropped and counted.
- ECB (date only): signal X_D = sum of the day's x (Frankfurt date D). Entry on the next TARGET / London business day
  at 08:00 London; exits (a) the same day 16:30 London (European cash close), (b) the following business day 08:00 London.
- Costs: IC spread at both actual bars, x1.5 variant; commission 0.6 bp round trip on FX and XAU (rounds 40-48);
  swap from research.swing.rates (`swap_frac_at`) per rollover crossed (triple on Wednesday for FX, Friday for indices).
  Latency variant: both legs 1 minute later.
- t: trades are averaged per entry day, t over days (day-clustered). F3 3-day: Newey-West, lag 2, on the daily series.

## Families and cells (76 counted)
- **F1 Fed (40 cells):** {EURUSD, USDJPY, XAUUSD, US500, BOOK} x L {5, 15} x exit {NY close, 1 day} x k {0, 1}.
  **Primary declared cell: BOOK, L = 15, 1 day, k = 1.**
- **F1 ECB (12 cells):** {EURUSD, DE40, BOOK} x exit {same-day close, 1 day} x k {0, 1}. Primary: BOOK, 1 day, k = 1.
- **F2 Fed filtered (20 cells):** F1 Fed with L = 15 only, restricted to speeches (i) outside the FOMC blackout
  (from the second Saturday before the meeting's first day through the day after its last day; scheduled meetings),
  (ii) whose entry is not 08:15-10:45 ET (the 08:30 / 10:00 data clocks), (iii) not on the first Friday of the month
  (Employment Situation proxy) and not on an FOMC-minutes day (scheduled decision + 21 days). {4 symbols, BOOK} x exit 2 x k 2.
- **F3 cross-bank (4 cells):** each London business day D: F = mean of Fed x over speeches dated D-6..D, E = the same
  for ECB (0 when a bank has none; no trade if neither has any). y = (F - E) / sd of y over the previous 250 days (min 120).
  y > k -> short EURUSD, y < -k -> long; entry D+1 08:00 London, hold {1, 3} business days (3 days: <= 120 h,
  overlapping, <= 3 open); k in {0, 1}.
- Diagnostic, not a cell: signed mid move T-1 -> T+5 and T-1 -> T+15 min vs the Fed side (does the market react to
  the dictionary tone at all?), and the same with the ECB D+1 open gap.
- Information subset (not counted): Chair / President only, primary configuration.

## Eras and checks
IS 2016-21 (IC), VAL 2022-24 (IC), PRE 2010-15 on Dukascopy (EURUSD, USDJPY, XAUUSD; cost = IC 2016-17 median half
spread by ET hour x 2 + 0.6 bp) for the primary cells and any cell with IS t >= 2. By year, ex 2020-03/04, spread x1.5,
+1 minute. Random-entry control (200 seeds): the same speeches' sides and clock times placed on random weekdays of the
same year (speech-time matched), cost and swap recomputed; percentile of the real net. Chance: per-trade sign flip shared
across all 76 cells, 95 % quantile of the max IS net t (1,000 draws).

## Bars
LIVE: IS t >= 2.5, VAL t >= 1.5, >= 2/3 years > 0, random >= 95 %, HOLD power >= 3. DEMO: IS t >= 2, VAL net > 0,
random >= 90 %; + positive at x1.5 and +1 minute. No HOLD opened in any case.

## Power arithmetic (before any return)
Fed Board speeches in the list: 2016-21 341 (57 / year), 2022-24 246 (82 / year). With ~75 % passing H + D >= 5 and
~10 % dropped for closed-market entries: ~40 / year IS, ~60 / year VAL. k = 0: ~100 HOLD trades (1.73 years at the VAL
rate) -> LIVE needs a net Sharpe per trade >= 3 / sqrt(100) = 0.30; k = 1 (|x| >= 1, ~40 % of speeches with weights):
~40 HOLD trades -> 0.47. A 1-day EURUSD trade has sd ~50 bp, so LIVE needs >= 15 bp net per speech (k = 0); the NY-close
exit (sd ~25-30 bp) needs ~8 bp. The literature size for speech tone is a few bp in 2-year yields over the day, i.e.
well under 5 bp in FX: **LIVE is out of reach for every Fed cell unless the effect is several times the literature**.
DEMO (IS t >= 2) with ~240 IS trades (k = 0) needs Sharpe 0.13: ~6.5 bp on 1-day EURUSD, ~3.5 bp at the NY close.
ECB: ~100 English speeches a year, ~85 trading days -> HOLD ~145 -> LIVE needs Sharpe 0.25 (~10 bp on a 08:00-16:30
EURUSD trade). F3: ~230 trade days a year -> HOLD ~400 -> LIVE Sharpe 0.15 (~7 bp a day on EURUSD), DEMO on IS
(~1,380 days) Sharpe 0.054 (~2.7 bp a day). F3 is the only family where LIVE is arithmetically reachable at a
plausible size.
