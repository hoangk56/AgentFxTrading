# Stream S: shock spillover between symbols (written 2026-10-04 17:58 UTC, before any number)

Question: when one market makes a large, fast move, do linked markets under-react (and drift after it) or over-react
(and revert)? Conditioning on big moves raises per-trade size, which is what intraday ideas lacked in rounds 3-7.

S1 large source shocks -> linked targets. Event = |source log return over the last 5 or 15 minutes| >= k x its
trailing 20-day sd at that horizon (k in {4, 6}); one event per source per 60 minutes (first crossing). Sources:
US500, USTEC, DE40, JP225, XAUUSD, XTIUSD, BTCUSD, USDJPY, EURUSD, AUDUSD. Targets: the other 25. Response of the
target from the minute after the event (+1 and +2 min entry) over 5, 15, 60, 240 minutes and to 20:00 UTC, signed by
(source direction x sign of the target's trailing 60-day beta to the source). Continuation = under-reaction / slow
diffusion across linked assets (Hou 2007; Cohen & Frazzini 2008; Hong, Torous & Valkanov 2007); reversal = liquidity
overshoot. Report both, by session.

S2 beta-gap catch-up. At the event's end, gap = target's actual move - trailing-60-day beta x source move (beta from
1-min or 5-min returns, causal). Hypothesis: the gap closes (target that under-moved catches up, over-mover reverts)
over 15-240 minutes. Trade the target in the gap-closing direction when |gap| > c x the target's horizon sd.

S3 safe-haven spillover. Equity drawdown events (US500 <= -1 % in 60 minutes, or <= -2 % since the previous 20:00 UTC)
-> USDJPY, USDCHF, XAUUSD, AUDJPY, EURUSD over the next 1-24 h (Ranaldo & Söderlind 2010; Fatum & Yamamoto 2016:
safe-haven currencies appreciate in stress). And the mirror: sharp equity rebounds. Event-clustered t.

S4 scheduled US data shocks. US releases at 08:30 New York (12:30/13:30 UTC by DST; NFP = first Friday of the month,
CPI ~ mid-month: use every weekday 08:30 NY as the event set and the subset of first Fridays). EURUSD/USDJPY reaction
in the first 1-5 minutes -> do slower-reacting assets (XAU, indices, AUDJPY, crosses, oil) continue over the next
15-120 minutes in the implied direction? (Andersen, Bollerslev, Diebold & Vega 2003/2007 on cross-market news
transmission.)

Mandatory: use the actual spread at the entry and exit minutes (spreads blow out at shocks), report events per year
(power), cluster t by event day, and a random-time control (same weekday/hour mix) for the best cells.
