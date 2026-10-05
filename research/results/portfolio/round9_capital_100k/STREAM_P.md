# Stream P: a $100,000 prop-firm account on cTrader

Read BRIEF.md first. Question: can the user's proven edge (C3 gotobi, possibly with other components) pass a $100k
prop-firm evaluation and earn payouts, at what risk settings, at which firm, and with what expected value per fee
paid? The objective here is NOT long-run return: it is P(pass) x payouts minus fees, under hard loss limits.

## P-A. Rules survey (web, dated 2026-10; rules change often, cite each page)
For prop firms that offer cTrader (e.g. FTMO, FundedNext, FXIFY, The5ers, Blue Guardian, Alpha Capital, Funding
Pips, Goat/others; verify cTrader support), $100k account, every plan type (2-step, 1-step, instant):
fee; profit targets per phase; max daily loss (balance- or equity-based? includes floating? reset time and time
zone); max loss (static / trailing / balance-based); minimum trading days; time limit; leverage on FX; commission
per lot and typical spreads (raw?); swaps; EAs/cBots allowed; news-trading and weekend-holding rules; restrictions
that could hit C3 (holding across the daily reset, trading at a fixed time each day, "consistency" rules, max lot or
max risk per trade rules, bans on strategies such as "gap trading", "tick scalping", "one-sided bets", copy trading
between own accounts); profit split, payout frequency, scaling plan, refund of the fee. Also: is the funded account
simulated, and is there public evidence of payout denials / firm closures (2023-2026: MyForexFunds, True Forex
Funds, etc.)? Table it.

## P-B. Model C3 under each rule set
- Input: research/results/portfolio/gotobi_cbot_trades.csv (2016-01..2026-09, $50 risk per leg, IC ticks), JP
  holiday gotobi days dropped (the live bot skips them). R per leg = net / 50 (commission included at IC's $3/lot/
  side: re-price it at the firm's commission). Note the CSV has closed trades only: for the equity-based daily loss,
  rebuild each leg's intrabar worst point from research/data/m1 (2016-2024; bid c/h/l and ask ca; cut ts <
  1735689600000) or, if you don't, assume a leg can be at -1 R at its worst and say so. Map each leg to the firm's
  trading day (e.g. FTMO resets at midnight CE(S)T = 22:00/23:00 UTC; C3's long leg 18:00 -> 00:55 UTC crosses it).
- Simulate the evaluation as a stream of gotobi days drawn by block bootstrap (blocks of ~10 gotobi days; also the
  historical sequence from every start date) at risk per leg r in {0.25, 0.5, 0.75, 1, 1.5, 2, 3} % (and phase-
  dependent schedules, e.g. higher in phase 1, lower when near the loss limit, stop when the target is hit).
  Outputs per firm and plan: P(pass phase 1), P(pass all phases), median and 90th percentile days to pass, P(breach)
  by cause (daily vs max loss), then the funded stage: expected payouts over 12 months (split, payout schedule,
  breach ends the account), and EV = E[payouts + refund] - fee. Also with the edge halved.
- Baseline with NO edge: the same trades with R demeaned (mean 0, same distribution). The gap between C3 and the
  no-edge baseline is what the edge is worth; the no-edge EV shows how much comes from the challenge's option-like
  payoff alone (be explicit that a no-edge EV > 0 relies on the firm paying, which is the firm's credit risk).
- Is C3 alone too slow (about 6 gotobi days a month)? If a time limit or inactivity rule binds, say what would be
  needed; do not invent an edge to fill it.

## P-C. Practicalities
GotobiBot sizes in fixed $ (RiskPerTradeMoney) and has SkipDates; would it run unchanged on the firm's cTrader
(symbol names, broker server time, commission, min-lot), and what must change (risk as % of balance, a daily-loss
guard that stops trading before the firm's limit). Don't edit the cBot; list the changes.

## What to return
Per BRIEF.md. In the answer paragraph say: which firm/plan and risk setting maximise EV per fee for C3, P(pass) and
expected payout per year with C3 vs with no edge, the main risks (rule violations, firm credit risk, edge halving),
and whether you would recommend it.
