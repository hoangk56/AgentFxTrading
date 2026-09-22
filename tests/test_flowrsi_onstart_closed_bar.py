"""
Regression guard for C-06 (audit 2026-09-22): boot snapshot ran on a forming bar.

``OnStart`` called ``EvaluateStrategySignals``, which takes
``index = Bars.ClosePrices.Count - 1``. Inside ``OnBarClosed`` that is the bar
that just closed; at start-up nothing has just closed, so it is the bar still
FORMING. Every RSI cross, FVG, liquidity sweep and entry candidate was computed
from a partial bar and sent straight to the AI.

Deploying 15 containers at 10:35 fires 15 snapshots against an M15 bar five
minutes old. A cross that exists mid-bar and reverses by the close can be
confirmed by the LLM and traded for real -- and it repeats on every restart.

When a position is already open, ``EvaluateStrategySignals(true)`` sends a
``MANAGE_ONLY`` snapshot and cannot open anything, so that path stays. What must
not happen is producing an ENTRY candidate from a partial bar.
"""

import re
from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "FlowRsiBot.cs"


def _on_start_boot_block() -> str:
    """The `if (UseAiGateMode && RunningMode == RunningMode.RealTime)` block in OnStart."""
    src = CS_PATH.read_text(encoding="utf-8")
    anchor = src.index("Dispatch initial boot snapshot to AI Server")
    open_idx = src.index("{", src.index("if (UseAiGateMode", anchor))
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError("Unbalanced braces in the OnStart boot block")


def test_boot_snapshot_does_not_evaluate_entries_while_flat():
    block = _on_start_boot_block()
    call = re.search(r"EvaluateStrategySignals\(", block)
    assert call, "OnStart no longer dispatches a boot snapshot at all"
    preceding = block[: call.start()]
    assert re.search(r"if\s*\([^)]*hasOpenPos", preceding), (
        "OnStart calls EvaluateStrategySignals unconditionally. While flat that "
        "produces an ENTRY candidate from the bar still forming at start-up, which "
        "the AI can confirm into a real trade on every restart."
    )


def test_boot_snapshot_still_runs_for_an_open_position():
    """Guard against over-fixing: a restart with a live position must still reach the AI."""
    block = _on_start_boot_block()
    assert "EvaluateStrategySignals(" in block, (
        "The boot snapshot was removed entirely - after a restart the AI would no "
        "longer be told about an already-open position (MANAGE_ONLY)."
    )
    assert "GetBotPositions()" in block, (
        "OnStart no longer checks for open positions before dispatching."
    )


def test_skipped_boot_evaluation_is_logged():
    block = _on_start_boot_block()
    assert "Print(" in block, (
        "Skipping the boot evaluation is invisible - no log line explains why no "
        "snapshot was sent at start-up."
    )
