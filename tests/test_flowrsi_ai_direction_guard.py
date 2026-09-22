"""
Regression guard for C-05 (audit 2026-09-22): wrong-side stop silently clamped.

Two holes compounded into one bad order:

1. ``ExecuteDecision`` executed ANY BUY/SELL the AI returned without comparing it
   to the ``candidate_action`` that was sent. ``MANAGE_ONLY`` was checked; a
   concrete BUY/SELL was not.
2. ``ExecuteTechnicalOrder`` measures ``slDistancePips`` with ``Math.Abs``, so a
   stop on the WRONG side still yields a large distance -- and that distance
   sizes the volume. The pre-flight boundary check then CLAMPED the stop to
   ``Bid/Ask -/+ (3*spread + 2 pips)`` rather than refusing.

Candidate BUY with a stop 20p below; LLM answers SELL at 80% confidence.
Sizing runs on 20p, the clamp drops the stop to ~5p, and a position sized for 20p
of risk goes out with a 5p stop and a 30p target. It gets swept.

Not yet observed in the 22/09 logs, but nothing on the path prevents it.
"""

import re
from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "FlowRsiBot.cs"


def _src() -> str:
    return CS_PATH.read_text(encoding="utf-8")


def _method_body(signature: str) -> str:
    src = _src()
    start = src.index(signature)
    open_idx = src.index("{", start)
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[open_idx : i + 1]
    raise AssertionError(f"Unbalanced braces in {signature!r}")


# ── Layer 1: the AI may not trade against the candidate it was asked about ──

def test_ai_action_opposite_to_the_candidate_is_refused():
    body = _method_body("private void ExecuteDecision(AgentDecision decision")
    entry_idx = body.index("// Handle BUY / SELL")
    preceding = body[:entry_idx]
    assert re.search(r"action\s*!=\s*allowedDirection", preceding), (
        "ExecuteDecision executes any BUY/SELL the AI returns without checking it "
        "against allowedDirection. A reversed answer is traded with SL/TP computed "
        "for the opposite side."
    )


def test_direction_guard_only_applies_to_concrete_directions():
    """MANAGE_ONLY / NONE candidates must not be caught by the new guard."""
    body = _method_body("private void ExecuteDecision(AgentDecision decision")
    entry_idx = body.index("// Handle BUY / SELL")
    guard = body[:entry_idx]
    match = re.search(r"action\s*!=\s*allowedDirection", guard)
    scope = guard[max(0, match.start() - 400) : match.start()]
    assert 'allowedDirection == "BUY"' in scope and 'allowedDirection == "SELL"' in scope, (
        "The direction guard must only fire when allowedDirection is a concrete "
        "BUY/SELL, otherwise it would also block legitimate MANAGE_ONLY handling."
    )


def test_manage_only_guard_is_preserved():
    body = _method_body("private void ExecuteDecision(AgentDecision decision")
    assert 'allowedDirection == "MANAGE_ONLY"' in body, (
        "The MANAGE_ONLY guard was lost."
    )


# ── Layer 2: a wrong-side stop is refused, and any clamp re-sizes the volume ──

def test_wrong_side_stop_is_rejected_not_clamped():
    body = _method_body("private void ExecuteTechnicalOrder(")
    boundary_idx = body.index("Pre-flight broker boundary checks")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    region = body[boundary_idx:order_idx]
    assert "return;" in region, (
        "The pre-flight section cannot refuse an order - a stop on the wrong side of "
        "market is still silently clamped to ~3x spread on a position sized for the "
        "original wide stop."
    )
    assert "Security Alert" in region, (
        "A refused wrong-side stop must be logged as a Security Alert, not dropped."
    )


def test_volume_is_resized_when_the_preflight_moves_the_stop():
    body = _method_body("private void ExecuteTechnicalOrder(")
    boundary_idx = body.index("Pre-flight broker boundary checks")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    region = body[boundary_idx:order_idx]
    assert "CalculateDynamicVolumeInUnits(" in region, (
        "targetUnits is still the value computed from the PRE-clamp stop distance. "
        "When the boundary check moves the stop closer, the position carries more "
        "dollar risk than the risk engine sized it for."
    )


def test_sizing_still_happens_before_the_order():
    """Guard against over-fixing: the risk engine must still size the entry."""
    body = _method_body("private void ExecuteTechnicalOrder(")
    assert "double targetUnits = CalculateDynamicVolumeInUnits(slDistancePips);" in body, (
        "The initial risk-engine sizing call was removed."
    )
