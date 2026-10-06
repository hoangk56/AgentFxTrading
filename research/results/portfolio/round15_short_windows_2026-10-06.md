# Round 15: very short windows (1-10 minutes) at benchmark minutes (2026-10-06)

LIVE needs a mid edge of cost + 0.145 x sd(w) at one trade a day. sd shrinks with the window, the round-trip cost does
not, so short windows help only if a flow is concentrated in a few minutes. Rounds 4 and 13 scanned windows of 15
minutes and more. Two streams ran from one brief ([round15_short_windows/BRIEF.md](round15_short_windows/BRIEF.md));
hypotheses with UTC times before their numbers (`HYPOTHESES_S/V.md`), write-ups `STREAM_S/V.md`, in
[round15_short_windows/](round15_short_windows/).

| stream | scope |
|---|---|
| S | FX (EURUSD, USDCHF, USDJPY, EURJPY, GBPJPY outside C3's Tokyo-fix hours): 85,225 cells of 1-10 minutes within +-30 min of 8 benchmark minutes, discovery on PRE 2004-15 (side fixed there), confirmation on IS and VAL; an all-day 1-5-minute EURUSD control |
| V | gold, silver, AUD/NZD, index CFDs, XTI: 25,704 cells of 1-10 minutes within +-20 min of 24 benchmark minutes (LBMA auctions, COMEX/NYMEX opens and settlement, cash opens and closes, data minutes); IS discovery with sides from a written mechanism (8,210 predicted cells), VAL check |

## Answer

**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** Stream S wrote two post-hoc drafts and advised
against both; the lead agrees:
- EURUSD short 12:50-13:00 London on Fridays: net +1.13 (t 3.81) IS / +1.31 (t 2.74) VAL, power 2.0-2.1, PRE net
  -0.08. It is a subset of E1, whose HOLD is already open, and was chosen with VAL in view.
- GBPJPY long 10:28-10:31 New York on the last weekday: +2.48 / +0.47, decaying (VAL/IS 0.45), no mechanism, the
  neighbouring windows are ~0.

## S. FX
- Alignment checked first: Dukascopy and IC both label bars by their start minute (IC panel close = last tick in
  [L, L+1) on 100 % of minutes); 1-minute returns correlate 0.99 at lag 0 on 2016-17.
- **The ECB V moved, in the market itself:** the drop sat in 13:13-13:14 London in 2004-15 and at 12:57 London (rebound
  13:02) from 2016; Dukascopy and IC agree on 2016-17. So the strongest PRE minute cells (t up to 15.9) have the
  opposite sign after 2015, and PRE selection at minute resolution did *worse* than chance: 25 of 409 PRE-carried cells
  confirm in IS against a null 95th percentile of 30.
- Benchmark minutes are not special in PRE (5.8 % of nearby cells beyond the null vs 6.8 % elsewhere). The all-day
  control finds 58 / 361 confirmations (null 15), but they are 0.1-0.3 bp Asian-session minutes.
- Even picking the best every-weekday window in hindsight, the largest |IS mid| is 0.88 bp in EURUSD and 0.45 in
  USDJPY, under the 0.8-1.2 bp LIVE line; 0.01 % of 1-minute cells and 0.55 % of 10-minute cells are net > 0 in both
  IS and VAL.
- Fridays carry about twice the ECB V in 2016-24 (Friday minus Mon-Thu +1.18 bp IS, t 3.5; +1.36 VAL), not in PRE.

## V. Metals, AUD/NZD, indices, oil
- Real at mid, far beyond chance: 608 predicted cells with side IS t >= 2 (null 95th percentile 258), 141 of them
  confirmed in VAL (null 23). Cost kills them: mid 0.3-2.7 bp against 1-7 bp round trips. Best predicted IS net t 1.69
  (HK50 open fade, VAL negative); 3 of 8,210 predicted cells are net > 0 in both eras, all with IS net t <= 0.43 and
  failing x1.5 or +1 minute.
- Families: opening overreaction (HK50 decaying, US500 VAL only), European-open drift (gone), close pressure and
  reversal (UK100 real below cost; US30 post-close reversal 16:04-16:14 ET is larger in VAL, +0.74 net t 2.9, but
  fails IS at the 2016-21 spread, 3x today's), LBMA and COMEX/NYMEX opens (below cost), data-minute continuation (none).
- **Most stable short-window effect of rounds 12-15** (post hoc, no side declared beforehand, information only):
  silver falls into the 12:00 London LBMA auction, +2.68 bp (t 8.3) IS / +2.72 (t 9.1) VAL, 9/9 years, bid and ask
  together; gold the same at the 15:00 PM auction (+1.09 / +0.94) and, decaying, at 10:30. Part of the drop is at
  T+30-45 s, the end of the auction's first round: the pre-2015 fixing pattern of Abrantes-Metz & Metz survived the
  electronic auction. At IC's costs it nets -0.21 / +0.11 bp in gold (commission + spread = the move); silver's 4-5 bp
  spread is 1.6x its move.

## What this says
- **Short windows raise the mid Sharpe but not past the commission.** The concentrated flows exist (the ECB V, the
  LBMA auctions, closes), but per trade they are 0.5-2.7 bp, and IC's round trip at those minutes is about the same.
- **Institutional timing moves at minute scale** (the ECB V moved ~16 minutes at the end of 2015), so 2004-15 cannot
  select minute windows for 2016+.
- **IC's own cost history is now a binding part of the bar for indices:** some index effects (US30 post-close reversal)
  are net > 0 at today's spreads and fail only on the 2016-21 spreads. Whether IS should be judged at the era's cost
  or at today's is the user's bar, and it is not changed here.

## Directions that need the user's decision
1. Dukascopy XAU/XAG M1 or ticks 2004-15: a clean PRE test of the LBMA auction drop (it would still need a venue with
   gold round trips <= ~0.7 bp, silver <= ~1.5 bp).
2. IC EURUSD ticks 2016-24 for second-level latency tests of the ECB slot.
3. A commission-free EURUSD venue (the every-day ECB-slot windows, IS mid 0.5-0.9 bp, could net > 0).
4. Whether index effects may be judged at today's IC costs in IS (a bar change; not applied).
5. New data after 2026-09-24 (unchanged).

## Process and disclosures
- HOLD was not loaded (Dukascopy ends 2015, the panel 2024-12-31, tick loads asserted < 2025, C3's 2025+ rows skipped).
- Stream V's first null run peaked at 4.0 GB RAM (over the 2.5 GB limit) and was rewritten in chunks (1.1 GB, same
  numbers). Scripts and outputs stay in the scratchpad (`r15/S`, `r15/V`). Nothing in `research/` code was edited.
