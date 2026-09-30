"""cBot/CryptoDonchianBot.cs against the research it implements and the three rules every bot of it must keep.

The research (research/results/portfolio/swing_lab_v2_2026-09-27.md, candidate C1, registered in prereg_swing_v2.md)
fixed one rule: H4, entry beyond the prior 55-bar channel, exit beyond the prior 20-bar channel, stop 3 x ATR20(H4),
5 days, lot = default risk x clip(strength / median, 0.5, 2). The cBot's defaults must stay equal to it, or a live
result no longer says anything about the backtest. The hard rules from the brief: lots never depend on account
capital, no position is held longer than 5 days, a bot never holds more than 3 positions.

The Mac has no dotnet, so like the other cBot tests these read the C# source; the build is checked on the VPS.
"""
import re
from tests._paths import REPO_ROOT, CBOT_DIR

SRC = (CBOT_DIR / "CryptoDonchianBot.cs").read_text(encoding="utf-8")
RULES = (REPO_ROOT / "research" / "swing" / "swing_rules.py").read_text(encoding="utf-8")
ENGINE = (REPO_ROOT / "research" / "swing" / "swing.py").read_text(encoding="utf-8")
PREREG = (REPO_ROOT / "research" / "results" / "portfolio" / "prereg_swing_v2.md").read_text(encoding="utf-8")
C1 = PREREG[PREREG.index("## C1"):PREREG.index("### C1 result")]


def _param(prop: str, key: str) -> str:
    m = re.search(r'\[Parameter\([^\]]*\b' + key + r' = ([^,\)]+)[^\]]*\)\]\s*public \w+ ' + re.escape(prop) + r' \{ get; set; \}', SRC)
    assert m, f"no {key} for {prop}"
    return m.group(1).strip()


def _default(prop: str) -> float:
    return float(_param(prop, "DefaultValue"))


def _body(signature: str) -> str:
    start = SRC.index(signature)
    open_idx = SRC.index("{", start)
    depth = 0
    for i in range(open_idx, len(SRC)):
        depth += {"{": 1, "}": -1}.get(SRC[i], 0)
        if depth == 0:
            return SRC[open_idx:i + 1]
    raise AssertionError(f"unbalanced braces in {signature}")


def _engine_const(name: str) -> float:
    m = re.search(r"^SCALE_MIN, SCALE_MAX, SCALE_MIN_HISTORY = ([\d.]+), ([\d.]+), (\d+)$", ENGINE, re.M)
    assert m, "research/swing/swing.py lost its scale constants"
    return float(m.group({"SCALE_MIN": 1, "SCALE_MAX": 2, "SCALE_MIN_HISTORY": 3}[name]))


def test_channels_are_the_registered_ones():
    assert "prior 55-bar high" in C1 and "prior 55-bar low" in C1
    assert "prior 20-bar low" in C1 and "prior 20-bar high" in C1
    assert _default("EntryPeriod") == 55 and _default("ExitPeriod") == 20
    assert _param("TradeShorts", "DefaultValue") == "true"                  # "below the 55-bar low -> sell"
    assert "Bars: H4 (UTC-aligned" in C1


def test_h4_bars_are_utc_aligned_from_h1():
    # IC's own H4 bars open at 21/22:00 UTC (the server day); the registered rule used 00:00/04:00/... UTC buckets.
    assert "MarketData.GetBars(TimeFrame.Hour)" in SRC and "TimeFrame.Hour4" not in SRC
    assert "public static DateTime H4BucketStart(DateTime t) => t.Date.AddHours(t.Hour / 4 * 4);" in SRC
    sync = _body("private void SyncH4Bars()")
    assert "for (; _nextH1 < forming; _nextH1++)" in sync          # only closed H1 bars feed prices
    assert "_openBarClose = _h1.ClosePrices[_nextH1];" in sync
    assert "SyncH4Bars();" in _body("private void HandleClosedBars()")


def test_signals_follow_swing_rules_donchian():
    rule = RULES[RULES.index("def donchian("):RULES.index("def carry(")]
    assert "le = b.c > hh" in rule and "lx = b.c < xl" in rule and "sx = b.c > xh" in rule
    entry = _body("private int EntrySignal(int i, out double level, out double atr, out double strength)")
    assert "close > hh" in entry and "close < ll" in entry
    assert "(close - hh) / atr + 1e-9" in entry and "(ll - close) / atr + 1e-9" in entry   # strength, as the rule's
    exit_ = _body("private bool ExitSignal(int i, int side)")
    assert "close < PriorLow(i, ExitPeriod)" in exit_ and "close > PriorHigh(i, ExitPeriod)" in exit_
    # prior_max/prior_min: bars i-n .. i-1, the signal bar itself excluded
    assert "for (int j = i - n; j < i; j++)" in _body("private double PriorHigh(int i, int n)")
    assert "for (int j = i - n; j < i; j++)" in _body("private double PriorLow(int i, int n)")


def test_stop_is_the_researched_one():
    assert "3 x ATR(20) of H4" in C1
    assert re.search(r"def donchian\([^)]*slk=3\.0", RULES)
    assert _default("StopAtrMultiplier") == 3.0 and _default("AtrPeriod") == 20
    atr = _body("private double Atr(int i)")                     # SMA of the true range, bar i included
    assert "for (int j = i - AtrPeriod + 1; j <= i; j++)" in atr and "sum / AtrPeriod" in atr
    assert "Math.Max(_barHigh[j], prevClose) - Math.Min(_barLow[j], prevClose)" in atr
    assert "double stopDistance = StopAtrMultiplier * p.Atr;" in _body("private void TryOpenPending(DateTime now)")


def test_lot_scaling_is_the_engines():
    assert "clip(breakout distance in ATR / causal median of earlier breakout distances, 0.5, 2)" in C1
    assert re.search(r"private const double ScaleMin = ([\d.]+);", SRC).group(1) == str(_engine_const("SCALE_MIN"))
    assert re.search(r"private const double ScaleMax = ([\d.]+);", SRC).group(1) == str(_engine_const("SCALE_MAX"))
    assert int(re.search(r"private const int ScaleMinHistory = (\d+);", SRC).group(1)) == _engine_const("SCALE_MIN_HISTORY")
    scale = _body("private double ScaleFor(double strength, out double median)")
    assert "Math.Max(ScaleMin, Math.Min(ScaleMax, strength / median))" in scale
    # causal: the bar's own strength joins the history only after its scale was taken
    scan = _body("private void HandleClosedBars()")
    assert scan.index("ScaleFor(strength, out double median)") < scan.index("_strengths.Add(strength);")


def test_lot_size_never_reads_the_account():
    for sig in ("private double VolumeForRisk(double stopPips, double riskMoney)",
                "private void TryOpenPending(DateTime now)", "private double ScaleFor(double strength, out double median)"):
        assert "Account." not in _body(sig), f"{sig} reads the account: lots must not depend on capital"
    sizing = _body("private double VolumeForRisk(double stopPips, double riskMoney)")
    assert "riskMoney / riskPerUnit" in sizing
    assert "Symbol.VolumeInUnitsMin" in sizing and "MaxMinLotRiskMultiple" in sizing
    assert "double riskMoney = RiskPerTradeMoney * p.Scale;" in _body("private void TryOpenPending(DateTime now)")


def test_no_position_outlives_five_days():
    assert "or 5 days" in C1
    assert _default("MaxHoldHours") == 120 and float(_param("MaxHoldHours", "MaxValue")) <= 120
    assert "TimeSpan.FromHours(MaxHoldHours) - TimeSpan.FromMinutes(1)" in SRC      # as the engine: deadline - 1 min
    close = _body("private void CloseDuePositions(DateTime now)")
    assert "DateTime deadline = pos.EntryTime + HoldLimit;" in close and "if (now >= deadline)" in close
    # A deadline inside a market break (IC crypto: Friday ~1 h, Saturday ~3 h; whole weekends until April 2024) closes the
    # position before the break, as the research did; otherwise it would only close when the market reopens.
    assert "else if (ClosedThrough(now, deadline))" in close
    closed = _body("private bool ClosedThrough(DateTime now, DateTime deadline)")
    assert "hours.TimeTillClose()" in closed and "return !hours.IsOpened(deadline);" in closed
    evaluate = _body("private void Evaluate()")
    assert evaluate.index("CloseDuePositions(now);") < evaluate.index("TryOpenPending(now);")   # close before open


def test_at_most_three_positions_and_one_attempt_per_signal_bar():
    assert _default("MaxPositions") == 3 and float(_param("MaxPositions", "MaxValue")) <= 3
    body = _body("private void TryOpenPending(DateTime now)")
    order = body.index("ExecuteMarketOrder(")
    assert body.index("if (own.Count >= MaxPositions)") < order
    assert body.index("EntryAlreadyTraded(p.Tag)") < order
    assert body.index("if (!Symbol.MarketHours.IsOpened()) return;") < order
    assert body.index("if (now > p.Deadline)") < order
    assert "ExecuteMarketOrder(tradeType, SymbolName, volume, _label, stopPips, null, Seal(comment))" in body
    assert SRC.count("ExecuteMarketOrder(") == 1
    traded = _body("private bool EntryAlreadyTraded(string tag)")
    assert "History.Any(h => IsOwnLabel(h.Label) && h.SymbolName == SymbolName" in traded


def test_exits_caught_after_a_restart():
    # Every bar closed after the entry is checked, so an exit signal the bot slept through still closes the position.
    body = _body("private void MarkSignalExits(int last)")
    assert "_barRevealed[j] > pos.EntryTime" in body and "ExitSignal(j, side)" in body
    assert "MarkSignalExits(last);" in _body("private void HandleClosedBars()")


def test_nothing_trades_on_a_stale_quote():
    assert "_lastTickAt = Server.Time;" in _body("protected override void OnTick()")
    assert "_lastTickAt" not in _body("protected override void OnTimer()")
    evaluate = _body("private void Evaluate()")
    guard = evaluate.index("if (!HasFreshQuote(now)) return;")
    assert guard < evaluate.index("CloseDuePositions(now);") and guard < evaluate.index("TryOpenPending(now);")


def test_kill_switch_reads_r_from_the_booked_risk():
    body = _body("private void RefreshKillSwitch()")
    assert "h.NetProfit / risk" in body and "KillSwitchTrades" in body
    assert 'string comment = $"{p.Tag} risk={bookedRisk.ToString("F2", CultureInfo.InvariantCulture)}";' in SRC
    assert "double bookedRisk = volume * stopPips * Symbol.PipValue;" in SRC
    assert _default("KillSwitchTrades") == 0          # off by default, see the parameter's comment


def test_backtests_never_reach_the_server():
    for sig in ("private void StartCommandPoll()", "private void SendLiveTickTelemetry(bool force = false)",
                "private void ReportPositionOpen(Position position, double slPips, string reason, PendingEntry signal)",
                "private void ReportPositionClosed(Position position, double pnl, string reason, double exitPrice, double pips)"):
        assert "RunningMode != RunningMode.RealTime" in _body(sig), sig


def test_runs_in_utc():
    assert "[Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.FullAccess)]" in SRC
