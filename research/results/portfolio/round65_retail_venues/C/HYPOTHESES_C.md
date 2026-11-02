# HYPOTHESES_C: HK CBBC mandatory-call clusters -> HK50

Written 2026-11-01 11:36 UTC (from `date -u`). No return was computed before or after this file: the stream stopped
at the data gate (step 1 of the brief), see STREAM_C.md.

## Mechanism
Issuers sell HSI bull / bear CBBCs to HK retail and hedge them in HSI futures. A mandatory call event (MCE) is
rule-based: the index trades at or through the call level, the CBBC stops trading, and the issuer unwinds the hedge
within minutes (bull call: sell futures; bear call: buy futures). A dense band of out-in-market notional just beyond
the price is a predictable burst of hedge flow in the direction of the break.

## Side (fixed before data)
Continuation: trade with the break direction (price falls into a bull band: short HK50; rises into a bear band: long).

## Declared plan (not run; data gate failed)
- Density D(level band) = sum over live HSI CBBCs with call level in the band of out-in-market units x entitlement
  (index-point notional), from the issuer daily trading summaries filed on day D-1 (known before the day).
- Event: first HK50 M1 close through the near edge of a band of width 100 HSI points whose D is in the top
  {20 %, 10 %} of the IS distribution of bands within 1 % of the price.
- Entry: open of the next M1 bar; hold {15, 30} min; one more declared cell: fade after 30 min for 30 min.
- Grid: 2 thresholds x 3 holds x {bull bands, bear bands} = 12 cells; report the max-over-cells null.
- Costs: IC HK50 spread by hour (round 28-29 models: minute fill at the next bar, spread x1.0 and x1.5, +1 min late).
- t clustered by day; IS 2016-2021, VAL 2022-2024; random benchmark: breaks of the same size through 100-point
  bands with low D (and through round-number levels, to separate J1 from round 28).

## Power arithmetic
J1 estimate: ~100-200 qualifying band breaks a year. A plausible net Sharpe per trade of 0.08-0.16 at ~270 HOLD
trades gives HOLD power 0.08-0.16 x sqrt(270) = 1.3-2.6, below the LIVE bar of 3 even before data limits.
LIVE would need net Sharpe per trade >= 3 / sqrt(270) = 0.18.
