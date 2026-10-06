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
    assert "_h1 = MarketData.GetBars(TimeFrame.Hour);" in SRC
    assert "Indicators.AverageTrueRange(_h1, AtrPeriod, MovingAverageType.Simple)" in SRC
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
    body = _body("private string DueExitReason(Position pos, DateTime now)")
    assert "now >= FixTime(info.Day)" in body and "now >= ShortExitTime(info.Day)" in body
    assert "TimeSpan.FromHours(MaxHoldHours)" in body
    assert "string reason = DueExitReason(pos, now);" in _body("private void CloseDueLegs(DateTime now)")
    assert "CloseDueLegs(now);" in _body("private void Evaluate()")


def test_one_position_at_a_time_and_one_attempt_per_leg():
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    order = body.index("ExecuteMarketOrderAsync(")
    # one leg at a time: only a position whose exit is due (closed in the same Evaluate) lets the next leg go out
    assert body.index("if (GetBotPositions().Any(p => DueExitReason(p, Server.Time) == null)) return;") < order
    # one order in flight; a lost result times out, and LegAlreadyTraded then finds a fill it missed
    assert body.index("if (_pendingOrderTag != null)") < order
    assert body.index("_pendingOrderTag = tag;") < order
    assert "if (_pendingOrderTag == tag) _pendingOrderTag = null;" in body[order:]
    assert body.index("LegAlreadyTraded(tag)") < order
    assert body.index("if (!Symbol.MarketHours.IsOpened()) return;") < order   # no fill on a stale weekend quote
    assert "ExecuteMarketOrder(" not in SRC and SRC.count("ExecuteMarketOrderAsync(") == 1


def test_the_fix_short_goes_out_before_the_long_closes():
    # gotobi_live_fills_2026-10-06: a short sent only after the long's close filled ~0.5-1.2 pip worse than the
    # backtest, which closes and opens on one tick. The short's order is asynchronous and sent first.
    evaluate = _body("private void Evaluate()")
    assert evaluate.index("TryOpenLeg(Leg.Short, today, shortDecoy);") < evaluate.index("CloseDueLegs(now);")
    assert evaluate.index("CloseDueLegs(now);") < evaluate.index("TryOpenLeg(Leg.Long, tomorrow, longDecoy);")


def test_a_failed_order_is_retried_within_seconds_then_backs_off():
    # 05/10/2026: two live shorts failed with TechnicalError at the fix and waited 30 s
    assert _default("OrderRetrySeconds") <= 2
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "(Server.Time - last).TotalSeconds < RetryDelaySeconds(tag)" in body
    assert "_orderFailures[tag] =" in body
    delay = _body("private double RetryDelaySeconds(string tag)")
    assert "Math.Min(60.0, OrderRetrySeconds * Math.Pow(2, Math.Max(0, fails - 1)))" in delay


def test_fills_are_logged_against_the_quote_at_send():
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert body.index("new SentQuote { Bid = Symbol.Bid, Ask = Symbol.Ask") < body.index("ExecuteMarketOrderAsync(")
    assert "FillNote(tradeType, result.Position.EntryPrice, quote)" in body
    note = _body("private string FillNote(TradeType side, double fill, SentQuote quote)")
    assert "side == TradeType.Buy ? fill - quote.Ask : quote.Bid - fill" in note      # + = against the trader
    close = _body("private TradeResult CloseWithReason(Position pos, string reason)")
    assert close.index("new SentQuote") < close.index("ClosePosition(pos)")
    closed = _body("private void OnPositionClosed(PositionClosedEventArgs args)")
    # a long closes on the bid (a sell), a short on the ask (a buy)
    assert "FillNote(pos.TradeType == TradeType.Buy ? TradeType.Sell : TradeType.Buy, exitPrice, closeQuote)" in closed
    traded = _body("private bool LegAlreadyTraded(string tag)")
    assert "GetBotPositions().Any(p => LegOf(p)?.Tag == tag)" in traded
    assert "History.Any(h => h.SymbolName == SymbolName && InferLeg(h.TradeType, h.EntryTime)?.Tag == tag)" in traded


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

def test_camouflage_needs_no_key():
    # nothing on the order says where the real stop is or which leg is a decoy, so no key is needed to hide it
    assert "private bool Camouflaged => VirtualStop;" in SRC
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
    body = _body("private string DueExitReason(Position pos, DateTime now)")
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


# --- plain orders: no Label, no Comment, like a trade placed by hand -------------------------------------------------
# One bot trades each symbol of an account and nothing is traded there by hand, so the symbol identifies the bot's
# positions; the leg, its day, decoy or not and the virtual stop are read back off the side, the entry time and the
# H1 ATR at the entry, so a restart needs no state.

def test_orders_carry_no_label_and_no_comment():
    body = _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "ExecuteMarketOrderAsync(tradeType, SymbolName, volume, null, orderStopPips, null, null, result =>" in body
    for gone in ("TagKeyFile", "Seal(", "Unseal(", "_tagKey", "IsOwnLabel", "ParseLeg", ".Comment", ".Label"):
        assert gone not in SRC, gone
    assert not re.search(r"\b_label\b", SRC)
    assert "#region Trade tags" not in SRC


def test_the_bot_owns_every_position_on_its_symbol():
    assert "private List<Position> GetBotPositions() => Positions.Where(p => p.SymbolName == SymbolName).ToList();" in SRC
    closed = _body("private void OnPositionClosed(PositionClosedEventArgs args)")
    assert "if (pos == null || pos.SymbolName != SymbolName) return;" in closed


def test_a_leg_is_read_off_its_side_and_entry_time():
    body = _body("private LegInfo InferLeg(TradeType side, DateTime entry)")
    # a buy is the long of the next day, opened from the earliest jittered entry to the latest one
    assert "var day = side == TradeType.Buy ? entry.Date.AddDays(1) : entry.Date;" in body
    assert "LongEntryTime(day).AddMinutes(-LongEntryJitterMinutes)" in body and "LongEntryLatest(day)" in body
    # a sell is the short of its own day, opened at the fix within the grace minutes
    assert "FixTime(day)" in body and "FixTime(day).AddMinutes(ShortEntryGraceMinutes" in body
    # the bot trades a plain weekday only as a decoy
    assert "Decoy = !IsTradingDay(day)" in body
    # outside both windows it is no leg: only Max hold and its broker stop apply
    assert body.count("return null;") >= 1


def test_the_virtual_stop_is_rebuilt_from_the_atr_at_the_entry():
    leg = _body("private LegInfo LegOf(Position pos)")
    assert "InferLeg(pos.TradeType, pos.EntryTime)" in leg
    assert "(info.Decoy ? DecoyStopAtrMultiplier : StopAtrMultiplier) * atr.Value / Symbol.PipSize" in leg
    atr = _body("private double? EntryAtr(DateTime entry)")
    # TryOpenLeg sizes on _atr.Result.Last(1): the last closed H1 bar before the entry
    assert "_atr.Result.Last(1)" in _body("private void TryOpenLeg(Leg leg, DateTime day, bool decoy)")
    assert "int i = _h1.OpenTimes.GetIndexByTime(entry);" in atr and "_atr.Result[i - 1]" in atr
