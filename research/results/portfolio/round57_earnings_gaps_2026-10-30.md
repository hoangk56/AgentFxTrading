# Round 57: large earnings gaps on US large-cap CFDs entered after the opening auction (follow vs fade), 2026-10-30

Brief: [round57_earnings_gaps/BRIEF.md](round57_earnings_gaps/BRIEF.md). Continues the user-approved single-stock CFD
direction. Research only. Same LIVE / DEMO bars as rounds 25-56. HOLD stayed closed: no 2025 / 2026 file requested,
every series cut at ts < 2025 at parse. HYPOTHESES_G.md (12:16 UTC) and addenda A1 (counts) / A2 (sample rule) were
fixed before any graded run; a code-debug run on 59 events at 12:22 is disclosed in A2 and not quoted.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. The Dukascopy datafeed throttled (0.1-2 files/s, many 503s, after ~19k
files pulled earlier the same day), so by the A2 rule the pull stopped at 13:20 UTC and the declared grid was graded
once on the complete random dates: 1,125 of 2,920 gaps >= 2 % (374 of 1,010 dates). The primary (follow every gap from
09:45 to 15:55, US500-hedged) is -3.2 bp IS (t -0.32) / -5.7 VAL (t -0.56); fading is -35 / -38. The 09:45-15:55
leg is +16 / +21 bp at mid, but random firms show the same leg signed by their own gaps (+14 / +24): there is no
earnings-specific continuation at 2-8 %. Only gaps > 8 % look different (follow down: +80.2 IS t 2.10 / +25.9 VAL t
0.64), but 60 % of that VAL sum is one trade, the 4-8 % down bucket reverses sign in VAL, the best IS mid t (3.31)
is near the 48-cell chance p95 (2.87), and ~60 HOLD trades put LIVE out of reach.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| G | 8-K 2.02 releases outside 09:30-16:00 with \|gap\| >= 2 % (first quote vs prior close), follow / fade from 09:45 or 10:00 ET, exit 15:55 or close of D+1 / D+2 / D+4, by gap bucket and sign, extends / retraces of 09:30-09:45, hedged / unhedged; 48 counted cells + reported variants; A2 subsample (38 % of dates) | **none**: primary -3.2 (t -0.32) / -5.7 (t -0.56); fade all 0/8 years; > 8 % down follow VAL rests on one trade (60 %); random-firm control printed nan (code keying), verdict unchanged | [STREAM_G.md](round57_earnings_gaps/STREAM_G.md), [HYPOTHESES_G.md](round57_earnings_gaps/HYPOTHESES_G.md), [G_out/grade.log](round57_earnings_gaps/G_out/grade.log) |

Correlation with C3: nothing survived; for information +0.027.

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Large earnings gaps of US large caps entered after the opening auction (09:45 / 10:00), follow or fade, same day to
  4 days: no earnings-specific continuation at 2-8 %; > 8 % too rare for HOLD power.

## Pitfalls
- The Dukascopy datafeed throttles for long stretches after heavy same-day pulls; more workers only raise the 503
  share. Order long pulls by random date so a cut sample stays unbiased, and fix the stop rule before grading.
- Compare an intraday leg with random firms signed the same way: the 09:45-close "continuation" is a market-wide
  morning-sign property, not an earnings effect.
- Gap firms' 09:45 spread is ~40 % wider than random firms' (14.5 vs 10.4 bp).

## Directions that need the user
Unchanged from rounds 54-56 (IC MT5 demo login for real open spreads: low; a no-commission venue: DEMO < 1-2 %;
small caps: LIVE ~1 %).

## State after round 57
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Four stock rounds (54-57) on
IC-listable large caps found no rule that clears IC's per-share commission plus spread: the single-stock CFD route is
exhausted for free data and fixed constraints. No free direction without a user decision has an expected LIVE >= 1 %.
