"""
Regression guard for C-07 (audit 2026-09-22): Asian range was off by one bar.

``TrackAsianSession`` took its hour from ``Server.Time`` -- the moment the tick
closed the bar -- while reading High/Low from ``Bars.LastBar``, the bar that
OPENED 15 minutes earlier. With ``asianEndHour = 6``:

  * the 05:45-06:00 bar closes at 06:00 -> hour 6, fails `hour < 6` -> the last
    bar of the Asian session is DROPPED from the range;
  * the 23:45-00:00 bar closes at 00:00 -> hour 0, passes `hour >= 0` -> a bar
    from the previous day is folded in, and because `_asianSessionDate != date`
    the range is RESET to that single bar's High/Low.

``InitializeAsianSession`` (run on restart) uses ``bar.OpenTime.Hour`` and is
correct, so the two paths disagreed: a container restart silently changed
``_asianLow``/``_asianHigh``, and with them the sweep threshold,
``IsEntryTooExtended`` and ``CheckStructuralInvalidation``.

No .NET toolchain in this suite, so this pins the source-level contract: the
hour and the High/Low must come from the same bar.
"""

import re
from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AsianRangeJudasSweepBot.cs"


def _src() -> str:
    return CS_PATH.read_text(encoding="utf-8")


def _track_call_argument() -> str:
    match = re.search(r"TrackAsianSession\((?P<arg>[^)]*)\);", _src())
    assert match, "TrackAsianSession call site not found"
    return match.group("arg").strip()


def test_session_hour_comes_from_the_bar_not_the_tick_clock():
    arg = _track_call_argument()
    assert arg != "Server.Time", (
        "TrackAsianSession is still driven by Server.Time (the tick that CLOSED the "
        "bar) while it reads High/Low from Bars.LastBar (the bar that OPENED 15m "
        "earlier) - the Asian range is off by one bar at both session edges."
    )


def test_session_hour_uses_the_same_bar_whose_high_low_is_read():
    """The time argument must be the OpenTime of the bar TrackAsianSession samples."""
    arg = _track_call_argument()
    assert "OpenTime" in arg, (
        f"TrackAsianSession must be passed a bar OpenTime so the hour and the "
        f"High/Low describe the same bar, got: {arg!r}"
    )
    assert "LastBar" in arg or "Bars[" in arg, (
        f"TrackAsianSession must be passed the OpenTime of the bar it samples "
        f"(Bars.LastBar), got: {arg!r}"
    )


def test_live_tracking_agrees_with_restart_initialisation():
    """Both paths must key off OpenTime, or a restart silently redraws the range."""
    src = _src()
    init_start = src.index("private void InitializeAsianSession")
    init_body = src[init_start : src.index("private void TrackAsianSession")]
    assert "bar.OpenTime" in init_body, (
        "InitializeAsianSession no longer reads bar.OpenTime - the restart path and "
        "the live path must agree on which bars belong to the Asian session."
    )
    assert "OpenTime" in _track_call_argument(), (
        "Live tracking and restart initialisation disagree on the bar time source."
    )
