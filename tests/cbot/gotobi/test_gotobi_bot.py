"""cBot/GotobiBot.cs against the research it implements and the three rules every bot of it must keep.

The research (research/results/portfolio/swing_lab_v2_2026-09-27.md, candidate C3) validated one schedule and one
stop; the cBot's defaults must stay equal to research/swing/swing_rules.gotobi, or a live result no longer says
anything about the backtest. The hard rules from the brief: lots never depend on account capital, no position is
held longer than 5 days, a bot never holds more than 3 positions (this one: 1 at a time).

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build is checked on the VPS.
"""
import re
from tests._paths import REPO_ROOT, CBOT_DIR

SRC = (CBOT_DIR / "GotobiBot.cs").read_text(encoding="utf-8")
RESEARCH = (REPO_ROOT / "research" / "swing" / "swing_rules.py").read_text(encoding="utf-8")


def _default(prop: str) -> float:
    m = re.search(r'DefaultValue = ([\d.]+)[^\]]*\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no [Parameter] default for {prop}"
    return float(m.group(1))


def _max_value(prop: str) -> float:
    m = re.search(r'MaxValue = ([\d.]+)\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no MaxValue for {prop}"
    return float(m.group(1))


def _body(signature: str) -> str:
    start = SRC.index(signature)
    open_idx = SRC.index("{", start)
    depth = 0
    for i in range(open_idx, len(SRC)):
        depth += {"{": 1, "}": -1}.get(SRC[i], 0)
        if depth == 0:
            return SRC[open_idx:i + 1]
    raise AssertionError(f"unbalanced braces in {signature}")


def _research_default(name: str) -> int:
    sig = re.search(r"def gotobi\(([^)]*)\)", RESEARCH, re.S).group(1)
    expr = re.search(rf"\b{name}=([^,]+)", sig).group(1)
    return eval(expr, {"__builtins__": {}})          # "18 * 60", "55", "2 * 60 + 55", "3.0"


def test_schedule_is_the_researched_one():
    assert _default("LongEntryHourUtc") * 60 + _default("LongEntryMinuteUtc") == _research_default("entry_utc")
    assert _default("FixHourUtc") * 60 + _default("FixMinuteUtc") == _research_default("fix_utc")
    assert _default("ShortExitHourUtc") * 60 + _default("ShortExitMinuteUtc") == _research_default("end_utc")


def test_stop_is_the_researched_one():
    assert _default("StopAtrMultiplier") == _research_default("slk")
    assert re.search(r"def _h1_atr_on\(b, symbol, n=(\d+)\)", RESEARCH).group(1) == str(int(_default("AtrPeriod")))
    assert "Indicators.AverageTrueRange(MarketData.GetBars(TimeFrame.Hour), AtrPeriod, MovingAverageType.Simple)" in SRC
    assert "_atr.Result.Last(1)" in _body("private void TryOpenLeg(")       # last closed H1 bar, as the research


def test_gotobi_calendar_matches_the_research_rule():
    body = _body("public static bool IsGotobi(DateTime date)")
    assert "new[] { 5, 10, 15, 20, 25, last }" in body
    assert "DateTime.DaysInMonth(d.Year, d.Month)" in body
    assert re.search(r"while \(moved\.DayOfWeek == DayOfWeek\.Saturday \|\| moved\.DayOfWeek == DayOfWeek\.Sunday\)\s*"
                     r"moved = moved\.AddDays\(-1\);", body), "a weekend gotobi day moves to the Friday before"


def test_short_is_not_chased_after_the_fix():
    # A short started 10 minutes after the fix lost money in 2016-2021 (window sensitivity in the report).
    assert _default("ShortEntryGraceMinutes") <= 5 and _max_value("ShortEntryGraceMinutes") < 10


def test_lot_size_never_reads_the_account():
    for sig in ("private double VolumeForRisk(double stopPips)", "private void TryOpenLeg(Leg leg, DateTime day, bool decoy)"):
        body = _body(sig)
        assert "Account." not in body, f"{sig} reads the account: lots must not depend on capital"
    sizing = _body("private double VolumeForRisk(double stopPips)")
    assert "RiskPerTradeMoney / riskPerUnit" in sizing
    assert "Symbol.VolumeInUnitsMin" in sizing and "MaxMinLotRiskMultiple" in sizing


def test_no_position_outlives_its_leg_or_five_days():
    assert _default("MaxHoldHours") <= 24 and _max_value("MaxHoldHours") <= 5 * 24
    body = _body("private void CloseDueLegs(DateTime now)")
    assert "now >= FixTime(info.Day)" in body and "now >= ShortExitTime(info.Day)" in body
    assert "TimeSpan.FromHours(MaxHoldHours)" in body
    assert "CloseDueLegs(now);" in _body("private void Evaluate()")


def test_one_position_at_a_time_and_one_attempt_per_leg():
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    order = body.index("ExecuteMarketOrder(")
    assert body.index("if (GetBotPositions().Count > 0) return;") < order
    assert body.index("LegAlreadyTraded(tag)") < order
    assert body.index("if (!Symbol.MarketHours.IsOpened()) return;") < order   # no fill on a stale weekend quote
    assert "ExecuteMarketOrder(tradeType, SymbolName, volume, _label, orderStopPips, null, Seal(comment))" in body
    assert SRC.count("ExecuteMarketOrder(") == 1
    traded = _body("private bool LegAlreadyTraded(string tag)")
    assert "History.Any(h => IsOwnLabel(h.Label) && h.SymbolName == SymbolName && ParseLeg(Unseal(h.Comment))?.Tag == tag)" in traded


def test_nothing_trades_on_a_stale_quote():
    # Backtests #366-#374: the 1 s timer bought USDJPY at Friday's ask on winter Sundays, an hour before the week's
    # first tick, because the backtest's schedule already said "open". Only a tick counts as a quote.
    assert "_lastTickAt = Server.Time;" in _body("protected override void OnTick()")
    assert "_lastTickAt" not in _body("protected override void OnTimer()")
    evaluate = _body("private void Evaluate()")
    guard = evaluate.index("if (!HasFreshQuote(now)) return;")
    assert guard < evaluate.index("CloseDueLegs(now);") and guard < evaluate.index("TryOpenLeg(")
    assert "(now - _lastTickAt).TotalSeconds <= MaxQuoteAgeSeconds" in SRC
    age = float(re.search(r"private const double MaxQuoteAgeSeconds = ([\d.]+);", SRC).group(1))
    assert 0 < age <= 120, "a quote older than a couple of minutes is not the market's price"


def test_christmas_2026_is_skipped_by_default():
    # 2026-12-25 is a Friday gotobi day and the broker is closed at the fix: the long bought on the 24th could not
    # be closed until the market reopens after the weekend.
    m = re.search(r'DefaultValue = "([^"]*)"\)\]\s*public string SkipDates \{ get; set; \}', SRC)
    assert m, "no [Parameter] default for SkipDates"
    assert "2026-12-25" in m.group(1).split(",")


def test_backtests_never_reach_the_server():
    for sig in ("private void StartCommandPoll()", "private void SendLiveTickTelemetry(bool force = false)",
                "private void ReportPositionOpen(Position position, double slPips, string reason)",
                "private void ReportPositionClosed(Position position, double pnl, string reason, double exitPrice, double pips)"):
        assert "RunningMode != RunningMode.RealTime" in _body(sig), sig


def test_runs_in_utc():
    assert "[Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]" in SRC


# --- camouflage: the broker must not read the strategy off the orders (virtual stop, decoys, jittered entries) ---

def test_camouflage_needs_the_tag_key_on_a_live_run():
    # without the key the comment is plain, and would show the real stop and which legs are decoys
    assert "private bool Camouflaged => VirtualStop && (RunningMode != RunningMode.RealTime || _tagKey != null);" in SRC
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "double orderStopPips = stopPips;" in body and "if (Camouflaged)" in body
    assert "if (!Camouflaged || DecoyLegProbability <= 0) return false;" in _body("private bool PlanLeg(Leg leg, DateTime day, out bool decoy)")


def test_broker_stop_is_never_wider_than_the_real_one():
    # a bot or VPS that dies loses at most 1 R a position
    for prop in ("EmergencyStopMin", "EmergencyStopMax"):
        assert _default(prop) <= 1.0 and _max_value(prop) <= 1.0
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "orderStopPips = stopPips * (EmergencyStopMin + _random.NextDouble() * Math.Max(0, EmergencyStopMax - EmergencyStopMin));" in body


def test_virtual_stop_closes_after_the_leg_exits_are_checked():
    body = _body("private void CloseDueLegs(DateTime now)")
    assert body.index("now >= FixTime(info.Day)") < body.index("VirtualStopHit(pos, info)")
    hit = _body("private bool VirtualStopHit(Position pos, LegInfo info)")
    assert "Symbol.Bid <= stop.Value" in hit and "Symbol.Ask >= stop.Value" in hit


def test_decoys_only_on_plain_weekdays_with_the_real_lot():
    plan = _body("private bool PlanLeg(Leg leg, DateTime day, out bool decoy)")
    assert plan.index("if (IsTradingDay(day)) return true;") < plan.index("Draw(")
    assert "IsGotobi(day) || _skipDates.Contains(day.Date)" in plan
    assert "DayOfWeek.Saturday" in plan and "DayOfWeek.Sunday" in plan
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "double volume = VolumeForRisk(stopPips);" in body          # the real leg's lot, not the decoy stop's
    assert body.count("VolumeForRisk(") == 1
    # a share of the decoys trades a small lot, drawn per leg; a real leg never does
    assert "if (decoy && Draw(tag, \"size\") < DecoySmallShare)" in body


def test_long_entry_jitter_stays_in_the_researched_window():
    # swing_lab_v2: the long leg's start hardly matters between 17:00 and 21:00 UTC
    centre = _default("LongEntryHourUtc") * 60 + _default("LongEntryMinuteUtc")
    jitter = _default("LongEntryJitterMinutes")
    assert 17 * 60 <= centre - jitter and centre + jitter <= 21 * 60
    assert "now >= JitteredLongEntry(tomorrow)" in _body("private void Evaluate()")
    # the fix is the edge: the short still opens at the fix, within the grace minutes
    assert "now >= FixTime(today)" in _body("private void Evaluate()")
