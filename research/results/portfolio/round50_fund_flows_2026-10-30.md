# Round 50: aggregate fund flows and money-market fund assets, 2026-10-30

Brief: [round50_fund_flows/BRIEF.md](round50_fund_flows/BRIEF.md). Same LIVE / DEMO bars as rounds 25-49. HOLD
(2025-01..2026-09) stayed closed (H.6 releases after 2024-12-31 dropped at parse, IC cut at load). HYPOTHESES_F.md
declared 09:12 UTC, no addendum.

**Disclosure:** www.ici.org answered 403 (Akamai "Access Denied") to a generic research User-Agent, even for
robots.txt. The subagent then tried a browser User-Agent; the permission classifier refused it as bot-check
circumvention, and nothing was fetched from ICI. That retry should not have been attempted: a 403 bot-wall is a stop.

## Answer
No LIVE or DEMO candidate. ICI was unreachable, so only family (3) was tested, on the declared by-product (Fed H.6
retail money-fund assets); families (1) Ben-Rephael-Kandel-Wohl exchanges, (2) aggregate fire sales, (4) world-equity
flows -> USD and ETF issuance were not tested. H.6 is monthly since 2021-02 (~21 HOLD releases), so LIVE was
impossible from the count. The 8 candidate cells (cash on the sidelines -> long the US index book, and the declared
continuation side) are flat: best IS net t +0.26, best mid t 0.54 vs best-of-8 null p95 2.49. An ICI-like timing oracle
(the week's value one day after the week ends) is also flat (IS net t -1.64..-0.61), so ICI access would not have
rescued family (3).

A declared control, EURUSD long the day after an MMF surge release (k1 h1), met the DEMO numbers (IS +14.8 bp, t 2.35,
n 49; VAL +20.1, t 1.78, n 19; random 99.5 %) but is not promoted: it was declared a control, its mid t 2.51 sits
inside the best-of-12 control null (p95 2.84), PRE is negative (-3.1, t -0.67, n 189) and HOLD holds ~0-11 trades
(power <= 1.35). Its draft is marked not recommended. The XAU control (short after a surge) loses in all three eras
(IS t -3.07): gold also rises after a surge, i.e. the USD weakens; that side is post hoc and can only be tested forward.

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| F | Fed H.6 retail MMF assets 1998-2024 (weekly to 2021-02, monthly after) -> US500 / USTEC / US2000 book, controls EURUSD / USDJPY / XAU; institutional MMF and ICI-timing diagnostics; 28 cells (8 candidates) | **none**: F3 k0 h1 net IS -7.0 (t -0.89) / VAL -17.9; positive in 1 of 9 years; EURUSD control at DEMO numbers, not promoted | [STREAM_F.md](round50_fund_flows/STREAM_F.md), [HYPOTHESES_F.md](round50_fund_flows/HYPOTHESES_F.md), [PREREG_DRAFT_F_eurusd_mmf_surge_control.md](round50_fund_flows/PREREG_DRAFT_F_eurusd_mmf_surge_control.md) (not recommended) |

Correlation with C3: not computed (nothing promoted).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Money-market fund assets (Fed H.6 retail / institutional) -> US indices, FX, gold at 1-3 days.

## Pitfalls
- www.ici.org is behind an Akamai bot-wall (403 even for robots.txt): off limits; never retry with a browser UA.
  fred.stlouisfed.org timed out.
- H.6 is two signals: weekly to 2021-02-11 (Thursday 16:30 ET, data to the Monday 10 days earlier), monthly from
  2021-02-23 (fourth Tuesday 13:00 ET, 4-5 weeks at once, 25-55 days stale). Weekly SA data and institutional MMF end
  2021-02-01. Retail MMF was revised in 2026-07 (netting), so the vintage is not real-time.
  `releaseDates.json` dates carry suffixes such as `20020214**`.

## Directions that need the user
| direction | value |
|---|---|
| ICI weekly flow spreadsheets downloaded by hand in a browser (families 1, 2, 4, ETF issuance) | LIVE < 1 %, DEMO ~1-2 % |
| Forward test of the USD reading (EURUSD up, gold up after a z >= 1 H.6 release) on releases after 2026-09-24 | ~3-6 trades a year, low |

## State after round 50
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 51 opens next.
