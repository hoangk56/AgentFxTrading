"""
Regression guard for C-09 (audit 2026-09-22): BE was marked done even when it failed.

``AiAgentBot``'s break-even block discarded the ``TradeResult`` from
``ModifyStopLossPrice``, added the id to ``_breakevenApplied`` regardless, and
then halved the position via ``ModifyVolume``. ``_breakevenApplied`` is what
gates re-entry into the block, so a rejection was permanent.

``InvalidStopLossTakeProfit`` is real in this deployment -- observed in
cbot-demo-demo-btcusd-all-flowrsi. When price jumps straight to the BE trigger
the broker refuses a stop that close to market, and the position ends up at HALF
size with its ORIGINAL stop still in place, never retried. Only the giveback
guard is left.

``FlowRsiBot`` and ``AsianRangeJudasSweepBot.ProcessBreakEvenLogic`` both check
``IsSuccessful`` first. This pins the same contract for the TMS bot.
"""

from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AiAgentBot.cs"


def _breakeven_block() -> str:
    """The `if (shouldMove) { ... }` body of the break-even branch."""
    src = CS_PATH.read_text(encoding="utf-8")
    anchor = src.index("// Breakeven: move SL to entry + offset when profit >= trigger")
    start = src.index("if (shouldMove)", anchor)
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError("Unbalanced braces in the break-even block")


def test_modify_stop_loss_result_is_captured():
    block = _breakeven_block()
    assert "= pos.ModifyStopLossPrice(" in block, (
        "The TradeResult from ModifyStopLossPrice is discarded - a broker rejection "
        "(InvalidStopLossTakeProfit) is indistinguishable from success."
    )


def test_breakeven_is_not_marked_applied_before_the_result_is_checked():
    block = _breakeven_block()
    check_idx = block.find("IsSuccessful")
    mark_idx = block.find("_breakevenApplied.Add")
    assert check_idx != -1, (
        "Nothing checks IsSuccessful - a failed BE is recorded as done and "
        "_breakevenApplied permanently blocks the retry."
    )
    assert check_idx < mark_idx, (
        "_breakevenApplied.Add runs before the IsSuccessful check - a rejected BE "
        "is still marked applied and never retried."
    )


def test_partial_close_does_not_run_when_the_stop_move_failed():
    block = _breakeven_block()
    check_idx = block.index("IsSuccessful")
    volume_idx = block.index("pos.ModifyVolume(")
    assert check_idx < volume_idx, (
        "ModifyVolume runs before the stop move is confirmed - the position is cut "
        "to half size while still carrying its original full-risk stop."
    )
    guard = block[check_idx:volume_idx]
    assert "continue" in guard or "return" in guard, (
        "A failed stop move does not short-circuit - execution falls through to the "
        "partial close anyway."
    )


def test_failed_breakeven_is_logged():
    block = _breakeven_block()
    check_idx = block.index("IsSuccessful")
    volume_idx = block.index("pos.ModifyVolume(")
    assert "Print(" in block[check_idx:volume_idx], (
        "A rejected break-even is swallowed silently - nothing to audit in the logs."
    )
