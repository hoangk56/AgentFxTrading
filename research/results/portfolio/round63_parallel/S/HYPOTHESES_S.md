# Round 63 stream S: hypotheses (overnight vs intraday returns of US large caps, auction execution)

Written 2026-10-31 14:32 UTC (from `date -u`), before any return was computed. Only schemas, row counts, ticker
lists and min / max dates of the downloaded files have been looked at so far.

## Venue and why this is new
Interactive Brokers (or any broker with auction access): market-on-close (MOC) and market-on-open (MOO) orders fill
at the primary listing's official closing / opening auction price. No spread is crossed; the cost is commission
(~USD 0.0035 / share, ~0.5 bp at a ~USD 70+ price) plus auction impact / tracking of the print. Rounds 54-57 failed on
IC's USD 0.02 / share commission (~12 bp round trip) and on Dukascopy's daily "open" being the session's first quote
(median 65 bp spread). Overnight / intraday decompositions were never tested in rounds 1-62 (round 56 tested close-to-
close reversal; round 57 the 09:45-close leg after earnings gaps only).

## Data (decided before any return)
- **stooq.com is not usable**: `https://stooq.com/robots.txt` is `User-agent: * / Disallow: /` (only Bingbot and
  Googlebot allowed). Not downloaded. research/data/stooq/ is still used as this stream's data folder (requests.log).
- **Prices**: Hugging Face `jwigginton/timeseries-daily-sp500` (huggingface.co robots: `Allow: /`; public, ungated),
  Yahoo-style daily open / high / low / close (split-adjusted), adj_close (split + dividend adjusted), volume for the
  503 S&P 500 members as of 2024-03-11, 1980-01-02..2024-03-11. No 2025-26 rows exist in the file.
- **Membership dates**: `jwigginton/index-constituents-sp500` (date_added for the same 503 names).
- **Survivorship**: the names are the 2024 survivors (no delisted / removed firms). Mitigation: a name enters the
  universe only from its S&P 500 `date_added` (no pre-inclusion run-up). The sample is still survivor-biased; the bias
  is mostly in the long-only level (B1), less in a dollar-neutral overnight / intraday spread, and is largest in PRE.
- **Opens**: Yahoo's open is the consolidated-tape open, which for large caps is normally the primary opening print
  but is not guaranteed to equal the official auction price; open-price noise shifts return between the overnight
  and intraday legs of the same day. Every rule below uses signals that do not share a price with the traded leg.
- **Dividends**: dividend on ex-date t from the adj-factor f = adj_close / close: d_t = 1 - f_{t-1} / f_t. The
  overnight leg gets the dividend (total return O_t / C_{t-1} - 1 + d_t); a short pays it.
- **ETFs**: SPY / QQQ / IWM are not in the file. The aggregate overnight drift is measured on the equal-weight
  universe basket (tradeable as auction orders in each name, or as SPY MOC / MOO at the same cost). Diagnostic only:
  IC US500 M1 mid at 16:00 vs 09:31 New York.
- Cleaning: drop name-days with open / close <= 0, open outside [low, high] by > 0.5 %, volume 0, |overnight| > 40 %
  (split / data errors), price < USD 5.

## Universe
Each day t: names in the S&P 500 (date_added <= t) with valid data on t and the previous 252 sessions as needed by
the signal, ranked by 63-day median dollar volume (close x volume, through t-1); the top 200. Decile = top / bottom
20 names, equal weight.

## Eras
PRE 2004-01-01..2015-12-31 (extra robustness era, declared; heavier survivorship), IS 2016-01-01..2021-12-31,
VAL 2022-01-01..2024-03-11 (the source ends 2024-03-11, so VAL is 2.2 years instead of 3). HOLD 2025-01..2026-10
stays closed (not in the file, nothing requested).

## Hypotheses (sides fixed here)
Literature: Lou, Polk & Skouras (2019 JFE): momentum profits accrue overnight, the intraday leg reverses; past
overnight returns predict future overnight returns (clientele persistence); "tug of war" between overnight and
intraday clienteles. Cliff, Cooper & Gulen (2008), Kelly & Clark (2011): US equity premium earned overnight. Berkman,
Koch, Tuttle & Zhang (2012): attention-driven overnight buying at the open reverses intraday.

Mechanism: retail / individual investors trade at the open (buy pressure, attention), institutions trade into the
close; overnight returns carry a risk / inventory premium for holding through the closed market.

| cell | rule | hold | side |
|---|---|---|---|
| B1 | long the EW universe basket (SPY proxy) | close t -> open t+1 | long; graded on excess over Fed funds x nights / 360 |
| X1a/b/c | signal = mean overnight log return over the past N = 21 / 63 / 252 sessions (through open t) | close t -> open t+1 | long top decile, short bottom decile |
| X2 | 12-1 momentum: total return close t-252 -> close t-21 | close t -> open t+1 | long winners, short losers |
| X3 | same 12-1 momentum | open t -> close t (signal through close t-1) | short winners, long losers (intraday reversal of momentum) |
| X4a/b | previous overnight return: r_on(t-1) (close t-2 -> open t-1), and mean r_on over the 21 sessions ending t-1 | open t -> close t | short high, long low |

7 dollar-neutral cells + B1 = 8 cells. No parameter is picked after looking: the best IS cell of each family is
reported with the max-over-cells null.

Diagnostics (not graded): the intraday (open -> close) leg of the basket; LPS-style decomposition of X2 into
overnight and intraday; by-year tables.

## Costs (per name, per side, per auction)
2 bp auction impact / tracking + 0.5 bp commission = 2.5 bp per side, 5 bp per round trip of USD 1. A dollar-neutral
book (USD 1 long + USD 1 short, return = r_long - r_short) costs 10 bp per day (full turnover every day is inherent
in an overnight-only or intraday-only book). Shorts pay borrow 0.5 %/yr / 360 per night held. Stress x1.5 (15 bp) and
x2 (20 bp). B1 costs 5 bp per day and is graded net of cash: excess = r_on - cost - DFF x calendar nights / 360.

## Statistics and bars
Daily book returns; t = Newey-West (lag 5). Bars from BRIEF: LIVE t >= 2.5 IS, >= 1.5 VAL, >= 2/3 of years positive,
beats >= 95 % of random books, HOLD power at VAL size >= 3; DEMO t >= 2.0 IS, net > 0 VAL, beats >= 90 % random;
net > 0 at costs x1.5 and one step late (signal lagged one more session) in IS and VAL.
Random benchmarks: (i) random books = 20 random long / 20 random short names from the same day's universe, same hold
and cost (1,000 draws); (ii) max-over-cells null: per-day permutation of every cell's signal across names, max IS
gross t over the 7 X cells (200 draws).

## Power arithmetic (before data)
One book trade per session. HOLD 2025-01-01..2026-10-29 ~ 1.83 y x 252 = ~460 sessions. LIVE needs net Sharpe per
session x sqrt(460) >= 3 -> per-session net Sharpe >= 0.140 -> annual net Sharpe >= 0.140 x sqrt(252) = 2.22.
- X cells: a decile long-short overnight book of large caps has a daily sd of roughly 40-60 bp, so LIVE needs a net
  mean of >= 6-8 bp per session, i.e. a gross overnight spread of >= 16-18 bp per day after the 10 bp cost. LPS's
  full-CRSP effects are a few % per month (~10-20 bp / day) and concentrated in small caps; in the top-200 I expect
  1-5 bp gross. Prior: LIVE ~1-2 %, DEMO (t >= 2 net IS) ~5 %.
- B1: basket overnight mean ~3-5 bp / night historically, sd ~70-90 bp: gross annual Sharpe ~0.6-1; net of 5 bp
  cost and the cash rate it is negative unless the drift is > ~6 bp / night. Prior: LIVE < 1 %, DEMO < 2 %.
- Reachable bars: every cell can reach LIVE only with an annual net Sharpe >= 2.2; anything weaker is DEMO at best.
