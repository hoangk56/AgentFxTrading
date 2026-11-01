# Round 49: central-bank speech text tone (Fed, ECB), 2026-10-30

Brief: [round49_cb_speech_tone/BRIEF.md](round49_cb_speech_tone/BRIEF.md). Same LIVE / DEMO bars as rounds 25-48.
HOLD (2025-01..2026-09) stayed closed (speech lists and texts cut before 2025 at parse, IC at load with an assert).
HYPOTHESES_T.md written 08:41 UTC, before any return. Disclosure: the FOMC calendar fetch (13 requests) overlapped the
speech fetch on www.federalreserve.gov for ~20 s at ~1.5 requests a second.

## Answer
No LIVE or DEMO candidate, no PREREG_DRAFT. The dictionary tone measure tracks policy (Fed yearly tone ~-0.30 in
2015-16, ~+0.40 in 2022-23), but the market does not trade on it: the policy-signed move from 1 minute before posting
to 15 minutes after is -1.2..+1.3 bp (|t| <= 1.3) in every era, and none of 76 cells reaches IS net t 2 (best +1.59 vs
chance p95 2.71). Only ~30 Fed speeches a year carry a signal (43 % of Board speeches are regulatory). Not a candidate:
Fed |x| >= 1 tone surprises drift in the policy direction from +15 minutes to the NY close in VAL on all four legs
(BOOK +16.7 bp, t 3.12), but this is 2022 (+52.4; 2023 +15.9, 2024 +3.6), IS is +3.0 (t 1.24) and PRE -3.7: a hiking-
cycle effect seen only in VAL (round 18: such rules keep ~19-31 % of VAL in HOLD).

## Stream
| stream | tested | verdict | detail |
|---|---|---|---|
| T | Hawk / dove dictionary tone of 1,156 Fed Board speeches 2006-24 (posting times) and the ECB speech CSV (dates only) vs each speaker's trailing tone -> EURUSD, USDJPY, XAU, US500 (DE40 for the ECB): F1 drift from +5 / +15 min to NY close / 1 day, F2 outside blackout and away from data, F3 weekly Fed-minus-ECB tone gap -> EURUSD; 76 cells | **none**: primary Fed BOOK 1 d net IS +2.92 (t 0.57) / VAL +17.50 (1.26); ECB BOOK IS -6.24 (wrong sign: hawkish ECB -> weaker euro next day, t -2.05); F3 IS t <= 0.14 | [STREAM_T.md](round49_cb_speech_tone/STREAM_T.md), [HYPOTHESES_T.md](round49_cb_speech_tone/HYPOTHESES_T.md) |

Correlation with C3: not computed (nothing survived).

## Exhausted after this round (add to PROMPT "Những họ đã cạn")
- Central-bank speech text tone (Fed Board, ECB; dictionary, speaker-relative surprise, blackout / data filters,
  cross-bank gap) at +5 minutes to 5 days. Do not register the 2022 Fed VAL drift.

## Pitfalls
- www.federalreserve.gov `json/ne-speeches.json` has posting times (ET) and runs to today: cut at parse. Speech text
  starts after `class='location'`; cut at the first footnote anchor or `lastUpdate`.
- The ECB `press/key/shared/data/all_ECB_speeches.csv` has no times, mixes German / French texts, interviews and
  introductory statements, and runs to 2026; www.ecb.europa.eu robots.txt sets Crawl-delay 5.
- FOMC pages write two-month meetings as "Jan/Feb 31-1" from 2016 and "July 31-August 1" before.
- Waiters should check the worker by PID: a `pgrep -f` miss once reported a live worker as dead.

## Directions that need the user
| direction | value |
|---|---|
| Paid wire timestamps for speech headlines | LIVE < 1 %, DEMO ~1-2 % |
| Intraday Treasury / Bund futures (rates channel) | LIVE < 1 %, DEMO ~2 % |
| LLM / FinBERT tone designed on 2010-21 only (VAL already seen) | LIVE < 1 %, DEMO ~2 % |

## State after round 49
C3 is the only LIVE algorithm; F3 live at 0.01 lot, E1 and the gold $50 rule on demo. Round 50 opens next.
