# Stream X hypotheses (exact rules), written 2026-10-04 18:05 UTC, before any round-8 number

Mechanisms come from STREAM_X.md (written 17:58 UTC). This file fixes the exact event definitions, windows, sides,
cells and costs before anything is computed. New hypotheses are appended below with their own timestamp, always
before their numbers.

## Common conventions (all X families)

- Data: shared panel (2016-01..2024-12, HOLD excluded). IS 2016-2021, VAL 2022-2024. PRE 2004-2015 only for daily
  FX/metal ideas (Dukascopy H1, bid closes; costs = IC 2016-17 median spread per symbol + 0.6 bp commission).
- Local times with DST: New York (US rules), London (EU rules), Tokyo / Hong Kong (none), Sydney (AU rules).
  "Price at T" = mid close of the last M1 bar that ends at or before T, looking back at most 5 minutes; otherwise
  the day is skipped for that symbol.
- Signals use data up to the bar ending at T. Entry fills at the close of the next bar (T+1 min), latency variant
  T+2 min. Scheduled exits fill at the bar ending at the exit time.
- Cost per leg = (spr_entry/2 + spr_exit/2) / mid x 1e4 (spread of the actual entry and exit minutes)
  + 0.6 bp commission for FX and metals (0 for indices, energies, crypto) + swap for every 21:00/22:00 UTC rollover
  crossed (FX/metals: research/swing/rates.py where the rates are local (USD, EUR, JPY); for AUD, NZD, CAD, CHF,
  GBP legs, whose FRED series are not cached and may not be fetched in this stream, the conservative proxy is
  charged: the paying side's 2026 fraction from research/swing/swing.swap_frac on both sides; indices -2 bp long,
  0 short per night). Rules that enter after the rollover and exit before 20:55 UTC pay no swap.
- Statistics: mean bp per trade at mid and net; t clustered by entry UTC day (sum bp of all legs that day, t over
  days); per-trade Sharpe = net mean / net sd; power = Sharpe x sqrt(expected HOLD trades in 21 months).
- z-scores of predictors use the trailing 60 trading days of the same predictor (excluding today).
- "Continuation" = trade in the direction of the predictor; a negative mean = reversal. Each cell is one two-sided
  test (sign chosen in IS only if the hypothesis does not fix it; here every hypothesis fixes the sign below).

## X2 cross-session spillover (cash-open flow of local investors)

X2a  Predictor P = ln US500(16:00 NY) - ln US500(09:30 NY) (US cash session). Side = sign(P) (continuation; Lin,
     Engle & Ito 1994 / Hamao, Masulis & Ng 1990 report foreign daytime -> domestic overnight transmission; the
     CFD trades the "overnight" continuously, so the question is the next cash session). Targets (entry at the
     open + 1 min, exit as listed):
     a1 JP225 09:00 -> 10:00 Tokyo; a2 JP225 09:00 -> 15:00 Tokyo; a3 HK50 09:30 -> 10:30 HK; a4 HK50 09:30 ->
     16:00 HK; a5 AUS200 10:00 -> 11:00 Sydney; a6 AUS200 10:00 -> 16:00 Sydney; a7 AUDJPY 23:00 -> 06:00 UTC;
     a8 USDJPY 23:00 -> 06:00 UTC (side for USDJPY/AUDJPY = sign(P): US equities up -> yen weaker).
     Conditions: all days (slope of target on z(P), t of slope with day-clustering = plain OLS t here, one obs/day),
     |z| >= 1, |z| >= 1.5. 8 x 3 = 24 cells.
X2b  Predictor = Asian composite: mean of z-scored returns of JP225, HK50, AUS200 over 00:00 UTC -> 07:59 London,
     the composite re-z-scored on its own trailing 60 days. Side = sign (continuation). Targets: DE40, UK100,
     EURUSD (side for EURUSD = sign: risk-on -> EUR up vs USD), entry 08:00 London + 1 min, exit 09:00 London and
     11:00 London. Conditions as X2a. 3 x 2 x 3 = 18 cells.
X2c  Predictor = European morning composite: mean z of DE40 and UK100 returns 08:00 London -> 09:29 NY. Side =
     continuation. Targets US500, USTEC: (i) 09:31 -> 10:30 NY, (ii) 10:00 -> 15:55 NY, (iii) 15:30 -> 15:59 NY
     (cross-asset analogue of Gao, Han, Li & Zhou 2018 intraday momentum). Conditions as X2a. 2 x 3 x 3 = 18 cells.
X2d  US500 overnight gap G = ln US500(09:30 NY) - ln US500(16:00 NY previous trading day), |z(G)| >= 1. Foreign
     confirmation F = sign of the mean z of the cash-session returns of JP225 (09:00-15:00 Tokyo), HK50
     (09:30-16:00 HK), AUS200 (10:00-16:00 Sydney), DE40 and UK100 (08:00 London -> 09:29 NY) on that date.
     Confirmed (sign F = sign G): continuation; unconfirmed: fade (side = -sign G). Targets US500, USTEC
     09:31 -> 10:30 NY and 09:31 -> 15:55 NY. 2 subsets x 2 targets x 2 windows = 8 cells.

## X3 risk-regime conditioning (daily, closes at 20:00 UTC)

Daily return of a symbol = ln P(20:00 UTC, day d) - ln P(20:00 UTC, previous trading day).
- VR = sd(US500 daily returns, last 5 days) / sd(last 60 days).
- AR = share of variance of the first principal component of the 20-day correlation matrix of the daily returns of
  the 24 non-crypto symbols (absorption ratio, Kritzman, Li, Page & Rigobon 2011; sign-invariant, unlike an average
  pairwise correlation of arbitrarily quoted FX pairs). HIGH = AR above the 80th percentile of its trailing 250 days.
- Risk-off legs (side): AUDJPY short, AUDUSD short, NZDUSD short (carry basket); USDJPY short, USDCHF short,
  XAUUSD long (haven basket). Risk-on = the opposite sides.
- Trade window: entry 23:00 UTC of day d (+1 min), exit 20:00 UTC of day d+1 (no rollover crossed); variant
  hold to 20:00 UTC of day d+2 (one rollover, swap charged).
- Regimes: R1 VR >= 1.5 -> risk-off; R2 VR >= 2.0 -> risk-off; R3 easing (VR < 1.0 today and max VR of the prior 5
  days >= 1.5) -> risk-on; R4 AR HIGH -> risk-off; R5 AR easing (AR below its trailing median today, HIGH on some
  of the prior 5 days) -> risk-on. 5 regimes x (6 legs + 2 baskets) = 40 cells (1-day hold); the 2-day hold is a
  robustness variant of the best basket only. Also the continuous slope of each leg's next-day return on ln VR
  (6 cells).
- PRE 2004-2015 (Dukascopy H1): the same R1-R3 with AUDJPY's own realised vol as the risk proxy, same legs.

## X4 crypto -> US equities

- B = ln BTCUSD(09:29 NY) - ln BTCUSD(16:00 NY previous trading day); G = same window for US500.
- Predictors: (i) z(B); (ii) z of the residual B - beta x G (beta = OLS over the trailing 250 days). Side = sign
  (BTC as a lead of risk appetite: continuation).
- Targets: US500, USTEC 09:31 -> 10:30 NY and 09:31 -> 15:55 NY. Conditions: all days slope, |z| >= 1, |z| >= 1.5.
  2 x 2 x 2 x 3 = 24 cells. BTC data start 2018 (IS = 2018-2021).
- Weekend (IC crypto open at weekends only from 2024-04): feasibility only. Report the number of weekends and whether
  BTC's CFD reopens before US500's; no verdict from it.

## X5 dollar-gold divergence (daily, 20:00 UTC closes)

- USD factor u = mean of (-EURUSD, -GBPUSD, +USDJPY, +USDCHF, +USDCAD, -AUDUSD, -NZDUSD) daily log returns;
  g = XAUUSD daily log return; z by trailing 60 days.
- Divergence event: z_g x z_u > 0 and min(|z_g|, |z_u|) >= k, k in {0.75, 1.0}. Hypothesis: the break of the usual
  negative co-movement reverts.
- Legs: (G) XAUUSD side -sign(z_g); (U) USD basket of two legs, EURUSD and USDJPY, side = against the USD move.
  Entry 20:01 UTC (+1 min fill), holds 1, 2, 3 days (exit 20:00 UTC), swaps charged (USD/EUR/JPY rates local).
- Cells: 2 k x 2 legs x 3 holds = 12, plus the continuous slope of next-day g and u on D = z_g + z_u (2 cells).
- PRE 2004-2015 (Dukascopy H1, all 7 USD pairs and gold present).

## X6 literature-driven screens (up to ~6), to be fixed after the literature search and before their numbers

Fixed 2026-10-04 18:40 UTC, after the literature search (lit/), before any number of these.

X6a European-open window (Bondarenko & Muravyev 2022, JFQA, doi 10.1017/s0022109022000783: the E-mini's whole
     average return accrues in the 4 hours around the European open, attributed to European investors processing the
     overnight information). Rule: long US500 and USTEC 07:00 -> 11:00 London local time every weekday (entry +1 min),
     variant 06:00 -> 10:00 London. No rollover crossed. Control: the same 4 hours shifted to 12:00-16:00 London.
     Differs from round 3 (whole-night premium; single-hour drift scan). 2 symbols x 2 windows = 4 cells.
X6b Crypto-stock weekend effect (Mourey, Shahrour & Soiman 2025, Finance Research Letters, doi
     10.1016/j.frl.2025.108661: negative weekend crypto returns predict Monday stock declines; positive ones do not).
     W = ln BTC(first reopen quote after the weekend + 5 min) - ln BTC(last Friday quote before 20:55 UTC); where
     IC BTC traded through the weekend (2024-05..12), the same two times. Targets: US500, USTEC (i) Sunday reopen + 5
     min -> 09:30 NY Monday, (ii) 09:31 -> 15:55 NY Monday. Conditions: slope over all weekends; W <= -1 sd (trailing
     52 weekends), side short. 2 x 2 x 2 = 8 cells. Expected power is low (~15 events in 21 months).
X6c Oil -> equity indices, weekly (Driesprong, Jacobsen & Maat 2008, JFE, doi 10.1016/j.jfineco.2007.07.008).
     Predictor: XTIUSD return Friday 20:00 UTC -> Friday 20:00 UTC, z on trailing 52 weeks. Side = -sign. Targets:
     US500, DE40, UK100, JP225 from Monday 07:00 UTC to Friday 20:00 UTC (4.5 days, 4 rollovers: index long -2 bp
     per night, short 0). Conditions: slope, |z| >= 1. 4 x 2 = 8 cells.
X6d Commodity currencies -> commodity prices, weekly (Chen, Rogoff & Rossi 2010, QJE, doi
     10.1162/qjec.2010.125.3.1145). Predictor: mean of z-scored weekly returns of AUDUSD, NZDUSD, -USDCAD.
     Side = +sign. Targets: XAUUSD, XAGUSD, XTIUSD, XBRUSD, same weekly window as X6c (swaps: metals via
     rates.py USD, energies IC's 2026 constant). Conditions: slope, |z| >= 1. 4 x 2 = 8 cells.
X6e Absorption-ratio shift (Kritzman, Li, Page & Rigobon 2011): dAR = (15-day mean AR - 250-day mean AR) / 250-day
     sd of AR >= 1 -> risk-off next day (X3 window 23:00 -> 20:00 UTC). Targets: US500 short, the carry basket,
     the haven basket. 3 cells (added to X3's count).

Added 2026-10-04 19:05 UTC, after X2-X6 IC numbers (so these are follow-ups, flagged post hoc), before their numbers.

F1 (X6c follow-up, robustness of a pre-registered cell, not a new mechanism). The pre-registered X6c slope of next-week
     US500 on oil z was negative in both eras. Checks, all on US500 with the X6c window: slope with z clipped at
     +-2.5; per-year slope; slope without 2020; the sign trade at |z| >= 0.5; a z-sized trade (side -sign(z), lot
     = clip(|z|, 0.5, 2) x default, i.e. within the 0.5-2x rule), net per unit lot; XBRUSD as the predictor; US30
     and USTEC as targets (robustness only). Random-entry control for the best of these: same weeks' count and side
     mix, entries on random weeks, 1000 seeds. Count: this adds 5 cells to the X6c family (13 in all).
F2 (X5 follow-up). X5's continuous slope says gold's next day CONTINUES when gold and the USD rise together (D > 0),
     opposite to the fade hypothesis, IS t +1.9 and VAL t +1.2. Check in PRE 2004-2015 (Dukascopy H1 bid, 20:00 UTC
     closes, the same u from 7 USD pairs): slope of next-day gold on D and the sign trade side = sign(D) at |D| >= 1,
     hold 1 day. One era, one look.
F3 X3 in PRE 2004-2015 as written in X3 (R1-R3 with AUDJPY's own 5/60-day vol ratio as the proxy; legs carry and
     haven baskets; entry 23:00 UTC, exit 20:00 UTC next day; costs: IC 2016-17 median spread by symbol and UTC hour
     + 0.6 bp commission; no swap crossed).
