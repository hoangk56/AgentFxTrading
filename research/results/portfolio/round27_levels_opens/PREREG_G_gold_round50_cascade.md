# PREREG (round 28 lead): one HOLD look for round 27's gold $50-level rule G1-XAU50. Tier DEMO

Registered 2026-10-18 00:26 UTC (`date -u`), before any 2025-26 gold price was loaded for this rule. The rule is
exactly the one in [PREREG_DRAFT_G_gold_round50_cascade.md](PREREG_DRAFT_G_gold_round50_cascade.md) (cell G1-XAU50:
offset c = 0.5, 30-minute exit, no protective stop). Nothing in it is changed or chosen here except the release
calendar from 2024 on, because the ForexFactory file the draft used ends on 2024-12-31 (below). Round 28 ran the same
rule on 21 other symbols and found the effect only in gold
([round28_round_levels_2026-10-17.md](../round28_round_levels_2026-10-17.md)); this is the one HOLD look for the gold
rule.

## Why DEMO and not LIVE
- IS / VAL meet every DEMO number: IS t 2.66 >= 2.0, VAL net > 0, random control 0.96 / 0.995 >= 0.90.
- They meet every LIVE number except power: 1.45 at the VAL size (1.64 under the registered calendar), against the 3
  that LIVE needs. The 30-minute hold was also picked after looking.
- So HOLD can reject the rule or keep it at DEMO. It cannot make it LIVE.

## What is looked at
- **HOLD**: NY sessions 2025-01-02 .. 2026-09-24; only trades triggered at or after 2025-01-01 00:00 UTC count.
- **Data**: IC XAUUSD ticks, `research/data/XAUUSD/t1/` 2024-12-26 .. 2026-09-24.
  - 2024-12-26..31 only warm up the 1,440-minute windows; no 2024 trade is reported.
  - The file count was checked before registration (file names only, no prices): one file per calendar day, none
    missing.
- **Calendar (the registered rule)**: High-impact USD minutes are
  - the ForexFactory rows for times before 2024-01-01, read exactly as in round 27;
  - the official-schedule list [usd_high_2024_2026.csv](prereg_code/usd_high_2024_2026.csv) from 2024-01-01 on.
- **How the official list was built**:
  - Sources are the publishers' own schedules and releases: BLS, BEA, Census, DOL, ADP, ISM, Conference Board,
    UMich, S&P Global, NY Fed, the Fed (FOMC and Chair) and Treasury (10- and 30-year auctions, FX report).
  - Dates are the actual release dates, after the 2025 shutdown delays and cancellations.
  - The event types were fixed before any trade was looked at.
  - Details are in [hold_prep_README.txt](prereg_code/hold_prep_README.txt).
- **Check against ForexFactory, 2024** ([calendar_check_2024.txt](prereg_code/calendar_check_2024.txt)):
  - 218 of FF's 238 minutes match within +-1 minute.
  - 8 of FF's other minutes are FF mistimings, e.g. ECI at 09:45 instead of 08:30.
  - The arming minutes differ on 0.49 % of 2024.
- **Effect on VAL** ([cal_swap_2024.txt](prereg_code/cal_swap_2024.txt)): under the registered calendar VAL is n 187,
  net +3.62 (t 2.05), against round 27's n 185, +3.27 (t 1.81). IS is unchanged.
  - One trade drops out: -51 bp, armed 9 minutes before a UMich release that FF had not rated High.
  - Three trades come in that FF's mistimings had blocked.
  - The conservative reference stays round 27's +3.27.
- **Reproduction before HOLD** ([repro_check_output.txt](prereg_code/repro_check_output.txt)): the code below, run with
  round 27's calendar, gives all 271 IS and 185 VAL trades identical to round 27 in every field. IS is +5.99 bp
  (t 2.66), VAL +3.27 (t 1.81).

## Bar (fixed now)
- **Reject if the HOLD mean net per trade at 250 ms latency is <= 0.** Otherwise the rule stays a DEMO candidate.
  - Fills: the ASK (buy) or BID (sell) of the first tick at or after trigger + 250 ms.
  - Exit: at market, 30 minutes after the trigger.
  - Costs: 0.6 bp round-trip commission.
- This bar removes only clear failures: a rule with no edge passes it about half the time.
- Reported, not gating: t clustered by UTC day, mid, net at 0 ms / next tick / 1000 ms, spread x1.5, both fills
  +1 minute, per-trade Sharpe, by year.
- Expected: about 108 trades (62 a year x 1.73 years).
- Expected HOLD t, under round 27's calendar / the registered one:

  | effect size | expected HOLD t |
  |---|---|
  | the VAL effect | 1.45 / 1.64 |
  | 0.65 of it (retention of declared rules) | 0.94 / 1.07 |
  | 0.25 of it (retention of post-hoc picks; the hold was one) | 0.36 / 0.41 |

## DEMO terms if it passes
Deploying it is the user's decision; no cBot is written here.
- About 60 trades a year.
- **Stop rule** (any one):
  - after 60 demo trades, the cumulative demo net is < 0;
  - after 120 demo trades, it is below the expected sum minus 1.5 sd, using VAL's per-trade mean and sd;
  - at any time after 30 trades, the median entry slippage against the 250 ms tick model is worse than 1 x s60.
- **Promotion to LIVE** (all of):
  - HOLD + demo pooled, day-clustered net t >= 2.5;
  - at least 100 demo trades;
  - pooled net > 0 at spread x1.5.

  At the VAL Sharpe (0.14-0.16) this needs about 320 trades, i.e. 4-5 years.

## Code and data (sha256; not edited before the HOLD run)
Copies are in [prereg_code/](prereg_code/). The run uses the identical scratchpad files, checked with `shasum -c` and
`cmp` before the run (round 24 lesson: the `.txt` copies cannot be imported).

| file | sha256 |
|---|---|
| `prereg_code/gcommon.py.txt` | `9cf1b896c062a5355e9fec28b41f3e68e227fe3c83a26a35bc7b4960a84039cc` |
| `prereg_code/engine.py.txt` (= round 27) | `92bc5847da24cbc864b1e2b5087bb0fcdb4e2aa887f169979851810d5b8fed15` |
| `prereg_code/fills.py.txt` (= round 27) | `cf637406c7c4a4442bf871ae03cb2499ea194ccff5976689bb1ab33171844f74` |
| `prereg_code/build_minutes_hold.py.txt` | `a7e82ce37c3bbe4780d23e0f1037beec9cfe74bf966306471072897fd9eab6bf` |
| `prereg_code/run_hold.py.txt` | `54952ea6016e874de81c1cc6889904513ced98453cf666299ad89647f644024f` |
| `prereg_code/usd_high_2024_2026.csv` | `30a931520991bb797f4222a20e504496e233bba2e5e978550d1d59012d57e823` |
| `r25/shared/cal/ff_events_utc.csv` (session scratchpad, 12 MB, not copied; only its rows before 2024 are read) | `7308d2ebf60c4d8f97332b832197f95292eeb6bc22efe12a1f1290f27d4f0bde` |

The calendar build is kept for provenance: `prereg_code/build_calendar.py.txt` (sha256 `3403164891ede801...`) and
`prereg_code/usd_high_2024_2026_detail.csv`, which gives the ET date, time and a note for every row.

Run from the repo root (`H` = the session scratchpad folder `r28/lead/hold`; HOLD_RUN=1 only here):

```
(cd $H && shasum -a 256 -c SHA256SUMS.txt)
HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $H/build_minutes_hold.py XAUUSD 2024-12-26 2026-09-24
HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $H/run_hold.py --minutes out/min_XAUUSD_20241226_20260924.npz \
    --sessions 2025-01-02 2026-09-24 --keep-from 2025-01-01 --cal reg --name HOLD
```

The decision number is the line `[HOLD] net 250 ms` in `out/summary_HOLD.txt`.

## HOLD result
(appended after the run, below this line; nothing above edited)

Run 2026-10-18 00:26:11-00:26:17 UTC with the hashed code. `shasum -c` and `cmp` against prereg_code/ passed before
the run. Output: [prereg_code/hold_output.txt](prereg_code/hold_output.txt); trades:
[prereg_code/trades_HOLD.csv](prereg_code/trades_HOLD.csv). One run; nothing was rerun.

| reading | HOLD 2025-01..2026-09 | VAL (registered calendar) |
|---|---|---|
| trades (per year) | 228 (132) | 187 (62) |
| mid, bp (t) | +3.80 (1.89) | +4.65 (2.62) |
| **net 250 ms, bp (t)** | **+2.87 (1.43)** | +3.62 (2.05) |
| net 0 ms / next tick / 1000 ms | +2.84 / +2.86 / +2.88 | +3.74 / +3.61 / +3.63 |
| net at spread x1.5 | +2.71 (1.35) | +3.41 (1.93) |
| net, both fills +1 minute | +1.81 (0.90) | +3.25 (1.97) |
| per-trade net Sharpe; median | 0.093; -0.44 | 0.158; -0.66 |
| by year | 2025 +0.80 (n 126), 2026 +5.43 (n 102) | 2022 +2.28, 2023 +5.24, 2024 +3.90 |

**Verdict: passes the registered bar (net > 0). The rule stays a DEMO candidate; it is not LIVE.**
- HOLD keeps 0.88 of round 27's VAL net (0.79 of the registered-calendar VAL). That is above the 0.65 retention of
  declared rules.
- The per-trade Sharpe falls to 0.093, so power at the HOLD rate is 1.40 (0.093 x sqrt(1.73 x 132)), against the 3
  that LIVE needs.

Information only ([prereg_code/hold_describe_output.txt](prereg_code/hold_describe_output.txt); no new rule is taken
from it):
- **Twice the expected trades** (228 against about 108): gold's price doubled. The traded $50 levels ran from
  2,650 to 5,500, against a mean of 2,101 in VAL and 1,537 in IS. Fixed dollar levels then sit closer together in
  percent, and more of them break fresh.
- **Right tail**: the top 5 trades make 518 of the 655 bp. Without them the mean is +0.61. Clipped at the IS 1 / 99 %
  quantiles: +3.18 (t 1.64).
- **Downward breaks** +5.81 (t 1.42, n 91), upward +0.92 (n 137): the same asymmetry as IS.
- **Dose**: the $100 levels inside the rule make +5.73 (t 2.11, n 108).
- **By half-year**: 2025 H1 -1.87, H2 +3.23; 2026 H1 +7.02, H2 (to Sep 24) +1.94.
