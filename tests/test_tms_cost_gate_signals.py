"""
Regression guard for C-04 (audit 2026-09-22): Cost Gate skipped TDI cross tracking.

The Cost Gate returns early when the bot is flat and out of session -- sensible
for skipping the HTTP round-trip, except it returned BEFORE ``GetTmsSignals``,
which is the ONLY place ``_lastCrossBar`` / ``_lastCrossDir`` are written.

So crosses that happened before the session opened were never recorded. A NY bot
(13:00 UTC) seeing a TDI cross up at 12:45 still carried yesterday's
``_lastCrossDir = -1`` into the open: ``bars_since_cross`` ~70 killed
``withinWindow``, so ``long_entry`` could not fire in the first bars of the
session, and the snapshot told the LLM ``bias = BEARISH`` / ``cross_direction =
"down"`` while the market had just crossed up.

Signal computation is pure arithmetic over cached bars. Only the HTTP send needs
gating. This pins that ordering.
"""

import re
from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AiAgentBot.cs"


def _src() -> str:
    return CS_PATH.read_text(encoding="utf-8")


def test_cross_state_is_updated_before_the_cost_gate_returns():
    src = _src()
    signals_idx = src.index("GetTmsSignals(index)")
    gate_idx = src.index("// Cost Gate:")
    assert signals_idx < gate_idx, (
        "The Cost Gate returns before GetTmsSignals runs. GetTmsSignals is the only "
        "writer of _lastCrossBar/_lastCrossDir, so every TDI cross outside session "
        "hours is lost and the first bars of the session run on stale bias."
    )


def test_cost_gate_still_blocks_the_http_round_trip():
    """Guard against over-fixing: the gate must still skip the AI request when flat/out of session."""
    src = _src()
    gate_idx = src.index("// Cost Gate:")
    gate_region = src[gate_idx : gate_idx + 600]
    assert "GetBotPositions().Length == 0" in gate_region, (
        "The Cost Gate no longer checks for an empty position list."
    )
    assert "is_trading_time" in gate_region, (
        "The Cost Gate no longer checks session trading hours."
    )
    assert "return;" in gate_region, (
        "The Cost Gate no longer returns - the bot would POST /trade around the clock."
    )


def test_get_tms_signals_remains_the_single_writer_of_cross_state():
    """If cross state ever moves elsewhere, the ordering above stops being the fix."""
    src = _src()
    start = src.index("private TmsSignals GetTmsSignals(int i)")
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                body = src[open_idx : i + 1]
                break
    else:
        raise AssertionError("Unbalanced braces in GetTmsSignals")

    assert "_lastCrossBar = i" in body and "_lastCrossDir = 1" in body, (
        "GetTmsSignals no longer writes the cross state."
    )
    # `private int _lastCrossBar = -1;` is a declaration, not a tracking write.
    assignments = re.findall(r"(?<!int )_lastCrossBar\s*=", src)
    writes_outside = len(assignments) - len(re.findall(r"(?<!int )_lastCrossBar\s*=", body))
    assert writes_outside == 0, (
        f"_lastCrossBar is now written in {writes_outside} place(s) outside "
        f"GetTmsSignals - revisit where cross tracking must run."
    )
