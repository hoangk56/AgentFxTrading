"""
Partial guard for X-03 (audit 2026-09-22): the BE panel advertised a dead value.

``breakEvenMode`` defaults to ``Risk_Reward_Ratio``, and ``ProcessBreakEvenLogic``
only reads ``breakEvenTrigger`` (pips) in the ``Fixed_Pips`` branch. The status
panel printed "BreakEven: ON (250 pips)" regardless, so the one number an operator
sees while tuning was the one number having no effect.

This fixes the reporting only. Whether the preset's per-symbol ``breakEvenTrigger``
values should be made live (by passing ``breakEvenMode=Fixed_Pips``) or dropped in
favour of ``breakEvenRrTrigger`` changes behaviour for 15 live bots and is left to
the operator.
"""

from pathlib import Path

CS_PATH = Path(__file__).resolve().parent.parent / "cBot" / "AsianRangeJudasSweepBot.cs"


def test_status_panel_reports_the_trigger_actually_in_force():
    src = CS_PATH.read_text(encoding="utf-8")
    line = next(l for l in src.splitlines() if '"BreakEven    :' in l)
    assert "breakEvenMode" in line, (
        "The BE status line prints breakEvenTrigger unconditionally, but that value is "
        "only read in Fixed_Pips mode - the default is Risk_Reward_Ratio."
    )
    assert "breakEvenRrTrigger" in line, (
        "In the default RR mode the panel must show breakEvenRrTrigger, the threshold "
        "that actually gates the break-even move."
    )
