"""
Regression guard for C-13 (audit 2026-09-22): exit price was read off the live spread.

Both bots took the exit price from ``Symbol.Bid``/``Symbol.Ask`` at the moment the
``Positions.Closed`` handler happened to run, not the price the position actually
closed at. When a stop is swept by a spike and price snaps back before the handler
executes, the dashboard shows an exit price that never traded, and every pip/RR
statistic derived from ``exit_price`` is wrong.

``AsianRangeJudasSweepBot`` already does this correctly, looking up
``History.FirstOrDefault(h => h.PositionId == ...)`` and using ``ClosingPrice``.
This pins the same contract for the other two bots.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _handler_body(cs_name: str, signature: str) -> str:
    src = (ROOT / "cBot" / cs_name).read_text(encoding="utf-8")
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
    raise AssertionError(f"Unbalanced braces in {cs_name} {signature!r}")


HANDLERS = [
    ("FlowRsiBot.cs", "private void OnPositionClosed(PositionClosedEventArgs args)"),
    ("AiAgentBot.cs", "private void OnPositionClosed(PositionClosedEventArgs args)"),
]


@pytest.mark.parametrize("cs_name,signature", HANDLERS, ids=[h[0] for h in HANDLERS])
def test_exit_price_prefers_the_booked_closing_price(cs_name, signature):
    body = _handler_body(cs_name, signature)
    assert "ClosingPrice" in body, (
        f"{cs_name} reports an exit price taken from the live Bid/Ask when the handler "
        f"runs, not the price the position closed at. A spike that snaps back produces "
        f"an exit price that never traded."
    )
    assert "PositionId" in body, (
        f"{cs_name} must look the closed trade up in History by PositionId."
    )


@pytest.mark.parametrize("cs_name,signature", HANDLERS, ids=[h[0] for h in HANDLERS])
def test_exit_price_falls_back_when_history_is_not_ready(cs_name, signature):
    body = _handler_body(cs_name, signature)
    assert "Symbol.Bid" in body and "Symbol.Ask" in body, (
        f"{cs_name} has no live-spread fallback for when History has not yet been "
        f"populated - a missing lookup would report no exit price at all."
    )


def test_judas_reference_pattern_is_intact():
    src = (ROOT / "cBot" / "AsianRangeJudasSweepBot.cs").read_text(encoding="utf-8")
    assert "History.FirstOrDefault(h => h.PositionId ==" in src, (
        "The Judas bot's History lookup - the reference pattern for this fix - is gone."
    )
