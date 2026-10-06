# Round 17: quote-based order-flow imbalance, and big-day intraday momentum in European indices (2026-10-06)

Two streams from one brief ([round17_microstructure/BRIEF.md](round17_microstructure/BRIEF.md)); hypotheses with UTC
times before their numbers (`HYPOTHESES_Y/Z.md`), write-ups `STREAM_Y/Z.md`, in
[round17_microstructure/](round17_microstructure/).

| stream | direction |
|---|---|
| Y | signed quote flow from IC ticks (price-only Cont-Kukanov-Stoikov OFI, tick rule, quote intensity) over 1-30 min as a predictor of the next 1-60 min, AUDUSD, NZDUSD, XAU, XAG, US30, USTEC, XTI; sides from the literature |
| Z | intraday momentum on top-decile move days in European index CFDs (STOXX50, F40, ES35, IT40, UK100; DE40, where round 13 saw it, information only), from midday cuts to the close; US30/USTEC as comparison |

## Answer
**No LIVE or DEMO candidate; nothing registered; HOLD not opened.** Stream Y wrote one draft (US30, top-0.1 % OFI
in the New York morning, follow 15 min: +8.11 bp t 2.11 IS / +10.07 t 5.77 VAL on 10 trades). The lead does not
register it: it is the IS-best of 60 US30 cells inside a family of ~1,600 rule cells whose chance maximum is t 3.4-3.8;
it is positive only at the 99.9th-percentile trigger (99th: -0.15 bp); dropping 2018-02-06 takes IS to t 1.67, dropping
2020 to 1.44; USTEC does not confirm it; expected HOLD t 0.6-1.0.

## Y. Order-flow imbalance
- The tick cache has bid and ask prices only (no sizes), so OFI is the price-only form; it correlates 0.91-0.997 with
  the tick rule and 0.44-0.93 with the window's own return.
- **Unconditional flow predicts reversal, not continuation**, in FX and metals (AUDUSD -0.057 bp per z, t -8.9 IS /
  -2.6 VAL): the own-return reversal. Only the part of the flow orthogonal to the return continues (the Hasbrouck sign,
  7/7 symbols in both eras), at 0.01-0.06 bp per z: about 1/20 of the cost.
- Inventory reversal at 1 minute is real (t 4-6) at ~0.05 bp gross: 1/25 of the cost. Quote-intensity and thin-hour
  rules have the wrong sign or flip in VAL. Predictability survives the first minute but is hundredths of a bp; latency
  from +1 s to +60 s barely matters.
- Chance: the screen is real (IS 248 cells with |t| >= 3 against a null 95th percentile of 23), but 214 of them are
  reversal, against the registered continuation side. Executable: 4 of 1,596 IS cells with net t >= 2 (fewer than
  chance gives).

## Z. Big-day intraday momentum in European indices
- 92 counted cells + 12 DE40 information cells. Top-decile mid +1.1 bp IS / +1.8 VAL on average per single-symbol
  cell against ~3.7 bp of cost; no European cell reaches IS net t 2.0; best IS net t +2.26 vs a shared null 95th
  percentile of 2.65 (p 0.16).
- **DE40 does not replicate** on the other European indices, nor on itself from a midday cut to the close: round 13's
  dose slope is a 15-minute effect near the close.
- US comparison: big-day continuation is March-April 2020 again (US30 IS dose t +3.3 → 0.0 without it).
- Pitfall found: a random-entry control with windows anywhere in the session contains the morning move that selected
  the day and earns +8 to +36 bp by construction for multi-hour holds; use random entries strictly after the signal
  (they earned the same as entering at the cut: no continuation left to time).

## What this says
- Signed quote flow from a CFD broker's prices adds a real but tiny predictive component (hundredths of a bp per z):
  the flow information that matters is priced in seconds, as round 8 found for cross-asset information.
- Big-day intraday momentum in Europe has the literature's sign at a third of IC's cost. With round 13 P and round 12
  L, the "flow proportional to the day's move" family holds only for gold at the COMEX settlement.

## Directions that need the user's decision
- Order-book sizes or traded volume (not in IC's tick cache) for a real OFI; low prior given the sizes above.
- A cheaper venue for European index futures (STOXX50 / F40 at ~0.5-1 bp) is the only change that would justify
  re-testing the +1-4 bp top-decile mid (same cost decision as rounds 15-16).

## Process and disclosures
- HOLD was not loaded (tick loader asserts days < 2025-01-01; bid-only caches cut at load; panel ends 2024-12-31).
- Timestamps: the round briefs of rounds 12-17 carried "written" times estimated by the lead that were 3-26 minutes
  later than the real file times; they were corrected to the file times on 2026-10-06. The order (brief before every
  hypothesis, hypothesis before its numbers) was never affected.
- Scripts and outputs in the scratchpad (`r17/Y`, `r17/Z`). Nothing in `research/` code was edited.
