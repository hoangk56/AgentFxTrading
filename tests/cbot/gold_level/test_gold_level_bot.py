"""cBot/GoldLevelBot.cs against the registered rule it implements (G1-XAU50) and the brief's hard rules.

The rule's numbers live in the registered code, research/results/portfolio/round27_levels_opens/prereg_code/: engine.py.txt
(levels, band, busy window, level memory, sessions, exclusions), run_hold.py.txt (the cell: G1, c 0.5, $10 grid, 30-minute
hold, $50 levels), build_minutes_hold.py.txt (the 24-hour envelope and s60) and fills.py.txt (the fill model). The
cBot's defaults must equal them, or a demo result no longer says anything about the holdout. The hard rules: lots never
depend on account capital, no position is held longer than 5 days, a bot never holds more than 3 positions (this one:
1 at a time).

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build and a backtest against the
holdout trades are checked on the VPS (research/results/portfolio/gold_level_cbot_2026-10-18.md).
"""
import csv
import datetime as dt
import re

from tests._paths import CBOT_DIR, REPO_ROOT

SRC = (CBOT_DIR / "GoldLevelBot.cs").read_text(encoding="utf-8")
PREREG = REPO_ROOT / "research" / "results" / "portfolio" / "round27_levels_opens" / "prereg_code"
ENGINE = (PREREG / "engine.py.txt").read_text(encoding="utf-8")
RUN = (PREREG / "run_hold.py.txt").read_text(encoding="utf-8")
MINUTES = (PREREG / "build_minutes_hold.py.txt").read_text(encoding="utf-8")
FILLS = (PREREG / "fills.py.txt").read_text(encoding="utf-8")
REGISTERED_CAL = PREREG / "usd_high_2024_2026.csv"
SEED = CBOT_DIR / "seeds" / "usd_high_calendar.csv"


def _default(prop: str) -> str:
    m = re.search(r'DefaultValue = ("[^"]*"|[\w.]+)[^\]]*\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no [Parameter] default for {prop}"
    return m.group(1).strip('"')


def _body(signature: str) -> str:
    start = SRC.index(signature)
    open_idx = SRC.index("{", start)
    depth = 0
    for i in range(open_idx, len(SRC)):
        depth += {"{": 1, "}": -1}.get(SRC[i], 0)
        if depth == 0:
            return SRC[open_idx:i + 1]
    raise AssertionError(f"unbalanced braces in {signature}")


def test_the_cell_is_the_registered_one():
    fam, c, s, u = re.search(r"FAM, C, S, U = '(\w+)', ([\d.]+), ([\d.]+), ([\d.]+)", RUN).groups()
    assert fam == "G1" and float(u) == 0.0                      # resting stops on the plain $10 grid
    assert float(_default("LevelStep")) == float(s)
    assert float(_default("StopOffsetSpreads")) == float(c)
    assert int(_default("HoldMinutes")) == int(re.search(r"^H = (\d+)", RUN, re.M).group(1))
    # trades only the levels whose grid index is a multiple of 5: the $50 levels
    assert "int(round((e[2] - U) / S)) % 5 == 0" in RUN
    assert float(_default("TradedMultiple")) == 5 * float(s)
    assert "return k % every == 0;" in _body("private bool IsTradedLevel(double level)")
    # the trade side follows the break: a buy stop above an upper level, a sell stop below a lower one
    assert "thr = L + c * sa if fam == 'G1'" in ENGINE and "thr = L - c * sa if fam == 'G1'" in ENGINE
    step = _body("private void Step(DateTime t, double bid, double ask, double mid, bool ok)")
    assert "Stop = side > 0 ? level + off : level - off" in step


def test_band_freshness_and_marketable_check_are_the_engines():
    d_frac = float(re.search(r"D_FRAC, PS_FRAC, TOUCH_FRAC = ([\d.]+),", ENGINE).group(1))
    assert float(_default("ArmBand")) == d_frac * float(_default("LevelStep"))
    assert "ku = np.floor((mid - u) / S) + 1.0" in ENGINE and "kd = np.ceil((mid - u) / S) - 1.0" in ENGINE
    assert "in_up = (Lup - mid) <= D" in ENGINE and "in_dn = (mid - Ldn) <= D" in ENGINE
    assert "arm_up = in_up & (Lup > M24) & ok & ~trig_up_now" in ENGINE
    assert "arm_dn = in_dn & (Ldn < m24) & ok & ~trig_dn_now" in ENGINE
    step = _body("private void Step(DateTime t, double bid, double ask, double mid, bool ok)")
    assert "LevelStep * (Math.Floor(mid / LevelStep) + 1.0)" in step
    assert "LevelStep * (Math.Ceiling(mid / LevelStep) - 1.0)" in step
    assert "bool armUp = up - mid <= ArmBand && up > high && !(ask >= up + off);" in step
    assert "bool armDn = mid - dn <= ArmBand && dn < low && !(bid <= dn - off);" in step
    # the 24-hour high / low: the minutes before this one, then this minute's earlier ticks (engine exmax / exmin)
    assert "M24 = np.maximum(mins.W_up[mi], exmax)" in ENGINE
    assert "double high = Math.Max(_wUp, _curMax), low = Math.Min(_wDn, _curMin);" in step


def test_trigger_cancel_busy_and_memory_are_the_engines():
    busy = int(re.search(r"^BUSY_MS = (\d+) \* 60000", ENGINE, re.M).group(1))
    day = int(re.search(r"^DAY_MS = (\d+) \* 60000", ENGINE, re.M).group(1))
    assert int(_default("BusyMinutes")) == busy
    assert int(_default("LevelMemoryMinutes")) == day
    assert "trig = lambda x, y: ask[x:y] >= thr" in ENGINE and "trig = lambda x, y: bid[x:y] <= thr" in ENGINE
    assert "(mid[x:y] < lo_band) | ~ok[x:y]" in ENGINE and "(mid[x:y] > hi_band) | ~ok[x:y]" in ENGINE
    step = _body("private void Step(DateTime t, double bid, double ask, double mid, bool ok)")
    assert "bool cancel = !ok || (a.Side > 0 ? mid < a.Level - ArmBand : mid > a.Level + ArmBand);" in step
    assert "(a.Side > 0 ? ask >= a.Stop : bid <= a.Stop)" in step
    # the cancelling tick itself can trigger nothing (engine: j < e), and the scan goes on from it (i = e)
    assert step.index("if (!cancel)") < step.index("Trigger(t, bid, ask)")
    assert "if (!ok || t < _busyUntil" in step
    # a level that triggered in the last day blocks the scan until its band is left (engine: i = e)
    assert "if key in traded and ts[a] - traded[key] < DAY_MS:\n            i = e" in ENGINE
    assert "(t - last).TotalMinutes < LevelMemoryMinutes" in step and "_mode = ArmMode.Blocked;" in step
    trig = _body("private void Trigger(DateTime t, double bid, double ask)")
    assert "_busyUntil = t.AddMinutes(BusyMinutes);" in trig and "_triggered[a.Key] = t;" in trig
    # every $10 trigger counts, traded or not
    assert trig.index("_triggered[a.Key] = t;") < trig.index("if (!a.Traded) return;")


def test_sessions_and_exclusions_are_the_engines():
    assert "t_start = ny_ms(d - timedelta(days=1), 18, 10)" in ENGINE and "t_end = ny_ms(d, 17, 0)" in ENGINE
    assert "if parts and d.weekday() < 5:" in ENGINE
    assert "ok = (ts >= ny_ms(d - timedelta(days=1), 18, 10)) & (ts < ny_ms(d, 15, 54))" in ENGINE
    assert (_default("ArmFromHourNewYork"), _default("ArmFromMinuteNewYork")) == ("18", "10")
    assert (_default("ArmToHourNewYork"), _default("ArmToMinuteNewYork")) == ("15", "54")
    assert "private static readonly TimeSpan SessionEndNewYork = new TimeSpan(17, 0, 0);" in SRC
    assert "return IsWeekday(d) ? d : (DateTime?)null;" in _body("private DateTime? SessionDay(DateTime utc)")
    # +-15 minutes of a release minute, both ends included
    assert "near = np.abs(rel_ms[k] - ts) <= 15 * 60000" in ENGINE
    assert int(_default("NewsExclusionMinutes")) == 15
    near = _body("private bool NearRelease(DateTime t)")
    assert "_releases[lo] <= t + w" in near and "_releases[m] < from" in near
    # 15 minutes without arming after a gap of more than 60 minutes; the session's first tick counts as one
    assert "gap = np.r_[np.inf, np.diff(ts)] > 3600000" in ENGINE and "(ts - gt[np.maximum(k, 0)] < 15 * 60000)" in ENGINE
    assert int(_default("GapMinutes")) == 60 and int(_default("GapCooldownMinutes")) == 15
    tick = _body("private void ProcessTick(DateTime t, double bid, double ask)")
    assert "if (newSession || (t - _lastTickAt).TotalMinutes > GapMinutes) _gapAt = t;" in tick
    allowed = _body("private bool ArmingAllowed(DateTime t, DateTime sessionDay)")
    assert "(t - _gapAt).TotalMinutes < GapCooldownMinutes" in allowed and "NearRelease(t)" in allowed
    # an arm lives in one session (gen_events runs per session); busy and memory carry over
    assert "if (newSession && _mode != ArmMode.Idle)" in tick


def test_envelope_and_spread_median_are_the_minute_files():
    assert "W_up = rolling_max_excl(mmax, 1440)" in MINUTES and "W_dn = -rolling_max_excl(-mmin, 1440)" in MINUTES
    assert "sw = sliding_window_view(lspr, 60)" in MINUTES and "np.nanmedian(blk, axis=1)" in MINUTES
    assert int(_default("FreshWindowMinutes")) == 1440 and int(_default("SpreadWindowMinutes")) == 60
    roll = _body("private void RollMinute(long minute)")
    assert "for (long k = minute - FreshWindowMinutes; k < minute; k++)" in roll
    assert "for (long k = minute - SpreadWindowMinutes; k < minute; k++)" in roll
    assert "if (_spreadBuf.Count > 0) _s60 = Median(_spreadBuf);" in roll      # none in the window: carried forward
    assert "(s[n / 2 - 1] + s[n / 2]) / 2.0" in _body("public static double Median(List<double> values)")
    tick = _body("private void ProcessTick(DateTime t, double bid, double ask)")
    # the tick is judged before it joins the envelope (exmax uses strictly earlier ticks)
    assert tick.index("Step(t, bid, ask, mid, ArmingAllowed(t, session.Value));") < tick.index("if (mid > _curMax) _curMax = mid;")
    # crossed or one-sided quotes are dropped, as gcommon.DayLoader does
    assert "if (!(bid > 0) || !(ask > 0) || ask < bid) return;" in tick


def test_the_fill_model_in_the_trade_log_is_the_registered_one():
    assert re.search(r"^LDEC = '(\d+)'", RUN, re.M).group(1) == _default("ModelLatencyMs")
    assert float(re.search(r"^COMM = ([\d.]+)", FILLS, re.M).group(1)) == float(
        re.search(r"private const double ModelCommissionBp = ([\d.]+);", SRC).group(1))
    assert int(re.search(r"^GAP_MS = (\d+)", FILLS, re.M).group(1)) == 60000 * int(
        re.search(r"private const int TradeLogFlushMinutes = (\d+);", SRC).group(1))
    cap = _body("private void CaptureModelPrices(DateTime t, double bid, double ask)")
    assert "tr.ModelEntry = tr.Side > 0 ? ask : bid;" in cap and "tr.ModelExit = tr.Side > 0 ? bid : ask;" in cap


def test_orders_trigger_like_the_rule_and_rest_at_the_broker():
    place = _body("private void TryPlace(DateTime now)")
    assert "StopTriggerMethod.Trade, StopTriggerMethod.Trade" in place     # buy stop on ask >= price, sell on bid <= price
    assert "arm.OrderPrice = side > 0 ? CeilToTick(arm.Stop) : FloorToTick(arm.Stop);" in SRC
    assert "ExecuteMarketOrder" not in SRC, "a trigger without a fill is logged as missed, never chased at market"
    assert SRC.count("PlaceStopOrderAsync(") == 1
    # no order inside an exclusion: cancelled CancelLeadSeconds before it, none placed that close to it
    assert "ClosingSoon(now)" in place and "ClosingSoon(now)" in _body("private void ManageOrders(DateTime now)")


def test_lot_is_fixed_one_position_at_a_time_held_minutes_not_days():
    place = _body("private void TryPlace(DateTime now)")
    assert "Account." not in place and "Account." not in _expr("private double OrderVolume()")
    assert "Lots * Symbol.LotSize" in _expr("private double OrderVolume()")
    assert "_working != null" in place and "GetBotPositions().Count > 0" in place
    assert int(_default("MaxHoldMinutes")) <= 24 * 60
    assert int(re.search(r'Max Hold \(minutes\)".*MaxValue = (\d+)\)', SRC).group(1)) <= 5 * 24 * 60
    exits = _body("private void ManageExits(DateTime now)")
    assert "now >= trade.ExitDue" in exits and "TimeSpan.FromMinutes(MaxHoldMinutes)" in exits


def _expr(signature: str) -> str:
    start = SRC.index(signature)
    return SRC[start:SRC.index(";", start)]


def _seed():
    lines = SEED.read_text().splitlines()
    valid = [re.search(r"valid_through=(\d{4}-\d{2}-\d{2})", ln) for ln in lines if ln.startswith("#")]
    valid = [m.group(1) for m in valid if m]
    rows = [ln.split(",")[0] for ln in lines if ln and not ln.startswith("#") and not ln.startswith("utc_minute")]
    return valid, rows


def test_seed_calendar_is_where_the_bot_reads_it_and_holds_the_registered_minutes():
    assert _default("CalendarFile") == "/workspace/cBot/seeds/usd_high_calendar.csv"
    valid, rows = _seed()
    assert len(valid) == 1, "the seed needs exactly one valid_through line"
    assert rows == sorted(set(rows))
    for r in rows:
        dt.datetime.strptime(r, "%Y-%m-%dT%H:%M")
    registered = sorted({r["utc_minute"] for r in csv.DictReader(REGISTERED_CAL.open())})
    # the registered calendar rule from 2025 on (the holdout and after) is in the seed unchanged
    reg_2025 = [r for r in registered if r >= "2025-01-01"]
    seed_until = [r for r in rows if r <= registered[-1]]
    assert [r for r in seed_until if r >= "2025-01-01"] == reg_2025
    assert valid[0] >= registered[-1][:10]
