HOLD PREPARATION: round 27 draft G1-XAU50 (gold; resting stop at a fresh $10 level +- 0.5 x s60; trade only $50 levels;
30-minute exit; 250 ms latency decides)

Written 2026-10-18 00:25 UTC (date -u) by the lead's helper. HOLD (2025-01-01 .. 2026-09-24) was NOT opened.
- No price dated 2025-01-01 or later was loaded, printed or computed.
- Every data run here had HOLD_RUN unset, and the loader then refuses any day >= 2025-01-01.
- The only process started with HOLD_RUN=1 was work/guard_test.py. It calls pure functions only and checks that the
  day 2026-09-25 is refused; the assert fires before any file is opened.
- Nothing under research/ or r27/ was edited.

Folder: /private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/lead/hold/

========================================================================================================================
1. FILES
========================================================================================================================
gcommon.py              round 27 gcommon.py + the HOLD switch + the registered calendar rule (section 3)
engine.py, fills.py     round 27 files, byte-identical (cmp; sha256 equal to r27/G/code/)
build_minutes_hold.py   round 27 build_minutes.py for a date range (the only change)
run_hold.py             round 27 run_real.py reduced to one bot: G1, c = 0.5, $10 grid (u = 0, S = 10); keeps the mod50
                        trades; writes the per-trade CSV / NPZ and a summary
usd_high_2024_2026.csv  official-schedule calendar 2024-01-01 .. 2026-09-30 (columns utc_minute, event, source):
                        814 rows, 699 unique minutes (2024: 262, 2025: 247, 2026 to Sep 30: 190;
                        HOLD 2025-01-01 .. 2026-09-24: 506 rows, 433 minutes)
calendar_check_2024.txt the 2024 comparison with ForexFactory (section 2)
calendar_fetch_log.txt  every fetch: date -u time, tool, URL, saved file, HTTP status. 749 lines; no e-mail or
                        personal data in any request. A few lines wrap because curl printed an error message.
SHA256SUMS.txt          the registered files (section 7)
out/                    minute files, trades_<run>.csv / .npz, summary_<run>.txt, repro_check.txt, cal_swap_2024.txt
work/                   calendar build and checks:
                          build_calendar.py, compare_2024.py, cal_swap_diff.py, repro_check.py, guard_test.py
                          fed_items.csv (parsed Fed monthly calendars)
                          cal_a.csv (Census, DOL, Treasury) and cal_b.csv (ISM, CB, UMich, S&P Global, NY Fed, ADP),
                            built by two helper agents from the publishers' pages; their scripts are in py_a/ and py_b/
                          usd_high_2024_2026_detail.csv (ET date / time and a note for every row)
                          dl/ (downloads, untrusted data), fetch.sh (the logging fetch helper)

========================================================================================================================
2. CALENDAR (task 1)
========================================================================================================================
Event types in the official list. Times are ET. Dates are the actual release dates, after the shutdown delays and
cancellations, not the originally planned ones.
- BLS, yearly release calendars bls.gov/schedule/<Y>/home.htm, cross-checked against the news-release archives (no
  difference):
    Employment Situation (NFP, AHE, unemployment rate) 08:30; CPI 08:30; PPI 08:30; JOLTS 10:00; ECI 08:30.
- BEA: GDP (advance / second / third; in 2025-26 also "initial" / "updated") and Personal Income and Outlays (core
  PCE).
    2024: BEA's 2024 schedule PDF (final version of 2024-12-05). The release pages confirm Sep 27 08:30, Oct 31 08:30,
          Nov 27 10:00 and Dec 20 08:30.
    2025-26: apps.bea.gov/API/signup/release_dates.json. The cancelled 2025-10-30 GDP advance estimate is absent;
             PIO came at 10:00 on 2025-04-30, 2025-12-05 and 2026-01-22.
- Census advance retail sales, 08:30.
    census.gov returns 403 to scripts, so the Census release PDFs, the release-date .xls and the schedule page were
    read from web.archive.org copies of the census.gov files. The content is Census's own.
- DOL weekly claims, 08:30, from the 136 release PDFs (embargo line).
    No national release on 2025-10-02 .. 11-13 (7 weeks, lapse in appropriations).
    Moved to Wednesday: 2024-07-03, 2024-11-27, 2025-01-08 (Carter day of mourning), 2025-06-18, 2025-11-26,
    2025-12-24, 2025-12-31.
- ADP National Employment Report (monthly), 08:15; ADP's releases.
    ADP kept its Wednesday dates while BLS was delayed. The weekly "NER Pulse" (Tuesdays since 2025-10-28) is not
    included.
- ISM Manufacturing and Services, 10:00; ISM's releases.
    January releases come one business day late.
- Conference Board consumer confidence, 10:00; CB's releases.
    Off the last-Tuesday rule on 2024-12-23 (Mon) and 2025-12-23.
- University of Michigan preliminary and final sentiment, 10:00; SCA report PDFs and the release-date table.
- S&P Global flash US PMI, 09:45 every month; the embargo line of each release PDF.
    15 of the 33 PDFs are web.archive.org copies of the same URLs.
- NY Fed Empire State, 08:30 (NY Fed's standing "released at 8:30" note); dates from NY Fed pages.
- FOMC, from the Fed monthly calendars and fomccalendars.htm:
    statement and rate decision 14:00 (SEP flagged at the * meetings), press conference 14:30, minutes 14:00.
    The 2025-01-08 minutes are missing from the January 2025 monthly page; they were taken from fomccalendars.htm.
- Fed Chair speeches and testimony: every Speeches / Testimony item of the Chair in the Fed monthly calendars, at its
  listed ET start time. This includes moderated discussions and pre-recorded remarks.
    Powell is Chair until May 2026; "Chairman Kevin Warsh" from June 2026 (1 speech, 1 discussion, 2 testimony days
    to Sep). Powell's 2026-05-31 speech as Governor is not a Chair event.
    3 weekend items are kept; all three fall outside the arming hours.
    Not included: Powell's unscheduled Sunday-evening video statement of 2026-01-11. It is in the Fed speech list but
    has no official time.
- Treasury 10-year note and 30-year bond auctions, including reopenings, all 66 of them: 13:00, the competitive close
  (FF lists the results at 13:01; that is within +-1 min).
- Treasury FX report (2024-06-20, 2024-11-14, 2025-06-05, 2026-01-29, 2026-07-23): 16:00.
    The time comes from the official page's <time> stamp; the press-release text gives no time. FF also had 16:00 for
    2024-06-20.

Not in the official list: types that FF rated High only now and then in 2022-24 and that are not among the listed
sources. These are pending home sales, Philly Fed, durable goods, new home sales, final manufacturing PMI, FOMC members
other than the Chair, and unscheduled Fed announcements.

Check of 2024 against ForexFactory (calendar_check_2024.txt):
- Unique minutes: FF 238, official 262.
- Matched within +-1 min: 218 (214 at the same minute). FF-only 20, official-only 44.
- The 20 FF-only minutes:
    10 are types the official list does not have: pending home sales 4, final manufacturing PMI 2, Waller 2, durable
       goods 1, new home sales 1.
     8 are FF mistimings:
         ECI at 09:45 four times (official 08:30);
         PCE 2024-10-31 at 10:00 (BEA: 08:30);
         Powell 04-16 at 12:10 (Fed calendar 13:15), 07-02 at 12:30 (09:30) and 12-04 at 13:45 (13:40).
     2 are Powell items the Fed calendar does not have: 02-05 and 03-22 at 11:30.
- The 44 official-only minutes:
    20 auctions (FF rated 4 of the 24 High);
    10 UMich and 3 Empire State releases that FF rated below High;
    CB 2024-12-23;
    the FX report of 2024-11-14;
    Powell's Sunday video of 2024-05-19;
    8 correct-time counterparts of the FF mistimings (ECI 3, PCE 2, Powell 3).
- Arming minutes of 2024 (341,648 clock minutes, 336,845 of them with ticks):
    excluded by FF 6,959 (2.04 %), by official 7,683 (2.25 %);
    1,682 minutes differ (0.49 %): 479 excluded only by FF, 1,203 only by official.
- Effect on the draft cell's trades (VAL 2024, out/cal_swap_2024.txt):
    75 trades are common, and all their readings are identical.
    1 trade is removed: 2024-08-16, net -50.96 bp. It was armed at 09:51 NY, 9 minutes before the 10:00 UMich prelim
      that FF did not rate High.
    3 trades are added: +20.86, -8.64 and +9.95 bp. FF blocked them with its 09:45 ECI mistiming, a 10:00 pending
      home sales row and a 10:00 PCE mistiming.

========================================================================================================================
3. CODE (task 2): logic unchanged
========================================================================================================================
engine.py and fills.py: byte-identical copies (cmp OK; sha256 92bc5847... and cf637406..., the same as r27/G/code).

gcommon.py: a copy of round 27's gcommon.py. `diff r27/G/code/gcommon.py gcommon.py` shows only these changes:
- OUT = r28/lead/hold/out/.
- HOLD switch HOLD_RUN = (os.environ.get('HOLD_RUN') == '1').
    Without it: LIMIT_DAY = 2025-01-01, HOLD_MS = 2025-01-01 00:00 UTC, i.e. round 27's guard. DayLoader.load asserts
      d < LIMIT_DAY and the last tick < HOLD_MS, and engine.SessionFeed stops at HOLD_MS.
    With HOLD_RUN=1: LIMIT_DAY = 2026-09-25 and HOLD_MS = 2026-09-25 00:00 UTC, so days up to 2026-09-24 are allowed.
    The era boundary is HOLD_START_MS = 2025-01-01 in both cases.
- era_of_ms returns 'HOLD' for 2025-01-01 <= t < 2026-09-25 when HOLD_RUN=1, and raises otherwise (as before).
- load_high_usd() = THE REGISTERED CALENDAR RULE.
    The High-impact USD minutes are the ForexFactory rows of r25/shared/cal/ff_events_utc.csv (cur USD, impact High,
    timed) for times < 2024-01-01 00:00 UTC, exactly as round 27 read them, and the rows of usd_high_2024_2026.csv
    for times >= 2024-01-01 00:00 UTC.
    Without HOLD_RUN=1 minutes >= 2025-01-01 are dropped, as before.
    load_high_usd(ff_only=True) is round 27's calendar (FF through 2024-12-31). It is used only for the reproduction
    and is refused with HOLD_RUN=1.

build_minutes_hold.py SYM START END
- Same arrays and code as round 27's build_minutes.py.
- T0M = START 00:00 UTC; days START..END; output out/min_<SYM>_<START>_<END>.npz.
- Asserts END < LIMIT_DAY before reading anything.

run_hold.py --minutes F --sessions D0 D1 [--keep-from D] --cal reg|ff --name NAME
- Runs one bot: G1, c 0.5, u 0, S 10, over NY sessions D0..D1. All $10 triggers feed the busy window and the
  1,440-minute rule, as in the tested cell.
- Keeps triggers >= keep-from whose level is a multiple of $50 (grid index % 5 == 0, as run_real.flags_for).
- engine.Minutes is subclassed only to read a given file. It asserts that the file covers each session with >= 25 h
  of warm-up.
- Per-trade rows (out/trades_<NAME>.csv, and .npz with every raw fills.outputs array):
    trigger time, arm time, era, side, level, stop price, s60;
    gross (mid) and net at L0 / tick / 250 / 1000 ms for h30, no stop;
    net at spread x1.5 (fills' net15 in the 250 ms column, as analyze.py's x15);
    net with both fills +1 minute (latency '60000', as analyze.py's '+1 min');
    exit / entry gap flags.
- Summary (out/summary_<NAME>.txt), for all trades and by era:
    n, mean net 250 and t clustered by UTC day;
    mid; the L0 / tick / 250 / 1000 means;
    x1.5 and +1 min (mean and t);
    per-trade Sharpe and median;
    n and net / x1.5 / +1 min by year.
- --cal ff is refused with HOLD_RUN=1 or with sessions in 2025.
- Guard checks (work/guard_test.py):
    Without HOLD_RUN: loading 2025-01-01 or 2026-09-24 is refused before the file is opened; era_of_ms(2025) raises;
      build_minutes_hold.py and run_hold.py given a 2025 date stop with an AssertionError at start.
    With HOLD_RUN=1: 2026-09-25 is refused, era_of_ms(2025-01-01) = 'HOLD', ff_only is refused, and the calendar runs
      to 2026-09-30.

Round 28 R1's look-ahead finding, checked here: it does not reach the tick engine.
- pre_minute.py sets mo.T0M = t0 - 60000 while its closes are stamped bar start + 60 s. So midx(close of bar i) = i + 2,
  and W_up[i+2] includes the close of bar i+1: a one-bar look-ahead in event selection.
- The tick engine uses engine.Minutes on min_<SYM>.npz: T0M is the true start of minute 0, and midx(tick) is the minute
  that contains the tick.
    W_up[m] / W_dn[m] cover minutes m-1440 .. m-1. A brute-force check on 4,000 random minutes gave 0 mismatches.
    Ticks of the current minute enter only through exmax / exmin, which use strictly earlier ticks.
    s60[m] covers minutes m-60 .. m-1.
- So only the draft's PRE (minute-level) readings are affected, not IS / VAL ticks and not HOLD.

========================================================================================================================
4. REPRODUCTION (task 3, no HOLD; out/repro_check.txt)
========================================================================================================================
cd /Users/hoangbk/00.code_base/105.AgentFxTrading; H=<folder above>
env -u HOLD_RUN PYTHONPATH=. research/.venv/bin/python $H/build_minutes_hold.py XAUUSD 2015-12-28 2021-12-31
env -u HOLD_RUN PYTHONPATH=. research/.venv/bin/python $H/build_minutes_hold.py XAUUSD 2021-12-27 2024-12-31
env -u HOLD_RUN PYTHONPATH=. research/.venv/bin/python $H/run_hold.py --minutes out/min_XAUUSD_20151228_20211231.npz \
    --sessions 2015-12-30 2021-12-31 --keep-from 2016-01-01 --cal ff --name IS_ff
env -u HOLD_RUN PYTHONPATH=. research/.venv/bin/python $H/run_hold.py --minutes out/min_XAUUSD_20211227_20241231.npz \
    --sessions 2022-01-01 2024-12-31 --keep-from 2022-01-01 --cal ff --name VAL_ff
env -u HOLD_RUN PYTHONPATH=. research/.venv/bin/python $H/run_hold.py --minutes out/min_XAUUSD_20211227_20241231.npz \
    --sessions 2022-01-01 2024-12-31 --keep-from 2022-01-01 --cal reg --name VAL_reg

Round 27's calendar (FF), exact match:
- Every one of the 271 IS and 185 VAL trades is identical to round 27's ev_XAU10_G1_0.5.npz (mod50 events):
    ts, arm time, level, side, stop, s60, mid and spread at the trigger;
    every net / gross / net15 value at all 5 latencies x 4 holds x 2 stop variants (np.array_equal on the float32
    arrays);
    the gap flags.
  The $10 event counts are also equal: 1,344 / 945.
- IS n 271:
    net +5.99 (t 2.66), mid +7.72 (t 3.41);
    L0 / tick / 250 / 1000 = +6.10 / +6.05 / +5.99 / +5.85;
    x1.5 +5.42, +1 min +6.19.
- VAL n 185:
    net +3.27 (t 1.81), mid +4.29 (t 2.37);
    +3.39 / +3.25 / +3.27 / +3.25;
    x1.5 +3.05, +1 min +2.87.
- By year: 2016 +4.84, 2017 +4.86, 2018 +6.17, 2019 +0.19, 2020 +8.26, 2021 +8.45, 2022 +2.28, 2023 +5.24, 2024 +3.04.
  These are the draft's numbers.
- Minute arrays:
    The IS file equals r27's min_XAUUSD.npz on its whole range, all 8 arrays.
    The late-start VAL file (from 2021-12-27) is identical from its minute 1500 on. The differences sit in the first
    540 minutes of 2021-12-27, before any session used. This is the warm-up argument for HOLD.

Registered calendar (official from 2024-01-01), run VAL_reg:
- IS and VAL 2022-23 are unchanged: the same FF rows.
- VAL 2024: n 78, net +3.90 (x1.5 +3.76, +1 min +3.11), against n 76 and +3.04 under FF. The 4 trades are listed in
  section 2.
- VAL 2022-24: n 187, net +3.62 (t 2.05), mid +4.65 (t 2.62), x1.5 +3.41, +1 min +3.25, per-trade Sharpe 0.158,
  against round 27's n 185, +3.27 (t 1.81), Sharpe 0.140.

========================================================================================================================
5. HOLD COMMANDS (for the lead; HOLD_RUN=1 only here)
========================================================================================================================
cd /Users/hoangbk/00.code_base/105.AgentFxTrading
H=/private/tmp/claude-501/-Users-hoangbk-00-code-base-105-AgentFxTrading/cff348f1-534e-440d-88da-40c31dade827/scratchpad/r28/lead/hold
(cd $H && shasum -a 256 -c SHA256SUMS.txt)            # all OK before running
HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $H/build_minutes_hold.py XAUUSD 2024-12-26 2026-09-24
HOLD_RUN=1 PYTHONPATH=. research/.venv/bin/python $H/run_hold.py --minutes out/min_XAUUSD_20241226_20260924.npz \
    --sessions 2025-01-02 2026-09-24 --keep-from 2025-01-01 --cal reg --name HOLD

Outputs:
- out/min_XAUUSD_20241226_20260924.npz
- out/trades_HOLD.csv and .npz
- out/summary_HOLD.txt. Its line "[HOLD] net 250 ms: n .. mean .. (t ..)" is the decision number; the draft's rule is
  net < 0 = reject. About 107 trades are expected.

- Warm-up: the minute file starts 2024-12-26 00:00 UTC (VAL days), more than 6 days before the first arming.
  SessionFeed preloads from d0 - 3 days (2024-12-30).
- No state carries over:
    The last possible 2024 trigger is before 15:54 NY on 2024-12-31 (that tick file ends at 21:59 UTC).
    The first possible HOLD arming is 2025-01-01 23:25 UTC (18:10 NY plus the 15-minute post-gap rule).
    That is more than 24 h, so the busy window and the 1,440-minute level rule start empty in any run.
- Session d = 2025-01-01 is left out, as specified. Its window (2024-12-31 23:10 UTC .. 2025-01-01 22:00 UTC) holds no
  2024 ticks. In VAL, IC gold reopened at 23:02 UTC on 2024-01-01, after that session's window. Starting at 2025-01-01
  would only add that session if it had more than 10 ticks; this can't be checked without HOLD data.

========================================================================================================================
6. NOTES FOR THE LEAD
========================================================================================================================
- The calendar swap moves VAL up (+3.27 -> +3.62, t 1.81 -> 2.05). Almost all of the move comes from one -51 bp trade
  that the official UMich row excludes. The type list was fixed by the brief before any trade was looked at.
  - HOLD runs under the registered calendar, so the comparable VAL is VAL_reg.
  - The draft's expected HOLD t (1.45 at the VAL size) used VAL_FF.
- Unscheduled items are absent in 2025-26, as they are in any schedule-based list: the 2026-01-11 Powell statement,
  ad-hoc Fed or Treasury announcements, and the ADP weekly series. FF would probably have listed some of them.
- Census rows rest on archived copies of census.gov files. S&P Global rows partly do too.
- Empire's 08:30 rests on NY Fed's standing note, not on per-release stamps.
- The FX-report time (16:00) is page metadata, not text.
- These choices affect at most a few minutes each. The claims gap of October-November 2025 adds arming time on 7
  Thursdays.
- The data read in HOLD: research/data/XAUUSD/t1/20241226..20260924.zticks. The XAUUSD files reach 20260924.
- Each run takes a few minutes at most and uses numpy only. One heavy process at a time is enough.

========================================================================================================================
7. FILES TO REGISTER (sha256; SHA256SUMS.txt, paths relative to this folder)
========================================================================================================================
9cf1b896c062a5355e9fec28b41f3e68e227fe3c83a26a35bc7b4960a84039cc  gcommon.py
92bc5847da24cbc864b1e2b5087bb0fcdb4e2aa887f169979851810d5b8fed15  engine.py   (= r27/G/code/engine.py)
cf637406c7c4a4442bf871ae03cb2499ea194ccff5976689bb1ab33171844f74  fills.py    (= r27/G/code/fills.py)
a7e82ce37c3bbe4780d23e0f1037beec9cfe74bf966306471072897fd9eab6bf  build_minutes_hold.py
54952ea6016e874de81c1cc6889904513ced98453cf666299ad89647f644024f  run_hold.py
30a931520991bb797f4222a20e504496e233bba2e5e978550d1d59012d57e823  usd_high_2024_2026.csv
7308d2ebf60c4d8f97332b832197f95292eeb6bc22efe12a1f1290f27d4f0bde  ../../../r25/shared/cal/ff_events_utc.csv (read for < 2024)
Provenance, optional:
3403164891ede801a2a7c79147c418a8b6d963047d46b8296980d9b1f761627f  work/build_calendar.py
dad1699dd8f5f542c7be05b0985b70f5b10b81448349a6452378eec0cfffd6a7  work/cal_a.csv
cac1d1fcf25b93f190f5816ffa2edf98e7f0bc2d47c406d41c26b4d349fc0839  work/cal_b.csv
c78e1383834e8a70bd4118b69fae76e42a4b6778f167c99c06a167450120c72e  work/fed_items.csv
