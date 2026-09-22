"""
Regression guard for C-02 (audit 2026-09-22): ADJUST must never widen the stop.

``AiAgentBot`` (TMS/ORB) sized every entry against ``MaxDollarRiskPerTrade``. The
``ADJUST`` branch then called ``pos.ModifyStopLossPrice`` after only two checks --
the Anti-Premature BE guard and a "SL is on the right side of market" buffer
check. Neither stops the LLM returning an ``new_sl_price`` FARTHER from entry than
the current SL ("give the trade room to breathe"), which silently multiplies the
risk the entry guardrails were built to cap (0.7xATR sized to $12 -> 2xATR ~ $36).

The other two bots already ratchet: ``FlowRsiBot.cs`` ("Strict One-Way Profit
Ratchet") and ``AsianRangeJudasSweepBot.SafeModifyPosition``. Server-side,
``validate_judas_adjust_decision`` only runs ``if is_judas`` -- TMS has no net.

No .NET toolchain here, so these tests pin the source-level contract AND evaluate
the extracted guard condition against the four widen/tighten scenarios, which is
what catches an inverted comparison.
"""

import re
from pathlib import Path

import pytest

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AiAgentBot.cs"


def _adjust_block() -> str:
    """The body of the `if (decision.action == "ADJUST")` branch in ExecuteDecision."""
    src = CS_PATH.read_text(encoding="utf-8")
    start = src.index('if (decision.action == "ADJUST")')
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError("Unbalanced braces in the ADJUST branch")


def _condition_after(block: str, if_idx: int) -> str:
    """Extract the parenthesised condition of the `if` starting at if_idx."""
    open_idx = block.index("(", if_idx)
    depth = 0
    for i in range(open_idx, len(block)):
        if block[i] == "(":
            depth += 1
        elif block[i] == ")":
            depth -= 1
            if depth == 0:
                return block[open_idx + 1 : i]
    raise AssertionError("Unbalanced parentheses in if condition")


def _ratchet_condition() -> str:
    """Find the guard that compares the proposed SL against the position's current SL."""
    block = _adjust_block()
    modify_idx = block.index("ModifyStopLossPrice")
    for match in re.finditer(r"\bif\s*\(", block):
        if match.start() > modify_idx:
            break
        cond = _condition_after(block, match.start())
        if "pos.StopLoss" in cond and "targetSL" in cond:
            return cond
    raise AssertionError(
        "No one-way SL ratchet found in the ADJUST branch: nothing compares the "
        "AI-proposed SL against pos.StopLoss before ModifyStopLossPrice, so an "
        "LLM 'give it room to breathe' ADJUST can widen the stop past the dollar "
        "risk the entry was sized for."
    )


def _guard_blocks(cond: str, *, is_buy: bool, target_sl: float, current_sl: float) -> bool:
    """Evaluate the extracted C# condition; True means the widening ADJUST is rejected."""
    py = cond
    py = py.replace("pos.TradeType == TradeType.Buy", "IS_BUY")
    py = py.replace("pos.TradeType == TradeType.Sell", "(not IS_BUY)")
    py = py.replace("targetSL.HasValue", "True").replace("pos.StopLoss.HasValue", "True")
    py = py.replace("targetSL.Value", "TARGET").replace("pos.StopLoss.Value", "CURRENT")
    py = py.replace("&&", " and ").replace("||", " or ")
    py = re.sub(r"!(?!=)", " not ", py)
    py = " ".join(py.split())  # C# wraps the condition over several lines; eval needs one
    return bool(
        eval(  # noqa: S307 - evaluating our own translated source under an empty builtins
            f"({py})",
            {"__builtins__": {}},
            {"IS_BUY": is_buy, "TARGET": target_sl, "CURRENT": current_sl},
        )
    )


# entry 100.0; BUY stop below market, SELL stop above market.
WIDEN_TIGHTEN_CASES = [
    # (id, is_buy, target_sl, current_sl, should_block)
    ("buy-widen", True, 98.0, 99.0, True),     # LLM drops the stop further away -> reject
    ("buy-tighten", True, 99.5, 99.0, False),  # stop pulled up toward profit -> allow
    ("sell-widen", False, 102.0, 101.0, True), # LLM lifts the stop further away -> reject
    ("sell-tighten", False, 100.5, 101.0, False),
]


@pytest.mark.parametrize(
    "case_id,is_buy,target_sl,current_sl,should_block",
    WIDEN_TIGHTEN_CASES,
    ids=[c[0] for c in WIDEN_TIGHTEN_CASES],
)
def test_ratchet_rejects_widening_and_allows_tightening(
    case_id, is_buy, target_sl, current_sl, should_block
):
    cond = _ratchet_condition()
    blocked = _guard_blocks(cond, is_buy=is_buy, target_sl=target_sl, current_sl=current_sl)
    if should_block:
        assert blocked, (
            f"[{case_id}] ratchet lets the stop MOVE AWAY from entry "
            f"({current_sl} -> {target_sl}): the dollar risk sized at entry is blown past."
        )
    else:
        assert not blocked, (
            f"[{case_id}] ratchet wrongly rejects a stop moving TOWARD profit "
            f"({current_sl} -> {target_sl}): break-even and trailing ADJUSTs would be dead."
        )


def test_ratchet_skips_the_position_rather_than_modifying_it():
    """A rejected ADJUST must leave the existing SL untouched, not fall through."""
    block = _adjust_block()
    cond_idx = block.index(_ratchet_condition())
    modify_idx = block.index("ModifyStopLossPrice")
    between = block[cond_idx:modify_idx]
    assert "continue" in between, (
        "The ratchet guard does not `continue` - a widening SL still reaches "
        "ModifyStopLossPrice further down the loop body."
    )


def test_ratchet_is_logged():
    """Operators must be able to see the AI proposing a wider stop."""
    block = _adjust_block()
    cond_idx = block.index(_ratchet_condition())
    modify_idx = block.index("ModifyStopLossPrice")
    assert "Print(" in block[cond_idx:modify_idx], (
        "Rejected widening ADJUSTs are dropped silently - no log line to audit."
    )


def test_existing_adjust_guards_are_preserved():
    """Guard against over-fixing: the BE guard and side/buffer validity check must survive."""
    block = _adjust_block()
    assert "Anti-Premature BE Guard" in block, "Anti-Premature BE guard was lost"
    assert "minBuffer" in block, "SL side/buffer validity check was lost"
