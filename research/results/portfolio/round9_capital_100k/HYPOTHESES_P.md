# Stream P hypotheses and model assumptions (written before any stream-P number was computed)

2026-10-05. Question: can C3 (gotobi Tokyo-fix basket, cBot/GotobiBot.cs) pass a $100k prop-firm evaluation on
cTrader and earn payouts, and what is EV = E[payouts + refund] - fee per firm/plan and risk setting, vs a no-edge
baseline. This stream does NOT look for a new edge; it re-weights C3's existing trade list under prop rules.

## Data use (declared)
- C3 trade list: research/results/portfolio/gotobi_cbot_trades.csv (cTrader backtest on IC ticks, $50/leg). Used in
  full 2016-01..2026-09 for closed-trade checks: allowed by BRIEF.md because C3 already passed its holdout and the
  use here is sizing / rule modelling, not edge discovery. JP holiday gotobi days dropped (tools/gotobi_holidays
  `no_fix_days`), as the live bot skips them.
- Intraday paths (for equity-based daily / max loss): IC M1 (bid o/h/l/c, ask close, spread stats) for USDJPY,
  EURJPY, GBPJPY cut at ts < 1735689600000 on load. So the path-exact event sample is 2016-01..2024-12. The MAIN
  simulation uses that sample (gotobi events 2016-2024); 2025-26 events (closed-trade only) enter a check run with
  their intraday path quantities imputed from 2016-24 legs (nearest final R, same symbol and leg) and are labelled.

## Model assumptions (M)
- M1 Unit. A "leg" = one pair, one direction. An "event" = one gotobi day: 3 long legs (open ~18:00 UTC D-1, close
  00:55 UTC D, stop 3 x ATR20(H1)) + 3 short legs (00:55 -> 02:55 UTC D). Risk r per leg = r % of the initial
  $100k (fixed $, as GotobiBot's RiskPerTradeMoney), unless a schedule says otherwise.
- M2 R unit. At $100k lots are >= ~1, so lot rounding vanishes; R_true = $ P/L / (lots x stop distance value), with
  the stop distance rebuilt as 3 x ATR20 of H1 bars from M1 (last H1 bar closed before entry). The CSV's net/50
  convention under-scales |R| by the lot rounding at $50; I report both means and use R_true where the path is known.
- M3 Costs. Gross P/L from the CSV (IC raw-spread fills). Commission re-priced at each firm's $/lot round turn.
  Swaps: MAIN excludes swaps (the cTrader backtest applied 2026 IC swaps to all years and firm swaps are unknown,
  often marked up); sensitivity adds IC swaps back. Spread sensitivity: +0.3 pip per side extra on every fill
  (prop-firm feeds are often wider than IC raw) -> costed in R via the leg's stop distance.
- M4 Intraday path. Per minute, each leg's worst point = bid low (long) / bid high + mean spread (short); the
  basket worst in a minute = sum of the legs' minute-worsts (conservative: assumes they coincide). Floating P/L
  includes the round-turn commission from the open. Closed legs keep their realised R.
- M5 Firm day. Each firm's daily reset in UTC (with its DST rule) splits an event: segment A = long legs from entry
  to the reset (firm-day D-1), segment B = reset -> 02:55 UTC (firm-day D: rest of the long legs + the short legs).
  Daily-loss reference: either the balance at the reset (floating excluded) or max(balance, equity) at the reset,
  per firm; the loss limit is a % of initial balance unless the firm says otherwise. Breach if equity falls below
  reference - limit at any minute (using the minute-worst). Max loss: static (equity >= B0 x (1 - M)) or trailing
  per firm. One event per firm day is assumed; overlaps are checked in the data.
- M6 Evaluation. Events in sequence; the target is checked on balance after each event closes (all flat 02:55
  UTC); min trading days counted as days with an opened trade (each event opens on 2 firm days). Time limits are
  applied with ~5.7 events per month (68 events / year, the 2016-24 average). Phase 2 restarts at $100k.
- M7 Sampling. Block bootstrap of events (blocks of 10 consecutive events, 20,000 paths) and, separately, every
  historical start event run forward (overlapping, so no independence claimed).
- M8 Funded stage. 12 months = 68 events. Payout on the firm's cadence (first after N days, then every K days),
  amount = split x (balance - B0) when above the firm's minimum; balance resets to B0 after a payout; a breach ends
  the account (no re-purchase in the base EV). Fee refunded with the first payout where the firm does so.
  EV = E[sum of payouts + refund] - fee. Firm credit risk and payout denial are NOT in EV; reported separately.
- M9 Edge variants. k = 1 (as measured), 0.5 (edge halved), 0 (no edge: every leg's R demeaned by its
  symbol x leg mean over the sample, the drift removed linearly over the leg's life so the path keeps its shape).
- M10 Risk grid. r in {0.25, 0.5, 0.75, 1, 1.5, 2, 3} % per leg, plus schedules: (S1) phase-1 higher, phase-2
  lower; (S2) daily-loss guard: skip the short legs of day D if the day is already down >= g; (S3) stop trading
  when the target is hit (always on in evaluation). Cells tried are counted.

## Hypotheses (H)
- HP1 (mechanism: C3's +~0.05 R/leg is a real flow premium; prop challenges are a short barrier option on the
  account). Under a 2-step 10%/5% target, 5% daily, 10% static max loss, C3 at the EV-best r has a higher P(pass
  all phases) than its no-edge baseline at the same r. Success = P(pass | C3) - P(pass | no edge) >= 10 percentage
  points at the EV-best r, and EV(C3) > EV(no edge).
- HP2 (constraint: daily loss is per firm day and the long leg crosses the reset). The binding constraint for r is
  the daily loss (6 correlated legs on firm-day D), not the max loss; above r ~0.8 % per leg the daily-loss breach
  share rises steeply. Success = breach-by-daily share > 50 % of breaches at r >= 1.5 %.
- HP3 (C3 is slow: ~5.7 events/month, ~+0.05 R/leg -> ~0.3 R per event net, ~1.7 R/month at 1 R = r). With a
  30-day phase-1 limit and a 10 % target, C3 cannot pass on edge at r <= 1 %; any pass there is variance. Success =
  median days-to-pass > 30 calendar days at r = 1 % for a 10 % target.
- HP4 (option value). The no-edge baseline has EV > 0 at some (firm, r) because the trader's loss is capped at the
  fee while payouts are a split of a large notional; this is pure convexity and is the firm's credit/denial risk.
  Reported, not counted as edge.
- HP5 (edge halved). With k = 0.5 the EV-best plan keeps EV(C3) > EV(no edge) but the gap shrinks roughly in
  proportion; success = sign preserved.

## Added during the run (each before its own numbers; flagged because the first guard results came first)
- M11 (added after the first FTMO/The5ers guard runs showed residual daily breaches on The5ers' max(balance,
  equity) basis and on the Brexit 2016-06-24 gap): guard slack 1.25 R per stopped leg (the in-sample worst 3-leg
  basket is -3.67 R), plus an equity kill switch 0.5 % of B0 before the daily / max-loss limit that closes all
  legs (fills assumed at the switch). Policies compared: none / guard / guard+kill / kill without the daily r cap.
- M12 (no-skill baseline): besides k=0 on the net mean (the brief's baseline), k=0 on the GROSS mean, so net
  = -costs, as a trader with no skill pays them. Expected: EV(no-skill) <= 0 at most plans.
- M13 Plans added after the survey: E8 One, E8 Pro, Goat Instant GOAT (only cTrader + cBot-on-VPS candidates
  besides FTMO / The5ers). Excluded with reasons: FundedNext (no $100k on cTrader, no bots on cTrader), FXIFY
  (no cTrader), Blue Guardian (no cTrader), Alpha Capital (cBots banned on cTrader), Funding Pips (VPS/VPN
  banned; funded 2-step force-closes overnight), Maven (EAs banned), Goat 1/2-step (VPS banned since 12 Aug 2026).
- Cells: grid 1,568 (7 plans x 4 edge variants x 4 policies x 7 r x {bootstrap, historical}); sensitivity 110;
  ~300 exploratory cells while building the engine. No edge is searched: the EV-best policy per plan is chosen
  in-sample on the same bootstrap (mild optimism; the top policies are within ~3 % EV of each other).
