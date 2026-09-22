"""
Regression guard for C-11 (audit 2026-09-22): min-lot clamp escaped the risk cap.

``CalculateDynamicVolumeInUnits`` sizes from ``MaxRiskPerTradeMoney``, then
clamps up to ``Symbol.VolumeInUnitsMin`` without re-checking what that clamped
size actually risks. On a small account trading an instrument with a large
minimum lot (US30, BTC, indices) and a wide technical stop, the broker minimum
at that stop can risk well over the configured cap -- and the order went out
anyway, with no warning in the log.

``AiAgentBot`` has this guard (Hard Guardrail 2 + Dynamic Risk Adaptation, and it
blocks the trade). FlowRsiBot did not.
"""

from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "FlowRsiBot.cs"


def _method_body(signature: str) -> str:
    src = CS_PATH.read_text(encoding="utf-8")
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


def test_risk_is_rechecked_after_the_minimum_lot_clamp():
    body = _method_body("private double CalculateDynamicVolumeInUnits(double slPips)")
    clamp_idx = body.index("if (normalizedUnits < Symbol.VolumeInUnitsMin)")
    after = body[clamp_idx:]
    assert "MaxRiskPerTradeMoney" in after, (
        "Nothing re-checks the dollar risk after the volume is clamped up to the "
        "broker minimum, so MaxRiskPerTradeMoney can be exceeded silently."
    )


def test_over_cap_minimum_lot_is_rejected_not_silently_traded():
    body = _method_body("private double CalculateDynamicVolumeInUnits(double slPips)")
    clamp_idx = body.index("if (normalizedUnits < Symbol.VolumeInUnitsMin)")
    after = body[clamp_idx:]
    assert "return 0" in after.replace("return 0.0", "return 0"), (
        "An over-cap minimum lot must be signalled to the caller (volume 0) so the "
        "entry can be refused."
    )
    assert "Print(" in after, "An over-cap minimum lot must be logged."


def test_caller_refuses_a_zero_volume():
    body = _method_body("private void ExecuteTechnicalOrder(")
    order_idx = body.index("var result = ExecuteMarketOrder(")
    before = body[:order_idx]
    assert "targetUnits <= 0" in before, (
        "ExecuteTechnicalOrder does not check for a refused (zero) volume and would "
        "send a zero-size order to the broker."
    )
