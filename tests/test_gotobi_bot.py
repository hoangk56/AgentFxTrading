"""cBot/GotobiBot.cs against the research it implements and the three rules every bot of it must keep.

The research (research/results/portfolio/swing_lab_v2_2026-09-27.md, candidate C3) validated one schedule and one
stop; the cBot's defaults must stay equal to research/scan/swing_rules.gotobi, or a live result no longer says
anything about the backtest. The hard rules from the brief: lots never depend on account capital, no position is
held longer than 5 days, a bot never holds more than 3 positions (this one: 1 at a time).

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build is checked on the VPS.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "cBot" / "GotobiBot.cs").read_text(encoding="utf-8")
RESEARCH = (ROOT / "research" / "scan" / "swing_rules.py").read_text(encoding="utf-8")


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
    for sig in ("private double VolumeForRisk(double stopPips)", "private void TryOpenLeg(Leg leg, DateTime day)"):
        body = _body(sig)
        assert "Account." not in body, f"{sig} reads the account: lots must not depend on capital"
    sizing = _body("private double VolumeForRisk(double stopPips)")
    assert "RiskPerTradeMoney / riskPerUnit" in sizing
    assert "Symbol.VolumeInUnitsMin" in sizing and "MaxMinLotRiskMultiple" in sizing


def test_no_position_outlives_its_leg_or_five_days():
    assert _default("MaxHoldHours") <= 24 and _max_value("MaxHoldHours") <= 5 * 24
    body = _body("private void CloseDueLegs(DateTime now)")
    assert "now >= FixTime(day)" in body and "now >= ShortExitTime(day)" in body
    assert "TimeSpan.FromHours(MaxHoldHours)" in body
    assert "CloseDueLegs(now);" in _body("private void Evaluate()")


def test_one_position_at_a_time_and_one_attempt_per_leg():
    body = _body("private void TryOpenLeg(Leg leg, DateTime day)")
    order = body.index("ExecuteMarketOrder(")
    assert body.index("if (GetBotPositions().Count > 0) return;") < order
    assert body.index("LegAlreadyTraded(tag)") < order
    assert body.index("if (!Symbol.MarketHours.IsOpened()) return;") < order   # no fill on a stale weekend quote
    assert "ExecuteMarketOrder(tradeType, SymbolName, volume, BotId, stopPips, null, tag)" in body
    assert SRC.count("ExecuteMarketOrder(") == 1
    traded = _body("private bool LegAlreadyTraded(string tag)")
    assert "History.Any(h => h.Label == BotId && h.SymbolName == SymbolName && h.Comment == tag)" in traded


def test_backtests_never_reach_the_server():
    for sig in ("private void StartCommandPoll()", "private void SendLiveTickTelemetry(bool force = false)",
                "private void ReportPositionOpen(Position position, double slPips, string reason)",
                "private void ReportPositionClosed(Position position, double pnl, string reason, double exitPrice, double pips)"):
        assert "RunningMode != RunningMode.RealTime" in _body(sig), sig


def test_runs_in_utc():
    assert "[Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]" in SRC
